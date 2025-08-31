# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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

from dataclasses import dataclass, field
import platform
from typing import Dict


@dataclass
class HFSS3DLayoutOptions:
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
        >>> options = HFSS3DLayoutOptions(
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
    solve_adaptive_only: bool = True
    validate_only: bool = True
    temp_directory: str = field(default_factory=lambda: "/tmp" if platform.system() != "Windows" else "D:\\Temp")

    def __post_init__(self):
        """Automatically validate options after initialization."""
        self.validate()

    def validate(self) -> None:
        """
        Validate all HFSS layout options for correctness.

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
            >>> options = HFSS3DLayoutOptions(enable_gpu=True)
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
            "tempdirectory": self.temp_directory,
        }
