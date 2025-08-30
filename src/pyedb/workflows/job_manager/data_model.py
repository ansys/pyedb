from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, Optional


class SimulationStatus(Enum):
    """Enumeration of possible simulation states"""

    PENDING = "Pending"
    RUNNING = "Running"
    COMPLETED = "Completed"
    FAILED = "Failed"
    CANCELLED = "Cancelled"


@dataclass
class ResourceRequirements:
    """Resource requirements for a simulation task"""

    min_cores: int = 1
    max_cores: int = 1
    min_memory_gb: int = 4
    estimated_memory_gb: int = 8
    estimated_duration_min: int = 30


@dataclass
class SimulationTask:
    """Represents a simulation task with its properties and status"""

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
