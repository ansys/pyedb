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

from pyedb.generic.general_methods import is_linux
from pyedb.workflows.job_manager.backend.job_submission import (
    HFSS3DLayoutBatchOptions,
    SchedulerType,
    create_hfss_config,
)
from pyedb.workflows.job_manager.backend.service import JobManager, ResourceLimits, SchedulerManager


@web.middleware
async def cors_middleware(request, handler):
    response = await handler(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


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
                self.ansys_path = os.path.join(list(installed_versions.values())[-1], "ansysedt.exe")  # latest
            else:
                if version not in installed_versions:
                    raise ValueError(f"ANSYS release {version} not found")
                self.ansys_path = os.path.join(installed_versions[version], "ansysedt.exe")

        self.manager = JobManager()
        self.manager.resource_limits = ResourceLimits(max_concurrent_jobs=2)
        self.manager.jobs = {}  # In-memory job store for demonstration
        # Pass the detected ANSYS path to the manager
        self.manager.ansys_path = self.ansys_path

        self.host, self.port = host, port
        self._url = f"http://{host}:{port}"

        # --- NEW: Setup aiohttp and Socket.IO server ---
        self.sio = self.manager.sio
        self.app = self.manager.app
        self.app.middlewares.append(cors_middleware)
        self._add_routes()
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
        if self.scheduler_type != SchedulerType.NONE:
            self._sch_mgr = SchedulerManager(self.scheduler_type)

    def _add_routes(self):
        self.app.router.add_get("/api/jobs", self.get_jobs)
        self.app.router.add_get("/api/scheduler_type", self.get_scheduler_type)
        self.app.router.add_get("/api/cluster_partitions", self.get_cluster_partitions)
        self.app.router.add_post("/api/submit", self.submit_job)
        self.app.router.add_post("/api/cancel/{job_id}", self.cancel_job)

    async def get_jobs(self, request):
        return web.json_response(list(self.manager.jobs.values()))

    async def get_scheduler_type(self, request):
        return web.json_response({"scheduler_type": self.scheduler_type.value})

    async def get_cluster_partitions(self, request):
        if self._sch_mgr:
            partitions = await self._sch_mgr.get_partitions()
            return web.json_response(partitions)
        return web.json_response([])

    async def submit_job(self, request):
        data = await request.json()
        project_path = data.get("project_path")
        options_data = data.get("batch_options", {})
        batch_options = HFSS3DLayoutBatchOptions(**options_data)

        config = self.create_simulation_config(
            project_path=project_path,
            ansys_edt_path=self.ansys_path,  # Use the detected ANSYS path
            scheduler_type=self.scheduler_type,
        )
        config.batch_options = batch_options
        job_id = await self.manager.submit_job(config)
        return web.json_response({"job_id": job_id})

    async def cancel_job(self, request):
        job_id = request.match_info["job_id"]
        await self.manager.cancel(job_id)
        return web.json_response({"status": "cancelled"})

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
