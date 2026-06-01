# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
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

"""Unit tests for grpc/database/variables.py and terminal/ — no license required."""

from unittest.mock import MagicMock, patch

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.grpc]


@pytest.mark.grpc
def _make_variable(name="my_var"):
    """Return a Variable instance with a mocked pedb."""
    from pyedb.grpc.database.variables import Variable

    pedb = MagicMock()
    pedb.logger = MagicMock()
    return Variable(pedb, name)


@pytest.mark.grpc
def _make_terminal():
    """Return a Terminal instance with mocked pedb and core."""
    from pyedb.grpc.database.terminal.terminal import Terminal

    pedb = MagicMock()
    pedb.logger = MagicMock()
    core = MagicMock()
    core.is_null = False
    terminal = Terminal.__new__(Terminal)
    terminal._pedb = pedb
    terminal.core = core
    terminal._reference_object = None
    # Setup internal mapping dicts
    terminal.__dict__["_Terminal__terminal_type_mapping"] = {
        "invalid": None,
    }
    terminal.__dict__["_Terminal__boundary_type_mapping"] = {}
    return terminal


@pytest.mark.grpc
class TestGrpcVariableUnit:
    """Unit tests for Variable (grpc)."""

    def test_name_property(self):
        """name returns the name set during construction."""
        var = _make_variable("trace_width")
        assert var.name == "trace_width"

    def test_is_design_variable_true_for_local(self):
        """_is_design_varible returns True for local (non-$) variables."""
        var = _make_variable("trace_width")
        assert var._is_design_varible is True

    def test_is_design_variable_false_for_project(self):
        """_is_design_varible returns False for project ($) variables."""
        var = _make_variable("$project_width")
        assert var._is_design_varible is False

    def test_value_getter_calls_get_variable_value(self):
        """value getter calls pedb.get_variable_value."""
        var = _make_variable("w")
        mock_core_val = MagicMock()
        mock_core_val.value = 0.0001
        var._pedb.get_variable_value.return_value = mock_core_val
        with patch("pyedb.grpc.database.variables.CoreValue") as mock_cv:
            mock_cv.return_value.value = 0.0001
            _ = var.value
        var._pedb.get_variable_value.assert_called_once_with("w")

    def test_value_setter_calls_set_variable_value(self):
        """value setter calls pedb.set_variable_value."""
        var = _make_variable("w")
        with patch("pyedb.grpc.database.variables.CoreValue") as mock_cv:
            mock_cv.return_value = MagicMock()
            var.value = "0.1mm"
        var._pedb.set_variable_value.assert_called_once()

    def test_description_getter_calls_get_variable_desc(self):
        """description getter calls pedb.get_variable_desc."""
        var = _make_variable("w")
        var._pedb.get_variable_desc.return_value = "trace width"
        result = var.description
        var._pedb.get_variable_desc.assert_called_once_with("w")
        assert result == "trace width"

    def test_description_setter_calls_set_variable_desc(self):
        """description setter calls pedb.set_variable_desc."""
        var = _make_variable("w")
        var.description = "new desc"
        var._pedb.set_variable_desc.assert_called_once_with("w", "new desc")

    def test_is_parameter_calls_pedb(self):
        """is_parameter delegates to pedb.is_parameter."""
        var = _make_variable("w")
        var._pedb.is_parameter.return_value = False
        result = var.is_parameter
        var._pedb.is_parameter.assert_called_once_with("w")
        assert result is False

    def test_delete_calls_pedb_delete(self):
        """delete calls pedb.delete with the variable name."""
        var = _make_variable("w")
        var._pedb.delete.return_value = True
        result = var.delete()
        var._pedb.delete.assert_called_once_with("w")
        assert result is True


