"""Tests related to Edb net classes
"""

import pytest

pytestmark = [pytest.mark.system, pytest.mark.legacy]


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, legacy_edb_app, local_scratch, target_path, target_path2, target_path4):
        self.edbapp = legacy_edb_app
        self.local_scratch = local_scratch
        self.target_path = target_path
        self.target_path2 = target_path2
        self.target_path4 = target_path4

    def test_net_classes_queries(self):
        """Evaluate net classes queries"""
        assert self.edbapp.net_classes.items
        assert self.edbapp.net_classes.create("DDR4_ADD", ["DDR4_A0", "DDR4_A1"])
        assert self.edbapp.net_classes["DDR4_ADD"].name == "DDR4_ADD"
        assert self.edbapp.net_classes["DDR4_ADD"].sub_elments
        self.edbapp.net_classes["DDR4_ADD"].name = "DDR4_ADD_RENAMED"
        assert not self.edbapp.net_classes["DDR4_ADD_RENAMED"].is_null
