"""Tests related to Edb padstacks
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
        """Access to pad parameters."""
        pin = self.edbapp.components.get_pin_from_component("J1", pinName="1")
        parameters = self.edbapp.padstacks.get_pad_parameters(
            pin[0], "1_Top", self.edbapp.padstacks.pad_type.RegularPad
        )
        assert isinstance(parameters[1], list)
        assert isinstance(parameters[0], int)

    def test_get_vias_from_nets(self):
        """Use padstacks' get_via_instance_from_net method."""
        assert self.edbapp.padstacks.get_via_instance_from_net("GND")
        assert not self.edbapp.padstacks.get_via_instance_from_net(["GND2"])

    def test_create_with_packstack_name(self):
        """Create a padstack"""
        # Create myVia
        self.edbapp.padstacks.create(padstackname="myVia")
        assert "myVia" in list(self.edbapp.padstacks.definitions.keys())
        self.edbapp.padstacks.definitions["myVia"].hole_range = "begin_on_upper_pad"
        assert self.edbapp.padstacks.definitions["myVia"].hole_range == "begin_on_upper_pad"
        self.edbapp.padstacks.definitions["myVia"].hole_range = "through"
        assert self.edbapp.padstacks.definitions["myVia"].hole_range == "through"
        # Create myVia_vullet
        self.edbapp.padstacks.create(padstackname="myVia_bullet", antipad_shape="Bullet")
        assert "myVia_bullet" in list(self.edbapp.padstacks.definitions.keys())
    
        self.edbapp.add_design_variable("via_x", 5e-3)
        self.edbapp["via_y"] = "1mm"
        assert self.edbapp["via_y"].value == 1e-3
        assert self.edbapp["via_y"].value_string == "1mm"
        assert self.edbapp.padstacks.place(["via_x", "via_x+via_y"], "myVia", via_name="via_test1")
        assert self.edbapp.padstacks.place(["via_x", "via_x+via_y*2"], "myVia_bullet")
        self.edbapp.padstacks["via_test1"].net_name = "GND"
        assert self.edbapp.padstacks["via_test1"].net_name == "GND"
        padstack = self.edbapp.padstacks.place(["via_x", "via_x+via_y*3"], "myVia", is_pin=True)
        for test_prop in (self.edbapp.padstacks.padstack_instances, self.edbapp.padstacks.instances):
            padstack_instance = test_prop[padstack.id]
            assert padstack_instance.is_pin
            assert padstack_instance.position
            assert padstack_instance.start_layer in padstack_instance.layer_range_names
            assert padstack_instance.stop_layer in padstack_instance.layer_range_names
            padstack_instance.position = [0.001, 0.002]
            assert padstack_instance.position == [0.001, 0.002]
            assert padstack_instance.parametrize_position()
            assert isinstance(padstack_instance.rotation, float)
            self.edbapp.padstacks.create_circular_padstack(padstackname="mycircularvia")
            assert "mycircularvia" in list(self.edbapp.padstacks.definitions.keys())
            assert not padstack_instance.backdrill_top
            assert not padstack_instance.backdrill_bottom
            assert padstack_instance.delete()
            via = self.edbapp.padstacks.place([0, 0], "myVia")
            assert via.set_backdrill_top("Inner4(Sig2)", 0.5e-3)
            assert via.backdrill_top
            assert via.set_backdrill_bottom("16_Bottom", 0.5e-3)
            assert via.backdrill_bottom
