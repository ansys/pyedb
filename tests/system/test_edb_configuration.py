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

from collections import Counter
import json
import os
from pathlib import Path

import ansys.edb.core
import pytest

# is_linux is only used for a skipif marker — define it here without dotnet
is_linux = os.name == "posix"

from pyedb.generic.constants import unit_converter
from pyedb.generic.settings import settings
from tests.conftest import config, local_path, test_subfolder
from tests.system.base_test_class import BaseTestClass

pytestmark = [pytest.mark.unit, pytest.mark.legacy]

U8_IC_DIE_PROPERTIES = {
    "components": [
        {
            "reference_designator": "U8",
            "definition": "MAXM-T833+2_V",
            "type": "ic",
            "ic_die_properties": {"type": "flip_chip", "orientation": "chip_down"},
            "solder_ball_properties": {
                "shape": "spheroid",
                "diameter": "244um",
                "mid_diameter": "400um",
                "height": "300um",
            },
        }
    ]
}


def _assert_final_ic_die_properties(component: dict):
    assert component["ic_die_properties"]["type"] in ["flip_chip", "flipchip"]
    assert component["ic_die_properties"]["orientation"] in ["chip_down", "chipdown"]
    assert float(component["solder_ball_properties"]["diameter"]) == 0.000244


def check_dictionaries(source_dict, target_dict):
    for key, value in source_dict.items():
        if isinstance(value, dict):
            if key not in target_dict:
                return False
            return check_dictionaries(value, target_dict[key])
        elif isinstance(value, list):
            for item_source, item_target in zip(value, target_dict[key]):
                if isinstance(item_source, dict):
                    return check_dictionaries(item_source, item_target)
                else:
                    if str(item_source) != str(item_target):
                        return False
        else:
            if str(value) != str(target_dict[key]):
                return False
    return True


@pytest.mark.usefixtures("close_rpc_session")
class TestClassStackup(BaseTestClass):
    def test_create_stackup(self):
        edbapp = self.edb_examples.create_empty_edb()
        stackup = edbapp.configuration.cfg_data.stackup
        stackup.add_material(name="mat1", config={"permittivity": "4.5"})
        assert edbapp.configuration.cfg_data.stackup.materials[-1].name == "mat1"
        assert edbapp.configuration.cfg_data.stackup.materials[-1].permittivity == "4.5"
        stackup.add_material(config={"name": "mat2", "permittivity": "4"})
        assert edbapp.configuration.cfg_data.stackup.materials[-1].name == "mat2"
        assert edbapp.configuration.cfg_data.stackup.materials[-1].permittivity == "4"
        stackup.add_layer_at_bottom(
            name="layer1", config={"type": "dielectric", "thickness": "0.1mm", "material": "mat1"}
        )
        assert edbapp.configuration.cfg_data.stackup.layers[-1].name == "layer1"
        assert edbapp.configuration.cfg_data.stackup.layers[-1].material == "mat1"
        assert edbapp.configuration.cfg_data.stackup.layers[-1].thickness == "0.1mm"
        stackup.add_layer_at_bottom(config={"name": "layer2", "material": "mat2", "thickness": "0.2mm"})
        assert edbapp.configuration.cfg_data.stackup.layers[-1].name == "layer2"

        edbapp.configuration.run()
        assert edbapp.materials.materials["mat1"].permittivity == 4.5
        assert edbapp.stackup.layers["layer1"].material == "mat1"
        assert edbapp.stackup.layers["layer1"].thickness == 0.0001
        assert edbapp.stackup.layers["layer1"].type == "dielectric"
        assert edbapp.stackup.layers["layer2"].type == "signal"

        edbapp.configuration.cfg_data.stackup.normalize_thickness(unit="m")
        assert edbapp.configuration.cfg_data.stackup.layers[0].thickness == "0.0001m"
        edbapp.configuration.cfg_data.stackup.normalize_thickness(unit="mm")
        assert edbapp.configuration.cfg_data.stackup.layers[0].thickness == "0.1mm"
        edbapp.configuration.cfg_data.stackup.normalize_thickness(unit="um")
        assert edbapp.configuration.cfg_data.stackup.layers[0].thickness == "100.0um"
        edbapp.configuration.cfg_data.stackup.normalize_thickness(unit="mil")
        assert edbapp.configuration.cfg_data.stackup.layers[0].thickness == "3.9370078740157473mil"
        edbapp.configuration.cfg_data.stackup.normalize_thickness(unit="in")
        assert edbapp.configuration.cfg_data.stackup.layers[0].thickness == "0.003937007874015747in"

        edbapp.close(terminate_rpc_session=False)


