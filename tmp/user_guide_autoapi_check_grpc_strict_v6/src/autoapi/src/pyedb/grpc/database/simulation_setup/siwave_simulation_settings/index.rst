src.pyedb.grpc.database.simulation_setup.siwave_simulation_settings
===================================================================

.. py:module:: src.pyedb.grpc.database.simulation_setup.siwave_simulation_settings


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.simulation_setup.siwave_simulation_settings.SIWaveSimulationSettings


Module Contents
---------------

.. py:class:: SIWaveSimulationSettings(pedb, core: ansys.edb.core.simulation_setup.siwave_simulation_settings.SIWaveSimulationSettings)

   .. py:attribute:: core


   .. py:property:: advanced
      :type: pyedb.grpc.database.simulation_setup.siwave_advanced_settings.SIWaveAdvancedSettings


      Advanced settings class.

      Returns
      -------
      :class:`SIWaveAdvancedSettings <pyedb.grpc.database.simulation_setup.
      siwave_advanced_settings.SIWaveAdvancedSettings>`




   .. py:property:: dc
      :type: pyedb.grpc.database.simulation_setup.siwave_dc_settings.SIWaveDCSettings


      DC settings class.

      Returns
      -------
      :class:`SIWaveDCSettings <pyedb.grpc.database.simulation_setup.
      siwave_dc_settings.SIWaveDCSettings>`




   .. py:property:: dc_advanced
      :type: pyedb.grpc.database.simulation_setup.siwave_dc_advanced.SIWaveDCAdvancedSettings


      DC advanced settings class.

      Returns
      -------
      :class:`SIWaveDCAdvancedSettings <pyedb.grpc.database.simulation_setup.
      siwave_dc_advanced.SIWaveDCAdvancedSettings>`




   .. py:property:: enabled
      :type: bool


      Enabled status of the SIWave simulation.

      Returns
      -------
      bool
          True if enabled, False otherwise.




   .. py:property:: general
      :type: pyedb.grpc.database.simulation_setup.siwave_general_settings.SIWaveGeneralSettings


      General settings class.

      Returns
      -------
      :class:`SIWaveGeneralSettings <pyedb.grpc.database.simulation_setup.
      siwave_general_settings.SIWaveGeneralSettings>`




   .. py:property:: s_parameter
      :type: pyedb.grpc.database.simulation_setup.siwave_s_parameter_settings.SIWaveSParameterSettings


      S-Parameter settings class.

      Returns
      -------
      :class:`SIWaveSParameterSettings <pyedb.grpc.database.simulation_setup.
      siwave_s_parameter_settings.SIWaveSParameterSettings>`




