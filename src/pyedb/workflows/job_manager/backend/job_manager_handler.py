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
Thread-safe façade for the async ANSYS Job Manager.

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

Examples
--------
>>> handler = JobManagerHandler()  # doctest: +SKIP
>>> handler.start_service()  # doctest: +SKIP
>>> config = handler.create_simulation_config("/path/to/project.aedt")  # doctest: +SKIP
>>> job_id = asyncio.run(handler.submit_job(config))  # doctest: +SKIP
>>> handler.close()  # doctest: +SKIP

For command-line usage:

.. code-block:: bash

    python -m pyedb.workflows.job_manager.backend.job_manager_handler --host localhost --port 8080
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
import time
from typing import Optional
import uuid

import aiohttp
from aiohttp import web
import requests

from pyedb.generic.general_methods import is_linux
from pyedb.workflows.job_manager.backend.job_submission import (
    HFSS3DLayoutBatchOptions,
    HFSSSimulationConfig,
    MachineNode,
    SchedulerType,
    create_hfss_config,
)
from pyedb.workflows.job_manager.backend.service import JobManager, ResourceLimits, SchedulerManager
from pyedb.workflows.utilities.hfss_log_parser import HFSSLogParser


def get_session(url: str) -> aiohttp.ClientSession:
    """
    Return an aiohttp.ClientSession with appropriate TLS configuration.

    Parameters
    ----------
    url : str
        Base URL; used only to decide whether TLS verification is required.

    Returns
    -------
    aiohttp.ClientSession
        Configured client session with timeout and SSL context.

    Notes
    -----
    The session is configured with:
    - 30-second total timeout
    - TLS verification for HTTPS URLs
    - Connection pooling (limit=20, limit_per_host=10)
    - Appropriate User-Agent header
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
    """
    CORS middleware for aiohttp server.

    Parameters
    ----------
    request : aiohttp.web.Request
        Incoming HTTP request
    handler : callable
        Next handler in the middleware chain

    Returns
    -------
    aiohttp.web.Response
        Response with CORS headers added
    """
    response = await handler(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


class JobManagerHandler:
    """
    Synchronous façade that controls an **async** Job Manager service.

    This class provides a thread-safe interface to manage asynchronous job
    execution while running the aiohttp server in a background thread.

    Parameters
    ----------
    edb : Optional[Edb]
        PyEDB instance for automatic ANSYS path detection
    version : Optional[str]
        Specific ANSYS version to use (e.g., "2023.1")
    host : str
        Hostname or IP address to bind the server
    port : int
        TCP port to listen on

    Attributes
    ----------
    ansys_path : str
        Path to ANSYS EDT executable
    scheduler_type : SchedulerType
        Detected scheduler type (SLURM, LSF, or NONE)
    manager : JobManager
        Underlying async job manager instance
    host : str
        Server hostname
    port : int
        Server port
    url : str
        Full server URL
    started : bool
        Whether the service is currently running

    Raises
    ------
    ValueError
        If specified ANSYS version is not found
    RuntimeError
        If service fails to start within timeout

    Examples
    --------
    >>> handler = JobManagerHandler()  # doctest: +SKIP
    >>> handler.start_service()  # doctest: +SKIP
    >>> print(f"Server running at {handler.url}")  # doctest: +SKIP
    >>> # Submit jobs via REST API or handler methods
    >>> handler.close()  # doctest: +SKIP
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
        """Add REST API routes to the aiohttp application."""
        self.app.router.add_get("/api/jobs", self.get_jobs)
        self.app.router.add_get("/api/queue", self.get_queue_status)
        self.app.router.add_get("/api/resources", self.get_resources)
        self.app.router.add_get("/api/scheduler_type", self.get_scheduler_type)
        self.app.router.add_get("/api/cluster_partitions", self.get_cluster_partitions)
        self.app.router.add_post("/api/submit", self.handle_submit_job)
        self.app.router.add_post("/api/cancel/{job_id}", self.cancel_job)
        self.app.router.add_get("/api/jobs/{job_id}/log", self.get_job_log)
        self.app.router.add_get("/api/me", self.get_me)
        self.app.router.add_get("/system/status", self.get_system_status)
        self.app.router.add_post("/jobs/submit", self.handle_submit_job)

    def _find_latest_log(self, project_path: str) -> Path | None:
        """
        Find the newest log file in batchinfo directories.

        Parameters
        ----------
        project_path : str
            Path to the AEDT project file

        Returns
        -------
        Path or None
            Path to the newest log file, or None if no logs found

        Notes
        -----
        Searches for pattern: <project>.aedb.batchinfo.<timestamp>/*.log
        and returns the most recently modified log file.
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

    def submit_job(self, config: HFSSSimulationConfig, priority: int = 0, timeout: float = 30.0) -> str:
        """
        Synchronously submit a simulation job.

        The method is thread-safe: it marshals the async work into the
        background event-loop and returns the job identifier.

        Parameters
        ----------
        config : HFSSSimulationConfig
            Fully-built and validated simulation configuration.
        priority : int, optional
            Job priority (higher → de-queued earlier).  Default 0.
        timeout : float, optional
            Seconds to wait for the submission to complete.  Default 30 s.

        Returns
        -------
        str
            Unique job identifier (same as ``config.jobid``).

        Raises
        ------
        RuntimeError
            If the service is not started or the submission times out.
        Exception
            Any validation / scheduler error raised by the underlying coroutine.

        Examples
        --------
        >>> from pyedb.workflows.job_manager.backend.job_manager_handler import JobManagerHandler
        >>> from pyedb.workflows.job_manager.backend.job_submission import create_hfss_config, SchedulerType

        >>> handler = JobManagerHandler()
        >>> handler.start_service()
        >>> cfg = create_hfss_config(
        >>>     ansys_edt_path=...,
        >>>     jobid="my_job",
        >>>     project_path=...,
        >>>     scheduler_type=SchedulerType.NONE
        >>> )
        >>> job_id = handler.submit_job(cfg, priority=0)
        >>> print("submitted", job_id)
        >>> # later
        >>> handler.close()
        """
        if not self.started:
            raise RuntimeError("Job-manager service is not started")

        # Ship coroutine to the background loop
        future = run_coroutine_threadsafe(self.manager.submit_job(config, priority=priority), self._loop)
        try:
            return future.result(timeout=timeout)  # block until done
        except _futs.TimeoutError as exc:
            raise RuntimeError("Job submission timed out") from exc

    def wait_until_done(self, job_id: str, poll_every: float = 2.0) -> str:
        """
        Block until the requested job reaches a terminal state
        (completed, failed, or cancelled).

        Returns
        -------
        str
            Terminal status string.
        """
        if not self.started:
            raise RuntimeError("Service not started")

        while True:
            rsp = requests.get(f"{self.url}/api/jobs", timeout=30).json()
            job = next((j for j in rsp if j["id"] == job_id), None)
            if not job:
                raise RuntimeError(f"Job {job_id} disappeared from manager")
            status = job["status"]
            if status in {"completed", "failed", "cancelled"}:
                return status
            time.sleep(poll_every)

    def wait_until_all_done(self, poll_every: float = 2.0) -> None:
        """
        Block until **every** job currently known to the manager
        is in a terminal state.
        """
        if not self.started:
            raise RuntimeError("Service not started")

        while True:
            rsp = requests.get(f"{self.url}/api/jobs", timeout=30).json()
            active = [j for j in rsp if j["status"] not in {"completed", "failed", "cancelled"}]
            if not active:
                return
            time.sleep(poll_every)

    async def get_system_status(self, request):
        """
        Get system status and scheduler information.

        Parameters
        ----------
        request : aiohttp.web.Request
            HTTP request object

        Returns
        -------
        aiohttp.web.Response
            JSON response with system status
        """
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
        """
        Get current user information.

        Parameters
        ----------
        request : aiohttp.web.Request
            HTTP request object

        Returns
        -------
        aiohttp.web.Response
            JSON response with username
        """
        import getpass

        return web.json_response({"username": getpass.getuser()})

    async def get_jobs(self, request):
        """
        Get list of all jobs with their current status.

        Parameters
        ----------
        request : aiohttp.web.Request
            HTTP request object

        Returns
        -------
        aiohttp.web.Response
            JSON array of job objects
        """
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
        """
        Get detected scheduler type.

        Parameters
        ----------
        request : aiohttp.web.Request
            HTTP request object

        Returns
        -------
        aiohttp.web.Response
            JSON response with scheduler type
        """
        return web.json_response({"scheduler_type": self.scheduler_type.value})

    async def get_cluster_partitions(self, request):
        """
        Get available cluster partitions/queues.

        Parameters
        ----------
        request : aiohttp.web.Request
            HTTP request object

        Returns
        -------
        aiohttp.web.Response
            JSON array of partition information
        """
        if self._sch_mgr:
            partitions = await self._sch_mgr.get_partitions()
            return web.json_response(partitions)
        return web.json_response([])

    async def get_job_log(self, request):
        """
        Get parsed HFSS log for a finished job.

        Parameters
        ----------
        request : aiohttp.web.Request
            HTTP request with job_id in URL path

        Returns
        -------
        aiohttp.web.Response
            - 200: JSON with parsed log data
            - 204: No log available yet
            - 404: Job not found
            - 500: Log parsing error
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

    async def handle_submit_job(self, request):
        """
        Submit a new simulation job.

        Parameters
        ----------
        request : aiohttp.web.Request
            HTTP request with JSON payload containing job configuration

        Returns
        -------
        aiohttp.web.Response
            JSON response with job ID and status

        Notes
        -----
        Expected JSON payload:

        .. code-block:: json

            {
                "config": {
                    "scheduler_type": "slurm|lsf|none",
                    "project_path": "/path/to/project.aedt",
                    ... other HFSS config fields
                },
                "user": "username",
                "machine_nodes": [...],
                "batch_options": {...}
            }
        """
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
        if config.scheduler_type != scheduler_type:
            print("Overriding scheduler type from client:", config.scheduler_type, "→", scheduler_type)
        config.scheduler_type = self.scheduler_type
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
        """
        Get current queue status for UI display.

        Parameters
        ----------
        request : aiohttp.web.Request
            HTTP request object

        Returns
        -------
        aiohttp.web.Response
            JSON with queue statistics
        """
        queue_stats = self.manager.job_pool.get_queue_stats()
        return web.json_response(queue_stats)

    async def get_resources(self, request):
        """
        Get current resource usage for UI display.

        Parameters
        ----------
        request : aiohttp.web.Request
            HTTP request object

        Returns
        -------
        aiohttp.web.Response
            JSON with current resource usage
        """
        resources = self.manager.resource_monitor.current_usage
        return web.json_response(resources)

    async def cancel_job(self, request):
        """
        Cancel a running or queued job.

        Parameters
        ----------
        request : aiohttp.web.Request
            HTTP request with job_id in URL path

        Returns
        -------
        aiohttp.web.Response
            JSON response with cancellation status
        """
        job_id = request.match_info["job_id"]
        success = await self.manager.cancel_job(job_id)
        return web.json_response({"status": "cancelled" if success else "failed", "success": success})

    @staticmethod
    def _detect_scheduler() -> SchedulerType:
        """
        Detect available job scheduler on the system.

        Returns
        -------
        SchedulerType
            Detected scheduler type (SLURM, LSF, or NONE)

        Notes
        -----
        Detection logic:
        - Windows: Always returns NONE
        - Linux: Checks for 'sinfo' (SLURM) or 'bhosts' (LSF) commands
        """
        if platform.system() == "Windows":
            return SchedulerType.NONE
        for cmd, enum in (("sinfo", SchedulerType.SLURM), ("bhosts", SchedulerType.LSF)):
            if shutil.which(cmd) is not None:
                return enum
        return SchedulerType.NONE

    @property
    def url(self) -> str:
        """
        Get the server URL.

        Returns
        -------
        str
            Full server URL (http://host:port)
        """
        return self._url

    def start_service(self) -> None:
        """
        Start the job manager service in a background thread.

        Raises
        ------
        RuntimeError
            If service fails to start within 10 seconds

        Notes
        -----
        This method is non-blocking and returns immediately.
        The service runs in a daemon thread with its own event loop.
        """
        if self.started:
            return
        self._thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self._thread.start()
        if not self._start_event.wait(timeout=10):
            raise RuntimeError("Job-Manager service failed to start within 10 s")

    async def _start_site(self) -> None:
        """
        Internal method to start the aiohttp server.

        This method runs in the background thread's event loop.
        """
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, self.host, self.port)
        await self.site.start()
        self.started = True
        self._start_event.set()

    def close(self) -> None:
        """
        Gracefully shutdown the job manager service.

        Notes
        -----
        This method is automatically called on program exit via atexit,
        but can also be called explicitly for clean shutdown.
        """
        if not self.started or not self._loop:
            return
        coro = self.stop_service()
        try:
            run_coroutine_threadsafe(coro, self._loop).result(timeout=10)
        except (_futs.TimeoutError, asyncio.TimeoutError):
            print("Warning: Service did not shut down gracefully.", file=sys.stderr)
        self.started = False

    async def stop_service(self) -> None:
        """
        Stop the aiohttp server and cleanup resources.

        This is the async version of close() that runs in the event loop.
        """
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

        # ---- make the first sample synchronous ----
        import datetime
        import math
        import os

        import psutil

        memory = psutil.virtual_memory()
        disk = psutil.disk_usage(os.sep)
        self.manager.resource_monitor.current_usage.update(
            {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": memory.percent,
                "memory_used_gb": round(memory.used / 1024**3, 2),
                "memory_total_gb": round(memory.total / 1024**3, 2),
                "memory_free_gb": round(memory.available / 1024**3, 2),
                "disk_usage_percent": disk.percent,
                "disk_free_gb": round(disk.free / 1024**3, 2),
                "timestamp": datetime.datetime.now().isoformat(),
            }
        )
        # ------------------------------------------

        # now start the periodic coroutine
        self.manager._monitor_task = self._loop.create_task(self.manager.resource_monitor.monitor_resources())
        self.manager._ensure_scheduler_monitor_running()

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
        """
        Create a validated HFSSSimulationConfig.

        Parameters
        ----------
        project_path : str
            Path to the AEDT project file
        ansys_edt_path : str, optional
            Path to ANSYS EDT executable. Uses detected path if None.
        jobid : str, optional
            Job identifier. Auto-generated if None.
        scheduler_type : SchedulerType, optional
            Scheduler type. Uses detected scheduler if None.
        cpu_cores : int
            Number of CPU cores for local execution
        user : str
            Username for job ownership

        Returns
        -------
        HFSSSimulationConfig
            Validated simulation configuration

        Raises
        ------
        ValueError
            If project_path is empty or invalid

        Notes
        -----
        The cpu_cores parameter is only used when scheduler_type is NONE (local execution).
        For cluster execution, cores are determined by the scheduler configuration.
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
    """
    Command-line entry point for the job manager backend.

    Example
    -------
    python -m pyedb.workflows.job_manager.backend.job_manager_handler --host localhost --port 8080
    """
    import argparse

    parser = argparse.ArgumentParser(description="Start the PyEDB job-manager backend.")
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="IP address or hostname to bind the server (default: localhost)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="TCP port to listen on (default: 8080)",
    )
    args = parser.parse_args()

    handler = JobManagerHandler(host=args.host, port=args.port)
    handler.start_service()
    print(f"✅ Job-manager backend listening on http://{handler.host}:{handler.port}")
    try:
        threading.Event().wait()  # Keep main thread alive
    except KeyboardInterrupt:
        print("\nShutting down...")
        handler.close()
        sys.exit(0)
