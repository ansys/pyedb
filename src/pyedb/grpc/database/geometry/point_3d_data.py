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

from ansys.edb.core.geometry.point3d_data import Point3DData as GrpcPoint3DData

from pyedb.grpc.database.utility.value import Value


class Point3DData:
    """Point 3D Data."""

    def __init__(self, x, y, z):
        self.core = GrpcPoint3DData.__init__(x, y, z)

    @property
    def x(self) -> float:
        """X position.

        Returns
        -------
        float
            X position value.

        """
        return Value(self.core.x)

    @x.setter
    def x(self, value):
        self.core.x = Value(value)

    @property
    def y(self) -> float:
        """Y position.

        Returns
        -------
        float
            Y position value.

        """
        return Value(self.core.y)

    @y.setter
    def y(self, value):
        self.core.y = Value(value)

    @property
    def z(self) -> float:
        """Z position.

        Returns
        -------
        float
            Z position value.

        """
        return Value(self.core.z)

    @z.setter
    def z(self, value):
        self.core.z = Value(value)
