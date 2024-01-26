from enum import Enum


class Type(Enum):
    CIRCUIT = 1
    COAXIAL = 2


class Pin:
    def __init__(self):
        self.component = ""
        self.name = ""


class Port(Type):
    def __init__(self):
        self.name = ""
        self.refdes = ""
        self.type = Type.COAXIAL
        self.positive_pin = Pin()
        self.negative_pin = Pin()
