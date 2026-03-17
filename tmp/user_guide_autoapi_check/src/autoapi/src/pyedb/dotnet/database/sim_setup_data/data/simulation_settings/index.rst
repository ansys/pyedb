src.pyedb.dotnet.database.sim_setup_data.data.simulation_settings
=================================================================

.. py:module:: src.pyedb.dotnet.database.sim_setup_data.data.simulation_settings


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.sim_setup_data.data.simulation_settings.BaseSimulationSettings
   src.pyedb.dotnet.database.sim_setup_data.data.simulation_settings.SimulationSettings
   src.pyedb.dotnet.database.sim_setup_data.data.simulation_settings.HFSSSimulationSettings
   src.pyedb.dotnet.database.sim_setup_data.data.simulation_settings.HFSSPISimulationSettings


Module Contents
---------------

.. py:class:: BaseSimulationSettings(pedb, sim_setup, edb_object)

   .. py:property:: enabled


.. py:class:: SimulationSettings(pedb, sim_setup, edb_object)

   Bases: :py:obj:`BaseSimulationSettings`


.. py:class:: HFSSSimulationSettings(pedb, sim_setup, edb_object)

   Bases: :py:obj:`SimulationSettings`


   .. py:property:: mesh_operations


.. py:class:: HFSSPISimulationSettings(pedb, sim_setup, edb_object)

   Bases: :py:obj:`SimulationSettings`


   .. py:property:: auto_select_nets_for_simulation

      Auto select nets for simulation.

      Returns
      -------
          bool



   .. py:property:: ignore_dummy_nets_for_selected_nets

      Auto select Nets for simulation

      Returns
      -------
          bool



   .. py:property:: ignore_small_holes

      Ignore small holes choice.

      Returns
      -------
          bool



   .. py:property:: ignore_small_holes_min_diameter

      Min diameter to ignore small holes.

      Returns
      -------
          str



   .. py:property:: improved_loss_model

      Improved Loss Model on power ground nets option.
      1: Level 1
      2: Level 2
      3: Level 3



   .. py:property:: include_enhanced_bond_wire_modeling

      Enhance Bond wire modeling.

      Returns
      -------
          bool



   .. py:property:: include_nets

      Add Additional Nets for simulation.

      Returns
      -------
          [str]
          List of net name.



   .. py:property:: min_plane_area_to_mesh

      The minimum area below which geometry is ignored.

      Returns
      -------
          str



   .. py:property:: min_void_area_to_mesh

      The minimum area below which voids are ignored.

      Returns
      -------
          str



   .. py:property:: model_type

      Model Type setting.

      0: RDL,
      1: Package
      2: PCB

      Returns
      -------
          int




   .. py:property:: perform_erc

      Perform ERC

      Returns
      -------
          bool



   .. py:property:: pi_slider_pos

      The Simulation Preference Slider setting
      Model type: ``0``= balanced, ``1``=Accuracy.
      Returns
      -------
          int



   .. py:property:: rms_surface_roughness

      RMS Surface Roughness setting

      Returns
      -------
          str



   .. py:property:: signal_nets_conductor_modeling
      :type: int


      Conductor Modeling.
      0: MeshInside,
      1: ImpedanceBoundary



   .. py:property:: signal_nets_error_tolerance

      Error Tolerance

      Returns
      -------
          str
      Value between 0.02 and 1.



   .. py:property:: signal_nets_include_improved_dielectric_fill_refinement


   .. py:property:: signal_nets_include_improved_loss_handling

      Improved Dielectric Fill Refinement choice.

      Returns
      -------
          bool



   .. py:property:: snap_length_threshold


   .. py:property:: surface_roughness_model

      Chosen Model setting
      Model allowed, ``"None"``, ``"Exponential"`` or ``"Hammerstad"``.

      Returns
      -------
          str




