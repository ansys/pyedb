# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from enum import Enum
import os
import xml.etree as ET

from pyedb.generic.general_methods import ET
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
    """XML control file handle for Siwave crosstalk scan."""

    def __init__(self, pedb, scan_type="impedance"):
        self._pedb = pedb
        self.file_path = ""
        if scan_type == "impedance":
            self.scan_type = ScanType.IMPEDANCE
        elif scan_type == "frequency_xtalk":
            self.scan_type = ScanType.FREQ_XTALK
        elif scan_type == "time_xtalk":
            self.scan_type = ScanType.TIME_XTALK
        else:
            self._pedb.logger.error(f"No valid scan type argument : {scan_type}")
            self._pedb.logger.error('Supported argument : "impedance", "frequency_xtalk", "time_xtalk"')

        self.impedance_scan = ImpedanceScan(self._pedb)
        self.frequency_xtalk_scan = CrosstalkFrequency(self._pedb)
        self.time_xtalk_scan = CrossTalkTime(self._pedb)

    def write_xml(self):
        """Write XML control file

        Returns
        -------
        bool
        """
        if not self.file_path:
            self._pedb.logger.error("No xml file path provided, please provide absolute valid one.")
            return False
        self._pedb.logger.info(f"Parsing xml file")
        scan_config = ET.Element("SiwaveScanConfig")
        scan_config.set("xmlns", "http://webstds.ipc.org/2581")
        scan_config.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        if self.scan_type == ScanType.IMPEDANCE:
            self.impedance_scan.extend_xml(scan_config)
        elif self.scan_type == ScanType.FREQ_XTALK:
            self.frequency_xtalk_scan.extend_xml(scan_config)
        elif self.scan_type == ScanType.TIME_XTALK:
            self.time_xtalk_scan.extend_xml(scan_config)
        try:
            ET.indent(scan_config)
        except AttributeError:
            pass
        tree = ET.ElementTree(scan_config)
        self._pedb.logger.info(f"Writing xml file")
        tree.write(self.file_path)
        return True if os.path.exists(self.file_path) else False
