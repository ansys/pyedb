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

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.no_licence, pytest.mark.legacy]


from pydantic import ValidationError
import pytest

from pyedb.configuration.cfg_terminals import (
    CfgBundleTerminal,
    CfgEdgeTerminal,
    CfgPadstackInstanceTerminal,
    CfgPinGroupTerminal,
    CfgPointTerminal,
    CfgTerminalInfo,
    CfgTerminals,
)


class TestCfgTerminalInfo:
    def test_from_pin(self):
        t = CfgTerminalInfo.from_pin("A1")
        assert t == {"pin": "A1"}

    def test_from_pin_with_refdes(self):
        t = CfgTerminalInfo.from_pin("A1", reference_designator="U1")
        assert t == {"pin": "A1", "reference_designator": "U1"}

    def test_from_pin_no_refdes_key_absent(self):
        t = CfgTerminalInfo.from_pin("A1")
        assert "reference_designator" not in t

    def test_from_net(self):
        t = CfgTerminalInfo.from_net("VDD")
        assert t == {"net": "VDD"}

    def test_from_net_with_refdes(self):
        t = CfgTerminalInfo.from_net("VDD", reference_designator="U1")
        assert t == {"net": "VDD", "reference_designator": "U1"}

    def test_from_net_no_refdes_key_absent(self):
        t = CfgTerminalInfo.from_net("VDD")
        assert "reference_designator" not in t

    def test_from_pin_group(self):
        t = CfgTerminalInfo.from_pin_group("pg1")
        assert t == {"pin_group": "pg1"}

    def test_from_padstack(self):
        t = CfgTerminalInfo.from_padstack("via_001")
        assert t == {"padstack": "via_001"}

    def test_from_coordinates(self):
        t = CfgTerminalInfo.from_coordinates("top", 0.001, 0.002, "SIG")
        assert t == {"coordinates": {"layer": "top", "point": [0.001, 0.002], "net": "SIG"}}

    def test_from_coordinates_str_values(self):
        t = CfgTerminalInfo.from_coordinates("top", "1mm", "2mm", "GND")
        assert t["coordinates"]["point"] == ["1mm", "2mm"]

    def test_from_nearest_pin(self):
        t = CfgTerminalInfo.from_nearest_pin("GND", search_radius="5mm")
        assert t == {"nearest_pin": {"reference_net": "GND", "search_radius": "5mm"}}

    def test_from_nearest_pin_default_radius(self):
        t = CfgTerminalInfo.from_nearest_pin("GND")
        assert t["nearest_pin"]["search_radius"] == "5mm"

    def test_from_nearest_pin_custom_radius(self):
        t = CfgTerminalInfo.from_nearest_pin("GND", search_radius="10mm")
        assert t["nearest_pin"]["search_radius"] == "10mm"


class TestCfgPadstackInstanceTerminal:
    def test_basic(self):
        t = CfgPadstackInstanceTerminal(name="t1", padstack_instance="via_1", impedance=50, boundary_type="port")
        d = t.model_dump(exclude_none=True)
        assert d["terminal_type"] == "padstack_instance"
        assert d["name"] == "t1"
        assert d["padstack_instance"] == "via_1"
        assert d["impedance"] == 50
        assert d["boundary_type"] == "port"

    def test_hfss_type_none_excluded(self):
        t = CfgPadstackInstanceTerminal(
            name="t1", padstack_instance="via_1", impedance=50, boundary_type="port", hfss_type=None
        )
        assert "hfss_type" not in t.model_dump(exclude_none=True)

    def test_optional_fields(self):
        t = CfgPadstackInstanceTerminal(
            name="t1",
            padstack_instance="via_1",
            impedance=50,
            boundary_type="port",
            hfss_type="Wave",
            is_circuit_port=True,
            reference_terminal="ref_t",
            layer="top",
            padstack_instance_id=42,
        )
        d = t.model_dump(exclude_none=True)
        assert d["hfss_type"] == "Wave"
        assert d["is_circuit_port"] is True
        assert d["reference_terminal"] == "ref_t"
        assert d["layer"] == "top"
        assert d["padstack_instance_id"] == 42

    def test_defaults(self):
        t = CfgPadstackInstanceTerminal(name="t1", padstack_instance="via_1", impedance=50, boundary_type="port")
        assert t.is_circuit_port is False
        assert t.amplitude == 1
        assert t.phase == 0
        assert t.terminal_to_ground == "kNoGround"

    def test_impedance_as_string(self):
        t = CfgPadstackInstanceTerminal(name="t1", padstack_instance="via_1", impedance="50ohm", boundary_type="port")
        assert t.impedance == "50ohm"

    def test_round_trip(self):
        t = CfgPadstackInstanceTerminal(
            name="t1",
            padstack_instance="via_1",
            impedance=50,
            boundary_type="port",
            hfss_type="Wave",
            layer="sig",
            padstack_instance_id=7,
        )
        d = t.model_dump()
        t2 = CfgPadstackInstanceTerminal.model_validate(d)
        assert t == t2

    def test_invalid_boundary_type(self):
        with pytest.raises(ValidationError):
            CfgPadstackInstanceTerminal(
                name="t1", padstack_instance="via_1", impedance=50, boundary_type="invalid_type"
            )


