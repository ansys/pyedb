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

from pyedb.configuration.cfg_ports_sources import (
    CfgCoordinateTerminalInfo,
    CfgDiffWavePort,
    CfgEdgePort,
    CfgNearestPinTerminalInfo,
    CfgPort,
    CfgPorts,
    CfgProbe,
    CfgProbes,
    CfgSource,
    CfgSources,
    CfgTerminalInfo,
)

pytestmark = [pytest.mark.unit, pytest.mark.no_licence, pytest.mark.legacy]


# ---------------------------------------------------------------------------
# CfgTerminalInfo helpers
# ---------------------------------------------------------------------------


class TestTerminalInfoFactories:
    def test_pin(self):
        d = CfgTerminalInfo.pin("A1", reference_designator="U1")
        assert d == {"pin": "A1", "reference_designator": "U1"}

    def test_pin_no_refdes(self):
        d = CfgTerminalInfo.pin("B2")
        assert d == {"pin": "B2"}

    def test_net(self):
        d = CfgTerminalInfo.net("VDD", reference_designator="U1")
        assert d == {"net": "VDD", "reference_designator": "U1"}

    def test_pin_group(self):
        assert CfgTerminalInfo.pin_group("pg_VDD") == {"pin_group": "pg_VDD"}

    def test_padstack(self):
        assert CfgTerminalInfo.padstack("via_A1") == {"padstack": "via_A1"}

    def test_coordinates(self):
        d = CfgTerminalInfo.coordinates("top", 0.001, 0.002, "SIG")
        assert d == {"coordinates": {"layer": "top", "point": [0.001, 0.002], "net": "SIG"}}

    def test_nearest_pin(self):
        d = CfgTerminalInfo.nearest_pin("GND", search_radius="3mm")
        assert d == {"nearest_pin": {"reference_net": "GND", "search_radius": "3mm"}}

    def test_nearest_pin_default_radius(self):
        d = CfgTerminalInfo.nearest_pin("GND")
        assert d["nearest_pin"]["search_radius"] == "5mm"


class TestCfgTerminalInfo:
    def test_pin_type(self):
        ti = CfgTerminalInfo(None, pin="A1", reference_designator="U1")
        assert ti.type == "pin"
        assert ti.value == "A1"
        assert ti.reference_designator == "U1"

    def test_net_type(self):
        ti = CfgTerminalInfo(None, net="VDD")
        assert ti.type == "net"

    def test_pin_group_type(self):
        ti = CfgTerminalInfo(None, pin_group="pg1")
        assert ti.type == "pin_group"

    def test_padstack_type(self):
        ti = CfgTerminalInfo(None, padstack="via_A1")
        assert ti.type == "padstack"

    def test_nearest_pin_type(self):
        ti = CfgTerminalInfo(None, nearest_pin={"reference_net": "GND", "search_radius": "5mm"})
        assert ti.type == "nearest_pin"

    def test_coordinates_type(self):
        ti = CfgTerminalInfo(None, coordinates={"layer": "top", "point": [0, 0], "net": "SIG"})
        assert ti.type == "coordinates"

    def test_export_properties_with_refdes(self):
        ti = CfgTerminalInfo(None, pin="A1", reference_designator="U1")
        d = ti.export_properties()
        assert d == {"pin": "A1", "reference_designator": "U1"}

    def test_export_properties_no_refdes(self):
        ti = CfgTerminalInfo(None, pin_group="pg1")
        d = ti.export_properties()
        assert d == {"pin_group": "pg1"}

    def test_update_contact_radius_no_pedb(self):
        ti = CfgTerminalInfo(None, pin="A1")
        ti.update_contact_radius("0.2mm")
        assert ti.contact_radius == "0.2mm"


class TestCfgCoordinateTerminalInfo:
    def test_init_and_export(self):
        ti = CfgCoordinateTerminalInfo(None, coordinates={"layer": "top", "point": [0.001, 0.002], "net": "SIG"})
        d = ti.export_properties()
        assert d == {"coordinates": {"layer": "top", "point": [0.001, 0.002], "net": "SIG"}}


class TestCfgNearestPinTerminalInfo:
    def test_init_and_export(self):
        ti = CfgNearestPinTerminalInfo(None, nearest_pin={"reference_net": "GND", "search_radius": "5mm"})
        d = ti.export_properties()
        assert d == {"nearest_pin": {"reference_net": "GND", "search_radius": "5mm"}}


# ---------------------------------------------------------------------------
# CfgPort (single port)
# ---------------------------------------------------------------------------


