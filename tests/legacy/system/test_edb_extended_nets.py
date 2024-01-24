"""Tests related to Edb extended nets
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

    def test_nets_queries(self):
        """Evaluate nets queries"""
        assert self.edbapp.extended_nets.auto_identify_signal()
        assert self.edbapp.extended_nets.auto_identify_power()
        extended_net_name, _ = next(iter(self.edbapp.extended_nets.items.items()))
        assert self.edbapp.extended_nets[extended_net_name]
        assert self.edbapp.extended_nets[extended_net_name].sub_elments
        assert self.edbapp.extended_nets[extended_net_name].components
        assert self.edbapp.extended_nets[extended_net_name].rlc
        assert self.edbapp.extended_nets[extended_net_name].serial_rlc
        assert self.edbapp.extended_nets.create("new_ex_net", "DDR4_A1")
