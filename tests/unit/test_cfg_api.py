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

from pyedb.configuration.cfg_operations import CfgCutout, CfgOperations

pytestmark = [pytest.mark.unit, pytest.mark.no_licence, pytest.mark.legacy]


class TestOperationsConfig:
    def test_empty(self):
        assert CfgOperations().to_dict() == {}

    def test_add_cutout(self):
        ops = CfgOperations()
        c = ops.add_cutout(signal_nets=["SIG1"], reference_nets=["GND"])
        assert isinstance(c, CfgCutout)
        d = ops.to_dict()
        assert "cutout" in d
        assert d["cutout"]["signal_list"] == ["SIG1"]

    def test_add_cutout_extent_type_convexhull(self):
        ops = CfgOperations()
        ops.add_cutout(signal_nets=["SIG"], reference_nets=["GND"], extent_type="ConvexHull")
        assert ops.to_dict()["cutout"]["extent_type"] == "ConvexHull"

    def test_add_cutout_extent_type_case_insensitive(self):
        ops = CfgOperations()
        ops.add_cutout(signal_nets=["SIG"], reference_nets=["GND"], extent_type="convexhull")
        assert ops.to_dict()["cutout"]["extent_type"] == "ConvexHull"

    def test_add_cutout_extent_type_boundingbox_case_insensitive(self):
        ops = CfgOperations()
        ops.add_cutout(signal_nets=["SIG"], reference_nets=["GND"], extent_type="BOUNDINGBOX")
        assert ops.to_dict()["cutout"]["extent_type"] == "BoundingBox"

    def test_add_cutout_expansion_size(self):
        ops = CfgOperations()
        ops.add_cutout(signal_nets=["SIG"], reference_nets=["GND"], expansion_size=0.003)
        assert ops.to_dict()["cutout"]["expansion_size"] == 0.003

    def test_generate_auto_hfss_regions(self):
        ops = CfgOperations()
        ops.generate_auto_hfss_regions = True
        d = ops.to_dict()
        assert d["generate_auto_hfss_regions"] is True
