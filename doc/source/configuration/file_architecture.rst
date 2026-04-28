Configuration file architecture
===============================

PyEDB configuration files let you describe design setup, modeling content,
excitations, and post-processing options in a single JSON or TOML document.
The same data model can be consumed from a file **or** built entirely in Python
through the programmatic API described in :doc:`cfg_api_guide`.

This page explains how the configuration file is organized, what each top-level
section is used for, and which fields are supported by each section.

.. note::

   While this guide uses JSON fragments for readability, the same hierarchy can
   also be written as TOML.  The section names and nested field names are
   identical in both formats.

Two ways to configure a design
-------------------------------

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - Approach
     - When to use
     - How to apply
   * - **File-based** (this page)
     - Reproducible, version-controlled, human-readable artifacts.
     - ``edb.configuration.run("my_config.json")``
   * - **Programmatic API** (:doc:`cfg_api_guide`)
     - Scripted workflows, templates, conditional logic.
     - ``cfg = edb.configuration.create_config_builder()`` → ``edb.configuration.run(cfg)``

.. tip::

   ``edb.configuration.run()`` accepts a file path, a plain dictionary, **or**
   an ``EdbConfigBuilder`` instance. You can
   mix and match approaches in the same script.

How a configuration file is consumed
--------------------------------------

At runtime, PyEDB parses the file (or builder) into a dictionary, maps each
top-level key to an internal section model, and then applies those models to
the active EDB design.

.. graphviz::

   digraph configuration_architecture {
       rankdir=LR;
       node [shape=box, style="rounded,filled", fillcolor="#F7F7F7", color="#4F81BD"];
       edge [color="#4F81BD"];

       file    [label="JSON / TOML file\nor EdbConfigBuilder"];
       load    [label="Configuration.load(...)"];
       cfgdata [label="CfgData\n(section manager)"];
       run     [label="Configuration.run(cfg)\napply methods"];
       design  [label="Active EDB design"];

       file -> load -> cfgdata -> run -> design;
   }

Top-level architecture
----------------------

A configuration file is a single dictionary. Every top-level key is optional.
If a section is omitted, PyEDB leaves that area unchanged.

.. list-table:: Top-level sections
   :header-rows: 1
   :widths: 18 14 38 30

   * - Section
     - JSON type
     - Purpose
     - Typical content
   * - ``general``
     - object
     - Global library paths and design flags.
     - SPICE library path, S-parameter library path, pad options.
   * - ``stackup``
     - object
     - Material definitions and layer stack.
     - ``materials[]``, ``layers[]``.
   * - ``nets``
     - object
     - Net classification.
     - ``signal_nets[]``, ``power_ground_nets[]``.
   * - ``components``
     - array
     - Component model and package settings.
     - RLC, S-parameter, SPICE, die, solder-ball, port properties.
   * - ``padstacks``
     - object
     - Padstack definitions and placed instances.
     - ``definitions[]``, ``instances[]``.
   * - ``pin_groups``
     - array
     - Named groups of pins for ports and sources.
     - Explicit pin lists or groups derived from nets.
   * - ``terminals``
     - array
     - Low-level EDB terminal definitions.
     - Padstack, pin-group, point, edge, and bundle terminals.
   * - ``ports``
     - array
     - Port definitions.
     - Circuit, coax, wave, gap, and differential wave ports.
   * - ``sources``
     - array
     - Current and voltage sources.
     - Positive and negative terminal specifiers, magnitude, impedance.
   * - ``probes``
     - array
     - Voltage probes.
     - Positive and negative terminal specifiers.
   * - ``setups``
     - array
     - Simulation setups.
     - HFSS, SIwave AC, SIwave DC, sweeps, mesh operations.
   * - ``boundaries``
     - object
     - HFSS region and dielectric extent settings.
     - Radiation/PML, air-box extents, dielectric extent.
   * - ``operations``
     - object
     - Layout operations applied after import.
     - Cutout and auto HFSS region generation.
   * - ``s_parameters``
     - array
     - S-parameter model assignments.
     - Touchstone path, component definition, reference net mapping.
   * - ``spice_models``
     - array
     - SPICE model assignments.
     - Model path, subcircuit, target components.
   * - ``package_definitions``
     - array
     - Thermal package definitions.
     - Theta values, power, geometry, heat sink.
   * - ``variables``
     - array
     - Design and project variables.
     - Name, value, description.
   * - ``modeler``
     - object
     - Geometry-driven construction and cleanup.
     - Traces, planes, padstacks, components, primitive deletion.

