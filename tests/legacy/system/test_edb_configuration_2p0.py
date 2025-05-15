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

from pyedb.dotnet.edb import Edb as EdbType

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


def _assert_initial_ic_die_properties(component: dict):
    assert component["ic_die_properties"]["type"] == "no_die"
    assert "orientation" not in component["ic_die_properties"]
    assert "height" not in component["ic_die_properties"]


def _assert_final_ic_die_properties(component: dict):
    assert component["ic_die_properties"]["type"] == "flip_chip"
    assert component["ic_die_properties"]["orientation"] == "chip_down"
    assert component["solder_ball_properties"]["diameter"] == "244um"


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
        assert set(list(edbapp.nets.nets.keys())) == set(["SFPA_RX_P", "SFPA_RX_N", "GND", "pyedb_cutout"])
        edbapp.close()

    def test_13b_stackup_materials(self, edb_examples):
        data = {
            "stackup": {
                "materials": [
                    {
                        "name": "copper",
                        "conductivity": 570000000,
                        "thermal_modifier": [
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
                        "thermal_modifier": [
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
                if p == "thermal_modifier":
                    continue
                assert value == target_mat[p]
        edbapp.close()
