Configuration API guide and complete example
============================================

The :mod:`pyedb.configuration` package provides a Python interface for
building the same configuration payload described in :doc:`file_architecture`.
Instead of manually authoring JSON, you populate a ``CfgData`` object and then pass it directly
to ``Configuration.run`` with no
serialization step required.

.. tip::

   The easiest way to obtain a builder when you already have an open EDB session
   is ``edb.configuration.create_config_builder()``.  This keeps everything
   within the ``edb.configuration`` namespace and avoids a direct import of
   ``CfgData``.

Why use the configuration API?
------------------------------

The programmatic API is useful when you want to:

* build configurations from templates or scripts,
* reuse helper functions across projects,
* validate values in Python before writing the file,
* generate only the sections you need,
* pass a builder directly to ``run()`` without touching the file system, and
* move between dictionary, JSON, and TOML forms.

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

   from pyedb.configuration import CfgData

   cfg = CfgData()
   cfg.general.anti_pads_always_on = False
   cfg.nets.add_signal_nets(["SIG1", "CLK"])

   # Apply to an open session later:
   edb.configuration.run(cfg)

   # Or persist to a file for review or version control:
   cfg.to_json("my_config.json")

Session-aware ``get()`` methods
--------------------------------

When a builder is created via ``edb.configuration.create_config_builder()`` it
is bound to the live EDB session. Each section exposes a ``get()`` (or
``get_layer`` / ``get_material`` / ``get_definition`` / ``get_instance``)
helper that retrieves an *existing* database object and wraps it in the
corresponding builder. This avoids having to define again objects that already
exist in the design.

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - Call
     - Returns
   * - ``cfg.components.get("U1")``
     - :class:`ComponentConfig` pre-loaded with all current EDB properties.
   * - ``cfg.stackup.get_layer("top")``
     - :class:`LayerConfig` pre-loaded with current layer properties.
   * - ``cfg.stackup.get_material("copper")``
     - :class:`MaterialConfig` pre-loaded with current material properties.
   * - ``cfg.nets.get("GND")``
     - :class:`CfgNet` bound to the live EDB session. Attributes: ``name``,
       ``is_power_ground`` (Boolean), ``classification`` (``"signal"`` or
       ``"power_ground"``). Returns ``False`` if the net does not exist.
   * - ``cfg.padstacks.get_definition("via_0.2")``
     - :class:`PadstackDefinitionConfig` pre-loaded with current definition.
   * - ``cfg.padstacks.get_instance("via_A1")``
     - :class:`PadstackInstanceConfig` pre-loaded with current instance data.
   * - ``cfg.pin_groups.get("pg_VDD")``
     - :class:`PinGroupConfig` pre-loaded with current pin membership.
   * - ``cfg.setups.get("hfss_bb")``
     - The matching registered setup builder (``HfssSetupConfig``, etc.).

Each ``get()`` call caches the result—calling it twice with the same name
returns the same object. If the object was already registered (for example, via
``add``), the cached entry is returned instead.

.. code-block:: python

   cfg = edb.configuration.create_config_builder()

   # ── Existing component ──────────────────────────────────────────────────
   u1 = cfg.components.get("U1")
   u1.set_solder_ball_properties("cylinder", "150um", "100um")
   u1.set_ic_die_properties("flip_chip", orientation="chip_down")

   # ── Existing layer ──────────────────────────────────────────────────────
   top = cfg.stackup.get_layer("top")
   top.set_huray_roughness("0.1um", "2.9")
   top.set_etching(factor=0.4)

   # ── Existing material ───────────────────────────────────────────────────
   cu = cfg.stackup.get_material("copper")
   cu.conductivity = 5.6e7

   # ── Net classification ──────────────────────────────────────────────────
   info = cfg.nets.get("GND")  # also adds GND to power_nets if it is one
   print(info["classification"])  # 'power_ground'

   # ── Existing padstack definition ────────────────────────────────────────
   via_def = cfg.padstacks.get_definition("via_0.2")
   via_def.hole_plating_thickness = "30um"

   # ── Existing padstack instance ──────────────────────────────────────────
   via = cfg.padstacks.get_instance("via_A1")
   via.set_backdrill("L3", "0.25mm", drill_from_bottom=True)

   # ── Existing pin group ──────────────────────────────────────────────────
   pg = cfg.pin_groups.get("pg_VDD")
   print(pg.pins)

   # ── Registered setup ────────────────────────────────────────────────────
   cfg.setups.add_hfss_setup("hfss_bb", adapt_type="broadband")
   setup = cfg.setups.get("hfss_bb")  # retrieve the same object
   setup.add_frequency_sweep("sw2", start="1GHz", stop="20GHz", step_or_count=100)

   edb.configuration.run(cfg)

