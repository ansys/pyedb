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

from typing import Dict, List

from pydantic import BaseModel, Field


class SolverOptions(BaseModel):
    """Configuration options for the SI-Wave solver.

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
    """

    extraction_mode: str = "si"
    custom_refinement: bool = False
    extraction_frequency: str = "10Ghz"
    compute_capacitance: bool = True
    compute_dc_parameters: bool = True
    compute_ac_rl: bool = True
    ground_power_ground_nets_for_si: bool = False
    small_hole_diameter: str = "auto"
    cg_max_passes: int = 10
    cg_percent_error: float = 0.02
    cg_percent_refinement_per_pass: float = 0.33
    rl_max_passes: int = 10
    rl_percent_error: float = 0.02
    rl_percent_refinement_per_pass: float = 0.33
    compute_dc_rl: bool = True
    compute_dc_cg: bool = True
    return_path_net_for_loop_parameters: bool = True


class Vrm(BaseModel):
    """Voltage Regulator Module configuration.

    Attributes:
        name (str): Name of the VRM, defaults to empty string
        voltage (float): Voltage value, defaults to 0.0
        power_net (str): Power net identifier, defaults to empty string
        reference_net (str): Reference net identifier, defaults to empty string
    """

    name: str = ""
    voltage: float = 0.0
    power_net: str = ""
    reference_net: str = ""


class ChannelSetup(BaseModel):
    """Channel configuration setup.

    Attributes:
        die_name (str): Name of the die, defaults to empty string
        pin_grouping_mode (str): Mode for pin grouping, defaults to "perpin"
        channel_component_exposure (Dict[str, bool]): Component exposure settings
        vrm_setup (List[Vrm]): List of VRM configurations
    """

    die_name: str = ""
    pin_grouping_mode: str = "perpin"
    channel_component_exposure: Dict[str, bool] = Field(default_factory=dict)
    vrm_setup: List[Vrm] = Field(default_factory=list)


class SIwaveCpaSetup(BaseModel):
    """Main configuration class for SI-Wave CPA (Channel Parameter Analyzer) setup.

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
    """

    name: str = ""
    mode: str = "channel"
    model_type: str = "rlcg"
    use_q3d_solver: bool = True
    net_processing_mode: str = "userspecified"
    return_path_net_for_loop_parameters: bool = True
    channel_setup: ChannelSetup = Field(default_factory=ChannelSetup)
    solver_options: SolverOptions = Field(default_factory=SolverOptions)
    nets_to_process: List[str] = Field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict) -> "SIwaveCpaSetup":
        """Convert dictionary to SIwaveCpaSetup object.

        Args:
            data (Dict): Dictionary containing SIwaveCpaSetup configuration

        Returns:
            SIwaveCpaSetup: New instance created from the dictionary
        """
        if "channel_setup" in data:
            data["channel_setup"] = ChannelSetup(**data["channel_setup"])
        if "solver_options" in data:
            data["solver_options"] = SolverOptions(**data["solver_options"])
        return cls(**data)

    def to_dict(self) -> Dict:
        """Convert SIwaveCpaSetup object to dictionary.

        Returns:
            Dict: Dictionary representation of the SIwaveCpaSetup instance
        """
        data = self.model_dump()
        if self.channel_setup:
            data["channel_setup"] = self.channel_setup.model_dump()
        if self.solver_options:
            data["solver_options"] = self.solver_options.model_dump()
        return data
