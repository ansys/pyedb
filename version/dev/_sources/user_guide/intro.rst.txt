Basic tutorial
==============

This tutorial walks you through creating a simple EDB from scratch using the pure Python client connected to the
``ansys-edb-core`` gRPC service.

Prerequisites
-------------
*   The PyEDB client is installed (`pip install pyedb`).
*   The ``ansys-edb-core`` service is installed and available (see :doc:`../installation`).

Import and Initialize with a Context Manager
--------------------------------------------

.. code-block:: python

   from pyedb import Edb
   from pyedb.libraries.rf_libraries.base_functions import CPW

   # Specify a path for the new EDB project
   edb_path = "/tmp/my_first_project.aedb"  # Note: Using a Linux path!

   # Create a new EDB project using a context manager
   edb = Edb(edbversion="2025.2")

   # Define materials and stackup
   edb.materials.add_conductor_material(name="gold", conductivity=4.1e7)
   edb.materials.add_dielectric_material(
       name="silicon", permittivity=11.9, dielectric_loss_tangent=0.01
   )
   edb.materials.add_dielectric_material(
       name="air", permittivity=1, dielectric_loss_tangent=0
   )

   edb.stackup.add_layer(
       layer_name="METAL_BOT",
       material="gold",
       thickness="4um",
       layer_type="signal",
       fillMaterial="air",
   )
   edb.stackup.add_layer(
       layer_name="substrate",
       base_layer="METAL_BOT",
       material="silicon",
       thickness="100um",
       layer_type="dielectric",
   )
   edb.stackup.add_layer(
       layer_name="METAL_TOP",
       base_layer="substrate",
       material="gold",
       thickness="4um",
       layer_type="signal",
       fillMaterial="SiO2",
   )

   # Create a simple CPW transimission line
   cpw = CPW(
       edb_cell=edb,
       width=10e-6,
       gap=5e-6,
       layer="METAL_TOP",
       ground_net="GND",
       ground_layer="METAL_BOT",
       length=1e-3,
   )
   cpw.substrate.er = edb.materials["silicon"].permittivity
   cpw.substrate.h = 100e-6  # 100um
   cpw.create()

   # Save the EDB project to the specified path
   edb.save()
   edb.close()

   print("EDB project created successfully on the server!")