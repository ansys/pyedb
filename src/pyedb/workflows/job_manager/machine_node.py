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
