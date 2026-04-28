Configuration API guide and complete example
============================================

The :mod:`pyedb.configuration.cfg_api` package provides a Python-first way to
build the same configuration payload described in
:doc:`file_architecture`. Instead of manually authoring JSON, you populate an
:class:`pyedb.configuration.cfg_api.EdbConfigBuilder`, serialize it with
``to_dict()``, ``to_json()``, or ``to_toml()``, and optionally apply it through
``edb.configuration.load(...)``.

Why use the configuration API?
------------------------------

The programmatic API is useful when you want to:

* build configurations from templates or scripts,
* reuse helper functions across projects,
* validate values in Python before writing the file,
* generate only the sections you need, and
* round-trip between dictionary, JSON, and TOML forms.

Configuration API workflow
--------------------------

.. graphviz::

   digraph cfg_api_workflow {
       rankdir=LR;
       node [shape=box, style="rounded,filled", fillcolor="#F7F7F7", color="#4F81BD"];

       builder [label="EdbConfigBuilder"];
       sections [label="Section builders\n(general, stackup, ports, ...)"];
       serialize [label="to_dict() / to_json() / to_toml()"];
       load [label="edb.configuration.load(...)"];
       design [label="Configured EDB design"];

       builder -> sections -> serialize -> load -> design;
   }

Core objects
------------

.. list-table:: Main API objects
   :header-rows: 1
   :widths: 30 28 42

   * - Object
     - Kind
     - Role
   * - :class:`pyedb.configuration.cfg_api.EdbConfigBuilder`
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
   * - :class:`pyedb.configuration.cfg_api.TerminalInfo`
     - Helper factory
     - Creates terminal-specifier dictionaries for ports, sources, and probes.

Section mapping
---------------

.. list-table:: Builder attributes to serialized sections
   :header-rows: 1
   :widths: 22 28 20 30

   * - Builder attribute
     - Builder class
     - Serializer
     - Output section
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
:class:`pyedb.configuration.cfg_api.TerminalInfo` instead of hand-authoring raw
terminal dictionaries.

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

The following example creates a broadly populated configuration object that
covers the major sections of the API and then exports it.

