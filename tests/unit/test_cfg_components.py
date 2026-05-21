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

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.no_licence, pytest.mark.legacy]


from unittest.mock import MagicMock

import pytest

from pyedb.configuration.cfg_components import (
    CfgComponent,
    CfgComponents,
    CfgPinPairModel,
    _height_from_diameter,
    _smallest_pin_pad_size,
)


class TestHeightFromDiameter:
    def test_um(self):
        assert _height_from_diameter("150um") == "100um"

    def test_mm(self):
        result = _height_from_diameter("0.15mm")
        assert "mm" in result

    def test_no_unit_defaults_to_um(self):
        result = _height_from_diameter("150")
        assert "um" in result

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            _height_from_diameter("bad_value")


class TestSmallestPinPadSize:
    def _make_comp(self, pins):
        comp = MagicMock()
        comp.pins = {str(i): p for i, p in enumerate(pins)}
        return comp

    def _make_pin(self, bbox):
        p = MagicMock()
        p.bounding_box = bbox
        return p

    def test_single_valid_pin(self):
        pin = self._make_pin(((0, 0), (100e-6, 50e-6)))
        comp = self._make_comp([pin])
        assert _smallest_pin_pad_size(comp) == pytest.approx(50e-6)

    def test_no_bbox_skipped(self):
        pin = MagicMock(spec=[])  # no bounding_box attr
        comp = self._make_comp([pin])
        assert _smallest_pin_pad_size(comp) is None

    def test_empty_bbox_skipped(self):
        pin = self._make_pin(None)
        comp = self._make_comp([pin])
        assert _smallest_pin_pad_size(comp) is None

    def test_zero_size_skipped(self):
        pin = self._make_pin(((0, 0), (0, 0)))
        comp = self._make_comp([pin])
        assert _smallest_pin_pad_size(comp) is None

    def test_picks_smallest(self):
        p1 = self._make_pin(((0, 0), (200e-6, 200e-6)))
        p2 = self._make_pin(((0, 0), (50e-6, 50e-6)))
        comp = self._make_comp([p1, p2])
        assert _smallest_pin_pad_size(comp) == pytest.approx(50e-6)


class TestCfgPinPairModel:
    def test_minimal(self):
        m = CfgPinPairModel(first_pin="1", second_pin="2")
        assert m.first_pin == "1"
        assert m.resistance is None
        assert m.is_parallel is False

    def test_all_fields(self):
        m = CfgPinPairModel(
            first_pin="1",
            second_pin="2",
            resistance="100ohm",
            inductance="1nH",
            capacitance="10nF",
            is_parallel=True,
            resistance_enabled=True,
            inductance_enabled=True,
            capacitance_enabled=True,
        )
        d = m.model_dump()
        assert d["resistance"] == "100ohm"
        assert d["is_parallel"] is True
        assert d["capacitance_enabled"] is True


