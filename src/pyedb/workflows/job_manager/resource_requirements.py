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
class ResourceRequirements:
    """
    Immutable specification of the resources a simulation task needs.

    Attributes
    ----------
    min_cores : int, default 1
        Minimum physical CPU cores required to start the task.
    max_cores : int, default 1
        Upper limit of cores the solver may scale up to (currently not enforced).
    min_memory_gb : int, default 4
        Minimum RAM (in GiB) required to start the task.
    estimated_memory_gb : int, default 8
        Expected peak memory usage for scheduling heuristics.
    estimated_duration_min : int, default 30
        Expected wall-time (in minutes) used for ETA calculations.
    """

    min_cores: int = 1
    max_cores: int = 1
    min_memory_gb: int = 4
    estimated_memory_gb: int = 8
    estimated_duration_min: int = 30
