.. _submit_job_production:

********************************************************************************
Job submission—production notes & quick-start
********************************************************************************

.. contents:: Table of contents
   :local:
   :depth: 3

.. rubric:: Submit and monitor HFSS 3-D Layout simulations through the PyEDB job manager
   with **zero** additional infrastructure on your workstation or **full** cluster support
   (SLURM, LSF, PBS, Windows-HPC, …).

--------------------------------------------------------------------
Pre-requisites
--------------------------------------------------------------------
1. **ANSYS Electronics Desktop** must be installed.
2. The environment variable ``ANSYSEM_ROOT<rrr>`` must point to the
   installation directory, e.g.

   .. code-block:: bash

      export ANSYSEM_ROOT252=/ansys_inc/v252/Linux64      # 2025 R2
      # or on Windows
      set ANSYSEM_ROOT252=C:\Program Files\AnsysEM\v252\Win64

   The backend automatically discovers the newest release if several
   ``ANSYSEM_ROOT<rrr>`` variables are present.

3. (Cluster only) A **scheduler template** for your workload manager
   must exist in ``pyedb/workflows/job_manager/scheduler_templates/``.
   Out-of-the-box templates are provided for **SLURM** and **LSF**;
   PBS, Torque, Windows-HPC, or cloud batch systems can be added
   by dropping a new YAML file—no code change required.

--------------------------------------------------------------------
Overview—how it works
--------------------------------------------------------------------
The job manager is an *asynchronous* micro-service that is **automatically**
started in a background thread when you instantiate :class:`.JobManagerHandler`.
It exposes:

* REST & Web-Socket endpoints (``http://localhost:8080`` by default)
* Thread-safe synchronous façade for scripts / Jupyter
* Native async API for advanced integrations
* CLI utilities ``submit_local_job`` and ``submit_job_on_scheduler`` for shell / CI pipelines

The **same backend code path** is used regardless of front-end style; the difference is
**who owns the event loop** and **how control is returned to the caller**.

.. tip:: **Quick-start server (any OS)**

     Save the launcher script as ``start_service.py`` (see :ref:`start_service_script`) and run:

     .. code-block:: bash

        python start_service.py --host 0.0.0.0 --port 9090

     The service is ready when the line
     “✅ Job-manager backend listening on http://0.0.0.0:9090.”
     appears; leave the terminal open or daemonize it with your favourite supervisor.

.. tip::
   The backend **auto-detects** the scheduler:

   * **Windows workstation** → ``SchedulerType.NONE`` (local subprocess)
   * **Linux workstation** → ``SchedulerType.NONE`` (local subprocess)
   * **Linux cluster with SLURM** → ``SchedulerType.SLURM``
   * **Linux cluster with LSF** → ``SchedulerType.LSF``

   You can still override the choice explicitly if needed.

--------------------------------------------------------------------
Synchronous usage (scripts & notebooks)
--------------------------------------------------------------------
Perfect when you simply want to “submit and wait” without learning ``asyncio``.

.. code-block:: python
   :caption: local_sync_demo.py
   :lineno-start: 1

   from pyedb.workflows.job_manager.backend.job_submission import (
       create_hfss_config,
       SchedulerType,
   )
   from pyedb.workflows.job_manager.backend.job_manager_handler import JobManagerHandler

   project_path = r"D:\Jobs\my_design.aedb"

   handler = JobManagerHandler()  # discovers ANSYS install & scheduler
   handler.start_service()  # starts background aiohttp server

   config = create_hfss_config(
       project_path=project_path,
   )
   config.machine_nodes[0].cores = 16  # use 16 local cores

   job_id = handler.submit_job(config)  # blocks until job accepted
   print("submitted job_id")

   status = handler.wait_until_done(job_id)  # polls until terminal
   print(f"job finished with status: {status}")

   handler.close()  # graceful shutdown

Production notes
^^^^^^^^^^^^^^^^
* Thread-safe: multiple threads may submit or cancel concurrently.
* Resource limits (CPU, memory, disk, concurrency) are enforced; jobs stay queued
  until resources are free.
* ``atexit`` ensures clean shutdown even if the user forgets ``close()``.
* Cluster runs: change ``SchedulerType.NONE`` → ``SLURM``/``LSF`` and supply
  ``scheduler_options``; the code path remains identical.

--------------------------------------------------------------------
Asynchronous usage (CLI & programmatic)
--------------------------------------------------------------------
Use when you need **non-blocking** behaviour inside an ``async`` function or from
the shell / CI pipelines.

CLI—``submit_local_job``
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

Example—CLI (cluster)
"""""""""""""""""""""""
.. code-block:: bash

   $ submit_job_on_scheduler \
         --project-path "/shared/antenna.AEDB" \
         --partition hpclarge \
         --nodes 2 \
         --cores-per-node 32

The command returns immediately after the job is **queued**; use the printed ID
with ``wait_until_done`` or monitor via the web UI.

Programmatic—native asyncio
"""""""""""""""""""""""""""""
.. code-block:: python

   import asyncio
   from pyedb.workflows.job_manager.backend.service import JobManager
   from pyedb.workflows.job_manager.backend.job_submission import create_hfss_config


   async def main():
       manager = JobManager()  # same back-end
       config = create_hfss_config(
           project_path="antenna.AEDB",
           scheduler_type="SLURM",  # or "LSF", "NONE", …
           scheduler_options={
               "queue": "hpclarge",
               "nodes": 2,
               "cores_per_node": 32,
               "time": "04:00:00",
           },
       )
       job_id = await manager.submit_job(config, priority=5)
       await manager.wait_until_all_done()  # non-blocking wait
       print("all done")


   asyncio.run(main())

--------------------------------------------------------------------
Choosing between sync & async
--------------------------------------------------------------------
.. list-table::
   :widths: 50 50
   :header-rows: 1

   * - Synchronous (scripts / notebooks)
     - Asynchronous (services / CLI)
   * - No ``asyncio`` knowledge required.
     - Caller runs inside ``async def``; operations are ``await``-ed.
   * - Blocking calls—caller waits for result.
     - Non-blocking—event loop stays responsive.
   * - Ideal for **interactive** work, **CI pipelines**, **quick scripts**.
     - Ideal for **web servers**, **micro-services**, **GUI applications**.

.. _start_service_script:

--------------------------------------------------------------------
Stand-alone server launcher script
--------------------------------------------------------------------
The file ``start_service.py`` is a minimal wrapper around
:class:`.JobManagerHandler` that exposes only ``--host`` and ``--port``.
It is **not** installed by pip; copy it from the doc folder or the
previous code block and place it anywhere in your ``PATH``.

--------------------------------------------------------------------
See also
--------------------------------------------------------------------
* :ref:`job_manager_rest_api`–Complete endpoint reference
* :class:`.JobManagerHandler`–API reference (sync façade)
* :class:`.JobManager`–API reference (async core)
* :doc:`configuration_syntax`–All scheduler & solver options
* :doc:`../tutorials/submit_batch`–Bulk submissions on SLURM/LSF