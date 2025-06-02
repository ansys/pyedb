from dataclasses import dataclass, field
from typing import Optional

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class CfgPinPair:
    type: str = "series"
    p1: str = "1"
    p2: str = "2"
    capacitance: Optional[str] = None
    inductance: Optional[str] = None
    resistance: Optional[str] = None


@dataclass_json
@dataclass
class CfgPinPairs:
    pin_pairs: list[CfgPinPair] = field(default_factory=list)


@dataclass_json
@dataclass
class CfgSolderBallProperties:
    shape: Optional[str] = "None"
    diameter: Optional[str] = "0um"
    height: Optional[str] = "0um"


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
    enabled: Optional[bool] = True
    rlc_model: Optional[CfgPinPairs] = None
    solder_ball_properties: Optional[CfgSolderBallProperties] = None
    port_properties: Optional[CfgPortProperties] = None


@dataclass_json
@dataclass
class CfgComponents:
    components: list[CfgComponent]
