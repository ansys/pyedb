src.pyedb.grpc.database.simulation_setup.q3d_general_settings
=============================================================

.. py:module:: src.pyedb.grpc.database.simulation_setup.q3d_general_settings


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.simulation_setup.q3d_general_settings.Q3DGeneralSettings


Module Contents
---------------

.. py:class:: Q3DGeneralSettings(pedb, core: ansys.edb.core.simulation_setup.q3d_simulation_settings.Q3DGeneralSettings)

   .. py:attribute:: core


   .. py:property:: do_ac
      :type: bool


      Whether to perform AC analysis.

      Returns
      -------
      bool
          True if AC analysis is to be performed, False otherwise.



   .. py:property:: do_cg
      :type: bool


      Whether to perform CG analysis.

      Returns
      -------
      bool
          True if CG analysis is to be performed, False otherwise.



   .. py:property:: do_dc
      :type: bool


      Whether to perform DC analysis.

      Returns
      -------
      bool
          True if DC analysis is to be performed, False otherwise.



   .. py:property:: do_dc_res_only
      :type: bool


      Whether to perform DC resistance only analysis.

      Returns
      -------
      bool
          True if DC resistance only analysis is to be performed, False otherwise.



   .. py:property:: save_fields
      :type: bool


      Whether to save fields.

      Returns
      -------
      bool
          True if fields are to be saved, False otherwise.



   .. py:property:: solution_frequency
      :type: float


      Solution frequency in Hz.

      Returns
      -------
      float
          Solution frequency in Hz.



