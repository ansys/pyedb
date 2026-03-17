src.pyedb.grpc.database.simulation_setup.raptor_x_simulation_setup
==================================================================

.. py:module:: src.pyedb.grpc.database.simulation_setup.raptor_x_simulation_setup


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.simulation_setup.raptor_x_simulation_setup.RaptorXSimulationSetup


Module Contents
---------------

.. py:class:: RaptorXSimulationSetup(pedb, core: ansys.edb.core.simulation_setup.raptor_x_simulation_setup.RaptorXSimulationSetup)

   Bases: :py:obj:`pyedb.grpc.database.simulation_setup.simulation_setup.SimulationSetup`


   RaptorX simulation setup.


   .. py:attribute:: core


   .. py:method:: create(edb: pyedb.grpc.edb.Edb, name: str = 'RaptorX_Simulation_Setup')
      :classmethod:


      Create RaptorX simulation setup.

      Parameters
      ----------
      edb : PyEDB Edb object
          PyEDB Edb object.
      name : str
          Name of the simulation setup.

      Returns
      -------
      RaptorXSimulationSetup
          RaptorX simulation setup object.




   .. py:property:: settings
      :type: pyedb.grpc.database.simulation_setup.raptor_x_simulation_settings.RaptorXSimulationSettings


      RaptorX simulation settings.

      Returns
      -------
      RaptorXSimulationSettings
          RaptorX simulation settings object.




