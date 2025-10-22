# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import annotations

import pyedb.siwave_core.cpa.simulation_setup_data_model
from pyedb.siwave_core.cpa.simulation_setup_data_model import SIwaveCpaSetup, Vrm
from pyedb.siwave_core.product_properties import SIwaveProperties


class ChannelSetup:
    """
    A class to manage the channel setup configuration for SIWave CPA simulations.

    Attributes:
        die_name (str): The name of the die associated with the channel setup.
        pin_grouping_mode (str): The mode for pin grouping, e.g., "perpin", "ploc", or "usediepingroups".
        channel_component_exposure (dict): A dictionary mapping component names to their exposure status (True/False).
        vrm (list): A list of VRM (Voltage Regulator Module) configurations.
    """

    def __init__(self, pedb, cfg_channel_setup=None):
        self._pedb = pedb
        self.__init_values()
        if cfg_channel_setup:
            self._apply_cfg_object(cfg_channel_setup)

    def __init_values(self):
        self.die_name = ""
        self.pin_grouping_mode = "perpin"
        self.channel_component_exposure = {}

    def _apply_cfg_object(self, channel_setup):
        self.die_name = channel_setup.die_name
        self.channel_component_exposure = channel_setup.channel_component_exposure
        self.pin_grouping_mode = channel_setup.pin_grouping_mode
        self.vrm = channel_setup.vrm_setup if hasattr(channel_setup, "vrm_setup") else []  # type: ignore[union-attr]

    @property
    def die_name(self):
        return self._pedb.active_cell.GetProductProperty(
            self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_CHANNEL_DIE_NAME
        )[1]

    @die_name.setter
    def die_name(self, value):
        """
        Get the die name from the SIWave properties.

        Returns:
            str: The die name.
        """

        self._pedb.active_cell.SetProductProperty(
            self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_CHANNEL_DIE_NAME, value
        )

    @property
    def pin_grouping_mode(self):
        """
        Get the pin grouping mode from the SIWave properties.

        Returns:
            str: The pin grouping mode ("perpin", "ploc", or "usediepingroups").
        """

        mode_mapping = {-1: "perpin", 0: "ploc", 1: "usediepingroups"}
        pg_mode = self._pedb.active_cell.GetProductProperty(
            self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_CHANNEL_PIN_GROUPING_MODE
        )[-1]
        return mode_mapping[int(pg_mode.split(":")[1])] if pg_mode else "perpin"

    @pin_grouping_mode.setter
    def pin_grouping_mode(self, value):
        mapping = {"perpin": -1, "ploc": 0, "usediepingroups": 1}
        if isinstance(value, str):
            if not value in mapping:
                raise f"value {value} not supported, must be {list(mapping.keys())}"
            value = mapping[value]
        if not value in [-1, 0, 1]:
            raise f"wrong value {value}"
        self._pedb.active_cell.SetProductProperty(
            self._pedb._edb.ProductId.SIWave,
            SIwaveProperties.CPA_CHANNEL_PIN_GROUPING_MODE,
            self.die_name + ":" + str(value),
        )

    @property
    def channel_component_exposure(self):
        """
        Get the channel component exposure configuration from the SIWave properties.

        Returns:
            dict: A dictionary mapping component names to their exposure status (True/False).
        """

        cmp_exposure = self._pedb.active_cell.GetProductProperty(
            self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_CHANNEL_COMPONENT_EXPOSURE_CONFIG
        )[-1]
        cmp_dict = {}
        for comp in cmp_exposure.split("*"):
            _comp = comp.split(":")
            cmp_dict[_comp[0]] = bool(_comp[1])
        return cmp_dict

    @channel_component_exposure.setter
    def channel_component_exposure(self, value):
        if not isinstance(value, dict):
            raise "Channel component exposure input must be a dictionary."
        channel_comp_exposure = ""
        for comp, enabled in value.items():
            if channel_comp_exposure:
                channel_comp_exposure += "*"
            channel_comp_exposure += f"{comp}:{int(enabled)}"
        self._pedb.active_cell.SetProductProperty(
            self._pedb._edb.ProductId.SIWave,
            SIwaveProperties.CPA_CHANNEL_COMPONENT_EXPOSURE_CONFIG,
            channel_comp_exposure,
        )

    @property
    def vrm(self):
        """
        Get the VRM (Voltage Regulator Module) setup from the SIWave properties.

        Returns:
            list: A list of VRM objects.
        """

        vrm = self._pedb.active_cell.GetProductProperty(
            self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_CHANNEL_VRM_SETUP
        )[-1]
        vrm_list = []
        for _vrm in vrm.split("*"):
            vrm_obj = Vrm()
            _vrm_values = _vrm.split(":")
            if len(_vrm_values) != 4:
                raise ValueError(
                    f"Invalid VRM format: {_vrm}. Expected format is 'name:voltage:power_net:reference_net'."
                )
            vrm_obj.name = _vrm_values[0]
            vrm_obj.voltage = float(_vrm_values[1])
            vrm_obj.power_net = _vrm_values[2]
            vrm_obj.reference_net = _vrm_values[3]
            vrm_list.append(vrm_obj)
        return vrm_list

    @vrm.setter
    def vrm(self, value):
        if not isinstance(value, list):
            raise "vrm setter must have list as input."
        vrm_str = ""
        for vrm in value:
            if isinstance(vrm, pyedb.siwave_core.cpa.simulation_setup_data_model.Vrm):
                if vrm_str:
                    vrm_str += "*"
                vrm_str += vrm.name
                vrm_str += ":"
                vrm_str += str(vrm.voltage)
                vrm_str += ":"
                vrm_str += vrm.power_net
                vrm_str += ":"
                vrm_str += vrm.reference_net
        self._pedb.active_cell.SetProductProperty(
            self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_CHANNEL_VRM_SETUP, vrm_str
        )

    # vrm_setup: Vrm = None


