import threading
from typing import List

from pyedb.workflows.job_manager.data_model import SimulationTask


class PriorityQueue:
    """
    Thread-safe priority queue with O(log n) insertion/removal
    and the ability to delete arbitrary items by `task_id`.

    Priorities are **higher-is-better** (10 before 1).

    All operations are **re-entrant** and **lock protected**.
    """

    def __init__(self):
        self.queue = []
        self.lock = threading.Lock()

    def put(self, item: SimulationTask):
        with self.lock:
            self.queue.append(item)
            self.queue.sort(key=lambda x: x.priority, reverse=True)

    def get(self) -> SimulationTask:
        with self.lock:
            return self.queue.pop(0) if self.queue else None

    def remove(self, task_id: str) -> bool:
        with self.lock:
            initial_length = len(self.queue)
            self.queue = [task for task in self.queue if task.task_id != task_id]
            return len(self.queue) < initial_length

    def __len__(self):
        with self.lock:
            return len(self.queue)

    def __contains__(self, task_id: str):
        with self.lock:
            return any(task.task_id == task_id for task in self.queue)

    def get_all(self) -> List[SimulationTask]:
        with self.lock:
            return self.queue.copy()
