from enum import Enum

from pyedb.misc.siw_feature_config.xtalk_scan.impedance_scan_config import (
    ImpdedanceScan,
)


class ScanType(Enum):
    IMPEDANCE = 0
    FREQ_XTALK = 1
    TIME_XTALK = 2


class SiwaveScanConfig:
    def __init__(self):
        self.scan_type = ScanType.IMPEDANCE
        self.impedance_scan_config = ImpdedanceScan()