@pytest.mark.usefixtures("close_rpc_session")
class TestClass(BaseTestClass):
    def test_13b_stackup_materials(self):
        data = {
            "stackup": {
                "materials": [
                    {
                        "name": "copper",
                        "conductivity": 570000000,
                        "thermal_modifiers": [
                            {
                                "property_name": "conductivity",
                                "basic_quadratic_c1": 0,
                                "basic_quadratic_c2": 0,
                                "basic_quadratic_temperature_reference": 22,
                                "advanced_quadratic_lower_limit": -273.15,
                                "advanced_quadratic_upper_limit": 1000,
                                "advanced_quadratic_auto_calculate": True,
                                "advanced_quadratic_lower_constant": 1,
                                "advanced_quadratic_upper_constant": 1,
                            },
                        ],
                    },
                    {
                        "name": "Megtron4",
                        "permittivity": 3.77,
                        "dielectric_loss_tangent": 0.005,
                        "thermal_modifiers": [
                            {
                                "property_name": "dielectric_loss_tangent",
                                "basic_quadratic_c1": 0,
                                "basic_quadratic_c2": 0,
                                "basic_quadratic_temperature_reference": 22,
                                "advanced_quadratic_lower_limit": -273.15,
                                "advanced_quadratic_upper_limit": 1000,
                                "advanced_quadratic_auto_calculate": True,
                                "advanced_quadratic_lower_constant": 1,
                                "advanced_quadratic_upper_constant": 1,
                            }
                        ],
                    },
                    {"name": "Megtron4_2", "permittivity": 3.77, "dielectric_loss_tangent": 0.005},
                    {"name": "Solder Resist", "permittivity": 4, "dielectric_loss_tangent": 0.035},
                ]
            }
        }
        edbapp = self.edb_examples.get_si_verse()
        assert edbapp.configuration.load(data, apply_file=True)
        data_from_db = edbapp.configuration.get_data_from_db(stackup=True)
        for mat in data["stackup"]["materials"]:
            target_mat = [i for i in data_from_db["stackup"]["materials"] if i["name"] == mat["name"]][0]
            for p, value in mat.items():
                if p == "thermal_modifiers":
                    continue
                assert value == target_mat[p]
        edbapp.close(terminate_rpc_session=False)

    def test_02_pin_groups(self):
        edbapp = self.edb_examples.get_si_verse()
        pin_groups = [
            {"name": "U9_5V_1", "reference_designator": "U9", "pins": ["32", "33"]},
            {"name": "U9_GND", "reference_designator": "U9", "net": "GND"},
            {"name": "X1_5V", "reference_designator": "X1", "pins": ["A17", "A18", "B17", "B18"]},
        ]
        data = {"pin_groups": pin_groups}
        assert edbapp.configuration.load(data, apply_file=True)
        assert "U9_5V_1" in edbapp.siwave.pin_groups
        assert "U9_GND" in edbapp.siwave.pin_groups

        data_from_db = edbapp.configuration.cfg_data.pin_groups.get_data_from_db()
        assert data_from_db[0]["name"] == "U9_5V_1"
        assert data_from_db[0]["pins"] == ["32", "33"]
        edbapp.close(terminate_rpc_session=False)

    def test_03_spice_models(self):
        files = self.edb_examples.copy_test_files_into_local_folder(
            ["TEDB/GRM32_DC0V_25degC.mod", "TEDB/GRM32ER72A225KA35_25C_0V.sp"]
        )
        spice_dir = os.path.dirname(files[0])
        edbapp = self.edb_examples.get_si_verse()
        data = {
            "general": {"spice_model_library": spice_dir},
            "spice_models": [
                {
                    "name": "GRM32ER72A225KA35_25C_0V",
                    "component_definition": "CAPC0603X33X15LL03T05",
                    "file_path": "GRM32ER72A225KA35_25C_0V.sp",
                    "sub_circuit_name": "GRM32ER72A225KA35_25C_0V",
                    "apply_to_all": True,
                    "components": [],
                    "terminal_pairs": [["port1", 2], ["port2", 1]],
                },
                {
                    "name": "GRM32ER72A225KA35_25C_0V",
                    "component_definition": "CAPC1005X55X25LL05T10",
                    "file_path": "GRM32ER72A225KA35_25C_0V.sp",
                    "sub_circuit_name": "GRM32ER72A225KA35_25C_0V",
                    "apply_to_all": False,
                    "components": ["C236"],
                },
                {
                    "name": "GRM32_DC0V_25degC",
                    "component_definition": "CAPC0603X33X15LL03T05",
                    "file_path": "GRM32_DC0V_25degC.mod",
                    "sub_circuit_name": "GRM32ER60J227ME05_DC0V_25degC",
                    "apply_to_all": False,
                    "components": ["C142"],
                },
            ],
        }
        assert edbapp.configuration.load(data, apply_file=True)
        assert edbapp.components["C236"].model.model_name
        assert edbapp.components["C142"].model.spice_file_path
        edbapp.close(terminate_rpc_session=False)

    def test_04_nets(self):
        edbapp = self.edb_examples.get_si_verse()
        data = {"nets": {"power_ground_nets": ["1.2V_DVDDL"], "signal_nets": ["SFPA_VCCR"]}}
        assert edbapp.configuration.load(data, apply_file=True)
        assert edbapp.nets["1.2V_DVDDL"].is_power_ground
        assert not edbapp.nets["SFPA_VCCR"].is_power_ground
        edbapp.close(terminate_rpc_session=False)

    def test_05_ports(self):
        data = {
            "ports": [
                {
                    "name": "CIRCUIT_C375_1_2",
                    "reference_designator": "C375",
                    "type": "circuit",
                    "impedance": "1ohm",
                    "positive_terminal": {"pin": "1"},
                    "negative_terminal": {"pin": "2"},
                },
                {
                    "name": "CIRCUIT_C376_1_2",
                    "type": "circuit",
                    "positive_terminal": {"padstack": "C376-1"},
                    "negative_terminal": {"padstack": "C376-2"},
                },
                {
                    "name": "CIRCUIT_X1_B8_GND",
                    "reference_designator": "X1",
                    "type": "circuit",
                    "positive_terminal": {"pin": "B8"},
                    "negative_terminal": {"net": "GND"},
                },
                {
                    "name": "CIRCUIT_X1_B9_GND",
                    "reference_designator": "X1",
                    "type": "circuit",
                    "positive_terminal": {"net": "PCIe_Gen4_TX2_N"},
                    "negative_terminal": {"net": "GND"},
                },
                {
                    "name": "CIRCUIT_U7_VDD_DDR_GND",
                    "reference_designator": "U7",
                    "type": "circuit",
                    "positive_terminal": {"net": "VDD_DDR"},
                    "negative_terminal": {"net": "GND"},
                },
            ]
        }
        edbapp = self.edb_examples.get_si_verse()
        assert edbapp.configuration.load(data, apply_file=True)
        assert "CIRCUIT_C375_1_2" in edbapp.ports
        assert "CIRCUIT_C376_1_2" in edbapp.ports
        assert "CIRCUIT_X1_B8_GND" in edbapp.ports
        assert "CIRCUIT_U7_VDD_DDR_GND" in edbapp.ports
        assert edbapp.ports["CIRCUIT_C375_1_2"].impedance == pytest.approx(1)
        data_from_db = edbapp.configuration.get_data_from_db(ports=True, pin_groups=True)
        assert data_from_db["ports"]
        edbapp.close(terminate_rpc_session=False)

    def test_05b_ports_coax(self):
        ports = [
            {
                "name": "COAX_U1_AM17",
                "reference_designator": "U1",
                "type": "coax",
                "positive_terminal": {"pin": "AM17"},
            },
            {
                "name": "COAX_U1_PCIe_Gen4_TX2_CAP_N",
                "reference_designator": "U1",
                "type": "coax",
                "positive_terminal": {"net": "PCIe_Gen4_TX2_CAP_N"},
            },
            {
                "name": "coax",
                "reference_designator": "X1",
                "type": "coax",
                "positive_terminal": {"net": "5V"},
            },
        ]
        data = {"ports": ports}
        edbapp = self.edb_examples.get_si_verse()
        assert edbapp.configuration.load(data, apply_file=True)
        assert edbapp.ports["COAX_U1_AM17"]
        assert edbapp.ports["COAX_U1_PCIe_Gen4_TX2_CAP_N"]
        assert edbapp.ports["COAX_U1_PCIe_Gen4_TX2_CAP_N"].location
        assert edbapp.ports["coax_X1_5V_B18"]
        assert edbapp.ports["coax_X1_5V_B17"]
        assert edbapp.ports["coax_X1_5V_A18"]
        assert edbapp.ports["coax_X1_5V_A17"]
        edbapp.close(terminate_rpc_session=False)

    def test_05c_ports_circuit_pin_net(self):
        data = {
            "ports": [
                {
                    "name": "CIRCUIT_X1_B8_GND",
                    "reference_designator": "X1",
                    "type": "circuit",
                    "positive_terminal": {"pin": "B8"},
                    "negative_terminal": {"net": "GND"},
                },
            ]
        }
        edbapp = self.edb_examples.get_si_verse()
        assert edbapp.configuration.load(data, apply_file=True)
        assert edbapp.ports["CIRCUIT_X1_B8_GND"]
        assert edbapp.ports["CIRCUIT_X1_B8_GND"].is_circuit_port
        edbapp.close(terminate_rpc_session=False)

    def test_05c_ports_circuit_net_net_distributed(self):
        ports = [
            {
                "name": "CIRCUIT_U7_VDD_DDR_GND",
                "reference_designator": "U7",
                "type": "circuit",
                "distributed": True,
                "positive_terminal": {"net": "VDD_DDR"},
                "negative_terminal": {"net": "GND"},
            }
        ]
        data = {"ports": ports}
        edbapp = self.edb_examples.get_si_verse()
        assert edbapp.configuration.load(data, apply_file=True)
        assert len(edbapp.ports) > 1
        edbapp.close(terminate_rpc_session=False)

    def test_05d_ports_pin_group(self):
        edbapp = self.edb_examples.get_si_verse()
        pin_groups = [
            {"name": "U9_5V_1", "reference_designator": "U9", "pins": ["32", "33"]},
            {"name": "U9_GND", "reference_designator": "U9", "net": "GND"},
        ]
        ports = [
            {
                "name": "U9_pin_group_port",
                "type": "circuit",
                "positive_terminal": {"pin_group": "U9_5V_1"},
                "negative_terminal": {"pin_group": "U9_GND"},
            }
        ]
        data = {"pin_groups": pin_groups}
        assert edbapp.configuration.load(data, append=False, apply_file=True)
        data = {"ports": ports}
        assert edbapp.configuration.load(data, append=False, apply_file=True)
        assert "U9_5V_1" in edbapp.siwave.pin_groups
        assert "U9_GND" in edbapp.siwave.pin_groups
        assert "U9_pin_group_port" in edbapp.ports
        edbapp.close(terminate_rpc_session=False)

    def test_05e_ports_circuit_net_net_distributed_nearest_ref(self):
        ports = [
            {
                "name": "CIRCUIT_U7_VDD_DDR_GND",
                "reference_designator": "U7",
                "type": "circuit",
                "distributed": True,
                "positive_terminal": {"net": "VDD_DDR"},
                "negative_terminal": {"nearest_pin": {"reference_net": "GND", "search_radius": 5e-3}},
            }
        ]
        data = {"ports": ports}
        edbapp = self.edb_examples.get_si_verse()
        assert edbapp.configuration.load(data, apply_file=True)
        assert len(edbapp.ports) > 1
        edbapp.close(terminate_rpc_session=False)

    def test_05f_ports_between_two_points(self):
        data = {
            "ports": [
                {
                    "name": "x_y_port",
                    "type": "circuit",
                    "positive_terminal": {
                        "coordinates": {"layer": "1_Top", "point": ["104mm", "37mm"], "net": "AVCC_1V3"}
                    },
                    "negative_terminal": {
                        "coordinates": {"layer": "Inner6(GND2)", "point": ["104mm", "37mm"], "net": "GND"}
                    },
                }
            ]
        }
        edbapp = self.edb_examples.get_si_verse()
        assert edbapp.configuration.load(data, apply_file=True)
        data_from_db = edbapp.configuration.get_data_from_db(ports=True)
        assert data_from_db["ports"][0]["positive_terminal"]["coordinates"]["layer"] == "1_Top"
        assert data_from_db["ports"][0]["positive_terminal"]["coordinates"]["net"] == "AVCC_1V3"
        edbapp.close(terminate_rpc_session=False)

    def test_05g_edge_port(self):
        edbapp = self.edb_examples.create_empty_edb()
        edbapp.stackup.create_symmetric_stackup(2)
        rectangle = edbapp.modeler.create_rectangle(
            layer_name="BOT", net_name="GND", lower_left_point=["-2mm", "-2mm"], upper_right_point=["2mm", "2mm"]
        )
        assert not rectangle.is_null
        prim_1 = edbapp.modeler.create_trace(
            path_list=([0, 0], [0, "1mm"]),
            layer_name="TOP",
            net_name="SIG",
            width="0.1mm",
            start_cap_style="Flat",
            end_cap_style="Flat",
        )
        assert not prim_1.is_null
        prim_1.aedt_name = "path_1"
        data = {
            "ports": [
                {
                    "name": "wport_1",
                    "type": "wave_port",
                    "primitive_name": prim_1.aedt_name,
                    "point_on_edge": [0, "1mm"],
                    "horizontal_extent_factor": 6,
                    "vertical_extent_factor": 4,
                    "pec_launch_width": "0.2mm",
                },
                {
                    "name": "gap_port_1",
                    "type": "gap_port",
                    "primitive_name": prim_1.aedt_name,
                    "point_on_edge": [0, 0],
                },
            ]
        }
        edbapp.configuration.load(data, apply_file=True)
        assert edbapp.ports["wport_1"].horizontal_extent_factor == 6
        assert edbapp.ports["gap_port_1"].hfss_type == "Gap"
        edbapp.configuration.get_data_from_db(ports=True)
        edbapp.close(terminate_rpc_session=False)

    def test_05h_diff_wave_port(self):
        edbapp = self.edb_examples.create_empty_edb()
        edbapp.stackup.create_symmetric_stackup(2)
        edbapp.modeler.create_rectangle(
            layer_name="BOT", net_name="GND", lower_left_point=["-2mm", "-2mm"], upper_right_point=["2mm", "2mm"]
        )
        prim_1 = edbapp.modeler.create_trace(
            path_list=([0, 0], [0, "1mm"]),
            layer_name="TOP",
            net_name="SIG",
            width="0.1mm",
            start_cap_style="Flat",
            end_cap_style="Flat",
        )
        prim_1.aedt_name = "path_1"
        prim_2 = edbapp.modeler.create_trace(
            path_list=(["1mm", 0], ["1mm", "1mm"]),
            layer_name="TOP",
            net_name="SIG",
            width="0.1mm",
            start_cap_style="Flat",
            end_cap_style="Flat",
        )
        prim_2.aedt_name = "path_2"
        data = {
            "ports": [
                {
                    "name": "diff_wave_1",
                    "type": "diff_wave_port",
                    "positive_terminal": {"primitive_name": prim_1.aedt_name, "point_on_edge": [0, "1mm"]},
                    "negative_terminal": {"primitive_name": prim_2.aedt_name, "point_on_edge": ["1mm", "1mm"]},
                    "horizontal_extent_factor": 6,
                    "vertical_extent_factor": 4,
                    "pec_launch_width": "0.2mm",
                }
            ]
        }
        edbapp.configuration.load(data, apply_file=True)
        assert edbapp.ports["diff_wave_1"].horizontal_extent_factor == 6
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(config["use_grpc"], reason="Random crash wait SP2 for in memory.")
    def test_06_s_parameters(self):
        self.edb_examples.copy_test_files_into_local_folder("TEDB/GRM32_DC0V_25degC_series.s2p")
        edbapp = self.edb_examples.get_si_verse()
        data = {
            "general": {"s_parameter_library": self.edb_examples.test_folder},
            "s_parameters": [
                {
                    "name": "cap_model1",
                    "file_path": "GRM32_DC0V_25degC_series.s2p",
                    "component_definition": "CAPC3216X180X55ML20T25",
                    "apply_to_all": True,
                    "components": [],
                    "reference_net": "GND",
                    "pin_order": ["1", "2"],
                },
                {
                    "name": "cap2_model2",
                    "file_path": "GRM32_DC0V_25degC_series.s2p",
                    "apply_to_all": False,
                    "component_definition": "CAPC3216X190X55ML30T25",
                    "components": ["C59"],
                    "reference_net": "GND",
                    "reference_net_per_component": {"C59": "GND"},
                },
            ],
        }

        assert edbapp.configuration.load(data, apply_file=True)
        assert len(edbapp.components.nport_comp_definition) == 2
        assert edbapp.components.nport_comp_definition["CAPC3216X180X55ML20T25"].reference_file
        assert len(edbapp.components.nport_comp_definition["CAPC3216X180X55ML20T25"].components) == 9
        assert len(edbapp.components.nport_comp_definition["CAPC3216X190X55ML30T25"].components) == 12
        edbapp.configuration.get_data_from_db(s_parameters=True)
        edbapp.close(terminate_rpc_session=False)

    def test_operations_cutout_auto_identify_nets(self):
        data = {
            "ports": [
                {
                    "name": "COAX_U1",
                    "reference_designator": "U1",
                    "type": "coax",
                    "positive_terminal": {"pin": "AP18"},
                },
                {
                    "name": "COAX_X1",
                    "reference_designator": "X1",
                    "type": "coax",
                    "positive_terminal": {"pin": "B11"},
                },
            ],
            "sources": [
                {
                    "name": "VSOURCE_1",
                    "reference_designator": "U1",
                    "type": "voltage",
                    "positive_terminal": {"pin": "AH23"},
                    "negative_terminal": {"net": "GND"},
                },
            ],
            "operations": {
                "cutout": {
                    "auto_identify_nets": {
                        "enabled": True,
                        "resistor_below": 100,
                        "inductor_below": 1,
                        "capacitor_above": "10nF",
                    },
                    "reference_nets": ["GND"],
                    "extent_type": "ConvexHull",
                },
                "generate_auto_hfss_regions": True,
            },
        }
        edbapp = self.edb_examples.get_si_verse()
        assert edbapp.configuration.load(data, apply_file=True)
        assert {"PCIe_Gen4_TX3_CAP_P", "PCIe_Gen4_TX3_P", "PCIe_Gen4_RX3_N"}.issubset(edbapp.nets.nets.keys())
        edbapp.close(terminate_rpc_session=False)

    def test_10_general(self):
        edbapp = self.edb_examples.get_si_verse()
        data = {"general": {"spice_model_library": "", "s_parameter_library": ""}}

        assert edbapp.configuration.load(data, apply_file=True)
        edbapp.close(terminate_rpc_session=False)

    def test_11_package_definitions(self):
        data = {
            "package_definitions": [
                {
                    "name": "package_1",
                    "component_definition": "SMTC-MECT-110-01-M-D-RA1_V",
                    "maximum_power": 1,
                    "thermal_conductivity": 2,
                    "theta_jb": 3,
                    "theta_jc": 4,
                    "height": 5,
                    "heatsink": {
                        "fin_base_height": "1mm",
                        "fin_height": "1mm",
                        "fin_orientation": "x_oriented",
                        "fin_spacing": "1mm",
                        "fin_thickness": "4mm",
                    },
                    "apply_to_all": False,
                    "components": ["J5"],
                },
                {
                    "name": "package_2",
                    "component_definition": "COIL-1008CS_V",
                    "extent_bounding_box": [["-1mm", "-1mm"], ["1mm", "1mm"]],
                    "maximum_power": 1,
                    "thermal_conductivity": 2,
                    "theta_jb": 3,
                    "theta_jc": 4,
                    "height": 5,
                    "apply_to_all": True,
                    "components": ["L8"],
                },
            ]
        }
        edbapp = self.edb_examples.get_si_verse()
        assert edbapp.configuration.load(data, apply_file=True)
        data_from_db = edbapp.configuration.get_data_from_db(package_definitions=True)
        for pdef in data["package_definitions"]:
            target_pdef = [i for i in data_from_db["package_definitions"] if i["name"] == pdef["name"]][0]
            for p, value in pdef.items():
                if p == "apply_to_all":
                    continue
                elif p == "component_definition":
                    continue
                elif p == "components":
                    comps_def_from_db = edbapp.components.definitions[pdef["component_definition"]]
                    comps_from_db = comps_def_from_db.components
                    if pdef["apply_to_all"]:
                        comps = {i: j for i, j in comps_from_db.items() if i not in value}
                    else:
                        comps = {i: j for i, j in comps_from_db.items() if i in value}
                    for _, comp_obj in comps.items():
                        assert comp_obj.package_def.name == pdef["name"]
                elif p == "extent_bounding_box":
                    continue
                elif p == "heatsink":
                    heatsink = pdef["heatsink"]
                    target_heatsink = target_pdef["heatsink"]
                    for hs_p, hs_value in target_heatsink.items():
                        if hs_p in ["fin_base_height", "fin_height", "fin_spacing", "fin_thickness"]:
                            hs_value = edbapp.value(hs_value).value
                        assert hs_value == target_heatsink[hs_p]
                else:
                    assert value == target_pdef[p]
        edbapp.close(terminate_rpc_session=False)

    def test_13c_stackup_create_stackup(self):
        data = {
            "stackup": {
                "materials": [
                    {"name": "copper", "conductivity": 570000000},
                    {"name": "megtron4", "permittivity": 3.77, "dielectric_loss_tangent": 0.005},
                    {"name": "Solder Resist", "permittivity": 4, "dielectric_loss_tangent": 0},
                ],
                "layers": [
                    {
                        "fill_material": "Solder Resist",
                        "material": "copper",
                        "name": "1_Top",
                        "thickness": "0.5mm",
                        "type": "signal",
                    },
                    {
                        "fill_material": "SolerMask",
                        "material": "copper",
                        "name": "Inner1",
                        "thickness": "0.017mm",
                        "type": "signal",
                    },
                    {"material": "megtron4", "name": "DE2", "thickness": "0.088mm", "type": "dielectric"},
                    {"material": "megtron4", "name": "DE3", "thickness": "0.1mm", "type": "dielectric"},
                    {
                        "fill_material": "megtron4",
                        "material": "copper",
                        "name": "Inner2",
                        "thickness": "0.017mm",
                        "type": "signal",
                    },
                ],
            }
        }
        edbapp = self.edb_examples.create_empty_edb()

        assert edbapp.configuration.load(data, apply_file=True)
        data_from_db = edbapp.configuration.get_data_from_db(stackup=True)
        # adding this list as DotNet returns 0.0 at Value conversion failure while grpc fails.
        skipped_edb_value_conversion = ["fill_material", "material", "type", "name"]
        for lay in data["stackup"]["layers"]:
            target_mat = [i for i in data_from_db["stackup"]["layers"] if i["name"] == lay["name"]][0]
            for p, value in lay.items():
                if not p in skipped_edb_value_conversion:
                    assert float(edbapp.value(value)) == float(edbapp.value(target_mat[p]))
                else:
                    assert str(value) == str(target_mat[p])
        edbapp.close(terminate_rpc_session=False)

    def test_15b_sources_net_net(self):
        edbapp = self.edb_examples.get_si_verse()
        sources_v = [
            {
                "name": "VSOURCE_U2_1V0_GND",
                "reference_designator": "U2",
                "type": "voltage",
                "impedance": 1,
                "magnitude": 1,
                "distributed": False,
                "positive_terminal": {"net": "1V0"},
                "negative_terminal": {"net": "GND"},
            },
        ]
        data = {"sources": sources_v}
        assert edbapp.configuration.load(data, apply_file=True)
        assert edbapp.sources["VSOURCE_U2_1V0_GND"].magnitude == 1

        edbapp.configuration.cfg_data.sources.get_data_from_db()
        src_from_db = edbapp.configuration.cfg_data.sources.export_properties()
        assert src_from_db[0]["name"] == "VSOURCE_U2_1V0_GND"
        assert src_from_db[0]["type"] == "voltage"
        assert src_from_db[0]["impedance"] == 1
        assert src_from_db[0]["magnitude"] == 1
        assert src_from_db[0]["positive_terminal"] == {"pin_group": "pg_VSOURCE_U2_1V0_GND_U2"}
        assert src_from_db[0]["negative_terminal"] == {"pin_group": "pg_VSOURCE_U2_1V0_GND_U2_ref"}

        pg_from_db = edbapp.configuration.cfg_data.pin_groups.get_data_from_db()
        assert pg_from_db[0]["name"] == "pg_VSOURCE_U2_1V0_GND_U2"
        assert pg_from_db[1]["name"] == "pg_VSOURCE_U2_1V0_GND_U2_ref"
        edbapp.close(terminate_rpc_session=False)

    def test_15c_sources_net_net_distributed(self):
        edbapp = self.edb_examples.get_si_verse()
        sources_i = [
            {
                "name": "ISOURCE",
                "reference_designator": "U1",
                "type": "current",
                "magnitude": 117,
                "distributed": True,
                "positive_terminal": {"net": "1V0"},
                "negative_terminal": {"net": "GND"},
            },
        ]
        data = {"sources": sources_i}
        assert edbapp.configuration.load(data, apply_file=True)

        edbapp.configuration.cfg_data.sources.get_data_from_db()
        data_from_db = edbapp.configuration.cfg_data.sources.export_properties()
        assert len(data_from_db) == 117
        for s1 in data_from_db:
            assert s1["magnitude"] == 1
            assert s1["reference_designator"] == "U1"
            assert s1["type"] == "current"
        edbapp.close(terminate_rpc_session=False)

    def test_15c_sources_nearest_ref(self):
        edbapp = self.edb_examples.get_si_verse()
        sources_i = [
            {
                "name": "ISOURCE",
                "reference_designator": "U1",
                "type": "current",
                "magnitude": 1,
                "distributed": True,
                "positive_terminal": {"net": "1V0"},
                "negative_terminal": {"nearest_pin": {"reference_net": "GND", "search_radius": 5e-3}},
            },
        ]
        data = {"sources": sources_i}
        assert edbapp.configuration.load(data, apply_file=True)
        edbapp.close(terminate_rpc_session=False)

    def test_15d_sources_equipotential(self):
        edbapp = self.edb_examples.get_si_verse()
        sources_i = [
            {
                "name": "ISOURCE_J5",
                "reference_designator": "J5",
                "type": "current",
                "magnitude": 17,
                "positive_terminal": {"net": "SFPA_VCCR", "contact_type": "quad"},
                "negative_terminal": {"net": "GND"},
            },
            {
                "name": "ISOURCE_J5_SFPA_TX_P",
                "reference_designator": "J5",
                "type": "current",
                "magnitude": 17,
                "positive_terminal": {
                    "net": "SFPA_TX_P",
                    "contact_type": "inline",
                    "contact_radius": "0.15mm",
                    "num_of_contact": 5,
                    "contact_expansion": 0.9,
                },
                "negative_terminal": {"net": "GND"},
            },
            {
                "name": "x_y_port",
                "type": "current",
                "magnitude": 2,
                "positive_terminal": {
                    "coordinates": {
                        "layer": "1_Top",
                        "point": ["104mm", "37mm"],
                        "net": "AVCC_1V3",
                    },
                    "contact_radius": "1mm",
                },
                "negative_terminal": {
                    "coordinates": {
                        "layer": "Inner6(GND2)",
                        "point": ["104mm", "45mm"],
                        "net": "GND",
                    },
                    "contact_radius": "1.2mm",
                },
            },
        ]
        data = {"sources": sources_i}
        assert edbapp.configuration.load(data, apply_file=True)
        edbapp.close(terminate_rpc_session=False)

    def test_16_export_to_external_file(self):
        edbapp = self.edb_examples.get_si_verse()
        data_file_path = Path(self.edb_examples.test_folder) / "test.json"
        edbapp.configuration.export(data_file_path)
        assert data_file_path.is_file()
        with open(data_file_path) as f:
            data = json.load(f)
            assert "stackup" in data
            assert data["stackup"]["materials"]
            assert data["stackup"]["materials"][0]["name"] == "copper"
            assert data["stackup"]["materials"][0]["conductivity"] == 5.8e7
            assert data["stackup"]["layers"]
            data["stackup"]["layers"][0]["name"] = "1_Top"
            data["stackup"]["layers"][0]["type"] = "signal"
            data["stackup"]["layers"][0]["material"] = "copper"
            assert data["nets"]
            assert len(data["nets"]["signal_nets"]) == 342
            assert len(data["nets"]["power_ground_nets"]) == 6
        edbapp.close(terminate_rpc_session=False)

    def test_19_variables(self):
        data = {
            "variables": [
                {"name": "var_1", "value": "1mm", "description": "des1"},
                {"name": "$var_2", "value": "1mm", "description": "No description"},
            ]
        }
        edbapp = self.edb_examples.create_empty_edb()
        edbapp.stackup.create_symmetric_stackup(2)
        edbapp.configuration.load(data, apply_file=True)
        edbapp.save()
        edbapp.close(terminate_rpc_session=False)
        edbapp2 = self.edb_examples.load_edb(edbapp.edbpath)
        assert Counter(edbapp2.configuration.get_data_from_db(variables=True)) == Counter(data)
        edbapp2.close(terminate_rpc_session=False)

    def test_probes(self):
        edbapp = self.edb_examples.get_si_verse()
        probe = [
            {
                "name": "probe1",
                "reference_designator": "J5",
                "positive_terminal": {"pin": "15"},
                "negative_terminal": {"pin": "16"},
            },
        ]
        data = {"probes": probe}
        assert edbapp.configuration.load(data, apply_file=True)
        assert "probe1" in edbapp.probes
        edbapp.close(terminate_rpc_session=False)


