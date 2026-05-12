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

import json
from unittest.mock import MagicMock

import pytest

from pyedb.configuration.cfg_boundaries import CfgBoundaries

pytestmark = [pytest.mark.unit, pytest.mark.no_licence, pytest.mark.legacy]


# ---------------------------------------------------------------------------
# GeneralConfig
# ---------------------------------------------------------------------------


class TestBoundariesConfig:
    def test_empty(self):
        assert CfgBoundaries().to_dict() == {}

    def test_radiation_boundary(self):
        b = CfgBoundaries()
        b.set_radiation_boundary()
        d = b.to_dict()
        assert d["use_open_region"] is True
        assert d["open_region_type"] == "radiation"

    def test_pml_boundary(self):
        b = CfgBoundaries()
        b.set_pml_boundary("5GHz", radiation_level=20, is_pml_visible=True)
        d = b.to_dict()
        assert d["open_region_type"] == "pml"
        assert d["operating_freq"] == "5GHz"
        assert d["radiation_level"] == 20
        assert d["is_pml_visible"] is True

    def test_air_box_extents(self):
        b = CfgBoundaries()
        b.set_air_box_extents(0.15, truncate_at_ground=True, sync=True)
        d = b.to_dict()
        assert d["air_box_horizontal_extent"]["size"] == 0.15
        assert d["truncate_air_box_at_ground"] is True
        assert d["sync_air_box_vertical_extent"] is True

    def test_air_box_asymmetric_vertical(self):
        b = CfgBoundaries()
        b.set_air_box_extents(
            horizontal_size=0.1,
            positive_vertical_size=0.2,
            negative_vertical_size=0.05,
        )
        d = b.to_dict()
        assert d["air_box_positive_vertical_extent"]["size"] == 0.2
        assert d["air_box_negative_vertical_extent"]["size"] == 0.05

    def test_manual_attributes(self):
        b = CfgBoundaries()
        b.dielectric_extent_type = "ConvexHull"
        b.honor_user_dielectric = True
        d = b.to_dict()
        assert d["dielectric_extent_type"] == "ConvexHull"
        # honor_user_dielectric is only emitted when True
        assert d["honor_user_dielectric"] is True

    def test_honor_user_dielectric_default_not_emitted(self):
        b = CfgBoundaries()
        # Default is False → should not appear in the serialised dict
        assert "honor_user_dielectric" not in b.to_dict()