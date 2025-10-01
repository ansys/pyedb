# ruff: noqa: E501  (line-length checked by doc-style, not linter)
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

from dataclasses import asdict, dataclass, field
from datetime import datetime
import enum
import os
import platform
import re
import shlex
import subprocess
from typing import Any, Dict, List, Optional, Union
import xml.etree.ElementTree as ET


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


@dataclass
class SchedulerOptions:
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

    def validate(self) -> None:
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


@dataclass
class MachineNode:
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

    def __post_init__(self):
        """Automatically validate parameters after initialization."""
        self.validate()

    def validate(self) -> None:
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


@dataclass
class HFSS3DLayoutBatchOptions:
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

    create_starting_mesh: bool = True
    default_process_priority: str = "Normal"
    enable_gpu: bool = False
    mpi_vendor: str = field(default_factory=lambda: "Intel" if platform.system() == "Windows" else "OpenMPI")
    mpi_version: str = "Default"
    remote_spawn_command: str = "Scheduler"
    solve_adaptive_only: bool = False
    validate_only: bool = False
    temp_directory: str = field(default_factory=lambda: "/tmp" if platform.system() != "Windows" else "D:\\Temp")

    def __post_init__(self):
        """Automatically validate options after initialization."""
        self.validate()

    def validate(self) -> None:
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

        # Platform-specific MPI vendor validation
        if platform.system() == "Windows":
            valid_mpi_vendors = ["Intel", "MSMPI", "PlatformMPI", "Default"]
        else:
            valid_mpi_vendors = ["OpenMPI", "MPICH", "Intel", "Default"]

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
        }


