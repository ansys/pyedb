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

from pyedb.modeler.geometry_operators import GeometryOperators as go

pytestmark = [pytest.mark.unit, pytest.mark.no_licence, pytest.mark.legacy]


class TestClass:
    def test_find_points_along_lines(self, points_for_line_detection):
        distance_threshold = 0.015
        minimum_number_of_points = 10

        lines, lines_idx, nppoints, nplines, nslines, nlines = go.find_points_along_lines(
            points=points_for_line_detection,
            minimum_number_of_points=minimum_number_of_points,
            distance_threshold=distance_threshold,
            return_additional_info=True,
        )
        assert len(lines) == 20
        assert nppoints == 800
        assert nplines == 28
        assert nslines == 8
        assert nlines == 20

    def test_find_points_along_lines_2(self, points_for_line_detection_135):
        distance_threshold = 0.015
        minimum_number_of_points = 10

        lines, lines_idx, nppoints, nplines, nslines, nlines = go.find_points_along_lines(
            points=points_for_line_detection_135,
            minimum_number_of_points=minimum_number_of_points,
            distance_threshold=distance_threshold,
            selected_angles=[0, 135],
            return_additional_info=True,
        )
        assert len(lines) == 21
        assert nppoints == 1200
        assert nplines == 24
        assert nslines == 7
        assert nlines == 21
