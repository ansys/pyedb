src.pyedb.siwave_core.cpa.simulation_setup_data_model
=====================================================

.. py:module:: src.pyedb.siwave_core.cpa.simulation_setup_data_model


Classes
-------

.. autoapisummary::

   src.pyedb.siwave_core.cpa.simulation_setup_data_model.SolverOptions
   src.pyedb.siwave_core.cpa.simulation_setup_data_model.Vrm
   src.pyedb.siwave_core.cpa.simulation_setup_data_model.ChannelSetup
   src.pyedb.siwave_core.cpa.simulation_setup_data_model.SIwaveCpaSetup


Module Contents
---------------

.. py:class:: SolverOptions(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Configuration options for the SI-Wave solver.

   Attributes:
       extraction_mode (str): Mode of extraction, defaults to "si"
       custom_refinement (bool): Enable custom refinement settings, defaults to False
       extraction_frequency (str): Frequency for extraction, defaults to "10Ghz"
       compute_capacitance (bool): Enable capacitance computation, defaults to True
       compute_dc_parameters (bool): Enable DC parameters computation, defaults to True
       compute_ac_rl (bool): Enable AC RL computation, defaults to True
       ground_power_ground_nets_for_si (bool): Ground power/ground nets for SI analysis, defaults to False
       small_hole_diameter (str): Small hole diameter setting, defaults to "auto"
       cg_max_passes (int): Maximum passes for CG computation, defaults to 10
       cg_percent_error (float): Percentage error threshold for CG computation, defaults to 0.02
       cg_percent_refinement_per_pass (float): Refinement percentage per pass for CG, defaults to 0.33
       rl_max_passes (int): Maximum passes for RL computation, defaults to 10
       rl_percent_error (float): Percentage error threshold for RL computation, defaults to 0.02
       rl_percent_refinement_per_pass (float): Refinement percentage per pass for RL, defaults to 0.33
       compute_dc_rl (bool): Enable DC RL computation, defaults to True
       compute_dc_cg (bool): Enable DC CG computation, defaults to True
       return_path_net_for_loop_parameters (bool): Include return path net for loop parameters, defaults to True


   .. py:attribute:: extraction_mode
      :type:  str
      :value: 'si'



   .. py:attribute:: custom_refinement
      :type:  bool
      :value: False



   .. py:attribute:: extraction_frequency
      :type:  str
      :value: '10Ghz'



   .. py:attribute:: compute_capacitance
      :type:  bool
      :value: True



   .. py:attribute:: compute_dc_parameters
      :type:  bool
      :value: True



   .. py:attribute:: compute_ac_rl
      :type:  bool
      :value: True



   .. py:attribute:: ground_power_ground_nets_for_si
      :type:  bool
      :value: False



   .. py:attribute:: small_hole_diameter
      :type:  str
      :value: 'auto'



   .. py:attribute:: cg_max_passes
      :type:  int
      :value: 10



   .. py:attribute:: cg_percent_error
      :type:  float
      :value: 0.02



   .. py:attribute:: cg_percent_refinement_per_pass
      :type:  float
      :value: 0.33



   .. py:attribute:: rl_max_passes
      :type:  int
      :value: 10



   .. py:attribute:: rl_percent_error
      :type:  float
      :value: 0.02



   .. py:attribute:: rl_percent_refinement_per_pass
      :type:  float
      :value: 0.33



   .. py:attribute:: compute_dc_rl
      :type:  bool
      :value: True



   .. py:attribute:: compute_dc_cg
      :type:  bool
      :value: True



   .. py:attribute:: return_path_net_for_loop_parameters
      :type:  bool
      :value: True



.. py:class:: Vrm(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Voltage Regulator Module configuration.

   Attributes:
       name (str): Name of the VRM, defaults to empty string
       voltage (float): Voltage value, defaults to 0.0
       power_net (str): Power net identifier, defaults to empty string
       reference_net (str): Reference net identifier, defaults to empty string


   .. py:attribute:: name
      :type:  str
      :value: ''



   .. py:attribute:: voltage
      :type:  float
      :value: 0.0



   .. py:attribute:: power_net
      :type:  str
      :value: ''



   .. py:attribute:: reference_net
      :type:  str
      :value: ''



.. py:class:: ChannelSetup(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Channel configuration setup.

   Attributes:
       die_name (str): Name of the die, defaults to empty string
       pin_grouping_mode (str): Mode for pin grouping, defaults to "perpin"
       channel_component_exposure (Dict[str, bool]): Component exposure settings
       vrm_setup (List[Vrm]): List of VRM configurations


   .. py:attribute:: die_name
      :type:  str
      :value: ''



   .. py:attribute:: pin_grouping_mode
      :type:  str
      :value: 'perpin'



   .. py:attribute:: channel_component_exposure
      :type:  Dict[str, bool]
      :value: None



   .. py:attribute:: vrm_setup
      :type:  List[Vrm]
      :value: None



.. py:class:: SIwaveCpaSetup(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Main configuration class for SI-Wave CPA (Channel Parameter Analyzer) setup.

   Attributes:
       name (str): Name of the setup, defaults to empty string
       mode (str): Operation mode, defaults to "channel"
       model_type (str): Type of model, defaults to "rlcg"
       use_q3d_solver (bool): Use Q3D solver flag, defaults to True
       net_processing_mode (str): Net processing mode, defaults to "userspecified"
       return_path_net_for_loop_parameters (bool): Include return path net for loop parameters, defaults to True
       channel_setup (ChannelSetup): Channel configuration settings
       solver_options (SolverOptions): Solver configuration options
       nets_to_process (List[str]): List of nets to process


   .. py:attribute:: name
      :type:  str
      :value: ''



   .. py:attribute:: mode
      :type:  str
      :value: 'channel'



   .. py:attribute:: model_type
      :type:  str
      :value: 'rlcg'



   .. py:attribute:: use_q3d_solver
      :type:  bool
      :value: True



   .. py:attribute:: net_processing_mode
      :type:  str
      :value: 'userspecified'



   .. py:attribute:: return_path_net_for_loop_parameters
      :type:  bool
      :value: True



   .. py:attribute:: channel_setup
      :type:  ChannelSetup
      :value: None



   .. py:attribute:: solver_options
      :type:  SolverOptions
      :value: None



   .. py:attribute:: nets_to_process
      :type:  List[str]
      :value: None



   .. py:method:: from_dict(data: Dict) -> SIwaveCpaSetup
      :classmethod:


      Convert dictionary to SIwaveCpaSetup object.

      Args:
          data (Dict): Dictionary containing SIwaveCpaSetup configuration

      Returns:
          SIwaveCpaSetup: New instance created from the dictionary



   .. py:method:: to_dict() -> Dict

      Convert SIwaveCpaSetup object to dictionary.

      Returns:
          Dict: Dictionary representation of the SIwaveCpaSetup instance



