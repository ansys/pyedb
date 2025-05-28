from dataclasses import dataclass


@dataclass
class CfgDefinition:
    name: str
    hole_diameter: str
    hole_plating_thickness: str
    hole_material: str
    hole_range: str = "through"


@dataclass
class CfgBackDrillTop:
    drill_to_layer: str
    drill_diameter: str
    stub_length: str


@dataclass
class CfgBackDrillBottom:
    drill_to_layer: str
    drill_diameter: str
    stub_length: str


@dataclass
class CfgInstance:
    name: str
    backdrill_top: CfgBackDrillTop
    backdrill_bottom: CfgBackDrillBottom


@dataclass
class CfgPadStacks:
    definitions: list[CfgDefinition] = "default_factory"
    instances: list[CfgInstance] = "default_factory"