class TestCfgPinGroupTerminal:
    def test_basic(self):
        t = CfgPinGroupTerminal(name="t1", pin_group="pg_VDD", impedance=50, boundary_type="port")
        d = t.model_dump(exclude_none=True)
        assert d["terminal_type"] == "pin_group"
        assert d["pin_group"] == "pg_VDD"
        assert d["is_circuit_port"] is True

    def test_reference_terminal(self):
        t = CfgPinGroupTerminal(
            name="t1", pin_group="pg_VDD", impedance=50, boundary_type="port", reference_terminal="ref_t"
        )
        assert t.model_dump(exclude_none=True)["reference_terminal"] == "ref_t"

    def test_no_reference_terminal_excluded(self):
        t = CfgPinGroupTerminal(name="t1", pin_group="pg_VDD", impedance=50, boundary_type="port")
        assert "reference_terminal" not in t.model_dump(exclude_none=True)

    def test_amplitude_phase(self):
        t = CfgPinGroupTerminal(
            name="t1", pin_group="pg_VDD", impedance=50, boundary_type="port", amplitude=2, phase=90
        )
        assert t.amplitude == 2
        assert t.phase == 90

    def test_round_trip(self):
        t = CfgPinGroupTerminal(name="t1", pin_group="pg_VDD", impedance=50, boundary_type="port")
        t2 = CfgPinGroupTerminal.model_validate(t.model_dump())
        assert t == t2


class TestCfgPointTerminal:
    def test_basic(self):
        t = CfgPointTerminal(name="t1", x=0.001, y=0.002, layer="top", net="SIG", impedance=50, boundary_type="port")
        d = t.model_dump(exclude_none=True)
        assert d["terminal_type"] == "point"
        assert d["x"] == 0.001
        assert d["y"] == 0.002
        assert d["layer"] == "top"
        assert d["net"] == "SIG"

    def test_no_ref_terminal_key_when_none(self):
        t = CfgPointTerminal(name="t1", x=0, y=0, layer="top", net="SIG", impedance=50, boundary_type="port")
        assert "reference_terminal" not in t.model_dump(exclude_none=True)

    def test_is_circuit_port_default_true(self):
        t = CfgPointTerminal(name="t1", x=0, y=0, layer="top", net="SIG", impedance=50, boundary_type="port")
        assert t.is_circuit_port is True

    def test_string_coordinates(self):
        t = CfgPointTerminal(name="t1", x="1mm", y="2mm", layer="top", net="SIG", impedance=50, boundary_type="port")
        assert t.x == "1mm"
        assert t.y == "2mm"

    def test_round_trip(self):
        t = CfgPointTerminal(name="t1", x=1e-3, y=2e-3, layer="top", net="SIG", impedance=50, boundary_type="port")
        t2 = CfgPointTerminal.model_validate(t.model_dump())
        assert t == t2


class TestCfgEdgeTerminal:
    def test_basic(self):
        t = CfgEdgeTerminal(
            name="t1",
            primitive="prim1",
            point_on_edge_x=0.001,
            point_on_edge_y=0.002,
            impedance=50,
            boundary_type="port",
        )
        d = t.model_dump(exclude_none=True)
        assert d["terminal_type"] == "edge"
        assert d["primitive"] == "prim1"
        assert d["hfss_type"] == "Wave"
        assert d["horizontal_extent_factor"] == 6
        assert d["vertical_extent_factor"] == 8
        assert d["pec_launch_width"] == "0.02mm"

    def test_custom_extent(self):
        t = CfgEdgeTerminal(
            name="t1",
            primitive="prim1",
            point_on_edge_x=0,
            point_on_edge_y=0,
            impedance=50,
            boundary_type="port",
            horizontal_extent_factor=8,
            vertical_extent_factor=10,
        )
        d = t.model_dump(exclude_none=True)
        assert d["horizontal_extent_factor"] == 8
        assert d["vertical_extent_factor"] == 10

    def test_hfss_type_gap(self):
        t = CfgEdgeTerminal(
            name="t1",
            primitive="p",
            point_on_edge_x=0,
            point_on_edge_y=0,
            impedance=50,
            boundary_type="port",
            hfss_type="Gap",
        )
        assert t.hfss_type == "Gap"

    def test_pec_launch_width_custom(self):
        t = CfgEdgeTerminal(
            name="t1",
            primitive="p",
            point_on_edge_x=0,
            point_on_edge_y=0,
            impedance=50,
            boundary_type="port",
            pec_launch_width="0.05mm",
        )
        assert t.pec_launch_width == "0.05mm"

    def test_round_trip(self):
        t = CfgEdgeTerminal(
            name="t1", primitive="p", point_on_edge_x=0, point_on_edge_y=0, impedance=50, boundary_type="port"
        )
        t2 = CfgEdgeTerminal.model_validate(t.model_dump())
        assert t == t2


