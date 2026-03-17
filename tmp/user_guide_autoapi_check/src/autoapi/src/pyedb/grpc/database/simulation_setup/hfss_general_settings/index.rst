src.pyedb.grpc.database.simulation_setup.hfss_general_settings
==============================================================

.. py:module:: src.pyedb.grpc.database.simulation_setup.hfss_general_settings


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.simulation_setup.hfss_general_settings.BroadbandAdaptiveSolution
   src.pyedb.grpc.database.simulation_setup.hfss_general_settings.AdaptiveFrequency
   src.pyedb.grpc.database.simulation_setup.hfss_general_settings.MultiFrequencyAdaptiveSolution
   src.pyedb.grpc.database.simulation_setup.hfss_general_settings.MatrixConvergenceDataEntry
   src.pyedb.grpc.database.simulation_setup.hfss_general_settings.MatrixConvergenceData
   src.pyedb.grpc.database.simulation_setup.hfss_general_settings.SingleFrequencyAdaptiveSolution
   src.pyedb.grpc.database.simulation_setup.hfss_general_settings.HFSSGeneralSettings


Module Contents
---------------

.. py:class:: BroadbandAdaptiveSolution(pedb, core)

   .. py:attribute:: core


   .. py:property:: high_frequency
      :type: str


      High frequency for broadband adaptive solution.

      Returns
      -------
      float
          High frequency value in Hz.




   .. py:property:: low_frequency
      :type: str


      Low frequency for broadband adaptive solution.

      Returns
      -------
      float
          Low frequency value in Hz.




   .. py:property:: max_delta
      :type: str


      Maximum delta for broadband adaptive solution.

      Returns
      -------
      float
          Maximum delta value.




   .. py:property:: max_num_passes
      :type: int


      Maximum number of passes for broadband adaptive solution.

      Returns
      -------
      int
          Maximum number of passes.




   .. py:property:: max_passes
      :type: int


      Maximum number of passes for broadband adaptive solution.

      Returns
      -------
      int
          Maximum number of passes.




.. py:class:: AdaptiveFrequency(pedb, core)

   .. py:attribute:: core


   .. py:property:: adaptive_frequency
      :type: str


      Adaptive frequency value.

      Returns
      -------
      float
          Adaptive frequency in Hz.




   .. py:property:: max_delta
      :type: str


      Maximum delta for the adaptive frequency.

      Returns
      -------
      float
          Maximum delta value.




   .. py:property:: output_variables
      :type: dict[str, float]


      Map of output variable names to maximum delta S.

      Returns
      -------
      dict[str, float]
          Dictionary of output variable names and delta S value.




   .. py:method:: add_output_variable(name: str, delta_s: float)

      Add an output variable for the adaptive frequency.

      Parameters
      ----------
      name : str
          Name of the output variable.
      delta_s : float
          Delta S value.




   .. py:method:: delete_output_variable(name: str) -> bool

      Delete an output variable from the adaptive frequency.

      Parameters
      ----------
      name : str
          Name of the output variable to delete.

      Returns
      -------
      bool




.. py:class:: MultiFrequencyAdaptiveSolution(pedb, core)

   .. py:attribute:: core


   .. py:property:: adaptive_frequencies
      :type: list[AdaptiveFrequency]



   .. py:property:: max_passes
      :type: int


      Maximum number of passes for multi-frequency adaptive solution.

      Returns
      -------
      int
          Maximum number of passes.




.. py:class:: MatrixConvergenceDataEntry(pedb, core)

   .. py:attribute:: core


   .. py:property:: mag_limit
      :type: float


      Magnitude limit for the matrix convergence data entry.

      Returns
      -------
      float
          Magnitude limit value.




   .. py:property:: phase_limit
      :type: float


      Phase limit for the matrix convergence data entry.

      Returns
      -------
      float
          Phase limit value.




   .. py:property:: port_1_name
      :type: str


      Name of the first port.

      Returns
      -------
      str
          First port name.




   .. py:property:: port_2_name
      :type: str


      Name of the second port.

      Returns
      -------
      str
          Second port name.




.. py:class:: MatrixConvergenceData(pedb, core)

   .. py:attribute:: core


   .. py:property:: all_constant
      :type: bool


      Indicates whether all matrix convergence data entries are constant.

      Returns
      -------
      bool
          True if all entries are constant, False otherwise.




   .. py:property:: all_diag_constant
      :type: bool


      Indicates whether all diagonal matrix convergence data entries are constant.

      Returns
      -------
      bool
          True if all diagonal entries are constant, False otherwise.




   .. py:property:: all_off_diag_constant
      :type: bool


      Indicates whether all off-diagonal matrix convergence data entries are constant.

      Returns
      -------
      bool
          True if all off-diagonal entries are constant, False otherwise.




   .. py:property:: entry_list
      :type: list[MatrixConvergenceDataEntry]


      List of matrix convergence data entries.

      Returns
      -------
      list[MatrixConvergenceDataEntry]
          List of matrix convergence data entries.




   .. py:property:: mag_min_threshold
      :type: float


      Magnitude minimum threshold for matrix convergence data.

      Returns
      -------
      float
          Magnitude minimum threshold value.




   .. py:method:: add_entry(port_name_1, port_name_2, mag_limit, phase_limit)

      Add a matrix convergence data entry.

      Parameters
      ----------
      port_name_1 : str
          Name of the first port.
      port_name_2 : str
          Name of the second port.
      mag_limit : float
          Magnitude limit.
      phase_limit : float
          Phase limit.



   .. py:method:: set_all_constant(mag_limit, phase_limit, port_names)

      Set all matrix convergence data entries to constant values.

      Parameters
      ----------
      mag_limit : float
          Magnitude limit.
      phase_limit : float
          Phase limit.
      port_names : list[str]
          List of port names.



   .. py:method:: set_all_diag_constant(mag_limit, phase_limit, port_names, clear_entries)

      Set all diagonal matrix convergence data entries to constant values.

      Parameters
      ----------
      mag_limit : float
          Magnitude limit.
      phase_limit : float
          Phase limit.
      port_names : list[str]
          List of port names.
      clear_entries : bool
          Whether to clear existing entries.



   .. py:method:: set_all_off_diag_constant(mag_limit, phase_limit, port_names, clear_entries)

      Set all off-diagonal matrix convergence data entries to constant values.

      Parameters
      ----------
      mag_limit : float
          Magnitude limit.
      phase_limit : float
          Phase limit.
      port_names : list[str]
          List of port names.
      clear_entries : bool
          Whether to clear existing entries.