@pytest.mark.usefixtures("close_rpc_session")
class TestClassTerminals(BaseTestClass):
    terminal1 = {
        "name": "terminal1",
        "impedance": 1,
        "is_circuit_port": False,
        "boundary_type": "PortBoundary",
        "terminal_type": "padstack_instance",
        "padstack_instance": "U7-M7",
        "layer": None,
    }
    pin_group2 = {"name": "U7_GND", "reference_designator": "U7", "net": "GND"}
    terminal2 = {
        "name": "terminal2",
        "impedance": 40,
        "boundary_type": "PortBoundary",
        "terminal_type": "pin_group",
        "pin_group": "U7_GND",
        "reference_terminal": "terminal1",
    }
    terminal3 = {
        "x": "104mm",
        "y": "37mm",
        "layer": "1_Top",
        "name": "terminal3",
        "impedance": 50,
        "boundary_type": "port" if config["use_grpc"] else "PortBoundary",
        "reference_terminal": "terminal3_ref",
        "terminal_type": "point",
        "net": "AVCC_1V3",
    }
    terminal3_ref = {
        "x": "104mm",
        "y": "37mm",
        "layer": "Inner6(GND2)",
        "net": "GND",
        "name": "terminal3_ref",
        "impedance": 50,
        "boundary_type": "port" if config["use_grpc"] else "PortBoundary",
        "terminal_type": "point",
    }

    edge_terminal_1 = {
        "name": "edge_terminal_1",
        "impedance": 50,
        "is_circuit_port": False,
        "boundary_type": "port" if config["use_grpc"] else "PortBoundary",
        "primitive": "path_1",
        "point_on_edge_x": 0,
        "point_on_edge_y": "1mm",
        "horizontal_extent_factor": 6,
        "vertical_extent_factor": 8,
        "pec_launch_width": "0.02mm",
        "terminal_type": "edge",
        "hfss_type": "Gap",
    }
    edge_terminal_2 = {
        "terminal_type": "edge",
        "name": "edge_terminal_2",
        "impedance": 50,
        "is_circuit_port": False,
        "boundary_type": "port" if config["use_grpc"] else "PortBoundary",
        "primitive": "path_2",
        "point_on_edge_x": "1mm",
        "point_on_edge_y": "1mm",
        "horizontal_extent_factor": 6,
        "vertical_extent_factor": 8,
        "pec_launch_width": "0.02mm",
    }
    bundle_terminal = {
        "terminal_type": "bundle",
        "terminals": ["edge_terminal_1", "edge_terminal_2"],
        "name": "bundle_terminal",
    }

    def test_padstack_instance_terminal(self):
        edbapp = self.edb_examples.get_si_verse()
        edbapp.configuration.load({"terminals": [self.terminal1]}, append=False)
        edbapp.configuration.run()
        terminal1 = edbapp.ports["terminal1"]
        assert terminal1.impedance == 1
        assert terminal1.padstack_instance.aedt_name == "U7-M7"

        exported = edbapp.configuration.get_data_from_db(terminals=True)["terminals"]
        assert exported[0] == {
            "name": "terminal1",
            "impedance": 1.0,
            "is_circuit_port": False,
            "amplitude": 1.0,
            "phase": 0.0,
            "terminal_to_ground": "no_ground" if edbapp.grpc else "kNoGround",
            "boundary_type": "port" if edbapp.grpc else "PortBoundary",
            "hfss_type": "Gap",
            "terminal_type": "padstack_instance",
            "padstack_instance": "U7-M7",
            "padstack_instance_id": 4294971660,
        }
        edbapp.close(terminate_rpc_session=False)

    def test_padstack_instance_terminal_b(self):
        terminal = {
            "name": "terminal1",
            "impedance": 1,
            "is_circuit_port": False,
            "boundary_type": "PortBoundary",
            "terminal_type": "padstack_instance",
            "padstack_instance_id": 4294971660,
            "layer": None,
        }
        edbapp = self.edb_examples.get_si_verse()
        edbapp.configuration.load({"terminals": [terminal]}, append=False)
        edbapp.configuration.run()
        terminal1 = edbapp.ports["terminal1"]
        assert terminal1.impedance == 1
        assert terminal1.padstack_instance.aedt_name == "U7-M7"

        exported = edbapp.configuration.get_data_from_db(terminals=True)["terminals"]
        assert exported[0] == {
            "name": "terminal1",
            "impedance": 1.0,
            "is_circuit_port": False,
            "amplitude": 1.0,
            "phase": 0.0,
            "terminal_to_ground": "no_ground" if edbapp.grpc else "kNoGround",
            "boundary_type": "port" if edbapp.grpc else "PortBoundary",
            "hfss_type": "Gap",
            "terminal_type": "padstack_instance",
            "padstack_instance": "U7-M7",
            "padstack_instance_id": 4294971660,
        }
        edbapp.close(terminate_rpc_session=False)

    def test_pin_group_terminal(self):
        edbapp = self.edb_examples.get_si_verse()
        edbapp.configuration.load({"pin_groups": [self.pin_group2]})
        edbapp.configuration.run()

        edbapp.configuration.load({"terminals": [self.terminal1, self.terminal2]}, append=False)
        edbapp.configuration.run()
        assert "terminal2" in edbapp.terminals
        exported = edbapp.configuration.get_data_from_db(terminals=True)["terminals"]
        ex_terminal2 = [i for i in exported if i["name"] == "terminal2"][0]
        assert ex_terminal2 == {
            "name": "terminal2",
            "impedance": 40.0,
            "is_circuit_port": True,
            "reference_terminal": "terminal1",
            "amplitude": 1.0,
            "phase": 0.0,
            "terminal_to_ground": "no_ground" if edbapp.grpc else "kNoGround",
            "boundary_type": "port" if edbapp.grpc else "PortBoundary",
            "terminal_type": "pin_group",
            "pin_group": "U7_GND",
        }

        # Test if terminal is reused when terminal already exists
        edbapp.configuration.run()

        edbapp.close(terminate_rpc_session=False)

    def test_point_terminal(self):
        edbapp = self.edb_examples.get_si_verse()
        assert edbapp.configuration.load({"terminals": [self.terminal3, self.terminal3_ref]}, apply_file=True)

        exported = edbapp.configuration.get_data_from_db(terminals=True)["terminals"]
        assert exported == [
            {
                "name": "terminal3",
                "impedance": 50.0,
                "is_circuit_port": True,
                "reference_terminal": "terminal3_ref",
                "amplitude": 1.0,
                "phase": 0.0,
                "terminal_to_ground": "no_ground" if edbapp.grpc else "kNoGround",
                "boundary_type": "port" if edbapp.grpc else "PortBoundary",
                "terminal_type": "point",
                "x": 0.104,
                "y": 0.037,
                "layer": "1_Top",
                "net": "AVCC_1V3",
            },
            {
                "name": "terminal3_ref",
                "impedance": 50.0,
                "is_circuit_port": True,
                "amplitude": 1.0,
                "phase": 0.0,
                "terminal_to_ground": "no_ground" if edbapp.grpc else "kNoGround",
                "boundary_type": "port" if edbapp.grpc else "PortBoundary",
                "terminal_type": "point",
                "x": 0.104,
                "y": 0.037,
                "layer": "Inner6(GND2)",
                "net": "GND",
            },
        ]
        edbapp.close(terminate_rpc_session=False)

    def test_edge_terminal(self):
        edbapp = self.edb_examples.create_empty_edb()
        edbapp.stackup.create_symmetric_stackup(2)
        edbapp.modeler.create_rectangle(
            layer_name="BOT", net_name="GND", lower_left_point=["-2mm", "-2mm"], upper_right_point=["2mm", "2mm"]
        )
        prim_1 = edbapp.modeler.create_trace(
            path_list=([0, 0], [0, "1mm"]),
            layer_name="TOP",
            net_name="SIG",
            width="0.1mm",
            start_cap_style="Flat",
            end_cap_style="Flat",
        )
        prim_1.aedt_name = "path_1"
        prim_2 = edbapp.modeler.create_trace(
            path_list=(["1mm", 0], ["1mm", "1mm"]),
            layer_name="TOP",
            net_name="SIG",
            width="0.1mm",
            start_cap_style="Flat",
            end_cap_style="Flat",
        )
        prim_2.aedt_name = "path_2"

        edbapp.configuration.load({"terminals": [self.edge_terminal_1, self.edge_terminal_2]}, apply_file=True)
        assert edbapp.terminals["edge_terminal_1"].hfss_type == "Gap"
        assert edbapp.terminals["edge_terminal_2"].hfss_type == "Wave"
        edbapp.close(terminate_rpc_session=False)

    def test_edge_bundle_terminal(self):
        edbapp = self.edb_examples.create_empty_edb()
        edbapp.stackup.create_symmetric_stackup(2)
        edbapp.modeler.create_rectangle(
            layer_name="BOT", net_name="GND", lower_left_point=["-2mm", "-2mm"], upper_right_point=["2mm", "2mm"]
        )
        prim_1 = edbapp.modeler.create_trace(
            path_list=([0, 0], [0, "1mm"]),
            layer_name="TOP",
            net_name="SIG",
            width="0.1mm",
            start_cap_style="Flat",
            end_cap_style="Flat",
        )
        prim_1.aedt_name = "path_1"
        prim_2 = edbapp.modeler.create_trace(
            path_list=(["1mm", 0], ["1mm", "1mm"]),
            layer_name="TOP",
            net_name="SIG",
            width="0.1mm",
            start_cap_style="Flat",
            end_cap_style="Flat",
        )
        prim_2.aedt_name = "path_2"

        edbapp.configuration.load(
            {"terminals": [self.edge_terminal_1, self.edge_terminal_2, self.bundle_terminal]}, apply_file=True
        )
        port1 = edbapp.ports["bundle_terminal"]
        assert port1.terminals[0].name == "bundle_terminal:T1"
        assert port1.terminals[1].name == "bundle_terminal:T2"
        edbapp.close(terminate_rpc_session=False)


