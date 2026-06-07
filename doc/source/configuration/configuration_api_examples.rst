Configuration API: practical examples
======================================

What is ``CfgData``?
---------------------

Think of ``CfgData`` as a **live blueprint** of your PCB design setup.
Instead of manually crafting a JSON file, you describe what you want—nets,
components, ports, setups, and geometry—through a clean Python object-oriented
API.  When you are happy with the blueprint, you hand it to PyEDB and it
applies every change to the open layout in a single atomic operation.

The key insight is that the builder **separates intent from execution**:

* You populate the builder incrementally—in any order, across multiple helper
  functions, or from data read from external sources.
* Nothing touches the EDB layout until you call ``edb.configuration.run(cfg)``.
* The same builder can also be serialized to a portable JSON or TOML file for
  version control, review, or reuse in another project.

This separates three concerns that are often tangled together in scripted
workflows: *definition*, *validation*, and *application*.

Creating a builder
------------------

**From an active EDB session (recommended)**

When you already have an open EDB layout the preferred way is:

.. code-block:: python

   from pyedb import Edb

   edb = Edb("my_design.aedb", version="2026.1")
   cfg = edb.configuration.create_config_builder()

``create_config_builder()`` returns a ``CfgData`` instance that is *bound* to
the live session. Bound builders can read existing objects from the database.
This is useful for ``cfg.components.get("U1")``, ``cfg.stackup.get_layer("1_Top")``,
``cfg.nets.get("GND")``, etc.

**Standalone (no session required)**

.. code-block:: python

   from pyedb.configuration import CfgData

   cfg = CfgData()

Standalone builders are ideal for templates, CI pipelines, or situations where
you want to author a configuration before opening any design.

Loading from an existing file or dictionary
-------------------------------------------

You can initialize a builder from a previously saved configuration so that you
only override the values that need to change:

.. code-block:: python

   from pyedb.configuration import CfgData

   # Start from a JSON baseline and tweak one setup
   cfg = CfgData.from_json("baseline_config.json")
   cfg.setups.add_hfss_setup("new_setup", adapt_type="broadband")
   cfg.to_json("updated_config.json")

   # Or build from a plain dictionary (for example, loaded from a database)
   cfg2 = CfgData.from_dict({"nets": {"signal_nets": ["CLK", "DATA"]}})

Applying a configuration to the layout
---------------------------------------

Passing a builder directly to ``run()`` serializes it internally, so you never
need to call ``to_dict()`` yourself:

.. code-block:: python

   edb.configuration.run(cfg)  # load + apply in one call
   edb.configuration.run("my.json")  # from a file
   edb.configuration.run({"nets": {}})  # from a raw dict

Exporting to a file or dictionary
-----------------------------------

.. code-block:: python

   cfg.to_json("my_config.json")  # human-readable JSON
   cfg.to_toml("my_config.toml")  # TOML alternative
   payload = cfg.to_dict()  # plain Python dict (for inspection or APIs)

The exported file can later be applied without any Python script:

.. code-block:: python

   edb.configuration.run("my_config.json")

Practical examples
------------------

The following examples are derived from the integration test suite and
demonstrate real-world usage patterns, from simple coaxial-port workflows to
full stackup and modeler operations.

.. note::

   All examples assume ``edb`` is an open :class:`Edb` session.
   examples below assume that the design *ANSYS-HSD_V1* is open.
   Replace it with ``Edb("your_design.aedb", ...)``.

Example 1: Coax ports with explicit solder-ball geometry
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Perform a PCIe Gen4 channel cut-out, assign cylindrical solder balls on the
BGA component, place one coax port per signal net, and add an HFSS setup with a
linear sweep, all in about fifteen lines.

