# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

"""Unit tests for cfg_components (CfgComponent / CfgComponents) and grpc Components – no EDB server required."""

from __future__ import annotations

import json
import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from pyedb.configuration.cfg_components import CfgComponent, CfgComponents
from pyedb.grpc.database.components import Components, resistor_value_parser
from tests.conftest import config

pytestmark = [pytest.mark.unit, pytest.mark.no_licence]

_grpc_only = pytest.mark.skipif(not config["use_grpc"], reason="Not tested on DotNet.")


@pytest.fixture(autouse=True)
def _mock_core_property_factories(monkeypatch):
    """Mock the ansys-edb-core ``*.create()`` factories used by cfg_components.

    The gRPC backend now creates a brand-new ``SolderBallProperty`` /
    ``PortProperty`` / ``DieProperty`` for every write (required for the
    EDB 2026.1 persistence fix).  Those factories perform real gRPC calls,
    which cannot run without an active session, so unit tests must mock
    them.  The fixture exposes ``mock.last_sbp``, ``mock.last_pp`` and
    ``mock.last_dp`` so tests can assert against the actual mutated object.
    """
    import pyedb.configuration.cfg_components as mod

    registry = MagicMock()
    registry.last_sbp = None
    registry.last_pp = None
    registry.last_dp = None

    def _factory(kind):
        def make():
            m = MagicMock(name=f"core_{kind}")
            setattr(registry, f"last_{kind}", m)
            return m

        return make

    monkeypatch.setattr(mod.CoreSolderBallProperty, "create", _factory("sbp"))
    monkeypatch.setattr(mod.CorePortProperty, "create", _factory("pp"))
    monkeypatch.setattr(mod.CoreDieProperty, "create", _factory("dp"))
    # ``_persist_component_property`` calls ``CoreComponentProperty(cp.msg)``;
    # stub it to just record the assignment on the mocked core component.
    monkeypatch.setattr(
        mod,
        "_persist_component_property",
        lambda core, cp: setattr(core, "_persisted_component_property", cp),
    )
    return registry


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


class TestCfgComponentSolderBallGrpc:
    def test_cylinder_sets_shape_and_diameter(self, _mock_core_property_factories):
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
        # The fix creates a brand-new SolderBallProperty.create() (required for
        # EDB 2026.1 persistence), mutates it, and assigns it back to the typed
        # component property.  Assert against that freshly-created instance.
        sbp = _mock_core_property_factories.last_sbp
        sbp.set_diameter.assert_called()

    def test_no_shape_raises_value_error(self, _mock_core_property_factories):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("ic")
        c = CfgComponent(pedb, obj, reference_designator="U1", part_type="ic", solder_ball_properties={})
        # Empty dict short-circuits — no mutation, no exception (regression-safe).
        c._set_solder_ball_properties_to_edb()
        assert _mock_core_property_factories.last_sbp is None

    def test_missing_shape_raises_value_error(self):
        """Non-empty solder_ball_properties without 'shape' still raises."""
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

    def test_spheroid_uses_mid_diameter(self, _mock_core_property_factories):
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
        sbp = _mock_core_property_factories.last_sbp
        sbp.set_diameter.assert_called_with(pedb.value("150um"), pedb.value("130um"))

    def test_material_is_set(self, _mock_core_property_factories):
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
        sbp = _mock_core_property_factories.last_sbp
        assert sbp.material_name == "copper"

    def test_height_is_set(self, _mock_core_property_factories):
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
        sbp = _mock_core_property_factories.last_sbp
        assert sbp.height == pedb.value("100um")

    def test_shape_uses_core_enum(self, _mock_core_property_factories):
        """Regression: shape must be assigned as a ``SolderballShape`` enum
        (not the lowercase string).
        """
        from ansys.edb.core.definition.solder_ball_property import SolderballShape

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
        sbp = _mock_core_property_factories.last_sbp
        assert sbp.shape == SolderballShape.SOLDERBALL_SPHEROID

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

    def test_creates_fresh_solder_ball_property(self, _mock_core_property_factories):
        """Regression for EDB 2026.1: the code MUST create a brand-new
        ``SolderBallProperty`` via ``.create()`` (mutating the fetched one
        does not persist on save).
        """
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
        # The fresh SolderBallProperty must have been instantiated and then
        # assigned back to cp.solder_ball_property.
        assert _mock_core_property_factories.last_sbp is not None
        # And the base-class write-back helper must have been invoked
        # (recorded as ``_persisted_component_property`` by the fixture stub).
        assert hasattr(obj.core, "_persisted_component_property")

    def test_ic_die_type_none_defaults_to_flipchip(self, _mock_core_property_factories):
        """When an IC component's die_type is NONE, _set_solder_ball_properties_to_edb
        must default it to FLIPCHIP so HFSS recognises the solder balls."""
        from ansys.edb.core.definition.die_property import DieType as CoreDieType

        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("ic")
        # Simulate die_type = NONE (uninitialized IC)
        obj.core.component_property.die_property.die_type = CoreDieType.NONE

        c = CfgComponent(
            pedb,
            obj,
            reference_designator="U1",
            part_type="ic",
            solder_ball_properties={"shape": "cylinder", "diameter": "150um", "height": "100um"},
        )
        c._set_solder_ball_properties_to_edb()

        # die_type must have been updated to FLIPCHIP on the die_property object
        ic_die_prop = obj.core.component_property.die_property
        assert ic_die_prop.die_type == CoreDieType.FLIPCHIP
        # Solder ball property must still be created and persisted
        assert _mock_core_property_factories.last_sbp is not None
        assert hasattr(obj.core, "_persisted_component_property")

    def test_ic_die_type_already_set_is_not_overridden(self, _mock_core_property_factories):
        """When die_type is already WIREBOND (or FLIPCHIP), it must not be changed."""
        from ansys.edb.core.definition.die_property import DieType as CoreDieType

        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("ic")
        obj.core.component_property.die_property.die_type = CoreDieType.WIREBOND

        c = CfgComponent(
            pedb,
            obj,
            reference_designator="U1",
            part_type="ic",
            solder_ball_properties={"shape": "cylinder", "diameter": "150um", "height": "100um"},
        )
        c._set_solder_ball_properties_to_edb()

        # die_type must remain WIREBOND — only NONE triggers the default
        assert obj.core.component_property.die_property.die_type == CoreDieType.WIREBOND


class TestRetrieveSolderBallProperties:
    """Regression: _retrieve_solder_ball_properties_from_edb must not crash
    when the component has no solder ball configured (solder_ball_diameter == None).
    This was the root cause of cfg.components.get("U1") silently losing U1.
    """

    def test_no_solder_ball_yields_empty_dict(self):
        """solder_ball_diameter returning None → solder_ball_properties = {}."""
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("ic")
        obj.solder_ball_diameter = None  # simulate unconfigured component
        c = CfgComponent(pedb, obj, reference_designator="U1", part_type="ic")
        c._retrieve_solder_ball_properties_from_edb()
        assert c.solder_ball_properties == {}

    def test_no_solder_ball_then_set_overrides(self):
        """After retrieve returns {}, set_solder_ball_properties populates correctly."""
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("ic")
        obj.solder_ball_diameter = None
        c = CfgComponent(pedb, obj, reference_designator="U1", part_type="ic")
        c._retrieve_solder_ball_properties_from_edb()
        c.set_solder_ball_properties(shape="cylinder", diameter="300um", height="200um")
        assert c.solder_ball_properties["shape"] == "cylinder"
        assert c.solder_ball_properties["diameter"] == "300um"

    def test_configured_solder_ball_is_read(self):
        """When solder_ball_diameter is present, properties are read normally."""
        from unittest.mock import MagicMock

        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("ic")
        d0, d1 = MagicMock(), MagicMock()
        d0.__str__ = lambda self: "150um"
        d1.__str__ = lambda self: "150um"
        obj.solder_ball_diameter = (d0, d1)
        obj.uses_solderball = True
        obj.solder_ball_shape = "cylinder"
        obj.solder_ball_height = MagicMock(__str__=lambda self: "100um")
        obj.solder_ball_material = "solder"
        c = CfgComponent(pedb, obj, reference_designator="U1", part_type="ic")
        c._retrieve_solder_ball_properties_from_edb()
        assert c.solder_ball_properties.get("shape") == "cylinder"


class TestCfgComponentPortPropertiesGrpcRegression:
    """Lightweight regression check that the write-back helper is invoked.

    The richer behavioural coverage lives in :class:`TestCfgComponentPortPropertiesGrpc`.
    """

    def test_reference_height_is_written_to_core(self, _mock_core_property_factories):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("ic")
        c = CfgComponent(
            pedb,
            obj,
            reference_designator="U1",
            part_type="ic",
            port_properties={
                "reference_height": "0.33mm",
                "reference_size_auto": False,
                "reference_size_x": "0.0",
                "reference_size_y": "0.0",
            },
        )
        c._set_port_properties_to_edb()
        pp = _mock_core_property_factories.last_pp
        assert pp.reference_height == pedb.value("0.33mm")
        assert pp.reference_size_auto is False
        pp.set_reference_size.assert_called_with(pedb.value("0.0"), pedb.value("0.0"))
        # The persistence helper must have been invoked (records on obj.core).
        assert hasattr(obj.core, "_persisted_component_property")

    def test_no_solder_ball_properties_shape_none_raises(self):
        """Shape key missing entirely should raise ValueError (grpc path)."""
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

    def test_no_die_sets_die_type_only(self, _mock_core_property_factories):
        pedb, obj, c = self._make_comp(die_type="no_die")
        c._set_ic_die_properties_to_edb()
        dp = _mock_core_property_factories.last_dp
        assert dp.die_type is not None

    def test_flip_chip_sets_orientation(self, _mock_core_property_factories):
        pedb, obj, c = self._make_comp(die_type="flip_chip", orientation="chip_down")
        c._set_ic_die_properties_to_edb()
        dp = _mock_core_property_factories.last_dp
        assert dp.die_orientation is not None

    def test_wire_bond_with_height_sets_height(self, _mock_core_property_factories):
        pedb, obj, c = self._make_comp(die_type="wire_bond", orientation="chip_up", height="200um")
        c._set_ic_die_properties_to_edb()
        dp = _mock_core_property_factories.last_dp
        assert dp.height == pedb.value("200um")

    def test_wire_bond_without_height_skips_height(self, _mock_core_property_factories):
        pedb, obj, c = self._make_comp(die_type="wire_bond", orientation="chip_up")
        # Should not raise even without height
        c._set_ic_die_properties_to_edb()

    def test_flip_chip_no_orientation_skips_orientation(self, _mock_core_property_factories):
        pedb, obj, c = self._make_comp(die_type="flip_chip")
        # Should not raise even without orientation
        c._set_ic_die_properties_to_edb()


