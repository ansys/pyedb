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

import time
from typing import Callable, Dict

from pyedb.workflows.job_manager.data_model import SimulationTask
from pyedb.workflows.job_manager.logger import logger


class PyEDBIntegration:
    """Handles actual PyEDB solver integration"""

    @staticmethod
    def run_simulation(task: SimulationTask, callback: Callable[[float, float], None]) -> Dict:
        """
        Run an actual PyEDB simulation

        Args:
            task: The simulation task to run
            callback: Function to call with progress and memory usage updates

        Returns:
            Simulation results

        Raises:
            Exception: If simulation fails
        """
        # This is where the actual PyEDB integration would go
        # For demonstration, we'll simulate the behavior

        try:
            # Import pyedb (commented out for demonstration)
            # import pyedb
            pass
        except ImportError:
            logger.warning("PyEDB not available, using simulation mode")
            return PyEDBIntegration._simulate_solver(task, callback)

        # Actual PyEDB integration would go here
        # For now, we'll use the simulation
        return PyEDBIntegration._simulate_solver(task, callback)

    @staticmethod
    def _simulate_solver(task: SimulationTask, callback: Callable[[float, float], None]) -> Dict:
        """
        Simulate a PyEDB solver for demonstration purposes

        Args:
            task: The simulation task to run
            callback: Function to call with progress and memory usage updates

        Returns:
            Simulation results
        """
        total_steps = 100
        peak_memory = 0
        memory_usage = task.resource_reqs.min_memory_gb

        for step in range(total_steps):
            # Simulate memory usage (peak at 50% progress)
            if step < total_steps / 2:
                memory_usage = task.resource_reqs.min_memory_gb + (
                    task.resource_reqs.estimated_memory_gb - task.resource_reqs.min_memory_gb
                ) * (step / (total_steps / 2))
            else:
                memory_usage = task.resource_reqs.estimated_memory_gb - (
                    task.resource_reqs.estimated_memory_gb - task.resource_reqs.min_memory_gb
                ) * ((step - total_steps / 2) / (total_steps / 2))

            peak_memory = max(peak_memory, memory_usage)

            # Update progress
            progress = (step + 1) / total_steps * 100
            callback(progress, peak_memory)

            # Simulate work
            time.sleep(0.5)

            # Simulate occasional failures
            import random

            if random.random() < 0.02:  # 2% chance of failure
                raise RuntimeError("Simulation failed due to convergence issues")

        # Return simulated results
        return {
            "simulation_time": total_steps * 0.5,
            "cores_used": task.resource_reqs.min_cores,
            "peak_memory_gb": round(peak_memory, 1),
            "max_temperature": 85.3,
            "min_temperature": 22.1,
            "average_temperature": 45.7,
            "message": "Simulation completed successfully",
        }
