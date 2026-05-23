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

"""Unit tests for grpc/database/definition/wirebond_def.py — no license required."""

from unittest.mock import MagicMock

import pytest

from pyedb.grpc.database.definition.wirebond_def import (
    ApdBondwireDef,
    BondwireDef,
    Jedec4BondwireDef,
    Jedec5BondwireDef,
)
from tests.conftest import config

_grpc_only = pytest.mark.skipif(not config["use_grpc"], reason="Not tested on DotNet.")


# Helpers
def _make_value(v):
    """Return a mock that mimics ansys-edb-core Value with a .value attribute."""
    m = MagicMock()
    m.value = v
    return m


def _make_pedb():
    """Return a lightweight mock of the Edb object."""
    pedb = MagicMock()
    # pedb.value(x) just wraps x in a mock Value whose .value == x
    pedb.value.side_effect = _make_value
    return pedb


# BondwireDef (base)
@_grpc_only
class TestBondwireDefBase:
    def setup_method(self):
        self.pedb = _make_pedb()
        self.core = MagicMock()
        self.bwd = BondwireDef(self.pedb, self.core)

    def test_name_getter(self):
        self.core.name.value = "wire1"
        assert self.bwd.name == "wire1"

    def test_name_setter(self):
        self.bwd.name = "wire2"
        self.pedb.value.assert_called_with("wire2")

    def test_delete(self):
        self.bwd.delete()
        self.core.delete.assert_called_once()


# Jedec4BondwireDef
@_grpc_only
class TestJedec4BondwireDef:
    def setup_method(self):
        self.pedb = _make_pedb()
        self.core = MagicMock()
        self.core.is_null = False
        self.j4 = Jedec4BondwireDef(self.pedb, self.core)

    def test_inherits_base_get_parameters(self):
        self.core.get_parameters.return_value = _make_value(100e-6)
        assert self.j4.get_parameters() == 100e-6

    def test_inherits_base_set_parameters(self):
        self.j4.set_parameters(100e-6)
        self.core.set_parameters.assert_called_once()
        args = self.core.set_parameters.call_args[0]
        assert args[0].value == 100e-6

    def test_height_property_roundtrip(self):
        self.core.get_parameters.return_value = _make_value(200e-6)
        assert self.j4.height == 200e-6
        self.j4.height = 300e-6
        self.core.set_parameters.assert_called_once()

    @pytest.mark.unit
    def test_create_calls_core_create(self, monkeypatch):
        mock_core_create = MagicMock(return_value=self.core)
        import pyedb.grpc.database.definition.wirebond_def as wbd_module

        monkeypatch.setattr(wbd_module.CoreJedec4BondwireDef, "create", mock_core_create)
        edb_mock = MagicMock()
        result = Jedec4BondwireDef.create(edb_mock, "J4_test")
        mock_core_create.assert_called_once_with(edb_mock._db, "J4_test")
        assert isinstance(result, Jedec4BondwireDef)

    @pytest.mark.unit
    def test_find_by_name_returns_instance(self, monkeypatch):
        import pyedb.grpc.database.definition.wirebond_def as wbd_module

        monkeypatch.setattr(wbd_module.CoreJedec4BondwireDef, "find_by_name", MagicMock(return_value=self.core))
        edb_mock = MagicMock()
        result = Jedec4BondwireDef.find_by_name(edb_mock, "J4_test")
        assert isinstance(result, Jedec4BondwireDef)

    @pytest.mark.unit
    def test_find_by_name_returns_none_when_not_found(self, monkeypatch):
        import pyedb.grpc.database.definition.wirebond_def as wbd_module

        monkeypatch.setattr(wbd_module.CoreJedec4BondwireDef, "find_by_name", MagicMock(return_value=None))
        edb_mock = MagicMock()
        result = Jedec4BondwireDef.find_by_name(edb_mock, "missing")
        assert result is None


