from enum import Enum


class SourceType(Enum):
    VOLTAGE = 1
    CURRENT = 2


class Terminal:
    def __init__(self):
        self.refdes = ""
        self.net = ""
        self.pin = ""


class Source:
    def __init__(self):
        self.name = ""
        self.type = SourceType.VOLTAGE
        self.magnitude = 1
        self.positive_terminal = Terminal()
        self.negative_terminal = Terminal()
