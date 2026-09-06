.. _ref_user_guide:

==========
User guide
==========

This section provides brief tutorials for helping you understand how to use PyEDB effectively.

For end-to-end examples, see :ref:`pyedb_examples`. New to PyEDB? Start with the
:doc:`../getting_started/quick_start` and the :doc:`../getting_started/object_model` before returning here.

I want to...
------------

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Goal
     - Where to go
   * - Open or create an EDB for the first time
     - :doc:`../getting_started/quick_start`
   * - Walk through a complete first workflow, explained step by step
     - :doc:`first_pyedb_workflow`
   * - Understand what objects ``Edb`` exposes (stackup, nets, components, ...)
     - :doc:`../getting_started/object_model`
   * - Inspect a board (cells, layers, nets, components)
     - :doc:`../getting_started/quick_start`, :doc:`design_navigation`
   * - Retrieve a full design inventory report (counts, BOM, materials audit)
     - :doc:`design_inventory_report`
   * - Modify a stackup or add materials
     - :doc:`stackup_and_materials`
   * - Find, rename, or classify nets
     - :doc:`components_and_nets`
   * - Place or edit components
     - :doc:`components_and_nets`
   * - Work with padstacks and vias, including back-drilling
     - :doc:`padstacks_and_vias`
   * - Find primitives (traces, polygons) by layer, net, or type
     - :doc:`geometry_and_connectivity`
   * - Find disconnected traces or isolated vias
     - :doc:`find_isolated_vias`
   * - Create ports or sources
     - :doc:`ports_and_sources`
   * - Build a cutout around selected nets
     - :doc:`cutouts`
   * - Compare extent strategies or build a custom-shaped cutout
     - :doc:`advanced_cutout_strategies`
   * - Configure an HFSS 3D Layout setup
     - :doc:`simulation_setups`, :doc:`../workflows/sipi/hfss_auto_configuration`
   * - Create a SIwave simulation setup
     - :doc:`simulation_setups`
   * - Validate a design (DC shorts, DRC, illegal names)
     - :doc:`validation_and_drc`
   * - Drive a workflow from a JSON/TOML configuration file
     - :doc:`../configuration/index`
   * - Compare two design revisions and detect what changed
     - :doc:`compare_database_revisions`
   * - Batch-process an entire library of designs
     - :doc:`batch_processing_multiple_designs`
   * - Prepare a high-speed channel (SI) for HFSS 3D Layout simulation
     - :doc:`si_example_wave_ports`
   * - Prepare a power-delivery network (PI) for a SIwave DCIR analysis
     - :doc:`pi_example_power_aware_dcir`
   * - Convert a script from the DotNet backend to gRPC
     - :doc:`../grpc_migration/migration_guide`
   * - Choose or troubleshoot a backend
     - :doc:`../getting_started/backend_compatibility_migration`


.. grid:: 2

   .. grid-item-card:: Basic tutorial
            :link: intro
            :link-type: doc
            :margin: 2 2 0 0

            How to use PyEDB.

   .. grid-item-card:: Your first workflow, step by step
            :link: first_pyedb_workflow
            :link-type: doc
            :margin: 2 2 0 0

            A narrative, beginner-oriented walkthrough of the five-stage PyEDB script pattern.

   .. grid-item-card:: Architecture and navigation
            :link: design_navigation
            :link-type: doc
            :margin: 2 2 0 0

            Core architecture, backend selection, and design navigation.

   .. grid-item-card:: Common tasks
            :link: common_tasks
            :link-type: doc
            :margin: 2 2 0 0

            Common automated tasks with PyEDB.

   .. grid-item-card:: Stackup and materials
            :link: stackup_and_materials
            :link-type: doc
            :margin: 2 2 0 0

            Define layer stacks and assign materials.

   .. grid-item-card:: Components and nets
            :link: components_and_nets
            :link-type: doc
            :margin: 2 2 0 0

            Inspect components, and find, rename, or group nets.

   .. grid-item-card:: Padstacks and vias
            :link: padstacks_and_vias
            :link-type: doc
            :margin: 2 2 0 0

            Padstack definitions, placed instances, and back-drilling.

   .. grid-item-card:: Geometry and connectivity
            :link: geometry_and_connectivity
            :link-type: doc
            :margin: 2 2 0 0

            Find primitives by layer, net, or type; locate padstack instances on a net.

   .. grid-item-card:: Find isolated vias
            :link: find_isolated_vias
            :link-type: doc
            :margin: 2 2 0 0

            Detect disconnected traces and electrically isolated padstack instances.

   .. grid-item-card:: Ports and sources
            :link: ports_and_sources
            :link-type: doc
            :margin: 2 2 0 0

            Create ports, voltage/current sources, and probes.

   .. grid-item-card:: Cutouts
            :link: cutouts
            :link-type: doc
            :margin: 2 2 0 0

            Build a cutout around selected signal and reference nets.

   .. grid-item-card:: Advanced cutout strategies
            :link: advanced_cutout_strategies
            :link-type: doc
            :margin: 2 2 0 0

            Compare extent algorithms and build a custom-shaped cutout polygon.

   .. grid-item-card:: Simulation setups
            :link: simulation_setups
            :link-type: doc
            :margin: 2 2 0 0

            Create HFSS and SIwave simulation setups.

   .. grid-item-card:: Validation and DRC
            :link: validation_and_drc
            :link-type: doc
            :margin: 2 2 0 0

            Layout hygiene checks and the full design-rule-check engine.

   .. grid-item-card:: Design inventory report
            :link: design_inventory_report
            :link-type: doc
            :margin: 2 2 0 0

            Retrieve a full data snapshot: counts, BOM, materials audit, in one JSON report.

   .. grid-item-card:: Compare database revisions
            :link: compare_database_revisions
            :link-type: doc
            :margin: 2 2 0 0

            Detect exactly what changed between two design revisions.

   .. grid-item-card:: Batch-process multiple designs
            :link: batch_processing_multiple_designs
            :link-type: doc
            :margin: 2 2 0 0

            Run the same recipe across an entire design library with isolated failures.

   .. grid-item-card:: SI example: high-speed channel prep
            :link: si_example_wave_ports
            :link-type: doc
            :margin: 2 2 0 0

            Step-by-step signal-integrity workflow: differential pair, ports, HFSS setup.

   .. grid-item-card:: PI example: power-aware DCIR prep
            :link: pi_example_power_aware_dcir
            :link-type: doc
            :margin: 2 2 0 0

            Step-by-step power-integrity workflow: net classification, DC-short check, DCIR setup.

   .. grid-item-card:: Advanced libraries
            :link: libraries/index
            :link-type: doc
            :margin: 2 2 0 0

            PyEDB advanced libraries.

   .. grid-item-card:: Communication protocol
            :link: communication_protocols
            :link-type: doc
            :margin: 2 2 0 0

            How PyEDB communicates with the ``ansys-edb-core`` gRPC service.

   .. grid-item-card:: Security considerations
            :link: security_considerations
            :link-type: doc
            :margin: 2 2 0 0

            Information on security considerations.

.. toctree::
   :hidden:
   :maxdepth: 2

   intro
   first_pyedb_workflow
   common_tasks
   design_navigation
   stackup_and_materials
   components_and_nets
   padstacks_and_vias
   geometry_and_connectivity
   find_isolated_vias
   ports_and_sources
   cutouts
   advanced_cutout_strategies
   simulation_setups
   validation_and_drc
   design_inventory_report
   compare_database_revisions
   batch_processing_multiple_designs
   si_example_wave_ports
   pi_example_power_aware_dcir
   libraries/index
   communication_protocols
   security_considerations
