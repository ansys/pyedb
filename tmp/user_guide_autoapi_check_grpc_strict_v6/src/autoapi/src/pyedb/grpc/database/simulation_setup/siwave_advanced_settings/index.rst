src.pyedb.grpc.database.simulation_setup.siwave_advanced_settings
=================================================================

.. py:module:: src.pyedb.grpc.database.simulation_setup.siwave_advanced_settings


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.simulation_setup.siwave_advanced_settings.SIWaveAdvancedSettings


Module Contents
---------------

.. py:class:: SIWaveAdvancedSettings(pedb, core: ansys.edb.core.simulation_setup.siwave_simulation_settings.SIWaveAdvancedSettings)

   SIWave advanced settings class.


   .. py:attribute:: core


   .. py:property:: ac_dc_merge_mode
      :type: int


      AC/DC merge mode.

      Returns
      -------
      int
          AC/DC merge mode.



   .. py:property:: cross_talk_threshold
      :type: float


      Cross talk threshold.

      Returns
      -------
      float
          Cross talk threshold.



   .. py:property:: ignore_non_functional_pads
      :type: bool


      Ignore non-functional pads flag.

      Returns
      -------
      bool
          Ignore non-functional pads flag.



   .. py:property:: include_co_plane_coupling
      :type: bool


      Include co-plane coupling flag.

      Returns
      -------
      bool
          Include co-plane coupling flag.



   .. py:property:: include_fringe_plane_coupling
      :type: bool


      Include fringe plane coupling flag.

      Returns
      -------
      bool
          Include fringe plane coupling flag.



   .. py:property:: include_inf_gnd
      :type: bool


      Include infinite ground flag.

      Returns
      -------
      bool
          Include infinite ground flag.



   .. py:property:: include_inter_plane_coupling
      :type: bool


      Include inter-plane coupling flag.

      Returns
      -------
      bool
          Include inter-plane coupling flag.



   .. py:property:: include_split_plane_coupling
      :type: bool


      Include split plane coupling flag.

      Returns
      -------
      bool
          Include split plane coupling flag.



   .. py:property:: include_trace_plane_coupling
      :type: bool


      Include trace-plane coupling flag.

      Returns
      -------
      bool
          Include trace-plane coupling flag.



   .. py:property:: include_vi_sources
      :type: bool


      Include VI sources flag.

      Returns
      -------
      bool
          Include VI sources flag.



   .. py:property:: inf_gnd_location
      :type: float


      Infinite ground location.

      Returns
      -------
      float
          Infinite ground location.



   .. py:property:: max_coupled_lines
      :type: int


      Maximum coupled lines.

      Returns
      -------
      int
          Maximum coupled lines.



   .. py:property:: mesh_automatic
      :type: bool


      Automatic mesh flag.

      Returns
      -------
      bool
          Automatic mesh flag.



   .. py:property:: mesh_frequency
      :type: float


      Mesh frequency.

      Returns
      -------
      float
          Mesh frequency.



   .. py:property:: min_pad_area_to_mesh
      :type: float


      Minimum pad area to mesh.

      Returns
      -------
      float
          Minimum pad area to mesh.



   .. py:property:: min_plane_area_to_mesh
      :type: float


      Minimum plane area to mesh.

      Returns
      -------
      float
          Minimum plane area to mesh.



   .. py:property:: min_void_area
      :type: str


      Minimum void area.

      Returns
      -------
      float
          Minimum void area.



   .. py:property:: perform_erc
      :type: bool


      Perform ERC flag.

      Returns
      -------
      bool
          Perform ERC flag.



   .. py:property:: return_current_distribution
      :type: bool


      Return current distribution flag.

      Returns
      -------
      bool
          Return current distribution flag.



   .. py:property:: snap_length_threshold
      :type: float


      Snap length threshold.

      Returns
      -------
      float
          Snap length threshold.