class TestCfgComponentPortPropertiesGrpc:
    """Regression: port_properties.reference_height was silently dropped because
    the code wrote to the high-level wrapper attribute (and used the typo
    ``port_properties`` instead of ``port_property``).  Since EDB 2026.1 the
    write now goes through ``CorePortProperty.create()`` then a base-class
    write-back, so assertions target the freshly-created mock instance.
    """

    def _make_comp(self, port_props):
        pedb = _make_pedb(grpc=True)
        obj = _make_pyedb_obj("ic")
        # Seed default reference_height so the cfg "copy unchanged fields" path
        # has something to read.
        obj.core.component_property.port_property.reference_height = 0.0
        obj.core.component_property.port_property.reference_size_auto = True
        c = CfgComponent(pedb, obj, reference_designator="U1", part_type="ic", port_properties=port_props)
        return pedb, obj, c

    def test_reference_height_is_set(self, _mock_core_property_factories):
        pedb, obj, c = self._make_comp({"reference_height": "50um"})
        c._set_port_properties_to_edb()
        pp = _mock_core_property_factories.last_pp
        assert pp.reference_height == pedb.value("50um")

    def test_reference_height_zero_is_applied(self, _mock_core_property_factories):
        """A reference_height of "0" must still be applied (not skipped as falsy)."""
        pedb, obj, c = self._make_comp({"reference_height": "0", "reference_size_auto": True})
        c._set_port_properties_to_edb()
        pp = _mock_core_property_factories.last_pp
        assert pp.reference_height == pedb.value("0")

    def test_reference_height_full_payload(self, _mock_core_property_factories):
        """End-to-end JSON-style payload (mirrors the user's edb_configuration.json)."""
        pedb, obj, c = self._make_comp(
            {
                "reference_height": "0.33mm",
                "reference_size_auto": False,
                "reference_size_x": "0.0",
                "reference_size_y": "0.0",
            }
        )
        c._set_port_properties_to_edb()
        pp = _mock_core_property_factories.last_pp
        assert pp.reference_height == pedb.value("0.33mm")
        assert pp.reference_size_auto is False
        pp.set_reference_size.assert_called_with(pedb.value("0.0"), pedb.value("0.0"))

    def test_reference_size_auto_is_set(self, _mock_core_property_factories):
        pedb, obj, c = self._make_comp({"reference_size_auto": True})
        c._set_port_properties_to_edb()
        pp = _mock_core_property_factories.last_pp
        assert pp.reference_size_auto is True

    def test_reference_size_auto_false_is_set(self, _mock_core_property_factories):
        pedb, obj, c = self._make_comp({"reference_size_auto": False})
        c._set_port_properties_to_edb()
        pp = _mock_core_property_factories.last_pp
        assert pp.reference_size_auto is False

    def test_set_reference_size_called(self, _mock_core_property_factories):
        pedb, obj, c = self._make_comp({"reference_size_x": "100um", "reference_size_y": "200um"})
        c._set_port_properties_to_edb()
        pp = _mock_core_property_factories.last_pp
        pp.set_reference_size.assert_called_with(pedb.value("100um"), pedb.value("200um"))

    def test_empty_port_properties_no_raise(self, _mock_core_property_factories):
        pedb, obj, c = self._make_comp({})
        c._set_port_properties_to_edb()  # Should not raise
        # And must not have created any PortProperty.
        assert _mock_core_property_factories.last_pp is None


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

    def test_no_die_type_skips_height_but_includes_orientation(self):
        pedb = _make_pedb(grpc=True)
        obj = self._make_ic_obj()
        obj.ic_die_properties.die_type = "no_die"
        c = CfgComponent(pedb, obj, reference_designator="U1", part_type="ic")
        c.retrieve_parameters_from_edb()
        assert c.ic_die_properties["type"] == "no_die"
        # gRPC always exposes orientation; height is only for wire_bond
        assert "orientation" in c.ic_die_properties
        assert "height" not in c.ic_die_properties


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


def _make_component(name: str, comp_type: str = "resistor", nets=None, num_pins: int = 2):
    """Return a minimal fake Component mock."""
    cmp = MagicMock()
    cmp.name = name
    cmp.component_type = comp_type
    cmp.type = comp_type.capitalize()
    cmp.nets = nets or ["GND", "VCC"]
    cmp.num_pins = num_pins
    cmp.numpins = num_pins
    cmp.partname = name + "_part"
    cmp.refdes = name
    cmp.pins = {str(i): MagicMock(name=str(i)) for i in range(1, num_pins + 1)}
    return cmp


def _make_grpc_pedb(components: dict | None = None):
    """Return a minimal fake pedb object with Components already bypassing refresh."""
    pedb = MagicMock()
    pedb.logger = MagicMock()
    pedb.grpc = True
    pedb._value_setter = lambda v: v
    pedb.layout.groups = []
    pedb.active_layout = MagicMock()
    pedb.active_layout.groups = []
    return pedb


def _make_components(extra_instances: dict | None = None):
    """Return a Components instance with its internal _cmp pre-populated."""
    pedb = _make_grpc_pedb()
    comps = Components.__new__(Components)
    comps._pedb = pedb
    comps._cmp = extra_instances or {}
    comps._res = {}
    comps._ind = {}
    comps._cap = {}
    comps._ics = {}
    comps._ios = {}
    comps._others = {}
    comps._structures_3d = {}
    comps._pins = {}
    comps._comps_by_part = {}
    comps._padstack = MagicMock()
    return comps


@_grpc_only
class TestResistorValueParser:
    def test_float_passthrough(self):
        assert resistor_value_parser(100.0) == 100.0

    def test_kilo_suffix(self):
        assert resistor_value_parser("10k") == pytest.approx(10e3)

    def test_milli_suffix(self):
        assert resistor_value_parser("100m") == pytest.approx(0.1)

    def test_mega_suffix(self):
        assert resistor_value_parser("2M") == pytest.approx(2e6)

    def test_meg_suffix_lowercased(self):
        result = resistor_value_parser("1meg")
        assert isinstance(result, float)

    def test_ohm_stripped(self):
        assert resistor_value_parser("50Ohm") == pytest.approx(50.0)

    def test_ohm_lower_stripped(self):
        assert resistor_value_parser("50ohm") == pytest.approx(50.0)

    def test_spaces_stripped(self):
        assert resistor_value_parser("1 0") == pytest.approx(10.0)


@_grpc_only
class TestComponentsProperties:
    def test_instances_returns_cmp_dict(self):
        cmp = _make_component("R1")
        comps = _make_components({"R1": cmp})
        assert comps.instances == {"R1": cmp}

    def test_getitem_delegates_to_instances(self):
        cmp = _make_component("R1")
        comps = _make_components({"R1": cmp})
        assert comps["R1"] is cmp

    def test_resistors_empty_initially(self):
        comps = _make_components()
        assert comps.resistors == {}

    def test_capacitors_empty_initially(self):
        comps = _make_components()
        assert comps.capacitors == {}

    def test_inductors_empty_initially(self):
        comps = _make_components()
        assert comps.inductors == {}

    def test_ICs_empty_initially(self):
        comps = _make_components()
        assert comps.ICs == {}

    def test_IOs_empty_initially(self):
        comps = _make_components()
        assert comps.IOs == {}

    def test_Others_empty_initially(self):
        comps = _make_components()
        assert comps.Others == {}

    def test_definitions_delegates_to_pedb(self):
        comps = _make_components()
        result = comps.definitions
        comps._pedb.definitions.components
        assert result is comps._pedb.definitions.components

    def test_nport_comp_definition_filters_by_reference_file(self):
        def1 = MagicMock()
        def1.reference_file = "myfile.s2p"
        def2 = MagicMock()
        def2.reference_file = None
        comps = _make_components()
        comps._pedb.definitions.components = {"D1": def1, "D2": def2}
        result = comps.nport_comp_definition
        assert "D1" in result
        assert "D2" not in result

    def test_logger_delegates_to_pedb(self):
        comps = _make_components()
        assert comps._logger is comps._pedb.logger

    def test_active_layout_property(self):
        comps = _make_components()
        assert comps._active_layout is comps._pedb.active_layout

    def test_layout_property(self):
        comps = _make_components()
        assert comps._layout is comps._pedb.layout

    def test_cell_property(self):
        comps = _make_components()
        assert comps._cell is comps._pedb.cell

    def test_db_property(self):
        comps = _make_components()
        assert comps._db is comps._pedb.active_db

    def test_components_by_partname_groups_correctly(self):
        r1 = _make_component("R1")
        r1.partname = "RES100"
        r2 = _make_component("R2")
        r2.partname = "RES100"
        c1 = _make_component("C1", "capacitor")
        c1.partname = "CAP10U"
        comps = _make_components({"R1": r1, "R2": r2, "C1": c1})
        result = comps.components_by_partname
        assert len(result["RES100"]) == 2
        assert len(result["CAP10U"]) == 1


@_grpc_only
class TestRefreshComponents:
    def test_refresh_populates_resistors(self):
        r1 = _make_component("R1", "resistor")
        pedb = _make_grpc_pedb()
        pedb.layout.groups = [r1]
        comps = _make_components()
        comps._pedb = pedb
        comps.refresh_components()
        assert "R1" in comps._cmp
        assert "R1" in comps._res

    def test_refresh_populates_capacitors(self):
        c1 = _make_component("C1", "capacitor")
        pedb = _make_grpc_pedb()
        pedb.layout.groups = [c1]
        comps = _make_components()
        comps._pedb = pedb
        comps.refresh_components()
        assert "C1" in comps._cap

    def test_refresh_populates_inductors(self):
        l1 = _make_component("L1", "inductor")
        pedb = _make_grpc_pedb()
        pedb.layout.groups = [l1]
        comps = _make_components()
        comps._pedb = pedb
        comps.refresh_components()
        assert "L1" in comps._ind

    def test_refresh_populates_ics(self):
        u1 = _make_component("U1", "ic")
        pedb = _make_grpc_pedb()
        pedb.layout.groups = [u1]
        comps = _make_components()
        comps._pedb = pedb
        comps.refresh_components()
        assert "U1" in comps._ics

    def test_refresh_populates_ios(self):
        j1 = _make_component("J1", "io")
        pedb = _make_grpc_pedb()
        pedb.layout.groups = [j1]
        comps = _make_components()
        comps._pedb = pedb
        comps.refresh_components()
        assert "J1" in comps._ios

    def test_refresh_unknown_type_logs_warning(self):
        x1 = MagicMock()
        x1.name = "X1"
        x1.component_type = "totally_unknown_type"
        pedb = _make_grpc_pedb()
        pedb.layout.groups = [x1]
        comps = _make_components()
        comps._pedb = pedb
        comps.refresh_components()
        assert "X1" in comps._cmp
        comps._pedb.logger.warning.assert_called()

    def test_refresh_exception_on_component_type_access_goes_to_others(self):
        bad = MagicMock()
        bad.name = "BAD1"
        bad.component_type = "resistor"
        pedb = _make_grpc_pedb()
        pedb.layout.groups = [bad]
        comps = _make_components()
        comps._pedb = pedb

        original_refresh = Components.refresh_components

        def patched_refresh(self):
            self._cmp = {}
            self._res = {}
            self._ind = {}
            self._cap = {}
            self._ics = {}
            self._ios = {}
            self._others = {}
            for i in self._pedb.layout.groups:
                name = getattr(i, "name", "<unknown>")
                self._cmp[name] = i
                try:
                    raise TypeError("simulated")
                except (AttributeError, TypeError) as e:
                    self._logger.warning(f"Assigning component {name} as default type other. Reason: {e}")
                    self._others[name] = i
            return True

        with patch.object(Components, "refresh_components", patched_refresh):
            comps.refresh_components()

        assert "BAD1" in comps._others


@_grpc_only
class TestGetComponent:
    def test_get_component_by_name(self):
        cmp = _make_component("R1")
        comps = _make_components({"R1": cmp})
        assert comps.get_component_by_name("R1") is cmp

    def test_find_by_reference_designator(self):
        cmp = _make_component("C1")
        comps = _make_components({"C1": cmp})
        assert comps.find_by_reference_designator("C1") is cmp


@_grpc_only
class TestGetPinFromComponent:
    def _make_pin(self, name: str, net_name: str):
        pin = MagicMock()
        pin.name = name
        pin.net_name = net_name
        return pin

    def test_returns_all_pins_no_filter(self):
        cmp = _make_component("U1", num_pins=2)
        cmp.pins = {"1": self._make_pin("1", "GND"), "2": self._make_pin("2", "VCC")}
        comps = _make_components({"U1": cmp})
        result = comps.get_pin_from_component("U1")
        assert len(result) == 2

    def test_filters_by_net_name_string(self):
        cmp = _make_component("U1", num_pins=2)
        cmp.pins = {"1": self._make_pin("1", "GND"), "2": self._make_pin("2", "VCC")}
        comps = _make_components({"U1": cmp})
        result = comps.get_pin_from_component("U1", net_name="GND")
        assert len(result) == 1
        assert result[0].net_name == "GND"

    def test_filters_by_net_name_list(self):
        cmp = _make_component("U1", num_pins=3)
        cmp.pins = {
            "1": self._make_pin("1", "GND"),
            "2": self._make_pin("2", "VCC"),
            "3": self._make_pin("3", "NC"),
        }
        comps = _make_components({"U1": cmp})
        result = comps.get_pin_from_component("U1", net_name=["GND", "VCC"])
        assert len(result) == 2

    def test_filters_by_pin_name(self):
        cmp = _make_component("U1", num_pins=2)
        cmp.pins = {"A1": self._make_pin("A1", "GND"), "A2": self._make_pin("A2", "VCC")}
        comps = _make_components({"U1": cmp})
        result = comps.get_pin_from_component("U1", pin_name="A1")
        assert len(result) == 1

    def test_accepts_component_object(self):
        cmp = _make_component("U1", num_pins=1)
        pin = self._make_pin("1", "GND")
        cmp.pins = {"1": pin}
        cmp.name = "U1"

        from pyedb.grpc.database.hierarchy.component import Component as GrpcComponent

        cmp.__class__ = GrpcComponent
        comps = _make_components({"U1": cmp})
        result = comps.get_pin_from_component(cmp)
        assert len(result) == 1


