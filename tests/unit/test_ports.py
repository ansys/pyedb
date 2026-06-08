# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Unit tests for source_excitations.py – no EDB license required."""

from unittest.mock import MagicMock, patch

import pytest

from pyedb.grpc.database.source_excitations import SourceExcitation, SourceExcitationInternal

pytestmark = [pytest.mark.unit, pytest.mark.no_licence, pytest.mark.grpc]


# ---------------------------------------------------------------------------
# SourceExcitationInternal – static / pure-logic methods
# ---------------------------------------------------------------------------


class TestNormalizeNetList:
    """Tests for SourceExcitationInternal._normalize_net_list."""

    def test_single_string_net(self):
        result = SourceExcitationInternal._normalize_net_list("GND")
        assert result == {"GND"}

    def test_list_of_strings(self):
        result = SourceExcitationInternal._normalize_net_list(["GND", "VCC"])
        assert result == {"GND", "VCC"}

    def test_empty_string_ignored(self):
        result = SourceExcitationInternal._normalize_net_list(["GND", "", "VCC"])
        assert "" not in result
        assert result == {"GND", "VCC"}

    def test_net_object_with_name(self):
        from pyedb.grpc.database.net.net import Net

        class FakeNet(Net):
            def __init__(self, name):
                self._name = name

            @property
            def name(self):
                return self._name

        net = FakeNet("SIGP")
        result = SourceExcitationInternal._normalize_net_list(net)
        assert "SIGP" in result

    def test_net_object_with_empty_name(self):
        from pyedb.grpc.database.net.net import Net

        class FakeNet(Net):
            def __init__(self, name):
                self._name = name

            @property
            def name(self):
                return self._name

        net = FakeNet("")
        result = SourceExcitationInternal._normalize_net_list(net)
        assert result == set()

    def test_mixed_strings_and_net_objects(self):
        from pyedb.grpc.database.net.net import Net

        class FakeNet(Net):
            def __init__(self, name):
                self._name = name

            @property
            def name(self):
                return self._name

        net = FakeNet("SIGP")
        result = SourceExcitationInternal._normalize_net_list(["GND", net])
        assert result == {"GND", "SIGP"}

    def test_duplicate_nets_deduplicated(self):
        result = SourceExcitationInternal._normalize_net_list(["GND", "GND"])
        assert result == {"GND"}


class TestIsNegativeNet:
    """Tests for SourceExcitationInternal._is_negative_net."""

    @pytest.mark.parametrize(
        "net_name",
        [
            "DIFF_n",
            "DIFF_neg",
            "DIFF_negative",
            "DIFF_N",
            "DIFF_NEG",
            "DIFF_NEGATIVE",
            "CLK:n",
            "CLK:neg",
            "CLK:negative",
        ],
    )
    def test_negative_net_patterns(self, net_name):
        assert SourceExcitationInternal._is_negative_net(net_name) is True

    @pytest.mark.parametrize(
        "net_name",
        [
            "DIFF_p",
            "DIFF_pos",
            "GND",
            "VCC",
            "CLK_neg_extra",  # pattern in middle, not end
            "signal_n_something",  # pattern in middle
        ],
    )
    def test_non_negative_net_patterns(self, net_name):
        assert SourceExcitationInternal._is_negative_net(net_name) is False

    def test_empty_string_returns_false(self):
        assert SourceExcitationInternal._is_negative_net("") is False

    def test_none_returns_false(self):
        assert SourceExcitationInternal._is_negative_net(None) is False

    def test_non_string_returns_false(self):
        assert SourceExcitationInternal._is_negative_net(42) is False


# ---------------------------------------------------------------------------
# SourceExcitation – instance logic methods mocked
# ---------------------------------------------------------------------------


def _make_excitation():
    """Build a SourceExcitation with a mocked _pedb."""
    pedb = MagicMock()
    exc = SourceExcitation.__new__(SourceExcitation)
    exc._pedb = pedb
    return exc, pedb


class TestGetUniquTerminalName:
    def test_name_not_existing_returned_as_is(self):
        exc, pedb = _make_excitation()
        pedb.terminals = {"existing": MagicMock()}
        result = exc._get_unique_terminal_name("new_terminal")
        assert result == "new_terminal"

    def test_name_conflict_gets_suffix(self):
        exc, pedb = _make_excitation()
        pedb.terminals = {"t1": MagicMock(), "t1_1": MagicMock()}
        result = exc._get_unique_terminal_name("t1")
        assert result == "t1_2"

    def test_first_conflict_resolved(self):
        exc, pedb = _make_excitation()
        pedb.terminals = {"t1": MagicMock()}
        result = exc._get_unique_terminal_name("t1")
        assert result == "t1_1"