class SolverOptions:
    """
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
    """

    def __init__(self, pedb, cfg_solver_options=None):
        self._pedb = pedb
        self.__init_values()
        if cfg_solver_options:
            self._apply_cfg_object(cfg_solver_options)

    def __init_values(
        self,
    ):
        self.mode = "si"
        self.custom_refinement = False
        self.extraction_frequency = "10Ghz"
        self.compute_capacitance = True
        self.compute_dc_rl = True
        self.compute_dc_parameters = True
        self.compute_dc_cg = True
        self.compute_ac_rl = True
        self.ground_power_nets_for_si = True
        self.small_hole_diameter = 0.0
        self.adaptive_refinement_cg_max_passes = 10
        self.adaptive_refinement_rl_max_passes = 10
        self.adaptive_refinement_cg_percent_error = 0.02
        self.adaptive_refinement_rl_percent_error = 0.02
        self.rl_percent_refinement_per_pass = 0.33
        self.cg_percent_refinement_per_pass = 0.33
        self.return_path_net_for_loop_parameters = True

    def _apply_cfg_object(self, solver_options):
        self.extraction_mode = solver_options.extraction_mode
        self.custom_refinement = solver_options.custom_refinement
        self.extraction_frequency = solver_options.extraction_frequency
        self.compute_capacitance = solver_options.compute_capacitance
        self.compute_dc_parameters = solver_options.compute_dc_parameters
        self.compute_dc_rl = solver_options.compute_dc_rl
        self.compute_dc_cg = solver_options.compute_dc_cg
        self.compute_ac_rl = solver_options.compute_ac_rl
        self.ground_power_nets_for_si = solver_options.ground_power_ground_nets_for_si
        self.small_hole_diameter = solver_options.small_hole_diameter
        self.adaptive_refinement_cg_max_passes = solver_options.cg_max_passes
        self.adaptive_refinement_rl_max_passes = solver_options.rl_max_passes
        self.adaptive_refinement_cg_percent_error = solver_options.cg_percent_error
        self.adaptive_refinement_rl_percent_error = solver_options.rl_percent_error
        self.rl_percent_refinement_per_pass = solver_options.rl_percent_refinement_per_pass
        self.return_path_net_for_loop_parameters = solver_options.return_path_net_for_loop_parameters

    @property
    def extraction_mode(self):
        """
        Get the extraction mode.

        Returns:
            str: The extraction mode ("si" or "pi").
        """

        mode = self._pedb.active_cell.GetProductProperty(
            self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_EXTRACTION_MODE
        )
        if mode == "1":
            return "si"
        return "pi"

    @extraction_mode.setter
    def extraction_mode(self, value):
        if value == "si":
            self._pedb.active_cell.SetProductProperty(
                self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_EXTRACTION_MODE, "1"
            )
        else:
            self._pedb.active_cell.SetProductProperty(
                self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_EXTRACTION_MODE, "0"
            )

    @property
    def custom_refinement(self):
        """
        Get whether custom refinement is enabled.

        Returns:
            bool: True if custom refinement is enabled, False otherwise.
        """

        refine = self._pedb.active_cell.GetProductProperty(
            self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_CUSTOM_REFINEMENT
        )[-1]
        if refine == "1":
            return True
        return False

    @custom_refinement.setter
    def custom_refinement(self, value):
        if value:
            self._pedb.active_cell.SetProductProperty(
                self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_CUSTOM_REFINEMENT, "1"
            )
        else:
            self._pedb.active_cell.SetProductProperty(
                self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_CUSTOM_REFINEMENT, "0"
            )

    @property
    def extraction_frequency(self):
        """
        Get the extraction frequency.

        Returns:
            str: The extraction frequency.
        """
        return self._pedb.active_cell.GetProductProperty(
            self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_EXTRACTION_FREQUENCY
        )[-1]

    @extraction_frequency.setter
    def extraction_frequency(self, value):
        freq = self._pedb.edb_value(value).ToString()
        self._pedb.active_cell.SetProductProperty(
            self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_EXTRACTION_FREQUENCY, freq
        )

    @property
    def compute_capacitance(self):
        """
        Get whether capacitance computation is enabled.

        Returns:
            bool: True if enabled, False otherwise.
        """

        compute = self._pedb.active_cell.GetProductProperty(
            self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_COMPUTE_CAPACITANCE
        )[-1]
        if compute == "1":
            return True
        return False

    @compute_capacitance.setter
    def compute_capacitance(self, value):
        if value:
            self._pedb.active_cell.SetProductProperty(
                self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_COMPUTE_CAPACITANCE, "1"
            )
        else:
            self._pedb.active_cell.SetProductProperty(
                self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_COMPUTE_CAPACITANCE, "0"
            )

    @property
    def compute_dc_parameters(self):
        """
        Property setter for the `compute_dc_parameters` attribute.

        Sets whether the computation of DC parameters is enabled in the SIWave properties.

        Args:
            value (bool): True to enable DC parameter computation, False to disable it.
        """
        compute = self._pedb.active_cell.GetProductProperty(
            self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_COMPUTE_DC_PARAMS
        )[-1]
        if compute == "1":
            return True
        return False

    @compute_dc_parameters.setter
    def compute_dc_parameters(self, value):
        if value:
            self._pedb.active_cell.SetProductProperty(
                self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_COMPUTE_DC_PARAMS, "1"
            )
        else:
            self._pedb.active_cell.GetProductProperty(
                self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_COMPUTE_DC_PARAMS, "0"
            )

    @property
    def compute_dc_rl(self):
        """
        Get whether DC resistance and inductance computation is enabled.

        Returns:
            bool: True if DC resistance and inductance computation is enabled, False otherwise.
        """
        _res = self._pedb.active_cell.GetProductProperty(
            self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_DC_PARAMS_COMPUTE_RL
        )[-1]
        if _res == "1":
            return True
        return False

    @compute_dc_rl.setter
    def compute_dc_rl(self, value):
        if value:
            self._pedb.active_cell.SetProductProperty(
                self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_DC_PARAMS_COMPUTE_RL, "1"
            )
        else:
            self._pedb.active_cell.SetProductProperty(
                self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_DC_PARAMS_COMPUTE_RL, "0"
            )

    @property
    def compute_dc_cg(self):
        """
        Get whether DC capacitance and conductance computation is enabled.

        Returns:
            bool: True if DC capacitance and conductance computation is enabled, False otherwise.
        """
        _res = self._pedb.active_cell.GetProductProperty(
            self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_DC_PARAMS_COMPUTE_CG
        )[-1]
        if _res == "1":
            return True
        return False

    @compute_dc_cg.setter
    def compute_dc_cg(self, value):
        if value:
            self._pedb.active_cell.SetProductProperty(
                self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_DC_PARAMS_COMPUTE_CG, "1"
            )
        else:
            self._pedb.active_cell.SetProductProperty(
                self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_DC_PARAMS_COMPUTE_CG, "0"
            )

    @property
    def compute_ac_rl(self):
        """
        Get whether AC resistance and inductance computation is enabled.

        Returns:
            bool: True if AC resistance and inductance computation is enabled, False otherwise.
        """
        _res = self._pedb.active_cell.GetProductProperty(
            self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_AC_PARAMS_COMPUTE_RL
        )[-1]
        if _res == "1":
            return True
        return False

    @compute_ac_rl.setter
    def compute_ac_rl(self, value):
        if value:
            self._pedb.active_cell.SetProductProperty(
                self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_AC_PARAMS_COMPUTE_RL, "1"
            )
        else:
            self._pedb.active_cell.SetProductProperty(
                self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_AC_PARAMS_COMPUTE_RL, "0"
            )

    @property
    def ground_power_nets_for_si(self):
        """
        Gets the ground power nets for SI analysis setting from the database.

        Returns:
            bool: True if grounding power nets for SI analysis is enabled, False otherwise.
        """
        _res = self._pedb.active_cell.GetProductProperty(
            self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_GROUND_PG_NETS_FOR_SI
        )[-1]
        if _res == "1":
            return True
        return False

    @ground_power_nets_for_si.setter
    def ground_power_nets_for_si(self, value):
        if value:
            self._pedb.active_cell.SetProductProperty(
                self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_GROUND_PG_NETS_FOR_SI, "1"
            )
        else:
            self._pedb.active_cell.SetProductProperty(
                self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_GROUND_PG_NETS_FOR_SI, "0"
            )

    @property
    def small_hole_diameter(self):
        """
        Gets the small hole diameter setting from the database.

        Returns:
            float|str: The small hole diameter as a float, or 'auto' if the value is set to -1.
        """
        _res = self._pedb.active_cell.GetProductProperty(
            self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_SMALL_HOLE_DIAMETER
        )[-1]
        if _res == "-1":
            return "auto"
        else:
            return float(_res)

    @small_hole_diameter.setter
    def small_hole_diameter(self, value):
        if value == "auto" or value == -1:
            self._pedb.active_cell.SetProductProperty(
                self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_SMALL_HOLE_DIAMETER, "-1"
            )
        else:
            self._pedb.active_cell.SetProductProperty(
                self._pedb._edb.ProductId.SIWave,
                SIwaveProperties.CPA_SMALL_HOLE_DIAMETER,
                self._pedb.edb_value(value).ToString(),
            )

    @property
    def model_type(self):
        """
        Gets the model type setting from the database.

        Returns:
            str: The model type. Returns "rlcg" if the model type is set to "0", otherwise "esd_r".
        """
        return self._pedb.active_cell.GetProductProperty(
            self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_MODEL_TYPE
        )[-1]

    @model_type.setter
    def model_type(self, value):
        self._pedb.active_cell.SetProductProperty(
            self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_MODEL_TYPE, value.lower()
        )

    @property
    def adaptive_refinement_cg_max_passes(self):
        """
        Gets the maximum number of passes for CG adaptive refinement from the database.

        Returns:
            int: The maximum number of passes for CG adaptive refinement.
        """
        return int(
            self._pedb.active_cell.GetProductProperty(
                self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_ADAPTIVE_REFINEMENT_CG_MAX_PASSES
            )[-1]
        )

    @adaptive_refinement_cg_max_passes.setter
    def adaptive_refinement_cg_max_passes(self, value):
        self._pedb.active_cell.SetProductProperty(
            self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_ADAPTIVE_REFINEMENT_CG_MAX_PASSES, str(int(value))
        )

    @property
    def adaptive_refinement_cg_percent_error(self):
        """
        Gets the target error percentage for CG adaptive refinement from the database.

        Returns:
            float: The target error percentage for CG adaptive refinement.
        """
        return float(
            self._pedb.active_cell.GetProductProperty(
                self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_ADAPTIVE_REFINEMENT_CG_PERCENT_ERROR
            )[-1]
        )

    @adaptive_refinement_cg_percent_error.setter
    def adaptive_refinement_cg_percent_error(self, value):
        self._pedb.active_cell.SetProductProperty(
            self._pedb._edb.ProductId.SIWave,
            SIwaveProperties.CPA_ADAPTIVE_REFINEMENT_CG_PERCENT_ERROR,
            str(float(value)),
        )

    @property
    def cg_percent_refinement_per_pass(self):
        """
        Gets the percentage of CG refinement per pass from the database.

        Returns:
            float: The percentage of CG refinement per pass.
        """
        return float(
            self._pedb.active_cell.GetProductProperty(
                self._pedb._edb.ProductId.SIWave,
                SIwaveProperties.CPA_ADAPTIVE_REFINEMENT_CG_PERCENT_REFINEMENT_PER_PASS,
            )[-1]
        )

    @cg_percent_refinement_per_pass.setter
    def cg_percent_refinement_per_pass(self, value):
        self._pedb.active_cell.SetProductProperty(
            self._pedb._edb.ProductId.SIWave,
            SIwaveProperties.CPA_ADAPTIVE_REFINEMENT_CG_PERCENT_REFINEMENT_PER_PASS,
            str(float(value)),
        )

    @property
    def adaptive_refinement_rl_max_passes(self):
        """
        Gets the maximum number of passes for RL adaptive refinement from the database.

        Returns:
            int: The maximum number of passes for RL adaptive refinement.
        """
        return int(
            float(
                self._pedb.active_cell.GetProductProperty(
                    self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_ADAPTIVE_REFINEMENT_RL_MAX_PASSES
                )[-1]
            )
        )

    @adaptive_refinement_rl_max_passes.setter
    def adaptive_refinement_rl_max_passes(self, value):
        self._pedb.active_cell.SetProductProperty(
            self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_ADAPTIVE_REFINEMENT_RL_MAX_PASSES, str(float(value))
        )

    @property
    def adaptive_refinement_rl_percent_error(self):
        """
        Gets the target error percentage for RL adaptive refinement from the database.

        Returns:
            float: The target error percentage for RL adaptive refinement.
        """
        return float(
            self._pedb.active_cell.GetProductProperty(
                self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_ADAPTIVE_REFINEMENT_RL_PERCENT_ERROR
            )[-1]
        )

    @adaptive_refinement_rl_percent_error.setter
    def adaptive_refinement_rl_percent_error(self, value):
        self._pedb.active_cell.SetProductProperty(
            self._pedb._edb.ProductId.SIWave,
            SIwaveProperties.CPA_ADAPTIVE_REFINEMENT_RL_PERCENT_ERROR,
            str(float(value)),
        )

    @property
    def rl_percent_refinement_per_pass(self):
        """
        Gets the percentage of RL refinement per pass from the database.

        Returns:
            float: The percentage of RL refinement per pass.
        """
        return float(
            self._pedb.active_cell.GetProductProperty(
                self._pedb._edb.ProductId.SIWave,
                SIwaveProperties.CPA_ADAPTIVE_REFINEMENT_RL_PERCENT_REFINEMENT_PER_PASS,
            )[-1]
        )

    @rl_percent_refinement_per_pass.setter
    def rl_percent_refinement_per_pass(self, value):
        self._pedb.active_cell.SetProductProperty(
            self._pedb._edb.ProductId.SIWave,
            SIwaveProperties.CPA_ADAPTIVE_REFINEMENT_RL_PERCENT_REFINEMENT_PER_PASS,
            str(float(value)),
        )

    @property
    def return_path_net_for_loop_parameters(self):
        """
        Gets the return path net setting for loop parameters from the database.

        Returns:
            bool: True if the return path net is enabled for loop parameters, False otherwise.
        """
        _res = self._pedb.active_cell.GetProductProperty(
            self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_RETURN_PATH_NET_FOR_LOOP_PARAMS
        )[-1]
        if _res == "1":
            return True
        return False

    @return_path_net_for_loop_parameters.setter
    def return_path_net_for_loop_parameters(self, value):
        if value:
            self._pedb.active_cell.SetProductProperty(
                self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_RETURN_PATH_NET_FOR_LOOP_PARAMS, "1"
            )
        else:
            self._pedb.active_cell.SetProductProperty(
                self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_RETURN_PATH_NET_FOR_LOOP_PARAMS, "0"
            )


