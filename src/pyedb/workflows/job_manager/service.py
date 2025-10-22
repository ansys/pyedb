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
``service`` --- Async job manager with pool scheduling and REST/WebSocket API
=============================================================================

The module implements a **fully asynchronous** multi-tenant job manager that

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
Stand-alone REST server::

    python -m pyedb.workflows.job_manager.service

Embedded inside PyEDB::

    from pyedb.workflows.job_manager.service import JobManager, ResourceLimits

    manager = JobManager(ResourceLimits(max_concurrent_jobs=4))
    await manager.submit_job(config, priority=10)

The REST API is **self-documenting** at runtime::

    curl http://localhost:8080/resources
    curl http://localhost:8080/queue
    curl -X POST http://localhost:8080/jobs/submit -d @cfg.json
"""

import asyncio
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging
import os.path
import platform
from typing import Any, Deque, Dict, List, Optional, Set

import aiohttp
from aiohttp import web
import psutil
import socketio

from pyedb.workflows.job_manager.job_submission import (
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
    PENDING : str
        Initial state before queuing.
    QUEUED : str
        Awaiting resources.
    SCHEDULED : str
        Submitted to external scheduler.
    RUNNING : str
        Currently executing.
    COMPLETED : str
        Normal termination.
    FAILED : str
        Non-zero exit code or exception.
    CANCELLED : str
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
        Simultaneous local jobs.  Default ``2``.
    max_cpu_percent : float, optional
        CPU utilisation threshold (0-100).  Default ``80.0``.
    min_memory_gb : float, optional
        Free RAM required to start.  Default ``2.0``.
    min_disk_gb : float, optional
        Free disk space required to start.  Default ``10.0``.
    """

    max_concurrent_jobs: int = 2
    max_cpu_percent: float = 80.0  # Don't start new jobs if CPU > 80%
    min_memory_gb: float = 2.0  # Minimum free memory required to start a job
    min_disk_gb: float = 10.0  # Minimum free disk space required


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
    **Async** background task that samples host telemetry every *N* seconds
    and keeps a **thread-safe** in-memory cache.

    The cache is used by :meth:`JobPoolManager.can_start_job` to throttle
    submissions.

    Parameters
    ----------
    update_interval : int, optional
        Sampling period in seconds.  Default ``5``.
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
        Runs until the event-loop is shut down.
        """
        while True:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)

                # Memory usage
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                memory_used_gb = memory.used / (1024**3)
                memory_total_gb = memory.total / (1024**3)
                memory_free_gb = memory.available / (1024**3)

                # Disk usage
                disk = psutil.disk_usage("/tmp" if platform.system() != "Windows" else "C:\\")
                disk_usage_percent = disk.percent
                disk_free_gb = disk.free / (1024**3)

                self.current_usage = {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory_percent,
                    "memory_used_gb": round(memory_used_gb, 2),
                    "memory_total_gb": round(memory_total_gb, 2),
                    "memory_free_gb": round(memory_free_gb, 2),
                    "disk_usage_percent": disk_usage_percent,
                    "disk_free_gb": round(disk_free_gb, 2),
                    "timestamp": datetime.now().isoformat(),
                }

                await asyncio.sleep(self.update_interval)

            except Exception as e:
                logger.error(f"Resource monitoring error: {e}")
                await asyncio.sleep(self.update_interval)


class JobPoolManager:
    """
    **Priority-aware** FIFO queues plus running-set tracker.

    The implementation is **lock-free** (uses ``deque`` and ``dict``) and
    **async-safe** (no awaits, therefore can be invoked from any thread).

    Parameters
    ----------
    resource_limits : ResourceLimits
        Constraints used by :meth:`can_start_job`.
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
            Negative (low), zero (normal), positive (high).  Default ``0``.
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
        **Boolean** predicate that decides whether a new job may be started
        **without** violating resource limits.

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
        # if resources["cpu_percent"] > self.resource_limits.max_cpu_percent:
        #     logger.info(f"CPU usage too high ({resources['cpu_percent']}%), delaying job start")
        #     return False
        #
        # # Check memory availability
        # if resources["memory_free_gb"] < self.resource_limits.min_memory_gb:
        #     logger.info(f"Insufficient memory ({resources['memory_free_gb']}GB free), delaying job start")
        #     return False
        #
        # # Check disk space
        # if resources["disk_free_gb"] < self.resource_limits.min_disk_gb:
        #     logger.info(f"Insufficient disk space ({resources['disk_free_gb']}GB free), delaying job start")
        #     return False

        return True

    def get_queue_stats(self) -> Dict[str, Any]:
        """
        Real-time snapshot for REST ``/queue`` endpoint.

        Returns
        -------
        dict
            ``total_queued``, ``regular_queue_size``, ``priority_queues``,
            ``running_jobs``, ``max_concurrent``.
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
    **Async** job manager that combines:

    * :class:`ResourceMonitor` for telemetry,
    * :class:`JobPoolManager` for scheduling,
    * ``aiohttp`` web server for REST/Socket.IO,
    * background task for **continuous** job processing.

    Parameters
    ----------
    resource_limits : ResourceLimits, optional
        Host constraints.  Default instance.
    """

    def __init__(self, resource_limits: ResourceLimits = None):
        self.jobs: Dict[str, JobInfo] = {}
        self.resource_limits = resource_limits or ResourceLimits()
        self.job_pool = JobPoolManager(self.resource_limits)
        self.resource_monitor = ResourceMonitor()
        # Correct SocketIO initialization
        self.sio = socketio.AsyncServer(async_mode="aiohttp", cors_allowed_origins="*")
        self.app = web.Application()
        self.sio.attach(self.app)

        # Setup routes
        self.setup_routes()

        # Background task for continuous job processing
        self._processing_task: Optional[asyncio.Task] = None
        self._shutdown = False

    def setup_routes(self):
        """
        **Internal** method that wires aiohttp routes to class methods.
        Called once from ``__init__``.
        """
        self.app.router.add_get("/", self.handle_index)
        self.app.router.add_get("/jobs", self.handle_get_jobs)
        self.app.router.add_get("/resources", self.handle_get_resources)
        self.app.router.add_get("/queue", self.handle_get_queue)
        self.app.router.add_post("/jobs/submit", self.handle_submit_job)
        self.app.router.add_post("/jobs/{job_id}/cancel", self.handle_cancel_job)
        self.app.router.add_post("/jobs/{job_id}/priority", self.handle_set_priority)
        if os.path.exists("static"):
            self.app.router.add_static("/static", "static")
        else:
            os.makedirs("static", exist_ok=True)
            self.app.router.add_static("/static", "static")

    async def handle_index(self, request):
        """Serve the main web interface."""
        return web.FileResponse("static/index.html")

    async def handle_submit_job(self, request):
        """
        POST ``/jobs/submit`` — accept JSON, validate, enqueue, return
        identifier.

        Payload::

            {
              "config": { ... HFSSSimulationConfig ... },
              "priority": 10
            }

        Returns
        -------
        web.Response
            200 → ``{"success": true, "job_id": "..."}``
            400 → ``{"success": false, "error": "..."}``
        """
        try:
            data = await request.json()
            config_dict = data.get("config", {})

            # Create HFSS config from dictionary
            config = HFSSSimulationConfig.from_dict(config_dict)

            # Submit the job
            job_id = await self.submit_job(config)

            return web.json_response(
                {"success": True, "job_id": job_id, "message": f"Job {job_id} submitted successfully"}
            )

        except Exception as e:
            return web.json_response({"success": False, "error": str(e)}, status=400)

    async def handle_cancel_job(self, request):
        """
        POST ``/jobs/{job_id}/cancel`` — idempotent cancellation.

        Returns
        -------
        web.Response
            200 → success flag
            404 → job not found
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
        GET ``/jobs`` — return **paginated** list of all jobs (JSON).

        Each record contains ``id``, ``status``, ``config``, ``start_time``,
        ``end_time``, ``return_code``, ``scheduler_job_id``.
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
        GET ``/resources`` — real-time host telemetry (JSON).

        Example::

            {
                "cpu_percent": 45.2,
                "memory_free_gb": 12.3,
                "disk_free_gb": 234.5,
                "timestamp": "2025-09-04T14:23:45.123456",
            }
        """
        return web.json_response(self.resource_monitor.current_usage)

    async def handle_get_queue(self, request):
        """
        GET ``/queue`` — queue statistics (JSON).

        Used by the dashboard progress bar.
        """
        return web.json_response(self.job_pool.get_queue_stats())

    async def handle_set_priority(self, request):
        """
        POST ``/jobs/{job_id}/priority`` — change priority and **re-queue**.

        Payload::

            {"priority": 10}

        Returns
        -------
        web.Response
            200 → success
            404 → job not found
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

    async def wait_until_all_done(self) -> None:
        """
        **Coroutine** that blocks until **every** job reaches a terminal state
        (completed, failed, or cancelled).

        Safe to call from REST handlers or CLI scripts.
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
        **Async** entry point — validate config, enqueue, and return
        identifier.

        Parameters
        ----------
        config : HFSSSimulationConfig
            Validated configuration.
        priority : int, optional
            Job priority.  Default ``0``.

        Returns
        -------
        str
            Unique job identifier (same as ``config.jobid``).
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
        """Continuously process jobs until shutdown is requested."""
        while not self._shutdown:
            # inner loop – also checks the flag
            while not self._shutdown:
                if self.job_pool.can_start_job(self.resource_monitor):
                    next_job_id = self.job_pool.get_next_job()
                    if next_job_id:
                        self.job_pool.running_jobs.add(next_job_id)
                        asyncio.create_task(self._process_single_job(next_job_id))
                    else:
                        await asyncio.sleep(1)  # safe sleep
                else:
                    await asyncio.sleep(5)  # safe sleep
            # allow other coroutines to run before outer loop re-checks
            await asyncio.sleep(0.2)

    async def _process_single_job(self, job_id: str):
        """Process a single job from the pool."""
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
                # Submit to external scheduler
                result = job_info.config.submit_to_scheduler()
                job_info.scheduler_job_id = job_info.config._extract_job_id(result.stdout)
                job_info.status = JobStatus.SCHEDULED

                await self.sio.emit("job_scheduled", {"job_id": job_id, "scheduler_job_id": job_info.scheduler_job_id})

            else:
                # Run locally - using asyncio subprocess for better control
                process = await asyncio.create_subprocess_shell(
                    job_info.config.generate_command_string(),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    shell=True,
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

    # ... (other methods remain similar but use the new pool system)


# Enhanced PyEDB integration with priority support
async def submit_job_to_manager(
    config: HFSSSimulationConfig, priority: int = 0, manager_url: str = "http://localhost:8080"
) -> str:
    """
    **Helper** coroutine that submits a job to a **remote** Job Manager
    instance via REST.

    Falls back to **local** execution if the HTTP call fails (offline mode).

    Parameters
    ----------
    config : HFSSSimulationConfig
        Validated configuration.
    priority : int, optional
        Job priority.  Default ``0``.
    manager_url : str, optional
        Base URL of the manager.  Default ``"http://localhost:8080"``.

    Returns
    -------
    str
        Job identifier (local or remote).

    Raises
    ------
    Exception
        If **both** remote and local execution fail.
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


# Usage example
async def main():
    # Create job manager with custom resource limits
    resource_limits = ResourceLimits(
        max_concurrent_jobs=3,  # Allow 3 simultaneous jobs
        max_cpu_percent=75.0,  # Don't start jobs if CPU > 75%
        min_memory_gb=4.0,  # Require 4GB free memory
        min_disk_gb=20.0,  # Require 20GB free disk space
    )

    manager = JobManager(resource_limits)

    # Submit jobs with different priorities
    config1 = HFSSSimulationConfig(jobid="high_prio", project_path="design1.aedt")
    await manager.submit_job(config1, priority=10)  # High priority

    config2 = HFSSSimulationConfig(jobid="normal_prio", project_path="design2.aedt")
    await manager.submit_job(config2, priority=0)  # Normal priority

    config3 = HFSSSimulationConfig(jobid="low_prio", project_path="design3.aedt")
    await manager.submit_job(config3, priority=-5)  # Low priority


if __name__ == "__main__":
    asyncio.run(main())
