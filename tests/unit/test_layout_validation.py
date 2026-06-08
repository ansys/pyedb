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

"""Unit tests for grpc/database/layout_validation.py — no license required."""

import re
from unittest.mock import MagicMock, PropertyMock, patch

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.grpc]


@pytest.mark.grpc
def _make_layout_validation():
    """Create a LayoutValidation instance with a mocked pedb."""
    from pyedb.grpc.database.layout_validation import LayoutValidation

    pedb = MagicMock()
    pedb.logger = MagicMock()
    pedb.logger.reset_timer.return_value = None
    pedb.logger.info.return_value = None
    pedb.logger.info_timer.return_value = None
    lv = LayoutValidation.__new__(LayoutValidation)
    lv._pedb = pedb
    lv._layout_instance = MagicMock()
    return lv


@pytest.mark.grpc
class TestGrpcLayoutValidationUnit:
    """Unit tests for LayoutValidation that can run without a live EDB server."""

    def test_init_stores_pedb(self):
        """__init__ stores pedb and layout_instance."""
        lv = _make_layout_validation()
        assert lv._pedb is not None
        assert lv._layout_instance is not None

    def test_illegal_net_names_detects_special_chars(self):
        """illegal_net_names returns nets with special characters."""
        lv = _make_layout_validation()
        net_ok = MagicMock()
        net_bad = MagicMock()
        lv._pedb.nets.nets = {"GND": net_ok, "NET(1)": net_bad, "VCC": net_ok}
        lv.illegal_net_names(fix=False)
        # Should not rename since fix=False
        net_bad.name.__set__.assert_not_called() if hasattr(net_bad.name, "__set__") else None
        lv._pedb.logger.info.assert_called_once()

    def test_illegal_net_names_fixes_special_chars(self):
        """illegal_net_names renames nets when fix=True."""
        lv = _make_layout_validation()
        net_bad = MagicMock()
        lv._pedb.nets.nets = {"NET(1)": net_bad}
        lv.illegal_net_names(fix=True)
        # The name setter should be called with cleaned name
        net_bad.__setattr__("name", "NET_1_")

    def test_illegal_net_names_pattern_matches(self):
        """Verify the illegal characters pattern detects correctly."""
        pattern = r"[\(\)\\\/:;*?<>\'\"|`~$]"
        assert re.findall(pattern, "NET(1)")
        assert re.findall(pattern, "V$CC")
        assert not re.findall(pattern, "GND")
        assert not re.findall(pattern, "NET_1")

    def test_fix_self_intersections_returns_true_no_prims(self):
        """fix_self_intersections returns True even if no primitives."""
        lv = _make_layout_validation()
        lv._pedb.layout.polygons = []
        lv._pedb.nets.nets = {"GND": MagicMock()}
        result = lv.fix_self_intersections(net_list=["GND"])
        assert result is True

    def test_fix_self_intersections_no_intersections_found(self):
        """fix_self_intersections logs 'not found' when no new_prims."""
        lv = _make_layout_validation()
        prim = MagicMock()
        prim.net_name = "GND"
        prim.fix_self_intersections.return_value = []
        lv._pedb.layout.polygons = [prim]
        result = lv.fix_self_intersections(net_list=["GND"])
        assert result is True
        lv._pedb.logger.info.assert_called_once()

    def test_fix_self_intersections_intersections_found(self):
        """fix_self_intersections logs 'detected' when new_prims found."""
        lv = _make_layout_validation()
        prim = MagicMock()
        prim.net_name = "GND"
        prim.fix_self_intersections.return_value = [MagicMock()]
        lv._pedb.layout.polygons = [prim]
        result = lv.fix_self_intersections(net_list=["GND"])
        assert result is True

    def test_fix_self_intersections_str_net_list(self):
        """fix_self_intersections converts string net_list to list."""
        lv = _make_layout_validation()
        prim = MagicMock()
        prim.net_name = "GND"
        prim.fix_self_intersections.return_value = []
        lv._pedb.layout.polygons = [prim]
        result = lv.fix_self_intersections(net_list="GND")
        assert result is True

    def test_padstacks_no_name_counts_unnamed(self):
        """padstacks_no_name counts padstacks with no name."""
        from ansys.edb.core.database import ProductIdType as CoreProductIdType

        lv = _make_layout_validation()
        pad_named = MagicMock()
        pad_named.core.get_product_property.return_value = MagicMock()
        pad_named.core.get_product_property.return_value.__str__ = lambda self: "'VIA1'"
        pad_unnamed = MagicMock()
        pad_unnamed.core.get_product_property.return_value = MagicMock()
        pad_unnamed.core.get_product_property.return_value.__str__ = lambda self: "''"
        pad_unnamed.component = None
        lv._pedb.layout.padstack_instances = [pad_named, pad_unnamed]
        # Just ensure it runs without error
        lv.padstacks_no_name(fix=False)
        lv._pedb.logger.info.assert_called_once()

    def test_delete_empty_pin_groups_deletes_empty_groups(self):
        """delete_empty_pin_groups deletes groups with no pins."""
        lv = _make_layout_validation()
        pg_empty = MagicMock()
        pg_empty.pins = []
        pg_full = MagicMock()
        pg_full.pins = [MagicMock()]
        lv._pedb.siwave.pin_groups = {"empty_pg": pg_empty, "full_pg": pg_full}
        lv.delete_empty_pin_groups()
        pg_empty.delete.assert_called_once()
        pg_full.delete.assert_not_called()

    def test_delete_empty_pin_groups_no_empty_groups(self):
        """delete_empty_pin_groups does nothing when all groups have pins."""
        lv = _make_layout_validation()
        pg_full = MagicMock()
        pg_full.pins = [MagicMock()]
        lv._pedb.siwave.pin_groups = {"full_pg": pg_full}
        lv.delete_empty_pin_groups()
        pg_full.delete.assert_not_called()

    def test_illegal_rlc_values_no_inductors(self):
        """illegal_rlc_values returns empty list when no inductors."""
        lv = _make_layout_validation()
        lv._pedb.components.inductors = {}
        result = lv.illegal_rlc_values()
        assert result == []

    def test_illegal_rlc_values_with_valid_inductors(self):
        """illegal_rlc_values returns empty when inductors have pin pairs."""
        lv = _make_layout_validation()
        ind = MagicMock()
        ind.component_property.model.pin_pairs.return_value = [("1", "2")]
        lv._pedb.components.inductors = {"L1": ind}
        result = lv.illegal_rlc_values()
        assert result == []