Generated API reference
-----------------------

Use the generated AutoAPI pages when you want full class signatures, member
lists, or direct links to a specific configuration builder implementation.

.. list-table:: Key AutoAPI links
   :header-rows: 1
   :widths: 38 62

   * - Page
     - When to use it
   * - :doc:`Configuration package overview <../autoapi/pyedb/configuration/index>`
     - Browse every configuration submodule from one landing page.
   * - :doc:`Configuration runtime <../autoapi/pyedb/configuration/configuration/index>`
     - Review ``Configuration.load()``, ``Configuration.run()``, and runtime helpers.
   * - :doc:`Setup builders <../autoapi/pyedb/configuration/cfg_setup/index>`
     - Inspect HFSS and SIwave setup classes including sweep helpers.
   * - :doc:`Ports, sources, and probes <../autoapi/pyedb/configuration/cfg_ports_sources/index>`
     - Inspect ``TerminalInfo`` and excitation builders.
   * - :doc:`Terminal builders <../autoapi/pyedb/configuration/cfg_terminals/index>`
     - Review explicit low-level terminal payload classes.
   * - :doc:`Stackup builders <../autoapi/pyedb/configuration/cfg_stackup/index>`
     - Inspect material, roughness, etching, and layer builders.
   * - :doc:`Component builders <../autoapi/pyedb/configuration/cfg_components/index>`
     - Review component, package, and model-assignment helpers.
   * - :doc:`Padstack builders <../autoapi/pyedb/configuration/cfg_padstacks/index>`
     - Inspect padstack definitions, instances, and backdrill payloads.
   * - :doc:`Boundaries and operations <../autoapi/pyedb/configuration/cfg_boundaries/index>` /
       :doc:`operations <../autoapi/pyedb/configuration/cfg_operations/index>`
     - Review air-box, dielectric extent, and cutout configuration classes.

Applying a configuration
------------------------

``run()`` is the single method to both *load* and *apply* a configuration.
You can pass any of the supported input types directly:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Input type
     - Behaviour
   * - ``CfgData``
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

