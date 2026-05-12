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

from pyedb.configuration.cfg_components import CfgComponent


pytestmark = [pytest.mark.unit, pytest.mark.no_licence, pytest.mark.legacy]


class TestComponentConfig:
    def test_minimal(self):
        c = CfgComponent("U1")
        d = c.to_dict()
        assert d == {"reference_designator": "U1"}

    def test_with_type_and_enabled(self):
        c = CfgComponent("R1", part_type="resistor", enabled=False)
        d = c.to_dict()
        assert d["part_type"] == "resistor"
        assert d["enabled"] is False

    def test_pin_pair_rlc(self):
        c = CfgComponent("R1")
        c.add_pin_pair_rlc("1", "2", resistance="1kohm", resistance_enabled=True)
        d = c.to_dict()
        assert len(d["pin_pair_model"]) == 1
        assert d["pin_pair_model"][0]["resistance"] == "1kohm"

    def test_multiple_pin_pair_rlc(self):
        c = CfgComponent("C1")
        c.add_pin_pair_rlc("1", "2", capacitance="100nF", capacitance_enabled=True)
        c.add_pin_pair_rlc("2", "3", resistance="10ohm", resistance_enabled=True)
        d = c.to_dict()
        assert len(d["pin_pair_model"]) == 2

    def test_s_parameter_model(self):
        c = CfgComponent("U1")
        c.set_s_parameter_model("model1", "/path/to/model.s2p", "GND")
        d = c.to_dict()
        assert d["s_parameter_model"]["model_name"] == "model1"
        assert d["s_parameter_model"]["reference_net"] == "GND"

    def test_spice_model(self):
        c = CfgComponent("U2")
        c.set_spice_model("ic_spice", "/path/ic.sp", "IC_SUB")
        d = c.to_dict()
        assert d["spice_model"]["model_name"] == "ic_spice"
        assert d["spice_model"]["sub_circuit"] == "IC_SUB"

    def test_netlist_model(self):
        c = CfgComponent("Q1")
        c.set_netlist_model(".subckt Q1 ...")
        d = c.to_dict()
        assert d["netlist_model"]["netlist"] == ".subckt Q1 ..."

    def test_ic_die_properties_no_die(self):
        c = CfgComponent("U1")
        c.set_ic_die_properties("no_die")
        d = c.to_dict()
        assert d["ic_die_properties"]["type"] == "no_die"

    def test_ic_die_properties_flip_chip(self):
        c = CfgComponent("U1")
        c.set_ic_die_properties("flip_chip", orientation="chip_down")
        d = c.to_dict()
        assert d["ic_die_properties"]["type"] == "flip_chip"
        assert d["ic_die_properties"]["orientation"] == "chip_down"

    def test_ic_die_properties_wire_bond(self):
        c = CfgComponent("U1")
        c.set_ic_die_properties("wire_bond", orientation="chip_up", height="200um")
        d = c.to_dict()
        assert d["ic_die_properties"]["height"] == "200um"

    def test_solder_ball_cylinder(self):
        c = CfgComponent("U1")
        c.set_solder_ball_properties("cylinder", "150um", "100um")
        d = c.to_dict()
        assert d["solder_ball_properties"]["shape"] == "cylinder"
        assert d["solder_ball_properties"]["diameter"] == "150um"

    def test_solder_ball_spheroid(self):
        c = CfgComponent("U1")
        c.set_solder_ball_properties("spheroid", "150um", "100um", mid_diameter="130um")
        d = c.to_dict()
        assert d["solder_ball_properties"]["mid_diameter"] == "130um"

    def test_port_properties(self):
        c = CfgComponent("U1")
        c.set_port_properties(reference_height="50um", reference_size_auto=False)
        d = c.to_dict()
        assert d["port_properties"]["reference_height"] == "50um"
        assert d["port_properties"]["reference_size_auto"] is False