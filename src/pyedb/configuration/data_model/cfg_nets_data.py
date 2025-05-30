from dataclasses import dataclass, field

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class CfgNets:
    power_ground_nets: list[str] = field(default_factory=list)
    signal_nets: list[str] = field(default_factory=list)
