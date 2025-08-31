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

import enum


class SchedulerType(enum.Enum):
    """
    Enumeration of supported enterprise job schedulers.

    This enum defines all supported job scheduler types for industrial HPC environments.
    Each scheduler type corresponds to specific enterprise-grade job management systems.

    Attributes:
        NONE: Direct execution without scheduler (using local resources)
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
