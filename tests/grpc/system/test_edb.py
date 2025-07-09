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

"""Tests related to Edb
"""

import os
from typing import Sequence

import pytest

from pyedb.generic.general_methods import is_linux
from pyedb.grpc.edb import Edb as Edb
from tests.conftest import desktop_version, local_path
from tests.legacy.system.conftest import test_subfolder

pytestmark = [pytest.mark.system, pytest.mark.grpc]
ON_CI = os.environ.get("CI", "false").lower() == "true"


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, local_scratch, target_path, target_path2, target_path4):
        self.local_scratch = local_scratch
        self.target_path = target_path
        self.target_path2 = target_path2
        self.target_path4 = target_path4

    def test_hfss_create_coax_port_on_component_from_hfss(self, edb_examples):
        """Create a coaxial port on a component from its pin."""
        # Done
        edbapp = edb_examples.get_si_verse()
        assert edbapp.hfss.create_coax_port_on_component("U1", "DDR4_DQS0_P")
        assert edbapp.hfss.create_coax_port_on_component("U1", ["DDR4_DQS0_P", "DDR4_DQS0_N"], True)
        edbapp.close()

    def test_layout_bounding_box(self, edb_examples):
        """Evaluate layout bounding box"""
        edbapp = edb_examples.get_si_verse()
        assert len(edbapp.get_bounding_box()) == 2
        assert edbapp.get_bounding_box() == [[-0.01426004895, -0.00455000106], [0.15010507444, 0.08000000002]]
        edbapp.close()

    def test_siwave_create_circuit_port_on_net(self, edb_examples):
        """Create a circuit port on a net."""
        #  Done
        edbapp = edb_examples.get_si_verse()
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

        # TODO: Moves this piece of code in another place
        assert "test" in edbapp.terminals
        assert edbapp.siwave.create_pin_group_on_net("U1", "1V0", "PG_V1P0_S0")
        assert edbapp.siwave.create_pin_group_on_net("U1", "GND", "U1_GND")
        assert edbapp.siwave.create_circuit_port_on_pin_group("PG_V1P0_S0", "U1_GND", impedance=50, name="test_port")
        edbapp.excitations["test_port"].name = "test_rename"
        assert any(port for port in list(edbapp.excitations) if port == "test_rename")
        edbapp.close()

    def test_siwave_create_voltage_source(self, edb_examples):
        """Create a voltage source."""
        # Done
        edbapp = edb_examples.get_si_verse()
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
        edbapp.close()

    def test_siwave_create_current_source(self, edb_examples):
        """Create a current source."""
        # Done
        edbapp = edb_examples.get_si_verse()
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

        # TODO: Moves this piece of code in another place
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
        ref_term = vprobe_2.ref_terminal
        assert isinstance(ref_term.location, list)
        # ref_term.location = [0, 0] # position setter is crashing check pyedb-core bug #431
        assert ref_term.layer
        ref_term.layer.name = "Inner1(GND1"
        ref_term.layer.name = "test"
        assert "test" in edbapp.stackup.layers
        u6 = edbapp.components["U6"]
        assert edbapp.create_current_source(
            u6.pins["H8"].get_terminal(create_new_terminal=True), u6.pins["G9"].get_terminal(create_new_terminal=True)
        )
        edbapp.close()

    def test_siwave_create_dc_terminal(self, edb_examples):
        """Create a DC terminal."""
        # Done
        edbapp = edb_examples.get_si_verse()
        assert edbapp.siwave.create_dc_terminal("U1", "DDR4_DQ40", "dc_terminal1") == "dc_terminal1"
        edbapp.close()

    def test_siwave_create_resistors_on_pin(self, edb_examples):
        """Create a resistor on pin."""
        # Done
        edbapp = edb_examples.get_si_verse()
        pins = edbapp.components.get_pin_from_component("U1")
        assert "RST4000" == edbapp.siwave.create_resistor_on_pin(pins[302], pins[10], 40, "RST4000")
        edbapp.close()

    def test_siwave_add_syz_analsyis(self, edb_examples):
        """Add a sywave AC analysis."""
        # Done
        edbapp = edb_examples.get_si_verse()
        assert edbapp.siwave.add_siwave_syz_analysis(start_freq="=1GHz", stop_freq="10GHz", step_freq="10MHz")
        edbapp.close()

    def test_siwave_add_dc_analysis(self, edb_examples):
        """Add a sywave DC analysis."""
        # Done
        edbapp = edb_examples.get_si_verse()
        assert edbapp.siwave.add_siwave_dc_analysis(name="Test_dc")
        edbapp.close()

    def test_hfss_mesh_operations(self, edb_examples):
        """Retrieve the trace width for traces with ports."""
        # Done
        edbapp = edb_examples.get_si_verse()
        edbapp.components.create_port_on_component(
            "U1",
            ["VDD_DDR"],
            reference_net="GND",
            port_type="circuit_port",
        )
        mesh_ops = edbapp.hfss.get_trace_width_for_traces_with_ports()
        assert len(mesh_ops) > 0
        edbapp.close()

    def test_add_variables(self, edb_examples):
        """Add design and project variables."""
        edbapp = edb_examples.get_si_verse()
        edbapp.add_design_variable("my_variable", "1mm")
        assert "my_variable" in edbapp.active_cell.get_all_variable_names()
        assert edbapp.modeler.parametrize_trace_width("DDR4_DQ25")
        assert edbapp.modeler.parametrize_trace_width("DDR4_A2")
        edbapp.add_design_variable("my_parameter", "2mm", True)
        assert "my_parameter" in edbapp.active_cell.get_all_variable_names()
        variable_value = edbapp.active_cell.get_variable_value("my_parameter").value
        assert variable_value == 2e-3
        if edbapp.grpc:
            assert not edbapp.add_design_variable("my_parameter", "2mm", True)
        else:
            # grpc and DotNet variable implementation server are too different.
            assert not edbapp.add_design_variable("my_parameter", "2mm", True)[0]
        edbapp.add_project_variable("$my_project_variable", "3mm")
        if edbapp.grpc:
            assert edbapp.db.get_variable_value("$my_project_variable") == 3e-3
        else:
            # grpc implementation is very different.
            assert edbapp.get_variable_value("$my_project_variable") == 3e-3
        if edbapp.grpc:
            assert not edbapp.add_project_variable("$my_project_variable", "3mm")
        else:
            # grpc and DotNet variable implementation server are too different.
            assert not edbapp.add_project_variable("$my_project_variable", "3mm")[0]
        edbapp.close()

    def test_save_edb_as(self, edb_examples):
        """Save edb as some file."""
        # Done
        edbapp = edb_examples.get_si_verse()
        assert edbapp.save_edb_as(os.path.join(self.local_scratch.path, "si_verse_new.aedb"))
        assert os.path.exists(os.path.join(self.local_scratch.path, "si_verse_new.aedb", "edb.def"))
        edbapp.close()

    def test_create_custom_cutout_0(self, edb_examples):
        """Create custom cutout 0."""
        # Done
        edbapp = edb_examples.get_si_verse()
        output = os.path.join(self.local_scratch.path, "cutout.aedb")
        assert edbapp.cutout(
            ["DDR4_DQS0_P", "DDR4_DQS0_N"],
            ["GND"],
            output_aedb_path=output,
            open_cutout_at_end=False,
            use_pyaedt_extent_computing=True,
            use_pyaedt_cutout=False,
        )
        assert os.path.exists(os.path.join(output, "edb.def"))
        bounding = edbapp.get_bounding_box()
        assert bounding

        cutout_line_x = 41
        cutout_line_y = 30
        points = [[bounding[0][0], bounding[0][1]]]
        points.append([cutout_line_x, bounding[0][1]])
        points.append([cutout_line_x, cutout_line_y])
        points.append([bounding[0][0], cutout_line_y])
        points.append([bounding[0][0], bounding[0][1]])

        output = os.path.join(self.local_scratch.path, "cutout2.aedb")

        assert edbapp.cutout(
            custom_extent=points,
            signal_list=["GND", "1V0"],
            output_aedb_path=output,
            open_cutout_at_end=False,
            include_partial_instances=True,
            use_pyaedt_cutout=False,
        )
        assert os.path.exists(os.path.join(output, "edb.def"))
        # edbapp.close()

    def test_create_custom_cutout_1(self, edb_examples):
        """Create custom cutout 1."""
        # Done
        edbapp = edb_examples.get_si_verse()
        spice_path = os.path.join(local_path, "example_models", test_subfolder, "GRM32_DC0V_25degC.mod")
        assert edbapp.components.instances["R8"].assign_spice_model(spice_path)
        assert edbapp.nets.nets
        assert edbapp.cutout(
            signal_list=["1V0"],
            reference_list=[
                "GND",
                "LVDS_CH08_N",
                "LVDS_CH08_P",
                "LVDS_CH10_N",
                "LVDS_CH10_P",
                "LVDS_CH04_P",
                "LVDS_CH04_N",
            ],
            extent_type="Bounding",
            extent_defeature=0.001,
            preserve_components_with_model=True,
            keep_lines_as_path=True,
        )
        assert "A0_N" not in edbapp.nets.nets
        # assert isinstance(edbapp.layout_validation.disjoint_nets("GND", order_by_area=True), list)
        # assert isinstance(edbapp.layout_validation.disjoint_nets("GND", keep_only_main_net=True), list)
        # assert isinstance(edbapp.layout_validation.disjoint_nets("GND", clean_disjoints_less_than=0.005), list)
        assert edbapp.layout_validation.fix_self_intersections("PGND")
        assert edbapp.layout_validation.fix_self_intersections()
        edbapp.close()

    def test_create_custom_cutout_2(self, edb_examples):
        """Create custom cutout 2."""
        # Done
        edbapp = edb_examples.get_si_verse()
        bounding = edbapp.get_bounding_box()
        assert bounding
        cutout_line_x = 41
        cutout_line_y = 30
        points = [[bounding[0][0], bounding[0][1]]]
        points.append([cutout_line_x, bounding[0][1]])
        points.append([cutout_line_x, cutout_line_y])
        points.append([bounding[0][0], cutout_line_y])
        points.append([bounding[0][0], bounding[0][1]])

        assert edbapp.cutout(
            signal_list=["1V0"],
            reference_list=["GND"],
            extent_type="ConvexHull",
            custom_extent=points,
            simple_pad_check=False,
        )
        edbapp.close()

    def test_create_custom_cutout_3(self, edb_examples):
        """Create custom cutout 3."""
        # Done
        edbapp = edb_examples.get_si_verse()
        edbapp.components.create_port_on_component(
            "U1",
            ["5V"],
            reference_net="GND",
            port_type="circuit_port",
        )
        edbapp.components.create_port_on_component("U2", ["5V"], reference_net="GND")
        edbapp.hfss.create_voltage_source_on_net("U4", "5V", "U4", "GND")
        legacy_name = edbapp.edbpath
        assert edbapp.cutout(
            signal_list=["5V"],
            reference_list=["GND"],
            extent_type="ConvexHull",
            use_pyaedt_extent_computing=True,
            check_terminals=True,
        )
        assert edbapp.edbpath == legacy_name
        # assert edbapp.are_port_reference_terminals_connected(common_reference="GND")

        edbapp.close()

    def test_create_custom_cutout_4(self, edb_examples):
        """Create custom cutout 4."""
        # Done
        edbapp = edb_examples.get_si_verse()
        edbapp.components.create_pingroup_from_pins(
            [i for i in list(edbapp.components.instances["U1"].pins.values()) if i.net_name == "GND"]
        )

        assert edbapp.cutout(
            signal_list=["DDR4_DQS0_P", "DDR4_DQS0_N"],
            reference_list=["GND"],
            extent_type="ConvexHull",
            use_pyaedt_extent_computing=True,
            include_pingroups=True,
            check_terminals=True,
            expansion_factor=4,
        )
        edbapp.close()
        source_path = os.path.join(local_path, "example_models", test_subfolder, "MicrostripSpliGnd.aedb")
        target_path = os.path.join(self.local_scratch.path, "MicrostripSpliGnd.aedb")
        self.local_scratch.copyfolder(source_path, target_path)

        # TODO check for building project with checking terminals
        # edbapp = Edb(target_path, edbversion=desktop_version)
        #
        # assert edbapp.cutout(
        #     signal_list=["trace_n"],
        #     reference_list=["ground"],
        #     extent_type="Conformal",
        #     use_pyaedt_extent_computing=True,
        #     check_terminals=True,
        #     expansion_factor=2,
        #     include_voids_in_extents=True,
        # )
        # edbapp.close()
        # source_path = os.path.join(local_path, "example_models", test_subfolder, "Multizone_GroundVoids.aedb")
        # target_path = os.path.join(self.local_scratch.path, "Multizone_GroundVoids.aedb")
        # self.local_scratch.copyfolder(source_path, target_path)
        #
        # edbapp = Edb(target_path, edbversion=desktop_version)
        #
        # assert edbapp.cutout(
        #     signal_list=["DIFF_N", "DIFF_P"],
        #     reference_list=["GND"],
        #     extent_type="Conformal",
        #     use_pyaedt_extent_computing=True,
        #     check_terminals=True,
        #     expansion_factor=3,
        # )
        # edbapp.close()

    @pytest.mark.skipif(
        is_linux and ON_CI,
        reason="Test is slow due to software rendering fallback and lack of GPU acceleration.",
    )
    def test_export_to_hfss(self):
        """Export EDB to HFSS."""
        # Done
        edb = Edb(
            edbpath=os.path.join(local_path, "example_models", test_subfolder, "simple.aedb"),
            edbversion=desktop_version,
        )
        options_config = {"UNITE_NETS": 1, "LAUNCH_Q3D": 0}
        out = edb.write_export3d_option_config_file(self.local_scratch.path, options_config)
        assert os.path.exists(out)
        out = edb.export_hfss(self.local_scratch.path)
        assert os.path.exists(out)
        edb.close()

    @pytest.mark.skipif(
        is_linux and ON_CI,
        reason="Test is slow due to software rendering fallback and lack of GPU acceleration.",
    )
    def test_export_to_q3d(self):
        """Export EDB to Q3D."""
        # Done
        edb = Edb(
            edbpath=os.path.join(local_path, "example_models", test_subfolder, "simple.aedb"),
            edbversion=desktop_version,
        )
        options_config = {"UNITE_NETS": 1, "LAUNCH_Q3D": 0}
        out = edb.write_export3d_option_config_file(self.local_scratch.path, options_config)
        assert os.path.exists(out)
        out = edb.export_q3d(self.local_scratch.path, net_list=["ANALOG_A0", "ANALOG_A1", "ANALOG_A2"], hidden=True)
        assert os.path.exists(out)
        edb.close()

    @pytest.mark.skipif(
        is_linux and ON_CI,
        reason="Test is slow due to software rendering fallback and lack of GPU acceleration.",
    )
    def test_074_export_to_maxwell(self):
        """Export EDB to Maxwell 3D."""

        # Done

        edb = Edb(
            edbpath=os.path.join(local_path, "example_models", test_subfolder, "simple.aedb"),
            edbversion=desktop_version,
        )
        options_config = {"UNITE_NETS": 1, "LAUNCH_MAXWELL": 0}
        out = edb.write_export3d_option_config_file(self.local_scratch.path, options_config)
        assert os.path.exists(out)
        out = edb.export_maxwell(self.local_scratch.path, num_cores=6)
        assert os.path.exists(out)
        edb.close()

    def test_create_edge_port_on_polygon(self):
        """Create lumped and vertical port."""
        edb = Edb(
            edbpath=os.path.join(local_path, "example_models", test_subfolder, "edge_ports.aedb"),
            edbversion=desktop_version,
        )
        if edb.grpc:
            # grpc PrimitiveType enum changed.
            poly_list = [poly for poly in edb.layout.primitives if poly.primitive_type.value == 2]
        else:
            poly_list = [poly for poly in edb.layout.primitives if poly.primitive_type == "polygon"]
        if edb.grpc:
            port_poly = [poly for poly in poly_list if poly.edb_uid == 17][0]
            ref_poly = [poly for poly in poly_list if poly.edb_uid == 19][0]
        else:
            port_poly = [poly for poly in poly_list if poly.id == 17][0]
            ref_poly = [poly for poly in poly_list if poly.id == 19][0]
        port_location = [-65e-3, -13e-3]
        ref_location = [-63e-3, -13e-3]
        if edb.grpc:
            assert edb.source_excitation.create_edge_port_on_polygon(
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
        if edb.grpc:
            port_poly = [poly for poly in poly_list if poly.edb_uid == 23][0]
            ref_poly = [poly for poly in poly_list if poly.edb_uid == 22][0]
        else:
            port_poly = [poly for poly in poly_list if poly.id == 23][0]
            ref_poly = [poly for poly in poly_list if poly.id == 22][0]
        port_location = [-65e-3, -10e-3]
        ref_location = [-65e-3, -10e-3]
        if edb.grpc:
            assert edb.source_excitation.create_edge_port_on_polygon(
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
        if edb.grpc:
            port_poly = [poly for poly in poly_list if poly.edb_uid == 25][0]
        else:
            port_poly = [poly for poly in poly_list if poly.id == 25][0]
        port_location = [-65e-3, -7e-3]
        if edb.grpc:
            assert edb.source_excitation.create_edge_port_on_polygon(
                polygon=port_poly, terminal_point=port_location, reference_layer="gnd"
            )
        else:
            # method already deprecated in grpc.
            assert edb.hfss.create_edge_port_on_polygon(
                polygon=port_poly, terminal_point=port_location, reference_layer="gnd"
            )
        sig = edb.modeler.create_trace([[0, 0], ["9mm", 0]], "sig2", "1mm", "SIG", "Flat", "Flat")
        # TODO grpc create trace must return PyEDB path not internal one.
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
        # TODO return impedance value as float in grpc.
        if edb.grpc:
            assert gap_port.port_post_processing_prop.renormalization_impedance == 50
        else:
            assert gap_port.renormalization_impedance == 50
        gap_port.is_circuit_port = True
        assert gap_port.is_circuit_port
        edb.close()

    @pytest.mark.skipif(
        is_linux and ON_CI,
        reason="Randomly crashing on Linux.",
    )
    def test_edb_statistics(self, edb_examples):
        """Get statistics."""
        edb = edb_examples.get_si_verse()
        edb_stats = edb.get_statistics(compute_area=True)
        assert edb_stats
        assert edb_stats.num_layers
        assert edb_stats.stackup_thickness
        assert edb_stats.num_vias
        assert edb_stats.occupying_ratio
        assert edb_stats.occupying_surface
        assert edb_stats.layout_size
        assert edb_stats.num_polygons
        assert edb_stats.num_traces
        assert edb_stats.num_nets
        assert edb_stats.num_discrete_components
        assert edb_stats.num_inductors
        assert edb_stats.num_capacitors
        assert edb_stats.num_resistors
        assert edb_stats.occupying_ratio["1_Top"] == 0.301682
        assert edb_stats.occupying_ratio["Inner1(GND1)"] == 0.937467
        assert edb_stats.occupying_ratio["16_Bottom"] == 0.204925
        edb.close()

    def test_create_rlc_component(self, edb_examples):
        """Create rlc components from pin"""
        edb = edb_examples.get_si_verse()
        pins = edb.components.get_pin_from_component("U1", "1V0")
        ref_pins = edb.components.get_pin_from_component("U1", "GND")
        assert edb.components.create([pins[0], ref_pins[0]], "test_0rlc", r_value=1.67, l_value=1e-13, c_value=1e-11)
        assert edb.components.create([pins[0], ref_pins[0]], "test_1rlc", r_value=None, l_value=1e-13, c_value=1e-11)
        assert edb.components.create([pins[0], ref_pins[0]], "test_2rlc", r_value=None, c_value=1e-13)
        edb.close()

    def test_create_rlc_boundary_on_pins(self, edb_examples):
        """Create hfss rlc boundary on pins."""
        # Done
        edb = edb_examples.get_si_verse()
        pins = edb.components.get_pin_from_component("U1", "1V0")
        ref_pins = edb.components.get_pin_from_component("U1", "GND")
        assert edb.hfss.create_rlc_boundary_on_pins(pins[0], ref_pins[0], rvalue=1.05, lvalue=1.05e-12, cvalue=1.78e-13)
        edb.close()

    def test_configure_hfss_analysis_setup_enforce_causality(self, edb_examples):
        """Configure HFSS analysis setup."""
        # Done
        edb = edb_examples.get_si_verse()
        assert len(edb.active_cell.simulation_setups) == 0
        edb.hfss.add_setup()
        assert edb.hfss_setups
        assert len(edb.active_cell.simulation_setups) == 1
        assert list(edb.active_cell.simulation_setups)[0]
        setup = list(edb.hfss_setups.values())[0]
        setup.add_sweep()
        assert len(setup.sweep_data) == 1
        if edb.grpc:
            assert not setup.sweep_data[0].interpolation_data.enforce_causality
        else:
            assert not setup.sweep_data[0].enforce_causality
        sweeps = setup.sweep_data
        for sweep in sweeps:
            if edb.grpc:
                sweep.interpolation_data.enforce_causality = True
            else:
                sweep.enforce_causality = True
        setup.sweep_data = sweeps
        if edb.grpc:
            assert setup.sweep_data[0].interpolation_data.enforce_causality
        else:
            assert setup.sweep_data[0].enforce_causality
        edb.close()

    def test_create_various_ports_0(self):
        """Create various ports."""
        edb = Edb(
            edbpath=os.path.join(local_path, "example_models", "edb_edge_ports.aedb"),
            edbversion=desktop_version,
        )
        if edb.grpc:
            prim_1_id = [i.edb_uid for i in edb.modeler.primitives if i.net.name == "trace_2"][0]
            assert edb.source_excitation.create_edge_port_vertical(prim_1_id, ["-66mm", "-4mm"], "port_ver")
        else:
            # This method is also available at same location in grpc but is deprecated.
            prim_1_id = [i.id for i in edb.modeler.primitives if i.net.name == "trace_2"][0]
            assert edb.hfss.create_edge_port_vertical(prim_1_id, ["-66mm", "-4mm"], "port_ver")

        prim_2_id = [i.id for i in edb.modeler.primitives if i.net.name == "trace_3"][0]
        if edb.grpc:
            assert edb.source_excitation.create_edge_port_horizontal(
                prim_1_id, ["-60mm", "-4mm"], prim_2_id, ["-59mm", "-4mm"], "port_hori", 30, "Lower"
            )
        else:
            # This method is also available at same location in grpc but is deprecated.
            assert edb.hfss.create_edge_port_horizontal(
                prim_1_id, ["-60mm", "-4mm"], prim_2_id, ["-59mm", "-4mm"], "port_hori", 30, "Lower"
            )
        if edb.grpc:
            assert edb.source_excitation.get_ports_number() == 2
        else:
            assert edb.hfss.get_ports_number() == 2
        port_ver = edb.ports["port_ver"]
        assert not port_ver.is_null
        assert not port_ver.is_circuit_port
        if edb.grpc:
            assert port_ver.type.name == "EDGE"
        else:
            # grpc is too different
            assert port_ver.boundary_type == "PortBoundary"

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

        # TODO implement wave port with grPC
        # wave_port = edb.source_excitation.create_bundle_wave_port["wave_port"]
        # wave_port.horizontal_extent_factor = 10
        # wave_port.vertical_extent_factor = 10
        # assert wave_port.horizontal_extent_factor == 10
        # assert wave_port.vertical_extent_factor == 10
        # wave_port.radial_extent_factor = 1
        # assert wave_port.radial_extent_factor == 1
        # assert wave_port.pec_launch_width
        # assert not wave_port.deembed
        # assert wave_port.deembed_length == 0.0
        # assert wave_port.do_renormalize
        # wave_port.do_renormalize = False
        # assert not wave_port.do_renormalize
        # assert edb.source_excitation.create_differential_wave_port(
        #     traces[1].id,
        #     trace_paths[0][0],
        #     traces[2].id,
        #     trace_paths[1][0],
        #     horizontal_extent_factor=8,
        #     port_name="df_port",
        # )
        # assert edb.ports["df_port"]
        # p, n = edb.ports["df_port"].terminals
        # assert p.name == "df_port:T1"
        # assert n.name == "df_port:T2"
        # assert edb.ports["df_port"].decouple()
        # p.couple_ports(n)
        #
        # traces_id = [i.id for i in traces]
        # paths = [i[1] for i in trace_paths]
        # df_port = edb.source_excitation.create_bundle_wave_port(traces_id, paths)
        # assert df_port.name
        # assert df_port.terminals
        # df_port.horizontal_extent_factor = 10
        # df_port.vertical_extent_factor = 10
        # df_port.deembed = True
        # df_port.deembed_length = "1mm"
        # assert df_port.horizontal_extent_factor == 10
        # assert df_port.vertical_extent_factor == 10
        # assert df_port.deembed
        # assert df_port.deembed_length == 1e-3
        edb.close()

    def test_create_various_ports_1(self):
        """Create various ports."""
        """Create various ports."""
        edb = Edb(
            edbpath=os.path.join(local_path, "example_models", "edb_edge_ports.aedb"),
            edbversion=desktop_version,
        )
        kwargs = {
            "layer_name": "TOP",
            "net_name": "SIGP",
            "width": "0.1mm",
            "start_cap_style": "Flat",
            "end_cap_style": "Flat",
        }
        traces = []
        trace_pathes = [
            [["-40mm", "-10mm"], ["-30mm", "-10mm"]],
            [["-40mm", "-10.2mm"], ["-30mm", "-10.2mm"]],
            [["-40mm", "-10.4mm"], ["-30mm", "-10.4mm"]],
        ]
        for p in trace_pathes:
            t = edb.modeler.create_trace(path_list=p, **kwargs)
            traces.append(t)

        assert edb.hfss.create_wave_port(traces[0], trace_pathes[0][0], "wave_port")

        assert edb.hfss.create_differential_wave_port(
            traces[0],
            trace_pathes[0][0],
            traces[1],
            trace_pathes[1][0],
            horizontal_extent_factor=8,
        )

        paths = [i[1] for i in trace_pathes]
        assert edb.hfss.create_bundle_wave_port(traces, paths)
        p = edb.ports["wave_port"]
        p.horizontal_extent_factor = 6
        p.vertical_extent_factor = 5
        p.pec_launch_width = "0.02mm"
        p.radial_extent_factor = 1
        assert p.horizontal_extent_factor == 6
        assert p.vertical_extent_factor == 5
        assert p.pec_launch_width == "0.02mm"
        assert p.radial_extent_factor == 1
        edb.close()

    def test_set_all_antipad_values(self, edb_examples):
        """Set all anti-pads from all pad-stack definition to the given value."""
        #  Done
        edb = edb_examples.get_si_verse()
        assert edb.padstacks.set_all_antipad_value(0.0)
        edb.close()

    def test_hfss_simulation_setup(self, edb_examples):
        """Create a setup from a template and evaluate its properties."""
        # Done
        edbapp = edb_examples.get_si_verse()
        setup1 = edbapp.hfss.add_setup("setup1")
        assert not edbapp.hfss.add_setup("setup1")
        assert setup1.set_solution_single_frequency()
        assert setup1.set_solution_multi_frequencies()
        assert setup1.set_solution_broadband()
        if edbapp.grpc:
            setup1.settings.options.enhanced_low_frequency_accuracy = True
            assert setup1.settings.options.enhanced_low_frequency_accuracy
            setup1.settings.options.order_basis = setup1.settings.options.order_basis.FIRST_ORDER
            assert setup1.settings.options.order_basis.name == "FIRST_ORDER"
            setup1.settings.options.relative_residual = 0.0002
            assert setup1.settings.options.relative_residual == 0.0002
            setup1.settings.options.use_shell_elements = True
            assert setup1.settings.options.use_shell_elements
        else:
            # grpc simulation setup is too different.
            setup1.hfss_solver_settings.enhanced_low_freq_accuracy = True
            assert setup1.hfss_solver_settings.enhanced_low_freq_accuracy
            # Currently EDB api has a bug for this feature.
            # setup1.hfss_solver_settings.order_basis
            setup1.hfss_solver_settings.relative_residual = 0.0002
            assert setup1.hfss_solver_settings.relative_residual == 0.0002
            setup1.hfss_solver_settings.use_shell_elements = True
            assert setup1.hfss_solver_settings.use_shell_elements

        setup1b = edbapp.setups["setup1"]
        assert not setup1.is_null
        if edbapp.grpc:
            assert setup1b.add_adaptive_frequency_data("5GHz", "0.01")
            setup1.settings.general.adaptive_solution_type = setup1.settings.general.adaptive_solution_type.BROADBAND
            setup1.settings.options.max_refinement_per_pass = 20
            assert setup1.settings.options.max_refinement_per_pass == 20
            setup1.settings.options.min_passes = 2
            assert setup1.settings.options.min_passes == 2
            setup1.settings.general.save_fields = True
            assert setup1.settings.general.save_fields
            setup1.settings.general.save_rad_fields_only = True
            assert setup1.settings.general.save_rad_fields_only
            setup1.settings.general.use_parallel_refinement = True
            assert setup1.settings.general.use_parallel_refinement

            assert edbapp.setups["setup1"].settings.general.adaptive_solution_type.name == "BROADBAND"
            edbapp.setups["setup1"].settings.options.use_max_refinement = True
            assert edbapp.setups["setup1"].settings.options.use_max_refinement

            edbapp.setups["setup1"].settings.advanced.defeature_absolute_length = "1um"
            assert edbapp.setups["setup1"].settings.advanced.defeature_absolute_length == "1um"
            edbapp.setups["setup1"].settings.advanced.defeature_ratio = 1e-5
            assert edbapp.setups["setup1"].settings.advanced.defeature_ratio == 1e-5
            edbapp.setups["setup1"].settings.advanced.healing_option = 0
            assert edbapp.setups["setup1"].settings.advanced.healing_option == 0
            edbapp.setups["setup1"].settings.advanced.remove_floating_geometry = True
            assert edbapp.setups["setup1"].settings.advanced.remove_floating_geometry
            edbapp.setups["setup1"].settings.advanced.small_void_area = 0.1
            assert edbapp.setups["setup1"].settings.advanced.small_void_area == 0.1
            edbapp.setups["setup1"].settings.advanced.union_polygons = False
            assert not edbapp.setups["setup1"].settings.advanced.union_polygons
            edbapp.setups["setup1"].settings.advanced.use_defeature = False
            assert not edbapp.setups["setup1"].settings.advanced.use_defeature
            edbapp.setups["setup1"].settings.advanced.use_defeature_absolute_length = True
            assert edbapp.setups["setup1"].settings.advanced.use_defeature_absolute_length

            edbapp.setups["setup1"].settings.advanced.num_via_density = 1.0
            assert edbapp.setups["setup1"].settings.advanced.num_via_density == 1.0
            edbapp.setups["setup1"].settings.advanced.via_material = "pec"
            assert edbapp.setups["setup1"].settings.advanced.via_material == "pec"
            edbapp.setups["setup1"].settings.advanced.num_via_sides = 8
            assert edbapp.setups["setup1"].settings.advanced.num_via_sides == 8
            assert edbapp.setups["setup1"].settings.advanced.via_model_type.name == "MESH"
            edbapp.setups["setup1"].settings.advanced_meshing.layer_snap_tol = "1e-6"
            assert edbapp.setups["setup1"].settings.advanced_meshing.layer_snap_tol == "1e-6"

            edbapp.setups["setup1"].settings.advanced_meshing.arc_to_chord_error = "0.1"
            assert edbapp.setups["setup1"].settings.advanced_meshing.arc_to_chord_error == "0.1"
            edbapp.setups["setup1"].settings.advanced_meshing.max_num_arc_points = 12
            assert edbapp.setups["setup1"].settings.advanced_meshing.max_num_arc_points == 12

            edbapp.setups["setup1"].settings.dcr.max_passes = 11
            assert edbapp.setups["setup1"].settings.dcr.max_passes == 11
            edbapp.setups["setup1"].settings.dcr.min_converged_passes = 2
            assert edbapp.setups["setup1"].settings.dcr.min_converged_passes == 2
            edbapp.setups["setup1"].settings.dcr.min_passes = 5
            assert edbapp.setups["setup1"].settings.dcr.min_passes == 5
            edbapp.setups["setup1"].settings.dcr.percent_error = 2.0
            assert edbapp.setups["setup1"].settings.dcr.percent_error == 2.0
            edbapp.setups["setup1"].settings.dcr.percent_refinement_per_pass = 20.0
            assert edbapp.setups["setup1"].settings.dcr.percent_refinement_per_pass == 20.0

            edbapp.setups["setup1"].settings.solver.max_delta_z0 = 0.5
            assert edbapp.setups["setup1"].settings.solver.max_delta_z0 == 0.5
            edbapp.setups["setup1"].settings.solver.max_triangles_for_wave_port = 1000
            assert edbapp.setups["setup1"].settings.solver.max_triangles_for_wave_port == 1000
            edbapp.setups["setup1"].settings.solver.min_triangles_for_wave_port = 500
            assert edbapp.setups["setup1"].settings.solver.min_triangles_for_wave_port == 500
            edbapp.setups["setup1"].settings.solver.set_triangles_for_wave_port = True
            assert edbapp.setups["setup1"].settings.solver.set_triangles_for_wave_port
        else:
            setup1.adaptive_settings.max_refine_per_pass = 20
            assert setup1.adaptive_settings.max_refine_per_pass == 20
            setup1.adaptive_settings.min_passes = 2
            assert setup1.adaptive_settings.min_passes == 2
            setup1.adaptive_settings.save_fields = True
            assert setup1.adaptive_settings.save_fields
            setup1.adaptive_settings.save_rad_field_only = True
            assert setup1.adaptive_settings.save_rad_field_only
            # setup1.adaptive_settings.use_parallel_refinement = True
            # assert setup1.settings.general.use_parallel_refinement

            assert edbapp.setups["setup1"].adaptive_settings.adapt_type == "kBroadband"
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
            assert edbapp.setups["setup1"].via_settings.via_style == "k25DViaWirebond"
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
        edbapp.close()

    def test_hfss_simulation_setup_mesh_operation(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        setup = edbapp.create_hfss_setup(name="setup")
        mop = setup.add_length_mesh_operation(net_layer_list={"GND": ["1_Top", "16_Bottom"]}, name="m1")
        assert mop.enabled
        assert mop.net_layer_info[0] == ("GND", "1_Top", True)
        assert mop.net_layer_info[1] == ("GND", "16_Bottom", True)
        assert mop.name == "m1"
        if edbapp.grpc:
            assert mop.max_elements == "1000"
        else:
            assert mop.max_elements == 1000
        assert mop.restrict_max_elements
        assert mop.restrict_max_length
        assert mop.max_length == "1mm"
        assert setup.mesh_operations
        assert edbapp.setups["setup"].mesh_operations

        mop = edbapp.setups["setup"].add_skin_depth_mesh_operation({"GND": ["1_Top", "16_Bottom"]})
        assert mop.net_layer_info[0] == ("GND", "1_Top", True)
        assert mop.net_layer_info[1] == ("GND", "16_Bottom", True)
        if edbapp.grpc:
            assert mop.max_elements == "1000"
        else:
            assert mop.max_elements == 1000
        assert mop.restrict_max_elements
        assert mop.skin_depth == "1um"
        assert mop.surface_triangle_length == "1mm"
        assert mop.number_of_layers == "2"

        mop.skin_depth = "5um"
        mop.surface_triangle_length = "2mm"
        mop.number_of_layer_elements = "3"

        assert mop.skin_depth == "5um"
        assert mop.surface_triangle_length == "2mm"
        assert mop.number_of_layer_elements == "3"
        edbapp.close()

    def test_hfss_frequency_sweep(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        setup1 = edbapp.create_hfss_setup("setup1")
        assert edbapp.setups["setup1"].name == "setup1"
        setup1.add_sweep(name="sw1", distribution="linear_count", start_freq="1MHz", stop_freq="100MHz", step=10)
        assert edbapp.setups["setup1"].sweep_data[0].name == "sw1"
        if edbapp.grpc:
            assert edbapp.setups["setup1"].sweep_data[0].frequency_data.start_f == "1MHz"
            assert edbapp.setups["setup1"].sweep_data[0].frequency_data.end_f == "100MHz"
            assert edbapp.setups["setup1"].sweep_data[0].frequency_data.step == "10"
        else:
            # grpc sweep data has completely changed.
            assert edbapp.setups["setup1"].sweep_data[0].frequency_string[0] == "LINC 0.001GHz 0.1GHz 10"
        setup1.add_sweep(name="sw2", distribution="linear", start_freq="210MHz", stop_freq="300MHz", step="10MHz")
        if edbapp.grpc:
            assert edbapp.setups["setup1"].sweep_data[0].name == "sw2"
        else:
            # Dotnet api is not adding in the same order.
            assert edbapp.setups["setup1"].sweep_data[-1].name == "sw2"
        setup1.add_sweep(name="sw3", distribution="log_scale", start_freq="1GHz", stop_freq="10GHz", step=10)
        if edbapp.grpc:
            assert edbapp.setups["setup1"].sweep_data[0].name == "sw3"
            setup1.sweep_data[2].use_q3d_for_dc = True
        else:
            assert edbapp.setups["setup1"].sweep_data[-1].name == "sw3"
            setup1.sweep_data[-1].use_q3d_for_dc = True
        edbapp.close()

    def test_siwave_dc_simulation_setup(self, edb_examples):
        """Create a dc simulation setup and evaluate its properties."""
        # Obsolete addressed in config 2.0 section.
        pass

    def test_siwave_ac_simulation_setup(self, edb_examples):
        """Create an ac simulation setup and evaluate its properties."""
        # Obsolete addressed in config 2.0 section.
        pass

    def test_siwave_create_port_between_pin_and_layer(self, edb_examples):
        """Create circuit port between pin and a reference layer."""
        # Done

        edbapp = edb_examples.get_si_verse()
        assert edbapp.siwave.create_port_between_pin_and_layer(
            component_name="U1", pins_name="A27", layer_name="16_Bottom", reference_net="GND"
        )
        U7 = edbapp.components["U7"]
        assert U7.pins["G7"].create_port()
        assert U7.pins["F7"].create_port(reference=U7.pins["E7"])
        pin_group = edbapp.siwave.create_pin_group_on_net(
            reference_designator="U7", net_name="GND", group_name="U7_GND"
        )
        assert pin_group
        U7.pins["R9"].create_port(name="test", reference=pin_group)
        if edbapp.grpc:
            padstack_instance_terminals = [
                term for term in list(edbapp.terminals.values()) if term.type.name == "PADSTACK_INST"
            ]
        else:
            padstack_instance_terminals = [
                term for term in list(edbapp.terminals.values()) if term.terminal_type == "PadstackInstanceTerminal"
            ]
        for term in padstack_instance_terminals:
            assert term.position
        pos_pin = edbapp.padstacks.get_pinlist_from_component_and_net("C173")[1]
        neg_pin = edbapp.padstacks.get_pinlist_from_component_and_net("C172")[0]
        edbapp.create_port(
            pos_pin.get_terminal(create_new_terminal=True),
            neg_pin.get_terminal(create_new_terminal=True),
            is_circuit_port=True,
            name="test1",
        )
        assert edbapp.ports["test1"]
        edbapp.ports["test1"].is_circuit_port = True
        assert edbapp.ports["test1"].is_circuit_port
        edbapp.close()

    def test_siwave_source_setter(self):
        """Evaluate siwave sources property."""
        # Done
        source_path = os.path.join(local_path, "example_models", test_subfolder, "test_sources.aedb")
        target_path = os.path.join(self.local_scratch.path, "test_134_source_setter.aedb")
        self.local_scratch.copyfolder(source_path, target_path)
        edbapp = Edb(target_path, edbversion=desktop_version)
        sources = list(edbapp.siwave.sources.values())
        sources[0].magnitude = 1.45
        sources[1].magnitude = 1.45
        # TODO grpc return float value.
        assert sources[0].magnitude == 1.45
        assert sources[1].magnitude == 1.45
        edbapp.close()

    def test_delete_pingroup(self):
        """Delete siwave pin groups."""
        # Done
        source_path = os.path.join(local_path, "example_models", test_subfolder, "test_pin_group.aedb")
        target_path = os.path.join(self.local_scratch.path, "test_135_pin_group.aedb")
        self.local_scratch.copyfolder(source_path, target_path)
        edbapp = Edb(target_path, edbversion=desktop_version)
        for _, pingroup in edbapp.siwave.pin_groups.items():
            pingroup.delete()
        assert not edbapp.siwave.pin_groups
        edbapp.close()

    def test_create_padstack_instance(self, edb_examples):
        """Create padstack instances."""
        # Done
        edb = Edb(edbversion=desktop_version)
        edb.stackup.add_layer(layer_name="1_Top", fillMaterial="air", thickness="30um")
        edb.stackup.add_layer(layer_name="contact", fillMaterial="air", thickness="100um", base_layer="1_Top")

        assert edb.padstacks.create(
            pad_shape="Rectangle",
            padstackname="pad",
            x_size="350um",
            y_size="500um",
            holediam=0,
        )
        pad_instance1 = edb.padstacks.place(position=["-0.65mm", "-0.665mm"], definition_name="pad")
        assert pad_instance1
        pad_instance1.start_layer = "1_Top"
        pad_instance1.stop_layer = "1_Top"
        assert pad_instance1.start_layer == "1_Top"
        assert pad_instance1.stop_layer == "1_Top"

        assert edb.padstacks.create(pad_shape="Circle", padstackname="pad2", paddiam="350um", holediam="15um")
        pad_instance2 = edb.padstacks.place(position=["-0.65mm", "-0.665mm"], definition_name="pad2")
        assert pad_instance2
        pad_instance2.start_layer = "1_Top"
        pad_instance2.stop_layer = "1_Top"
        assert pad_instance2.start_layer == "1_Top"
        assert pad_instance2.stop_layer == "1_Top"

        assert edb.padstacks.create(
            pad_shape="Circle",
            padstackname="test2",
            paddiam="400um",
            holediam="200um",
            antipad_shape="Rectangle",
            anti_pad_x_size="700um",
            anti_pad_y_size="800um",
            start_layer="1_Top",
            stop_layer="1_Top",
        )

        pad_instance3 = edb.padstacks.place(position=["-1.65mm", "-1.665mm"], definition_name="test2")
        assert pad_instance3.start_layer == "1_Top"
        assert pad_instance3.stop_layer == "1_Top"
        # TODO check with dev the Property ID
        # pad_instance3.dcir_equipotential_region = True
        # assert pad_instance3.dcir_equipotential_region
        # pad_instance3.dcir_equipotential_region = False
        # assert not pad_instance3.dcir_equipotential_region

        trace = edb.modeler.create_trace([[0, 0], [0, 10e-3]], "1_Top", "0.1mm", "trace_with_via_fence")
        edb.padstacks.create("via_0")
        trace.create_via_fence("1mm", "1mm", "via_0")
        edb.close()

    def test_stackup_properties(self):
        """Evaluate stackup properties."""
        # Done
        edb = Edb(edbversion=desktop_version)
        edb.stackup.add_layer(layer_name="gnd", fillMaterial="air", thickness="10um")
        edb.stackup.add_layer(layer_name="diel1", fillMaterial="air", thickness="200um", base_layer="gnd")
        edb.stackup.add_layer(layer_name="sig1", fillMaterial="air", thickness="10um", base_layer="diel1")
        edb.stackup.add_layer(layer_name="diel2", fillMaterial="air", thickness="200um", base_layer="sig1")
        edb.stackup.add_layer(layer_name="sig3", fillMaterial="air", thickness="10um", base_layer="diel2")
        assert edb.stackup.thickness == 0.00043
        assert edb.stackup.num_layers == 5
        edb.close()

    def test_hfss_extent_info(self):
        """HFSS extent information."""

        # TODO check config file 2.0

        # Obsolete addressed in config 2.0 section.
        pass

    def test_import_gds_from_tech(self):
        """Use techfile."""
        from pyedb.dotnet.database.edb_data.control_file import ControlFile

        c_file_in = os.path.join(
            local_path,
            "example_models",
            "cad",
            "GDS",
            "sky130_fictitious_dtc_example_control_no_map.xml",
        )
        c_map = os.path.join(local_path, "example_models", "cad", "GDS", "dummy_layermap.map")
        gds_in = os.path.join(
            local_path,
            "example_models",
            "cad",
            "GDS",
            "sky130_fictitious_dtc_example.gds",
        )
        gds_out = os.path.join(self.local_scratch.path, "sky130_fictitious_dtc_example.gds")
        self.local_scratch.copyfile(gds_in, gds_out)

        c = ControlFile(c_file_in, layer_map=c_map)
        setup = c.setups.add_setup("Setup1", "1GHz", 0.02, 10)
        setup.add_sweep("Sweep1", "0.01GHz", "5GHz", "0.1GHz")
        c.boundaries.units = "um"
        c.stackup.units = "um"
        c.boundaries.add_port("P1", x1=223.7, y1=222.6, layer1="Metal6", x2=223.7, y2=100, layer2="Metal6")
        c.boundaries.add_extent()
        comp = c.components.add_component("B1", "BGA", "IC", "Flip chip", "Cylinder")
        comp.solder_diameter = "65um"
        comp.add_pin("1", "81.28", "84.6", "met2")
        comp.add_pin("2", "211.28", "84.6", "met2")
        comp.add_pin("3", "211.28", "214.6", "met2")
        comp.add_pin("4", "81.28", "214.6", "met2")
        for via in c.stackup.vias:
            via.create_via_group = True
            via.snap_via_group = True
        c.write_xml(os.path.join(self.local_scratch.path, "test_138.xml"))
        c.import_options.import_dummy_nets = True

        edb = Edb(
            gds_out,
            edbversion=desktop_version,
            control_file=os.path.join(self.local_scratch.path, "test_138.xml"),
        )

        assert edb
        assert "P1" and "P2" in edb.ports
        assert "Setup1" and "Setup Test" in edb.setups
        assert "B1" in edb.components.instances
        edb.close()

    def test_database_properties(self, edb_examples):
        """Evaluate database properties."""
        # Done
        edb = edb_examples.get_si_verse()
        assert isinstance(edb.dataset_defs, list)
        assert isinstance(edb.material_defs, list)
        assert isinstance(edb.component_defs, list)
        assert isinstance(edb.package_defs, list)
        assert isinstance(edb.padstack_defs, list)
        assert isinstance(edb.jedec5_bondwire_defs, list)
        assert isinstance(edb.jedec4_bondwire_defs, list)
        assert isinstance(edb.apd_bondwire_defs, list)
        assert isinstance(edb.version, tuple)
        assert isinstance(edb.footprint_cells, list)
        edb.close()

    def test_backdrill_via_with_offset(self):
        """Set backdrill from top."""

        edb = Edb(edbversion=desktop_version)
        edb.stackup.add_layer(layer_name="bot")
        edb.stackup.add_layer(layer_name="diel1", base_layer="bot", layer_type="dielectric", thickness="127um")
        edb.stackup.add_layer(layer_name="signal1", base_layer="diel1")
        edb.stackup.add_layer(layer_name="diel2", base_layer="signal1", layer_type="dielectric", thickness="127um")
        edb.stackup.add_layer(layer_name="signal2", base_layer="diel2")
        edb.stackup.add_layer(layer_name="diel3", base_layer="signal2", layer_type="dielectric", thickness="127um")
        edb.stackup.add_layer(layer_name="top", base_layer="diel2")
        edb.padstacks.create(padstackname="test1")
        padstack_instance = edb.padstacks.place(position=[0, 0], net_name="test", definition_name="test1")
        edb.padstacks.definitions["test1"].hole_range = "through"
        drill_layer = edb.stackup.layers["signal1"]
        drill_diameter = "200um"
        drill_offset = "100um"
        padstack_instance.set_back_drill_by_layer(
            drill_to_layer=drill_layer, diameter=drill_diameter, offset=drill_offset
        )
        assert padstack_instance.backdrill_type == "layer_drill"
        assert padstack_instance.get_back_drill_by_layer()
        layer, offset, diameter = padstack_instance.get_back_drill_by_layer()
        assert layer == "signal1"
        assert offset == 100e-6
        assert diameter == 200e-6
        edb.close()

    def test_add_layer_api_with_control_file(self):
        """Add new layers with control file."""
        from pyedb.grpc.database.control_file import ControlFile

        # Done
        ctrl = ControlFile()
        # Material
        ctrl.stackup.add_material(material_name="Copper", conductivity=5.56e7)
        ctrl.stackup.add_material(material_name="BCB", permittivity=2.7)
        ctrl.stackup.add_material(material_name="Silicon", conductivity=0.04)
        ctrl.stackup.add_material(material_name="SiliconOxide", conductivity=4.4)
        ctrl.stackup.units = "um"
        assert len(ctrl.stackup.materials) == 4
        assert ctrl.stackup.units == "um"
        # Dielectrics
        ctrl.stackup.add_dielectric(material="Silicon", layer_name="Silicon", thickness=180)
        ctrl.stackup.add_dielectric(layer_index=1, material="SiliconOxide", layer_name="USG1", thickness=1.2)
        assert next(diel for diel in ctrl.stackup.dielectrics if diel.name == "USG1").properties["Index"] == 1
        ctrl.stackup.add_dielectric(material="BCB", layer_name="BCB2", thickness=9.5, base_layer="USG1")
        ctrl.stackup.add_dielectric(
            material="BCB", layer_name="BCB1", thickness=4.1, base_layer="BCB2", add_on_top=False
        )
        ctrl.stackup.add_dielectric(layer_index=4, material="BCB", layer_name="BCB3", thickness=6.5)
        assert ctrl.stackup.dielectrics[0].properties["Index"] == 0
        assert ctrl.stackup.dielectrics[1].properties["Index"] == 1
        assert ctrl.stackup.dielectrics[2].properties["Index"] == 3
        assert ctrl.stackup.dielectrics[3].properties["Index"] == 2
        assert ctrl.stackup.dielectrics[4].properties["Index"] == 4
        # Metal layer
        ctrl.stackup.add_layer(
            layer_name="9", elevation=185.3, material="Copper", target_layer="meta2", gds_type=0, thickness=6
        )
        assert [layer for layer in ctrl.stackup.layers if layer.name == "9"]
        ctrl.stackup.add_layer(
            layer_name="15", elevation=194.8, material="Copper", target_layer="meta3", gds_type=0, thickness=3
        )
        assert [layer for layer in ctrl.stackup.layers if layer.name == "15"]
        # Via layer
        ctrl.stackup.add_via(
            layer_name="14", material="Copper", target_layer="via2", start_layer="meta2", stop_layer="meta3", gds_type=0
        )
        assert [layer for layer in ctrl.stackup.vias if layer.name == "14"]
        # Port
        ctrl.boundaries.add_port(
            "test_port", x1=-21.1, y1=-288.7, layer1="meta3", x2=21.1, y2=-288.7, layer2="meta3", z0=50
        )
        assert ctrl.boundaries.ports
        # setup using q3D for DC point
        setup = ctrl.setups.add_setup("test_setup", "10GHz")
        assert setup
        setup.add_sweep(
            name="test_sweep",
            start="0GHz",
            stop="20GHz",
            step="10MHz",
            sweep_type="Interpolating",
            step_type="LinearStep",
            use_q3d=True,
        )
        assert setup.sweeps

    @pytest.mark.skipif(is_linux, reason="Failing download files")
    def test_create_edb_with_dxf(self):
        """Create EDB from dxf file."""
        src = os.path.join(local_path, "example_models", test_subfolder, "edb_test_82.dxf")
        dxf_path = self.local_scratch.copyfile(src)
        edb3 = Edb(dxf_path, edbversion=desktop_version)
        assert len(edb3.modeler.polygons) == 1
        assert edb3.modeler.polygons[0].polygon_data.points == [
            (0.0, 0.0),
            (0.0, 0.0012),
            (-0.0008, 0.0012),
            (-0.0008, 0.0),
        ]
        edb3.close()

    @pytest.mark.skipif(is_linux, reason="Not supported in IPY")
    def test_solve_siwave(self):
        """Solve EDB with Siwave."""
        target_path = os.path.join(local_path, "example_models", "T40", "ANSYS-HSD_V1_DCIR.aedb")
        out_edb = os.path.join(self.local_scratch.path, "to_be_solved.aedb")
        self.local_scratch.copyfolder(target_path, out_edb)
        edbapp = Edb(out_edb, edbversion=desktop_version)
        edbapp.siwave.create_exec_file(add_dc=True)
        out = edbapp.solve_siwave()
        res = edbapp.export_siwave_dc_results(out, "SIwaveDCIR1")
        for i in res:
            assert os.path.exists(i)

    def test_cutout_return_clipping_extent(self, edb_examples):
        """"""
        # Done
        edbapp = edb_examples.get_si_verse()
        extent = edbapp.cutout(
            signal_list=["PCIe_Gen4_RX0_P", "PCIe_Gen4_RX0_N", "PCIe_Gen4_RX1_P", "PCIe_Gen4_RX1_N"],
            reference_list=["GND"],
        )
        assert extent
        assert len(extent) == 55
        if edbapp.grpc:
            # grpc and dotnet have rounding differences
            assert extent[0] == [0.011025799607142596, 0.04451508809926884]
            assert extent[10] == [0.02214231174553801, 0.02851039223066996]
            assert extent[20] == [0.06722930402216426, 0.02605468368384399]
            assert extent[30] == [0.06793706871543964, 0.02961898967909681]
            assert extent[40] == [0.0655032742298304, 0.03147893183305721]
            assert extent[50] == [0.01143465157862367, 0.046365530038092975]
        else:
            assert extent[0] == [0.011025799702099603, 0.04451508810211455]
            assert extent[10] == [0.022142311790681247, 0.02851039231475559]
            assert extent[20] == [0.06722930398844625, 0.026054683772800503]
            assert extent[30] == [0.06793706863503707, 0.02961898962849831]
            assert extent[40] == [0.06550327418370948, 0.031478931749766806]
            assert extent[50] == [0.01143465165463851, 0.04636552997976474]
        edbapp.close_edb()

    def test_move_and_edit_polygons(self):
        """Move a polygon."""
        # Done
        target_path = os.path.join(self.local_scratch.path, "test_move_edit_polygons", "test.aedb")
        edbapp = Edb(target_path, edbversion=desktop_version)

        edbapp.stackup.add_layer("GND")
        edbapp.stackup.add_layer("Diel", "GND", layer_type="dielectric", thickness="0.1mm", material="FR4_epoxy")
        edbapp.stackup.add_layer("TOP", "Diel", thickness="0.05mm")
        points = [[0.0, -1e-3], [0.0, -10e-3], [100e-3, -10e-3], [100e-3, -1e-3], [0.0, -1e-3]]
        polygon = edbapp.modeler.create_polygon(points, "TOP")
        assert polygon.center == [0.05, -0.0055]
        assert polygon.move(["1mm", 1e-3])
        assert round(polygon.center[0], 6) == 0.051
        assert round(polygon.center[1], 6) == -0.0045

        assert polygon.rotate(angle=45)
        assert polygon.bbox == [0.012463, -0.043037, 0.089537, 0.034037]
        assert polygon.rotate(angle=34, center=[0, 0])
        assert polygon.bbox == [0.03084, -0.025152, 0.058755, 0.074728]
        assert polygon.scale(factor=1.5)
        assert polygon.bbox == [0.023861, -0.050122, 0.065734, 0.099698]
        assert polygon.scale(factor=-0.5, center=[0, 0])
        assert polygon.bbox == [-0.032867, -0.049849, -0.01193, 0.025061]
        assert polygon.move_layer("GND")
        assert len(edbapp.modeler.polygons) == 1
        assert edbapp.modeler.polygons[0].layer_name == "GND"
        edbapp.close()

    def test_multizone(self, edb_examples):
        # Done
        # edbapp = edb_examples.get_multizone_pcb()
        # common_reference_net = "gnd"
        # edb_zones = edbapp.copy_zones()
        # assert edb_zones
        # defined_ports, project_connexions = edbapp.cutout_multizone_layout(edb_zones, common_reference_net)
        # assert defined_ports
        # assert project_connexions
        pass

    def test_icepak(self, edb_examples):
        # Done
        edbapp = edb_examples.get_si_verse(additional_files_folders=["siwave/icepak_component.pwrd"])
        edbapp.siwave.icepak_use_minimal_comp_defaults = True
        assert edbapp.siwave.icepak_use_minimal_comp_defaults
        edbapp.siwave.icepak_use_minimal_comp_defaults = False
        assert not edbapp.siwave.icepak_use_minimal_comp_defaults
        edbapp.siwave.icepak_component_file = edb_examples.get_local_file_folder("siwave/icepak_component.pwrd")
        assert edbapp.siwave.icepak_component_file == edb_examples.get_local_file_folder("siwave/icepak_component.pwrd")
        edbapp.close()

    def test_dcir_properties(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        setup = edbapp.create_siwave_dc_setup()
        if edbapp.grpc:
            # grpc settings is replacing dc_ir_settings
            # TODO check is grpc can be backward compatible
            setup.settings.export_dc_thermal_data = True
            assert setup.settings.export_dc_thermal_data
            assert not setup.settings.import_thermal_data
            setup.settings.dc_report_show_active_devices = True
            assert setup.settings.dc_report_show_active_devices
            assert not setup.settings.per_pin_use_pin_format
            setup.settings.use_loop_res_for_per_pin = True
            assert setup.settings.use_loop_res_for_per_pin
            setup.settings.dc_report_config_file = edbapp.edbpath
            assert setup.settings.dc_report_config_file
            setup.settings.full_dc_report_path = edbapp.edbpath
            assert setup.settings.full_dc_report_path
            setup.settings.icepak_temp_file = edbapp.edbpath
            assert setup.settings.icepak_temp_file
            setup.settings.per_pin_res_path = edbapp.edbpath
            assert setup.settings.per_pin_res_path
            setup.settings.via_report_path = edbapp.edbpath
            assert setup.settings.via_report_path
            setup.settings.source_terms_to_ground = {"test": 1}
            assert setup.settings.source_terms_to_ground
        else:
            setup.dc_ir_settings.export_dc_thermal_data = True
            assert setup.dc_ir_settings.export_dc_thermal_data
            assert not setup.dc_ir_settings.import_thermal_data
            setup.dc_ir_settings.dc_report_show_active_devices = True
            assert setup.dc_ir_settings.dc_report_show_active_devices
            assert not setup.dc_ir_settings.per_pin_use_pin_format
            setup.dc_ir_settings.use_loop_res_for_per_pin = True
            assert setup.dc_ir_settings.use_loop_res_for_per_pin
            setup.dc_ir_settings.dc_report_config_file = edbapp.edbpath
            assert setup.dc_ir_settings.dc_report_config_file
            setup.dc_ir_settings.full_dc_report_path = edbapp.edbpath
            assert setup.dc_ir_settings.full_dc_report_path
            setup.dc_ir_settings.icepak_temp_file = edbapp.edbpath
            assert setup.dc_ir_settings.icepak_temp_file
            setup.dc_ir_settings.per_pin_res_path = edbapp.edbpath
            assert setup.dc_ir_settings.per_pin_res_path
            setup.dc_ir_settings.via_report_path = edbapp.edbpath
            assert setup.dc_ir_settings.via_report_path
            setup.dc_ir_settings.source_terms_to_ground = {"test": 1}
            assert setup.dc_ir_settings.source_terms_to_ground
        edbapp.close()

    def test_arbitrary_wave_ports(self):
        # TODO check later when sever instances is improved.
        example_folder = os.path.join(local_path, "example_models", test_subfolder)
        source_path_edb = os.path.join(example_folder, "example_arbitrary_wave_ports.aedb")
        target_path_edb = os.path.join(self.local_scratch.path, "test_wave_ports", "test.aedb")
        self.local_scratch.copyfolder(source_path_edb, target_path_edb)
        edbapp = Edb(target_path_edb, edbversion=desktop_version)
        assert edbapp.create_model_for_arbitrary_wave_ports(
            temp_directory=self.local_scratch.path,
            output_edb=os.path.join(self.local_scratch.path, "wave_ports.aedb"),
            mounting_side="top",
        )
        edb_model = os.path.join(self.local_scratch.path, "wave_ports.aedb")
        assert os.path.isdir(edb_model)
        edbapp.close()

    def test_bondwire(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        bondwire_1 = edbapp.modeler.create_bondwire(
            definition_name="Default",
            placement_layer="Postprocessing",
            width="0.5mm",
            material="copper",
            start_layer_name="1_Top",
            start_x="82mm",
            start_y="30mm",
            end_layer_name="1_Top",
            end_x="71mm",
            end_y="23mm",
            bondwire_type="apd",
            net="1V0",
            start_cell_instance_name="test",
        )
        bondwire_1.material = "Gold"
        assert bondwire_1.material == "Gold"
        bondwire_1.type = "jedec4"
        if edbapp.grpc:
            assert bondwire_1.type == "jedec4"
        else:
            assert bondwire_1.type == "jedec_4"
        bondwire_1.cross_section_type = "round"
        assert bondwire_1.cross_section_type == "round"
        bondwire_1.cross_section_height = "0.1mm"
        assert bondwire_1.cross_section_height == 0.0001
        bondwire_1.set_definition_name("J4_LH10")
        assert bondwire_1.get_definition_name() == "J4_LH10"
        bondwire_1.trajectory = [1, 0.1, 0.2, 0.3]
        assert bondwire_1.trajectory == [1, 0.1, 0.2, 0.3]
        bondwire_1.width = "0.2mm"
        assert bondwire_1.width == 0.0002
        edbapp.close()

    def test_voltage_regulator(self, edb_examples):
        # TODO working with EDB NET only. Not implemented yet in grpc yet. Also Voltage regulator is bugged in DotNet.
        edbapp = edb_examples.get_si_verse()
        if not edbapp.grpc:
            positive_sensor_pin = edbapp.components["U1"].pins["A2"]
            negative_sensor_pin = edbapp.components["U1"].pins["A3"]
            vrm = edbapp.siwave.create_vrm_module(
                name="test",
                positive_sensor_pin=positive_sensor_pin,
                negative_sensor_pin=negative_sensor_pin,
                voltage="1.5V",
                load_regulation_current="0.5A",
                load_regulation_percent=0.2,
            )
            assert vrm.component
            assert vrm.component.refdes == "U1"
            assert vrm.negative_remote_sense_pin
            assert vrm.negative_remote_sense_pin.name == "U1-A3"
            assert vrm.positive_remote_sense_pin
            assert vrm.positive_remote_sense_pin.name == "U1-A2"
            assert vrm.voltage == 1.5
            assert vrm.is_active
            assert not vrm.is_null
            assert vrm.id
            assert edbapp.voltage_regulator_modules
            assert "test" in edbapp.voltage_regulator_modules
        edbapp.close()

    def test_workflow(self, edb_examples):
        # TODO check with config file 2.0
        from pathlib import Path

        edbapp = edb_examples.get_si_verse()
        path_bom = Path(edb_examples.test_folder) / "bom.csv"
        edbapp.workflow.export_bill_of_materials(path_bom)
        assert path_bom.exists()
        edbapp.close()
        pass

    def test_create_port_on_component_no_ref_pins_in_component(self, edb_examples):
        # Done
        edbapp = edb_examples.get_no_ref_pins_component()
        edbapp.components.create_port_on_component(
            component="J2E2",
            net_list=[
                "net1",
                "net2",
                "net3",
                "net4",
                "net5",
                "net6",
                "net7",
                "net8",
                "net9",
                "net10",
                "net11",
                "net12",
                "net13",
                "net14",
                "net15",
            ],
            port_type="circuit_port",
            reference_net=["GND"],
            extend_reference_pins_outside_component=True,
        )
        assert len(edbapp.ports) == 15
        edbapp.close()

    def test_create_ping_group(self, edb_examples):
        # Done
        edbapp = edb_examples.get_si_verse()
        assert edbapp.modeler.create_pin_group(
            name="test1", pins_by_id=[4294969495, 4294969494, 4294969496, 4294969497]
        )

        assert edbapp.modeler.create_pin_group(
            name="test2", pins_by_id=[4294969502, 4294969503], pins_by_aedt_name=["U1-A11", "U1-A12", "U1-A13"]
        )
        assert edbapp.modeler.create_pin_group(
            name="test3",
            pins_by_id=[4294969502, 4294969503],
            pins_by_aedt_name=["U1-A11", "U1-A12", "U1-A13"],
            pins_by_name=["A11", "A12", "A15", "A16"],
        )
        edbapp.close()

    def test_create_edb_with_zip(self):
        """Create EDB from zip file."""
        # Done
        src = os.path.join(local_path, "example_models", "TEDB", "ANSYS-HSD_V1_0.zip")
        zip_path = self.local_scratch.copyfile(src)
        edb = Edb(zip_path, edbversion=desktop_version)
        assert edb.nets
        assert edb.components
        edb.close()

    @pytest.mark.parametrize("positive_net_names", (["2V5", "NetR105_2"], ["2V5", "GND", "NetR105_2"], "2V5"))
    @pytest.mark.parametrize("nets_mode", ("str", "net"))
    def test_create_circuit_port_on_component(self, edb_examples, nets_mode: str, positive_net_names: Sequence[str]):
        edbapp = edb_examples.get_si_verse()
        positive_net_list = [positive_net_names] if not isinstance(positive_net_names, list) else positive_net_names
        reference_net_names = ["GND"]
        if edbapp.grpc:
            assert edbapp.source_excitation.create_port_on_component(
                component="U10",
                net_list=positive_net_names if nets_mode == "str" else [edbapp.nets[net] for net in positive_net_list],
                port_type="circuit_port",
                do_pingroup=False,
                reference_net=(
                    reference_net_names if nets_mode == "str" else [edbapp.nets[net] for net in reference_net_names]
                ),
            )
        else:
            # method from components class is deprecated in grpc and is now in SourceExcitation class.
            assert edbapp.components.create_port_on_component(
                component="U10",
                net_list=positive_net_names if nets_mode == "str" else [edbapp.nets[net] for net in positive_net_list],
                port_type="circuit_port",
                do_pingroup=False,
                reference_net=(
                    reference_net_names if nets_mode == "str" else [edbapp.nets[net] for net in reference_net_names]
                ),
            )
        assert len(edbapp.excitations) == 2 * len(set(positive_net_list) - set(reference_net_names))

    def test_create_circuit_port_on_component_string_net_list(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        positive_net_names = "2V5"
        reference_net_names = "GND"
        component_name = "U10"
        for pin in edbapp.components[component_name].pins.values():
            pin.is_pin = False
        if edbapp.grpc:
            assert edbapp.source_excitation.create_port_on_component(
                component=component_name,
                net_list=positive_net_names,
                port_type="circuit_port",
                do_pingroup=False,
                reference_net=reference_net_names,
            )
        else:
            # method from Components class deprecated in grpc and moved to SourceExcitation.
            assert edbapp.components.create_port_on_component(
                component=component_name,
                net_list=positive_net_names,
                port_type="circuit_port",
                do_pingroup=False,
                reference_net=reference_net_names,
            )
        assert len(edbapp.excitations) == 2

    def test_create_circuit_port_on_component_set_is_pin(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        positive_net_names = ["2V5", "NetR105_2"]
        reference_net_names = ["GND"]
        component_name = "U10"
        for pin in edbapp.components[component_name].pins.values():
            pin.is_pin = False
        if edbapp.grpc:
            assert edbapp.source_excitation.create_port_on_component(
                component=component_name,
                net_list=positive_net_names,
                port_type="circuit_port",
                do_pingroup=False,
                reference_net=reference_net_names,
            )
        else:
            # Method from Components class deprecated in grpc and moved to SourceExcitation.
            assert edbapp.components.create_port_on_component(
                component=component_name,
                net_list=positive_net_names,
                port_type="circuit_port",
                do_pingroup=False,
                reference_net=reference_net_names,
            )
        assert len(edbapp.excitations) == 4

    @pytest.mark.parametrize("comp_mode", ("str", "comp"))
    def test_create_circuit_port_on_component_pins_comp_mode(self, comp_mode: str, edb_examples):
        edbapp = edb_examples.get_si_verse()
        component_name = "U10"
        edbcomp = edbapp.components[component_name]
        positive_pin_names = ["4"]
        reference_pin_names = ["2"]
        if edbapp.grpc:
            assert edbapp.source_excitation.create_port_on_pins(
                refdes=component_name if comp_mode == "str" else edbcomp,
                pins=positive_pin_names,
                reference_pins=reference_pin_names,
            )
        else:
            # Method from Components class deprecated in grpc and moved to SourceExcitations.
            assert edbapp.components.create_port_on_pins(
                refdes=component_name if comp_mode == "str" else edbcomp,
                pins=positive_pin_names,
                reference_pins=reference_pin_names,
            )
        assert len(edbapp.excitations) == 2

    @pytest.mark.parametrize("pins_mode", ("global_str", "int", "str", "pin"))
    def test_create_circuit_port_on_component_pins_pins_mode(self, edb_examples, pins_mode: str):
        # Check issue #550 on changing edb_uid to id.
        edbapp = edb_examples.get_si_verse()
        component_name = "U10"
        edbcomp = edbapp.components[component_name]
        positive_pin_names = ["4"]
        reference_pin_names = ["2"]
        if edbapp.grpc:
            positive_pin_numbers = [edbcomp.pins[pin].edb_uid for pin in positive_pin_names]
            reference_pin_numbers = [edbcomp.pins[pin].edb_uid for pin in reference_pin_names]
        else:
            positive_pin_numbers = [edbcomp.pins[pin].id for pin in positive_pin_names]
            reference_pin_numbers = [edbcomp.pins[pin].id for pin in reference_pin_names]
        if pins_mode == "global_str":
            positive_pin_names = [f"{component_name}-{pin}" for pin in positive_pin_names]
            reference_pin_names = [f"{component_name}-{pin}" for pin in reference_pin_names]
        assert len(edbapp.excitations) == 0
        if edbapp.grpc:
            assert edbapp.source_excitation.create_port_on_pins(
                refdes=component_name if pins_mode == "str" else None,
                pins=(
                    positive_pin_names
                    if pins_mode == "str" or pins_mode == "global_str"
                    else (
                        positive_pin_numbers
                        if pins_mode == "int"
                        else [edbcomp.pins[pin] for pin in positive_pin_names]
                    )
                ),
                reference_pins=(
                    reference_pin_names
                    if pins_mode == "str" or pins_mode == "global_str"
                    else (
                        reference_pin_numbers
                        if pins_mode == "int"
                        else [edbcomp.pins[pin] for pin in reference_pin_names]
                    )
                ),
            )
        else:
            assert edbapp.components.create_port_on_pins(
                refdes=component_name if pins_mode == "str" else None,
                pins=(
                    positive_pin_names
                    if pins_mode == "str" or pins_mode == "global_str"
                    else (
                        positive_pin_numbers
                        if pins_mode == "int"
                        else [edbcomp.pins[pin] for pin in positive_pin_names]
                    )
                ),
                reference_pins=(
                    reference_pin_names
                    if pins_mode == "str" or pins_mode == "global_str"
                    else (
                        reference_pin_numbers
                        if pins_mode == "int"
                        else [edbcomp.pins[pin] for pin in reference_pin_names]
                    )
                ),
            )
        assert len(edbapp.excitations) == 2

    def test_create_circuit_port_on_component_pins_pingroup_on_single_pin(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        component_name = "U10"
        edbcomp = edbapp.components[component_name]
        positive_pin_names = ["4"]
        reference_pin_names = ["2"]
        if edbapp.grpc:
            assert edbapp.source_excitation.create_port_on_pins(
                refdes=edbcomp,
                pins=positive_pin_names,
                reference_pins=reference_pin_names,
                pingroup_on_single_pin=True,
            )
        else:
            # Method from COmponents deprecated in grpc and moved to SourceExcitation-
            assert edbapp.components.create_port_on_pins(
                refdes=edbcomp,
                pins=positive_pin_names,
                reference_pins=reference_pin_names,
                pingroup_on_single_pin=True,
            )
        assert len(edbapp.excitations) == 2

    def test_create_circuit_port_on_component_pins_no_pins(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        component_name = "U10"
        edbcomp = edbapp.components[component_name]
        positive_pin_names = []
        reference_pin_names = ["2"]
        if edbapp.grpc:
            assert not edbapp.source_excitation.create_port_on_pins(
                refdes=edbcomp,
                pins=positive_pin_names,
                reference_pins=reference_pin_names,
            )
        else:
            # Method deprecated in grpc and moved to SourceExcitation class.
            assert not edbapp.components.create_port_on_pins(
                refdes=edbcomp,
                pins=positive_pin_names,
                reference_pins=reference_pin_names,
            )
        assert len(edbapp.excitations) == 0

    def test_create_circuit_port_on_component_pins_no_reference_pins(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        component_name = "U10"
        edbcomp = edbapp.components[component_name]
        positive_pin_names = ["4"]
        reference_pin_names = []
        if edbapp.grpc:
            assert not edbapp.source_excitation.create_port_on_pins(
                refdes=edbcomp,
                pins=positive_pin_names,
                reference_pins=reference_pin_names,
            )
        else:
            # Method deprecated in grpc and moved to SourceExcitation class.
            assert not edbapp.components.create_port_on_pins(
                refdes=edbcomp,
                pins=positive_pin_names,
                reference_pins=reference_pin_names,
            )
        assert len(edbapp.excitations) == 0

    def test_active_cell_setter(self):
        """Use multiple cells."""
        src = os.path.join(local_path, "example_models", "TEDB", "multi_cells.aedb")
        edb = Edb(edbpath=src, edbversion=desktop_version)
        edb.active_cell = edb.circuit_cells[0]
        assert len(edb.modeler.primitives) == 2096
        assert len(edb.components.instances) == 509
        assert len(edb.padstacks.instances) == 5699

        edb.active_cell = edb.circuit_cells[1]
        assert len(edb.modeler.primitives) == 203
        assert len(edb.components.instances) == 66
        assert len(edb.padstacks.instances) == 473

        edb.active_cell = edb.circuit_cells[2]
        assert len(edb.modeler.primitives) == 2096
        assert len(edb.components.instances) == 509
        assert len(edb.padstacks.instances) == 5699

        edb.active_cell = edb.circuit_cells[3]
        assert len(edb.modeler.primitives) == 203
        assert len(edb.components.instances) == 66
        assert len(edb.padstacks.instances) == 473

        edb.active_cell = "main"
        assert len(edb.modeler.primitives) == 2096
        assert len(edb.components.instances) == 509
        assert len(edb.padstacks.instances) == 5699

        edb.active_cell = "main_cutout"
        assert len(edb.modeler.primitives) == 203
        assert len(edb.components.instances) == 66
        assert len(edb.padstacks.instances) == 473

        edb.close()

    def test_import_layout_file(self):
        input_file = os.path.join(local_path, "example_models", "cad", "GDS", "sky130_fictitious_dtc_example.gds")
        control_file = os.path.join(
            local_path, "example_models", "cad", "GDS", "sky130_fictitious_dtc_example_control_no_map.xml"
        )
        map_file = os.path.join(local_path, "example_models", "cad", "GDS", "dummy_layermap.map")
        edb = Edb(edbversion=desktop_version)
        assert edb.import_layout_file(input_file=input_file, control_file=control_file, map_file=map_file)

    @pytest.mark.parametrize("positive_pin_names", (["R20", "R21", "T20"], ["R20"]))
    @pytest.mark.parametrize("pec_boundary", (False, True))
    def test_create_circuit_port_on_component_pins_pingroup_on_multiple_pins(
        self, edb_examples, pec_boundary: bool, positive_pin_names: Sequence[str]
    ):
        EXPECTED_TERMINAL_TYPE = "PinGroupTerminal" if len(positive_pin_names) > 1 else "PadstackInstanceTerminal"
        edbapp = edb_examples.get_si_verse()
        component_name = "U1"
        edbcomp = edbapp.components[component_name]
        reference_pin_names = ["N21", "R19", "T21"]
        assert edbapp.components.create_port_on_pins(
            refdes=edbcomp,
            pins=positive_pin_names,
            reference_pins=reference_pin_names,
            pec_boundary=pec_boundary,
        )
        assert len(edbapp.excitations) == 2
        for excitation in edbapp.excitations.values():
            if excitation.is_reference_terminal:
                assert excitation.terminal_type == "PinGroupTerminal"
            else:
                assert excitation.terminal_type == EXPECTED_TERMINAL_TYPE

    @pytest.mark.parametrize("positive_pin_names", (["R20", "R21", "T20"], ["R20"]))
    @pytest.mark.parametrize("pec_boundary", (False, True))
    def test_create_circuit_port_on_component_pins_pingroup_on_multiple_pins(
        self, edb_examples, pec_boundary: bool, positive_pin_names: Sequence[str]
    ):
        EXPECTED_TERMINAL_TYPE = "PinGroupTerminal" if len(positive_pin_names) > 1 else "PadstackInstanceTerminal"
        edbapp = edb_examples.get_si_verse()
        component_name = "U1"
        edbcomp = edbapp.components[component_name]
        reference_pin_names = ["N21", "R19", "T21"]
        assert edbapp.components.create_port_on_pins(
            refdes=edbcomp,
            pins=positive_pin_names,
            reference_pins=reference_pin_names,
            pec_boundary=pec_boundary,
        )
        assert len(edbapp.excitations) == 2
        for excitation in edbapp.excitations.values():
            if excitation.is_reference_terminal:
                assert excitation.terminal_type == "PinGroupTerminal"
            else:
                assert excitation.terminal_type == EXPECTED_TERMINAL_TYPE

    def test_hfss_get_trace_width_for_traces_with_ports(self, edb_examples):
        """Retrieve the trace width for traces with ports."""
        edbapp = edb_examples.get_si_verse()
        from pyedb.generic.constants import SourceType

        assert edbapp.components.create_port_on_component(
            "U1",
            ["VDD_DDR"],
            reference_net="GND",
            port_type=SourceType.CircPort,
        )
        trace_widths = edbapp.hfss.get_trace_width_for_traces_with_ports()
        assert len(trace_widths) > 0
        edbapp.close()

    def test_add_cpa_simulation_setup(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        cpa_setup = edbapp.siwave.add_cpa_analysis(name="test_cpa")
        assert cpa_setup.name == "test_cpa"
        cpa_setup.name = "test_cpa2"
        assert cpa_setup.name == "test_cpa2"
        cpa_setup.mode = "channel"
        assert cpa_setup.mode == "channel"
        assert cpa_setup.model_type == "rlcg"
        cpa_setup.model_type = "esd_r"
        assert cpa_setup.model_type == "esd_r"
        assert cpa_setup.net_processing_mode == "all"
        cpa_setup.net_processing_mode = "userdefined"
        assert cpa_setup.net_processing_mode == "userdefined"
        assert not cpa_setup.use_q3d_solver
        cpa_setup.use_q3d = True
        assert cpa_setup.use_q3d
        assert cpa_setup.solver_options.adaptive_refinement_cg_max_passes == 10
        cpa_setup.solver_options.adaptive_refinement_cg_max_passes = 20
        assert cpa_setup.solver_options.adaptive_refinement_cg_max_passes == 20
        assert cpa_setup.solver_options.adaptive_refinement_cg_percent_error == 0.02
        cpa_setup.solver_options.adaptive_refinement_cg_percent_error = 0.05
        assert cpa_setup.solver_options.adaptive_refinement_cg_percent_error == 0.05
        assert cpa_setup.solver_options.adaptive_refinement_rl_max_passes == 10
        cpa_setup.solver_options.adaptive_refinement_rl_max_passes = 20
        assert cpa_setup.solver_options.adaptive_refinement_rl_max_passes == 20
        assert cpa_setup.solver_options.adaptive_refinement_rl_percent_error == 0.02
        cpa_setup.solver_options.adaptive_refinement_rl_percent_error = 0.001
        assert cpa_setup.solver_options.adaptive_refinement_rl_percent_error == 0.001
        assert cpa_setup.solver_options.cg_percent_refinement_per_pass == 0.33
        cpa_setup.solver_options.cg_percent_refinement_per_pass = 0.45
        assert cpa_setup.solver_options.cg_percent_refinement_per_pass == 0.45
        assert cpa_setup.solver_options.compute_ac_rl
        cpa_setup.solver_options.compute_ac_rl = False
        assert not cpa_setup.solver_options.compute_ac_rl
        assert cpa_setup.solver_options.compute_capacitance
        cpa_setup.solver_options.compute_capacitance = False
        assert not cpa_setup.solver_options.compute_capacitance
        assert cpa_setup.solver_options.compute_dc_cg
        cpa_setup.solver_options.compute_dc_cg = False
        assert not cpa_setup.solver_options.compute_dc_cg
        assert cpa_setup.solver_options.compute_dc_rl
        cpa_setup.solver_options.compute_dc_rl = False
        assert not cpa_setup.solver_options.compute_dc_rl
        assert not cpa_setup.solver_options.custom_refinement
        cpa_setup.solver_options.custom_refinement = True
        assert cpa_setup.solver_options.custom_refinement
        assert cpa_setup.solver_options.extraction_frequency == "10Ghz"
        cpa_setup.solver_options.extraction_frequency = "20Ghz"
        assert cpa_setup.solver_options.extraction_frequency == "20Ghz"
        assert cpa_setup.solver_options.ground_power_nets_for_si
        cpa_setup.solver_options.ground_power_nets_for_si = False
        assert not cpa_setup.solver_options.ground_power_nets_for_si
        assert cpa_setup.solver_options.mode == "si"
        cpa_setup.solver_options.mode = "pi"
        assert cpa_setup.solver_options.mode == "pi"
        assert not cpa_setup.solver_options.model_type
        assert cpa_setup.solver_options.rl_percent_refinement_per_pass == 0.33
        cpa_setup.solver_options.rl_percent_refinement_per_pass = 0.66
        assert cpa_setup.solver_options.rl_percent_refinement_per_pass == 0.66
        cpa_setup.solver_options.small_hole_diameter = 0.1
        assert cpa_setup.solver_options.small_hole_diameter == 0.1

    def test_load_cpa_cfg(self, edb_examples):
        from pyedb.siwave_core.cpa.simulation_setup_data_model import (
            SIwaveCpaSetup,
            Vrm,
        )

        cpa_cfg = SIwaveCpaSetup()
        cpa_cfg.name = "test_cpa"
        cpa_cfg.mode = "channel"
        cpa_cfg.net_processing_mode = "userspecified"
        cpa_cfg.use_q3d_solver = True
        cpa_cfg.nets_to_process = ["VDD", "GND"]
        cpa_cfg.return_path_net_for_loop_parameters = True
        cpa_cfg.solver_options.small_hole_diameter = "auto"
        cpa_cfg.solver_options.extraction_frequency = "15Ghz"
        cpa_cfg.solver_options.custom_refinement = False
        cpa_cfg.solver_options.compute_dc_parameters = True
        cpa_cfg.solver_options.compute_ac_rl = True
        cpa_cfg.solver_options.compute_capacitance = True
        cpa_cfg.solver_options.rl_percent_refinement_per_pass = 0.45
        cpa_cfg.solver_options.compute_dc_cg = True
        cpa_cfg.solver_options.compute_dc_rl = True
        cpa_cfg.solver_options.ground_power_ground_nets_for_si = True
        cpa_cfg.solver_options.return_path_net_for_loop_parameters = False
        vrm = Vrm(name="test_vrm", voltage=2.5, reference_net="GND", power_net="VDD")
        cpa_cfg.channel_setup.vrm_setup = [vrm]
        cpa_cfg.channel_setup.pin_grouping_mode = "perpin"
        cpa_cfg.channel_setup.die_name = "die_test"
        cpa_cfg.channel_setup.channel_component_exposure = {"U1": True, "X1": True}

        cfg_dict = cpa_cfg.to_dict()
        assert cfg_dict["name"] == "test_cpa"
        cfg_dict["name"] = "test_cpa2"
        cpa_cfg = cpa_cfg.from_dict(cfg_dict)
        edbapp = edb_examples.get_si_verse()
        cpa_setup = edbapp.siwave.add_cpa_analysis(siwave_cpa_setup_class=cpa_cfg)
        assert cpa_setup.name == "test_cpa2"
        assert cpa_setup.mode == "channel"
        assert cpa_setup.net_processing_mode == "userspecified"
        assert cpa_setup.use_q3d_solver
        assert cpa_setup.nets_to_process == ["VDD", "GND"]
        assert cpa_setup.model_type == "rlcg"
        assert cpa_setup.channel_setup.channel_component_exposure == {"U1": True, "X1": True}
        assert cpa_setup.channel_setup.die_name == "die_test"
        assert cpa_setup.channel_setup.pin_grouping_mode == "perpin"
        assert len(cpa_setup.channel_setup.vrm) == 1
        assert cpa_setup.channel_setup.vrm[0].name == "test_vrm"
        assert cpa_setup.channel_setup.vrm[0].voltage == 2.5
        assert cpa_setup.channel_setup.vrm[0].reference_net == "GND"
        assert cpa_setup.channel_setup.vrm[0].power_net == "VDD"
        assert cpa_setup.solver_options.compute_dc_parameters == True
        assert cpa_setup.solver_options.compute_ac_rl == True
        assert cpa_setup.solver_options.compute_capacitance == True
        assert cpa_setup.solver_options.compute_dc_cg == True
        assert cpa_setup.solver_options.compute_dc_rl == True
        assert cpa_setup.solver_options.rl_percent_refinement_per_pass == 0.45
        assert cpa_setup.solver_options.small_hole_diameter == "auto"
        assert cpa_setup.solver_options.extraction_frequency == "15Ghz"
        assert cpa_setup.solver_options.ground_power_nets_for_si == True
        assert not cpa_setup.solver_options.return_path_net_for_loop_parameters
        edbapp.close()

    def test_compare_edbs(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        edb_base = os.path.join(local_path, "example_models", "TEDB", "ANSYS-HSD_V1.aedb")
        assert edbapp.compare(edb_base)
        folder = edbapp.edbpath[:-5] + "_compare_results"
        assert os.path.exists(folder)

    def test_create_layout_component(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        out_file = os.path.join(self.local_scratch.path, "test.aedbcomp")
        edbapp.export_layout_component(component_path=out_file)
        assert os.path.isfile(out_file)
        edbapp.close()
        edbapp = Edb(edbversion=desktop_version)
        layout_comp = edbapp.import_layout_component(out_file)
        assert not layout_comp.cell_instance.is_null
