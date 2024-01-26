from enum import Enum


class SimulationType(Enum):
    HFSS = 1
    SIWAVE_SYZ = 2
    SIWAVE_DC = 3


class SweepType(Enum):
    INTERPOLATING = 1
    DISCRETE = 2


class SweepDistributionType(Enum):
    LINEAR = 1
    DECADE_COUNT = 2


class FrequencySweep:
    def __init__(self):
        self.sweep_type = SweepType.INTERPOLATING
        self.distribution_type = SweepDistributionType.LINEAR
        self.start_frequency = "0GHz"
        self.stop_frequency = "20GHz"
        self.step_frequency = "10MHz"


class SimulationSetup(SimulationType):
    def __init__(self):
        self.name = ""
        self.type = SimulationType.HFSS
        self.adaptive_frequency = "5GHz"
        self.max_num_passes = 10
        self.max_delta_s = 0.02
        self.sweep = FrequencySweep()
