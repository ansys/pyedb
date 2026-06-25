# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

from unittest.mock import MagicMock

import pytest

from pyedb.configuration.cfg_nets import CfgNets
from pyedb.configuration.cfg_operations import CfgOperations

pytestmark = [pytest.mark.unit, pytest.mark.no_licence, pytest.mark.legacy]


class TestCfgNet:
    """Tests for the inner CfgNet class using a mock pedb."""

    def _make_net(self, name, is_power_ground=False):
        mock_net = MagicMock()
        mock_net.is_power_ground = is_power_ground
        mock_pedb = MagicMock()
        mock_pedb.nets.nets = {name: mock_net}
        return CfgNets.CfgNet(mock_pedb, name), mock_net

    def test_name(self):
        net, _ = self._make_net("GND")
        assert net.name == "GND"

    def test_is_power_ground_false(self):
        net, _ = self._make_net("CLK", is_power_ground=False)
        assert net.is_power_ground is False

    def test_is_power_ground_true(self):
        net, _ = self._make_net("VDD", is_power_ground=True)
        assert net.is_power_ground is True

    def test_is_power_ground_setter(self):
        net, mock_net = self._make_net("GND")
        net.is_power_ground = True
        assert mock_net.is_power_ground is True

    def test_classification_power_ground(self):
        net, _ = self._make_net("VDD", is_power_ground=True)
        assert net.classification == "power_ground"

    def test_classification_signal(self):
        net, _ = self._make_net("CLK", is_power_ground=False)
        assert net.classification == "signal"

    def test_repr(self):
        net, _ = self._make_net("GND", is_power_ground=True)
        assert "GND" in repr(net)
        assert "power_ground" in repr(net)


