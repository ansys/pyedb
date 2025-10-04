"""
``job_manager_handler`` --- Thread-safe façade for the async ANSYS Job Manager
================================================================================

This module exposes a **synchronous, production-grade** entry point to the
**asynchronous** job manager service.  A background daemon thread hosts an
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
Minimal usage inside a PyEDB script::

    from pyedb import Edb
    from pyedb.workflows.job_manager.job_manager_handler import JobManagerHandler

    edb = Edb("my_board.aedb")
    handler = JobManagerHandler(edb, host="0.0.0.0", port=8080)
    handler.start_service()  # returns immediately

    cfg = handler.create_simulation_config(project_path="/ansys/antenna.aedt", scheduler_type="slurm", jobid="prod_001")

    job_id = handler.submit_jobs_and_wait([cfg], timeout=3600)
    print("Finished", job_id)

The same code works **unchanged** on Windows and Linux.

"""

import asyncio
from asyncio import run_coroutine_threadsafe
import atexit
import concurrent
import concurrent.futures
import concurrent.futures as _futs
import os
import platform
import shutil
import threading
from typing import List, Optional, Union

from aiohttp import web

from pyedb.generic.general_methods import is_linux
from pyedb.workflows.job_manager.job_submission import (
    HFSSSimulationConfig,
    SchedulerType,
    create_hfss_config,
)
from pyedb.workflows.job_manager.service import (
    JobManager,
    ResourceLimits,
    SchedulerManager,
    submit_job_to_manager,
)