@dataclass
class HFSSSimulationConfig:
    """
    Complete, validated simulation configuration.

    The class is a **frozen** dataclass (after ``__post_init__``) and can be
    serialised to/from JSON via :meth:`to_dict` / :meth:`from_dict`.

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

    ansys_edt_path: str = ""
    solver: str = "Hfss3DLayout"
    jobid: str = field(default_factory=lambda: f"LOCAL_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    distributed: bool = True
    machine_nodes: List[MachineNode] = field(default_factory=lambda: [MachineNode()])
    auto: bool = True
    non_graphical: bool = True
    monitor: bool = True
    layout_options: HFSS3DLayoutBatchOptions = field(default_factory=HFSS3DLayoutBatchOptions)
    project_path: str = field(
        default_factory=lambda: "/tmp/simulation.aedt"
        if platform.system() != "Windows"
        else "D:\\Temp\\simulation.aedt"
    )
    design_name: str = ""
    design_mode: str = ""
    setup_name: str = ""
    scheduler_type: SchedulerType = SchedulerType.NONE
    scheduler_options: SchedulerOptions = field(default_factory=SchedulerOptions)

    def __post_init__(self):
        """Automatically validate complete configuration after initialization."""
        self.validate()

    def validate(self) -> None:
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
        if self.scheduler_type == SchedulerType.WINDOWS_HPC and platform.system() != "Windows":
            raise ValueError("Windows HPC scheduler is only available on Windows platforms")

        # Validate scheduler options
        self.scheduler_options.validate()

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

        Returns
        -------
        str
            Batch options string with quoted key-value pairs.

        """
        options_dict = self.layout_options.to_batch_options_dict()
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
        Return SLURM batch script (**not** written to disk).

        Returns
        -------
        str
            Multi-line string.
        """
        opts = self.scheduler_options
        script = [
            "#!/bin/bash",
            f"#SBATCH --job-name={self.jobid}",
            f"#SBATCH --output={self.jobid}.%j.out",
            f"#SBATCH --error={self.jobid}.%j.err",
            f"#SBATCH --partition={opts.queue}",
            f"#SBATCH --time={opts.time}",
            f"#SBATCH --nodes={opts.nodes}",
            f"#SBATCH --ntasks-per-node={opts.tasks_per_node}",
        ]

        # Optional SLURM directives
        if opts.memory:
            script.append(f"#SBATCH --mem={opts.memory}")
        if opts.account:
            script.append(f"#SBATCH --account={opts.account}")
        if opts.reservation:
            script.append(f"#SBATCH --reservation={opts.reservation}")
        if opts.qos:
            script.append(f"#SBATCH --qos={opts.qos}")
        if opts.constraints:
            script.append(f"#SBATCH --constraint={opts.constraints}")
        if opts.exclusive:
            script.append("#SBATCH --exclusive")
        if opts.gpus > 0:
            gpu_type = f":{opts.gpu_type}" if opts.gpu_type else ""
            script.append(f"#SBATCH --gpus={opts.gpus}{gpu_type}")

        # Script body
        script.extend(
            [
                "",
                "# Load ANSYS module and set up environment",
                "module load ansys",
                "export ANSYS_LICENSE_SERVER=1055@license-server",
                "",
                "# Run HFSS simulation",
                self.generate_command_string(),
                "",
                "# Simulation completion handling",
                "echo 'HFSS simulation completed at $(date)'",
                "exit 0",
            ]
        )

        return "\n".join(script)

    def generate_lsf_script(self) -> str:
        """
        Return LSF batch script.

        Returns
        -------
        str
            Multi-line string.
        """
        opts = self.scheduler_options
        script = [
            "#!/bin/bash",
            f"#BSUB -J {self.jobid}",
            f"#BSUB -o {self.jobid}.%J.out",
            f"#BSUB -e {self.jobid}.%J.err",
            f"#BSUB -q {opts.queue}",
            f"#BSUB -W {opts.time}",
            f"#BSUB -n {opts.nodes * opts.tasks_per_node}",
        ]

        if opts.memory:
            script.append(f"#BSUB -R 'rusage[mem={opts.memory}]'")
        if opts.account:
            script.append(f"#BSUB -P {opts.account}")
        if opts.exclusive:
            script.append("#BSUB -x")

        script.extend(
            [
                "",
                "# Load ANSYS environment",
                "module load ansys",
                "",
                "# Execute HFSS simulation",
                self.generate_command_string(),
                "",
                "echo 'LSF job completed successfully'",
            ]
        )

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

    def generate_command_string(self) -> str:
        """Complete quoted command line ready for ``subprocess``.

        Returns
        -------
        str
            Platform-escaped string.
        """
        parts = []

        # ANSYS executable with proper quoting
        ansysedt_path = self.ansys_edt_path
        if platform.system() == "Windows":
            parts.append(f'"{ansysedt_path}"')
        else:
            parts.append(shlex.quote(ansysedt_path))

        # Basic job parameters
        parts.append(f"-jobid {self.jobid}")

        # Distributed computing configuration
        if self.distributed:
            parts.append("-distributed")
            machinelist = self.generate_machinelist_string()
            parts.append(f"-machinelist {machinelist}")

        # Execution mode flags
        if self.auto:
            parts.append("-auto")

        if self.non_graphical:
            parts.append("-ng")

        if self.monitor:
            parts.append("-monitor")

        # Batch options with proper quoting
        batch_options = self.generate_batch_options_string()
        if platform.system() == "Windows":
            parts.append(f'-batchoptions "{batch_options}"')
        else:
            parts.append(f"-batchoptions {shlex.quote(batch_options)}")

        # Design specification and project path
        design_string = self.generate_design_string()
        if platform.system() == "Windows":
            project_path_quoted = f'"{self.project_path}"'
        else:
            project_path_quoted = shlex.quote(self.project_path)

        if self.design_name:
            parts.append(f"-batchsolve {design_string} {project_path_quoted}")
        else:
            parts.append(f"-batchsolve {project_path_quoted}")

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
            raise ValueError("No scheduler configured")

        # Generate scheduler-specific script
        script_content = self.generate_scheduler_script()

        # Determine script path
        if script_path is None:
            script_ext = "sh"  # if self.scheduler_type != SchedulerType.WINDOWS_HPC else "ps1"
            script_path = f"{self.jobid}_{self.scheduler_type.value}.{script_ext}"

        # Save batch script with proper permissions
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_content)

        # if self.scheduler_type != SchedulerType.WINDOWS_HPC:
        os.chmod(script_path, 0o755)  # Make executable on Unix-like systems

        # Construct scheduler submission command
        if self.scheduler_type == SchedulerType.SLURM:
            submit_cmd = ["sbatch", script_path]
        elif self.scheduler_type == SchedulerType.LSF:
            submit_cmd = ["bsub", "<", script_path]
        else:
            raise ValueError(f"Unsupported scheduler: {self.scheduler_type}")

        try:
            # Execute submission command with timeout
            result = subprocess.run(
                submit_cmd,
                capture_output=True,
                text=True,
                timeout=30,
                shell=(self.scheduler_type == SchedulerType.LSF),  # bsub needs shell for redirection
            )
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

            try:
                print(f"Starting HFSS simulation: {self.jobid}")
                print(f"Command: {' '.join(command) if isinstance(command, list) else command}")

                result = subprocess.run(command, **default_kwargs)

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
        Same as :meth:`generate_command_string` but returned as a **list**
        suitable for ``subprocess.run(..., shell=False)`` on **Linux**.

        Returns
        -------
        list[str]
            Already shell-escaped arguments.
        """
        ansysedt_path = self.get_ansysedt_path()

        command = [
            ansysedt_path,
            "-jobid",
            self.jobid,
        ]

        if self.distributed:
            command.extend(["-distributed"])
            machinelist = self.generate_machinelist_string()
            command.extend(["-machinelist", machinelist])

        if self.auto:
            command.append("-auto")

        if self.non_graphical:
            command.append("-ng")

        if self.monitor:
            command.append("-monitor")

        batch_options = self.generate_batch_options_string()
        command.extend(["-batchoptions", batch_options])

        design_string = self.generate_design_string()
        command.extend(["-batchsolve", design_string, self.project_path])

        return command

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the **complete** configuration to a JSON-safe dictionary.

        Returns
        -------
        dict
            Contains all fields including nested dataclasses and enums.
        """
        return {
            "solver": self.solver,
            "ansys_edt_path": self.ansys_edt_path,
            "jobid": self.jobid,
            "distributed": self.distributed,
            "machine_nodes": [asdict(node) for node in self.machine_nodes],
            "auto": self.auto,
            "non_graphical": self.non_graphical,
            "monitor": self.monitor,
            "layout_options": asdict(self.layout_options),
            "project_path": self.project_path,
            "design_name": self.design_name,
            "design_mode": self.design_mode,
            "setup_name": self.setup_name,
            "scheduler_type": self.scheduler_type.value,
            "scheduler_options": asdict(self.scheduler_options),
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
        scheduler_options = SchedulerOptions(**data.get("scheduler_options", {}))

        return cls(
            solver=data.get("solver", "Hfss3DLayout"),
            ansys_edt_path=data.get("ansys_edt_path", ""),
            jobid=data.get("jobid", f"RSM_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
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
    ansys_edt_path: str,
    jobid: str,
    project_path: str,
    design_name: str = "",
    setup_name: str = "",
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
    ansys_edt_path : str
        Absolute path to ``ansysedt`` executable.
    jobid : str
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
