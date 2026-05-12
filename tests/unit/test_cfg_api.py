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

import json
from unittest.mock import MagicMock

import pytest

from pyedb.configuration.cfg_nets import CfgNets
from pyedb.configuration.cfg_operations import CfgOperations

pytestmark = [pytest.mark.unit, pytest.mark.no_licence, pytest.mark.legacy]


class TestNetsConfig:
    def test_empty(self):
        n = CfgNets()
        assert n.to_dict() == {}

    def test_signal_nets(self):
        n = CfgNets()
        n.add_signal_nets(["SIG1", "SIG2"])
        d = n.to_dict()
        assert d["signal_nets"] == ["SIG1", "SIG2"]
        assert "power_ground_nets" not in d

    def test_power_ground_nets(self):
        n = CfgNets()
        n.add_power_ground_nets(["VDD", "GND"])
        d = n.to_dict()
        assert d["power_ground_nets"] == ["VDD", "GND"]

    def test_accumulates(self):
        n = CfgNets()
        n.add_signal_nets(["A"])
        n.add_signal_nets(["B", "C"])
        assert n.to_dict()["signal_nets"] == ["A", "B", "C"]

    def test_add_reference_nets(self):
        n = CfgNets()
        n.add_reference_nets(["GND", "AGND"])
        # reference_nets are NOT serialized in to_dict (only used for cutout forwarding)
        assert "reference_nets" not in n.to_dict()
        assert n.reference_nets == ["GND", "AGND"]

    def test_reference_nets_property(self):
        n = CfgNets()
        n.add_reference_nets(["GND"])
        assert n.reference_nets == ["GND"]

    def test_signal_nets_property(self):
        n = CfgNets()
        n.add_signal_nets(["CLK", "DATA"])
        assert n.signal_nets == ["CLK", "DATA"]

    def test_power_ground_nets_property(self):
        n = CfgNets()
        n.add_power_ground_nets(["VDD"])
        assert n.power_ground_nets == ["VDD"]

    def test_reference_nets_usable_in_cutout(self):
        """Verify the reference_nets property can be passed directly to add_cutout."""
        n = CfgNets()
        n.add_signal_nets(["SIG"])
        n.add_reference_nets(["GND"])
        ops = CfgOperations()
        c = ops.add_cutout(signal_nets=n.signal_nets, reference_nets=n.reference_nets)
        d = c.to_dict()
        assert d["cutout"]["signal_list"] == ["SIG"]
        assert d["cutout"]["reference_list"] == ["GND"]
