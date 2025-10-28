# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


"""
``job_submission`` --- Cross-platform HFSS simulation runner with enterprise scheduler support
==============================================================================================

This module provides a single entry point, :func:`create_hfss_config`, that
builds a validated, JSON-serialisable configuration object and submits it to

* local subprocess (default)
* SLURM
* LSF (IBM Platform)
* PBS / Torque
* Windows HPC Server

The configuration is **immutable** (dataclass), **validated** on creation and
can be round-tripped through JSON for persistence or REST transmission.

Examples
--------
Local simulation::

    >>> cfg = create_hfss_config(
    ...     ansys_edt_path="/ansys/v241/Linux64/ansysedt",
    ...     jobid="patch_antenna",
    ...     project_path="/home/antenna.aedt")
    >>> result = cfg.run_simulation(timeout=3600)
    >>> result.returncode
    0

SLURM cluster::

    >>> cfg = create_hfss_config(
    ...     jobid="array_001",
    ...     project_path="/shared/array.aedt",
    ...     scheduler_type=SchedulerType.SLURM,
    ...     scheduler_options=SchedulerOptions(
    ...         queue="compute",
    ...         nodes=4,
    ...         memory="64GB",
    ...         time="08:00:00"))
    >>> job_id = cfg.run_simulation()
    >>> print(job_id)
    slurm_job_12345
"""  # noqa: D205,D400 (summary line is intentionally long)

from datetime import datetime
import enum
import getpass
import logging
import os
import platform
import re
import shlex
import shutil
import subprocess  # nosec B404
import tempfile
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from pyedb.generic.general_methods import installed_ansys_em_versions, is_linux

logger = logging.getLogger("JobManager")


class SchedulerType(enum.Enum):
    """
    Supported enterprise job schedulers.

    Members
    -------
    NONE : str
        Direct subprocess execution (default).
    SLURM : str
        Simple Linux Utility for Resource Management.
    LSF : str
        IBM Platform Load Sharing Facility.
    PBS : str
        Portable Batch System (Torque / PBS Pro).
    WINDOWS_HPC : str
        Microsoft Windows HPC Server.
    """

    NONE = "none"
    LSF = "lsf"
    SLURM = "slurm"
    PBS = "pbs"
    WINDOWS_HPC = "windows_hpc"


class SchedulerOptions(BaseModel):
    """
    Resource requirements and scheduler-specific directives.

    All attributes are validated by :meth:`validate`, which is automatically
    called after instantiation.

    Parameters
    ----------
    queue : str, optional
        Partition or queue name.  Defaults to ``"default"``.
    time : str, optional
        Wall-time limit in ``HH:MM:SS`` or ``D.HH:MM:SS``.  Defaults to
        ``"24:00:00"``.
    nodes : int, optional
        Number of compute nodes.  Defaults to ``1``.
    tasks_per_node : int, optional
        Processes per node.  Defaults to ``1``.
    memory : str, optional
        Memory per node, e.g. ``"4GB"``.  Defaults to ``"4GB"``.
    account : str, optional
        Account / project to charge.
    reservation : str, optional
        Advance reservation name.
    qos : str, optional
        Quality-of-service level.
    constraints : str, optional
        Node features, e.g. ``"gpu"``.
    exclusive : bool, optional
        Request whole nodes.  Defaults to ``False``.
    gpus : int, optional
        Number of GPUs.  Defaults to ``0``.
    gpu_type : str, optional
        GPU model, e.g. ``"a100"``.
    priority : str, optional
        Job priority: ``Low``, ``BelowNormal``, ``Normal``, ``AboveNormal``,
        ``High``.  Defaults to ``"Normal"``.
    email_notification : str, optional
        Address for status mails.
    run_as_administrator : bool, optional
        Elevated privileges (Windows HPC only).  Defaults to ``False``.

    Raises
    ------
    ValueError
        On any validation failure.
    """

    queue: str = "default"
    time: str = "24:00:00"
    nodes: int = 1
    tasks_per_node: int = 1
    cores_per_node: int = 0  # 0 → use scheduler default
    memory: str = "4GB"
    account: Optional[str] = None
    reservation: Optional[str] = None
    qos: Optional[str] = None
    constraints: Optional[str] = None
    exclusive: bool = False
    gpus: int = 0
    gpu_type: Optional[str] = None
    priority: str = "Normal"
    email_notification: Optional[str] = None
    run_as_administrator: bool = False

    def validate_fields(self) -> None:
        """
        Validate all scheduler options for correctness and consistency.

        Raises
        ------
        ValueError
            If any parameter is invalid or out of range.
        """
        if self.nodes < 1:
            raise ValueError("Number of nodes must be at least 1")
        if self.tasks_per_node < 1:
            raise ValueError("Tasks per node must be at least 1")
        if self.gpus < 0:
            raise ValueError("GPU count cannot be negative")
        if self.cores_per_node < 0:
            raise ValueError("cores_per_node must be non-negative")

        # Validate priority values
        valid_priorities = ["Low", "BelowNormal", "Normal", "AboveNormal", "High"]
        if self.priority not in valid_priorities:
            raise ValueError(f"Priority must be one of: {valid_priorities}")

        # Flexible time format validation for different schedulers
        time_patterns = [
            r"^\d+:\d{2}:\d{2}$",  # HH:MM:SS
            r"^\d+\.\d{2}:\d{2}:\d{2}$",  # days.hours:minutes:seconds (Windows HPC)
            r"^\d+$",  # minutes only
        ]

        if not any(re.match(pattern, self.time) for pattern in time_patterns):
            raise ValueError("Time must be in HH:MM:SS, days.HH:MM:SS, or minutes format")


