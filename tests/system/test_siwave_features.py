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

"""Tests related to Edb"""

import os

from defusedxml.ElementTree import parse as defused_parse
import pytest

from tests.system.base_test_class import BaseTestClass

pytestmark = [pytest.mark.system, pytest.mark.legacy]


@pytest.mark.usefixtures("close_rpc_session")
class TestClass(BaseTestClass):
    @pytest.fixture(autouse=True)
    def init(self, edb_examples, local_scratch, target_path, target_path2, target_path4):
        self.edbapp = edb_examples.get_si_verse()
        self.local_scratch = local_scratch
        self.target_path = target_path
        self.target_path2 = target_path2
        self.target_path4 = target_path4

    def test_create_impedance_scan(self):
        xtalk_scan = self.edbapp.siwave.create_impedance_crosstalk_scan(scan_type="impedance")
        for net in list(self.edbapp.nets.signal.keys()):
            xtalk_scan.impedance_scan.add_single_ended_net(
                name=net, nominal_impedance=45.0, warning_threshold=40.0, violation_threshold=30.0
            )
        xtalk_scan.file_path = os.path.join(self.local_scratch.path, "test_impedance_scan.xml")
        assert xtalk_scan.write_xml()
        tree = defused_parse(xtalk_scan.file_path)
        root = tree.getroot()
        nets = [child for child in root[0] if "SingleEndedNets" in child.tag][0]
        assert len(nets) == 342
        for net in nets:
            net_dict = net.attrib
            assert net_dict["Name"]
            assert float(net_dict["NominalZ0"]) == 45.0
            assert float(net_dict["WarningThreshold"]) == 40.0
            assert float(net_dict["ViolationThreshold"]) == 30.0

    def test_create_frequency_xtalk_scan(self):
        xtalk_scan = self.edbapp.siwave.create_impedance_crosstalk_scan(scan_type="frequency_xtalk")
        for net in list(self.edbapp.nets.signal.keys()):
            xtalk_scan.frequency_xtalk_scan.add_single_ended_net(
                name=net,
                next_warning_threshold=5.0,
                next_violation_threshold=8.0,
                fext_warning_threshold_warning=8.0,
                fext_violation_threshold=10.0,
            )

        xtalk_scan.file_path = os.path.join(self.local_scratch.path, "test_impedance_scan.xml")
        assert xtalk_scan.write_xml()
        tree = defused_parse(xtalk_scan.file_path)
        root = tree.getroot()
        nets = [child for child in root[0] if "SingleEndedNets" in child.tag][0]
        assert len(nets) == 342
        for net in nets:
            net_dict = net.attrib
            assert net_dict["Name"]
            assert float(net_dict["FEXTWarningThreshold"]) == 8.0
            assert float(net_dict["FEXTViolationThreshold"]) == 10.0
            assert float(net_dict["NEXTWarningThreshold"]) == 5.0
            assert float(net_dict["NEXTViolationThreshold"]) == 8.0

    def test_create_time_xtalk_scan(self):
        xtalk_scan = self.edbapp.siwave.create_impedance_crosstalk_scan(scan_type="time_xtalk")
        for net in list(self.edbapp.nets.signal.keys()):
            xtalk_scan.time_xtalk_scan.add_single_ended_net(
                name=net, driver_rise_time="132ps", voltage="2.4V", driver_impedance=45.0, termination_impedance=51.0
            )
        driver_pins = [pin for pin in list(self.edbapp.components["U1"].pins.values()) if "DDR4" in pin.net_name]
        receiver_pins = [pin for pin in list(self.edbapp.components["U1"].pins.values()) if pin.net_name == "GND"]
        for pin in driver_pins:
            xtalk_scan.time_xtalk_scan.add_driver_pins(
                name=pin.name, ref_des="U1", rise_time="20ps", voltage="1.2V", impedance=120.0
            )
        for pin in receiver_pins:
            xtalk_scan.time_xtalk_scan.add_receiver_pin(name=pin.name, ref_des="U1", impedance=80.0)
        xtalk_scan.file_path = os.path.join(self.local_scratch.path, "test_impedance_scan.xml")
        assert xtalk_scan.write_xml()
        tree = defused_parse(xtalk_scan.file_path)
        root = tree.getroot()
        nets = [child for child in root[0] if "SingleEndedNets" in child.tag][0]
        assert len(nets) == 342
        driver_pins = [child for child in root[0] if "DriverPins" in child.tag][0]
        assert len(driver_pins) == 120
        receiver_pins = [child for child in root[0] if "ReceiverPins" in child.tag][0]
        assert len(receiver_pins) == 403
        for net in nets:
            net_dict = net.attrib
            assert net_dict["Name"]
            assert net_dict["DriverRiseTime"] == "132ps"
            assert net_dict["Voltage"] == "2.4V"
            assert float(net_dict["DriverImpedance"]) == 45.0
            assert float(net_dict["TerminationImpedance"]) == 51.0
        for pin in driver_pins:
            pin_dict = pin.attrib
            assert pin_dict["Name"]
            assert pin_dict["RefDes"] == "U1"
            assert pin_dict["DriverRiseTime"] == "20ps"
            assert pin_dict["Voltage"] == "1.2V"
            assert float(pin_dict["DriverImpedance"]) == 120.0
        for pin in receiver_pins:
            pin_dict = pin.attrib
            assert pin_dict["Name"]
            assert float(pin_dict["ReceiverImpedance"]) == 80.0
