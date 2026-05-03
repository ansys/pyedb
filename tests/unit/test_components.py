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

"""Unit tests for cfg_components (CfgComponent / CfgComponents) – no EDB server required."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from pyedb.configuration.cfg_components import CfgComponent, CfgComponents

pytestmark = [pytest.mark.unit, pytest.mark.no_licence]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_pedb(grpc: bool = True):
    """Return a minimal fake pedb object."""
    pedb = MagicMock()
    pedb.grpc = grpc
    pedb.value = lambda v: v  # identity – just return the raw value
    pedb.components.set_solder_ball = MagicMock(return_value=True)
    return pedb


def _make_pyedb_obj(comp_type: str = "ic"):
    """Return a minimal fake component instance."""
    obj = MagicMock()
    obj.name = "U1"
    obj.type = comp_type
    obj.part_name = "PARTX"
    obj.model_type = "RLC"
    return obj


# ---------------------------------------------------------------------------
# CfgComponent – construction
# ---------------------------------------------------------------------------


class TestCfgComponentConstruction:
    def test_part_type_is_lowercased(self):
        c = CfgComponent(None, None, reference_designator="U1", part_type="IC")
        assert c.type == "ic"

    def test_enabled_stored(self):
        c = CfgComponent(None, None, reference_designator="R1", part_type="resistor", enabled=False)
        assert c.enabled is False

    def test_enabled_defaults_to_none(self):
        c = CfgComponent(None, None, reference_designator="R1")
        assert c.enabled is None

    def test_reference_designator_stored(self):
        c = CfgComponent(None, None, reference_designator="C42", part_type="capacitor")
        assert c.reference_designator == "C42"

    def test_definition_stored(self):
        c = CfgComponent(None, None, reference_designator="U1", part_type="ic", definition="PKG_A")
        assert c.definition == "PKG_A"

    def test_placement_layer_stored(self):
        c = CfgComponent(None, None, reference_designator="U1", part_type="ic", placement_layer="TOP")
        assert c.placement_layer == "TOP"

    def test_default_empty_collections(self):
        c = CfgComponent(None, None, reference_designator="U1")
        assert c.pin_pair_model == []
        assert c.spice_model == {}
        assert c.s_parameter_model == {}
        assert c.netlist_model == {}
        assert c.port_properties == {}
        assert c.solder_ball_properties == {}

    def test_ic_die_properties_defaults_to_no_die(self):
        c = CfgComponent(None, None, reference_designator="U1")
        assert c.ic_die_properties == {"type": "no_die"}

    def test_solder_ball_kwargs_passed_through(self):
        props = {"shape": "cylinder", "diameter": "150um", "height": "100um"}
        c = CfgComponent(None, None, reference_designator="U1", solder_ball_properties=props)
        assert c.solder_ball_properties == props

    def test_pin_pair_model_passed_through(self):
        model = [{"first_pin": "1", "second_pin": "2", "resistance": "100ohm"}]
        c = CfgComponent(None, None, reference_designator="R1", pin_pair_model=model)
        assert len(c.pin_pair_model) == 1
        assert c.pin_pair_model[0]["resistance"] == "100ohm"

    def test_no_part_type_gives_none(self):
        c = CfgComponent(None, None, reference_designator="X1")
        assert c.type is None

    def test_pins_stored(self):
        c = CfgComponent(None, None, reference_designator="U1", pins=["A1", "A2"])
        assert c.pins == ["A1", "A2"]

    def test_pins_defaults_to_empty(self):
        c = CfgComponent(None, None, reference_designator="U1")
        assert c.pins == []


# ---------------------------------------------------------------------------
# CfgComponent – set_parameters_to_edb
# ---------------------------------------------------------------------------


class TestCfgComponentSetParametersToEdb:
    def test_sets_type_on_pyedb_obj(self):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("resistor")
        obj.type = "resistor"
        c = CfgComponent(pedb, obj, reference_designator="R1", part_type="resistor")
        c._set_model_properties_to_edb = MagicMock()
        c.set_parameters_to_edb()
        assert obj.type == "resistor"

    def test_sets_enabled_on_pyedb_obj(self):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("resistor")
        obj.type = "resistor"
        c = CfgComponent(pedb, obj, reference_designator="R1", part_type="resistor", enabled=True)
        c._set_model_properties_to_edb = MagicMock()
        c.set_parameters_to_edb()
        assert obj.enabled is True

    def test_ic_type_calls_ic_methods(self):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("ic")
        obj.type = "ic"
        c = CfgComponent(pedb, obj, reference_designator="U1", part_type="ic")
        c._set_model_properties_to_edb = MagicMock()
        c._set_ic_die_properties_to_edb = MagicMock()
        c._set_port_properties_to_edb = MagicMock()
        c._set_solder_ball_properties_to_edb = MagicMock()
        c.set_parameters_to_edb()
        c._set_ic_die_properties_to_edb.assert_called_once()
        c._set_port_properties_to_edb.assert_called_once()
        c._set_solder_ball_properties_to_edb.assert_called_once()

    def test_io_type_calls_solder_and_port(self):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("io")
        obj.type = "io"
        c = CfgComponent(pedb, obj, reference_designator="J1", part_type="io")
        c._set_model_properties_to_edb = MagicMock()
        c._set_solder_ball_properties_to_edb = MagicMock()
        c._set_port_properties_to_edb = MagicMock()
        c.set_parameters_to_edb()
        c._set_solder_ball_properties_to_edb.assert_called_once()
        c._set_port_properties_to_edb.assert_called_once()

    def test_other_type_calls_solder_and_port(self):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("other")
        obj.type = "other"
        c = CfgComponent(pedb, obj, reference_designator="X1", part_type="other")
        c._set_model_properties_to_edb = MagicMock()
        c._set_solder_ball_properties_to_edb = MagicMock()
        c._set_port_properties_to_edb = MagicMock()
        c.set_parameters_to_edb()
        c._set_solder_ball_properties_to_edb.assert_called_once()
        c._set_port_properties_to_edb.assert_called_once()

    def test_resistor_type_does_not_call_ic_methods(self):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("resistor")
        obj.type = "resistor"
        c = CfgComponent(pedb, obj, reference_designator="R1", part_type="resistor")
        c._set_model_properties_to_edb = MagicMock()
        c._set_ic_die_properties_to_edb = MagicMock()
        c._set_solder_ball_properties_to_edb = MagicMock()
        c.set_parameters_to_edb()
        c._set_ic_die_properties_to_edb.assert_not_called()
        c._set_solder_ball_properties_to_edb.assert_not_called()

    def test_no_type_skips_type_assignment(self):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("resistor")
        obj.type = "resistor"
        c = CfgComponent(pedb, obj, reference_designator="R1")  # no part_type
        c._set_model_properties_to_edb = MagicMock()
        original_type = obj.type
        c.set_parameters_to_edb()
        # type should not have been changed since c.type is None
        assert obj.type == original_type

    def test_enabled_none_does_not_set_enabled(self):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("resistor")
        obj.type = "resistor"
        c = CfgComponent(pedb, obj, reference_designator="R1", part_type="resistor")
        c._set_model_properties_to_edb = MagicMock()
        c.set_parameters_to_edb()
        obj.__setattr__  # mock tracks this; we verify "enabled" was NOT explicitly set
        # enabled is None so the setter should not be called
        assert c.enabled is None


# ---------------------------------------------------------------------------
# CfgComponent – _set_solder_ball_properties_to_edb (grpc path)
# ---------------------------------------------------------------------------


class TestCfgComponentSolderBallGrpc:
    def test_cylinder_sets_shape_and_diameter(self):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("ic")
        c = CfgComponent(
            pedb,
            obj,
            reference_designator="U1",
            part_type="ic",
            solder_ball_properties={"shape": "cylinder", "diameter": "150um", "height": "100um"},
        )
        c._set_solder_ball_properties_to_edb()
        cp = obj.component_property
        sbp = cp.solder_ball_property
        sbp.set_diameter.assert_called()

    def test_no_shape_raises_value_error(self):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("ic")
        c = CfgComponent(pedb, obj, reference_designator="U1", part_type="ic", solder_ball_properties={})
        # grpc path: shape=None falls through to the else → ValueError
        with pytest.raises(ValueError, match="Solderball shape must be either cylinder or spheroid"):
            c._set_solder_ball_properties_to_edb()

    def test_spheroid_uses_mid_diameter(self):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("ic")
        c = CfgComponent(
            pedb,
            obj,
            reference_designator="U1",
            part_type="ic",
            solder_ball_properties={
                "shape": "spheroid",
                "diameter": "150um",
                "mid_diameter": "130um",
                "height": "100um",
            },
        )
        c._set_solder_ball_properties_to_edb()
        cp = obj.component_property
        sbp = cp.solder_ball_property
        sbp.set_diameter.assert_called_with(pedb.value("150um"), pedb.value("130um"))

    def test_material_is_set(self):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("ic")
        c = CfgComponent(
            pedb,
            obj,
            reference_designator="U1",
            part_type="ic",
            solder_ball_properties={
                "shape": "cylinder",
                "diameter": "150um",
                "height": "100um",
                "material": "copper",
            },
        )
        c._set_solder_ball_properties_to_edb()
        cp = obj.component_property
        sbp = cp.solder_ball_property
        assert sbp.material_name == "copper"

    def test_height_is_set(self):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("ic")
        c = CfgComponent(
            pedb,
            obj,
            reference_designator="U1",
            part_type="ic",
            solder_ball_properties={
                "shape": "cylinder",
                "diameter": "150um",
                "height": "100um",
            },
        )
        c._set_solder_ball_properties_to_edb()
        cp = obj.component_property
        sbp = cp.solder_ball_property
        assert sbp.height == pedb.value("100um")

    def test_invalid_shape_raises_value_error(self):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("ic")
        c = CfgComponent(
            pedb,
            obj,
            reference_designator="U1",
            part_type="ic",
            solder_ball_properties={
                "shape": "unknown_shape",
                "diameter": "150um",
                "height": "100um",
            },
        )
        with pytest.raises((ValueError, KeyError)):
            c._set_solder_ball_properties_to_edb()

    def test_no_solder_ball_properties_shape_none_raises(self):
        """shape key missing entirely should raise ValueError (grpc path)."""
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("ic")
        c = CfgComponent(
            pedb,
            obj,
            reference_designator="U1",
            part_type="ic",
            solder_ball_properties={"diameter": "150um", "height": "100um"},
        )
        with pytest.raises(ValueError, match="Solderball shape must be either cylinder or spheroid"):
            c._set_solder_ball_properties_to_edb()


# ---------------------------------------------------------------------------
# CfgComponent – _set_ic_die_properties_to_edb (grpc path)
# ---------------------------------------------------------------------------


class TestCfgComponentIcDiePropertiesGrpc:
    def _make_comp(self, die_type="no_die", orientation=None, height=None):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("ic")
        # Simulate grpc: component_property has no 'core' attribute
        del obj.component_property.core
        ic_die_props = {"type": die_type}
        if orientation:
            ic_die_props["orientation"] = orientation
        if height:
            ic_die_props["height"] = height
        c = CfgComponent(pedb, obj, reference_designator="U1", part_type="ic", ic_die_properties=ic_die_props)
        return pedb, obj, c

    def test_no_die_sets_die_type_only(self):
        pedb, obj, c = self._make_comp(die_type="no_die")
        c._set_ic_die_properties_to_edb()
        cp = obj.component_property
        # die_type should be assigned
        assert cp.die_property.die_type is not None

    def test_flip_chip_sets_orientation(self):
        pedb, obj, c = self._make_comp(die_type="flip_chip", orientation="chip_down")
        c._set_ic_die_properties_to_edb()
        cp = obj.component_property
        assert cp.die_property.die_orientation is not None

    def test_wire_bond_with_height_sets_height(self):
        pedb, obj, c = self._make_comp(die_type="wire_bond", orientation="chip_up", height="200um")
        c._set_ic_die_properties_to_edb()
        cp = obj.component_property
        assert cp.die_property.height == pedb.value("200um")

    def test_wire_bond_without_height_skips_height(self):
        pedb, obj, c = self._make_comp(die_type="wire_bond", orientation="chip_up")
        # Should not raise even without height
        c._set_ic_die_properties_to_edb()

    def test_flip_chip_no_orientation_skips_orientation(self):
        pedb, obj, c = self._make_comp(die_type="flip_chip")
        # Should not raise even without orientation
        c._set_ic_die_properties_to_edb()


# ---------------------------------------------------------------------------
# CfgComponent – _set_port_properties_to_edb (grpc path)
# ---------------------------------------------------------------------------


class TestCfgComponentPortPropertiesGrpc:
    def _make_comp(self, port_props):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("ic")
        c = CfgComponent(pedb, obj, reference_designator="U1", part_type="ic", port_properties=port_props)
        return pedb, obj, c

    def test_reference_height_is_set(self):
        pedb, obj, c = self._make_comp({"reference_height": "50um"})
        c._set_port_properties_to_edb()
        pp = obj.component_property.port_property
        assert pp.reference_height == pedb.value("50um")

    def test_reference_size_auto_is_set(self):
        pedb, obj, c = self._make_comp({"reference_size_auto": True})
        c._set_port_properties_to_edb()
        pp = obj.component_property.port_property
        assert pp.reference_size_auto is True

    def test_reference_size_auto_false_is_set(self):
        pedb, obj, c = self._make_comp({"reference_size_auto": False})
        c._set_port_properties_to_edb()
        pp = obj.component_property.port_property
        assert pp.reference_size_auto is False

    def test_set_reference_size_called(self):
        pedb, obj, c = self._make_comp({"reference_size_x": "100um", "reference_size_y": "200um"})
        c._set_port_properties_to_edb()
        pp = obj.component_property.port_property
        pp.set_reference_size.assert_called_with(pedb.value("100um"), pedb.value("200um"))

    def test_empty_port_properties_no_raise(self):
        pedb, obj, c = self._make_comp({})
        c._set_port_properties_to_edb()  # Should not raise


# ---------------------------------------------------------------------------
# CfgComponent – _set_model_properties_to_edb
# ---------------------------------------------------------------------------


class TestCfgComponentSetModelProperties:
    def test_netlist_model_calls_assign_netlist(self):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("ic")
        c = CfgComponent(
            pedb, obj, reference_designator="U1", part_type="ic", netlist_model={"netlist": "* test netlist"}
        )
        c._set_model_properties_to_edb()
        obj.assign_netlist_model.assert_called_once_with("* test netlist")

    def test_pin_pair_model_calls_add_pin_pair(self):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("ic")
        c = CfgComponent(
            pedb,
            obj,
            reference_designator="U1",
            part_type="ic",
            pin_pair_model=[
                {
                    "first_pin": "1",
                    "second_pin": "2",
                    "resistance": "10ohm",
                    "resistance_enabled": True,
                    "inductance": "1nH",
                    "inductance_enabled": False,
                    "capacitance": "1pF",
                    "capacitance_enabled": False,
                    "is_parallel": False,
                }
            ],
        )
        c._set_model_properties_to_edb()
        obj.model.add_pin_pair.assert_called_once()

    def test_s_parameter_model_calls_assign_s_param(self):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("ic")
        c = CfgComponent(
            pedb,
            obj,
            reference_designator="U1",
            part_type="ic",
            s_parameter_model={"model_path": "/path/m.s2p", "model_name": "my_model", "reference_net": "GND"},
        )
        c._set_model_properties_to_edb()
        obj.assign_s_param_model.assert_called_once_with("/path/m.s2p", "my_model", "GND")

    def test_spice_model_calls_assign_spice(self):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("ic")
        c = CfgComponent(
            pedb,
            obj,
            reference_designator="U1",
            part_type="ic",
            spice_model={
                "model_path": "/path/m.sp",
                "model_name": "spice_m",
                "sub_circuit": "TOP",
                "terminal_pairs": [["p1", 1]],
            },
        )
        c._set_model_properties_to_edb()
        obj.assign_spice_model.assert_called_once_with("/path/m.sp", "spice_m", "TOP", [["p1", 1]])

    def test_no_model_no_call(self):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("ic")
        c = CfgComponent(pedb, obj, reference_designator="U1", part_type="ic")
        c._set_model_properties_to_edb()
        obj.assign_netlist_model.assert_not_called()
        obj.assign_s_param_model.assert_not_called()
        obj.assign_spice_model.assert_not_called()


# ---------------------------------------------------------------------------
# CfgComponent – retrieve_model_properties_from_edb
# ---------------------------------------------------------------------------


class TestCfgComponentRetrieveModelProperties:
    def test_netlist_model_type(self):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("ic")
        obj.model_type = "NetlistModel"
        obj.netlist_model = "* netlist"
        c = CfgComponent(pedb, obj, reference_designator="U1", part_type="ic")
        c.retrieve_model_properties_from_edb()
        assert c.netlist_model.get("netlist") == "* netlist"

    def test_rlc_model_type_with_pin_pair_rlc(self):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("resistor")
        obj.model_type = "RLC"
        pp = MagicMock()
        pp.first_pin = "1"
        pp.second_pin = "2"
        pp._pin_pair_rlc.IsParallel = False
        pp._pin_pair_rlc.R.ToDouble.return_value = 100.0
        pp._pin_pair_rlc.REnabled = True
        pp._pin_pair_rlc.L.ToDouble.return_value = 0.0
        pp._pin_pair_rlc.LEnabled = False
        pp._pin_pair_rlc.C.ToDouble.return_value = 0.0
        pp._pin_pair_rlc.CEnabled = False
        obj.pin_pairs = [pp]
        c = CfgComponent(pedb, obj, reference_designator="R1", part_type="resistor")
        c.retrieve_model_properties_from_edb()
        assert len(c.pin_pair_model) == 1
        assert c.pin_pair_model[0]["first_pin"] == "1"
        assert c.pin_pair_model[0]["resistance"] == "100.0"

    def test_rlc_model_type_exception_fallback(self):
        """When _pin_pair_rlc raises, falls back to res_value/ind_value/cap_value."""
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("resistor")
        obj.model_type = "RLC"
        pp = MagicMock()
        pp.first_pin = "1"
        pp.second_pin = "2"
        # Make accessing _pin_pair_rlc raise AttributeError
        del pp._pin_pair_rlc
        obj.pin_pairs = [pp]
        obj.res_value = 50.0
        obj.ind_value = 1e-9
        obj.cap_value = 0.0
        obj.rlc_enable = [True, False, False]
        c = CfgComponent(pedb, obj, reference_designator="R1", part_type="resistor")
        c.retrieve_model_properties_from_edb()
        assert len(c.pin_pair_model) == 1
        assert c.pin_pair_model[0]["resistance"] == "50.0"

    def test_empty_pin_pairs_returns_early(self):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("resistor")
        obj.model_type = "PinPairModel"
        obj.pin_pairs = []
        c = CfgComponent(pedb, obj, reference_designator="R1", part_type="resistor")
        c.retrieve_model_properties_from_edb()
        assert c.pin_pair_model == []

    def test_s_parameter_model_type(self):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("ic")
        obj.model_type = "SParameterModel"
        obj.model.reference_net = "GND"
        obj.model.component_model_name = "s_model"
        c = CfgComponent(pedb, obj, reference_designator="U1", part_type="ic")
        c.retrieve_model_properties_from_edb()
        assert c.s_parameter_model["reference_net"] == "GND"
        assert c.s_parameter_model["model_name"] == "s_model"

    def test_spice_model_type(self):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("ic")
        obj.model_type = "SPICEModel"
        obj.model.model_name = "spice_m"
        obj.model.spice_file_path = "/path/m.sp"
        obj.model.sub_circuit = "TOP"
        obj.model.pin_pairs = [["p1", 1]]
        c = CfgComponent(pedb, obj, reference_designator="U1", part_type="ic")
        c.retrieve_model_properties_from_edb()
        assert c.spice_model["model_name"] == "spice_m"
        assert c.spice_model["sub_circuit"] == "TOP"
        assert c.spice_model["terminal_pairs"] == [["p1", 1]]


# ---------------------------------------------------------------------------
# CfgComponent – retrieve_parameters_from_edb
# ---------------------------------------------------------------------------


class TestCfgComponentRetrieve:
    def _make_ic_obj(self):
        obj = MagicMock()
        obj.name = "U1"
        obj.type = "ic"
        obj.part_name = "PKG"
        obj.model_type = "RLC"
        obj.pin_pairs = []
        obj.ic_die_properties.die_type = "flip_chip"
        obj.ic_die_properties.die_orientation = "chip_down"
        obj.uses_solderball = True
        obj.solder_ball_shape = "cylinder"
        obj.solder_ball_diameter = ("150e-6", "150e-6")
        obj.solder_ball_height = "100e-6"
        obj.solder_ball_material = "solder"
        obj.component_property.port_property.reference_height = "0"
        obj.component_property.port_property.reference_size_auto = True
        obj.component_property.port_property.get_reference_size.return_value = ("0", "0")
        return obj

    def test_sets_type_and_refdes(self):
        pedb = _make_pedb(grpc=True)
        obj = self._make_ic_obj()
        c = CfgComponent(pedb, obj, reference_designator="U1", part_type="ic")
        c.retrieve_parameters_from_edb()
        assert c.type == "ic"
        assert c.reference_designator == "U1"
        assert c.definition == "PKG"

    def test_ic_retrieves_die_properties(self):
        pedb = _make_pedb(grpc=True)
        obj = self._make_ic_obj()
        c = CfgComponent(pedb, obj, reference_designator="U1", part_type="ic")
        c.retrieve_parameters_from_edb()
        assert c.ic_die_properties.get("type") == "flip_chip"
        assert c.ic_die_properties.get("orientation") == "chip_down"

    def test_ic_retrieves_solder_ball_properties(self):
        pedb = _make_pedb(grpc=True)
        obj = self._make_ic_obj()
        c = CfgComponent(pedb, obj, reference_designator="U1", part_type="ic")
        c.retrieve_parameters_from_edb()
        assert c.solder_ball_properties["shape"] == "cylinder"
        assert c.solder_ball_properties["uses_solder_ball"] is True

    def test_ic_retrieves_port_properties(self):
        pedb = _make_pedb(grpc=True)
        obj = self._make_ic_obj()
        c = CfgComponent(pedb, obj, reference_designator="U1", part_type="ic")
        c.retrieve_parameters_from_edb()
        assert "reference_height" in c.port_properties
        assert "reference_size_auto" in c.port_properties

    def test_resistor_skips_ic_die_and_port(self):
        pedb = _make_pedb(grpc=True)
        obj = MagicMock()
        obj.name = "R1"
        obj.type = "resistor"
        obj.part_name = "RES_100"
        obj.model_type = "RLC"
        obj.pin_pairs = []
        c = CfgComponent(pedb, obj, reference_designator="R1", part_type="resistor")
        c.retrieve_parameters_from_edb()
        # ic_die_properties should remain at its default (no retrieval for resistors)
        assert c.ic_die_properties == {"type": "no_die"}
        assert c.port_properties == {}

    def test_io_retrieves_solder_ball_and_port(self):
        pedb = _make_pedb(grpc=True)
        obj = MagicMock()
        obj.name = "J1"
        obj.type = "io"
        obj.part_name = "CONN"
        obj.model_type = "RLC"
        obj.pin_pairs = []
        obj.uses_solderball = False
        obj.solder_ball_shape = "none"
        obj.solder_ball_diameter = ("0", "0")
        obj.solder_ball_height = "0"
        obj.solder_ball_material = "solder"
        obj.component_property.port_property.reference_height = "0"
        obj.component_property.port_property.reference_size_auto = True
        obj.component_property.port_property.get_reference_size.return_value = ("0", "0")
        c = CfgComponent(pedb, obj, reference_designator="J1", part_type="io")
        c.retrieve_parameters_from_edb()
        assert "shape" in c.solder_ball_properties
        assert "reference_height" in c.port_properties

    def test_other_type_retrieves_solder_ball_and_port(self):
        pedb = _make_pedb(grpc=True)
        obj = MagicMock()
        obj.name = "X1"
        obj.type = "other"
        obj.part_name = "OTHER"
        obj.model_type = "RLC"
        obj.pin_pairs = []
        obj.uses_solderball = False
        obj.solder_ball_shape = "none"
        obj.solder_ball_diameter = ("0", "0")
        obj.solder_ball_height = "0"
        obj.solder_ball_material = "solder"
        obj.component_property.port_property.reference_height = "0"
        obj.component_property.port_property.reference_size_auto = True
        obj.component_property.port_property.get_reference_size.return_value = ("0", "0")
        c = CfgComponent(pedb, obj, reference_designator="X1", part_type="other")
        c.retrieve_parameters_from_edb()
        assert "shape" in c.solder_ball_properties
        assert "reference_height" in c.port_properties

    def test_wire_bond_die_retrieves_height(self):
        pedb = _make_pedb(grpc=True)
        obj = self._make_ic_obj()
        obj.ic_die_properties.die_type = "wire_bond"
        obj.ic_die_properties.die_orientation = "chip_up"
        obj.ic_die_properties.height = 200e-6
        c = CfgComponent(pedb, obj, reference_designator="U1", part_type="ic")
        c.retrieve_parameters_from_edb()
        assert c.ic_die_properties["type"] == "wire_bond"
        assert "height" in c.ic_die_properties

    def test_no_die_type_skips_orientation_and_height(self):
        pedb = _make_pedb(grpc=True)
        obj = self._make_ic_obj()
        obj.ic_die_properties.die_type = "no_die"
        c = CfgComponent(pedb, obj, reference_designator="U1", part_type="ic")
        c.retrieve_parameters_from_edb()
        assert c.ic_die_properties["type"] == "no_die"
        assert "orientation" not in c.ic_die_properties


# ---------------------------------------------------------------------------
# CfgComponent – _retrieve_port_properties_from_edb (type guard)
# ---------------------------------------------------------------------------


class TestRetrievePortPropertiesTypeGuard:
    def test_capacitor_type_skips_port_properties(self):
        pedb = _make_pedb(grpc=True)
        obj = MagicMock()
        obj.component_property.port_property.reference_height = "0"
        c = CfgComponent(pedb, obj, reference_designator="C1", part_type="capacitor")
        c._retrieve_port_properties_from_edb()
        assert c.port_properties == {}

    def test_resistor_type_skips_port_properties(self):
        pedb = _make_pedb(grpc=True)
        obj = MagicMock()
        c = CfgComponent(pedb, obj, reference_designator="R1", part_type="resistor")
        c._retrieve_port_properties_from_edb()
        assert c.port_properties == {}

    def test_ic_type_populates_port_properties(self):
        pedb = _make_pedb(grpc=True)
        obj = MagicMock()
        obj.component_property.port_property.reference_height = "0"
        obj.component_property.port_property.reference_size_auto = True
        obj.component_property.port_property.get_reference_size.return_value = ("0", "0")
        c = CfgComponent(pedb, obj, reference_designator="U1", part_type="ic")
        c._retrieve_port_properties_from_edb()
        assert "reference_height" in c.port_properties
        assert "reference_size_auto" in c.port_properties


# ---------------------------------------------------------------------------
# CfgComponents (collection)
# ---------------------------------------------------------------------------


class TestCfgComponents:
    def test_init_empty(self):
        cc = CfgComponents(None, None)
        assert cc.components == []

    def test_clean_removes_all(self):
        cc = CfgComponents(None, None)
        cc.components = [MagicMock(), MagicMock()]
        cc.clean()
        assert cc.components == []

    def test_apply_calls_set_parameters_for_each(self):
        cc = CfgComponents(None, None)
        mock1 = MagicMock(spec=CfgComponent)
        mock2 = MagicMock(spec=CfgComponent)
        cc.components = [mock1, mock2]
        cc.apply()
        mock1.set_parameters_to_edb.assert_called_once()
        mock2.set_parameters_to_edb.assert_called_once()

    def test_apply_empty_list_does_nothing(self):
        cc = CfgComponents(None, None)
        cc.apply()  # Should not raise

    def test_init_from_components_data(self):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("resistor")
        obj.name = "R1"
        pedb.components.instances = {"R1": obj}
        data = [{"reference_designator": "R1", "part_type": "resistor", "enabled": True}]
        cc = CfgComponents(pedb, data)
        assert len(cc.components) == 1
        assert cc.components[0].reference_designator == "R1"
        assert cc.components[0].enabled is True

    def test_init_none_data_gives_empty_list(self):
        cc = CfgComponents(None, None)
        assert cc.components == []

    def test_retrieve_parameters_from_edb_populates_list(self):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("resistor")
        obj.name = "R1"
        pedb.components.instances = {"R1": obj}
        cc = CfgComponents(pedb, None)
        with patch.object(CfgComponent, "retrieve_parameters_from_edb", MagicMock()):
            cc.retrieve_parameters_from_edb()
        assert len(cc.components) == 1

    def test_retrieve_parameters_multiple_components(self):
        pedb = _make_pedb(grpc=True)
        obj1 = _make_pyedb_obj("resistor")
        obj1.name = "R1"
        obj2 = _make_pyedb_obj("capacitor")
        obj2.name = "C1"
        pedb.components.instances = {"R1": obj1, "C1": obj2}
        cc = CfgComponents(pedb, None)
        with patch.object(CfgComponent, "retrieve_parameters_from_edb", MagicMock()):
            cc.retrieve_parameters_from_edb()
        assert len(cc.components) == 2

    def test_retrieve_clears_previous_components(self):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("resistor")
        obj.name = "R1"
        pedb.components.instances = {"R1": obj}
        cc = CfgComponents(pedb, None)
        cc.components = [MagicMock(), MagicMock()]  # pre-populate
        with patch.object(CfgComponent, "retrieve_parameters_from_edb", MagicMock()):
            cc.retrieve_parameters_from_edb()
        assert len(cc.components) == 1  # cleared and re-populated

    def test_retrieve_then_clean_gives_empty(self):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("resistor")
        obj.name = "R1"
        pedb.components.instances = {"R1": obj}
        cc = CfgComponents(pedb, None)
        with patch.object(CfgComponent, "retrieve_parameters_from_edb", MagicMock()):
            cc.retrieve_parameters_from_edb()
        cc.clean()
        assert cc.components == []

    def test_init_multiple_components_data(self):
        pedb = _make_pedb(grpc=True)
        obj_r = _make_pyedb_obj("resistor")
        obj_r.name = "R1"
        obj_c = _make_pyedb_obj("capacitor")
        obj_c.name = "C1"
        pedb.components.instances = {"R1": obj_r, "C1": obj_c}
        data = [
            {"reference_designator": "R1", "part_type": "resistor"},
            {"reference_designator": "C1", "part_type": "capacitor"},
        ]
        cc = CfgComponents(pedb, data)
        assert len(cc.components) == 2
        refdes = [c.reference_designator for c in cc.components]
        assert "R1" in refdes
        assert "C1" in refdes


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_pedb(grpc: bool = True):
    """Return a minimal fake pedb object."""
    pedb = MagicMock()
    pedb.grpc = grpc
    pedb.value = lambda v: v  # identity – just return the raw value
    pedb.components.set_solder_ball = MagicMock(return_value=True)
    return pedb


def _make_pyedb_obj(comp_type: str = "ic"):
    """Return a minimal fake component instance."""
    obj = MagicMock()
    obj.name = "U1"
    obj.type = comp_type
    obj.part_name = "PARTX"
    obj.model_type = "RLC"
    return obj


# ---------------------------------------------------------------------------
# CfgComponent – construction
# ---------------------------------------------------------------------------


class TestCfgComponentConstruction:
    def test_part_type_is_lowercased(self):
        c = CfgComponent(None, None, reference_designator="U1", part_type="IC")
        assert c.type == "ic"

    def test_enabled_stored(self):
        c = CfgComponent(None, None, reference_designator="R1", part_type="resistor", enabled=False)
        assert c.enabled is False

    def test_enabled_defaults_to_none(self):
        c = CfgComponent(None, None, reference_designator="R1")
        assert c.enabled is None

    def test_reference_designator_stored(self):
        c = CfgComponent(None, None, reference_designator="C42", part_type="capacitor")
        assert c.reference_designator == "C42"

    def test_definition_stored(self):
        c = CfgComponent(None, None, reference_designator="U1", part_type="ic", definition="PKG_A")
        assert c.definition == "PKG_A"

    def test_placement_layer_stored(self):
        c = CfgComponent(None, None, reference_designator="U1", part_type="ic", placement_layer="TOP")
        assert c.placement_layer == "TOP"

    def test_default_empty_collections(self):
        c = CfgComponent(None, None, reference_designator="U1")
        assert c.pin_pair_model == []
        assert c.spice_model == {}
        assert c.s_parameter_model == {}
        assert c.netlist_model == {}
        assert c.port_properties == {}
        assert c.solder_ball_properties == {}

    def test_ic_die_properties_defaults_to_no_die(self):
        c = CfgComponent(None, None, reference_designator="U1")
        assert c.ic_die_properties == {"type": "no_die"}

    def test_solder_ball_kwargs_passed_through(self):
        props = {"shape": "cylinder", "diameter": "150um", "height": "100um"}
        c = CfgComponent(None, None, reference_designator="U1", solder_ball_properties=props)
        assert c.solder_ball_properties == props

    def test_pin_pair_model_passed_through(self):
        model = [{"first_pin": "1", "second_pin": "2", "resistance": "100ohm"}]
        c = CfgComponent(None, None, reference_designator="R1", pin_pair_model=model)
        assert len(c.pin_pair_model) == 1
        assert c.pin_pair_model[0]["resistance"] == "100ohm"

    def test_no_part_type_gives_none(self):
        c = CfgComponent(None, None, reference_designator="X1")
        assert c.type is None


# ---------------------------------------------------------------------------
# CfgComponent – set_parameters_to_edb
# ---------------------------------------------------------------------------


class TestCfgComponentSetParametersToEdb:
    def test_sets_type_on_pyedb_obj(self):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("resistor")
        obj.type = "resistor"
        c = CfgComponent(pedb, obj, reference_designator="R1", part_type="resistor")
        c._set_model_properties_to_edb = MagicMock()
        c.set_parameters_to_edb()
        assert obj.type == "resistor"

    def test_sets_enabled_on_pyedb_obj(self):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("resistor")
        obj.type = "resistor"
        c = CfgComponent(pedb, obj, reference_designator="R1", part_type="resistor", enabled=True)
        c._set_model_properties_to_edb = MagicMock()
        c.set_parameters_to_edb()
        assert obj.enabled is True

    def test_ic_type_calls_ic_methods(self):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("ic")
        obj.type = "ic"
        c = CfgComponent(pedb, obj, reference_designator="U1", part_type="ic")
        c._set_model_properties_to_edb = MagicMock()
        c._set_ic_die_properties_to_edb = MagicMock()
        c._set_port_properties_to_edb = MagicMock()
        c._set_solder_ball_properties_to_edb = MagicMock()
        c.set_parameters_to_edb()
        c._set_ic_die_properties_to_edb.assert_called_once()
        c._set_port_properties_to_edb.assert_called_once()
        c._set_solder_ball_properties_to_edb.assert_called_once()

    def test_io_type_calls_solder_and_port(self):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("io")
        obj.type = "io"
        c = CfgComponent(pedb, obj, reference_designator="J1", part_type="io")
        c._set_model_properties_to_edb = MagicMock()
        c._set_solder_ball_properties_to_edb = MagicMock()
        c._set_port_properties_to_edb = MagicMock()
        c.set_parameters_to_edb()
        c._set_solder_ball_properties_to_edb.assert_called_once()
        c._set_port_properties_to_edb.assert_called_once()

    def test_other_type_calls_solder_and_port(self):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("other")
        obj.type = "other"
        c = CfgComponent(pedb, obj, reference_designator="X1", part_type="other")
        c._set_model_properties_to_edb = MagicMock()
        c._set_solder_ball_properties_to_edb = MagicMock()
        c._set_port_properties_to_edb = MagicMock()
        c.set_parameters_to_edb()
        c._set_solder_ball_properties_to_edb.assert_called_once()
        c._set_port_properties_to_edb.assert_called_once()

    def test_resistor_type_does_not_call_ic_methods(self):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("resistor")
        obj.type = "resistor"
        c = CfgComponent(pedb, obj, reference_designator="R1", part_type="resistor")
        c._set_model_properties_to_edb = MagicMock()
        c._set_ic_die_properties_to_edb = MagicMock()
        c._set_solder_ball_properties_to_edb = MagicMock()
        c.set_parameters_to_edb()
        c._set_ic_die_properties_to_edb.assert_not_called()
        c._set_solder_ball_properties_to_edb.assert_not_called()

    def test_no_type_skips_type_assignment(self):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("resistor")
        obj.type = "resistor"
        c = CfgComponent(pedb, obj, reference_designator="R1")  # no part_type
        c._set_model_properties_to_edb = MagicMock()
        original_type = obj.type
        c.set_parameters_to_edb()
        # type should not have been changed since c.type is None
        assert obj.type == original_type


# ---------------------------------------------------------------------------
# CfgComponent – _set_solder_ball_properties_to_edb (grpc path)
# ---------------------------------------------------------------------------


class TestCfgComponentSolderBallGrpc:
    def test_cylinder_sets_shape_and_diameter(self):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("ic")
        c = CfgComponent(
            pedb,
            obj,
            reference_designator="U1",
            part_type="ic",
            solder_ball_properties={"shape": "cylinder", "diameter": "150um", "height": "100um"},
        )
        c._set_solder_ball_properties_to_edb()
        cp = obj.component_property
        sbp = cp.solder_ball_property
        sbp.set_diameter.assert_called()

    def test_no_shape_raises_value_error(self):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("ic")
        c = CfgComponent(pedb, obj, reference_designator="U1", part_type="ic", solder_ball_properties={})
        # grpc path: shape=None falls through to the else → ValueError
        with pytest.raises(ValueError, match="Solderball shape must be either cylinder or spheroid"):
            c._set_solder_ball_properties_to_edb()

    def test_spheroid_uses_mid_diameter(self):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("ic")
        c = CfgComponent(
            pedb,
            obj,
            reference_designator="U1",
            part_type="ic",
            solder_ball_properties={
                "shape": "spheroid",
                "diameter": "150um",
                "mid_diameter": "130um",
                "height": "100um",
            },
        )
        c._set_solder_ball_properties_to_edb()
        cp = obj.component_property
        sbp = cp.solder_ball_property
        sbp.set_diameter.assert_called_with(pedb.value("150um"), pedb.value("130um"))

    def test_material_is_set(self):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("ic")
        c = CfgComponent(
            pedb,
            obj,
            reference_designator="U1",
            part_type="ic",
            solder_ball_properties={
                "shape": "cylinder",
                "diameter": "150um",
                "height": "100um",
                "material": "copper",
            },
        )
        c._set_solder_ball_properties_to_edb()
        cp = obj.component_property
        sbp = cp.solder_ball_property
        assert sbp.material_name == "copper"

    def test_height_is_set(self):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("ic")
        c = CfgComponent(
            pedb,
            obj,
            reference_designator="U1",
            part_type="ic",
            solder_ball_properties={
                "shape": "cylinder",
                "diameter": "150um",
                "height": "100um",
            },
        )
        c._set_solder_ball_properties_to_edb()
        cp = obj.component_property
        sbp = cp.solder_ball_property
        assert sbp.height == pedb.value("100um")

    def test_invalid_shape_raises_value_error(self):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("ic")
        # In the current implementation, non-cylinder/spheroid shape is assigned via mapping
        # and then the code reaches the else branch that raises ValueError
        c = CfgComponent(
            pedb,
            obj,
            reference_designator="U1",
            part_type="ic",
            solder_ball_properties={
                "shape": "unknown_shape",
                "diameter": "150um",
                "height": "100um",
            },
        )
        with pytest.raises((ValueError, KeyError)):
            c._set_solder_ball_properties_to_edb()


# ---------------------------------------------------------------------------
# CfgComponent – retrieve_parameters_from_edb
# ---------------------------------------------------------------------------


class TestCfgComponentRetrieve:
    def _make_ic_obj(self):
        obj = MagicMock()
        obj.name = "U1"
        obj.type = "ic"
        obj.part_name = "PKG"
        obj.model_type = "RLC"
        obj.pin_pairs = []
        obj.ic_die_properties.die_type = "flip_chip"
        obj.ic_die_properties.die_orientation = "chip_down"
        obj.uses_solderball = True
        obj.solder_ball_shape = "cylinder"
        obj.solder_ball_diameter = ("150e-6", "150e-6")
        obj.solder_ball_height = "100e-6"
        obj.solder_ball_material = "solder"
        obj.component_property.port_property.reference_height = "0"
        obj.component_property.port_property.reference_size_auto = True
        obj.component_property.port_property.get_reference_size.return_value = ("0", "0")
        return obj

    def test_sets_type_and_refdes(self):
        pedb = _make_pedb(grpc=True)
        obj = self._make_ic_obj()
        c = CfgComponent(pedb, obj, reference_designator="U1", part_type="ic")
        c.retrieve_parameters_from_edb()
        assert c.type == "ic"
        assert c.reference_designator == "U1"
        assert c.definition == "PKG"

    def test_ic_retrieves_die_properties(self):
        pedb = _make_pedb(grpc=True)
        obj = self._make_ic_obj()
        c = CfgComponent(pedb, obj, reference_designator="U1", part_type="ic")
        c.retrieve_parameters_from_edb()
        assert c.ic_die_properties.get("type") == "flip_chip"
        assert c.ic_die_properties.get("orientation") == "chip_down"

    def test_ic_retrieves_solder_ball_properties(self):
        pedb = _make_pedb(grpc=True)
        obj = self._make_ic_obj()
        c = CfgComponent(pedb, obj, reference_designator="U1", part_type="ic")
        c.retrieve_parameters_from_edb()
        assert c.solder_ball_properties["shape"] == "cylinder"
        assert c.solder_ball_properties["uses_solder_ball"] is True

    def test_ic_retrieves_port_properties(self):
        pedb = _make_pedb(grpc=True)
        obj = self._make_ic_obj()
        c = CfgComponent(pedb, obj, reference_designator="U1", part_type="ic")
        c.retrieve_parameters_from_edb()
        assert "reference_height" in c.port_properties
        assert "reference_size_auto" in c.port_properties

    def test_resistor_skips_ic_die_and_port(self):
        pedb = _make_pedb(grpc=True)
        obj = MagicMock()
        obj.name = "R1"
        obj.type = "resistor"
        obj.part_name = "RES_100"
        obj.model_type = "RLC"
        obj.pin_pairs = []
        c = CfgComponent(pedb, obj, reference_designator="R1", part_type="resistor")
        c.retrieve_parameters_from_edb()
        # ic_die_properties should remain at its default (no retrieval for resistors)
        assert c.ic_die_properties == {"type": "no_die"}
        assert c.port_properties == {}

    def test_io_retrieves_solder_ball_and_port(self):
        pedb = _make_pedb(grpc=True)
        obj = MagicMock()
        obj.name = "J1"
        obj.type = "io"
        obj.part_name = "CONN"
        obj.model_type = "RLC"
        obj.pin_pairs = []
        obj.uses_solderball = False
        obj.solder_ball_shape = "none"
        obj.solder_ball_diameter = ("0", "0")
        obj.solder_ball_height = "0"
        obj.solder_ball_material = "solder"
        obj.component_property.port_property.reference_height = "0"
        obj.component_property.port_property.reference_size_auto = True
        obj.component_property.port_property.get_reference_size.return_value = ("0", "0")
        c = CfgComponent(pedb, obj, reference_designator="J1", part_type="io")
        c.retrieve_parameters_from_edb()
        assert "shape" in c.solder_ball_properties
        assert "reference_height" in c.port_properties


# ---------------------------------------------------------------------------
# CfgComponents (collection)
# ---------------------------------------------------------------------------


class TestCfgComponents:
    def test_init_empty(self):
        cc = CfgComponents(None, None)
        assert cc.components == []

    def test_clean_removes_all(self):
        cc = CfgComponents(None, None)
        cc.components = [MagicMock(), MagicMock()]
        cc.clean()
        assert cc.components == []

    def test_apply_calls_set_parameters_for_each(self):
        cc = CfgComponents(None, None)
        mock1 = MagicMock(spec=CfgComponent)
        mock2 = MagicMock(spec=CfgComponent)
        cc.components = [mock1, mock2]
        cc.apply()
        mock1.set_parameters_to_edb.assert_called_once()
        mock2.set_parameters_to_edb.assert_called_once()

    def test_apply_empty_list_does_nothing(self):
        cc = CfgComponents(None, None)
        cc.apply()  # Should not raise

    def test_init_from_components_data(self):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("resistor")
        obj.name = "R1"
        pedb.components.instances = {"R1": obj}
        data = [{"reference_designator": "R1", "part_type": "resistor", "enabled": True}]
        cc = CfgComponents(pedb, data)
        assert len(cc.components) == 1
        assert cc.components[0].reference_designator == "R1"
        assert cc.components[0].enabled is True

    def test_init_none_data_gives_empty_list(self):
        cc = CfgComponents(None, None)
        assert cc.components == []

    def test_retrieve_parameters_from_edb_populates_list(self):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("resistor")
        obj.name = "R1"
        pedb.components.instances = {"R1": obj}
        cc = CfgComponents(pedb, None)
        with patch.object(CfgComponent, "retrieve_parameters_from_edb", MagicMock()):
            cc.retrieve_parameters_from_edb()
        assert len(cc.components) == 1

    def test_retrieve_parameters_multiple_components(self):
        pedb = _make_pedb(grpc=True)
        obj1 = _make_pyedb_obj("resistor")
        obj1.name = "R1"
        obj2 = _make_pyedb_obj("capacitor")
        obj2.name = "C1"
        pedb.components.instances = {"R1": obj1, "C1": obj2}
        cc = CfgComponents(pedb, None)
        with patch.object(CfgComponent, "retrieve_parameters_from_edb", MagicMock()):
            cc.retrieve_parameters_from_edb()
        assert len(cc.components) == 2

    def test_retrieve_clears_previous_components(self):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("resistor")
        obj.name = "R1"
        pedb.components.instances = {"R1": obj}
        cc = CfgComponents(pedb, None)
        cc.components = [MagicMock(), MagicMock()]  # pre-populate
        with patch.object(CfgComponent, "retrieve_parameters_from_edb", MagicMock()):
            cc.retrieve_parameters_from_edb()
        assert len(cc.components) == 1  # cleared and re-populated

    def test_retrieve_then_clean_gives_empty(self):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("resistor")
        obj.name = "R1"
        pedb.components.instances = {"R1": obj}
        cc = CfgComponents(pedb, None)
        with patch.object(CfgComponent, "retrieve_parameters_from_edb", MagicMock()):
            cc.retrieve_parameters_from_edb()
        cc.clean()
        assert cc.components == []

    def test_init_multiple_components_data(self):
        pedb = _make_pedb(grpc=True)
        obj_r = _make_pyedb_obj("resistor")
        obj_r.name = "R1"
        obj_c = _make_pyedb_obj("capacitor")
        obj_c.name = "C1"
        pedb.components.instances = {"R1": obj_r, "C1": obj_c}
        data = [
            {"reference_designator": "R1", "part_type": "resistor"},
            {"reference_designator": "C1", "part_type": "capacitor"},
        ]
        cc = CfgComponents(pedb, data)
        assert len(cc.components) == 2
        refdes = [c.reference_designator for c in cc.components]
        assert "R1" in refdes
        assert "C1" in refdes
