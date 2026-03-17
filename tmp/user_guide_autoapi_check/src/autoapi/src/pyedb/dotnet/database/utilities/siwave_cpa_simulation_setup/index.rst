src.pyedb.dotnet.database.utilities.siwave_cpa_simulation_setup
===============================================================

.. py:module:: src.pyedb.dotnet.database.utilities.siwave_cpa_simulation_setup


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.utilities.siwave_cpa_simulation_setup.ChannelSetup
   src.pyedb.dotnet.database.utilities.siwave_cpa_simulation_setup.SolverOptions
   src.pyedb.dotnet.database.utilities.siwave_cpa_simulation_setup.SIWaveCPASimulationSetup


Module Contents
---------------

.. py:class:: ChannelSetup(pedb, cfg_channel_setup=None)

   A class to manage the channel setup configuration for SIWave CPA simulations.

   Attributes:
       die_name (str): The name of the die associated with the channel setup.
       pin_grouping_mode (str): The mode for pin grouping, e.g., "perpin", "ploc", or "usediepingroups".
       channel_component_exposure (dict): A dictionary mapping component names to their exposure status (True/False).
       vrm (list): A list of VRM (Voltage Regulator Module) configurations.


   .. py:property:: die_name


   .. py:property:: pin_grouping_mode

      Get the pin grouping mode from the SIWave properties.

      Returns:
          str: The pin grouping mode ("perpin", "ploc", or "usediepingroups").



   .. py:property:: channel_component_exposure

      Get the channel component exposure configuration from the SIWave properties.

      Returns:
          dict: A dictionary mapping component names to their exposure status (True/False).



   .. py:property:: vrm

      Get the VRM (Voltage Regulator Module) setup from the SIWave properties.

      Returns:
          list: A list of VRM objects.



.. py:class:: SolverOptions(pedb, cfg_solver_options=None)

   A class to manage solver options for SIWave CPA simulations.

   Attributes:
       mode (str): The extraction mode, either "si" or "pi".
       custom_refinement (bool): Whether custom refinement is enabled.
       extraction_frequency (str): The frequency for extraction, e.g., "10Ghz".
       compute_capacitance (bool): Whether to compute capacitance.
       compute_dc_rl (bool): Whether to compute DC resistance and inductance.
       compute_dc_parameters (bool): Whether to compute DC parameters.
       compute_dc_cg (bool): Whether to compute DC capacitance and conductance.
       compute_ac_rl (bool): Whether to compute AC resistance and inductance.
       ground_power_nets_for_si (bool): Whether to ground power nets for SI analysis.
       small_hole_diameter (float or str): The diameter of small holes, or "auto".
       adaptive_refinement_cg_max_passes (int): Maximum passes for adaptive refinement of CG.
       adaptive_refinement_rl_max_passes (int): Maximum passes for adaptive refinement of RL.
       adaptive_refinement_cg_percent_error (float): Percent error for CG adaptive refinement.
       adaptive_refinement_rl_percent_error (float): Percent error for RL adaptive refinement.
       rl_percent_refinement_per_pass (float): Percent refinement per pass for RL.
       cg_percent_refinement_per_pass (float): Percent refinement per pass for CG.
       return_path_net_for_loop_parameters (bool): Whether to use return path net for loop parameters.

   Methods:
       __init__(pedb, cfg_solver_options=None): Initializes the SolverOptions object.
       __init_values(): Initializes default values for solver options.
       _apply_cfg_object(solver_options): Applies configuration from a given solver options object.


   .. py:property:: extraction_mode

      Get the extraction mode.

      Returns:
          str: The extraction mode ("si" or "pi").



   .. py:property:: custom_refinement

      Get whether custom refinement is enabled.

      Returns:
          bool: True if custom refinement is enabled, False otherwise.



   .. py:property:: extraction_frequency

      Get the extraction frequency.

      Returns:
          str: The extraction frequency.



   .. py:property:: compute_capacitance

      Get whether capacitance computation is enabled.

      Returns:
          bool: True if enabled, False otherwise.



   .. py:property:: compute_dc_parameters

      Property setter for the `compute_dc_parameters` attribute.

      Sets whether the computation of DC parameters is enabled in the SIWave properties.

      Args:
          value (bool): True to enable DC parameter computation, False to disable it.



   .. py:property:: compute_dc_rl

      Get whether DC resistance and inductance computation is enabled.

      Returns:
          bool: True if DC resistance and inductance computation is enabled, False otherwise.



   .. py:property:: compute_dc_cg

      Get whether DC capacitance and conductance computation is enabled.

      Returns:
          bool: True if DC capacitance and conductance computation is enabled, False otherwise.



   .. py:property:: compute_ac_rl

      Get whether AC resistance and inductance computation is enabled.

      Returns:
          bool: True if AC resistance and inductance computation is enabled, False otherwise.



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



