.. _job_manager:

================================================================================
Job Manager --- Async scheduler façade for HFSS/3D-Layout simulations
================================================================================

.. contents:: Table of Contents
   :local:
   :depth: 2

--------
Overview
--------

The *Job Manager* is a **thread-safe, production-grade** façade around an
**asynchronous** scheduler service that can:

* launch HFSS / HFSS-3D-Layout simulations **locally** (sub-process) or
  on **enterprise clusters** (SLURM, LSF, PBS, Windows-HPC),
* enforce **host resource limits** (CPU, memory, disk, concurrency),
* expose a **REST/Socket.IO** micro-service API,
* guarantee **exactly once** execution and **graceful draining** on shutdown.

Two integration levels are provided:

1. **Zero-conf embedded mode** import :class:`JobManagerHandler`, hand it a
   PyEDB ``Edb`` object, and call :meth:`submit_jobs_and_wait` from an
   interactive script or Jupyter.
2. **Stand-alone service** run ``python -m pyedb.workflows.job_manager.service``
   (or a Docker container) and submit jobs via HTTP/JSON from any language.

The public surface is intentionally tiny: three factory helpers, two submission
methods, and a handful of data containers. Everything else is **private**
implementation detail that can evolve without breaking user code.

--------
Glossary
--------

.. glossary::

   job
      A single HFSS/3D-Layout solve request described by a
      :class:`HFSSSimulationConfig` object.

   scheduler
      An *external* batch system such as SLURM, LSF, PBS or Windows-HPC.  The
      special value ``SchedulerType.NONE`` means *run locally in a sub-process*.

   local run
      A simulation that is executed by the same host that hosts the Job Manager
      service (via ``asyncio.subprocess``).

   remote run
      A simulation that is forwarded to an *external* scheduler.  The Job
      Manager merely **submits** the job and **monitors** its state.

-----------------
Quick-start guide
-----------------

Embedded (synchronous) API
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pyedb import Edb
   from pyedb.workflows.job_manager import JobManagerHandler

   edb = Edb("my_board.aedb")
   handler = JobManagerHandler(edb, host="0.0.0.0", port=8080)
   handler.start_service()  # returns immediately

   cfg = handler.create_simulation_config(
       project_path="/ansys/antenna.aedt", scheduler_type="slurm", jobid="demo_001"
   )

   job_ids = handler.submit_jobs_and_wait([cfg], timeout=3600)
   print("Finished", job_ids)

The snippet above works **unchanged** on Windows and Linux.

Stand-alone REST service
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   $ python -m pyedb.workflows.job_manager.service
   INFO:JobManager:Resource monitor started (interval=5 s)
   INFO:JobManager:aiohttp server on http://0.0.0.0:8080

Query telemetry and submit a job from *curl*:

.. code-block:: bash

   # system telemetry
   curl http://localhost:8080/resources

   # queue statistics
   curl http://localhost:8080/queue

   # submit a job (JSON body)
   curl -X POST http://localhost:8080/jobs/submit \
        -H "Content-Type: application/json" \
        -d @my_cfg.json

The service embeds a **live dashboard** served at ``http://<host>:<port>/``.

------------------------
Synchronous entry points
------------------------

.. automodule:: pyedb.workflows.job_manager.job_manager_handler
   :members:
   :undoc-members:
   :show-inheritance:
   :inherited-members:

----------------------------------
Configuration & submission helpers
----------------------------------

.. automodule:: pyedb.workflows.job_manager.job_submission
   :members:
   :exclude-members: HFSSSimulationConfig, SchedulerOptions, MachineNode, HFSS3DLayoutBatchOptions
   :undoc-members:

---------------------------------------
Low-level data model (immutable configs)
---------------------------------------

.. autoclass:: pyedb.workflows.job_manager.job_submission.HFSSSimulationConfig
   :members:
   :special-members: __str__
   :undoc-members:

.. autoclass:: pyedb.workflows.job_manager.job_submission.SchedulerOptions
   :members:
   :undoc-members:

.. autoclass:: pyedb.workflows.job_manager.job_submission.MachineNode
   :members:
   :undoc-members:

.. autoclass:: pyedb.workflows.job_manager.job_submission.HFSS3DLayoutBatchOptions
   :members:
   :undoc-members:

