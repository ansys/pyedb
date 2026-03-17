src.pyedb.dotnet.database.sim_setup_data.data.sweep_data
========================================================

.. py:module:: src.pyedb.dotnet.database.sim_setup_data.data.sweep_data


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.sim_setup_data.data.sweep_data.SweepData


Module Contents
---------------

.. py:class:: SweepData(pedb, edb_object=None, name: str = None, sim_setup=None)

   Bases: :py:obj:`object`


   Manages EDB methods for a frequency sweep.

   Parameters
   ----------
   sim_setup : :class:`pyedb.dotnet.database.edb_data.siwave_simulation_setup_data.SiwaveSYZSimulationSetup`
   name : str, optional
       Name of the frequency sweep.
   edb_object : :class:`Ansys.Ansoft.Edb.Utility.SIWDCIRSimulationSettings`, optional
       EDB object. The default is ``None``.


   .. py:attribute:: sim_setup
      :value: None



   .. py:property:: name

      Name of the sweep.



   .. py:property:: frequencies

      List of frequency points.



   .. py:property:: adaptive_sampling

      Flag indicating if adaptive sampling is turned on.

      Returns
      -------
      bool
          ``True`` if adaptive sampling is used, ``False`` otherwise.



   .. py:property:: adv_dc_extrapolation

      Flag indicating if advanced DC extrapolation is turned on.

      Returns
      -------
      bool
          ``True`` if advanced DC Extrapolation is used, ``False`` otherwise.



   .. py:property:: compute_dc_point

      Flag indicating if computing the exact DC point is turned on.



   .. py:property:: auto_s_mat_only_solve

      Flag indicating if Auto SMatrix only solve is turned on.



   .. py:property:: enforce_causality

      Flag indicating if causality is enforced.

      Returns
      -------
      bool
          ``True`` if enforce causality is used, ``False`` otherwise.



   .. py:property:: enforce_dc_and_causality

      Flag indicating if DC point and causality are enforced.

      Returns
      -------
      bool
          ``True`` if enforce dc point and causality is used, ``False`` otherwise.



   .. py:property:: enforce_passivity

      Flag indicating if passivity is enforced.

      Returns
      -------
      bool
          ``True`` if enforce passivity is used, ``False`` otherwise.



   .. py:property:: freq_sweep_type

      Sweep type.

      Options are:
      - ``"kInterpolatingSweep"``
      - ``"kDiscreteSweep"``
      - ``"kBroadbandFastSweep"``

      Returns
      -------
      str
          Sweep type.



   .. py:property:: type

      Sweep type.



   .. py:property:: interpolation_use_full_basis

      Flag indicating if full-basis elements is used.

      Returns
      -------
      bool
          ``True`` if full basis interpolation is used, ``False`` otherwise.



   .. py:property:: interpolation_use_port_impedance

      Flag indicating if port impedance interpolation is turned on.

      Returns
      -------
      bool
          ``True`` if port impedance is used, ``False`` otherwise.



   .. py:property:: interpolation_use_prop_const

      Flag indicating if propagation constants are used.

      Returns
      -------
      bool
          ``True`` if propagation constants are used, ``False`` otherwise.



   .. py:property:: interpolation_use_s_matrix

      Flag indicating if the S matrix is used.

      Returns
      -------
      bool
          ``True`` if S matrix are used, ``False`` otherwise.



   .. py:property:: max_solutions

      Number of maximum solutions.

      Returns
      -------
      int



   .. py:property:: min_freq_s_mat_only_solve

      Minimum frequency SMatrix only solve.

      Returns
      -------
      str
          Frequency with units.



   .. py:property:: min_solved_freq

      Minimum solved frequency with units.

      Returns
      -------
      str
          Frequency with units.



   .. py:property:: passivity_tolerance

      Tolerance for passivity enforcement.

      Returns
      -------
      float



   .. py:property:: relative_s_error

      S-parameter error tolerance.

      Returns
      -------
      float



   .. py:property:: save_fields

      Flag indicating if the extraction of surface current data is turned on.

      Returns
      -------
      bool
          ``True`` if save fields is enabled, ``False`` otherwise.



   .. py:property:: save_rad_fields_only

      Flag indicating if the saving of only radiated fields is turned on.

      Returns
      -------
      bool
          ``True`` if save radiated field only is used, ``False`` otherwise.



   .. py:property:: use_q3d_for_dc

      Flag indicating if the Q3D solver is used for DC point extraction.

      Returns
      -------
      bool
          ``True`` if Q3d for DC point is used, ``False`` otherwise.



   .. py:method:: set_frequencies_linear_scale(start='0.1GHz', stop='20GHz', step='50MHz')

      Set a linear scale frequency sweep.

      Parameters
      ----------
      start : str, float, optional
          Start frequency. The default is ``"0.1GHz"``.
      stop : str, float, optional
          Stop frequency. The default is ``"20GHz"``.
      step : str, float, optional
          Step frequency. The default is ``"50MHz"``.

      Returns
      -------
      bool
          ``True`` if correctly executed, ``False`` otherwise.



   .. py:method:: set_frequencies_linear_count(start='1kHz', stop='0.1GHz', count=10)

      Set a linear count frequency sweep.

      Parameters
      ----------
      start : str, float, optional
          Start frequency. The default is ``"1kHz"``.
      stop : str, float, optional
          Stop frequency. The default is ``"0.1GHz"``.
      count : int, optional
          Step frequency. The default is ``10``.

      Returns
      -------
      bool
          ``True`` if correctly executed, ``False`` otherwise.



   .. py:method:: set_frequencies_log_scale(start='1kHz', stop='0.1GHz', samples=10)

      Set a log-count frequency sweep.

      Parameters
      ----------
      start : str, float, optional
          Start frequency. The default is ``"1kHz"``.
      stop : str, float, optional
          Stop frequency. The default is ``"0.1GHz"``.
      samples : int, optional
          Step frequency. The default is ``10``.

      Returns
      -------
      bool
          ``True`` if correctly executed, ``False`` otherwise.



   .. py:method:: set_frequencies(frequency_list=None, update=True)

      Set frequency list to the sweep frequencies.

      Parameters
      ----------
      frequency_list : list, optional
           List of lists with four elements. The default is ``None``. If provided, each list must contain:
            1 - frequency type (``"linear count"``, ``"log scale"``, or ``"linear scale"``)
            2 - start frequency
            3 - stop frequency
            4 - step frequency or count
      Returns
      -------
      bool
          ``True`` if correctly executed, ``False`` otherwise.



   .. py:method:: add(sweep_type, start, stop, increment)


   .. py:property:: frequency_string

      A string describing the frequency sweep. Below is an example.
      ['LIN 0GHz 20GHz 0.05GHz', 'LINC 20GHz 30GHz 10', 'DEC 40GHz 50GHz 10']



   .. py:method:: add_frequencies(frequencies)


   .. py:method:: clear()


   .. py:property:: use_hfss_solver_regions


   .. py:property:: hfss_solver_region_setup_name


   .. py:property:: hfss_solver_region_sweep_name


