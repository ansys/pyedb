from dataclasses import dataclass, field
from typing import Union

from dataclasses_json import dataclass_json


@dataclass_json()
@dataclass
class CfgPinGroup:
    name: str = ""
    reference_designator: str = ""
    pins: list[str] = field(default_factory=list)
    net: Union[str, list[str]] = field(default_factory=list)


@dataclass_json
@dataclass
class CfgTerminal:
    pingroup: str = ""


@dataclass_json
@dataclass
class CfgPorts:
    name: str = ""
    type: str = ""
    positive_terminal: CfgTerminal = None
    negative_terminal: CfgTerminal = None


@dataclass_json
@dataclass
class CfgSource:
    name: str = ""
    type: str = ""
    magnitude: float = 0.0
    positive_terminal: CfgTerminal = None
    negative_terminal: CfgTerminal = None
