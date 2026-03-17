src.pyedb.grpc.database.simulation_setup.siwave_cpa_simulation_setup
====================================================================

.. py:module:: src.pyedb.grpc.database.simulation_setup.siwave_cpa_simulation_setup


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.simulation_setup.siwave_cpa_simulation_setup.ChannelSetup
   src.pyedb.grpc.database.simulation_setup.siwave_cpa_simulation_setup.SolverOptions
   src.pyedb.grpc.database.simulation_setup.siwave_cpa_simulation_setup.SIWaveCPASimulationSetup


Module Contents
---------------

.. py:class:: ChannelSetup(pedb, cfg_channel_setup=None)

   Represents the setup configuration for a channel in SIwave CPA simulations.

   Attributes:
       die_name (str): The name of the die associated with the channel setup.
       pin_grouping_mode (str): The mode for pin grouping. Options are "perpin", "ploc", or "usediepingroups".
       channel_component_exposure (dict): A dictionary mapping component names to their exposure status (True/False).
       vrm (list): A list of VRM (Voltage Regulator Module) configurations.


   .. py:property:: die_name

      Gets the die name from the database.

      Returns:
          str: The die name.



   .. py:property:: pin_grouping_mode

      Gets the pin grouping mode from the database.

      Returns:
          str: The pin grouping mode ("perpin", "ploc", or "usediepingroups").



   .. py:property:: channel_component_exposure

      Gets the channel component exposure configuration from the database.

      Returns:
          dict: A dictionary mapping component names to their exposure status (True/False).



   .. py:property:: vrm

      Gets the VRM (Voltage Regulator Module) setup from the database.

      Returns:
          list: A list of Vrm objects representing the VRM setup.

      Raises:
          ValueError: If the VRM format is invalid.



.. py:class:: SolverOptions(pedb, cfg_solver_options=None)

   Represents solver options configuration for SIwave CPA simulations.

   Attributes:
       extraction_mode (str): Extraction mode ('si' or 'pi')
       custom_refinement (bool): Whether to use custom refinement settings
       extraction_frequency (str): Frequency for extraction (e.g. '10Ghz')
       compute_capacitance (bool): Whether to compute capacitance
       compute_dc_parameters (bool): Whether to compute DC parameters
       compute_dc_rl (bool): Whether to compute DC RL parameters
       compute_dc_cg (bool): Whether to compute DC CG parameters
       compute_ac_rl (bool): Whether to compute AC RL parameters
       ground_power_nets_for_si (bool): Whether to ground power nets for SI analysis
       small_hole_diameter (float|str): Small hole diameter value or 'auto'
       adaptive_refinement_cg_max_passes (int): Max passes for CG adaptive refinement
       adaptive_refinement_rl_max_passes (int): Max passes for RL adaptive refinement
       adaptive_refinement_cg_percent_error (float): Target error for CG refinement
       adaptive_refinement_rl_percent_error (float): Target error for RL refinement
       rl_percent_refinement_per_pass (float): RL refinement percentage per pass
       cg_percent_refinement_per_pass (float): CG refinement percentage per pass
       return_path_net_for_loop_parameters (bool): Whether to use return path net


   .. py:property:: extraction_mode

      Gets the extraction mode from the database.

      Returns:
          str: The extraction mode. Returns "si" if the mode is set to "1", otherwise "pi".



   .. py:property:: custom_refinement

      Gets the custom refinement setting from the database.

      Returns:
          bool: True if custom refinement is enabled, False otherwise.



   .. py:property:: extraction_frequency

      Gets the extraction frequency from the database.

      Returns:
          str: The extraction frequency value as a string.



   .. py:property:: compute_capacitance

      Gets the compute capacitance setting from the database.

      Returns:
          bool: True if capacitance computation is enabled, False otherwise.



   .. py:property:: compute_dc_parameters

      Gets the compute DC parameters setting from the database.

      Returns:
          bool: True if DC parameters computation is enabled, False otherwise.



   .. py:property:: compute_dc_rl

      Gets the compute DC RL parameters setting from the database.

      Returns:
          bool: True if DC RL parameters computation is enabled, False otherwise.



   .. py:property:: compute_dc_cg

      Gets the compute DC CG parameters setting from the database.

      Returns:
          bool: True if DC CG parameters computation is enabled, False otherwise.



   .. py:property:: compute_ac_rl

      Gets the compute AC RL parameters setting from the database.

      Returns:
          bool: True if AC RL parameters computation is enabled, False otherwise.



   .. py:property:: ground_power_nets_for_si

      Gets the ground power nets for SI analysis setting from the database.

      Returns:
          bool: True if grounding power nets for SI analysis is enabled, False otherwise.



   .. py:property:: small_hole_diameter

      Gets the small hole diameter setting from the database.

      Returns:
          float|str: The small hole diameter as a float, or 'auto' if the value is set to -1.



   .. py:property:: model_type

      Gets the model type setting from the database.

      Returns:
          str: The model type. Returns "rlcg" if the model type is set to "0", otherwise "esd_r".



   .. py:property:: adaptive_refinement_cg_max_passes

      Gets the maximum number of passes for CG adaptive refinement from the database.

      Returns:
          int: The maximum number of passes for CG adaptive refinement.



   .. py:property:: adaptive_refinement_cg_percent_error

      Gets the target error percentage for CG adaptive refinement from the database.

      Returns:
          float: The target error percentage for CG adaptive refinement.



   .. py:property:: cg_percent_refinement_per_pass

      Gets the percentage of CG refinement per pass from the database.

      Returns:
          float: The percentage of CG refinement per pass.



   .. py:property:: adaptive_refinement_rl_max_passes

      Gets the maximum number of passes for RL adaptive refinement from the database.

      Returns:
          int: The maximum number of passes for RL adaptive refinement.



   .. py:property:: adaptive_refinement_rl_percent_error

      Gets the target error percentage for RL adaptive refinement from the database.

      Returns:
          float: The target error percentage for RL adaptive refinement.



   .. py:property:: rl_percent_refinement_per_pass

      Gets the percentage of RL refinement per pass from the database.

      Returns:
          float: The percentage of RL refinement per pass.



   .. py:property:: return_path_net_for_loop_parameters

      Gets the return path net setting for loop parameters from the database.

      Returns:
          bool: True if the return path net is enabled for loop parameters, False otherwise.



