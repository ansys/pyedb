from dataclasses import dataclass

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class CfgGeneral:
    spice_model_library: str = None
    s_parameter_library: str = None
