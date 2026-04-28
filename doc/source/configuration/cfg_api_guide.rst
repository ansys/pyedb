Configuration API guide and complete example
============================================

The :mod:`pyedb.configuration.cfg_api` package provides a Python-first way to
build the same configuration payload described in :doc:`file_architecture`.
Instead of manually authoring JSON, you populate an
``EdbConfigBuilder`` and then pass it directly
to ``Configuration.run`` with no
serialization step required.

.. tip::

   The easiest way to obtain a builder when you already have an open EDB session
   is ``edb.configuration.create_config_builder()``.  This keeps everything
   within the ``edb.configuration`` namespace and avoids a direct import of
   ``EdbConfigBuilder``.

Why use the configuration API?
------------------------------

The programmatic API is useful when you want to:

* build configurations from templates or scripts,
* reuse helper functions across projects,
* validate values in Python before writing the file,
* generate only the sections you need,
* pass a builder directly to ``run()`` without touching the file system, and
* round-trip between dictionary, JSON, and TOML forms.

Configuration API workflow
--------------------------

.. graphviz::

   digraph cfg_api_workflow {
       rankdir=LR;
       node [shape=box, style="rounded,filled", fillcolor="#F7F7F7", color="#4F81BD"];
       edge [color="#4F81BD"];

       create  [label="edb.configuration\n.create_config_builder()"];
       builder [label="EdbConfigBuilder\n(section builders)"];
       run     [label="edb.configuration.run(cfg)\n— or —\nload(cfg, apply_file=True)"];
       design  [label="Configured EDB design"];
       persist [label="cfg.to_json()\ncfg.to_toml()\ncfg.to_dict()", shape=note, fillcolor="#FFF8DC"];

       create  -> builder -> run -> design;
       builder -> persist [style=dashed];
   }

Two entry points
----------------

There are two equivalent ways to start a programmatic configuration:

**1. From an open EDB session (recommended)**

.. code-block:: python

   # No extra imports needed – the builder is created inside the session.
   cfg = edb.configuration.create_config_builder()
   cfg.general.anti_pads_always_on = False
   cfg.nets.add_signal_nets(["SIG1", "CLK"])
   edb.configuration.run(cfg)  # load + apply in one call

**2. Standalone (scripts, templates, CI)**

.. code-block:: python

   from pyedb.configuration.cfg_api import EdbConfigBuilder

   cfg = EdbConfigBuilder()
   cfg.general.anti_pads_always_on = False
   cfg.nets.add_signal_nets(["SIG1", "CLK"])

   # Apply to an open session later:
   edb.configuration.run(cfg)

   # Or persist to a file for review / source control:
   cfg.to_json("my_config.json")

Core objects
------------

.. list-table:: Main API objects
   :header-rows: 1
   :widths: 32 15 53

   * - Object
     - Kind
     - Role
   * - ``edb.configuration.create_config_builder()``
     - Factory method
     - Returns a fresh ``EdbConfigBuilder``
       tied to the current session namespace.
   * - ``EdbConfigBuilder``
      - Root builder
     - Owns every configuration section and serializes the final payload.
   * - ``cfg.general``
     - Section builder
     - Global library paths and design flags.
   * - ``cfg.stackup``
     - Section builder
     - Materials and layers.
   * - ``cfg.nets``
     - Section builder
     - Signal and power-ground net classification.
   * - ``cfg.components``
     - Section builder
     - Component model and package data.
   * - ``cfg.padstacks``
     - Section builder
     - Padstack definitions and instances.
   * - ``cfg.pin_groups``
     - Section builder
     - Named pin-group creation.
   * - ``cfg.terminals``
     - Section builder
     - Explicit low-level terminal objects.
   * - ``cfg.ports`` / ``cfg.sources`` / ``cfg.probes``
     - Section builders
     - Excitations and measurements.
   * - ``cfg.setups``
     - Section builder
     - HFSS and SIwave setup creation.
   * - ``cfg.boundaries``
     - Section builder
     - Open-region and extent setup.
   * - ``cfg.operations``
     - Section builder
     - Cutout and automatic HFSS-region operations.
   * - ``cfg.s_parameters`` / ``cfg.spice_models``
     - Section builders
     - Model assignment by component definition.
   * - ``cfg.package_definitions``
     - Section builder
     - Thermal package definitions.
   * - ``cfg.variables``
     - Section builder
     - Design or project variables.
   * - ``cfg.modeler``
     - Section builder
     - Geometry-driven creation and cleanup.
   * - ``TerminalInfo``
      - Helper factory
     - Creates terminal-specifier dictionaries for ports, sources, and probes.