Minimal file shape
------------------

The following skeleton shows the overall shape of a complete configuration
payload:

.. code-block:: json

   {
     "general": {},
     "stackup": {
       "materials": [],
       "layers": []
     },
     "nets": {
       "signal_nets": [],
       "power_ground_nets": []
     },
     "components": [],
     "padstacks": {
       "definitions": [],
       "instances": []
     },
     "pin_groups": [],
     "terminals": [],
     "ports": [],
     "sources": [],
     "probes": [],
     "setups": [],
     "boundaries": {},
     "operations": {},
     "s_parameters": [],
     "spice_models": [],
     "package_definitions": [],
     "variables": [],
     "modeler": {}
   }

Supported sections and fields
-----------------------------

``general``
~~~~~~~~~~~

Use this section for design-wide paths and a small number of global options.

.. list-table:: ``general`` fields
   :header-rows: 1
   :widths: 28 18 54

   * - Field
     - Type
     - Purpose
   * - ``spice_model_library``
     - string
     - Base folder used to resolve relative paths in ``spice_models``.
   * - ``s_parameter_library``
     - string
     - Base folder used to resolve relative paths in ``s_parameters``.
   * - ``anti_pads_always_on``
     - boolean
     - Controls the design option that keeps anti-pads enabled.
   * - ``suppress_pads``
     - boolean
     - Controls the design option that suppresses pads where supported.

``stackup``
~~~~~~~~~~~

This section defines materials and the layer sequence.

``stackup.materials[]`` objects support these keys:

* ``name``
* ``conductivity``
* ``dielectric_loss_tangent``
* ``magnetic_loss_tangent``
* ``mass_density``
* ``permittivity``
* ``permeability``
* ``poisson_ratio``
* ``specific_heat``
* ``thermal_conductivity``
* ``youngs_modulus``
* ``thermal_expansion_coefficient``
* ``dc_conductivity``
* ``dc_permittivity``
* ``dielectric_model_frequency``
* ``loss_tangent_at_frequency``
* ``permittivity_at_frequency``
* ``thermal_modifiers``

``stackup.layers[]`` objects support these keys:

* ``name``
* ``type``
* ``material``
* ``fill_material``
* ``thickness``
* ``roughness``
* ``etching``

``roughness`` supports:

* ``enabled``
* ``top`` / ``bottom`` / ``side``
* Each surface can use either a Huray model
  (``model``, ``nodule_radius``, ``surface_ratio``)
  or a Groisse model (``model``, ``roughness``).

``etching`` supports:

* ``factor``
* ``etch_power_ground_nets``
* ``enabled``

Example:

.. code-block:: json

   {
     "stackup": {
       "materials": [
         {
           "name": "copper",
           "conductivity": 58000000.0
         },
         {
           "name": "fr4",
           "permittivity": 4.4,
           "dielectric_loss_tangent": 0.02
         }
       ],
       "layers": [
         {
           "name": "top",
           "type": "signal",
           "material": "copper",
           "fill_material": "fr4",
           "thickness": "35um"
         },
         {
           "name": "diel1",
           "type": "dielectric",
           "material": "fr4",
           "thickness": "100um"
         }
       ]
     }
   }

``nets``
~~~~~~~~

Use this section to classify nets by intent.

.. list-table:: ``nets`` fields
   :header-rows: 1
   :widths: 28 18 54

   * - Field
     - Type
     - Purpose
   * - ``signal_nets``
     - array of strings
     - Nets treated as signal nets.
   * - ``power_ground_nets``
     - array of strings
     - Nets treated as power or ground nets.

``components``
~~~~~~~~~~~~~~

This section assigns electrical and package-related properties to component
instances.

Each ``components[]`` entry supports these keys:

.. list-table:: ``components[]`` fields
   :header-rows: 1
   :widths: 28 18 54

   * - Field
     - Type
     - Purpose
   * - ``reference_designator``
     - string
     - Component instance name such as ``U1`` or ``R15``.
   * - ``part_type``
     - string
     - Component type such as ``resistor``, ``capacitor``, or ``ic``.
   * - ``enabled``
     - boolean
     - Enables or disables application of the entry.
   * - ``definition``
     - string
     - Component definition / part name.
   * - ``placement_layer``
     - string
     - Placement layer used when constructing components in ``modeler``.
   * - ``pin_pair_model``
     - array
     - Pin-pair RLC model definitions.
   * - ``s_parameter_model``
     - object
     - S-parameter model assignment for the component.
   * - ``spice_model``
     - object
     - SPICE model assignment for the component.
   * - ``netlist_model``
     - object
     - Raw netlist payload.
   * - ``ic_die_properties``
     - object
     - Die configuration for IC components.
   * - ``solder_ball_properties``
     - object
     - Solder-ball geometry and material.
   * - ``port_properties``
     - object
     - Port reference geometry.

