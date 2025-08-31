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

import threading
from typing import List

from pyedb.workflows.job_manager.simulation_task import SimulationTask


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
