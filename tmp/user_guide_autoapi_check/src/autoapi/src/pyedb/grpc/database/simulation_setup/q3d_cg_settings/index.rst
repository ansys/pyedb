src.pyedb.grpc.database.simulation_setup.q3d_cg_settings
========================================================

.. py:module:: src.pyedb.grpc.database.simulation_setup.q3d_cg_settings


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.simulation_setup.q3d_cg_settings.Q3DCGSettings


Module Contents
---------------

.. py:class:: Q3DCGSettings(pedb, core: ansys.edb.core.simulation_setup.q3d_simulation_settings.Q3DCGSettings)

   Q3D CG settings class.


   .. py:attribute:: core


   .. py:property:: auto_incr_sol_order
      :type: bool


      Get auto increment solution order setting.

      Returns
      -------
      bool
          Auto increment solution order setting.



   .. py:property:: compression_tol
      :type: float


      Get compression tolerance.

      Returns
      -------
      float
          Compression tolerance.



   .. py:property:: max_passes
      :type: int


      Maximum number of passes.

      Returns
      -------
      int
          Maximum number of passes.



   .. py:property:: max_refine_per_pass
      :type: float


      Maximum refinement per pass.

      Returns
      -------
      float
          Maximum refinement per pass.



   .. py:property:: min_converged_passes
      :type: int


      Minimum number of converged passes.

      Returns
      -------
      int
          Minimum number of converged passes.



   .. py:property:: min_passes
      :type: int


      Minimum number of passes.
      Returns



   .. py:property:: percent_error
      :type: float


      Percent error during conduction adaptive passes.

      Returns
      -------
      float
          Percent error during conduction adaptive passes.



   .. py:property:: solution_order
      :type: str


      Get solution order.

      Returns
      -------
      str
          Solution order.



   .. py:property:: solver_type
      :type: str


      Get solver type.

      Returns
      -------
      str
          Solver type.



