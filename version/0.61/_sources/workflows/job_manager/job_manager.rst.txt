.. _job_manager_backend:

================================================================================
PyEDB job manager backend—production documentation
================================================================================

.. contents:: Table of Contents
   :depth: 3

--------
Overview
--------

The job manager backend is a **hybrid async/sync service** that schedules and
monitors HFSS / 3D-Layout simulations on:

* Local workstations (sub-process)
* Enterprise clusters (SLURM, LSF, PBS, Windows-HPC)

It exposes **thread-safe** synchronous façades for legacy code bases while
keeping a fully **asynchronous core** for high-throughput scenarios.

.. mermaid::
   :caption: High-level architecture

   graph TD
      subgraph "Sync World (Legacy PyEDB)"
         A[PyEDB Script] -->|uses| B[JobManagerHandler]
      end

      subgraph "Async Core"
         B -->|starts thread| C[asyncio Event Loop]
         C --> D[aiohttp Web Server]
         C --> E[JobManager]
         E --> F[ResourceMonitor]
         E --> G[SchedulerManager]
      end

      E -->|subprocess| H[Local ansysedt]
      G -->|sbatch / bsub| I[SLURM / LSF]

      D --> J[REST clients]
      D --> K[Web UI]

-----------------
Module Reference
-----------------

job_manager_handler.py
~~~~~~~~~~~~~~~~~~~~~~
**Thread-safe synchronous façade**

* Bridges blocking code to the async ``JobManager`` without exposing ``asyncio``
* Auto-detects ANSYS installation and cluster scheduler
* Starts / stops a daemon thread hosting the aiohttp server
* Provides convenience helpers such as ``create_simulation_config()``

job_submission.py
~~~~~~~~~~~~~~~~~
**Cross-platform simulation launcher**

* Immutable data models: ``HFSSSimulationConfig``, ``SchedulerOptions``, ``MachineNode``
* Generates ready-to-run shell commands or batch scripts (SLURM/LSF)
* Entry point: ``create_hfss_config()`` → ``config.run_simulation()``

service.py
~~~~~~~~~~
**Async job manager & REST layer**

* ``JobManager``: priority queues, resource limits, Socket. IO push
* ``ResourceMonitor``: async telemetry (CPU, RAM, disk)
* ``SchedulerManager``: live cluster introspection (partitions, queues)
* Self-hosted aiohttp application with REST + WebSocket endpoints

-----------------
REST API
-----------------

Base URL defaults to ``http://localhost:8080``.
All JSON payloads use ``Content-Type: application/json``.

Jobs
~~~~
.. list-table::
   :header-rows: 1

   * - Method
     - Route
     - Description
     - Payload
     - Response
   * - ``POST``
     - ``/jobs/submit``
     - Queue new simulation
     - ``{"config": {...}, "priority": 0}``
     - ``{"job_id": "uuid", "status": "queued"}``
   * - ``GET``
     - ``/jobs``
     - List all jobs
     - —
     - JSON array
   * - ``POST``
     - ``/jobs/{id}/cancel``
     - Cancel queued / running job
     - —
     - ``{"success": true}``
   * - ``POST``
     - ``/jobs/{id}/priority``
     - Change job priority
     - ``{"priority": 5}``
     - ``{"success": true}``

Resources & Queues
~~~~~~~~~~~~~~~~~~
.. list-table::
   :header-rows: 1

   * - Method
     - Route
     - Description
     - Response
   * - ``GET``
     - ``/resources``
     - Host telemetry snapshot
     - ``{"cpu_percent": 12.3, "memory_free_gb": 45.6, ...}``
   * - ``GET``
     - ``/queue``
     - Queue statistics
     - ``{"total_queued": 7, "running_jobs": 2, ...}``
   * - ``PUT``
     - ``/pool/limits``
     - Edit concurrency limits
     - ``{"max_concurrent_jobs": 4}``

Cluster Introspection
~~~~~~~~~~~~~~~~~~~~~
.. list-table::
   :header-rows: 1

   * - Method
     - Route
     - Description
     - Response
   * - ``GET``
     - ``/scheduler/partitions``
     - Available partitions / queues
     - JSON array
   * - ``GET``
     - ``/system/status``
     - Combined status object
     - Scheduler, resources, limits

WebSocket Events
~~~~~~~~~~~~~~~~
Connect to ``ws://host:port`` with Socket.IO.
Emitted server → client:

* ``job_queued``
* ``job_started``
* ``job_scheduled``
* ``job_completed``
* ``limits_updated``

-----------------
Quick Examples
-----------------

Synchronous (Legacy Code)
~~~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: python

   from pyedb.workflows.job_manager.backend.job_manager_handler import JobManagerHandler

   handler = JobManagerHandler()
   handler.start_service()

   cfg = handler.create_simulation_config(
       "/path/to/antenna.aedt", scheduler_type="slurm", cpu_cores=16
   )

   job_id = asyncio.run(handler.submit_job(cfg))
   print("Submitted", job_id)

   # Wait until finished
   while handler.manager.jobs[job_id].status not in {"completed", "failed"}:
       time.sleep(1)

   handler.close()

Asynchronous (Native Asyncio)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: python

   from pyedb.workflows.job_manager.backend.service import JobManager, ResourceLimits

   manager = JobManager(ResourceLimits(max_concurrent_jobs=4))

   config = HFSSSimulationConfig.from_dict({...})
   job_id = await manager.submit_job(config, priority=5)

   await manager.wait_until_all_done()

Command Line
~~~~~~~~~~~~
.. code-block:: bash

   python -m pyedb.workflows.job_manager.backend.job_manager_handler \
          --host 0.0.0.0 --port 8080

-----------------
Deployment Notes
-----------------

* The service is **self-contained**; no external database is required (jobs are
  stored in-memory).  For persistence, plug in a small SQLite layer inside
  ``JobManager.jobs``.

* When running inside **Docker**, expose port ``8080`` and mount the project
  directory into the container so that ``ansysedt`` can access ``.aedt`` files.

* **CPU / RAM limits** are soft limits; tune ``ResourceLimits`` to your
  workstation or cluster node size.

* **TLS termination** should be handled by an upstream reverse proxy (nginx,
  reverse proxy, etc.); the backend only speaks plain HTTP/WebSocket.

-----------------
See Also
-----------------

* :ref:`job_manager_handler_discussion`—architectural trade-offs
* ``examples/job_manager/``—full CLI & Jupyter demos
* `ANSYS HFSS batch options documentation <https://ansyshelp.ansys.com>`_