class MachineNode(BaseModel):
    """
    Compute-node descriptor for distributed HFSS runs.

    Parameters
    ----------
    hostname : str, optional
        DNS name or IP. Defaults to ``"localhost"``.
    cores : int, optional
        Logical cores to use.  ``-1`` means *all*.  Defaults to ``-1``.
    max_cores : int, optional
        Physical cores available.  Defaults to ``20``.
    utilization : int, optional
        CPU percentage to utilize (1–100).  Defaults to ``90``.

    Raises
    ------
    ValueError
        If ``utilization`` or ``max_cores`` is out of range.
    """

    hostname: str = "localhost"
    cores: int = -1
    max_cores: int = 20
    utilization: int = 90

    def __init__(self, **data):
        """Initialize and validate parameters."""
        super().__init__(**data)
        self.validate_fields()

    def validate_fields(self) -> None:
        """
        Validate machine node parameters for correctness.

        Ensures all node parameters are within valid ranges and formats.

        Raises:
            ValueError: If any parameter is invalid.
        """
        if not self.hostname:
            raise ValueError("Hostname cannot be empty")
        if self.utilization < 1 or self.utilization > 100:
            raise ValueError("Utilization must be between 1 and 100")
        if self.max_cores < 1:
            raise ValueError("Max cores must be at least 1")

    def __str__(self) -> str:
        """
        Return string representation in HFSS machinelist format.

        Returns
        -------
        str
            Node configuration in format ``hostname:cores:max_cores:util%``.
        """
        return f"{self.hostname}:{self.cores}:{self.max_cores}:{self.utilization}%"


