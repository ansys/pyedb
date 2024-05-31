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

    def test_01_create_edb(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        for i in [
            "components.json",
            "setups_hfss.json",
        ]:
            with open(self.local_input_folder / i) as f:
                data = json.load(f)
            assert edbapp.configuration.load(data, apply_file=True)
        assert not edbapp.components.capacitors["C375"].is_enabled
        assert edbapp.components.instances["U1"].solder_ball_height == 406e-6
        assert edbapp.components.instances["U1"].solder_ball_diameter[0] == 244e-6
        assert edbapp.components.instances["U3"].type == "Other"
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
        with open(self.local_input_folder / "operations_cutout.json") as f:
            data = json.load(f)

        edbapp = edb_examples.get_si_verse()
        assert edbapp.configuration.load(data, apply_file=True)
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
        edbapp = edb_examples.get_si_verse()
        assert edbapp.configuration.load(str(self.local_input_folder / "package_def.json"), apply_file=True)
        assert edbapp.definitions.package["package_1"].maximum_power == 1
        assert edbapp.definitions.package["package_1"].therm_cond == 1
        assert edbapp.definitions.package["package_1"].theta_jb == 1
        assert edbapp.definitions.package["package_1"].theta_jc == 1
        assert edbapp.definitions.package["package_1"].height == 1
        assert edbapp.definitions.package["package_1"].heatsink.fin_base_height == 0.001
        assert edbapp.definitions.package["package_1"].heatsink.fin_height == 0.001
        assert edbapp.definitions.package["package_1"].heatsink.fin_orientation == "x_oriented"
        assert edbapp.definitions.package["package_1"].heatsink.fin_spacing == 0.001
        assert edbapp.definitions.package["package_1"].heatsink.fin_thickness == 0.004
        edbapp.close()

    def test_12_setup_siwave_dc(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        assert edbapp.configuration.load(str(self.local_input_folder / "setups_siwave_dc.json"), apply_file=True)
        edbapp.close()

    def test_13_stackup(self, edb_examples):
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
        assert edbapp.configuration.load(data, apply_file=True)
        assert list(edbapp.stackup.layers.keys())[:4] == ["1_Top", "Inner1", "DE2", "DE3"]
        assert edbapp.stackup.layers["1_Top"].thickness == 0.0005
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

    def test_components(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        config = edbapp.configuration.load(str(self.local_input_folder / "components.json"), apply_file=False)
        assert config.components
        capacitors = [comp for comp in config.components if comp.part_type.name == "CAPACITOR"]
        assert len(capacitors) == 2
        assert not capacitors[0].enabled
        assert not capacitors[-1].enabled
        inductor = next(comp for comp in config.components if comp.reference_designator == "L2")
        assert inductor.rlc_model.capacitance == "100nf"
        assert inductor.rlc_model.inductance == "1nh"
        assert inductor.rlc_model.resistance == "0.001"
        u1 = next(comp for comp in config.components if comp.reference_designator == "U1")
        assert u1.solder_balls.shape.name == "CYLINDER"
        assert u1.solder_balls.height == "406um"
        assert u1.solder_balls.diameter == "244um"
        assert u1.solder_balls.mid_diameter == "244um"
        assert u1.solder_balls.enable
        config = edbapp.configuration.load(str(self.local_input_folder / "components.json"), apply_file=True)
        assert edbapp.components["U1"].solder_ball_height == 406e-6
        assert edbapp.components["U1"].solder_ball_diameter[0] == 244e-6
        assert edbapp.components["U1"].solder_ball_diameter[1] == 244e-6
        assert not edbapp.components["C375"].is_enabled
        assert not edbapp.components["L2"].is_enabled
        assert edbapp.components["L2"].ind_value == "1nH"
        assert edbapp.components["L2"].cap_value == "100nF"
        assert edbapp.components["L2"].res_value == "0.001"
        edbapp.close()
