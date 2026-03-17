src.pyedb.grpc.database.utility.sweep_data_distribution
=======================================================

.. py:module:: src.pyedb.grpc.database.utility.sweep_data_distribution


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.utility.sweep_data_distribution.SweepDataDistribution


Module Contents
---------------

.. py:class:: SweepDataDistribution

   .. py:method:: get_distribution(sweep_type='linear', start='0Ghz', stop='10GHz', step='10MHz', count=10, decade_number=6, octave_number=5) -> str
      :staticmethod:


      Return the Sweep data distribution.

      Parameters
      ----------
      sweep_type : str
          Sweep type. Supported values : `"linear"`, `"linear_count"`, `"exponential"`, `"decade_count"`,
          `"octave_count"`
      start : str, float
          Start frequency.
      stop : str, float
          Stop frequency
      step : str, float
          Step frequency
      count : int
          Count number
      decade_number : int
          Decade number
      octave_number : int
          Octave number

      Return
      ------
      str
          Sweep Data distribution.