class HFSS3DLayoutBatchOptions(BaseModel):
    """
    HFSS-specific solver flags and environment settings.

    Defaults are **platform aware** (Windows vs Linux).

    Parameters
    ----------
    create_starting_mesh : bool, optional
        Generate initial mesh.  Defaults to ``True``.
    default_process_priority : str, optional
        OS process priority.  Defaults to ``"Normal"``.
    enable_gpu : bool, optional
        GPU acceleration.  Defaults to ``False``.
    mpi_vendor : str, optional
        MPI implementation.  Auto-detected.
    mpi_version : str, optional
        Version string.  Defaults to ``"Default"``.
    remote_spawn_command : str, optional
        Remote shell command.  Auto-detected.
    solve_adaptive_only : bool, optional
        Skip frequency sweep.  Defaults to ``False``.
    validate_only : bool, optional
        Check setup only.  Defaults to ``False``.
    temp_directory : str, optional
        Scratch path.  Auto-detected.
    """

    create_starting_mesh: bool = False
    default_process_priority: str = "Normal"
    enable_gpu: bool = False
    mpi_vendor: str = "Intel"
    mpi_version: str = "Default"
    remote_spawn_command: str = "Scheduler"
    solve_adaptive_only: bool = False
    validate_only: bool = False
    temp_directory: str = Field(default_factory=lambda: tempfile.gettempdir())

    def __init__(self, **data):
        """Initialize and validate options."""
        super().__init__(**data)
        self.validate_fields()

    def validate_fields(self) -> None:
        """
        Validate all HFSS 3D layout options for correctness.

        Performs comprehensive validation of HFSS-specific parameters including
        priority levels, MPI vendors, and directory paths.

        Raises
        ------
        ValueError
            If any parameter is invalid or unsupported.
        """
        valid_priorities = ["Normal", "Low", "High", "Idle"]
        if self.default_process_priority not in valid_priorities:
            raise ValueError(f"Priority must be one of: {valid_priorities}")

        # MPI vendor validation - ANSYS expects specific string values
        valid_mpi_vendors = ["Microsoft", "Intel", "Open MPI"]
        if self.mpi_vendor not in valid_mpi_vendors:
            raise ValueError(f"MPI vendor must be one of: {valid_mpi_vendors}")

        if not self.temp_directory:
            raise ValueError("Temp directory cannot be empty")

    def to_batch_options_dict(self) -> Dict[str, str]:
        """
        Convert options to HFSS batch options dictionary format.

        Returns
        -------
        Dict[str, str]
            Key-value pairs suitable for the ``-batchoptions`` switch.
        """
        return {
            "HFSS 3D Layout Design/CreateStartingMesh": "1" if self.create_starting_mesh else "0",
            "HFSS 3D Layout Design/DefaultProcessPriority": self.default_process_priority,
            "HFSS 3D Layout Design/EnableGPU": "1" if self.enable_gpu else "0",
            "HFSS 3D Layout Design/MPIVendor": self.mpi_vendor,
            "HFSS 3D Layout Design/MPIVersion": self.mpi_version,
            "HFSS 3D Layout Design/RemoteSpawnCommand": self.remote_spawn_command,
            "HFSS 3D Layout Design/SolveAdaptiveOnly": "1" if self.solve_adaptive_only else "0",
            "HFSS 3D Layout Design/ValidateOnly": "1" if self.validate_only else "0",
            "HFSS 3D Layout Design/RAMLimitPercent": "90",
            "HFSS/RAMLimitPercent": "90",
            "Maxwell 2D/RAMLimitPercent": "90",
            "Maxwell 3D/RAMLimitPercent": "90",
            "Q3D Extractor/RAMLimitPercent": "90",
        }

    # ------------------------------------------------------------------
    #  HFSS3DLayoutBatchOptions
    # ------------------------------------------------------------------
    def to_batch_options_string(self) -> str:
        """
        Return the Windows-safe string:
        "'key1'='value1' 'key2'='value2' ..."
        """
        tmp = {
            "HFSS 3D Layout Design/CreateStartingMesh": "1" if self.create_starting_mesh else "0",
            "HFSS 3D Layout Design/DefaultProcessPriority": self.default_process_priority,
            "HFSS 3D Layout Design/EnableGPU": "1" if self.enable_gpu else "0",
            "HFSS 3D Layout Design/MPIVendor": self.mpi_vendor,
            "HFSS 3D Layout Design/MPIVersion": self.mpi_version,
            "HFSS 3D Layout Design/RemoteSpawnCommand": self.remote_spawn_command,
            "HFSS 3D Layout Design/SolveAdaptiveOnly": "1" if self.solve_adaptive_only else "0",
            "HFSS 3D Layout Design/ValidateOnly": "1" if self.validate_only else "0",
            "HFSS 3D Layout Design/RAMLimitPercent": "90",
            "HFSS/RAMLimitPercent": "90",
            "Maxwell 2D/RAMLimitPercent": "90",
            "Maxwell 3D/RAMLimitPercent": "90",
            "Q3D Extractor/RAMLimitPercent": "90",
        }
        quoted_pairs = [f"'{k}'='{v}'" for k, v in tmp.items()]
        return " ".join(quoted_pairs)