.. code-block:: python

   from pyedb import Edb

   edb = Edb("ANSYS-HSD_V1.aedb", version="2026.1")

   # Signal nets of interest
   signal_nets = [
       "PCIe_Gen4_RX0_P",
       "PCIe_Gen4_RX0_N",
       "PCIe_Gen4_RX1_P",
       "PCIe_Gen4_RX1_N",
       "PCIe_Gen4_RX2_P",
       "PCIe_Gen4_RX2_N",
       "PCIe_Gen4_RX3_P",
       "PCIe_Gen4_RX3_N",
   ]

   cfg = edb.configuration.create_config_builder()

   # Classify nets — signal_nets / reference_nets are reusable list properties
   cfg.nets.add_signal_nets(signal_nets)
   cfg.nets.add_reference_nets(["GND"])

   # Cut the board to the nets of interest (3 mm expansion, convex hull)
   cfg.operations.add_cutout(
       signal_nets=cfg.nets.signal_nets,
       reference_nets=cfg.nets.reference_nets,
       extent_type="ConvexHull",
       expansion_size=3e-3,
   )

   # HFSS setup + linear sweep from 1 GHz to 10 GHz in 0.5 GHz steps
   setup = cfg.setups.add_hfss_setup(name="HFSS_PCIe")
   setup.add_frequency_sweep(
       name="Sweep_LIN",
       start="1GHz",
       stop="10GHz",
       step_or_count="0.5GHz",  # step string → linear_scale distribution
   )

   # Set 300 µm cylindrical solder balls on U1 before placing coax ports
   # (solder-ball geometry is a component property, not a port property)
   u1 = cfg.components.get("U1")
   u1.set_solder_ball_properties(shape="cylinder", diameter="300um", height="300um")

   # One coax port per signal net on U1
   cfg.ports.add_coax_port(reference_designator="U1", net_list=signal_nets)

   # Apply everything to the layout
   edb.configuration.run(cfg)
   edb.close()

Example 2: Circuit ports via pin groups
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use pin groups to bundle the GND pins on U1 into a single reference and create
one differential circuit port per signal net pair.

.. code-block:: python

   from pyedb import Edb

   edb = Edb("ANSYS-HSD_V1.aedb", version="2026.1")

   signal_nets = [
       "PCIe_Gen4_RX0_P",
       "PCIe_Gen4_RX0_N",
       "PCIe_Gen4_RX1_P",
       "PCIe_Gen4_RX1_N",
       "PCIe_Gen4_RX2_P",
       "PCIe_Gen4_RX2_N",
       "PCIe_Gen4_RX3_P",
       "PCIe_Gen4_RX3_N",
   ]

   cfg = edb.configuration.create_config_builder()
   cfg.nets.add_signal_nets(signal_nets)
   cfg.nets.add_reference_nets(["GND"])

   # Same convex-hull cutout as before
   cfg.operations.add_cutout(
       signal_nets=cfg.nets.signal_nets,
       reference_nets=cfg.nets.reference_nets,
       extent_type="ConvexHull",
       expansion_size=3e-3,
   )

   # HFSS setup
   setup = cfg.setups.add_hfss_setup(name="HFSS_PCIe")
   setup.add_frequency_sweep(
       name="Sweep_LIN", start="1GHz", stop="10GHz", step_or_count="0.5GHz"
   )

   # Create one pin group per net on U1 — the builder accepts a list for bulk creation
   cfg.pin_groups.add(reference_designator="U1", nets="GND")
   cfg.pin_groups.add(reference_designator="U1", nets=cfg.nets.signal_nets)

   # One circuit port per signal net: positive on the signal net, negative on GND
   for net in cfg.nets.signal_nets:
       cfg.ports.add_circuit_port(
           reference_designator="U1",
           positive_net=net,
           negative_net="GND",
       )

   edb.configuration.run(cfg)
   edb.close()

Example 3: Auto-discover solder-ball dimensions from existing component data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When solder-ball dimensions are already encoded in the component definition,
omit ``diameter`` and ``height`` and let PyEDB read them from the footprint.

.. code-block:: python

   from pyedb import Edb

   edb = Edb("ANSYS-HSD_V1.aedb", version="2026.1")

   signal_nets = [
       "PCIe_Gen4_RX0_P",
       "PCIe_Gen4_RX0_N",
       "PCIe_Gen4_RX1_P",
       "PCIe_Gen4_RX1_N",
       "PCIe_Gen4_RX2_P",
       "PCIe_Gen4_RX2_N",
       "PCIe_Gen4_RX3_P",
       "PCIe_Gen4_RX3_N",
   ]

   cfg = edb.configuration.create_config_builder()
   cfg.nets.add_signal_nets(signal_nets)
   cfg.nets.add_reference_nets(["GND"])
   cfg.operations.add_cutout(
       signal_nets=cfg.nets.signal_nets,
       reference_nets=cfg.nets.reference_nets,
       extent_type="ConvexHull",
       expansion_size=3e-3,
   )

   setup = cfg.setups.add_hfss_setup(name="HFSS_PCIe")
   setup.add_frequency_sweep(
       name="Sweep_LIN", start="1GHz", stop="10GHz", step_or_count="0.5GHz"
   )

   # Pass only shape + reference_designator — diameter and height are inferred
   # from the existing padstack geometry of component U1
   u1 = cfg.components.get("U1")
   u1.set_solder_ball_properties(shape="cylinder", reference_designator="U1")

   cfg.ports.add_coax_port(reference_designator="U1", net_list=signal_nets)

   edb.configuration.run(cfg)
   edb.close()

