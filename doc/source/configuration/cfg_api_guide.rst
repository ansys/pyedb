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
   * - ``EdbConfigBuilder`` builder
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
   * - ``TerminalInfo`` helper
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
   # ----- HFSS setup -----
   hfss = cfg.setups.add_hfss_setup(
       "hfss_bb",
       adapt_type="broadband",          # "single" | "broadband" | "multi_frequencies"
   )

   # Adaptive refinement – only one of these three is active at a time:
   hfss.set_broadband_adaptive(
       low_freq="1GHz",
       high_freq="20GHz",
       max_passes=20,
       max_delta=0.02,
   )
   # hfss.set_single_frequency_adaptive(freq="5GHz", max_passes=20, max_delta=0.02)
   # hfss.add_multi_frequency_adaptive("5GHz", max_passes=20, max_delta=0.02)
   # hfss.add_multi_frequency_adaptive("10GHz")

   # Automatic mesh seeding
   hfss.set_auto_mesh_operation(
       enabled=True,
       trace_ratio_seeding=3.0,
       signal_via_side_number=12,
   )

   # Length-based mesh operation
   hfss.add_length_mesh_operation(
       name="mesh1",
       nets_layers_list={"DDR4_DQ0": ["top"]},
       max_length="0.5mm",
       max_elements=1000,
       restrict_length=True,
       refine_inside=False,
   )

   # Frequency sweep (method-chaining supported)
   sweep = hfss.add_frequency_sweep(
       "sweep1",
       sweep_type="interpolation",      # "interpolation" | "discrete"
       use_q3d_for_dc=False,
       compute_dc_point=False,
       enforce_causality=False,
       enforce_passivity=True,
       adv_dc_extrapolation=False,
   )
   sweep.add_linear_count_frequencies("1GHz", "20GHz", 100)
   sweep.add_single_frequency("5GHz")

   # ----- SIwave AC setup -----
   siwave_ac = cfg.setups.add_siwave_ac_setup(
       "siw_ac",
       si_slider_position=2,            # 0=Speed | 1=Balanced | 2=Accuracy
       pi_slider_position=1,
       use_si_settings=True,
   )
   siwave_ac.add_frequency_sweep(
       "siw_sw1",
       sweep_type="interpolation",
       compute_dc_point=False,
       enforce_passivity=True,
   ).add_log_count_frequencies("1kHz", "1GHz", 100)

   # ----- SIwave DC setup -----
   cfg.setups.add_siwave_dc_setup(
       "siw_dc",
       dc_slider_position=1,            # 0=Speed | 1=Balanced | 2=Accuracy
       export_dc_thermal_data=True,
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

Setups
------

Three setup types are available via ``cfg.setups``.  Each ``add_*`` method
returns a typed builder so that IDEs provide full autocomplete.

**HFSS setup** — ``cfg.setups.add_hfss_setup(name, adapt_type="single")``

.. list-table::
   :header-rows: 1
   :widths: 35 15 50

   * - Method / parameter
     - Default
     - Description
   * - ``add_hfss_setup(name, adapt_type)``
     - –
     - Create setup. ``adapt_type``: ``"single"`` \| ``"broadband"`` \|
       ``"multi_frequencies"``.
   * - ``.set_single_frequency_adaptive(freq, max_passes, max_delta)``
     - ``"5GHz"``, ``20``, ``0.02``
     - Refine at one adaptive frequency.
   * - ``.set_broadband_adaptive(low_freq, high_freq, max_passes, max_delta)``
     - ``"1GHz"``, ``"10GHz"``, ``20``, ``0.02``
     - Refine across a low/high frequency pair.
   * - ``.add_multi_frequency_adaptive(freq, max_passes, max_delta)``
     - –, ``20``, ``0.02``
     - Append one adaptive point (call multiple times).
   * - ``.set_auto_mesh_operation(enabled, trace_ratio_seeding, signal_via_side_number)``
     - ``True``, ``3.0``, ``12``
     - Configure automatic mesh seeding.
   * - ``.add_length_mesh_operation(name, nets_layers_list, max_length, max_elements, restrict_length, refine_inside)``
     - –, –, ``"1mm"``, ``1000``, ``True``, ``False``
     - Append a length-based mesh operation.
   * - ``.add_frequency_sweep(name, sweep_type, …)``
     - –, ``"interpolation"``
     - Add a sweep; returns :class:`FrequencySweepConfig`.

**SIwave AC setup** — ``cfg.setups.add_siwave_ac_setup(name, …)``

.. list-table::
   :header-rows: 1
   :widths: 35 15 50

   * - Parameter
     - Default
     - Description
   * - ``si_slider_position``
     - ``1``
     - SI accuracy slider: 0 = Speed, 1 = Balanced, 2 = Accuracy.
   * - ``pi_slider_position``
     - ``1``
     - PI accuracy slider (same scale).
   * - ``use_si_settings``
     - ``True``
     - ``True`` = SI slider active; ``False`` = PI slider active.
   * - ``.add_frequency_sweep(name, sweep_type, …)``
     - –, ``"interpolation"``
     - Add a sweep; returns :class:`FrequencySweepConfig`.

**SIwave DC setup** — ``cfg.setups.add_siwave_dc_setup(name, …)``

.. list-table::
   :header-rows: 1
   :widths: 35 15 50

   * - Parameter
     - Default
     - Description
   * - ``dc_slider_position``
     - ``1``
     - DC accuracy slider: 0 = Speed, 1 = Balanced, 2 = Accuracy.
   * - ``export_dc_thermal_data``
     - ``False``
     - Export DC thermal (loss) data after the solve.

**Frequency sweep** — returned by ``add_frequency_sweep(…)``

All sweep types share the same :class:`FrequencySweepConfig` builder.

.. list-table::
   :header-rows: 1
   :widths: 35 15 50

   * - Parameter / method
     - Default
     - Description
   * - ``sweep_type``
     - ``"interpolation"``
     - ``"interpolation"`` or ``"discrete"``.
   * - ``use_q3d_for_dc``
     - ``False``
     - Use Q3D solver for DC point (HFSS only).
   * - ``compute_dc_point``
     - ``False``
     - Enable AC/DC merge.
   * - ``enforce_causality``
     - ``False``
     - Enforce causality.
   * - ``enforce_passivity``
     - ``True``
     - Enforce passivity.
   * - ``adv_dc_extrapolation``
     - ``False``
     - Enable advanced DC extrapolation.
   * - ``use_hfss_solver_regions``
     - ``False``
     - Solve using HFSS solver regions.
   * - ``hfss_solver_region_setup_name``
     - ``"<default>"``
     - HFSS solver-region setup name.
   * - ``hfss_solver_region_sweep_name``
     - ``"<default>"``
     - HFSS solver-region sweep name.
   * - ``.add_linear_count_frequencies(start, stop, count)``
     - –
     - Linear distribution with explicit point count.
   * - ``.add_log_count_frequencies(start, stop, count)``
     - –
     - Logarithmic distribution with explicit point count.
   * - ``.add_linear_scale_frequencies(start, stop, step)``
     - –
     - Linear distribution with explicit step size.
   * - ``.add_log_scale_frequencies(start, stop, step)``
     - –
     - Logarithmic distribution with explicit step.
   * - ``.add_single_frequency(freq)``
     - –
     - Single discrete frequency point.

Stackup
-------

**Materials** — ``cfg.stackup.add_material(name, …)``

.. list-table::
   :header-rows: 1
   :widths: 35 15 50

   * - Parameter
     - Default
     - Description
   * - ``conductivity``
     - –
     - Electrical conductivity in S/m (e.g. ``5.8e7`` for copper).
   * - ``permittivity``
     - –
     - Relative permittivity.
   * - ``dielectric_loss_tangent``
     - –
     - Dielectric loss tangent.
   * - ``magnetic_loss_tangent``
     - –
     - Magnetic loss tangent.
   * - ``mass_density``
     - –
     - Mass density in kg/m³.
   * - ``permeability``
     - –
     - Relative permeability.
   * - ``poisson_ratio``
     - –
     - Poisson's ratio.
   * - ``specific_heat``
     - –
     - Specific heat in J/(kg·K).
   * - ``thermal_conductivity``
     - –
     - Thermal conductivity in W/(m·K).
   * - ``youngs_modulus``
     - –
     - Young's modulus in Pa.
   * - ``thermal_expansion_coefficient``
     - –
     - CTE in 1/K.
   * - ``dc_conductivity``
     - –
     - DC conductivity override.
   * - ``dc_permittivity``
     - –
     - DC permittivity override.
   * - ``dielectric_model_frequency``
     - –
     - Reference frequency for frequency-dependent model.
   * - ``loss_tangent_at_frequency``
     - –
     - Loss tangent at *dielectric_model_frequency*.
   * - ``permittivity_at_frequency``
     - –
     - Permittivity at *dielectric_model_frequency*.

**Layers** — ``cfg.stackup.add_signal_layer(name, …)`` / ``add_dielectric_layer(name, …)``

.. list-table::
   :header-rows: 1
   :widths: 35 15 50

   * - Parameter / method
     - Default
     - Description
   * - ``material``
     - ``"copper"`` / ``"FR4_epoxy"``
     - Conductor or dielectric material name.
   * - ``fill_material``
     - ``"FR4_epoxy"``
     - Fill material for signal layers.
   * - ``thickness``
     - ``"35um"`` / ``"100um"``
     - Layer thickness.
   * - ``.set_huray_roughness(nodule_radius, surface_ratio, enabled, top, bottom, side)``
     - –, –, ``True``, ``True``, ``True``, ``True``
     - Huray roughness model.
   * - ``.set_groisse_roughness(roughness_value, enabled, top, bottom, side)``
     - –, ``True``, ``True``, ``True``, ``True``
     - Groisse roughness model.
   * - ``.set_etching(factor, etch_power_ground_nets, enabled)``
     - ``0.5``, ``False``, ``True``
     - Trapezoidal etching model.

Padstacks
---------

**Definitions** — ``cfg.padstacks.add_definition(name, …)``

.. list-table::
   :header-rows: 1
   :widths: 35 15 50

   * - Parameter
     - Default
     - Description
   * - ``hole_plating_thickness``
     - –
     - Plating thickness, e.g. ``"25um"``.
   * - ``material``
     - –
     - Hole conductor material name.
   * - ``hole_range``
     - –
     - Layer range the hole spans.
   * - ``pad_parameters``
     - –
     - Raw pad-parameter dictionary.
   * - ``hole_parameters``
     - –
     - Raw hole-parameter dictionary.
   * - ``solder_ball_parameters``
     - –
     - Raw solder-ball parameter dictionary.

**Instances** — ``cfg.padstacks.add_instance(…)``

.. list-table::
   :header-rows: 1
   :widths: 35 15 50

   * - Parameter / method
     - Default
     - Description
   * - ``name``
     - –
     - Instance AEDT name.
   * - ``net_name``
     - –
     - Net name.
   * - ``definition``
     - –
     - Padstack definition name.
   * - ``layer_range``
     - –
     - ``[start_layer, stop_layer]``.
   * - ``position``
     - –
     - ``[x, y]`` in metres.
   * - ``rotation``
     - –
     - Rotation in degrees.
   * - ``is_pin``
     - ``False``
     - Whether the instance is a component pin.
   * - ``hole_override_enabled``
     - –
     - Enable hole-size override.
   * - ``hole_override_diameter``
     - –
     - Override drill diameter.
   * - ``solder_ball_layer``
     - –
     - Layer on which the solder ball sits.
   * - ``.set_backdrill(drill_to_layer, diameter, stub_length, drill_from_bottom)``
     - –, –, ``None``, ``True``
     - Configure backdrill.

Components
----------

**Adding** — ``cfg.components.add(reference_designator, …)``

.. list-table::
   :header-rows: 1
   :widths: 35 15 50

   * - Parameter
     - Default
     - Description
   * - ``part_type``
     - –
     - ``"resistor"``, ``"capacitor"``, ``"inductor"``, ``"ic"``, ``"io"``, ``"other"``.
   * - ``enabled``
     - –
     - Whether the component is enabled.
   * - ``definition``
     - –
     - Component part / definition name.
   * - ``placement_layer``
     - –
     - Layer on which the component is placed.

**Model helpers** on the returned :class:`ComponentConfig`:

.. list-table::
   :header-rows: 1
   :widths: 50 50

   * - Method
     - Description
   * - ``.add_pin_pair_rlc(first_pin, second_pin, resistance, inductance, capacitance, is_parallel, *_enabled)``
     - Append a series/parallel RLC model between two pins.
   * - ``.set_s_parameter_model(model_name, model_path, reference_net)``
     - Assign a Touchstone model.
   * - ``.set_spice_model(model_name, model_path, sub_circuit, terminal_pairs)``
     - Assign a SPICE subcircuit model.
   * - ``.set_netlist_model(netlist)``
     - Assign a raw netlist.
   * - ``.set_ic_die_properties(die_type, orientation, height)``
     - Set die type (``"flip_chip"``, ``"wire_bond"``, ``"no_die"``).
   * - ``.set_solder_ball_properties(shape, diameter, height, material, mid_diameter)``
     - Configure solder-ball geometry.
   * - ``.set_port_properties(reference_height, reference_size_auto, reference_size_x, reference_size_y)``
     - Configure port reference geometry.

Pin groups
----------

``cfg.pin_groups.add(name, reference_designator, pins=None, net=None)``

Provide either *pins* (explicit list) **or** *net* (all pins on that net).

Terminals (low-level)
---------------------

Most users use ``ports`` / ``sources`` instead.  Use the terminal builders
only when fine-grained control over individual terminal objects is required.

.. list-table::
   :header-rows: 1
   :widths: 50 50

   * - Method
     - Type created
   * - ``.add_padstack_instance_terminal(name, padstack_instance, impedance, boundary_type, hfss_type, …)``
     - :class:`PadstackInstanceTerminal`
   * - ``.add_pin_group_terminal(name, pin_group, impedance, boundary_type, …)``
     - :class:`PinGroupTerminal`
   * - ``.add_point_terminal(name, x, y, layer, net, impedance, boundary_type, …)``
     - :class:`PointTerminal`
   * - ``.add_edge_terminal(name, primitive, point_on_edge_x, point_on_edge_y, impedance, boundary_type, …)``
     - :class:`EdgeTerminal`
   * - ``.add_bundle_terminal(name, terminals)``
     - :class:`BundleTerminal`

Ports
-----

.. list-table::
   :header-rows: 1
   :widths: 50 50

   * - Method
     - Description
   * - ``.add_circuit_port(name, positive_terminal, negative_terminal, reference_designator, impedance, distributed)``
     - Lumped circuit port.
   * - ``.add_coax_port(name, positive_terminal, reference_designator, impedance)``
     - Coaxial (via) port.
   * - ``.add_wave_port(name, primitive_name, point_on_edge, horizontal_extent_factor, vertical_extent_factor, pec_launch_width)``
     - Wave port on a trace edge.
   * - ``.add_gap_port(name, primitive_name, point_on_edge, …)``
     - Gap port on a trace edge.
   * - ``.add_diff_wave_port(name, positive_terminal, negative_terminal, …)``
     - Differential wave port.

Sources
-------

.. list-table::
   :header-rows: 1
   :widths: 50 50

   * - Method
     - Description
   * - ``.add_current_source(name, positive_terminal, negative_terminal, magnitude, impedance, …)``
     - Current source (default magnitude ``0.001`` A).
   * - ``.add_voltage_source(name, positive_terminal, negative_terminal, magnitude, impedance, …)``
     - Voltage source (default magnitude ``1.0`` V).

Boundaries
----------

.. list-table::
   :header-rows: 1
   :widths: 50 50

   * - Method
     - Description
   * - ``.set_radiation_boundary(use_open_region=True)``
     - Enable radiation open-region boundary.
   * - ``.set_pml_boundary(operating_freq, radiation_level, is_pml_visible)``
     - Enable PML open-region boundary.
   * - ``.set_air_box_extents(horizontal_size, horizontal_is_multiple, positive_vertical_size, …)``
     - Set air-box padding on all sides.
   * - ``.set_extent(extent_type, base_polygon, truncate_air_box_at_ground)``
     - Set the layout extent shape.
   * - ``.set_dielectric_extent(extent_type, expansion_size, is_multiple, base_polygon, honor_user_dielectric)``
     - Configure the dielectric envelope.

Operations
----------

``cfg.operations.add_cutout(signal_nets, reference_nets, extent_type, expansion_size, expansion_factor, …)``

.. list-table::
   :header-rows: 1
   :widths: 35 15 50

   * - Parameter
     - Default
     - Description
   * - ``signal_nets``
     - –
     - Signal nets to retain inside the cutout.
   * - ``reference_nets``
     - –
     - Reference (ground) nets.
   * - ``extent_type``
     - ``"ConvexHull"``
     - ``"BoundingBox"`` \| ``"Conformal"`` \| ``"ConvexHull"`` (case-insensitive).
   * - ``expansion_size``
     - ``0.002``
     - Absolute boundary expansion in metres.
   * - ``expansion_factor``
     - ``0``
     - Relative expansion factor (takes precedence when > 0).
   * - ``auto_identify_nets_enabled``
     - ``False``
     - Auto-populate signal nets from passive thresholds.
   * - ``resistor_below``
     - ``100``
     - Resistance threshold for auto-identification (Ω).
   * - ``inductor_below``
     - ``1``
     - Inductance threshold for auto-identification (H).
   * - ``capacitor_above``
     - ``"10nF"``
     - Capacitance threshold for auto-identification.

``cfg.operations.generate_auto_hfss_regions = True``  to generate automatic HFSS solver regions.

S-parameters
------------

``cfg.s_parameters.add(name, component_definition, file_path, reference_net, apply_to_all, components, reference_net_per_component, pin_order)``

SPICE models
------------

``cfg.spice_models.add(name, component_definition, file_path, sub_circuit_name, apply_to_all, components, terminal_pairs)``

Package definitions
-------------------

``cfg.package_definitions.add(name, component_definition, apply_to_all, components, maximum_power, thermal_conductivity, theta_jb, theta_jc, height, extent_bounding_box)``

Call ``.set_heatsink(fin_base_height, fin_height, fin_orientation, fin_spacing, fin_thickness)`` on the returned object to add heat-sink fin geometry.

Variables
---------

``cfg.variables.add(name, value, description="")``

Prefix *name* with ``$`` for project-scope variables; no prefix for design-scope.

Modeler
-------

.. list-table::
   :header-rows: 1
   :widths: 50 50

   * - Method
     - Description
   * - ``.add_trace(name, layer, width, net_name, path, incremental_path, start_cap_style, end_cap_style, corner_style)``
     - Create a trace.
   * - ``.add_rectangular_plane(layer, name, net_name, lower_left_point, upper_right_point, corner_radius, rotation, voids)``
     - Create a rectangle.
   * - ``.add_circular_plane(layer, name, net_name, radius, position, voids)``
     - Create a circle.
   * - ``.add_polygon_plane(layer, name, net_name, points, voids)``
     - Create a polygon.
   * - ``.add_padstack_definition(name, hole_plating_thickness, material, hole_range, …)``
     - Add a padstack definition in the modeler section.
   * - ``.add_padstack_instance(name, net_name, definition, layer_range, position, rotation, …)``
     - Place a padstack instance.
   * - ``.add_component(reference_designator, part_type, enabled, definition, placement_layer, pins)``
     - Add a component created from padstack instances.
   * - ``.delete_primitives_by_layer(layer_names)``
     - Schedule all primitives on listed layers for deletion.
   * - ``.delete_primitives_by_name(primitive_names)``
     - Schedule named primitives for deletion.
   * - ``.delete_primitives_by_net(net_names)``
     - Schedule all primitives on listed nets for deletion.

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