.. autoclass:: pyedb.workflows.job_manager.job_submission.SchedulerType
   :members:
   :undoc-members:

---------------------------
Asynchronous service engine
---------------------------

.. automodule:: pyedb.workflows.job_manager.service
   :members:
   :exclude-members: JobStatus, ResourceLimits, JobInfo, ResourceMonitor, JobPoolManager
   :undoc-members:

--------------------------------------------------------
Internal state enumerations & resource-limit containers
--------------------------------------------------------

.. autoclass:: pyedb.workflows.job_manager.service.JobStatus
   :members:
   :undoc-members:

.. autoclass:: pyedb.workflows.job_manager.service.ResourceLimits
   :members:
   :undoc-members:

.. autoclass:: pyedb.workflows.job_manager.service.JobInfo
   :members:
   :undoc-members:

.. autoclass:: pyedb.workflows.job_manager.service.ResourceMonitor
   :members:
   :undoc-members:

.. autoclass:: pyedb.workflows.job_manager.service.JobPoolManager
   :members:
   :undoc-members:

---------------------
REST / Socket.IO API
---------------------

The service exposes the following **self-documenting** endpoints:

.. list-table::
   :header-rows: 1

   * - Verb
     - Path
     - Description
   * - ``GET``
     - ``/``
     - Serve live dashboard (``index.html``)
   * - ``GET``
     - ``/resources``
     - Real-time host telemetry (CPU, memory, disk)
   * - ``GET``
     - ``/queue``
     - Queue statistics (queued vs. running)
   * - ``GET``
     - ``/jobs``
     - Paginated list of all jobs (full metadata)
   * - ``POST``
     - ``/jobs/submit``
     - Submit a new job (JSON payload)
   * - ``POST``
     - ``/jobs/{job_id}/cancel``
     - Idempotent cancellation request
   * - ``POST``
     - ``/jobs/{job_id}/priority``
     - Change priority and re-queue

Socket.IO events (all ``async``) are emitted for every state transition:

* ``job_queued``
* ``job_started``
* ``job_scheduled``  (external scheduler only)
* ``job_completed``

The payload contains the ``job_id`` plus whatever metadata is useful for UI
progress bars or downstream automation.

-----------------
Error handling
-----------------

All APIs (embedded **and** REST) follow the same conventions:

* **Validation errors** are raised as :class:`ValueError` (embedded) or
  returned as HTTP **400** with ``{"success": false, "error": "<msg>"}``.
* **Missing resources** (project file, executable, etc.) raise
  :class:`FileNotFoundError` / HTTP **400**.
* **Scheduler submission failures** raise :class:`RuntimeError` / HTTP **502**.
* **Local subprocess timeouts** raise :class:`asyncio.TimeoutError` /
  HTTP **504**.

The caller can therefore trap **one** exception type (embedded) or inspect the
HTTP status code (REST) and decide whether to retry, abort or alert.

-----------------
Thread & process safety
-----------------------

* The embedded façade :class:`JobManagerHandler` is **fully thread-safe**.
  All public methods may be invoked from any Python thread.
* The underlying service is **single-threaded** (``asyncio``) and therefore
  lock-free; cross-thread communication is performed with
  :func:`asyncio.run_coroutine_threadsafe`.
* Graceful shutdown is guaranteed via :mod:`atexit` (embedded) or ``SIGTERM``
  handlers (stand-alone).  Running jobs are given a **30 s** window to
  terminate cleanly before being hard-killed.

-----------------
Platform support
-----------------

=================== ===================== =====================
Scheduler           Linux                 Windows
=================== ===================== =====================
Local subprocess    ✅                    ✅
SLURM               ✅                    ❌
LSF                 ✅                    ❌
PBS / Torque        ✅                    ❌
Windows-HPC         ❌                    ✅
=================== ===================== =====================


The synchronous façade is designed for **batch scripts** that need to run
simulations in parallel and wait for all jobs to complete before proceeding.
The :meth:`submit_jobs_and_wait` method blocks until all jobs have reached a
terminal state (completed, failed, or cancelled).