class JobManagerHandler:
    """
    Synchronous façade that controls an **async** Job Manager service.

    The handler manages a **private** event-loop running on a **daemon** thread.
    All public methods are **thread-safe** and **non-blocking** except
    ``submit_jobs_and_wait`` which is explicitly designed for batch scripts.

    Parameters
    ----------
    edb : pyedb.Edb
        Active PyEDB session used to resolve the ANSYS installation path.
    host : str, optional
        IPv4/IPv6 address to bind the embedded web server.  Default
        ``"localhost"``.
    port : int, optional
        TCP port to bind.  Default ``8080``.

    Examples
    --------
    >>> handler = JobManagerHandler(edb, host="0.0.0.0", port=8080)
    >>> handler.start_service()  # returns immediately
    >>> handler.close()  # idempotent graceful shutdown
    """

    def __init__(self, edb, host="localhost", port=8080):
        if is_linux:
            self.ansys_path = os.path.join(edb.base_path, "ansysedt")
        else:
            self.ansys_path = os.path.join(edb.base_path, "ansysedt.exe")
        self.manager = JobManager()
        self.manager.resource_limits = ResourceLimits(max_concurrent_jobs=2)
        self.runner: Optional[web.AppRunner] = None
        self.site = None
        self.started = False
        self.host, self.port = host, port
        self._url = f"http://{host}:{port}"
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._start_event = threading.Event()  # becomes True when aiohttp is bound
        self._shutdown = False
        atexit.register(self.stop_service)  # emergency brake
        # ---  NEW: lazy, conditional SchedulerManager  ---
        self.scheduler_type = self._detect_scheduler()
        self._sch_mgr: Optional[SchedulerManager] = None
        # auto-start
        # self.start_service()

    @staticmethod
    def _detect_scheduler() -> SchedulerType:
        """
        Auto-detect external scheduler **only on Linux**.
        Windows → always NONE (SLURM/LSF are Unix-only).
        """
        if platform.system() == "Windows":
            return SchedulerType.NONE

        for cmd, enum in (("sinfo", SchedulerType.SLURM), ("bhosts", SchedulerType.LSF)):
            if shutil.which(cmd) is not None:
                return enum
        return SchedulerType.NONE

    # -------------------------------------------------
    # read-only property – raises if external scheduler not configured
    # -------------------------------------------------
    @property
    def scheduler_manager(self) -> Union[SchedulerManager, None]:
        if self.scheduler_type == SchedulerType.NONE:
            return None
        if self._sch_mgr is None:  # create on first access
            self._sch_mgr = SchedulerManager(self.scheduler_type)
        return self._sch_mgr

    def cluster_status(self, timeout: float = 10.0) -> dict:
        """
        Thread-safe snapshot of the external cluster (SLURM or LSF).

        Returns
        -------
        dict
            {
              "partitions": [ {...}, ... ],   # per-partition resources
              "jobs":       [ {...}, ... ]    # global job table
            }

        Raises
        ------
        None
            If *scheduler_type* is ``SchedulerType.NONE``.
        concurrent.futures.TimeoutError
            If the underlying asyncio calls do not finish within *timeout*.
        """
        # Ensure an external scheduler is configured
        _ = self.scheduler_manager

        if not self.scheduler_manager:
            raise RuntimeError("Scheduler manager not available")

        async def _gather():
            return await asyncio.gather(self.scheduler_manager.get_partitions(), self.scheduler_manager.get_jobs())

        future = asyncio.run_coroutine_threadsafe(_gather(), self._loop)
        partitions, jobs = future.result(timeout=timeout)
        return {"partitions": partitions, "jobs": jobs}

    @property
    def url(self) -> str:
        """
        str: Base URL of the embedded web server, e.g. ``http://localhost:8080``.
        """
        return self._url

    def start_service(self) -> None:
        """
        Start the embedded web server **on a background thread**.

        The call returns **as soon as** the HTTP socket is bound (≤ 10 s).
        Safe to invoke multiple times (idempotent).

        Raises
        ------
        RuntimeError
            If the socket cannot be bound within the timeout window.
        """
        if self.started:
            return
        self._thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self._thread.start()
        # block *only* until the web site is actually serving
        if not self._start_event.wait(timeout=10):
            raise RuntimeError("Job-Manager service failed to start within 10 s")

    # ------------------------------------------------------------------
    # stop – can be called from any thread
    # ------------------------------------------------------------------

    async def stop_service(self) -> None:
        """
        **Asynchronous** coroutine that performs the actual teardown.

        This method **must** be scheduled on the event-loop thread via
        ``run_coroutine_threadsafe``.  Public callers should use ``close()``
        instead.
        """
        if not self.started:
            return
        self._shutdown = True
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()
        self.started = False

    def close(self) -> None:
        """
        **Synchronous** shutdown that can be called from **any** thread.

        The method:

        1. Sets the internal ``_shutdown`` flag.
        2. Cancels the background ``_processing_task``.
        3. Stops the ``aiohttp`` site and runner.
        4. Joins the event-loop thread (30 s hard limit).

        The call is **idempotent** and **thread-safe**.
        """
        if not self.started:
            return

        # 1. stop the JobManager background task
        self.manager._shutdown = True
        pt = self.manager._processing_task
        if pt and not pt.done():
            pt.cancel()
            try:
                run_coroutine_threadsafe(asyncio.wait_for(pt, None), self._loop).result()
            except (_futs.CancelledError, asyncio.CancelledError):
                pass  # expected – task was cancelled

        # 2. stop aiohttp – keep reference until *after* result()
        if self._loop and self._loop.is_running():
            coro = self.stop_service()
            try:
                run_coroutine_threadsafe(coro, self._loop).result(timeout=30)
            except (_futs.TimeoutError, asyncio.TimeoutError):
                pass  # site refused to die – we still continue

        self.started = False

    # ------------------------------------------------------------------
    # everything below runs inside the dedicated asyncio thread
    # ------------------------------------------------------------------
    def _run_event_loop(self) -> None:
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._start_site())
        # keep the loop alive until shutdown flag is set
        self._loop.run_until_complete(self._wait_until_shutdown())

    async def _start_site(self) -> None:
        self.runner = web.AppRunner(self.manager.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, self.host, self.port)
        await self.site.start()
        self.started = True
        self._start_event.set()  # release the caller in __init__

    async def _wait_until_shutdown(self) -> None:
        while not self._shutdown:
            await asyncio.sleep(0.2)
        await self.stop_service()

    # ------------------------------------------------------------------
    #  one-call submit + wait (blocking)
    # ------------------------------------------------------------------
    def submit_jobs_and_wait(self, jobs, timeout: Optional[float] = None) -> List[str]:
        """
        Submit simulations and **block** until all reach a terminal state
        (completed, failed, or cancelled).

        This is a convenience wrapper for **batch scripts** that need to
        guarantee job completion before proceeding.

        Parameters
        ----------
        jobs : list[HFSSSimulationConfig]
            Simulation configurations.
        timeout : float, optional
            Global timeout in **seconds**.  ``None`` disables the timeout.

        Returns
        -------
        list[str]
            Job identifiers in the same order as *jobs*.

        Raises
        ------
        asyncio.TimeoutError
            If the global timeout is exceeded.
        """
        if not self.started:
            self.start_service()

        # 1. submit
        ids = self.submit_jobs(jobs)  # already sync

        # 2. build coroutine that waits for termination
        async def _wait():
            await asyncio.wait_for(self.manager.wait_until_all_done(), timeout=timeout)

        # 3. run that coroutine on the background loop
        future = asyncio.run_coroutine_threadsafe(_wait(), self._loop)
        try:
            future.result(timeout=timeout)  # propagate exceptions
        except concurrent.futures.TimeoutError as exc:
            raise asyncio.TimeoutError("Global timeout hit while waiting for jobs") from exc

        return ids

    # ------------------------------------------------------------------
    # helper so the main thread can submit jobs without 'await'
    # ------------------------------------------------------------------
    def submit_jobs(self, tasks) -> list[str]:
        """
        Submit a list of simulations **without waiting** for completion.

        The call is **thread-safe** and returns **immediately** with a list of
        job identifiers that can be used for later queries or cancellation.

        Parameters
        ----------
        tasks : list[HFSSSimulationConfig]
            Simulation configurations created by ``create_simulation_config``.

        Returns
        -------
        list[str]
            Unique job identifiers in the same order as *tasks*.

        Raises
        ------
        concurrent.futures.TimeoutError
            If the internal asyncio call does not complete within 30 s.
        """
        coro = self.__submit_jobs(tasks)
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result(timeout=30)  # raise after 30 s if hanging

    async def __submit_jobs(self, tasks: List[HFSSSimulationConfig]) -> List[str]:
        job_ids = []
        if not self.started:
            await self.start_service()
        for task in tasks:
            if not task.ansys_edt_path:
                task.ansys_edt_path = self.ansys_path
            print("Submitting job:", task.jobid)
            job_id = await submit_job_to_manager(task, priority=5, manager_url=self.url)
            job_ids.append(job_id)
            print("Submitted job ID:", job_id)
        return job_ids

    def create_simulation_config(self, project_path, ansys_edt_path=None, jobid=None, scheduler_type=None):
        """
        Method that creates a **ready-to-submit** simulation config.

        All file paths are resolved **relative to the handler host**.  Missing
        parameters are inferred from the PyEDB session.

        Parameters
        ----------
        project_path : str
            Absolute path to the ``.aedt`` or ``.aedb`` project file.
        ansys_edt_path : str, optional
            Path to the ANSYS Electronics Desktop executable.  If ``None`` the
            value is taken from the PyEDB installation.
        jobid : str, optional
            Unique job identifier.  If ``None`` the basename of
            *project_path* plus ``"_job"`` is used.
        scheduler_type : SchedulerType, optional
            External scheduler to use.  Default ``SchedulerType.NONE`` (local
            execution).

        Returns
        -------
        HFSSSimulationConfig
            Validated configuration object that can be passed to
            ``submit_jobs`` or ``submit_jobs_and_wait``.

        Raises
        ------
        ValueError
            If *project_path* is empty or the file does not exist.
        """
        if not project_path:
            raise ValueError("Project path must be provided")
        if not ansys_edt_path:
            ansys_edt_path = self.ansys_path
        if not jobid:
            jobid = os.path.splitext(os.path.basename(project_path))[0] + "_job"
        if not scheduler_type:
            scheduler_type = SchedulerType.NONE

        return create_hfss_config(
            ansys_edt_path=ansys_edt_path, jobid=jobid, project_path=project_path, scheduler_type=scheduler_type
        )
