src.pyedb.grpc.database.simulation_setup.adaptive_frequency
===========================================================

.. py:module:: src.pyedb.grpc.database.simulation_setup.adaptive_frequency


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.simulation_setup.adaptive_frequency.AdaptiveFrequency


Module Contents
---------------

.. py:class:: AdaptiveFrequency(core: ansys.edb.core.simulation_setup.adaptive_solutions.AdaptiveFrequency)

   PyEDB Adaptive Frequency class.


   .. py:attribute:: core


   .. py:property:: adaptive_frequency
      :type: float


      Get the adaptive frequency value.

      Returns
      -------
      float
          Adaptive frequency value.



   .. py:property:: max_delta

      Get the maximum delta value.

      Returns
      -------
      float
          Maximum delta value.



   .. py:property:: output_variables
      :type: dict[str, str]


      Map of output variable names to maximum delta S.



   .. py:method:: add_output_variable(variable_name: str, max_delta_s: float)

      Add an output variable with its maximum delta S.

      Parameters
      ----------
      variable_name : str
          Name of the output variable.
      max_delta_s : float
          Maximum delta S for the output variable.