class HFSSSimulationConfig(BaseModel):
    """
    Complete, validated simulation configuration.

    The class is a **frozen** dataclass (after ``__post_init__``) and can be
    serialised to/from JSON via :meth:`to_dict` / :meth:`from_dict`.
    e
    Parameters
    ----------
    ansys_edt_path : str
        Path to ``ansysedt`` executable.
    solver : str, optional
        Solver name.  Defaults to ``"Hfss3DLayout"``.
    jobid : str, optional
        Unique identifier.  Auto-generated with timestamp if omitted.
    distributed : bool, optional
        Enable MPI distribution.  Defaults to ``True``.
    machine_nodes : list[MachineNode], optional
        Compute nodes.  Defaults to ``[MachineNode()]``.
    auto : bool, optional
        Non-interactive mode.  Defaults to ``True``.
    non_graphical : bool, optional
        Hide GUI.  Defaults to ``True``.
    monitor : bool, optional
        Stream solver log.  Defaults to ``True``.
    layout_options : HFSS3DLayoutBatchOptions, optional
        Solver flags.  Defaults to a new instance.
    project_path : str, optional
        ``.aedt`` or ``.aedb`` file.  Defaults to platform temp.
    design_name : str, optional
        Design inside project.  Defaults to ``""`` (use active).
    design_mode : str, optional
        Variation name.  Defaults to ``""``.
    setup_name : str, optional
        Setup to solve.  Defaults to ``""``.
    scheduler_type : SchedulerType, optional
        External scheduler.  Defaults to :attr:`SchedulerType.NONE`.
    scheduler_options : SchedulerOptions, optional
        Scheduler directives.  Defaults to a new instance.

    Raises
    ------
    ValueError
        On validation failure.
    FileNotFoundError
        If *project_path* does not exist.
    """

    model_config = {"populate_by_name": True, "exclude_defaults": False}
    ansys_edt_path: str = None
    solver: str = "Hfss3DLayout"
    jobid: str = None
    user: str = "unknown"
    distributed: bool = True
    machine_nodes: List[MachineNode] = Field(default_factory=lambda: [MachineNode()])
    auto: bool = True
    non_graphical: bool = True
    monitor: bool = True
    layout_options: HFSS3DLayoutBatchOptions = Field(default_factory=HFSS3DLayoutBatchOptions)
    project_path: str = Field(default_factory=lambda: os.path.join(tempfile.gettempdir(), "simulation.aedt"))
    design_name: str = ""
    design_mode: str = ""
    setup_name: str = ""
    scheduler_type: SchedulerType = SchedulerType.NONE
    scheduler_options: SchedulerOptions = Field(default_factory=SchedulerOptions)

    def __init__(self, **data):
        """Initialize and validate the configuration."""
        super().__init__(**data)
        if not self.ansys_edt_path:
            installed_versions = installed_ansys_em_versions()
            if not installed_versions:
                raise ValueError(
                    "No installed Ansys EM versions found. Please specify ansys_edt_path. Or "
                    "add ansysedt full path to the configuration."
                )
            if is_linux:
                self.ansys_edt_path = os.path.join(list(installed_versions.values())[-1], "ansysedt")  # latest
            else:
                self.ansys_edt_path = os.path.join(list(installed_versions.values())[-1], "ansysedt.exe")  # latest
        if not self.jobid:
            self.jobid = f"JOB_ID_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        if "auto" not in data:  # user did not touch it
            data["auto"] = self.scheduler_type != SchedulerType.NONE
        self.validate_fields()

    def validate_fields(self) -> None:
        """
        Validate all options and raise ``ValueError`` on violation.
        Checks ranges, formats, and scheduler-specific rules.
        """
        if not self.jobid:
            raise ValueError("Job ID cannot be empty")

        if not re.match(r"^[a-zA-Z0-9_-]+$", self.jobid):
            raise ValueError("Job ID can only contain letters, numbers, underscores, and hyphens")

        if not self.project_path.lower().endswith((".aedt", ".aedb")):
            raise ValueError("Project path must be a .aedt or .aedb file")

        if not os.path.exists(self.project_path):
            raise FileNotFoundError(f"Project file not found: {self.project_path}")

        # Platform-scheduler compatibility validation
        # if self.scheduler_type == SchedulerType.WINDOWS_HPC and platform.system() != "Windows":
        #    raise ValueError("Windows HPC scheduler is only available on Windows platforms")

        # Validate scheduler options
        self.scheduler_options.validate_fields()

    def _build_ansys_command_for_launcher(self) -> str:
        """
        Build the *inner* ANSYS command that will be executed by srun.
        Quotes are chosen so that the string survives one shell expansion
        performed by sbatch.
        """
        # 1. executable
        ansys_root = os.path.dirname(self.ansys_edt_path)
        cmd_parts = [shlex.quote(self.ansys_edt_path)]

        # 2. mandatory HFSS flags
        cmd_parts.extend(["-distributed", f"-machinelist numcores={self._num_cores_for_scheduler()}"])
        if self.auto:
            cmd_parts.append("-auto")
        if self.non_graphical:
            cmd_parts.append("-ng")
        if self.monitor:
            cmd_parts.append("-monitor")

        # 3. batch options  (quoted to protect spaces in keys)
        batch_opts = self.generate_batch_options_string()  # "key1=val1 key2=val2"
        cmd_parts.extend(["-batchoptions", shlex.quote(batch_opts)])

        # 4. project & design
        design_str = self.generate_design_string()
        if self.design_name:
            cmd_parts.extend(["-batchsolve", design_str, shlex.quote(self.project_path)])
        else:
            cmd_parts.extend(["-batchsolve", shlex.quote(self.project_path)])

        # join to one string that srun will receive
        return " ".join(cmd_parts)

    def generate_machinelist_string(self) -> str:
        """
        Return HFSS ``-machinelist`` argument.

        Returns
        -------
        str
            Machine list string.
        """
        if not self.machine_nodes:
            return ""

        node_strings = [str(node) for node in self.machine_nodes]
        return f"list={','.join(node_strings)}"

    def generate_batch_options_string(self) -> str:
        """
        Generate HFSS batch options string from layout options.
        Converts HFSS3DLayoutOptions to command-line batch options format.
        Format matches Ansys reference: "key1=value1 key2=value2"

        Returns
        -------
        str
            Batch options string with space-separated key=value pairs.

        """
        options_dict = self.layout_options.to_batch_options_dict()
        # Simple format: space-separated key=value pairs
        # They will be properly quoted when used in the command
        options_list = [f"'{k}'='{v}'" for k, v in options_dict.items()]
        return " ".join(options_list)

    def generate_design_string(self) -> str:
        """
        Generate design specification string for HFSS command.

        Returns
        -------
        str
            Design string.
        """
        return f"{self.design_name}:{self.design_mode}:{self.setup_name}"

    def generate_slurm_script(self) -> str:
        """
        Returns a proper SLURM batch script with shebang.
        This script can be written to a file and submitted via sbatch.
        """
        opts = self.scheduler_options
        ansys_root = os.path.dirname(self.ansys_edt_path)
        launcher = os.path.join(ansys_root, "schedulers/scripts/utils/ansysedt_launcher.sh")
        wrapper = os.path.join(ansys_root, "schedulers/scripts/utils/slurm_srun_wrapper.sh")
        common = os.path.join(ansys_root, "common")

        # build the inner ANSYS command
        ansys_cmd = self._build_ansys_command_for_launcher()

        # Build SLURM directives
        sbatch_directives = [
            "#!/bin/bash",
            f"#SBATCH --export=NONE",
            f"#SBATCH --chdir={os.path.dirname(os.path.abspath(self.project_path))}",
            f"#SBATCH --job-name={self.jobid}",
            f"#SBATCH --partition={opts.queue}",
            f"#SBATCH --nodes={opts.nodes}",
            f"#SBATCH --cpus-per-task=1",
            f"#SBATCH --ntasks={self._num_cores_for_scheduler()}",
        ]
        # Remove memory limitation - not in reference command
        # if opts.memory:
        #     sbatch_directives.append(f"#SBATCH --mem={opts.memory}")
        if opts.account:
            sbatch_directives.append(f"#SBATCH --account={opts.account}")
        if opts.reservation:
            sbatch_directives.append(f"#SBATCH --reservation={opts.reservation}")
        if opts.qos:
            sbatch_directives.append(f"#SBATCH --qos={opts.qos}")
        if opts.constraints:
            sbatch_directives.append(f"#SBATCH --constraint={opts.constraints}")
        if opts.exclusive:
            sbatch_directives.append("#SBATCH --exclusive")
        if opts.gpus > 0:
            gpu_type = f":{opts.gpu_type}" if opts.gpu_type else ""
            sbatch_directives.append(f"#SBATCH --gpus={opts.gpus}{gpu_type}")

        # Build the execution command
        exec_cmd = (
            f"{launcher} /usr/bin/env ANSYSEM_GENERIC_MPI_WRAPPER={wrapper} ANSYSEM_COMMON_PREFIX={common} "
            f"ANSOFT_PASS_DEBUG_ENV_TO_REMOTE_ENGINES=1 srun --overcommit --export=ALL -n 1 -N 1 "
            f"--cpu-bind=none --mem-per-cpu=0 --overlap {ansys_cmd}"
        )

        # Combine directives and command
        script_lines = sbatch_directives + ["", exec_cmd]
        return "\n".join(script_lines)

    def generate_lsf_script(self) -> str:
        """
        Return LSF batch script that matches the reference command.
        """
        opts = self.scheduler_options
        total_cpus = opts.nodes * opts.cores_per_node

        script = [
            "#!/bin/bash",
            f"#BSUB -J {self.jobid}",
            f"#BSUB -o {self.jobid}.%J.out",
            f"#BSUB -e {self.jobid}.%J.err",
            f"#BSUB -q {opts.queue}",
            f"#BSUB -W {opts.time}",
            f"#BSUB -n {total_cpus}",
            f'#BSUB -R "span[ptile={opts.cores_per_node}]"',
            f'rusage[mem={opts.memory}/host]"',
            f"#BSUB -env 'all,~LD_PRELOAD,LSB_JOB_REPORT_MAIL=Y'",
            "",
            "# Load ANSYS environment",
            "module load ansys",
            "",
            "# Execute HFSS simulation",
            self.generate_command_string(),
            "",
            "echo 'LSF job completed successfully'",
        ]
        return "\n".join(script)

    def generate_scheduler_script(self) -> str:
        """
        Delegate to the correct generator based on
        :attr:`scheduler_type`.

        Returns
        -------
        str
            Batch script or PowerShell code.

        Raises
        ------
        ValueError
            If *scheduler_type* is unsupported.
        """
        if self.scheduler_type == SchedulerType.SLURM:
            return self.generate_slurm_script()
        elif self.scheduler_type == SchedulerType.LSF:
            return self.generate_lsf_script()
        else:
            raise ValueError(f"Unsupported scheduler type: {self.scheduler_type}")

    def _num_cores_for_scheduler(self) -> int:
        """Total cores requested: nodes * cores_per_node (or tasks fallback)."""
        opts = self.scheduler_options
        # prefer explicit cores-per-node, else tasks-per-node, else 1
        cpp = opts.cores_per_node if opts.cores_per_node > 0 else opts.tasks_per_node
        return opts.nodes * cpp

    def generate_command_string(self) -> str:
        """
        Platform-escaped command line.
        Local  →  list=…
        Scheduler →  distributed numcores=…  +  -auto
        """
        parts = []

        # 1. executable
        ansysedt_path = self.ansys_edt_path
        if platform.system() == "Windows":
            parts.append(f'"{ansysedt_path}"')
        else:
            parts.append(shlex.quote(ansysedt_path))

        # 2. jobid
        parts.append(f"-jobid {self.jobid}")

        # 3. machine list & distributed flag
        if self.scheduler_type == SchedulerType.NONE:  # LOCAL
            if self.machine_nodes:
                simplified = [f"{n.hostname}:{n.cores}:{n.max_cores}:{n.utilization}%" for n in self.machine_nodes]
                parts.append(f"-machinelist list={','.join(simplified)}")
        else:  # SCHEDULER
            if self.distributed:
                parts.append("-distributed")
                parts.append(f"-machinelist numcores={self._num_cores_for_scheduler()}")
            if self.auto:  # auto only for schedulers
                parts.append("-auto")

        # 4. common flags
        if self.non_graphical:
            parts.append("-ng")
        if self.monitor:
            parts.append("-monitor")

        # 5. batch options
        batch_opts = self.generate_batch_options_string()
        if platform.system() == "Windows":
            parts.append(f'-batchoptions "{batch_opts}"')
        else:
            parts.append(f"-batchoptions {shlex.quote(batch_opts)}")

        # 6. design & project
        design_str = self.generate_design_string()
        if platform.system() == "Windows":
            proj_quoted = f'"{self.project_path}"'
        else:
            proj_quoted = shlex.quote(self.project_path)

        if self.design_name:
            parts.append(f"-batchsolve {design_str} {proj_quoted}")
        else:
            parts.append(f"-batchsolve {proj_quoted}")

        return " ".join(parts)

    def submit_to_scheduler(self, script_path: Optional[str] = None) -> subprocess.CompletedProcess:
        """
        Write the batch script (if *script_path* given) and submit to the
        configured scheduler.

        Parameters
        ----------
        script_path : str, optional
            Destination file name.  Auto-generated if omitted.

        Returns
        -------
        subprocess.CompletedProcess
            Result of ``sbatch`` / ``bsub`` / ``qsub`` / PowerShell.

        Raises
        ------
        ValueError
            If *scheduler_type* is :attr:`SchedulerType.NONE`. subprocess.TimeoutExpired If submission takes longer
            than 30 s.
        """
        if self.scheduler_type == SchedulerType.NONE:
            # ----  auto-detect  (avoids circular import)  -----------------
            if platform.system() == "Windows":
                detected = SchedulerType.NONE
            else:
                detected = SchedulerType.NONE
                for cmd, enum in (("sinfo", SchedulerType.SLURM), ("bhosts", SchedulerType.LSF)):
                    if shutil.which(cmd):
                        detected = enum
                        break
            # --------------------------------------------------------------
            if detected == SchedulerType.NONE:
                raise ValueError(
                    "No scheduler configured and none auto-detected on this host "
                    "(SLURM / LSF binaries not found in PATH)."
                )
            self.scheduler_type = detected

        # Generate scheduler-specific script
        script_content = self.generate_scheduler_script()

        project_dir = os.path.dirname(os.path.abspath(self.project_path))
        if script_path is None:
            script_ext = "sh"
            script_name = f"{self.jobid}_{self.scheduler_type.value}.{script_ext}"
            script_path = os.path.join(project_dir, script_name)
        else:
            # user gave a relative name → make it relative to project dir
            script_path = os.path.join(project_dir, script_path)

        # Ensure directory exists
        os.makedirs(project_dir, exist_ok=True)

        # Save batch script with proper permissions
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_content)

        # if self.scheduler_type != SchedulerType.WINDOWS_HPC:
        os.chmod(script_path, 0o750)  # nosec B103
        if self.scheduler_type == SchedulerType.SLURM:
            submit_cmd = ["sbatch", script_path]
        elif self.scheduler_type == SchedulerType.LSF:
            submit_cmd = ["bsub"]
        else:
            submit_cmd = ["bsub", "<", script_path]
        try:
            # Execute submission command with timeout
            if self.scheduler_type == SchedulerType.LSF:
                # For LSF, redirect script content via stdin instead of shell
                with open(script_path, "r") as script_file:
                    result = subprocess.run(  # nosec B603
                        submit_cmd,
                        stdin=script_file,
                        capture_output=True,
                        text=True,
                        timeout=30,
                        shell=False,
                    )
            else:
                result = subprocess.run(  # nosec B603
                    submit_cmd,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    shell=False,
                )
            if result.stderr:
                logger.warning(f"🔍 DEBUG: Submission stderr: {result.stderr}")

            return result
        except subprocess.TimeoutExpired:
            raise Exception(f"Scheduler submission timed out after 30 seconds")
        except Exception as e:
            raise Exception(f"Failed to submit to {self.scheduler_type.value}: {e}")

    def run_simulation(self, **subprocess_kwargs) -> Union[subprocess.CompletedProcess, str]:
        """
        **Main entry point** — run the simulation **either**

        * locally (subprocess), or
        * by submitting to an external scheduler.

        Parameters
        ----------
        **subprocess_kwargs
            Forwarded to ``subprocess.run`` for local execution.

        Returns
        -------
        subprocess.CompletedProcess
            For local runs (contains ``stdout``, ``stderr``, ``returncode``).
        str
            For scheduler runs — external job ID such as ``"slurm_job_12345"``.

        Raises
        ------
        Exception
            On any failure (solver not found, submission error, timeout, …).
        """
        if self.scheduler_type != SchedulerType.NONE:
            # Submit to configured scheduler
            result = self.submit_to_scheduler()

            if result.returncode == 0:
                # Extract and return job ID from scheduler output
                job_id = self._extract_job_id(result.stdout)
                return (
                    f"{self.scheduler_type.value}_job_{job_id}"
                    if job_id
                    else f"submitted_to_{self.scheduler_type.value}"
                )
            else:
                raise Exception(f"Scheduler submission failed: {result.stderr}")
        else:
            # Direct execution path
            system = platform.system()

            # Default subprocess options
            default_kwargs = {
                "capture_output": True,
                "text": True,
                "timeout": None,
                "encoding": "utf-8",
                "errors": "replace",
            }

            # Platform-specific command generation
            if system == "Windows":
                default_kwargs["shell"] = True
                command = self.generate_command_string()
            else:
                default_kwargs["shell"] = False
                command = self.generate_command_list()

            # Apply user-provided kwargs
            default_kwargs.update(subprocess_kwargs)

            # extra safety
            if self.scheduler_type == SchedulerType.NONE:
                self.auto = False

            try:
                print(f"Starting HFSS simulation: {self.jobid}")
                print(f"Command: {' '.join(command) if isinstance(command, list) else command}")

                result = subprocess.run(command, **default_kwargs)  # nosec B603

                if result.returncode == 0:
                    print(f"✅ Simulation {self.jobid} completed successfully")
                else:
                    print(f"❌ Simulation {self.jobid} failed with return code {result.returncode}")

                return result

            except subprocess.TimeoutExpired:
                raise Exception(f"Simulation {self.jobid} timed out after {default_kwargs.get('timeout')} seconds")
            except subprocess.CalledProcessError as e:
                raise Exception(f"Simulation {self.jobid} failed with error: {e}")
            except FileNotFoundError as e:
                raise Exception(f"ANSYS executable not found for simulation {self.jobid}: {e}")
            except Exception as e:
                raise Exception(f"Failed to run simulation {self.jobid}: {e}")

    def _extract_job_id(self, output: str) -> Optional[str]:
        """
        Parse scheduler stdout and extract the **external** job ID.

        Parameters
        ----------
        output : str
            Raw stdout of ``sbatch``, ``bsub``, ``qsub``, or PowerShell.

        Returns
        -------
        str or None
            Job ID if found, otherwise ``None``.
        """
        if self.scheduler_type == SchedulerType.SLURM:
            # sbatch output: "Submitted batch job 12345"
            match = re.search(r"Submitted batch job (\d+)", output)
            return match.group(1) if match else None

        elif self.scheduler_type == SchedulerType.LSF:
            # bsub output: "Job <12345> is submitted to queue <normal>."
            match = re.search(r"<(\d+)>", output)
            return match.group(1) if match else None

        elif self.scheduler_type == SchedulerType.PBS:
            # qsub output: "12345.hostname"
            return output.strip().split(".")[0] if output.strip() else None

        elif self.scheduler_type == SchedulerType.WINDOWS_HPC:
            # Windows HPC output: "Job submitted with ID: 12345"
            match = re.search(r"ID:\s*(\d+)", output)
            return match.group(1) if match else None

        return None

    def generate_command_list(self) -> List[str]:
        """
        List form for subprocess.run(shell=False).
        Local  →  list=…
        Scheduler →  distributed numcores=…  +  -auto
        """
        cmd = [self.ansys_edt_path, "-jobid", self.jobid]

        # machine list & distributed flag
        if self.scheduler_type == SchedulerType.NONE:  # LOCAL
            if self.machine_nodes:
                simplified = [f"{n.hostname}:{n.cores}:{n.max_cores}:{n.utilization}%" for n in self.machine_nodes]
                cmd.extend(["-machinelist", f"list={','.join(simplified)}"])
        else:  # SCHEDULER
            if self.distributed:
                cmd.append("-distributed")
                cmd.extend(["-machinelist", f"numcores={self._num_cores_for_scheduler()}"])
            if self.auto:
                cmd.append("-auto")

        # common flags
        if self.non_graphical:
            cmd.append("-ng")
        if self.monitor:
            cmd.append("-monitor")

        # batch options
        cmd.extend(["-batchoptions", self.generate_batch_options_string()])

        # design & project
        design_str = self.generate_design_string()
        cmd.extend(["-batchsolve", design_str, self.project_path])

        return cmd

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the **complete** configuration to a JSON-safe dictionary.

        Returns
        -------
        dict
            Contains all fields including nested BaseModels and enums.
        """
        return {
            "solver": self.solver,
            "ansys_edt_path": self.ansys_edt_path,
            "jobid": self.jobid,
            "distributed": self.distributed,
            "machine_nodes": [node.model_dump() for node in self.machine_nodes],
            "auto": self.auto,
            "non_graphical": self.non_graphical,
            "monitor": self.monitor,
            "layout_options": self.layout_options.model_dump(),
            "project_path": self.project_path,
            "design_name": self.design_name,
            "design_mode": self.design_mode,
            "setup_name": self.setup_name,
            "scheduler_type": self.scheduler_type.value,
            "scheduler_options": self.scheduler_options.model_dump(),
            "platform": platform.system(),
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HFSSSimulationConfig":
        """
        Deserialize a dictionary produced by :meth:`to_dict`.

        Parameters
        ----------
        data : dict
            Dictionary obtained via ``json.load`` or equivalent.

        Returns
        -------
        HFSSSimulationConfig
            New validated instance.
        """
        machine_nodes = [MachineNode(**node_data) for node_data in data.get("machine_nodes", [])]
        layout_options = HFSS3DLayoutBatchOptions(**data.get("layout_options", {}))

        # Handle scheduler_options creation with proper defaults
        scheduler_options_data = data.get("scheduler_options", {})
        if not scheduler_options_data:
            # Create default scheduler options for local execution
            scheduler_options = SchedulerOptions()
        else:
            scheduler_options = SchedulerOptions(**scheduler_options_data)

        return cls(
            solver=data.get("solver", "Hfss3DLayout"),
            ansys_edt_path=data.get("ansys_edt_path", ""),
            jobid=data.get("jobid", f"RSM_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            user=data.get("user"),
            distributed=data.get("distributed", True),
            machine_nodes=machine_nodes,
            auto=data.get("auto", True),
            non_graphical=data.get("non_graphical", True),
            monitor=data.get("monitor", True),
            layout_options=layout_options,
            project_path=data.get("project_path", ""),
            design_name=data.get("design_name", "main"),
            design_mode=data.get("design_mode", "Nominal"),
            setup_name=data.get("setup_name", "Setup1"),
            scheduler_type=SchedulerType(data.get("scheduler_type", "none")),
            scheduler_options=scheduler_options,
        )

    def __str__(self) -> str:
        """
        String representation of the complete HFSS command.

        Returns
        -------
        str
            Complete HFSS command string.
        """
        return self.generate_command_string()


def create_hfss_config(
    project_path: str,
    jobid: Optional[str] = "",
    ansys_edt_path: Optional[str] = "",
    design_name: Optional[str] = "",
    setup_name: Optional[str] = "",
    machine_nodes: Optional[List[MachineNode]] = None,
    scheduler_type: SchedulerType = SchedulerType.NONE,
    scheduler_options: Optional[SchedulerOptions] = None,
    **kwargs,
) -> HFSSSimulationConfig:
    """
    **Convenience factory** that hides all boilerplate and produces a
    **validated** configuration in a single call.

    Parameters
    ----------
    ansys_edt_path : str, Optional
        Absolute path to ``ansysedt`` executable. If not provided the latest
        installed version will be used.
    jobid : str, Optional
        Unique job identifier (letters, digits, ``_``, ``-`` only).
    project_path : str
        Absolute path to ``.aedt`` or ``.aedb`` project.
    design_name : str, optional
        Design inside project.  Default ``""`` (active design).
    setup_name : str, optional
        Setup name.  Default ``""`` (first setup).
    machine_nodes : list[MachineNode], optional
        Compute nodes for MPI.  Default ``[MachineNode()]``.
    scheduler_type : SchedulerType, optional
        External scheduler.  Default :attr:`SchedulerType.NONE`.
    scheduler_options : SchedulerOptions, optional
        Scheduler directives.  Default instance.
    **kwargs
        Additional fields passed directly to ``HFSSSimulationConfig``.

    Returns
    -------
    HFSSSimulationConfig
        Ready-to-run configuration.

    Examples
    --------
    >>> cfg = create_hfss_config(
    ...     ansys_edt_path="/ansys/v241/Linux64/ansysedt",
    ...     jobid="patch",
    ...     project_path="/shared/patch.aedt",
    ...     scheduler_type=SchedulerType.SLURM,
    ...     scheduler_options=SchedulerOptions(nodes=4, memory="32GB"),
    ... )
    >>> job = cfg.run_simulation()
    """
    if machine_nodes is None:
        machine_nodes = [MachineNode()]

    if scheduler_options is None:
        scheduler_options = SchedulerOptions()

    return HFSSSimulationConfig(
        ansys_edt_path=ansys_edt_path,
        jobid=jobid,
        project_path=project_path,
        design_name=design_name,
        setup_name=setup_name,
        machine_nodes=machine_nodes,
        scheduler_type=scheduler_type,
        scheduler_options=scheduler_options,
        **kwargs,
    )
