src.pyedb.grpc.database.simulation_setup.hfss_pi_simulation_settings
====================================================================

.. py:module:: src.pyedb.grpc.database.simulation_setup.hfss_pi_simulation_settings


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.simulation_setup.hfss_pi_simulation_settings.HFSSPISimulationSettings


Module Contents
---------------

.. py:class:: HFSSPISimulationSettings(pedb, core: ansys.edb.core.simulation_setup.hfss_pi_simulation_settings.HFSSPISimulationSettings)

   PyEDB HFSS PI simulation setup class.


   .. py:attribute:: core


   .. py:property:: advanced
      :type: pyedb.grpc.database.simulation_setup.hfss_pi_advanced_settings.HFSSPIAdvancedSettings


      Get the HFSS PI advanced simulation settings.

      Returns
      -------
      HFSSPIAdvancedSettings
          The HFSS PI advanced simulation settings object.




   .. py:property:: enabled
      :type: bool


      Get or set the enabled status of the HFSS PI simulation setup.

      Returns
      -------
      bool
          True if the simulation setup is enabled, False otherwise.




   .. py:property:: general
      :type: pyedb.grpc.database.simulation_setup.hfss_pi_general_settings.HFSSPIGeneralSettings


      Get the HFSS PI general simulation settings.

      Returns
      -------
      HFSSPIGeneralSettings
          The HFSS PI general simulation settings object.




   .. py:property:: solver

      Get the HFSS PI solver simulation settings.

      Returns
      -------
      HFSSPISolverSettings
          The HFSS PI solver simulation settings object.




