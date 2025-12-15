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

from ansys.edb.core.primitive.rectangle import (
    Rectangle as GrpcRectangle,
    RectangleRepresentationType as GrpcRectangleRepresentationType,
)

from pyedb.grpc.database.layers.layer import Layer
from pyedb.grpc.database.primitive.primitive import Primitive
from pyedb.grpc.database.utility.value import Value


class Rectangle(Primitive):
    """Class representing a rectangle object."""

    def __init__(self, pedb, edb_object=None):
        if edb_object:
            Primitive.__init__(self, pedb, edb_object)
            self.core = edb_object
        self._pedb = pedb
        self._mapping_representation_type = {
            "center_width_height": GrpcRectangleRepresentationType.CENTER_WIDTH_HEIGHT,
            "lower_left_upper_right": GrpcRectangleRepresentationType.LOWER_LEFT_UPPER_RIGHT,
        }

    @property
    def representation_type(self) -> str:
        """Representation type.

        Returns
        -------
        str.
            ``"center_width_height"`` or ``"lower_left_upper_right"``.
        """
        return self.core.representation_type.name.lower()

    @representation_type.setter
    def representation_type(self, value):
        if not value in self._mapping_representation_type:
            self.core.representation_type = GrpcRectangleRepresentationType.INVALID_RECT_TYPE
        else:
            self.core.representation_type = self._mapping_representation_type[value]

    @classmethod
    def create(
        cls,
        layout,
        layer: Union[str, Layer] = None,
        net: Union[str, "Net"] = None,
        rep_type: str = "center_width_height",
        param1: float = None,
        param2: float = None,
        param3: float = None,
        param4: float = None,
        corner_rad: float = 0.0,
        rotation: float = 0.0,
    ):
        """
        Create a rectangle primitive in the specified layout, layer, and net with the given parameters.

        Parameters
        ----------
        layout : Layout
            The layout in which the rectangle will be created. If not provided, the active layout of the `pedb` instance
            will be used.
        layer : Union[str, Layer], optional
            The layer in which the rectangle will be created. This parameter is required and must be specified.
        net : Union[str, Net], optional
            The net to which the rectangle will belong. This parameter is required and must be specified.
        rep_type : str, optional
            The representation type of the rectangle. Options are `"center_width_height"` or `"lower_left_upper_right"`.
            The default value is `"center_width_height"`.
        param1 : float, optional
            The first parameter defining the rectangle. Its meaning depends on the `rep_type`.
        param2 : float, optional
            The second parameter defining the rectangle. Its meaning depends on the `rep_type`.
        param3 : float, optional
            The third parameter defining the rectangle. Its meaning depends on the `rep_type`.
        param4 : float, optional
            The fourth parameter defining the rectangle. Its meaning depends on the `rep_type`.
        corner_rad : float, optional
            The corner radius of the rectangle. The default value is `0.0`.
        rotation : float, optional
            The rotation angle of the rectangle in degrees. The default value is `0.0`.

        Returns
        -------
        Rectangle
            The created rectangle primitive.

        Raises
        ------
        ValueError
            If the `layer` parameter is not provided.
        ValueError
            If the `net` parameter is not provided.

        Notes
        -----
        - The created rectangle is added to the modeler primitives of the `pedb` instance.
        - The `rep_type` determines how the parameters are interpreted:
            - `"center_width_height"`: `param1` and `param2` represent the center coordinates, while `param3` and
            `param4` represent the width and height.
            - `"lower_left_upper_right"`: `param1` and `param2` represent the lower-left corner coordinates, while
            `param3` and `param4` represent the upper-right corner coordinates.
        """
        if not layout:
            raise ValueError("Layout must be provided.")
        if not layer:
            raise ValueError("Layer must be provided.")
        if not net:
            raise ValueError("Net must be provided.")

        rep_type_mapping = {
            "center_width_height": GrpcRectangleRepresentationType.CENTER_WIDTH_HEIGHT,
            "lower_left_upper_right": GrpcRectangleRepresentationType.LOWER_LEFT_UPPER_RIGHT,
        }
        rep_type = rep_type_mapping.get(rep_type, GrpcRectangleRepresentationType.INVALID_RECT_TYPE)
        edb_object = GrpcRectangle.create(
            layout=layout.core,
            layer=layer,
            net=net.core,
            rep_type=rep_type,
            param1=Value(param1),
            param2=Value(param2),
            param3=Value(param3),
            param4=Value(param4),
            corner_rad=Value(corner_rad),
            rotation=Value(rotation),
        )
        # keep cache synced
        new_rect = cls(layout._pedb, edb_object)
        layout._pedb.modeler._add_primitive(new_rect)
        return new_rect

    def delete(self):
        """Delete the rectangle primitive from the layout."""
        # Remove from cache
        self._pedb.modeler._remove_primitive(self)
        self.core.delete()

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
        parameters = self.core.get_parameters()
        representation_type = parameters[0].name.lower()
        parameter1 = Value(parameters[1])
        parameter2 = Value(parameters[2])
        parameter3 = Value(parameters[3])
        parameter4 = Value(parameters[4])
        corner_radius = Value(parameters[5])
        rotation = Value(parameters[6])
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

        return self.core.set_parameters(
            self.representation_type[rep_type],
            Value(param1),
            Value(param2),
            Value(param3),
            Value(param4),
            Value(corner_rad),
            Value(rotation),
        )
