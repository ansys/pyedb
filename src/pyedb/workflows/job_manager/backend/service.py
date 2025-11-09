# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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


"""
Async job manager with pool scheduling and REST/WebSocket API.

The module implements a **fully asynchronous** multi-tenant job manager that:

* enforces **host resource limits** (CPU, memory, disk, concurrency),
* maintains **priority queues** (negative → low, zero → normal, positive → high),
* exposes **REST** and **Socket.IO** endpoints for integration,
* supports **external schedulers** (SLURM, LSF, PBS, Windows-HPC) **and**
  local subprocess execution,
* guarantees **exactly-once** execution and **graceful draining** on shutdown.

It is designed to be **embedded** inside a PyEDB process or **deployed** as a
stand-alone micro-service (Docker, systemd, Kubernetes).

Examples
--------
Stand-alone REST server:

.. code-block:: bash

    python -m pyedb.workflows.job_manager.service

Embedded inside PyEDB:

.. code-block:: python

    from pyedb.workflows.job_manager.service import JobManager, ResourceLimits

    manager = JobManager(ResourceLimits(max_concurrent_jobs=4))
    await manager.submit_job(config, priority=10)

The REST API is **self-documenting** at runtime:

.. code-block:: bash

    curl http://localhost:8080/resources
    curl http://localhost:8080/queue
    curl -X POST http://localhost:8080/jobs/submit -d @cfg.json
"""

import asyncio
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import getpass
import logging
import os.path
import platform
from typing import Any, Deque, Dict, List, Optional, Set

import aiohttp
from aiohttp import web
import psutil
import socketio

from pyedb.workflows.job_manager.backend.job_submission import (
    HFSSSimulationConfig,
    SchedulerType,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("JobManager")


class JobStatus(Enum):
    """
    Terminal and non-terminal job states used internally and exposed via REST.

    Members
    -------
    PENDING
        Initial state before queuing.
    QUEUED
        Awaiting resources in local queue.
    SCHEDULED
        Submitted to external scheduler.
    RUNNING
        Currently executing.
    COMPLETED
        Normal termination.
    FAILED
        Non-zero exit code or exception.
    CANCELLED
        User-initiated abort.
    """

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SCHEDULED = "scheduled"
    QUEUED = "queued"  # Specifically for local queue


@dataclass
class ResourceLimits:
    """
    Host-level resource constraints enforced by the manager.

    All attributes are **checked** before starting a new job; if any limit is
    exceeded the job remains in the queue.

    Parameters
    ----------
    max_concurrent_jobs : int, optional
        Simultaneous local jobs. Default is ``1``.
    max_cpu_percent : float, optional
        CPU utilisation threshold (0-100). Default is ``80.0``.
    min_memory_gb : float, optional
        Free RAM required to start (GB). Default is ``2.0``.
    min_disk_gb : float, optional
        Free disk space required to start (GB). Default is ``10.0``.
    """

    max_concurrent_jobs: int = 1
    max_cpu_percent: float = 80.0  # Don't start new jobs if CPU > 80%
    min_memory_gb: float = 2.0  # Minimum free memory required to start a job
    min_disk_gb: float = 2.0  # Minimum free disk space required


@dataclass
class JobInfo:
    """
    **Mutable** state container for a single simulation.

    Attributes
    ----------
    config : HFSSSimulationConfig
        Immutable configuration.
    status : JobStatus
        Current life-cycle state.
    start_time : datetime or None
        When the job entered ``RUNNING``.
    end_time : datetime or None
        When the job reached a terminal state.
    return_code : int or None
        Exit code of the solver or scheduler.
    output : str
        Stdout captured (local runs only).
    error : str
        Stderr captured (local runs only).
    process : asyncio.subprocess.Process or None
        Handle for local cancellation.
    scheduler_job_id : str or None
        External identifier (SLURM, LSF, …).
    local_resources : dict or None
        Snapshot of host telemetry at start time.
    priority : int
        Higher numbers are de-queued first.
    """

    config: HFSSSimulationConfig
    status: JobStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    return_code: Optional[int] = None
    output: str = ""
    error: str = ""
    process: Optional[Any] = None
    scheduler_job_id: Optional[str] = None
    local_resources: Optional[Dict[str, Any]] = None
    priority: int = 0  # Higher number = higher priority


class ResourceMonitor:
    """
    **Async** background task that samples host telemetry every *N* seconds.

    The monitor keeps a **thread-safe** in-memory cache used by
    :meth:`JobPoolManager.can_start_job` to throttle submissions.

    Parameters
    ----------
    update_interval : int, optional
        Sampling period in seconds. Default is ``5``.

    Attributes
    ----------
    current_usage : dict
        Cached resource usage information with keys:
        - cpu_percent: Current CPU usage percentage
        - memory_percent: Current memory usage percentage
        - memory_used_gb: Memory used in GB
        - memory_total_gb: Total memory in GB
        - memory_free_gb: Free memory in GB
        - disk_usage_percent: Disk usage percentage
        - disk_free_gb: Free disk space in GB
        - timestamp: Last update timestamp
    """

    def __init__(self, update_interval: int = 5):
        self.update_interval = update_interval
        self.current_usage = {
            "cpu_percent": 0,
            "memory_percent": 0,
            "memory_used_gb": 0,
            "memory_total_gb": 0,
            "memory_free_gb": 0,
            "disk_usage_percent": 0,
            "disk_free_gb": 0,
            "timestamp": datetime.now().isoformat(),
        }

    async def monitor_resources(self):
        """
        **Infinite** coroutine that updates :attr:`current_usage`.

        Runs until the event-loop is shut down. Samples CPU, memory, and disk
        usage at regular intervals.
        """
        await self._sample_once()
        while True:
            await self._sample_once()
            await asyncio.sleep(self.update_interval)

    async def _sample_once(self):
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)

            # Memory usage
            memory = psutil.virtual_memory()
            memory_total_gb = memory.total / (1024**3)
            memory_used_gb = memory.used / (1024**3)
            memory_free_gb = memory.available / (1024**3)

            # Disk usage (checking the root directory)
            disk = psutil.disk_usage(os.path.abspath(os.sep))
            disk_usage_percent = disk.percent
            disk_free_gb = disk.free / (1024**3)

            self.current_usage.update(
                {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_used_gb": round(memory_used_gb, 2),
                    "memory_total_gb": round(memory_total_gb, 2),
                    "memory_free_gb": round(memory_free_gb, 2),
                    "disk_usage_percent": disk_usage_percent,
                    "disk_free_gb": round(disk_free_gb, 2),
                    "timestamp": datetime.now().isoformat(),
                }
            )

        except Exception as e:
            logger.error(f"Resource monitoring error: {e}")


