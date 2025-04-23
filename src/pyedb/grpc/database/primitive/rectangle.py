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


from ansys.edb.core.primitive.rectangle import (
    RectangleRepresentationType as GrpcRectangleRepresentationType,
)
from ansys.edb.core.primitive.rectangle import Rectangle as GrpcRectangle
from ansys.edb.core.utility.value import Value as GrpcValue

from pyedb.grpc.database.primitive.primitive import Primitive


class Rectangle(GrpcRectangle, Primitive):
    """Class representing a rectangle object."""

    def __init__(self, pedb, edb_object):
        Primitive.__init__(self, pedb, edb_object)
        GrpcRectangle.__init__(self, edb_object.msg)
        self._pedb = pedb
        self._mapping_representation_type = {
            "center_width_height": GrpcRectangleRepresentationType.CENTER_WIDTH_HEIGHT,
            "lower_left_upper_right": GrpcRectangleRepresentationType.LOWER_LEFT_UPPER_RIGHT,
        }

    @property
    def polygon_data(self):
        """PolygonData.

        Returns
        -------
        :class:`PolygonData <ansys.edb.core.geometry.polygon_data.PolygonData>`

        """
        return self.cast().polygon_data

    @property
    def representation_type(self):
        """Representation type.

        Returns
        -------
        str.
            ``"center_width_height"`` or ``"lower_left_upper_right"``.
        """
        return super().representation_type.name.lower()

    @representation_type.setter
    def representation_type(self, value):
        if not value in self._mapping_representation_type:
            super().representation_type = GrpcRectangleRepresentationType.INVALID_RECT_TYPE
        else:
            super().representation_type = self._mapping_representation_type[value]

    def get_parameters(self):
        """Get coordinates parameters.

        Returns
        -------
        tuple[
            str,
            float,
            float,
            float,
            float,
            float,
            float`
        ]

            Returns a tuple of the following format:

            **(representation_type, parameter1, parameter2, parameter3, parameter4, corner_radius, rotation)**

            **representation_type** : Type that defines given parameters meaning.

            **parameter1** : X value of lower left point or center point.

            **parameter2** : Y value of lower left point or center point.

            **parameter3** : X value of upper right point or width.

            **parameter4** : Y value of upper right point or height.

            **corner_radius** : Corner radius.

            **rotation** : Rotation.
        """
        parameters = super().get_parameters()
        representation_type = parameters[0].name.lower()
        parameter1 = parameters[1].value
        parameter2 = parameters[2].value
        parameter3 = parameters[3].value
        parameter4 = parameters[4].value
        corner_radius = parameters[5].value
        rotation = parameters[6].value
        return representation_type, parameter1, parameter2, parameter3, parameter4, corner_radius, rotation

    def set_parameters(self, rep_type, param1, param2, param3, param4, corner_rad, rotation):
        """Set coordinates parameters.

        Parameters
        ----------
        rep_type : :class:`RectangleRepresentationType`
            Type that defines given parameters meaning.
        param1 : :class:`Value <ansys.edb.utility.Value>`
            X value of lower left point or center point.
        param2 : :class:`Value <ansys.edb.utility.Value>`
            Y value of lower left point or center point.
        param3 : :class:`Value <ansys.edb.utility.Value>`
            X value of upper right point or width.
        param4 : :class:`Value <ansys.edb.utility.Value>`
            Y value of upper right point or height.
        corner_rad : :class:`Value <ansys.edb.utility.Value>`
            Corner radius.
        rotation : :class:`Value <ansys.edb.utility.Value>`
            Rotation.
        """

        return super().set_parameters(
            self.representation_type[rep_type],
            GrpcValue(param1),
            GrpcValue(param2),
            GrpcValue(param3),
            GrpcValue(param4),
            GrpcValue(corner_rad),
            GrpcValue(rotation),
        )
