from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class CfgGeneral:
    spice_model_library: Optional[str] = None
    s_parameter_library: Optional[str] = None
