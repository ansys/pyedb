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


from ansys.edb.core.primitive.circle import Circle as GrpcCircle
from ansys.edb.core.utility.value import Value as GrpcValue

from pyedb.grpc.database.primitive.primitive import Primitive


class Circle(GrpcCircle, Primitive):
    def __init__(self, pedb, edb_object):
        GrpcCircle.__init__(self, edb_object.msg)
        Primitive.__init__(self, pedb, edb_object)
        self._pedb = pedb

    def get_parameters(self):
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
        params = super().get_parameters()
        return params[0].value, params[1].value, params[2].value

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
        super().set_parameters(GrpcValue(center_x), GrpcValue(center_y), GrpcValue(radius))
