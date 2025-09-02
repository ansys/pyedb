"""
HFSS Simulation Configuration Parser and Runner with Enterprise Scheduler Support

This module provides a comprehensive, production-ready solution for configuring,
validating, and executing ANSYS HFSS simulations across Windows and Linux platforms
with support for all major enterprise job schedulers including Windows HPC Server,
SLURM, LSF, and PBS.

The module is designed for industrial and academic HPC environments with features
for resource management, job tracking, error handling, and automation.

Key Features:
- Cross-platform support (Windows & Linux)
- Enterprise scheduler integration (Windows HPC, SLURM, LSF, PBS)
- Comprehensive input validation and error handling
- JSON serialization/deserialization for configuration persistence
- Built-in subprocess execution with timeout management
- Production-ready logging and monitoring capabilities
- GPU and resource management support
- Email notifications and job priority management

Example:
    >>> from pyedb.workflows.job_manager.job_submission import (HFSSSimulationConfig, MachineNode,
    ...                             SchedulerType, SchedulerOptions)
    >>> # Windows HPC configuration
    >>> config = HFSSSimulationConfig(
    ...     jobid="production_simulation_001",
    ...     project_path="C:\\Projects\\antenna_design.aedt",
    ...     scheduler_type=SchedulerType.WINDOWS_HPC,
    ...     scheduler_options=SchedulerOptions(
    ...         queue="gpuNodes",
    ...         time="3.00:00:00",
    ...         nodes=4,
    ...         memory="64GB",
    ...         priority="High"
    ...     )
    ... )
    >>> # Submit to scheduler
    >>> job_id = config.run_simulation()
    >>> print(f"Job submitted with ID: {job_id}")

"""

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
    Enumeration of supported enterprise job schedulers.

    This enum defines all supported job scheduler types for industrial HPC environments.
    Each scheduler type corresponds to specific enterprise-grade job management systems.

    Attributes:
        NONE: Direct execution without scheduler (for development and testing)
        LSF: IBM Platform LSF scheduler - Enterprise workload manager
        SLURM: Simple Linux Utility for Resource Management - Academic and research HPC
        PBS: Portable Batch System (Torque/PBS Pro) - Cross-platform batch system
        WINDOWS_HPC: Microsoft Windows HPC Server - Enterprise Windows scheduler

    Example:
        >>> scheduler = SchedulerType.WINDOWS_HPC
        >>> print(f"Using scheduler: {scheduler.value}")
        Using scheduler: windows_hpc
    """

    NONE = "none"
    LSF = "lsf"
    SLURM = "slurm"
    PBS = "pbs"
    WINDOWS_HPC = "windows_hpc"


@dataclass
class SchedulerOptions:
    """
    Comprehensive configuration options for enterprise job schedulers.

    This class encapsulates all scheduler-specific parameters for resource allocation,
    job prioritization, and execution constraints across different scheduler platforms.

    Attributes:
        queue (str): Queue/partition name for job placement. Default: "default"
        time (str): Maximum walltime in format HH:MM:SS or days.hours:minutes:seconds.
                   Default: "24:00:00" (24 hours)
        nodes (int): Number of compute nodes to request. Default: 1
        tasks_per_node (int): Number of tasks/processes per node. Default: 1
        memory (str): Memory requirement with units (e.g., "4GB", "8G"). Default: "4GB"
        account (Optional[str]): Account/project to charge for resource usage.
        reservation (Optional[str]): Reservation name for guaranteed resources.
        qos (Optional[str]): Quality of Service level for priority scheduling.
        constraints (Optional[str]): Node constraints (e.g., "gpu", "skylake", "ib").
        exclusive (bool): Request exclusive node access. Default: False
        gpus (int): Number of GPUs to request. Default: 0
        gpu_type (Optional[str]): Specific GPU type (e.g., "a100", "v100", "rtx4090").
        priority (str): Job priority level. Valid values: "Low", "BelowNormal", "Normal",
                       "AboveNormal", "High". Default: "Normal"
        email_notification (Optional[str]): Email address for job status notifications.
        run_as_administrator (bool): Run with elevated privileges (Windows HPC). Default: False

    Raises:
        ValueError: If any parameter fails validation checks.

    Example:
        >>> opts = SchedulerOptions(
        ...     queue="gpuPartition",
        ...     time="48:00:00",
        ...     nodes=2,
        ...     gpus=4,
        ...     memory="64GB",
        ...     priority="High",
        ...     email_notification="user@company.com"
        ... )
        >>> opts.validate()
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

        Performs comprehensive validation of all scheduler parameters including
        value ranges, format compliance, and platform-specific constraints.

        Raises:
            ValueError: If any parameter is invalid or out of range.

        Example:
            >>> opts = SchedulerOptions(nodes=0, time="invalid")
            >>> opts.validate()
            ValueError: Number of nodes must be at least 1
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
    Represents a computational node for distributed HFSS simulations.

    This class models individual compute nodes in a distributed simulation environment,
    including resource allocation and utilization parameters.

    Attributes:
        hostname (str): Network hostname or IP address of the compute node.
                       Default: "localhost"
        cores (int): Number of CPU cores to use. -1 indicates all available cores.
                    Default: -1
        max_cores (int): Maximum number of cores that can be used on this node.
                        Default: 20
        utilization (int): CPU utilization percentage (1-100). Default: 90

    Raises:
        ValueError: If parameters fail validation checks.

    Example:
        >>> node = MachineNode("compute-node-1", 16, 32, 80)
        >>> print(node)
        compute-node-1:16:32:80%
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

        Returns:
            str: Node configuration in format "hostname:cores:max_cores:utilization%"

        Example:
            >>> node = MachineNode("node1", 8, 16, 80)
            >>> str(node)
            'node1:8:16:80%'
        """
        return f"{self.hostname}:{self.cores}:{self.max_cores}:{self.utilization}%"


@dataclass
class HFSS3DLayoutBatchOptions:
    """
    HFSS 3D Layout specific simulation options and configuration.

    This class encapsulates all HFSS-specific simulation parameters including
    mesh generation, solver settings, MPI configuration, and resource management.

    Attributes:
        create_starting_mesh (bool): Enable creation of starting mesh. Default: True
        default_process_priority (str): Process priority level. Valid values:
                                       "Normal", "Low", "High", "Idle". Default: "Normal"
        enable_gpu (bool): Enable GPU acceleration for solver. Default: False
        mpi_vendor (str): MPI implementation vendor. Platform-specific defaults:
                         Windows: "Intel", Linux: "OpenMPI". Default: Platform-specific
        mpi_version (str): MPI version specification. Default: "Default"
        remote_spawn_command (str): Remote process spawn command. Platform-specific:
                                   Windows: "SSH", Linux: "ssh". Default: Platform-specific
        solve_adaptive_only (bool): Solve adaptive passes only. Default: True
        validate_only (bool): Validate setup without solving. Default: True
        temp_directory (str): Temporary directory for simulation files.
                             Windows: "D:\\Temp", Linux: "/tmp". Default: Platform-specific

    Raises:
        ValueError: If any parameter fails validation.

    Example:
        >>> options = HFSS3DLayoutBatchOptions(
        ...     enable_gpu=True,
        ...     temp_directory="/scratch/hfss_temp",
        ...     mpi_vendor="Intel"
        ... )
        >>> options.validate()
    """

    create_starting_mesh: bool = True
    default_process_priority: str = "Normal"
    enable_gpu: bool = False
    mpi_vendor: str = field(default_factory=lambda: "Intel" if platform.system() == "Windows" else "OpenMPI")
    mpi_version: str = "Default"
    remote_spawn_command: str = field(default_factory=lambda: "SSH" if platform.system() == "Windows" else "ssh")
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

        Raises:
            ValueError: If any parameter is invalid or unsupported.
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

        Returns:
            Dict[str, str]: Dictionary of HFSS batch options in key-value format.

        Example:
            >>> options = HFSS3DLayoutBatchOptions(enable_gpu=True)
            >>> batch_dict = options.to_batch_options_dict()
            >>> print(batch_dict['HFSS 3D Layout Design/EnableGPU'])
            '1'
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
    Main configuration class for ANSYS HFSS simulations with enterprise scheduler support.

    This comprehensive class manages all aspects of HFSS simulation configuration,
    validation, and execution across multiple platforms and scheduler environments.

    Attributes:
        solver (str): Solver type. Default: "Hfss3DLayout"
        jobid (str): Unique job identifier with auto-generated timestamp.
        distributed (bool): Enable distributed computing. Default: True
        machine_nodes (List[MachineNode]): List of compute nodes for distribution.
        auto (bool): Enable auto mode. Default: True
        non_graphical (bool): Enable non-graphical mode. Default: True
        monitor (bool): Enable job monitoring. Default: True
        layout_options (HFSS3DLayoutBatchOptions): HFSS-specific simulation options.
        project_path (str): Path to .aedt project file.
        design_name (str): Design name within project. Default: "main"
        design_mode (str): Design mode. Default: "Nominal"
        setup_name (str): Setup name. Default: "Setup1"
        scheduler_type (SchedulerType): Job scheduler type. Default: SchedulerType.NONE
        scheduler_options (SchedulerOptions): Scheduler-specific configuration options.

    Raises:
        ValueError: If configuration parameters are invalid.
        FileNotFoundError: If project file or ANSYS executable not found.
        OSError: If unsupported operating system detected.

    Example:
        >>> config = HFSSSimulationConfig(
        ...     jobid="production_sim_001",
        ...     project_path="C:\\Projects\\design.aedt",
        ...     scheduler_type=SchedulerType.WINDOWS_HPC,
        ...     scheduler_options=SchedulerOptions(
        ...         nodes=4,
        ...         memory="64GB",
        ...         priority="High"
        ...     )
        ... )
        >>> result = config.run_simulation()
    """

    ansysedt_path: str = None
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
        Validate complete simulation configuration for production readiness.

        Performs comprehensive validation of all configuration parameters including:
        - Job ID format and uniqueness requirements
        - Project file existence and format validation
        - Design and setup name validation
        - Platform-scheduler compatibility checks
        - Scheduler option validation

        Raises:
            ValueError: If any configuration parameter is invalid.
            FileNotFoundError: If project file does not exist.
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
        Generate machinelist string for distributed computing configuration.

        Converts the list of MachineNode objects into HFSS-compatible machinelist format.

        Returns:
            str: Machinelist string in format "list=node1:cores:max_cores:util%,node2:..."

        Example:
            >>> config.machine_nodes = [MachineNode("node1", 8, 16, 80), MachineNode("node2", 8, 16, 80)]
            >>> machinelist = config.generate_machinelist_string()
            >>> print(machinelist)
            list=node1:8:16:80%,node2:8:16:80%
        """
        if not self.machine_nodes:
            return ""

        node_strings = [str(node) for node in self.machine_nodes]
        return f"list={','.join(node_strings)}"

    def generate_batch_options_string(self) -> str:
        """
        Generate HFSS batch options string from layout options.

        Converts HFSS3DLayoutOptions to command-line batch options format.

        Returns:
            str: Batch options string with quoted key-value pairs.

        Example:
            >>> options_str = config.generate_batch_options_string()
            >>> print(options_str)
            'HFSS 3D Layout Design/CreateStartingMesh'='1' ... 'tempdirectory'='/tmp'
        """
        options_dict = self.layout_options.to_batch_options_dict()
        options_list = [f"'{k}'='{v}'" for k, v in options_dict.items()]
        return " ".join(options_list)

    def generate_design_string(self) -> str:
        """
        Generate design specification string for HFSS command.

        Returns:
            str: Design string in format "design_name:design_mode:setup_name".

        Example:
            >>> design_str = config.generate_design_string()
            >>> print(design_str)
            main:Nominal:Setup1
        """
        return f"{self.design_name}:{self.design_mode}:{self.setup_name}"

    def generate_slurm_script(self) -> str:
        """
        Generate SLURM batch script for job submission.

        Creates a complete SLURM batch script with all necessary directives
        and environment setup for HFSS simulation.

        Returns:
            str: Complete SLURM batch script as multi-line string.

        Example:
            >>> slurm_script = config.generate_slurm_script()
            >>> with open("job.slurm", "w") as f:
            ...     f.write(slurm_script)
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
        Generate LSF batch script for IBM Platform LSF.

        Creates a complete LSF batch script with all necessary directives
        for enterprise workload management.

        Returns:
            str: Complete LSF batch script as multi-line string.
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

    def generate_pbs_script(self) -> str:
        """
        Generate PBS/Torque batch script for job submission.

        Creates a complete PBS batch script for portable batch system environments.

        Returns:
            str: Complete PBS batch script as multi-line string.
        """
        opts = self.scheduler_options
        script = [
            "#!/bin/bash",
            f"#PBS -N {self.jobid}",
            f"#PBS -o {self.jobid}.$PBS_JOBID.out",
            f"#PBS -e {self.jobid}.$PBS_JOBID.err",
            f"#PBS -q {opts.queue}",
            f"#PBS -l walltime={opts.time}",
            f"#PBS -l nodes={opts.nodes}:ppn={opts.tasks_per_node}",
        ]

        if opts.memory:
            script.append(f"#PBS -l mem={opts.memory}")
        if opts.account:
            script.append(f"#PBS -A {opts.account}")

        script.extend(
            [
                "",
                "# Set up ANSYS environment",
                "module load ansys",
                "",
                "# Run simulation",
                self.generate_command_string(),
                "",
                "echo 'PBS job completed'",
            ]
        )

        return "\n".join(script)

    def generate_windows_hpc_script(self) -> str:
        """
        Generate Windows HPC PowerShell script for job submission.

        Creates a PowerShell script that handles Windows HPC job submission,
        monitoring, and cleanup using HPC PowerShell cmdlets.

        Returns:
            str: Complete PowerShell script for Windows HPC.
        """
        opts = self.scheduler_options

        script = [
            "# Windows HPC PowerShell Script for HFSS Simulation",
            "# Generated: " + datetime.now().isoformat(),
            "",
            '$jobName = "' + self.jobid + '"',
            '$command = "' + self.generate_command_string().replace('"', '`"') + '"',
            "",
            "# Create job XML configuration",
            '$xmlContent = @"',
            "<Job>",
            f"  <Name>{self.jobid}</Name>",
            f"  <Priority>{opts.priority}</Priority>",
            "  <JobType>Interactive</JobType>",
            "  <Resources>",
            f"    <MinNodes>{opts.nodes}</MinNodes>",
            f"    <MaxNodes>{opts.nodes}</MaxNodes>",
            f"    <NodeGroups>{opts.queue}</NodeGroups>",
            "  </Resources>",
            "  <Tasks>",
            "    <Task>",
            "      <Name>HFSS_Simulation_Task</Name>",
            '      <CommandLine>cmd /c "$command"</CommandLine>',
            f"      <IsConsole>true</IsConsole>",
            f"      <WorkDirectory>{os.path.dirname(self.project_path)}</WorkDirectory>",
            "      <TaskType>Basic</TaskType>",
            f"      <RequiredNodes>{opts.nodes}</RequiredNodes>",
            "    </Task>",
            "  </Tasks>",
            "</Job>",
            '"@',
            "",
            "# Save XML to temporary file",
            '$xmlFile = [System.IO.Path]::GetTempFileName() + ".xml"',
            "Set-Content -Path $xmlFile -Value $xmlContent -Encoding UTF8",
            "",
            "# Submit job to HPC cluster",
            "try {",
            '    Write-Host "Submitting job to Windows HPC cluster..."',
            "    $job = Submit-HpcJob -File $xmlFile",
            '    Write-Host "Job submitted with ID: $($job.Id)"',
            "    ",
            "    # Monitor job status with progress reporting",
            '    while ($job.State -eq "Configuring" -or $job.State -eq "Submitted" -or $job.State -eq "Running") {',
            "        Start-Sleep -Seconds 30",
            "        $job = Get-HpcJob -Id $job.Id",
            '        Write-Host "Job status: $($job.State)"',
            "    }",
            "    ",
            '    Write-Host "Job completed with final status: $($job.State)"',
            "    ",
            "    # Get job exit code if available",
            "    if ($job.ExitCode) {",
            '        Write-Host "Job exit code: $($job.ExitCode)"',
            "    }",
            "}",
            "catch {",
            '    Write-Error "Failed to submit job: $_"',
            "    exit 1",
            "}",
            "finally {",
            "    # Cleanup temporary files",
            "    if (Test-Path $xmlFile) {",
            "        Remove-Item $xmlFile -Force -ErrorAction SilentlyContinue",
            "    }",
            "}",
            "",
            "exit 0",
        ]

        return "\n".join(script)

    def generate_windows_hpc_xml(self) -> str:
        """
        Generate Windows HPC Job XML configuration file.

        Creates a properly formatted XML job definition file for Windows HPC Server
        with all necessary parameters for resource allocation and job management.

        Returns:
            str: XML content for HPC job submission.

        Example:
            >>> xml_content = config.generate_windows_hpc_xml()
            >>> with open("hpc_job.xml", "w") as f:
            ...     f.write(xml_content)
        """
        opts = self.scheduler_options

        # Create XML structure with proper namespace
        job = ET.Element("Job")
        ET.SubElement(job, "Name").text = self.jobid
        ET.SubElement(job, "Priority").text = opts.priority

        # Email notifications if configured
        if opts.email_notification:
            notifications = ET.SubElement(job, "Notifications")
            notification = ET.SubElement(notifications, "Notification")
            ET.SubElement(notification, "Email").text = opts.email_notification
            ET.SubElement(notification, "Event").text = "JobCompletion"

        # Resource allocation
        resources = ET.SubElement(job, "Resources")
        ET.SubElement(resources, "MinNodes").text = str(opts.nodes)
        ET.SubElement(resources, "MaxNodes").text = str(opts.nodes)
        if opts.queue and opts.queue != "default":
            ET.SubElement(resources, "NodeGroups").text = opts.queue

        # Task definition
        tasks = ET.SubElement(job, "Tasks")
        task = ET.SubElement(tasks, "Task")
        ET.SubElement(task, "Name").text = "HFSS_Simulation_Task"
        ET.SubElement(task, "CommandLine").text = f'cmd /c "{self.generate_command_string()}"'
        ET.SubElement(task, "IsConsole").text = "true"
        ET.SubElement(task, "WorkDirectory").text = os.path.dirname(self.project_path)
        ET.SubElement(task, "TaskType").text = "Basic"
        ET.SubElement(task, "RequiredNodes").text = str(opts.nodes)

        # Administrator privileges if requested
        if opts.run_as_administrator:
            ET.SubElement(task, "RunAsAdministrator").text = "true"

        # Convert to formatted XML string
        ET.indent(job, space="  ")
        return ET.tostring(job, encoding="unicode", method="xml")

    def generate_scheduler_script(self) -> str:
        """
        Generate appropriate scheduler script based on configured scheduler type.

        Returns:
            str: Complete batch script for the configured scheduler.

        Raises:
            ValueError: If unsupported scheduler type is specified.
        """
        if self.scheduler_type == SchedulerType.SLURM:
            return self.generate_slurm_script()
        elif self.scheduler_type == SchedulerType.LSF:
            return self.generate_lsf_script()
        elif self.scheduler_type == SchedulerType.PBS:
            return self.generate_pbs_script()
        elif self.scheduler_type == SchedulerType.WINDOWS_HPC:
            return self.generate_windows_hpc_script()
        else:
            raise ValueError(f"Unsupported scheduler type: {self.scheduler_type}")

    def generate_command_string(self) -> str:
        """
        Generate complete HFSS command string for execution.

        Constructs the full ANSYS HFSS command line with all options, parameters,
        and proper quoting for cross-platform compatibility.

        Returns:
            str: Complete HFSS command string ready for execution.

        Example:
            >>> command = config.generate_command_string()
            >>> print(f"Executing: {command}")
        """
        parts = []

        # ANSYS executable with proper quoting
        ansysedt_path = self.ansysedt_path
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
        Submit job to configured scheduler with proper error handling.

        Args:
            script_path: Optional path to save the generated batch script.
                        If None, uses auto-generated filename.

        Returns:
            subprocess.CompletedProcess: Result of the scheduler submission command.

        Raises:
            ValueError: If no scheduler is configured or invalid parameters.
            Exception: If scheduler submission fails.

        Example:
            >>> result = config.submit_to_scheduler()
            >>> if result.returncode == 0:
            ...     print("Job submitted successfully")
        """
        if self.scheduler_type == SchedulerType.NONE:
            raise ValueError("No scheduler configured")

        # Handle Windows HPC separately due to XML-based submission
        if self.scheduler_type == SchedulerType.WINDOWS_HPC:
            return self.submit_to_windows_hpc()

        # Generate scheduler-specific script
        script_content = self.generate_scheduler_script()

        # Determine script path
        if script_path is None:
            script_ext = "sh" if self.scheduler_type != SchedulerType.WINDOWS_HPC else "ps1"
            script_path = f"{self.jobid}_{self.scheduler_type.value}.{script_ext}"

        # Save batch script with proper permissions
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_content)

        if self.scheduler_type != SchedulerType.WINDOWS_HPC:
            os.chmod(script_path, 0o755)  # Make executable on Unix-like systems

        # Construct scheduler submission command
        if self.scheduler_type == SchedulerType.SLURM:
            submit_cmd = ["sbatch", script_path]
        elif self.scheduler_type == SchedulerType.LSF:
            submit_cmd = ["bsub", "<", script_path]
        elif self.scheduler_type == SchedulerType.PBS:
            submit_cmd = ["qsub", script_path]
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

    def submit_to_windows_hpc(self) -> subprocess.CompletedProcess:
        """
        Submit job to Windows HPC Server using PowerShell.

        Specialized method for Windows HPC job submission using XML job definitions
        and HPC PowerShell cmdlets.

        Returns:
            subprocess.CompletedProcess: Result of PowerShell submission command.

        Raises:
            ValueError: If not running on Windows platform.
            Exception: If HPC submission fails.
        """
        if platform.system() != "Windows":
            raise ValueError("Windows HPC is only available on Windows platforms")

        # Generate XML job definition
        xml_content = self.generate_windows_hpc_xml()
        xml_file = f"{self.jobid}_hpc_job.xml"

        try:
            # Save XML job definition
            with open(xml_file, "w", encoding="utf-8") as f:
                f.write(xml_content)

            # PowerShell script for job submission
            ps_script = f"""
            try {{
                Import-Module HPC -ErrorAction Stop
                $job = Submit-HpcJob -File "{xml_file}"
                Write-Output "Job submitted with ID: $($job.Id)"
                Remove-Item "{xml_file}" -Force -ErrorAction SilentlyContinue
                exit 0
            }}
            catch {{
                Write-Error "Failed to submit job: $_"
                if (Test-Path "{xml_file}") {{
                    Remove-Item "{xml_file}" -Force -ErrorAction SilentlyContinue
                }}
                exit 1
            }}
            """

            # Execute PowerShell submission
            result = subprocess.run(
                ["powershell", "-Command", ps_script], capture_output=True, text=True, timeout=45, encoding="utf-8"
            )
            return result

        except Exception as e:
            # Cleanup on error
            if os.path.exists(xml_file):
                os.remove(xml_file)
            raise Exception(f"Failed to submit to Windows HPC: {e}")

    def run_simulation(self, **subprocess_kwargs) -> Union[subprocess.CompletedProcess, str]:
        """
        Execute HFSS simulation using appropriate method based on configuration.

        This is the primary method for simulation execution. It handles:
        - Scheduler submission (returns job ID)
        - Direct execution (returns subprocess result)
        - Comprehensive error handling and logging

        Args:
            **subprocess_kwargs: Additional arguments for subprocess.run() in direct mode.

        Returns:
            Union[subprocess.CompletedProcess, str]:
                - For scheduler submission: Job ID string
                - For direct execution: subprocess.CompletedProcess object

        Raises:
            Exception: If simulation execution fails with detailed error information.

        Example:
            >>> # Scheduler submission
            >>> job_id = config.run_simulation()
            >>> print(f"Job ID: {job_id}")
            >>>
            >>> # Direct execution
            >>> result = config.run_simulation(timeout=3600)
            >>> print(f"Return code: {result.returncode}")
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
        Extract job ID from scheduler submission output.

        Args:
            output (str): Scheduler command output text.

        Returns:
            Optional[str]: Extracted job ID or None if not found.
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
        Generate command as list for subprocess execution without shell.

        Returns:
            List[str]: Command as list of arguments for subprocess.run().

        Note:
            Preferred for Linux execution for better security and control.
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
        Convert configuration to dictionary for serialization and persistence.

        Returns:
            Dict[str, Any]: Dictionary representation of the complete configuration.

        Example:
            >>> config_dict = config.to_dict()
            >>> with open('config.json', 'w') as f:
            ...     json.dump(config_dict, f, indent=2)
        """
        return {
            "solver": self.solver,
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
        Create configuration instance from dictionary representation.

        Args:
            data (Dict[str, Any]): Dictionary containing serialized configuration data.

        Returns:
            HFSSSimulationConfig: New configuration instance.

        Example:
            >>> with open('config.json', 'r') as f:
            ...     data = json.load(f)
            >>> config = HFSSSimulationConfig.from_dict(data)
        """
        machine_nodes = [MachineNode(**node_data) for node_data in data.get("machine_nodes", [])]
        layout_options = HFSS3DLayoutBatchOptions(**data.get("layout_options", {}))
        scheduler_options = SchedulerOptions(**data.get("scheduler_options", {}))

        return cls(
            solver=data.get("solver", "Hfss3DLayout"),
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

        Returns:
            str: Complete HFSS command string.
        """
        return self.generate_command_string()


def create_hfss_config(
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
    Helper function for quick creation of HFSS simulation configurations.

    This factory function provides a convenient way to create HFSS simulation
    configurations with sensible defaults and reduced boilerplate.

    Args:
        jobid (str): Unique job identifier.
        project_path (str): Path to .aedt project file.
        design_name (str): Design name within project. Default: "main"
        setup_name (str): Setup name. Default: "Setup1"
        machine_nodes (Optional[List[MachineNode]]): List of compute nodes.
        scheduler_type (SchedulerType): Job scheduler type. Default: SchedulerType.NONE
        scheduler_options (Optional[SchedulerOptions]): Scheduler configuration options.
        **kwargs: Additional arguments for HFSSSimulationConfig.

    Returns:
        HFSSSimulationConfig: Configured simulation instance.

    Example:
        >>> config = create_hfss_config(
        ...     jobid="quick_sim",
        ...     project_path="design.aedt",
        ...     scheduler_type=SchedulerType.SLURM,
        ...     scheduler_options=SchedulerOptions(nodes=2, memory="8GB")
        ... )
    """
    if machine_nodes is None:
        machine_nodes = [MachineNode()]

    if scheduler_options is None:
        scheduler_options = SchedulerOptions()

    return HFSSSimulationConfig(
        jobid=jobid,
        project_path=project_path,
        design_name=design_name,
        setup_name=setup_name,
        machine_nodes=machine_nodes,
        scheduler_type=scheduler_type,
        scheduler_options=scheduler_options,
        **kwargs,
    )