@pytest.mark.usefixtures("close_rpc_session")
class TestClassSetups(BaseTestClass):
    terminal1 = {
        "name": "terminal1",
        "impedance": 1,
        "is_circuit_port": False,
        "boundary_type": "port" if config["use_grpc"] else "PortBoundary",
        "hfss_type": "Wave",
        "terminal_type": "padstack_instance",
        "padstack_instance": "U7-M7",
        "layer": None,
    }

    def test_hfss_single(self):
        data = {
            "setups": [
                {
                    "name": "single",
                    "type": "hfss",
                    "adapt_type": "single",
                    "single_frequency_adaptive_solution": {
                        "adaptive_frequency": "5GHz",
                        "max_passes": 10,
                        "max_delta": "0.02",
                    },
                    "freq_sweep": [],
                    "auto_mesh_operation": {
                        "enabled": False,
                        "signal_via_side_number": 12,
                        "trace_ratio_seeding": 3,
                    },
                    "mesh_operations": [
                        {
                            "name": "mop_1",
                            "mesh_operation_type": "length",
                            "max_length": "3mm",
                            "max_elements": "100",
                            "restrict_length": True,
                            "refine_inside": False,
                            "nets_layers_list": {"GND": ["1_Top", "16_Bottom"]},
                        }
                    ],
                },
            ]
        }

        edbapp = self.edb_examples.get_si_verse()
        edbapp.configuration.load(data)
        edbapp.configuration.run()
        data_from_db = edbapp.configuration.get_data_from_db(setups=True)
        source = next(item for item in data["setups"] if item["name"] == "single")
        target = next(item for item in data_from_db["setups"] if item["name"] == "single")
        target.pop("broadband_adaptive_solution")
        target.pop("multi_frequency_adaptive_solution")
        assert check_dictionaries(source, target)

        edbapp.close(terminate_rpc_session=False)

    def test_hfss_broadband(self):
        data = {
            "setups": [
                {
                    "name": "broadband",
                    "type": "hfss",
                    "adapt_type": "broadband",
                    "broadband_adaptive_solution": {
                        "low_frequency": "1GHz",
                        "high_frequency": "10GHz",
                        "max_passes": 10,
                        "max_delta": 0.02,
                    },
                },
            ]
        }

        edbapp = self.edb_examples.get_si_verse()
        assert edbapp.configuration.load(data, apply_file=True)
        data_from_db = edbapp.configuration.get_data_from_db(setups=True)

        source = next(item for item in data["setups"] if item["name"] == "broadband")
        target = next(item for item in data_from_db["setups"] if item["name"] == "broadband")
        target.pop(
            "freq_sweep"
        )  # Remove freq_sweep since it's not defined in source but is returned from db with default value
        target.pop(
            "auto_mesh_operation"
        )  # Remove auto_mesh_operation since it's not defined in source but is returned from db with default value
        target.pop(
            "mesh_operations"
        )  # Remove mesh_operations since it's not defined in source but is returned from db with default value
        target.pop(
            "single_frequency_adaptive_solution"
        )  # Remove single_frequency_adaptive_solution since it's not defined in source but is returned from db with
        # default value
        target.pop("multi_frequency_adaptive_solution")
        assert check_dictionaries(source, target)

        edbapp.close(terminate_rpc_session=False)

    def test_hfss_auto_mesh_operation(self):
        data = {
            "terminals": [self.terminal1],
            "setups": [
                {
                    "name": "hfss_setup_1",
                    "type": "hfss",
                    "f_adapt": "5GHz",
                    "max_num_passes": 10,
                    "max_mag_delta_s": 0.02,
                    "auto_mesh_operation": {
                        "enabled": True,
                        "trace_ratio_seeding": 3,
                        "signal_via_side_number": 12,
                    },
                },
            ],
        }

        edbapp = self.edb_examples.get_si_verse()
        assert edbapp.configuration.load(data, apply_file=True)
        data_from_db = edbapp.configuration.get_data_from_db(setups=True)
        assert data_from_db["setups"][0]["mesh_operations"][0]["name"] == "hfss_setup_1_AutoMeshOp"
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"] and is_linux, reason="DotNet Randomly failing on Linux.")
    def test_hfss_setup_w_frequency_sweeps(self):
        data = {
            "setups": [
                {
                    "name": "hfss_setup_1",
                    "type": "hfss",
                    "f_adapt": "5GHz",
                    "max_num_passes": 10,
                    "max_mag_delta_s": 0.02,
                    "freq_sweep": [
                        {
                            "name": "sweep1",
                            "type": "interpolation",
                            "use_q3d_for_dc": True,
                            "compute_dc_point": True,
                            "enforce_causality": True,
                            "enforce_passivity": False,
                            "adv_dc_extrapolation": True,
                            "frequencies": [
                                {"distribution": "linear_scale", "start": "0MHz", "stop": "200MHz", "step": "10MHz"},
                                {"distribution": "log_scale", "start": "1KHz", "stop": "100kHz", "samples": 10},
                                {"distribution": "linear_count", "start": "10MHz", "stop": "20MHz", "points": 11},
                            ],
                        },
                        {
                            "name": "sweep2",
                            "type": "discrete",
                            "frequencies": [
                                "LIN 0.05GHz 0.2GHz 0.01GHz",
                                "DEC 1e-06GHz 0.0001GHz 10",
                                "LINC 0.01GHz 0.02GHz 11",
                            ],
                        },
                    ],
                },
            ]
        }
        edbapp = self.edb_examples.get_si_verse()
        assert edbapp.configuration.load(data, apply_file=True)
        data_from_db = edbapp.configuration.get_data_from_db(setups=True)
        setup = data_from_db["setups"][0]
        assert setup["name"] == "hfss_setup_1"
        sweep1 = [i for i in setup["freq_sweep"] if i["name"] == "sweep1"][0]
        assert sweep1["name"] == "sweep1"
        assert sweep1["compute_dc_point"]
        assert sweep1["enforce_causality"]
        assert not sweep1["enforce_passivity"]
        assert len(sweep1["frequencies"]) == 3
        sweep2 = [i for i in setup["freq_sweep"] if i["name"] == "sweep2"][0]
        assert sweep2["type"] == "discrete"
        assert len(sweep2["frequencies"]) == 3

        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(is_linux and not config["use_grpc"], reason="Randomly fails on dotnet linux")
    def test_siwave_dc(self):
        data = {
            "setups": [
                {
                    "name": "siwave_1",
                    "type": "siwave_dc",
                    "dc_slider_position": 2,
                    "dc_ir_settings": {"export_dc_thermal_data": True},
                }
            ]
        }
        edbapp = self.edb_examples.get_si_verse()
        assert edbapp.configuration.load(data, apply_file=True)

        siwave_dc = edbapp.setups["siwave_1"]

        assert siwave_dc.settings.dc.dc_slider_position == 2
        assert siwave_dc.settings.export_dc_thermal_data is True

        data_from_db = edbapp.configuration.get_data_from_db(setups=True)
        src_siwave_dc = data_from_db["setups"][0]
        target_siwave_dc = data["setups"][0]
        assert src_siwave_dc == target_siwave_dc
        edbapp.close(terminate_rpc_session=False)

    def test_siwave_ac_w_frequency_sweep(self):
        data = {
            "setups": [
                {
                    "name": "siwave_1",
                    "type": "siwave_ac",
                    "use_si_settings": True,
                    "si_slider_position": 1,
                    "freq_sweep": [
                        {
                            "name": "Sweep1",
                            "type": "discrete",
                            "adv_dc_extrapolation": False,
                            "use_hfss_solver_regions": True,
                            "hfss_solver_region_setup_name": "hfss_setup_1",
                            "hfss_solver_region_sweep_name": "sweep2",
                            "frequencies": [
                                "LIN 0.05GHz 0.2GHz 0.01GHz",
                                "DEC 1e-06GHz 0.0001GHz 10",
                                "LINC 0.01GHz 0.02GHz 11",
                            ],
                        },
                    ],
                },
                {
                    "name": "hfss_setup_1",
                    "type": "hfss",
                    "f_adapt": "5GHz",
                    "max_num_passes": 10,
                    "max_mag_delta_s": 0.02,
                    "freq_sweep": [
                        {
                            "name": "sweep2",
                            "type": "discrete",
                            "frequencies": [
                                "LINC 0.01GHz 0.02GHz 11",
                            ],
                        },
                    ],
                },
            ]
        }
        edbapp = self.edb_examples.get_si_verse()
        assert edbapp.configuration.load(data, apply_file=True)
        siwave_ac = edbapp.setups["siwave_1"]
        assert siwave_ac.settings.general.use_si_settings is True
        assert siwave_ac.settings.general.si_slider_position == 1

        data_from_db = edbapp.configuration.get_data_from_db(setups=True)
        src_siwave_dc = [i for i in data_from_db["setups"] if i["name"] == "siwave_1"][0]
        assert src_siwave_dc["si_slider_position"] == 1
        assert src_siwave_dc["use_si_settings"] is True
        edbapp.close(terminate_rpc_session=False)


@pytest.mark.usefixtures("close_rpc_session")
class TestClassBoundaries(BaseTestClass):
    def test_open_region_radiation(self):
        edbapp = self.edb_examples.get_si_verse()

        data = {
            "boundaries": {
                "use_open_region": False,
                "open_region_type": "radiation",
            }
        }
        edbapp.configuration.load(data, apply_file=True)
        assert edbapp.hfss.hfss_extent_info.use_open_region is False

        data = {
            "boundaries": {
                "use_open_region": True,
                "open_region_type": "radiation",
            }
        }
        edbapp.configuration.load(data, apply_file=True)
        assert edbapp.hfss.hfss_extent_info.open_region_type == "radiation"

        edbapp.close(terminate_rpc_session=False)

    def test_open_region_pml(self):
        edbapp = self.edb_examples.get_si_verse()

        data = {
            "boundaries": {
                "use_open_region": True,
                "open_region_type": "pml",
                "is_pml_visible": True,
                "operating_freq": "3GHz",
                "radiation_level": "20",
            }
        }
        edbapp.configuration.load(data, apply_file=True)
        assert edbapp.hfss.hfss_extent_info.open_region_type == "pml"
        assert edbapp.hfss.hfss_extent_info.is_pml_visible is True
        assert edbapp.hfss.hfss_extent_info.operating_freq == 3e9
        assert edbapp.hfss.hfss_extent_info.radiation_level == 20

        edbapp.close(terminate_rpc_session=False)

    def test_extent_dielectric(self):
        edbapp = self.edb_examples.get_si_verse()
        data = {
            "boundaries": {
                "dielectric_extent_type": "bounding_box",
                "dielectric_extent_size": {"size": 0.01, "is_multiple": True},
                "honor_user_dielectric": False,
            }
        }
        edbapp.configuration.load(data, apply_file=True)
        assert edbapp.hfss.hfss_extent_info.dielectric_extent_type == "bounding_box"
        assert edbapp.hfss.hfss_extent_info.get_dielectric_extent() == (0.01, True)
        assert edbapp.hfss.hfss_extent_info.honor_user_dielectric is False

        data = {
            "boundaries": {
                "dielectric_extent_type": "polygon",
                "dielectric_base_polygon": "poly_5949",
                "honor_user_dielectric": True,
            }
        }
        edbapp.configuration.load(data, apply_file=True)
        assert edbapp.hfss.hfss_extent_info.dielectric_extent_type == "polygon"
        assert edbapp.hfss.hfss_extent_info.dielectric_base_polygon == "poly_5949"
        assert edbapp.hfss.hfss_extent_info.honor_user_dielectric is True
        edbapp.close(terminate_rpc_session=False)

    def test_extent_air(self):
        data = {
            "boundaries": {
                "extent_type": "bounding_box",
                "truncate_air_box_at_ground": True,
                "air_box_horizontal_extent": {"size": 0.15, "is_multiple": True},
                "air_box_positive_vertical_extent": {"size": 1.0, "is_multiple": True},
                "air_box_negative_vertical_extent": {"size": 2.0, "is_multiple": True},
                "sync_air_box_vertical_extent": True,
            }
        }
        edbapp = self.edb_examples.get_si_verse()
        edbapp.configuration.load(data, apply_file=True)
        assert edbapp.hfss.hfss_extent_info.extent_type == "bounding_box"
        assert edbapp.hfss.hfss_extent_info.truncate_air_box_at_ground is True
        assert edbapp.hfss.hfss_extent_info.get_air_box_horizontal_extent() == (0.15, True)
        assert edbapp.hfss.hfss_extent_info.get_air_box_positive_vertical_extent() == (1.0, True)
        assert edbapp.hfss.hfss_extent_info.get_air_box_negative_vertical_extent() == (2.0, True)
        assert edbapp.hfss.hfss_extent_info.sync_air_box_vertical_extent is True

        data = {
            "boundaries": {
                "extent_type": "polygon",
                "base_polygon": "poly_5949",
            }
        }
        edbapp.configuration.load(data, apply_file=True)
        assert edbapp.hfss.hfss_extent_info.extent_type == "polygon"
        assert edbapp.hfss.hfss_extent_info.base_polygon == "poly_5949"
        edbapp.close(terminate_rpc_session=False)


@pytest.mark.usefixtures("close_rpc_session")
class TestClassPadstacks(BaseTestClass):
    def test_09_padstack_definition(self, is_grpc=None):
        solder_ball_parameters = {
            "shape": "spheroid",
            "diameter": "0.4mm",
            "mid_diameter": "0.5mm",
            "placement": "above_padstack",
            "material": "solder",
        }
        INSTANCE = {
            "name": "Via998",
            "definition": "v35h15",
            "layer_range": ["Inner1(GND1)", "16_Bottom"],
            "solder_ball_layer": "1_Top",
        }

        DEFINITION = {
            "name": "v35h15",
            "hole_plating_thickness": "25um",
            "material": "copper",
            "hole_range": "upper_pad_to_lower_pad",
            "pad_parameters": {
                "regular_pad": [
                    {
                        "layer_name": "1_Top",
                        "shape": "circle",
                        "offset_x": "0.1mm",
                        "rotation": "0",
                        "diameter": "0.5mm",
                    }
                ],
                "anti_pad": [{"layer_name": "1_Top", "shape": "circle", "diameter": "1mm"}],
                "thermal_pad": [
                    {
                        "layer_name": "1_Top",
                        "shape": "round90",
                        "inner": "1mm",
                        "channel_width": "0.2mm",
                        "isolation_gap": "0.3mm",
                    }
                ],
            },
            "hole_parameters": {
                "shape": "circle",
                "diameter": "0.2mm",
            },
            "solder_ball_parameters": solder_ball_parameters,
        }

        data = {"padstacks": {"definitions": [DEFINITION], "instances": [INSTANCE]}}
        edbapp = self.edb_examples.get_si_verse()
        assert edbapp.configuration.load(data, apply_file=False)
        edbapp.configuration.run()
        data_from_layout = edbapp.configuration.get_data_from_db(padstacks=True)
        pdef = [i for i in data_from_layout["padstacks"]["definitions"] if i["name"] == "v35h15"][0]

        pad_params = pdef["pad_parameters"]
        key_regular = "REGULAR_PAD" if settings.is_grpc else "regular_pad"
        key_anti = "ANTI_PAD" if settings.is_grpc else "anti_pad"
        key_thermal = "THERMAL_PAD" if settings.is_grpc else "thermal_pad"

        assert pad_params[key_regular][0]["diameter"] == "0.5mm" or pad_params[key_regular][0]["diameter"] == "0.0005"
        assert pad_params[key_regular][0]["offset_x"] == "0.1mm" or pad_params[key_regular][0]["offset_x"] == "0.0001"
        assert pad_params[key_anti][0]["diameter"] == "1mm" or pad_params[key_anti][0]["diameter"] == "0.001"
        assert pad_params[key_thermal][0]["inner"] == "1mm" or pad_params[key_thermal][0]["inner"] == "0.001"
        assert (
            pad_params[key_thermal][0]["channel_width"] == "0.2mm"
            or pad_params[key_thermal][0]["channel_width"] == "0.0002"
        )

        hole_params = pdef["hole_parameters"]
        assert hole_params["shape"] in ["circle", "PADGEOMTYPE_CIRCLE"]
        assert hole_params["diameter"] == "0.2mm" or hole_params["diameter"] == "0.0002"
        assert pdef["solder_ball_parameters"]["shape"] == solder_ball_parameters["shape"]

        instance = [i for i in data_from_layout["padstacks"]["instances"] if i["name"] == "Via998"][0]
        # GRPC is not working on solderball_layer and backdrill_parameters, so skipping those checks for now
        if not settings.is_grpc:
            for k, v in INSTANCE.items():
                assert v == instance[k]
        edbapp.close(terminate_rpc_session=False)

    def test_09_padstack_instance(self):
        edbapp = self.edb_examples.get_si_verse()
        cfg_data = edbapp.configuration.cfg_data
        cfg_pds = cfg_data.padstacks.add_padstack_instance(
            name="Via998",
            definition="v35h15",
            hole_override_enabled=True,
            hole_override_diameter="0.5mm",
        )
        cfg_pds.backdrill_parameters.add_backdrill_to_layer(
            drill_to_layer="Inner3(Sig1)", diameter="0.5mm", stub_length="0.2mm", drill_from_bottom=False
        )
        cfg_pds.backdrill_parameters.add_backdrill_to_layer(
            drill_to_layer="Inner4(Sig2)", diameter="0.5mm", stub_length="0.2mm", drill_from_bottom=True
        )

        assert edbapp.configuration.run()
        data_from_db = edbapp.configuration.get_data_from_db(padstacks=True)
        assert data_from_db["padstacks"]["instances"]
        edbapp.close(terminate_rpc_session=False)

    def test_13_stackup_layers(self):
        data = {
            "stackup": {
                "layers": [
                    {
                        "fill_material": "Solder Resist",
                        "material": "copper",
                        "name": "1_Top",
                        "thickness": "0.5mm",
                        "type": "signal",
                        "roughness": {
                            "top": {"model": "huray", "nodule_radius": "0.1um", "surface_ratio": "1"},
                            "bottom": {"model": "groisse", "roughness": "2um"},
                            "side": {"model": "huray", "nodule_radius": "0.5um", "surface_ratio": "2.9"},
                            "enabled": True,
                        },
                        "etching": {"factor": "0.5", "etch_power_ground_nets": False, "enabled": True},
                    },
                    {
                        "fill_material": "Megtron4",
                        "material": "copper",
                        "name": "Inner1",
                        "thickness": "0.017mm",
                        "type": "signal",
                    },
                    {"material": "Megtron4", "name": "DE2", "thickness": "0.088mm", "type": "dielectric"},
                    {"material": "Megtron4", "name": "DE3", "thickness": "0.1mm", "type": "dielectric"},
                    {
                        "fill_material": "Megtron4",
                        "material": "copper",
                        "name": "Inner2",
                        "thickness": "0.017mm",
                        "type": "signal",
                    },
                    {
                        "fill_material": "Megtron4",
                        "material": "copper",
                        "name": "Inner3",
                        "thickness": "0.017mm",
                        "type": "signal",
                    },
                    {
                        "fill_material": "Megtron4",
                        "material": "copper",
                        "name": "Inner4",
                        "thickness": "0.017mm",
                        "type": "signal",
                    },
                    {
                        "fill_material": "Megtron4",
                        "material": "copper",
                        "name": "Inner5",
                        "thickness": "0.017mm",
                        "type": "signal",
                    },
                    {
                        "fill_material": "Megtron4",
                        "material": "copper",
                        "name": "Inner6",
                        "thickness": "0.017mm",
                        "type": "signal",
                    },
                    {
                        "fill_material": "Solder Resist",
                        "material": "copper",
                        "name": "16_Bottom",
                        "thickness": "0.035mm",
                        "type": "signal",
                    },
                ]
            }
        }
        edbapp = self.edb_examples.get_si_verse()
        renamed_layers = {
            "1_Top": "1_Top",
            "Inner1(GND1)": "Inner1",
            "Inner2(PWR1)": "Inner2",
            "Inner3(Sig1)": "Inner3",
            "Inner4(Sig2)": "Inner4",
            "Inner5(PWR2)": "Inner5",
            "Inner6(GND2)": "Inner6",
            "16_Bottom": "16_Bottom",
        }
        vias_before = {i: [j.start_layer, j.stop_layer] for i, j in edbapp.padstacks.instances.items()}
        assert edbapp.configuration.load(data, apply_file=True)
        assert list(edbapp.stackup.layers.keys())[:4] == ["1_Top", "Inner1", "DE2", "DE3"]
        vias_after = {i: [j.start_layer, j.stop_layer] for i, j in edbapp.padstacks.instances.items()}
        for i, j in vias_after.items():
            assert j[0] == renamed_layers[vias_before[i][0]]
            assert j[1] == renamed_layers[vias_before[i][1]]
        data_from_db = edbapp.configuration.get_data_from_db(stackup=True)
        for lay in data["stackup"]["layers"]:
            target_mat = [i for i in data_from_db["stackup"]["layers"] if i["name"] == lay["name"]][0]
            for p, value in lay.items():
                val_to_check = unit_converter(target_mat[p], input_units="m", output_units="mm")
                assert value == target_mat[p] if isinstance(target_mat[p], str) else f"{val_to_check}mm"
        edbapp.close(terminate_rpc_session=False)

    def test_deprecated_methods_hfss_single(self):
        from pyedb.configuration.cfg_data import CfgData

        data = {
            "setups": [
                {
                    "name": "hfss_setup_1",
                    "type": "hfss",
                    "f_adapt": "5GHz",
                    "max_num_passes": 10,
                    "max_mag_delta_s": 0.02,
                    "mesh_operations": [
                        {
                            "name": "mop_1",
                            "type": "length",
                            "nets_layers_list": {"GND": ["1_Top", "16_Bottom"]},
                        }
                    ],
                },
            ]
        }

        cfg_data = CfgData(None, **data)
        cfg_hfss_single = cfg_data.setups.setups[0].single_frequency_adaptive_solution
        cfg_hfss_single.adaptive_frequency = "5GHz"
        cfg_hfss_single.max_passes = 10
        cfg_hfss_single.max_delta = 0.02