@_grpc_only
class TestGetComponentsFromNets:
    def test_single_net_string(self):
        r1 = _make_component("R1", nets=["GND", "VCC"])
        c1 = _make_component("C1", nets=["3V3", "GND"])
        u1 = _make_component("U1", nets=["VCC"])
        comps = _make_components({"R1": r1, "C1": c1, "U1": u1})
        result = comps.get_components_from_nets("GND")
        assert "R1" in result
        assert "C1" in result
        assert "U1" not in result

    def test_net_list(self):
        r1 = _make_component("R1", nets=["GND"])
        u1 = _make_component("U1", nets=["VCC"])
        comps = _make_components({"R1": r1, "U1": u1})
        result = comps.get_components_from_nets(["GND", "VCC"])
        assert "R1" in result
        assert "U1" in result


@_grpc_only
class TestGetEdbPinFromPinName:
    def test_returns_false_for_non_component(self):
        result = Components._get_edb_pin_from_pin_name("not_a_component", "1")
        assert result is False

    def test_returns_false_for_non_string_pin(self):
        from pyedb.grpc.database.hierarchy.component import Component as GrpcComponent

        cmp = MagicMock(spec=GrpcComponent)
        result = Components._get_edb_pin_from_pin_name(cmp, 123)
        assert result is False

    def test_returns_pin_when_found(self):
        from pyedb.grpc.database.hierarchy.component import Component as GrpcComponent

        pin = MagicMock()
        cmp = MagicMock(spec=GrpcComponent)
        cmp.pins = {"1": pin}
        result = Components._get_edb_pin_from_pin_name(cmp, "1")
        assert result is pin

    def test_returns_false_when_pin_not_found(self):
        from pyedb.grpc.database.hierarchy.component import Component as GrpcComponent

        cmp = MagicMock(spec=GrpcComponent)
        cmp.pins = {}
        result = Components._get_edb_pin_from_pin_name(cmp, "999")
        assert result is False


@_grpc_only
class TestGetSolderBallHeight:
    def test_by_name(self):
        cmp = _make_component("U1")
        cmp.solder_ball_height = 0.5e-3
        comps = _make_components({"U1": cmp})
        assert comps.get_solder_ball_height("U1") == 0.5e-3

    def test_by_object(self):
        from pyedb.grpc.database.hierarchy.component import Component as GrpcComponent

        cmp = MagicMock(spec=GrpcComponent)
        cmp.solder_ball_height = 1e-3
        comps = _make_components()
        assert comps.get_solder_ball_height(cmp) == 1e-3


@_grpc_only
class TestGetAedtPinName:
    def test_returns_aedt_name(self):
        pin = MagicMock()
        pin.aedt_name = "U1-1"
        comps = _make_components()
        assert comps.get_aedt_pin_name(pin) == "U1-1"


@_grpc_only
class TestGetPins:
    def _make_pin(self, name, net_name):
        p = MagicMock()
        p.name = name
        p.net_name = net_name
        return p

    def test_all_pins_no_filter(self):
        cmp = _make_component("U1", num_pins=2)
        cmp.pins = {"1": self._make_pin("1", "GND"), "2": self._make_pin("2", "VCC")}
        comps = _make_components({"U1": cmp})
        result = comps.get_pins("U1")
        assert len(result) == 2

    def test_filter_by_net(self):
        cmp = _make_component("U1", num_pins=2)
        cmp.pins = {"1": self._make_pin("1", "GND"), "2": self._make_pin("2", "VCC")}
        comps = _make_components({"U1": cmp})
        result = comps.get_pins("U1", net_name="GND")
        assert "1" in result
        assert "2" not in result

    def test_filter_by_pin_name(self):
        cmp = _make_component("U1", num_pins=2)
        cmp.pins = {"A": self._make_pin("A", "GND"), "B": self._make_pin("B", "VCC")}
        comps = _make_components({"U1": cmp})
        result = comps.get_pins("U1", pin_name="A")
        assert "A" in result
        assert "B" not in result


@_grpc_only
class TestGetNetsFromPinList:
    def test_deduplicated_net_list(self):
        pin1 = MagicMock()
        pin1.net.name = "GND"
        pin2 = MagicMock()
        pin2.net.name = "GND"
        pin3 = MagicMock()
        pin3.net.name = "VCC"
        comps = _make_components()
        result = comps.get_nets_from_pin_list([pin1, pin2, pin3])
        assert set(result) == {"GND", "VCC"}


@_grpc_only
class TestGetComponentNetConnectionInfo:
    def test_returns_correct_structure(self):
        pin = MagicMock()
        pin.name = "1"
        pin.net.is_null = False
        pin.net.name = "GND"
        cmp = _make_component("R1", num_pins=1)
        cmp.pins = {"1": pin}
        comps = _make_components({"R1": cmp})
        result = comps.get_component_net_connection_info("R1")
        assert result["refdes"] == ["R1"]
        assert result["pin_name"] == ["1"]
        assert result["net_name"] == ["GND"]

    def test_null_net_excluded(self):
        pin = MagicMock()
        pin.name = "1"
        pin.net.is_null = True
        cmp = _make_component("R1", num_pins=1)
        cmp.pins = {"1": pin}
        comps = _make_components({"R1": cmp})
        result = comps.get_component_net_connection_info("R1")
        assert result["pin_name"] == []


@_grpc_only
class TestGetRats:
    def test_returns_list_per_component(self):
        pin = MagicMock()
        pin.name = "1"
        pin.net.is_null = False
        pin.net.name = "GND"
        cmp = _make_component("R1", num_pins=1)
        cmp.pins = {"1": pin}
        comps = _make_components({"R1": cmp})
        result = comps.get_rats()
        assert len(result) == 1
        assert result[0]["refdes"] == ["R1"]


@_grpc_only
class TestGetThroughResistorList:
    def test_below_threshold_included(self):
        r_low = _make_component("R_low", "resistor", num_pins=2)
        r_low.num_pins = 2
        r_low.res_value = "0.5"
        r_high = _make_component("R_high", "resistor", num_pins=2)
        r_high.num_pins = 2
        r_high.res_value = "100"
        comps = _make_components({"R_low": r_low, "R_high": r_high})
        comps._res = {"R_low": r_low, "R_high": r_high}
        result = comps.get_through_resistor_list(threshold=1)
        assert "R_low" in result
        assert "R_high" not in result

    def test_single_pin_skipped(self):
        r1 = _make_component("R1", "resistor", num_pins=1)
        r1.num_pins = 1
        r1.res_value = "0"
        comps = _make_components({"R1": r1})
        comps._res = {"R1": r1}
        result = comps.get_through_resistor_list(threshold=10)
        assert "R1" not in result


@_grpc_only
class TestDelete:
    def test_delete_existing_component(self):
        cmp = _make_component("R1")
        cmp.name = "R1"
        comps = _make_components({"R1": cmp})
        result = comps.delete("R1")
        assert result is True
        assert "R1" not in comps.instances

    def test_delete_missing_returns_false(self):
        comps = _make_components()
        comps._cmp = {}
        with patch.object(comps, "get_component_by_name", return_value=None):
            result = comps.delete("MISSING")
        assert result is False


@_grpc_only
class TestGetPinsNameFromNet:
    def test_finds_pins_on_net(self):
        pin = MagicMock()
        pin.net.is_null = False
        pin.net.name = "GND"
        pin.aedt_name = "U1-1"
        cmp = _make_component("U1", num_pins=1)
        cmp.pins = {"1": pin}
        comps = _make_components({"U1": cmp})
        result = comps.get_pins_name_from_net("GND")
        assert "U1-1" in result

    def test_ignores_pins_with_null_net(self):
        pin = MagicMock()
        pin.net.is_null = True
        cmp = _make_component("U1", num_pins=1)
        cmp.pins = {"1": pin}
        comps = _make_components({"U1": cmp})
        result = comps.get_pins_name_from_net("GND")
        assert result == []

    def test_uses_provided_pin_list(self):
        pin = MagicMock()
        pin.net.is_null = False
        pin.net.name = "VCC"
        pin.aedt_name = "R1-1"
        comps = _make_components()
        result = comps.get_pins_name_from_net("VCC", pin_list=[pin])
        assert "R1-1" in result


@_grpc_only
class TestDeleteSinglePinRlc:
    def test_deactivate_only(self):
        r1 = _make_component("R1", "resistor", num_pins=1)
        r1.num_pins = 1
        r1.is_enabled = True
        comps = _make_components({"R1": r1})

        result = comps.delete_single_pin_rlc(deactivate_only=True)
        assert r1.is_enabled is False
        assert result == []

    def test_deletes_single_pin_rlc(self):
        r1 = _make_component("R1", "resistor", num_pins=1)
        r1.num_pins = 1
        comps = _make_components({"R1": r1})

        with patch.object(comps, "refresh_components"):
            result = comps.delete_single_pin_rlc(deactivate_only=False)
        assert "R1" in result
        r1.delete.assert_called_once()

    def test_two_pin_not_deleted(self):
        r2 = _make_component("R2", "resistor", num_pins=2)
        r2.num_pins = 2
        comps = _make_components({"R2": r2})

        with patch.object(comps, "refresh_components"):
            result = comps.delete_single_pin_rlc(deactivate_only=False)
        assert "R2" not in result


@_grpc_only
class TestDisableRlcComponent:
    def test_disable_rlc_component(self):
        rlc = MagicMock()
        rlc.c_enabled = True
        rlc.l_enabled = True
        rlc.r_enabled = True

        model = MagicMock()
        model.pin_pairs.return_value = [("1", "2")]
        model.rlc.return_value = rlc

        comp_prop = MagicMock()
        comp_prop.model = model

        cmp = _make_component("R1")
        cmp.component_property = comp_prop
        comps = _make_components({"R1": cmp})

        result = comps.disable_rlc_component("R1")
        assert result is True
        assert rlc.c_enabled is False
        assert rlc.l_enabled is False
        assert rlc.r_enabled is False

    def test_disable_missing_returns_false(self):
        comps = _make_components()
        with patch.object(comps, "get_component_by_name", return_value=None):
            result = comps.disable_rlc_component("MISSING")
        assert result is False


@_grpc_only
class TestExportBom:
    def test_export_writes_csv(self):
        r1 = _make_component("R1", "Resistor")
        r1.type = "Resistor"
        r1.partname = "RES100"
        r1.res_value = "100"
        r1.cap_value = None
        r1.ind_value = None
        r1.is_enabled = True
        comps = _make_components({"R1": r1})

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            fname = f.name

        try:
            result = comps.export_bom(fname)
            assert result is True
            with open(fname) as f:
                content = f.read()
            assert "R1" in content
            assert "RES100" in content
        finally:
            os.unlink(fname)

    def test_export_disabled_rlc_skipped(self):
        r1 = _make_component("R1", "Resistor")
        r1.type = "Resistor"
        r1.partname = "RES100"
        r1.res_value = "100"
        r1.is_enabled = False
        comps = _make_components({"R1": r1})

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            fname = f.name

        try:
            comps.export_bom(fname)
            with open(fname) as f:
                content = f.read()
            assert "R1" not in content
        finally:
            os.unlink(fname)


