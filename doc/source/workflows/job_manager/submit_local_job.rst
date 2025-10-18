.. _job_manager_usage:

********************************************************************************
Job Submission – Sync & Async Walk-through
********************************************************************************

.. contents:: Table of contents
   :local:
   :depth: 3

.. rubric:: Submit and monitor HFSS/3-D Layout simulations through the PyEDB Job Manager
   with **zero** additional infrastructure on your workstation or **full** cluster support
   (SLURM, LSF, PBS, Windows-HPC).

--------------------------------------------------------------------
Overview
--------------------------------------------------------------------
The Job Manager is an *asynchronous* micro-service that is **automatically** started
in a background thread when you instantiate :class:`.JobManagerHandler`.
It exposes:

* REST & Web-Socket endpoints (``http://localhost:8080`` by default)
* Thread-safe synchronous façade for scripts / Jupyter
* Native async API for advanced integrations
* CLI utility ``submit_local_job`` for shell / CI pipelines

The same backend code-path is used regardless of front-end style; the difference is
**who owns the event-loop** and **how control is returned to the caller**.

--------------------------------------------------------------------
Synchronous Usage (Scripts & Notebooks)
--------------------------------------------------------------------
Perfect when you simply want to *“submit and wait”* without learning ``asyncio``.

.. code-block:: python
   :caption: local_sync_demo.py
   :linenos:

   from pyedb.workflows.job_manager.backend.job_submission import (
       create_hfss_config,
       SchedulerType,
   )
   from pyedb.workflows.job_manager.backend.job_manager_handler import JobManagerHandler

   project_to_solve = r"D:\Temp\test_jobs\test4.aedb"

   handler = JobManagerHandler()  # discovers ANSYS install
   handler.start_service()  # starts background aiohttp server

   cfg = create_hfss_config(
       project_path=project_to_solve, scheduler_type=SchedulerType.NONE
   )
   cfg.machine_nodes[0].cores = 8  # use 8 local cores

   job_id = handler.submit_job(cfg)  # ← blocks until job accepted
   print("submitted", job_id)

   status = handler.wait_until_done(job_id)  # ← polls until terminal
   print("job finished with status:", status)

   handler.close()  # graceful shutdown

Step-by-step
^^^^^^^^^^^^
.. list-table::
   :widths: 10 90
   :header-rows: 1

   * - Line
     - Description
   * - 6
     - Creates a *synchronous façade* around the async service; auto-detects
       ANSYS version and scheduler (NONE on Windows, SLURM/LSF on Linux if present).
   * - 7
     - Spawns a **daemon thread**, starts an *aiohttp* event-loop inside it,
       and binds the REST/WebSocket API to ``http://localhost:8080``.
   * - 9-11
     - Builds a validated :class:`.HFSSSimulationConfig`; ``machine_nodes`` is
       overridden to use 8 CPU cores for a local *subprocess* run.
   * - 13
     - Marshals the async coroutine into the background loop and returns the
       real job ID (``str``) to the caller.
   * - 16
     - Polls ``GET /api/jobs`` every 2 s until the job reaches
       ``completed``, ``failed``, or ``cancelled``.
   * - 18
     - Cancels background tasks, stops the web server, and joins the daemon thread.

Production notes
^^^^^^^^^^^^^^^^
* Thread-safe: multiple threads may submit or cancel concurrently.
* Resource limits (CPU, memory, disk, concurrency) are enforced; jobs stay queued
  until resources are free.
* ``atexit`` ensures clean shutdown even if the user forgets ``close()``.
* Cluster runs: change ``SchedulerType.NONE`` → ``SLURM``/``LSF`` and supply
  ``scheduler_options``; the code path remains identical.

--------------------------------------------------------------------
Asynchronous Usage (CLI & Programmatic)
--------------------------------------------------------------------
Use when you need **non-blocking** behaviour inside an *async* function or from
the shell / CI pipelines.

CLI – ``submit_local_job``
^^^^^^^^^^^^^^^^^^^^^^^^^^
The package installs a console entry-point that talks to the **same** REST API.

Installation
""""""""""""
.. code-block:: bash

   $ pip install -e .                      # or production wheel
   $ which submit_local_job
   /usr/local/bin/submit_local_job

Synopsis
""""""""
.. code-block:: bash

   $ submit_local_job --project-path <PATH> [options]

.. sphinx_argparse_cli::
   :module: pyedb.workflows.cli.submit_local_job
   :func: build_parser
   :prog: submit_local_job
   :nested: full

Environment variables
"""""""""""""""""""""
.. envvar:: PYEDB_JOB_MANAGER_HOST

   Fallback for ``--host``.

.. envvar:: PYEDB_JOB_MANAGER_PORT

   Fallback for ``--port``.

Exit codes
""""""""""
===== =========================================================
Code  Meaning
===== =========================================================
``0`` Job accepted by manager.
``1`` CLI validation or connection error.
``2`` Unexpected runtime exception.
===== =========================================================

Example – CLI
"""""""""""""
.. code-block:: bash

   $ submit_local_job \
         --host 127.0.0.1 \
         --port 8080 \
         --project-path "/shared/antenna.aedb" \
         --num-cores 16

The command returns immediately after the job is **queued**; use the printed ID
with ``wait_until_done`` or monitor via the web UI.

Programmatic – native asyncio
"""""""""""""""""""""""""""""
.. code-block:: python

   import asyncio
   from pyedb.workflows.job_manager.backend.service import JobManager
   from pyedb.workflows.job_manager.backend.job_submission import create_hfss_config


   async def main():
       manager = JobManager()  # same backend
       cfg = create_hfss_config(project_path="antenna.aedb", scheduler_type="NONE")
       job_id = await manager.submit_job(cfg, priority=5)
       await manager.wait_until_all_done()  # non-blocking wait
       print("all done")


   asyncio.run(main())

--------------------------------------------------------------------
Choosing Between Sync & Async
--------------------------------------------------------------------
.. list-table::
   :widths: 50 50
   :header-rows: 1

   * - Synchronous (scripts / notebooks)
     - Asynchronous (services / CLI)
   * - No ``asyncio`` knowledge required.
     - Caller runs inside ``async def``; operations are ``await``-ed.
   * - Blocking calls – caller waits for result.
     - Non-blocking – event loop stays responsive.
   * - Ideal for **interactive** work, **CI pipelines**, **quick scripts**.
     - Ideal for **web servers**, **micro-services**, **GUI applications**.

--------------------------------------------------------------------
See Also
--------------------------------------------------------------------
* :ref:`job_manager_rest_api` – Complete endpoint reference
* :class:`.JobManagerHandler` – API reference (sync façade)
* :class:`.JobManager` – API reference (async core)
* :doc:`configuration_syntax` – All scheduler & solver options
* :doc:`../tutorials/submit_batch` – Bulk submissions on SLURM/LSF