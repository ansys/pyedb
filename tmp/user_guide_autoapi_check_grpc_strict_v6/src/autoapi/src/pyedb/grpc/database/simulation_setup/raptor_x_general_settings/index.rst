src.pyedb.grpc.database.simulation_setup.raptor_x_general_settings
==================================================================

.. py:module:: src.pyedb.grpc.database.simulation_setup.raptor_x_general_settings


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.simulation_setup.raptor_x_general_settings.RaptorXGeneralSettings


Module Contents
---------------

.. py:class:: RaptorXGeneralSettings(pedb, core: ansys.edb.core.simulation_setup.raptor_x_simulation_settings.RaptorXGeneralSettings)

   Raptor X general settings class.


   .. py:attribute:: core


   .. py:property:: global_temperature
      :type: float


      Simulation temperature in degrees Celsius.

      Returns
      -------
      float
          Global temperature in Kelvin.



   .. py:property:: max_frequency
      :type: float


      Maximum frequency for the simulation in Hz.

      Returns
      -------
      float
          Maximum frequency in Hz.



   .. py:property:: netlist_export_spectre
      :type: bool


      Flag indicating if the netlist is exported in Spectre format.



   .. py:property:: save_netlist
      :type: bool


      Flag indicating if the netlist is saved.



   .. py:property:: save_rfm
      :type: bool


      Flag indicating if the RFM file is saved.



   .. py:property:: use_gold_em_solver
      :type: bool


      Flag indicating if the Gold EM solver is used.



