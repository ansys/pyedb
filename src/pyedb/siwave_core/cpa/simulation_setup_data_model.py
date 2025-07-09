from dataclasses import dataclass, field


@dataclass
class SolverOptions:
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


@dataclass
class Vrm:
    name: str = ""
    voltage: float = 0.0
    power_net: str = ""
    reference_net: str = ""


@dataclass
class ChannelSetup:
    die_name: str = ""
    pin_grouping_mode: str = "perpin"  # usediepingroups and ploc are supported
    channel_component_exposure: dict[str, bool] = field(default_factory=dict)
    vrm_setup: list[Vrm] = field(default_factory=list)


@dataclass
class SIwaveCpaSetup:
    name: str = ""
    mode: str = "channel"
    model_type: str = "rlcg"
    use_q3d_solver: bool = True
    net_processing_mode: str = "userspecified"
    return_path_net_for_loop_parameters: str = ""
    channel_setup: ChannelSetup = field(default_factory=ChannelSetup)
    solver_options: SolverOptions = field(default_factory=SolverOptions)
    nets_to_process: list[str] = field(default_factory=list)
