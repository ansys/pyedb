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

"""Tests related to Edb ports, sources, and excitations."""

import os
from pathlib import Path

import ansys.edb.core
import pytest

from tests.conftest import config
from tests.system.base_test_class import BaseTestClass

pytestmark = [pytest.mark.system, pytest.mark.grpc]


@pytest.mark.usefixtures("close_rpc_session")
class TestClass(BaseTestClass):
    def test_hfss_create_coax_port_on_component(self):
        """Create a coaxial port on a component from its pin."""
        edbapp = self.edb_examples.get_si_verse()
        assert edbapp.excitation_manager.create_coax_port_on_component("U1", "DDR4_DQS0_P")
        assert edbapp.excitation_manager.create_coax_port_on_component("U1", ["DDR4_DQS0_P", "DDR4_DQS0_N"], True)
        edbapp.close(terminate_rpc_session=False)

    def test_siwave_create_circuit_port_on_net(self):
        """Create a circuit port on a net."""
        edbapp = self.edb_examples.get_si_verse()
        initial_len = len(edbapp.padstacks.pingroups)
        assert edbapp.excitation_manager.create_circuit_port_on_net("U1", "1V0", "U1", "GND", 50, "test") == "test"
        p2 = edbapp.excitation_manager.create_circuit_port_on_net("U1", "PLL_1V8", "U1", "GND", 50, "test")
        assert p2 != "test" and "test" in p2
        pins = edbapp.components.get_pin_from_component("U1")
        p3 = edbapp.excitation_manager.create_circuit_port_on_pin(pins[200], pins[0], 45)
        assert p3 != ""
        p4 = edbapp.excitation_manager.create_circuit_port_on_net("U1", "USB3_D_P")
        assert len(edbapp.padstacks.pingroups) == initial_len + 6
        assert "GND" in p4 and "USB3_D_P" in p4
        assert "test" in edbapp.terminals
        assert edbapp.siwave.create_pin_group_on_net("U1", "1V0", "PG_V1P0_S0")
        assert edbapp.siwave.create_pin_group_on_net("U1", "GND", "U1_GND")
        assert edbapp.excitation_manager.create_circuit_port_on_pin_group(
            "PG_V1P0_S0", "U1_GND", impedance=50, name="test_port"
        )
        edbapp.ports["test_port"].name = "test_rename"
        assert any(port for port in list(edbapp.ports) if port == "test_rename")
        edbapp.close(terminate_rpc_session=False)

    def test_siwave_create_voltage_source(self):
        """Create a voltage source."""
        edbapp = self.edb_examples.get_si_verse()
        assert "Vsource_" in edbapp.excitation_manager.create_voltage_source_on_net(
            "U1", "USB3_D_P", "U1", "GND", 3.3, 0
        )
        assert len(edbapp.terminals) == 2
        assert list(edbapp.terminals.values())[0].magnitude == 3.3

        pins = edbapp.components.get_pin_from_component("U1")
        assert "VSource_" in edbapp.excitation_manager.create_voltage_source_on_pin(
            pins[300], pins[10], voltage_value=3.3, phase_value=1
        )
        assert len(edbapp.terminals) == 4
        assert list(edbapp.terminals.values())[2].phase == 1.0
        assert list(edbapp.terminals.values())[2].magnitude == 3.3

        u6 = edbapp.components["U6"]
        term1 = u6.pins["F2"].get_terminal(create_new_terminal=True)
        term2 = u6.pins["F1"].get_terminal(create_new_terminal=True)
        voltage_source = edbapp.create_voltage_source(terminal=term1, ref_terminal=term2)
        assert not voltage_source.is_null
        # testing source to ground assignment
        setup = edbapp.siwave.add_siwave_dc_analysis(name="Test_dc")
        setup.settings.add_source_terminal_to_ground("Vsource_U1_USB3_D_P_U1_GND", 1)
        if edbapp.grpc:
            assert "Vsource_U1_USB3_D_P_U1_GND" in setup.settings.source_terms_to_ground
        else:
            assert "Vsource_U1_USB3_D_P_U1_GND" in setup.settings.dc_ir.source_terms_to_ground
        edbapp.close(terminate_rpc_session=False)

    def test_siwave_create_current_source(self):
        """Create a current source."""
        edbapp = self.edb_examples.get_si_verse()
        assert edbapp.excitation_manager.create_current_source_on_net("U1", "USB3_D_N", "U1", "GND", 0.1, 0)
        pins = edbapp.components.get_pin_from_component("U1")
        assert "I22" == edbapp.excitation_manager.create_current_source_on_pin(pins[301], pins[10], 0.1, 0, "I22")

        assert edbapp.siwave.create_pin_group_on_net(reference_designator="U1", net_name="GND", group_name="gnd")
        edbapp.siwave.create_pin_group(reference_designator="U1", pin_numbers=["A27", "A28"], group_name="vrm_pos")
        edbapp.excitation_manager.create_current_source_on_pin_group(
            pos_pin_group_name="vrm_pos", neg_pin_group_name="gnd", name="vrm_current_source"
        )

        edbapp.siwave.create_pin_group(reference_designator="U1", pin_numbers=["R23", "P23"], group_name="sink_pos")
        edbapp.siwave.create_pin_group_on_net(reference_designator="U1", net_name="GND", group_name="gnd2")

        assert edbapp.excitation_manager.create_voltage_source_on_pin_group(
            "sink_pos", "gnd2", name="vrm_voltage_source"
        )
        edbapp.siwave.create_pin_group(reference_designator="U1", pin_numbers=["A27", "A28"], group_name="vp_pos")
        assert edbapp.siwave.create_pin_group_on_net(reference_designator="U1", net_name="GND", group_name="vp_neg")
        assert edbapp.siwave.pin_groups["vp_pos"]
        assert edbapp.siwave.pin_groups["vp_pos"].pins
        assert edbapp.siwave.create_voltage_probe_on_pin_group("vprobe", "vp_pos", "vp_neg")
        assert edbapp.terminals["vprobe"]
        edbapp.siwave.place_voltage_probe(
            "vprobe_2", "1V0", ["112mm", "24mm"], "1_Top", "GND", ["112mm", "27mm"], "Inner1(GND1)"
        )
        vprobe_2 = edbapp.terminals["vprobe_2"]
        ref_term = vprobe_2.reference_terminal
        assert isinstance(ref_term.location, list) or isinstance(ref_term.location, tuple)
        assert ref_term.layer
        ref_term.layer.name = "Inner1(GND1"
        ref_term.layer.name = "test"
        assert "test" in edbapp.stackup.layers
        u6 = edbapp.components["U6"]
        assert edbapp.create_current_source(
            u6.pins["H8"].get_terminal(create_new_terminal=True), u6.pins["G9"].get_terminal(create_new_terminal=True)
        )
        edbapp.close(terminate_rpc_session=False)

    def test_siwave_create_dc_terminal(self):
        """Create a DC terminal."""
        edbapp = self.edb_examples.get_si_verse()
        assert edbapp.siwave.create_dc_terminal("U1", "DDR4_DQ40", "dc_terminal1") == "dc_terminal1"
        edbapp.close(terminate_rpc_session=False)

    def test_siwave_create_resistor_on_pin(self):
        """Create a resistor on pin."""
        edbapp = self.edb_examples.get_si_verse()
        pins = edbapp.components.get_pin_from_component("U1")
        assert "RST4000" == edbapp.excitation_manager.create_resistor_on_pin(pins[302], pins[10], 40, "RST4000")
        edbapp.close(terminate_rpc_session=False)

    def test_create_rlc_boundary_on_pins(self):
        """Create HFSS RLC boundary on pins."""
        edb = self.edb_examples.get_si_verse()
        pins = edb.components.get_pin_from_component("U1", "1V0")
        ref_pins = edb.components.get_pin_from_component("U1", "GND")
        assert edb.excitation_manager.create_rlc_boundary_on_pins(
            pins[0], ref_pins[0], rvalue=1.05, lvalue=1.05e-12, cvalue=1.78e-13
        )
        edb.close(terminate_rpc_session=False)

    @pytest.mark.skipif(
        config["use_grpc"] and ansys.edb.core.__version__ == "0.2.6",
        reason="Test skipped for ansys-edb-core version 0.2.6",
    )
    def test_create_edge_port_on_polygon(self):
        """Create lumped and vertical port."""
        target_path = self.edb_examples.copy_test_files_into_local_folder("TEDB/edge_ports.aedb")[0]
        edb = self.edb_examples.load_edb(target_path)

        poly_list = [poly for poly in edb.layout.primitives if poly.primitive_type == "polygon"]
        port_poly = [poly for poly in poly_list if poly.id == 17][0]
        ref_poly = [poly for poly in poly_list if poly.id == 19][0]
        port_location = [-65e-3, -13e-3]
        ref_location = [-63e-3, -13e-3]
        assert edb.excitation_manager.create_edge_port_on_polygon(
            polygon=port_poly,
            reference_polygon=ref_poly,
            terminal_point=port_location,
            reference_point=ref_location,
        )
        port_poly = [poly for poly in poly_list if poly.id == 23][0]
        ref_poly = [poly for poly in poly_list if poly.id == 22][0]
        port_location = [-65e-3, -10e-3]
        ref_location = [-65e-3, -10e-3]
        assert edb.excitation_manager.create_edge_port_on_polygon(
            polygon=port_poly,
            reference_polygon=ref_poly,
            terminal_point=port_location,
            reference_point=ref_location,
        )
        port_poly = [poly for poly in poly_list if poly.id == 25][0]
        port_location = [-65e-3, -7e-3]
        assert edb.excitation_manager.create_edge_port_on_polygon(
            polygon=port_poly, terminal_point=port_location, reference_layer="gnd"
        )
        sig = edb.modeler.create_trace([[0, 0], ["9mm", 0]], "sig2", "1mm", "SIG", "Flat", "Flat")
        assert sig.create_edge_port("pcb_port_1", "end", "Wave", None, 8, 8)
        assert sig.create_edge_port("pcb_port_2", "start", "Gap")
        gap_port = edb.ports["pcb_port_2"]
        if edb.grpc:
            assert edb.ports["pcb_port_1"].is_wave_port
            assert not edb.ports["pcb_port_2"].is_wave_port
            assert gap_port.component.is_null
            assert not gap_port.is_circuit_port
        else:
            assert not gap_port.component
        assert gap_port.source_amplitude == 0.0
        assert gap_port.source_phase == 0.0
        assert gap_port.impedance
        from ansys.edb.core.database import ProductIdType  # noqa: F401

        assert not gap_port.deembed
        gap_port.name = "gap_port"
        assert gap_port.name == "gap_port"
        assert gap_port.renormalization_impedance == 50
        gap_port.is_circuit_port = True
        assert gap_port.is_circuit_port
        edb.close(terminate_rpc_session=False)

    @pytest.mark.skipif(
        config["use_grpc"] and ansys.edb.core.__version__ == "0.2.6",
        reason="Test skipped for ansys-edb-core version 0.2.6",
    )
    def test_create_various_ports_0(self):
        """Create various port types (edge, horizontal, wave, differential)."""
        target_path = self.edb_examples.copy_test_files_into_local_folder("edb_edge_ports.aedb")[0]
        edb = self.edb_examples.load_edb(target_path)
        if edb.grpc:
            prim_1_id = [i.edb_uid for i in edb.layout.primitives if i.net.name == "trace_2"][0]
            assert edb.excitation_manager.create_edge_port_vertical(prim_1_id, ["-66mm", "-4mm"], "port_ver")
            edge = edb.ports["port_ver"].core.edges[0]
            assert edge.point == (-0.066, -0.004)
        else:
            prim_1_id = [i.id for i in edb.modeler.primitives if i.net.name == "trace_2"][0]
            assert edb.excitation_manager.create_edge_port_vertical(prim_1_id, ["-66mm", "-4mm"], "port_ver")

        prim_2_id = [i.id for i in edb.layout.primitives if i.net.name == "trace_3"][0]
        if edb.grpc:
            assert edb.excitation_manager.create_edge_port_horizontal(
                prim_1_id, ["-60mm", "-4mm"], prim_2_id, ["-59mm", "-4mm"], "port_hori", 30, "Lower"
            )
        else:
            assert edb.excitation_manager.create_edge_port_horizontal(
                prim_1_id, ["-60mm", "-4mm"], prim_2_id, ["-59mm", "-4mm"], "port_hori", 30, "Lower"
            )
        if edb.grpc:
            assert edb.excitation_manager.get_ports_number() == 2
        else:
            assert edb.hfss.get_ports_number() == 2
        port_ver = edb.ports["port_ver"]
        assert not port_ver.is_null
        assert not port_ver.is_circuit_port
        assert port_ver.boundary_type in ["PortBoundary", "port"]

        port_hori = edb.ports["port_hori"]
        assert port_hori.reference_terminal

        kwargs = {
            "layer_name": "Top",
            "net_name": "SIGP",
            "width": "0.1mm",
            "start_cap_style": "Flat",
            "end_cap_style": "Flat",
        }
        traces = []
        trace_paths = [
            [["-40mm", "-10mm"], ["-30mm", "-10mm"]],
            [["-40mm", "-10.2mm"], ["-30mm", "-10.2mm"]],
            [["-40mm", "-10.4mm"], ["-30mm", "-10.4mm"]],
        ]
        for p in trace_paths:
            t = edb.modeler.create_trace(path_list=p, **kwargs)
            traces.append(t)

        paths_ids = [i.id for i in traces]
        pts = [i.center_line[0] for i in traces]
        if edb.grpc:
            wave_port = edb.excitation_manager.create_bundle_wave_port(paths_ids, pts)
        else:
            wave_port = edb.excitation_manager.create_bundle_wave_port(paths_ids, pts)
        wave_port.horizontal_extent_factor = 10
        assert wave_port.horizontal_extent_factor == 10
        wave_port.vertical_extent_factor = 10
        wave_port.radial_extent_factor = 1
        assert wave_port.radial_extent_factor == 1
        wave_port.pec_launch_width = "0.02mm"
        assert wave_port.pec_launch_width
        assert not wave_port.deembed
        assert wave_port.deembed_length == 0.0
        assert not wave_port.do_renormalize
        if edb.grpc:
            assert edb.excitation_manager.create_differential_wave_port(
                traces[1].id,
                trace_paths[0][0],
                traces[2].id,
                trace_paths[1][0],
                horizontal_extent_factor=8,
                port_name="df_port",
            )
        else:
            assert edb.excitation_manager.create_differential_wave_port(
                traces[1].id,
                trace_paths[0][0],
                traces[2].id,
                trace_paths[1][0],
                horizontal_extent_factor=8,
                port_name="df_port",
            )
        assert not edb.ports["df_port"].is_null
        p, n = edb.ports["df_port"].terminals
        assert p.name == "df_port:T1"
        assert n.name == "df_port:T2"
        edb.ports["df_port"].decouple()
        p.couple_ports(n)

        traces_id = [i.id for i in traces]
        paths = [i[1] for i in trace_paths]
        if edb.grpc:
            df_port = edb.excitation_manager.create_bundle_wave_port(traces_id, paths)
        else:
            df_port = edb.excitation_manager.create_bundle_wave_port(traces_id, paths)
        assert df_port.name
        assert df_port.terminals
        df_port.horizontal_extent_factor = 10
        df_port.vertical_extent_factor = 10
        df_port.deembed = True
        df_port.deembed_length = "1mm"
        assert df_port.horizontal_extent_factor == 10
        assert df_port.vertical_extent_factor == 10
        assert df_port.deembed
        assert df_port.deembed_length == 1e-3
        edb.close(terminate_rpc_session=False)

    @pytest.mark.skipif(
        config["use_grpc"] and ansys.edb.core.__version__ == "0.2.6",
        reason="Test skipped for ansys-edb-core version 0.2.6",
    )
    def test_create_various_ports_1(self):
        """Create wave port and differential wave port via traces."""
        target_path = self.edb_examples.copy_test_files_into_local_folder("edb_edge_ports.aedb")[0]
        edb = self.edb_examples.load_edb(target_path)
        kwargs = {
            "layer_name": "TOP",
            "net_name": "SIGP",
            "width": "0.1mm",
            "start_cap_style": "Flat",
            "end_cap_style": "Flat",
        }
        traces = []
        trace_paths = [
            [["-40mm", "-10mm"], ["-30mm", "-10mm"]],
            [["-40mm", "-10.2mm"], ["-30mm", "-10.2mm"]],
            [["-40mm", "-10.4mm"], ["-30mm", "-10.4mm"]],
        ]
        for p in trace_paths:
            t = edb.modeler.create_trace(path_list=p, **kwargs)
            traces.append(t)

        if config["use_grpc"]:
            assert edb.excitation_manager.create_wave_port(traces[0].id, trace_paths[0][1], "wave_port")
        else:
            assert edb.excitation_manager.create_wave_port(traces[0], trace_paths[0][0], "wave_port")

        assert edb.excitation_manager.create_differential_wave_port(
            traces[0],
            trace_paths[0][0],
            traces[1],
            trace_paths[1][0],
            horizontal_extent_factor=8,
        )

        paths = [i[1] for i in trace_paths]
        if config["use_grpc"]:
            p = edb.excitation_manager.create_bundle_wave_port(traces, paths, port_name="port2")
        else:
            p = edb.excitation_manager.create_bundle_wave_port(traces, paths)
        p.horizontal_extent_factor = 6
        p.vertical_extent_factor = 5
        p.pec_launch_width = "0.02mm"
        p.radial_extent_factor = 1
        assert p.horizontal_extent_factor == 6
        assert p.vertical_extent_factor == 5
        assert p.pec_launch_width == "0.02mm"
        assert p.radial_extent_factor == 1
        edb.close(terminate_rpc_session=False)

    @pytest.mark.skipif(
        config["use_grpc"] and config["desktopVersion"] < "2026.1", reason="working with latest release"
    )
    def test_ports_and_sources_creation(self):
        """Create ports and sources from padstack terminals."""
        edbapp = self.edb_examples.get_si_verse()
        p1 = edbapp.padstacks.instances_by_name["Via1"].create_terminal("p1")
        p2 = edbapp.padstacks.instances_by_name["Via2"].create_terminal("p2")
        edbapp.create_port(p1, p2, True, "test")
        assert edbapp.ports["test"]
        p3 = edbapp.padstacks.instances_by_name["Via3"].create_terminal("p3")
        p4 = edbapp.padstacks.instances_by_name["Via4"].create_terminal("p4")
        edbapp.create_port(p3, p4, False, "test2")
        assert edbapp.ports["test2"]

    def test_horizontal_wave_ports(self):
        """Create horizontal wave ports from voids."""
        local_path = Path(__file__).parent.parent
        example_folder = os.path.join(local_path, "example_models", "TEDB")
        source_path_edb = os.path.join(example_folder, "example_arbitrary_wave_ports.aedb")
        edbapp = self.edb_examples.load_edb(source_path_edb)
        voids = edbapp.layout.primitives[0].voids
        for void in voids:
            edbapp.excitation_manager.create_horizontal_wave_port(void)
        assert len(edbapp.ports) == 6
        edbapp.close(terminate_rpc_session=False)
