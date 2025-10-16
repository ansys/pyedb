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
import getpass
import os
from pathlib import Path
import platform
import shutil
import ssl
import sys
import threading
from typing import Optional
import uuid

import aiohttp
from aiohttp import web
from yarl import URL

from pyedb.generic.general_methods import is_linux
from pyedb.workflows.job_manager.backend.job_submission import (
    HFSS3DLayoutBatchOptions,
    HFSSSimulationConfig,
    MachineNode,
    SchedulerType,
    create_hfss_config,
)
from pyedb.workflows.job_manager.backend.service import JobManager, ResourceLimits, SchedulerManager
from pyedb.workflows.log_parser.hfss_log_parser import HFSSLogParser


def get_session(url: str) -> aiohttp.ClientSession:
    """
    Return an aiohttp.ClientSession.

    Parameters
    ----------
    url : str
        Base URL; used only to decide whether TLS verification is required.
    """
    timeout = aiohttp.ClientTimeout(total=30)

    # --- actually use the url ----------------------------------------------
    tls = url.lower().startswith("https://")
    ssl_context = ssl.create_default_context() if tls else False
    # -----------------------------------------------------------------------

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:  # synchronous context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return aiohttp.ClientSession(
        timeout=timeout,
        headers={"User-Agent": "pyedb-job-manager/1.0"},
        connector=aiohttp.TCPConnector(
            limit=20,
            limit_per_host=10,
            ssl=ssl_context,
            loop=loop,
        ),
        loop=loop,
    )


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
            if is_linux:
                self.ansys_path = os.path.join(edb.base_path, "ansysedt" if is_linux else "ansysedt")
            else:
                self.ansys_path = os.path.join(edb.base_path, "ansysedt" if is_linux else "ansysedt.exe")
        else:
            from pyedb.generic.general_methods import installed_ansys_em_versions

            installed_versions = installed_ansys_em_versions()
            if not version:
                if is_linux:
                    self.ansys_path = os.path.join(list(installed_versions.values())[-1], "ansysedt")  # latest
                else:
                    self.ansys_path = os.path.join(list(installed_versions.values())[-1], "ansysedt.exe")  # latest
            else:
                if version not in installed_versions:
                    raise ValueError(f"ANSYS release {version} not found")
                if is_linux:
                    self.ansys_path = os.path.join(installed_versions[version], "ansysedt")
                else:
                    self.ansys_path = os.path.join(installed_versions[version], "ansysedt.exe")
        self.scheduler_type = self._detect_scheduler()
        self.manager = JobManager(scheduler_type=self.scheduler_type)
        self.manager.resource_limits = ResourceLimits(max_concurrent_jobs=1)
        self.manager.jobs = {}  # In-memory job store -TODO add persistence database
        # Pass the detected ANSYS path to the manager
        self.manager.ansys_path = self.ansys_path

        self.host, self.port = host, port
        self._url = f"http://{host}:{port}"

        # Setup aiohttp and Socket.IO server ---
        self.sio = self.manager.sio
        self.app = self.manager.app
        self.app.middlewares.append(cors_middleware)
        self._add_routes()
        # ----------------------------------------

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
        self.app.router.add_get("/api/queue", self.get_queue_status)
        self.app.router.add_get("/api/resources", self.get_resources)
        self.app.router.add_get("/api/scheduler_type", self.get_scheduler_type)
        self.app.router.add_get("/api/cluster_partitions", self.get_cluster_partitions)
        self.app.router.add_post("/api/submit", self.submit_job)
        self.app.router.add_post("/api/cancel/{job_id}", self.cancel_job)
        self.app.router.add_get("/api/jobs/{job_id}/log", self.get_job_log)
        self.app.router.add_get("/api/me", self.get_me)
        self.app.router.add_get("/system/status", self.get_system_status)
        self.app.router.add_post("/jobs/submit", self.submit_job)

    def _find_latest_log(self, project_path: str) -> Path | None:
        """
        Return the newest *.log file inside the newest *.aedb.batchinfo folder
        that ANSYS creates next to the project.
        """
        proj = Path(project_path).resolve()
        base = proj.with_suffix("")  # strip .aedt / .aedb
        batch_parent = proj.parent  # folder that contains the project

        # all timestamped folders:  <proj>.aedb.batchinfo.<timestamp>
        batch_folders = sorted(
            batch_parent.glob(f"{base.name}.aedb.batchinfo*"), key=lambda p: p.stat().st_mtime, reverse=True
        )
        for bf in batch_folders:
            # newest *.log inside that folder
            try:
                return max(bf.glob("*.log"), key=lambda p: p.stat().st_mtime)
            except ValueError:  # no *.log here
                continue
        return None

    async def get_system_status(self, request):
        """Return the real scheduler that was detected at start-up."""
        return web.json_response(
            {
                "mode": self.scheduler_type.value,  # ← real value: "slurm", "lsf", "none"
                "scheduler_detection": {
                    "active_scheduler": self.scheduler_type.name,
                    "detected_by": "JobManagerHandler",
                },
            }
        )

    async def get_me(self, request):
        """Return the login name of the process that owns the server."""
        import getpass

        return web.json_response({"username": getpass.getuser()})

    async def get_jobs(self, request):
        jobs_data = []
        for job_id, job_info in self.manager.jobs.items():
            jobs_data.append(
                {
                    "id": job_id,
                    "user": job_info.config.user or getpass.getuser(),
                    "config": job_info.config.to_dict(),
                    "status": job_info.status.value,
                    "start_time": job_info.start_time.isoformat() if job_info.start_time else None,
                    "end_time": job_info.end_time.isoformat() if job_info.end_time else None,
                    "return_code": job_info.return_code,
                    "scheduler_job_id": job_info.scheduler_job_id,
                    "priority": job_info.priority,
                }
            )
        return web.json_response(jobs_data)

    async def get_scheduler_type(self, request):
        return web.json_response({"scheduler_type": self.scheduler_type.value})

    async def get_cluster_partitions(self, request):
        if self._sch_mgr:
            partitions = await self._sch_mgr.get_partitions()
            return web.json_response(partitions)
        return web.json_response([])

    # job_manager_handler.py  (add as a new coroutine)

    async def get_job_log(self, request):
        """
        Return parsed HFSS log for a finished job.
        204 No Content when log is not available yet.
        """
        job_id = request.match_info["job_id"]
        job_info = self.manager.jobs.get(job_id)
        if not job_info:
            return web.json_response({"error": "Job not found"}, status=404)

        log_file = self._find_latest_log(job_info.config.project_path)
        if not log_file or not log_file.exists():
            return web.Response(status=204)  # No Content

        try:
            parsed = HFSSLogParser(log_file).parse()
            out = parsed.to_dict()
            out["log_parser"] = {
                "is_converged": parsed.adaptive[-1].converged if parsed.adaptive else False,
            }
            return web.json_response(out)
        except Exception as exc:
            return web.json_response({"error": str(exc)}, status=500)

    async def submit_job(self, request):
        data = await request.json()

        # 1.  decide which scheduler the UI *really* wants
        sched_type_str = data.get("config", {}).get("scheduler_type", "none")
        try:
            scheduler_type = SchedulerType(sched_type_str.lower())
        except ValueError:
            scheduler_type = SchedulerType.NONE

        # 2.  inject the server-side ANSYS path (never trust the client)
        data["config"]["ansys_edt_path"] = self.ansys_path
        config = HFSSSimulationConfig.from_dict(data["config"])

        # 3.  overwrite scheduler type and user with authoritative values
        config.scheduler_type = scheduler_type
        config.user = data.get("user") or getpass.getuser()

        # 4.  optional machine nodes / batch options
        if data.get("machine_nodes"):
            config.machine_nodes = [MachineNode(**n) for n in data["machine_nodes"]]
        if data.get("batch_options"):
            config.layout_options = HFSS3DLayoutBatchOptions(**data["batch_options"])

        # 5.  FINAL guarantee – path must be non-empty and exist
        if not config.ansys_edt_path or not os.path.isfile(config.ansys_edt_path):
            config.ansys_edt_path = self.ansys_path
        # rebuild so every cached field (command string, scripts, …) is correct
        config = HFSSSimulationConfig(**config.model_dump())

        # 6.  submit to the async manager and return the job id
        job_id = await self.manager.submit_job(config)
        return web.json_response({"job_id": job_id, "status": "submitted"})

    async def get_queue_status(self, request):
        """Get current queue status for UI display"""
        queue_stats = self.manager.job_pool.get_queue_stats()
        return web.json_response(queue_stats)

    async def get_resources(self, request):
        """Get current resource usage for UI display"""
        resources = self.manager.resource_monitor.current_usage
        return web.json_response(resources)

    async def cancel_job(self, request):
        job_id = request.match_info["job_id"]
        success = await self.manager.cancel_job(job_id)
        return web.json_response({"status": "cancelled" if success else "failed", "success": success})

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

    def create_simulation_config(
        self,
        project_path: str,
        ansys_edt_path: str | None = None,
        jobid: str | None = None,
        scheduler_type: SchedulerType | None = None,
        cpu_cores: int = 1,
        user: str = "unknown",
    ) -> HFSSSimulationConfig:
        """Create a validated HFSSSimulationConfig.

        Parameters
        ----------
        cpu_cores : int
            Number of logical cores the user requested in the UI.
            Used only when scheduler_type == NONE (local run).
            :param ansys_edt_path:
        """
        if not project_path:
            raise ValueError("Project path must be provided")

        if ansys_edt_path is None:
            ansys_edt_path = self.ansys_path
        if jobid is None:
            jobid = f"{Path(project_path).stem}_{uuid.uuid4().hex[:6]}"
        if scheduler_type is None:
            scheduler_type = self.scheduler_type

        # Build ONE machine-node that carries the requested CPU count
        machine_nodes = [
            MachineNode(
                hostname="localhost",
                cores=cpu_cores,  # <-- honour UI choice
                max_cores=cpu_cores,
                utilization=90,
            )
        ]

        cfg = create_hfss_config(
            ansys_edt_path=ansys_edt_path,
            jobid=jobid,
            project_path=project_path,
            scheduler_type=scheduler_type,
            machine_nodes=machine_nodes,
        )
        cfg.user = user
        return cfg


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