class TestComponentConfig:
    def test_minimal(self):
        c = CfgComponent("U1")
        d = c.to_dict()
        assert d == {"reference_designator": "U1"}

    def test_with_type_and_enabled(self):
        c = CfgComponent(_pedb="R1", part_type="resistor", enabled=False)
        d = c.to_dict()
        assert d["part_type"] == "resistor"
        assert d["enabled"] is False

    def test_enabled_true(self):
        c = CfgComponent("U1", part_type="ic", enabled=True)
        assert c.to_dict()["enabled"] is True

    def test_definition_and_placement_layer(self):
        c = CfgComponent("U1", definition="BGA_256", placement_layer="1_Top")
        d = c.to_dict()
        assert d["definition"] == "BGA_256"
        assert d["placement_layer"] == "1_Top"

    def test_pins(self):
        c = CfgComponent("U1", pins=["1", "2", "3"])
        assert c.to_dict()["pins"] == ["1", "2", "3"]

    def test_empty_pins_not_in_dict(self):
        c = CfgComponent("U1")
        assert "pins" not in c.to_dict()

    def test_pin_pair_rlc(self):
        c = CfgComponent("R1")
        c.add_pin_pair_rlc(first_pin="1", second_pin="2", resistance="1kohm", resistance_enabled=True)
        d = c.to_dict()
        assert len(d["pin_pair_model"]) == 1
        assert d["pin_pair_model"][0]["resistance"] == "1kohm"

    def test_pin_pair_rlc_all_fields(self):
        c = CfgComponent("R1")
        c.add_pin_pair_rlc(
            first_pin="1",
            second_pin="2",
            resistance="100ohm",
            inductance="1nH",
            capacitance="10nF",
            is_parallel=True,
            resistance_enabled=True,
            inductance_enabled=True,
            capacitance_enabled=True,
        )
        pp = c.to_dict()["pin_pair_model"][0]
        assert pp["is_parallel"] is True
        assert pp["inductance_enabled"] is True

    def test_multiple_pin_pair_rlc(self):
        c = CfgComponent("C1")
        c.add_pin_pair_rlc(first_pin="1", second_pin="2", capacitance="100nF", capacitance_enabled=True)
        c.add_pin_pair_rlc(first_pin="2", second_pin="3", resistance="10ohm", resistance_enabled=True)
        assert len(c.to_dict()["pin_pair_model"]) == 2

    def test_s_parameter_model(self):
        c = CfgComponent("U1")
        c.set_s_parameter_model(model_name="model1", model_path="/path/to/model.s2p", reference_net="GND")
        d = c.to_dict()
        assert d["s_parameter_model"]["model_name"] == "model1"
        assert d["s_parameter_model"]["reference_net"] == "GND"

    def test_spice_model(self):
        c = CfgComponent("U2")
        c.set_spice_model(model_name="ic_spice", model_path="/path/ic.sp", sub_circuit="IC_SUB")
        d = c.to_dict()
        assert d["spice_model"]["model_name"] == "ic_spice"
        assert d["spice_model"]["sub_circuit"] == "IC_SUB"

    def test_spice_model_terminal_pairs(self):
        c = CfgComponent("U2")
        c.set_spice_model("m", "/f.sp", terminal_pairs=[("1", "a"), ("2", "b")])
        assert c.spice_model["terminal_pairs"] == [("1", "a"), ("2", "b")]

    def test_spice_model_default_terminal_pairs(self):
        c = CfgComponent("U2")
        c.set_spice_model("m", "/f.sp")
        assert c.spice_model["terminal_pairs"] == []

    def test_netlist_model(self):
        c = CfgComponent("Q1")
        c.set_netlist_model(".subckt Q1 ...")
        d = c.to_dict()
        assert d["netlist_model"]["netlist"] == ".subckt Q1 ..."

    def test_ic_die_properties_default_not_in_dict(self):
        """Default ic_die {'type': 'no_die'} must be omitted when not explicitly set."""
        c = CfgComponent("U1")
        assert "ic_die_properties" not in c.to_dict()

    def test_ic_die_properties_no_die_explicit(self):
        c = CfgComponent("U1")
        c.set_ic_die_properties("no_die")
        d = c.to_dict()
        assert d["ic_die_properties"]["type"] == "no_die"

    def test_ic_die_properties_flip_chip(self):
        c = CfgComponent("U1")
        c.set_ic_die_properties(die_type="flip_chip", orientation="chip_down")
        d = c.to_dict()
        assert d["ic_die_properties"]["type"] == "flip_chip"
        assert d["ic_die_properties"]["orientation"] == "chip_down"

    def test_ic_die_properties_wire_bond(self):
        c = CfgComponent("U1")
        c.set_ic_die_properties(die_type="wire_bond", orientation="chip_up", height="200um")
        d = c.to_dict()
        assert d["ic_die_properties"]["height"] == "200um"

    def test_ic_die_no_height_when_not_wire_bond(self):
        c = CfgComponent("U1")
        c.set_ic_die_properties(die_type="flip_chip", orientation="chip_down", height="100um")
        assert "height" not in c.to_dict()["ic_die_properties"]

    def test_solder_ball_cylinder(self):
        c = CfgComponent("U1")
        c.set_solder_ball_properties(shape="cylinder", diameter="150um", height="100um")
        d = c.to_dict()
        assert d["solder_ball_properties"]["shape"] == "cylinder"
        assert d["solder_ball_properties"]["diameter"] == "150um"

    def test_solder_ball_height_auto_derived(self):
        """Height is derived as 2/3 * diameter when not provided."""
        c = CfgComponent("U1")
        c.set_solder_ball_properties(shape="cylinder", diameter="150um")
        assert c.solder_ball_properties["height"] == "100um"

    def test_solder_ball_diameter_default_when_no_pedb(self):
        """Diameter defaults to '150um' when no pedb and no diameter given."""
        c = CfgComponent("U1")
        c.set_solder_ball_properties()
        assert c.solder_ball_properties["diameter"] == "150um"

    def test_solder_ball_spheroid(self):
        c = CfgComponent("U1")
        c.set_solder_ball_properties(shape="spheroid", diameter="150um", height="100um", mid_diameter="130um")
        d = c.to_dict()
        assert d["solder_ball_properties"]["mid_diameter"] == "130um"

    def test_solder_ball_spheroid_mid_diameter_defaults_to_diameter(self):
        c = CfgComponent("U1")
        c.set_solder_ball_properties(shape="spheroid", diameter="150um", height="100um")
        assert c.solder_ball_properties["mid_diameter"] == "150um"

    def test_solder_ball_with_pedb_auto_size(self):
        """When pedb is attached and component exists, diameter is taken from pin pad size."""
        mock_pin = MagicMock()
        mock_pin.bounding_box = ((0, 0), (200e-6, 200e-6))
        mock_comp = MagicMock()
        mock_comp.pins = {"1": mock_pin}
        mock_pedb = MagicMock()
        mock_pedb.components.instances.get.return_value = mock_comp
        c = CfgComponent(mock_pedb, reference_designator="U1")
        c.set_solder_ball_properties(shape="cylinder")
        assert c.solder_ball_properties["diameter"] != "150um"

    def test_port_properties(self):
        c = CfgComponent("U1")
        c.set_port_properties(reference_height="50um", reference_size_auto=False)
        d = c.to_dict()
        assert d["port_properties"]["reference_height"] == "50um"
        assert d["port_properties"]["reference_size_auto"] is False

    def test_port_properties_defaults(self):
        c = CfgComponent("U1")
        c.set_port_properties()
        pp = c.port_properties
        assert pp["reference_height"] == "0"
        assert pp["reference_size_auto"] is True
        assert pp["reference_size_x"] == "0"
        assert pp["reference_size_y"] == "0"

    def test_set_parameters_to_edb_no_obj(self):
        """set_parameters_to_edb is a no-op when pyedb_obj is None."""
        c = CfgComponent("U1")
        c.set_parameters_to_edb()  # must not raise

    def test_retrieve_parameters_from_edb_no_obj(self):
        """retrieve_parameters_from_edb is a no-op when pyedb_obj is None."""
        c = CfgComponent("U1")
        c.retrieve_parameters_from_edb()  # must not raise

    def test_ic_die_properties_no_die(self):
        c = CfgComponent("U1")
        c.set_ic_die_properties("no_die")
        d = c.to_dict()
        assert d["ic_die_properties"]["type"] == "no_die"