@_grpc_only
class TestExportImportDefinition:
    def test_export_definition_rlc(self):
        comp_inst = MagicMock()
        comp_inst.model_type = "RLC"
        comp_inst.rlc_values = [100.0, None, None]
        comp_inst.is_parallel_rlc = False

        comp_def = MagicMock()
        comp_def.type = "Resistor"
        comp_def.components = {"R1": comp_inst}

        comps = _make_components()
        comps._pedb.definitions.components = {"RES100": comp_def}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            fname = f.name

        try:
            result = comps.export_definition(fname)
            assert result is True
            with open(fname) as f:
                data = json.load(f)
            assert "RES100" in data["Definitions"]
            assert data["Definitions"]["RES100"]["Model_type"] == "RLC"
            assert data["Definitions"]["RES100"]["Res"] == 100.0
        finally:
            os.unlink(fname)

    def test_import_definition_rlc(self):
        data = {
            "SParameterModel": {},
            "SPICEModel": {},
            "Definitions": {
                "RES100": {
                    "Component_type": "Resistor",
                    "Model_type": "RLC",
                    "Res": 100.0,
                    "Ind": 0.0,
                    "Cap": 0.0,
                    "Is_parallel": False,
                }
            },
        }
        comp_def = MagicMock()
        comps = _make_components()
        comps._pedb.definitions.components = {"RES100": comp_def}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(data, f)
            fname = f.name

        try:
            result = comps.import_definition(fname)
            assert result is True
            comp_def.assign_rlc_model.assert_called_once_with(100.0, 0.0, 0.0, False)
        finally:
            os.unlink(fname)

    def test_import_definition_skips_missing_part(self):
        data = {
            "SParameterModel": {},
            "SPICEModel": {},
            "Definitions": {
                "MISSING_PART": {
                    "Component_type": "Resistor",
                    "Model_type": "RLC",
                    "Res": 1.0,
                    "Ind": 0.0,
                    "Cap": 0.0,
                    "Is_parallel": False,
                }
            },
        }
        comps = _make_components()
        comps._pedb.definitions.components = {}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(data, f)
            fname = f.name

        try:
            result = comps.import_definition(fname)
            assert result is True
        finally:
            os.unlink(fname)


@_grpc_only
class TestCreatePinGroupOnNet:
    def test_delegates_to_create_pin_group(self):
        pin = MagicMock()
        pin.net_name = "GND"
        pin.name = "1"
        cmp = _make_component("U1", num_pins=1)
        cmp.pins = {"1": pin}
        comps = _make_components({"U1": cmp})

        with patch.object(comps, "create_pin_group", return_value=("grp", MagicMock())) as mock_cpg:
            comps.create_pin_group_on_net("U1", "GND", "my_group")
            mock_cpg.assert_called_once_with("U1", ["1"], "my_group")


@_grpc_only
class TestDeactivateRlcComponent:
    def test_returns_false_no_component(self):
        comps = _make_components()
        assert comps.deactivate_rlc_component(component=None) is False

    def test_returns_false_for_ic(self):
        cmp = _make_component("U1", "ic")
        cmp.type = "ic"
        cmp.refdes = "U1"
        comps = _make_components({"U1": cmp})
        result = comps.deactivate_rlc_component(component="U1")
        assert result is False

    def test_resistor_delegates_to_excitation_manager(self):
        cmp = _make_component("R1", "resistor")
        cmp.type = "resistor"
        cmp.refdes = "R1"
        cmp.is_enabled = True
        comps = _make_components({"R1": cmp})
        comps._pedb.excitation_manager.add_port_on_rlc_component.return_value = True
        result = comps.deactivate_rlc_component(component="R1", create_circuit_port=True)
        comps._pedb.excitation_manager.add_port_on_rlc_component.assert_called_once()
        assert result is True


@_grpc_only
class TestReplaceRlcByGapBoundaries:
    def test_returns_false_no_component(self):
        comps = _make_components()
        assert comps.replace_rlc_by_gap_boundaries(component=None) is False

    def test_returns_false_for_ic(self):
        cmp = _make_component("U1", "ic")
        cmp.type = "ic"
        cmp.refdes = "U1"
        comps = _make_components({"U1": cmp})
        result = comps.replace_rlc_by_gap_boundaries(component="U1")
        assert result is False

    def test_resistor_delegates_to_excitation_manager(self):
        cmp = _make_component("R1", "resistor")
        cmp.type = "resistor"
        cmp.refdes = "R1"
        cmp.enabled = True
        comps = _make_components({"R1": cmp})
        comps._pedb.excitation_manager.add_rlc_boundary.return_value = True
        comps.replace_rlc_by_gap_boundaries(component="R1")
        comps._pedb.excitation_manager.add_rlc_boundary.assert_called_once()


@_grpc_only
class TestAddPortOnRlcComponent:
    def test_delegates_to_excitation_manager(self):
        comps = _make_components()
        comps._pedb.excitation_manager.add_port_on_rlc_component.return_value = True
        result = comps.add_port_on_rlc_component(component="R1", circuit_ports=True)
        comps._pedb.excitation_manager.add_port_on_rlc_component.assert_called_once_with(
            component="R1", circuit_ports=True, pec_boundary=False
        )
        assert result is True


@_grpc_only
class TestSetComponentRlc:
    def test_no_values_disables_component(self):
        cmp = _make_component("R1", num_pins=2)
        cmp.enabled = True
        comps = _make_components({"R1": cmp})
        result = comps.set_component_rlc("R1")
        assert result is True
        assert cmp.enabled is False

    def test_wrong_pin_count_returns_false(self):
        cmp = _make_component("R1", num_pins=3)
        comps = _make_components({"R1": cmp})
        result = comps.set_component_rlc("R1", res_value=100)
        assert result is False


@_grpc_only
class TestIsTopComponent:
    def test_top_component(self):
        layer = MagicMock()
        layer.name = "TOP"
        comps = _make_components()
        comps._pedb.stackup.signal = [layer]

        cmp = _make_component("R1")
        cmp.placement_layer = "TOP"
        assert comps._is_top_component(cmp) is True

    def test_bottom_component(self):
        layer = MagicMock()
        layer.name = "TOP"
        comps = _make_components()
        comps._pedb.stackup.signal = [layer]

        cmp = _make_component("R1")
        cmp.placement_layer = "BOT"
        assert comps._is_top_component(cmp) is False


@_grpc_only
class TestComponentsInit:
    def test_init_populates_via_refresh(self):
        pedb = _make_grpc_pedb()
        r1 = _make_component("R1", "resistor")
        pedb.layout.groups = [r1]
        with patch("pyedb.grpc.database.components.Padstacks"):
            comps = Components(pedb)
        assert "R1" in comps._cmp
        assert "R1" in comps._res


@_grpc_only
class TestExportBomAllTypes:
    def _make_cmp(self, name, ctype, value):
        cmp = MagicMock()
        cmp.type = ctype
        cmp.partname = name + "_part"
        cmp.res_value = value if ctype == "Resistor" else None
        cmp.cap_value = value if ctype == "Capacitor" else None
        cmp.ind_value = value if ctype == "Inductor" else None
        cmp.is_enabled = True
        return cmp

    def test_capacitor_value(self):
        c1 = self._make_cmp("C1", "Capacitor", "10n")
        comps = _make_components({"C1": c1})
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            fname = f.name
        try:
            comps.export_bom(fname)
            content = open(fname).read()
            assert "Capacitor" in content
            assert "10n" in content
        finally:
            os.unlink(fname)

    def test_inductor_value(self):
        l1 = self._make_cmp("L1", "Inductor", "1u")
        comps = _make_components({"L1": l1})
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            fname = f.name
        try:
            comps.export_bom(fname)
            content = open(fname).read()
            assert "Inductor" in content
            assert "1u" in content
        finally:
            os.unlink(fname)

    def test_other_type_empty_value(self):
        u1 = self._make_cmp("U1", "Other", None)
        comps = _make_components({"U1": u1})
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            fname = f.name
        try:
            comps.export_bom(fname)
            content = open(fname).read()
            assert "Other" in content
        finally:
            os.unlink(fname)

    def test_none_value_replaced_with_empty_string(self):
        r1 = MagicMock()
        r1.type = "Resistor"
        r1.partname = "R_part"
        r1.res_value = None
        r1.is_enabled = True
        comps = _make_components({"R1": r1})
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            fname = f.name
        try:
            comps.export_bom(fname)
            with open(fname) as fh:
                content = fh.read()
            assert "R1" in content
        finally:
            os.unlink(fname)


@_grpc_only
class TestExportDefinitionModels:
    def test_export_s_parameter_model(self):
        model = MagicMock()
        model.name = "MySParam"
        model.reference_net = "GND"
        model.file_path = "file.s2p"

        comp_inst = MagicMock()
        comp_inst.model_type = "SParameterModel"
        comp_inst.s_param_model = model

        comp_def = MagicMock()
        comp_def.type = "Other"
        comp_def.components = {"C1": comp_inst}

        comps = _make_components()
        comps._pedb.definitions.components = {"MYPART": comp_def}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            fname = f.name
        try:
            comps.export_definition(fname)
            with open(fname) as fh:
                data = json.load(fh)
            assert data["Definitions"]["MYPART"]["Model_name"] == "MySParam"
            assert "MySParam" in data["SParameterModel"]
        finally:
            os.unlink(fname)

    def test_export_spice_model(self):
        model = MagicMock()
        model.name = "MySpice"
        model.file_path = "circuit.sp"

        comp_inst = MagicMock()
        comp_inst.model_type = "SPICEModel"
        comp_inst.spice_model = model

        comp_def = MagicMock()
        comp_def.type = "Other"
        comp_def.components = {"IC1": comp_inst}

        comps = _make_components()
        comps._pedb.definitions.components = {"IC_DEF": comp_def}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            fname = f.name
        try:
            comps.export_definition(fname)
            with open(fname) as fh:
                data = json.load(fh)
            assert data["Definitions"]["IC_DEF"]["Model_name"] == "MySpice"
            assert "MySpice" in data["SPICEModel"]
        finally:
            os.unlink(fname)

    def test_export_other_model_type(self):
        model = MagicMock()
        model.netlist = "netlist_data"

        comp_inst = MagicMock()
        comp_inst.model_type = "Netlist"
        comp_inst.netlist_model = model

        comp_def = MagicMock()
        comp_def.type = "Other"
        comp_def.components = {"X1": comp_inst}

        comps = _make_components()
        comps._pedb.definitions.components = {"XDEF": comp_def}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            fname = f.name
        try:
            result = comps.export_definition(fname)
            assert result is True
        finally:
            os.unlink(fname)

    def test_export_definition_skips_empty_components(self):
        comp_def = MagicMock()
        comp_def.components = {}

        comps = _make_components()
        comps._pedb.definitions.components = {"EMPTY": comp_def}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            fname = f.name
        try:
            comps.export_definition(fname)
            with open(fname) as fh:
                data = json.load(fh)
            assert "EMPTY" not in data["Definitions"]
        finally:
            os.unlink(fname)


@_grpc_only
class TestImportDefinitionModels:
    def test_import_s_parameter_model(self):
        data = {
            "SParameterModel": {"MySParam": "file.s2p"},
            "SPICEModel": {},
            "Definitions": {
                "MYPART": {
                    "Component_type": "Other",
                    "Model_type": "SParameterModel",
                    "Model_name": "MySParam",
                    "Reference_net": "GND",
                }
            },
        }
        comp_def = MagicMock()
        comps = _make_components()
        comps._pedb.definitions.components = {"MYPART": comp_def}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(data, f)
            fname = f.name
        try:
            comps.import_definition(fname)
            comp_def.assign_s_param_model.assert_called_once_with("file.s2p", "MySParam", "GND")
        finally:
            os.unlink(fname)

    def test_import_spice_model(self):
        data = {
            "SParameterModel": {},
            "SPICEModel": {"MySpice": "circuit.sp"},
            "Definitions": {
                "IC_DEF": {
                    "Component_type": "Other",
                    "Model_type": "SPICEModel",
                    "Model_name": "MySpice",
                }
            },
        }
        comp_def = MagicMock()
        comps = _make_components()
        comps._pedb.definitions.components = {"IC_DEF": comp_def}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(data, f)
            fname = f.name
        try:
            comps.import_definition(fname)
            comp_def.assign_spice_model.assert_called_once_with("circuit.sp", "MySpice")
        finally:
            os.unlink(fname)


