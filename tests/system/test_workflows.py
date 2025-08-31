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

"""Tests related to Edb"""

import os
import time

import pytest

from pyedb.workflows.job_manager.data_model import ResourceRequirements
from pyedb.workflows.job_manager.solver_runner_manager import SolverRunnerManager
from tests.system.base_test_class import BaseTestClass

pytestmark = [pytest.mark.system, pytest.mark.grpc]

ON_CI = os.environ.get("CI", "false").lower() == "true"


class TestClass(BaseTestClass):
    @pytest.fixture(autouse=True)
    def init(self, local_scratch):
        self.local_scratch = local_scratch

    def test_job_manager(self, local_scratch):
        persistence_file = os.path.join(local_scratch.path, "solver_state.json")
        manager = SolverRunnerManager(
            max_workers=2, web_port=5000, working_directory=self.local_scratch.path, persistence_file=persistence_file
        )

        # Define a callback function for task completion
        def simulation_callback(task_id, result, error):
            if error:
                print(f"Task {task_id} failed: {error}")
            else:
                print(f"Task {task_id} completed in {result['simulation_time']}s with {result['cores_used']} cores")
                print(f"Peak memory usage: {result['peak_memory_gb']}GB")

        # Submit various types of simulation tasks
        tasks = [
            {
                "task_id": "hfss_antenna_1",
                "project_name": "5G_Antenna_Design",
                "solver_type": "hfss",
                "solver_config": {"frequency": "28GHz", "iterations": 1000, "precision": "high"},
                "resource_reqs": ResourceRequirements(
                    min_cores=4, max_cores=8, min_memory_gb=16, estimated_memory_gb=32, estimated_duration_min=45
                ),
                "priority": 10,
            },
            {
                "task_id": "mechanical_thermal_1",
                "project_name": "CPU_Heat_Sink",
                "solver_type": "mechanical",
                "solver_config": {"analysis_type": "thermal", "temperature_range": "20-100C"},
                "resource_reqs": ResourceRequirements(
                    min_cores=2, max_cores=4, min_memory_gb=8, estimated_memory_gb=16, estimated_duration_min=30
                ),
                "priority": 8,
            },
            {
                "task_id": "hfss_filter_1",
                "project_name": "Bandpass_Filter",
                "solver_type": "hfss",
                "solver_config": {"frequency": "10GHz", "iterations": 500, "precision": "medium"},
                "resource_reqs": ResourceRequirements(
                    min_cores=2, max_cores=4, min_memory_gb=4, estimated_memory_gb=8, estimated_duration_min=20
                ),
                "priority": 6,
            },
        ]

        for task_config in tasks:
            manager.submit_task(
                task_id=task_config["task_id"],
                project_name=task_config["project_name"],
                solver_config=task_config["solver_config"],
                resource_reqs=task_config["resource_reqs"],
                solver_type=task_config["solver_type"],
                priority=task_config["priority"],
                callback=simulation_callback,
            )

        print("=" * 60)
        print("PyEDB Solver Manager Started")
        print("=" * 60)
        print(f"Web interface: http://localhost:5000")
        print(f"Monitoring {len(tasks)} simulation tasks")
        print("Press Ctrl+C to stop the manager")
        print("=" * 60)

        try:
            # Keep the main thread alive and display periodic updates
            while True:
                time.sleep(10)
                stats = manager.get_stats()
                print(
                    f"\nCurrent status: {stats['running_tasks']} running, "
                    f"{stats['pending_tasks']} pending, "
                    f"{stats['completed_tasks']} completed"
                )
                print(
                    f"Resource usage: {stats['allocated_cores']}/{stats['total_cores']} cores, "
                    f"{stats['allocated_memory_gb']}/{stats['total_memory_gb']} GB memory"
                )

        except KeyboardInterrupt:
            print("\nShutting down solver manager...")
