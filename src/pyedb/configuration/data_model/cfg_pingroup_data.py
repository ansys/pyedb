from dataclasses import dataclass
from typing import Union


@dataclass
class CfgPinGroup:
    name: str
    reference_designator: str
    pins: list[str]
    net: Union[str, list[str]]


@dataclass
class CfgTerminal:
    pingroup: str


@dataclass
class CfgPorts:
    name: str
    type: str
    positive_terminal: CfgTerminal
    negative_terminal: CfgTerminal


@dataclass
class CfgSource:
    name: str
    type: str
    magnitude: float
    positive_terminal: CfgTerminal
    negative_terminal: CfgTerminal


@dataclass
class CfgPinGroups:
    pin_groups: list[CfgPinGroup] = "default_factory"
    ports: list[CfgPorts] = "default_factory"
    sources: list[CfgSource] = "default_factory"
