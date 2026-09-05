Common Tasks
============

This section provides quick recipes for everyday operations with PyEDB.

Each recipe below is self-contained: it declares ``edb_path`` explicitly, opens the design, performs
the task, and closes the session. Replace ``edb_path`` with the path to your own ``.aedb`` folder.

Accessing and Modifying Nets
----------------------------
.. code-block:: python

   from pyedb import Edb

   edb_path = "my_project.aedb"
   edb = Edb(edbpath=edb_path, version="2026.1", grpc=False)

   # Get a net by name
   net = edb.nets["DDR0_DQ0"]

   # Rename a net
   net.name = "DDR0_DQ0_NEW"

   # Get all net names
   all_net_names = edb.nets.netlist

   edb.save()
   edb.close()

Working with Components
-----------------------
.. code-block:: python

   from pyedb import Edb

   edb_path = "my_project.aedb"
   edb = Edb(edbpath=edb_path, version="2026.1", grpc=False)

   # Get a component by name
   comp = edb.components["R1"]

   # Get component placement
   print(f"Component {comp.name} is at {comp.location}")

   # Set new placement
   comp.location = [0.01, 0.02]  # X, Y

   edb.save()
   edb.close()

Creating a Simple Simulation Setup
----------------------------------
.. code-block:: python

   from pyedb import Edb

   edb_path = "my_project.aedb"
   edb = Edb(edbpath=edb_path, version="2026.1", grpc=False)

   # Create a SIwave DC IR analysis setup
   setup = edb.simulation_setups.create_siwave_dcir_setup(name="my_dc_analysis")

   # Add a 3.3V voltage source between pins 1 and 2 of voltage regulator "J1"
   vrm_component = edb.components["J1"]
   positive_pin = vrm_component.pins["1"]
   negative_pin = vrm_component.pins["2"]
   edb.excitation_manager.create_voltage_source(
       terminal=positive_pin, ref_terminal=negative_pin, magnitude=3.3, phase=0
   )

   # Save and close EDB
   edb.save()
   edb.close()
