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

import pytest

from pyedb.generic.general_methods import is_linux
from pyedb.grpc.edb import EdbGrpc as Edb
from tests.conftest import desktop_version, local_path
from tests.legacy.system.conftest import test_subfolder

pytestmark = [pytest.mark.system, pytest.mark.legacy]


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
        # Done
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
        # Done
        edbapp = edb_examples.get_si_verse()
        edbapp.add_design_variable("my_variable", "1mm")
        assert "my_variable" in edbapp.active_cell.get_all_variable_names()
        assert edbapp.modeler.parametrize_trace_width("DDR4_DQ25")
        assert edbapp.modeler.parametrize_trace_width("DDR4_A2")
        edbapp.add_design_variable("my_parameter", "2mm", True)
        assert "my_parameter" in edbapp.active_cell.get_all_variable_names()
        variable_value = edbapp.active_cell.get_variable_value("my_parameter").value
        assert variable_value == 2e-3
        assert not edbapp.add_design_variable("my_parameter", "2mm", True)
        edbapp.add_project_variable("$my_project_variable", "3mm")
        assert edbapp.db.get_variable_value("$my_project_variable") == 3e-3
        assert not edbapp.add_project_variable("$my_project_variable", "3mm")
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

    def test_create_custom_cutout_1(self, edb_examples):
        """Create custom cutout 1."""
        # DOne
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
            number_of_threads=4,
            extent_defeature=0.001,
            preserve_components_with_model=True,
            keep_lines_as_path=True,
        )
        assert "A0_N" not in edbapp.nets.nets
        # assert isinstance(edbapp.layout_validation.disjoint_nets("GND", order_by_area=True), list)
        # assert isinstance(edbapp.layout_validation.disjoint_nets("GND", keep_only_main_net=True), list)
        # assert isinstance(edbapp.layout_validation.disjoint_nets("GND", clean_disjoints_less_than=0.005), list)
        # assert edbapp.layout_validation.fix_self_intersections("PGND")
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
            number_of_threads=4,
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
            number_of_threads=4,
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
            number_of_threads=4,
            extent_type="ConvexHull",
            use_pyaedt_extent_computing=True,
            include_pingroups=True,
            check_terminals=True,
            expansion_factor=4,
        )
        edbapp.close()

    def test_export_to_hfss(self):
        """Export EDB to HFSS."""
        # Done
        edb = Edb(
            edbpath=os.path.join(local_path, "example_models", test_subfolder, "simple.aedb"),
            edbversion=desktop_version,
            restart_rpc_server=True,
        )
        options_config = {"UNITE_NETS": 1, "LAUNCH_Q3D": 0}
        out = edb.write_export3d_option_config_file(self.local_scratch.path, options_config)
        assert os.path.exists(out)
        out = edb.export_hfss(self.local_scratch.path)
        assert os.path.exists(out)
        edb.close()

    def test_export_to_q3d(self):
        """Export EDB to Q3D."""
        # Done
        edb = Edb(
            edbpath=os.path.join(local_path, "example_models", test_subfolder, "simple.aedb"),
            edbversion=desktop_version,
            restart_rpc_server=True,
        )
        options_config = {"UNITE_NETS": 1, "LAUNCH_Q3D": 0}
        out = edb.write_export3d_option_config_file(self.local_scratch.path, options_config)
        assert os.path.exists(out)
        out = edb.export_q3d(self.local_scratch.path, net_list=["ANALOG_A0", "ANALOG_A1", "ANALOG_A2"], hidden=True)
        assert os.path.exists(out)
        edb.close()

    def test_074_export_to_maxwell(self):
        """Export EDB to Maxwell 3D."""

        # Done

        edb = Edb(
            edbpath=os.path.join(local_path, "example_models", test_subfolder, "simple.aedb"),
            edbversion=desktop_version,
            restart_rpc_server=True,
        )
        options_config = {"UNITE_NETS": 1, "LAUNCH_MAXWELL": 0}
        out = edb.write_export3d_option_config_file(self.local_scratch.path, options_config)
        assert os.path.exists(out)
        out = edb.export_maxwell(self.local_scratch.path, num_cores=6)
        assert os.path.exists(out)
        edb.close()

    def test_create_edge_port_on_polygon(self):
        """Create lumped and vertical port."""
        # Done
        edb = Edb(
            edbpath=os.path.join(local_path, "example_models", test_subfolder, "edge_ports.aedb"),
            edbversion=desktop_version,
            restart_rpc_server=True,
        )
        poly_list = [poly for poly in edb.layout.primitives if poly.primitive_type.value == 2]
        port_poly = [poly for poly in poly_list if poly.edb_uid == 17][0]
        ref_poly = [poly for poly in poly_list if poly.edb_uid == 19][0]
        port_location = [-65e-3, -13e-3]
        ref_location = [-63e-3, -13e-3]
        assert edb.source_excitation.create_edge_port_on_polygon(
            polygon=port_poly,
            reference_polygon=ref_poly,
            terminal_point=port_location,
            reference_point=ref_location,
        )
        port_poly = [poly for poly in poly_list if poly.edb_uid == 23][0]
        ref_poly = [poly for poly in poly_list if poly.edb_uid == 22][0]
        port_location = [-65e-3, -10e-3]
        ref_location = [-65e-3, -10e-3]
        assert edb.source_excitation.create_edge_port_on_polygon(
            polygon=port_poly,
            reference_polygon=ref_poly,
            terminal_point=port_location,
            reference_point=ref_location,
        )
        port_poly = [poly for poly in poly_list if poly.edb_uid == 25][0]
        port_location = [-65e-3, -7e-3]
        assert edb.source_excitation.create_edge_port_on_polygon(
            polygon=port_poly, terminal_point=port_location, reference_layer="gnd"
        )
        sig = edb.modeler.create_trace([[0, 0], ["9mm", 0]], "sig2", "1mm", "SIG", "Flat", "Flat")
        from pyedb.grpc.edb_core.primitive.path import Path as PyEDBPath

        sig = PyEDBPath(edb, sig)
        # TODO check bug #435 can't get product properties skipping wave port for now
        assert sig.create_edge_port("pcb_port_1", "end", "Wave", None, 8, 8)
        assert sig.create_edge_port("pcb_port_2", "start", "gap")
        gap_port = edb.ports["pcb_port_2"]
        assert gap_port.component.is_null
        assert gap_port.magnitude == 0.0
        assert gap_port.phase == 0.0
        assert gap_port.impedance
        assert not gap_port.deembed
        gap_port.name = "gap_port"
        assert gap_port.name == "gap_port"
        assert gap_port.port_post_processing_prop.renormalization_impedance.value == 50
        gap_port.is_circuit_port = True
        assert gap_port.is_circuit_port
        edb.close()

    def test_edb_statistics(self, edb_examples):
        """Get statistics."""
        # Done
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
        assert edb_stats.occupying_ratio["1_Top"] == 0.30168200230804587
        assert edb_stats.occupying_ratio["Inner1(GND1)"] == 0.9374673366306919
        assert edb_stats.occupying_ratio["16_Bottom"] == 0.20492545425825437
        edb.close()

    def test_hfss_set_bounding_box_extent(self, edb_examples):
        """Configure HFSS with bounding box"""

        # obsolete check with config file 2.0

        # edb =  edb_examples.get_si_verse()
        # #initial_extent_info = edb.active_cell.GetHFSSExtentInfo()
        # assert edb.active_cell.hfss_extent_info.extent_type.name == "POLYGON"
        # config = SimulationConfiguration()
        # config.radiation_box = RadiationBoxType.BoundingBox
        # assert edb.hfss.configure_hfss_extents(config)
        # final_extent_info = edb.active_cell.GetHFSSExtentInfo()
        # #assert final_extent_info.ExtentType == edb.u utility.HFSSExtentInfoType.BoundingBox
        # edb.close()

        pass

    def test_create_rlc_component(self, edb_examples):
        """Create rlc components from pin"""
        # Done
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
        assert not setup.sweep_data[0].interpolation_data.enforce_causality
        sweeps = setup.sweep_data
        for sweep in sweeps:
            sweep.interpolation_data.enforce_causality = True
        setup.sweep_data = sweeps
        assert setup.sweep_data[0].interpolation_data.enforce_causality
        edb.close()

    def test_configure_hfss_analysis_setup(self, edb_examples):
        """Configure HFSS analysis setup."""
        # TODO adapt for config file 2.0
        edb = edb_examples.get_si_verse()
        # sim_setup = SimulationConfiguration()
        # sim_setup.mesh_sizefactor = 1.9
        # assert not sim_setup.do_lambda_refinement
        # edb.hfss.configure_hfss_analysis_setup(sim_setup)
        # mesh_size_factor = (
        #    list(edb.active_cell.SimulationSetups)[0]
        #    .GetSimSetupInfo()
        #    .get_SimulationSettings()
        #    .get_InitialMeshSettings()
        #    .get_MeshSizefactor()
        # )
        # assert mesh_size_factor == 1.9
        edb.close()

    def test_create_various_ports_0(self):
        """Create various ports."""
        edb = Edb(
            edbpath=os.path.join(local_path, "example_models", "edb_edge_ports.aedb"),
            edbversion=desktop_version,
            restart_rpc_server=True,
        )
        prim_1_id = [i.id for i in edb.modeler.primitives if i.net.name == "trace_2"][0]
        assert edb.source_excitation.create_edge_port_vertical(prim_1_id, ["-66mm", "-4mm"], "port_ver")

        prim_2_id = [i.id for i in edb.modeler.primitives if i.net.name == "trace_3"][0]
        assert edb.source_excitation.create_edge_port_horizontal(
            prim_1_id, ["-60mm", "-4mm"], prim_2_id, ["-59mm", "-4mm"], "port_hori", 30, "Lower"
        )
        assert edb.source_excitation.get_ports_number() == 2
        port_ver = edb.ports["port_ver"]
        assert not port_ver.is_null
        assert not port_ver.is_circuit_port
        assert port_ver.type.name == "EDGE"

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
        edb = Edb(
            edbpath=os.path.join(local_path, "example_models", "edb_edge_ports.aedb"),
            edbversion=desktop_version,
            restart_rpc_server=True,
        )
        kwargs = {
            "layer_name": "TOP",
            "net_name": "SIGP",
            "width": "0.1mm",
            "start_cap_style": "Flat",
            "end_cap_style": "Flat",
        }
        traces = [
            [["-40mm", "-10mm"], ["-30mm", "-10mm"]],
            [["-40mm", "-10.2mm"], ["-30mm", "-10.2mm"]],
            [["-40mm", "-10.4mm"], ["-30mm", "-10.4mm"]],
        ]
        edb_traces = []
        for p in traces:
            t = edb.modeler.create_trace(path_list=p, **kwargs)
            edb_traces.append(t)
        assert edb_traces[0].length == 0.02

        # TODO add wave port support
        # assert edb.source_excitation.create_wave_port(traces[0], trace_pathes[0][0], "wave_port")
        #
        # assert edb.source_excitation.create_differential_wave_port(
        #     traces[0],
        #     trace_pathes[0][0],
        #     traces[1],
        #     trace_pathes[1][0],
        #     horizontal_extent_factor=8,
        # )
        #
        # paths = [i[1] for i in trace_pathes]
        # assert edb.source_excitation.create_bundle_wave_port(traces, paths)
        # p = edb.excitations["wave_port"]
        # p.horizontal_extent_factor = 6
        # p.vertical_extent_factor = 5
        # p.pec_launch_width = "0.02mm"
        # p.radial_extent_factor = 1
        # assert p.horizontal_extent_factor == 6
        # assert p.vertical_extent_factor == 5
        # assert p.pec_launch_width == "0.02mm"
        # assert p.radial_extent_factor == 1
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

        setup1.settings.options.enhanced_low_frequency_accuracy = True
        assert setup1.settings.options.enhanced_low_frequency_accuracy
        setup1.settings.options.order_basis = setup1.settings.options.order_basis.FIRST_ORDER
        assert setup1.settings.options.order_basis.name == "FIRST_ORDER"
        setup1.settings.options.relative_residual = 0.0002
        assert setup1.settings.options.relative_residual == 0.0002
        setup1.settings.options.use_shell_elements = True
        assert setup1.settings.options.use_shell_elements

        setup1b = edbapp.setups["setup1"]
        assert not setup1.is_null
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
        # if float(edbapp.edbversion) >= 2024.1:
        #     via_settings.via_mesh_plating = True
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
        edbapp.close()

    def test_hfss_simulation_setup_mesh_operation(self, edb_examples):
        # Done
        edbapp = edb_examples.get_si_verse()
        setup = edbapp.create_hfss_setup(name="setup")
        mop = setup.add_length_mesh_operation(net_layer_list={"GND": ["1_Top", "16_Bottom"]}, name="m1")
        assert mop.enabled
        assert mop.net_layer_info[0] == ("GND", "1_Top", True)
        assert mop.net_layer_info[1] == ("GND", "16_Bottom", True)
        assert mop.name == "m1"
        assert mop.max_elements == "1000"
        assert mop.restrict_max_elements
        assert mop.restrict_max_length
        assert mop.max_length == "1mm"
        assert setup.mesh_operations
        assert edbapp.setups["setup"].mesh_operations

        mop = edbapp.setups["setup"].add_skin_depth_mesh_operation({"GND": ["1_Top", "16_Bottom"]})
        assert mop.net_layer_info[0] == ("GND", "1_Top", True)
        assert mop.net_layer_info[1] == ("GND", "16_Bottom", True)
        assert mop.max_elements == "1000"
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
        # Done
        edbapp = edb_examples.get_si_verse()
        setup1 = edbapp.create_hfss_setup("setup1")
        assert edbapp.setups["setup1"].name == "setup1"
        setup1.add_sweep(name="sw1", distribution="linear_count", start_freq="1MHz", stop_freq="100MHz", step=10)
        assert edbapp.setups["setup1"].sweep_data[0].name == "sw1"
        assert edbapp.setups["setup1"].sweep_data[0].start_f == "1MHz"
        assert edbapp.setups["setup1"].sweep_data[0].end_f == "100MHz"
        assert edbapp.setups["setup1"].sweep_data[0].step == "10"
        setup1.add_sweep(name="sw2", distribution="linear", start_freq="210MHz", stop_freq="300MHz", step="10MHz")
        assert edbapp.setups["setup1"].sweep_data[0].name == "sw2"
        setup1.add_sweep(name="sw3", distribution="log_scale", start_freq="1GHz", stop_freq="10GHz", step=10)
        assert edbapp.setups["setup1"].sweep_data[0].name == "sw3"
        setup1.sweep_data[2].use_q3d_for_dc = True
        edbapp.close()

    def test_siwave_dc_simulation_setup(self, edb_examples):
        """Create a dc simulation setup and evaluate its properties."""
        # TODO check with config file 2.0
        edb = edb_examples.get_si_verse()
        setup1 = edb.create_siwave_dc_setup("DC1")
        setup1.dc_settings.restore_default()
        setup1.dc_advanced_settings.restore_default()

        settings = self.edbapp.setups["DC1"].get_configurations()
        for k, v in setup1.dc_settings.defaults.items():
            # NOTE: On Linux it seems that there is a strange behavior with use_dc_custom_settings
            # See https://github.com/ansys/pyedb/pull/791#issuecomment-2358036067
            if k in ["compute_inductance", "plot_jv", "use_dc_custom_settings"]:
                continue
            assert settings["dc_settings"][k] == v

        for k, v in setup1.dc_advanced_settings.defaults.items():
            assert settings["dc_advanced_settings"][k] == v

        for p in [0, 1, 2]:
            setup1.set_dc_slider(p)
            settings = edb.setups["DC1"].get_configurations()
            for k, v in setup1.dc_settings.dc_defaults.items():
                assert settings["dc_settings"][k] == v[p]

            for k, v in setup1.dc_advanced_settings.dc_defaults.items():
                assert settings["dc_advanced_settings"][k] == v[p]
        edb.close()

    def test_siwave_ac_simulation_setup(self, edb_examples):
        """Create an ac simulation setup and evaluate its properties."""
        # TODO check with config file 2.0
        # edb = edb_examples.get_si_verse()
        # setup1 = edb.create_siwave_syz_setup("AC1")
        # assert setup1.name == "AC1"
        # assert setup1.enabled
        # setup1.advanced_settings.restore_default()
        #
        # settings = edb.setups["AC1"].get_configurations()
        # for k, v in setup1.advanced_settings.defaults.items():
        #     if k in ["min_plane_area_to_mesh"]:
        #         continue
        #     assert settings["advanced_settings"][k] == v
        #
        # for p in [0, 1, 2]:
        #     setup1.set_si_slider(p)
        #     settings = edb.setups["AC1"].get_configurations()
        #     for k, v in setup1.advanced_settings.si_defaults.items():
        #         assert settings["advanced_settings"][k] == v[p]
        #
        # for p in [0, 1, 2]:
        #     setup1.pi_slider_position = p
        #     settings = edb.setups["AC1"].get_configurations()
        #     for k, v in setup1.advanced_settings.pi_defaults.items():
        #         assert settings["advanced_settings"][k] == v[p]
        #
        # sweep = setup1.add_sweep(
        #     name="sweep1",
        #     frequency_set=[
        #         ["linear count", "0", "1kHz", 1],
        #         ["log scale", "1kHz", "0.1GHz", 10],
        #         ["linear scale", "0.1GHz", "10GHz", "0.1GHz"],
        #     ],
        # )
        # assert 0 in sweep.frequencies
        # assert not sweep.adaptive_sampling
        # assert not sweep.adv_dc_extrapolation
        # assert sweep.auto_s_mat_only_solve
        # assert not sweep.enforce_causality
        # assert not sweep.enforce_dc_and_causality
        # assert sweep.enforce_passivity
        # assert sweep.freq_sweep_type == "kInterpolatingSweep"
        # assert sweep.interpolation_use_full_basis
        # assert sweep.interpolation_use_port_impedance
        # assert sweep.interpolation_use_prop_const
        # assert sweep.max_solutions == 250
        # assert sweep.min_freq_s_mat_only_solve == "1MHz"
        # assert not sweep.min_solved_freq
        # assert sweep.passivity_tolerance == 0.0001
        # assert sweep.relative_s_error == 0.005
        # assert not sweep.save_fields
        # assert not sweep.save_rad_fields_only
        # assert not sweep.use_q3d_for_dc
        #
        # sweep.adaptive_sampling = True
        # sweep.adv_dc_extrapolation = True
        # sweep.compute_dc_point = True
        # sweep.auto_s_mat_only_solve = False
        # sweep.enforce_causality = True
        # sweep.enforce_dc_and_causality = True
        # sweep.enforce_passivity = False
        # sweep.freq_sweep_type = "kDiscreteSweep"
        # sweep.interpolation_use_full_basis = False
        # sweep.interpolation_use_port_impedance = False
        # sweep.interpolation_use_prop_const = False
        # sweep.max_solutions = 200
        # sweep.min_freq_s_mat_only_solve = "2MHz"
        # sweep.min_solved_freq = "1Hz"
        # sweep.passivity_tolerance = 0.0002
        # sweep.relative_s_error = 0.004
        # sweep.save_fields = True
        # sweep.save_rad_fields_only = True
        # sweep.use_q3d_for_dc = True
        #
        # assert sweep.adaptive_sampling
        # assert sweep.adv_dc_extrapolation
        # assert sweep.compute_dc_point
        # assert not sweep.auto_s_mat_only_solve
        # assert sweep.enforce_causality
        # assert sweep.enforce_dc_and_causality
        # assert not sweep.enforce_passivity
        # assert sweep.freq_sweep_type == "kDiscreteSweep"
        # assert not sweep.interpolation_use_full_basis
        # assert not sweep.interpolation_use_port_impedance
        # assert not sweep.interpolation_use_prop_const
        # assert sweep.max_solutions == 200
        # assert sweep.min_freq_s_mat_only_solve == "2MHz"
        # assert sweep.min_solved_freq == "1Hz"
        # assert sweep.passivity_tolerance == 0.0002
        # assert sweep.relative_s_error == 0.004
        # assert sweep.save_fields
        # assert sweep.save_rad_fields_only
        # assert sweep.use_q3d_for_dc
        # edb.close()
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
        padstack_instance_terminals = [
            term for term in list(edbapp.terminals.values()) if term.type.name == "PADSTACK_INST"
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
        # TODO cast source type and remove EdbValue
        source_path = os.path.join(local_path, "example_models", test_subfolder, "test_sources.aedb")
        target_path = os.path.join(self.local_scratch.path, "test_134_source_setter.aedb")
        self.local_scratch.copyfolder(source_path, target_path)
        edbapp = Edb(target_path, edbversion=desktop_version, restart_rpc_server=True)
        sources = list(edbapp.siwave.sources.values())
        sources[0].magnitude = 1.45
        assert sources[0].magnitude.value == 1.45
        sources[1].magnitude = 1.45
        assert sources[1].magnitude.value == 1.45
        edbapp.close()

    def test_delete_pingroup(self):
        """Delete siwave pin groups."""
        # Done
        source_path = os.path.join(local_path, "example_models", test_subfolder, "test_pin_group.aedb")
        target_path = os.path.join(self.local_scratch.path, "test_135_pin_group.aedb")
        self.local_scratch.copyfolder(source_path, target_path)
        edbapp = Edb(target_path, edbversion=desktop_version, restart_rpc_server=True)
        for _, pingroup in edbapp.siwave.pin_groups.items():
            pingroup.delete()
        assert not edbapp.siwave.pin_groups
        edbapp.close()

    # def test_design_options(self):
    #     """Evaluate Edb design settings and options."""
    #     self.edbapp.design_options.suppress_pads = False
    #     assert not self.edbapp.design_options.suppress_pads
    #     self.edbapp.design_options.antipads_always_on = True
    #     assert self.edbapp.design_options.antipads_always_on

    # def test_pins(self):
    #     """Evaluate the pins."""
    #     assert len(self.edbapp.padstacks.pins) > 0

    def test_create_padstack_instance(self, edb_examples):
        """Create padstack instances."""
        # TODO Check material init
        # edb = Edb(edbversion=desktop_version, restart_rpc_server=True)
        # edb.stackup.add_layer(layer_name="1_Top", fillMaterial="air", thickness="30um")
        # edb.stackup.add_layer(layer_name="contact", fillMaterial="air", thickness="100um", base_layer="1_Top")
        #
        # assert edb.padstacks.create(
        #     pad_shape="Rectangle",
        #     padstackname="pad",
        #     x_size="350um",
        #     y_size="500um",
        #     holediam=0,
        # )
        # pad_instance1 = edb.padstacks.place(position=["-0.65mm", "-0.665mm"], definition_name="pad")
        # assert pad_instance1
        # pad_instance1.start_layer = "1_Top"
        # pad_instance1.stop_layer = "1_Top"
        # assert pad_instance1.start_layer == "1_Top"
        # assert pad_instance1.stop_layer == "1_Top"
        #
        # assert edb.padstacks.create(pad_shape="Circle", padstackname="pad2", paddiam="350um", holediam="15um")
        # pad_instance2 = edb.padstacks.place(position=["-0.65mm", "-0.665mm"], definition_name="pad2")
        # assert pad_instance2
        # pad_instance2.start_layer = "1_Top"
        # pad_instance2.stop_layer = "1_Top"
        # assert pad_instance2.start_layer == "1_Top"
        # assert pad_instance2.stop_layer == "1_Top"
        #
        # assert edb.padstacks.create(
        #     pad_shape="Circle",
        #     padstackname="test2",
        #     paddiam="400um",
        #     holediam="200um",
        #     antipad_shape="Rectangle",
        #     anti_pad_x_size="700um",
        #     anti_pad_y_size="800um",
        #     start_layer="1_Top",
        #     stop_layer="1_Top",
        # )
        #
        # pad_instance3 = edb.padstacks.place(position=["-1.65mm", "-1.665mm"], definition_name="test2")
        # assert pad_instance3.start_layer == "1_Top"
        # assert pad_instance3.stop_layer == "1_Top"
        # pad_instance3.dcir_equipotential_region = True
        # assert pad_instance3.dcir_equipotential_region
        # pad_instance3.dcir_equipotential_region = False
        # assert not pad_instance3.dcir_equipotential_region
        #
        # trace = edb.modeler.create_trace([[0, 0], [0, 10e-3]], "1_Top", "0.1mm", "trace_with_via_fence")
        # edb.padstacks.create("via_0")
        # trace.create_via_fence("1mm", "1mm", "via_0")
        #
        # edb.close()
        pass

    def test_stackup_properties(self):
        """Evaluate stackup properties."""
        # TODO check material init
        edb = Edb(edbversion=desktop_version, restart_rpc_server=True)
        edb.stackup.add_layer(layer_name="gnd", fillMaterial="air", thickness="10um")
        edb.stackup.add_layer(layer_name="diel1", fillMaterial="air", thickness="200um", base_layer="gnd")
        edb.stackup.add_layer(layer_name="sig1", fillMaterial="air", thickness="10um", base_layer="diel1")
        edb.stackup.add_layer(layer_name="diel2", fillMaterial="air", thickness="200um", base_layer="sig1")
        edb.stackup.add_layer(layer_name="sig3", fillMaterial="air", thickness="10um", base_layer="diel2")
        assert edb.stackup.thickness == 0.00043
        assert edb.stackup.num_layers == 5
        edb.close()
        pass

    def test_hfss_extent_info(self):
        """HFSS extent information."""

        # TODO check config file 2.0

        # from pyedb.grpc.edb_core.primitive.primitive import Primitive
        #
        # config = {
        #     "air_box_horizontal_extent_enabled": False,
        #     "air_box_horizontal_extent": 0.01,
        #     "air_box_positive_vertical_extent": 0.3,
        #     "air_box_positive_vertical_extent_enabled": False,
        #     "air_box_negative_vertical_extent": 0.1,
        #     "air_box_negative_vertical_extent_enabled": False,
        #     "base_polygon": self.edbapp.modeler.polygons[0],
        #     "dielectric_base_polygon": self.edbapp.modeler.polygons[1],
        #     "dielectric_extent_size": 0.1,
        #     "dielectric_extent_size_enabled": False,
        #     "dielectric_extent_type": "conforming",
        #     "extent_type": "conforming",
        #     "honor_user_dielectric": False,
        #     "is_pml_visible": False,
        #     "open_region_type": "pml",
        #     "operating_freq": "2GHz",
        #     "radiation_level": 1,
        #     "sync_air_box_vertical_extent": False,
        #     "use_open_region": False,
        #     "use_xy_data_extent_for_vertical_expansion": False,
        #     "truncate_air_box_at_ground": True,
        # }
        # hfss_extent_info = self.edbapp.hfss.hfss_extent_info
        # hfss_extent_info.load_config(config)
        # exported_config = hfss_extent_info.export_config()
        # for i, j in exported_config.items():
        #     if not i in config:
        #         continue
        #     if isinstance(j, Primitive):
        #         assert j.id == config[i].id
        #     elif isinstance(j, EdbValue):
        #         assert j.tofloat == hfss_extent_info._get_edb_value(config[i]).ToDouble()
        #     else:
        #         assert j == config[i]
        pass

    def test_import_gds_from_tech(self):
        """Use techfile."""
        from pyedb.dotnet.edb_core.edb_data.control_file import ControlFile

        c_file_in = os.path.join(
            local_path, "example_models", "cad", "GDS", "sky130_fictitious_dtc_example_control_no_map.xml"
        )
        c_map = os.path.join(local_path, "example_models", "cad", "GDS", "dummy_layermap.map")
        gds_in = os.path.join(local_path, "example_models", "cad", "GDS", "sky130_fictitious_dtc_example.gds")
        gds_out = os.path.join(self.local_scratch.path, "sky130_fictitious_dtc_example.gds")
        self.local_scratch.copyfile(gds_in, gds_out)

        c = ControlFile(c_file_in, layer_map=c_map)
        setup = c.setups.add_setup("Setup1", "1GHz")
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

        # TODO check why GDS import fails with components init.

        # edb = Edb(edbpath=gds_out, edbversion=desktop_version,
        #           technology_file=os.path.join(self.local_scratch.path, "test_138.xml"), restart_rpc_server=True
        # )
        #
        # assert edb
        # assert "P1" in edb.excitations
        # assert "Setup1" in edb.setups
        # assert "B1" in edb.components.instances
        # edb.close()

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
        assert edb.source_version == ""
        edb.source_version = "2022.2"
        assert edb.source == ""
        assert isinstance(edb.version, tuple)
        assert isinstance(edb.footprint_cells, list)

    def test_backdrill_via_with_offset(self):
        """Set backdrill from top."""

        #  TODO when material init is fixed
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
        padstack_instance.set_backdrill_top(drill_depth="signal1", drill_diameter="200um", offset="100um")
        assert len(padstack_instance.backdrill_top) == 3
        assert padstack_instance.backdrill_top[0] == "signal1"
        assert padstack_instance.backdrill_top[1] == "200um"
        assert padstack_instance.backdrill_top[2] == "100um"
        padstack_instance2 = edb.padstacks.place(position=[0.5, 0.5], net_name="test", definition_name="test1")
        padstack_instance2.set_backdrill_bottom(drill_depth="signal1", drill_diameter="200um", offset="100um")
        assert len(padstack_instance2.backdrill_bottom) == 3
        assert padstack_instance2.backdrill_bottom[0] == "signal1"
        assert padstack_instance2.backdrill_bottom[1] == "200um"
        assert padstack_instance2.backdrill_bottom[2] == "100um"
        edb.close()

    def test_add_layer_api_with_control_file(self):
        """Add new layers with control file."""
        from pyedb.grpc.edb_core.control_file import ControlFile

        # TODO when material init fixed

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
        # Done
        src = os.path.join(local_path, "example_models", test_subfolder, "edb_test_82.dxf")
        dxf_path = self.local_scratch.copyfile(src)
        edb3 = Edb(dxf_path, edbversion=desktop_version, restart_rpc_server=True)
        assert len(edb3.modeler.polygons) == 1
        assert edb3.modeler.polygons[0].polygon_data.points == [
            (0.0, 0.0),
            (0.0, 0.0012),
            (-0.0008, 0.0012),
            (-0.0008, 0.0),
        ]
        edb3.close()
        del edb3

    @pytest.mark.skipif(is_linux, reason="Not supported in IPY")
    def test_solve_siwave(self):
        """Solve EDB with Siwave."""
        # DOne
        target_path = os.path.join(local_path, "example_models", "T40", "ANSYS-HSD_V1_DCIR.aedb")
        out_edb = os.path.join(self.local_scratch.path, "to_be_solved.aedb")
        self.local_scratch.copyfolder(target_path, out_edb)
        edbapp = Edb(out_edb, edbversion=desktop_version, restart_rpc_server=True)
        edbapp.siwave.create_exec_file(add_dc=True)
        out = edbapp.solve_siwave()
        assert os.path.exists(out)
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
        assert extent[0] == [0.011025799607142596, 0.04451508809926884]
        assert extent[10] == [0.02214231174553801, 0.02851039223066996]
        assert extent[20] == [0.06722930402216426, 0.02605468368384399]
        assert extent[30] == [0.06793706871543964, 0.02961898967909681]
        assert extent[40] == [0.0655032742298304, 0.03147893183305721]
        assert extent[50] == [0.01143465157862367, 0.046365530038092975]
        edbapp.close_edb()

    def test_move_and_edit_polygons(self):
        """Move a polygon."""
        # TODO wait to fix loading syslib material
        # target_path = os.path.join(self.local_scratch.path, "test_move_edit_polygons", "test.aedb")
        # edbapp = Edb(target_path, edbversion=desktop_version, restart_rpc_server=True)
        #
        # edbapp.stackup.add_layer("GND")
        # edbapp.stackup.add_layer("Diel", "GND", layer_type="dielectric", thickness="0.1mm", material="FR4_epoxy")
        # edbapp.stackup.add_layer("TOP", "Diel", thickness="0.05mm")
        # points = [[0.0, -1e-3], [0.0, -10e-3], [100e-3, -10e-3], [100e-3, -1e-3], [0.0, -1e-3]]
        # polygon = edbapp.modeler.create_polygon(points, "TOP")
        # assert polygon.center == [0.05, -0.0055]
        # assert polygon.move(["1mm", 1e-3])
        # assert round(polygon.center[0], 6) == 0.051
        # assert round(polygon.center[1], 6) == -0.0045
        #
        # assert polygon.rotate(angle=45)
        # expected_bbox = [0.012462680425333156, -0.043037319574666846, 0.08953731957466685, 0.034037319574666845]
        # assert all(isclose(x, y, rel_tol=1e-15) for x, y in zip(expected_bbox, polygon.bbox))
        #
        # assert polygon.rotate(angle=34, center=[0, 0])
        # expected_bbox = [0.03083951217158376, -0.025151830651067256, 0.05875505636026722, 0.07472816865208806]
        # assert all(isclose(x, y, rel_tol=1e-15) for x, y in zip(expected_bbox, polygon.bbox))
        #
        # assert polygon.scale(factor=1.5)
        # expected_bbox = [0.0238606261244129, -0.05012183047685609, 0.06573394240743807, 0.09969816847787688]
        # assert all(isclose(x, y, rel_tol=1e-15) for x, y in zip(expected_bbox, polygon.bbox))
        #
        # assert polygon.scale(factor=-0.5, center=[0, 0])
        # expected_bbox = [-0.032866971203719036, -0.04984908423893844, -0.01193031306220645, 0.025060915238428044]
        # assert all(isclose(x, y, rel_tol=1e-15) for x, y in zip(expected_bbox, polygon.bbox))
        #
        # assert polygon.move_layer("GND")
        # assert len(edbapp.modeler.polygons) == 1
        # assert edbapp.modeler.polygons[0].layer_name == "GND"
        pass

    def test_multizone(self, edb_examples):
        # TODO check bug #447

        # edbapp = edb_examples.get_multizone_pcb()
        # common_reference_net = "gnd"
        # edb_zones = edbapp.copy_zones()
        # assert edb_zones
        # defined_ports, project_connexions = edbapp.cutout_multizone_layout(edb_zones, common_reference_net)
        #
        # assert defined_ports
        # assert project_connexions
        # edbapp.close_edb()
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
        # Done
        edbapp = edb_examples.get_si_verse()
        setup = edbapp.create_siwave_dc_setup()
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
        edbapp.close()

    def test_arbitrary_wave_ports(self):
        # TODO check bug #448 PolygonData.scale failing
        example_folder = os.path.join(local_path, "example_models", test_subfolder)
        source_path_edb = os.path.join(example_folder, "example_arbitrary_wave_ports.aedb")
        target_path_edb = os.path.join(self.local_scratch.path, "test_wave_ports", "test.aedb")
        self.local_scratch.copyfolder(source_path_edb, target_path_edb)
        edbapp = Edb(target_path_edb, desktop_version, restart_rpc_server=True)
        assert edbapp.create_model_for_arbitrary_wave_ports(
            temp_directory=self.local_scratch.path,
            output_edb="wave_ports.aedb",
            mounting_side="top",
        )
        edb_model = os.path.join(self.local_scratch.path, "wave_ports.aedb")
        assert os.path.isdir(edb_model)
        edbapp.close()

    def test_bondwire(self, edb_examples):
        # TODO check bug #449  and # 450 change trajectory and start end elevation.
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
        assert bondwire_1.type == "jedec4"
        bondwire_1.cross_section_type = "round"
        assert bondwire_1.cross_section_type == "round"
        bondwire_1.cross_section_height = "0.1mm"
        assert bondwire_1.cross_section_height == 0.0001
        bondwire_1.set_definition_name("J4_LH10")
        assert bondwire_1.get_definition_name() == "J4_LH10"
        # bondwire_1.trajectory = [1, 0.1, 0.2, 0.3]
        # assert bondwire_1.trajectory == [1, 0.1, 0.2, 0.3]
        bondwire_1.width = "0.2mm"
        assert bondwire_1.width == 0.0002
        bondwire_1.start_elevation = "16_Bottom"
        # bondwire_1.end_elevation = "16_Bottom"
        # assert len(edbapp.layout.bondwires) == 1
        edbapp.close()

    def test_voltage_regulator(self, edb_examples):
        # TODO is not working with EDB NET not implemented yet in Grpc
        # edbapp = edb_examples.get_si_verse()
        # positive_sensor_pin = edbapp.components["U1"].pins["A2"]
        # negative_sensor_pin = edbapp.components["U1"].pins["A3"]
        # vrm = edbapp.siwave.create_vrm_module(
        #     name="test",
        #     positive_sensor_pin=positive_sensor_pin,
        #     negative_sensor_pin=negative_sensor_pin,
        #     voltage="1.5V",
        #     load_regulation_current="0.5A",
        #     load_regulation_percent=0.2,
        # )
        # assert vrm.component
        # assert vrm.component.refdes == "U1"
        # assert vrm.negative_remote_sense_pin
        # assert vrm.negative_remote_sense_pin.name == "U1-A3"
        # assert vrm.positive_remote_sense_pin
        # assert vrm.positive_remote_sense_pin.name == "U1-A2"
        # assert vrm.voltage == 1.5
        # assert vrm.is_active
        # assert not vrm.is_null
        # assert vrm.id
        # assert edbapp.voltage_regulator_modules
        # assert "test" in edbapp.voltage_regulator_modules
        # edbapp.close()
        pass

    def test_workflow(self, edb_examples):
        # TODO check with config file 2.0

        # edbapp = edb_examples.get_si_verse()
        # path_bom = Path(edb_examples.test_folder) / "bom.csv"
        # edbapp.workflow.export_bill_of_materials(path_bom)
        # assert path_bom.exists()
        # edbapp.close()
        pass

    def test_create_port_ob_component_no_ref_pins_in_component(self, edb_examples):
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
        edb = Edb(zip_path, edbversion=desktop_version, restart_rpc_server=True)
        assert edb.nets
        assert edb.components
        edb.close()
