src.pyedb.grpc.database.simulation_setup.simulation_setup
=========================================================

.. py:module:: src.pyedb.grpc.database.simulation_setup.simulation_setup


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.simulation_setup.simulation_setup.SimulationSetupDeprecated
   src.pyedb.grpc.database.simulation_setup.simulation_setup.SimulationSetup


Module Contents
---------------

.. py:class:: SimulationSetupDeprecated

   .. py:property:: type


   .. py:property:: sweeps


   .. py:property:: frequency_sweeps


.. py:class:: SimulationSetup(pedb, core: ansys.edb.core.simulation_setup.simulation_setup.SimulationSetup)

   Bases: :py:obj:`SimulationSetupDeprecated`


   .. py:attribute:: core


   .. py:method:: cast()

      Cast a core SimulationSetup to PyEDB SimulationSetup.



   .. py:property:: id
      :type: int


      Unique ID of the EDB object.

      Returns
      -------
      int
          Simulation setup ID.



   .. py:property:: is_null
      :type: bool


      Check if the simulation setup is null.

      Returns
      -------
      bool
          True if the simulation setup is null, False otherwise.



   .. py:property:: name
      :type: str


      Get or set the name of the simulation setup.

      Returns
      -------
      str
          Simulation setup name.



   .. py:property:: position
      :type: int


      Get or set the position of the simulation setup.

      Returns
      -------
      int
          Simulation setup position.



   .. py:property:: sweep_data
      :type: list[pyedb.grpc.database.simulation_setup.sweep_data.SweepData]


      Get the sweep data associated with the simulation setup.

      Returns
      -------
      list[SweepData]
          List of sweep data objects.



   .. py:method:: add_frequency_sweep(frequency_sweep: list[str])

      This method is deprecated. Please use 'add_sweep' with appropriate parameters instead.



   .. py:method:: add_sweep(name=None, distribution='linear', start_freq='0GHz', stop_freq='20GHz', step='10MHz', discrete=False, frequency_set=None) -> Union[pyedb.grpc.database.simulation_setup.sweep_data.SweepData, None]

      Add a HFSS frequency sweep.

      This method was refactored to reduce complexity. The behaviour is compatible
      with the previous implementation: it accepts either a legacy `frequency_set`
      or single-sweep parameters.

      Returns
      -------
      SweepData | None
          The newly added sweep when single sweep parameters are used, or None when
          `frequency_set` is provided (legacy multi-sweep behavior).



   .. py:method:: clear_sweeps()

      Clear all frequency sweeps from the simulation setup.



   .. py:property:: setup_type
      :type: str


      Get the type of the simulation setup.

      Returns
      -------
      str
          Simulation setup type.