class JobPoolManager:
    """
    **Priority-aware** FIFO queues plus running-set tracker.

    The implementation is **lock-free** (uses ``deque`` and ``dict``) and
    **async-safe** (no awaits, therefore can be invoked from any thread).

    Parameters
    ----------
    resource_limits : ResourceLimits
        Constraints used by :meth:`can_start_job`.

    Attributes
    ----------
    job_queue : Deque[str]
        FIFO queue for normal priority jobs
    priority_queue : Dict[int, List[str]]
        Priority-based queues (key=priority, value=job_ids)
    running_jobs : Set[str]
        Set of currently running job IDs
    job_priorities : Dict[str, int]
        Mapping of job_id to priority
    """

    def __init__(self, resource_limits: ResourceLimits):
        self.resource_limits = resource_limits
        self.job_queue: Deque[str] = deque()  # FIFO queue for job IDs
        self.priority_queue: Dict[int, List[str]] = {}  # Priority-based queue
        self.running_jobs: Set[str] = set()
        self.job_priorities: Dict[str, int] = {}

    def add_job(self, job_id: str, priority: int = 0):
        """
        Insert job into the **appropriate** queue (priority or FIFO).

        Parameters
        ----------
        job_id : str
            Unique identifier.
        priority : int, optional
            Negative (low), zero (normal), positive (high). Default is ``0``.
        """
        self.job_priorities[job_id] = priority

        if priority > 0:
            if priority not in self.priority_queue:
                self.priority_queue[priority] = []
            self.priority_queue[priority].append(job_id)
            # Sort priority queues to maintain order
            for pq in self.priority_queue.values():
                pq.sort(key=lambda x: self.job_priorities.get(x, 0), reverse=True)
        else:
            self.job_queue.append(job_id)

    def get_next_job(self) -> Optional[str]:
        """
        Return the **next** job to be started (highest priority first).

        Returns
        -------
        str or None
            Job identifier or ``None`` if all queues are empty.

        Notes
        -----
        Priority queues are checked first (highest to lowest), then the
        normal FIFO queue.
        """
        # First check priority queues (highest priority first)
        for priority in sorted(self.priority_queue.keys(), reverse=True):
            if self.priority_queue[priority]:
                return self.priority_queue[priority].pop(0)

        # Then check regular queue
        if self.job_queue:
            return self.job_queue.popleft()

        return None

    def remove_job(self, job_id: str):
        """
        **Idempotently** remove a job from **all** queues.

        Parameters
        ----------
        job_id : str
            Identifier to purge.
        """
        if job_id in self.job_queue:
            self.job_queue.remove(job_id)

        for priority, jobs in self.priority_queue.items():
            if job_id in jobs:
                jobs.remove(job_id)

        if job_id in self.job_priorities:
            del self.job_priorities[job_id]

    def can_start_job(self, resource_monitor: ResourceMonitor) -> bool:
        """
        **Boolean** predicate that decides whether a new job may be started.

        Checks resource limits without violating constraints.

        Parameters
        ----------
        resource_monitor : ResourceMonitor
            Source of current host telemetry.

        Returns
        -------
        bool
            ``True`` → job may be started, ``False`` → remain queued.
        """
        resources = resource_monitor.current_usage

        # Check if we've reached max concurrent jobs
        if len(self.running_jobs) >= self.resource_limits.max_concurrent_jobs:
            return False

        # Check CPU usage
        if resources["cpu_percent"] > self.resource_limits.max_cpu_percent:
            logger.info(f"CPU usage too high ({resources['cpu_percent']}%), delaying job start")
            return False

        # Check memory availability
        if resources["memory_free_gb"] < self.resource_limits.min_memory_gb:
            logger.info(f"Insufficient memory ({resources['memory_free_gb']}GB free), delaying job start")
            return False

        # Check disk space
        if resources["disk_free_gb"] < self.resource_limits.min_disk_gb:
            logger.info(f"Insufficient disk space ({resources['disk_free_gb']}GB free), delaying job start")
            return False
        return True

    def get_queue_stats(self) -> Dict[str, Any]:
        """
        Real-time snapshot for REST ``/queue`` endpoint.

        Returns
        -------
        dict
            Queue statistics with keys:
            - total_queued: Total jobs in all queues
            - regular_queue_size: Jobs in normal FIFO queue
            - priority_queues: Dict of priority -> count
            - running_jobs: Number of currently running jobs
            - max_concurrent: Maximum concurrent jobs allowed
        """
        total_queued = len(self.job_queue)
        for jobs in self.priority_queue.values():
            total_queued += len(jobs)

        return {
            "total_queued": total_queued,
            "regular_queue_size": len(self.job_queue),
            "priority_queues": {prio: len(jobs) for prio, jobs in self.priority_queue.items()},
            "running_jobs": len(self.running_jobs),
            "max_concurrent": self.resource_limits.max_concurrent_jobs,
        }


