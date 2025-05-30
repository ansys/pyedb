from dataclasses import dataclass, field

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class CfgDefinition:
    name: str = ""
    hole_diameter: str = ""
    hole_plating_thickness: str = ""
    hole_material: str = ""
    hole_range: str = "through"


@dataclass_json
@dataclass
class CfgBackDrillTop:
    drill_to_layer: str = ""
    drill_diameter: str = ""
    stub_length: str = ""


@dataclass_json
@dataclass
class CfgBackDrillBottom:
    drill_to_layer: str = ""
    drill_diameter: str = ""
    stub_length: str = ""


@dataclass_json
@dataclass
class CfgInstance:
    name: str = ""
    backdrill_top: CfgBackDrillTop = None
    backdrill_bottom: CfgBackDrillBottom = None


@dataclass_json
@dataclass
class CfgPadStacks:
    definitions: list[CfgDefinition] = field(default_factory=list)
    instances: list[CfgInstance] = field(default_factory=list)
