src.pyedb.grpc.database.simulation_setup.siwave_dc_advanced
===========================================================

.. py:module:: src.pyedb.grpc.database.simulation_setup.siwave_dc_advanced


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.simulation_setup.siwave_dc_advanced.SIWaveDCAdvancedSettings


Module Contents
---------------

.. py:class:: SIWaveDCAdvancedSettings(pedb, core: ansys.edb.core.simulation_setup.siwave_simulation_settings.SIWaveDCAdvancedSettings)

   Siwave DC Advanced simulation settings class.


   .. py:attribute:: core


   .. py:property:: dc_min_plane_area_to_mesh
      :type: str


      Minimum plane area to mesh.

      Returns
      -------
      float
          Minimum plane area to mesh value.



   .. py:property:: dc_min_void_area_to_mesh
      :type: str


      Minimum void area to mesh.

      Returns
      -------
      str
          Minimum void area to mesh value.



   .. py:property:: energy_error
      :type: float


      Energy error.

      Returns
      -------
      float
          Energy error value.



   .. py:property:: max_init_mesh_edge_length
      :type: str


      Maximum initial mesh edge length.

      Returns
      -------
      str
          Maximum initial mesh edge length value.



   .. py:property:: max_num_passes
      :type: int


      Maximum number of passes.

      Returns
      -------
      int
          Maximum number of passes value.



   .. py:property:: max_passes
      :type: int


      Maximum number of passes for broadband adaptive solution.

      Returns
      -------
      int
          Maximum number of passes.




   .. py:property:: mesh_bws
      :type: bool


      Mesh BWS.

      Returns
      -------
      bool
          Mesh BWS value.



   .. py:property:: mesh_vias
      :type: bool


      Mesh vias.

      Returns
      -------
      bool
          Mesh vias value.



   .. py:property:: min_num_passes
      :type: int


      Minimum number of passes.

      Returns
      -------
      int
          Minimum number of passes value.



   .. py:property:: num_bw_sides
      :type: int


      Number of BWS sides.

      Returns
      -------
      int
          Number of BWS sides value.



   .. py:property:: num_via_sides
      :type: int


      Number of via sides.

      Returns
      -------
      int
          Number of via sides value.



   .. py:property:: percent_local_refinement
      :type: float


      Percentage of local refinement.

      Returns
      -------
      float
          Percentage of local refinement value.



   .. py:property:: perform_adaptive_refinement
      :type: bool


      Perform adaptive refinement.

      Returns
      -------
      bool
          Perform adaptive refinement value.



   .. py:property:: refine_bws
      :type: bool


      Refine BWS.

      Returns
      -------
      bool
          Refine BWS value.



   .. py:property:: refine_vias
      :type: bool


      Refine vias.

      Returns
      -------
      bool
          Refine vias value.



