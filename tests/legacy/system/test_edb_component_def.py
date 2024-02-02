"""Tests related to Edb component definitions
"""
import math
import os

import pytest

# from pyedb import Edb
from pyedb.dotnet.edb import Edb
from tests.conftest import desktop_version, local_path
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
        assert self.edbapp.definitions

    def test_s_parameter(self):
        sparam_path = os.path.join(local_path, "example_models", test_subfolder, "GRM32_DC0V_25degC_series.s2p")

        self.edbapp.definitions.components["CAPC3216X180X55ML20T25"].add_n_port_model(sparam_path, "GRM32_DC0V_25degC_series")
        self.edbapp.components["C200"].use_s_parameter_model("GRM32_DC0V_25degC_series")
