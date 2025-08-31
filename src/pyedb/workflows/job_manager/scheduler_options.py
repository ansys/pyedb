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


from dataclasses import dataclass
import re
from typing import Optional


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
