src.pyedb.grpc.database.simulation_setup.hfss_advanced_meshing_settings
=======================================================================

.. py:module:: src.pyedb.grpc.database.simulation_setup.hfss_advanced_meshing_settings


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.simulation_setup.hfss_advanced_meshing_settings.HFSSAdvancedMeshingSettings


Module Contents
---------------

.. py:class:: HFSSAdvancedMeshingSettings(parent)

   .. py:attribute:: core


   .. py:property:: arc_step_size
      :type: str


      Get or set the arc step size.

      Returns
      -------
      float
          Arc step size.



   .. py:property:: arc_to_chord_error
      :type: str


      Get or set the arc to chord error.

      Returns
      -------
      float
          Arc to chord error.



   .. py:property:: circle_start_azimuth
      :type: str


      Get or set the circle start azimuth.

      Returns
      -------
      float
          Circle start azimuth.



   .. py:property:: layer_snap_tol
      :type: str


      Get or set the layer snap tolerance.

      Returns
      -------
      str
          Layer snap tolerance.



   .. py:property:: max_arc_points
      :type: int


      Get or set the maximum number of arc points.

      .. deprecated:: 0.77.3
          Use :attr:`max_num_arc_points` instead.



   .. py:property:: max_num_arc_points
      :type: int


      Get or set the maximum number of arc points.

      Returns
      -------
      int
          Maximum number of arc points.



   .. py:property:: use_arc_chord_error_approx
      :type: bool


      Get or set whether to use arc chord error approximation.

      Returns
      -------
      bool
          True if using arc chord error approximation, False otherwise.



