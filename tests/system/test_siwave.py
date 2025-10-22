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

import json
import os
import time

import pytest

from pyedb.siwave import Siwave
from tests.conftest import desktop_version, local_path
from tests.system.base_test_class import BaseTestClass

pytestmark = [pytest.mark.unit, pytest.mark.legacy]


@pytest.mark.skipif(True, reason="skipping test on CI because they fail in non-graphical")
class TestClass(BaseTestClass):
    @pytest.fixture(autouse=True)
    def init(self, local_scratch):
        self.local_scratch = local_scratch

    def test_siwave(self):
        """Create Siwave."""

        siw = Siwave(desktop_version)
        time.sleep(10)
        example_project = os.path.join(local_path, "example_models", "siwave", "siw_dc.siw")
        target_path = os.path.join(self.local_scratch.path, "siw_dc.siw")
        self.local_scratch.copyfile(example_project, target_path)
        assert siw
        assert siw.close_project()
        siw.open_project(target_path)
        siw.run_dc_simulation()
        export_report = os.path.join(siw.results_directory, "test.htm")
        assert siw.export_siwave_report("DC IR Sim 3", export_report)
        assert siw.export_dc_simulation_report("DC IR Sim 3", os.path.join(siw.results_directory, "test2"))
        export_data = os.path.join(siw.results_directory, "test.txt")
        assert siw.export_element_data("DC IR Sim 3", export_data)
        export_icepak = os.path.join(siw.results_directory, "icepak.aedt")
        assert siw.export_icepak_project(export_icepak, "DC IR Sim 3")
        assert siw.quit_application()

    def test_configuration(self, edb_examples):
        edbapp = edb_examples.get_si_verse(edbapp=False)
        data = {
            "ports": [
                {
                    "name": "CIRCUIT_X1_B8_GND",
                    "reference_designator": "X1",
                    "type": "circuit",
                    "positive_terminal": {"pin": "B8"},
                    "negative_terminal": {"net": "GND"},
                }
            ],
            "operations": {
                "cutout": {
                    "custom_extent": [
                        [77, 54],
                        [5, 54],
                        [5, 20],
                        [77, 20],
                    ],
                    "custom_extent_units": "mm",
                }
            },
        }

        cfg_json = os.path.join(edb_examples.test_folder, "cfg.json")
        with open(cfg_json, "w") as f:
            json.dump(data, f)

        siw = Siwave(desktop_version)
        siw.import_edb(edbapp)
        siw.load_configuration(cfg_json)
        cfg_json_2 = os.path.join(edb_examples.test_folder, "cfg2.json")
        siw.export_configuration(cfg_json_2)
        siw.quit_application()
        with open(cfg_json_2, "r") as f:
            json_data = json.load(f)
        assert json_data["ports"][0]["name"] == "CIRCUIT_X1_B8_GND"

        siw = Siwave(desktop_version)
        siw.import_edb(edbapp)
        siw.load_configuration(cfg_json_2)
        siw.quit_application()
