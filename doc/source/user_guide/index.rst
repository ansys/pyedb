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
   * - Understand what objects ``Edb`` exposes (stackup, nets, components, ...)
     - :doc:`../getting_started/object_model`
   * - Inspect a board (cells, layers, nets, components)
     - :doc:`../getting_started/quick_start`, :doc:`design_navigation`
   * - Modify a stackup or add materials
     - :doc:`stackup_and_materials`
   * - Find, rename, or classify nets
     - :doc:`components_and_nets`
   * - Place or edit components
     - :doc:`components_and_nets`
   * - Work with padstacks and vias, including back-drilling
     - :doc:`padstacks_and_vias`
   * - Create ports or sources
     - :doc:`ports_and_sources`
   * - Build a cutout around selected nets
     - :doc:`cutouts`
   * - Configure an HFSS 3D Layout setup
     - :doc:`simulation_setups`, :doc:`../workflows/sipi/hfss_auto_configuration`
   * - Create a SIwave simulation setup
     - :doc:`simulation_setups`
   * - Validate a design (DC shorts, DRC, illegal names)
     - :doc:`validation_and_drc`
   * - Drive a workflow from a JSON/TOML configuration file
     - :doc:`../configuration/index`
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
   common_tasks
   design_navigation
   stackup_and_materials
   components_and_nets
   padstacks_and_vias
   ports_and_sources
   cutouts
   simulation_setups
   validation_and_drc
   libraries/index
   communication_protocols
   security_considerations
