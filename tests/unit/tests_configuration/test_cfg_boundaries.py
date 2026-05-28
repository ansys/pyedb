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

import pytest

from pyedb.configuration.cfg_boundaries import CfgBoundaries

pytestmark = [pytest.mark.unit, pytest.mark.no_licence, pytest.mark.legacy]


class TestBoundariesConfig:
    def test_empty(self):
        assert CfgBoundaries().model_dump(exclude_none=True, exclude_defaults=True) == {}

    def test_create(self):
        b = CfgBoundaries.create(use_open_region=True)
        assert b.use_open_region is True

    def test_radiation_boundary(self):
        b = CfgBoundaries()
        b.set_radiation_boundary()
        d = b.model_dump(exclude_none=True, exclude_defaults=True)
        assert d["use_open_region"] is True
        assert d["open_region_type"] == "radiation"

    def test_radiation_boundary_use_open_false(self):
        b = CfgBoundaries()
        b.set_radiation_boundary(use_open_region=False)
        assert b.use_open_region is False
        assert b.open_region_type == "radiation"

    def test_pml_boundary(self):
        b = CfgBoundaries()
        b.set_pml_boundary("5GHz", radiation_level=20, is_pml_visible=True)
        d = b.model_dump(exclude_none=True, exclude_defaults=True)
        assert d["open_region_type"] == "pml"
        assert d["operating_freq"] == "5GHz"
        assert d["radiation_level"] == 20
        assert d["is_pml_visible"] is True

    def test_pml_boundary_defaults(self):
        b = CfgBoundaries()
        b.set_pml_boundary("2.4GHz")
        assert b.radiation_level == 20
        assert b.is_pml_visible is False

    def test_air_box_extents(self):
        b = CfgBoundaries()
        b.set_air_box_extents(0.15, truncate_at_ground=True, sync=True)
        d = b.model_dump(exclude_none=True, exclude_defaults=True)
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
        d = b.model_dump(exclude_none=True, exclude_defaults=True)
        assert d["air_box_positive_vertical_extent"]["size"] == 0.2
        assert d["air_box_negative_vertical_extent"]["size"] == 0.05

    def test_air_box_is_multiple(self):
        b = CfgBoundaries()
        b.set_air_box_extents(0.1, horizontal_is_multiple=True)
        assert b.air_box_horizontal_extent.is_multiple is True

    def test_set_extent_default(self):
        b = CfgBoundaries()
        b.set_extent()
        assert b.extent_type == "BoundingBox"
        assert b.truncate_air_box_at_ground is False

    def test_set_extent_with_base_polygon(self):
        b = CfgBoundaries()
        b.set_extent(extent_type="Polygon", base_polygon="my_poly", truncate_air_box_at_ground=True)
        assert b.base_polygon == "my_poly"
        assert b.truncate_air_box_at_ground is True

    def test_set_extent_no_base_polygon_not_set(self):
        """base_polygon must not be set when not passed."""
        b = CfgBoundaries()
        b.set_extent()
        assert b.base_polygon is None

    def test_set_dielectric_extent_default(self):
        b = CfgBoundaries()
        b.set_dielectric_extent()
        assert b.dielectric_extent_type == "BoundingBox"
        assert b.dielectric_extent_size.size == 0
        assert b.dielectric_extent_size.is_multiple is False

    def test_set_dielectric_extent_with_values(self):
        b = CfgBoundaries()
        b.set_dielectric_extent(extent_type="ConvexHull", expansion_size=0.01, is_multiple=True)
        assert b.dielectric_extent_type == "ConvexHull"
        assert b.dielectric_extent_size.size == 0.01
        assert b.dielectric_extent_size.is_multiple is True

    def test_set_dielectric_extent_with_base_polygon(self):
        b = CfgBoundaries()
        b.set_dielectric_extent(base_polygon="poly1")
        assert b.dielectric_base_polygon == "poly1"

    def test_set_dielectric_extent_honor_user(self):
        b = CfgBoundaries()
        b.set_dielectric_extent(honor_user_dielectric=True)
        assert b.honor_user_dielectric is True

    def test_honor_user_dielectric_default_not_emitted(self):
        b = CfgBoundaries()
        d = b.model_dump(exclude_none=True, exclude_defaults=True)
        assert "honor_user_dielectric" not in d

    def test_padding_data_model(self):
        pd = CfgBoundaries.PaddingData(size="0.5mm", is_multiple=False)
        assert pd.size == "0.5mm"
        assert pd.is_multiple is False

    def test_full_config_roundtrip(self):
        b = CfgBoundaries()
        b.set_radiation_boundary()
        b.set_air_box_extents(0.2, sync=True)
        b.set_extent("ConvexHull")
        b.set_dielectric_extent("BoundingBox", 0.01)
        d = b.model_dump(exclude_none=True, exclude_defaults=True)
        assert d["open_region_type"] == "radiation"
        assert d["air_box_horizontal_extent"]["size"] == 0.2
        assert d["extent_type"] == "ConvexHull"
        assert d["dielectric_extent_size"]["size"] == 0.01

    def test_manual_attributes(self):
        b = CfgBoundaries()
        b.dielectric_extent_type = "ConvexHull"
        b.honor_user_dielectric = True
        d = b.model_dump(exclude_none=True, exclude_defaults=True)
        assert d["dielectric_extent_type"] == "ConvexHull"
        # honor_user_dielectric is only emitted when True
        assert d["honor_user_dielectric"] is True
