# job_manager_service.py
"""
Enhanced Job Manager with Sophisticated Pool Management for Local Resources
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
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SCHEDULED = "scheduled"
    QUEUED = "queued"  # Specifically for local queue


@dataclass
class ResourceLimits:
    """Resource limits for job scheduling."""

    max_concurrent_jobs: int = 2
    max_cpu_percent: float = 80.0  # Don't start new jobs if CPU > 80%
    min_memory_gb: float = 2.0  # Minimum free memory required to start a job
    min_disk_gb: float = 10.0  # Minimum free disk space required


@dataclass
class JobInfo:
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
    """Manages the job pool with sophisticated scheduling algorithms."""

    def __init__(self, resource_limits: ResourceLimits):
        self.resource_limits = resource_limits
        self.job_queue: Deque[str] = deque()  # FIFO queue for job IDs
        self.priority_queue: Dict[int, List[str]] = {}  # Priority-based queue
        self.running_jobs: Set[str] = set()
        self.job_priorities: Dict[str, int] = {}

    def add_job(self, job_id: str, priority: int = 0):
        """Add a job to the appropriate queue based on priority."""
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
        """Get the next job to process based on priority and queue order."""
        # First check priority queues (highest priority first)
        for priority in sorted(self.priority_queue.keys(), reverse=True):
            if self.priority_queue[priority]:
                return self.priority_queue[priority].pop(0)

        # Then check regular queue
        if self.job_queue:
            return self.job_queue.popleft()

        return None

    def remove_job(self, job_id: str):
        """Remove a job from all queues."""
        if job_id in self.job_queue:
            self.job_queue.remove(job_id)

        for priority, jobs in self.priority_queue.items():
            if job_id in jobs:
                jobs.remove(job_id)

        if job_id in self.job_priorities:
            del self.job_priorities[job_id]

    def can_start_job(self, resource_monitor: ResourceMonitor) -> bool:
        """Check if system resources allow starting a new job."""
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
        """Get statistics about the job queue."""
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
    """Job Manager with pool management."""

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
        self._processing_task = None

    def setup_routes(self):
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
        """Submit a new job."""
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
        """Cancel a running job."""
        job_id = request.match_info.get("job_id")

        if job_id not in self.jobs:
            return web.json_response({"success": False, "error": f"Job {job_id} not found"}, status=404)

        success = await self.cancel_job(job_id)

        return web.json_response(
            {"success": success, "message": f'Job {job_id} cancellation {"initiated" if success else "failed"}'}
        )

    async def handle_get_jobs(self, request):
        """Return list of all jobs."""
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
        """Return current resource usage."""
        return web.json_response(self.resource_monitor.current_usage)

    async def handle_get_queue(self, request):
        """Return queue statistics."""
        return web.json_response(self.job_pool.get_queue_stats())

    async def handle_set_priority(self, request):
        """Set job priority."""
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

    async def submit_job(self, config: HFSSSimulationConfig, priority: int = 0) -> str:
        """Submit a job to the pool with optional priority."""
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
        """Continuously process jobs from the pool."""
        while True:
            try:
                # Check if we can start a new job
                if self.job_pool.can_start_job(self.resource_monitor):
                    next_job_id = self.job_pool.get_next_job()

                    if next_job_id:
                        # Process the job
                        self.job_pool.running_jobs.add(next_job_id)
                        asyncio.create_task(self._process_single_job(next_job_id))
                    else:
                        # No jobs in queue, wait a bit
                        await asyncio.sleep(1)
                else:
                    # Resources constrained, wait before checking again
                    await asyncio.sleep(5)

            except Exception as e:
                logger.error(f"Job processing error: {e}")
                await asyncio.sleep(5)

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
        """Cancel a job from any state."""
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
    Submit a job to the job manager service with priority support.
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
