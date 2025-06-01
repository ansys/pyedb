from dataclasses import dataclass, field

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class CfgPinPair:
    type: str = "series"
    p1: str = "1"
    p2: str = "2"
    capacitance: str = None
    inductance: str = None
    resistance: str = None


@dataclass_json
@dataclass
class CfgPinPairs:
    pin_pairs: list[CfgPinPair] = field(default_factory=list)


@dataclass_json
@dataclass
class CfgSolderBallProperties:
    shape: str = "None"
    diameter: str = "0um"
    height: str = "0um"


@dataclass_json
@dataclass
class CfgPortProperties:
    reference_offset: float = 0
    reference_size_auto: bool = True
    reference_size_x: float = 0.0
    reference_size_y: float = 0.0


@dataclass_json
@dataclass
class CfgComponent:
    reference_designator: str = ""
    part_type: str = ""
    enabled: bool = True
    rlc_model: CfgPinPairs = None
    solder_ball_properties: CfgSolderBallProperties = None
    port_properties: CfgPortProperties = None


@dataclass_json
@dataclass
class CfgComponents:
    components: list[CfgComponent]
