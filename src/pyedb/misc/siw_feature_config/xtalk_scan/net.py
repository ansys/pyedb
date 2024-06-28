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


class SingleEndedNet:
    """Single ended net class handler."""

    def __init__(self):
        self.name = None
        self.nominal_impedance = None
        self.warning_threshold = None
        self.violation_threshold = None
        self.fext_warning_threshold = None
        self.fext_violation_threshold = None
        self.next_warning_threshold = None
        self.next_violation_threshold = None
        self.driver_rise_time = None
        self.voltage = None
        self.driver_impedance = None
        self.termination_impedance = None

    def extend_xml(self, parent):
        """Write XMl object section."""
        net = ET.SubElement(parent, "Net")
        if self.name is not None:
            net.set("Name", self.name)
        if self.nominal_impedance is not None:
            net.set("NominalZ0", str(self.nominal_impedance))
        if self.warning_threshold is not None:
            net.set("WarningThreshold", str(self.warning_threshold))
        if self.violation_threshold is not None:
            net.set("ViolationThreshold", str(self.violation_threshold))
        if self.fext_warning_threshold is not None:
            net.set("FEXTWarningThreshold", str(self.fext_warning_threshold))
        if self.fext_violation_threshold is not None:
            net.set("FEXTViolationThreshold", str(self.fext_violation_threshold))
        if self.next_warning_threshold is not None:
            net.set("NEXTWarningThreshold", str(self.next_warning_threshold))
        if self.next_violation_threshold is not None:
            net.set("NEXTViolationThreshold", str(self.next_violation_threshold))
        if self.driver_rise_time is not None:
            net.set("DriverRiseTime", str(self.driver_rise_time))
        if self.voltage is not None:
            net.set("Voltage", str(self.voltage))
        if self.driver_impedance is not None:
            net.set("DriverImpedance", str(self.driver_impedance))
        if self.termination_impedance is not None:
            net.set("TerminationImpedance", str(self.termination_impedance))
