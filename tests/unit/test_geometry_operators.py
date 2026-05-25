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

from pyedb.generic.geometry_operators import GeometryOperators as go
from pyedb.misc.utilities import compute_arc_points

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

    from pyedb.misc.utilities import compute_arc_points

    def test_arc_less_than_180(self):
        """Test arc with h < r (arc < 180°)."""
        p1 = [0.0, 0.0]
        p2 = [2.0, 0.0]
        h = 0.2  # Small arc, h < r
        xr, yr = compute_arc_points(p1, p2, h, n=6)

        assert len(xr) == 6, f"Expected 6 points, got {len(xr)}"
        assert len(yr) == 6, f"Expected 6 points, got {len(yr)}"

        # Check that all points are above the chord (positive y for h > 0)
        assert all(y > 0 for y in yr), "All points should be above chord for positive h"
        print("✓ Arc < 180° test passed")

    def test_arc_greater_than_180(self):
        """Test arc with h > r (arc > 180°)."""
        p1 = [0.0, 0.0]
        p2 = [2.0, 0.0]
        h = 1.5  # Large arc, h > r (arc > 180°)
        xr, yr = compute_arc_points(p1, p2, h, n=6)

        assert len(xr) == 6, f"Expected 6 points, got {len(xr)}"
        assert len(yr) == 6, f"Expected 6 points, got {len(yr)}"

        # Check that points are on the correct side
        assert all(y > 0 for y in yr), "All points should be above chord for positive h"
        print("✓ Arc > 180° test passed")

    def test_negative_arc(self):
        """Test arc with negative sagitta."""
        p1 = [0.0, 0.0]
        p2 = [2.0, 0.0]
        h = -0.2  # Negative arc
        xr, yr = compute_arc_points(p1, p2, h, n=6)

        assert len(xr) == 6, f"Expected 6 points, got {len(xr)}"
        assert len(yr) == 6, f"Expected 6 points, got {len(yr)}"

        # Check that all points are below the chord (negative y for h < 0)
        assert all(y < 0 for y in yr), "All points should be below chord for negative h"
        print("✓ Negative arc test passed")

    def test_zero_height(self):
        """Test arc with zero height."""
        p1 = [0.0, 0.0]
        p2 = [2.0, 0.0]
        h = 0.0
        xr, yr = compute_arc_points(p1, p2, h, n=6)

        assert xr == [], "Expected empty list for zero height"
        assert yr == [], "Expected empty list for zero height"
        print("✓ Zero height test passed")

    def test_same_start_end(self):
        """Test arc with same start and end points."""
        p1 = [1.0, 1.0]
        p2 = [1.0, 1.0]
        h = 0.5
        xr, yr = compute_arc_points(p1, p2, h, n=6)

        assert xr == [], "Expected empty list for same start/end"
        assert yr == [], "Expected empty list for same start/end"
