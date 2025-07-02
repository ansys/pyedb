from dataclasses import dataclass, field

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class DcParameter:
    rl: bool = True
    cg: bool = True


@dataclass_json
@dataclass
class AdaptiveSettings:
    cg_max_passes: int = 10
    cg_percent_error: float = 0.02
    cg_percent_refinement_per_pass: float = 0.33
    rl_max_passes: int = 10
    rl_percent_error: float = 0.02
    rl_percent_refinement_per_pass: float = 0.33


@dataclass_json
@dataclass
class SolverOptions:
    extraction_mode: str = "si"
    custom_refinement: bool = False
    extraction_frequency: str = "10Ghz"
    compute_capacitance: bool = True
    compute_dc_parameters: bool = True
    dc_parameters: DcParameter = None
    compute_ac_rl: bool = True
    ground_power_ground_nets_for_si: bool = False
    small_hole_diameter: str = "auto"
    adaptive_settings: AdaptiveSettings = None


@dataclass_json
@dataclass
class Vrm:
    voltage: float = 0.0
    pwr_net: str = ""
    gnd_net: str = ""


@dataclass_json
@dataclass
class ChannelSetup:
    die_name: str = ""
    pin_grouping_mode: str = "perpin"  # usediepingroups and ploc are supported
    channel_component_exposure: list[str] = field(default_factory=list)
    vrm_setup: Vrm = None


@dataclass_json
@dataclass
class SIwaveCpaSetup:
    name: str = ""
    mode: str = "channel"
    model_type: str = "rlcg"
    use_q3d_solcer: bool = True
    net_processing_mode: str = "userspecified"
    return_path_net_for_loop_parameters: str = ""
    channel_setup: ChannelSetup = None
    solver_options: SolverOptions = None