Terminal Info helpers
---------------------

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

   from pyedb.configuration import TerminalInfo

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
   from pyedb.configuration import TerminalInfo

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
   # Optional: store reference nets so they can be forwarded to add_cutout
   cfg.nets.add_reference_nets(["GND"])

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
   # Coax port – padstack shortcut (most common)
   cfg.ports.add_coax_port("coax1", padstack="v1")
   # Coax port – net shortcut (distributed if >1 matching pin)
   cfg.ports.add_coax_port("coax_vdd", net="VDD", reference_designator="U1")
   # Coax port – pin shortcut
   cfg.ports.add_coax_port("coax_a1", pin="A1", reference_designator="U1", impedance=50)

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
       adapt_type="broadband",  # "single" | "broadband" | "multi_frequencies"
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

   # Frequency sweep – Option A: inline (start/stop/step_or_count in one call)
   hfss.add_frequency_sweep(
       "sweep1",
       start="1GHz",
       stop="20GHz",
       step_or_count=100,
       distribution="linear_count",  # or "log_count" | "linear_scale" | "log_scale" | "single"
       sweep_type="interpolation",
       enforce_passivity=True,
   )

   # Frequency sweep – Option B: chained (add multiple ranges on one sweep)
   sweep2 = hfss.add_frequency_sweep(
       "sweep2",
       sweep_type="interpolation",
       use_q3d_for_dc=False,
       compute_dc_point=False,
       enforce_causality=False,
       enforce_passivity=True,
       adv_dc_extrapolation=False,
   )
   sweep2.add_linear_count_frequencies("1GHz", "20GHz", 100)
   sweep2.add_single_frequency("5GHz")

   # ----- SIwave AC setup -----
   siwave_ac = cfg.setups.add_siwave_ac_setup(
       "siw_ac",
       si_slider_position=2,  # 0=Speed | 1=Balanced | 2=Accuracy
       pi_slider_position=1,
       use_si_settings=True,
   )
   # Inline sweep (start/stop/step_or_count) – no separate chaining call needed
   siwave_ac.add_frequency_sweep(
       "siw_sw1",
       start="1kHz",
       stop="1GHz",
       step_or_count=100,
       distribution="log_count",
       compute_dc_point=False,
       enforce_passivity=True,
   )

   # ----- SIwave DC setup -----
   cfg.setups.add_siwave_dc_setup(
       "siw_dc",
       dc_slider_position=1,  # 0=Speed | 1=Balanced | 2=Accuracy
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
   # Option A: explicit lists
   cfg.operations.add_cutout(
       signal_nets=["DDR4_DQ0", "CLK"],
       reference_nets=["GND"],
       extent_type="ConvexHull",  # case-insensitive
       expansion_size=0.002,
       auto_identify_nets_enabled=True,
   )
   # Option B: reuse previously stored net lists (no duplication)
   cfg.operations.add_cutout(
       signal_nets=cfg.nets.signal_nets,
       reference_nets=cfg.nets.reference_nets,
       extent_type="ConvexHull",
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

``CfgData`` can be passed **directly** to ``edb.configuration.run()``,
no ``.to_dict()`` call is required:

.. code-block:: python

   cfg = edb.configuration.create_config_builder()
   cfg.nets.add_signal_nets(["SIG1", "CLK"])
   cfg.nets.add_power_ground_nets(["VDD", "GND"])

   # Pass the builder directly — to_dict() is called internally.
   edb.configuration.run(cfg)

If you also want to save the configuration for review, archiving, or reuse in
another project, serialize the builder before (or instead of) calling ``run()``:

.. code-block:: python

   # Inspect as a plain dict (optional — not needed to call run())
   payload = cfg.to_dict()

   # Write to disk
   cfg.to_json("my_project_config.json")
   cfg.to_toml("my_project_config.toml")

   # Apply the saved file later via file path
   edb.configuration.run("my_project_config.json")

.. note::

   ``edb.configuration.run(cfg)`` accepts a ``CfgData`` instance
   directly and handles the serialization step internally. You only need
   ``cfg.to_dict()`` when you want to inspect the payload programmatically or
   pass it to another API that expects a plain dictionary.

Round-trip helpers
------------------

The root builder supports round-tripping from existing dictionaries, JSON, or
TOML files. This is useful for loading a template, tweaking specific values, and
re-exporting.

.. code-block:: python

   from pyedb.configuration import CfgData

   # Load from a file, modify, and save back
   cfg = CfgData.from_json("base_config.json")
   cfg.general.suppress_pads = True
   cfg.stackup.add_material("silver", conductivity=6.3e7)
   cfg.to_json("modified_config.json")

   # Load from a dict
   cfg2 = CfgData.from_dict({"nets": {"signal_nets": ["CLK"]}})
   cfg2.to_toml("nets_only.toml")

Practical recommendations
-------------------------

* **Use** ``edb.configuration.create_config_builder()`` when working inside an
  active EDB session. It avoids the extra import and keeps calling conventions
  consistent.
* **Call** ``edb.configuration.run(cfg)`` to load and apply in a single
  statement. Pass ``None`` (the default) to apply previously loaded data again.
* **Prefer** ``TerminalInfo`` factory methods
  over hand-written terminal dictionaries.
* **Build only the sections you need**: empty sections are omitted by
  ``CfgData.to_dict()`` so the
  serialized payload stays minimal.
* **Persist to JSON / TOML** when you want a reviewed artifact kept in version
  control and applied without a Python script.
* **Store reusable snippets** as plain Python functions that accept and return
  a ``CfgData`` instance. Composing
  builders is straightforward.

Related reference
-----------------

For the file-oriented view of the same data model, including field-by-field
section descriptions, see :doc:`file_architecture`.
