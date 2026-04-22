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
import warnings

from pyedb.dotnet.clr_module import Tuple
from pyedb.dotnet.database.geometry.point_data import PointData

if TYPE_CHECKING:
    from pyedb.dotnet.edb import Edb


class SystemObject(object):
    def __init__(self, pedb: "Edb", core):
        """
        Initialize a SystemObject with reference to the EDB instance and core object.

        This is the base class for all EDB wrapper objects that encapsulate .NET Core objects.
        It provides access to the parent EDB database instance and the underlying .NET object.

        Parameters
        ----------
        pedb : Edb
            Reference to the parent Edb instance. This provides access to the top-level database
            operations, utilities, and other EDB components. Cannot be None.
        core : object
            The underlying .NET Core object that this wrapper encapsulates. This is typically
            an object from the ANSYS EDB .NET API (e.g., EDBLayer, EDBPrimitive, etc.).
            Cannot be None.

        Raises
        ------
        TypeError
            If pedb is not an Edb instance or core is None.

        Notes
        -----
        The core object is stored as a private attribute with name mangling (`__core`) to prevent
        accidental modification by subclasses. Access the core object via the `core` property.

        The pedb instance is stored as a protected attribute (`_pedb`) to allow subclasses to
        access the database reference for performing database operations.

        Examples
        --------
        This class is typically not instantiated directly by users, but subclasses like
        `ObjBase` are used throughout the pyEDB library:

        >>> from pyedb import Edb
        >>> edb = Edb(db_path, edbversion="2024.2")  # doctest: +SKIP
        >>> # SystemObject is instantiated internally by wrapper classes
        >>> layer = edb.layout.layers[0]  # Returns a layer object whose parent class is SystemObject
        """
        self._pedb = pedb
        self.__core = core

    @property
    def core(self):
        return self.__core

    @core.setter
    def core(self, value):
        self.__core = value

    @property
    def _edb_object(self):
        warnings.warn("Deprecated internal property. Use `core` property instead.", DeprecationWarning, stacklevel=2)
        return self.__core

    @_edb_object.setter
    def _edb_object(self, value):
        self.__core = value


class BBox:
    """Bounding box."""

    def __init__(self, pedb, core=None, point_1=None, point_2=None):
        """
        Initialize a bounding box with two corner points.

        A bounding box is defined by two corner points representing the minimum and maximum
        extents of a rectangular region. The bounding box can be initialized either by providing
        a pre-constructed .NET Core Tuple object or by specifying two corner points as coordinate pairs.

        Parameters
        ----------
        pedb : Edb
            Reference to the parent Edb instance. This is used to access database resources
            for creating PointData objects when constructing the bounding box from coordinates.
        core : tuple, optional
            A pre-constructed .NET Core Tuple object containing two PointData objects.
            If provided, this is used directly and `point_1` and `point_2` are ignored.
            Default is None.
        point_1 : array_like, optional
            The first corner point of the bounding box as a coordinate pair [x, y].
            Used when `core` is None. This represents one corner (typically minimum coordinates).
            Default is None.
        point_2 : array_like, optional
            The second corner point of the bounding box as a coordinate pair [x, y].
            Used when `core` is None. This represents the opposite corner (typically maximum coordinates).
            Default is None.

        """

        self._pedb = pedb
        if core:
            self.core = core
        else:
            point_1 = PointData.create_from_xy(self._pedb, x=point_1[0], y=point_1[1])
            point_2 = PointData.create_from_xy(self._pedb, x=point_2[0], y=point_2[1])
            self.core = Tuple[self._pedb.core.Geometry.PointData, self._pedb.core.Geometry.PointData](
                point_1.core, point_2.core
            )

    @property
    def point_1(self):
        return [self.core.Item1.X.ToDouble(), self.core.Item1.Y.ToDouble()]

    @property
    def point_2(self):
        return [self.core.Item2.X.ToDouble(), self.core.Item2.Y.ToDouble()]

    @property
    def corner_points(self):
        return [self.point_1, self.point_2]


class ObjBase(SystemObject):
    """Manages EDB functionalities for a base object."""

    @property
    def is_null(self):
        """Flag indicating if this object is null."""
        return self.core.IsNull()

    @property
    def type(self):
        """Type of the edb object."""
        try:
            return self.core.GetType()
        except AttributeError:  # pragma: no cover
            return None

    @property
    def name(self):
        """Name of the definition."""
        return self.core.GetName()

    @name.setter
    def name(self, value):
        self.core.SetName(value)
