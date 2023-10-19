"""Tests related to Edb
"""

import pytest
from pyedb.generic.constants import SourceType

pytestmark = pytest.mark.system

class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, edbapp, local_scratch, target_path, target_path2, target_path4):
        self.edbapp = edbapp
        self.local_scratch = local_scratch
        self.target_path = target_path
        self.target_path2 = target_path2
        self.target_path4 = target_path4

    def test_hfss_create_coax_port_on_component_from_hfss(self):
        """Create a coaxial port on a component from its pin."""
        assert self.edbapp.hfss.create_coax_port_on_component("U1", "DDR4_DQS0_P")
        assert self.edbapp.hfss.create_coax_port_on_component("U1", ["DDR4_DQS0_P", "DDR4_DQS0_N"])

    def test_layout_bounding_box(self):
        """Evaluate layout bounding box"""
        assert len(self.edbapp.get_bounding_box()) == 2
        assert self.edbapp.get_bounding_box() == [[-0.01426004895, -0.00455000106], [0.15010507444, 0.08000000002]]

    def test_siwave_create_circuit_port_on_net(self):
        """Create a circuit port on a net."""
        initial_len = len(self.edbapp.padstacks.pingroups)
        assert self.edbapp.siwave.create_circuit_port_on_net("U1", "1V0", "U1", "GND", 50, "test") == "test"
        p2 = self.edbapp.siwave.create_circuit_port_on_net("U1", "PLL_1V8", "U1", "GND", 50, "test")
        assert p2 != "test" and "test" in p2
        pins = self.edbapp.components.get_pin_from_component("U1")
        p3 = self.edbapp.siwave.create_circuit_port_on_pin(pins[200], pins[0], 45)
        assert p3 != ""
        p4 = self.edbapp.hfss.create_circuit_port_on_net("U1", "USB3_D_P")
        assert len(self.edbapp.padstacks.pingroups) == initial_len + 6
        assert "GND" in p4 and "USB3_D_P" in p4

        # TODO: Moves this piece of code in another place
        assert "test" in self.edbapp.terminals
        assert self.edbapp.siwave.create_pin_group_on_net("U1", "1V0", "PG_V1P0_S0")
        assert self.edbapp.siwave.create_circuit_port_on_pin_group(
            "PG_V1P0_S0", "PinGroup_2", impedance=50, name="test_port"
        )
        self.edbapp.excitations["test_port"].name = "test_rename"
        assert any(port for port in list(self.edbapp.excitations) if port == "test_rename")

    def test_siwave_create_voltage_source(self):
        """Create a voltage source."""
        assert len(self.edbapp.sources) == 0
        assert "Vsource_" in self.edbapp.siwave.create_voltage_source_on_net("U1", "USB3_D_P", "U1", "GND", 3.3, 0)
        assert len(self.edbapp.sources) == 2
        assert list(self.edbapp.sources.values())[0].magnitude == 3.3

        pins = self.edbapp.components.get_pin_from_component("U1")
        assert "VSource_" in self.edbapp.siwave.create_voltage_source_on_pin(pins[300], pins[10], 3.3, 0)
        assert len(self.edbapp.sources) == 3
        assert len(self.edbapp.probes) == 0  
        
        list(self.edbapp.sources.values())[0].phase = 1
        assert list(self.edbapp.sources.values())[0].phase == 1

    def test_siwave_create_current_source(self):
        """Create a current source."""
        assert self.edbapp.siwave.create_current_source_on_net("U1", "USB3_D_N", "U1", "GND", 0.1, 0) != ""
        pins = self.edbapp.components.get_pin_from_component("U1")
        assert "I22" == self.edbapp.siwave.create_current_source_on_pin(pins[301], pins[10], 0.1, 0, "I22")

        assert self.edbapp.siwave.create_pin_group_on_net(reference_designator="U1", net_name="GND", group_name="gnd")
        self.edbapp.siwave.create_pin_group(reference_designator="U1", pin_numbers=["A27", "A28"], group_name="vrm_pos")
        self.edbapp.siwave.create_current_source_on_pin_group(
            pos_pin_group_name="vrm_pos", neg_pin_group_name="gnd", name="vrm_current_source"
        )

        self.edbapp.siwave.create_pin_group(
            reference_designator="U1", pin_numbers=["A14", "A15"], group_name="sink_pos"
        )

        # TODO: Moves this piece of code in another place
        assert self.edbapp.siwave.create_voltage_source_on_pin_group("sink_pos", "gnd", name="vrm_voltage_source")
        self.edbapp.siwave.create_pin_group(reference_designator="U1", pin_numbers=["A27", "A28"], group_name="vp_pos")
        self.edbapp.siwave.create_pin_group(reference_designator="U1", pin_numbers=["A14", "A15"], group_name="vp_neg")
        assert self.edbapp.siwave.create_voltage_probe_on_pin_group("vprobe", "vp_pos", "vp_neg")
        assert self.edbapp.probes["vprobe"]

    def test_siwave_create_dc_terminal(self):
        """Create a DC terminal."""
        assert self.edbapp.siwave.create_dc_terminal("U1", "DDR4_DQ40", "dc_terminal1") == "dc_terminal1"

    def test_siwave_create_resistors_on_pin(self):
        """Create a resistor on pin."""
        pins = self.edbapp.components.get_pin_from_component("U1")
        assert "RST4000" == self.edbapp.siwave.create_resistor_on_pin(pins[302], pins[10], 40, "RST4000")

    def test_siwave_add_syz_analsyis(self):
        """Add a sywave AC analysis."""
        assert self.edbapp.siwave.add_siwave_syz_analysis()

    def test_siwave_add_dc_analysis(self):
        """Add a sywave DC analysis."""
        setup = self.edbapp.siwave.add_siwave_dc_analysis()
        assert setup.add_source_terminal_to_ground(list(self.edbapp.sources.keys())[0], 2)

    def test_hfss_mesh_operations(self):
        """Retrieve the trace width for traces with ports."""
        self.edbapp.components.create_port_on_component(
            "U1",
            ["VDD_DDR"],
            reference_net="GND",
            port_type=SourceType.CircPort,
        )
        mesh_ops = self.edbapp.hfss.get_trace_width_for_traces_with_ports()
        assert len(mesh_ops) > 0