.. py:class:: SingleFrequencyAdaptiveSolution(pedb, core)

   .. py:attribute:: core


   .. py:property:: adaptive_frequency
      :type: float


      Adaptive frequency for single frequency adaptive solution.

      Returns
      -------
      float
          Adaptive frequency in Hz.




   .. py:property:: max_delta
      :type: float


      Maximum delta for single frequency adaptive solution.

      Returns
      -------
      float
          Maximum delta value.




   .. py:property:: max_passes
      :type: int


      Maximum number of passes for single frequency adaptive solution.

      Returns
      -------
      int
          Maximum number of passes.




   .. py:property:: mx_conv_data
      :type: MatrixConvergenceData


      Matrix convergence data for single frequency adaptive solution.

      Returns
      -------
      :class:`MatrixConvergenceData
      <pyedb.grpc.database.simulation_setup.hfss_general_settings.MatrixConvergenceData>`
          Matrix convergence data object.




   .. py:property:: use_mx_conv_data
      :type: bool


      Indicates whether to use matrix convergence data.

      Returns
      -------
      bool
          True if matrix convergence data is used, False otherwise.




.. py:class:: HFSSGeneralSettings(parent)

   PyEDB-core HFSS general settings class.


   .. py:attribute:: core


   .. py:property:: adapt_type
      :type: str


      Adaptation type.

      ..deprecated:: 0.67.0
          This property is deprecated and will be removed in future versions.
          Attribute added for dotnet compatibility.
          Use :attr:`adaptive_solution_type` instead.




   .. py:property:: adaptive_solution_type
      :type: str


      Adaptive solution type.

      Returns
      -------
      str
          Adaptive solution type name. Returned values are `single`, `multi_frequencies`, `broadband`,
          or `num_adapt_type`.




   .. py:property:: adaptive_frequency_data_list

      List the adaptive frequency data entries for multi-frequency adaptive solution.

      Returns
      -------
      list[AdaptiveFrequency]
          List of adaptive frequency data entries.



   .. py:property:: broadband_adaptive_solution
      :type: BroadbandAdaptiveSolution


      Settings for a broadband adaptive solution.

      Returns
      -------
      :class:`HFSSBroadbandAdaptiveSolution
      <pyedb.grpc.database.simulation_setup.hfss_simulation_settings.HFSSBroadbandAdaptiveSolution>`
          Broadband adaptive solution settings object.




   .. py:property:: mesh_region_name
      :type: str


      Name of the mesh region to use.

      Returns
      -------
      str
          Mesh region name.




   .. py:property:: multi_frequency_adaptive_solution
      :type: MultiFrequencyAdaptiveSolution



   .. py:property:: save_fields
      :type: bool


      Indicates whether to save fields.

      Returns
      -------
      bool
          True if fields are to be saved, False otherwise.




   .. py:property:: save_rad_field_only
      :type: bool


      Indicates whether to save radiation field only.

      .. deprecated:: 0.67.0
          This property is deprecated and will be removed in future versions.
          Use :attr:`save_rad_fields_only` instead.




   .. py:property:: save_rad_fields_only
      :type: bool


      Indicates whether to save radiation fields only.

      Returns
      -------
      bool
          True if only radiation fields are to be saved, False otherwise.




   .. py:property:: single_frequency_adaptive_solution


   .. py:property:: use_mesh_region
      :type: bool


      Indicates whether to use a mesh region.

      Returns
      -------
      bool
          True if a mesh region is used, False otherwise.




   .. py:property:: use_parallel_refinement
      :type: bool


      Indicates whether to use parallel refinement.

      Returns
      -------
      bool
          True if parallel refinement is used, False otherwise.




   .. py:property:: max_refine_per_pass
      :type: float


      Maximum refinement per pass.

      .. deprecated:: 0.67.0
      This property is deprecated and will be removed in future versions.
      use settings.options.max_refinement_per_pass instead.




   .. py:property:: min_passes
      :type: int


      Minimum number of passes.

      .. deprecated:: 0.67.0
      This property is deprecated and will be removed in future versions.
      use settings.options.min_passes instead.




   .. py:property:: use_max_refinement
      :type: bool


      Indicates whether to use maximum refinement.

      .. deprecated:: 0.67.0
      This property is deprecated and will be removed in future versions.
      use settings.options.use_max_refinement instead.