Applying a configuration
------------------------

``run()`` is the single method to both *load* and *apply* a configuration.
You can pass any of the supported input types directly:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Input type
     - Behaviour
   * - ``EdbConfigBuilder``
     - Serialized to a dict via ``to_dict()`` then loaded and applied.
   * - ``dict``
     - Merged with the existing ``data`` store then applied.
   * - ``str`` / ``Path``
     - JSON or TOML file loaded from disk then applied.
   * - ``None`` (default)
     - Applies the previously loaded ``cfg_data`` as-is.

.. code-block:: python

   # Variant A – builder (most ergonomic)
   cfg = edb.configuration.create_config_builder()
   cfg.nets.add_signal_nets(["SIG"])
   edb.configuration.run(cfg)

   # Variant B – dictionary
   edb.configuration.run({"nets": {"signal_nets": ["SIG"]}})

   # Variant C – file path
   edb.configuration.run("my_config.json")

   # Variant D – apply previously loaded data
   edb.configuration.load("base.json")
   edb.configuration.load("overlay.json")  # merges on top
   edb.configuration.run()

Section mapping
---------------

.. list-table:: Builder attributes to serialized sections
   :header-rows: 1
   :widths: 22 28 20 30

   * - Builder attribute
     - Builder class
     - Method
     - Output section key
   * - ``cfg.general``
     - ``GeneralConfig``
     - ``to_dict()``
     - ``general``
   * - ``cfg.stackup``
     - ``StackupConfig``
     - ``to_dict()``
     - ``stackup``
   * - ``cfg.nets``
     - ``NetsConfig``
     - ``to_dict()``
     - ``nets``
   * - ``cfg.components``
     - ``ComponentsConfig``
     - ``to_list()``
     - ``components``
   * - ``cfg.padstacks``
     - ``PadstacksConfig``
     - ``to_dict()``
     - ``padstacks``
   * - ``cfg.pin_groups``
     - ``PinGroupsConfig``
     - ``to_list()``
     - ``pin_groups``
   * - ``cfg.terminals``
     - ``TerminalsConfig``
     - ``to_list()``
     - ``terminals``
   * - ``cfg.ports``
     - ``PortsConfig``
     - ``to_list()``
     - ``ports``
   * - ``cfg.sources``
     - ``SourcesConfig``
     - ``to_list()``
     - ``sources``
   * - ``cfg.probes``
     - ``ProbesConfig``
     - ``to_list()``
     - ``probes``
   * - ``cfg.setups``
     - ``SetupsConfig``
     - ``to_list()``
     - ``setups``
   * - ``cfg.boundaries``
     - ``BoundariesConfig``
     - ``to_dict()``
     - ``boundaries``
   * - ``cfg.operations``
     - ``OperationsConfig``
     - ``to_dict()``
     - ``operations``
   * - ``cfg.s_parameters``
     - ``SParameterModelsConfig``
     - ``to_list()``
     - ``s_parameters``
   * - ``cfg.spice_models``
     - ``SpiceModelsConfig``
     - ``to_list()``
     - ``spice_models``
   * - ``cfg.package_definitions``
     - ``PackageDefinitionsConfig``
     - ``to_list()``
     - ``package_definitions``
   * - ``cfg.variables``
     - ``VariablesConfig``
     - ``to_list()``
     - ``variables``
   * - ``cfg.modeler``
     - ``ModelerConfig``
     - ``to_dict()``
     - ``modeler``

TerminalInfo helpers
--------------------

