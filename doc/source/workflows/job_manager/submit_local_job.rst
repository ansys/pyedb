.. _cli-submit-local-job:

********************************************************************************
``submit_local_job`` – submit HFSS jobs to the local job-manager
********************************************************************************

.. contents:: Table of contents
   :local:
   :depth: 2

Synopsis
========

.. code-block:: bash

   $ submit_local_job --help
   $ submit_local_job --project-path <PATH> [options]

Description
===========

``submit_local_job`` is an *async* command-line utility that ships with **PyEDB**.
It wraps the low-level ``pyedb.workflows.job_manager.backend.job_submission`` API
and pushes an HFSS project to the local job-manager REST service.

The utility is fully self-contained (only Python ≥ 3.8 and aiohttp are required)
and is intended for CI/CD pipelines, desktop automation, or interactive use.

Installation
============

Editable/development install
----------------------------

.. code-block:: bash

   $ git clone https://github.com/<org>/<repo>.git
   $ cd <repo>
   $ python -m pip install -e .

The console entry-point ``submit_local_job`` is automatically created by *setuptools*
via the following stanza in ``pyproject.toml`` (or ``setup.cfg``):

.. code-block:: toml

   [project.scripts]
   submit_local_job = "pyedb.workflows.cli.submit_local_job:main"

Arguments & Options
===================

.. sphinx_argparse_cli::
   :module: pyedb.workflows.cli.submit_local_job
   :func: build_parser
   :prog: submit_local_job
   :nested: full

Environment variables
=====================

.. envvar:: PYEDB_JOB_MANAGER_HOST

   Fallback value for ``--host`` if the option is omitted.

.. envvar:: PYEDB_JOB_MANAGER_PORT

   Fallback value for ``--port`` if the option is omitted.

Exit status
===========

===== =========================================================
Code  Meaning
===== =========================================================
``0`` Job configuration successfully submitted and accepted.
``1`` CLI validation error, missing file, or connection failure.
``2`` Unexpected runtime exception (stack trace printed to stderr).
===== =========================================================

Examples
========

Submit with explicit values
---------------------------

.. code-block:: bash

   $ submit_local_job \
         --host 127.0.0.1 \
         --port 8080 \
         --project-path "D:/Jobs/antenna.aedb" \
         --num-cores 16

Use environment defaults
------------------------

.. code-block:: bash

   $ export PYEDB_JOB_MANAGER_HOST=jobmgr.acme.com
   $ export PYEDB_JOB_MANAGER_PORT=80
   $ submit_local_job --project-path ~/feed_network.aedb

Troubleshooting
===============

Connection refused
------------------

Ensure the job-manager service is running and reachable:

.. code-block:: bash

   $ curl -i http://<host>:<port>/health

Verbose logging
---------------

Set the log level via the standard :mod:`logging` configuration, e.g.

.. code-block:: bash

   $ LOG_LEVEL=DEBUG submit_local_job ...

See also
========

* :ref:`job-manager-rest-api`
* :doc:`configuration_syntax`
* :doc:`../tutorials/submit_batch`