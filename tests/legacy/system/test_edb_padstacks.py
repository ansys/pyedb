"""Tests related to Edb
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

    def test_get_pad_parameters(self):
        """Test EDB access to pad parameters."""
        pin = self.edbapp.components.get_pin_from_component("J1", pinName="1")
        parameters = self.edbapp.padstacks.get_pad_parameters(
            pin[0], "1_Top", self.edbapp.padstacks.pad_type.RegularPad
        )
        assert isinstance(parameters[1], list)
        assert isinstance(parameters[0], int)

    def test_get_vias_from_nets(self):
        assert self.edbapp.padstacks.get_via_instance_from_net("GND")
        assert not self.edbapp.padstacks.get_via_instance_from_net(["GND2"])