Example 4: Net classification and live querying
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The builder exposes a ``nets.get()`` method that queries the live EDB session so
you can inspect a net's current classification before deciding how to categorize
it.  ``add_signal_nets`` / ``add_power_ground_nets`` are mutually exclusive: a
net is automatically removed from any other list when it is added to a new one.

.. code-block:: python

   from pyedb import Edb

   edb = Edb("ANSYS-HSD_V1.aedb", version="2026.1")
   cfg = edb.configuration.create_config_builder()

   # Query a net that currently exists in the EDB layout
   net = cfg.nets.get("PCIe_Gen4_RX0_P")
   print(net.classification)  # "signal"
   print(net.is_power_ground)  # False

   # Reclassify it as power/ground …
   cfg.nets.add_power_ground_nets(["PCIe_Gen4_RX0_P"])
   print("PCIe_Gen4_RX0_P" in cfg.nets.power_ground_nets)  # True

   # … then move it back to signal — it is removed from power_ground_nets automatically
   cfg.nets.add_signal_nets(["PCIe_Gen4_RX0_P"])
   print("PCIe_Gen4_RX0_P" in cfg.nets.signal_nets)  # True
   print("PCIe_Gen4_RX0_P" in cfg.nets.power_ground_nets)  # False

   # Finalise as power/ground and apply — the EDB layout is updated
   cfg.nets.add_power_ground_nets(["PCIe_Gen4_RX0_P"])
   edb.configuration.run(cfg)

   # Verify the change was written to the database
   print(edb.nets.nets["PCIe_Gen4_RX0_P"].is_power_ground)  # True
   edb.close()

Example 5: Gap port on an existing polygon
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Attach a gap port to the midpoint of the first arc of an existing polygon.
The primitive and its edge point are read directly from the live EDB layout.

.. code-block:: python

   from pyedb import Edb

   edb = Edb("ANSYS-HSD_V1.aedb", version="2026.1")
   cfg = edb.configuration.create_config_builder()

   # Pick the first polygon in the layout and one of its edge midpoints
   polygon = edb.layout.polygons[0]
   midpoint = polygon.arcs[0].midpoint

   # add_gap_port accepts live EDB primitives directly
   cfg.ports.add_gap_port(
       name="my_gap_port",
       primitive=polygon,
       point_on_edge=midpoint,
       pec_launch_width="0.02mm",
   )

   edb.configuration.run(cfg)
   print("my_gap_port" in edb.ports)  # True
   edb.close()

Example 6: Differential wave port
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Define a differential wave port on two existing trace primitives. The positive
and negative terminals are placed at the start and end of each trace center line
for a clean modal excitation.

.. code-block:: python

   from pyedb import Edb

   edb = Edb("ANSYS-HSD_V1.aedb", version="2026.1")
   cfg = edb.configuration.create_config_builder()

   # Retrieve the two complementary traces from the live layout
   path_p = edb.nets.nets["PCIe_Gen4_RX3_P"].primitives[0]
   path_n = edb.nets.nets["PCIe_Gen4_RX3_N"].primitives[0]

   # Use the centre-line endpoints as edge probe points
   point_p = path_p.center_line[0]
   point_n = path_p.center_line[-1]

   cfg.ports.add_diff_wave_port(
       name="diff_wave_RX3",
       positive_primitive=path_p,
       positive_terminal_point=point_p,
       negative_primitive=path_n,
       negative_terminal_point=point_n,
   )

   edb.configuration.run(cfg)

   port = edb.ports["diff_wave_RX3"]
   print(port.hfss_type)  # "Wave"
   print(len(port.terminals))  # 2
   edb.close()

Example 7: Single-ended wave port
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Place a wave port on the start of a single trace. The primitive is looked up
from the active net object so you never need to know the internal primitive ID.

