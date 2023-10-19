"""Tests related to Edb nets
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

    def test_nets_queries(self):
        """Evaluate nets queries"""
        assert len(self.edbapp.nets.netlist) > 0
        signalnets = self.edbapp.nets.signal
        assert not signalnets[list(signalnets.keys())[0]].is_power_ground
        assert not signalnets[list(signalnets.keys())[0]].IsPowerGround()
        assert len(list(signalnets[list(signalnets.keys())[0]].primitives)) > 0
        assert len(signalnets) > 2

        powernets = self.edbapp.nets.power
        assert len(powernets) > 2
        assert powernets["AVCC_1V3"].is_power_ground
        powernets["AVCC_1V3"].is_power_ground = False
        assert not powernets["AVCC_1V3"].is_power_ground
        powernets["AVCC_1V3"].is_power_ground = True
        assert powernets["AVCC_1V3"].name == "AVCC_1V3"
        assert powernets["AVCC_1V3"].IsPowerGround()
        assert len(list(powernets["AVCC_1V3"].components.keys())) > 0
        assert len(powernets["AVCC_1V3"].primitives) > 0

        assert self.edbapp.nets.find_or_create_net("GND")
        assert self.edbapp.nets.find_or_create_net(start_with="gn")
        assert self.edbapp.nets.find_or_create_net(start_with="g", end_with="d")
        assert self.edbapp.nets.find_or_create_net(end_with="d")
        assert self.edbapp.nets.find_or_create_net(contain="usb")
        assert self.edbapp.nets["AVCC_1V3"].extended_net

        self.edbapp.differential_pairs.auto_identify()
        diff_pair = self.edbapp.differential_pairs.create("new_pair1", "PCIe_Gen4_RX1_P", "PCIe_Gen4_RX1_N")
        assert diff_pair.positive_net.name == "PCIe_Gen4_RX1_P"
        assert diff_pair.negative_net.name == "PCIe_Gen4_RX1_N"
        assert self.edbapp.differential_pairs.items

        assert self.edbapp.net_classes.items
        assert self.edbapp.net_classes.create("DDR4_ADD", ["DDR4_A0", "DDR4_A1"])
        assert self.edbapp.net_classes["DDR4_ADD"].name == "DDR4_ADD"
        assert self.edbapp.net_classes["DDR4_ADD"].nets
        self.edbapp.net_classes["DDR4_ADD"].name = "DDR4_ADD_RENAMED"
        assert not self.edbapp.net_classes["DDR4_ADD_RENAMED"].is_null
