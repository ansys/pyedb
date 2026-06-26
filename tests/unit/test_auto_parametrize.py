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

"""Unit tests for auto_parametrize_design fixes (no license required).

Covers:
- _value_setter preserves Value objects with parametric expressions
- PadProperties._pad_parameter_value uses self.pad_type (not hardcoded REGULAR_PAD)
- PadProperties with empty antipad (geometry_type == 0, no crash)
- _update_pad_parameters_parameters writes to correct pad_type
- position_and_rotation setter passes Value expressions directly to set_position_and_rotation
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

from ansys.edb.core.definition.padstack_def_data import PadType as CorePadType
import pytest

from pyedb.grpc.database.definition.padstack_def import PadProperties
from pyedb.grpc.database.primitive.padstack_instance import PadstackInstance
from pyedb.grpc.database.utility.value import Value
from tests.conftest import config

pytestmark = [
    pytest.mark.unit,
    pytest.mark.skipif(not config["use_grpc"], reason="gRPC tests only"),
]


class _FakeCoreValue:
    """Minimal stand-in for ansys.edb.core.utility.value.Value (CoreValue)."""

    def __init__(self, expression, owner=None):
        self._expression = str(expression)
        try:
            self._numeric = float(expression)
        except (ValueError, TypeError):
            self._numeric = 0.0

    @property
    def value(self):
        return self._numeric

    def __str__(self):
        return self._expression

    def __float__(self):
        return self._numeric

    def __repr__(self):
        return f"_FakeCoreValue({self._expression!r})"


@pytest.fixture(autouse=True)
def _patch_core_value(monkeypatch):
    """Replace CoreValue everywhere so tests run without an active gRPC session."""
    monkeypatch.setattr(
        "ansys.edb.core.utility.value.Value.__init__",
        lambda self, expression, owner=None: _FakeCoreValue.__init__(self, expression, owner),
        raising=True,
    )
    # Also patch the import inside pyedb.grpc.database.utility.value
    monkeypatch.setattr(
        "pyedb.grpc.database.utility.value.CoreValue",
        _FakeCoreValue,
        raising=True,
    )


def _make_pedb(variables=None):
    """Return a minimal mock pedb object with a working _value_setter / value."""
    from pyedb.grpc.edb import Edb as GrpcEdb

    pedb = MagicMock()
    pedb.variables = variables or {}
    pedb.active_db = None
    pedb.active_cell = None

    # Wire up real _value_setter / value so expressions are preserved
    pedb._value_setter = lambda val: GrpcEdb._value_setter(pedb, val)
    pedb.value = lambda val: GrpcEdb.value(pedb, val)
    return pedb


def _make_padstack_mock(pad_data_by_type):
    """Return a mock padstack data object whose get_pad_parameters respects pad_type."""

    def _get_pad_parameters(layer, pad_type):
        return pad_data_by_type.get((layer, pad_type), ())

    mock = MagicMock()
    mock.get_pad_parameters.side_effect = _get_pad_parameters
    mock.set_pad_parameters = MagicMock()
    return mock


def _geom(value):
    """Create a minimal geometry-type enum-like object."""
    return SimpleNamespace(value=value, name=f"PADGEOMTYPE_{value}")


def _pad_tuple(geom_value, sizes, offsetx=0.0, offsety=0.0, rotation=0.0):
    """Build a return value matching get_pad_parameters signature."""
    return (_geom(geom_value), sizes, offsetx, offsety, rotation)


class TestValueSetter:
    """_value_setter must preserve Value objects that carry expressions."""

    def _make_edb(self):
        from pyedb.grpc.edb import Edb as GrpcEdb

        edb = MagicMock()
        edb.active_db = None
        edb.active_cell = None
        edb._value_setter = lambda val: GrpcEdb._value_setter(edb, val)
        edb.value = lambda val: GrpcEdb.value(edb, val)
        return edb

    def test_plain_float_returns_float(self):
        edb = self._make_edb()
        result = edb._value_setter(1e-4)
        assert isinstance(result, float)
        assert result == pytest.approx(1e-4)

    def test_plain_int_returns_int(self):
        edb = self._make_edb()
        result = edb._value_setter(5)
        # int is not float → returned as-is
        assert result == 5

    def test_string_expression_without_dollar_returns_value(self):
        edb = self._make_edb()
        result = edb._value_setter("1e-4+trace_delta")
        assert isinstance(result, Value)

    def test_string_expression_with_dollar_returns_value(self):
        edb = self._make_edb()
        result = edb._value_setter("1e-4+$layer_delta")
        assert isinstance(result, Value)

    def test_value_with_expression_is_preserved(self):
        """Regression: _value_setter must NOT convert Value→float, dropping the expression."""
        edb = self._make_edb()
        # Build a Value that wraps a fake CoreValue expression
        core_expr = _FakeCoreValue("1e-4+$layer_delta")
        v = Value(core_expr, None)
        # Float representation is 1e-4 (delta=0), but the Value object must survive
        result = edb._value_setter(v)
        assert isinstance(result, Value), "Value must be returned as-is, not converted to float"
        assert result is v

    def test_value_without_expression_is_preserved(self):
        """Plain numeric Value should also pass through as Value, not become bare float."""
        edb = self._make_edb()
        v = Value(1e-4)
        result = edb._value_setter(v)
        assert isinstance(result, Value)


class TestPadPropertiesPadTypeRouting:
    """_pad_parameter_value must query using self.pad_type, not REGULAR_PAD."""

    def _make_pad_props(self, pad_type, pad_data_by_type, layer="TOP"):
        pedb_padstack = MagicMock()
        pedb_padstack._pedb = _make_pedb()
        core = _make_padstack_mock(pad_data_by_type)
        return PadProperties(core, layer, pad_type, pedb_padstack)

    def test_regular_pad_reads_regular_pad_slot(self):
        regular_tuple = _pad_tuple(1, [_FakeCoreValue(5e-4)])  # Circle, diameter 0.5 mm
        anti_tuple = _pad_tuple(1, [_FakeCoreValue(8e-4)])  # Circle, diameter 0.8 mm

        pad = self._make_pad_props(
            CorePadType.REGULAR_PAD,
            {("TOP", CorePadType.REGULAR_PAD): regular_tuple, ("TOP", CorePadType.ANTI_PAD): anti_tuple},
        )
        assert pad.geometry_type == 1
        assert float(pad.parameters_values[0]) == pytest.approx(5e-4)

    def test_antipad_reads_antipad_slot(self):
        """Regression: antipad must read ANTI_PAD data, not REGULAR_PAD data."""
        regular_tuple = _pad_tuple(1, [_FakeCoreValue(5e-4)])
        anti_tuple = _pad_tuple(1, [_FakeCoreValue(8e-4)])

        antipad = self._make_pad_props(
            CorePadType.ANTI_PAD,
            {("TOP", CorePadType.REGULAR_PAD): regular_tuple, ("TOP", CorePadType.ANTI_PAD): anti_tuple},
        )
        assert antipad.geometry_type == 1
        assert float(antipad.parameters_values[0]) == pytest.approx(8e-4)

    def test_empty_antipad_returns_geometry_type_zero(self):
        """Regression: empty antipad (no data) must return geometry_type==0, not raise IndexError."""
        antipad = self._make_pad_props(
            CorePadType.ANTI_PAD,
            {},  # No data → get_pad_parameters returns ()
        )
        assert antipad.geometry_type == 0

    def test_empty_antipad_parameters_values_returns_none(self):
        antipad = self._make_pad_props(CorePadType.ANTI_PAD, {})
        assert antipad.parameters_values is None

    def test_empty_antipad_parameters_values_string_returns_none(self):
        antipad = self._make_pad_props(CorePadType.ANTI_PAD, {})
        assert antipad.parameters_values_string is None

    def test_empty_antipad_offsets_and_rotation_return_zero(self):
        antipad = self._make_pad_props(CorePadType.ANTI_PAD, {})
        assert float(antipad.offset_x) == 0.0
        assert float(antipad.offset_y) == 0.0
        assert float(antipad.rotation) == 0.0

    def test_set_parameters_writes_to_correct_pad_type(self):
        """Regression: setting antipad.parameters must write to ANTI_PAD slot, not REGULAR_PAD."""
        regular_tuple = _pad_tuple(1, [_FakeCoreValue(5e-4)])
        anti_tuple = _pad_tuple(1, [_FakeCoreValue(8e-4)])

        antipad = self._make_pad_props(
            CorePadType.ANTI_PAD,
            {("TOP", CorePadType.REGULAR_PAD): regular_tuple, ("TOP", CorePadType.ANTI_PAD): anti_tuple},
        )
        antipad.parameters = {"Diameter": "9e-4+$antipad_delta"}

        # set_pad_parameters must have been called with ANTI_PAD
        call_kwargs = antipad._edb_padstack.set_pad_parameters.call_args
        assert call_kwargs.kwargs["pad_type"] == CorePadType.ANTI_PAD

    def test_set_parameters_writes_to_regular_pad_for_pad(self):
        regular_tuple = _pad_tuple(1, [_FakeCoreValue(5e-4)])

        pad = self._make_pad_props(
            CorePadType.REGULAR_PAD,
            {("TOP", CorePadType.REGULAR_PAD): regular_tuple},
        )
        pad.parameters = {"Diameter": "5e-4+$pad_delta"}

        call_kwargs = pad._edb_padstack.set_pad_parameters.call_args
        assert call_kwargs.kwargs["pad_type"] == CorePadType.REGULAR_PAD


class TestPadPropertiesParameterExpressions:
    """parameters setter must forward string expressions through _value_setter."""

    def _make_regular_pad(self, layer="TOP"):
        pedb_padstack = MagicMock()
        pedb_padstack._pedb = _make_pedb()
        regular_tuple = _pad_tuple(1, [_FakeCoreValue(5e-4)])
        core = _make_padstack_mock({(layer, CorePadType.REGULAR_PAD): regular_tuple})
        return PadProperties(core, layer, CorePadType.REGULAR_PAD, pedb_padstack)

    def test_string_expression_reaches_set_pad_parameters(self):
        pad = self._make_regular_pad()
        pad.parameters = {"Diameter": "5e-4+$pad_delta"}

        call_kwargs = pad._edb_padstack.set_pad_parameters.call_args
        sizes = call_kwargs.kwargs["sizes"]
        assert len(sizes) == 1
        result = sizes[0]
        # Must be a Value (not a bare float) so the expression is preserved in EDB
        assert isinstance(result, Value), f"Expected Value, got {type(result)}: {result}"


class TestPadstackInstancePositionAndRotation:
    """position_and_rotation setter must preserve Value expressions and not wrap in CorePointData."""

    def _make_padstack_instance(self):
        pedb = _make_pedb()
        core = MagicMock()
        core.set_position_and_rotation = MagicMock()
        inst = PadstackInstance.__new__(PadstackInstance)
        inst._pedb = pedb
        inst.core = core
        return inst

    def test_plain_floats_are_set(self):
        inst = self._make_padstack_instance()
        inst.position_and_rotation = [1e-3, 2e-3, 0.0]

        inst.core.set_position_and_rotation.assert_called_once()
        kw = inst.core.set_position_and_rotation.call_args.kwargs
        assert float(kw["x"]) == pytest.approx(1e-3)
        assert float(kw["y"]) == pytest.approx(2e-3)
        assert float(kw["rotation"]) == pytest.approx(0.0)

    def test_value_expression_is_preserved_for_x_and_y(self):
        """Regression: Value objects with expressions must reach set_position_and_rotation intact."""
        inst = self._make_padstack_instance()

        core_x = _FakeCoreValue("1e-3+via_offset_x")
        core_y = _FakeCoreValue("2e-3+via_offset_y")
        val_x = Value(core_x, None)
        val_y = Value(core_y, None)
        val_r = Value(0.0)

        inst.position_and_rotation = [val_x, val_y, val_r]

        inst.core.set_position_and_rotation.assert_called_once()
        kw = inst.core.set_position_and_rotation.call_args.kwargs
        # x and y must arrive as Value (not bare floats)
        assert isinstance(kw["x"], Value), f"x must be Value, got {type(kw['x'])}"
        assert isinstance(kw["y"], Value), f"y must be Value, got {type(kw['y'])}"
        # The Value must be the same object passed in (expression preserved)
        assert kw["x"] is val_x
        assert kw["y"] is val_y

    def test_string_expressions_arrive_as_value(self):
        inst = self._make_padstack_instance()
        inst.position_and_rotation = ["1e-3+via_offset_x", "2e-3+via_offset_y", "0.0"]

        kw = inst.core.set_position_and_rotation.call_args.kwargs
        assert isinstance(kw["x"], Value)
        assert isinstance(kw["y"], Value)
