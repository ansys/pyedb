.. _comms_protocols:

Communication protocol: gRPC
=============================

When the gRPC backend is selected (``grpc=True``, or automatically for Ansys release 2026.1 and later),
PyEDB communicates with the ``ansys-edb-core`` service using **gRPC (Remote Procedure Calls)**. This is
the long-term supported communication protocol for PyEDB.

.. note::

   The DotNet backend (``grpc=False``) does not use gRPC. It loads the EDB .NET libraries directly into
   the Python process through the ``pythonnet`` bridge. For a full backend comparison, see
   :doc:`../getting_started/backend_compatibility_migration`.

The gRPC protocol offers key benefits over the DotNet backend:

*   **Headless operation:** Enables operation on servers without a GUI (for example Linux, Docker).
*   **Performance:** High-speed communication, ideal for processing large, complex designs.
*   **Reliability:** Robust connection handling and error reporting.
*   **Decoupled development:** The Python client and the core service can be updated independently.

Checking the connection
------------------------
You can check the status and version of the connection from your Python script.

.. code-block:: python

   from pyedb import Edb

   edb = Edb(edbpath="/tmp/my_project.aedb", version="2026.1", grpc=True)
   print(edb.version)
   edb.close()

If the connection was successful, you should see console output similar to this:

.. code-block:: console

   PyEDB INFO: gRPC mode enabled.
   PyEDB INFO: RPC server started, fast mode active
   PyEDB INFO: EDB initialized.
