src.pyedb.grpc.database.simulation_setup.hfss_pi_solver_settings
================================================================

.. py:module:: src.pyedb.grpc.database.simulation_setup.hfss_pi_solver_settings


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.simulation_setup.hfss_pi_solver_settings.HFSSPISolverSettings


Module Contents
---------------

.. py:class:: HFSSPISolverSettings(pedb, core: ansys.edb.core.simulation_setup.hfss_pi_simulation_settings.HFSSPISolverSettings)

   HFSS PI solver settings class.


   .. py:attribute:: core


   .. py:property:: enhanced_low_frequency_accuracy
      :type: bool


      Flag indicating if enhanced low-frequency accuracy is enabled during simulation.

      Returns
      -------
      bool
          Enhanced low frequency accuracy setting value.



   .. py:property:: via_area_cutoff_circ_elems
      :type: float


      Pwr/Gnd vias with an area smaller than this value are simplified during simulation.

      Returns
      -------
      str
          Via area cutoff circular elements setting value.



