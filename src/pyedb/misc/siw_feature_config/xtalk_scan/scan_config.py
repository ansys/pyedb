from enum import Enum

from pyedb.misc.siw_feature_config.xtalk_scan.fd_xtalk_scan_config import (
    CrosstalkFrequency,
)
from pyedb.misc.siw_feature_config.xtalk_scan.impedance_scan_config import ImpedanceScan
from pyedb.misc.siw_feature_config.xtalk_scan.td_xtalk_config import CrossTalkTime


class ScanType(Enum):
    IMPEDANCE = 0
    FREQ_XTALK = 1
    TIME_XTALK = 2


class SiwaveScanConfig:
    def __init__(self):
        self.scan_type = ScanType.IMPEDANCE
        self.impedance_scan = ImpedanceScan()
        self.frequency_xtalk_scan = CrosstalkFrequency()
        self.time_xtalk_scan = CrossTalkTime()

    def write_wml(self):
        pass