class SIWaveCPASimulationSetup:
    """
    Represents the setup configuration for SIwave CPA simulations.

    Attributes:
        _pedb: The database object representing the active cell.
        _channel_setup (ChannelSetup): The channel setup configuration.
        _solver_options (SolverOptions): The solver options configuration.
    """

    def __init__(self, pedb, name=None, siwave_cpa_setup_class=None):
        self._pedb = pedb
        self._channel_setup = ChannelSetup(pedb)
        self._solver_options = SolverOptions(pedb)
        self.type = "cpa"
        if isinstance(siwave_cpa_setup_class, SIwaveCpaSetup):
            self._apply_cfg_object(siwave_cpa_setup_class)
        else:
            self.__init_values()

        if (
            not self._pedb.active_cell.GetProductProperty(
                self._pedb._edb.ProductId.SIWave,
                SIwaveProperties.CPA_SIM_NAME,
            )
            == name
        ):
            self._pedb.active_cell.SetProductProperty(
                self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_SIM_NAME, name
            )

    def __init_values(self):
        self.mode = "channel"
        self.model_type = "rlcg"
        self.use_q3d_solver = False
        self.net_processing_mode = "all"

    def _apply_cfg_object(self, siwave_cpa_setup_class):
        if isinstance(siwave_cpa_setup_class, SIwaveCpaSetup):
            self.name = siwave_cpa_setup_class.name
            self.mode = siwave_cpa_setup_class.mode
            self.nets_to_process = siwave_cpa_setup_class.nets_to_process
            self.model_type = siwave_cpa_setup_class.model_type
            self.use_q3d_solver = siwave_cpa_setup_class.use_q3d_solver
            self.net_processing_mode = siwave_cpa_setup_class.net_processing_mode
            self.channel_setup = ChannelSetup(self._pedb, siwave_cpa_setup_class.channel_setup)
            self.solver_options = SolverOptions(self._pedb, siwave_cpa_setup_class.solver_options)

    @property
    def name(self) -> str:
        """
        Gets the name of the simulation setup.

        Returns:
            str: The name of the simulation setup.
        """
        return self._pedb.active_cell.GetProductProperty(
            self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_SIM_NAME
        )[-1]

    @name.setter
    def name(self, value):
        self._pedb.active_cell.SetProductProperty(
            self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_SIM_NAME, value
        )

    @property
    def mode(self):
        """
        Gets the mode of the simulation setup.

        Returns:
            str: The mode of the simulation setup ("channel" or "no_channel").
        """
        cpa_mode = self._pedb.active_cell.GetProductProperty(
            self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_CHANNEL_SETUP
        )[-1]
        if cpa_mode == "1":
            return "channel"
        return "no_channel"

    @mode.setter
    def mode(self, value):
        if value == "channel":
            self._pedb.active_cell.SetProductProperty(
                self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_CHANNEL_SETUP, "1"
            )
        else:
            self._pedb.active_cell.SetProductProperty(
                self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_CHANNEL_SETUP, "0"
            )

    @property
    def model_type(self):
        """
        Gets the model type of the simulation setup.

        Returns:
            str: The model type ("rlcg" or "esd_r").
        """
        mod_type = self._pedb.active_cell.GetProductProperty(
            self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_ESD_R_MODEL
        )[-1]
        if mod_type == "0":
            return "rlcg"
        else:
            return "esd_r"

    @model_type.setter
    def model_type(self, value):
        if value == "rlcg":
            self._pedb.active_cell.SetProductProperty(
                self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_ESD_R_MODEL, "0"
            )
        elif value == "esd_r":
            self._pedb.active_cell.SetProductProperty(
                self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_ESD_R_MODEL, "1"
            )

    @property
    def use_q3d_solver(self):
        """
        Gets the Q3D solver usage setting.

        Returns:
            bool: True if the Q3D solver is used, False otherwise.
        """
        return bool(
            int(
                self._pedb.active_cell.GetProductProperty(
                    self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_USE_Q3D_SOLVER
                )[-1]
            )
        )

    @use_q3d_solver.setter
    def use_q3d_solver(self, value):
        if value:
            self._pedb.active_cell.SetProductProperty(
                self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_USE_Q3D_SOLVER, "1"
            )
        else:
            self._pedb.active_cell.SetProductProperty(
                self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_USE_Q3D_SOLVER, "0"
            )

    @property
    def net_processing_mode(self):
        """
        Gets the net processing mode.

        Returns:
            str: The net processing mode.
        """
        return self._pedb.active_cell.GetProductProperty(
            self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_NET_PROCESSING_MODE
        )[-1]

    @net_processing_mode.setter
    def net_processing_mode(self, value):
        self._pedb.active_cell.SetProductProperty(
            self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_NET_PROCESSING_MODE, str(value)
        )

    @property
    def channel_setup(self):
        """
        Gets the channel setup configuration.

        Returns:
            ChannelSetup: The channel setup configuration.
        """
        return self._channel_setup

    @channel_setup.setter
    def channel_setup(self, value):
        if isinstance(value, ChannelSetup):
            self._channel_setup = value

    @property
    def solver_options(self):
        """
        Gets the solver options configuration.

        Returns:
            SolverOptions: The solver options configuration.
        """
        return self._solver_options

    @solver_options.setter
    def solver_options(self, value):
        if isinstance(value, SolverOptions):
            self._solver_options = value

    @property
    def nets_to_process(self):
        """
        Gets the list of nets to process.

        Returns:
            list: A list of nets to process.
        """
        nets = self._pedb.active_cell.GetProductProperty(
            self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_NETS_TO_PROCESS
        )[-1]
        return nets.split("*")

    @nets_to_process.setter
    def nets_to_process(self, value):
        if isinstance(value, list):
            nets = "*".join(value)
            self._pedb.active_cell.SetProductProperty(
                self._pedb._edb.ProductId.SIWave, SIwaveProperties.CPA_NETS_TO_PROCESS, nets
            )
        else:
            raise TypeError("nets_to_process must be a list of strings.")