class TestCfgBundleTerminal:
    def test_basic(self):
        t = CfgBundleTerminal(name="bundle1", terminals=["t1", "t2"])
        d = t.model_dump(exclude_none=True)
        assert d["terminal_type"] == "bundle"
        assert d["terminals"] == ["t1", "t2"]
        assert d["name"] == "bundle1"

    def test_empty_terminals_list(self):
        t = CfgBundleTerminal(name="b", terminals=[])
        assert t.terminals == []

    def test_round_trip(self):
        t = CfgBundleTerminal(name="bundle1", terminals=["t1", "t2"])
        t2 = CfgBundleTerminal.model_validate(t.model_dump())
        assert t == t2


class TestCfgTerminals:
    def test_empty(self):
        tc = CfgTerminals()
        assert tc.terminals == []

    def test_add_padstack_instance_terminal(self):
        tc = CfgTerminals()
        t = tc.add_padstack_instance_terminal("t1", "via_1", 50, "port")
        assert isinstance(t, CfgPadstackInstanceTerminal)
        assert len(tc.terminals) == 1
        assert tc.terminals[0].name == "t1"

    def test_add_padstack_instance_terminal_all_params(self):
        tc = CfgTerminals()
        t = tc.add_padstack_instance_terminal(
            name="t1",
            padstack_instance="via_1",
            impedance=50,
            boundary_type="port",
            hfss_type="Wave",
            is_circuit_port=True,
            reference_terminal="ref_t",
            amplitude=2,
            phase=90,
            terminal_to_ground="kNegativeNode",
            layer="top",
            padstack_instance_id=42,
        )
        assert t.hfss_type == "Wave"
        assert t.is_circuit_port is True
        assert t.reference_terminal == "ref_t"
        assert t.amplitude == 2
        assert t.phase == 90
        assert t.terminal_to_ground == "kNegativeNode"
        assert t.layer == "top"
        assert t.padstack_instance_id == 42

    def test_add_pin_group_terminal(self):
        tc = CfgTerminals()
        t = tc.add_pin_group_terminal("t2", "pg1", 50, "port")
        assert isinstance(t, CfgPinGroupTerminal)
        assert t.pin_group == "pg1"

    def test_add_pin_group_terminal_all_params(self):
        tc = CfgTerminals()
        t = tc.add_pin_group_terminal(
            name="t2",
            pin_group="pg1",
            impedance=50,
            boundary_type="port",
            reference_terminal="ref_t",
            amplitude=1.5,
            phase=45,
            terminal_to_ground="kNegativeNode",
        )
        assert t.reference_terminal == "ref_t"
        assert t.amplitude == 1.5
        assert t.phase == 45
        assert t.terminal_to_ground == "kNegativeNode"

    def test_add_point_terminal(self):
        tc = CfgTerminals()
        t = tc.add_point_terminal("t3", 0.001, 0.002, "top", "SIG", 50, "port")
        assert isinstance(t, CfgPointTerminal)
        assert t.x == 0.001

    def test_add_point_terminal_all_params(self):
        tc = CfgTerminals()
        t = tc.add_point_terminal(
            name="t3",
            x=0.001,
            y=0.002,
            layer="top",
            net="SIG",
            impedance=50,
            boundary_type="port",
            reference_terminal="ref_t",
            amplitude=1,
            phase=0,
            terminal_to_ground="kNoGround",
        )
        assert t.reference_terminal == "ref_t"
        assert t.terminal_to_ground == "kNoGround"

    def test_add_edge_terminal(self):
        tc = CfgTerminals()
        t = tc.add_edge_terminal("t4", "prim1", 0, 0, 50, "port")
        assert isinstance(t, CfgEdgeTerminal)
        assert t.terminal_type == "edge"

    def test_add_edge_terminal_all_params(self):
        tc = CfgTerminals()
        t = tc.add_edge_terminal(
            name="t4",
            primitive="prim1",
            point_on_edge_x=0.001,
            point_on_edge_y=0.002,
            impedance=50,
            boundary_type="port",
            hfss_type="Gap",
            horizontal_extent_factor=8,
            vertical_extent_factor=10,
            pec_launch_width="0.05mm",
            is_circuit_port=True,
            reference_terminal="ref_t",
            amplitude=2,
            phase=30,
            terminal_to_ground="kNegativeNode",
        )
        assert t.hfss_type == "Gap"
        assert t.horizontal_extent_factor == 8
        assert t.vertical_extent_factor == 10
        assert t.pec_launch_width == "0.05mm"
        assert t.is_circuit_port is True
        assert t.reference_terminal == "ref_t"
        assert t.amplitude == 2
        assert t.phase == 30
        assert t.terminal_to_ground == "kNegativeNode"

    def test_add_bundle_terminal(self):
        tc = CfgTerminals()
        t = tc.add_bundle_terminal("bundle1", ["t1", "t2"])
        assert isinstance(t, CfgBundleTerminal)
        assert t.terminals == ["t1", "t2"]

    def test_multiple_terminals_order_preserved(self):
        tc = CfgTerminals()
        tc.add_padstack_instance_terminal("t1", "via_1", 50, "port")
        tc.add_pin_group_terminal("t2", "pg1", 50, "port")
        tc.add_bundle_terminal("bundle1", ["t1", "t2"])
        assert [t.terminal_type for t in tc.terminals] == ["padstack_instance", "pin_group", "bundle"]

    def test_model_dump_serialization(self):
        tc = CfgTerminals()
        tc.add_padstack_instance_terminal("pt1", "v1", 50, "port")
        data = tc.model_dump(exclude_none=True)
        assert data["terminals"][0]["name"] == "pt1"
        assert data["terminals"][0]["terminal_type"] == "padstack_instance"

    def test_create_round_trip_padstack(self):
        tc = CfgTerminals()
        tc.add_padstack_instance_terminal("t1", "via_1", 50, "port", hfss_type="Wave")
        data = tc.model_dump(exclude_none=True)
        tc2 = CfgTerminals.create(data["terminals"])
        assert tc2.terminals[0].name == "t1"
        assert tc2.terminals[0].padstack_instance == "via_1"

    def test_create_round_trip_pin_group(self):
        tc = CfgTerminals()
        tc.add_pin_group_terminal("t2", "pg1", 50, "port")
        data = tc.model_dump(exclude_none=True)
        tc2 = CfgTerminals.create(data["terminals"])
        assert isinstance(tc2.terminals[0], CfgPinGroupTerminal)

    def test_create_round_trip_point(self):
        tc = CfgTerminals()
        tc.add_point_terminal("t3", 1e-3, 2e-3, "top", "SIG", 50, "port")
        data = tc.model_dump(exclude_none=True)
        tc2 = CfgTerminals.create(data["terminals"])
        assert isinstance(tc2.terminals[0], CfgPointTerminal)
        assert tc2.terminals[0].x == 1e-3

    def test_create_round_trip_edge(self):
        tc = CfgTerminals()
        tc.add_edge_terminal("t4", "prim1", 0, 0, 50, "port")
        data = tc.model_dump(exclude_none=True)
        tc2 = CfgTerminals.create(data["terminals"])
        assert isinstance(tc2.terminals[0], CfgEdgeTerminal)

    def test_create_round_trip_bundle(self):
        tc = CfgTerminals()
        tc.add_bundle_terminal("b1", ["t1", "t2"])
        data = tc.model_dump(exclude_none=True)
        tc2 = CfgTerminals.create(data["terminals"])
        assert isinstance(tc2.terminals[0], CfgBundleTerminal)
        assert tc2.terminals[0].terminals == ["t1", "t2"]

    def test_create_round_trip_mixed(self):
        tc = CfgTerminals()
        tc.add_padstack_instance_terminal("t1", "via_1", 50, "port")
        tc.add_pin_group_terminal("t2", "pg1", 50, "port")
        tc.add_point_terminal("t3", 0, 0, "top", "SIG", 50, "port")
        tc.add_edge_terminal("t4", "prim1", 0, 0, 50, "port")
        tc.add_bundle_terminal("b1", ["t1", "t2"])
        data = tc.model_dump(exclude_none=True)
        tc2 = CfgTerminals.create(data["terminals"])
        assert len(tc2.terminals) == 5
        types = [t.terminal_type for t in tc2.terminals]
        assert types == ["padstack_instance", "pin_group", "point", "edge", "bundle"]

    def test_model_validate_round_trip(self):
        tc = CfgTerminals()
        tc.add_padstack_instance_terminal("t1", "via_1", 50, "port", hfss_type="Wave", layer="sig")
        tc.add_bundle_terminal("b1", ["t1"])
        tc2 = CfgTerminals.model_validate(tc.model_dump())
        assert len(tc2.terminals) == 2