class TestCfgPort:
    def test_circuit_port(self):
        p = CfgPort("p1", "circuit", {"pin_group": "pg1"}, {"net": "GND"})
        d = p.export_properties()
        assert d["type"] == "circuit"
        assert d["positive_terminal"] == {"pin_group": "pg1"}
        assert d["negative_terminal"] == {"net": "GND"}

    def test_coax_no_neg_terminal(self):
        p = CfgPort("coax1", "coax", {"padstack": "via_1"})
        d = p.export_properties()
        assert "negative_terminal" not in d

    def test_impedance(self):
        p = CfgPort("p1", "circuit", {"net": "SIG"}, {"net": "GND"}, impedance=50)
        assert p.export_properties()["impedance"] == 50

    def test_distributed(self):
        p = CfgPort("p1", "circuit", {"net": "SIG"}, {"net": "GND"}, distributed=True)
        assert p.export_properties()["distributed"] is True

    def test_reference_designator(self):
        p = CfgPort("p1", "circuit", {"pin": "A1"}, {"pin": "B1"}, reference_designator="U1")
        assert p.export_properties()["reference_designator"] == "U1"

    def test_set_parameters_no_pedb(self):
        p = CfgPort("p1", "circuit", {"pin_group": "pg1"}, {"pin_group": "pg2"})
        result = p.set_parameters_to_edb()
        assert result == p.export_properties()

    def test_nearest_pin_negative_terminal(self):
        p = CfgPort(
            "p1", "coax", {"padstack": "via_A1"}, {"nearest_pin": {"reference_net": "GND", "search_radius": "5mm"}}
        )
        d = p.export_properties()
        assert d["negative_terminal"] == {"nearest_pin": {"reference_net": "GND", "search_radius": "5mm"}}

    def test_coordinate_positive_terminal(self):
        p = CfgPort(
            "p1",
            "circuit",
            {"coordinates": {"layer": "top", "point": [0.001, 0.002], "net": "SIG"}},
            {"pin_group": "pg_gnd"},
        )
        d = p.export_properties()
        assert "coordinates" in d["positive_terminal"]


# ---------------------------------------------------------------------------
# CfgEdgePort
# ---------------------------------------------------------------------------


class TestCfgEdgePort:
    def test_wave_port(self):
        ep = CfgEdgePort("wp1", "wave_port", "trace1", [0.001, 0.002])
        d = ep.export_properties()
        assert d["type"] == "wave_port"
        assert d["primitive_name"] == "trace1"
        assert d["point_on_edge"] == [0.001, 0.002]
        assert d["horizontal_extent_factor"] == 5
        assert d["vertical_extent_factor"] == 3
        assert d["pec_launch_width"] == "0.01mm"

    def test_gap_port(self):
        ep = CfgEdgePort("gp1", "gap_port", "trace2", [0.003, 0.004], horizontal_extent_factor=3)
        d = ep.export_properties()
        assert d["horizontal_extent_factor"] == 3

    def test_gap_port_custom_extent(self):
        ep = CfgEdgePort(
            "gp1", "gap_port", "trace2", [0.003, 0.004], horizontal_extent_factor=3, vertical_extent_factor=2
        )
        d = ep.export_properties()
        assert d["horizontal_extent_factor"] == 3
        assert d["vertical_extent_factor"] == 2

    def test_set_parameters_no_pedb(self):
        ep = CfgEdgePort("wp1", "wave_port", "trace1", [0.001, 0.002])
        result = ep.set_parameters_to_edb()
        assert result == ep.export_properties()


# ---------------------------------------------------------------------------
# CfgDiffWavePort
# ---------------------------------------------------------------------------


class TestCfgDiffWavePort:
    def test_diff_wave_port(self):
        dp = CfgDiffWavePort(
            "diff1",
            {"primitive_name": "trace_p", "point_on_edge": [0, 0]},
            {"primitive_name": "trace_n", "point_on_edge": [0, 1e-4]},
        )
        d = dp.export_properties()
        assert d["type"] == "diff_wave_port"
        assert d["positive_terminal"]["primitive_name"] == "trace_p"
        assert d["negative_terminal"]["primitive_name"] == "trace_n"
        assert d["horizontal_extent_factor"] == 5

    def test_custom_extents(self):
        dp = CfgDiffWavePort(
            "diff2",
            {"primitive_name": "tp", "point_on_edge": [0, 0]},
            {"primitive_name": "tn", "point_on_edge": [0, 1e-4]},
            horizontal_extent_factor=8,
            pec_launch_width="0.02mm",
        )
        d = dp.export_properties()
        assert d["horizontal_extent_factor"] == 8
        assert d["pec_launch_width"] == "0.02mm"

    def test_set_parameters_no_pedb(self):
        dp = CfgDiffWavePort(
            "diff1",
            {"primitive_name": "tp", "point_on_edge": [0, 0]},
            {"primitive_name": "tn", "point_on_edge": [0, 1e-4]},
        )
        result = dp.set_parameters_to_edb()
        assert result == dp.export_properties()


