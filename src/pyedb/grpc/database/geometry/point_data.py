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

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ansys.edb.core.geometry.point_data import PointData as CorePointData

    from pyedb.grpc.edb import Edb

from pyedb.grpc.database.utility.value import Value


class PointData:
    """Class managing :class:`Point Data <ansys.edb.core.geometry.point_data.PointData>`"""

    def __init__(self, pedb: "Edb", core: "CorePointData"):
        self._pedb = pedb
        self.core = core

    @classmethod
    def create(cls, pedb: "Edb", x: float | str, y: float | str) -> "PointData":
        """Create a new PointData object."""
        core = pedb.core.geometry.point_data.PointData(pedb.value(x), pedb.value(y))
        return cls(pedb, core)

    @property
    def x(self) -> Value:
        """
        X coordinate.

        This property is read-only.
        """
        return self._pedb.value(self.core.x)

    @property
    def y(self) -> Value:
        """
        Y coordinate.

        This property is read-only.
        """
        return self._pedb.value(self.core.y)

    @property
    def arc_height(self) -> Value:
        """Height of the arc. This property is read-only."""
        return self._pedb.value(self.core.arc_height)

    @property
    def is_arc(self) -> bool:
        """
        Flag indicating if the point represents an arc.

        This property is read-only.
        """
        return self.core.is_arc

    def rotate(self, angle: str | float | Value, center: list[str | float | Value]) -> "PointData":
        """Rotate a point at a given center by a given angle.

        Parameters
        ----------
        angle : float, Value
            Angle in radians.
        center : list of float, str, Value
            Center.

        Returns
        -------
        .PointData or :obj:`None`
            PointData after rotating or :obj:`None` if either point is an arc.
        """
        cx = self._pedb.value(center[0])
        cy = self._pedb.value(center[1])
        angle = self._pedb.value(angle)
        dx = self.x - cx
        dy = self.y - cy

        xi = dx * angle.cos() - dy * angle.sin() + cx
        yi = dx * angle.sin() + dy * angle.cos() + cy
        return PointData.create(self._pedb, str(xi), str(yi))
