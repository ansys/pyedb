Getting Started: Your First Script
==================================

This tutorial walks you through creating a simple EDB from scratch using the pure Python client connected to the ``ansys-edb-core`` gRPC service.

Prerequisites
-------------
*   The PyEDB client is installed (`pip install pyedb`).
*   The ``ansys-edb-core`` service is installed and available (see :doc:`../installation`).

Step 1: Import and Initialize with a Context Manager
----------------------------------------------------
We use a `with` statement to ensure the connection to the gRPC service is properly opened and closed, even if an error occurs.

.. code-block:: python

   import pyedb

   # Specify a path for the new EDB project
   edb_path = "/tmp/my_first_project.aedb"  # Note: Using a Linux path!

   # Use a context manager for safe resource handling
   with pyedb.Edb(edbpath=edb_path, edbversion="2025.2") as edb:
        # All operations happen within this block
        print(f"Connected to EDB core service: {edb.core_server_version}")

        # Step 2: Define a Material
        edb.materials.add_material("my_copper", conductivity=5.8e7)

        # Step 3: Create a Primitive Trace
        points = [[0.0, 0.0], [5e-3, 0.0], [5e-3, 5e-3]]
        trace = edb.modeler.create_path(
            points,
            layer_name="TOP",
            width=100e-6,
            material="my_copper",
            net_name="my_net"
        )

        # Step 4: Save is automatic when exiting the block, but can be manual.
        edb.save()
   # The connection is automatically closed here

   print("EDB project created successfully on the server!")