class JobManager:
    """
    **Async** job manager combining resource monitoring and job scheduling.

    This class provides the core functionality for:

    * Resource monitoring via :class:`ResourceMonitor`
    * Job scheduling via :class:`JobPoolManager`
    * REST/Socket.IO API via aiohttp web server
    * Background task for continuous job processing

    Parameters
    ----------
    resource_limits : ResourceLimits, optional
        Host constraints. Creates default instance if None.
    scheduler_type : SchedulerType, optional
        Type of job scheduler to use. Default is ``SchedulerType.NONE``.

    Attributes
    ----------
    jobs : Dict[str, JobInfo]
        Dictionary of all managed jobs
    resource_limits : ResourceLimits
        Current resource constraints
    job_pool : JobPoolManager
        Priority-aware job queue manager
    resource_monitor : ResourceMonitor
        Host resource usage monitor
    ansys_path : str or None
        Path to ANSYS EDT executable
    sio : socketio.AsyncServer
        Socket.IO server for real-time updates
    app : web.Application
        aiohttp web application
    """

    def __init__(self, resource_limits: ResourceLimits = None, scheduler_type: SchedulerType = SchedulerType.NONE):
        logging.basicConfig(level=logging.DEBUG, format="%(levelname)s:%(name)s:%(message)s")
        self.jobs: Dict[str, JobInfo] = {}
        if resource_limits is None:
            resource_limits = ResourceLimits()
        self.resource_limits = resource_limits
        self.job_pool = JobPoolManager(self.resource_limits)
        self.resource_monitor = ResourceMonitor()
        self.ansys_path = None  # Will be set by JobManagerHandler

        # Initialize scheduler manager
        self.scheduler_type = scheduler_type
        if scheduler_type in {SchedulerType.SLURM, SchedulerType.LSF}:
            self._sch_mgr = SchedulerManager(scheduler_type)
        else:
            self._sch_mgr = None

        # Correct SocketIO initialization
        self.sio = socketio.AsyncServer(async_mode="aiohttp", cors_allowed_origins="*")
        self.app = web.Application()
        self.sio.attach(self.app)

        # Setup routes
        self.setup_routes()

        # Background task for continuous job processing
        self._processing_task: Optional[asyncio.Task] = None
        self._shutdown = False
        # Start resource monitoring immediately
        self._monitor_task = None
        self._ensure_monitor_running()
        # Background task for scheduler monitoring
        self._scheduler_monitor_task: Optional[asyncio.Task] = None
        self._ensure_scheduler_monitor_running()

    def _ensure_monitor_running(self):
        """Ensure resource monitoring task is running."""
        try:
            loop = asyncio.get_running_loop()
            if self._monitor_task is None or self._monitor_task.done():
                self._monitor_task = loop.create_task(self.resource_monitor.monitor_resources())
        except RuntimeError:
            # No event loop running yet, will be started when JobManagerHandler starts
            pass

    def _ensure_scheduler_monitor_running(self):
        """Ensure scheduler monitoring task is running for Slurm/LSF jobs."""
        if self._sch_mgr is None:
            # No scheduler configured, skip monitoring
            return
        try:
            loop = asyncio.get_running_loop()
            if self._scheduler_monitor_task is None or self._scheduler_monitor_task.done():
                self._scheduler_monitor_task = loop.create_task(self._monitor_scheduler_jobs())
                logger.info(f"Started scheduler monitoring for {self.scheduler_type.value}")
        except RuntimeError:
            # No event loop running yet, will be started when JobManagerHandler starts
            pass

    async def _monitor_scheduler_jobs(self):
        """
        Continuously monitor jobs submitted to external schedulers (Slurm/LSF).

        This background task polls the scheduler queue every 30 seconds and updates
        job statuses based on the actual scheduler state.
        """
        logger.info(f"✅ Scheduler monitoring loop started for {self.scheduler_type.value}")

        while not self._shutdown:
            try:
                # Find all jobs that are currently scheduled (submitted to external scheduler)
                scheduled_jobs = {
                    job_id: job_info
                    for job_id, job_info in self.jobs.items()
                    if job_info.status == JobStatus.SCHEDULED and job_info.scheduler_job_id
                }

                if not scheduled_jobs:
                    # No jobs to monitor, sleep longer
                    await asyncio.sleep(10)
                    continue

                # Get current scheduler job list
                scheduler_jobs = await self._sch_mgr.get_jobs()
                scheduler_job_ids = {job["job_id"] for job in scheduler_jobs}
                scheduler_job_states = {job["job_id"]: job["state"] for job in scheduler_jobs}

                logger.info(
                    f"Monitoring {len(scheduled_jobs)} scheduled jobs. Scheduler has {len(scheduler_jobs)} jobs."
                )

                for job_id, job_info in scheduled_jobs.items():
                    scheduler_job_id = job_info.scheduler_job_id

                    if scheduler_job_id in scheduler_job_ids:
                        # Job still exists in scheduler queue
                        state = scheduler_job_states.get(scheduler_job_id, "UNKNOWN")

                        # Map scheduler states to our JobStatus
                        if state in ["RUNNING", "R"]:
                            if job_info.status != JobStatus.RUNNING:
                                job_info.status = JobStatus.RUNNING
                                if not job_info.start_time:
                                    job_info.start_time = datetime.now()
                                await self.sio.emit(
                                    "job_started",
                                    {
                                        "job_id": job_id,
                                        "scheduler_job_id": scheduler_job_id,
                                        "start_time": job_info.start_time.isoformat(),
                                    },
                                )
                                logger.info(f"Job {job_id} (scheduler ID: {scheduler_job_id}) is now RUNNING")

                        elif state in ["PENDING", "PD", "PEND"]:
                            # Job is still pending/queued in scheduler
                            logger.debug(f"Job {job_id} (scheduler ID: {scheduler_job_id}) is PENDING in scheduler")

                        elif state in ["COMPLETING", "CG"]:
                            # Job is completing, keep current status
                            logger.debug(f"Job {job_id} (scheduler ID: {scheduler_job_id}) is COMPLETING")

                    else:
                        # Job no longer in scheduler queue - it has completed or failed
                        # Check if we can find output files to determine success/failure
                        job_info.end_time = datetime.now()
                        self.job_pool.running_jobs.discard(job_id)

                        # Try to determine if job completed successfully by checking output directory
                        output_dir = job_info.config.working_directory
                        log_file = os.path.join(output_dir, f"{job_info.config.jobid}.log")

                        # Default to completed - scheduler jobs that finish typically completed
                        # unless we can detect otherwise
                        if os.path.exists(log_file):
                            try:
                                # Check if log indicates success or failure
                                with open(log_file, "r") as f:
                                    log_content = f.read()
                                    if "error" in log_content.lower() or "failed" in log_content.lower():
                                        job_info.status = JobStatus.FAILED
                                        job_info.error = "Job failed based on log file content"
                                    else:
                                        job_info.status = JobStatus.COMPLETED
                                        job_info.return_code = 0
                            except Exception as e:
                                logger.warning(f"Could not read log file for job {job_id}: {e}")
                                job_info.status = JobStatus.COMPLETED
                                job_info.return_code = 0
                        else:
                            # No log file found, assume completed
                            job_info.status = JobStatus.COMPLETED
                            job_info.return_code = 0

                        await self.sio.emit(
                            "job_completed",
                            {
                                "job_id": job_id,
                                "scheduler_job_id": scheduler_job_id,
                                "status": job_info.status.value,
                                "end_time": job_info.end_time.isoformat(),
                                "return_code": job_info.return_code,
                            },
                        )

                        logger.info(
                            f"Job {job_id} (scheduler ID: {scheduler_job_id}) completed with status "
                            f"{job_info.status.value}"
                        )

            except Exception as e:
                logger.error(f"Error in scheduler monitoring loop: {e}")

            # Poll every 5 seconds for responsive status updates
            await asyncio.sleep(5)

        logger.info("Scheduler monitoring loop stopped")

    def setup_routes(self):
        """
        Internal method that wires aiohttp routes to class methods.

        Called once from __init__. Sets up all REST API endpoints.
        """
        self.app.router.add_get("/", self.handle_index)
        self.app.router.add_get("/jobs", self.handle_get_jobs)
        self.app.router.add_get("/resources", self.handle_get_resources)
        self.app.router.add_get("/queue", self.handle_get_queue)
        self.app.router.add_post("/jobs/submit", self.handle_submit_job)
        self.app.router.add_post("/jobs/{job_id}/cancel", self.handle_cancel_job)
        self.app.router.add_post("/jobs/{job_id}/priority", self.handle_set_priority)
        self.app.router.add_put("/pool/limits", self.handle_edit_concurrent_limits)
        self.app.router.add_post("/system/start_monitoring", self.handle_start_monitoring)
        self.app.router.add_get("/scheduler/partitions", self.handle_get_partitions)
        self.app.router.add_get("/system/status", self.handle_get_system_status)
        if os.path.exists("static"):
            self.app.router.add_static("/static", "static")
        else:
            os.makedirs("static", exist_ok=True)
            self.app.router.add_static("/static", "static")

    async def handle_get_system_status(self, request):
        """
        Get system and scheduler status.

        Parameters
        ----------
        request : aiohttp.web.Request
            HTTP request object

        Returns
        -------
        aiohttp.web.Response
            JSON response with system status information
        """
        # Ensure resource monitoring is active
        self._ensure_monitor_running()

        running_jobs = sum(1 for job in self.jobs.values() if job.status == JobStatus.RUNNING)
        queued_jobs = sum(1 for job in self.jobs.values() if job.status == JobStatus.QUEUED)
        status = {
            "scheduler_detection": {
                "active_scheduler": self.scheduler_type.name,
                "detected_by": "JobManager",
                "backend_available": True,
            },
            "resource_monitoring": {
                "active": self._monitor_task is not None and not self._monitor_task.done(),
                "last_update": self.resource_monitor.current_usage.get("timestamp", "Never"),
                **self.resource_monitor.current_usage,
            },
            "mode": self.scheduler_type.value,
            "local_pool": {
                "running_jobs": running_jobs,
                "queued_jobs": queued_jobs,
                "max_concurrent": self.resource_limits.max_concurrent_jobs,
            },
        }
        return web.json_response(status)

    async def handle_get_partitions(self, request):
        """
        Get scheduler partitions/queues.

        Parameters
        ----------
        request : aiohttp.web.Request
            HTTP request object

        Returns
        -------
        aiohttp.web.Response
            JSON response with partition information or error
        """
        if not self._sch_mgr:
            return web.json_response({"error": "Scheduler not supported"}, status=400)
        try:
            partitions = await self._sch_mgr.get_partitions()
            return web.json_response(partitions)
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def handle_start_monitoring(self, request):
        """
        Manually start resource monitoring.

        Parameters
        ----------
        request : aiohttp.web.Request
            HTTP request object

        Returns
        -------
        aiohttp.web.Response
            JSON response indicating success or failure
        """
        try:
            if self._monitor_task is None or self._monitor_task.done():
                self._monitor_task = asyncio.create_task(self.resource_monitor.monitor_resources())
                return web.json_response({"success": True, "message": "Resource monitoring started"})
            else:
                return web.json_response({"success": True, "message": "Resource monitoring already active"})
        except Exception as e:
            return web.json_response({"success": False, "error": str(e)}, status=500)

    async def handle_index(self, request):
        """
        Serve the main web interface.

        Parameters
        ----------
        request : aiohttp.web.Request
            HTTP request object

        Returns
        -------
        aiohttp.web.FileResponse
            Static HTML file
        """
        return web.FileResponse("static/index.html")

    async def handle_submit_job(self, request):
        """
        Submit a new job for execution.

        Parameters
        ----------
        request : aiohttp.web.Request
            HTTP POST request with JSON payload

        Returns
        -------
        aiohttp.web.Response
            JSON response with job ID or error

        Notes
        -----
        Expected JSON payload:

        .. code-block:: json

            {
                "config": {
                    "jobid": "job_123",
                    "project_path": "/path/to/project.aedt",
                    ... other HFSS config fields
                },
                "priority": 0
            }
        """
        try:
            logger.info("🔍 ROUTE HIT: /jobs/submit")
            data = await request.json()
            config_dict = data.get("config", {})

            # Create HFSS config from dictionary
            config = HFSSSimulationConfig.from_dict(config_dict)
            if "user" not in data["config"] or data["config"]["user"] is None:
                data["config"]["user"] = getpass.getuser()

            # Overwrite scheduler type and user with authoritative values
            if config.scheduler_type != self.scheduler_type:
                print("Overriding scheduler type from client:", config.scheduler_type, "→", self.scheduler_type)
            config.scheduler_type = self.scheduler_type

            # Submit the job
            job_id = await self.submit_job(config)

            return web.json_response(
                {"success": True, "job_id": job_id, "message": f"Job {job_id} submitted successfully"}
            )

        except Exception as e:
            return web.json_response({"success": False, "error": str(e)}, status=400)

    async def handle_cancel_job(self, request):
        """
        Cancel a running or queued job.

        Parameters
        ----------
        request : aiohttp.web.Request
            HTTP request with job_id in URL path

        Returns
        -------
        aiohttp.web.Response
            JSON response indicating success or failure
        """
        job_id = request.match_info.get("job_id")

        if job_id not in self.jobs:
            return web.json_response({"success": False, "error": f"Job {job_id} not found"}, status=404)

        success = await self.cancel_job(job_id)

        return web.json_response(
            {"success": success, "message": f"Job {job_id} cancellation {'initiated' if success else 'failed'}"}
        )

    async def handle_get_jobs(self, request):
        """
        Get list of all jobs.

        Parameters
        ----------
        request : aiohttp.web.Request
            HTTP request object

        Returns
        -------
        aiohttp.web.Response
            JSON array of job objects with status information
        """
        jobs_data = []
        for job_id, job_info in self.jobs.items():
            jobs_data.append(
                {
                    "id": job_id,
                    "config": job_info.config.to_dict(),
                    "status": job_info.status.value,
                    "start_time": job_info.start_time.isoformat() if job_info.start_time else None,
                    "end_time": job_info.end_time.isoformat() if job_info.end_time else None,
                    "return_code": job_info.return_code,
                    "scheduler_job_id": job_info.scheduler_job_id,
                }
            )

        return web.json_response(jobs_data)

    async def handle_get_resources(self, request):
        """
        Get current resource usage.

        Parameters
        ----------
        request : aiohttp.web.Request
            HTTP request object

        Returns
        -------
        aiohttp.web.Response
            JSON with current host resource usage
        """
        return web.json_response(self.resource_monitor.current_usage)

    async def handle_get_queue(self, request):
        """
        Get queue statistics.

        Parameters
        ----------
        request : aiohttp.web.Request
            HTTP request object

        Returns
        -------
        aiohttp.web.Response
            JSON with queue statistics for dashboard display
        """
        stats = self.job_pool.get_queue_stats()
        logger.info(f"/queue endpoint returning max_concurrent = {stats['max_concurrent']}")
        return web.json_response(stats)

    async def handle_set_priority(self, request):
        """
        Change job priority and re-queue.

        Parameters
        ----------
        request : aiohttp.web.Request
            HTTP POST request with JSON payload

        Returns
        -------
        aiohttp.web.Response
            JSON response indicating success or failure
        """
        job_id = request.match_info.get("job_id")

        if job_id not in self.jobs:
            return web.json_response({"success": False, "error": "Job not found"}, status=404)

        try:
            data = await request.json()
            priority = data.get("priority", 0)

            # Update priority in the pool
            self.job_pool.remove_job(job_id)
            self.job_pool.add_job(job_id, priority)

            return web.json_response({"success": True, "message": f"Priority set to {priority}"})

        except Exception as e:
            return web.json_response({"success": False, "error": str(e)}, status=400)

    async def handle_edit_concurrent_limits(self, request):
        """
        Edit concurrent job limits.

        Parameters
        ----------
        request : aiohttp.web.Request
            HTTP PUT request with JSON payload

        Returns
        -------
        aiohttp.web.Response
            JSON response indicating success or failure
        """
        try:
            data = await request.json()

            if not data:
                return web.json_response({"error": "No data provided"}, status=400)

            # Update the concurrent job limits
            updated_limits = await self.edit_concurrent_limits(data)

            if updated_limits:
                return web.json_response(
                    {"success": True, "message": "Concurrent job limits updated successfully", "limits": updated_limits}
                )
            else:
                return web.json_response({"error": "Failed to update limits"}, status=400)

        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def wait_until_all_done(self) -> None:
        """
        **Coroutine** that blocks until **every** job reaches a terminal state.

        Safe to call from REST handlers or CLI scripts. Polls job status
        until all jobs are completed, failed, or cancelled.
        """
        while True:
            # All jobs that are NOT in a terminal state
            active = [
                j
                for j in self.jobs.values()
                if j.status not in {JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED}
            ]
            if not active:
                return
            await asyncio.sleep(1)  # be nice to the event-loop

    async def submit_job(self, config: HFSSSimulationConfig, priority: int = 0) -> str:
        """
        **Async** entry point for job submission.

        Parameters
        ----------
        config : HFSSSimulationConfig
            Validated simulation configuration.
        priority : int, optional
            Job priority. Default is ``0``.

        Returns
        -------
        str
            Unique job identifier (same as ``config.jobid``).

        Notes
        -----
        This method:
        1. Creates a JobInfo object with QUEUED status
        2. Adds the job to the appropriate queue
        3. Notifies web clients via Socket.IO
        4. Starts the processing loop if not already running
        """
        job_id = config.jobid

        # Create job info
        job_info = JobInfo(config=config, status=JobStatus.QUEUED, priority=priority)
        self.jobs[job_id] = job_info

        # Add to job pool
        self.job_pool.add_job(job_id, priority)

        # Notify web clients
        await self.sio.emit(
            "job_queued",
            {"job_id": job_id, "priority": priority, "queue_position": self.job_pool.get_queue_stats()["total_queued"]},
        )

        logger.info(f"Job {job_id} queued with priority {priority}")

        # Trigger processing if not already running
        if not self._processing_task or self._processing_task.done():
            self._processing_task = asyncio.create_task(self._process_jobs_continuously())

        return job_id

    async def _process_jobs_continuously(self):
        """
        Continuously process jobs until shutdown is requested.

        This is the main job processing loop that:
        - Checks if new jobs can be started based on resource limits
        - Dequeues the highest priority job
        - Starts job execution in a separate task
        - Sleeps when no jobs can be started or queue is empty
        """
        logger.info("✅ Job processing loop started.")
        while not self._shutdown:
            can_start = self.job_pool.can_start_job(self.resource_monitor)
            if can_start:
                next_job_id = self.job_pool.get_next_job()
                if next_job_id:
                    logger.info(f"Dequeued job {next_job_id}. Starting...")
                    self.job_pool.running_jobs.add(next_job_id)
                    asyncio.create_task(self._process_single_job(next_job_id))
                    # Continue immediately to check if we can start more jobs
                    # The running_jobs check will prevent exceeding max_concurrent
                    continue
                else:
                    logger.info("Queue is empty, sleeping.")
                    await asyncio.sleep(1)
            else:
                logger.warning("Cannot start new job, waiting...")
                await asyncio.sleep(5)

    async def _process_single_job(self, job_id: str):
        """
        Process a single job from the pool.

        Parameters
        ----------
        job_id : str
            Job identifier to process

        Notes
        -----
        This method handles:
        - Local execution via subprocess
        - Scheduler submission (SLURM/LSF)
        - Status updates and notifications
        - Error handling and cleanup
        """
        job_info = self.jobs.get(job_id)
        if not job_info or job_info.status != JobStatus.QUEUED:
            self.job_pool.running_jobs.discard(job_id)
            return

        # Update job status
        job_info.status = JobStatus.RUNNING
        job_info.start_time = datetime.now()
        job_info.local_resources = self.resource_monitor.current_usage.copy()

        # Notify web clients
        await self.sio.emit(
            "job_started",
            {"job_id": job_id, "start_time": job_info.start_time.isoformat(), "resources": job_info.local_resources},
        )

        logger.info(f"Job {job_id} started")

        try:
            # Run the simulation
            if job_info.config.scheduler_type != SchedulerType.NONE:
                #  Make sure the executable path is present
                if not job_info.config.ansys_edt_path or not os.path.exists(job_info.config.ansys_edt_path):
                    if self.ansys_path and os.path.exists(self.ansys_path):
                        job_info.config = HFSSSimulationConfig(
                            **{**job_info.config.model_dump(), "ansys_edt_path": self.ansys_path}
                        )
                        logger.info(f"Using JobManager's detected ANSYS path: {self.ansys_path}")
                    else:
                        raise FileNotFoundError(
                            f"ANSYS executable not found. Config path: {job_info.config.ansys_edt_path}, "
                            f"Manager path: {self.ansys_path}"
                        )

                # Now generate the script – the path is guaranteed to be non-empty
                result = job_info.config.submit_to_scheduler()
                job_info.scheduler_job_id = job_info.config._extract_job_id(result.stdout)
                job_info.status = JobStatus.SCHEDULED
                logger.info(
                    f"Job {job_id} submitted to scheduler with ID: {job_info.scheduler_job_id}, status: SCHEDULED"
                )
                await self.sio.emit("job_scheduled", {"job_id": job_id, "scheduler_job_id": job_info.scheduler_job_id})

            else:
                # ----------------  local mode – same guarantee  -----------------
                if not job_info.config.ansys_edt_path or not os.path.exists(job_info.config.ansys_edt_path):
                    if self.ansys_path and os.path.exists(self.ansys_path):
                        job_info.config = HFSSSimulationConfig(
                            **{**job_info.config.model_dump(), "ansys_edt_path": self.ansys_path}
                        )
                        logger.info(f"Using JobManager's detected ANSYS path: {self.ansys_path}")
                    else:
                        raise FileNotFoundError(
                            f"ANSYS executable not found. Config path: {job_info.config.ansys_edt_path}, "
                            f"Manager path: {self.ansys_path}"
                        )

                # Generate command as list for secure execution
                command_list = job_info.config.generate_command_list()

                # Log the command being executed for debugging
                logger.info(f"Executing command for job {job_id}: {' '.join(command_list)}")
                logger.info(f"ANSYS executable path: {job_info.config.ansys_edt_path}")
                logger.info(f"Project path: {job_info.config.project_path}")

                # Check if project file exists
                if not os.path.exists(job_info.config.project_path):
                    raise FileNotFoundError(f"Project file not found: {job_info.config.project_path}")

                # Run locally - using asyncio subprocess for better control with secure command list
                process = await asyncio.create_subprocess_exec(
                    *command_list,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )

                job_info.process = process

                # Wait for completion with timeout (24 hours max)
                try:
                    stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=86400)

                    job_info.return_code = process.returncode
                    job_info.output = stdout.decode() if stdout else ""
                    job_info.error = stderr.decode() if stderr else ""

                    if process.returncode == 0:
                        job_info.status = JobStatus.COMPLETED
                        logger.info(f"Job {job_id} completed successfully")
                    else:
                        job_info.status = JobStatus.FAILED
                        logger.error(f"Job {job_id} failed with return code {process.returncode}")

                except asyncio.TimeoutError:
                    job_info.status = JobStatus.FAILED
                    job_info.error = "Job timed out after 24 hours"
                    process.terminate()
                    logger.error(f"Job {job_id} timed out")

        except Exception as e:
            job_info.status = JobStatus.FAILED
            job_info.error = str(e)
            logger.error(f"Job {job_id} failed with error: {e}")

        finally:
            job_info.end_time = datetime.now()
            self.job_pool.running_jobs.discard(job_id)

            # Notify web clients
            await self.sio.emit(
                "job_completed",
                {
                    "job_id": job_id,
                    "status": job_info.status.value,
                    "end_time": job_info.end_time.isoformat(),
                    "return_code": job_info.return_code,
                },
            )

    async def cancel_job(self, job_id: str) -> bool:
        """
        **Cancel** a queued or running job.

        Parameters
        ----------
        job_id : str
            Identifier returned by :meth:`submit_job`.

        Returns
        -------
        bool
            ``True`` → cancellation succeeded, ``False`` → job not found or
            already terminal.

        Notes
        -----
        For queued jobs: immediately removes from queue and marks as cancelled.
        For running jobs: attempts to terminate the process and cleanup.
        """
        job_info = self.jobs.get(job_id)
        if not job_info:
            return False

        if job_info.status == JobStatus.QUEUED:
            # Remove from queue
            self.job_pool.remove_job(job_id)
            job_info.status = JobStatus.CANCELLED
            job_info.end_time = datetime.now()
            return True

        elif job_info.status == JobStatus.SCHEDULED:
            # Cancel job in external scheduler
            if job_info.scheduler_job_id:
                try:
                    success = await self._sch_mgr.cancel_job(job_info.scheduler_job_id)
                    if success:
                        job_info.status = JobStatus.CANCELLED
                        job_info.end_time = datetime.now()
                        self.job_pool.running_jobs.discard(job_id)
                        logger.info(f"Cancelled scheduler job {job_id} (scheduler ID: {job_info.scheduler_job_id})")
                        return True
                    else:
                        logger.warning(f"Failed to cancel scheduler job {job_info.scheduler_job_id}")
                        return False
                except Exception as e:
                    logger.error(f"Error cancelling scheduler job {job_id}: {e}")
                    return False
            return False

        elif job_info.status == JobStatus.RUNNING and job_info.process:
            try:
                job_info.process.terminate()
                await asyncio.sleep(2)
                if job_info.process.returncode is None:
                    job_info.process.kill()

                job_info.status = JobStatus.CANCELLED
                job_info.end_time = datetime.now()
                return True

            except Exception as e:
                logger.error(f"Failed to cancel job {job_id}: {e}")
                return False

        return False

    async def edit_concurrent_limits(self, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Edit concurrent job limits in the pool.

        Parameters
        ----------
        update_data : dict
            Fields to update in resource limits. Valid fields:
            - max_concurrent_jobs: Positive integer
            - max_cpu_percent: Float between 0 and 100
            - min_memory_gb: Non-negative float
            - min_disk_gb: Non-negative float

        Returns
        -------
        dict or None
            Updated limits data or None if update failed

        Raises
        ------
        ValueError
            If any field validation fails
        """
        try:
            # Define allowed fields for editing
            allowed_fields = ["max_concurrent_jobs", "max_cpu_percent", "min_memory_gb", "min_disk_gb"]

            # Update allowed fields
            updated = False
            old_limits = {}

            for field in allowed_fields:
                if field in update_data:
                    old_value = getattr(self.resource_limits, field)
                    new_value = update_data[field]

                    # Validate the new value
                    if field == "max_concurrent_jobs" and (not isinstance(new_value, int) or new_value < 1):
                        raise ValueError("max_concurrent_jobs must be a positive integer")
                    elif field == "max_cpu_percent" and (
                        not isinstance(new_value, (int, float)) or new_value <= 0 or new_value > 100
                    ):
                        raise ValueError("max_cpu_percent must be between 0 and 100")
                    elif field in ["min_memory_gb", "min_disk_gb"] and (
                        not isinstance(new_value, (int, float)) or new_value < 0
                    ):
                        raise ValueError(f"{field} must be a non-negative number")

                    old_limits[field] = old_value
                    setattr(self.resource_limits, field, new_value)
                    self.job_pool.resource_limits = self.resource_limits
                    updated = True

            if updated:
                # Log the changes
                for field in old_limits:
                    logger.info(
                        f"Resource limit {field} changed from {old_limits[field]} to "
                        f"{getattr(self.resource_limits, field)}"
                    )

                # Notify web clients about the update
                await self.sio.emit(
                    "limits_updated",
                    {
                        "old_limits": old_limits,
                        "new_limits": {
                            "max_concurrent_jobs": self.resource_limits.max_concurrent_jobs,
                            "max_cpu_percent": self.resource_limits.max_cpu_percent,
                            "min_memory_gb": self.resource_limits.min_memory_gb,
                            "min_disk_gb": self.resource_limits.min_disk_gb,
                        },
                    },
                )

                # Return updated limits data
                return {
                    "max_concurrent_jobs": self.resource_limits.max_concurrent_jobs,
                    "max_cpu_percent": self.resource_limits.max_cpu_percent,
                    "min_memory_gb": self.resource_limits.min_memory_gb,
                    "min_disk_gb": self.resource_limits.min_disk_gb,
                }

            return None

        except Exception as e:
            logger.error(f"Failed to update concurrent limits: {e}")
            return None


async def submit_job_to_manager(
    config: HFSSSimulationConfig, priority: int = 0, manager_url: str = "http://localhost:8080"
) -> str:
    """
    **Helper** coroutine that submits a job to a **remote** Job Manager.

    Falls back to **local** execution if the HTTP call fails (offline mode).

    Parameters
    ----------
    config : HFSSSimulationConfig
        Validated configuration.
    priority : int, optional
        Job priority. Default is ``0``.
    manager_url : str, optional
        Base URL of the manager. Default is ``"http://localhost:8080"``.

    Returns
    -------
    str
        Job identifier (local or remote).

    Raises
    ------
    Exception
        If **both** remote and local execution fail.

    Notes
    -----
    This function is useful for clients that want to submit jobs to a
    remote manager but maintain offline capability.
    """
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{manager_url}/jobs/submit"
            async with session.post(url, json={"config": config.to_dict(), "priority": priority}) as response:
                result = await response.json()

                if result["success"]:
                    return result["job_id"]
                else:
                    raise Exception(f"Job submission failed: {result['error']}")

    except Exception as e:
        logger.error(f"Failed to submit job to manager: {e}")
        # Fall back to local execution
        return await config.run_simulation()


# --------------------------------------------------------------------------- #
#  SchedulerManager  –  live SLURM / LSF introspection
# --------------------------------------------------------------------------- #
class SchedulerManager:
    """
    Thin async wrapper around cluster scheduler commands.

    Provides live introspection of SLURM and LSF clusters including:

    * List of partitions / queues with resource information
    * Per-partition: total & free cores, total & free memory
    * Global job table (running, pending, etc.)

    All methods are **coroutines** so they can be awaited from the REST layer
    without blocking the event-loop.

    Parameters
    ----------
    scheduler_type : SchedulerType
        Type of scheduler (SLURM or LSF only)

    Raises
    ------
    ValueError
        If scheduler_type is not SLURM or LSF
    """

    def __init__(self, scheduler_type: SchedulerType):
        if scheduler_type not in {SchedulerType.SLURM, SchedulerType.LSF}:
            raise ValueError("Only SLURM and LSF are supported")
        self.scheduler_type = scheduler_type

    async def get_partitions(self) -> List[Dict[str, Any]]:
        """
        Get list of scheduler partitions/queues with resource information.

        Returns
        -------
        List[Dict[str, Any]]
            List of partition dictionaries with keys:
            - name: Partition/queue name
            - cores_total: Total available cores
            - cores_used: Currently used cores
            - memory_total_gb: Total memory in GB
            - memory_used_gb: Currently used memory in GB

        Raises
        ------
        RuntimeError
            If scheduler command execution fails
        """
        if self.scheduler_type == SchedulerType.SLURM:
            return await self._slurm_partitions()
        else:  # LSF
            return await self._lsf_partitions()

    async def get_jobs(self) -> List[Dict[str, Any]]:
        """
        Get global job table (all users).

        Returns
        -------
        List[Dict[str, Any]]
            List of job dictionaries with keys:
            - job_id: Scheduler job ID
            - partition: Partition/queue name
            - user: Job owner username
            - state: Job state (RUNNING, PENDING, etc.)
            - nodes: Number of nodes allocated
            - cpus: Number of CPUs allocated
            - memory_gb: Memory allocated in GB

        Raises
        ------
        RuntimeError
            If scheduler command execution fails
        """
        if self.scheduler_type == SchedulerType.SLURM:
            return await self._slurm_jobs()
        else:
            return await self._lsf_jobs()

    async def _slurm_partitions(self) -> List[Dict[str, Any]]:
        """Parse SLURM partition information from sinfo command."""
        cmd = ["sinfo", "-h", "-o", "%R %F %C %m"]  # PARTITION NODES(A/I/O/T) CPUS(A/I/O/T) MEMORY
        stdout = await self._run(cmd)
        out = []
        for line in stdout.splitlines():
            if not line.strip():
                continue
            part, node_str, cpu_str, mem_mb = line.split()
            na, ni, no, nt = map(int, node_str.split("/"))
            ca, ci, co, ct = map(int, cpu_str.split("/"))
            mem_total = float(mem_mb.rstrip("+MGTP")) / 1024  # GB
            out.append(
                {
                    "name": part,
                    "nodes_total": nt,
                    "nodes_used": na + no,
                    "cores_total": ct,
                    "cores_used": ca + co,
                    "memory_total_gb": mem_total,
                    "memory_used_gb": mem_total * (na + no) / max(nt, 1),
                }
            )
        return out

    async def _slurm_jobs(self) -> List[Dict[str, Any]]:
        """Parse SLURM job information from squeue command."""
        cmd = ["squeue", "-h", "-o", "%i %u %P %T %D %C %m"]
        stdout = await self._run(cmd)
        jobs = []
        for line in stdout.splitlines():
            if not line.strip():
                continue
            job_id, user, partition, state, nodes, cpus, mem_str = line.split()
            # unify memory to GiB
            mem_str = mem_str.strip()
            if mem_str.endswith(("M", "G", "T")):
                unit = mem_str[-1]
                val = float(mem_str[:-1])
                if unit == "M":
                    memory_gb = val / 1024
                elif unit == "G":
                    memory_gb = val
                else:  # T
                    memory_gb = val * 1024
            else:  # plain number → assume MiB
                memory_gb = float(mem_str) / 1024
            jobs.append(
                {
                    "job_id": job_id,
                    "partition": partition,
                    "user": user,
                    "state": state,
                    "nodes": int(nodes),
                    "cpus": int(cpus),
                    "memory_gb": memory_gb,
                }
            )
        return jobs

    async def _lsf_partitions(self) -> List[Dict[str, Any]]:
        """Parse LSF queue information from bqueues and bhosts commands."""
        # 1. queues → max slots
        qraw = await self._run(["bqueues", "-o", "queue_name:20 max:10 num_proc:10", "-noheader"])
        qinfo = {}
        for ln in qraw.splitlines():
            if not ln.strip():
                continue
            name, max_s, num_p = ln.split()
            qinfo[name] = {
                "nodes_total": int(num_p),
                "nodes_used": 0,
                "cores_total": int(num_p),
                "cores_used": 0,
                "mem_total_gb": 0.0,
                "mem_used_gb": 0.0,
            }

        # 2. hosts → real cores + real memory
        hraw = await self._run(["bhosts", "-o", "host_name:20 ncpus:10 max_mem:15", "-noheader"])
        for ln in hraw.splitlines():
            if not ln.strip():
                continue
            host, ncpus, max_mem_kb = ln.split()
            max_mem_gb = int(max_mem_kb) / 1024**2
            for q in qinfo.values():
                q["mem_total_gb"] += max_mem_gb
                # LSF does not give per-host used mem; keep 0 for now
        return [{"name": q, **qinfo[q]} for q in qinfo]

    async def _lsf_jobs(self) -> List[Dict[str, Any]]:
        """Parse LSF job information from bjobs command."""
        cmd = ["bjobs", "-u", "all", "-o", "jobid:10 user:15 queue:15 stat:10 slots:10 mem:10", "-noheader"]
        stdout = await self._run(cmd)
        jobs = []
        for line in stdout.splitlines():
            if not line.strip():
                continue
            job_id, user, queue, state, slots, mem = line.split()
            jobs.append(
                {
                    "job_id": job_id,
                    "partition": queue,
                    "user": user,
                    "state": state,
                    "nodes": 1,  # LSF does not expose node count directly
                    "cpus": int(slots),
                    "memory_gb": int(mem) / 1024 if mem.isdigit() else float(mem),
                }
            )
        return jobs

    async def _run(self, cmd: List[str]) -> str:
        """
        Run scheduler command and return output.

        Parameters
        ----------
        cmd : List[str]
            Command and arguments to execute

        Returns
        -------
        str
            Command stdout as string

        Raises
        ------
        RuntimeError
            If command returns non-zero exit code
        """
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"{' '.join(cmd)} failed: {stderr.decode()}")
        return stdout.decode().strip()


# Usage example
async def main():
    """
    Example usage of the JobManager class.

    This demonstrates how to create a job manager with custom resource
    limits and submit jobs with different priorities.
    """
    # Create job manager with custom resource limits
    resource_limits = ResourceLimits(
        max_concurrent_jobs=3,  # Allow 3 simultaneous jobs
        max_cpu_percent=75.0,  # Don't start jobs if CPU > 75%
        min_memory_gb=4.0,  # Require 4GB free memory
        min_disk_gb=20.0,  # Require 20GB free disk space
    )

    manager = JobManager(resource_limits)


if __name__ == "__main__":
    asyncio.run(main())