class TestPortExist:
    def test_port_exists(self):
        exc, pedb = _make_excitation()
        pedb.ports = {"Port1": MagicMock(), "Port2": MagicMock()}
        assert exc._port_exist("Port1") is True

    def test_port_not_exists(self):
        exc, pedb = _make_excitation()
        pedb.ports = {"Port1": MagicMock()}
        assert exc._port_exist("Port2") is False

    def test_empty_ports(self):
        exc, pedb = _make_excitation()
        pedb.ports = {}
        assert exc._port_exist("Port1") is False


class TestCheckGnd:
    def test_gnd_found(self):
        exc, pedb = _make_excitation()
        pedb.nets.is_net_in_component.side_effect = lambda comp, net: net == "GND"
        result = exc._check_gnd("U1")
        assert result == "GND"

    def test_pgnd_found_when_no_gnd(self):
        exc, pedb = _make_excitation()
        pedb.nets.is_net_in_component.side_effect = lambda comp, net: net == "PGND"
        result = exc._check_gnd("U1")
        assert result == "PGND"

    def test_agnd_found(self):
        exc, pedb = _make_excitation()
        pedb.nets.is_net_in_component.side_effect = lambda comp, net: net == "AGND"
        result = exc._check_gnd("U1")
        assert result == "AGND"

    def test_dgnd_found(self):
        exc, pedb = _make_excitation()
        pedb.nets.is_net_in_component.side_effect = lambda comp, net: net == "DGND"
        result = exc._check_gnd("U1")
        assert result == "DGND"

    def test_no_gnd_raises_value_error(self):
        exc, pedb = _make_excitation()
        pedb.nets.is_net_in_component.return_value = False
        with pytest.raises(ValueError, match="No GND"):
            exc._check_gnd("U1")


class TestPropertiesPassThrough:
    """Verify that ports / sources / probes / excitations delegate to _pedb."""

    def test_ports_delegates_to_pedb(self):
        exc, pedb = _make_excitation()
        pedb.ports = {"p1": MagicMock()}
        assert exc.ports is pedb.ports

    def test_sources_delegates_to_pedb(self):
        exc, pedb = _make_excitation()
        pedb.sources = {"s1": MagicMock()}
        assert exc.sources is pedb.sources

    def test_probes_delegates_to_pedb(self):
        exc, pedb = _make_excitation()
        pedb.probes = {"pr1": MagicMock()}
        assert exc.probes is pedb.probes

    def test_excitations_deprecated_returns_ports(self):
        exc, pedb = _make_excitation()
        pedb.ports = {"p1": MagicMock()}
        # Accessing the deprecated property should still work and return ports
        with pytest.warns(FutureWarning):
            result = exc.excitations
        assert result is pedb.ports

    def test_pin_groups_returns_dict(self):
        exc, pedb = _make_excitation()
        pg1 = MagicMock()
        pg1.name = "pg1"
        pedb.layout.pin_groups = [pg1]
        result = exc.pin_groups
        assert "pg1" in result
        assert result["pg1"] is pg1


class TestGetPinsForPorts:
    """Tests for _get_pins_for_ports."""

    def test_padstack_instance_passthrough(self):
        from pyedb.grpc.database.primitive.padstack_instance import PadstackInstance

        exc, pedb = _make_excitation()
        pin = MagicMock(spec=PadstackInstance)
        result = exc._get_pins_for_ports([pin], None)
        assert result == [pin]

    def test_string_pin_resolved_from_component(self):
        exc, pedb = _make_excitation()
        comp = MagicMock()
        pin = MagicMock()
        comp.pins = {"Pin1": pin}
        result = exc._get_pins_for_ports(["Pin1"], comp)
        assert result == [pin]

    def test_string_pin_not_in_component_searched_globally(self):
        exc, pedb = _make_excitation()
        comp = MagicMock()
        comp.pins = {}
        # Global padstack instance with matching name
        psi = MagicMock()
        psi.name = "GlobalPin"
        psi.aedt_name = "GlobalPin"
        pedb.padstacks.instances = {1: psi}
        result = exc._get_pins_for_ports(["GlobalPin"], comp)
        assert result == [psi]

    def test_int_id_resolved_from_padstacks(self):
        exc, pedb = _make_excitation()
        psi = MagicMock()
        pedb.padstacks.instances = {42: psi}
        result = exc._get_pins_for_ports([42], None)
        assert result == [psi]

    def test_unknown_int_id_returns_empty(self):
        exc, pedb = _make_excitation()
        pedb.padstacks.instances = {}
        result = exc._get_pins_for_ports([99], None)
        assert result == []