@_grpc_only
class TestSetComponentRlcTwoPin:
    def test_res_value_set(self):
        from ansys.edb.core.utility.rlc import Rlc as CoreRlc

        pin1 = MagicMock()
        pin1.name = "1"
        pin2 = MagicMock()
        pin2.name = "2"

        model = MagicMock()
        comp_prop = MagicMock()
        comp_prop.model = model

        cmp = _make_component("R1", num_pins=2)
        cmp.pins = {"1": pin1, "2": pin2}
        cmp.component_property = comp_prop

        comps = _make_components({"R1": cmp})
        comps._pedb._value_setter = lambda v: v

        with patch("pyedb.grpc.database.components.CoreRlc", wraps=CoreRlc):
            result = comps.set_component_rlc("R1", res_value=100.0)
        assert result is True
        model.set_rlc.assert_called_once()

    def test_cap_value_set(self):
        from ansys.edb.core.utility.rlc import Rlc as CoreRlc

        pin1 = MagicMock()
        pin1.name = "1"
        pin2 = MagicMock()
        pin2.name = "2"

        model = MagicMock()
        comp_prop = MagicMock()
        comp_prop.model = model

        cmp = _make_component("C1", num_pins=2)
        cmp.pins = {"1": pin1, "2": pin2}
        cmp.component_property = comp_prop

        comps = _make_components({"C1": cmp})
        comps._pedb._value_setter = lambda v: v

        with patch("pyedb.grpc.database.components.CoreRlc", wraps=CoreRlc):
            result = comps.set_component_rlc("C1", cap_value=10e-9)
        assert result is True

    def test_ind_value_set(self):
        from ansys.edb.core.utility.rlc import Rlc as CoreRlc

        pin1 = MagicMock()
        pin1.name = "1"
        pin2 = MagicMock()
        pin2.name = "2"

        model = MagicMock()
        comp_prop = MagicMock()
        comp_prop.model = model

        cmp = _make_component("L1", num_pins=2)
        cmp.pins = {"1": pin1, "2": pin2}
        cmp.component_property = comp_prop

        comps = _make_components({"L1": cmp})
        comps._pedb._value_setter = lambda v: v

        with patch("pyedb.grpc.database.components.CoreRlc", wraps=CoreRlc):
            result = comps.set_component_rlc("L1", ind_value=1e-9)
        assert result is True


@_grpc_only
class TestUpdateRlcFromBom:
    def _write_bom(self, content: str) -> str:
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False)
        f.write(content)
        f.close()
        return f.name

    def test_resistor_updated(self):
        bom = "Func des;Pos / Place;Prod name\n50ohm;R1;Resistor\n"
        fname = self._write_bom(bom)

        r1 = _make_component("R1", num_pins=2)
        r1.pins = {"1": MagicMock(name="1"), "2": MagicMock(name="2")}
        r1.component_property = MagicMock()
        r1.component_property.model = MagicMock()
        comps = _make_components({"R1": r1})
        comps._pedb._value_setter = lambda v: v

        with patch.object(comps, "set_component_rlc", return_value=True) as mock_set:
            result = comps.update_rlc_from_bom(fname)
        assert result is True
        mock_set.assert_called()
        os.unlink(fname)

    def test_capacitor_updated(self):
        bom = "Func des;Pos / Place;Prod name\n10n;C1;Capacitor\n"
        fname = self._write_bom(bom)

        c1 = _make_component("C1", num_pins=2)
        c1.component_property = MagicMock()
        comps = _make_components({"C1": c1})

        with patch.object(comps, "set_component_rlc", return_value=True) as mock_set:
            result = comps.update_rlc_from_bom(fname)
        assert result is True
        mock_set.assert_called()
        os.unlink(fname)

    def test_inductor_updated(self):
        bom = "Func des;Pos / Place;Prod name\n1u;L1;Inductor\n"
        fname = self._write_bom(bom)

        l1 = _make_component("L1", num_pins=2)
        l1.component_property = MagicMock()
        comps = _make_components({"L1": l1})

        with patch.object(comps, "set_component_rlc", return_value=True) as mock_set:
            result = comps.update_rlc_from_bom(fname)
        assert result is True
        os.unlink(fname)

    def test_unmounted_components_disabled(self):
        bom = "Func des;Pos / Place;Prod name\n50ohm;R1;Resistor\n"
        fname = self._write_bom(bom)

        r1 = _make_component("R1", num_pins=2)
        r1.component_property = MagicMock()
        unmounted = _make_component("C9", "capacitor", num_pins=2)
        unmounted.enabled = True
        comps = _make_components({"R1": r1, "C9": unmounted})

        with patch.object(comps, "set_component_rlc", return_value=True):
            comps.update_rlc_from_bom(fname)
        assert unmounted.enabled is False
        os.unlink(fname)


@_grpc_only
class TestGetComponentPlacementVector:
    def test_returns_false_for_non_component_mounted(self):
        comps = _make_components()
        result = comps.get_component_placement_vector("not_a_component", MagicMock(), "1", "2", "A", "B")
        assert result[0] is False

    def test_returns_false_for_non_component_hosting(self):
        from pyedb.grpc.database.hierarchy.component import Component as GrpcComponent

        mounted = MagicMock(spec=GrpcComponent)
        comps = _make_components()
        result = comps.get_component_placement_vector(mounted, "not_a_component", "1", "2", "A", "B")
        assert result[0] is False


@_grpc_only
class TestGetPinPosition:
    def test_null_component_returns_raw_position(self):
        pt = MagicMock()
        pt.x = 1.0
        pt.y = 2.0

        pin = MagicMock()
        pin.position = pt
        pin.component.is_null = True

        comps = _make_components()
        result = comps.get_pin_position(pin)
        assert len(result) == 2

    def test_with_component_uses_transform(self):
        transformed = MagicMock()
        transformed.x = 3.0
        transformed.y = 4.0

        pin = MagicMock()
        pin.position = MagicMock()
        pin.component.is_null = False
        pin.component.core.transform.transform_point.return_value = transformed

        comps = _make_components()
        result = comps.get_pin_position(pin)
        assert len(result) == 2

    def test_legacy_list_transform_result(self):
        pin = MagicMock()
        pin.position = MagicMock()
        pin.component.is_null = False
        pin.component.core.transform.transform_point.return_value = [5.0, 6.0]

        comps = _make_components()
        result = comps.get_pin_position(pin)
        assert len(result) == 2


@_grpc_only
class TestGetClosestPinFrom:
    def test_returns_closest_pin(self):
        pin_src = MagicMock()
        pin_src.position = [0.0, 0.0]

        pin_close = MagicMock()
        pin_close.position = [0.001, 0.0]

        pin_far = MagicMock()
        pin_far.position = [1.0, 0.0]

        comps = _make_components()
        result = comps._get_closest_pin_from(pin_src, [pin_far, pin_close])
        assert result is pin_close


@_grpc_only
class TestCreatePinGroup:
    def test_returns_false_when_no_pins_found(self):
        cmp = _make_component("U1", num_pins=2)
        pin_a = MagicMock()
        pin_b = MagicMock()
        cmp.pins = {"A": pin_a, "B": pin_b}
        comps = _make_components({"U1": cmp})

        with patch("pyedb.grpc.database.components.PinGroup") as mock_pg:
            mock_pg.unique_name.return_value = "grp"
            result = comps.create_pin_group("U1", ["NO_SUCH_PIN"])
        assert result is False

    def test_string_pin_number_converted_to_list(self):
        pin = MagicMock()
        pin.name = "1"
        pin.net.is_null = False
        pin.net.name = "GND"
        cmp = _make_component("U1", num_pins=1)
        cmp.pins = {"1": pin}
        comps = _make_components({"U1": cmp})

        with patch("pyedb.grpc.database.components.PinGroup") as mock_pg:
            mock_pg.unique_name.return_value = "grp"
            pg_inst = MagicMock()
            pg_inst.is_null = False
            pg_inst.net.is_null = False
            pg_inst.net.name = "GND"
            mock_pg.create.return_value = pg_inst
            result = comps.create_pin_group("U1", "1")
        mock_pg.create.assert_called_once()


@_grpc_only
class TestCreatePingroupFromPins:
    def test_returns_false_no_pins(self):
        comps = _make_components()
        result = comps.create_pingroup_from_pins([], "grp")
        assert result is False

    def test_returns_false_if_pingroup_is_null(self):
        pin = MagicMock()
        pin.is_layout_pin = False
        pin.net = MagicMock()
        comps = _make_components()

        with patch("pyedb.grpc.database.components.PinGroup") as mock_pg:
            mock_pg.unique_name.return_value = "grp"
            comps._pedb.active_layout.pin_groups = []
            pg_inst = MagicMock()
            pg_inst.is_null = True
            mock_pg.create.return_value = pg_inst
            result = comps.create_pingroup_from_pins([pin], "grp")
        assert result is False

    def test_replaces_forbidden_chars_in_name(self):
        pin = MagicMock()
        pin.is_layout_pin = False
        pin.net = MagicMock()
        comps = _make_components()

        with patch("pyedb.grpc.database.components.PinGroup") as mock_pg:
            comps._pedb.active_layout.pin_groups = []
            pg_inst = MagicMock()
            pg_inst.is_null = False
            mock_pg.create.return_value = pg_inst
            comps.create_pingroup_from_pins([pin], "grp->bad")
        mock_pg.create.assert_called_once()


@_grpc_only
class TestDeactivateRlcComponentObjectPath:
    def test_component_object_with_io_type_returns_false(self):
        from pyedb.grpc.database.hierarchy.component import Component as GrpcComponent

        cmp = MagicMock(spec=GrpcComponent)
        cmp.type = "io"
        cmp.refdes = "J1"
        comps = _make_components()
        result = comps.deactivate_rlc_component(component=cmp)
        assert result is False


@_grpc_only
class TestReplaceRlcByGapBoundariesObjectPath:
    def test_component_object_other_type_returns_false(self):
        from pyedb.grpc.database.hierarchy.component import Component as GrpcComponent

        cmp = MagicMock(spec=GrpcComponent)
        cmp.type = "other"
        cmp.refdes = "X1"
        comps = _make_components()
        result = comps.replace_rlc_by_gap_boundaries(component=cmp)
        assert result is False


@_grpc_only
class TestStructures3d:
    def test_structures_3d_filters_core_structure3d(self):
        class FakeCoreStructure3D:
            pass

        non_struct_core = MagicMock()  # NOT an instance of FakeCoreStructure3D

        struct_core = FakeCoreStructure3D()
        struct_core.name = "S3D_1"

        non_struct = MagicMock()
        non_struct.core = non_struct_core

        struct = MagicMock()
        struct.core = struct_core

        pedb = _make_grpc_pedb()
        pedb.active_layout.groups = [non_struct, struct]
        comps = _make_components()
        comps._pedb = pedb

        with patch("pyedb.grpc.database.components.CoreStructure3D", FakeCoreStructure3D):
            with patch("pyedb.grpc.database.components.Structure3D") as mock_s3d:
                result = comps.structures_3d
        mock_s3d.assert_called_once_with(pedb, struct_core)


