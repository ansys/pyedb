from dataclasses import dataclass


@dataclass
class CfgHeatSink:
    fin_base_height: float
    fin_height: float
    fin_orientation: str
    fin_spacing: float
    fin_thickness: float


@dataclass
class CfgPackageDefinition:
    name: str
    component_definition: str
    maximum_power: float
    therm_cond: float
    theta_jb: float
    theta_jc: float
    height: float
    heatsink: CfgHeatSink


@dataclass
class CfgPackageDefinitions:
    definitions: list[CfgPackageDefinition] = "default_factory"