.. code-block:: python

   from pyedb import Edb

   edb = Edb("ANSYS-HSD_V1.aedb", version="2026.1")
   cfg = edb.configuration.create_config_builder()

   # Get the first primitive on the RX3_P net and use its first centre-line point
   path = edb.nets.nets["PCIe_Gen4_RX3_P"].primitives[0]
   point_on_edge = path.center_line[0]

   cfg.ports.add_wave_port(
       name="wave_RX3_P",
       primitive=path,
       point_on_edge=point_on_edge,
   )

   edb.configuration.run(cfg)

   port = edb.ports["wave_RX3_P"]
   print(port.hfss_type)  # "Wave"
   print(port.net_name)  # "PCIe_Gen4_RX3_P"
   edb.close()

Example 8: Full HFSS setup with broadband adaptation and auto mesh
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Configure an HFSS setup with broadband adaptive meshing, automatic mesh
seeding, and a linear-scale sweep, all from the builder.

.. code-block:: python

   from pyedb import Edb

   edb = Edb("ANSYS-HSD_V1.aedb", version="2026.1")
   cfg = edb.configuration.create_config_builder()

   signal_nets = [
       "PCIe_Gen4_RX0_P",
       "PCIe_Gen4_RX0_N",
       "PCIe_Gen4_RX1_P",
       "PCIe_Gen4_RX1_N",
       "PCIe_Gen4_RX2_P",
       "PCIe_Gen4_RX2_N",
       "PCIe_Gen4_RX3_P",
       "PCIe_Gen4_RX3_N",
   ]

   # Solder balls + coax ports are needed so auto-mesh can target the right nets
   u1 = cfg.components.get("U1")
   u1.set_solder_ball_properties(shape="cylinder", reference_designator="U1")
   cfg.ports.add_coax_port(reference_designator="U1", net_list=signal_nets)

   # Create the HFSS setup
   hfss = cfg.setups.add_hfss_setup(name="HFSS_Full")

   # Linear sweep in 0.5 GHz steps from 1 GHz to 10 GHz
   hfss.add_frequency_sweep(
       name="Sweep_LIN", start="1GHz", stop="10GHz", step_or_count="0.5GHz"
   )

   # Automatic mesh seeding — seeds trace widths and via side counts
   hfss.set_auto_mesh_operation(
       enabled=True,
       trace_ratio_seeding=3.0,
       signal_via_side_number=12,
   )

   # Broadband adaptive solution (sweeps 5–10 GHz, tight 0.05 tolerance)
   hfss.set_broadband_adaptive(
       low_freq="5GHz",
       high_freq="10GHz",
       max_delta=0.05,
       max_passes=30,
   )

   edb.configuration.run(cfg)

   setup = edb.setups["HFSS_Full"]
   print(setup.frequency_sweeps["Sweep_LIN"].frequency_string[0])
   # "LIN 1GHz 10GHz 0.5GHz"
   edb.close()

Example 9: SIwave AC setup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add a SIwave AC setup tuned for SI accuracy and a fine linear sweep from DC to
35 GHz.

.. code-block:: python

   from pyedb import Edb

   edb = Edb("ANSYS-HSD_V1.aedb", version="2026.1")
   cfg = edb.configuration.create_config_builder()

   # si_slider_position: 0 = Speed, 1 = Balanced, 2 = Accuracy
   siwave_ac = cfg.setups.add_siwave_ac_setup(
       name="SIwave_AC",
       use_si_settings=True,
       si_slider_position=2,
   )

   # Linear sweep from 0 GHz to 35 GHz in 0.1 GHz steps
   siwave_ac.add_frequency_sweep(
       name="Sweep_SIwave",
       start="0GHz",
       stop="35GHz",
       step_or_count="0.1GHz",
   )

   edb.configuration.run(cfg)

   setup = edb.setups["SIwave_AC"]
   print(setup.si_slider_position)  # 2
   edb.close()

Example 10: SIwave DC setup with thermal export
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a SIwave DC IR-drop setup at maximum accuracy and enable thermal loss
data export for downstream thermal analysis.

.. code-block:: python

   from pyedb import Edb

   edb = Edb("ANSYS-HSD_V1.aedb", version="2026.1")
   cfg = edb.configuration.create_config_builder()

   # dc_slider_position: 0 = Speed, 1 = Balanced, 2 = Accuracy
   cfg.setups.add_siwave_dc_setup(
       name="SIwave_DC",
       dc_slider_position=2,
       export_dc_thermal_data=True,  # write thermal CSV after solve
   )

   edb.configuration.run(cfg)

   edb_setup = edb.setups["SIwave_DC"]
   print(edb_setup.dc_settings.dc_slider_position)  # 2
   print(edb_setup.dc_ir_settings.export_dc_thermal_data)  # True
   edb.close()

