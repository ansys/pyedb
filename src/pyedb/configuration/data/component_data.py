from enum import Enum


class PinpairModel:
    def __init__(self):
        self.type = "series"
        self.pin1 = ""
        self.pin2 = ""


class RlcModel:
    def __init__(self):
        self._model = [PinpairModel()]


class Type(Enum):
    RESISTOR = 1
    CAPACITOR = 2
    INDUCTOR = 3
    IO = 4
    IC = 5
    OTHER = 6


class Component(Type):
    def __init__(self):
        self.part_type = Type.RESISTOR
        self.ref_des = ""
        self.enabled = True
        self.model = RlcModel()