class TestComponentsConfig:
    def test_empty(self):
        assert CfgComponents().to_list() == []

    def test_add_returns_component_config(self):
        cc = CfgComponents()
        comp = cc.add(reference_designator="R1", part_type="resistor")
        assert isinstance(comp, CfgComponent)

    def test_add_all_params(self):
        cc = CfgComponents()
        comp = cc.add("U1", part_type="ic", enabled=True, definition="BGA", placement_layer="1_Top")
        assert comp.definition == "BGA"
        assert comp.placement_layer == "1_Top"
        assert comp.enabled is True

    def test_to_list(self):
        cc = CfgComponents()
        cc.add(reference_designator="R1", part_type="resistor", enabled=True)
        cc.add(reference_designator="C1", part_type="capacitor")
        lst = cc.to_list()
        assert len(lst) == 2
        assert lst[0]["reference_designator"] == "R1"

    def test_clean(self):
        cc = CfgComponents()
        cc.add("R1")
        cc.clean()
        assert cc.components == []

    def test_get_cached(self):
        """get() returns existing component without querying EDB."""
        cc = CfgComponents()
        comp = cc.add("R1", part_type="resistor")
        result = cc.get("R1")
        assert result is comp

    def test_get_raises_without_pedb(self):
        cc = CfgComponents()
        with pytest.raises(KeyError):
            cc.get("R1")

    def test_get_raises_when_not_found(self):
        mock_pedb = MagicMock()
        mock_pedb.components.instances = {}
        cc = CfgComponents(pedb=mock_pedb)
        with pytest.raises(KeyError):
            cc.get("MISSING")

    def test_retrieve_parameters_from_edb_without_pedb(self):
        cc = CfgComponents()
        cc.add("R1")
        result = cc.retrieve_parameters_from_edb()
        # clean() is called first, then no pedb → returns serialized list of components at that moment
        assert isinstance(result, list)

    def test_retrieve_parameters_from_edb_clears_first(self):
        cc = CfgComponents()
        cc.add("R1")
        cc.retrieve_parameters_from_edb()
        assert len(cc.components) == 0  # clean() was called, no pedb to reload from

    def test_get_data_from_db_without_pedb(self):
        cc = CfgComponents()
        result = cc.get_data_from_db()
        assert result == []  # clean() wipes components, no pedb to reload

    def test_init_from_components_data(self):
        data = [{"reference_designator": "R1", "part_type": "resistor"}]
        cc = CfgComponents(components_data=data)
        assert len(cc.components) == 1
        assert cc.components[0].reference_designator == "R1"
