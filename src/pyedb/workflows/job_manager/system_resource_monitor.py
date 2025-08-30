import threading
from typing import Dict, Tuple

import psutil

from pyedb.workflows.job_manager.data_model import SimulationTask


class SystemResourceMonitor:
    """
    Live view of **host-level** CPU and memory usage.

    Uses `psutil` to cache current metrics and provides the
    scheduling predicate `can_run_task`.

    Thread-safe (uses `threading.RLock`).
    """

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
        """
        Returns
        -------
        dict
            total_cores : int
            total_memory_gb : float
            available_memory_gb : float
            memory_percent_used : float
            cpu_percent : float
        """
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
        Decide whether the host can accommodate *one more* task.

        Parameters
        ----------
        task : SimulationTask
            The candidate task.
        running_tasks : dict[str, SimulationTask]
            Snapshot of currently running tasks (values contain allocated cores/memory).

        Returns
        -------
        (can_run, reason): tuple[bool, str]
            `can_run` is `True` only if both core and memory constraints are met;
            `reason` is a human-readable explanation otherwise.
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
