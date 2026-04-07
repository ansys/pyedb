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
import warnings
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from pyedb.dotnet.edb import Edb

from pyedb.dotnet.database.utilities.value import Value


class PointData:
    """Point Data."""

    def __init__(self, pedb: "Edb", core: Any | None = None) -> None:
        self._pedb = pedb
        self.core = core

    @classmethod
    def create(cls, pedb: "Edb", x: float | str, y: float | str) -> "PointData":
        """Create a PointData object."""
        edb_object = pedb.core.Geometry.PointData(pedb.edb_value(x), pedb.edb_value(y))
        return cls(pedb, edb_object)

    @classmethod
    def create_arc_point(cls, pedb, arc_height):
        """Create a arc PointData object."""
        edb_object = pedb.core.Geometry.PointData(pedb.edb_value(arc_height))
        return cls(pedb, edb_object)

    @classmethod
    def create_from_x(cls, pedb: Any, x: float) -> "PointData":
        """Create a new PointData object."""
        warnings.warn("Use create_arc_point instead",DeprecationWarning, stacklevel=2)
        edb_object = pedb.core.Geometry.PointData(pedb.edb_value(x))
        return cls(pedb, edb_object)

    @classmethod
    def create_from_xy(cls, pedb: Any, x: float, y: float) -> "PointData":
        """Create a new PointData object."""
        warnings.warn("Use create instead", DeprecationWarning, stacklevel=2)
        edb_object = pedb.core.Geometry.PointData(pedb.edb_value(x), pedb.edb_value(y))
        return cls(pedb, edb_object)

    @property
    def x(self) -> Value:
        """X coordinate."""
        return self._pedb.value(self.core.X)

    @x.setter
    def x(self, value: float|Value) -> None:
        self.core.X = self._pedb.edb_value(value)

    @property
    def x_evaluated(self) -> float:
        return self.core.X.ToDouble()

    @property
    def y(self) -> Value:
        """Y coordinate."""
        return self._pedb.value(self.core.Y)

    @y.setter
    def y(self, value: float|Value) -> None:
        self.core.Y = self._pedb.edb_value(value)

    @property
    def y_evaluated(self) -> float:
        return self.core.Y.ToDouble()

    @property
    def arc_height(self)->Value:
        """Height of the arc. This property is read-only."""
        return self._pedb.value(self.core.GetArcHeight())

    @property
    def is_arc(self)->bool:
        """
        Flag indicating if the point represents an arc.

        This property is read-only.
        """
        return self.core.IsArc()

    def rotate(self, angle:str|float, center: tuple[str|float])->"PointData":
        """Rotate the point."""
        cx = self._pedb.value(center[0])
        cy = self._pedb.value(center[1])
        angle = self._pedb.value(angle)
        dx = self.x - cx
        dy = self.y - cy

        xi  = dx*angle.cos() - dy*angle.sin() + cx
        yi  = dx*angle.sin() + dy*angle.cos() + cy
        return PointData.create(self._pedb, str(xi), str(yi))

    def move(self, dx:str|float, dy:str|float)->"PointData":
        """Move the point."""
        dx = self._pedb.value(dx)
        dy = self._pedb.value(dy)
        return PointData.create(self._pedb, str(self.x + dx), str(self.y + dy))