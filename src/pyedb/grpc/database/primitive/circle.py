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


from typing import Union

from ansys.edb.core.primitive.circle import Circle as GrpcCircle

from pyedb.grpc.database.layers.layer import Layer
from pyedb.grpc.database.net.net import Net
from pyedb.grpc.database.primitive.primitive import Primitive
from pyedb.grpc.database.utility.value import Value


class Circle(Primitive):
    def __init__(self, pedb, edb_object=None):
        if edb_object:
            self.core = edb_object
            Primitive.__init__(self, pedb, edb_object)
        self._pedb = pedb

    @classmethod
    def create(
        cls,
        layout,
        layer: Union[str, Layer] = None,
        net: Union[str, Net, None] = None,
        center_x: float = None,
        center_y: float = None,
        radius: float = 0.0,
    ):
        if not layout:
            raise Exception("Layout not defined.")
        if not layer:
            raise ValueError("Layer must be provided to create a circle.")
        if center_x is None or center_y is None:
            raise ValueError("Center x and y values must be provided to create a circle.")
        edb_object = GrpcCircle.create(
            layout=layout.core,
            layer=layer,
            net=net.core,
            center_x=Value(center_x),
            center_y=Value(center_y),
            radius=Value(radius),
        )
        new_circle = cls(layout._pedb, edb_object)
        layout._pedb.modeler._add_primitive(new_circle)
        return new_circle

    def delete(self):
        """Delete the circle from the layout."""
        self._pedb.modeler._remove_primitive(self)
        self.core.delete()

    def get_parameters(self) -> tuple[float, float, float]:
        """Returns parameters.

        Returns
        -------
        tuple[
            :class:`.Value`,
            :class:`.Value`,
            :class:`.Value`
        ]

            Returns a tuple in this format:

            **(center_x, center_y, radius)**

            **center_x** : X value of center point.

            **center_y** : Y value of center point.

            **radius** : Radius value of the circle.


        """
        params = self.core.get_parameters()
        return Value(params[0]), Value(params[1]), Value(params[2])

    def set_parameters(self, center_x, center_y, radius):
        """Set parameters.

        Parameters
        ----------
        center_x : float
            Center x value.
        center_y : float
            Center y value
        radius : float
            Circle radius.

        """
        self.core.set_parameters(Value(center_x), Value(center_y), Value(radius))