Nested component objects support these keys:

* ``pin_pair_model[]``: ``first_pin``, ``second_pin``, ``resistance``,
  ``inductance``, ``capacitance``, ``is_parallel``,
  ``resistance_enabled``, ``inductance_enabled``, ``capacitance_enabled``.
* ``s_parameter_model``: ``model_name``, ``model_path``, ``reference_net``.
* ``spice_model``: ``model_name``, ``model_path``, ``sub_circuit``,
  ``terminal_pairs``.
* ``netlist_model``: ``netlist``.
* ``ic_die_properties``: ``type`` (``flip_chip``, ``wire_bond``, ``no_die``),
  ``orientation`` (``chip_up`` or ``chip_down``), ``height``.
* ``solder_ball_properties``: ``shape`` (``cylinder``, ``spheroid``,
  ``no_solder_ball``), ``diameter``, ``height``, ``material``,
  ``mid_diameter``.
* ``port_properties``: ``reference_height``, ``reference_size_auto``,
  ``reference_size_x``, ``reference_size_y``.

``padstacks``
~~~~~~~~~~~~~

Use this section to define padstack definitions and update placed padstack
instances.

``padstacks.definitions[]`` supports:

* ``name``
* ``hole_plating_thickness``
* ``material`` (serialized as the hole material)
* ``hole_range``
* ``pad_parameters``
* ``hole_parameters``
* ``solder_ball_parameters``

``padstacks.instances[]`` supports:

* ``name``
* ``id``
* ``backdrill_parameters``
* ``is_pin``
* ``net_name``
* ``layer_range``
* ``definition``
* ``position``
* ``rotation``
* ``hole_override_enabled``
* ``hole_override_diameter``
* ``solder_ball_layer``

``backdrill_parameters`` can define ``from_top`` and/or ``from_bottom``. Each
branch can use either:

* ``drill_to_layer`` + ``diameter``
* ``drill_to_layer`` + ``diameter`` + ``stub_length``
* ``drill_depth`` + ``diameter``

``pin_groups``
~~~~~~~~~~~~~~

Use pin groups to name a set of pins once and then reuse that name in ports,
sources, probes, or explicit terminals.

Each ``pin_groups[]`` entry supports:

* ``name``
* ``reference_designator``
* ``pins`` (explicit pin list)
* ``net`` (single net name or list of net names)

Define either ``pins`` or ``net``.

``terminals``
~~~~~~~~~~~~~

This is the low-level terminal section. Most users do not need it because
``ports``, ``sources``, and ``probes`` create terminals implicitly. It becomes
useful when you want explicit terminal objects or bundle terminals.

Supported terminal entry types are:

* ``padstack_instance``
* ``pin_group``
* ``point``
* ``edge``
* ``bundle``

Common terminal keys are:

* ``name``
* ``impedance``
* ``is_circuit_port``
* ``reference_terminal``
* ``amplitude``
* ``phase``
* ``terminal_to_ground``
* ``boundary_type``
* ``hfss_type``

Type-specific keys:

* ``padstack_instance``: ``padstack_instance``, ``padstack_instance_id``,
  ``layer``
* ``pin_group``: ``pin_group``
* ``point``: ``x``, ``y``, ``layer``, ``net``
* ``edge``: ``primitive``, ``point_on_edge_x``, ``point_on_edge_y``,
  ``horizontal_extent_factor``, ``vertical_extent_factor``,
  ``pec_launch_width``
* ``bundle``: ``terminals``

``ports``, ``sources``, and ``probes``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These sections use terminal *specifiers* rather than low-level terminal objects.

Supported terminal-specifier forms are:

.. list-table:: Terminal specifiers
   :header-rows: 1
   :widths: 24 34 42

   * - Specifier
     - Shape
     - Purpose
   * - Pin
     - ``{"pin": "A1"}``
     - Address a specific component pin.
   * - Net
     - ``{"net": "VDD"}``
     - Address pins on a named net.
   * - Pin group
     - ``{"pin_group": "pg_VDD"}``
     - Reuse a previously defined pin group.
   * - Padstack instance
     - ``{"padstack": "via_1"}``
     - Address a named padstack instance.
   * - Coordinates
     - ``{"coordinates": {"layer": "top", "point": [x, y], "net": "SIG"}}``
     - Create a point-based terminal at a coordinate.
   * - Nearest pin
     - ``{"nearest_pin": {"reference_net": "GND", "search_radius": "5mm"}}``
     - Choose a reference pin automatically for negative terminals.