.. code-block:: python

   from pyedb.configuration.cfg_api import EdbConfigBuilder, TerminalInfo


   def build_complete_config() -> EdbConfigBuilder:
       cfg = EdbConfigBuilder()

       # ------------------------------------------------------------------
       # General design options
       # ------------------------------------------------------------------
       cfg.general.spice_model_library = "/models/spice"
       cfg.general.s_parameter_library = "/models/snp"
       cfg.general.anti_pads_always_on = False
       cfg.general.suppress_pads = True

       # ------------------------------------------------------------------
       # Stackup
       # ------------------------------------------------------------------
       cfg.stackup.add_material("copper", conductivity=5.8e7)
       cfg.stackup.add_material(
           "fr4",
           permittivity=4.4,
           dielectric_loss_tangent=0.02,
       )
       cfg.stackup.add_signal_layer(
           "top",
           material="copper",
           fill_material="fr4",
           thickness="35um",
       )
       cfg.stackup.add_dielectric_layer("diel1", material="fr4", thickness="100um")
       cfg.stackup.add_signal_layer(
           "bot",
           material="copper",
           fill_material="fr4",
           thickness="35um",
       )

       # ------------------------------------------------------------------
       # Nets
       # ------------------------------------------------------------------
       cfg.nets.add_signal_nets(["DDR4_DQ0", "DDR4_DQ1", "CLK"])
       cfg.nets.add_power_ground_nets(["VDD", "VCC", "GND"])

       # ------------------------------------------------------------------
       # Components
       # ------------------------------------------------------------------
       r1 = cfg.components.add("R1", part_type="resistor", enabled=True)
       r1.add_pin_pair_rlc("1", "2", resistance="100ohm", resistance_enabled=True)

       c1 = cfg.components.add("C1", part_type="capacitor")
       c1.add_pin_pair_rlc("1", "2", capacitance="100nF", capacitance_enabled=True)

       u1 = cfg.components.add("U1", part_type="ic")
       u1.set_ic_die_properties("flip_chip", orientation="chip_down")
       u1.set_solder_ball_properties("cylinder", "150um", "100um")
       u1.set_port_properties(reference_height="50um")

       # ------------------------------------------------------------------
       # Padstacks
       # ------------------------------------------------------------------
       cfg.padstacks.add_definition(
           "via_0.2",
           material="copper",
           hole_plating_thickness="25um",
       )
       via = cfg.padstacks.add_instance(
           name="v1",
           net_name="GND",
           layer_range=["top", "bot"],
       )
       via.set_backdrill("L3", "0.25mm", drill_from_bottom=True)

       # ------------------------------------------------------------------
       # Pin groups
       # ------------------------------------------------------------------
       cfg.pin_groups.add("pg_VDD", "U1", net="VDD")
       cfg.pin_groups.add("pg_GND", "U1", pins=["A1", "A2", "B1"])

       # ------------------------------------------------------------------
       # Explicit low-level terminals (optional)
       # ------------------------------------------------------------------
       cfg.terminals.add_pin_group_terminal("t_vdd", "pg_VDD", 50, "port")
       cfg.terminals.add_pin_group_terminal(
           "t_gnd",
           "pg_GND",
           50,
           "port",
           reference_terminal="t_vdd",
       )
       cfg.terminals.add_bundle_terminal("bundle_demo", ["t_vdd", "t_gnd"])

       # ------------------------------------------------------------------
       # Ports
       # ------------------------------------------------------------------
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
       cfg.ports.add_diff_wave_port(
           "diff1",
           positive_terminal={
               "primitive_name": "tp",
               "point_on_edge": [0.0, 0.0],
           },
           negative_terminal={
               "primitive_name": "tn",
               "point_on_edge": [0.0, 1e-4],
           },
       )

       # ------------------------------------------------------------------
       # Sources and probes
       # ------------------------------------------------------------------
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

       # ------------------------------------------------------------------
       # Simulation setups
       # ------------------------------------------------------------------
       hfss = cfg.setups.add_hfss_setup("hfss_bb")
       hfss.set_broadband_adaptive("1GHz", "20GHz", max_passes=20, max_delta=0.02)
       hfss.set_auto_mesh_operation(enabled=True)
       hfss.add_length_mesh_operation(
           "mesh1",
           {"DDR4_DQ0": ["top"]},
           max_length="0.5mm",
       )
       hfss_sweep = hfss.add_frequency_sweep("sweep1")
       hfss_sweep.add_linear_count_frequencies("1GHz", "20GHz", 100)
       hfss_sweep.add_single_frequency("5GHz")

       hfss_single = cfg.setups.add_hfss_setup("hfss_single")
       hfss_single.set_single_frequency_adaptive("5GHz", max_passes=15)

       hfss_multi = cfg.setups.add_hfss_setup("hfss_multi")
       hfss_multi.add_multi_frequency_adaptive("2GHz")
       hfss_multi.add_multi_frequency_adaptive("10GHz")

       siwave_ac = cfg.setups.add_siwave_ac_setup(
           "siw_ac",
           si_slider_position=2,
           pi_slider_position=1,
       )
       siwave_sweep = siwave_ac.add_frequency_sweep("siw_sw1")
       siwave_sweep.add_log_count_frequencies("1kHz", "1GHz", 100)

       cfg.setups.add_siwave_dc_setup(
           "siw_dc",
           dc_slider_position=1,
           export_dc_thermal_data=True,
       )

       # ------------------------------------------------------------------
       # Boundaries
       # ------------------------------------------------------------------
       cfg.boundaries.set_radiation_boundary()
       cfg.boundaries.set_air_box_extents(0.15, truncate_at_ground=True)
       cfg.boundaries.set_dielectric_extent(
           "BoundingBox",
           expansion_size=0.001,
           honor_user_dielectric=True,
       )

       # ------------------------------------------------------------------
       # Operations
       # ------------------------------------------------------------------
       cfg.operations.add_cutout(
           signal_nets=["DDR4_DQ0", "CLK"],
           reference_nets=["GND"],
           extent_type="ConvexHull",
           expansion_size=0.002,
           auto_identify_nets_enabled=True,
       )
       cfg.operations.generate_auto_hfss_regions = True

       # ------------------------------------------------------------------
       # Model assignments
       # ------------------------------------------------------------------
       cfg.s_parameters.add(
           "cap_model",
           component_definition="CAP_100nF",
           file_path="/snp/cap.s2p",
           reference_net="GND",
       )
       cfg.s_parameters.add(
           "res_model",
           component_definition="RES_100OHM",
           file_path="/snp/res.s2p",
           apply_to_all=False,
           components=["R1"],
           reference_net="GND",
       )
       cfg.spice_models.add(
           "ic_spice",
           component_definition="IC_U1",
           file_path="/spice/ic.sp",
           sub_circuit_name="IC_TOP",
       )

       # ------------------------------------------------------------------
       # Thermal package definitions
       # ------------------------------------------------------------------
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

       # ------------------------------------------------------------------
       # Variables
       # ------------------------------------------------------------------
       cfg.variables.add("trace_width", "0.15mm", "Default trace width")
       cfg.variables.add("via_diameter", 0.2)
       cfg.variables.add("$project_temp", "25cel")

       # ------------------------------------------------------------------
       # Modeler geometry
       # ------------------------------------------------------------------
       cfg.modeler.add_trace(
           "trace1",
           "top",
           "0.15mm",
           net_name="DDR4_DQ0",
           path=[[0.0, 0.0], [0.01, 0.0]],
       )
       cfg.modeler.add_rectangular_plane(
           "bot",
           "gnd_plane",
           "GND",
           lower_left_point=[-0.05, -0.05],
           upper_right_point=[0.05, 0.05],
       )
       cfg.modeler.add_circular_plane(
           "top",
           "via_plane",
           "VDD",
           radius="0.5mm",
           position=[0.0, 0.0],
       )
       cfg.modeler.add_polygon_plane(
           "bot",
           "poly1",
           "VCC",
           points=[[0.0, 0.0], [0.01, 0.0], [0.01, 0.01], [0.0, 0.01]],
       )
       cfg.modeler.delete_primitives_by_layer(["old_layer"])
       cfg.modeler.delete_primitives_by_net(["old_net"])

       return cfg


   cfg = build_complete_config()

   # Plain Python dictionary
   config_dict = cfg.to_dict()

   # Persist to files
   cfg.to_json("complete_config.json")
   cfg.to_toml("complete_config.toml")

