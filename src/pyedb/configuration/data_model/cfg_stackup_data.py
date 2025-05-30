from dataclasses import dataclass, field
from typing import Union

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class CfgMaterial:
    name: str = ""
    conductivity: float = 0.0
    permittivity: float = 0.0
    dielectric_loss_tangent: float = 0.0


@dataclass_json
@dataclass
class CfgLayer:
    fill_material: str = ""
    material: str = ""
    name: str = ""
    thickness: Union[str, float] = ""
    type: str = ""


@dataclass_json
@dataclass
class CfgStackup:
    materials: list[CfgMaterial] = field(default_factory=list)
    layers: list = field(default_factory=list)
