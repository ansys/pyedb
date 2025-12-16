# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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


from ansys.edb.core.geometry.arc_data import ArcData as GrpcArcData

from pyedb.grpc.database.utility.value import Value


class ArcData:
    """Class managing ArcData."""

    def __init__(self, edb_object):
        self.core = edb_object

    @property
    def height(self) -> float:
        """Arc data height.

        Returns
        -------
        float
            Height value.

        """
        return Value(self.core.height)

    @property
    def direction(self) -> str:
        """Arc data direction.

        Returns
        -------
        str
            Direction value.

        """
        return str(self.core.direction)

    @property
    def center(self) -> list[float]:
        """Arc data center.

        Returns
        -------
        [float, float]
            [x value, y value]

        """
        return [Value(self.core.center.x), Value(self.core.center.y)]

    @property
    def start(self) -> list[float]:
        """Arc data start point.

        Returns
        -------
        [float, float]
            [x value, y value]

        """
        return [Value(self.core.start.x), Value(self.core.start.y)]

    @property
    def end(self) -> list[float]:
        """Arc data end point.

        Returns
        -------
        [float, float]
            [x value, y value]

        """
        return [Value(self.core.end.x), Value(self.core.end.y)]

    @property
    def midpoint(self) -> list[float]:
        """Arc data mid point.

        Returns
        -------
        [float, float]
            [x value, y value]

        """
        return [Value(self.core.midpoint.x), Value(self.core.midpoint.y)]

    @property
    def points(self) -> list[list[float]]:
        """Arc data points.

        Returns
        -------
        [[float, float]]
            [[x value, y value]]

        """
        return [[Value(pt.x), Value(pt.y)] for pt in self.core.points]

    def is_segment(self) -> bool:
        """Check if arc data is a segment.

        Returns
        -------
        bool
            True if arc data is a segment, false otherwise.

        """
        return self.core.is_segment()

    @property
    def length(self) -> list[float]:
        """Arc data length.

        Returns
        -------
        float
            Length value.

        """
        return self.core.length

    def is_point(self):
        """Check if arc data is a point.

        Returns
        -------
        bool
            True if arc data is a point, false otherwise.

        """
        return self.core.is_point()

    def is_ccw(self):
        """Check if arc data is counter-clockwise.

        Returns
        -------
        bool
            True if arc data is counter-clockwise, false otherwise.

        """
        return self.core.is_ccw()
