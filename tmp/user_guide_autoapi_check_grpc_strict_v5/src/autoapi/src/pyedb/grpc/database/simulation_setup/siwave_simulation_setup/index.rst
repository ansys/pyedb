src.pyedb.grpc.database.simulation_setup.siwave_simulation_setup
================================================================

.. py:module:: src.pyedb.grpc.database.simulation_setup.siwave_simulation_setup


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.simulation_setup.siwave_simulation_setup.SiwaveSimulationSetup


Module Contents
---------------

.. py:class:: SiwaveSimulationSetup(pedb, core: ansys.edb.core.simulation_setup.siwave_simulation_setup.SIWaveSimulationSetup)

   Bases: :py:obj:`pyedb.grpc.database.simulation_setup.simulation_setup.SimulationSetup`


   SIwave simulation setup class.


   .. py:attribute:: core
      :type:  ansys.edb.core.simulation_setup.siwave_simulation_setup.SIWaveSimulationSetup


   .. py:method:: create(edb: pyedb.grpc.edb.Edb, name: str = 'siwave_setup') -> SiwaveSimulationSetup
      :classmethod:


      Create a SIWave simulation setup object.

      Parameters
      ----------
      edb : :class:`Edb`
          Inherited object.

      name : str, optional
          Name of the simulation setup. The default is "siwave_setup".

      Returns
      -------
      SiwaveSimulationSetup
          The SIWave simulation setup object.



   .. py:property:: settings
      :type: pyedb.grpc.database.simulation_setup.siwave_simulation_settings.SIWaveSimulationSettings


      Setup simulation settings.



   .. py:property:: advanced_settings
      :type: pyedb.grpc.database.simulation_setup.siwave_advanced_settings.SIWaveAdvancedSettings


      Setup advanced settings.



   .. py:property:: dc_settings
      :type: pyedb.grpc.database.simulation_setup.siwave_dc_settings.SIWaveDCSettings


      Setup dc settings.

      .. deprecated:: 0.70.0
      Use :attr:`dc_advanced_settings is deprecated. Use :attr:`settings.dc instead.




   .. py:property:: dc_advanced_settings
      :type: pyedb.grpc.database.simulation_setup.siwave_dc_advanced.SIWaveDCAdvancedSettings


      Setup dc settings.

      .. deprecated:: 0.70.0
      Use :attr:`dc_advanced_settings is deprecated. Use :attr:`settings.dc_advanced instead.




   .. py:property:: use_si_settings
      :type: bool


      Whether to use SI settings.

      .. deprecated:: 0.70.0
      Use :attr:`settings.use_si_settings is deprecated. Use :attr:`settings.general.use_si_settings` instead.




   .. py:property:: si_slider_position
      :type: int


      SI slider position.

      .. deprecated:: 0.70.0
      Use :attr:`settings.si_slider_position is deprecated. Use :attr:`settings.general.si_slider_position` instead.



   .. py:property:: pi_slider_position
      :type: int


      I slider position.

      .. deprecated:: 0.70.0
      Use :attr:`settings.pi_slider_position is deprecated. Use :attr:`settings.general.pi_slider_position` instead.



