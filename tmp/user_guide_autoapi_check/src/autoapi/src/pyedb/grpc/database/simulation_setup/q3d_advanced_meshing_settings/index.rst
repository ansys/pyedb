src.pyedb.grpc.database.simulation_setup.q3d_advanced_meshing_settings
======================================================================

.. py:module:: src.pyedb.grpc.database.simulation_setup.q3d_advanced_meshing_settings


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.simulation_setup.q3d_advanced_meshing_settings.Q3DAdvancedMeshingSettings


Module Contents
---------------

.. py:class:: Q3DAdvancedMeshingSettings(pedb, core: ansys.edb.core.simulation_setup.q3d_simulation_settings.Q3DAdvancedMeshingSettings)

   Q3D advanced meshing settings class.


   .. py:attribute:: core


   .. py:property:: arc_step_size
      :type: float


      Arc step size in micrometers.

      Returns
      -------
      float
          Arc step size in micrometers.



   .. py:property:: arc_to_chord_error
      :type: float


      Arc to chord error in micrometers.

      Returns
      -------
      float
          Arc to chord error in micrometers.



   .. py:property:: circle_start_azimuth
      :type: float


      Circle start azimuth in degrees.

      Returns
      -------
      float
          Circle start azimuth in degrees.



   .. py:property:: layer_alignment
      :type: str


      Snapping tolerance for hierarchical layer alignment.

      Returns
      -------
      float
          Snapping tolerance for hierarchical layer alignment.



   .. py:property:: max_num_arc_points
      :type: int


      Maximum number of points used to approximate arcs.

      Returns
      -------
      int
          Maximum number of arc points.



   .. py:property:: use_arc_chord_error_approx
      :type: bool


      Flag indicating if arc to chord error approximation is used.

      Returns
      -------
      bool
          True if arc to chord error approximation is used, False otherwise.