Serializing and applying
------------------------

Use the builder when you want to generate a payload, then apply it through the
runtime configuration interface.

.. code-block:: python

   from pyedb import Edb

   cfg = build_complete_config()

   # Serialize only
   payload = cfg.to_dict()

   # Or write a file
   cfg.to_json("my_project_config.json")

   # Apply to an opened EDB design
   app = Edb()
   app.configuration.load(payload, apply_file=True)

Round-trip helpers
------------------

The root builder also supports round-tripping from existing dictionaries,
JSON, or TOML files.

.. code-block:: python

   from pyedb.configuration.cfg_api import EdbConfigBuilder

   cfg = EdbConfigBuilder.from_json("my_project_config.json")
   data = cfg.to_dict()
   cfg2 = EdbConfigBuilder.from_dict(data)
   cfg2.to_toml("my_project_config.toml")

Practical recommendations
-------------------------

* Prefer :class:`pyedb.configuration.cfg_api.TerminalInfo` for terminal
  specifiers instead of writing raw dictionaries by hand.
* Build only the sections you need; empty sections are omitted by
  :meth:`pyedb.configuration.cfg_api.EdbConfigBuilder.to_dict`.
* Use the section builders for readability and consistent key names.
* Store reusable configuration snippets in Python functions that return an
  :class:`pyedb.configuration.cfg_api.EdbConfigBuilder`.
* Use JSON or TOML export when you want a reviewed artifact checked into source
  control.

Related reference
-----------------

For the file-oriented view of the same data model, including field-by-field
section descriptions, see :doc:`file_architecture`.

