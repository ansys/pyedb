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
from pyedb.misc.siw_feature_config.xtalk_scan.pins import DriverPin, ReceiverPin


class CrossTalkTime:
    """Time domain crosstalk configuration class handler."""

    def __init__(self, pedb):
        self._pedb = pedb
        self.nets = {}
        self.driver_pins = []
        self.receiver_pins = []

    def add_single_ended_net(
        self,
        name,
        driver_rise_time=5.0,
        voltage=10,
        driver_impedance=5.0,
        termination_impedance=5.0,
    ):
        """Add single ended net.

        Parameters
        ----------
        name : str
            Net name.
        driver_rise_time : flot or str
            Near end crosstalk warning threshold value. Default value is ``5.0``.
        voltage : float, str
            Near end crosstalk violation threshold value. Default value is ``10.0

        driver_impedance : float, str
            Far end crosstalk violation threshold value, Default value is ``5.0``
        termination_impedance : float, str
            Far end crosstalk warning threshold value, Default value is ``5.0``

        Returns
        -------
        bool
        """
        if name and name not in self.nets:
            net = SingleEndedNet()
            net.name = name
            net.driver_rise_time = driver_rise_time
            net.voltage = voltage
            net.driver_impedance = driver_impedance
            net.termination_impedance = termination_impedance
            self.nets[name] = net
            return True
        else:
            self._pedb.logger.error(f"Net {name} already assigned.")
            return False

    def add_driver_pins(self, name, ref_des, rise_time="100ps", voltage=1.0, impedance=50.0):
        pin = DriverPin()
        pin.name = name
        pin.ref_des = ref_des
        pin.driver_rise_time = rise_time
        pin.voltage = voltage
        pin.driver_impedance = impedance
        self.driver_pins.append(pin)

    def add_receiver_pin(self, name, ref_des, impedance):
        pin = ReceiverPin()
        pin.name = name
        pin.ref_des = ref_des
        pin.receiver_impedance = impedance
        self.receiver_pins.append(pin)

    def extend_xml(self, parent):
        time_scan = ET.SubElement(parent, "TdXtalkConfig")
        single_ended_nets = ET.SubElement(time_scan, "SingleEndedNets")
        for net in list(self.nets.values()):
            net.extend_xml(single_ended_nets)
        driver_pins = ET.SubElement(time_scan, "DriverPins")
        for pin in self.driver_pins:
            pin.extend_xml(driver_pins)
        receiver_pins = ET.SubElement(time_scan, "ReceiverPins")
        for pin in self.receiver_pins:
            pin.extend_xml(receiver_pins)
