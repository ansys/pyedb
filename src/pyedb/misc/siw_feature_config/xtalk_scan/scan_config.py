from enum import Enum


class ScanType(Enum):
    IMPEDANCE = 0
    FREQ_XTALK = 1
    TIME_XTALK = 2


class SiwaveScanConfig:
    def __init__(self):
        self.scan_type = ScanType.IMPEDANCE