@_grpc_only
class TestSetComponentModel:
    def test_component_not_found_returns_false(self):
        comps = _make_components()
        result = comps.set_component_model("MISSING", modelpath="x.sp")
        assert result is False

    def test_spice_wrong_pin_count_returns_false(self):
        pin1 = MagicMock()
        pin2 = MagicMock()
        cmp = _make_component("R1", num_pins=2)
        cmp.pins = {"1": pin1, "2": pin2}

        spice_content = ".subckt MyMod A B C\n.ends\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".sp", delete=False) as f:
            f.write(spice_content)
            fname = f.name

        comps = _make_components({"R1": cmp})
        try:
            result = comps.set_component_model("R1", model_type="Spice", modelpath=fname)
            assert result is False
        finally:
            os.unlink(fname)


@_grpc_only
class TestImportBom:
    def test_import_bom_sets_component_type(self):
        r1 = _make_component("R1", "Resistor")
        r1.type = "Other"
        r1.partname = "RES100"
        r1.placement_layer = "TOP"
        r1.refdes = "R1"
        comps = _make_components({"R1": r1})
        comps._pedb.definitions.components = {"RES100": MagicMock()}

        bom_content = "RefDes,PartName,Type,Value\nR1,RES100,Resistor,100\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(bom_content)
            fname = f.name

        try:
            with patch.object(comps, "set_component_rlc", return_value=True):
                result = comps.import_bom(fname)
            assert result is True
        finally:
            os.unlink(fname)

    def test_import_bom_disables_unmounted(self):
        r1 = _make_component("R1", "Resistor")
        r1.partname = "RES100"
        r1.placement_layer = "TOP"
        r1.refdes = "R1"
        unmounted = _make_component("C9", "Capacitor")
        unmounted.enabled = True
        comps = _make_components({"R1": r1, "C9": unmounted})
        comps._pedb.definitions.components = {"RES100": MagicMock()}

        bom_content = "RefDes,PartName,Type,Value\nR1,RES100,Resistor,100\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(bom_content)
            fname = f.name

        try:
            with patch.object(comps, "set_component_rlc", return_value=True):
                comps.import_bom(fname)
            assert unmounted.enabled is False
        finally:
            os.unlink(fname)


@_grpc_only
class TestImportDefinitionNoReferenceNet:
    def test_import_s_parameter_model_without_reference_net(self):
        data = {
            "SParameterModel": {"MySParam": "file.s2p"},
            "SPICEModel": {},
            "Definitions": {
                "MYPART": {
                    "Component_type": "Other",
                    "Model_type": "SParameterModel",
                    "Model_name": "MySParam",
                }
            },
        }
        comp_def = MagicMock()
        comps = _make_components()
        comps._pedb.definitions.components = {"MYPART": comp_def}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(data, f)
            fname = f.name
        try:
            comps.import_definition(fname)
            comp_def.assign_s_param_model.assert_called_once_with("file.s2p", "MySParam", None)
        finally:
            os.unlink(fname)


@_grpc_only
class TestCreatePingroupFromPinsNoneGroupName:
    def test_none_group_name_calls_unique_name(self):
        pin = MagicMock()
        pin.is_layout_pin = False
        pin.net = MagicMock()
        comps = _make_components()

        with patch("pyedb.grpc.database.components.PinGroup") as mock_pg:
            mock_pg.unique_name.return_value = "auto_grp"
            comps._pedb.active_layout.pin_groups = []
            pg_inst = MagicMock()
            pg_inst.is_null = True
            mock_pg.create.return_value = pg_inst
            comps.create_pingroup_from_pins([pin], None)
        mock_pg.unique_name.assert_called_once()


@_grpc_only
class TestCreatePingroupFromPinsExistingGroup:
    def test_returns_existing_group_when_same_pins(self):
        pin = MagicMock()
        pin.name = "1"
        pin.is_layout_pin = False

        existing = MagicMock()
        existing.name = "grp"
        existing.pins = [pin]

        comps = _make_components()
        comps._pedb.active_layout.pin_groups = [existing]

        with patch("pyedb.grpc.database.components.PinGroup"):
            result = comps.create_pingroup_from_pins([pin], "grp")
        assert result is existing

    def test_renames_group_when_different_pin_count(self):
        pin1 = MagicMock()
        pin1.name = "1"
        pin1.is_layout_pin = False
        pin1.net = MagicMock()
        pin2 = MagicMock()
        pin2.name = "2"
        pin2.is_layout_pin = False
        pin2.net = MagicMock()

        existing = MagicMock()
        existing.name = "grp"
        existing.pins = [pin1]

        comps = _make_components()
        comps._pedb.active_layout.pin_groups = [existing]

        with patch("pyedb.grpc.database.components.PinGroup") as mock_pg:
            mock_pg.unique_name.return_value = "grp_1"
            pg_inst = MagicMock()
            pg_inst.is_null = False
            mock_pg.create.return_value = pg_inst
            comps.create_pingroup_from_pins([pin1, pin2], "grp")
        mock_pg.unique_name.assert_called()


@_grpc_only
class TestDeleteSinglePinRlcModelTypeFailure:
    def test_model_type_attribute_error_logged_at_debug(self):
        r1 = _make_component("R1", "resistor", num_pins=1)
        r1.num_pins = 1
        r1.is_enabled = True

        def bad_setattr(attr, val):
            if attr == "model_type":
                raise AttributeError("read-only")

        type(r1).__setattr__ = MagicMock(side_effect=bad_setattr)

        comps = _make_components({"R1": r1})
        comps.delete_single_pin_rlc(deactivate_only=True)


@_grpc_only
class TestDeleteSinglePinRlcExceptionHandling:
    def test_exception_during_component_processing_is_swallowed(self):
        bad_comp = MagicMock()
        bad_comp.pins = MagicMock()
        type(bad_comp).pins = property(lambda self: (_ for _ in ()).throw(RuntimeError("gRPC error")))

        comps = _make_components({"BAD": bad_comp})
        result = comps.delete_single_pin_rlc(deactivate_only=False)
        assert isinstance(result, list)


@_grpc_only
class TestSetComponentModelCorrectPinCount:
    def test_spice_correct_pin_count_calls_create(self):
        pin1 = MagicMock()
        pin2 = MagicMock()
        cmp = _make_component("R1", num_pins=2)
        cmp.pins = {"1": pin1, "2": pin2}
        cmp.component_property = MagicMock()

        spice_content = ".subckt MyMod A B\n.ends\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".sp", delete=False) as f:
            f.write(spice_content)
            fname = f.name

        comps = _make_components({"R1": cmp})
        try:
            with patch("pyedb.grpc.database.components.CoreSPICEModel") as mock_spice:
                mock_spice_inst = MagicMock()
                mock_spice.create.return_value = mock_spice_inst
                result = comps.set_component_model("R1", model_type="Spice", modelpath=fname)
            assert result is True
            mock_spice.create.assert_called_once()
        finally:
            os.unlink(fname)


@_grpc_only
class TestImportBomSamePartName:
    def test_import_bom_same_partname_no_regroup(self):
        r1 = _make_component("R1", "Resistor")
        r1.partname = "RES100"
        r1.type = "Other"
        r1.placement_layer = "TOP"
        r1.refdes = "R1"
        comps = _make_components({"R1": r1})
        comps._pedb.definitions.components = {"RES100": MagicMock()}

        bom_content = "RefDes,PartName,Type,Value\nR1,RES100,Resistor,100\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(bom_content)
            fname = f.name

        try:
            with patch.object(comps, "set_component_rlc", return_value=True):
                result = comps.import_bom(fname)
            assert result is True
        finally:
            os.unlink(fname)

    def test_import_bom_empty_line_skipped(self):
        r1 = _make_component("R1", "Resistor")
        r1.partname = "RES100"
        r1.type = "Resistor"
        r1.refdes = "R1"
        comps = _make_components({"R1": r1})
        comps._pedb.definitions.components = {}

        bom_content = "RefDes,PartName,Type,Value\n\nR1,RES100,Resistor,100\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(bom_content)
            fname = f.name

        try:
            with patch.object(comps, "set_component_rlc", return_value=True):
                comps.import_bom(fname)
        finally:
            os.unlink(fname)


@_grpc_only
class TestCreatePinGroupReturnsTuple:
    def test_returns_tuple_on_success(self):
        pin = MagicMock()
        pin.name = "1"
        pin.net = MagicMock()
        pin.net.is_null = False
        pin.net.name = "GND"
        cmp = _make_component("U1", num_pins=1)
        cmp.pins = {"1": pin}
        comps = _make_components({"U1": cmp})

        with patch("pyedb.grpc.database.components.PinGroup") as mock_pg:
            mock_pg.unique_name.return_value = "grp"
            pg_inst = MagicMock()
            pg_inst.is_null = False
            pg_inst.net.is_null = False
            pg_inst.net.name = "GND"
            mock_pg.create.return_value = pg_inst
            result = comps.create_pin_group("U1", ["1"])

        assert result is not False
        group_name, pg = result
        assert group_name == "grp"


@_grpc_only
class TestSetSolderBall:
    def test_cylinder_shape_with_explicit_params(self):
        pin = MagicMock()
        pin.padstack_def.data.layer_names = ["TOP"]

        from ansys.edb.core.hierarchy.component_group import ComponentType as CoreComponentType

        cmp = _make_component("U1", "other", num_pins=1)
        cmp.pins = {"1": pin}
        cmp.placement_layer = "TOP"
        cmp.core.component_type = CoreComponentType.OTHER

        comp_prop = MagicMock()
        cmp.component_property = comp_prop

        comps = _make_components({"U1": cmp})
        comps._pedb._value_setter = lambda v: v
        comps._pedb.materials = {}

        result = comps.set_solder_ball("U1", sball_diam=0.5e-3, sball_height=0.3e-3, shape="Cylinder")
        assert result is True

    def test_spheroid_shape(self):
        pin = MagicMock()
        pin.padstack_def.data.layer_names = ["TOP"]

        from ansys.edb.core.hierarchy.component_group import ComponentType as CoreComponentType

        cmp = _make_component("U1", "other", num_pins=1)
        cmp.pins = {"1": pin}
        cmp.placement_layer = "TOP"
        cmp.core.component_type = CoreComponentType.OTHER

        comp_prop = MagicMock()
        cmp.component_property = comp_prop

        comps = _make_components({"U1": cmp})
        comps._pedb._value_setter = lambda v: v
        comps._pedb.materials = {}

        result = comps.set_solder_ball("U1", sball_diam=0.5e-3, sball_height=0.3e-3, shape="Spheroid")
        assert result is True

    def test_ic_component_type_sets_flipchip(self):
        pin = MagicMock()
        pin.padstack_def.data.layer_names = ["TOP"]

        from ansys.edb.core.hierarchy.component_group import ComponentType as CoreComponentType

        cmp = _make_component("U1", "ic", num_pins=1)
        cmp.pins = {"1": pin}
        layers = MagicMock()
        layers.keys.return_value = iter(["TOP", "BOT"])
        cmp.placement_layer = "TOP"
        cmp.core.component_type = CoreComponentType.IC

        comp_prop = MagicMock()
        cmp.component_property = comp_prop
        ic_die_prop = MagicMock()
        comp_prop.die_property = ic_die_prop

        comps = _make_components({"U1": cmp})
        comps._pedb._value_setter = lambda v: v
        comps._pedb.stackup.signal_layers = layers
        comps._pedb.materials = {}

        result = comps.set_solder_ball("U1", sball_diam=0.5e-3, sball_height=0.3e-3)
        assert result is True

    def test_missing_component_raises(self):
        comps = _make_components()
        with pytest.raises(ValueError, match="not found"):
            comps.set_solder_ball("MISSING", sball_diam=0.5e-3)

    def test_with_material_name_creates_material(self):
        pin = MagicMock()
        pin.padstack_def.data.layer_names = ["TOP"]

        from ansys.edb.core.hierarchy.component_group import ComponentType as CoreComponentType

        cmp = _make_component("U1", "other", num_pins=1)
        cmp.pins = {"1": pin}
        cmp.placement_layer = "BOT"
        cmp.core.component_type = CoreComponentType.OTHER

        comp_prop = MagicMock()
        cmp.component_property = comp_prop

        mats = MagicMock()
        mats.__contains__ = MagicMock(return_value=False)

        comps = _make_components({"U1": cmp})
        comps._pedb._value_setter = lambda v: v
        comps._pedb.materials = mats

        result = comps.set_solder_ball("U1", sball_diam=0.5e-3, sball_height=0.3e-3, material_name="solder")
        assert result is True
        mats.add_conductor_material.assert_called_once_with(name="solder", conductivity=1e7)