# Jedec5BondwireDef  — regression tests for the reported bug
@_grpc_only
class TestJedec5BondwireDef:
    def setup_method(self):
        self.pedb = _make_pedb()
        self.core = MagicMock()
        self.core.is_null = False
        self.j5 = Jedec5BondwireDef(self.pedb, self.core)

    def _mock_get_parameters(self, height, die_pad_angle, lead_pad_angle):
        """Configure core.get_parameters() to return three Value mocks."""
        self.core.get_parameters.return_value = (
            _make_value(height),
            _make_value(die_pad_angle),
            _make_value(lead_pad_angle),
        )

    def test_get_parameters_returns_tuple_of_three_floats(self):
        self._mock_get_parameters(100e-6, 90.0, 45.0)
        result = self.j5.get_parameters()
        assert result == (100e-6, 90.0, 45.0)

    def test_set_parameters_passes_all_three_values_to_core(self):
        """Regression: set_parameters must accept three arguments, not one."""
        self.j5.set_parameters(100e-6, 90.0, 45.0)
        self.core.set_parameters.assert_called_once()
        args = self.core.set_parameters.call_args[0]
        assert len(args) == 3
        assert args[0].value == 100e-6
        assert args[1].value == 90.0
        assert args[2].value == 45.0

    def test_set_parameters_one_arg_raises_type_error(self):
        """Regression: calling j5.set_parameters(height) alone must raise TypeError."""
        with pytest.raises(TypeError):
            self.j5.set_parameters(100e-6)

    def test_height_getter_returns_first_element(self):
        self._mock_get_parameters(150e-6, 60.0, 30.0)
        assert self.j5.height == 150e-6

    def test_height_setter_preserves_existing_angles(self):
        """Regression: setting height alone must keep die_pad_angle and lead_pad_angle."""
        self._mock_get_parameters(100e-6, 90.0, 45.0)
        self.j5.height = 200e-6
        self.core.set_parameters.assert_called_once()
        args = self.core.set_parameters.call_args[0]
        assert args[0].value == 200e-6  # new height
        assert args[1].value == 90.0  # preserved die_pad_angle
        assert args[2].value == 45.0  # preserved lead_pad_angle

    @pytest.mark.unit
    def test_create_calls_core_create(self, monkeypatch):
        import pyedb.grpc.database.definition.wirebond_def as wbd_module

        mock_core_create = MagicMock(return_value=self.core)
        monkeypatch.setattr(wbd_module.CoreJedec5BondwireDef, "create", mock_core_create)
        edb_mock = MagicMock()
        result = Jedec5BondwireDef.create(edb_mock, "J5_test")
        mock_core_create.assert_called_once_with(edb_mock._db, "J5_test")
        assert isinstance(result, Jedec5BondwireDef)

    @pytest.mark.unit
    def test_find_by_name_returns_instance(self, monkeypatch):
        import pyedb.grpc.database.definition.wirebond_def as wbd_module

        monkeypatch.setattr(wbd_module.CoreJedec5BondwireDef, "find_by_name", MagicMock(return_value=self.core))
        edb_mock = MagicMock()
        result = Jedec5BondwireDef.find_by_name(edb_mock, "J5_test")
        assert isinstance(result, Jedec5BondwireDef)

    @pytest.mark.unit
    def test_find_by_name_returns_none_when_not_found(self, monkeypatch):
        import pyedb.grpc.database.definition.wirebond_def as wbd_module

        monkeypatch.setattr(wbd_module.CoreJedec5BondwireDef, "find_by_name", MagicMock(return_value=None))
        edb_mock = MagicMock()
        result = Jedec5BondwireDef.find_by_name(edb_mock, "missing")
        assert result is None


# ApdBondwireDef
@_grpc_only
class TestApdBondwireDef:
    def setup_method(self):
        self.pedb = _make_pedb()
        self.core = MagicMock()
        self.core.is_null = False
        self.apd = ApdBondwireDef(self.pedb, self.core)

    def test_get_parameters_returns_string(self):
        """Core returns a Value object whose .value is the bwd descriptor string."""
        self.core.get_parameters.return_value = _make_value("bwd(nm='APD_test', ...)")
        assert self.apd.get_parameters() == "bwd(nm='APD_test', ...)"

    def test_get_parameters_plain_string_fallback(self):
        """If core ever returns a plain str directly, it must pass through unchanged."""
        self.core.get_parameters.return_value = "bwd(nm='APD_test', ...)"
        assert self.apd.get_parameters() == "bwd(nm='APD_test', ...)"

    def test_set_parameters_passes_string_to_core(self):
        block = "bwd(nm='APD_test', ...)"
        self.apd.set_parameters(block)
        self.core.set_parameters.assert_called_once_with(block)

    def test_parameter_block_getter(self):
        self.core.get_parameters.return_value = _make_value("bwd(nm='APD_test', ...)")
        assert self.apd.parameter_block == "bwd(nm='APD_test', ...)"

    def test_parameter_block_setter(self):
        block = "bwd(nm='APD_test', ...)"
        self.apd.parameter_block = block
        self.core.set_parameters.assert_called_once_with(block)

    def test_height_getter_raises_attribute_error(self):
        with pytest.raises(AttributeError, match="APD bondwire definitions do not have a height parameter"):
            _ = self.apd.height

    def test_height_setter_raises_attribute_error(self):
        with pytest.raises(AttributeError, match="APD bondwire definitions do not have a height parameter"):
            self.apd.height = 100e-6

    @pytest.mark.unit
    def test_create_calls_core_create(self, monkeypatch):
        import pyedb.grpc.database.definition.wirebond_def as wbd_module

        mock_core_create = MagicMock(return_value=self.core)
        monkeypatch.setattr(wbd_module.CoreApdBondwireDef, "create", mock_core_create)
        edb_mock = MagicMock()
        result = ApdBondwireDef.create(edb_mock, "APD_test")
        mock_core_create.assert_called_once_with(edb_mock._db, "APD_test")
        assert isinstance(result, ApdBondwireDef)

    @pytest.mark.unit
    def test_find_by_name_returns_instance(self, monkeypatch):
        import pyedb.grpc.database.definition.wirebond_def as wbd_module

        monkeypatch.setattr(wbd_module.CoreApdBondwireDef, "find_by_name", MagicMock(return_value=self.core))
        edb_mock = MagicMock()
        result = ApdBondwireDef.find_by_name(edb_mock, "APD_test")
        assert isinstance(result, ApdBondwireDef)

    @pytest.mark.unit
    def test_find_by_name_returns_none_when_not_found(self, monkeypatch):
        import pyedb.grpc.database.definition.wirebond_def as wbd_module

        monkeypatch.setattr(wbd_module.CoreApdBondwireDef, "find_by_name", MagicMock(return_value=None))
        edb_mock = MagicMock()
        result = ApdBondwireDef.find_by_name(edb_mock, "missing")
        assert result is None
