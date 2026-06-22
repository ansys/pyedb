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

"""Unit tests for LayerMap wrapper (no EDB license required)."""

from unittest.mock import MagicMock

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.grpc]


@pytest.mark.grpc
class TestLayerMap:
    def _make(self):
        from pyedb.grpc.database.utility.layer_map import LayerMap

        core = MagicMock()
        core.id = 3
        core.is_null = False
        core.get_mapping_forward.return_value = 5
        core.get_mapping_backward.return_value = 2
        return LayerMap(core), core

    def test_id(self):
        lm, core = self._make()
        assert lm.id == 3

    def test_is_null_false(self):
        lm, core = self._make()
        assert lm.is_null is False

    def test_is_null_true(self):
        lm, core = self._make()
        core.is_null = True
        assert lm.is_null is True

    def test_clear(self):
        lm, core = self._make()
        lm.clear()
        core.clear.assert_called_once()

    def test_get_mapping_forward(self):
        lm, core = self._make()
        result = lm.get_mapping_forward(1)
        assert result == 5
        core.get_mapping_forward.assert_called_once_with(1)

    def test_get_mapping_backward(self):
        lm, core = self._make()
        result = lm.get_mapping_backward(5)
        assert result == 2
        core.get_mapping_backward.assert_called_once_with(5)

    def test_set_mapping(self):
        lm, core = self._make()
        lm.set_mapping(1, 5)
        core.set_mapping.assert_called_once_with(1, 5)
