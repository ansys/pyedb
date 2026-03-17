src.pyedb.dotnet.database.sim_setup_data.data.adaptive_frequency_data
=====================================================================

.. py:module:: src.pyedb.dotnet.database.sim_setup_data.data.adaptive_frequency_data


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.sim_setup_data.data.adaptive_frequency_data.AdaptiveFrequencyData


Module Contents
---------------

.. py:class:: AdaptiveFrequencyData(adaptive_frequency_data)

   Bases: :py:obj:`object`


   Manages EDB methods for adaptive frequency data.


   .. py:property:: adaptive_frequency

      Adaptive frequency for the setup.

      Returns
      -------
      str
          Frequency with units.



   .. py:property:: max_delta

      Maximum change of S-parameters between two consecutive passes, which serves as
      a stopping criterion.

      Returns
      -------
      str



   .. py:property:: max_passes

      Maximum allowed number of mesh refinement cycles.

      Returns
      -------
      int