For ``ports``, ``sources``, and ``probes``, use
``TerminalInfo`` factory methods instead of
writing raw terminal dictionaries by hand.

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - Factory call
     - Use when …
   * - ``TerminalInfo.pin("A1", reference_designator="U1")``
     - targeting a named pin on a component.
   * - ``TerminalInfo.net("VDD", reference_designator="U1")``
     - connecting to a net on a specific component.
   * - ``TerminalInfo.pin_group("pg_VDD")``
     - referencing a pre-defined pin group.
   * - ``TerminalInfo.padstack("via_1")``
     - targeting a named padstack instance (coax ports).
   * - ``TerminalInfo.coordinates("top", 0.001, 0.002, "SIG")``
     - placing a terminal at an exact XY coordinate on a layer.
   * - ``TerminalInfo.nearest_pin("GND", search_radius="5mm")``
     - auto-resolving a reference terminal from a ground net.

.. code-block:: python

   from pyedb.configuration.cfg_api import TerminalInfo

   TerminalInfo.pin("A1", reference_designator="U1")
   TerminalInfo.net("VDD", reference_designator="U1")
   TerminalInfo.pin_group("pg_VDD")
   TerminalInfo.padstack("via_1")
   TerminalInfo.coordinates("top", 0.001, 0.002, "SIG")
   TerminalInfo.nearest_pin("GND", search_radius="5mm")

Complete example
----------------

The following example uses ``edb.configuration.create_config_builder()`` to
obtain a builder from an open session, populates all major sections, then
applies the configuration with a single ``run()`` call.

