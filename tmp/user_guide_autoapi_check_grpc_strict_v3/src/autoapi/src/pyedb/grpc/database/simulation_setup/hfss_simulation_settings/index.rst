src.pyedb.grpc.database.simulation_setup.hfss_simulation_settings
=================================================================

.. py:module:: src.pyedb.grpc.database.simulation_setup.hfss_simulation_settings


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.simulation_setup.hfss_simulation_settings.HFSSSimulationSettings


Module Contents
---------------

.. py:class:: HFSSSimulationSettings(parent)

   PyEDB-core HFSS simulation settings class.


   .. py:attribute:: core


   .. py:property:: advanced
      :type: pyedb.grpc.database.simulation_setup.hfss_advanced_settings.HFSSAdvancedSettings


      HFSS Advanced settings class.


      Returns
      -------
      :class:`HFSSAdvancedSettings <pyedb.grpc.database.simulation_setup.hfss_advanced_settings.HFSSAdvancedSettings>`




   .. py:property:: advanced_meshing
      :type: pyedb.grpc.database.simulation_setup.hfss_advanced_meshing_settings.HFSSAdvancedMeshingSettings


      Advanced meshing class.

      Returns
      -------
      :class:`HFSSAdvancedMeshingSettings <pyedb.grpc.database.simulation_setup.
      hfss_advanced_meshing_settings.HFSSAdvancedMeshingSettings>`




   .. py:property:: dcr
      :type: pyedb.grpc.database.simulation_setup.hfss_dcr_settings.HFSSDCRSettings


      Dcr.

      Returns
      -------
      :class:`HFSSDCRSettings <pyedb.grpc.database.simulation_setup.hfss_dcr_settings.HFSSDCRSettings>`




   .. py:property:: general
      :type: pyedb.grpc.database.simulation_setup.hfss_general_settings.HFSSGeneralSettings


      General settings class.

      Returns
      -------
      :class:`HFSSGeneralSettings <pyedb.grpc.database.simulation_setup.hfss_general_settings.HFSSGeneralSettings>`




   .. py:property:: options
      :type: pyedb.grpc.database.simulation_setup.hfss_settings_options.HFSSSettingsOptions


      HFSS option class.

      Returns
      -------
      :class:`HFSSSettingsOptions <pyedb.grpc.database.simulation_setup.hfss_settings_options.HFSSSettingsOptions>`




   .. py:property:: solver
      :type: pyedb.grpc.database.simulation_setup.hfss_solver_settings.HFSSSolverSettings


      HFSS solver settings class.

      Returns
      -------
      :class:`HFSSSolverSettings <pyedb.grpc.database.simulation_setup.hfss_solver_settings.HFSSSolverSettings>`




   .. py:property:: enhanced_low_frequency_accuracy
      :type: bool


      Enhanced low frequency accuracy flag.

      .. deprecated:: 0.67.0
          This property is deprecated. Please use :attr:`options.enhanced_low_frequency_accuracy`
          instead.
          This attribute was added for dotnet compatibility and will be removed in future releases.



   .. py:property:: relative_residual
      :type: float


      Relative residual value.

      .. deprecated:: 0.67.0
          This property is deprecated. Please use :attr:`options.relative_residual`
          instead.
          This attribute was added for dotnet compatibility and will be removed in future releases.



   .. py:property:: use_shell_elements
      :type: bool


      Use shell elements flag.

      .. deprecated:: 0.67.0
          This property is deprecated. Please use :attr:`options.use_shell_elements`
          instead.
          This attribute was added for dotnet compatibility and will be removed in future releases.