class TestNetsConfig:
    def test_empty(self):
        n = CfgNets()
        assert n.signal_nets == []
        assert n.power_nets == []

    def test_init_with_values(self):
        n = CfgNets(signal_nets=["CLK"], power_nets=["VDD"], reference_nets=["GND"])
        assert n.signal_nets == ["CLK"]
        assert n.power_nets == ["VDD"]
        assert n.reference_nets == ["GND"]

    def test_signal_nets(self):
        n = CfgNets()
        n.add_signal_nets(["SIG1", "SIG2"])
        assert n.signal_nets == ["SIG1", "SIG2"]
        assert n.power_nets == []

    def test_power_ground_nets(self):
        n = CfgNets()
        n.add_power_ground_nets(["VDD", "GND"])
        assert n.power_ground_nets == ["VDD", "GND"]

    def test_power_ground_nets_setter(self):
        n = CfgNets()
        n.power_ground_nets = ["V1", "V2"]
        assert n.power_nets == ["V1", "V2"]

    def test_power_ground_nets_setter_none(self):
        n = CfgNets()
        n.power_ground_nets = None
        assert n.power_nets == []

    def test_accumulates(self):
        n = CfgNets()
        n.add_signal_nets(["A"])
        n.add_signal_nets(["B", "C"])
        assert n.signal_nets == ["A", "B", "C"]

    def test_add_reference_nets(self):
        n = CfgNets()
        n.add_reference_nets(["GND", "AGND"])
        assert n.reference_nets == ["GND", "AGND"]

    def test_add_single_string(self):
        """add_signal_nets accepts a plain string (not just lists)."""
        n = CfgNets()
        n.add_signal_nets("CLK")
        assert "CLK" in n.signal_nets

    def test_exclusive_signal_to_power(self):
        n = CfgNets()
        n.add_signal_nets(["CLK"])
        n.add_power_ground_nets(["CLK"])
        assert "CLK" not in n.signal_nets
        assert "CLK" in n.power_nets

    def test_exclusive_power_to_signal(self):
        n = CfgNets()
        n.add_power_ground_nets(["GND"])
        n.add_signal_nets(["GND"])
        assert "GND" not in n.power_nets
        assert "GND" in n.signal_nets

    def test_exclusive_reference_to_signal(self):
        n = CfgNets()
        n.add_reference_nets(["GND"])
        n.add_signal_nets(["GND"])
        assert "GND" not in n.reference_nets
        assert "GND" in n.signal_nets

    def test_no_duplicate(self):
        n = CfgNets()
        n.add_signal_nets(["A"])
        n.add_signal_nets(["A"])
        assert n.signal_nets.count("A") == 1

    def test_add_cfgnet_object(self):
        """add_signal_nets accepts CfgNet objects."""
        mock_pedb = MagicMock()
        mock_pedb.nets.nets = {"SIG": MagicMock()}
        net_obj = CfgNets.CfgNet(mock_pedb, "SIG")
        n = CfgNets()
        n.add_signal_nets(net_obj)
        assert "SIG" in n.signal_nets

    def test_get_raises_without_pedb(self):
        n = CfgNets()
        with pytest.raises(KeyError):
            n.get("GND")

    def test_get_returns_false_when_not_found(self):
        mock_pedb = MagicMock()
        mock_pedb.nets.nets = {}
        n = CfgNets(pedb=mock_pedb)
        result = n.get("MISSING")
        assert result is False

    def test_get_returns_cfgnet(self):
        mock_net = MagicMock()
        mock_pedb = MagicMock()
        mock_pedb.nets.nets = {"GND": mock_net}
        n = CfgNets(pedb=mock_pedb)
        result = n.get("GND")
        assert isinstance(result, CfgNets.CfgNet)
        assert result.name == "GND"

    def test_get_parameters_from_edb_without_pedb(self):
        n = CfgNets(signal_nets=["SIG"], power_nets=["PWR"])
        d = n.get_parameters_from_edb()
        assert d["signal_nets"] == ["SIG"]
        assert d["power_ground_nets"] == ["PWR"]

    def test_get_data_from_db_without_pedb(self):
        n = CfgNets(signal_nets=["SIG"])
        d = n.get_data_from_db()
        assert "signal_nets" in d

    def test_apply_without_pedb(self):
        """apply() with no pedb is a no-op (should not raise)."""
        n = CfgNets(signal_nets=["SIG"])
        n.apply()  # no error

    def test_reference_nets_usable_in_cutout(self):
        n = CfgNets()
        n.add_signal_nets(["SIG"])
        n.add_reference_nets(["GND"])
        ops = CfgOperations()
        ops.add_cutout(signal_nets=n.signal_nets, reference_nets=n.reference_nets)
        d = ops.model_dump()
        assert d["cutout"]["signal_nets"] == ["SIG"]
        assert d["cutout"]["reference_nets"] == ["GND"]

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

    def test_set_parameters_to_edb_with_pedb(self):
        """set_parameters_to_edb writes classifications into EDB when pedb is attached."""
        mock_net_sig = MagicMock()
        mock_net_pwr = MagicMock()
        mock_pedb = MagicMock()
        mock_pedb.nets.nets = {"CLK": mock_net_sig, "VDD": mock_net_pwr}
        mock_pedb.nets.__contains__ = lambda self, item: item in ["CLK", "VDD"]
        n = CfgNets(pedb=mock_pedb, signal_nets=["CLK"], power_nets=["VDD"])
        n.set_parameters_to_edb()
        assert mock_net_sig.is_power_ground is False
        assert mock_net_pwr.is_power_ground is True

    def test_set_parameters_to_edb_skips_missing_nets(self):
        """set_parameters_to_edb skips nets not present in EDB."""
        mock_pedb = MagicMock()
        mock_pedb.nets.nets = {}
        mock_pedb.nets.__contains__ = lambda self, item: False
        n = CfgNets(pedb=mock_pedb, signal_nets=["MISSING"])
        n.set_parameters_to_edb()  # should not raise

    def test_get_parameters_from_edb_with_pedb(self):
        """get_parameters_from_edb reads from EDB when pedb is attached."""
        mock_pedb = MagicMock()
        mock_pedb.nets.signal = ["CLK", "DATA"]
        mock_pedb.nets.power = ["VDD", "GND"]
        n = CfgNets(pedb=mock_pedb)
        d = n.get_parameters_from_edb()
        assert d["signal_nets"] == ["CLK", "DATA"]
        assert d["power_ground_nets"] == ["VDD", "GND"]
        assert n.signal_nets == ["CLK", "DATA"]
        assert n.power_nets == ["VDD", "GND"]
