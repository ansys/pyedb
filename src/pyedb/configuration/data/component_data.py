from enum import Enum


class PinpairModel:
    def __init__(self):
        self._type = "series"
        self._pin1 = ""
        self._pin2 = ""


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
        self._part_type = Type.RESISTOR
        self._ref_des = ""
        self._enabled = True
        self._model = RlcModel()
