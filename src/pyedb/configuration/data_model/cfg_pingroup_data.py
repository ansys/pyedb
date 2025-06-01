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
    pingroup: str = ""


@dataclass_json
@dataclass
class CfgTerminal:
    pingroup: str = ""
