# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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
    """
    SIwave frequency domain crosstalk configuration handler.

    This class manages frequency domain crosstalk scanning configuration including
    transmission line segment length, frequency, and net-specific crosstalk thresholds.

    Parameters
    ----------
    pedb : object
        PyEDB instance.

    Examples
    --------
    >>> from pyedb import Edb
    >>> edb = Edb("path/to/aedb")
    >>> xtalk_freq = CrosstalkFrequency(edb)
    >>> xtalk_freq.min_transmission_line_segment_length = "0.5mm"
    >>> xtalk_freq.frequency = "5e9Hz"
    >>> xtalk_freq.add_single_ended_net("USB_DP", next_warning_threshold=3.0, fext_warning_threshold=2.0)

    """

    def __init__(self, pedb) -> None:
        """
        Initialize frequency domain crosstalk configuration.

        Parameters
        ----------
        pedb : object
            PyEDB instance.

        """
        self._pedb = pedb
        self.min_transmission_line_segment_length: str = "0.25mm"
        self.frequency: str = "2e9Hz"
        self.nets: dict[str, SingleEndedNet] = {}

    def extend_xml(self, parent) -> None:
        """
        Write class XML section.

        Parameters
        ----------
        parent : xml.etree.ElementTree.Element
            Parent XML element to extend.

        """
        freq_scan = ET.SubElement(parent, "FdXtalkConfig")
        freq_scan.set("MinTlineSegmentLength", self.min_transmission_line_segment_length)
        freq_scan.set("XtalkFrequency", self.frequency)
        nets = ET.SubElement(freq_scan, "SingleEndedNets")
        for net in list(self.nets.values()):
            net.extend_xml(nets)

    def add_single_ended_net(
        self,
        name: str,
        next_warning_threshold: float | str = 5.0,
        next_violation_threshold: float | str = 10.0,
        fext_warning_threshold_warning: float | str = 5.0,
        fext_violation_threshold: float | str = 5.0,
    ) -> bool:
        """
        Add single ended net to frequency domain crosstalk configuration.

        Parameters
        ----------
        name : str
            Net name.
        next_warning_threshold : float or str, optional
            Near end crosstalk warning threshold value in dB.
            The default is ``5.0``.
        next_violation_threshold : float or str, optional
            Near end crosstalk violation threshold value in dB.
            The default is ``10.0``.
        fext_warning_threshold_warning : float or str, optional
            Far end crosstalk warning threshold value in dB.
            The default is ``5.0``.
        fext_violation_threshold : float or str, optional
            Far end crosstalk violation threshold value in dB.
            The default is ``5.0``.

        Returns
        -------
        bool
            ``True`` if the net was added successfully, ``False`` otherwise.

        Examples
        --------
        >>> xtalk_freq = CrosstalkFrequency(pedb)
        >>> xtalk_freq.add_single_ended_net("USB_DP", next_warning_threshold=3.0, fext_warning_threshold=2.0)
        True

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
