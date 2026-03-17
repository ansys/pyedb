src.pyedb.grpc.database.simulation_setup.q3d_acrl_settings
==========================================================

.. py:module:: src.pyedb.grpc.database.simulation_setup.q3d_acrl_settings


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.simulation_setup.q3d_acrl_settings.Q3DACRLSettings


Module Contents
---------------

.. py:class:: Q3DACRLSettings(pedb, core: ansys.edb.core.simulation_setup.q3d_simulation_settings.Q3DACRLSettings)

   Q3D ACRL settings class.


   .. py:attribute:: core


   .. py:property:: max_passes
      :type: int


      Maximum number of mesh refinement cycles to perform.

      Returns
      -------
      int
          Maximum number of passes.



   .. py:property:: max_refine_per_pass
      :type: float


      Maximum percentage of elements to refine per pass.

      Returns
      -------
      float
          Maximum percentage of elements to refine per pass.



   .. py:property:: min_converged_passes
      :type: int


      Minimum number of converged passes required.

      Returns
      -------
      int
          Minimum number of converged passes.



   .. py:property:: min_passes
      :type: int


      Minimum number of passes required.

      Returns
      -------
      int
          Minimum number of passes.



   .. py:property:: percent_error
      :type: float


      Target percent error for convergence.

      Returns
      -------
      float
          Target percent error.



