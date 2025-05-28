from dataclasses import dataclass


@dataclass
class CfgPinPair:
    type: str
    p1: str = "1"
    p2: str = "2"
    capacitance = ""
    inductance = ""
    resistance = ""


@dataclass
class CfgSolderBallProperties:
    shape: str = "cylinder"
    diameter: str = "150um"
    height: str = "100um"


@dataclass
class CfgPortProperties:
    reference_offset: float = 0
    reference_size_auto: bool = True
    reference_size_x: float = 0.0
    reference_size_y: float = 0.0


@dataclass
class CfgComponent:
    reference_designator: str = ""
    part_type: str = ""
    enabled: bool = True
    rlc_model: dict[str, list[CfgPinPair]] = None
    solder_ball_properties: CfgSolderBallProperties = None
    port_properties: CfgPortProperties = None


@dataclass
class CfgComponents:
    components: list[CfgComponent] = "default_factory"
