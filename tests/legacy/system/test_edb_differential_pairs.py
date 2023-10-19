"""Tests related to Edb differential pairs
"""

import pytest

pytestmark = pytest.mark.system

class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, edbapp, local_scratch, target_path, target_path2, target_path4):
        self.edbapp = edbapp
        self.local_scratch = local_scratch
        self.target_path = target_path
        self.target_path2 = target_path2
        self.target_path4 = target_path4

    def test_differential_pairs_queries(self):
        """Evaluate differential pairs queries"""
        self.edbapp.differential_pairs.auto_identify()
        diff_pair = self.edbapp.differential_pairs.create("new_pair1", "PCIe_Gen4_RX1_P", "PCIe_Gen4_RX1_N")
        assert diff_pair.positive_net.name == "PCIe_Gen4_RX1_P"
        assert diff_pair.negative_net.name == "PCIe_Gen4_RX1_N"
        assert self.edbapp.differential_pairs.items
