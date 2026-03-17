src.pyedb.grpc.database.simulation_setup.siwave_dcir_simulation_setup
=====================================================================

.. py:module:: src.pyedb.grpc.database.simulation_setup.siwave_dcir_simulation_setup


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.simulation_setup.siwave_dcir_simulation_setup.SIWaveDCIRSimulationSetup


Module Contents
---------------

.. py:class:: SIWaveDCIRSimulationSetup(pedb, core: ansys.edb.core.simulation_setup.siwave_dcir_simulation_setup.SIWaveDCIRSimulationSetup)

   Bases: :py:obj:`pyedb.grpc.database.simulation_setup.simulation_setup.SimulationSetup`


   Siwave Dcir simulation setup class.


   .. py:attribute:: core


   .. py:method:: create(edb: pyedb.Edb, name: str = 'Siwave_DCIR')
      :classmethod:


      Create a SIWave DCIR simulation setup.

      Parameters
      ----------
      edb : Edb object
          An EDB instance.

      name : str
          Name of the simulation setup.

      Returns
      -------
      SIWaveDCIRSimulationSetup
          The SIWave DCIR simulation setup object.




   .. py:property:: dc_ir_settings

      SIWave DCIR simulation settings.

      ... deprecated:: 0.77.3
      Use :attr:`settings.dc
      <pyedb.grpc.database.simulation_setup.siwave_dcir_simulation_setup.SIWaveDCIRSimulationSetup.settings.dc>`
      instead.




   .. py:property:: settings
      :type: pyedb.grpc.database.simulation_setup.siwave_dcir_settings.SIWaveDCIRSettings


      SIWave DCIR simulation settings.

      Returns
      -------
      SIWaveSimulationSettings
          The SIWave DCIR simulation settings object.




   .. py:property:: dc_settings
      :type: pyedb.grpc.database.simulation_setup.siwave_dcir_settings.SIWaveDCIRSettings


      SIWave DCIR simulation settings.

      Returns
      -------
      SIWaveDCIRSettings
          The SIWave DCIR simulation settings object.




