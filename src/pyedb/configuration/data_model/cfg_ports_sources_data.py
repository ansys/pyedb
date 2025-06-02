from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class CfgTerminal:
    pin: str = ""
    net: str = ""
    pin_group: str = ""


@dataclass_json
@dataclass
class CfgPort:
    name: str = ""
    reference_designator: str = ""
    type: str = ""
    positive_terminal: Optional[CfgTerminal] = None
    negative_terminal: Optional[CfgTerminal] = None


@dataclass_json
@dataclass
class CfgSource:
    name: str = ""
    reference_designator: str = ""
    type: str = ""
    magnitude: float = 0.0
    positive_terminal: CfgTerminal = None
    negative_terminal: CfgTerminal = None
