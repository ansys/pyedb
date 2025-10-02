# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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

import os

import pytest

from pyedb.dotnet.database.edb_data.simulation_configuration import (
    SimulationConfiguration,
)
from pyedb.generic.constants import SolverType
from pyedb.generic.design_types import Edb
from tests.conftest import desktop_version, local_path, test_subfolder
from tests.system.base_test_class import BaseTestClass

pytestmark = [pytest.mark.system, pytest.mark.legacy]


class TestClass(BaseTestClass):
    @pytest.fixture(autouse=True)
    def init(self, local_scratch, target_path, target_path2, target_path4):
        self.local_scratch = local_scratch
        self.target_path = target_path
        self.target_path2 = target_path2
        self.target_path4 = target_path4

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

        edb.close(terminate_rpc_session=False)

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
        edbapp.close(terminate_rpc_session=False)

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
        edbapp.close(terminate_rpc_session=False)

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
        edb.close(terminate_rpc_session=False)

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
        edb.close(terminate_rpc_session=False)

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
        edbapp.close(terminate_rpc_session=False)

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
        assert not port1.deembed
        assert port1.impedance == 50.0
        assert not port1.is_circuit_port
        assert not port1.renormalize
        assert port1.renormalize_z0 == (50.0, 0.0)
        assert not port1.get_pin_group_terminal_reference_pin()
        assert not port1.get_pad_edge_terminal_reference_pin()
        edbapp.close(terminate_rpc_session=False)

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
        edbapp.close()

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
        edbapp.close(terminate_rpc_session=False)
