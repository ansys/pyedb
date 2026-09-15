# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

from __future__ import annotations

from pyedb.grpc.database.geometry.point_data import PointData
from pyedb.grpc.database.geometry.polygon_data import PolygonData
from pyedb.grpc.database.primitive.primitive import Primitive


class PrimitiveInstanceCollection(Primitive):
    """Wraps a ``PrimitiveInstanceCollection`` core object.

    A ``PrimitiveInstanceCollection`` efficiently represents large quantities of geometry
    (typically resulting from GDS/GDSII imports) as numerous instantiations of the same
    geometry at different locations, instead of one individual primitive per instantiation.

    Reading the instantiated geometry (:attr:`instantiated_geometry`, :attr:`geometry`,
    :attr:`positions`) is a **read-only, non-mutating** operation performed lazily on demand.
    Converting the collection into individual, persisted primitives (:meth:`decompose`) is a
    **mutating** operation and must be triggered explicitly by the caller.
    """

    def __init__(self, pedb, core=None):
        if core:
            self.core = core
            Primitive.__init__(self, pedb, core)
        self._pedb = pedb

    @property
    def geometry(self) -> PolygonData:
        """Base geometry that the primitive instance collection instantiates.

        Returns
        -------
        :class:`PolygonData <pyedb.grpc.database.geometry.polygon_data.PolygonData>`
        """
        return PolygonData(self._pedb, self.core.geometry)

    @geometry.setter
    def geometry(self, value):
        self.core.geometry = value.core if hasattr(value, "core") else value

    @property
    def positions(self) -> list[PointData]:
        """Positions the base geometry is instantiated at.

        Returns
        -------
        list[:class:`PointData <pyedb.grpc.database.geometry.point_data.PointData>`]
        """
        return [PointData(self._pedb, point) for point in self.core.positions]

    @property
    def instantiated_geometry(self) -> list[PolygonData]:
        """Geometry instantiated at each location in the primitive instance collection.

        This is a **read-only** property. Unlike :meth:`decompose`, accessing it does **not**
        mutate the layout: no new primitives are created and the collection is left untouched.
        It is intended for lazily inspecting/measuring the individual instantiated shapes
        (points, area, bounding box, etc.) without paying the cost of materializing them into
        real, persisted primitives.

        Returns
        -------
        list[:class:`PolygonData <pyedb.grpc.database.geometry.polygon_data.PolygonData>`]
        """
        return [PolygonData(self._pedb, polygon_data) for polygon_data in self.core.instantiated_geometry]

    def decompose(self):
        """Decompose into individual primitives.

        A primitive will be created for each geometry instantiation. This operation **mutates**
        the layout (it materializes and persists one primitive per instance) and can be
        expensive for large collections. It is not called automatically; call it explicitly
        when individual, persisted primitives are required.
        """
        self.core.decompose()

    def delete(self):
        """Delete the primitive instance collection from the layout."""
        self.core.delete()
