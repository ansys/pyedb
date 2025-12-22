Welcome to PyEDB |version|
==========================

**Useful links**:
`Installation <https://edb.docs.pyansys.com/version/stable/installation.html>`_ |
`Source Repository <https://github.com/ansys/pyedb>`_ |
`Issues <https://github.com/ansys/pyedb/issues>`_

PyEDB is a Python client library that provides a high-level interface to create, modify,
and analyze PCB designs by communicating with the ``ansys-edb-core`` gRPC service.

.. note::

   **Architecture Notice: Standalone gRPC Service**
   PyEDB is a standalone Python client library that connects to the ``ansys-edb-core`` gRPC service.

.. admonition:: For users of the legacy `pyedb.dotnet` API
   :class: danger

   The ``dotnet`` module is **deprecated and archived** with Ansys release 2026R1. Access the archived code and migration guide :ref:`here <archive>`.


Getting Started
===============

.. toctree::
   :maxdepth: 1

   why_pyedb
   installation
   user_guide/index
   migration_guide
   changelog

Reference
=========

.. toctree::
   :maxdepth: 1

   examples/index
   workflows/index
   grpc_api/index
   glossary
   troubleshooting

Project
=======

.. toctree::
   :maxdepth: 1

   contribution_guide
   archive



* :ref:`genindex`
