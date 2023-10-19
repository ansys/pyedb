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

    def test_components_get_pin_from_component(self):
        """Evaluate access to a pin from a component."""
        comp = self.edbapp.components.get_component_by_name("J1")
        assert comp is not None
        pin = self.edbapp.components.get_pin_from_component("J1", pinName="1")
        assert pin is not False

    def test_components_create_coax_port_on_component(self):
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

    def test_components_properties(self):
        """Access components properties."""
        assert len(self.edbapp.components.components) > 2
        assert len(self.edbapp.components.inductors) > 0
        assert len(self.edbapp.components.resistors) > 0
        assert len(self.edbapp.components.capacitors) > 0
        assert len(self.edbapp.components.ICs) > 0
        assert len(self.edbapp.components.IOs) > 0
        assert len(self.edbapp.components.Others) > 0

    def test_components_rlc_components_values(self):
        """Update values of an RLC component."""
        assert self.edbapp.components.set_component_rlc("C1", res_value=1e-3, cap_value="10e-6", isparallel=False)
        assert self.edbapp.components.set_component_rlc("L10", res_value=1e-3, ind_value="10e-6", isparallel=True)

    def test_components_R1_queries(self):
        """Evaluate queries over component R1."""
        assert "R1" in list(self.edbapp.components.components.keys())
        assert not self.edbapp.components.components["R1"].is_null
        assert self.edbapp.components.components["R1"].res_value
        assert self.edbapp.components.components["R1"].placement_layer
        assert isinstance(self.edbapp.components.components["R1"].lower_elevation, float)
        assert isinstance(self.edbapp.components.components["R1"].upper_elevation, float)
        assert self.edbapp.components.components["R1"].top_bottom_association == 2
        assert self.edbapp.components.components["R1"].pinlist
        assert self.edbapp.components.components["R1"].pins
        assert self.edbapp.components.components["R1"].pins["1"].pin_number
        assert self.edbapp.components.components["R1"].pins["1"].component
        assert (
            self.edbapp.components.components["R1"].pins["1"].lower_elevation
            == self.edbapp.components.components["R1"].lower_elevation
        )
        assert (
            self.edbapp.components.components["R1"].pins["1"].placement_layer
            == self.edbapp.components.components["R1"].placement_layer
        )
        assert (
            self.edbapp.components.components["R1"].pins["1"].upper_elevation
            == self.edbapp.components.components["R1"].upper_elevation
        )
        assert (
            self.edbapp.components.components["R1"].pins["1"].top_bottom_association
            == self.edbapp.components.components["R1"].top_bottom_association
        )
        assert self.edbapp.components.components["R1"].pins["1"].position
        assert self.edbapp.components.components["R1"].pins["1"].rotation

    def test_components_create_clearance_on_component(self):
        """Evaluate the creation of a clearance on soldermask."""
        comp = self.edbapp.components.components["U1"]
        assert comp.create_clearance_on_component()

    def test_components_get_components_from_nets(self):
        """Access to components from nets."""
        assert self.edbapp.components.get_components_from_nets("DDR4_DQS0_P")

    def test_components_resistors(self):
        """Evaluate the components resistors."""
        assert "R1" in list(self.edbapp.components.resistors.keys())
        assert "C1" not in list(self.edbapp.components.resistors.keys())

    def test_components_capacitors(self):
        """Evaluate the components capacitors."""
        assert "C1" in list(self.edbapp.components.capacitors.keys())
        assert "R1" not in list(self.edbapp.components.capacitors.keys())

    def test_components_inductors(self):
        """Evaluate the components inductors."""
        assert "L10" in list(self.edbapp.components.inductors.keys())
        assert "R1" not in list(self.edbapp.components.inductors.keys())

    def test_components_integrated_circuits(self):
        """Evaluate the components integrated circuits."""
        assert "U1" in list(self.edbapp.components.ICs.keys())
        assert "R1" not in list(self.edbapp.components.ICs.keys())

    def test_components_inputs_outputs(self):
        """Evaluate the components inputs and outputs."""
        assert "X1" in list(self.edbapp.components.IOs.keys())
        assert "R1" not in list(self.edbapp.components.IOs.keys())

    def test_components_others(self):
        """Evaluate the components other core components."""
        assert "B1" in self.edbapp.components.Others
        assert "R1" not in self.edbapp.components.Others

    def test_components_components_by_partname(self):
        """Evaluate the components by partname"""
        comp = self.edbapp.components.components_by_partname
        assert "ALTR-FBGA24_A-130" in comp
        assert len(comp["ALTR-FBGA24_A-130"]) == 1

    def test_components_get_through_resistor_list(self):
        """Evaluate the components retrieve through resistors."""
        assert self.edbapp.components.get_through_resistor_list(10)

    def test_components_get_rats(self):
        """Retrieve a list of dictionaries of the reference designator, pin names, and net names."""
        assert len(self.edbapp.components.get_rats()) > 0

    def test_components_get_component_net_connections_info(self):
        """Evaluate net connection information."""
        assert len(self.edbapp.components.get_component_net_connection_info("U1")) > 0

    def test_components_get_pin_name_and_position(self):
        """Retrieve components name and position."""
        cmp_pinlist = self.edbapp.padstacks.get_pinlist_from_component_and_net("U6", "GND")
        pin_name = self.edbapp.components.get_aedt_pin_name(cmp_pinlist[0])
        assert type(pin_name) is str
        assert len(pin_name) > 0
        assert len(cmp_pinlist[0].position) == 2
        assert len(self.edbapp.components.get_pin_position(cmp_pinlist[0])) == 2

    def test_components_get_pins_name_from_net(self):
        """Retrieve pins belonging to a net."""
        cmp_pinlist = self.edbapp.components.get_pin_from_component("U6")
        assert len(self.edbapp.components.get_pins_name_from_net(cmp_pinlist, "GND")) > 0
        assert len(self.edbapp.components.get_pins_name_from_net(cmp_pinlist, "5V")) == 0

    def test_components_delete_single_pin_rlc(self):
        """Delete all RLC components with a single pin."""
        assert len(self.edbapp.components.delete_single_pin_rlc()) == 0

    def test_components_set_component_rlc(self):
        """Update values for an RLC component."""
        assert self.edbapp.components.set_component_rlc("R1", 30, 1e-9, 1e-12)

    def test_components_disable_rlc_component(self):
        """Disable a RLC component."""
        assert self.edbapp.components.disable_rlc_component("R1")

    def test_components_delete(self):
        """Delete a component"""
        assert self.edbapp.components.delete("R1")
