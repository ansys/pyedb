# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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

"""Tests related to Edb component definitions"""

import os

import pytest

from tests.conftest import local_path, test_subfolder
from tests.system.base_test_class import BaseTestClass

pytestmark = [pytest.mark.system, pytest.mark.legacy]


@pytest.mark.usefixtures("close_rpc_session")
class TestClass(BaseTestClass):
    @pytest.fixture(autouse=True)
    def init(self, local_scratch, target_path, target_path2, target_path4):
        self.local_scratch = local_scratch
        self.target_path = target_path
        self.target_path2 = target_path2
        self.target_path4 = target_path4

    def test_definitions(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        assert isinstance(edbapp.definitions.components, dict)
        assert isinstance(edbapp.definitions.packages, dict)
        edbapp.close(terminate_rpc_session=False)

    def test_component_s_parameter(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        sparam_path = os.path.join(local_path, "example_models", test_subfolder, "GRM32_DC0V_25degC_series.s2p")
        edbapp.definitions.components["CAPC3216X180X55ML20T25"].add_n_port_model(
            sparam_path, "GRM32_DC0V_25degC_series"
        )
        assert edbapp.definitions.components["CAPC3216X180X55ML20T25"].component_models
        cap_model = list(edbapp.definitions.components["CAPC3216X180X55ML20T25"].component_models.values())[0]
        assert not cap_model.is_null
        assert cap_model.reference_file
        assert edbapp.components["C200"].use_s_parameter_model("GRM32_DC0V_25degC_series")
        edbapp.close(terminate_rpc_session=False)

    def test_add_package_def(self, edb_examples):
        # Done
        edbapp = edb_examples.get_si_verse()
        package = edbapp.definitions.add_package("package_1", "SMTC-MECT-110-01-M-D-RA1_V")
        assert package
        package.maximum_power = 1
        assert edbapp.definitions.packages["package_1"].maximum_power == 1
        package.thermal_conductivity = 1
        assert edbapp.definitions.packages["package_1"].thermal_conductivity == 1
        package.theta_jb = 1
        assert edbapp.definitions.packages["package_1"].theta_jb == 1
        package.theta_jc = 1
        assert edbapp.definitions.packages["package_1"].theta_jc == 1
        package.height = 1
        assert edbapp.definitions.packages["package_1"].height == 1
        assert package.set_heatsink("1mm", "2mm", "x_oriented", "3mm", "4mm")
        assert package.heat_sink.fin_base_height == 0.001
        assert package.heat_sink.fin_height == 0.002
        assert package.heat_sink.fin_orientation == "x_oriented"
        assert package.heat_sink.fin_spacing == 0.003
        assert package.heat_sink.fin_thickness == 0.004
        package.name = "package_1b"
        assert edbapp.definitions.packages["package_1b"]

        assert edbapp.definitions.add_package("package_2", boundary_points=[["-1mm", "-1mm"], ["1mm", "1mm"]])
        edbapp.components["J5"].package_def = "package_2"
        assert edbapp.components["J5"].package_def.name == "package_2"
        edbapp.close(terminate_rpc_session=False)

    def test_wirebond_definitions(self, edb_examples):
        edbapp = edb_examples.get_wirebond_jedec4_project()
        assert list(edbapp.definitions.jedec4_bondwires.keys())[0] == "Default"
        assert list(edbapp.definitions.jedec5_bondwires.keys())[0] == "Default"
        jedec4_bw = list(edbapp.definitions.jedec4_bondwires.values())[0]
        jedec4_bw.height = 20e-6
        assert jedec4_bw.height == 20e-6
        edbapp.close(terminate_rpc_session=False)
