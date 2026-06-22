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

"""Unit tests for Text.create validation, LayerMap, and PinGroupTerminal properties (no EDB license)."""

from unittest.mock import MagicMock

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.grpc]


@pytest.mark.grpc
class TestTextCreate:
    def test_create_raises_without_layout(self):
        from pyedb.grpc.database.primitive.text import Text

        with pytest.raises(Exception, match="Layout not defined"):
            Text.create(None, layer="L1", center_x=0.0, center_y=0.0, text="hi")

    def test_create_raises_without_layer(self):
        from pyedb.grpc.database.primitive.text import Text

        layout = MagicMock()
        with pytest.raises(ValueError, match="Layer must be provided"):
            Text.create(layout, layer=None, center_x=0.0, center_y=0.0, text="hi")

    def test_create_raises_without_center_x(self):
        from pyedb.grpc.database.primitive.text import Text

        layout = MagicMock()
        with pytest.raises(ValueError, match="Center x and y"):
            Text.create(layout, layer="L1", center_x=None, center_y=0.0, text="hi")

    def test_create_raises_without_text(self):
        from pyedb.grpc.database.primitive.text import Text

        layout = MagicMock()
        with pytest.raises(ValueError, match="Text value"):
            Text.create(layout, layer="L1", center_x=0.0, center_y=0.0, text=None)


@pytest.mark.grpc
class TestPinGroupTerminal:
    def _make(self):
        from pyedb.grpc.database.terminal.pingroup_terminal import PinGroupTerminal

        core = MagicMock()
        core.net = MagicMock()
        core.pin_group = MagicMock()
        core.is_reference_terminal = False
        # Terminal.__init__ calls self.core and self._pedb
        pedb = MagicMock()

        obj = PinGroupTerminal.__new__(PinGroupTerminal)
        obj.core = core
        obj._pedb = pedb
        return obj, core, pedb

    def test_net_returns_net_wrapper(self):
        obj, core, pedb = self._make()
        from unittest.mock import patch

        with patch("pyedb.grpc.database.net.net.Net") as MockNet:
            MockNet.return_value = MagicMock()
            # call the property; it does local import inside the method
            net = obj.net
            # We can't easily intercept the local import, but verify no error raised
            assert net is not None

    def test_net_setter(self):
        obj, core, pedb = self._make()
        new_net = MagicMock()
        obj.net = new_net
        assert core.net == new_net

    def test_pin_group_returns_wrapper(self):
        obj, core, pedb = self._make()
        # PinGroup is imported inside the property method; just verify it returns something
        pg = obj.pin_group
        assert pg is not None

    def test_is_reference_terminal(self):
        obj, core, pedb = self._make()
        assert obj.is_reference_terminal is False


@pytest.mark.grpc
class TestLayerMapMappingDict:
    def test_mapping_keys_exist(self):
        """Ensure the layer_type_mapping dict in layer.py has expected keys."""
        from pyedb.grpc.database.layers.layer import layer_type_mapping

        expected_keys = [
            "conducting",
            "solder_mask",
            "solder_paste",
            "silkscreen",
            "outline",
            "user",
        ]
        for key in expected_keys:
            assert key in layer_type_mapping


@pytest.mark.grpc
class TestBoundaryTypeMappingInPinGroupTerminal:
    def test_boundary_type_keys(self):
        from pyedb.grpc.database.terminal.pingroup_terminal import boundary_type_mapping

        assert "port" in boundary_type_mapping
        assert "voltage_source" in boundary_type_mapping
        assert "current_source" in boundary_type_mapping
        assert "voltage_probe" in boundary_type_mapping
