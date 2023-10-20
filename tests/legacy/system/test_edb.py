"""Tests related to Edb
"""

import os
from pyedb.legacy.edb_core.edb_data.simulation_configuration import SimulationConfiguration
import pytest

from pyedb import Edb
from pyedb.generic.constants import RadiationBoxType, SourceType
from pyedb.generic.constants import SolverType
from tests.conftest import local_path
from tests.conftest import desktop_version
from tests.legacy.system.conftest import test_subfolder

pytestmark = pytest.mark.system

class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, edbapp, local_scratch, target_path, target_path2, target_path4):
        self.edbapp = edbapp
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
        assert self.edbapp.siwave.create_circuit_port_on_pin_group(
            "PG_V1P0_S0", "PinGroup_2", impedance=50, name="test_port"
        )
        self.edbapp.excitations["test_port"].name = "test_rename"
        assert any(port for port in list(self.edbapp.excitations) if port == "test_rename")

    def test_siwave_create_voltage_source(self):
        """Create a voltage source."""
        assert len(self.edbapp.sources) == 0
        assert "Vsource_" in self.edbapp.siwave.create_voltage_source_on_net("U1", "USB3_D_P", "U1", "GND", 3.3, 0)
        assert len(self.edbapp.sources) == 2
        assert list(self.edbapp.sources.values())[0].magnitude == 3.3

        pins = self.edbapp.components.get_pin_from_component("U1")
        assert "VSource_" in self.edbapp.siwave.create_voltage_source_on_pin(pins[300], pins[10], 3.3, 0)
        assert len(self.edbapp.sources) == 3
        assert len(self.edbapp.probes) == 0  
        
        list(self.edbapp.sources.values())[0].phase = 1
        assert list(self.edbapp.sources.values())[0].phase == 1

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
            reference_designator="U1", pin_numbers=["A14", "A15"], group_name="sink_pos"
        )

        # TODO: Moves this piece of code in another place
        assert self.edbapp.siwave.create_voltage_source_on_pin_group("sink_pos", "gnd", name="vrm_voltage_source")
        self.edbapp.siwave.create_pin_group(reference_designator="U1", pin_numbers=["A27", "A28"], group_name="vp_pos")
        self.edbapp.siwave.create_pin_group(reference_designator="U1", pin_numbers=["A14", "A15"], group_name="vp_neg")
        assert self.edbapp.siwave.create_voltage_probe_on_pin_group("vprobe", "vp_pos", "vp_neg")
        assert self.edbapp.probes["vprobe"]

    def test_siwave_create_dc_terminal(self):
        """Create a DC terminal."""
        assert self.edbapp.siwave.create_dc_terminal("U1", "DDR4_DQ40", "dc_terminal1") == "dc_terminal1"

    def test_siwave_create_resistors_on_pin(self):
        """Create a resistor on pin."""
        pins = self.edbapp.components.get_pin_from_component("U1")
        assert "RST4000" == self.edbapp.siwave.create_resistor_on_pin(pins[302], pins[10], 40, "RST4000")

    def test_siwave_add_syz_analsyis(self):
        """Add a sywave AC analysis."""
        assert self.edbapp.siwave.add_siwave_syz_analysis()

    def test_siwave_add_dc_analysis(self):
        """Add a sywave DC analysis."""
        setup = self.edbapp.siwave.add_siwave_dc_analysis()
        assert setup.add_source_terminal_to_ground(list(self.edbapp.sources.keys())[0], 2)

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
            reference_list=["GND"],
            extent_type="Bounding",
            number_of_threads=4,
            extent_defeature=0.001,
            preserve_components_with_model=True,
        )
        assert "A0_N" not in edbapp.nets.nets
        assert isinstance(edbapp.nets.find_and_fix_disjoint_nets("GND", order_by_area=True), list)
        assert isinstance(edbapp.nets.find_and_fix_disjoint_nets("GND", keep_only_main_net=True), list)
        assert isinstance(edbapp.nets.find_and_fix_disjoint_nets("GND", clean_disjoints_less_than=0.005), list)
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

    # def test_create_edb(self):
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
        out = edb.write_export3d_option_config_file(self.local_scratch, options_config)
        assert os.path.exists(out)
        out = edb.export_hfss(self.local_scratch)
        assert os.path.exists(out)
        edb.close()

    def test_export_to_q3d(self):
        """Export EDB to Q3D."""
        edb = Edb(
            edbpath=os.path.join(local_path, "example_models", test_subfolder, "simple.aedb"),
            edbversion=desktop_version,
        )
        options_config = {"UNITE_NETS": 1, "LAUNCH_Q3D": 0}
        out = edb.write_export3d_option_config_file(self.local_scratch, options_config)
        assert os.path.exists(out)
        out = edb.export_q3d(self.local_scratch, net_list=["ANALOG_A0", "ANALOG_A1", "ANALOG_A2"], hidden=True)
        assert os.path.exists(out)
        edb.close()

    def test_074_export_to_maxwell(self):
        """Export EDB to Maxwell 3D."""
        edb = Edb(
            edbpath=os.path.join(local_path, "example_models", test_subfolder, "simple.aedb"),
            edbversion=desktop_version,
        )
        options_config = {"UNITE_NETS": 1, "LAUNCH_MAXWELL": 0}
        out = edb.write_export3d_option_config_file(self.local_scratch, options_config)
        assert os.path.exists(out)
        out = edb.export_maxwell(self.local_scratch, num_cores=6)
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
        edb.close()

    def test_hfss_set_bounding_box_extent(self):
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
