# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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


class ArcData(GrpcArcData):
    """Class managing ArcData."""

    def __init__(self, pedb, edb_object):
        self._pedb = pedb
        optional = {"height": edb_object.height, "direction": edb_object.direction}
        super.__init__(edb_object.start, edb_object.end, optional)

    @property
    def center(self) -> list[float]:
        """Arc data center.

        Returns
        -------
        [float, float]
            [x value, y value]

        """
        return [Value(super().center.x), Value(super().center.y)]

    @property
    def start(self) -> list[float]:
        """Arc data start point.

        Returns
        -------
        [float, float]
            [x value, y value]

        """
        return [Value(super().start.x), Value(super().start.y)]

    @property
    def end(self) -> list[float]:
        """Arc data end point.

        Returns
        -------
        [float, float]
            [x value, y value]

        """
        return [Value(self.end.x), Value(self.end.y)]

    @property
    def mid_point(self) -> list[float]:
        """Arc data mid point.

        Returns
        -------
        [float, float]
            [x value, y value]

        """
        return [Value(self.midpoint.x), Value(self.midpoint.y)]

    @property
    def points(self) -> list[list[float]]:
        """Arc data points.

        Returns
        -------
        [[float, float]]
            [[x value, y value]]

        """
        return [[Value(pt.x), Value(pt.y)] for pt in self.points]
