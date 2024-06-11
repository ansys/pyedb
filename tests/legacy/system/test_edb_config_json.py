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
import json
from pathlib import Path

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.legacy]


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, local_scratch):
        self.local_scratch = local_scratch
        local_path = Path(__file__).parent.parent.parent
        example_folder = local_path / "example_models" / "TEDB"
        src_edb = example_folder / "ANSYS-HSD_V1.aedb"
        src_input_folder = example_folder / "edb_config_json"

        self.local_edb = Path(self.local_scratch.path) / "ansys.aedb"
        self.local_input_folder = Path(self.local_scratch.path) / "input_files"
        self.local_scratch.copyfolder(str(src_edb), str(self.local_edb))
        self.local_scratch.copyfolder(str(src_input_folder), str(self.local_input_folder))
        self.local_scratch.copyfile(
            str(example_folder / "GRM32_DC0V_25degC_series.s2p"),
            str(self.local_input_folder / "GRM32_DC0V_25degC_series.s2p"),
        )
        self.local_scratch.copyfile(
            str(example_folder / "GRM32ER72A225KA35_25C_0V.sp"),
            str(self.local_input_folder / "GRM32ER72A225KA35_25C_0V.sp"),
        )

    def test_01_setups(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        for i in [
            "setups_hfss.json",
        ]:
            with open(self.local_input_folder / i) as f:
                data = json.load(f)
            assert edbapp.configuration.load(data, apply_file=True)

        edbapp.close()

    def test_01a_setups_frequency_sweeps(self, edb_examples):
        data = {
            "setups": [
                {
                    "name": "hfss_setup_1",
                    "type": "HFSS",
                    "f_adapt": "5GHz",
                    "max_num_passes": 10,
                    "max_mag_delta_s": 0.02,
                    "freq_sweep": [
                        {
                            "name": "sweep1",
                            "type": "Interpolation",
                            "frequencies": [
                                {
                                    "distribution": "linear scale",
                                    "start": "50MHz",
                                    "stop": "200MHz",
                                    "step": "10MHz"
                                }
                            ]
                        },
                        {
                            "name": "sweep2",
                            "type": "Interpolation",
                            "frequencies": [
                                {
                                    "distribution": "log scale",
                                    "start": "1KHz",
                                    "stop": "100kHz",
                                    "samples": 10
                                }
                            ]
                        },
                        {
                            "name": "sweep3",
                            "type": "Interpolation",
                            "frequencies": [
                                {
                                    "distribution": "linear count",
                                    "start": "10MHz",
                                    "stop": "20MHz",
                                    "points": 11
                                }
                            ]
                        }
                    ]
                },
            ]
        }
        edbapp = edb_examples.get_si_verse()
        assert edbapp.configuration.load(data, apply_file=True)
        #assert len(edbapp.setups["hfss_setup_1"].frequency_sweeps["sweep1"].frequencies) == 16
        #assert len(edbapp.setups["hfss_setup_1"].frequency_sweeps["sweep2"].frequencies) == 20
        #assert len(edbapp.setups["hfss_setup_1"].frequency_sweeps["sweep3"].frequencies) == 11
        edbapp.close()

    def test_02_pin_groups(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        pin_groups = [
            {"name": "U9_5V_1", "reference_designator": "U9", "pins": ["32", "33"]},
            {"name": "U9_GND", "reference_designator": "U9", "net": "GND"},
        ]
        data = {"pin_groups": pin_groups}
        assert edbapp.configuration.load(data, apply_file=True)
        assert "U9_5V_1" in edbapp.siwave.pin_groups
        assert "U9_GND" in edbapp.siwave.pin_groups
        edbapp.close()

    def test_03_spice_models(self, edb_examples):
        with open(self.local_input_folder / "spice.json") as f:
            data = json.load(f)
        data["general"]["spice_model_library"] = self.local_input_folder

        edbapp = edb_examples.get_si_verse()
        assert edbapp.configuration.load(data, apply_file=True)
        assert edbapp.components["R107"].model.model_name
        assert edbapp.components["R107"].model.spice_file_path
        assert edbapp.components["R106"].model.spice_file_path
        edbapp.close()

    def test_04_nets(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        assert edbapp.configuration.load(str(self.local_input_folder / "nets.json"), apply_file=True)
        assert edbapp.nets["1.2V_DVDDL"].is_power_ground
        assert not edbapp.nets["SFPA_VCCR"].is_power_ground
        edbapp.close()

    def test_05_ports(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        assert edbapp.configuration.load(str(self.local_input_folder / "ports_coax.json"), apply_file=True)
        assert edbapp.configuration.load(str(self.local_input_folder / "ports_circuit.json"), apply_file=True)
        assert "COAX_U1_AM17" in edbapp.ports
        assert "COAX_U1_PCIe_Gen4_TX2_CAP_N" in edbapp.ports
        assert "CIRCUIT_C375_1_2" in edbapp.ports
        assert "CIRCUIT_X1_B8_GND" in edbapp.ports
        assert "CIRCUIT_U7_VDD_DDR_GND" in edbapp.ports
        edbapp.close()

    def test_05b_ports_coax(self, edb_examples):
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
        ]
        data = {"ports": ports}
        edbapp = edb_examples.get_si_verse()
        assert edbapp.configuration.load(data, apply_file=True)
        assert edbapp.ports["COAX_U1_AM17"]
        assert edbapp.ports["COAX_U1_PCIe_Gen4_TX2_CAP_N"]
        edbapp.close()

    def test_05c_ports_circuit_pin_net(self, edb_examples):
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
        edbapp = edb_examples.get_si_verse()
        assert edbapp.configuration.load(data, apply_file=True)
        assert edbapp.ports["CIRCUIT_X1_B8_GND"]
        assert edbapp.ports["CIRCUIT_X1_B8_GND"].is_circuit_port
        edbapp.close()

    def test_05c_ports_circuit_net_net_distributed(self, edb_examples):
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
        edbapp = edb_examples.get_si_verse()
        assert edbapp.configuration.load(data, apply_file=True)
        assert len(edbapp.ports) > 1
        edbapp.close()

    def test_05d_ports_pin_group(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
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
        edbapp.close()

    def test_05e_ports_circuit_net_net_distributed_nearest_ref(self, edb_examples):
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
        edbapp = edb_examples.get_si_verse()
        assert edbapp.configuration.load(data, apply_file=True)
        assert len(edbapp.ports) > 1
        edbapp.close()

    def test_06_s_parameters(self, edb_examples):
        with open(self.local_input_folder / "s_parameter.json") as f:
            data = json.load(f)
        data["general"]["s_parameter_library"] = self.local_input_folder

        edbapp = edb_examples.get_si_verse()
        assert edbapp.configuration.load(data, apply_file=True)
        assert len(edbapp.components.nport_comp_definition) == 2
        assert edbapp.components.nport_comp_definition["CAPC3216X180X55ML20T25"].reference_file
        assert len(edbapp.components.nport_comp_definition["CAPC3216X180X55ML20T25"].components) == 9
        assert len(edbapp.components.nport_comp_definition["CAPC3216X190X55ML30T25"].components) == 12
        edbapp.close()

    def test_07_boundaries(self, edb_examples):
        with open(self.local_input_folder / "boundaries.json") as f:
            data = json.load(f)

        edbapp = edb_examples.get_si_verse()
        assert edbapp.configuration.load(data, apply_file=True)
        edbapp.close()

    def test_08a_operations_cutout(self, edb_examples):
        data = {
            "operations": {
                "cutout": {
                    "signal_list": ["SFPA_RX_P", "SFPA_RX_N"],
                    "reference_list": ["GND"],
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
                    "simple_pad_check": True,
                    "keep_lines_as_path": False,
                }
            }
        }
        edbapp = edb_examples.get_si_verse()
        assert edbapp.configuration.load(data, apply_file=True)
        assert set(list(edbapp.nets.nets.keys())) == set(["SFPA_RX_P", "SFPA_RX_N", "GND"])
        edbapp.close()

    def test_09_padstacks(self, edb_examples):
        data = {
            "padstacks": {
                "definitions": [
                    {
                        "name": "v40h20",
                        # "hole_diameter": "0.18mm",
                        "hole_plating_thickness": "25um",
                        "hole_material": "copper",
                        "hole_range": "through",
                    }
                ],
                "instances": [
                    {
                        "name": "Via998",
                        "backdrill_top": {
                            "drill_to_layer": "Inner3(Sig1)",
                            "drill_diameter": "0.5mm",
                            "stub_length": "0.2mm",
                        },
                        "backdrill_bottom": {
                            "drill_to_layer": "Inner4(Sig2)",
                            "drill_diameter": "0.5mm",
                            "stub_length": "0.2mm",
                        },
                    }
                ],
            }
        }

        edbapp = edb_examples.get_si_verse()
        assert edbapp.configuration.load(data, apply_file=True)
        edbapp.close()

    def test_10_general(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        assert edbapp.configuration.load(str(self.local_input_folder / "general.toml"), apply_file=True)
        edbapp.close()

    def test_11_package_definitions(self, edb_examples):
        data = {
            "package_definitions": [
                {
                    "name": "package_1",
                    "component_definition": "SMTC-MECT-110-01-M-D-RA1_V",
                    "maximum_power": 1,
                    "therm_cond": 2,
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
                    "therm_cond": 2,
                    "theta_jb": 3,
                    "theta_jc": 4,
                    "height": 5,
                    "apply_to_all": True,
                    "components": ["L8"],
                },
            ]
        }
        edbapp = edb_examples.get_si_verse()
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
                            hs_value = edbapp.edb_value(hs_value).ToDouble()
                        assert hs_value == target_heatsink[hs_p]
                else:
                    assert value == target_pdef[p]
        edbapp.close()

    def test_12_setup_siwave_dc(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        assert edbapp.configuration.load(str(self.local_input_folder / "setups_siwave_dc.json"), apply_file=True)
        edbapp.close()

    def test_13_stackup_layers(self, edb_examples):
        data = {
            "stackup": {
                "layers": [
                    {
                        "fill_material": "Solder Resist",
                        "material": "copper",
                        "name": "1_Top",
                        "thickness": "0.5mm",
                        "type": "signal",
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
        edbapp = edb_examples.get_si_verse()
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
                value = edbapp.edb_value(value).ToDouble() if p in ["thickness"] else value
                assert value == target_mat[p]
        edbapp.close()

    def test_13b_stackup_materials(self, edb_examples):
        data = {
            "stackup": {
                "materials": [
                    {"name": "copper", "conductivity": 570000000},
                    {"name": "Megtron4", "permittivity": 3.77, "dielectric_loss_tangent": 0.005},
                    {"name": "Megtron4_2", "permittivity": 3.77, "dielectric_loss_tangent": 0.005},
                    {"name": "Solder Resist", "permittivity": 4, "dielectric_loss_tangent": 0},
                ]
            }
        }
        edbapp = edb_examples.get_si_verse()
        assert edbapp.configuration.load(data, apply_file=True)
        data_from_db = edbapp.configuration.get_data_from_db(stackup=True)
        for mat in data["stackup"]["materials"]:
            target_mat = [i for i in data_from_db["stackup"]["materials"] if i["name"] == mat["name"]][0]
            for p, value in mat.items():
                assert value == target_mat[p]
        edbapp.close()

    def test_13c_stackup_create_stackup(self, edb_examples):
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
                        "fill_material": "megtron4",
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
        edbapp = edb_examples.create_empty_edb()

        assert edbapp.configuration.load(data, apply_file=True)

        data_from_db = edbapp.configuration.get_data_from_db(stackup=True)
        for lay in data["stackup"]["layers"]:
            target_mat = [i for i in data_from_db["stackup"]["layers"] if i["name"] == lay["name"]][0]
            for p, value in lay.items():
                value = edbapp.edb_value(value).ToDouble() if p in ["thickness"] else value
                assert value == target_mat[p]
        edbapp.close()

    def test_14_setup_siwave_syz(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        assert edbapp.configuration.load(str(self.local_input_folder / "setups_siwave_syz.json"), apply_file=True)
        setup = edbapp.setups["siwave_syz"]
        edbapp.close()

    def test_15b_sources(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        sources_v = [
            {
                "name": "VSOURCE_U2_1V0_GND",
                "reference_designator": "U2",
                "type": "voltage",
                "magnitude": 1,
                "distributed": False,
                "positive_terminal": {"net": "1V0"},
                "negative_terminal": {"net": "GND"},
            },
        ]
        data = {"sources": sources_v}
        assert edbapp.configuration.load(data, apply_file=True)
        assert edbapp.sources["VSOURCE_U2_1V0_GND"].magnitude == 1
        sources_i = [
            {
                "name": "ISOURCE",
                "reference_designator": "U1",
                "type": "current",
                "magnitude": 1,
                "distributed": True,
                "positive_terminal": {"net": "1V0"},
                "negative_terminal": {"net": "GND"},
            },
        ]
        data = {"sources": sources_i}
        assert edbapp.configuration.load(data, apply_file=True, append=False)
        assert not edbapp.sources["ISOURCE_U1_1V0_M16"].magnitude == 1
        edbapp.close()

    def test_15c_sources_nearest_ref(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
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
        edbapp.close()

    def test_16_components_rlc(self, edb_examples):
        components = [
            {
                "reference_designator": "C375",
                "enabled": False,
                "value": 100e-9,
            },
            {
                "reference_designator": "L2",
                "part_type": "resistor",
                "rlc_model": [
                    {
                        "type": "series",
                        "capacitance": "100nf",
                        "inductance": "1nh",
                        "resistance": "0.001",
                        "p1": "1",
                        "p2": "2",
                    }
                ],
            },
        ]
        data = {"components": components}
        edbapp = edb_examples.get_si_verse()
        assert edbapp.configuration.load(data, apply_file=True)
        assert edbapp.components["C375"].enabled == False
        assert edbapp.components["C375"].value == 100e-9
        assert edbapp.components["L2"].type == "Resistor"
        edbapp.close()

    def test_15b_component_solder_ball(self, edb_examples):
        components = [
            {
                "reference_designator": "U1",
                "part_type": "io",
                "solder_ball_properties": {"shape": "cylinder", "diameter": "244um", "height": "406um"},
                "port_properties": {
                    "reference_offset": "0.1mm",
                    "reference_size_auto": True,
                    "reference_size_x": 0,
                    "reference_size_y": 0,
                },
            },
        ]
        data = {"components": components}
        edbapp = edb_examples.get_si_verse()
        assert edbapp.configuration.load(data, apply_file=True)
        assert edbapp.components["U1"].type == "IO"
        assert edbapp.components["U1"].solder_ball_shape == "Cylinder"
        assert edbapp.components["U1"].solder_ball_height == 406e-6
        assert edbapp.components["U1"].solder_ball_diameter == (244e-6, 244e-6)

        edbapp.close()

    def test_16_export_to_external_file(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        data_file_path = Path(edb_examples.test_folder) / "test.json"
        edbapp.configuration.export(data_file_path)
        assert data_file_path.is_file()