# ---------------------------------------------------------------------------
# CfgPorts (collection)
# ---------------------------------------------------------------------------


class TestCfgPorts:
    def test_empty(self):
        assert CfgPorts().export_properties() == []

    def test_add_coax_port(self):
        pc = CfgPorts()
        pc.add_coax_port("coax1", {"padstack": "v1"})
        assert pc.export_properties()[0]["type"] == "coax"

    def test_add_diff_wave_port(self):
        pc = CfgPorts()
        pc.add_diff_wave_port(
            "diff1",
            {"primitive_name": "tp", "point_on_edge": [0, 0]},
            {"primitive_name": "tn", "point_on_edge": [0, 1e-4]},
        )
        assert pc.export_properties()[0]["type"] == "diff_wave_port"

    def test_add_circuit_port(self):
        pc = CfgPorts()
        p = pc.add_circuit_port("p1", positive_terminal={"net": "SIG"}, negative_terminal={"net": "GND"})
        assert isinstance(p, CfgPort)
        assert pc.export_properties()[0]["type"] == "circuit"

    def test_add_coax_port_padstack_shortcut(self):
        pc = CfgPorts()
        pc.add_coax_port("coax1", padstack="via_A1")
        d = pc.export_properties()[0]
        assert d["type"] == "coax"
        assert d["positive_terminal"] == {"padstack": "via_A1"}

    def test_add_coax_port_net_shortcut(self):
        pc = CfgPorts()
        pc.add_coax_port("coax_vdd", net="VDD", reference_designator="U1")
        d = pc.export_properties()[0]
        assert d["positive_terminal"] == {"net": "VDD", "reference_designator": "U1"}

    def test_add_coax_port_pin_shortcut(self):
        pc = CfgPorts()
        pc.add_coax_port("coax_a1", pin="A1", reference_designator="U1", impedance=50)
        d = pc.export_properties()[0]
        assert d["positive_terminal"] == {"pin": "A1", "reference_designator": "U1"}
        assert d["impedance"] == 50

    def test_add_coax_port_net_missing_refdes_raises(self):
        pc = CfgPorts()
        with pytest.raises(ValueError, match="reference_designator"):
            pc.add_coax_port("coax_vdd", net="VDD")

    def test_add_coax_port_pin_missing_refdes_raises(self):
        pc = CfgPorts()
        with pytest.raises(ValueError, match="reference_designator"):
            pc.add_coax_port("coax_a1", pin="A1")

    def test_add_coax_port_no_terminal_raises(self):
        pc = CfgPorts()
        with pytest.raises(ValueError):
            pc.add_coax_port("coax_bad")

    def test_add_coax_port_positive_terminal_dict(self):
        pc = CfgPorts()
        pc.add_coax_port("coax1", positive_terminal={"padstack": "via_B1"})
        assert pc.export_properties()[0]["positive_terminal"] == {"padstack": "via_B1"}

    def test_add_wave_port(self):
        pc = CfgPorts()
        pc.add_wave_port("wp1", "prim1", [0.001, 0.002])
        assert pc.export_properties()[0]["type"] == "wave_port"

    def test_add_gap_port(self):
        pc = CfgPorts()
        pc.add_gap_port("gp1", "prim2", [0.003, 0.004])
        assert pc.export_properties()[0]["type"] == "gap_port"

    def test_add_diff_wave_port_dict_form(self):
        pc = CfgPorts()
        pc.add_diff_wave_port(
            "diff1",
            positive_terminal={"primitive_name": "tp", "point_on_edge": [0, 0]},
            negative_terminal={"primitive_name": "tn", "point_on_edge": [0, 1e-4]},
        )
        assert pc.export_properties()[0]["type"] == "diff_wave_port"

    def test_add_diff_wave_port_flat_form(self):
        pc = CfgPorts()
        pc.add_diff_wave_port(
            "diff2",
            positive_primitive="tp",
            positive_terminal_point=[0, 0],
            negative_primitive="tn",
            negative_terminal_point=[0, 1e-4],
        )
        d = pc.export_properties()[0]
        assert d["positive_terminal"]["primitive_name"] == "tp"

    def test_add_diff_wave_port_missing_args_raises(self):
        pc = CfgPorts()
        with pytest.raises(ValueError):
            pc.add_diff_wave_port("diff1", positive_primitive="tp")

    def test_add_coax_net_list_no_refdes_raises(self):
        pc = CfgPorts()
        with pytest.raises(ValueError):
            pc.add_coax_port("coax", net_list=["VDD"])

    def test_add_coax_net_list_no_pedb_raises(self):
        pc = CfgPorts()
        with pytest.raises(RuntimeError):
            pc.add_coax_port("coax", reference_designator="U1", net_list=["VDD"])

    def test_multiple_ports(self):
        pc = CfgPorts()
        pc.add_circuit_port("p1", positive_terminal={"net": "A"}, negative_terminal={"net": "GND"})
        pc.add_coax_port("p2", padstack="v1")
        pc.add_wave_port("p3", "t1", [0, 0])
        assert len(pc.export_properties()) == 3

    def test_init_from_ports_data(self):
        data = [
            {
                "name": "p1",
                "type": "circuit",
                "positive_terminal": {"pin_group": "pg1"},
                "negative_terminal": {"pin_group": "pg2"},
            }
        ]
        pc = CfgPorts(ports_data=data)
        assert len(pc.ports) == 1
        assert pc.ports[0].name == "p1"

    def test_init_from_edge_port_data(self):
        data = [{"name": "wp1", "type": "wave_port", "primitive_name": "trace1", "point_on_edge": [0, 0]}]
        pc = CfgPorts(ports_data=data)
        assert isinstance(pc.ports[0], CfgEdgePort)

    def test_init_from_diff_port_data(self):
        data = [
            {
                "name": "d1",
                "type": "diff_wave_port",
                "positive_terminal": {"primitive_name": "t1", "point_on_edge": [0, 0]},
                "negative_terminal": {"primitive_name": "t2", "point_on_edge": [0, 1e-4]},
            }
        ]
        pc = CfgPorts(ports_data=data)
        assert isinstance(pc.ports[0], CfgDiffWavePort)

    def test_init_unknown_port_type_raises(self):
        with pytest.raises(ValueError):
            CfgPorts(
                ports_data=[
                    {"name": "x", "type": "unknown", "positive_terminal": {"pin": "A1"}, "negative_terminal": {}}
                ]
            )

    def test_get_data_from_db_no_pedb(self):
        pc = CfgPorts()
        pc.add_coax_port("p1", padstack="v1")
        result = pc.get_data_from_db()
        assert result[0]["name"] == "p1"

    def test_apply_no_pedb(self):
        pc = CfgPorts()
        pc.add_coax_port("p1", padstack="v1")
        pc.apply()  # must not raise