.. code-block:: python

   from pyedb import Edb
   from pyedb.configuration.cfg_api import TerminalInfo

   edb = Edb("my_design.aedb")

   # ----------------------------------------------------------------
   # Obtain a builder from the active session
   # ----------------------------------------------------------------
   cfg = edb.configuration.create_config_builder()

   # ----------------------------------------------------------------
   # General design options
   # ----------------------------------------------------------------
   cfg.general.spice_model_library = "/models/spice"
   cfg.general.s_parameter_library = "/models/snp"
   cfg.general.anti_pads_always_on = False
   cfg.general.suppress_pads = True

   # ----------------------------------------------------------------
   # Stackup
   # ----------------------------------------------------------------
   cfg.stackup.add_material("copper", conductivity=5.8e7)
   cfg.stackup.add_material("fr4", permittivity=4.4, dielectric_loss_tangent=0.02)
   cfg.stackup.add_signal_layer(
       "top", material="copper", fill_material="fr4", thickness="35um"
   )
   cfg.stackup.add_dielectric_layer("diel1", material="fr4", thickness="100um")
   cfg.stackup.add_signal_layer(
       "bot", material="copper", fill_material="fr4", thickness="35um"
   )

   # ----------------------------------------------------------------
   # Nets
   # ----------------------------------------------------------------
   cfg.nets.add_signal_nets(["DDR4_DQ0", "DDR4_DQ1", "CLK"])
   cfg.nets.add_power_ground_nets(["VDD", "VCC", "GND"])

   # ----------------------------------------------------------------
   # Components
   # ----------------------------------------------------------------
   r1 = cfg.components.add("R1", part_type="resistor", enabled=True)
   r1.add_pin_pair_rlc("1", "2", resistance="100ohm", resistance_enabled=True)

   c1 = cfg.components.add("C1", part_type="capacitor")
   c1.add_pin_pair_rlc("1", "2", capacitance="100nF", capacitance_enabled=True)

   u1 = cfg.components.add("U1", part_type="ic")
   u1.set_ic_die_properties("flip_chip", orientation="chip_down")
   u1.set_solder_ball_properties("cylinder", "150um", "100um")
   u1.set_port_properties(reference_height="50um")

   # ----------------------------------------------------------------
   # Padstacks
   # ----------------------------------------------------------------
   cfg.padstacks.add_definition(
       "via_0.2", material="copper", hole_plating_thickness="25um"
   )
   via = cfg.padstacks.add_instance(name="v1", net_name="GND", layer_range=["top", "bot"])
   via.set_backdrill("L3", "0.25mm", drill_from_bottom=True)

   # ----------------------------------------------------------------
   # Pin groups
   # ----------------------------------------------------------------
   cfg.pin_groups.add("pg_VDD", "U1", net="VDD")
   cfg.pin_groups.add("pg_GND", "U1", pins=["A1", "A2", "B1"])

   # ----------------------------------------------------------------
   # Explicit low-level terminals (optional; most users use ports/sources)
   # ----------------------------------------------------------------
   cfg.terminals.add_pin_group_terminal("t_vdd", "pg_VDD", 50, "port")
   cfg.terminals.add_pin_group_terminal(
       "t_gnd", "pg_GND", 50, "port", reference_terminal="t_vdd"
   )
   cfg.terminals.add_bundle_terminal("bundle_demo", ["t_vdd", "t_gnd"])

   # ----------------------------------------------------------------
   # Ports
   # ----------------------------------------------------------------
   cfg.ports.add_circuit_port(
       "port_U1",
       positive_terminal=TerminalInfo.pin_group("pg_VDD"),
       negative_terminal=TerminalInfo.pin_group("pg_GND"),
       impedance=50,
   )
   cfg.ports.add_wave_port(
       "wport1",
       primitive_name="trace1",
       point_on_edge=[0.001, 0.002],
       horizontal_extent_factor=6,
   )
   cfg.ports.add_coax_port("coax1", positive_terminal=TerminalInfo.padstack("v1"))

   # ----------------------------------------------------------------
   # Sources and probes
   # ----------------------------------------------------------------
   cfg.sources.add_current_source(
       "isrc1",
       positive_terminal=TerminalInfo.pin_group("pg_VDD"),
       negative_terminal=TerminalInfo.pin_group("pg_GND"),
       magnitude=0.5,
   )
   cfg.sources.add_voltage_source(
       "vsrc1",
       positive_terminal=TerminalInfo.net("VDD"),
       negative_terminal=TerminalInfo.net("GND"),
       magnitude=1.0,
   )
   cfg.probes.add(
       "probe1",
       positive_terminal=TerminalInfo.net("DDR4_DQ0"),
       negative_terminal=TerminalInfo.net("GND"),
   )

   # ----------------------------------------------------------------
   # Simulation setups
   # ----------------------------------------------------------------
   hfss = cfg.setups.add_hfss_setup("hfss_bb")
   hfss.set_broadband_adaptive("1GHz", "20GHz", max_passes=20, max_delta=0.02)
   hfss.set_auto_mesh_operation(enabled=True)
   hfss.add_length_mesh_operation("mesh1", {"DDR4_DQ0": ["top"]}, max_length="0.5mm")
   sweep = hfss.add_frequency_sweep("sweep1")
   sweep.add_linear_count_frequencies("1GHz", "20GHz", 100)
   sweep.add_single_frequency("5GHz")

   siwave_ac = cfg.setups.add_siwave_ac_setup(
       "siw_ac", si_slider_position=2, pi_slider_position=1
   )
   siwave_ac.add_frequency_sweep("siw_sw1").add_log_count_frequencies("1kHz", "1GHz", 100)

   cfg.setups.add_siwave_dc_setup(
       "siw_dc", dc_slider_position=1, export_dc_thermal_data=True
   )

   # ----------------------------------------------------------------
   # Boundaries
   # ----------------------------------------------------------------
   cfg.boundaries.set_radiation_boundary()
   cfg.boundaries.set_air_box_extents(0.15, truncate_at_ground=True)
   cfg.boundaries.set_dielectric_extent(
       "BoundingBox", expansion_size=0.001, honor_user_dielectric=True
   )

   # ----------------------------------------------------------------
   # Operations (cutout)
   # ----------------------------------------------------------------
   cfg.operations.add_cutout(
       signal_nets=["DDR4_DQ0", "CLK"],
       reference_nets=["GND"],
       extent_type="ConvexHull",
       expansion_size=0.002,
       auto_identify_nets_enabled=True,
   )
   cfg.operations.generate_auto_hfss_regions = True

   # ----------------------------------------------------------------
   # Model assignments
   # ----------------------------------------------------------------
   cfg.s_parameters.add(
       "cap_model",
       component_definition="CAP_100nF",
       file_path="/snp/cap.s2p",
       reference_net="GND",
   )
   cfg.spice_models.add(
       "ic_spice",
       component_definition="IC_U1",
       file_path="/spice/ic.sp",
       sub_circuit_name="IC_TOP",
   )

   # ----------------------------------------------------------------
   # Thermal package definitions
   # ----------------------------------------------------------------
   pkg = cfg.package_definitions.add(
       "PKG_U1",
       component_definition="IC_U1",
       apply_to_all=True,
       maximum_power="5W",
       theta_jb="10C/W",
       theta_jc="5C/W",
       height="1mm",
   )
   pkg.set_heatsink(
       fin_base_height="0.5mm",
       fin_height="3mm",
       fin_orientation="x_oriented",
       fin_spacing="1mm",
       fin_thickness="0.2mm",
   )

   # ----------------------------------------------------------------
   # Variables
   # ----------------------------------------------------------------
   cfg.variables.add("trace_width", "0.15mm", "Default trace width")
   cfg.variables.add("$project_temp", "25cel")

   # ----------------------------------------------------------------
   # Modeler geometry
   # ----------------------------------------------------------------
   cfg.modeler.add_trace(
       "trace1", "top", "0.15mm", net_name="DDR4_DQ0", path=[[0.0, 0.0], [0.01, 0.0]]
   )
   cfg.modeler.add_rectangular_plane(
       "bot",
       "gnd_plane",
       "GND",
       lower_left_point=[-0.05, -0.05],
       upper_right_point=[0.05, 0.05],
   )
   cfg.modeler.delete_primitives_by_layer(["old_layer"])

   # ----------------------------------------------------------------
   # Apply everything to the open EDB design in one call
   # ----------------------------------------------------------------
   edb.configuration.run(cfg)

