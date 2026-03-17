src.pyedb.grpc.database.simulation_setup.siwave_s_parameter_settings
====================================================================

.. py:module:: src.pyedb.grpc.database.simulation_setup.siwave_s_parameter_settings


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.simulation_setup.siwave_s_parameter_settings.SIWaveSParameterSettings


Module Contents
---------------

.. py:class:: SIWaveSParameterSettings(pedb, core: ansys.edb.core.simulation_setup.siwave_simulation_settings.SIWaveSParameterSettings)

   SIWave S-Parameter simulation settings class.


   .. py:attribute:: core


   .. py:property:: dc_behavior
      :type: str


      Get or set the DC behavior for S-Parameter simulation.

      Returns
      -------
      str
          The DC behavior as a string.



   .. py:property:: extrapolation
      :type: str


      Get or set the S-Parameter extrapolation method.

      Returns
      -------
      str
          The S-Parameter extrapolation method as a string.



   .. py:property:: interpolation
      :type: str


      Get or set the S-Parameter interpolation method.

      Returns
      -------
      str
          The S-Parameter interpolation method as a string.



   .. py:property:: use_state_space
      :type: bool


      Get or set whether to use state space representation.

      Returns
      -------
      bool
          True if state space representation is used, False otherwise.