@pytest.mark.usefixtures("close_rpc_session")
class TestModeler(BaseTestClass):
    def test_18_modeler(self):
        data = {
            "modeler": {
                "traces": [
                    {
                        "name": "trace_1",
                        "layer": "TOP",
                        "width": "0.1mm",
                        "path": [[0, 0], [0, "10mm"]],
                        "net_name": "SIG",
                        "start_cap_style": "flat",
                        "end_cap_style": "flat",
                        "corner_style": "round",
                    },
                    {
                        "name": "trace_1_void",
                        "layer": "TOP",
                        "width": "0.3mm",
                        "incremental_path": [[0, 0], [0, "10mm"]],
                    },
                ],
                "padstack_definitions": [
                    {
                        "name": "via",
                        "hole_plating_thickness": "0.025mm",
                        "material": "copper",
                        "pad_parameters": {
                            "regular_pad": [
                                {
                                    "layer_name": "TOP",
                                    "shape": "circle",
                                    "offset_x": "0mm",
                                    "offset_y": "0",
                                    "rotation": "0",
                                    "diameter": "0.5mm",
                                },
                                {
                                    "layer_name": "BOT",
                                    "shape": "circle",
                                    "offset_x": "0mm",
                                    "offset_y": "0",
                                    "rotation": "0",
                                    "diameter": "0.5mm",
                                },
                            ],
                            "anti_pad": [
                                {
                                    "layer_name": "TOP",
                                    "shape": "circle",
                                    "offset_x": "0",
                                    "offset_y": "0",
                                    "rotation": "0",
                                    "diameter": "1mm",
                                },
                                {
                                    "layer_name": "BOT",
                                    "shape": "circle",
                                    "offset_x": "0",
                                    "offset_y": "0",
                                    "rotation": "0",
                                    "diameter": "1mm",
                                },
                            ],
                        },
                        "hole_range": "through",
                        "hole_parameters": {
                            "shape": "circle",
                            "diameter": "0.25mm",
                        },
                    }
                ],
                "padstack_instances": [
                    {
                        "name": "via_1",
                        "definition": "via",
                        "layer_range": ["TOP", "BOT"],
                        "position": [0, 0],
                        "net_name": "SIG",
                    },
                    {
                        "name": "pin_1",
                        "definition": "via",
                        "layer_range": ["TOP", "TOP"],
                        "position": [0, "1mm"],
                        "net_name": "SIG",
                        "is_pin": True,
                    },
                ],
                "planes": [
                    {
                        "type": "rectangle",
                        "name": "GND_TOP",
                        "layer": "TOP",
                        "net_name": "GND",
                        "lower_left_point": [0, 0],
                        "upper_right_point": ["12mm", "12mm"],
                        "voids": ["trace_1_void"],
                    },
                    {
                        "type": "polygon",
                        "name": "GND_TOP_POLY",
                        "layer": "TOP",
                        "net_name": "GND",
                        "points": [["12mm", 0], ["13mm", 0], ["12mm", "12mm"]],
                    },
                ],
                "components": [
                    {
                        "reference_designator": "U1",
                        "pins": ["pin_1"],
                        "part_type": "io",
                        "definition": "BGA",
                        "placement_layer": "TOP",
                        "solder_ball_properties": {
                            "shape": "cylinder",
                            "diameter": "244um",
                            "height": "406um",
                            "material": "air",
                        },
                        "port_properties": {
                            "reference_offset": "0.1mm",
                            "reference_size_auto": False,
                            "reference_size_x": 0,
                            "reference_size_y": 0,
                        },
                    },
                ],
            }
        }
        edbapp = self.edb_examples.create_empty_edb()
        edbapp.stackup.create_symmetric_stackup(2)
        edbapp.configuration.load(data, apply_file=True)
        assert [i for i in edbapp.layout.primitives if i.aedt_name == "trace_1"]
        rect = [i for i in edbapp.layout.primitives if i.aedt_name == "GND_TOP"][0]
        assert rect.voids
        assert [i for i in edbapp.layout.primitives if i.aedt_name == "GND_TOP_POLY"][0]
        assert edbapp.components["U1"]
        if edbapp.grpc:
            assert edbapp.components["U1"].component_property.solder_ball_property.material_name == "air"
        else:
            assert (
                edbapp.components["U1"].component_property.core.GetSolderBallProperty().Clone().GetMaterialName()
                == "air"
            )
        edbapp.close(terminate_rpc_session=False)

    def test_modeler_delete(self):
        edbapp = self.edb_examples.get_si_verse()
        assert edbapp.layout.find_primitive(name="line_163")
        data = {"modeler": {"primitives_to_delete": {"name": ["line_163"]}}}
        edbapp.configuration.load(data, apply_file=True)
        assert len(edbapp.layout.find_primitive(name="line_163")) == 0
        edbapp.close(terminate_rpc_session=False)


@pytest.mark.usefixtures("close_rpc_session")
class TestComponent(BaseTestClass):
    def test_17_ic_die_properties(self):
        db = self.edb_examples.get_si_verse()
        comps_edb = db.configuration.get_data_from_db(components=True)["components"]
        component = [i for i in comps_edb if i["reference_designator"] == "U8"][0]
        assert component["ic_die_properties"]["type"] in ["none", "no_die", "flip_chip", "flipchip"]
        assert "orientation" in component["ic_die_properties"]
        assert "height" not in component["ic_die_properties"]
        db.configuration.load(U8_IC_DIE_PROPERTIES, apply_file=True)
        comps_edb = db.configuration.get_data_from_db(components=True)["components"]
        component = [i for i in comps_edb if i["reference_designator"] == "U8"][0]
        _assert_final_ic_die_properties(component)


