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
    from ansys.edb.core.typing import ValueLike
    from pyedb.grpc.edb import Edb
    from pyedb.grpc.database.utility.value import Value

from pyedb.grpc.database.inner.base import ObjBase


class Transform(ObjBase):
    """
    Wrapper around the EDB ``Transform`` object.

    This class exposes transformation properties such as rotation, offsets, and mirroring,
    and provides setters for updating these values.

    Parameters
    ----------
    pedb : Edb
        The parent EDB instance.
    core_object : Ansys.EdB.Utility.Transform
        The underlying .NET Transform object.
    """

    def __init__(self, pedb, core_object):
        super().__init__(pedb, core_object)

    @classmethod
    def create(
            cls,
            pedb: "Edb",
            scale: "ValueLike"=1,
            angle: "ValueLike"=0,
            mirror: bool=False,
            offset_x: "ValueLike"=0,
            offset_y: "ValueLike"=0,
    ) -> "Transform":
        """
        Create a new ``Transform`` object.

        Parameters
        ----------
        pedb : Edb
            The EDB session.
        scale : ValueLike
            Scale factor.
        angle : ValueLike
            Rotation angle in radians.
        mirror : bool
            Mirror about Y axis.
        offset_x : ValueLike
            Offset in X.
        offset_y : ValueLike
            Offset in Y.

        Returns
        -------
        Transform
            A new Transform wrapper object.
        """
        from ansys.edb.core.utility.transform import Transform as CoreTransform

        core_obj = CoreTransform.create(scale, angle, mirror, offset_x, offset_y)

        return cls(pedb, core_obj)

    @property
    def scale(self) -> "Value":
        """Scale property."""
        return self._pedb.value(self.core_object.scale)

    @scale.setter
    def scale(self, value: "ValueLike"):
        self.core_object.scale = value

    @property
    def rotation(self) -> "Value":
        """
        float: Rotation value in degrees.
        """
        return self._pedb.value(self.core_object.rotation)

    @rotation.setter
    def rotation(self, value: "ValueLike"):
        self.core_object.rotation = value

    @property
    def offset_x(self) -> "Value":
        """
        float: X-axis offset value.
        """
        return self._pedb.value(self.core_object.offset_x)

    @offset_x.setter
    def offset_x(self, value: "ValueLike"):
        self.core_object.offset_x = value

    @property
    def offset_y(self) -> "Value":
        """
        float: Y-axis offset value.
        """
        return self._pedb.value(self.core_object.offset_y)

    @offset_y.setter
    def offset_y(self, value: "ValueLike"):
        self.core_object.offset_y = value

    @property
    def mirror(self) -> bool:
        """
        bool: Indicates whether the transform applies mirroring.
        """
        return self.core_object.Mirror

    def set_x_offset(self, x_offset: float) -> bool:
        """
        Set the X offset.

        Parameters
        ----------
        x_offset : float
            X-axis offset value.

        Returns
        -------
        bool
            True if the operation succeeded.
        """
        return self.core_object.SetXOffsetValue(self._pedb.value(x_offset).core_object)

    def set_y_offset(self, y_offset: float) -> bool:
        """
        Set the Y offset.

        Parameters
        ----------
        y_offset : float
            Y-axis offset value.

        Returns
        -------
        bool
            True if the operation succeeded.
        """
        return self.core_object.SetYOffsetValue(self._pedb.value(y_offset).core_object)

    def set_mirror(self, mirror: bool) -> bool:
        """
        Set the mirror flag.

        Parameters
        ----------
        mirror : bool
            ``True`` to enable mirroring, ``False`` to disable.

        Returns
        -------
        bool
            True if the operation succeeded.
        """
        return self.core_object.SetMirror(mirror)