class TestCheckBeforeTerminalAssignment:
    def test_no_connectable_returns_false(self):
        exc, pedb = _make_excitation()
        assert exc.check_before_terminal_assignement(None) is False

    def test_no_existing_terminal_returns_true(self):
        exc, pedb = _make_excitation()
        connectable = MagicMock()
        connectable.id = 1
        term = MagicMock()
        term.id = 2  # different id
        pedb.active_layout.terminals = [term]
        result = exc.check_before_terminal_assignement(connectable)
        assert result is True

    def test_existing_terminal_delete_false_returns_false(self):
        exc, pedb = _make_excitation()
        connectable = MagicMock()
        connectable.id = 1
        term = MagicMock()
        term.id = 1  # same id – existing terminal
        pedb.active_layout.terminals = [term]
        result = exc.check_before_terminal_assignement(connectable, delete_existing_terminal=False)
        assert result is False


class TestCreatePortReturnsFalseOnNoSources:
    def test_create_source_on_component_returns_false_for_empty(self):
        exc, pedb = _make_excitation()
        result = exc.create_source_on_component(None)
        assert result is False

    def test_add_port_on_rlc_component_returns_false_for_non_component(self):
        exc, pedb = _make_excitation()
        # passing a plain string that the mock will NOT resolve to a Component instance
        pedb.components.instances = {}
        # Component class comparison fails; returns False
        result = exc.add_port_on_rlc_component(None)
        assert result is False


class TestGetPortsNumber:
    def test_counts_non_reference_terminals(self):
        exc, pedb = _make_excitation()
        t1 = MagicMock()
        t1.is_reference_terminal = False
        t2 = MagicMock()
        t2.is_reference_terminal = True
        t3 = MagicMock()
        t3.is_reference_terminal = False
        pedb.layout.terminals = [t1, t2, t3]
        assert exc.get_ports_number() == 2

    def test_no_terminals(self):
        exc, pedb = _make_excitation()
        pedb.layout.terminals = []
        assert exc.get_ports_number() == 0


class TestCreatePortOnComponentValidation:
    def test_integer_port_type_coax(self):
        """Integer 0 should map to coax_port type."""
        exc, pedb = _make_excitation()
        comp = MagicMock()
        comp.name = "U1"
        comp.pins = {}
        pedb.components.instances = {"U1": comp}
        # No pins => returns False after logging
        result = exc.create_port_on_component("U1", ["NET1"], port_type=0, reference_net="GND")
        assert result is False

    def test_integer_port_type_circuit(self):
        """Integer 1 should map to circuit_port type."""
        exc, pedb = _make_excitation()
        comp = MagicMock()
        comp.name = "U1"
        comp.pins = {}
        pedb.components.instances = {"U1": comp}
        result = exc.create_port_on_component("U1", ["NET1"], port_type=1, reference_net="GND")
        assert result is False

    def test_unsupported_integer_port_type(self):
        """Unsupported integer port type returns False."""
        exc, pedb = _make_excitation()
        comp = MagicMock()
        comp.name = "U1"
        comp.pins = {}
        pedb.components.instances = {"U1": comp}
        result = exc.create_port_on_component("U1", ["NET1"], port_type=99, reference_net="GND")
        assert result is False


class TestCreatePortOnPinsValidation:
    def test_no_pins_raises_runtime_warning(self):
        exc, pedb = _make_excitation()
        comp = MagicMock()
        pedb.components.instances = {"U1": comp}
        comp.rlc_values = [None, None, None]
        with patch.object(exc, "_get_pins_for_ports", return_value=[]):
            with pytest.raises(RuntimeWarning, match="No pins found"):
                exc.create_port_on_pins("U1", "Pin1", "GND")

    def test_no_ref_pins_raises_runtime_warning(self):
        exc, pedb = _make_excitation()
        comp = MagicMock()
        pedb.components.instances = {"U1": comp}
        comp.rlc_values = [None, None, None]
        pin = MagicMock()
        with patch.object(exc, "_get_pins_for_ports", side_effect=[[pin], []]):
            with pytest.raises(RuntimeWarning, match="No reference pins found"):
                exc.create_port_on_pins("U1", "Pin1", "GND")


