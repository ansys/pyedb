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

"""Tests related to Edb component definitions
"""
import os

import pytest

from tests.conftest import local_path
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

    def test_definitions(self):
        assert isinstance(self.edbapp.definitions.component, dict)
        assert isinstance(self.edbapp.definitions.package, dict)

    def test_component_s_parameter(self):
        sparam_path = os.path.join(local_path, "example_models", test_subfolder, "GRM32_DC0V_25degC_series.s2p")

        self.edbapp.definitions.component["CAPC3216X180X55ML20T25"].add_n_port_model(sparam_path, "GRM32_DC0V_25degC_series")
        self.edbapp.components["C200"].use_s_parameter_model("GRM32_DC0V_25degC_series")

    def test_add_package_def(self):
        package = self.edbapp.definitions.add_package_def("package_1")
        assert package
        package.maximum_power = 1
        assert self.edbapp.definitions.package['package_1'].maximum_power == 1
        package.therm_cond = 1
        assert self.edbapp.definitions.package['package_1'].therm_cond == 1
        package.theta_jb = 1
        assert self.edbapp.definitions.package['package_1'].theta_jb == 1
        package.theta_jc = 1
        assert self.edbapp.definitions.package['package_1'].theta_jc == 1
        package.height = 1
        assert self.edbapp.definitions.package['package_1'].height == 1

        package.name = "package_1b"
        assert self.edbapp.definitions.package['package_1b']
