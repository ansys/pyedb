from dataclasses import dataclass, field

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class SolverOptions:
    extraction_mode: str = "si"


@dataclass_json
@dataclass
class Vrm:
    voltage: float = 0.0
    pwr_net: str = ""
    gnd_net: str = ""


@dataclass_json
@dataclass
class ChannelConfiguration:
    die_name: str = ""
    pin_grouping_mode: str = "perpin"  # usediepingroups and ploc are supported
    channel_comp_exposure: list[str] = field(default_factory=list)
    expose: bool = True


@dataclass_json
@dataclass
class SIwaveCPAProperties:
    name: str = ""
    mode: str = "channel"
    model_type: str = "rlcg"
    use_q3d_solcer: bool = True
    net_processing_mode: str = "userspecified"
    return_path_net_for_loop_params: str = ""