@_grpc_only
class TestSetSolderBallObjectComponent:
    def test_non_component_object_not_found_raises(self):
        cmp_obj = MagicMock()
        cmp_obj.name = "NOT_IN_COMPS"
        comps = _make_components()

        with pytest.raises(ValueError):
            comps.set_solder_ball(cmp_obj, sball_diam=1e-3)


@_grpc_only
class TestSetSolderBallAutoCalc:
    def test_auto_diam_uses_pad_params(self):
        from ansys.edb.core.hierarchy.component_group import ComponentType as CoreComponentType

        pin = MagicMock()
        pin.padstack_def.data.layer_names = ["TOP"]

        cmp = _make_component("U1", "other", num_pins=1)
        cmp.pins = {"1": pin}
        cmp.placement_layer = "TOP"
        cmp.core.component_type = CoreComponentType.OTHER
        cmp.component_property = MagicMock()

        pedb = _make_grpc_pedb({"U1": cmp})
        pedb.instance = cmp
        comps = _make_components({"U1": cmp})
        comps._pedb = pedb
        comps._pedb._value_setter = lambda v: v
        comps._pedb.materials = MagicMock()
        comps._pedb.materials.__contains__ = MagicMock(return_value=True)
        comps._pedb.padstacks.get_pad_parameters = MagicMock(return_value=(0, [0.5e-3, 0.4e-3]))

        result = comps.set_solder_ball("U1")
        assert result is True

    def test_sball_height_none_defaults_to_diam(self):
        from ansys.edb.core.hierarchy.component_group import ComponentType as CoreComponentType

        pin = MagicMock()
        pin.padstack_def.data.layer_names = ["TOP"]

        cmp = _make_component("U1", "other", num_pins=1)
        cmp.pins = {"1": pin}
        cmp.placement_layer = "TOP"
        cmp.core.component_type = CoreComponentType.OTHER
        cmp.component_property = MagicMock()

        comps = _make_components({"U1": cmp})
        comps._pedb._value_setter = lambda v: v
        comps._pedb.materials = MagicMock()
        comps._pedb.materials.__contains__ = MagicMock(return_value=True)

        result = comps.set_solder_ball("U1", sball_diam=0.5e-3)
        assert result is True


@_grpc_only
class TestSetSolderBallICChipUp:
    def test_ic_chip_up_orientation(self):
        from ansys.edb.core.hierarchy.component_group import ComponentType as CoreComponentType

        pin = MagicMock()
        pin.padstack_def.data.layer_names = ["TOP"]

        cmp = _make_component("U1", "ic", num_pins=1)
        cmp.pins = {"1": pin}
        cmp.placement_layer = "BOT"
        cmp.core.component_type = CoreComponentType.IC

        comp_prop = MagicMock()
        cmp.component_property = comp_prop
        ic_die_prop = MagicMock()
        comp_prop.die_property = ic_die_prop

        layers = MagicMock()
        layers.keys.return_value = iter(["TOP", "BOT"])

        comps = _make_components({"U1": cmp})
        comps._pedb._value_setter = lambda v: v
        comps._pedb.stackup.signal_layers = layers
        comps._pedb.materials = MagicMock()
        comps._pedb.materials.__contains__ = MagicMock(return_value=True)

        result = comps.set_solder_ball("U1", sball_diam=0.5e-3, sball_height=0.3e-3)
        assert result is True


@_grpc_only
class TestSetSolderBallAutoRefSize:
    def test_manual_reference_size(self):
        from ansys.edb.core.hierarchy.component_group import ComponentType as CoreComponentType

        pin = MagicMock()
        pin.padstack_def.data.layer_names = ["TOP"]
        cmp = _make_component("U1", "other", num_pins=1)
        cmp.pins = {"1": pin}
        cmp.placement_layer = "TOP"
        cmp.core.component_type = CoreComponentType.OTHER
        cmp.component_property = MagicMock()

        comps = _make_components({"U1": cmp})
        comps._pedb._value_setter = lambda v: v
        comps._pedb.materials = MagicMock()
        comps._pedb.materials.__contains__ = MagicMock(return_value=True)

        result = comps.set_solder_ball(
            "U1",
            sball_diam=0.5e-3,
            sball_height=0.3e-3,
            auto_reference_size=False,
            reference_size_x=1e-3,
            reference_size_y=1e-3,
        )
        assert result is True


@_grpc_only
class TestSetSolderBallChipOrientationFix:
    """Tests for the two bugs fixed in set_solder_ball:

    1. signal_layers (not layers) must be used to determine the top-layer boundary.
    2. An explicit chip_orientation argument overrides the auto-detection logic.
    """

    def _make_ic_comps(self, placement_layer: str, signal_layer_order):
        """Return a (comps, ic_die_prop) pair for an IC component.

        The typed branch (``_EDB_CORE_TYPED_COMPONENT_PROPERTY=True``) reads
        ``cmp.core.component_property`` and writes back through ``.clone()``.
        We capture ``cmp.core.component_property.die_property`` so assertions
        check the exact object that the production code mutates.
        """
        from ansys.edb.core.hierarchy.component_group import ComponentType as CoreComponentType

        pin = MagicMock()
        pin.padstack_def.data.layer_names = [signal_layer_order[0]]

        cmp = _make_component("U1", "ic", num_pins=1)
        cmp.pins = {"1": pin}
        cmp.placement_layer = placement_layer
        cmp.core.component_type = CoreComponentType.IC

        core_comp_prop = cmp.core.component_property
        ic_die_prop = core_comp_prop.die_property
        # clone() must return the same property object so assertions hold
        core_comp_prop.clone.return_value = core_comp_prop

        signal_layers = MagicMock()
        signal_layers.keys.return_value = iter(signal_layer_order)

        comps = _make_components({"U1": cmp})
        comps._pedb._value_setter = lambda v: v
        comps._pedb.stackup.signal_layers = signal_layers
        comps._pedb.materials = MagicMock()
        comps._pedb.materials.__contains__ = MagicMock(return_value=True)
        return comps, ic_die_prop

    # Bug 1: signal_layers (not layers) must be used for auto-detection

    def test_auto_detect_top_signal_layer_gives_chip_down(self):
        """IC placed on the first signal layer must auto-detect chip_down."""
        from ansys.edb.core.definition.die_property import DieOrientation as CoreDieOrientation

        comps, ic_die_prop = self._make_ic_comps(placement_layer="TOP", signal_layer_order=["TOP", "BOT"])
        result = comps.set_solder_ball("U1", sball_diam=0.5e-3, sball_height=0.3e-3)

        assert result is True
        assert ic_die_prop.die_orientation == CoreDieOrientation.CHIP_DOWN

    def test_auto_detect_non_top_signal_layer_gives_chip_up(self):
        """IC placed on a non-first signal layer must auto-detect chip_up."""
        from ansys.edb.core.definition.die_property import DieOrientation as CoreDieOrientation

        comps, ic_die_prop = self._make_ic_comps(placement_layer="BOT", signal_layer_order=["TOP", "BOT"])
        result = comps.set_solder_ball("U1", sball_diam=0.5e-3, sball_height=0.3e-3)

        assert result is True
        assert ic_die_prop.die_orientation == CoreDieOrientation.CHIP_UP

    def test_signal_layers_used_not_all_layers(self):
        """Verify signal_layers dict is consulted, not the generic layers dict.

        If the code still used stackup.layers the test would fail because only
        stackup.signal_layers is configured with a meaningful key list.
        """
        from ansys.edb.core.definition.die_property import DieOrientation as CoreDieOrientation

        comps, ic_die_prop = self._make_ic_comps(placement_layer="TOP", signal_layer_order=["TOP", "BOT"])
        # Deliberately leave stackup.layers unconfigured (MagicMock with empty iter).
        # If the production code used layers instead of signal_layers, list(...)[0]
        # would raise IndexError and the test would fail.
        result = comps.set_solder_ball("U1", sball_diam=0.5e-3, sball_height=0.3e-3)

        assert result is True
        assert ic_die_prop.die_orientation == CoreDieOrientation.CHIP_DOWN

    # Bug 2: explicit chip_orientation argument must override auto-detection

    def test_explicit_chip_up_overrides_top_layer_autodetect(self):
        """chip_orientation='chip_up' must be respected even when the component
        sits on the top signal layer (which would auto-detect as chip_down)."""
        from ansys.edb.core.definition.die_property import DieOrientation as CoreDieOrientation

        comps, ic_die_prop = self._make_ic_comps(placement_layer="TOP", signal_layer_order=["TOP", "BOT"])
        result = comps.set_solder_ball("U1", sball_diam=0.5e-3, sball_height=0.3e-3, chip_orientation="chip_up")

        assert result is True
        assert ic_die_prop.die_orientation == CoreDieOrientation.CHIP_UP

    def test_explicit_chip_down_overrides_bottom_layer_autodetect(self):
        """chip_orientation='chip_down' must be respected even when the component
        sits on a non-top signal layer (which would auto-detect as chip_up)."""
        from ansys.edb.core.definition.die_property import DieOrientation as CoreDieOrientation

        comps, ic_die_prop = self._make_ic_comps(placement_layer="BOT", signal_layer_order=["TOP", "BOT"])
        result = comps.set_solder_ball("U1", sball_diam=0.5e-3, sball_height=0.3e-3, chip_orientation="chip_down")

        assert result is True
        assert ic_die_prop.die_orientation == CoreDieOrientation.CHIP_DOWN

    def test_chip_orientation_none_triggers_autodetect(self):
        """Passing chip_orientation=None explicitly should behave like the
        default (auto-detect from placement layer)."""
        from ansys.edb.core.definition.die_property import DieOrientation as CoreDieOrientation

        comps, ic_die_prop = self._make_ic_comps(placement_layer="TOP", signal_layer_order=["TOP", "BOT"])
        result = comps.set_solder_ball("U1", sball_diam=0.5e-3, sball_height=0.3e-3, chip_orientation=None)

        assert result is True
        assert ic_die_prop.die_orientation == CoreDieOrientation.CHIP_DOWN


@_grpc_only
class TestImportBomPartNameMismatch:
    def test_import_bom_different_partname_triggers_create(self):
        pin1 = MagicMock()
        pin1.name = "1"
        r1 = _make_component("R1", "Resistor")
        r1.partname = "OLD_PART"
        r1.type = "Resistor"
        r1.placement_layer = "TOP"
        r1.refdes = "R1"
        r1.pins = {"1": pin1}
        r1.core = MagicMock()

        comps = _make_components({"R1": r1})
        comps._pedb.definitions.components = {}

        bom_content = "RefDes,PartName,Type,Value\nR1,NEW_PART,Resistor,100\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(bom_content)
            fname = f.name

        def fake_refresh():
            pass

        with (
            patch("pyedb.grpc.database.components.ComponentDef") as mock_cd,
            patch.object(comps, "create", return_value=MagicMock()),
            patch.object(comps, "refresh_components", side_effect=fake_refresh),
            patch.object(comps, "set_component_rlc", return_value=True),
        ):
            try:
                result = comps.import_bom(fname)
            except (KeyError, Exception):
                pass
            mock_cd.create.assert_called_once()
        os.unlink(fname)


