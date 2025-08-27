Common Tasks
============

This section provides quick recipes for everyday operations with PyEDB.

Accessing and Modifying Nets
----------------------------
.. code-block:: python

   from pyedb import Edb

   edb = Edb(edbpath=edb_path, version="2025.2", grpc=True)
   # Get a net by name
   net = edb.nets["DDR0_DQ0"]

   # Rename a net
   net.name = "DDR0_DQ0_NEW"

   # Get all net names
   all_net_names = list(edb.nets.netlist.keys())

Working with Components
-----------------------
.. code-block:: python

   from pyedn import Edb

   edb = Edb(edbpath=edb_path)
   # Get a component by name
   comp = edb.components["R1"]

   # Get component placement
   print(f"Component {comp.name} is at {comp.location}")

   # Set new placement
   comp.location = [0.01, 0.02]  # X, Y

Creating a Simple Simulation Setup
----------------------------------
.. code-block:: python

   from pyedb import Edb

   edb = Edb(edbpath=edb_path, version="2025.2", grpc=True)
   # Create a SIwave DC IR analysis setup
   setup = edb.create_siwave_dc_setup("my_dc_analysis")

   # Add a 3.3V voltage source
   vrm_components = edb.components.Others["J1"]
   positive_pin = vrm_components.pins["1"]
   negative_pin = vrm_components.pins["2"]
   edb.source_excitation.create_voltage_source(
       terminal=positive_pin, ref_terminal=negative_pin, magnitude=3.3, phase=0
   )

   # Save and close EDB
   edb.save()
   edb.close()