Persisting the configuration
-----------------------------

If you want to save the configuration for review, archiving, or reuse in
another project, serialize the builder before (or instead of) calling ``run()``.

.. code-block:: python

   # Inspect as a plain dict
   payload = cfg.to_dict()

   # Write to disk
   cfg.to_json("my_project_config.json")
   cfg.to_toml("my_project_config.toml")

   # Apply later via file path
   edb.configuration.run("my_project_config.json")

Round-trip helpers
------------------

The root builder supports round-tripping from existing dictionaries, JSON, or
TOML files. This is useful for loading a template, tweaking specific values, and
re-exporting.

.. code-block:: python

   from pyedb.configuration.cfg_api import EdbConfigBuilder

   # Load from a file, modify, and save back
   cfg = EdbConfigBuilder.from_json("base_config.json")
   cfg.general.suppress_pads = True
   cfg.stackup.add_material("silver", conductivity=6.3e7)
   cfg.to_json("modified_config.json")

   # Load from a dict
   cfg2 = EdbConfigBuilder.from_dict({"nets": {"signal_nets": ["CLK"]}})
   cfg2.to_toml("nets_only.toml")

Practical recommendations
-------------------------

* **Use** ``edb.configuration.create_config_builder()`` when working inside an
  active EDB session. It avoids the extra import and keeps calling conventions
  consistent.
* **Call** ``edb.configuration.run(cfg)`` to load and apply in a single
  statement. Pass ``None`` (the default) to re-apply previously loaded data.
* **Prefer** ``TerminalInfo`` factory methods
  over hand-written terminal dictionaries.
* **Build only the sections you need**: empty sections are omitted by
  ``EdbConfigBuilder.to_dict()`` so the
  serialized payload stays minimal.
* **Persist to JSON / TOML** when you want a reviewed, version-controlled
  artifact that can be applied without a Python script.
* **Store reusable snippets** as plain Python functions that accept and return
  an ``EdbConfigBuilder``. Composing
  builders is straightforward.

Related reference
-----------------

For the file-oriented view of the same data model, including field-by-field
section descriptions, see :doc:`file_architecture`.
