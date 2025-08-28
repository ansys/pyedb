Migration Guide: DotNet to gRPC
===============================

This guide helps you migrate scripts from the legacy ``pyedb.dotnet`` API to the modern gRPC-based PyEDB client.

Key Conceptual Changes
----------------------
1.  **Import Structure:** The top-level import is now the gRPC client.
2.  **No AEDT:** Your script does not requires AEDT to be running. It connects to the ``ansys-edb-core`` service.

Side-by-Side Code Comparison
----------------------------

**Initialization and Setup**

   .. code-block:: python
      :caption: Legacy DotNet (Archived)

      # This required AEDT to be installed on Windows and Linux
      from pyedb import Edb

      # This would start an AEDT process
      edb = Edb(edbpath=edb_path, version="2025.2", grpc=False)
      # ... your code ...
      edb.save()
      edb.close()  # Mandatory to close AEDT



   .. code-block:: python
      :caption: Modern gRPC (Recommended)

       # This connects to the standalone ansys-edb-core service
       from pyedb import Edb

       edb = Edb(edbpath=edb_path, version="2025.2", grpc=True)
       edb.save()
       edb.close()
       # Connection closed automatically when edb is closed.

 ..Note:: The RPC server can only run on single Python thread but can open multiple EDB instances.
          However if you close one edb instance, the default behavior is to close the server. Therefore the other EDB
          instances will be disconnected. To close an EDB instance without closing the server you can use the following code:

.. code-block:: python
   edb.close(terminate_rpc_session=False)


**Common Method Calls**
The core API (methods on `edb.modeler`, `edb.nets`, `edb.components`) is intentionally very similar to ease migration.
Most method names and signatures are unchanged. Check the :doc:`api` documentation for details.

.. code-block:: python
   :caption: Method calls are largely identical

   # Both APIs have the same high-level methods
   net = edb.nets["DDR0_DQ0"]
   net.name = "DDR0_DQ0_NEW"

   rect = edb.modeler.create_rectangle(
       layer_name="TOP", point1=[0, 0], point2=[10e-3, 5e-3]
   )

Handling Breaking Changes
-------------------------
If you encounter a method or property that existed in the `dotnet` API but is not yet implemented in the gRPC client,
you have two options:

1.  **Check for Alternatives:** The new API might have a differently named method or a new, more efficient way to
accomplish the same task. Check the :doc:`api` documentation.
2.  **Report the Gap:** Open an issue on the `PyEDB GitHub repository <https://github.com/ansys/pyedb/issues>`_. This
helps the development team prioritize which legacy features to port next.

Getting Help
------------
If you get stuck during migration, please search for or open a discussion on the
`GitHub Discussions <https://github.com/ansys/pyedb/discussions>`_ page. The community and development team can
provide guidance.