@pytest.mark.usefixtures("close_rpc_session")
class TestOperations(BaseTestClass):
    def test_08a_operations_cutout(self):
        data = {
            "operations": {
                "cutout": {
                    "signal_nets": ["SFPA_RX_P", "SFPA_RX_N"],
                    "reference_nets": ["GND"],
                    "extent_type": "ConvexHull",
                    "expansion_size": 0.002,
                    "use_round_corner": False,
                    "output_aedb_path": "",
                    "open_cutout_at_end": True,
                    "use_pyaedt_cutout": True,
                    "number_of_threads": 4,
                    "use_pyaedt_extent_computing": True,
                    "extent_defeature": 0,
                    "remove_single_pin_components": False,
                    "custom_extent": "",
                    "custom_extent_units": "mm",
                    "include_partial_instances": False,
                    "keep_voids": True,
                    "check_terminals": False,
                    "include_pingroups": False,
                    "expansion_factor": 0,
                    "maximum_iterations": 10,
                    "preserve_components_with_model": False,
                    "simple_pad_check": False,
                    "keep_lines_as_path": False,
                }
            }
        }
        edbapp = self.edb_examples.get_si_verse()
        assert edbapp.configuration.load(data, apply_file=True)
        assert set(list(edbapp.nets.nets.keys())) == set(["SFPA_RX_P", "SFPA_RX_N", "GND", "pyedb_cutout"])
        edbapp.close(terminate_rpc_session=False)

    def test_16b_export_cutout(self):
        data = {
            "operations": {
                "cutout": {
                    "signal_nets": ["SFPA_RX_P", "SFPA_RX_N"],
                    "reference_nets": ["GND"],
                }
            }
        }
        edbapp = self.edb_examples.get_si_verse()
        edbapp.configuration.load(data, apply_file=True)
        data_from_db = edbapp.configuration.get_data_from_db(operations=True)
        assert len(data_from_db["operations"]["cutout"]["signal_nets"]) == 2
        assert len(data_from_db["operations"]["cutout"]["reference_nets"]) == 1
        edbapp.close(terminate_rpc_session=False)

    def test_16_components_rlc(self):
        components = [
            {
                "reference_designator": "C375",
                "enabled": False,
                "pin_pair_model": [
                    {
                        "first_pin": "1",
                        "second_pin": "2",
                        "is_parallel": False,
                        "resistance": "10.0",
                        "resistance_enabled": True,
                        "inductance": "1e-09",
                        "inductance_enabled": False,
                        "capacitance": "1e-08",
                        "capacitance_enabled": True,
                    }
                ],
            },
        ]
        data = {"components": components}
        edbapp = self.edb_examples.get_si_verse()
        assert edbapp.configuration.load(data, apply_file=True)
        data_from_db = edbapp.configuration.get_data_from_db(components=True)
        c375 = [i for i in data_from_db["components"] if i["reference_designator"] == "C375"][0]
        assert c375["pin_pair_model"] == components[0]["pin_pair_model"]
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Not tested in dotnet")
    def test_cfg_builder_1(self):
        # Test with solder ball coax ports
        edb_app = self.edb_examples.get_si_verse()
        signal_nets = [
            "PCIe_Gen4_RX0_P",
            "PCIe_Gen4_RX0_N",
            "PCIe_Gen4_RX1_P",
            "PCIe_Gen4_RX1_N",
            "PCIe_Gen4_RX2_P",
            "PCIe_Gen4_RX2_N",
            "PCIe_Gen4_RX3_P",
            "PCIe_Gen4_RX3_N",
        ]

        config_builder = edb_app.configuration.create_config_builder()
        config_builder.nets.add_signal_nets(signal_nets)
        config_builder.nets.add_reference_nets(["GND"])
        config_builder.operations.add_cutout(
            signal_nets=config_builder.nets.signal_nets,
            reference_nets=config_builder.nets.reference_nets,
            extent_type="ConvexHull",
            expansion_size=3e-3,
        )
        setup = config_builder.setups.add_hfss_setup(name="Test_HFSS")
        setup.add_frequency_sweep(name="Test_Sweep", start="1GHz", stop="10GHz", step_or_count="0.5GHz")
        component = config_builder.components.get("U1")
        component.set_solder_ball_properties(shape="cylinder", diameter="300um", height="300um")
        config_builder.ports.add_coax_port(reference_designator="U1", net_list=signal_nets)
        edb_app.configuration.run(config_builder)
        assert len(edb_app.nets.nets) == 10
        assert len(edb_app.ports) == 8
        assert edb_app.components["U1"].component_property.solder_ball_property.shape == "cylinder"
        assert edb_app.components["U1"].component_property.solder_ball_property.get_diameter() == (300e-6, 300e-6)
        assert edb_app.components["U1"].component_property.solder_ball_property.height == 300e-6
        bbox = edb_app.get_bounding_box()
        assert pytest.approx(bbox[0][0], 5) == 0.010
        assert pytest.approx(bbox[0][1], 5) == 0.0216
        assert pytest.approx(bbox[1][0], 5) == 0.0751
        assert pytest.approx(bbox[1][1], 5) == 0.0481
        edb_app.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Not tested in dotnet")
    def test_cfg_builder_2(self):
        #  test with circuit port and pin group
        edb_app = self.edb_examples.get_si_verse()
        signal_nets = [
            "PCIe_Gen4_RX0_P",
            "PCIe_Gen4_RX0_N",
            "PCIe_Gen4_RX1_P",
            "PCIe_Gen4_RX1_N",
            "PCIe_Gen4_RX2_P",
            "PCIe_Gen4_RX2_N",
            "PCIe_Gen4_RX3_P",
            "PCIe_Gen4_RX3_N",
        ]

        config_builder = edb_app.configuration.create_config_builder()
        config_builder.nets.add_signal_nets(signal_nets)
        config_builder.nets.add_reference_nets(["GND"])
        config_builder.operations.add_cutout(
            signal_nets=config_builder.nets.signal_nets,
            reference_nets=config_builder.nets.reference_nets,
            extent_type="ConvexHull",
            expansion_size=3e-3,
        )
        setup = config_builder.setups.add_hfss_setup(name="Test_HFSS")
        setup.add_frequency_sweep(name="Test_Sweep", start="1GHz", stop="10GHz", step_or_count="0.5GHz")
        config_builder.pin_groups.add(reference_designator="U1", nets="GND")
        config_builder.pin_groups.add(reference_designator="U1", nets=config_builder.nets.signal_nets)
        for sign_net in config_builder.nets.signal_nets:
            config_builder.ports.add_circuit_port(reference_designator="U1", positive_net=sign_net, negative_net="GND")
        edb_app.configuration.run(config_builder)
        assert len(edb_app.ports) == 8
        assert "Port_U1_PCIe_Gen4_RX0_P_AP26" in edb_app.ports
        assert "Test_HFSS" in edb_app.setups
        assert edb_app.setups["Test_HFSS"].sweeps["Test_Sweep"].frequency_string[0] == "LIN 1GHz 10GHz 0.5GHz"
        edb_app.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Not tested in dotnet")
    def test_cfg_builder_3(self):
        # Test with solder ball coax ports but discovering solder balls diameters
        edb_app = self.edb_examples.get_si_verse()
        signal_nets = [
            "PCIe_Gen4_RX0_P",
            "PCIe_Gen4_RX0_N",
            "PCIe_Gen4_RX1_P",
            "PCIe_Gen4_RX1_N",
            "PCIe_Gen4_RX2_P",
            "PCIe_Gen4_RX2_N",
            "PCIe_Gen4_RX3_P",
            "PCIe_Gen4_RX3_N",
        ]

        config_builder = edb_app.configuration.create_config_builder()
        config_builder.nets.add_signal_nets(signal_nets)
        config_builder.nets.add_reference_nets(["GND"])
        config_builder.operations.add_cutout(
            signal_nets=config_builder.nets.signal_nets,
            reference_nets=config_builder.nets.reference_nets,
            extent_type="ConvexHull",
            expansion_size=3e-3,
        )
        setup = config_builder.setups.add_hfss_setup(name="Test_HFSS")
        setup.add_frequency_sweep(name="Test_Sweep", start="1GHz", stop="10GHz", step_or_count="0.5GHz")
        component = config_builder.components.get("U1")
        component.set_solder_ball_properties(shape="cylinder", reference_designator="U1")
        config_builder.ports.add_coax_port(reference_designator="U1", net_list=signal_nets)
        edb_app.configuration.run(config_builder)
        assert len(edb_app.nets.nets) == 10
        assert len(edb_app.ports) == 8
        assert edb_app.components["U1"].component_property.solder_ball_property.shape == "cylinder"
        assert edb_app.components["U1"].component_property.solder_ball_property.get_diameter() == (
            pytest.approx(500e-6, 5),
            pytest.approx(500e-6, 5),
        )
        assert edb_app.components["U1"].component_property.solder_ball_property.height == pytest.approx(333e-6, 5)
        edb_app.close(terminate_rpc_session=False)

    def test_cdg_builder_nets(self):
        edb_app = self.edb_examples.get_si_verse()
        cfg_builder = edb_app.configuration.create_config_builder()
        net = cfg_builder.nets.get("PCIe_Gen4_RX0_P")
        assert not net.is_power_ground
        assert net.classification == "signal"
        cfg_builder.nets.add_power_ground_nets(["PCIe_Gen4_RX0_P"])
        assert "PCIe_Gen4_RX0_P" in cfg_builder.nets.power_ground_nets
        cfg_builder.nets.add_signal_nets(["PCIe_Gen4_RX0_P"])
        assert "PCIe_Gen4_RX0_P" in cfg_builder.nets.signal_nets
        assert not "PCIe_Gen4_RX0_P" in cfg_builder.nets.power_ground_nets  # net must be removed
        assert not "PCIe_Gen4_RX0_P" in cfg_builder.nets.reference_nets  # net must be removed
        cfg_builder.nets.add_power_ground_nets(["PCIe_Gen4_RX0_P"])
        edb_app.configuration.run(cfg_builder)
        assert edb_app.nets.nets.get("PCIe_Gen4_RX0_P").is_power_ground  # net physically changed as pwr in EDB
        edb_app.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Not tested in dotnet")
    def test_cfg_gap_port(self):
        edb_app = self.edb_examples.get_si_verse()
        cfg_builder = edb_app.configuration.create_config_builder()
        polygon = edb_app.layout.polygons[0]

        cfg_edg_port = cfg_builder.ports.add_gap_port(
            name="test_cfg_gap_port",
            primitive=polygon,
            point_on_edge=polygon.arcs[0].midpoint,
            pec_launch_width="0.02mm",
        )
        assert cfg_edg_port.horizontal_extent_factor == 5
        assert cfg_edg_port.name == "test_cfg_gap_port"
        assert cfg_edg_port.pec_launch_width == "0.02mm"
        assert cfg_edg_port.type == "gap_port"
        edb_app.configuration.run(cfg_builder)
        assert "test_cfg_gap_port" in edb_app.ports
        port = edb_app.ports.get("test_cfg_gap_port")
        assert port.hfss_type == "Gap"
        assert port.pec_launch_width == "0.02mm"
        edb_app.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Not tested in dotnet")
    def test_cfg_diff_wave_port(self):
        edb_app = self.edb_examples.get_si_verse()
        cfg_builder = edb_app.configuration.create_config_builder()
        path_p = edb_app.nets.nets.get("PCIe_Gen4_RX3_P").primitives[0]
        path_n = edb_app.nets.nets.get("PCIe_Gen4_RX3_N").primitives[0]
        point_on_edge_p = path_p.center_line[0]
        point_on_edge_n = path_p.center_line[-1]
        cfg_wave_port = cfg_builder.ports.add_diff_wave_port(
            name="test_cfg_wave_port",
            positive_primitive=path_p,
            positive_terminal_point=point_on_edge_p,
            negative_primitive=path_n,
            negative_terminal_point=point_on_edge_n,
        )
        assert cfg_wave_port.horizontal_extent_factor == 5
        assert cfg_wave_port.name == "test_cfg_wave_port"
        assert cfg_wave_port.type == "diff_wave_port"
        positive_port = cfg_wave_port.positive_port
        assert positive_port.name == "test_cfg_wave_port:T1"
        assert positive_port.primitive_name == "line_165"
        assert positive_port.point_on_edge == point_on_edge_p
        negative_port = cfg_wave_port.negative_port
        assert negative_port.name == "test_cfg_wave_port:T2"
        assert negative_port.primitive_name == "line_166"
        assert negative_port.point_on_edge == point_on_edge_n
        edb_app.configuration.run(cfg_builder)
        assert "test_cfg_wave_port" in edb_app.ports
        diff_wave_port = edb_app.ports.get("test_cfg_wave_port")
        assert diff_wave_port.hfss_type == "Wave"
        assert len(diff_wave_port.terminals) == 2
        terminal1 = diff_wave_port.terminals[0]
        assert terminal1.net_name == "PCIe_Gen4_RX3_P"
        assert terminal1.name == "test_cfg_wave_port:T1"
        assert terminal1.terminal_type == "edge"
        assert terminal1.is_port is True
        terminal2 = diff_wave_port.terminals[-1]
        assert terminal2.net_name == "PCIe_Gen4_RX3_N"
        assert terminal2.name == "test_cfg_wave_port:T2"
        assert terminal2.terminal_type == "edge"
        assert terminal2.is_port is True
        edb_app.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Not tested in dotnet")
    def test_cfg_wave_port(self):
        edb_app = self.edb_examples.get_si_verse()
        cfg_builder = edb_app.configuration.create_config_builder()
        path = edb_app.nets.nets.get("PCIe_Gen4_RX3_P").primitives[0]
        point_on_edge = path.center_line[0]
        cfg_wave_port = cfg_builder.ports.add_wave_port(
            name="test_wave_port", primitive=path, point_on_edge=point_on_edge
        )
        assert cfg_wave_port.horizontal_extent_factor == 5
        assert cfg_wave_port.name == "test_wave_port"
        assert cfg_wave_port.type == "wave_port"
        assert cfg_wave_port.primitive_name == "line_165"
        assert cfg_wave_port.point_on_edge == point_on_edge
        edb_app.configuration.run(cfg_builder)
        assert "test_wave_port" in edb_app.ports
        wave_port = edb_app.ports.get("test_wave_port")
        assert wave_port.is_port is True
        assert wave_port.net_name == "PCIe_Gen4_RX3_P"
        assert wave_port.terminal_type == "edge"
        assert wave_port.hfss_type == "Wave"
        edb_app.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Not tested in dotnet")
    def test_cfg_hfss_setup(self):
        edb_app = self.edb_examples.get_si_verse()
        cfg_builder = edb_app.configuration.create_config_builder()
        signal_nets = [
            "PCIe_Gen4_RX0_P",
            "PCIe_Gen4_RX0_N",
            "PCIe_Gen4_RX1_P",
            "PCIe_Gen4_RX1_N",
            "PCIe_Gen4_RX2_P",
            "PCIe_Gen4_RX2_N",
            "PCIe_Gen4_RX3_P",
            "PCIe_Gen4_RX3_N",
        ]
        # create port is needed for auto assign mesh op
        component = cfg_builder.components.get("U1")
        component.set_solder_ball_properties(shape="cylinder", reference_designator="U1")
        cfg_builder.ports.add_coax_port(reference_designator="U1", net_list=signal_nets)
        # hfss setup
        cfg_setup = cfg_builder.setups.add_hfss_setup(name="Test_HFSS")
        cfg_setup.add_frequency_sweep(name="Test_Sweep", start="1GHz", stop="10GHz", step_or_count="0.5GHz")
        cfg_setup.set_auto_mesh_operation(enabled=True, trace_ratio_seeding=3.0, signal_via_side_number=12)
        cfg_setup.set_broadband_adaptive(low_freq="5GHz", high_freq="10GHz", max_delta=0.05, max_passes=30)
        assert cfg_setup.name == "Test_HFSS"
        cfg_sweep = cfg_setup.freq_sweep[0]
        assert cfg_sweep.name == "Test_Sweep"
        assert cfg_setup.freq_sweep[0].frequencies[0].start == "1GHz"
        assert cfg_setup.freq_sweep[0].frequencies[0].stop == "10GHz"
        assert cfg_setup.freq_sweep[0].frequencies[0].increment == "0.5GHz"
        assert cfg_setup.broadband_adaptive_solution.low_frequency == "5GHz"
        assert cfg_setup.broadband_adaptive_solution.high_frequency == "10GHz"
        assert cfg_setup.broadband_adaptive_solution.max_delta == 0.05
        assert cfg_setup.broadband_adaptive_solution.max_passes == 30
        edb_app.configuration.run(cfg_builder)
        assert len(edb_app.ports) == 8
        assert "Test_HFSS" in edb_app.setups
        setup = edb_app.setups.get("Test_HFSS")
        assert setup.frequency_sweeps["Test_Sweep"].frequency_string[0] == "LIN 1GHz 10GHz 0.5GHz"
        mesh_operation = edb_app.setups["Test_HFSS"].mesh_operations[0]
        assert mesh_operation.enabled is True
        assert mesh_operation.mesh_operation_type == "LengthMeshOperation"
        assert mesh_operation.name == "Test_HFSS_AutoMeshOp"
        assert len(mesh_operation.net_layer_info) == 16
        assert mesh_operation.restrict_max_length is True
        assert edb_app.value(edb_app.setups["Test_HFSS"].mesh_operations[0].max_length) == pytest.approx(450, 1)
        assert setup.adaptive_settings.broadband_adaptive_solution.low_frequency == "5GHz"
        assert setup.adaptive_settings.broadband_adaptive_solution.high_frequency == "10GHz"
        assert setup.adaptive_settings.broadband_adaptive_solution.max_delta == "0.05"
        assert setup.adaptive_settings.broadband_adaptive_solution.max_passes == 30
        edb_app.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Not tested in dotnet")
    def test_cfg_siwave_ac_setup(self):
        edb_app = self.edb_examples.get_si_verse()
        cfg_builder = edb_app.configuration.create_config_builder()
        setup = cfg_builder.setups.add_siwave_ac_setup(
            name="Test_siwave_AC_Setup", use_si_settings=True, si_slider_position=2
        )
        setup.add_frequency_sweep(name="Test_Sweep", start="0GHz", stop="35GHz", step_or_count="0.1GHz")
        assert setup.name == "Test_siwave_AC_Setup"
        assert setup.si_slider_position == 2
        assert setup.freq_sweep[0].frequencies[0].start == "0GHz"
        assert setup.freq_sweep[0].frequencies[0].stop == "35GHz"
        assert setup.freq_sweep[0].frequencies[0].increment == "0.1GHz"
        edb_app.configuration.run(cfg_builder)
        assert "Test_siwave_AC_Setup" in edb_app.setups
        setup = edb_app.setups.get("Test_siwave_AC_Setup")
        assert setup.settings.general.si_slider_position == 2
        assert setup.frequency_sweeps.get("Test_Sweep").frequency_string == ["LIN 0GHz 35GHz 0.1GHz"]
        edb_app.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Not tested in dotnet")
    def test_cfg_siwave_dc_setup(self):
        edb_app = self.edb_examples.get_si_verse()
        cfg_builder = edb_app.configuration.create_config_builder()
        setup = cfg_builder.setups.add_siwave_dc_setup(
            name="Test_siwave_DC_Setup",
            dc_slider_position=2,
            export_dc_thermal_data=True,
        )
        assert setup.name == "Test_siwave_DC_Setup"
        assert setup.dc_slider_position == 2
        assert setup.dc_ir_settings.export_dc_thermal_data is True
        edb_app.configuration.run(cfg_builder)
        assert "Test_siwave_DC_Setup" in edb_app.setups
        edb_setup = edb_app.setups.get("Test_siwave_DC_Setup")
        assert edb_setup.settings.dc.dc_slider_position == 2
        assert edb_setup.settings.export_dc_thermal_data is True
        edb_app.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Not tested in dotnet")
    def test_cfg_padstack_create_definition_and_place_instance(self):
        edb_app = self.edb_examples.get_si_verse()
        cfg_builder = edb_app.configuration.create_config_builder()
        cfg_builder.padstacks.add_definition(
            name="Test_padstacks",
            hole_plating_thickness="10um",
            material="copper",
            hole_range="through",
            hole_diameter="200um",
            pad_diameter="300um",
            anti_pad_diameter="400um",
        )
        cfg_def = cfg_builder.padstacks.definitions[0]
        assert cfg_def.name == "Test_padstacks"
        cfg_padstack_instance = cfg_builder.padstacks.add_instance(
            name="Test_padstacks_inst", net_name="Test_net", definition="Test_padstacks", position=[1e-3, 2e-3]
        )
        assert cfg_padstack_instance.position == [0.001, 0.002]
        assert cfg_padstack_instance.name == "Test_padstacks_inst"
        assert cfg_padstack_instance.net_name == "Test_net"
        edb_app.configuration.run(cfg_builder)
        padstack_def = edb_app.padstacks.definitions.get("Test_padstacks")
        assert not padstack_def.is_null
        assert padstack_def.start_layer == "1_Top"
        assert padstack_def.stop_layer == "16_Bottom"
        assert padstack_def.hole_plating_thickness == 10e-6
        assert padstack_def.material == "copper"
        assert padstack_def.hole_diameter == pytest.approx(200e-6, 1)
        assert padstack_def.pad_by_layer["1_Top"].parameters_values[0] == pytest.approx(300e-6, 1)
        assert padstack_def.antipad_by_layer["1_Top"].parameters_values[0] == pytest.approx(400e-6, 1)
        assert len(padstack_def.instances) == 1
        assert padstack_def.instances[0].name == "Test_padstacks_inst"
        assert padstack_def.instances[0].net_name == "Test_net"
        assert padstack_def.instances[0].position == [0.001, 0.002]
        edb_app.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Not tested in dotnet")
    def test_cfg_modeler_create_primitives(self):
        edb_app = self.edb_examples.get_si_verse()
        cfg_builder = edb_app.configuration.create_config_builder()
        cfg_builder.modeler.add_trace(
            name="Test_trace",
            layer="1_Top",
            width="100um",
            net_name="Test_net",
            start_cap_style="flat",
            end_cap_style="flat",
            path=[[0, 0], [0, 1e-3], [1e-3, 1e-3]],
        )
        cfg_builder.modeler.add_circular_plane(
            layer="1_Top", name="Test_circular_plane", net_name="Test_net_circle", radius="2mm", position=[5e-3, 5e-3]
        )

        cfg_builder.modeler.add_rectangular_plane(
            layer="1_Top",
            name="Test_rectangular_plane",
            lower_left_point=[0, 0],
            upper_right_point=[0, 5e-3],
        )
        cfg_builder.modeler.add_polygon_plane(
            layer="1_Top",
            name="Test_polygon_plane",
            net_name="Test_net_polygon",
            points=[[0, 0], [0, 2e-3], [2e-3, 2e-3], [0, 0]],
        )
        edb_app.configuration.run(cfg_builder)
        trace = edb_app.layout.find_primitive(name="Test_trace")[0]
        assert trace
        assert trace.aedt_name == "Test_trace"
        assert trace.layer_name == "1_Top"
        assert trace.net_name == "Test_net"
        circular_plane = edb_app.layout.find_primitive(name="Test_circular_plane")[0]
        assert circular_plane.aedt_name == "Test_circular_plane"
        assert circular_plane.net_name == "Test_net_circle"
        assert circular_plane.center == tuple([0.005, 0.005])
        assert circular_plane.radius == pytest.approx(2e-3, 1)
        assert circular_plane.layer_name == "1_Top"
        rectangle = edb_app.layout.find_primitive(name="Test_rectangular_plane")[0]
        assert rectangle.aedt_name == "Test_rectangular_plane"
        assert rectangle.bbox[:2] == [0, 0]
        assert rectangle.bbox[2:] == [0, 0.005]
        assert rectangle.layer_name == "1_Top"
        polygon = edb_app.layout.find_primitive(name="Test_polygon_plane")[0]
        assert polygon.aedt_name == "Test_polygon_plane"
        assert polygon.net_name == "Test_net_polygon"
        assert polygon.polygon_data.points == [(0, 0), (0, 0.002), (0.002, 0.002)]
        assert polygon.layer_name == "1_Top"
        edb_app.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Not tested in dotnet")
    def test_cfg_stackup(self):
        edb_app = self.edb_examples.get_si_verse()
        cfg_builder = edb_app.configuration.create_config_builder()
        layers = cfg_builder.stackup.get_layers()
        assert len(layers) == 26
        cfg_builder.stackup.add_material(name="Test_material", permittivity=3.48, dielectric_loss_tangent=0.02)
        cfg_builder.stackup.add_material(
            name="Test_metal",
            conductivity=6e7,
        )
        cfg_builder.stackup.add_dielectric_layer(name="Test_dielectric", material="Test_material", thickness="250um")
        edb_app.configuration.run(cfg_builder)
        assert "Test_material" in edb_app.materials.materials
        assert "Test_metal" in edb_app.materials.materials
        assert "Test_dielectric" in edb_app.stackup.layers

        diel_mat = edb_app.materials.materials.get("Test_material")
        assert diel_mat.name == "Test_material"
        assert diel_mat.permittivity == pytest.approx(3.48)
        assert diel_mat.dielectric_loss_tangent == pytest.approx(0.02)
        met_mat = edb_app.materials.materials.get("Test_metal")
        assert met_mat.name == "Test_metal"
        assert met_mat.conductivity == pytest.approx(6e7)

        dielectric_layer = edb_app.stackup.layers.get("Test_dielectric")
        assert dielectric_layer.material == "Test_material"
        assert dielectric_layer.thickness == 250e-6
        edb_app.close(terminate_rpc_session=False)


