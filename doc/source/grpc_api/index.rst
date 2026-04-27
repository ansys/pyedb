=============
API reference
=============

This section documents the public PyEDB gRPC API for EDB applications and modules.
Use the search feature or the links below to browse the available package,
subpackage, class, and method references.

The ``Edb`` class is the main entry point for the gRPC workflow. Once an
``Edb`` instance is initialized, the related database helpers, applications,
and methods become available from that object.

If EDB is launched within the ``HfssdLayout`` class, EDB is available in read-only mode.

.. note:: PyEDB supports gRPC.

   Starting with ANSYS release 2025.2, PyEDB is beta-compatible with gRPC.
   The main advantages are:

   - Better compatibility with Linux
   - Better performance starting with ANSYS release 2026.1

   PyEDB gRPC provides backward compatibility with previous versions.

   The default value of the ``grpc`` flag is ``False``, which means that PyEDB
   uses the DotNet implementation unless gRPC is explicitly enabled. PyEDB gRPC
   is the long-term supported implementation, and new features are developed for
   it first. Users are therefore encouraged to migrate to gRPC when possible.

   For backend compatibility and migration guidance, see :doc:`../getting_started/backend_compatibility_migration`.

To enable PyEDB gRPC, use one of these options:

*   Explicit import
*   Using grpc flag

.. code:: python

   # Explicit import
   from pyedb.grpc.edb import Edb

   # Using grpc flag
   from pyedb import Edb

   edb = Edb(edbpath=r"my_edb_path", edbversion="2026.1", grpc=True)


API documentation
-----------------

The public gRPC reference is organized around the top-level package, the
``database`` subpackage, and the ``edb`` module.

.. toctree::
   :maxdepth: 5

   database <../autoapi/pyedb/grpc/database/index>
   edb <../autoapi/pyedb/grpc/edb/index>
