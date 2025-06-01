from dataclasses import dataclass, field

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class CfgSparameter:
    name: str = ""
    component_definition: str = ""
    file_path: str = ""
    apply_to_all: bool = True
    components: list[str] = field(default_factory=list)
    reference_net: str = ""
    reference_net_per_component: dict[str, str] = field(default_factory=dict)