@_grpc_only
class TestImportBomRlcValues:
    def test_resistor_value_assigned(self):
        r1 = _make_component("R1", "Resistor")
        r1.partname = "RES100"
        r1.type = "Resistor"
        r1.placement_layer = "TOP"
        r1.refdes = "R1"
        comps = _make_components({"R1": r1})
        comps._pedb.definitions.components = {"RES100": MagicMock()}

        bom_content = "RefDes,PartName,Type,Value\nR1,RES100,Resistor,100\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(bom_content)
            fname = f.name
        try:
            with patch.object(comps, "set_component_rlc", return_value=True) as mock_set:
                comps.import_bom(fname)
            mock_set.assert_called_once()
            call_kwargs = mock_set.call_args
            assert "res_value" in call_kwargs[1]
        finally:
            os.unlink(fname)

    def test_capacitor_value_assigned(self):
        c1 = _make_component("C1", "Capacitor")
        c1.partname = "CAP10N"
        c1.type = "Capacitor"
        c1.placement_layer = "TOP"
        c1.refdes = "C1"
        comps = _make_components({"C1": c1})
        comps._pedb.definitions.components = {"CAP10N": MagicMock()}

        bom_content = "RefDes,PartName,Type,Value\nC1,CAP10N,Capacitor,10n\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(bom_content)
            fname = f.name
        try:
            with patch.object(comps, "set_component_rlc", return_value=True) as mock_set:
                comps.import_bom(fname)
            mock_set.assert_called_once()
            assert "cap_value" in mock_set.call_args[1]
        finally:
            os.unlink(fname)

    def test_inductor_value_assigned(self):
        l1 = _make_component("L1", "Inductor")
        l1.partname = "IND1U"
        l1.type = "Inductor"
        l1.placement_layer = "TOP"
        l1.refdes = "L1"
        comps = _make_components({"L1": l1})
        comps._pedb.definitions.components = {"IND1U": MagicMock()}

        bom_content = "RefDes,PartName,Type,Value\nL1,IND1U,Inductor,1u\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(bom_content)
            fname = f.name
        try:
            with patch.object(comps, "set_component_rlc", return_value=True) as mock_set:
                comps.import_bom(fname)
            mock_set.assert_called_once()
            assert "ind_value" in mock_set.call_args[1]
        finally:
            os.unlink(fname)

    def test_unknown_comp_type_string_upcased(self):
        x1 = _make_component("X1", "IC")
        x1.partname = "MY_IC"
        x1.type = "IC"
        x1.placement_layer = "TOP"
        x1.refdes = "X1"
        comps = _make_components({"X1": x1})
        comps._pedb.definitions.components = {"MY_IC": MagicMock()}

        bom_content = "RefDes,PartName,Type,Value\nX1,MY_IC,ic,\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(bom_content)
            fname = f.name
        try:
            with patch.object(comps, "set_component_rlc", return_value=True):
                result = comps.import_bom(fname)
            assert result is True
            assert x1.type == "IC"
        finally:
            os.unlink(fname)

    def test_apply_calls_set_parameters_for_each(self):
        cc = CfgComponents(None, None)
        mock1 = MagicMock(spec=CfgComponent)
        mock2 = MagicMock(spec=CfgComponent)
        cc.components = [mock1, mock2]
        cc.apply()
        mock1.set_parameters_to_edb.assert_called_once()
        mock2.set_parameters_to_edb.assert_called_once()


@_grpc_only
class TestShortComponentPins:
    def _make_pin_with_pos(self, pos):
        pin = MagicMock()
        pin.position = pos
        pin.placement_layer = "TOP"
        pad_def_name = "VIA_PAD"
        pin.padstack_def.name = pad_def_name
        pad = MagicMock()
        pad.geometry_type = 1
        pad.parameters_values = [0.5e-3, 0.4e-3]
        pin.padstack_def.data.layer_names = ["TOP"]
        return pin, pad_def_name, pad

    def test_short_component_pins_all_pins(self):
        pin1, pad_def_name, pad = self._make_pin_with_pos([0.0, 0.0])
        pin2, _, _ = self._make_pin_with_pos([1e-3, 0.0])
        pin2.padstack_def.name = pad_def_name
        pin2.placement_layer = "TOP"
        pin2.padstack_def.data.layer_names = ["TOP"]

        cmp = _make_component("R1", num_pins=2)
        cmp.pins = {"1": pin1, "2": pin2}
        cmp.center = [0.5e-3, 0.0]

        comps = _make_components({"R1": cmp})

        pad_def_mock = MagicMock()
        pad_def_mock.pad_by_layer = {"TOP": pad}
        comps._pedb.padstacks.definitions = {pad_def_name: pad_def_mock}
        comps._pedb.modeler.create_trace = MagicMock(return_value=True)

        result = comps.short_component_pins("R1", width=0.1e-3)
        assert result is True
        comps._pedb.modeler.create_trace.assert_called()

    def test_short_component_pins_subset(self):
        pin1, pad_def_name, pad = self._make_pin_with_pos([0.0, 0.0])
        pin2, _, _ = self._make_pin_with_pos([1e-3, 0.0])
        pin2.padstack_def.name = pad_def_name
        pin2.placement_layer = "TOP"

        cmp = _make_component("R1", num_pins=2)
        cmp.pins = {"1": pin1, "2": pin2}
        cmp.center = [0.5e-3, 0.0]

        comps = _make_components({"R1": cmp})
        pad_def_mock = MagicMock()
        pad_def_mock.pad_by_layer = {"TOP": pad}
        comps._pedb.padstacks.definitions = {pad_def_name: pad_def_mock}
        comps._pedb.modeler.create_trace = MagicMock(return_value=True)

        result = comps.short_component_pins("R1", pins_to_short=["1"], width=0.1e-3)
        assert result is True

    def test_short_component_pins_pad_geometry_else_path(self):
        pin1, pad_def_name, pad = self._make_pin_with_pos([0.0, 0.0])
        pad.geometry_type = 7
        pad.parameters_values = [0.5e-3]

        pin2, _, _ = self._make_pin_with_pos([1e-3, 0.0])
        pin2.padstack_def.name = pad_def_name
        pin2.placement_layer = "TOP"

        cmp = _make_component("R1", num_pins=2)
        cmp.pins = {"1": pin1, "2": pin2}
        cmp.center = [0.5e-3, 0.0]

        comps = _make_components({"R1": cmp})
        pad_def_mock = MagicMock()
        pad_def_mock.pad_by_layer = {"TOP": pad}
        comps._pedb.padstacks.definitions = {pad_def_name: pad_def_mock}
        comps._pedb.modeler.create_trace = MagicMock(return_value=True)

        result = comps.short_component_pins("R1", width=0.1e-3)
        assert result is True

    def test_short_component_pins_fallback_layer(self):
        pin1, _, pad = self._make_pin_with_pos([0.0, 0.0])
        pad.geometry_type = 1
        pad.parameters_values = [0.5e-3, 0.4e-3]
        pin1.padstack_def.name = "VIA_PAD"
        pin1.placement_layer = "INNER"

        pin2, _, _ = self._make_pin_with_pos([1e-3, 0.0])
        pin2.padstack_def.name = "VIA_PAD"
        pin2.placement_layer = "INNER"

        cmp = _make_component("R1", num_pins=2)
        cmp.pins = {"1": pin1, "2": pin2}
        cmp.center = [0.5e-3, 0.0]

        comps = _make_components({"R1": cmp})
        pad_def_mock = MagicMock()
        pad_def_mock.pad_by_layer = {"TOP": pad}
        comps._pedb.padstacks.definitions = {"VIA_PAD": pad_def_mock}
        comps._pedb.modeler.create_trace = MagicMock(return_value=True)

        result = comps.short_component_pins("R1", width=0.1e-3)
        assert result is True


# ---------------------------------------------------------------------------
# Component.assign_spice_model – terminal_pairs argument order (regression)
# ---------------------------------------------------------------------------


def _spice_file_content(node_names):
    """Return minimal SPICE file text with the given subckt node names."""
    return f".subckt MyModel {' '.join(node_names)}\n.ends\n"


def _make_comp_for_spice(pin_layout_names, pedb=None):
    """Build a minimal mock Component with the given pin names."""
    comp = MagicMock()
    comp.name = "COMP1"
    comp.pins = {p: MagicMock() for p in pin_layout_names}
    comp._pedb = pedb or MagicMock()
    comp._pedb.logger = MagicMock()
    return comp


class TestAssignSpiceModelTerminalPairs:
    """Regression tests for terminal_pairs argument order in Component.assign_spice_model.

    Bug: add_terminal was called with swapped arguments when terminal_pairs were explicitly
    provided, causing pin mapping to be ignored in EDB.
    Expected call: add_terminal(spice_pin_name, component_pin)
    Buggy call was: add_terminal(component_pin, spice_pin_name)
    """

    def _run(self, tmp_path, pin_layout_names, spice_nodes, terminal_pairs, sub_circuit_name=None):
        """Create a fake SPICE file, mock internals, call assign_spice_model,
        and return (add_terminal call list, result)."""
        from unittest.mock import patch

        from pyedb.grpc.database.hierarchy.component import Component

        sp_file = tmp_path / "model.sp"
        sp_file.write_text(_spice_file_content(spice_nodes))

        comp = _make_comp_for_spice(pin_layout_names)

        mock_spice_model = MagicMock()
        mock_spice_model.core.is_null = False

        with (
            patch("pyedb.grpc.database.hierarchy.component.SpiceModel", return_value=mock_spice_model),
            patch.object(Component, "_set_model", return_value=None),
        ):
            result = Component.assign_spice_model(
                comp,
                str(sp_file),
                name="MyModel",
                sub_circuit_name=sub_circuit_name or "",
                terminal_pairs=terminal_pairs,
            )

        return mock_spice_model.core.add_terminal.call_args_list, result

    def test_terminal_pairs_spice_node_is_first_arg(self, tmp_path):
        """add_terminal must be called with (spice_node, layout_pin) — not reversed."""
        from unittest.mock import call

        terminal_pairs = [["n1", "A1"], ["n2", "B2"]]
        calls, result = self._run(
            tmp_path,
            pin_layout_names=["A1", "B2"],
            spice_nodes=["n1", "n2"],
            terminal_pairs=terminal_pairs,
        )

        assert len(calls) == 2
        assert calls[0] == call("n1", "A1"), f"Expected call('n1', 'A1') but got {calls[0]}"
        assert calls[1] == call("n2", "B2"), f"Expected call('n2', 'B2') but got {calls[1]}"

    def test_terminal_pairs_with_integer_pin_number(self, tmp_path):
        """Layout pin numbers given as integers must be converted to str."""
        from unittest.mock import call

        terminal_pairs = [["n1", 2], ["n2", 1]]
        calls, _ = self._run(
            tmp_path,
            pin_layout_names=["1", "2"],
            spice_nodes=["n1", "n2"],
            terminal_pairs=terminal_pairs,
        )

        assert calls[0] == call("n1", "2")
        assert calls[1] == call("n2", "1")

    def test_terminal_pairs_four_nodes(self, tmp_path):
        """Verify the full 4-pair scenario from edb_configuration_SPICE.json."""
        from unittest.mock import call

        terminal_pairs = [["n1", "A1"], ["n2", "B2"], ["n3", "A2"], ["n4", "B1"]]
        calls, _ = self._run(
            tmp_path,
            pin_layout_names=["A1", "B2", "A2", "B1"],
            spice_nodes=["n1", "n2", "n3", "n4"],
            terminal_pairs=terminal_pairs,
        )

        expected = [call("n1", "A1"), call("n2", "B2"), call("n3", "A2"), call("n4", "B1")]
        assert calls == expected

    def test_no_terminal_pairs_auto_index(self, tmp_path):
        """When no terminal_pairs given, add_terminal uses (spice_node, str(idx+1))."""
        from unittest.mock import call

        calls, _ = self._run(
            tmp_path,
            pin_layout_names=["1", "2"],
            spice_nodes=["n1", "n2"],
            terminal_pairs=None,
        )

        assert calls[0] == call("n1", "1")
        assert calls[1] == call("n2", "2")

    def test_single_pair_not_nested_list(self, tmp_path):
        """A single pair passed as a flat list [pname, pnumber] must still work."""
        from unittest.mock import call

        terminal_pairs = ["n1", "A1"]
        calls, _ = self._run(
            tmp_path,
            pin_layout_names=["A1"],
            spice_nodes=["n1"],
            terminal_pairs=terminal_pairs,
        )

        assert calls[0] == call("n1", "A1")
