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

"""Tests related to Edb"""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from pyedb.generic.general_methods import is_linux
from tests.conftest import config
from tests.system.base_test_class import BaseTestClass

pytestmark = [pytest.mark.system, pytest.mark.grpc]

ON_CI = os.environ.get("CI", "false").lower() == "true"


@pytest.mark.usefixtures("close_rpc_session")
class TestClass(BaseTestClass):
    def test_hfss_create_coax_port_on_component_from_hfss(self):
        """Create a coaxial port on a component from its pin."""
        edbapp = self.edb_examples.get_si_verse()
        assert edbapp.hfss.create_coax_port_on_component("U1", "DDR4_DQS0_P")
        assert edbapp.hfss.create_coax_port_on_component("U1", ["DDR4_DQS0_P", "DDR4_DQS0_N"], True)
        edbapp.close(terminate_rpc_session=False)

    def test_layout_bounding_box(self):
        """Evaluate layout bounding box"""
        edbapp = self.edb_examples.get_si_verse()
        assert len(edbapp.get_bounding_box()) == 2
        bbox = [[round(i, 6) for i in j] for j in edbapp.get_bounding_box()]
        assert bbox == [[-0.014260, -0.004550], [0.150105, 0.080000]]
        edbapp.close(terminate_rpc_session=False)

    def test_siwave_create_circuit_port_on_net(self):
        """Create a circuit port on a net."""
        edbapp = self.edb_examples.get_si_verse()
        initial_len = len(edbapp.padstacks.pingroups)
        assert edbapp.siwave.create_circuit_port_on_net("U1", "1V0", "U1", "GND", 50, "test") == "test"
        p2 = edbapp.siwave.create_circuit_port_on_net("U1", "PLL_1V8", "U1", "GND", 50, "test")
        assert p2 != "test" and "test" in p2
        pins = edbapp.components.get_pin_from_component("U1")
        p3 = edbapp.siwave.create_circuit_port_on_pin(pins[200], pins[0], 45)
        assert p3 != ""
        p4 = edbapp.hfss.create_circuit_port_on_net("U1", "USB3_D_P")
        assert len(edbapp.padstacks.pingroups) == initial_len + 6
        assert "GND" in p4 and "USB3_D_P" in p4
        assert "test" in edbapp.terminals
        assert edbapp.siwave.create_pin_group_on_net("U1", "1V0", "PG_V1P0_S0")
        assert edbapp.siwave.create_pin_group_on_net("U1", "GND", "U1_GND")
        assert edbapp.siwave.create_circuit_port_on_pin_group("PG_V1P0_S0", "U1_GND", impedance=50, name="test_port")
        edbapp.excitations["test_port"].name = "test_rename"
        assert any(port for port in list(edbapp.excitations) if port == "test_rename")
        edbapp.close(terminate_rpc_session=False)

    def test_siwave_create_voltage_source(self):
        """Create a voltage source."""
        edbapp = self.edb_examples.get_si_verse()
        assert "Vsource_" in edbapp.siwave.create_voltage_source_on_net("U1", "USB3_D_P", "U1", "GND", 3.3, 0)
        assert len(edbapp.terminals) == 2
        assert list(edbapp.terminals.values())[0].magnitude == 3.3

        pins = edbapp.components.get_pin_from_component("U1")
        assert "VSource_" in edbapp.siwave.create_voltage_source_on_pin(
            pins[300], pins[10], voltage_value=3.3, phase_value=1
        )
        assert len(edbapp.terminals) == 4
        assert list(edbapp.terminals.values())[2].phase == 1.0
        assert list(edbapp.terminals.values())[2].magnitude == 3.3

        u6 = edbapp.components["U6"]
        voltage_source = edbapp.create_voltage_source(
            u6.pins["F2"].get_terminal(create_new_terminal=True), u6.pins["F1"].get_terminal(create_new_terminal=True)
        )
        assert not voltage_source.is_null
        edbapp.close(terminate_rpc_session=False)

    def test_siwave_create_current_source(self):
        """Create a current source."""

        edbapp = self.edb_examples.get_si_verse()
        assert edbapp.siwave.create_current_source_on_net("U1", "USB3_D_N", "U1", "GND", 0.1, 0)
        pins = edbapp.components.get_pin_from_component("U1")
        assert "I22" == edbapp.siwave.create_current_source_on_pin(pins[301], pins[10], 0.1, 0, "I22")

        assert edbapp.siwave.create_pin_group_on_net(reference_designator="U1", net_name="GND", group_name="gnd")
        edbapp.siwave.create_pin_group(reference_designator="U1", pin_numbers=["A27", "A28"], group_name="vrm_pos")
        edbapp.siwave.create_current_source_on_pin_group(
            pos_pin_group_name="vrm_pos", neg_pin_group_name="gnd", name="vrm_current_source"
        )

        edbapp.siwave.create_pin_group(reference_designator="U1", pin_numbers=["R23", "P23"], group_name="sink_pos")
        edbapp.siwave.create_pin_group_on_net(reference_designator="U1", net_name="GND", group_name="gnd2")

        # move to source_excitations when dotnet is removed
        assert edbapp.siwave.create_voltage_source_on_pin_group("sink_pos", "gnd2", name="vrm_voltage_source")
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
        # ref_term.location = [0, 0] # position setter is crashing check pyedb-core bug #431
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

    def test_siwave_create_resistors_on_pin(self):
        """Create a resistor on pin."""
        edbapp = self.edb_examples.get_si_verse()
        pins = edbapp.components.get_pin_from_component("U1")
        assert "RST4000" == edbapp.siwave.create_resistor_on_pin(pins[302], pins[10], 40, "RST4000")
        edbapp.close(terminate_rpc_session=False)

    def test_siwave_add_syz_analsyis(self):
        """Add a sywave AC analysis."""
        edbapp = self.edb_examples.get_si_verse()
        syz_setup = edbapp.siwave.add_siwave_syz_analysis(start_freq="1GHz", stop_freq="10GHz", step_freq="10MHz")
        syz_setup.use_custom_settings = False
        assert not syz_setup.use_custom_settings
        syz_setup.advanced_settings.min_void_area = "4mm2"
        assert syz_setup.advanced_settings.min_void_area == "4mm2"
        syz_setup.advanced_settings.mesh_automatic = True
        assert syz_setup.advanced_settings.mesh_automatic
        syz_setup.dc_advanced_settings.dc_min_plane_area_to_mesh = "0.5mm2"
        assert syz_setup.dc_advanced_settings.dc_min_plane_area_to_mesh == "0.5mm2"
        syz_setup.dc_settings.use_dc_custom_settings = False
        assert not syz_setup.dc_settings.use_dc_custom_settings
        syz_sweep = syz_setup.add_sweep()
        syz_sweep.enforce_causality = False
        assert not syz_sweep.enforce_causality
        edbapp.close(terminate_rpc_session=False)

    def test_siwave_add_dc_analysis(self):
        """Add a sywave DC analysis."""
        edbapp = self.edb_examples.get_si_verse()
        assert edbapp.siwave.add_siwave_dc_analysis(name="Test_dc")
        edbapp.close(terminate_rpc_session=False)

    def test_hfss_mesh_operations(self):
        """Retrieve the trace width for traces with ports."""
        edbapp = self.edb_examples.get_si_verse()
        edbapp.components.create_port_on_component(
            "U1",
            ["VDD_DDR"],
            reference_net="GND",
            port_type="circuit_port",
        )
        mesh_ops = edbapp.hfss.get_trace_width_for_traces_with_ports()
        assert len(mesh_ops) > 0
        edbapp.close(terminate_rpc_session=False)

    def test_add_variables(self):
        """Add design and project variables."""
        edbapp = self.edb_examples.get_si_verse()
        edbapp.add_design_variable("my_variable", "1mm")
        assert "my_variable" in edbapp.get_all_variable_names()
        assert edbapp.modeler.parametrize_trace_width("DDR4_DQ25")
        assert edbapp.modeler.parametrize_trace_width("DDR4_A2")
        if edbapp.grpc:
            edbapp.add_design_variable("my_parameter", "2mm", "test description")
        else:
            edbapp.add_design_variable("my_parameter", "2mm", True)
        assert "my_parameter" in edbapp.get_all_variable_names()
        variable_value = edbapp.get_variable_value("my_parameter")
        assert variable_value.value == 2e-3
        if edbapp.grpc:
            assert not edbapp.add_design_variable("my_parameter", "2mm", "test description")
        else:
            # grpc and DotNet variable implementation server are too different.
            assert not edbapp.add_design_variable("my_parameter", "2mm", True)[0]
        edbapp.add_project_variable("$my_project_variable", "3mm")
        if edbapp.grpc:
            assert edbapp.db.get_variable_value("$my_project_variable") == 3e-3
        else:
            # grpc implementation is very different.
            assert edbapp.get_variable_value("$my_project_variable").value == 3e-3
        if edbapp.grpc:
            assert not edbapp.add_project_variable("$my_project_variable", "3mm")
        else:
            # grpc and DotNet variable implementation server are too different.
            assert not edbapp.add_project_variable("$my_project_variable", "3mm")[0]
        edbapp.close(terminate_rpc_session=False)

    def test_save_edb_as(self):
        """Save edb as some file."""
        edbapp = self.edb_examples.create_empty_edb()
        target_path = Path(self.edb_examples.test_folder) / "si_verse_new.aedb"
        assert edbapp.save_as(target_path)
        assert (target_path / "edb.def").exists()
        edbapp.close(terminate_rpc_session=False)

    def test_export_3d(self):
        """Export EDB to HFSS."""
        mock_process = MagicMock()
        edb = self.edb_examples.create_empty_edb()
        options_config = {"UNITE_NETS": 1, "LAUNCH_Q3D": 0}
        out = edb.write_export3d_option_config_file(self.edb_examples.test_folder, options_config)
        assert Path(out).exists()
        with patch("subprocess.run", return_value=mock_process) as mock_run:
            executable = "siwave" if is_linux else "siwave.exe"

            edb.export_hfss(None)
            popen_args, _ = mock_run.call_args
            input_cmd = popen_args[0]

            input_cmd_ = [
                str(Path(edb.ansys_em_path) / executable),
                "-RunScriptAndExit",
                str(Path(edb.edbpath).parent / "export_cad.py"),
            ]
            assert input_cmd == input_cmd_  # if is_linux else " ".join(input_cmd_)

            edb.export_q3d(None)
            popen_args, _ = mock_run.call_args
            input_cmd = popen_args[0]

            input_cmd_ = [
                str(Path(edb.ansys_em_path) / executable),
                "-RunScriptAndExit",
                str(Path(edb.edbpath).parent / "export_cad.py"),
            ]
            assert input_cmd == input_cmd_  # if is_linux else " ".join(input_cmd_)

            edb.export_maxwell(None)
            popen_args, _ = mock_run.call_args
            input_cmd = popen_args[0]

            input_cmd_ = [
                str(Path(edb.ansys_em_path) / executable),
                "-RunScriptAndExit",
                str(Path(edb.edbpath).parent / "export_cad.py"),
            ]
            assert input_cmd == input_cmd_  # if is_linux else " ".join(input_cmd_)

        edb.close(terminate_rpc_session=False)

    def test_create_edge_port_on_polygon(self):
        """Create lumped and vertical port."""
        target_path = self.edb_examples.copy_test_files_into_local_folder("TEDB/edge_ports.aedb")[0]
        edb = self.edb_examples.load_edb(target_path)
        poly_list = [poly for poly in edb.layout.primitives if poly.primitive_type == "polygon"]
        port_poly = [poly for poly in poly_list if poly.id == 17][0]
        ref_poly = [poly for poly in poly_list if poly.id == 19][0]
        port_location = [-65e-3, -13e-3]
        ref_location = [-63e-3, -13e-3]
        if edb.grpc:
            assert edb.excitation_manager.create_edge_port_on_polygon(
                polygon=port_poly,
                reference_polygon=ref_poly,
                terminal_point=port_location,
                reference_point=ref_location,
            )
        else:
            # method already deprecated in grpc.
            assert edb.hfss.create_edge_port_on_polygon(
                polygon=port_poly,
                reference_polygon=ref_poly,
                terminal_point=port_location,
                reference_point=ref_location,
            )
        port_poly = [poly for poly in poly_list if poly.id == 23][0]
        ref_poly = [poly for poly in poly_list if poly.id == 22][0]
        port_location = [-65e-3, -10e-3]
        ref_location = [-65e-3, -10e-3]
        if edb.grpc:
            assert edb.excitation_manager.create_edge_port_on_polygon(
                polygon=port_poly,
                reference_polygon=ref_poly,
                terminal_point=port_location,
                reference_point=ref_location,
            )
        else:
            # method already deprecated in grpc.
            assert edb.hfss.create_edge_port_on_polygon(
                polygon=port_poly,
                reference_polygon=ref_poly,
                terminal_point=port_location,
                reference_point=ref_location,
            )
        port_poly = [poly for poly in poly_list if poly.id == 25][0]
        port_location = [-65e-3, -7e-3]
        if edb.grpc:
            assert edb.excitation_manager.create_edge_port_on_polygon(
                polygon=port_poly, terminal_point=port_location, reference_layer="gnd"
            )
        else:
            # method already deprecated in grpc.
            assert edb.hfss.create_edge_port_on_polygon(
                polygon=port_poly, terminal_point=port_location, reference_layer="gnd"
            )
        sig = edb.modeler.create_trace([[0, 0], ["9mm", 0]], "sig2", "1mm", "SIG", "Flat", "Flat")
        assert sig.create_edge_port("pcb_port_1", "end", "Wave", None, 8, 8)
        assert sig.create_edge_port("pcb_port_2", "start", "gap")
        gap_port = edb.ports["pcb_port_2"]
        if edb.grpc:
            assert gap_port.component.is_null
        else:
            assert not gap_port.component
        assert gap_port.source_amplitude == 0.0
        assert gap_port.source_phase == 0.0
        assert gap_port.impedance
        assert not gap_port.deembed
        gap_port.name = "gap_port"
        assert gap_port.name == "gap_port"
        assert gap_port.renormalization_impedance == 50
        gap_port.is_circuit_port = True
        assert gap_port.is_circuit_port
        edb.close(terminate_rpc_session=False)

    @pytest.mark.skipif(
        is_linux and ON_CI,
        reason="Randomly crashing on Linux.",
    )
    def test_edb_statistics(self):
        """Get statistics."""
        edb = self.edb_examples.get_si_verse()
        edb_stats = edb.get_statistics(compute_area=False)
        assert edb_stats
        assert edb_stats.num_layers
        assert edb_stats.stackup_thickness
        assert edb_stats.num_vias
        # assert edb_stats.occupying_ratio
        # assert edb_stats.occupying_surface
        assert edb_stats.layout_size
        assert edb_stats.num_polygons
        assert edb_stats.num_traces
        assert edb_stats.num_nets
        assert edb_stats.num_discrete_components
        assert edb_stats.num_inductors
        assert edb_stats.num_capacitors
        assert edb_stats.num_resistors

        # assert edb_stats.occupying_ratio["1_Top"] == 0.301682
        # assert edb_stats.occupying_ratio["Inner1(GND1)"] == 0.937467
        # assert edb_stats.occupying_ratio["16_Bottom"] == 0.204925
        edb.close(terminate_rpc_session=False)

    def test_create_rlc_component(self):
        """Create rlc components from pin"""
        edb = self.edb_examples.get_si_verse()
        pins = edb.components.get_pin_from_component("U1", "1V0")
        ref_pins = edb.components.get_pin_from_component("U1", "GND")
        assert edb.components.create([pins[0], ref_pins[0]], "test_0rlc", r_value=1.67, l_value=1e-13, c_value=1e-11)
        assert edb.components.create([pins[0], ref_pins[0]], "test_1rlc", r_value=None, l_value=1e-13, c_value=1e-11)
        assert edb.components.create([pins[0], ref_pins[0]], "test_2rlc", r_value=None, c_value=1e-13)
        edb.close(terminate_rpc_session=False)

    def test_create_rlc_boundary_on_pins(self):
        """Create hfss rlc boundary on pins."""
        edb = self.edb_examples.get_si_verse()
        pins = edb.components.get_pin_from_component("U1", "1V0")
        ref_pins = edb.components.get_pin_from_component("U1", "GND")
        assert edb.hfss.create_rlc_boundary_on_pins(pins[0], ref_pins[0], rvalue=1.05, lvalue=1.05e-12, cvalue=1.78e-13)
        edb.close(terminate_rpc_session=False)

    def test_configure_hfss_analysis_setup_enforce_causality(self):
        """Configure HFSS analysis setup."""
        edb = self.edb_examples.get_si_verse()
        assert len(edb.setups) == 0
        edb.hfss.add_setup()
        assert edb.hfss_setups
        assert len(edb.setups) == 1
        assert list(edb.setups)[0]
        setup = list(edb.hfss_setups.values())[0]
        setup.add_sweep()
        assert len(setup.sweep_data) == 1
        assert not setup.sweep_data[0].enforce_causality
        sweeps = setup.sweep_data
        for sweep in sweeps:
            sweep.enforce_causality = True
        setup.sweep_data = sweeps
        assert setup.sweep_data[0].enforce_causality
        edb.close()

    def test_create_various_ports_0(self):
        """Create various ports."""
        target_path = self.edb_examples.copy_test_files_into_local_folder("edb_edge_ports.aedb")[0]
        edb = self.edb_examples.load_edb(target_path)
        if edb.grpc:
            prim_1_id = [i.edb_uid for i in edb.modeler.primitives if i.net.name == "trace_2"][0]
            assert edb.excitation_manager.create_edge_port_vertical(prim_1_id, ["-66mm", "-4mm"], "port_ver")
        else:
            # This method is also available at same location in grpc but is deprecated.
            prim_1_id = [i.id for i in edb.modeler.primitives if i.net.name == "trace_2"][0]
            assert edb.hfss.create_edge_port_vertical(prim_1_id, ["-66mm", "-4mm"], "port_ver")

        prim_2_id = [i.id for i in edb.modeler.primitives if i.net.name == "trace_3"][0]
        if edb.grpc:
            assert edb.excitation_manager.create_edge_port_horizontal(
                prim_1_id, ["-60mm", "-4mm"], prim_2_id, ["-59mm", "-4mm"], "port_hori", 30, "Lower"
            )
        else:
            # This method is also available at same location in grpc but is deprecated.
            assert edb.hfss.create_edge_port_horizontal(
                prim_1_id, ["-60mm", "-4mm"], prim_2_id, ["-59mm", "-4mm"], "port_hori", 30, "Lower"
            )
        if edb.grpc:
            assert edb.excitation_manager.get_ports_number() == 2
        else:
            assert edb.hfss.get_ports_number() == 2
        port_ver = edb.ports["port_ver"]
        assert not port_ver.is_null
        assert not port_ver.is_circuit_port
        assert port_ver.boundary_type in ["PortBoundary", "port"]  # grpc returns 'port'

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
            wave_port = edb.hfss.create_bundle_wave_port(paths_ids, pts)
        wave_port.horizontal_extent_factor = 10
        assert wave_port.horizontal_extent_factor == 10
        wave_port.vertical_extent_factor = 10
        wave_port.radial_extent_factor = 1
        assert wave_port.radial_extent_factor == 1
        wave_port.pec_launch_width = "0.02mm"
        assert wave_port.pec_launch_width
        assert not wave_port.deembed
        assert wave_port.deembed_length == 0.0
        # TODO check bug pyedb-core #675
        # wave_port.do_renormalize = True
        # assert wave_port.do_renormalize
        # wave_port.do_renormalize = False
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
            assert edb.hfss.create_differential_wave_port(
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
            df_port = edb.hfss.create_bundle_wave_port(traces_id, paths)
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

    def test_create_various_ports_1(self):
        """Create various ports."""
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
            assert edb.hfss.create_wave_port(traces[0], trace_paths[0][0], "wave_port")

        assert edb.hfss.create_differential_wave_port(
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
            p = edb.hfss.create_bundle_wave_port(traces, paths)
        p.horizontal_extent_factor = 6
        p.vertical_extent_factor = 5
        p.pec_launch_width = "0.02mm"
        p.radial_extent_factor = 1
        assert p.horizontal_extent_factor == 6
        assert p.vertical_extent_factor == 5
        assert p.pec_launch_width == "0.02mm"
        assert p.radial_extent_factor == 1
        edb.close(terminate_rpc_session=False)

    def test_set_all_antipad_values(self):
        """Set all anti-pads from all pad-stack definition to the given value."""
        edb = self.edb_examples.get_si_verse()
        assert edb.padstacks.set_all_antipad_value(0.0)
        edb.close(terminate_rpc_session=False)

    @pytest.mark.skipif(config["use_grpc"], reason="This method is not yet implemented in grpc.")
    def test_hfss_simulation_setup(self):
        """Create a setup from a template and evaluate its properties."""
        edbapp = self.edb_examples.get_si_verse()
        setup1 = edbapp.hfss.add_setup("setup1")
        assert not edbapp.hfss.add_setup("setup1")
        assert setup1.set_solution_single_frequency()
        if "adaptive_solution_type" in dir(setup1.adaptive_settings):
            assert setup1.adaptive_settings.adaptive_solution_type == "single"
        else:
            assert len(setup1.adaptive_settings.adaptive_frequency_data_list) == 1
        assert setup1.set_solution_multi_frequencies(frequencies=("5GHz", "10GHz", "100GHz"))
        if "adaptive_solution_type" in dir(setup1.adaptive_settings):
            assert setup1.adaptive_settings.adaptive_solution_type == "multi_frequencies"
        else:
            assert len(setup1.adaptive_settings.adaptive_frequency_data_list) == 3
        assert setup1.set_solution_broadband()
        if "adaptive_solution_type" in dir(setup1.adaptive_settings):
            assert setup1.adaptive_settings.adaptive_solution_type == "broadband"
        else:
            assert len(setup1.adaptive_settings.adaptive_frequency_data_list) == 2
        setup1.hfss_solver_settings.enhanced_low_frequency_accuracy = True
        assert setup1.hfss_solver_settings.enhanced_low_frequency_accuracy
        setup1.hfss_solver_settings.relative_residual = 0.0002
        assert setup1.hfss_solver_settings.relative_residual == 0.0002
        setup1.hfss_solver_settings.use_shell_elements = True
        assert setup1.hfss_solver_settings.use_shell_elements

        setup1 = edbapp.setups["setup1"]
        assert not setup1.is_null
        setup1.adaptive_settings.max_refine_per_pass = 20
        assert setup1.adaptive_settings.max_refine_per_pass == 20
        setup1.adaptive_settings.min_passes = 2
        assert setup1.adaptive_settings.min_passes == 2
        setup1.adaptive_settings.save_fields = True
        assert setup1.adaptive_settings.save_fields
        setup1.adaptive_settings.save_rad_field_only = True
        assert setup1.adaptive_settings.save_rad_field_only
        assert edbapp.setups["setup1"].adaptive_settings.adapt_type in ["kBroadband", "broadband"]
        edbapp.setups["setup1"].adaptive_settings.use_max_refinement = True
        assert edbapp.setups["setup1"].adaptive_settings.use_max_refinement
        edbapp.setups["setup1"].defeature_settings.defeature_abs_length = "1um"
        assert edbapp.setups["setup1"].defeature_settings.defeature_abs_length == "1um"
        edbapp.setups["setup1"].defeature_settings.defeature_ratio = 1e-5
        assert edbapp.setups["setup1"].defeature_settings.defeature_ratio == 1e-5
        edbapp.setups["setup1"].defeature_settings.healing_option = 0
        assert edbapp.setups["setup1"].defeature_settings.healing_option == 0
        edbapp.setups["setup1"].defeature_settings.remove_floating_geometry = True
        assert edbapp.setups["setup1"].defeature_settings.remove_floating_geometry
        edbapp.setups["setup1"].defeature_settings.small_void_area = 0.1
        assert edbapp.setups["setup1"].defeature_settings.small_void_area == 0.1
        edbapp.setups["setup1"].defeature_settings.union_polygons = False
        assert not edbapp.setups["setup1"].defeature_settings.union_polygons
        edbapp.setups["setup1"].defeature_settings.use_defeature = False
        assert not edbapp.setups["setup1"].defeature_settings.use_defeature
        edbapp.setups["setup1"].defeature_settings.use_defeature_abs_length = True
        assert edbapp.setups["setup1"].defeature_settings.use_defeature_abs_length
        edbapp.setups["setup1"].via_settings.via_density = 1.0
        assert edbapp.setups["setup1"].via_settings.via_density == 1.0
        edbapp.setups["setup1"].via_settings.via_material = "pec"
        assert edbapp.setups["setup1"].via_settings.via_material == "pec"
        edbapp.setups["setup1"].via_settings.via_num_sides = 8
        assert edbapp.setups["setup1"].via_settings.via_num_sides == 8
        assert edbapp.setups["setup1"].via_settings.via_style in ["k25DViaWirebond", "mesh"]
        edbapp.setups["setup1"].advanced_mesh_settings.layer_snap_tol = "1e-6"
        assert edbapp.setups["setup1"].advanced_mesh_settings.layer_snap_tol == "1e-6"
        edbapp.setups["setup1"].curve_approx_settings.arc_to_chord_error = "0.1"
        assert edbapp.setups["setup1"].curve_approx_settings.arc_to_chord_error == "0.1"
        edbapp.setups["setup1"].curve_approx_settings.max_arc_points = 12
        assert edbapp.setups["setup1"].curve_approx_settings.max_arc_points == 12
        edbapp.setups["setup1"].dcr_settings.conduction_max_passes = 11
        assert edbapp.setups["setup1"].dcr_settings.conduction_max_passes == 11
        edbapp.setups["setup1"].dcr_settings.conduction_min_converged_passes = 2
        assert edbapp.setups["setup1"].dcr_settings.conduction_min_converged_passes == 2
        edbapp.setups["setup1"].dcr_settings.conduction_min_passes = 5
        assert edbapp.setups["setup1"].dcr_settings.conduction_min_passes == 5
        edbapp.setups["setup1"].dcr_settings.conduction_per_error = 2.0
        assert edbapp.setups["setup1"].dcr_settings.conduction_per_error == 2.0
        edbapp.setups["setup1"].dcr_settings.conduction_per_refine = 20.0
        assert edbapp.setups["setup1"].dcr_settings.conduction_per_refine == 20.0
        edbapp.setups["setup1"].hfss_port_settings.max_delta_z0 = 0.5
        assert edbapp.setups["setup1"].hfss_port_settings.max_delta_z0 == 0.5
        edbapp.setups["setup1"].hfss_port_settings.max_triangles_wave_port = 1000
        assert edbapp.setups["setup1"].hfss_port_settings.max_triangles_wave_port == 1000
        edbapp.setups["setup1"].hfss_port_settings.min_triangles_wave_port = 500
        assert edbapp.setups["setup1"].hfss_port_settings.min_triangles_wave_port == 500
        edbapp.setups["setup1"].hfss_port_settings.enable_set_triangles_wave_port = True
        assert edbapp.setups["setup1"].hfss_port_settings.enable_set_triangles_wave_port
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(config["use_grpc"], reason="This method is not yet implemented in grpc.")
    def test_hfss_simulation_setups_consolidation(self):
        """Create a setup from a template and evaluate its properties."""
        edbapp = self.edb_examples.get_si_verse()
        setup1 = edbapp.hfss.add_setup("setup1")
        assert not edbapp.hfss.add_setup("setup1")
        assert setup1.set_solution_single_frequency()
        if "adaptive_solution_type" in dir(setup1.adaptive_settings):
            assert setup1.adaptive_settings.adaptive_solution_type == "single"
        else:
            assert len(setup1.adaptive_settings.adaptive_frequency_data_list) == 1
        assert setup1.set_solution_multi_frequencies(frequencies=("5GHz", "10GHz", "100GHz"))
        if "adaptive_solution_type" in dir(setup1.adaptive_settings):
            assert setup1.adaptive_settings.adaptive_solution_type == "multi_frequencies"
        else:
            assert len(setup1.adaptive_settings.adaptive_frequency_data_list) == 3
        assert setup1.set_solution_broadband()
        if "adaptive_solution_type" in dir(setup1.adaptive_settings):
            assert setup1.adaptive_settings.adaptive_solution_type == "broadband"
        else:
            assert len(setup1.adaptive_settings.adaptive_frequency_data_list) == 2
        setup1.hfss_solver_settings.enhanced_low_frequency_accuracy = True
        assert setup1.hfss_solver_settings.enhanced_low_frequency_accuracy
        setup1.hfss_solver_settings.relative_residual = 0.0002
        assert setup1.hfss_solver_settings.relative_residual == 0.0002
        setup1.hfss_solver_settings.use_shell_elements = True
        assert setup1.hfss_solver_settings.use_shell_elements

        setup1 = edbapp.setups["setup1"]
        assert not setup1.is_null
        setup1.adaptive_settings.max_refine_per_pass = 20
        assert setup1.adaptive_settings.max_refine_per_pass == 20
        setup1.adaptive_settings.min_passes = 2
        assert setup1.adaptive_settings.min_passes == 2
        setup1.adaptive_settings.save_fields = True
        assert setup1.adaptive_settings.save_fields
        setup1.adaptive_settings.save_rad_field_only = True
        assert setup1.adaptive_settings.save_rad_field_only
        assert edbapp.setups["setup1"].adaptive_settings.adapt_type in ["kBroadband", "broadband"]
        edbapp.setups["setup1"].adaptive_settings.use_max_refinement = True
        assert edbapp.setups["setup1"].adaptive_settings.use_max_refinement
        edbapp.setups["setup1"].defeature_settings.defeature_abs_length = "1um"
        assert edbapp.setups["setup1"].defeature_settings.defeature_abs_length == "1um"
        edbapp.setups["setup1"].defeature_settings.defeature_ratio = 1e-5
        assert edbapp.setups["setup1"].defeature_settings.defeature_ratio == 1e-5
        edbapp.setups["setup1"].defeature_settings.healing_option = 0
        assert edbapp.setups["setup1"].defeature_settings.healing_option == 0
        edbapp.setups["setup1"].defeature_settings.remove_floating_geometry = True
        assert edbapp.setups["setup1"].defeature_settings.remove_floating_geometry
        edbapp.setups["setup1"].defeature_settings.small_void_area = 0.1
        assert edbapp.setups["setup1"].defeature_settings.small_void_area == 0.1
        edbapp.setups["setup1"].defeature_settings.union_polygons = False
        assert not edbapp.setups["setup1"].defeature_settings.union_polygons
        edbapp.setups["setup1"].defeature_settings.use_defeature = False
        assert not edbapp.setups["setup1"].defeature_settings.use_defeature
        edbapp.setups["setup1"].defeature_settings.use_defeature_abs_length = True
        assert edbapp.setups["setup1"].defeature_settings.use_defeature_abs_length
        edbapp.setups["setup1"].via_settings.via_density = 1.0
        assert edbapp.setups["setup1"].via_settings.via_density == 1.0
        edbapp.setups["setup1"].via_settings.via_material = "pec"
        assert edbapp.setups["setup1"].via_settings.via_material == "pec"
        edbapp.setups["setup1"].via_settings.via_num_sides = 8
        assert edbapp.setups["setup1"].via_settings.via_num_sides == 8
        assert edbapp.setups["setup1"].via_settings.via_style in ["k25DViaWirebond", "mesh"]
        edbapp.setups["setup1"].advanced_mesh_settings.layer_snap_tol = "1e-6"
        assert edbapp.setups["setup1"].advanced_mesh_settings.layer_snap_tol == "1e-6"
        edbapp.setups["setup1"].curve_approx_settings.arc_to_chord_error = "0.1"
        assert edbapp.setups["setup1"].curve_approx_settings.arc_to_chord_error == "0.1"
        edbapp.setups["setup1"].curve_approx_settings.max_arc_points = 12
        assert edbapp.setups["setup1"].curve_approx_settings.max_arc_points == 12
        edbapp.setups["setup1"].dcr_settings.conduction_max_passes = 11
        assert edbapp.setups["setup1"].dcr_settings.conduction_max_passes == 11
        edbapp.setups["setup1"].dcr_settings.conduction_min_converged_passes = 2
        assert edbapp.setups["setup1"].dcr_settings.conduction_min_converged_passes == 2
        edbapp.setups["setup1"].dcr_settings.conduction_min_passes = 5
        assert edbapp.setups["setup1"].dcr_settings.conduction_min_passes == 5
        edbapp.setups["setup1"].dcr_settings.conduction_per_error = 2.0
        assert edbapp.setups["setup1"].dcr_settings.conduction_per_error == 2.0
        edbapp.setups["setup1"].dcr_settings.conduction_per_refine = 20.0
        assert edbapp.setups["setup1"].dcr_settings.conduction_per_refine == 20.0
        edbapp.setups["setup1"].hfss_port_settings.max_delta_z0 = 0.5
        assert edbapp.setups["setup1"].hfss_port_settings.max_delta_z0 == 0.5
        edbapp.setups["setup1"].hfss_port_settings.max_triangles_wave_port = 1000
        assert edbapp.setups["setup1"].hfss_port_settings.max_triangles_wave_port == 1000
        edbapp.setups["setup1"].hfss_port_settings.min_triangles_wave_port = 500
        assert edbapp.setups["setup1"].hfss_port_settings.min_triangles_wave_port == 500
        edbapp.setups["setup1"].hfss_port_settings.enable_set_triangles_wave_port = True
        assert edbapp.setups["setup1"].hfss_port_settings.enable_set_triangles_wave_port
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="grpc consolidated sources only")
    def test_siwaves_simulation_setups_consolidation(self):
        edbapp = self.edb_examples.create_empty_edb()
        setup = edbapp.simulation_setups.create_siwave_setup()
        assert not setup.is_null
        setup.name = "test_siwave_setup"
        assert setup.name == "test_siwave_setup"

        # settings advanced
        adv_settings = setup.settings.advanced
        adv_settings.cross_talk_threshold = -60
        assert adv_settings.cross_talk_threshold == -60
        adv_settings.ignore_non_functional_pads = False
        assert not adv_settings.ignore_non_functional_pads
        adv_settings.include_co_plane_coupling = False
        assert not adv_settings.include_co_plane_coupling
        adv_settings.include_fringe_plane_coupling = False
        assert not adv_settings.include_fringe_plane_coupling
        adv_settings.include_inf_gnd = True
        assert adv_settings.include_inf_gnd
        adv_settings.include_inter_plane_coupling = True
        assert adv_settings.include_inter_plane_coupling
        adv_settings.include_split_plane_coupling = False
        assert not adv_settings.include_split_plane_coupling
        adv_settings.inf_gnd_location = 1e-3
        assert adv_settings.inf_gnd_location == 1e-3
        # TODO check pyedb-core bug #681 -> setter is not working
        # adv_settings.max_coupled_lines = 30
        # assert adv_settings.max_coupled_lines == 30
        adv_settings.mesh_automatic = False
        assert not adv_settings.mesh_automatic
        adv_settings.mesh_frequency = 30e9
        assert adv_settings.mesh_frequency == 30e9
        adv_settings.min_pad_area_to_mesh = 1e-5
        assert adv_settings.min_pad_area_to_mesh == 1e-5
        adv_settings.min_plane_area_to_mesh = 1e-5
        assert adv_settings.min_plane_area_to_mesh == 1e-5
        adv_settings.min_void_area = "3mm2"
        assert adv_settings.min_void_area == "3mm2"
        adv_settings.perform_erc = True
        assert adv_settings.perform_erc
        adv_settings.return_current_distribution = True
        assert adv_settings.return_current_distribution
        adv_settings.snap_length_threshold = 30e-6
        assert adv_settings.snap_length_threshold == 30e-6

        # dc
        dc = setup.settings.dc
        dc.compute_inductance = True
        assert dc.compute_inductance
        dc.contact_radius = "1mm"
        assert dc.contact_radius == "1mm"
        dc.dc_report_config_file = "custom_dc_report.cfg"
        assert dc.dc_report_config_file == "custom_dc_report.cfg"
        dc.dc_slider_pos = 2
        assert dc.dc_slider_pos == 2
        dc.export_dc_thermal_data = True
        assert dc.export_dc_thermal_data
        dc.full_dc_report_path = "full_dc_report.txt"
        assert dc.full_dc_report_path == "full_dc_report.txt"
        dc.icepak_temp_file = "icepak_temp_file.txt"
        assert dc.icepak_temp_file == "icepak_temp_file.txt"
        dc.import_thermal_data = True
        assert dc.import_thermal_data
        dc.per_pin_res_path = "per_pin_res.txt"
        assert dc.per_pin_res_path == "per_pin_res.txt"
        dc.per_pin_res_path = "per_pin_res.txt"
        assert dc.per_pin_res_path == "per_pin_res.txt"
        dc.per_pin_res_path = "per_pin_res.txt"
        assert dc.per_pin_res_path == "per_pin_res.txt"
        dc.plot_jv = False
        assert not dc.plot_jv
        dc.source_terms_to_ground = {"gnd": 1}
        dc.use_dc_custom_settings = True
        assert dc.use_dc_custom_settings
        dc.use_loop_res_for_per_pin = True
        assert dc.use_loop_res_for_per_pin
        dc.via_report_path = "via_report.txt"
        assert dc.via_report_path == "via_report.txt"

        # dc advanced
        dc_adv = setup.settings.dc_advanced
        dc_adv.dc_min_plane_area_to_mesh = "0.30mm2"
        assert dc_adv.dc_min_plane_area_to_mesh == "0.30mm2"
        dc_adv.dc_min_void_area_to_mesh = "0.02mm2"
        assert dc_adv.dc_min_void_area_to_mesh == "0.02mm2"
        dc_adv.energy_error = 1.5
        assert dc_adv.energy_error == 1.5
        dc_adv.max_init_mesh_edge_length = "2.0mm"
        assert dc_adv.max_init_mesh_edge_length == "2.0mm"
        dc_adv.max_num_passes = 10
        assert dc_adv.max_num_passes == 10
        dc_adv.mesh_bws = False
        assert not dc_adv.mesh_bws
        dc_adv.mesh_vias = False
        assert not dc_adv.mesh_vias
        dc_adv.min_num_passes = 5
        assert dc_adv.min_num_passes == 5
        dc_adv.num_bw_sides = 12
        assert dc_adv.num_bw_sides == 12
        dc_adv.num_via_sides = 12
        assert dc_adv.num_via_sides == 12
        dc_adv.percent_local_refinement = 30
        assert dc_adv.percent_local_refinement == 30
        dc_adv.refine_bws = True
        assert dc_adv.refine_bws
        dc_adv.refine_vias = True
        assert dc_adv.refine_vias

        # general
        general = setup.settings.general
        general.pi_slider_pos = 0
        assert general.pi_slider_pos == 0
        general.si_slider_pos = 2
        assert general.si_slider_pos == 2
        general.use_custom_settings = True
        assert general.use_custom_settings
        general.user_si_settings = False
        assert not general.user_si_settings

        # s-parameters
        sp = setup.settings.s_parameter
        sp.dc_behavior = "zero"
        assert sp.dc_behavior == "zero"
        sp.extrapolation = "same"
        assert sp.extrapolation == "same"
        sp.interpolation = "point"
        assert sp.interpolation == "point"
        sp.use_state_space = False
        assert not sp.use_state_space
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="grpc consolidated sources only")
    def test_siwaves_dcir_simulation_setups_consolidation(self):
        edbapp = self.edb_examples.create_empty_edb()
        setup = edbapp.simulation_setups.create_siwave_dcir_setup()
        assert not setup.is_null
        setup.name = "test_siwave_dcir_setup"
        assert setup.name == "test_siwave_dcir_setup"

        # setting.advanced
        dc = setup.settings.dc
        dc.compute_inductance = True
        assert dc.compute_inductance
        dc.contact_radius = "1mm"
        assert dc.contact_radius == "1mm"
        dc.dc_report_config_file = "custom_dc_report.cfg"
        assert dc.dc_report_config_file == "custom_dc_report.cfg"
        dc.dc_report_config_file = "custom_dc_report.cfg"
        assert dc.dc_report_config_file == "custom_dc_report.cfg"
        dc.dc_slider_pos = 2
        assert dc.dc_slider_pos == 2
        dc.export_dc_thermal_data = True
        assert dc.export_dc_thermal_data
        dc.full_dc_report_path = "full_dc_report.txt"
        assert dc.full_dc_report_path == "full_dc_report.txt"
        dc.icepak_temp_file = "icepak_temp_file.txt"
        assert dc.icepak_temp_file == "icepak_temp_file.txt"
        dc.import_thermal_data = True
        assert dc.import_thermal_data
        dc.per_pin_res_path = "per_pin_res.txt"
        assert dc.per_pin_res_path == "per_pin_res.txt"
        dc.plot_jv = False
        assert not dc.plot_jv
        dc.source_terms_to_ground = {"gnd": 1}
        dc.use_dc_custom_settings = True
        assert dc.use_dc_custom_settings
        dc.use_loop_res_for_per_pin = True
        assert dc.use_loop_res_for_per_pin
        dc.via_report_path = "via_report.txt"
        assert dc.via_report_path == "via_report.txt"

        # dc advanced
        dc_adv = setup.settings.dc_advanced
        dc_adv.dc_min_plane_area_to_mesh = "0.30mm2"
        assert dc_adv.dc_min_plane_area_to_mesh == "0.30mm2"
        dc_adv.dc_min_void_area_to_mesh = "0.02mm2"
        assert dc_adv.dc_min_void_area_to_mesh == "0.02mm2"
        dc_adv.energy_error = 1.5
        assert dc_adv.energy_error == 1.5
        dc_adv.max_init_mesh_edge_length = "2.0mm"
        assert dc_adv.max_init_mesh_edge_length == "2.0mm"
        dc_adv.max_num_passes = 10
        assert dc_adv.max_num_passes == 10
        dc_adv.mesh_bws = False
        assert not dc_adv.mesh_bws
        dc_adv.mesh_vias = False
        assert not dc_adv.mesh_vias
        dc_adv.min_num_passes = 5
        assert dc_adv.min_num_passes == 5
        dc_adv.num_bw_sides = 12
        assert dc_adv.num_bw_sides == 12
        dc_adv.num_via_sides = 12
        assert dc_adv.num_via_sides == 12
        dc_adv.percent_local_refinement = 30
        assert dc_adv.percent_local_refinement == 30
        dc_adv.refine_bws = True
        assert dc_adv.refine_bws
        dc_adv.refine_vias = True
        assert dc_adv.refine_vias

        # general
        general = setup.settings.general
        general.pi_slider_pos = 0
        assert general.pi_slider_pos == 0
        general.si_slider_pos = 2
        assert general.si_slider_pos == 2
        general.use_custom_settings = True
        assert general.use_custom_settings
        general.user_si_settings = False
        assert not general.user_si_settings
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="grpc consolidated sources only")
    def test_raptor_x_simulation_setups_consolidation(self):
        edbapp = self.edb_examples.create_empty_edb()
        setup = edbapp.simulation_setups.create_raptor_x_setup()
        assert not setup.is_null
        setup.name = "test_raptorx_setup"
        assert setup.name == "test_raptorx_setup"
        assert not setup.sweep_data  # default we don't create sweep if not data provided while setup creation
        # advanced general settings
        adv_settings = setup.settings.advanced
        adv_settings.auto_removal_sliver_poly = 1e-2
        assert adv_settings.auto_removal_sliver_poly == 1e-2
        adv_settings.cells_per_wavelength = 60
        assert adv_settings.cells_per_wavelength == 60
        adv_settings.defuse_enable_hybrid_extraction = True
        assert adv_settings.defuse_enable_hybrid_extraction
        adv_settings.edge_mesh = 1e-6
        assert adv_settings.edge_mesh == 1e-6
        adv_settings.eliminate_slit_per_holes = 2.0
        assert adv_settings.eliminate_slit_per_holes == 2.0
        adv_settings.mesh_bws = 25e9
        assert adv_settings.mesh_bws == 25e9
        adv_settings.net_settings_options = {"VDD": ["mesh_vias", "via_diameter"]}
        assert adv_settings.net_settings_options == {"VDD": ["mesh_vias", "via_diameter"]}
        adv_settings.override_shrink_factor = 2.0
        assert adv_settings.override_shrink_factor == 2.0
        adv_settings.plane_projection_factor = 2.0
        assert adv_settings.plane_projection_factor == 2.0
        adv_settings.use_accelerate_via_extraction = False
        assert not adv_settings.use_accelerate_via_extraction
        adv_settings.use_auto_removal_sliver_poly = True
        assert adv_settings.use_auto_removal_sliver_poly
        adv_settings.use_cells_per_wavelength = True
        assert adv_settings.use_cells_per_wavelength
        adv_settings.use_edge_mesh = True
        assert adv_settings.use_edge_mesh
        adv_settings.use_eliminate_slit_per_holes = True
        assert adv_settings.use_eliminate_slit_per_holes
        adv_settings.use_enable_advanced_cap_effects = True
        assert adv_settings.use_enable_advanced_cap_effects
        adv_settings.use_enable_etch_transform = True
        assert adv_settings.use_enable_etch_transform
        adv_settings.use_enable_substrate_network_extraction = False
        assert not adv_settings.use_enable_substrate_network_extraction
        adv_settings.use_extract_floating_metals_floating = False
        assert not adv_settings.use_extract_floating_metals_floating
        adv_settings.use_extract_floating_metals_dummy = True
        assert adv_settings.use_extract_floating_metals_dummy
        adv_settings.use_lde = True
        assert adv_settings.use_lde
        adv_settings.use_mesh_frequency = True
        assert adv_settings.use_mesh_frequency
        adv_settings.use_overwrite_shrink_factor = True
        assert adv_settings.use_overwrite_shrink_factor
        adv_settings.use_relaxed_z_axis = True
        assert adv_settings.use_relaxed_z_axis

        # general settings
        general = setup.settings.general
        general.global_temperature = 30.0
        assert general.global_temperature == 30.0
        general.max_frequency = 35e9
        assert general.max_frequency == 35e9
        general.netlist_export_spectre = True
        assert general.netlist_export_spectre
        general.save_netlist = True
        assert general.save_netlist
        general.save_rfm = True
        assert general.save_rfm
        general.use_gold_em_solver = True
        assert general.use_gold_em_solver
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="grpc consolidated sources only")
    def test_q3d_simulation_setups_consolidation(self):
        edbapp = self.edb_examples.create_empty_edb()
        setup = edbapp.simulation_setups.create_q3d_setup()
        assert not setup.is_null
        setup.name = "test_q3d_setup"
        assert setup.name == "test_q3d_setup"
        assert setup.setup_type == "q3d"

        # acrl settings
        acrl = setup.settings.acrl
        acrl.max_frequency = 20
        assert acrl.max_frequency == 20
        acrl.max_refine_per_pass = 25
        assert acrl.max_refine_per_pass == 25
        acrl.min_converged_passes = 2
        assert acrl.min_converged_passes == 2
        acrl.min_passes = 2
        assert acrl.min_passes == 2
        acrl.percent_error = 0.5
        assert acrl.percent_error == 0.5

        # advanced meshing settings
        adv_mesh = setup.settings.advanced_meshing
        adv_mesh.arc_step_size = 0.2
        assert adv_mesh.arc_step_size == 0.2
        adv_mesh.arc_to_chord_error = 1e-6
        assert adv_mesh.arc_to_chord_error == 1e-6
        adv_mesh.circle_start_azimuth = 15
        assert adv_mesh.circle_start_azimuth == 15
        # TODO check pyedb-core bug #682 -> setter is broken
        # adv_mesh.layer_alignment = 1e-4
        # assert adv_mesh.layer_alignment == 1e-4
        adv_mesh.max_num_arc_points = 6
        assert adv_mesh.max_num_arc_points == 6
        adv_mesh.use_arc_chord_error_approx = True
        assert adv_mesh.use_arc_chord_error_approx

        # cg settings
        cg = setup.settings.cg
        # TODO check pyedb-core bug #683 -> setter is broken
        # cg.auto_incr_sol_order = False
        # assert not cg.auto_incr_sol_order
        cg.compression_tol = 1e-6
        assert cg.compression_tol == 1e-6
        cg.max_passes = 20
        assert cg.max_passes == 20
        cg.max_refine_per_pass = 20
        assert cg.max_refine_per_pass == 20
        cg.min_converged_passes = 2
        assert cg.min_converged_passes == 2
        cg.min_passes = 2
        assert cg.min_passes == 2
        cg.percent_error = 0.5
        assert cg.percent_error == 0.5
        cg.solution_order = "higher"
        assert cg.solution_order == "higher"

        # dcrl settings
        dcrl = setup.settings.dcrl
        dcrl.max_passes = 20
        assert dcrl.max_passes == 20
        dcrl.max_refine_per_pass = 20
        assert dcrl.max_refine_per_pass == 20
        dcrl.min_converged_passes = 2
        assert dcrl.min_converged_passes == 2
        dcrl.min_passes = 2
        assert dcrl.min_passes == 2
        dcrl.percent_error = 0.5
        assert dcrl.percent_error == 0.5
        dcrl.solution_order = "higher"
        assert dcrl.solution_order == "higher"

        # general settings
        general = setup.settings.general
        general.do_ac = True
        assert general.do_ac
        general.do_cg = True
        assert general.do_cg
        general.do_dc = False
        assert not general.do_dc
        general.do_dc_res_only = True
        assert general.do_dc_res_only
        general.save_netlist = True
        assert general.save_netlist
        general.solution_frequency = 20e9
        assert general.solution_frequency == 20e9
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="grpc consolidated sources only")
    def test_sweep(self):
        edbapp = self.edb_examples.create_empty_edb()
        setup = edbapp.simulation_setups.create_hfss_setup(
            name="test_hfss_setup", distribution="decade_count", start_freq="0GHz", stop_freq="1GHz", freq_step="10"
        )
        sweep = setup.sweep_data[0]
        sweep.compute_dc_point = True
        assert sweep.compute_dc_point
        sweep.enabled = False
        assert not sweep.enabled
        sweep.enabled = True
        sweep.enforce_causality = True
        sweep.enforce_passivity = False
        assert not sweep.enforce_passivity
        assert sweep.frequency_string == "DEC 0GHz 1GHz 10"
        sweep.name = "renamed_sweep"
        assert sweep.name == "renamed_sweep"
        sweep.save_fields = True
        assert sweep.save_fields
        sweep.save_rad_fields_only = True
        assert sweep.save_rad_fields_only
        sweep.type = "discrete"
        assert sweep.type == "discrete"
        sweep.use_hfss_solver_regions = True
        assert sweep.use_hfss_solver_regions
        sweep.use_q3d_for_dc = True
        assert sweep.use_q3d_for_dc
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(config["use_grpc"], reason="Safeguard test for dotnet compatibility with grpc")
    def test_siwave_simulation_setup_dotnet_compatibility(self):
        edbapp = self.edb_examples.create_empty_edb()
        setup = edbapp.create_siwave_dc_setup()
        settings = setup.settings

        # settings
        settings.dc_report_config_file = "custom_dc_report.cfg"
        assert settings.dc_report_config_file == "custom_dc_report.cfg"
        settings.enabled = False
        assert not settings.enabled
        settings.enabled = True
        assert not settings.frequency_sweeps
        settings.icepak_temp_file = "icepak_temp_file.txt"
        assert settings.icepak_temp_file == "icepak_temp_file.txt"
        settings.icepak_temp_file_path = "icepak_temp_file_path.txt"
        assert settings.icepak_temp_file_path == "icepak_temp_file_path.txt"
        settings.import_thermal_data = True
        assert settings.import_thermal_data
        settings.per_pin_res_path = "per_pin_res.txt"
        assert settings.per_pin_res_path == "per_pin_res.txt"
        settings.pin_use_pin_format = True
        assert settings.pin_use_pin_format
        settings.via_report_path = "via_report.txt"
        assert settings.via_report_path == "via_report.txt"
        settings.use_loop_res_for_per_pin = False
        assert not settings.use_loop_res_for_per_pin
        assert settings.setup_type == "siwave_dc"

        settings.export_dc_thermal_data = True
        assert settings.export_dc_thermal_data
        settings.full_dc_report_path = "full_dc_report.txt"
        assert settings.full_dc_report_path == "full_dc_report.txt"

        # dc settings same as grpc
        dc = settings.dc
        dc.compute_inductance = True
        assert dc.compute_inductance
        dc.contact_radius = "1mm"
        assert dc.contact_radius == "1mm"
        dc.dc_slider_pos = 0
        assert dc.dc_slider_pos == 0
        dc.plot_jv = False
        assert not dc.plot_jv
        dc.use_dc_customer_settings = False
        assert not dc.use_dc_customer_settings

        # dc advanced settings same as grpc
        dc_adv = settings.dc_advanced
        dc_adv.dc_min_plane_area_to_mesh = "0.30mm2"
        assert dc_adv.dc_min_plane_area_to_mesh == "0.30mm2"
        dc_adv.dc_min_void_area_to_mesh = "0.02mm2"
        assert dc_adv.dc_min_void_area_to_mesh == "0.02mm2"
        dc_adv.energy_error = 1.5
        assert dc_adv.energy_error == 1.5
        dc_adv.max_init_mesh_edge_length = "2.0mm"
        assert dc_adv.max_init_mesh_edge_length == "2.0mm"
        dc_adv.max_num_passes = 10
        assert dc_adv.max_num_passes == 10
        dc_adv.mesh_bws = False
        assert not dc_adv.mesh_bws
        dc_adv.mesh_vias = False
        assert not dc_adv.mesh_vias
        dc_adv.min_num_passes = 5
        dc_adv.num_bw_sides = 12
        assert dc_adv.num_bw_sides == 12
        dc_adv.num_via_sides = 12
        assert dc_adv.num_via_sides == 12
        dc_adv.percent_local_refinement = 30
        assert dc_adv.percent_local_refinement == 30
        dc_adv.refine_bws = True
        assert dc_adv.refine_bws
        dc_adv.refine_vias = True
        assert dc_adv.refine_vias

        # general settings same as grpc
        general = settings.general
        general.compute_inductance = True
        assert general.compute_inductance
        general.contact_radius = "1mm"
        assert general.contact_radius == "1mm"
        general.dc_slider_pos = 0
        assert general.dc_slider_pos == 0
        general.plot_jv = False
        assert not general.plot_jv
        general.use_dc_custom_settings = False
        assert not general.use_dc_custom_settings
        edbapp.close()