.. code-block:: python

   handler = JobManagerHandler(edb, host="0.0.0.0", port=8080)
   handler.start_service()

   cfg1 = handler.create_simulation_config(
       project_path="antenna.aedt", jobid="antenna_001"
   )
   cfg2 = handler.create_simulation_config(project_path="patch.aedt", jobid="patch_001")

   job_ids = handler.submit_jobs_and_wait([cfg1, cfg2], timeout=3600)
   print("Batch completed", job_ids)



The Job Manager can forward jobs to **external schedulers** such as SLURM, LSF,
PBS or Windows-HPC.  The user must provide a valid :class:`SchedulerOptions`
object that specifies the queue, nodes, memory, and other scheduler-specific
directives.

.. code-block:: python

   handler = JobManagerHandler(edb, host="0.0.0.0", port=8080)
   handler.start_service()

   cfg = handler.create_simulation_config(
       project_path="antenna.aedt",
       jobid="antenna_001",
       scheduler_type="slurm",
       scheduler_options=SchedulerOptions(nodes=4, memory="32GB"),
   )

   job_id = handler.submit_jobs([cfg])[0]
   print("Job submitted to SLURM", job_id)

-----------------
Troubleshooting
-----------------

Service fails to bind port
~~~~~~~~~~~~~~~~~~~~~~~~~~
* **Symptom**: ``RuntimeError: Job-Manager service failed to start within 10 s``
* **Cause**: Port already in use or insufficient privileges.
* **Fix**: Choose another port or stop the conflicting process:

.. code-block:: bash

   lsof -ti:8080 | xargs kill -9

Scheduler submission returns 127
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* **Symptom**: ``sbatch: command not found``
* **Cause**: ANSYS environment module not loaded or scheduler client not installed.
* **Fix**: Ensure the scheduler client is in ``$PATH`` or load the module:

.. code-block:: bash

   module load slurm

Jobs stuck in “queued” state
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* **Symptom**: Jobs never start despite idle CPUs.
* **Cause**: Resource limits too strict (``max_cpu_percent`` too low).
* **Fix**: Relax limits in :class:`ResourceLimits` or disable throttling:

.. code-block:: python

   ResourceLimits(max_cpu_percent=100)

-----------------------
Security Considerations
-----------------------

* **Bind address**: never expose ``--host 0.0.0.0`` on public networks
  without a firewall or reverse proxy.
* **Input validation**: all JSON payloads are validated against strict
  dataclass fields; arbitrary code execution is not possible.
* **File paths**: the service does **not** perform path traversal checks;
  run inside a container with read-only project mounts if untrusted users
  submit jobs.
* **Secrets**: scheduler passwords or API tokens should be injected via
  environment variables, not checked into YAML files.

-----------------
Performance Tuning
-----------------

High-throughput scenarios
~~~~~~~~~~~~~~~~~~~~~~~~~

* Increase ``max_concurrent_jobs`` only after verifying CPU **and** I/O
  head-room.
* Place the **temporary directory** (`HFSS3DLayoutBatchOptions.temp_directory`)
  on a **local NVMe** disk to avoid network latency.
* Disable **real-time log streaming** (`monitor=False`) if stdout is
  voluminous.
* Use **priority queues** to keep short exploratory jobs from starving
  long-running production jobs.

-----------------
FAQ
-----------------

**Q**: Does the manager restart failed jobs automatically?
**A**: No; clients must re-submit after inspecting the error field.

**Q**: Can I change the ANSYS version per job?
**A**: Yes—provide the full path in ``ansys_edt_path`` inside each
:class:`HFSSSimulationConfig`.

--------------------------
Complete API description
--------------------------

.. currentmodule:: pyedb.workflows.job_manager

.. autosummary::
   :toctree: _autosummary
   :template: custom-class-template.rst
   :nosignatures:

   job_manager_handler.JobManagerHandler
   job_submission.HFSSSimulationConfig
   job_submission.SchedulerOptions
   job_submission.MachineNode
   job_submission.HFSS3DLayoutBatchOptions
   job_submission.SchedulerType
   service.JobManager
   service.ResourceLimits
   service.JobStatus
   service.JobInfo
   service.ResourceMonitor
   service.JobPoolManager

-----------------
See also
-----------------

* :ref:`pyedb` - PyEDB documentation
* :ref:`aiohttp` - aiohttp documentation
* :ref:`socketio` - Socket.IO documentation