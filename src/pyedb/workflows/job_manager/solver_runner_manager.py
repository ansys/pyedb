from datetime import datetime
import json
import os
import threading
import time
from typing import Any, Callable, Dict, List, Optional
import webbrowser

from flask import Flask, jsonify, render_template, request
import psutil

from pyedb.workflows.job_manager.data_model import (
    ResourceRequirements,
    SimulationStatus,
    SimulationTask,
)
from pyedb.workflows.job_manager.logger import logger
from pyedb.workflows.job_manager.priority_queue import PriorityQueue
from pyedb.workflows.job_manager.pyedb_integration import PyEDBIntegration
from pyedb.workflows.job_manager.system_resource_monitor import SystemResourceMonitor


class SolverRunnerManager:
    """
    # PyEDB Solver Manager

    A **lightweight, production-ready task queue** for running Ansys Electronics Desktop
    (PyEDB) or any other solver processes **locally** with:

    * **Resource-aware scheduling** (CPU cores, RAM)
    * **Priority queue**
    * **Persistent state** (auto-restore after restarts)
    * **REST-style web dashboard**
    * **Thread-safe** design

    ## Quick start

    ```python
    from solver_manager import SolverRunnerManager, ResourceRequirements

    with SolverRunnerManager(max_workers=2, persistence_file="state.json") as mgr:
        mgr.submit_task(
            task_id="antenna_1",
            project_name="5G_Antenna",
            solver_type="hfss",
            solver_config={"freq": "28 GHz"},
            resource_reqs=ResourceRequirements(min_cores=4, min_memory_gb=16),
            priority=10
        )
    Open http://localhost:5000 in your browser to monitor tasks.
    """

    def __init__(
        self,
        max_workers: int = 1,
        persistence_file: Optional[str] = None,
        web_interface: bool = True,
        web_port: int = 5000,
    ):
        """
        Central orchestrator that **owns** the queues, workers, web UI
        and persistence layer.

        Context-manager safe (`__enter__`, `__exit__`) – resources are
        gracefully released on exit.

        Parameters
        ----------
        max_workers : int, default 1
            Number of **concurrent** solver threads (not processes) to run.
        persistence_file : str | None, optional
            Path to a JSON file for crash-recovery. Directory is auto-created.
        web_interface : bool, default True
            Spawn Flask dashboard on `http://0.0.0.0:<web_port>`.
        web_port : int, default 5000
            Port for the dashboard.

        Example
        -------
        ```python
        with SolverRunnerManager(max_workers=4, persistence_file="state.json") as mgr:
            mgr.submit_task(...)
            # Web UI automatically opens in default browser
        ```
        """
        self.max_workers = max_workers
        self.persistence_file = persistence_file

        # Task queues
        self.pending_queue = PriorityQueue()
        self.running_tasks: Dict[str, SimulationTask] = {}
        self.completed_tasks: Dict[str, SimulationTask] = {}

        # Resource monitoring
        self.resource_monitor = SystemResourceMonitor()

        # Worker management
        self.workers: List[threading.Thread] = []
        self.is_running = False
        self.lock = threading.RLock()

        # Web interface
        self.web_interface = None
        self.web_port = web_port
        if web_interface:
            self._start_web_interface()

        # Statistics
        self.stats = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "tasks_cancelled": 0,
            "total_cpu_time": 0.0,
            "total_memory_hours": 0.0,
            "start_time": datetime.now(),
        }

        # Load previous state if persistence is enabled
        if self.persistence_file and os.path.exists(self.persistence_file):
            self._load_state()

        # Start the worker threads
        self.start()

    def submit_task(
        self,
        task_id: str,
        project_name: str,
        solver_config: Dict,
        resource_reqs: ResourceRequirements,
        solver_type: str = "hfss",
        priority: int = 1,
        callback: Optional[Callable] = None,
    ) -> str:
        """
        Enqueue a new simulation task.

        Duplicate `task_id` or impossible resource requests raise
        `ValueError` **synchronously**.

        Parameters
        ----------
        task_id : str
            Must be unique across the lifetime of the persistence file.
        project_name : str
        solver_config : dict
        resource_reqs : ResourceRequirements
        solver_type : str, default "hfss"
        priority : int, 1-10
        callback : callable, optional
            Signature `callback(task_id, result, error)` invoked on the worker thread.

        Returns
        -------
        str
            The same `task_id` passed in (for fluent chaining).
        """
        with self.lock:
            # Check if task ID already exists
            if task_id in self.running_tasks or task_id in self.completed_tasks or task_id in self.pending_queue:
                raise ValueError(f"Task ID '{task_id}' already exists")

            # Validate priority
            priority = max(1, min(10, priority))

            # Validate resource requirements
            system_info = self.resource_monitor.get_current_usage()
            if resource_reqs.min_cores > system_info["total_cores"]:
                raise ValueError(
                    f"Requested {resource_reqs.min_cores} cores but system only has {system_info['total_cores']}"
                )

            if resource_reqs.min_memory_gb > system_info["total_memory_gb"]:
                raise ValueError(
                    f"Requested {resource_reqs.min_memory_gb}GB memory but system only has "
                    f"{system_info['total_memory_gb']:.1f}GB"
                )

            # Create and queue the task
            task = SimulationTask(
                task_id=task_id,
                project_name=project_name,
                solver_config=solver_config,
                resource_reqs=resource_reqs,
                priority=priority,
                callback=callback,
                solver_type=solver_type,
            )
            self.pending_queue.put(task)
            logger.info(f"Task {task_id} submitted for project {project_name} with priority {priority}")

            # Persist state if enabled
            if self.persistence_file:
                self._save_state()

            return task_id

    def get_task_status(self, task_id: str) -> Optional[SimulationStatus]:
        """Return the current `SimulationStatus` or `None` if unknown."""
        with self.lock:
            # Check running tasks
            if task_id in self.running_tasks:
                return self.running_tasks[task_id].status

            # Check completed tasks
            if task_id in self.completed_tasks:
                return self.completed_tasks[task_id].status

            # Check pending tasks
            if task_id in self.pending_queue:
                return SimulationStatus.PENDING

            return None

    def get_task_info(self, task_id: str) -> Optional[Dict]:
        """Full JSON serialisation of the requested task."""
        with self.lock:
            # Check running tasks
            if task_id in self.running_tasks:
                return self.running_tasks[task_id].to_dict()

            # Check completed tasks
            if task_id in self.completed_tasks:
                return self.completed_tasks[task_id].to_dict()

            # Check pending tasks
            for task in self.pending_queue.get_all():
                if task.task_id == task_id:
                    return task.to_dict()

            return None

    def get_task_result(self, task_id: str) -> Optional[Any]:
        """Return the `result` payload if task is COMPLETED, otherwise `None`."""
        with self.lock:
            if task_id in self.completed_tasks:
                return self.completed_tasks[task_id].result
            return None

    def cancel_task(self, task_id: str) -> bool:
        """
        Attempt to cancel a **PENDING** or **RUNNING** task.

        Returns
        -------
        bool
            `True` if task was successfully moved to CANCELLED state.
        """
        with self.lock:
            # Check if task is running
            if task_id in self.running_tasks:
                task = self.running_tasks[task_id]

                # Try to terminate the process
                if task.process_id:
                    try:
                        process = psutil.Process(task.process_id)
                        process.terminate()
                        try:
                            process.wait(timeout=5)
                        except (psutil.TimeoutExpired, psutil.NoSuchProcess):
                            try:
                                process.kill()
                            except psutil.NoSuchProcess:
                                pass
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass

                task.status = SimulationStatus.CANCELLED
                task.end_time = datetime.now()
                self.completed_tasks[task_id] = task
                del self.running_tasks[task_id]

                self.stats["tasks_cancelled"] += 1
                logger.info(f"Task {task_id} cancelled")

                if self.persistence_file:
                    self._save_state()

                return True

            # Check if task is pending
            if self.pending_queue.remove(task_id):
                task = None
                # We need to find the task to update its status
                for t in self.pending_queue.get_all():
                    if t.task_id == task_id:
                        task = t
                        break

                if task:
                    task.status = SimulationStatus.CANCELLED
                    task.end_time = datetime.now()
                    self.completed_tasks[task_id] = task

                    self.stats["tasks_cancelled"] += 1
                    logger.info(f"Task {task_id} cancelled")

                    if self.persistence_file:
                        self._save_state()

                    return True

            return False

    def set_task_priority(self, task_id: str, priority: int) -> bool:
        """
        Re-prioritise a **PENDING** task.

        Returns
        -------
        bool
            `True` if the task was found and updated.
        """
        with self.lock:
            # Only pending tasks can have their priority changed
            for task in self.pending_queue.get_all():
                if task.task_id == task_id:
                    # Remove and re-add with new priority
                    self.pending_queue.remove(task_id)
                    task.priority = max(1, min(10, priority))
                    self.pending_queue.put(task)

                    logger.info(f"Task {task_id} priority set to {priority}")

                    if self.persistence_file:
                        self._save_state()

                    return True

            return False

    def list_tasks(self, status_filter: Optional[SimulationStatus] = None) -> List[Dict]:
        """
        List **all** tasks (pending, running, completed).

        Parameters
        ----------
        status_filter : SimulationStatus | None
            If provided, return only tasks in that state.

        Returns
        -------
        list[dict]
            List of `task.to_dict()` objects.
        """
        with self.lock:
            tasks = []

            # Add pending tasks
            for task in self.pending_queue.get_all():
                if status_filter is None or task.status == status_filter:
                    tasks.append(task.to_dict())

            # Add running tasks
            for task in self.running_tasks.values():
                if status_filter is None or task.status == status_filter:
                    tasks.append(task.to_dict())

            # Add completed tasks
            for task in self.completed_tasks.values():
                if status_filter is None or task.status == status_filter:
                    tasks.append(task.to_dict())

            return tasks

    def get_stats(self) -> Dict:
        """
        Aggregated metrics and live resource usage.

        Returns
        -------
        dict
            tasks_completed, tasks_failed, tasks_cancelled,
            total_cpu_time, total_memory_hours,
            pending_tasks, running_tasks, completed_tasks,
            total_cores, total_memory_gb, available_memory_gb,
            allocated_cores, allocated_memory_gb, ...
        """
        with self.lock:
            stats = self.stats.copy()
            stats["uptime"] = (datetime.now() - stats["start_time"]).total_seconds()
            stats["pending_tasks"] = len(self.pending_queue)
            stats["running_tasks"] = len(self.running_tasks)
            stats["completed_tasks"] = len(self.completed_tasks)

            # Add system resource information
            system_info = self.resource_monitor.get_current_usage()
            stats.update(system_info)

            # Calculate allocated resources
            allocated_cores = 0
            allocated_memory_gb = 0

            for task in self.running_tasks.values():
                if task.actual_cores_used:
                    allocated_cores += task.actual_cores_used
                else:
                    allocated_cores += task.resource_reqs.min_cores

                if task.peak_memory_used_gb:
                    allocated_memory_gb += task.peak_memory_used_gb
                else:
                    allocated_memory_gb += task.resource_reqs.estimated_memory_gb

            stats["allocated_cores"] = allocated_cores
            stats["allocated_memory_gb"] = round(allocated_memory_gb, 1)
            stats["available_cores"] = system_info["total_cores"] - allocated_cores
            stats["available_memory_gb"] = round(system_info["available_memory_gb"] - allocated_memory_gb, 1)

            return stats

    def start(self) -> None:
        """
        Idempotent start of the worker threads.
        Automatically called during `__init__`.
        """
        with self.lock:
            if self.is_running:
                return

            self.is_running = True
            for i in range(self.max_workers):
                worker = threading.Thread(target=self._worker_loop, name=f"SolverWorker-{i}", daemon=True)
                worker.start()
                self.workers.append(worker)

            logger.info(f"Started {self.max_workers} solver worker threads")

    def stop(self, wait: bool = True) -> None:
        """
        Gracefully shut down the manager.

        Parameters
        ----------
        wait : bool, default True
            - `True`: block until running tasks finish naturally.
            - `False`: cancel all running and pending tasks immediately.
        """
        with self.lock:
            if not self.is_running:
                return

            self.is_running = False

            if not wait:
                # Cancel all running tasks
                for task_id in list(self.running_tasks.keys()):
                    self.cancel_task(task_id)

                # Cancel all pending tasks
                while True:
                    task = self.pending_queue.get()
                    if task is None:
                        break
                    task.status = SimulationStatus.CANCELLED
                    task.end_time = datetime.now()
                    self.completed_tasks[task.task_id] = task

            # Persist state if enabled
            if self.persistence_file:
                self._save_state()

            logger.info("Solver manager stopped")

    def _worker_loop(self) -> None:
        """Main loop for worker threads"""
        while self.is_running:
            try:
                # Check if we can run any tasks
                task_to_run = None
                with self.lock:
                    # Check all pending tasks in priority order
                    for task in self.pending_queue.get_all():
                        can_run, reason = self.resource_monitor.can_run_task(task, self.running_tasks)
                        if can_run:
                            task_to_run = task
                            self.pending_queue.remove(task.task_id)
                            break

                if task_to_run is None:
                    time.sleep(1)  # Wait before checking again
                    continue

                with self.lock:
                    # Move task to running state
                    task_to_run.status = SimulationStatus.RUNNING
                    task_to_run.start_time = datetime.now()
                    self.running_tasks[task_to_run.task_id] = task_to_run

                    if self.persistence_file:
                        self._save_state()

                logger.info(f"Starting task {task_to_run.task_id} with {task_to_run.resource_reqs.min_cores} cores")

                # Run the simulation
                try:
                    # Define progress callback
                    def progress_callback(progress: float, memory_usage: float):
                        with self.lock:
                            task_to_run.progress = progress
                            task_to_run.peak_memory_used_gb = memory_usage
                            task_to_run.actual_cores_used = task_to_run.resource_reqs.min_cores
                            if task_to_run.start_time and progress > 0:
                                elapsed = (datetime.now() - task_to_run.start_time).total_seconds()
                                task_to_run.estimated_time_remaining = elapsed / progress * (100 - progress)

                    # Run the actual simulation
                    result = PyEDBIntegration.run_simulation(task_to_run, progress_callback)

                    with self.lock:
                        task_to_run.status = SimulationStatus.COMPLETED
                        task_to_run.result = result
                        task_to_run.end_time = datetime.now()
                        task_to_run.progress = 100.0
                        task_to_run.estimated_time_remaining = 0

                        # Update statistics
                        if task_to_run.actual_cores_used and task_to_run.start_time and task_to_run.end_time:
                            runtime_hours = (task_to_run.end_time - task_to_run.start_time).total_seconds() / 3600
                            self.stats["total_cpu_time"] += runtime_hours * task_to_run.actual_cores_used

                        if task_to_run.peak_memory_used_gb and task_to_run.start_time and task_to_run.end_time:
                            runtime_hours = (task_to_run.end_time - task_to_run.start_time).total_seconds() / 3600
                            self.stats["total_memory_hours"] += runtime_hours * task_to_run.peak_memory_used_gb

                        # Move from running to completed
                        self.completed_tasks[task_to_run.task_id] = task_to_run
                        del self.running_tasks[task_to_run.task_id]

                        self.stats["tasks_completed"] += 1

                        if self.persistence_file:
                            self._save_state()

                    logger.info(f"Task {task_to_run.task_id} completed successfully")

                    # Call callback if provided
                    if task_to_run.callback:
                        try:
                            task_to_run.callback(task_to_run.task_id, result, None)
                        except Exception as e:
                            logger.error(f"Callback for task {task_to_run.task_id} failed: {e}")

                except Exception as e:
                    with self.lock:
                        task_to_run.status = SimulationStatus.FAILED
                        task_to_run.error_message = str(e)
                        task_to_run.end_time = datetime.now()

                        # Move from running to completed (failed)
                        self.completed_tasks[task_to_run.task_id] = task_to_run
                        del self.running_tasks[task_to_run.task_id]

                        self.stats["tasks_failed"] += 1

                        if self.persistence_file:
                            self._save_state()

                    logger.error(f"Task {task_to_run.task_id} failed: {e}")

                    # Call callback if provided
                    if task_to_run.callback:
                        try:
                            task_to_run.callback(task_to_run.task_id, None, e)
                        except Exception as callback_error:
                            logger.error(f"Callback for task {task_to_run.task_id} failed: {callback_error}")

            except Exception as e:
                logger.error(f"Worker thread encountered error: {e}")
                time.sleep(1)  # Avoid tight loop on errors

    def _save_state(self) -> None:
        """Save the current state to the persistence file"""
        try:
            with self.lock:
                state = {
                    "pending_tasks": [task.to_dict() for task in self.pending_queue.get_all()],
                    "running_tasks": {k: v.to_dict() for k, v in self.running_tasks.items()},
                    "completed_tasks": {k: v.to_dict() for k, v in self.completed_tasks.items()},
                    "stats": self.stats,
                    "save_time": datetime.now().isoformat(),
                }

                # Create directory if it doesn't exist
                os.makedirs(
                    os.path.dirname(self.persistence_file) if os.path.dirname(self.persistence_file) else ".",
                    exist_ok=True,
                )

                with open(self.persistence_file, "w") as f:
                    json.dump(state, f, indent=2)

                logger.debug("State saved to persistence file")
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    def _load_state(self) -> None:
        """Load state from the persistence file"""
        try:
            with open(self.persistence_file, "r") as f:
                state = json.load(f)

            with self.lock:
                # Clear current state
                self.pending_queue = PriorityQueue()
                self.running_tasks.clear()
                self.completed_tasks.clear()

                # Load pending tasks
                for task_data in state.get("pending_tasks", []):
                    task = SimulationTask.from_dict(task_data)
                    self.pending_queue.put(task)

                # Load running tasks
                for task_id, task_data in state.get("running_tasks", {}).items():
                    task = SimulationTask.from_dict(task_data)
                    self.running_tasks[task_id] = task

                # Load completed tasks
                for task_id, task_data in state.get("completed_tasks", {}).items():
                    task = SimulationTask.from_dict(task_data)
                    self.completed_tasks[task_id] = task

                # Load statistics
                self.stats = state.get("stats", self.stats)

            logger.info("State loaded from persistence file")
        except Exception as e:
            logger.error(f"Failed to load state: {e}")

    def _start_web_interface(self) -> None:
        """Start the web interface for monitoring"""
        app = Flask(__name__, template_folder=os.path.dirname(os.path.abspath(__file__)))

        @app.route("/")
        def index():
            return render_template("solver_dashboard.html")

        @app.route("/api/tasks")
        def api_tasks():
            status_filter = request.args.get("status")
            if status_filter:
                try:
                    status = SimulationStatus(status_filter)
                    tasks = self.list_tasks(status)
                except ValueError:
                    tasks = self.list_tasks()
            else:
                tasks = self.list_tasks()
            return jsonify(tasks)

        @app.route("/api/task/<task_id>")
        def api_task(task_id):
            task_info = self.get_task_info(task_id)
            if task_info:
                return jsonify(task_info)
            return jsonify({"error": "Task not found"}), 404

        @app.route("/api/stats")
        def api_stats():
            return jsonify(self.get_stats())

        @app.route("/api/cancel/<task_id>", methods=["POST"])
        def api_cancel(task_id):
            if self.cancel_task(task_id):
                return jsonify({"success": True})
            return jsonify({"error": "Failed to cancel task"}), 400

        @app.route("/api/priority/<task_id>/<int:priority>", methods=["POST"])
        def api_priority(task_id, priority):
            if self.set_task_priority(task_id, priority):
                return jsonify({"success": True})
            return jsonify({"error": "Failed to set priority"}), 400

        # Start the Flask app in a separate thread
        def run_flask():
            app.run(host="0.0.0.0", port=self.web_port, debug=False, use_reloader=False)

        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()

        self.web_interface = app
        logger.info(f"Web interface started on port {self.web_port}")

        # Try to open the web interface in the default browser
        try:
            webbrowser.open(f"http://localhost:{self.web_port}")
        except:
            pass

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - stop the manager"""
        self.stop(wait=True)
