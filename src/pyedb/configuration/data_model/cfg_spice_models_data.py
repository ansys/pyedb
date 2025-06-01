from dataclasses import dataclass, field

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class CfgSpiceModelLib:
    spice_model_library: str = ""


@dataclass_json
@dataclass
class CfgSpiceModel:
    name: str = ""
    component_definition: str = ""
    file_path: str = ""
    sub_circuit_name: str = ""
    apply_to_all: bool = True
    components: [str] = field(default_factory=list)