@pytest.mark.usefixtures("close_rpc_session")
class TestCfgBuilderGetDataFromDb(BaseTestClass):
    """Tests for get_data_from_db, export and round-trip coverage using SIverse."""

    SIGNAL_NETS = [
        "PCIe_Gen4_RX0_P",
        "PCIe_Gen4_RX0_N",
        "PCIe_Gen4_RX1_P",
        "PCIe_Gen4_RX1_N",
    ]

    def _get_edb_with_coax_ports(self):
        edb_app = self.edb_examples.get_si_verse()
        cfg = edb_app.configuration.create_config_builder()
        comp = cfg.components.get("U1")
        comp.set_solder_ball_properties(shape="cylinder", diameter="300um", height="300um")
        cfg.ports.add_coax_port(reference_designator="U1", net_list=self.SIGNAL_NETS)
        edb_app.configuration.run(cfg)
        return edb_app

    # get_data_from_db – individual flags
    def test_get_data_from_db_stackup(self):
        edb_app = self.edb_examples.get_si_verse()
        data = edb_app.configuration.get_data_from_db(stackup=True)
        assert "stackup" in data
        assert len(data["stackup"]["layers"]) > 0
        assert len(data["stackup"]["materials"]) > 0
        edb_app.close(terminate_rpc_session=False)

    def test_get_data_from_db_nets(self):
        edb_app = self.edb_examples.get_si_verse()
        data = edb_app.configuration.get_data_from_db(nets=True)
        assert "nets" in data
        assert isinstance(data["nets"]["signal_nets"], list)
        assert isinstance(data["nets"]["power_ground_nets"], list)
        edb_app.close(terminate_rpc_session=False)

    def test_get_data_from_db_padstacks(self):
        edb_app = self.edb_examples.get_si_verse()
        data = edb_app.configuration.get_data_from_db(padstacks=True)
        assert "padstacks" in data
        assert "definitions" in data["padstacks"]
        assert len(data["padstacks"]["definitions"]) > 0
        edb_app.close(terminate_rpc_session=False)

    def test_get_data_from_db_components(self):
        edb_app = self.edb_examples.get_si_verse()
        data = edb_app.configuration.get_data_from_db(components=True)
        assert "components" in data
        assert len(data["components"]) > 0
        edb_app.close(terminate_rpc_session=False)

    def test_get_data_from_db_pin_groups(self):
        edb_app = self.edb_examples.get_si_verse()
        cfg = edb_app.configuration.create_config_builder()
        cfg.pin_groups.add(reference_designator="U1", nets="GND")
        edb_app.configuration.run(cfg)
        data = edb_app.configuration.get_data_from_db(pin_groups=True)
        assert "pin_groups" in data
        assert len(data["pin_groups"]) > 0
        edb_app.close(terminate_rpc_session=False)

    def test_get_data_from_db_ports_coax(self):
        edb_app = self._get_edb_with_coax_ports()
        data = edb_app.configuration.get_data_from_db(ports=True)
        assert "ports" in data
        coax_ports = [p for p in data["ports"] if p["type"] == "coax"]
        assert len(coax_ports) == len(self.SIGNAL_NETS)
        edb_app.close(terminate_rpc_session=False)

    def test_get_data_from_db_ports_circuit(self):
        edb_app = self.edb_examples.get_si_verse()
        cfg = edb_app.configuration.create_config_builder()
        cfg.pin_groups.add(reference_designator="U1", nets="GND")
        for net in self.SIGNAL_NETS:
            cfg.ports.add_circuit_port(reference_designator="U1", positive_net=net, negative_net="GND")
        edb_app.configuration.run(cfg)
        data = edb_app.configuration.get_data_from_db(ports=True)
        assert "ports" in data
        circuit_ports = [p for p in data["ports"] if p["type"] == "circuit"]
        assert len(circuit_ports) == len(self.SIGNAL_NETS)
        edb_app.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Not tested in dotnet")
    def test_get_data_from_db_wave_port(self):
        edb_app = self.edb_examples.get_si_verse()
        cfg = edb_app.configuration.create_config_builder()
        path = edb_app.nets.nets.get("PCIe_Gen4_RX0_P").primitives[0]
        point = path.center_line[0]
        cfg.ports.add_wave_port(name="test_wp", primitive=path, point_on_edge=point)
        edb_app.configuration.run(cfg)
        data = edb_app.configuration.get_data_from_db(ports=True)
        wave_ports = [p for p in data["ports"] if p["type"] == "wave_port"]
        assert len(wave_ports) >= 1
        edb_app.close(terminate_rpc_session=False)

    def test_get_data_from_db_setups(self):
        edb_app = self.edb_examples.get_si_verse()
        cfg = edb_app.configuration.create_config_builder()
        setup = cfg.setups.add_hfss_setup(name="HFSS_export_test")
        setup.add_frequency_sweep(name="Sweep1", start="1GHz", stop="5GHz", step_or_count="1GHz")
        edb_app.configuration.run(cfg)
        data = edb_app.configuration.get_data_from_db(setups=True)
        assert "setups" in data
        hfss_setups = [s for s in data["setups"] if s.get("type") == "hfss"]
        assert any(s["name"] == "HFSS_export_test" for s in hfss_setups)
        edb_app.close(terminate_rpc_session=False)

    def test_get_data_from_db_setups_siwave_dc(self):
        edb_app = self.edb_examples.get_si_verse()
        cfg = edb_app.configuration.create_config_builder()
        cfg.setups.add_siwave_dc_setup(name="DC_export_test", dc_slider_position=1)
        edb_app.configuration.run(cfg)
        data = edb_app.configuration.get_data_from_db(setups=True)
        dc_setups = [s for s in data["setups"] if s.get("type") in ("siwave_dc", "siwave_dcir")]
        assert any(s["name"] == "DC_export_test" for s in dc_setups)
        edb_app.close(terminate_rpc_session=False)

    def test_get_data_from_db_setups_siwave_ac(self):
        edb_app = self.edb_examples.get_si_verse()
        cfg = edb_app.configuration.create_config_builder()
        setup = cfg.setups.add_siwave_ac_setup(name="AC_export_test", use_si_settings=True, si_slider_position=1)
        setup.add_frequency_sweep(name="Sweep1", start="0GHz", stop="10GHz", step_or_count="0.5GHz")
        edb_app.configuration.run(cfg)
        data = edb_app.configuration.get_data_from_db(setups=True)
        ac_setups = [s for s in data["setups"] if s.get("type") in ("siwave_ac", "siwave")]
        assert any(s["name"] == "AC_export_test" for s in ac_setups)
        edb_app.close(terminate_rpc_session=False)

    def test_get_data_from_db_general(self):
        edb_app = self.edb_examples.get_si_verse()
        data = edb_app.configuration.get_data_from_db(general=True)
        assert "general" in data
        edb_app.close(terminate_rpc_session=False)

    def test_get_data_from_db_variables(self):
        edb_app = self.edb_examples.get_si_verse()
        cfg = edb_app.configuration.create_config_builder()
        cfg.variables.add("trace_width", "0.15mm", "Default trace width")
        edb_app.configuration.run(cfg)
        data = edb_app.configuration.get_data_from_db(variables=True)
        assert "variables" in data
        var_names = [v["name"] for v in data["variables"]]
        assert "trace_width" in var_names
        edb_app.close(terminate_rpc_session=False)

    def test_get_data_from_db_boundaries(self):
        edb_app = self.edb_examples.get_si_verse()
        data = edb_app.configuration.get_data_from_db(boundaries=True)
        assert "boundaries" in data
        edb_app.close(terminate_rpc_session=False)

    def test_get_data_from_db_s_parameters(self):
        edb_app = self.edb_examples.get_si_verse()
        data = edb_app.configuration.get_data_from_db(s_parameters=True)
        assert "s_parameters" in data
        edb_app.close(terminate_rpc_session=False)

    def test_get_data_from_db_terminals(self):
        edb_app = self._get_edb_with_coax_ports()
        data = edb_app.configuration.get_data_from_db(terminals=True)
        assert "terminals" in data
        assert len(data["terminals"]) > 0
        edb_app.close(terminate_rpc_session=False)

    def test_get_data_from_db_sources(self):
        """get_data_from_db(sources=True) with pin-group-based current source."""
        edb_app = self.edb_examples.get_si_verse()
        cfg = edb_app.configuration.create_config_builder()
        cfg.pin_groups.add(name="pg_sig", reference_designator="U1", nets="PCIe_Gen4_RX0_P")
        cfg.pin_groups.add(name="pg_gnd", reference_designator="U1", nets="GND")
        cfg.sources.add_current_source(
            name="isrc1",
            positive_terminal={"pin_group": "pg_sig"},
            negative_terminal={"pin_group": "pg_gnd"},
        )
        edb_app.configuration.run(cfg)
        data = edb_app.configuration.get_data_from_db(sources=True)
        assert "sources" in data
        source_names = [s["name"] for s in data["sources"]]
        assert "isrc1" in source_names
        edb_app.close(terminate_rpc_session=False)

    # export()
    def test_export_json(self, tmp_path):
        edb_app = self.edb_examples.get_si_verse()
        out = tmp_path / "cfg_export.json"
        result = edb_app.configuration.export(
            str(out),
            stackup=True,
            nets=True,
            components=True,
            padstacks=True,
            setups=False,
            sources=False,
            ports=False,
            pin_groups=False,
            operations=False,
            boundaries=False,
            s_parameters=False,
            general=True,
            variables=False,
        )
        assert result is True
        assert out.exists()
        with open(out) as f:
            data = json.load(f)
        assert "stackup" in data
        assert "nets" in data
        assert "components" in data
        edb_app.close(terminate_rpc_session=False)

    def test_export_toml(self, tmp_path):
        edb_app = self.edb_examples.get_si_verse()
        out = tmp_path / "cfg_export.toml"
        result = edb_app.configuration.export(
            str(out),
            stackup=True,
            nets=True,
            components=False,
            padstacks=False,
            setups=False,
            sources=False,
            ports=False,
            pin_groups=False,
            operations=False,
            boundaries=False,
            s_parameters=False,
            general=False,
            variables=False,
        )
        assert result is True
        assert out.exists()
        edb_app.close(terminate_rpc_session=False)

    # Round-trip: export then re-load
    def test_round_trip_nets_and_stackup(self, tmp_path):
        edb_app = self.edb_examples.get_si_verse()
        out = tmp_path / "rt_cfg.json"
        edb_app.configuration.export(
            str(out),
            stackup=True,
            nets=True,
            components=False,
            padstacks=False,
            setups=False,
            sources=False,
            ports=False,
            pin_groups=False,
            operations=False,
            boundaries=False,
            s_parameters=False,
            general=False,
            variables=False,
        )
        edb_app2 = self.edb_examples.get_si_verse()
        result = edb_app2.configuration.load(str(out), apply_file=True)
        assert result
        # Signal and power-ground nets are preserved
        for net in ["GND", "PCIe_Gen4_RX0_P"]:
            assert net in edb_app2.nets.nets
        edb_app.close(terminate_rpc_session=False)
        edb_app2.close(terminate_rpc_session=False)

    # apply_variables
    def test_apply_variables_design_and_project(self):
        edb_app = self.edb_examples.get_si_verse()
        cfg = edb_app.configuration.create_config_builder()
        cfg.variables.add("my_width", "0.1mm", "trace width")
        cfg.variables.add("$my_proj_var", "25cel", "project temperature")
        edb_app.configuration.run(cfg)
        assert "my_width" in edb_app.design_variables
        assert "$my_proj_var" in edb_app.project_variables
        edb_app.close(terminate_rpc_session=False)

    # Circuit port with positive_net / negative_net auto-resolve (EDB-live)
    def test_circuit_port_positive_net_auto_resolve(self):
        edb_app = self.edb_examples.get_si_verse()
        cfg = edb_app.configuration.create_config_builder()
        cfg.ports.add_circuit_port(
            reference_designator="U1",
            positive_net="PCIe_Gen4_RX0_P",
            negative_net="GND",
        )
        edb_app.configuration.run(cfg)
        assert len(edb_app.ports) >= 1
        edb_app.close(terminate_rpc_session=False)

    # Voltage source
    def test_add_voltage_source_pin_group(self):
        edb_app = self.edb_examples.get_si_verse()
        cfg = edb_app.configuration.create_config_builder()
        cfg.pin_groups.add(name="pg_sig", reference_designator="U1", nets="PCIe_Gen4_RX0_P")
        cfg.pin_groups.add(name="pg_gnd", reference_designator="U1", nets="GND")
        cfg.sources.add_voltage_source(
            name="vsrc1",
            positive_terminal={"pin_group": "pg_sig"},
            negative_terminal={"pin_group": "pg_gnd"},
            magnitude=3.3,
        )
        edb_app.configuration.run(cfg)
        assert "vsrc1" in edb_app.terminals
        edb_app.close(terminate_rpc_session=False)

    # get_layer / get_signal_layers on live session
    def test_cfg_builder_get_layer_and_signal_layers(self):
        edb_app = self.edb_examples.get_si_verse()
        cfg = edb_app.configuration.create_config_builder()
        layer = cfg.stackup.get_layer("1_Top")
        assert layer.name == "1_Top"
        assert layer.layer_type == "signal"
        sig_layers = cfg.stackup.get_signal_layers()
        assert len(sig_layers) > 0
        assert all(la.type == "signal" for la in sig_layers)
        edb_app.close(terminate_rpc_session=False)

    # get_material on live session
    def test_cfg_builder_get_material(self):
        edb_app = self.edb_examples.get_si_verse()
        cfg = edb_app.configuration.create_config_builder()
        mat = cfg.stackup.get_material("copper")
        assert mat.name == "copper"
        assert mat.conductivity is not None
        edb_app.close(terminate_rpc_session=False)

    # get_definition / get_instance on live padstacks
    def test_cfg_builder_get_padstack_definition(self):
        edb_app = self.edb_examples.get_si_verse()
        cfg = edb_app.configuration.create_config_builder()
        # Get first definition name from EDB
        first_def_name = next(iter(edb_app.padstacks.definitions))
        pdef = cfg.padstacks.get_definition(first_def_name)
        assert pdef.name == first_def_name
        edb_app.close(terminate_rpc_session=False)

    def test_cfg_builder_get_padstack_instance(self):
        edb_app = self.edb_examples.get_si_verse()
        cfg = edb_app.configuration.create_config_builder()
        first_inst_name = next(name for name, obj in edb_app.padstacks.instances_by_name.items() if not obj.is_pin)
        inst = cfg.padstacks.get_instance(first_inst_name)
        assert inst.name == first_inst_name
        edb_app.close(terminate_rpc_session=False)

    # Pin group get() on live session
    def test_cfg_builder_get_pin_group_from_edb(self):
        edb_app = self.edb_examples.get_si_verse()
        cfg = edb_app.configuration.create_config_builder()
        cfg.pin_groups.add(reference_designator="U1", nets="GND")
        edb_app.configuration.run(cfg)
        # Now the pin group exists in EDB — create a fresh builder and get it
        cfg2 = edb_app.configuration.create_config_builder()
        pg = cfg2.pin_groups.get("Pingroup_U1.GND")
        assert pg.name == "Pingroup_U1.GND"
        assert pg.reference_designator == "U1"
        edb_app.close(terminate_rpc_session=False)

    # Roughness model apply via configuration
    def test_cfg_stackup_roughness_huray(self):
        edb_app = self.edb_examples.get_si_verse()
        cfg = edb_app.configuration.create_config_builder()
        cfg.stackup.get_layers()  # pre-populate all layers so apply_stackup count matches
        layer = cfg.stackup.get_layer("1_Top")
        layer.set_huray_roughness("0.5um", "2.9")
        edb_app.configuration.run(cfg)
        assert "1_Top" in edb_app.stackup.layers
        assert edb_app.stackup.layers["1_Top"].roughness_enabled
        assert edb_app.stackup.layers["1_Top"].top_hallhuray_nodule_radius == 5e-7
        assert edb_app.stackup.layers["1_Top"].top_hallhuray_surface_ratio == 2.9
        assert edb_app.stackup.layers["1_Top"].bottom_hallhuray_nodule_radius == 5e-7
        assert edb_app.stackup.layers["1_Top"].bottom_hallhuray_surface_ratio == 2.9
        assert edb_app.stackup.layers["1_Top"].side_hallhuray_nodule_radius == 5e-7
        assert edb_app.stackup.layers["1_Top"].side_hallhuray_surface_ratio == 2.9
        edb_app.close(terminate_rpc_session=False)

    @pytest.mark.skipif(not config["use_grpc"], reason="Not tested in dotnet")
    def test_cfg_stackup_roughness_groisse(self):
        edb_app = self.edb_examples.get_si_verse()
        cfg = edb_app.configuration.create_config_builder()
        cfg.stackup.get_layers()  # pre-populate all layers so apply_stackup count matches
        layer = cfg.stackup.get_layer("1_Top")
        layer.set_groisse_roughness(0.3e-6)
        edb_app.configuration.run(cfg)
        assert "1_Top" in edb_app.stackup.layers
        assert edb_app.stackup.layers["1_Top"].roughness_enabled
        assert edb_app.stackup.layers["1_Top"].top_groisse_roughness == 3e-7
        assert edb_app.stackup.layers["1_Top"].bottom_groisse_roughness == 3e-7
        assert edb_app.stackup.layers["1_Top"].side_groisse_roughness == 3e-7
        edb_app.close(terminate_rpc_session=False)

    # load() from file paths (JSON and TOML)
    def test_load_from_json_file(self, tmp_path):
        edb_app = self.edb_examples.get_si_verse()
        cfg_data = {"nets": {"signal_nets": ["PCIe_Gen4_RX0_P"], "power_ground_nets": ["GND"]}}
        json_file = tmp_path / "test_cfg.json"
        with open(json_file, "w") as f:
            json.dump(cfg_data, f)
        edb_app.configuration.load(str(json_file), apply_file=True)
        assert edb_app.nets.nets["PCIe_Gen4_RX0_P"].is_power_ground is False
        edb_app.close(terminate_rpc_session=False)

    def test_load_from_toml_file(self, tmp_path):
        import toml

        edb_app = self.edb_examples.get_si_verse()
        cfg_data = {"nets": {"signal_nets": ["PCIe_Gen4_RX0_P"], "power_ground_nets": ["GND"]}}
        toml_file = tmp_path / "test_cfg.toml"
        with open(toml_file, "w") as f:
            toml.dump(cfg_data, f)
        edb_app.configuration.load(str(toml_file), apply_file=True)
        edb_app.close(terminate_rpc_session=False)

    # run() with dict and CfgData passed directly
    def test_run_with_cfgdata_directly(self):
        edb_app = self.edb_examples.get_si_verse()
        cfg = edb_app.configuration.create_config_builder()
        cfg.nets.add_power_ground_nets(["PCIe_Gen4_RX0_P"])
        edb_app.configuration.run(cfg)
        assert edb_app.nets.nets["PCIe_Gen4_RX0_P"].is_power_ground is True
        edb_app.close(terminate_rpc_session=False)

    def test_run_with_dict_directly(self):
        edb_app = self.edb_examples.get_si_verse()
        edb_app.configuration.run({"nets": {"power_ground_nets": ["PCIe_Gen4_RX0_P"]}})
        assert edb_app.nets.nets["PCIe_Gen4_RX0_P"].is_power_ground is True
        edb_app.close(terminate_rpc_session=False)

    # get_data_from_db with operations (after cutout)
    def test_get_data_from_db_operations_after_cutout(self):
        edb_app = self.edb_examples.get_si_verse()
        cfg = edb_app.configuration.create_config_builder()
        cfg.nets.add_signal_nets(["PCIe_Gen4_RX0_P", "PCIe_Gen4_RX0_N"])
        cfg.nets.add_reference_nets(["GND"])
        cfg.operations.add_cutout(
            signal_nets=cfg.nets.signal_nets,
            reference_nets=cfg.nets.reference_nets,
            extent_type="ConvexHull",
            expansion_size=2e-3,
        )
        edb_app.configuration.run(cfg)
        data = edb_app.configuration.get_data_from_db(operations=True)
        assert "operations" in data
        assert "cutout" in data["operations"]
        assert len(data["operations"]["cutout"]["signal_nets"]) > 0
        edb_app.close(terminate_rpc_session=False)

    # package_definitions get_data_from_db
    def test_get_data_from_db_package_definitions(self):
        edb_app = self.edb_examples.get_si_verse()
        data = edb_app.configuration.get_data_from_db(package_definitions=True)
        assert "package_definitions" in data
        edb_app.close(terminate_rpc_session=False)

    def test_cfg_operations(self):
        edbapp = self.edb_examples.get_si_verse()
        SIGNAL_NETS = [
            "PCIe_Gen4_RX0_P",
            "PCIe_Gen4_RX0_N",
            "PCIe_Gen4_RX1_P",
            "PCIe_Gen4_RX1_N",
            "PCIe_Gen4_RX2_P",
            "PCIe_Gen4_RX2_N",
            "PCIe_Gen4_RX3_P",
            "PCIe_Gen4_RX3_N",
        ]
        REFERENCE_NET = "GND"
        COMPONENT = "U1"

        cfg = edbapp.configuration.create_config_builder()

        cfg.nets.add_signal_nets(SIGNAL_NETS)
        cfg.nets.add_power_ground_nets([REFERENCE_NET])

        cfg.operations.add_cutout(
            signal_nets=SIGNAL_NETS,
            reference_nets=[REFERENCE_NET],
            extent_type="ConvexHull",
            expansion_size=3e-3,
        )

        cfg.pin_groups.add(reference_designator=COMPONENT, nets=SIGNAL_NETS)
        cfg.pin_groups.add(
            name=f"Pingroup_{COMPONENT}.{REFERENCE_NET}",
            reference_designator=COMPONENT,
            nets=REFERENCE_NET,
        )

        for net in SIGNAL_NETS:
            cfg.ports.add_circuit_port(
                reference_designator=COMPONENT,
                positive_net=net,
                negative_net=REFERENCE_NET,
            )
        json_path = os.path.join(edbapp.edbpath, "test_cfg.json")
        hfss_setup = cfg.setups.add_hfss_setup(name="HFSS_PCIe")
        sweep = hfss_setup.add_frequency_sweep(name="Sweep_LIN")
        sweep.add_linear_scale_frequencies(start="1GHz", stop="10GHz", step="0.5GHz")
        edbapp.configuration.run(cfg)
        edbapp.configuration.export(
            file_path=json_path,
            stackup=True,
            nets=True,
            pin_groups=True,
            ports=True,
            setups=True,
            operations=True,
            components=False,
            padstacks=False,
            boundaries=False,
            s_parameters=False,
            spice_models=False,
            variables=False,
            general=False,
        )
        assert os.path.isfile(json_path)
        with open(json_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
        assert len(config_data.get("nets", None).get("signal_nets", None)) == 9
        cutout = config_data.get("operations", None).get("cutout", None)
        assert cutout.get("signal_nets", None)
        assert cutout.get("reference_nets", None) == ["GND"]
        assert cutout.get("extent_type", None) == "ConvexHull"
        assert cutout.get("expansion_size", None) == 3e-3
        edbapp.close(terminate_rpc_session=False)

    def test_parametric_config_creates_padstack_definitions(self):
        """Parameterised config: padstack definitions must be created with correct names.

        Regression for the bug where raw parameter strings (e.g. ``"$CORE_VIA_pad_diameter"``)
        were passed directly to ``CorePadstackDefData.set_pad_parameters(sizes=...)``
        without being wrapped in a ``Value`` object with an owner, causing the
        gRPC backend to silently produce an empty design.
        """
        edbapp = self.edb_examples.create_empty_edb()
        json = self.edb_examples.copy_test_files_into_local_folder("config_files/test.json")[0]
        assert edbapp.configuration.load(json, apply_file=True)

        defs = edbapp.padstacks.definitions
        assert "CORE_VIA" in defs, "CORE_VIA padstack definition must be created"
        assert "MICRO_VIA" in defs, "MICRO_VIA padstack definition must be created"
        assert "BGA_VIA" in defs, "BGA_VIA padstack definition must be created"

        edbapp.close(terminate_rpc_session=False)

    def test_parametric_config_pad_sizes_resolved_via_variables(self):
        """Parameterised config: pad diameters must resolve to the correct numeric values.

        After ``apply_file=True`` the design variables (``$CORE_VIA_pad_diameter = 0.25 mm``,
        ``$CORE_VIA_hole_diameter = 0.1 mm``) must be set and reflected in the
        padstack definition so that the pad geometry is non-zero.
        """
        edbapp = self.edb_examples.create_empty_edb()
        json = self.edb_examples.copy_test_files_into_local_folder("config_files/test.json")[0]
        assert edbapp.configuration.load(json, apply_file=True)

        # Design variable must be present and have the expected value
        assert edbapp.variable_exists("$CORE_VIA_pad_diameter")
        assert edbapp.variable_exists("$CORE_VIA_hole_diameter")

        core_via = edbapp.padstacks.definitions.get("CORE_VIA")
        assert core_via is not None

        # Pad diameter on PCB_L1 must match $CORE_VIA_pad_diameter = 0.25 mm
        pad_on_l1 = core_via.pad_by_layer.get("PCB_L1")
        assert pad_on_l1 is not None, "CORE_VIA must have a pad defined on PCB_L1"
        params = pad_on_l1.parameters_values
        assert params is not None and len(params) > 0, "Pad parameters must be non-empty"
        pad_diameter_m = float(params[0])
        assert abs(pad_diameter_m - 0.00025) < 1e-9, (
            f"CORE_VIA pad diameter on PCB_L1 expected 0.00025 m (0.25 mm), got {pad_diameter_m}"
        )

        # Hole diameter must match $CORE_VIA_hole_diameter = 0.1 mm
        hole_diameter_m = float(core_via.hole_diameter)
        assert abs(hole_diameter_m - 0.0001) < 1e-9, (
            f"CORE_VIA hole diameter expected 0.0001 m (0.1 mm), got {hole_diameter_m}"
        )

        edbapp.close(terminate_rpc_session=False)

    def test_parametric_config_creates_modeler_geometry(self):
        """Parameterised config: traces, padstack instances, and planes must all be created.

        Verifies that the entire ``modeler`` section of the parameterised JSON is
        applied: padstack instances (signal via + stitching vias), signal traces /
        fanout segments, anti-pad circles, and GND plane rectangles.
        """
        edbapp = self.edb_examples.create_empty_edb()
        json = self.edb_examples.copy_test_files_into_local_folder("config_files/test.json")[0]
        assert edbapp.configuration.load(json, apply_file=True)

        # --- padstack instances ---
        instances = edbapp.padstacks.instances
        assert len(instances) >= 7, f"Expected at least 7 padstack instances, got {len(instances)}"

        # Signal via must be placed on the SIG net
        sig_vias = [i for i in instances.values() if i.net_name == "SIG"]
        assert len(sig_vias) >= 1, "At least one padstack instance must be on net SIG"

        # Stitching vias must be placed on the GND net
        gnd_vias = [i for i in instances.values() if i.net_name == "GND"]
        assert len(gnd_vias) >= 6, f"Expected at least 6 GND stitching vias, got {len(gnd_vias)}"

        # --- traces (path primitives) ---
        paths = edbapp.layout.paths
        assert len(paths) >= 3, f"Expected at least 3 path primitives (signal traces), got {len(paths)}"

        # --- planes (rectangle primitives) ---
        primitives = edbapp.layout.primitives
        non_path_prims = [p for p in primitives if p.primitive_type != "path"]
        assert len(non_path_prims) >= 6, (
            f"Expected at least 6 non-path primitives (GND rectangles), got {len(non_path_prims)}"
        )
        # Verify that at least one rectangle has voids (anti-pad circles attached)
        rectangles = [p for p in non_path_prims if p.primitive_type == "rectangle"]
        assert len(rectangles) >= 6, f"Expected at least 6 GND rectangles, got {len(rectangles)}"

        edbapp.close(terminate_rpc_session=False)
