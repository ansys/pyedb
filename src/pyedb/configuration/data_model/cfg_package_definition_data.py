from dataclasses import dataclass

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class CfgHeatSink:
    fin_base_height: float = 0.0
    fin_height: float = 0.0
    fin_orientation: str = str
    fin_spacing: float = 0.0
    fin_thickness: float = 0.0


@dataclass_json
@dataclass
class CfgPackageDefinition:
    name: str = ""
    component_definition: str = ""
    maximum_power: float = 0.0
    therm_cond: float = 0.0
    theta_jb: float = 0.0
    theta_jc: float = 0.0
    height: float = 0.0
    heatsink: CfgHeatSink = None
