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
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyedb.dotnet.database.utilities.value import Value
    from pyedb.dotnet.edb import Edb

from pyedb.dotnet.database.utilities.obj_base import ObjBase


class Transform(ObjBase):
    """
    Wrapper around the EDB ``Transform`` object.

    This class exposes transformation properties such as rotation, offsets, and mirroring,
    and provides setters for updating these values.

    Parameters
    ----------
    pedb : Edb
        The parent EDB instance.
    edb_object : Ansys.EdB.Utility.Transform
        The underlying .NET Transform object.
    """

    def __init__(self, pedb, edb_object):
        super().__init__(pedb, edb_object)

    @classmethod
    def create(cls, pedb: "Edb") -> "Transform":
        """
        Create a new ``Transform`` object.

        Parameters
        ----------
        pedb : Edb
            The parent EDB database instance.

        Returns
        -------
        Transform
            A new Transform wrapper object.
        """
        return cls(pedb, pedb.core.Utility.Transform())

    @property
    def scale(self) -> "Value":
        """Scale property."""
        return self._pedb.value(self._edb_object.Scale)

    @scale.setter
    def scale(self, value):
        self._edb_object.SetScaleValue(self._pedb.value(value)._edb_object)

    @property
    def rotation(self) -> "Value":
        """
        float: Rotation value in degrees.
        """
        return self._pedb.value(self._edb_object.Rotation)

    @rotation.setter
    def rotation(self, value):
        self._edb_object.SetRotationValue(self._pedb.value(value)._edb_object)

    @property
    def offset_x(self) -> "Value":
        """
        float: X-axis offset value.
        """
        return self._pedb.value(self._edb_object.XOffset)

    @offset_x.setter
    def offset_x(self, value):
        self._edb_object.SetXOffsetValue(self._pedb.value(value)._edb_object)

    @property
    def offset_y(self) -> "Value":
        """
        float: Y-axis offset value.
        """
        return self._pedb.value(self._edb_object.YOffset)

    @offset_y.setter
    def offset_y(self, value):
        self._edb_object.SetYOffsetValue(self._pedb.value(value)._edb_object)

    @property
    def mirror(self) -> bool:
        """
        bool: Indicates whether the transform applies mirroring.
        """
        return self._edb_object.Mirror

    @mirror.setter
    def mirror(self, value):
        self._edb_object.SetMirror(value)
