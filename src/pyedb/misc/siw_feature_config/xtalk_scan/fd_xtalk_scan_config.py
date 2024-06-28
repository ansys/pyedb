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

from pyedb.generic.general_methods import ET
from pyedb.misc.siw_feature_config.xtalk_scan.net import SingleEndedNet


class CrosstalkFrequency:
    """Siwave frequency domain crosstalk configuration handler."""

    def __init__(self, pedb):
        self._pedb = pedb
        self.min_transmission_line_segment_length = "0.25mm"
        self.frequency = "2e9Hz"
        self.nets = {}

    def extend_xml(self, parent):
        """Write class xml section.

        Parameters
        ----------
        parent : :class xml.etree.cElementTree object
        Parent object.

        """
        freq_scan = ET.SubElement(parent, "FdXtalkConfig")
        freq_scan.set("MinTlineSegmentLength", self.min_transmission_line_segment_length)
        freq_scan.set("XtalkFrequency", self.frequency)
        nets = ET.SubElement(freq_scan, "SingleEndedNets")
        for net in list(self.nets.values()):
            net.extend_xml(nets)

    def add_single_ended_net(
        self,
        name,
        next_warning_threshold=5.0,
        next_violation_threshold=10.0,
        fext_warning_threshold_warning=5.0,
        fext_violation_threshold=5.0,
    ):
        """Add single ended net.

        Parameters
        ----------
        name : str
            Net name.
        next_warning_threshold : flot or str
            Near end crosstalk warning threshold value. Default value is ``5.0``.
        next_violation_threshold : float, str
            Near end crosstalk violation threshold value. Default value is ``10.0

        fext_violation_threshold : float, str
            Far end crosstalk violation threshold value, Default value is ``5.0``
        fext_warning_threshold_warning : float, str
            Far end crosstalk warning threshold value, Default value is ``5.0``

        Returns
        -------
        bool
        """
        if name and name not in self.nets:
            net = SingleEndedNet()
            net.name = name
            net.next_warning_threshold = next_warning_threshold
            net.next_violation_threshold = next_violation_threshold
            net.fext_warning_threshold = fext_warning_threshold_warning
            net.fext_violation_threshold = fext_violation_threshold
            self.nets[name] = net
            return True
        else:
            self._pedb.logger.error(f"Net {name} already assigned.")
            return False
