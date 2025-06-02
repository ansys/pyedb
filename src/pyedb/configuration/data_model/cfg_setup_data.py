from dataclasses import dataclass, field

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class CfgFrequency:
    distribution: str = ""
    start: float = 0.0
    stop: float = 0.0
    step: float = 0.0
    points: int = 0
    samples: int = 0


@dataclass_json
@dataclass
class CfgFrequencySweep:
    name: str = ""
    type: str = ""
    frequencies: list[CfgFrequency] = field(default_factory=list)


@dataclass_json
@dataclass
class CfgDcIrSettings:
    export_dc_thermal_data: bool = False


@dataclass_json
@dataclass
class CfgSetup:
    name: str = ""
    type: str = ""
    f_adapt: str = ""
    max_num_passes: int = 20
    max_mag_delta_s: float = 0.02
    dc_slider_position: int = 1
    dc_ir_settings: CfgDcIrSettings = None
    freq_sweep: CfgFrequencySweep = None
