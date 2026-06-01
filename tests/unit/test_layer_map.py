# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT

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