Example 11: Define a new padstack and place an instance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Define a custom via padstack (including hole, pad, and anti-pad sizes) and
place one instance at a specific XY coordinate on the board.

.. code-block:: python

   from pyedb import Edb

   edb = Edb("ANSYS-HSD_V1.aedb", version="2026.1")
   cfg = edb.configuration.create_config_builder()

   # Define the via padstack — through all layers
   cfg.padstacks.add_definition(
       name="my_via",
       hole_plating_thickness="10um",
       material="copper",
       hole_range="through",
       hole_diameter="200um",
       pad_diameter="300um",
       anti_pad_diameter="400um",
   )

   # Place one instance of the new definition at (1 mm, 2 mm) on net "GND"
   cfg.padstacks.add_instance(
       name="my_via_inst",
       net_name="GND",
       definition="my_via",
       position=[1e-3, 2e-3],
   )

   edb.configuration.run(cfg)

   # Verify the definition and instance were created
   via_def = edb.padstacks.definitions["my_via"]
   print(via_def.hole_diameter)  # 200e-6
   print(via_def.hole_plating_thickness)  # 10e-6
   instance = via_def.instances[0]
   print(instance.name)  # "my_via_inst"
   print(instance.position)  # [0.001, 0.002]
   edb.close()

Example 12: Geometry creation via the modeler section
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create traces, circles, rectangles, and polygons entirely through the builder
without touching the low-level geometry API.  All primitives are created when
``run()`` is called.

.. code-block:: python

   from pyedb import Edb

   edb = Edb("ANSYS-HSD_V1.aedb", version="2026.1")
   cfg = edb.configuration.create_config_builder()

   # ── Trace ────────────────────────────────────────────────────────────────
   # An L-shaped 100 µm trace on layer 1_Top going right then up
   cfg.modeler.add_trace(
       name="my_trace",
       layer="1_Top",
       width="100um",
       net_name="SIG",
       start_cap_style="flat",
       end_cap_style="flat",
       path=[[0, 0], [0, 1e-3], [1e-3, 1e-3]],
   )

   # ── Circular plane ───────────────────────────────────────────────────────
   # A 2 mm radius circle centred at (5 mm, 5 mm)
   cfg.modeler.add_circular_plane(
       layer="1_Top",
       name="my_circle",
       net_name="GND",
       radius="2mm",
       position=[5e-3, 5e-3],
   )

   # ── Rectangular plane ────────────────────────────────────────────────────
   # A rectangle from (0,0) to (0, 5 mm)
   cfg.modeler.add_rectangular_plane(
       layer="1_Top",
       name="my_rectangle",
       lower_left_point=[0, 0],
       upper_right_point=[0, 5e-3],
   )

   # ── Polygon plane ────────────────────────────────────────────────────────
   # A small triangle (polygon must be closed — first == last point)
   cfg.modeler.add_polygon_plane(
       layer="1_Top",
       name="my_polygon",
       net_name="SIG2",
       points=[[0, 0], [0, 2e-3], [2e-3, 2e-3], [0, 0]],
   )

   edb.configuration.run(cfg)

   # Verify each primitive was created with the expected attributes
   trace = edb.layout.find_primitive(name="my_trace")[0]
   print(trace.layer_name)  # "1_Top"
   print(trace.net_name)  # "SIG"

   circle = edb.layout.find_primitive(name="my_circle")[0]
   print(circle.center)  # (0.005, 0.005)
   print(circle.radius)  # ~0.002

   edb.close()

Example 13: Stackup materials and layers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add custom dielectric and conductor materials to the material library and
insert a new dielectric layer into the stackup.

.. code-block:: python

   from pyedb import Edb

   edb = Edb("ANSYS-HSD_V1.aedb", version="2026.1")
   cfg = edb.configuration.create_config_builder()

   # Inspect how many layers the design already has
   layers = cfg.stackup.get_layers()
   print(f"Design has {len(layers)} layers")

   # Define a low-loss dielectric material
   cfg.stackup.add_material(
       name="my_dielectric",
       permittivity=3.48,
       dielectric_loss_tangent=0.02,
   )

   # Define a high-conductivity metal material
   cfg.stackup.add_material(
       name="my_metal",
       conductivity=6e7,
   )

   # Insert a new dielectric layer using the custom material
   cfg.stackup.add_dielectric_layer(
       name="my_diel_layer",
       material="my_dielectric",
       thickness="250um",
   )

   edb.configuration.run(cfg)

   # Verify the materials and layer were registered in the design
   diel = edb.materials.materials["my_dielectric"]
   print(diel.permittivity)  # ~3.48
   print(diel.dielectric_loss_tangent)  # ~0.02

   metal = edb.materials.materials["my_metal"]
   print(metal.conductivity)  # ~6e7

   layer = edb.stackup.layers["my_diel_layer"]
   print(layer.material)  # "my_dielectric"
   print(layer.thickness)  # 250e-6
   edb.close()

