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

        self.edbapp.definitions.component["CAPC3216X180X55ML20T25"].add_n_port_model(
            sparam_path, "GRM32_DC0V_25degC_series"
        )
        self.edbapp.components["C200"].use_s_parameter_model("GRM32_DC0V_25degC_series")

    def test_add_package_def(self):
        package = self.edbapp.definitions.add_package_def("package_1")
        assert package
        package.maximum_power = 1
        assert self.edbapp.definitions.package["package_1"].maximum_power == 1
        package.therm_cond = 1
        assert self.edbapp.definitions.package["package_1"].therm_cond == 1
        package.theta_jb = 1
        assert self.edbapp.definitions.package["package_1"].theta_jb == 1
        package.theta_jc = 1
        assert self.edbapp.definitions.package["package_1"].theta_jc == 1
        package.height = 1
        assert self.edbapp.definitions.package["package_1"].height == 1

        package.name = "package_1b"
        assert self.edbapp.definitions.package["package_1b"]