@pytest.mark.grpc
class TestGrpcTerminalUnit:
    """Unit tests for Terminal (grpc)."""

    def test_net_name_returns_empty_when_core_is_null(self):
        """net_name returns empty string when core.is_null is True."""
        from pyedb.grpc.database.terminal.terminal import Terminal

        pedb = MagicMock()
        core = MagicMock()
        core.is_null = True
        terminal = Terminal.__new__(Terminal)
        terminal._pedb = pedb
        terminal.core = core
        terminal._reference_object = None
        assert terminal.net_name == ""

    def test_net_name_returns_empty_when_net_is_null(self):
        """net_name returns empty string when core.net.is_null is True."""
        from pyedb.grpc.database.terminal.terminal import Terminal

        pedb = MagicMock()
        core = MagicMock()
        core.is_null = False
        core.net.is_null = True
        terminal = Terminal.__new__(Terminal)
        terminal._pedb = pedb
        terminal.core = core
        terminal._reference_object = None
        assert terminal.net_name == ""

    def test_net_name_returns_name(self):
        """net_name returns core.net.name when not null."""
        from pyedb.grpc.database.terminal.terminal import Terminal

        pedb = MagicMock()
        core = MagicMock()
        core.is_null = False
        core.net.is_null = False
        core.net.name = "GND"
        terminal = Terminal.__new__(Terminal)
        terminal._pedb = pedb
        terminal.core = core
        terminal._reference_object = None
        assert terminal.net_name == "GND"

    def test_is_port_true_when_boundary_is_port(self):
        """is_port returns True when boundary_type is 'port'."""
        from unittest.mock import PropertyMock

        from pyedb.grpc.database.terminal.terminal import Terminal

        pedb = MagicMock()
        core = MagicMock()
        terminal = Terminal.__new__(Terminal)
        terminal._pedb = pedb
        terminal.core = core
        terminal._reference_object = None

        with patch.object(type(terminal), "boundary_type", new_callable=PropertyMock) as mock_bt:
            mock_bt.return_value = "port"
            assert terminal.is_port is True

    def test_is_port_false_when_boundary_is_not_port(self):
        """is_port returns False when boundary_type is not 'port'."""
        from unittest.mock import PropertyMock

        from pyedb.grpc.database.terminal.terminal import Terminal

        pedb = MagicMock()
        core = MagicMock()
        terminal = Terminal.__new__(Terminal)
        terminal._pedb = pedb
        terminal.core = core
        terminal._reference_object = None

        with patch.object(type(terminal), "boundary_type", new_callable=PropertyMock) as mock_bt:
            mock_bt.return_value = "voltage_source"
            assert terminal.is_port is False

    def test_is_current_source_true(self):
        """is_current_source returns True when boundary_type is 'current_source'."""
        from unittest.mock import PropertyMock

        from pyedb.grpc.database.terminal.terminal import Terminal

        pedb = MagicMock()
        core = MagicMock()
        terminal = Terminal.__new__(Terminal)
        terminal._pedb = pedb
        terminal.core = core
        terminal._reference_object = None

        with patch.object(type(terminal), "boundary_type", new_callable=PropertyMock) as mock_bt:
            mock_bt.return_value = "current_source"
            assert terminal.is_current_source is True

    def test_is_voltage_source_true(self):
        """is_voltage_source returns True when boundary_type is 'voltage_source'."""
        from unittest.mock import PropertyMock

        from pyedb.grpc.database.terminal.terminal import Terminal

        pedb = MagicMock()
        core = MagicMock()
        terminal = Terminal.__new__(Terminal)
        terminal._pedb = pedb
        terminal.core = core
        terminal._reference_object = None

        with patch.object(type(terminal), "boundary_type", new_callable=PropertyMock) as mock_bt:
            mock_bt.return_value = "voltage_source"
            assert terminal.is_voltage_source is True

    def test_reference_net_name_empty_when_no_reference_object(self):
        """reference_net_name returns empty string when reference_object is falsy."""
        from unittest.mock import PropertyMock

        from pyedb.grpc.database.terminal.terminal import Terminal

        pedb = MagicMock()
        core = MagicMock()
        terminal = Terminal.__new__(Terminal)
        terminal._pedb = pedb
        terminal.core = core
        terminal._reference_object = None

        with patch.object(type(terminal), "reference_object", new_callable=PropertyMock) as mock_ro:
            mock_ro.return_value = None
            result = terminal.reference_net_name
        assert result == ""

    def test_reference_net_name_returns_net_name_when_reference_exists(self):
        """reference_net_name returns reference_object.net_name when present."""
        from unittest.mock import PropertyMock

        from pyedb.grpc.database.terminal.terminal import Terminal

        pedb = MagicMock()
        core = MagicMock()
        terminal = Terminal.__new__(Terminal)
        terminal._pedb = pedb
        terminal.core = core
        terminal._reference_object = None

        ref_obj = MagicMock()
        ref_obj.net_name = "GND"
        with patch.object(type(terminal), "reference_object", new_callable=PropertyMock) as mock_ro:
            mock_ro.return_value = ref_obj
            result = terminal.reference_net_name
        assert result == "GND"

    def test_reference_layer_logs_error_and_returns_none(self):
        """reference_layer logs an error and returns None."""
        from pyedb.grpc.database.terminal.terminal import Terminal

        pedb = MagicMock()
        core = MagicMock()
        terminal = Terminal.__new__(Terminal)
        terminal._pedb = pedb
        terminal.core = core
        terminal._reference_object = None

        result = terminal.reference_layer
        pedb.logger.error.assert_called_once()
        assert result is None
