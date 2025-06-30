==================
gRPC API reference
==================

This section describes EDB functions, classes, and methods
for EDB gRPC applications and modules. Use the search feature or click links
to view API documentation.

The PyEDB API includes classes for apps and modules. You must initialize the
``Edb`` class to get access to all modules and methods. All other classes and
methods are inherited into the ``Edb`` class.

If EDB is launched within the ``HfssdLayout`` class, EDB is accessible in read-only mode.

.. note:: PyEDB is now supporting gRPC
   **Starting ANSYS release 2025.2 PyEDB is compatible with gRPC.**
   The two main advantages are:
       - Better compatibility with Linux
       - PyEDB becomes ready to remote - client services

   If you want to know more about `gRPC <https://grpc.io>`_.

   PyEDB gRPC is providing backward compatibility with previous versions.

   The default grpc flag value is `False` so by default uses PyEDB DotNet.
   PyEDB gRPC becomes the long term supported version and new features are only implemented
   into this one. Therefore users are highly encouraged migrating to gRPC when possible to get the
   best user experience.

to enable PyEDB gRPC you have two options.
   - Explicit import
   - Using grpc flag

.. code:: python

   # Explicit import
   from pyedb.grpc.edb import Edb

   # Using grpc flag
   from pyedb import Edb

   edb = Edb(edbpath=r"my_edb_path", edbversion="2025.2", grpc=True)

.. toctree::
   :maxdepth: 3

   grpc/index








