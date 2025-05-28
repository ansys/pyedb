from dataclasses import dataclass
from typing import Union


@dataclass
class CfgMaterial:
    name: str
    conductivity: float
    permittivity: float
    dielectric_loss_tangent: float


@dataclass
class CfgLayer:
    fill_material: str
    material: str
    name: str
    thickness: Union[str, float]
    type: str


@dataclass
class CfgStackup:
    materials: [CfgMaterial] = "default_factory"
    layers: [] = "default_factory"
