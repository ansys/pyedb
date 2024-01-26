from enum import Enum


class Material:
    def __init__(self):
        self.name = ""
        self.permittivity = 1.0
        self.conductivity = 0.0
        self.dielectric_loss_tangent = 0.0


class LayerType(Enum):
    SIGNAL = 1
    DIELECTRIC = 2


class Layer:
    def __init__(self):
        self.name = ""
        self.material = Material()
        self.filling_material = Material()
        self.thickness = 0.0
        self.type = LayerType.SIGNAL


class Stackup:
    def __init__(self):
        self.layers = [Layer]
