from dataclasses import dataclass


@dataclass
class CfgFrequency:
    distribution: str
    start: float
    stop: float
    step: float
    points: int
    samples: int


@dataclass
class CfgFrequencySweep:
    name: str
    type: str
    frequencies: list[CfgFrequency]


@dataclass
class CfgDcIrSettings:
    export_dc_thermal_data: bool


@dataclass
class CfgSetup:
    name: str
    type: str
    f_adapt: str
    max_num_passes: int
    max_mag_delta_s: float
    dc_slider_position: int
    dc_ir_settings: CfgDcIrSettings


@dataclass
class CfgSetups:
    setups: list[CfgSetup] = "default_factory"
