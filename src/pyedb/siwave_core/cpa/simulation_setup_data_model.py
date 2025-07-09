from typing import Dict, List

from pydantic import BaseModel, Field


class SolverOptions(BaseModel):
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
    name: str = ""
    voltage: float = 0.0
    power_net: str = ""
    reference_net: str = ""


class ChannelSetup(BaseModel):
    die_name: str = ""
    pin_grouping_mode: str = "perpin"
    channel_component_exposure: Dict[str, bool] = Field(default_factory=dict)
    vrm_setup: List[Vrm] = Field(default_factory=list)


class SIwaveCpaSetup(BaseModel):
    name: str = ""
    mode: str = "channel"
    model_type: str = "rlcg"
    use_q3d_solver: bool = True
    net_processing_mode: str = "userspecified"
    return_path_net_for_loop_parameters: str = ""
    channel_setup: ChannelSetup = Field(default_factory=ChannelSetup)
    solver_options: SolverOptions = Field(default_factory=SolverOptions)
    nets_to_process: List[str] = Field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict) -> "SIwaveCpaSetup":
        """Convert dictionary to SIwaveCpaSetup object."""
        if "channel_setup" in data:
            data["channel_setup"] = ChannelSetup(**data["channel_setup"])
        if "solver_options" in data:
            data["solver_options"] = SolverOptions(**data["solver_options"])
        return cls(**data)

    def to_dict(self) -> Dict:
        """Convert SIwaveCpaSetup object to dictionary."""
        data = self.model_dump()
        if self.channel_setup:
            data["channel_setup"] = self.channel_setup.model_dump()
        if self.solver_options:
            data["solver_options"] = self.solver_options.model_dump()
        return data