# ---------------------------------------------------------------------------
# CfgSource (single source)
# ---------------------------------------------------------------------------


class TestCfgSource:
    def test_current_source(self):
        s = CfgSource("isrc1", "current", {"pin_group": "pg1"}, {"pin_group": "pg2"}, magnitude=0.001)
        d = s.export_properties()
        assert d["type"] == "current"
        assert d["magnitude"] == 0.001
        assert d["positive_terminal"] == {"pin_group": "pg1"}

    def test_voltage_source(self):
        s = CfgSource("vsrc1", "voltage", {"net": "VDD"}, {"net": "GND"}, magnitude=1.8)
        d = s.export_properties()
        assert d["type"] == "voltage"
        assert d["magnitude"] == 1.8

    def test_impedance(self):
        s = CfgSource("s1", "current", {"pin_group": "pg1"}, {"pin_group": "pg2"}, impedance=50)
        assert s.export_properties()["impedance"] == 50

    def test_set_parameters_no_pedb(self):
        s = CfgSource("s1", "current", {"pin_group": "pg1"}, {"pin_group": "pg2"})
        result = s.set_parameters_to_edb()
        assert result == s.export_properties()


# ---------------------------------------------------------------------------
# CfgSources (collection)
# ---------------------------------------------------------------------------


class TestCfgSources:
    def test_empty(self):
        assert CfgSources().export_properties() == []

    def test_add_current_source(self):
        sc = CfgSources()
        s = sc.add_current_source("isrc", {"pin_group": "pg1"}, {"pin_group": "pg2"})
        assert isinstance(s, CfgSource)
        assert sc.export_properties()[0]["type"] == "current"

    def test_add_current_source_all_params(self):
        sc = CfgSources()
        sc.add_current_source(
            "i1",
            {"pin_group": "pg1"},
            {"pin_group": "pg2"},
            magnitude=0.5,
            impedance=1e6,
            reference_designator="U1",
            distributed=True,
        )
        d = sc.export_properties()[0]
        assert d["magnitude"] == 0.5
        assert d["impedance"] == 1e6
        assert d["reference_designator"] == "U1"
        assert d["distributed"] is True

    def test_add_voltage_source(self):
        sc = CfgSources()
        sc.add_voltage_source("vsrc", {"net": "VDD"}, {"net": "GND"})
        assert sc.export_properties()[0]["type"] == "voltage"

    def test_add_voltage_source_all_params(self):
        sc = CfgSources()
        sc.add_voltage_source(
            "v1", {"pin_group": "pg1"}, {"pin_group": "pg2"}, magnitude=3.3, impedance=1e-6, distributed=False
        )
        d = sc.export_properties()[0]
        assert d["magnitude"] == 3.3

    def test_multiple_sources(self):
        sc = CfgSources()
        sc.add_current_source("i1", {"pin_group": "pg1"}, {"pin_group": "pg2"})
        sc.add_voltage_source("v1", {"net": "VDD"}, {"net": "GND"})
        assert len(sc.export_properties()) == 2

    def test_init_from_data(self):
        data = [
            {
                "name": "i1",
                "type": "current",
                "positive_terminal": {"pin_group": "pg1"},
                "negative_terminal": {"pin_group": "pg2"},
            }
        ]
        sc = CfgSources(sources_data=data)
        assert len(sc.sources) == 1

    def test_get_data_from_db_no_pedb(self):
        sc = CfgSources()
        sc.add_current_source("i1", {"pin_group": "pg1"}, {"pin_group": "pg2"})
        result = sc.get_data_from_db()
        assert result[0]["name"] == "i1"

    def test_apply_no_pedb(self):
        sc = CfgSources()
        sc.add_current_source("i1", {"pin_group": "pg1"}, {"pin_group": "pg2"})
        sc.apply()  # must not raise


