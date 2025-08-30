import threading
from typing import Dict, Tuple

import psutil

from pyedb.workflows.job_manager.data_model import SimulationTask


class SystemResourceMonitor:
    """Monitors system resources and checks availability"""

    def __init__(self):
        self.lock = threading.RLock()
        self.update_resources()

    def update_resources(self):
        """Update current system resource availability"""
        with self.lock:
            self.total_cores = psutil.cpu_count(logical=False)  # Physical cores
            self.total_memory_gb = psutil.virtual_memory().total / (1024**3)
            self.available_memory_gb = psutil.virtual_memory().available / (1024**3)

    def get_current_usage(self):
        """Get current system resource usage"""
        with self.lock:
            self.update_resources()
            return {
                "total_cores": self.total_cores,
                "total_memory_gb": round(self.total_memory_gb, 1),
                "available_memory_gb": round(self.available_memory_gb, 1),
                "memory_percent_used": round(
                    100 * (self.total_memory_gb - self.available_memory_gb) / self.total_memory_gb, 1
                ),
                "cpu_percent": psutil.cpu_percent(),
            }

    def can_run_task(self, task: SimulationTask, running_tasks: Dict[str, SimulationTask]) -> Tuple[bool, str]:
        """
        Check if there are enough resources to run a task

        Args:
            task: The task to check
            running_tasks: Currently running tasks

        Returns:
            Tuple of (can_run, reason)
        """
        with self.lock:
            self.update_resources()

            # Calculate currently allocated resources
            allocated_cores = 0
            allocated_memory_gb = 0

            for running_task in running_tasks.values():
                if running_task.actual_cores_used:
                    allocated_cores += running_task.actual_cores_used
                else:
                    # Use estimated cores if actual not available yet
                    allocated_cores += running_task.resource_reqs.min_cores

                if running_task.peak_memory_used_gb:
                    allocated_memory_gb += running_task.peak_memory_used_gb
                else:
                    # Use estimated memory if actual not available yet
                    allocated_memory_gb += running_task.resource_reqs.estimated_memory_gb

            # Calculate available resources
            available_cores = self.total_cores - allocated_cores
            available_memory_gb = self.available_memory_gb - allocated_memory_gb

            # Check if we have enough cores
            if task.resource_reqs.min_cores > available_cores:
                return False, f"Insufficient cores: {task.resource_reqs.min_cores} needed, {available_cores} available"

            # Check if we have enough memory
            if task.resource_reqs.min_memory_gb > available_memory_gb:
                return (
                    False,
                    f"Insufficient memory: {task.resource_reqs.min_memory_gb}GB needed,"
                    f" {available_memory_gb:.1f}GB available",
                )

            return True, "Resources available"
