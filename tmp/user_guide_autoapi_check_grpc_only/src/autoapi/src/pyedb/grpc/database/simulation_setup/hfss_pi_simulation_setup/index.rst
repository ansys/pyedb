src.pyedb.grpc.database.simulation_setup.hfss_pi_simulation_setup
=================================================================

.. py:module:: src.pyedb.grpc.database.simulation_setup.hfss_pi_simulation_setup


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.simulation_setup.hfss_pi_simulation_setup.HFSSPISimulationSetup


Module Contents
---------------

.. py:class:: HFSSPISimulationSetup(pedb, core: ansys.edb.core.simulation_setup.hfss_pi_simulation_setup.HFSSPISimulationSetup)

   Bases: :py:obj:`pyedb.grpc.database.simulation_setup.simulation_setup.SimulationSetup`


   HFSS PI simulation setup class.


   .. py:attribute:: core


   .. py:method:: create(edb: pyedb.grpc.edb.Edb, name: str = 'HFSS_PI') -> HFSSPISimulationSetup
      :classmethod:


      Create a HFSS PI simulation setup.

      Parameters
      ----------
      edb : Edb
          An EDB instance.

      name : str
          Name of the simulation setup.

      Returns
      -------
      HFSSPISimulationSetup
          The HFSS PI simulation setup object.




   .. py:property:: settings
      :type: pyedb.grpc.database.simulation_setup.hfss_pi_simulation_settings.HFSSPISimulationSettings


      Get the HFSS PI simulation settings.

      Returns
      -------
      HFSSPISimulationSettings
          The HFSS PI simulation settings object.