# ---------------------------------------------------------------------------
# CfgProbe / CfgProbes
# ---------------------------------------------------------------------------


class TestCfgProbe:
    def test_probe_export(self):
        p = CfgProbe("probe1", {"net": "SIG"}, {"net": "GND"})
        d = p.export_properties()
        assert d["name"] == "probe1"
        assert d["type"] == "probe"
        assert d["positive_terminal"] == {"net": "SIG"}
        assert d["negative_terminal"] == {"net": "GND"}

    def test_probe(self):
        p = CfgProbe("probe1", {"net": "SIG"}, {"net": "GND"})
        d = p.export_properties()
        assert d["name"] == "probe1"
        assert d["type"] == "probe"
        assert d["positive_terminal"] == {"net": "SIG"}

    def test_reference_designator(self):
        p = CfgProbe("probe2", {"pin": "A1"}, {"pin": "A2"}, reference_designator="U1")
        assert p.export_properties()["reference_designator"] == "U1"

    def test_set_parameters_no_pedb(self):
        p = CfgProbe("probe1", {"net": "SIG"}, {"net": "GND"})
        result = p.set_parameters_to_edb()
        assert result == p.export_properties()


class TestCfgProbes:
    def test_empty(self):
        assert CfgProbes().to_list() == []

    def test_add(self):
        pc = CfgProbes()
        probe = pc.add("pr1", {"net": "SIG"}, {"net": "GND"})
        assert isinstance(probe, CfgProbe)
        assert pc.to_list()[0]["name"] == "pr1"

    def test_add_with_reference_designator(self):
        pc = CfgProbes()
        pc.add("pr1", {"pin": "A1"}, {"pin": "A2"}, reference_designator="U1")
        assert pc.to_list()[0]["reference_designator"] == "U1"

    def test_multiple_probes(self):
        pc = CfgProbes()
        pc.add("pr1", {"net": "SIG1"}, {"net": "GND"})
        pc.add("pr2", {"net": "SIG2"}, {"net": "GND"})
        assert len(pc.to_list()) == 2

    def test_init_from_data(self):
        data = [
            {"name": "pr1", "type": "probe", "positive_terminal": {"net": "SIG"}, "negative_terminal": {"net": "GND"}}
        ]
        pc = CfgProbes(data=data)
        assert len(pc.probes) == 1

    def test_apply_no_pedb(self):
        pc = CfgProbes()
        pc.add("pr1", {"net": "SIG"}, {"net": "GND"})
        pc.apply()  # must not raise
