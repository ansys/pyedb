from dataclasses import dataclass


@dataclass
class CfgTerminal:
    pin: str
    net: str


@dataclass
class CfgPort:
    name: str
    reference_designator: str
    type: str
    positive_terminal: CfgTerminal
    negative_terminal: CfgTerminal


@dataclass
class CfgSource:
    name: str
    reference_designator: str
    type: str
    magnitude: float
    positive_terminal: CfgTerminal
    negative_terminal: CfgTerminal


@dataclass
class CfgPorts:
    ports: [CfgPort] = "default_factory"


@dataclass
class CfgSources:
    sources: [CfgSource] = "default_factory"
