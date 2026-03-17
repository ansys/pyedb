src.pyedb.grpc.database.simulation_setup.q3d_simulation_setup
=============================================================

.. py:module:: src.pyedb.grpc.database.simulation_setup.q3d_simulation_setup


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.simulation_setup.q3d_simulation_setup.Q3DSimulationSetup


Module Contents
---------------

.. py:class:: Q3DSimulationSetup(pedb, core: GrpcQ3DSimulationSetup)

   Bases: :py:obj:`pyedb.grpc.database.simulation_setup.simulation_setup.SimulationSetup`


   Q3D simulation setup management.

   Parameters
   ----------
   pedb : :class:`Edb`
       Inherited object.


   .. py:attribute:: core
      :type:  ansys.edb.core.simulation_setup.q3d_simulation_setup.Q3DSimulationSetup


   .. py:method:: create(edb: pyedb.grpc.edb.Edb, name: str = 'Q3D_setup') -> Q3DSimulationSetup
      :classmethod:


      Create a Q3D simulation setup.

      Parameters
      ----------
      edb : Edb
          Inherited object.

      name : str, optional
          Name of the simulation setup, by default "Q3D_setup".

      Returns
      -------
      Q3DSimulationSetup
          The Q3D simulation setup object.



   .. py:property:: settings
      :type: pyedb.grpc.database.simulation_setup.q3d_simulation_settings.Q3DSimulationSettings


      Q3D simulation settings.

      Returns
      -------
      Q3DSimulationSettings
          The Q3D simulation settings object.