Optional terminal-specifier helper fields supported by the runtime terminal
resolver are:

* ``reference_designator``
* ``contact_type`` (for example ``default``, ``full``, ``center``, ``quad``,
  ``inline``)
* ``contact_radius``
* ``num_of_contact``
* ``contact_expansion``

Each ``ports[]`` entry uses one of these shapes:

* Circuit or coax port:

  * ``name``
  * ``type`` = ``circuit`` or ``coax``
  * ``positive_terminal``
  * ``negative_terminal`` (circuit only)
  * ``reference_designator``
  * ``impedance``
  * ``distributed``

* Wave or gap port:

  * ``name``
  * ``type`` = ``wave_port`` or ``gap_port``
  * ``primitive_name``
  * ``point_on_edge``
  * ``horizontal_extent_factor``
  * ``vertical_extent_factor``
  * ``pec_launch_width``

* Differential wave port:

  * ``name``
  * ``type`` = ``diff_wave_port``
  * ``positive_terminal`` with ``primitive_name`` and ``point_on_edge``
  * ``negative_terminal`` with ``primitive_name`` and ``point_on_edge``
  * ``horizontal_extent_factor``
  * ``vertical_extent_factor``
  * ``pec_launch_width``

Each ``sources[]`` entry supports:

* ``name``
* ``type`` = ``current`` or ``voltage``
* ``positive_terminal``
* ``negative_terminal``
* ``magnitude``
* ``impedance``
* ``reference_designator``
* ``distributed``

Each ``probes[]`` entry supports:

* ``name``
* ``type`` = ``probe``
* ``positive_terminal``
* ``negative_terminal``
* ``reference_designator``

``setups``
~~~~~~~~~~

The ``setups`` array contains HFSS, SIwave AC, and SIwave DC simulation setup
objects.

Every setup has at least:

* ``name``
* ``type``

``hfss`` setups support:

* ``adapt_type`` = ``single``, ``broadband``, or ``multi_frequencies``
* ``single_frequency_adaptive_solution``
* ``broadband_adaptive_solution``
* ``multi_frequency_adaptive_solution``
* ``auto_mesh_operation``
* ``mesh_operations``
* ``freq_sweep``

``single_frequency_adaptive_solution`` supports:

* ``adaptive_frequency``
* ``max_passes``
* ``max_delta``

``broadband_adaptive_solution`` supports:

* ``low_frequency``
* ``high_frequency``
* ``max_passes``
* ``max_delta``

``multi_frequency_adaptive_solution`` supports:

* ``adapt_frequencies[]`` with ``adaptive_frequency``, ``max_passes``, and
  ``max_delta``

``auto_mesh_operation`` supports:

* ``enabled``
* ``trace_ratio_seeding``
* ``signal_via_side_number``

``mesh_operations[]`` currently supports length mesh operations with:

* ``type`` or ``mesh_operation_type`` = ``length``
* ``name``
* ``max_elements``
* ``max_length``
* ``restrict_length``
* ``refine_inside``
* ``nets_layers_list``

``siwave_ac`` setups support:

* ``use_si_settings``
* ``si_slider_position``
* ``pi_slider_position``
* ``freq_sweep``

``siwave_dc`` setups support:

* ``dc_slider_position``
* ``dc_ir_settings`` with ``export_dc_thermal_data``

All AC sweep objects inside ``freq_sweep`` support:

* ``name``
* ``type`` = ``discrete``, ``interpolation``, or ``interpolating``
* ``frequencies``
* ``use_q3d_for_dc``
* ``compute_dc_point``
* ``enforce_causality``
* ``enforce_passivity``
* ``adv_dc_extrapolation``
* ``use_hfss_solver_regions``
* ``hfss_solver_region_setup_name``
* ``hfss_solver_region_sweep_name``

Each ``frequencies[]`` entry supports:

* ``start``
* ``stop``
* ``increment``
* ``distribution`` = ``linear_scale``, ``log_scale``, ``single``,
  ``linear_count``, ``log_count``

``boundaries``
~~~~~~~~~~~~~~

Use this section to control HFSS open-region and dielectric extent settings.

Supported keys are:

* ``use_open_region``
* ``open_region_type``
* ``is_pml_visible``
* ``operating_freq``
* ``radiation_level``
* ``dielectric_extent_type``
* ``dielectric_base_polygon``
* ``dielectric_extent_size`` with ``size`` and ``is_multiple``
* ``honor_user_dielectric``
* ``extent_type``
* ``base_polygon``
* ``truncate_air_box_at_ground``
* ``air_box_horizontal_extent`` with ``size`` and ``is_multiple``
* ``air_box_positive_vertical_extent`` with ``size`` and ``is_multiple``
* ``air_box_negative_vertical_extent`` with ``size`` and ``is_multiple``
* ``sync_air_box_vertical_extent``

``operations``
~~~~~~~~~~~~~~

Use this section for cutout creation and automatic HFSS region generation.

Supported keys are:

* ``cutout``
* ``generate_auto_hfss_regions``

``cutout`` supports:

* ``auto_identify_nets`` with ``enabled``, ``resistor_below``,
  ``inductor_below``, ``capacitor_above``
* ``signal_list``
* ``reference_list``
* ``extent_type``
* ``expansion_size``
* ``number_of_threads``
* ``custom_extent``
* ``custom_extent_units``
* ``expansion_factor``

``s_parameters``
~~~~~~~~~~~~~~~~

Each ``s_parameters[]`` entry supports:

* ``name``
* ``component_definition``
* ``file_path``
* ``apply_to_all``
* ``components``
* ``reference_net``
* ``reference_net_per_component``
* ``pin_order``

Relative ``file_path`` values are resolved from ``general.s_parameter_library``.

``spice_models``
~~~~~~~~~~~~~~~~

Each ``spice_models[]`` entry supports:

* ``name``
* ``component_definition``
* ``file_path``
* ``sub_circuit_name``
* ``apply_to_all``
* ``components``
* ``terminal_pairs``

Relative ``file_path`` values are resolved from ``general.spice_model_library``.

``package_definitions``
~~~~~~~~~~~~~~~~~~~~~~~

Use this section for thermal package and heat-sink definitions.

Each ``package_definitions[]`` entry supports:

* ``name``
* ``component_definition``
* ``maximum_power``
* ``thermal_conductivity``
* ``theta_jb``
* ``theta_jc``
* ``height``
* ``apply_to_all``
* ``components``
* ``extent_bounding_box``
* ``heatsink``

``heatsink`` supports:

* ``fin_base_height``
* ``fin_height``
* ``fin_orientation``
* ``fin_spacing``
* ``fin_thickness``

``variables``
~~~~~~~~~~~~~

Each ``variables[]`` entry supports:

* ``name``
* ``value``
* ``description``

Names starting with ``$`` are created as project variables. Other names are
created as design variables.

``modeler``
~~~~~~~~~~~

Use this section to create traces, planes, padstack content, components, and
primitive deletions.

Supported keys are:

* ``traces``
* ``planes``
* ``padstack_definitions``
* ``padstack_instances``
* ``components``
* ``primitives_to_delete``

``traces[]`` support:

* ``name``
* ``layer``
* ``path``
* ``width``
* ``net_name``
* ``start_cap_style``
* ``end_cap_style``
* ``corner_style``
* ``incremental_path``

``planes[]`` support:

* Common: ``name``, ``layer``, ``net_name``, ``type``, ``voids``
* Rectangle: ``lower_left_point``, ``upper_right_point``, ``corner_radius``,
  ``rotation``
* Polygon: ``points``
* Circle: ``radius``, ``position``

``modeler.padstack_definitions[]`` and ``modeler.padstack_instances[]`` use the
same payload shapes as the top-level ``padstacks`` section.

``modeler.components[]`` use the same payload shape as the top-level
``components`` section, and can additionally be combined with the created
padstack instances referenced through ``pins`` in the lower-level runtime
configuration path.

``primitives_to_delete`` supports:

* ``layer_name``
* ``name``
* ``net_name``

Best practices
--------------

* Start with only the sections you need.
* Prefer ``pin_groups`` and terminal specifiers for readability.
* Use ``ports`` / ``sources`` / ``probes`` unless you explicitly need
  low-level ``terminals``.
* Keep relative model paths under ``general.spice_model_library`` and
  ``general.s_parameter_library``.
* When a section is empty, omit it entirely instead of writing empty values.
* For programmatic authoring, prefer :doc:`cfg_api_guide`.

Next step
---------

If you want to generate these payloads in Python instead of hand-authoring JSON,
continue with :doc:`cfg_api_guide`.

