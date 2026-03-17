src.pyedb.grpc.database.simulation_setup.q3d_simulation_settings
================================================================

.. py:module:: src.pyedb.grpc.database.simulation_setup.q3d_simulation_settings


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.simulation_setup.q3d_simulation_settings.Q3DSimulationSettings


Module Contents
---------------

.. py:class:: Q3DSimulationSettings(pedb, core: ansys.edb.core.simulation_setup.q3d_simulation_settings.Q3DSimulationSettings)

   Q3D simulation settings class.


   .. py:attribute:: core


   .. py:property:: acrl
      :type: pyedb.grpc.database.simulation_setup.q3d_acrl_settings.Q3DACRLSettings


      ACRL settings class.

      Returns
      -------
      :class:`Q3DACRLSettings <pyedb.grpc.database.simulation_setup.
      q3d_acrl_settings.Q3DACRLSettings>`




   .. py:property:: advanced
      :type: pyedb.grpc.database.simulation_setup.q3d_advanced_settings.Q3DAdvancedSettings


      Advanced settings class.

      Returns
      -------
      :class:`Q3DAdvancedSettings <pyedb.grpc.database.simulation_setup.
      q3d_advanced_settings.Q3DAdvancedSettings>`




   .. py:property:: advanced_meshing
      :type: pyedb.grpc.database.simulation_setup.q3d_advanced_meshing_settings.Q3DAdvancedMeshingSettings


      Advanced meshing settings class.

      Returns
      -------
      :class:`Q3DAdvancedMeshingSettings <pyedb.grpc.database.simulation_setup.
      q3d_advanced_meshing_settings.Q3DAdvancedMeshingSettings>`



   .. py:property:: cg
      :type: pyedb.grpc.database.simulation_setup.q3d_cg_settings.Q3DCGSettings


      CG settings class.

      Returns
      -------
      :class:`Q3DCGSettings <pyedb.grpc.database.simulation_setup.
      q3d_cg_settings.Q3DCGSettings>`




   .. py:property:: dcrl
      :type: pyedb.grpc.database.simulation_setup.q3d_dcrl_settings.Q3DDCRLSettings


      DCRL settings class.

      Returns
      -------
      :class:`Q3DDCRLSettings <pyedb.grpc.database.simulation_setup.
      q3d_dcrl_settings.Q3DDCRLSettings>`




   .. py:property:: enabled
      :type: bool


      Enabled flag.

      Returns
      -------
      bool
          Enabled flag.




   .. py:property:: general
      :type: pyedb.grpc.database.simulation_setup.q3d_general_settings.Q3DGeneralSettings


      General settings class.

      Returns
      -------
      :class:`Q3DGeneralSettings <pyedb.grpc.database.simulation_setup.
      q3d_general_settings.Q3DGeneralSettings>`