Example 14: Assign models from the Ansys vendor component library
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the vendor library to assign S-parameter models for discrete capacitors and
inductors without maintaining local ``.snp`` files. PyEDB looks up the part in
the Ansys built-in library, converts its scikit-rf ``Network`` to a Touchstone
file in a cache directory, and calls ``assign_s_param_model()`` automatically.

.. code-block:: python

   from pyedb import Edb

   edb = Edb("ANSYS-HSD_V1.aedb", version="2026.1")
   cfg = edb.configuration.create_config_builder()

   # ── Bypass capacitor — model from the Murata GRM series ──────────────────
   c1 = cfg.components.add("C1", part_type="capacitor")
   c1.set_vendor_library_model(
       vendor="Murata",
       series="GRM",
       part_name="GRM155R61A104KA01D",
       reference_net="GND",
       # touchstone_cache_dir is optional; defaults to <aedb>/component_lib_cache/
   )

   # ── Decoupling capacitor — another part from the same series ─────────────
   c2 = cfg.components.add("C2", part_type="capacitor")
   c2.set_vendor_library_model(
       vendor="Murata",
       series="GRM",
       part_name="GRM188R60J226MEA0D",
       reference_net="GND",
   )

   # ── Series inductor — Murata LQW15A series ───────────────────────────────
   l1 = cfg.components.add("L1", part_type="inductor")
   l1.set_vendor_library_model(
       vendor="Murata",
       series="LQW15A",
       part_name="LQW15AN3N9D00D",
       reference_net="GND",
       touchstone_cache_dir="/tmp/snp_cache",  # custom cache path
   )

   edb.configuration.run(cfg)
   edb.close()

The configuration can also be persisted as JSON and applied without a Python
script. The ``vendor_library_model`` key is fully round-tripped:

.. code-block:: python

   from pyedb import Edb
   from pyedb.configuration import CfgData

   # Build and save
   cfg = CfgData()
   c1 = cfg.components.add("C1", part_type="capacitor")
   c1.set_vendor_library_model(
       vendor="Murata",
       series="GRM",
       part_name="GRM155R61A104KA01D",
       reference_net="GND",
   )
   cfg.to_json("cap_model_config.json")

   # Apply from file in a separate session
   edb = Edb("ANSYS-HSD_V1.aedb", version="2026.1")
   edb.configuration.run("cap_model_config.json")
   edb.close()

.. note::

   ``vendor_library_model`` has higher priority than ``s_parameter_model`` and
   ``spice_model``.  If all three are set on the same component, only the vendor
   library assignment is applied. See the priority table in
   :doc:`configuration_api_guide` for the full ordering.

Exporting the builder as JSON for review and reuse
---------------------------------------------------

Any of the builder objects from the examples above can be serialized to a
self-contained JSON file. This is useful for code review, archiving a known-
good configuration, or sharing a setup with another team member who can apply
it without running the Python script themselves.

.. code-block:: python

   from pyedb import Edb

   edb = Edb("ANSYS-HSD_V1.aedb", version="2026.1")
   cfg = edb.configuration.create_config_builder()

   cfg.nets.add_signal_nets(["CLK", "DATA"])
   cfg.nets.add_reference_nets(["GND"])
   cfg.setups.add_hfss_setup("review_setup", adapt_type="broadband")

   # Export before applying — useful for review in version control
   cfg.to_json("review_config.json")
   cfg.to_toml("review_config.toml")

   # Inspect as a plain dict if you need to post-process the payload
   payload = cfg.to_dict()
   print(list(payload.keys()))  # ['nets', 'setups']

   # Apply from the file later (no Python script required)
   edb.configuration.run("review_config.json")
   edb.close()

See also
--------

* :doc:`file_architecture`: complete field-by-field reference for the JSON/TOML
  file format produced by ``to_json()`` / ``to_toml()``.
* :doc:`configuration_api_guide`: full API reference including all section
  builders, parameter tables, and session-aware ``get()`` helpers.
* :doc:`../autoapi/pyedb/configuration/index`: AutoAPI class reference for
  every configuration module.

