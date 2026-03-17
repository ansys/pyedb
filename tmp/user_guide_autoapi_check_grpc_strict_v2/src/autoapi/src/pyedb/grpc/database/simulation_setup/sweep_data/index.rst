src.pyedb.grpc.database.simulation_setup.sweep_data
===================================================

.. py:module:: src.pyedb.grpc.database.simulation_setup.sweep_data


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.simulation_setup.sweep_data.FrequencyData
   src.pyedb.grpc.database.simulation_setup.sweep_data.SweepData


Module Contents
---------------

.. py:class:: FrequencyData(core: ansys.edb.core.simulation_setup.simulation_setup.FrequencyData)

   .. py:property:: distribution
      :type: str


      Get the distribution type of the frequency data.

      Returns
      -------
      str
          Distribution type. Values are: "lin", "dec", "estp", "linc", "oct".



   .. py:property:: start_frequency
      :type: str


      Get the start frequency in Hz.

      Returns
      -------
      str
          Start frequency in Hz.



   .. py:property:: end_frequency
      :type: str


      Get the end frequency in Hz.

      Returns
      -------
      str
          End frequency in Hz.



   .. py:property:: step
      :type: str


      Get the frequency step in Hz.

      Returns
      -------
      str
          Frequency step in Hz.



.. py:class:: SweepData(pedb, name='sweep_data', distribution='lin', start_f=0.0, end_f=10000000000.0, step=10000000.0, core: GrpcSweepData = None, simsetup: SimulationSetup = None)

   Frequency sweep data class.
   PARAMETERS
   ----------
   pedb : Pedb
       Parent EDB object.
   name : str, default: “”
       Name of the sweep data.
   distribution : str, default: “lin”
       Distribution type of the frequency sweep. Supported types are: "lin", "dec", "estp", "linc", "oct".
   start_f : float, default: 0.0
       Start frequency of the sweep in Hz.
   end_f : float, default: 10e9
       End frequency of the sweep in Hz.
   step : float, default: 10e6
       Frequency step of the sweep in Hz.


   .. py:attribute:: simsetup
      :value: None



   .. py:property:: name
      :type: str


      Get the name of the frequency sweep data.



   .. py:property:: frequency_data
      :type: list[ansys.edb.core.simulation_setup.simulation_setup.FrequencyData]


      Get the frequency data of the sweep.

      Returns
      -------
      GrpcFrequencyData
          Frequency data object.



   .. py:method:: add_frequency_data(distribution: str, start_f: float, end_f: float, step: float)

      Add frequency data to the sweep.

      Parameters
      ----------
      distribution : str
          Distribution type of the frequency data. Supported types are: "lin", "dec", "estp", "linc", "oct".
      start_f : float
          Start frequency in Hz.
      end_f : float
          End frequency in Hz.
      step : float
          Frequency step in Hz.



   .. py:property:: enabled
      :type: bool


      Get the enabled status of the frequency sweep.

      Returns
      -------
      bool
          Enabled status.



   .. py:property:: type
      :type: str


      Get the type of the frequency sweep.

      Returns
      -------
      str
          Frequency sweep type. Values are: "interpolating", "discrete", "broadband".



   .. py:property:: use_q3d_for_dc
      :type: bool


      Get the flag indicating if Q3D is used for DC bias.

      Returns
      -------
      bool
          True if Q3D is used for DC bias, False otherwise.



   .. py:property:: save_fields
      :type: bool


      Get the flag indicating if fields are saved during the sweep.

      Returns
      -------
      bool
          True if fields are saved, False otherwise.



   .. py:property:: save_rad_fields_only
      :type: bool


      Get the flag indicating if only radiation fields are saved.

      Returns
      -------
      bool
          True if only radiation fields are saved, False otherwise.



   .. py:property:: compute_dc_point
      :type: bool


      Get the flag indicating if DC point is computed.

      Returns
      -------
      bool
          True if DC point is computed, False otherwise.



   .. py:property:: siwave_with_3dddm
      :type: bool


      Get the flag indicating if SIwave with 3D-DDM is used.

      Returns
      -------
      bool
          True if SIwave with 3D-DDM is used, False otherwise.



   .. py:property:: adv_dc_extrapolation
      :type: bool


      Get the flag indicating if advanced DC extrapolation is used.

      Returns
      -------
      bool
          True if advanced DC extrapolation is used, False otherwise.



   .. py:property:: use_hfss_solver_regions
      :type: bool


      Get the flag indicating if HFSS solver regions are used.

      Returns
      -------
      bool
          True if HFSS solver regions are used, False otherwise.



   .. py:property:: frequency_string
      :type: str


      Get the frequency sweep string.

      Returns
      -------
      str
          Frequency sweep string.



   .. py:property:: enforce_causality
      :type: bool


      Get the flag indicating if causality is enforced.

      Returns
      -------
      bool
          True if causality is enforced, False otherwise.



   .. py:property:: enforce_passivity
      :type: bool


      Get the flag indicating if passivity is enforced.

      Returns
      -------
      bool
          True if passivity is enforced, False otherwise.



   .. py:property:: interpolation_data

      Get the interpolation data points.

      Returns
      -------
      list[float]
          List of interpolation data points in Hz.