.. py:class:: SIWaveCPASimulationSetup(pedb, name=None, siwave_cpa_setup_class=None)

   Represents the setup configuration for SIwave CPA simulations.

   Attributes:
       _pedb: The database object representing the active cell.
       _channel_setup (ChannelSetup): The channel setup configuration.
       _solver_options (SolverOptions): The solver options configuration.


   .. py:attribute:: type
      :value: 'cpa'



   .. py:method:: create(edb: pyedb.grpc.edb.Edb, name=None, siwave_cpa_setup_class=None) -> SIWaveCPASimulationSetup
      :classmethod:


      Creates a new SIWaveCPASimulationSetup instance.

      Parameters:
      -----------
      edb (pyedb.Edb): The EDB object representing the active design.
      name (str, optional): The name of the simulation setup. If not provided, a unique name will be generated.
      siwave_cpa_setup_class (SIwaveCpaSetup, optional): An optional configuration object to initialize the setup.

      #Returns:
      --------
      SIWaveCPASimulationSetup: A new instance of SIWaveCPASimulationSetup.



   .. py:property:: name
      :type: str


      Gets the name of the simulation setup.

      Returns:
          str: The name of the simulation setup.



   .. py:property:: mode

      Gets the mode of the simulation setup.

      Returns:
          str: The mode of the simulation setup ("channel" or "no_channel").



   .. py:property:: model_type

      Gets the model type of the simulation setup.

      Returns:
          str: The model type ("rlcg" or "esd_r").



   .. py:property:: use_q3d_solver

      Gets the Q3D solver usage setting.

      Returns:
          bool: True if the Q3D solver is used, False otherwise.



   .. py:property:: net_processing_mode

      Gets the net processing mode.

      Returns:
          str: The net processing mode.



   .. py:property:: channel_setup

      Gets the channel setup configuration.

      Returns:
          ChannelSetup: The channel setup configuration.



   .. py:property:: solver_options

      Gets the solver options configuration.

      Returns:
          SolverOptions: The solver options configuration.



   .. py:property:: nets_to_process

      Gets the list of nets to process.

      Returns:
          list: A list of nets to process.