class TestCreateTerminalOnPinsInvalidSourceType:
    def test_invalid_source_type_returns_false(self):
        exc, pedb = _make_excitation()

        pos_pin = MagicMock()
        neg_pin = MagicMock()
        layer = MagicMock()
        pos_pin.get_layer_range.return_value = (layer, layer)
        neg_pin.get_layer_range.return_value = (layer, layer)
        pos_pin.name = "Pin1"
        neg_pin.name = "Pin2"

        # Patch PadstackInstanceTerminal.create to return mock terminals
        mock_pos_term = MagicMock()
        mock_pos_term.name = "Pin1"
        mock_neg_term = MagicMock()
        mock_neg_term.name = "Pin2"

        with patch("pyedb.grpc.database.source_excitations.PadstackInstanceTerminal") as mock_pit:
            mock_pit.create.side_effect = [mock_pos_term, mock_neg_term]
            pedb.terminals = {}
            pedb.active_layout = MagicMock()
            pedb._value_setter = MagicMock(return_value=50)
            result = exc._create_terminal_on_pins(pos_pin, neg_pin, source_type="invalid_type")
        assert result is False


class TestNormalizeNetListEdgeCases:
    def test_single_net_object_non_empty(self):
        from pyedb.grpc.database.net.net import Net

        class FakeNet(Net):
            def __init__(self, name):
                self._name = name

            @property
            def name(self):
                return self._name

        net = FakeNet("DDR4_DQ0")
        result = SourceExcitationInternal._normalize_net_list([net])
        assert "DDR4_DQ0" in result

    def test_non_string_non_net_ignored(self):
        result = SourceExcitationInternal._normalize_net_list([123, None, "GND"])
        assert result == {"GND"}


def _make_excitation_for_edge_port():
    """Build a SourceExcitation with the _create_edge_terminal and stackup mocked."""
    exc, pedb = _make_excitation()

    # Mock the edge terminal returned by _create_edge_terminal
    mock_term = MagicMock()
    mock_term.is_null = False
    mock_term.name = "P1"
    exc._create_edge_terminal = MagicMock(return_value=mock_term)

    # Mock _value_setter so impedance assignment doesn't crash
    pedb._value_setter = MagicMock(return_value=50)

    # Mock set_product_solver_option on the terminal
    mock_term.set_product_solver_option = MagicMock()

    return exc, pedb, mock_term


@pytest.mark.grpc
class TestCreateEdgePortVerticalReferenceLayer:
    """Regression tests – create_edge_port_vertical must not raise when reference_layer is specified."""

    def test_no_reference_layer_succeeds(self):
        """Without reference_layer the method returns the port name without touching reference_layer."""
        exc, pedb, mock_term = _make_excitation_for_edge_port()
        # signal_layers not consulted when reference_layer is None
        result = exc.create_edge_port_vertical(
            prim_id=1,
            point_on_edge=[0.0, 0.5e-3],
            port_name="P1",
        )
        assert result == "P1"
        # stackup.signal_layers should not have been accessed at all
        pedb.stackup.signal_layers.__contains__.assert_not_called()

    def test_valid_reference_layer_sets_terminal_reference_layer(self):
        """With a valid reference_layer string the setter is called on the terminal."""
        exc, pedb, mock_term = _make_excitation_for_edge_port()

        # Simulate the layer existing in signal_layers
        mock_stackup_layer = MagicMock()
        pedb.stackup.signal_layers = {"L2_BOT": mock_stackup_layer}

        result = exc.create_edge_port_vertical(
            prim_id=1,
            point_on_edge=[0.0, 0.5e-3],
            port_name="P1",
            reference_layer="L2_BOT",
        )

        assert result == "P1"
        # Verify that reference_layer was assigned on the terminal mock
        assert mock_term.reference_layer == "L2_BOT"

    def test_invalid_reference_layer_returns_none_and_logs_error(self):
        """With a reference_layer that does not exist the method returns None and logs an error."""
        exc, pedb, mock_term = _make_excitation_for_edge_port()

        # Layer NOT present in signal_layers
        pedb.stackup.signal_layers = {}

        result = exc.create_edge_port_vertical(
            prim_id=1,
            point_on_edge=[0.0, 0.5e-3],
            port_name="P1",
            reference_layer="NONEXISTENT",
        )

        assert result is None
        pedb.logger.error.assert_called_once()

    def test_reference_layer_not_assigned_when_layer_missing(self):
        """When reference_layer is invalid the method returns None (exits before assigning reference_layer)."""
        exc, pedb, mock_term = _make_excitation_for_edge_port()
        pedb.stackup.signal_layers = {}

        result = exc.create_edge_port_vertical(
            prim_id=1,
            point_on_edge=[0.0, 0.5e-3],
            port_name="P1",
            reference_layer="BAD_LAYER",
        )

        # Early exit means None is returned; the terminal name is never reached
        assert result is None
