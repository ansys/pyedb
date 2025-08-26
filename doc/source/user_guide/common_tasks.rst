Common Tasks
============

This section provides quick recipes for everyday operations with PyEDB.

Accessing and Modifying Nets
----------------------------
.. code-block:: python

   with pyedb.Edb(edbpath=edb_path) as edb:
       # Get a net by name
       net = edb.nets["DDR0_DQ0"]
       
       # Rename a net
       net.name = "DDR0_DQ0_NEW"
       
       # Get all net names
       all_net_names = list(edb.nets.netlist.keys())

Working with Components
-----------------------
.. code-block:: python

   with pyedb.Edb(edbpath=edb_path) as edb:
       # Get a component by name
       comp = edb.components["R1"]
       
       # Get component placement
       placement = comp.placement
       print(f"Component {comp.name} is at {placement}")
       
       # Set new placement
       comp.placement = [0.01, 0.02, 45.0]  # X, Y, Rotation

Creating a Simple Simulation Setup
----------------------------------
.. code-block:: python

   with pyedb.Edb(edbpath=edb_path) as edb:
       # Create a SIwave DC IR analysis setup
       setup = edb.create_siwave_dc_ir_setup("my_dc_analysis")
       
       # Add a voltage source
       setup.create_voltage_source("VSource1", "VCC", "GND", 3.3)
       
       # Solve the setup
       setup.solve()