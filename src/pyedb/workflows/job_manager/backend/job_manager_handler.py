"""
``job_manager_handler`` --- Thread-safe façade for the async ANSYS Job Manager
================================================================================

This module exposes a **synchronous, production-grade** entry point to the
**asynchronous** job manager service. A background daemon thread hosts an
``aiohttp`` web server that schedules and monitors HFSS/3D-Layout simulations
on the local machine or external clusters (SLURM, LSF, PBS, Windows-HPC).

The handler guarantees:

* **Non-blocking** start/stop semantics for the caller thread.
* **Graceful shutdown** via ``atexit`` or explicit ``close()``.
* **Thread-safe** job submission and cancellation.
* **Global timeout** support for batched workloads.
* **Zero configuration** when used with PyEDB ``Edb`` objects.
"""

import asyncio
from asyncio import run_coroutine_threadsafe
import atexit
import concurrent.futures as _futs
import os
import platform
import shutil
import sys
import threading
from typing import Optional
import uuid

from aiohttp import web
import socketio

from pyedb.generic.general_methods import is_linux
from pyedb.workflows.job_manager.backend.job_submission import SchedulerType, create_hfss_config
from pyedb.workflows.job_manager.backend.service import JobManager, ResourceLimits, SchedulerManager


class JobManagerHandler:
    """
    Synchronous façade that controls an **async** Job Manager service.
    This class now includes the aiohttp server and WebSocket implementation.
    """

    def __init__(self, edb=None, version=None, host="localhost", port=8080):
        if edb:
            self.ansys_path = os.path.join(edb.base_path, "ansysedt" if is_linux else "ansysedt.exe")
        else:
            from pyedb.generic.general_methods import installed_ansys_em_versions

            installed_versions = installed_ansys_em_versions()
            if not version:
                self.ansys_path = list(installed_versions.values())[-1]  # latest
            else:
                if version not in installed_versions:
                    raise ValueError(f"ANSYS release {version} not found")
                self.ansys_path = installed_versions[version]

        self.manager = JobManager()
        self.manager.resource_limits = ResourceLimits(max_concurrent_jobs=2)
        self.manager.jobs = {}  # In-memory job store for demonstration

        self.host, self.port = host, port
        self._url = f"http://{host}:{port}"

        # --- NEW: Setup aiohttp and Socket.IO server ---
        self.sio = socketio.AsyncServer(async_mode="aiohttp", cors_allowed_origins="*")
        self.app = self._create_web_app()
        self.sio.attach(self.app)
        # -----------------------------------------------

        self.runner: Optional[web.AppRunner] = None
        self.site = None
        self.started = False
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._start_event = threading.Event()
        self._shutdown = False
        atexit.register(self.close)

        self.scheduler_type = self._detect_scheduler()
        self._sch_mgr: Optional[SchedulerManager] = None

    def _create_web_app(self) -> web.Application:
        """Create and configure the aiohttp web application and its routes."""
        app = web.Application()

        async def get_system_status(request):
            """Endpoint to provide system and scheduler status."""
            running_jobs = sum(1 for job in self.manager.jobs.values() if job["status"] == "running")
            queued_jobs = sum(1 for job in self.manager.jobs.values() if job["status"] == "queued")
            status = {
                "scheduler_detection": {
                    "active_scheduler": self.scheduler_type.value,
                    "detected_by": "JobManagerHandler._detect_scheduler()",
                    "backend_available": True,
                },
                "mode": "local" if self.scheduler_type == SchedulerType.NONE else "scheduler",
                "local_pool": {
                    "running_jobs": running_jobs,
                    "queued_jobs": queued_jobs,
                    "max_concurrent": self.manager.resource_limits.max_concurrent_jobs,
                },
            }
            return web.json_response(status)

        async def submit_job(request):
            """Endpoint to submit a new job."""
            try:
                data = await request.json()
                priority = data.get("priority", 0)

                if not data.get("project_path"):
                    return web.json_response({"success": False, "error": "project_path is required"}, status=400)

                sim_config = self.create_simulation_config(
                    project_path=data["project_path"],
                    jobid=data.get("jobid"),
                    scheduler_type=self.scheduler_type,
                    ansys_edt_path=data.get("ansys_edt_path"),
                )

                # Populate all possible values from request data
                config_fields = [
                    "design_name",
                    "setup_name",
                    "sweep_name",
                    "solution_name",
                    "working_dir",
                    "output_dir",
                    "num_cores",
                    "memory_limit_gb",
                    "time_limit_hours",
                    "partition",
                    "queue",
                    "environment_vars",
                    "additional_args",
                ]

                for field in config_fields:
                    if field in data:
                        setattr(sim_config, field, data[field])

                job_id = await self.manager.submit_job(sim_config, priority)
                return web.json_response({"success": True, "job_id": job_id})
            except Exception as e:
                return web.json_response({"success": False, "error": str(e)}, status=500)

        async def get_all_jobs(request):
            """Endpoint to get the list of all jobs."""
            return web.json_response(list(self.manager.jobs.values()))

        async def get_queue_stats(request):
            """Endpoint to get queue statistics."""
            running_jobs = sum(1 for job in self.manager.jobs.values() if job["status"] == "running")
            queued_jobs = sum(1 for job in self.manager.jobs.values() if job["status"] == "queued")
            return web.json_response(
                {
                    "running_jobs": running_jobs,
                    "total_queued": queued_jobs,
                    "max_concurrent": self.manager.resource_limits.max_concurrent_jobs,
                }
            )

        async def edit_concurrent_limits(request):
            """Endpoint to edit concurrent job limits in the pool"""
            try:
                data = await request.json()

                if not data:
                    return web.json_response({"error": "No data provided"}, status=400)

                # Update the concurrent job limits
                updated_limits = await self.manager.edit_concurrent_limits(data)

                if updated_limits:
                    return web.json_response(
                        {
                            "success": True,
                            "message": "Concurrent job limits updated successfully",
                            "limits": updated_limits,
                        }
                    )
                else:
                    return web.json_response({"error": "Failed to update limits"}, status=400)

            except Exception as e:
                return web.json_response({"error": str(e)}, status=500)

        app.router.add_get("/system/status", get_system_status)
        app.router.add_post("/jobs/submit", submit_job)
        app.router.add_get("/jobs", get_all_jobs)
        app.router.add_get("/queue", get_queue_stats)
        app.router.add_put("/pool/limits", edit_concurrent_limits)

        return app

    @staticmethod
    def _detect_scheduler() -> SchedulerType:
        if platform.system() == "Windows":
            return SchedulerType.NONE
        for cmd, enum in (("sinfo", SchedulerType.SLURM), ("bhosts", SchedulerType.LSF)):
            if shutil.which(cmd) is not None:
                return enum
        return SchedulerType.NONE

    @property
    def url(self) -> str:
        return self._url

    def start_service(self) -> None:
        if self.started:
            return
        self._thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self._thread.start()
        if not self._start_event.wait(timeout=10):
            raise RuntimeError("Job-Manager service failed to start within 10 s")

    async def _start_site(self) -> None:
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, self.host, self.port)
        await self.site.start()
        self.started = True
        self._start_event.set()

    def close(self) -> None:
        if not self.started or not self._loop:
            return
        coro = self.stop_service()
        try:
            run_coroutine_threadsafe(coro, self._loop).result(timeout=10)
        except (_futs.TimeoutError, asyncio.TimeoutError):
            print("Warning: Service did not shut down gracefully.", file=sys.stderr)
        self.started = False

    async def stop_service(self) -> None:
        if not self.started:
            return
        self._shutdown = True
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()
        self.started = False

    def _run_event_loop(self) -> None:
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._start_site())
        self._loop.run_forever()

    def create_simulation_config(self, project_path, ansys_edt_path=None, jobid=None, scheduler_type=None):
        if not project_path:
            raise ValueError("Project path must be provided")
        if not ansys_edt_path:
            ansys_edt_path = self.ansys_path
        if not jobid:
            jobid = os.path.splitext(os.path.basename(project_path))[0] + f"_{uuid.uuid4().hex[:6]}"
        if not scheduler_type:
            scheduler_type = SchedulerType.NONE

        return create_hfss_config(
            ansys_edt_path=ansys_edt_path, jobid=jobid, project_path=project_path, scheduler_type=scheduler_type
        )


if __name__ == "__main__":
    # Simplified CLI for starting the service
    handler = JobManagerHandler(host="localhost", port=8080)
    handler.start_service()
    print(f"✅ Job-manager backend listening on http://{handler.host}:{handler.port}")
    try:
        threading.Event().wait()  # Keep main thread alive
    except KeyboardInterrupt:
        print("\nShutting down...")
        handler.close()
        sys.exit(0)
