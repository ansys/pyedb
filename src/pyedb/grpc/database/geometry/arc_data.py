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


class ArcData(GrpcArcData):
    """Class managing ArcData."""

    def __init__(self, pedb, edb_object):
        self._pedb = pedb
        optional = {"height": edb_object.height, "direction": edb_object.direction}
        super.__init__(edb_object.start, edb_object.end, optional)

    @property
    def center(self):
        """Arc data center.

        Returns
        -------
        [float, float]
            [x value, y value]

        """
        return [self.center.x.value, self.center.y.value]

    @property
    def start(self):
        """Arc data start point.

        Returns
        -------
        [float, float]
            [x value, y value]

        """
        return [self.start.x.value, self.start.y.value]

    @property
    def end(self):
        """Arc data end point.

        Returns
        -------
        [float, float]
            [x value, y value]

        """
        return [self.end.x.value, self.end.y.value]

    @property
    def mid_point(self):
        """Arc data mid point.

        Returns
        -------
        [float, float]
            [x value, y value]

        """
        return [self.midpoint.x.value, self.midpoint.y.value]

    @property
    def points(self):
        """Arc data points.

        Returns
        -------
        [[float, float]]
            [[x value, y value]]

        """
        return [[pt.x.value, pt.y.value] for pt in self.points]
