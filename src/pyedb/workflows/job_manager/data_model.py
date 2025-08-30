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
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, Optional


class SimulationStatus(Enum):
    """
    Canonical simulation life-cycle states.

    Members
    -------
    PENDING : `str`
        Task is waiting in the priority queue.
    RUNNING : `str`
        Task is currently being executed.
    COMPLETED : `str`
        Task finished successfully.
    FAILED : `str`
        Task finished with an error.
    CANCELLED : `str`
        Task was explicitly cancelled by the user.
    """

    PENDING = "Pending"
    RUNNING = "Running"
    COMPLETED = "Completed"
    FAILED = "Failed"
    CANCELLED = "Cancelled"


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


@dataclass
class SimulationTask:
    """
    A single simulation job managed by the queue.

    Attributes
    ----------
    task_id : str
        Globally unique identifier.
    project_name : str
        Human-readable project or design name.
    solver_config : Dict[str, Any]
        Arbitrary JSON-serialisable solver parameters.
    resource_reqs : ResourceRequirements
        Resource constraints and hints.
    priority : int, range 1-10, default 1
        10 = highest priority.
    status : SimulationStatus, default PENDING
        Current life-cycle stage.
    start_time : datetime | None
        UTC timestamp when the task entered RUNNING state.
    end_time : datetime | None
        UTC timestamp when the task finished (any terminal state).
    result : Any | None
        JSON-serialisable return value produced by the solver.
    error_message : str | None
        Populated when `status == FAILED`.
    callback : Callable[[str, Any, BaseException | None], None] | None
        Optional user callback invoked on completion/failure.
    process_id : int | None
        PID of the external solver process (if applicable).
    progress : float, 0-100
        Percentage reported by the solver.
    estimated_time_remaining : float | None
        Seconds left, computed from linear extrapolation.
    created_time : datetime
        UTC timestamp when the task was submitted.
    actual_cores_used : int | None
        Cores really granted by the scheduler.
    peak_memory_used_gb : float | None
        Maximum RSS observed during execution (GiB).
    solver_type : str, default "hfss"
        Identifier for the solver flavour (e.g. "hfss", "mechanical", "q3d").

    Methods
    -------
    to_dict() -> Dict[str, Any]
        Serialise task to a JSON-compatible dict.
    from_dict(data) -> SimulationTask
        Re-create task from dict (inverse of `to_dict`).
    """

    task_id: str
    project_name: str
    solver_config: Dict
    resource_reqs: ResourceRequirements
    priority: int = 1  # 1-10, with 10 being highest priority
    status: SimulationStatus = SimulationStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    result: Optional[Any] = None
    error_message: Optional[str] = None
    callback: Optional[Callable] = None
    process_id: Optional[int] = None
    progress: float = 0.0
    estimated_time_remaining: Optional[float] = None  # in seconds
    created_time: datetime = field(default_factory=datetime.now)
    actual_cores_used: Optional[int] = None
    peak_memory_used_gb: Optional[float] = None
    solver_type: str = "hfss"  # hfss, mechanical, etc.

    def to_dict(self) -> Dict:
        """Convert task to dictionary for serialization"""
        return {
            "task_id": self.task_id,
            "project_name": self.project_name,
            "solver_config": self.solver_config,
            "resource_reqs": {
                "min_cores": self.resource_reqs.min_cores,
                "max_cores": self.resource_reqs.max_cores,
                "min_memory_gb": self.resource_reqs.min_memory_gb,
                "estimated_memory_gb": self.resource_reqs.estimated_memory_gb,
                "estimated_duration_min": self.resource_reqs.estimated_duration_min,
            },
            "priority": self.priority,
            "status": self.status.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "result": self.result,
            "error_message": self.error_message,
            "process_id": self.process_id,
            "progress": self.progress,
            "estimated_time_remaining": self.estimated_time_remaining,
            "created_time": self.created_time.isoformat(),
            "actual_cores_used": self.actual_cores_used,
            "peak_memory_used_gb": self.peak_memory_used_gb,
            "solver_type": self.solver_type,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "SimulationTask":
        """Create task from dictionary"""
        resource_reqs = ResourceRequirements(
            min_cores=data["resource_reqs"]["min_cores"],
            max_cores=data["resource_reqs"]["max_cores"],
            min_memory_gb=data["resource_reqs"]["min_memory_gb"],
            estimated_memory_gb=data["resource_reqs"]["estimated_memory_gb"],
            estimated_duration_min=data["resource_reqs"]["estimated_duration_min"],
        )

        task = cls(
            task_id=data["task_id"],
            project_name=data["project_name"],
            solver_config=data["solver_config"],
            resource_reqs=resource_reqs,
            priority=data.get("priority", 1),
            solver_type=data.get("solver_type", "hfss"),
        )
        task.status = SimulationStatus(data["status"])
        task.start_time = datetime.fromisoformat(data["start_time"]) if data["start_time"] else None
        task.end_time = datetime.fromisoformat(data["end_time"]) if data["end_time"] else None
        task.result = data["result"]
        task.error_message = data["error_message"]
        task.process_id = data.get("process_id")
        task.progress = data.get("progress", 0.0)
        task.estimated_time_remaining = data.get("estimated_time_remaining")
        task.created_time = datetime.fromisoformat(data["created_time"]) if data["created_time"] else datetime.now()
        task.actual_cores_used = data.get("actual_cores_used")
        task.peak_memory_used_gb = data.get("peak_memory_used_gb")
        return task
