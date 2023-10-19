"""Tests related to Edb components
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

    def test_get_from_component(self):
        """Test EDB access to component data from a component."""
        comp = self.edbapp.components.get_component_by_name("J1")
        assert comp is not None
        pin = self.edbapp.components.get_pin_from_component("J1", pinName="1")
        assert pin is not False

    def test_create_coax_port_on_component(self):
        """Create a coaxial port on a component from its pin."""
        coax_port = self.edbapp.components["U6"].pins["R3"].create_coax_port("coax_port")
        coax_port.radial_extent_factor = 3
        assert coax_port.radial_extent_factor == 3
        assert coax_port.component
        assert self.edbapp.components["U6"].pins["R3"].terminal
        assert self.edbapp.components["U6"].pins["R3"].id
        assert self.edbapp.terminals
        assert self.edbapp.ports
        assert self.edbapp.components["U6"].pins["R3"].get_connected_objects()

    def test_component_properties(self):
        """Access components properties"""
        assert len(self.edbapp.components.components) > 2
        assert len(self.edbapp.components.inductors) > 0
        assert len(self.edbapp.components.resistors) > 0
        assert len(self.edbapp.components.capacitors) > 0
        assert len(self.edbapp.components.ICs) > 0
        assert len(self.edbapp.components.IOs) > 0
        assert len(self.edbapp.components.Others) > 0

