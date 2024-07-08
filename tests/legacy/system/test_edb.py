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
from pathlib import Path

import pytest

from pyedb.dotnet.edb import Edb
from pyedb.dotnet.edb_core.edb_data.edbvalue import EdbValue
from pyedb.dotnet.edb_core.edb_data.simulation_configuration import (
    SimulationConfiguration,
)
from pyedb.generic.constants import RadiationBoxType, SolverType, SourceType
from pyedb.generic.general_methods import is_linux
from tests.conftest import desktop_version, local_path
from tests.legacy.system.conftest import test_subfolder

pytestmark = [pytest.mark.system, pytest.mark.legacy]


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, legacy_edb_app, local_scratch, target_path, target_path2, target_path4):
        self.edbapp = legacy_edb_app
        self.local_scratch = local_scratch
        self.target_path = target_path
        self.target_path2 = target_path2
        self.target_path4 = target_path4

    def test_hfss_create_coax_port_on_component_from_hfss(self):
        """Create a coaxial port on a component from its pin."""
        assert self.edbapp.hfss.create_coax_port_on_component("U1", "DDR4_DQS0_P")
        assert self.edbapp.hfss.create_coax_port_on_component("U1", ["DDR4_DQS0_P", "DDR4_DQS0_N"])

    def test_layout_bounding_box(self):
        """Evaluate layout bounding box"""
        assert len(self.edbapp.get_bounding_box()) == 2
        assert self.edbapp.get_bounding_box() == [[-0.01426004895, -0.00455000106], [0.15010507444, 0.08000000002]]

    def test_siwave_create_circuit_port_on_net(self):
        """Create a circuit port on a net."""
        initial_len = len(self.edbapp.padstacks.pingroups)
        assert self.edbapp.siwave.create_circuit_port_on_net("U1", "1V0", "U1", "GND", 50, "test") == "test"
        p2 = self.edbapp.siwave.create_circuit_port_on_net("U1", "PLL_1V8", "U1", "GND", 50, "test")
        assert p2 != "test" and "test" in p2
        pins = self.edbapp.components.get_pin_from_component("U1")
        p3 = self.edbapp.siwave.create_circuit_port_on_pin(pins[200], pins[0], 45)
        assert p3 != ""
        p4 = self.edbapp.hfss.create_circuit_port_on_net("U1", "USB3_D_P")
        assert len(self.edbapp.padstacks.pingroups) == initial_len + 6
        assert "GND" in p4 and "USB3_D_P" in p4

        # TODO: Moves this piece of code in another place
        assert "test" in self.edbapp.terminals
        assert self.edbapp.siwave.create_pin_group_on_net("U1", "1V0", "PG_V1P0_S0")
        assert self.edbapp.siwave.create_pin_group_on_net("U1", "GND", "U1_GND")
        assert self.edbapp.siwave.create_circuit_port_on_pin_group(
            "PG_V1P0_S0", "U1_GND", impedance=50, name="test_port"
        )
        self.edbapp.excitations["test_port"].name = "test_rename"
        assert any(port for port in list(self.edbapp.excitations) if port == "test_rename")

    def test_siwave_create_voltage_source(self):
        """Create a voltage source."""
        assert len(self.edbapp.sources) == 0
        assert "Vsource_" in self.edbapp.siwave.create_voltage_source_on_net("U1", "USB3_D_P", "U1", "GND", 3.3, 0)
        assert len(self.edbapp.sources) == 1
        assert list(self.edbapp.sources.values())[0].magnitude == 3.3

        pins = self.edbapp.components.get_pin_from_component("U1")
        assert "VSource_" in self.edbapp.siwave.create_voltage_source_on_pin(pins[300], pins[10], 3.3, 0)
        assert len(self.edbapp.sources) == 2
        assert len(self.edbapp.probes) == 0
        list(self.edbapp.sources.values())[0].phase = 1
        assert list(self.edbapp.sources.values())[0].phase == 1
        u6 = self.edbapp.components["U6"]
        voltage_source = self.edbapp.create_voltage_source(
            u6.pins["F2"].get_terminal(create_new_terminal=True), u6.pins["F1"].get_terminal(create_new_terminal=True)
        )
        assert not voltage_source.is_null

    def test_siwave_create_current_source(self):
        """Create a current source."""
        assert self.edbapp.siwave.create_current_source_on_net("U1", "USB3_D_N", "U1", "GND", 0.1, 0) != ""
        pins = self.edbapp.components.get_pin_from_component("U1")
        assert "I22" == self.edbapp.siwave.create_current_source_on_pin(pins[301], pins[10], 0.1, 0, "I22")

        assert self.edbapp.siwave.create_pin_group_on_net(reference_designator="U1", net_name="GND", group_name="gnd")
        self.edbapp.siwave.create_pin_group(reference_designator="U1", pin_numbers=["A27", "A28"], group_name="vrm_pos")
        self.edbapp.siwave.create_current_source_on_pin_group(
            pos_pin_group_name="vrm_pos", neg_pin_group_name="gnd", name="vrm_current_source"
        )

        self.edbapp.siwave.create_pin_group(
            reference_designator="U1", pin_numbers=["R23", "P23"], group_name="sink_pos"
        )
        self.edbapp.siwave.create_pin_group_on_net(reference_designator="U1", net_name="GND", group_name="gnd2")

        # TODO: Moves this piece of code in another place
        assert self.edbapp.siwave.create_voltage_source_on_pin_group("sink_pos", "gnd2", name="vrm_voltage_source")
        self.edbapp.siwave.create_pin_group(reference_designator="U1", pin_numbers=["A27", "A28"], group_name="vp_pos")
        assert self.edbapp.siwave.create_pin_group_on_net(
            reference_designator="U1", net_name="GND", group_name="vp_neg"
        )
        assert self.edbapp.siwave.pin_groups["vp_pos"]
        assert self.edbapp.siwave.pin_groups["vp_pos"].pins
        assert self.edbapp.siwave.create_voltage_probe_on_pin_group("vprobe", "vp_pos", "vp_neg")
        assert self.edbapp.probes["vprobe"]
        self.edbapp.siwave.place_voltage_probe(
            "vprobe_2", "1V0", ["112mm", "24mm"], "1_Top", "GND", ["112mm", "27mm"], "Inner1(GND1)"
        )
        vprobe_2 = self.edbapp.probes["vprobe_2"]
        ref_term = vprobe_2.ref_terminal
        assert isinstance(ref_term.location, list)
        ref_term.location = [0, 0]
        assert ref_term.layer
        ref_term.layer = "1_Top"
        u6 = self.edbapp.components["U6"]
        self.edbapp.create_current_source(
            u6.pins["H8"].get_terminal(create_new_terminal=True), u6.pins["G9"].get_terminal(create_new_terminal=True)
        )

    def test_siwave_create_dc_terminal(self):
        """Create a DC terminal."""
        assert self.edbapp.siwave.create_dc_terminal("U1", "DDR4_DQ40", "dc_terminal1") == "dc_terminal1"

    def test_siwave_create_resistors_on_pin(self):
        """Create a resistor on pin."""
        pins = self.edbapp.components.get_pin_from_component("U1")
        assert "RST4000" == self.edbapp.siwave.create_resistor_on_pin(pins[302], pins[10], 40, "RST4000")

    def test_siwave_add_syz_analsyis(self):
        """Add a sywave AC analysis."""
        assert self.edbapp.siwave.add_siwave_syz_analysis(start_freq="=GHz", stop_freq="10GHz", step_freq="10MHz")

    def test_siwave_add_dc_analysis(self):
        """Add a sywave DC analysis."""
        assert self.edbapp.siwave.add_siwave_dc_analysis(name="Test_dc")

    def test_hfss_mesh_operations(self):
        """Retrieve the trace width for traces with ports."""
        self.edbapp.components.create_port_on_component(
            "U1",
            ["VDD_DDR"],
            reference_net="GND",
            port_type=SourceType.CircPort,
        )
        mesh_ops = self.edbapp.hfss.get_trace_width_for_traces_with_ports()
        assert len(mesh_ops) > 0

    def test_add_variables(self):
        """Add design and project variables."""
        result, var_server = self.edbapp.add_design_variable("my_variable", "1mm")
        assert result
        assert var_server
        result, var_server = self.edbapp.add_design_variable("my_variable", "1mm")
        assert not result
        assert self.edbapp.modeler.parametrize_trace_width("A0_N")
        assert self.edbapp.modeler.parametrize_trace_width("A0_N_R")
        result, var_server = self.edbapp.add_design_variable("my_parameter", "2mm", True)
        assert result
        assert var_server.IsVariableParameter("my_parameter")
        result, var_server = self.edbapp.add_design_variable("my_parameter", "2mm", True)
        assert not result
        result, var_server = self.edbapp.add_project_variable("$my_project_variable", "3mm")
        assert result
        assert var_server
        result, var_server = self.edbapp.add_project_variable("$my_project_variable", "3mm")
        assert not result

    def test_save_edb_as(self):
        """Save edb as some file."""
        assert self.edbapp.save_edb_as(os.path.join(self.local_scratch.path, "Gelileo_new.aedb"))
        assert os.path.exists(os.path.join(self.local_scratch.path, "Gelileo_new.aedb", "edb.def"))

    def test_create_custom_cutout_0(self):
        """Create custom cutout 0."""
        source_path = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1_cut.aedb")
        target_path = os.path.join(self.local_scratch.path, "ANSYS-HSD_V1_cutou1.aedb")
        self.local_scratch.copyfolder(source_path, target_path)
        edbapp = Edb(target_path, edbversion=desktop_version)
        output = os.path.join(self.local_scratch.path, "cutout.aedb")
        assert edbapp.cutout(
            ["DDR4_DQS0_P", "DDR4_DQS0_N"],
            ["GND"],
            output_aedb_path=output,
            open_cutout_at_end=False,
            use_pyaedt_extent_computing=True,
            use_pyaedt_cutout=False,
        )
        assert edbapp.cutout(
            ["DDR4_DQS0_P", "DDR4_DQS0_N"],
            ["GND"],
            output_aedb_path=output,
            open_cutout_at_end=False,
            remove_single_pin_components=True,
            use_pyaedt_cutout=False,
        )
        assert os.path.exists(os.path.join(output, "edb.def"))
        bounding = edbapp.get_bounding_box()
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
        output = os.path.join(self.local_scratch.path, "cutout3.aedb")

        assert edbapp.cutout(
            custom_extent=points,
            signal_list=["GND", "1V0"],
            output_aedb_path=output,
            open_cutout_at_end=False,
            include_partial_instances=True,
            use_pyaedt_cutout=False,
        )
        assert os.path.exists(os.path.join(output, "edb.def"))
        edbapp.close()

    def test_create_custom_cutout_1(self):
        """Create custom cutout 1."""
        source_path = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1.aedb")
        target_path = os.path.join(self.local_scratch.path, "ANSYS-HSD_V1_cutou2.aedb")
        self.local_scratch.copyfolder(source_path, target_path)
        edbapp = Edb(target_path, edbversion=desktop_version)
        spice_path = os.path.join(local_path, "example_models", test_subfolder, "GRM32_DC0V_25degC.mod")
        edbapp.components.instances["R8"].assign_spice_model(spice_path)
        edbapp.nets.nets
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
        assert isinstance(edbapp.nets.find_and_fix_disjoint_nets("GND", order_by_area=True), list)
        assert isinstance(edbapp.nets.find_and_fix_disjoint_nets("GND", keep_only_main_net=True), list)
        assert isinstance(edbapp.nets.find_and_fix_disjoint_nets("GND", clean_disjoints_less_than=0.005), list)
        assert edbapp.layout_validation.fix_self_intersections("PGND")

        edbapp.close()

    def test_create_custom_cutout_2(self):
        """Create custom cutout 2."""
        source_path = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1.aedb")
        target_path = os.path.join(self.local_scratch.path, "ANSYS-HSD_V1_cutou3.aedb")
        self.local_scratch.copyfolder(source_path, target_path)

        edbapp = Edb(target_path, edbversion=desktop_version)
        bounding = edbapp.get_bounding_box()
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

    def test_create_custom_cutout_3(self):
        """Create custom cutout 3."""
        source_path = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1.aedb")
        target_path = os.path.join(self.local_scratch.path, "ANSYS-HSD_V1_cutou5.aedb")
        self.local_scratch.copyfolder(source_path, target_path)

        edbapp = Edb(target_path, edbversion=desktop_version)
        edbapp.components.create_port_on_component(
            "U1",
            ["5V"],
            reference_net="GND",
            port_type=SourceType.CircPort,
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
        assert edbapp.are_port_reference_terminals_connected(common_reference="GND")

        edbapp.close()

    def test_create_custom_cutout_4(self):
        """Create custom cutout 4."""
        source_path = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1_cut.aedb")
        target_path = os.path.join(self.local_scratch.path, "ANSYS-HSD_V1_cut_smart.aedb")
        self.local_scratch.copyfolder(source_path, target_path)

        edbapp = Edb(target_path, edbversion=desktop_version)

        assert edbapp.cutout(
            signal_list=["DDR4_DQS0_P", "DDR4_DQS0_N"],
            reference_list=["GND"],
            number_of_threads=4,
            extent_type="ConvexHull",
            use_pyaedt_extent_computing=True,
            check_terminals=True,
            expansion_factor=4,
        )
        edbapp.close()
        source_path = os.path.join(local_path, "example_models", test_subfolder, "MicrostripSpliGnd.aedb")
        target_path = os.path.join(self.local_scratch.path, "MicrostripSpliGnd.aedb")
        self.local_scratch.copyfolder(source_path, target_path)

        edbapp = Edb(target_path, edbversion=desktop_version)

        assert edbapp.cutout(
            signal_list=["trace_n"],
            reference_list=["ground"],
            number_of_threads=4,
            extent_type="Conformal",
            use_pyaedt_extent_computing=True,
            check_terminals=True,
            expansion_factor=2,
            include_voids_in_extents=True,
        )
        edbapp.close()
        source_path = os.path.join(local_path, "example_models", test_subfolder, "Multizone_GroundVoids.aedb")
        target_path = os.path.join(self.local_scratch.path, "Multizone_GroundVoids.aedb")
        self.local_scratch.copyfolder(source_path, target_path)

        edbapp = Edb(target_path, edbversion=desktop_version)

        assert edbapp.cutout(
            signal_list=["DIFF_N", "DIFF_P"],
            reference_list=["GND"],
            number_of_threads=4,
            extent_type="Conformal",
            use_pyaedt_extent_computing=True,
            check_terminals=True,
            expansion_factor=3,
        )
        edbapp.close()

    # def test_create_EdbLegacy(self):
    #     """Create EDB."""
    #     edb = Edb(os.path.join(self.local_scratch.path, "temp.aedb"), edbversion=desktop_version)
    #     assert edb
    #     assert edb.active_layout
    #     edb.close()

    def test_export_to_hfss(self):
        """Export EDB to HFSS."""
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

    def test_export_to_q3d(self):
        """Export EDB to Q3D."""
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

    def test_074_export_to_maxwell(self):
        """Export EDB to Maxwell 3D."""
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

    # def test_change_design_variable_value(self):
    #     """Change a variable value."""
    #     self.edbapp.add_design_variable("ant_length", "1cm")
    #     self.edbapp.add_design_variable("my_parameter_default", "1mm", is_parameter=True)
    #     self.edbapp.add_design_variable("$my_project_variable", "1mm")
    #     changed_variable_1 = self.edbapp.change_design_variable_value("ant_length", "1m")
    #     if isinstance(changed_variable_1, tuple):
    #         changed_variable_done, ant_length_value = changed_variable_1
    #         assert changed_variable_done
    #     else:
    #         assert changed_variable_1
    #     changed_variable_2 = self.edbapp.change_design_variable_value("elephant_length", "1m")
    #     if isinstance(changed_variable_2, tuple):
    #         changed_variable_done, elephant_length_value = changed_variable_2
    #         assert not changed_variable_done
    #     else:
    #         assert not changed_variable_2
    #     changed_variable_3 = self.edbapp.change_design_variable_value("my_parameter_default", "1m")
    #     if isinstance(changed_variable_3, tuple):
    #         changed_variable_done, my_parameter_value = changed_variable_3
    #         assert changed_variable_done
    #     else:
    #         assert changed_variable_3
    #     changed_variable_4 = self.edbapp.change_design_variable_value("$my_project_variable", "1m")
    #     if isinstance(changed_variable_4, tuple):
    #         changed_variable_done, my_project_variable_value = changed_variable_4
    #         assert changed_variable_done
    #     else:
    #         assert changed_variable_4
    #     changed_variable_5 = self.edbapp.change_design_variable_value("$my_parameter", "1m")
    #     if isinstance(changed_variable_5, tuple):
    #         changed_variable_done, my_project_variable_value = changed_variable_5
    #         assert not changed_variable_done
    #     else:
    #         assert not changed_variable_5

    # def test_variables_value(self):
    #     """Evaluate variables value."""
    #     from pyedb.generic.general_methods import check_numeric_equivalence

    #     variables = {
    #         "var1": 0.01,
    #         "var2": "10um",
    #         "var3": [0.03, "test description"],
    #         "$var4": ["1mm", "Project variable."],
    #         "$var5": 0.1,
    #     }
    #     for key, val in variables.items():
    #         self.edbapp[key] = val
    #         if key == "var1":
    #             assert self.edbapp[key].value == val
    #         elif key == "var2":
    #             assert check_numeric_equivalence(self.edbapp[key].value, 1.0e-5)
    #         elif key == "var3":
    #             assert self.edbapp[key].value == val[0]
    #             assert self.edbapp[key].description == val[1]
    #         elif key == "$var4":
    #             assert self.edbapp[key].value == 0.001
    #             assert self.edbapp[key].description == val[1]
    #         elif key == "$var5":
    #             assert self.edbapp[key].value == 0.1
    #             assert self.edbapp.project_variables[key].delete()

    def test_create_edge_port_on_polygon(self):
        """Create lumped and vertical port."""
        edb = Edb(
            edbpath=os.path.join(local_path, "example_models", test_subfolder, "edge_ports.aedb"),
            edbversion=desktop_version,
        )
        poly_list = [poly for poly in edb.layout.primitives if int(poly.GetPrimitiveType()) == 2]
        port_poly = [poly for poly in poly_list if poly.GetId() == 17][0]
        ref_poly = [poly for poly in poly_list if poly.GetId() == 19][0]
        port_location = [-65e-3, -13e-3]
        ref_location = [-63e-3, -13e-3]
        assert edb.hfss.create_edge_port_on_polygon(
            polygon=port_poly,
            reference_polygon=ref_poly,
            terminal_point=port_location,
            reference_point=ref_location,
        )
        port_poly = [poly for poly in poly_list if poly.GetId() == 23][0]
        ref_poly = [poly for poly in poly_list if poly.GetId() == 22][0]
        port_location = [-65e-3, -10e-3]
        ref_location = [-65e-3, -10e-3]
        assert edb.hfss.create_edge_port_on_polygon(
            polygon=port_poly,
            reference_polygon=ref_poly,
            terminal_point=port_location,
            reference_point=ref_location,
        )
        port_poly = [poly for poly in poly_list if poly.GetId() == 25][0]
        port_location = [-65e-3, -7e-3]
        assert edb.hfss.create_edge_port_on_polygon(
            polygon=port_poly, terminal_point=port_location, reference_layer="gnd"
        )
        sig = edb.modeler.create_trace([[0, 0], ["9mm", 0]], "TOP", "1mm", "SIG", "Flat", "Flat")
        assert sig.create_edge_port("pcb_port_1", "end", "Wave", None, 8, 8)
        assert sig.create_edge_port("pcb_port_2", "start", "gap")
        gap_port = edb.ports["pcb_port_2"]
        assert gap_port.component is None
        assert gap_port.magnitude == 0.0
        assert gap_port.phase == 0.0
        assert gap_port.impedance
        assert not gap_port.deembed
        gap_port.name = "gap_port"
        assert gap_port.name == "gap_port"
        assert isinstance(gap_port.renormalize_z0, tuple)
        gap_port.is_circuit_port = True
        assert gap_port.is_circuit_port
        edb.close()

    def test_create_dc_simulation(self):
        """Create Siwave DC simulation"""
        edb = Edb(
            edbpath=os.path.join(local_path, "example_models", test_subfolder, "dc_flow.aedb"),
            edbversion=desktop_version,
        )
        sim_setup = edb.new_simulation_configuration()
        sim_setup.do_cutout_subdesign = False
        sim_setup.solver_type = SolverType.SiwaveDC
        sim_setup.add_voltage_source(
            positive_node_component="Q3",
            positive_node_net="SOURCE_HBA_PHASEA",
            negative_node_component="Q3",
            negative_node_net="HV_DC+",
        )
        sim_setup.add_current_source(
            name="I25",
            positive_node_component="Q5",
            positive_node_net="SOURCE_HBB_PHASEB",
            negative_node_component="Q5",
            negative_node_net="HV_DC+",
        )
        assert len(sim_setup.sources) == 2
        sim_setup.open_edb_after_build = False
        sim_setup.batch_solve_settings.output_aedb = os.path.join(self.local_scratch.path, "build.aedb")
        original_path = edb.edbpath
        assert sim_setup.batch_solve_settings.use_pyaedt_cutout
        assert not sim_setup.batch_solve_settings.use_default_cutout
        sim_setup.batch_solve_settings.use_pyaedt_cutout = True
        assert sim_setup.batch_solve_settings.use_pyaedt_cutout
        assert not sim_setup.batch_solve_settings.use_default_cutout
        assert sim_setup.build_simulation_project()
        assert edb.edbpath == original_path
        sim_setup.open_edb_after_build = True
        assert sim_setup.build_simulation_project()
        assert edb.edbpath == os.path.join(self.local_scratch.path, "build.aedb")

        edb.close()

    def test_edb_statistics(self):
        """Get statistics."""
        example_project = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1.aedb")
        target_path = os.path.join(self.local_scratch.path, "ANSYS-HSD_V1_110.aedb")
        self.local_scratch.copyfolder(example_project, target_path)
        edb = Edb(target_path, edbversion=desktop_version)
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
        assert edb_stats.occupying_ratio["1_Top"] == 0.3016820127679697
        assert edb_stats.occupying_ratio["Inner1(GND1)"] == 0.9374673461236078
        assert edb_stats.occupying_ratio["16_Bottom"] == 0.20492545496020312
        edb.close()

    def test_hfss_set_bounding_box_extent(self):
        """Configure HFSS with bounding box"""
        source_path = os.path.join(local_path, "example_models", test_subfolder, "test_107.aedb")
        target_path = os.path.join(self.local_scratch.path, "test_113.aedb")
        self.local_scratch.copyfolder(source_path, target_path)
        edb = Edb(target_path, edbversion=desktop_version)
        initial_extent_info = edb.active_cell.GetHFSSExtentInfo()
        assert initial_extent_info.ExtentType == edb.edb_api.utility.utility.HFSSExtentInfoType.Conforming
        config = SimulationConfiguration()
        config.radiation_box = RadiationBoxType.BoundingBox
        assert edb.hfss.configure_hfss_extents(config)
        final_extent_info = edb.active_cell.GetHFSSExtentInfo()
        assert final_extent_info.ExtentType == edb.edb_api.utility.utility.HFSSExtentInfoType.BoundingBox
        edb.close()

    def test_create_rlc_component(self):
        """Create rlc components from pin"""
        example_project = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1.aedb")
        target_path = os.path.join(self.local_scratch.path, "ANSYS_114.aedb")
        self.local_scratch.copyfolder(example_project, target_path)
        edb = Edb(target_path, edbversion=desktop_version)
        pins = edb.components.get_pin_from_component("U1", "1V0")
        ref_pins = edb.components.get_pin_from_component("U1", "GND")
        assert edb.components.create([pins[0], ref_pins[0]], "test_0rlc", r_value=1.67, l_value=1e-13, c_value=1e-11)
        assert edb.components.create([pins[0], ref_pins[0]], "test_1rlc", r_value=None, l_value=1e-13, c_value=1e-11)
        assert edb.components.create([pins[0], ref_pins[0]], "test_2rlc", r_value=None, c_value=1e-13)
        edb.close()

    def test_create_rlc_boundary_on_pins(self):
        """Create hfss rlc boundary on pins."""
        example_project = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1.aedb")
        target_path = os.path.join(self.local_scratch.path, "ANSYS-HSD_V1_115.aedb")
        if not os.path.exists(self.local_scratch.path):
            os.mkdir(self.local_scratch.path)
        self.local_scratch.copyfolder(example_project, target_path)
        edb = Edb(target_path, edbversion=desktop_version)
        pins = edb.components.get_pin_from_component("U1", "1V0")
        ref_pins = edb.components.get_pin_from_component("U1", "GND")
        assert edb.hfss.create_rlc_boundary_on_pins(pins[0], ref_pins[0], rvalue=1.05, lvalue=1.05e-12, cvalue=1.78e-13)
        edb.close()

    def test_configure_hfss_analysis_setup_enforce_causality(self):
        """Configure HFSS analysis setup."""
        source_path = os.path.join(local_path, "example_models", test_subfolder, "lam_for_top_place_no_setups.aedb")
        target_path = os.path.join(self.local_scratch.path, "lam_for_top_place_no_setups_t116.aedb")
        if not os.path.exists(self.local_scratch.path):
            os.mkdir(self.local_scratch.path)
        self.local_scratch.copyfolder(source_path, target_path)
        edb = Edb(target_path, edbversion=desktop_version)
        assert len(list(edb.active_cell.SimulationSetups)) == 0
        sim_config = SimulationConfiguration()
        sim_config.enforce_causality = False
        assert sim_config.do_lambda_refinement
        sim_config.mesh_sizefactor = 0.1
        assert sim_config.mesh_sizefactor == 0.1
        assert not sim_config.do_lambda_refinement
        sim_config.start_freq = "1GHz"
        edb.hfss.configure_hfss_analysis_setup(sim_config)
        assert len(list(edb.active_cell.SimulationSetups)) == 1
        setup = list(edb.active_cell.SimulationSetups)[0]
        ssi = setup.GetSimSetupInfo()
        assert len(list(ssi.SweepDataList)) == 1
        sweep = list(ssi.SweepDataList)[0]
        assert not sweep.EnforceCausality
        edb.close()

    def test_configure_hfss_analysis_setup(self):
        """Configure HFSS analysis setup."""
        source_path = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1.aedb")
        target_path = os.path.join(self.local_scratch.path, "test_0117.aedb")
        self.local_scratch.copyfolder(source_path, target_path)
        edb = Edb(target_path, edbversion=desktop_version)
        sim_setup = SimulationConfiguration()
        sim_setup.mesh_sizefactor = 1.9
        assert not sim_setup.do_lambda_refinement
        edb.hfss.configure_hfss_analysis_setup(sim_setup)
        mesh_size_factor = (
            list(edb.active_cell.SimulationSetups)[0]
            .GetSimSetupInfo()
            .get_SimulationSettings()
            .get_InitialMeshSettings()
            .get_MeshSizefactor()
        )
        assert mesh_size_factor == 1.9
        edb.close()

    def test_create_various_ports_0(self):
        """Create various ports."""
        edb = Edb(
            edbpath=os.path.join(local_path, "example_models", "edb_edge_ports.aedb"),
            edbversion=desktop_version,
        )
        prim_1_id = [i.id for i in edb.modeler.primitives if i.net_name == "trace_2"][0]
        assert edb.hfss.create_edge_port_vertical(prim_1_id, ["-66mm", "-4mm"], "port_ver")

        prim_2_id = [i.id for i in edb.modeler.primitives if i.net_name == "trace_3"][0]
        assert edb.hfss.create_edge_port_horizontal(
            prim_1_id, ["-60mm", "-4mm"], prim_2_id, ["-59mm", "-4mm"], "port_hori", 30, "Lower"
        )
        assert edb.hfss.get_ports_number() == 2
        port_ver = edb.ports["port_ver"]
        assert not port_ver.is_null
        assert port_ver.hfss_type == "Gap"
        port_hori = edb.ports["port_hori"]
        assert port_hori.ref_terminal

        kwargs = {
            "layer_name": "1_Top",
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

        assert edb.hfss.create_wave_port(traces[0].id, trace_paths[0][0], "wave_port")
        wave_port = edb.ports["wave_port"]
        wave_port.horizontal_extent_factor = 10
        wave_port.vertical_extent_factor = 10
        assert wave_port.horizontal_extent_factor == 10
        assert wave_port.vertical_extent_factor == 10
        wave_port.radial_extent_factor = 1
        assert wave_port.radial_extent_factor == 1
        assert wave_port.pec_launch_width
        assert not wave_port.deembed
        assert wave_port.deembed_length == 0.0
        assert wave_port.do_renormalize
        wave_port.do_renormalize = False
        assert not wave_port.do_renormalize
        assert edb.hfss.create_differential_wave_port(
            traces[0].id,
            trace_paths[0][0],
            traces[1].id,
            trace_paths[1][0],
            horizontal_extent_factor=8,
            port_name="df_port",
        )
        assert edb.ports["df_port"]
        p, n = edb.ports["df_port"].terminals
        assert edb.ports["df_port"].decouple()
        p.couple_ports(n)

        traces_id = [i.id for i in traces]
        paths = [i[1] for i in trace_paths]
        _, df_port = edb.hfss.create_bundle_wave_port(traces_id, paths)
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
        edb.close()

    def test_create_various_ports_1(self):
        """Create various ports."""
        edb = Edb(
            edbpath=os.path.join(local_path, "example_models", "edb_edge_ports.aedb"),
            edbversion=desktop_version,
        )
        kwargs = {
            "layer_name": "1_Top",
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
        p = edb.excitations["wave_port"]
        p.horizontal_extent_factor = 6
        p.vertical_extent_factor = 5
        p.pec_launch_width = "0.02mm"
        p.radial_extent_factor = 1
        assert p.horizontal_extent_factor == 6
        assert p.vertical_extent_factor == 5
        assert p.pec_launch_width == "0.02mm"
        assert p.radial_extent_factor == 1
        edb.close()

    def test_build_hfss_project_from_config_file(self):
        """Build a simulation project from config file."""
        source_path = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1.aedb")
        target_path = os.path.join(self.local_scratch.path, "test_0122.aedb")
        self.local_scratch.copyfolder(source_path, target_path)
        edbapp = Edb(target_path, edbversion=desktop_version)
        cfg_file = os.path.join(os.path.dirname(edbapp.edbpath), "test.cfg")
        with open(cfg_file, "w") as f:
            f.writelines("SolverType = 'Hfss3dLayout'\n")
            f.writelines("PowerNets = ['GND']\n")
            f.writelines("Components = ['U1', 'U7']")

        sim_config = SimulationConfiguration(cfg_file)
        assert edbapp.build_simulation_project(sim_config)
        edbapp.close()

    def test_set_all_antipad_values(self):
        """Set all anti-pads from all pad-stack definition to the given value."""
        source_path = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1.aedb")
        target_path = os.path.join(self.local_scratch.path, "test_0120.aedb")
        self.local_scratch.copyfolder(source_path, target_path)
        edbapp = Edb(target_path, edbversion=desktop_version)
        assert edbapp.padstacks.set_all_antipad_value(0.0)
        edbapp.close()

    def test_hfss_simulation_setup(self):
        """Create a setup from a template and evaluate its properties."""
        source_path = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1.aedb")
        target_path = os.path.join(self.local_scratch.path, "test_0129.aedb")
        self.local_scratch.copyfolder(source_path, target_path)
        edbapp = Edb(target_path, edbversion=desktop_version)
        setup1 = edbapp.create_hfss_setup("setup1")
        assert not edbapp.create_hfss_setup("setup1")
        assert setup1.set_solution_single_frequency()
        assert setup1.set_solution_multi_frequencies()
        assert setup1.set_solution_broadband()

        setup1.hfss_solver_settings.enhanced_low_freq_accuracy = True
        setup1.hfss_solver_settings.order_basis = "first"
        setup1.hfss_solver_settings.relative_residual = 0.0002
        setup1.hfss_solver_settings.use_shell_elements = True

        setup1b = edbapp.setups["setup1"]
        hfss_solver_settings = edbapp.setups["setup1"].hfss_solver_settings
        assert hfss_solver_settings.order_basis == "first"
        assert hfss_solver_settings.relative_residual == 0.0002
        assert hfss_solver_settings.solver_type
        assert hfss_solver_settings.enhanced_low_freq_accuracy
        assert not hfss_solver_settings.use_shell_elements

        assert setup1.adaptive_settings.add_adaptive_frequency_data("5GHz", 8, "0.01")
        assert setup1.adaptive_settings.adaptive_frequency_data_list
        setup1.adaptive_settings.adapt_type = "kBroadband"
        setup1.adaptive_settings.basic = False
        setup1.adaptive_settings.max_refinement = 1000001
        setup1.adaptive_settings.max_refine_per_pass = 20
        setup1.adaptive_settings.min_passes = 2
        setup1.adaptive_settings.save_fields = True
        setup1.adaptive_settings.save_rad_field_only = True
        setup1.adaptive_settings.use_convergence_matrix = True
        setup1.adaptive_settings.use_max_refinement = True

        assert edbapp.setups["setup1"].adaptive_settings.adapt_type == "kBroadband"
        assert not edbapp.setups["setup1"].adaptive_settings.basic
        assert edbapp.setups["setup1"].adaptive_settings.max_refinement == 1000001
        assert edbapp.setups["setup1"].adaptive_settings.max_refine_per_pass == 20
        assert edbapp.setups["setup1"].adaptive_settings.min_passes == 2
        assert edbapp.setups["setup1"].adaptive_settings.save_fields
        assert edbapp.setups["setup1"].adaptive_settings.save_rad_field_only
        # assert adaptive_settings.use_convergence_matrix
        assert edbapp.setups["setup1"].adaptive_settings.use_max_refinement

        setup1.defeature_settings.defeature_abs_length = "1um"
        setup1.defeature_settings.defeature_ratio = 1e-5
        setup1.defeature_settings.healing_option = 0
        setup1.defeature_settings.model_type = 1
        setup1.defeature_settings.remove_floating_geometry = True
        setup1.defeature_settings.small_void_area = 0.1
        setup1.defeature_settings.union_polygons = False
        setup1.defeature_settings.use_defeature = False
        setup1.defeature_settings.use_defeature_abs_length = True

        defeature_settings = edbapp.setups["setup1"].defeature_settings
        assert defeature_settings.defeature_abs_length == "1um"
        assert defeature_settings.defeature_ratio == 1e-5
        # assert defeature_settings.healing_option == 0
        # assert defeature_settings.model_type == 1
        assert defeature_settings.remove_floating_geometry
        assert defeature_settings.small_void_area == 0.1
        assert not defeature_settings.union_polygons
        assert not defeature_settings.use_defeature
        assert defeature_settings.use_defeature_abs_length

        via_settings = setup1.via_settings
        via_settings.via_density = 1
        if float(edbapp.edbversion) >= 2024.1:
            via_settings.via_mesh_plating = True
        via_settings.via_material = "pec"
        via_settings.via_num_sides = 8
        via_settings.via_style = "kNum25DViaStyle"

        via_settings = edbapp.setups["setup1"].via_settings
        assert via_settings.via_density == 1
        if float(edbapp.edbversion) >= 2024.1:
            assert via_settings.via_mesh_plating
        assert via_settings.via_material == "pec"
        assert via_settings.via_num_sides == 8
        # assert via_settings.via_style == "kNum25DViaStyle"

        advanced_mesh_settings = setup1.advanced_mesh_settings
        advanced_mesh_settings.layer_snap_tol = "1e-6"
        advanced_mesh_settings.mesh_display_attributes = "#0000001"
        advanced_mesh_settings.replace_3d_triangles = False

        advanced_mesh_settings = edbapp.setups["setup1"].advanced_mesh_settings
        assert advanced_mesh_settings.layer_snap_tol == "1e-6"
        assert advanced_mesh_settings.mesh_display_attributes == "#0000001"
        assert not advanced_mesh_settings.replace_3d_triangles

        curve_approx_settings = setup1.curve_approx_settings
        curve_approx_settings.arc_angle = "15deg"
        curve_approx_settings.arc_to_chord_error = "0.1"
        curve_approx_settings.max_arc_points = 12
        curve_approx_settings.start_azimuth = "1"
        curve_approx_settings.use_arc_to_chord_error = True

        curve_approx_settings = edbapp.setups["setup1"].curve_approx_settings
        assert curve_approx_settings.arc_to_chord_error == "0.1"
        assert curve_approx_settings.max_arc_points == 12
        assert curve_approx_settings.start_azimuth == "1"
        assert curve_approx_settings.use_arc_to_chord_error

        dcr_settings = setup1.dcr_settings
        dcr_settings.conduction_max_passes = 11
        dcr_settings.conduction_min_converged_passes = 2
        dcr_settings.conduction_min_passes = 2
        dcr_settings.conduction_per_error = 2.0
        dcr_settings.conduction_per_refine = 33.0

        dcr_settings = edbapp.setups["setup1"].dcr_settings
        assert dcr_settings.conduction_max_passes == 11
        assert dcr_settings.conduction_min_converged_passes == 2
        assert dcr_settings.conduction_min_passes == 2
        assert dcr_settings.conduction_per_error == 2.0
        assert dcr_settings.conduction_per_refine == 33.0

        hfss_port_settings = setup1.hfss_port_settings
        hfss_port_settings.max_delta_z0 = 0.5
        assert hfss_port_settings.max_delta_z0 == 0.5
        hfss_port_settings.max_triangles_wave_port = 1000
        assert hfss_port_settings.max_triangles_wave_port == 1000
        hfss_port_settings.min_triangles_wave_port = 200
        assert hfss_port_settings.min_triangles_wave_port == 200
        hfss_port_settings.set_triangles_wave_port = True
        assert hfss_port_settings.set_triangles_wave_port

        # mesh_operations = setup1.mesh_operations
        # setup1.mesh_operations = mesh_operations

        setup1.add_sweep(
            "sweep1",
            frequency_set=[
                ["linear count", "0", "1kHz", 1],
                ["log scale", "1kHz", "0.1GHz", 10],
                ["linear scale", "0.1GHz", "10GHz", "0.1GHz"],
            ],
        )
        assert "sweep1" in setup1.frequency_sweeps
        sweep1 = setup1.frequency_sweeps["sweep1"]
        sweep1.adaptive_sampling = True
        assert sweep1.adaptive_sampling

        edbapp.setups["setup1"].name = "setup1a"
        assert "setup1" not in edbapp.setups
        assert "setup1a" in edbapp.setups
        edbapp.close()

    def test_hfss_simulation_setup_mesh_operation(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        setup = edbapp.create_hfss_setup(name="setup")
        mop = setup.add_length_mesh_operation({"GND": ["1_Top", "16_Bottom"]}, "m1")
        assert mop.nets_layers_list == {"GND": ["1_Top", "16_Bottom"]}
        assert mop.type == "length"
        assert mop.name == "m1"
        assert mop.max_elements == 1000
        assert mop.restrict_max_elements
        assert mop.restrict_length
        assert mop.max_length == "1mm"
        setup = edbapp.setups["setup"]
        assert setup.mesh_operations
        assert edbapp.setups["setup"].mesh_operations

        mop = edbapp.setups["setup"].add_skin_depth_mesh_operation({"GND": ["1_Top", "16_Bottom"]})
        assert mop.nets_layers_list == {"GND": ["1_Top", "16_Bottom"]}
        assert mop.max_elements == 1000
        assert mop.restrict_max_elements
        assert mop.skin_depth == "1um"
        assert mop.surface_triangle_length == "1mm"
        assert mop.number_of_layer_elements == "2"

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
        setup1.add_sweep("sw1", ["linear count", "1MHz", "100MHz", 10])
        assert edbapp.setups["setup1"].sweeps["sw1"].name == "sw1"
        assert len(setup1.sweeps["sw1"].frequencies) == 10
        setup1.sweeps["sw1"].add("linear_scale", "210MHz", "300MHz", "10MHz")
        assert len(setup1.sweeps["sw1"].frequencies) == 20
        setup1.sweeps["sw1"].add("log_scale", "1GHz", "10GHz", 10)
        assert len(setup1.sweeps["sw1"].frequencies) == 31
        edbapp.close()

    def test_hfss_simulation_setup_b(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        setup1 = edbapp.create_hfss_setup("setup1")
        sweep1 = setup1.add_sweep(
            name="sweep1",
            frequency_set=[
                ["linear count", "1MHz", "10MHz", 10],
            ],
        )
        sweep2 = setup1.add_sweep(
            name="sweep2",
            frequency_set=[
                ["log scale", "1kHz", "100kHz", 10],
            ],
        )
        sweep3 = setup1.add_sweep(
            name="sweep3",
            frequency_set=[
                ["linear scale", "20MHz", "30MHz", "1MHz"],
            ],
        )
        edbapp.close()

    def test_siwave_dc_simulation_setup(self):
        """Create a dc simulation setup and evaluate its properties."""
        setup1 = self.edbapp.create_siwave_dc_setup("DC1")
        setup1.dc_settings.restore_default()
        setup1.dc_advanced_settings.restore_default()

        settings = self.edbapp.setups["DC1"].get_configurations()
        for k, v in setup1.dc_settings.defaults.items():
            if k in ["compute_inductance", "plot_jv"]:
                continue
            print(k)
            assert settings["dc_settings"][k] == v

        for k, v in setup1.dc_advanced_settings.defaults.items():
            print(k)
            assert settings["dc_advanced_settings"][k] == v

        for p in [0, 1, 2]:
            setup1.set_dc_slider(p)
            settings = self.edbapp.setups["DC1"].get_configurations()
            for k, v in setup1.dc_settings.dc_defaults.items():
                print(k)
                assert settings["dc_settings"][k] == v[p]

            for k, v in setup1.dc_advanced_settings.dc_defaults.items():
                print(k)
                assert settings["dc_advanced_settings"][k] == v[p]

    def test_siwave_ac_simulation_setup(self):
        """Create an ac simulation setup and evaluate its properties."""
        setup1 = self.edbapp.create_siwave_syz_setup("AC1")
        assert setup1.name == "AC1"
        assert setup1.enabled
        setup1.advanced_settings.restore_default()

        settings = self.edbapp.setups["AC1"].get_configurations()
        for k, v in setup1.advanced_settings.defaults.items():
            if k in ["min_plane_area_to_mesh"]:
                continue
            assert settings["advanced_settings"][k] == v

        for p in [0, 1, 2]:
            setup1.set_si_slider(p)
            settings = self.edbapp.setups["AC1"].get_configurations()
            for k, v in setup1.advanced_settings.si_defaults.items():
                assert settings["advanced_settings"][k] == v[p]

        for p in [0, 1, 2]:
            setup1.set_pi_slider(p)
            settings = self.edbapp.setups["AC1"].get_configurations()
            for k, v in setup1.advanced_settings.pi_defaults.items():
                assert settings["advanced_settings"][k] == v[p]

        sweep = setup1.add_sweep(
            name="sweep1",
            frequency_set=[
                ["linear count", "0", "1kHz", 1],
                ["log scale", "1kHz", "0.1GHz", 10],
                ["linear scale", "0.1GHz", "10GHz", "0.1GHz"],
            ],
        )
        assert 0 in sweep.frequencies
        assert not sweep.adaptive_sampling
        assert not sweep.adv_dc_extrapolation
        assert sweep.auto_s_mat_only_solve
        assert not sweep.enforce_causality
        assert not sweep.enforce_dc_and_causality
        assert sweep.enforce_passivity
        assert sweep.freq_sweep_type == "kInterpolatingSweep"
        assert sweep.interpolation_use_full_basis
        assert sweep.interpolation_use_port_impedance
        assert sweep.interpolation_use_prop_const
        assert sweep.max_solutions == 250
        assert sweep.min_freq_s_mat_only_solve == "1MHz"
        assert not sweep.min_solved_freq
        assert sweep.passivity_tolerance == 0.0001
        assert sweep.relative_s_error == 0.005
        assert not sweep.save_fields
        assert not sweep.save_rad_fields_only
        assert not sweep.use_q3d_for_dc

        sweep.adaptive_sampling = True
        sweep.adv_dc_extrapolation = True
        sweep.compute_dc_point = True
        sweep.auto_s_mat_only_solve = False
        sweep.enforce_causality = True
        sweep.enforce_dc_and_causality = True
        sweep.enforce_passivity = False
        sweep.freq_sweep_type = "kDiscreteSweep"
        sweep.interpolation_use_full_basis = False
        sweep.interpolation_use_port_impedance = False
        sweep.interpolation_use_prop_const = False
        sweep.max_solutions = 200
        sweep.min_freq_s_mat_only_solve = "2MHz"
        sweep.min_solved_freq = "1Hz"
        sweep.passivity_tolerance = 0.0002
        sweep.relative_s_error = 0.004
        sweep.save_fields = True
        sweep.save_rad_fields_only = True
        sweep.use_q3d_for_dc = True

        assert sweep.adaptive_sampling
        assert sweep.adv_dc_extrapolation
        assert sweep.compute_dc_point
        assert not sweep.auto_s_mat_only_solve
        assert sweep.enforce_causality
        assert sweep.enforce_dc_and_causality
        assert not sweep.enforce_passivity
        assert sweep.freq_sweep_type == "kDiscreteSweep"
        assert not sweep.interpolation_use_full_basis
        assert not sweep.interpolation_use_port_impedance
        assert not sweep.interpolation_use_prop_const
        assert sweep.max_solutions == 200
        assert sweep.min_freq_s_mat_only_solve == "2MHz"
        assert sweep.min_solved_freq == "1Hz"
        assert sweep.passivity_tolerance == 0.0002
        assert sweep.relative_s_error == 0.004
        assert sweep.save_fields
        assert sweep.save_rad_fields_only
        assert sweep.use_q3d_for_dc

    def test_edb_configuration_siwave_build_ac_project(self):
        """Build ac simulation project."""
        source_path = os.path.join(local_path, "example_models", test_subfolder, "padstacks.aedb")
        target_path = os.path.join(self.local_scratch.path, "test_133_simconfig.aedb")
        self.local_scratch.copyfolder(source_path, target_path)
        edbapp = Edb(target_path, edbversion=desktop_version)
        simconfig = edbapp.new_simulation_configuration()
        simconfig.solver_type = SolverType.SiwaveSYZ
        simconfig.mesh_freq = "40.25GHz"
        edbapp.build_simulation_project(simconfig)
        assert edbapp.siwave_ac_setups[simconfig.setup_name].advanced_settings.mesh_frequency == simconfig.mesh_freq
        edbapp.close()

    def test_siwave_create_port_between_pin_and_layer(self):
        """Create circuit port between pin and a reference layer."""
        source_path = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1.aedb")
        target_path = os.path.join(self.local_scratch.path, "test_0134.aedb")
        self.local_scratch.copyfolder(source_path, target_path)
        edbapp = Edb(target_path, edbversion=desktop_version)
        edbapp.siwave.create_port_between_pin_and_layer(
            component_name="U1", pins_name="A27", layer_name="16_Bottom", reference_net="GND"
        )
        U7 = edbapp.components["U7"]
        U7.pins["G7"].create_port()
        port = U7.pins["F7"].create_port(reference=U7.pins["E7"])
        port.is_circuit_port = True
        _, pin_group = edbapp.siwave.create_pin_group_on_net(
            reference_designator="U7", net_name="GND", group_name="U7_GND"
        )
        U7.pins["F7"].create_port(name="test", reference=pin_group)
        padstack_instance_terminals = [
            term for term in list(edbapp.terminals.values()) if "PadstackInstanceTerminal" in str(term.type)
        ]
        for term in padstack_instance_terminals:
            assert term.position
        pos_pin = edbapp.padstacks.get_pinlist_from_component_and_net("C173")[1]
        neg_pin = edbapp.padstacks.get_pinlist_from_component_and_net("C172")[0]
        edbapp.create_port(
            pos_pin.get_terminal(create_new_terminal=True),
            neg_pin.get_terminal(create_new_terminal=True),
            is_circuit_port=True,
            name="test",
        )
        assert edbapp.ports["test"]
        edbapp.ports["test"].is_circuit_port = True
        assert edbapp.ports["test"].is_circuit_port == True
        edbapp.close()

    def test_siwave_source_setter(self):
        """Evaluate siwave sources property."""
        source_path = os.path.join(local_path, "example_models", test_subfolder, "test_sources.aedb")
        target_path = os.path.join(self.local_scratch.path, "test_134_source_setter.aedb")
        self.local_scratch.copyfolder(source_path, target_path)
        edbapp = Edb(target_path, edbversion=desktop_version)
        sources = list(edbapp.siwave.sources.values())
        sources[0].magnitude = 1.45
        assert sources[0].magnitude == 1.45
        sources[1].magnitude = 1.45
        assert sources[1].magnitude == 1.45
        edbapp.close()

    def test_delete_pingroup(self):
        """Delete siwave pin groups."""
        source_path = os.path.join(local_path, "example_models", test_subfolder, "test_pin_group.aedb")
        target_path = os.path.join(self.local_scratch.path, "test_135_pin_group.aedb")
        self.local_scratch.copyfolder(source_path, target_path)
        edbapp = Edb(target_path, edbversion=desktop_version)
        for _, pingroup in edbapp.siwave.pin_groups.items():
            assert pingroup.delete()
        assert not edbapp.siwave.pin_groups
        edbapp.close()

    def test_design_options(self):
        """Evaluate Edb design settings and options."""
        self.edbapp.design_options.suppress_pads = False
        assert not self.edbapp.design_options.suppress_pads
        self.edbapp.design_options.antipads_always_on = True
        assert self.edbapp.design_options.antipads_always_on

    def test_pins(self):
        """Evaluate the pins."""
        assert len(self.edbapp.pins) > 0

    def test_create_padstack_instance(self):
        """Create padstack instances."""
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
        pad_instance3.dcir_equipotential_region = True
        assert pad_instance3.dcir_equipotential_region
        pad_instance3.dcir_equipotential_region = False
        assert not pad_instance3.dcir_equipotential_region

        trace = edb.modeler.create_trace([[0, 0], [0, 10e-3]], "1_Top", "0.1mm", "trace_with_via_fence")
        edb.padstacks.create_padstack("via_0")
        trace.create_via_fence("1mm", "1mm", "via_0")

        edb.close()

    def test_assign_hfss_extent_non_multiple_with_simconfig(self):
        """Build simulation project without multiple."""
        edb = Edb()
        edb.stackup.add_layer(layer_name="GND", fillMaterial="air", thickness="30um")
        edb.stackup.add_layer(layer_name="FR4", base_layer="gnd", thickness="250um")
        edb.stackup.add_layer(layer_name="SIGNAL", base_layer="FR4", thickness="30um")
        edb.modeler.create_trace(layer_name="SIGNAL", width=0.02, net_name="net1", path_list=[[-1e3, 0, 1e-3, 0]])
        edb.modeler.create_rectangle(
            layer_name="GND",
            representation_type="CenterWidthHeight",
            center_point=["0mm", "0mm"],
            width="4mm",
            height="4mm",
            net_name="GND",
        )
        sim_setup = edb.new_simulation_configuration()
        sim_setup.signal_nets = ["net1"]
        # sim_setup.power_nets = ["GND"]
        sim_setup.use_dielectric_extent_multiple = False
        sim_setup.use_airbox_horizontal_extent_multiple = False
        sim_setup.use_airbox_negative_vertical_extent_multiple = False
        sim_setup.use_airbox_positive_vertical_extent_multiple = False
        sim_setup.dielectric_extent = 0.0005
        sim_setup.airbox_horizontal_extent = 0.001
        sim_setup.airbox_negative_vertical_extent = 0.05
        sim_setup.airbox_positive_vertical_extent = 0.04
        sim_setup.add_frequency_sweep = False
        sim_setup.include_only_selected_nets = True
        sim_setup.do_cutout_subdesign = False
        sim_setup.generate_excitations = False
        edb.build_simulation_project(sim_setup)
        hfss_ext_info = edb.active_cell.GetHFSSExtentInfo()
        assert list(edb.nets.nets.values())[0].name == "net1"
        assert not edb.setups["Pyaedt_setup"].frequency_sweeps
        assert hfss_ext_info
        assert hfss_ext_info.AirBoxHorizontalExtent.Item1 == 0.001
        assert not hfss_ext_info.AirBoxHorizontalExtent.Item2
        assert hfss_ext_info.AirBoxNegativeVerticalExtent.Item1 == 0.05
        assert not hfss_ext_info.AirBoxNegativeVerticalExtent.Item2
        assert hfss_ext_info.AirBoxPositiveVerticalExtent.Item1 == 0.04
        assert not hfss_ext_info.AirBoxPositiveVerticalExtent.Item2
        assert hfss_ext_info.DielectricExtentSize.Item1 == 0.0005
        assert not hfss_ext_info.AirBoxPositiveVerticalExtent.Item2
        edb.close()

    def test_assign_hfss_extent_multiple_with_simconfig(self):
        """Build simulation project with multiple."""
        edb = Edb()
        edb.stackup.add_layer(layer_name="GND", fillMaterial="air", thickness="30um")
        edb.stackup.add_layer(layer_name="FR4", base_layer="gnd", thickness="250um")
        edb.stackup.add_layer(layer_name="SIGNAL", base_layer="FR4", thickness="30um")
        edb.modeler.create_trace(layer_name="SIGNAL", width=0.02, net_name="net1", path_list=[[-1e3, 0, 1e-3, 0]])
        edb.modeler.create_rectangle(
            layer_name="GND",
            representation_type="CenterWidthHeight",
            center_point=["0mm", "0mm"],
            width="4mm",
            height="4mm",
            net_name="GND",
        )
        sim_setup = edb.new_simulation_configuration()
        sim_setup.signal_nets = ["net1"]
        sim_setup.power_nets = ["GND"]
        sim_setup.use_dielectric_extent_multiple = True
        sim_setup.use_airbox_horizontal_extent_multiple = True
        sim_setup.use_airbox_negative_vertical_extent_multiple = True
        sim_setup.use_airbox_positive_vertical_extent_multiple = True
        sim_setup.dielectric_extent = 0.0005
        sim_setup.airbox_horizontal_extent = 0.001
        sim_setup.airbox_negative_vertical_extent = 0.05
        sim_setup.airbox_positive_vertical_extent = 0.04
        edb.build_simulation_project(sim_setup)
        hfss_ext_info = edb.active_cell.GetHFSSExtentInfo()
        assert hfss_ext_info
        assert hfss_ext_info.AirBoxHorizontalExtent.Item1 == 0.001
        assert hfss_ext_info.AirBoxHorizontalExtent.Item2
        assert hfss_ext_info.AirBoxNegativeVerticalExtent.Item1 == 0.05
        assert hfss_ext_info.AirBoxNegativeVerticalExtent.Item2
        assert hfss_ext_info.AirBoxPositiveVerticalExtent.Item1 == 0.04
        assert hfss_ext_info.AirBoxPositiveVerticalExtent.Item2
        assert hfss_ext_info.DielectricExtentSize.Item1 == 0.0005
        assert hfss_ext_info.AirBoxPositiveVerticalExtent.Item2
        edb.close()

    def test_stackup_properties(self):
        """Evaluate stackup properties."""
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
        from pyedb.dotnet.edb_core.edb_data.primitives_data import (
            EDBPrimitives as EDBPrimitives,
        )

        config = {
            "air_box_horizontal_extent_enabled": False,
            "air_box_horizontal_extent": 0.01,
            "air_box_positive_vertical_extent": 0.3,
            "air_box_positive_vertical_extent_enabled": False,
            "air_box_negative_vertical_extent": 0.1,
            "air_box_negative_vertical_extent_enabled": False,
            "base_polygon": self.edbapp.modeler.polygons[0],
            "dielectric_base_polygon": self.edbapp.modeler.polygons[1],
            "dielectric_extent_size": 0.1,
            "dielectric_extent_size_enabled": False,
            "dielectric_extent_type": "conforming",
            "extent_type": "conforming",
            "honor_user_dielectric": False,
            "is_pml_visible": False,
            "open_region_type": "pml",
            "operating_freq": "2GHz",
            "radiation_level": 1,
            "sync_air_box_vertical_extent": False,
            "use_open_region": False,
            "use_xy_data_extent_for_vertical_expansion": False,
            "truncate_air_box_at_ground": True,
        }
        hfss_extent_info = self.edbapp.hfss.hfss_extent_info
        hfss_extent_info.load_config(config)
        exported_config = hfss_extent_info.export_config()
        for i, j in exported_config.items():
            if not i in config:
                continue
            if isinstance(j, EDBPrimitives):
                assert j.id == config[i].id
            elif isinstance(j, EdbValue):
                assert j.tofloat == hfss_extent_info._get_edb_value(config[i]).ToDouble()
            else:
                assert j == config[i]

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

        edb = Edb(
            gds_out, edbversion=desktop_version, technology_file=os.path.join(self.local_scratch.path, "test_138.xml")
        )

        assert edb
        assert "P1" in edb.excitations
        assert "Setup1" in edb.setups
        assert "B1" in edb.components.instances
        edb.close()

    def test_database_properties(self):
        """Evaluate database properties."""
        assert isinstance(self.edbapp.dataset_defs, list)
        assert isinstance(self.edbapp.material_defs, list)
        assert isinstance(self.edbapp.component_defs, list)
        assert isinstance(self.edbapp.package_defs, list)

        assert isinstance(self.edbapp.padstack_defs, list)
        assert isinstance(self.edbapp.jedec5_bondwire_defs, list)
        assert isinstance(self.edbapp.jedec4_bondwire_defs, list)
        assert isinstance(self.edbapp.apd_bondwire_defs, list)
        assert self.edbapp.source_version == ""
        self.edbapp.source_version = "2022.2"
        assert self.edbapp.source == ""
        assert self.edbapp.scale(1.0)
        assert isinstance(self.edbapp.version, tuple)
        assert isinstance(self.edbapp.footprint_cells, list)

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
        from pyedb.dotnet.edb_core.edb_data.control_file import ControlFile

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
        edb3.close()
        del edb3

    def test_build_siwave_project_from_config_file(self):
        """Build Siwave simulation project from configuration file."""
        example_project = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1.aedb")
        target_path = os.path.join(self.local_scratch.path, "ANSYS-HSD_V1_15.aedb")
        self.local_scratch.copyfolder(example_project, target_path)
        cfg_file = os.path.join(target_path, "test.cfg")
        with open(cfg_file, "w") as f:
            f.writelines("SolverType = 'SiwaveSYZ'\n")
            f.writelines("PowerNets = ['GND']\n")
            f.writelines("Components = ['U1', 'U2']")
        sim_config = SimulationConfiguration(cfg_file)
        assert Edb(target_path, edbversion=desktop_version).build_simulation_project(sim_config)

    @pytest.mark.skipif(is_linux, reason="Not supported in IPY")
    def test_solve_siwave(self):
        """Solve EDB with Siwave."""
        target_path = os.path.join(local_path, "example_models", "T40", "ANSYS-HSD_V1_DCIR.aedb")
        out_edb = os.path.join(self.local_scratch.path, "to_be_solved.aedb")
        self.local_scratch.copyfolder(target_path, out_edb)
        edbapp = Edb(out_edb, edbversion=desktop_version)
        edbapp.siwave.create_exec_file(add_dc=True)
        out = edbapp.solve_siwave()
        assert os.path.exists(out)
        res = edbapp.export_siwave_dc_results(out, "SIwaveDCIR1")
        for i in res:
            assert os.path.exists(i)
        edbapp.close()

    def test_build_simulation_project(self):
        """Build a ready-to-solve simulation project."""
        target_path = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1.aedb")
        out_edb = os.path.join(self.local_scratch.path, "Build_project.aedb")
        self.local_scratch.copyfolder(target_path, out_edb)
        edbapp = Edb(out_edb, edbversion=desktop_version)
        sim_setup = SimulationConfiguration()
        sim_setup.signal_nets = [
            "DDR4_A0",
            "DDR4_A1",
            "DDR4_A2",
            "DDR4_A3",
            "DDR4_A4",
            "DDR4_A5",
        ]
        sim_setup.power_nets = ["GND"]
        sim_setup.do_cutout_subdesign = True
        sim_setup.components = ["U1", "U15"]
        sim_setup.use_default_coax_port_radial_extension = False
        sim_setup.cutout_subdesign_expansion = 0.001
        sim_setup.start_freq = 0
        sim_setup.stop_freq = 20e9
        sim_setup.step_freq = 10e6
        assert edbapp.build_simulation_project(sim_setup)
        edbapp.close()

    def test_build_simulation_project_with_multiple_batch_solve_settings(self):
        """Build a ready-to-solve simulation project."""
        target_path = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1.aedb")
        out_edb = os.path.join(self.local_scratch.path, "build_project2.aedb")
        self.local_scratch.copyfolder(target_path, out_edb)
        edbapp = Edb(out_edb, edbversion=desktop_version)
        sim_setup = SimulationConfiguration()
        sim_setup.batch_solve_settings.signal_nets = [
            "DDR4_A0",
            "DDR4_A1",
            "DDR4_A2",
            "DDR4_A3",
            "DDR4_A4",
            "DDR4_A5",
        ]
        sim_setup.batch_solve_settings.power_nets = ["GND"]
        sim_setup.batch_solve_settings.do_cutout_subdesign = True
        sim_setup.batch_solve_settings.components = ["U1", "U15"]
        sim_setup.batch_solve_settings.use_default_coax_port_radial_extension = False
        sim_setup.batch_solve_settings.cutout_subdesign_expansion = 0.001
        sim_setup.batch_solve_settings.start_freq = 0
        sim_setup.batch_solve_settings.stop_freq = 20e9
        sim_setup.batch_solve_settings.step_freq = 10e6
        sim_setup.batch_solve_settings.use_pyaedt_cutout = True
        assert edbapp.build_simulation_project(sim_setup)
        assert edbapp.are_port_reference_terminals_connected()
        port1 = list(edbapp.excitations.values())[0]
        assert port1.magnitude == 0.0
        assert port1.phase == 0
        assert port1.reference_net_name == "GND"
        assert not port1.deembed
        assert port1.impedance == 50.0
        assert not port1.is_circuit_port
        assert not port1.renormalize
        assert port1.renormalize_z0 == (50.0, 0.0)
        assert not port1.get_pin_group_terminal_reference_pin()
        assert not port1.get_pad_edge_terminal_reference_pin()
        edbapp.close()

    def test_simconfig_built_custom_sballs_height(self):
        """Build simulation project from custom sballs JSON file."""
        source_path = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1.aedb")
        target_path = os.path.join(self.local_scratch.path, "test_custom_sball_height", "ANSYS-HSD_V1.aedb")
        self.local_scratch.copyfolder(source_path, target_path)
        json_file = os.path.join(target_path, "simsetup_custom_sballs.json")
        edbapp = Edb(target_path, edbversion=desktop_version)
        simconfig = edbapp.new_simulation_configuration()
        simconfig.import_json(json_file)
        edbapp.build_simulation_project(simconfig)
        assert round(edbapp.components["X1"].solder_ball_height, 6) == 0.00025
        assert round(edbapp.components["U1"].solder_ball_height, 6) == 0.00035
        edbapp.close_edb()

    def test_cutout_return_clipping_extent(self):
        """"""
        source_path = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1.aedb")
        target_path = os.path.join(self.local_scratch.path, "test_return_clipping_extent", "test.aedb")
        self.local_scratch.copyfolder(source_path, target_path)
        edbapp = Edb(target_path, desktop_version)
        extent = edbapp.cutout(
            signal_list=["PCIe_Gen4_RX0_P", "PCIe_Gen4_RX0_N", "PCIe_Gen4_RX1_P", "PCIe_Gen4_RX1_N"],
            reference_list=["GND"],
        )
        assert extent
        assert len(extent) == 55
        assert extent[0] == [0.011025799702099603, 0.04451508810211455]
        assert extent[10] == [0.022142311790681247, 0.02851039231475559]
        assert extent[20] == [0.06722930398844625, 0.026054683772800503]
        assert extent[30] == [0.06793706863503707, 0.02961898962849831]
        assert extent[40] == [0.06550327418370948, 0.031478931749766806]
        assert extent[54] == [0.01102500189, 0.044555027391504444]
        edbapp.close_edb()

    def test_move_and_edit_polygons(self):
        """Move a polygon."""
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
        assert polygon.bbox == [0.012462680425333156, -0.043037319574666846, 0.08953731957466685, 0.034037319574666845]
        assert polygon.rotate(angle=34, center=[0, 0])
        assert polygon.bbox == [0.03083951217158376, -0.025151830651067256, 0.05875505636026722, 0.07472816865208806]
        assert polygon.scale(factor=1.5)
        assert polygon.bbox == [0.0238606261244129, -0.05012183047685609, 0.06573394240743807, 0.09969816847787688]
        assert polygon.scale(factor=-0.5, center=[0, 0])
        assert polygon.bbox == [-0.032866971203719036, -0.04984908423893844, -0.01193031306220645, 0.025060915238428044]
        assert polygon.move_layer("GND")
        assert len(edbapp.modeler.polygons) == 1
        assert edbapp.modeler.polygons[0].layer_name == "GND"

    def test_multizone(self, edb_examples):
        edbapp = edb_examples.get_multizone_pcb()
        common_reference_net = "gnd"
        edb_zones = edbapp.copy_zones()
        assert edb_zones
        defined_ports, project_connexions = edbapp.cutout_multizone_layout(edb_zones, common_reference_net)

        assert defined_ports
        assert project_connexions
        edbapp.close_edb()

    @pytest.mark.skipif(
        not desktop_version == "2024.2" or int(desktop_version.split(".")[0]) >= 2025,
        reason="Only supported with 2024.2 and higher",
    )
    def test_icepak(self, edb_examples):
        edbapp = edb_examples.get_si_verse(additional_files_folders=["siwave/icepak_component.pwrd"])
        edbapp.siwave.icepak_use_minimal_comp_defaults = True
        assert edbapp.siwave.icepak_use_minimal_comp_defaults
        edbapp.siwave.icepak_use_minimal_comp_defaults = False
        assert not edbapp.siwave.icepak_use_minimal_comp_defaults
        edbapp.siwave.icepak_component_file = edb_examples.get_local_file_folder("siwave/icepak_component.pwrd")
        assert edbapp.siwave.icepak_component_file == edb_examples.get_local_file_folder("siwave/icepak_component.pwrd")
        edbapp.close()

    def test_adaptive_broadband_setup_from_configfile(self):
        source_path = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1.aedb")
        target_path = os.path.join(self.local_scratch.path, "test_adaptive_broadband.aedb")
        self.local_scratch.copyfolder(source_path, target_path)
        edbapp = Edb(target_path, edbversion=desktop_version)
        cfg_file = os.path.join(target_path, "config_adaptive_broadband.json")
        sim_config = edbapp.new_simulation_configuration()
        sim_config.import_json(cfg_file)
        assert edbapp.build_simulation_project(sim_config)
        assert edbapp.setups["Pyaedt_setup"].adaptive_settings.adapt_type == "kBroadband"
        edbapp.close()

    @pytest.mark.skipif(
        not desktop_version == "2024.2" or int(desktop_version.split(".")[0]) >= 2025,
        reason="Only supported with 2024.2 and higher",
    )
    def test_dcir_properties(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        setup = edbapp.create_siwave_dc_setup()
        setup.dc_ir_settings.export_dc_thermal_data = True
        assert setup.dc_ir_settings.export_dc_thermal_data == True
        assert not setup.dc_ir_settings.import_thermal_data
        setup.dc_ir_settings.dc_report_show_active_devices = True
        assert setup.dc_ir_settings.dc_report_show_active_devices == True
        assert not setup.dc_ir_settings.per_pin_use_pin_format
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
        example_folder = os.path.join(local_path, "example_models", test_subfolder)
        source_path_edb = os.path.join(example_folder, "example_arbitrary_wave_ports.aedb")
        target_path_edb = os.path.join(self.local_scratch.path, "test_wave_ports", "test.aedb")
        self.local_scratch.copyfolder(source_path_edb, target_path_edb)
        edbapp = Edb(target_path_edb, desktop_version)
        edbapp.create_model_for_arbitrary_wave_ports(
            temp_directory=self.local_scratch.path,
            output_edb="wave_ports.aedb",
            mounting_side="top",
        )
        edb_model = os.path.join(self.local_scratch.path, "wave_ports.aedb")
        test_edb = Edb(edbpath=edb_model, edbversion=desktop_version)
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
        )
        bondwire_1.set_material("Gold")
        assert bondwire_1.get_material() == "Gold"
        bondwire_1.type = "jedec_4"
        assert bondwire_1.type == "jedec_4"
        bondwire_1.cross_section_type = "round"
        assert bondwire_1.cross_section_type == "round"
        bondwire_1.cross_section_height = "0.1mm"
        assert bondwire_1.cross_section_height == 0.0001
        bondwire_1.set_definition_name("J4_LH10")
        assert bondwire_1.get_definition_name() == "J4_LH10"
        bondwire_1.set_trajectory(1, 0.1, 0.2, 0.3)
        assert bondwire_1.get_trajectory() == [1, 0.1, 0.2, 0.3]
        bondwire_1.width = "0.2mm"
        assert bondwire_1.width == 0.0002
        bondwire_1.set_start_elevation("16_Bottom")
        bondwire_1.set_end_elevation("16_Bottom")
        assert len(edbapp.modeler.bondwires) == 1
        edbapp.close()

    def test_voltage_regulator(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
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
        edbapp = edb_examples.get_si_verse()
        path_bom = Path(edb_examples.test_folder) / "bom.csv"
        edbapp.workflow.export_bill_of_materials(path_bom)
        assert path_bom.exists()
        edbapp.close()

    def test_create_port_ob_component_no_ref_pins_in_component(self, edb_examples):
        edbapp = edb_examples.get_no_ref_pins_component()
        sim_setup = edbapp.new_simulation_configuration()
        sim_setup.signal_nets = [
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
        ]
        sim_setup.power_nets = ["GND"]
        sim_setup.solver_type = 7
        sim_setup.components = ["J2E2"]
        sim_setup.do_cutout_subdesign = False
        edbapp.build_simulation_project(sim_setup)
        assert len(edbapp.ports) == 15
