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

    @property
    def corner_radius(self):
        """Get corner radius.

        Returns
        -------
        float
            Corner radius.
        """
        return self.core.get_parameters()[5].value

    @corner_radius.setter
    def corner_radius(self, value):
        parameters = self.get_parameters()
        self.set_parameters(
            rep_type=parameters[0],
            param1=parameters[1],
            param2=parameters[2],
            param3=parameters[3],
            param4=parameters[4],
            corner_rad=Value(value),
            rotation=parameters[6],
        )

    @property
    def rotation(self):
        """Get rotation.

        Returns
        -------
        float
            Rotation.
        """
        return self.core.get_parameters()[6].value

    @rotation.setter
    def rotation(self, value):
        parameters = self.get_parameters()
        self.set_parameters(
            rep_type=parameters[0],
            param1=parameters[1],
            param2=parameters[2],
            param3=parameters[3],
            param4=parameters[4],
            corner_rad=parameters[5],
            rotation=Value(value),
        )

    @property
    def width(self):
        """Get rectangle width.

        Returns
        -------
        float
            Rectangle width.
        """
        if self.representation_type == "center_width_height":
            return self.core.get_parameters()[3].value
        elif self.representation_type == "lower_left_upper_right":
            lower_left_x = self.core.get_parameters()[1].value
            upper_right_x = self.core.get_parameters()[3].value
            return upper_right_x - lower_left_x
        else:
            return None

    @width.setter
    def width(self, value):
        parameters = self.get_parameters()
        self.set_parameters(
            rep_type=parameters[0],
            param1=parameters[1],
            param2=parameters[2],
            param3=Value(value),
            param4=parameters[4],
            corner_rad=parameters[5],
            rotation=parameters[6],
        )

    @property
    def height(self):
        """Get rectangle height.

        Returns
        -------
        float
            Rectangle height.
        """
        if self.representation_type == "center_width_height":
            return self.core.get_parameters()[4].value
        elif self.representation_type == "lower_left_upper_right":
            lower_left_y = self.core.get_parameters()[2].value
            upper_right_y = self.core.get_parameters()[4].value
            return upper_right_y - lower_left_y
        else:
            return None

    @height.setter
    def height(self, value):
        parameters = self.get_parameters()
        self.set_parameters(
            rep_type=parameters[0],
            param1=parameters[1],
            param2=parameters[2],
            param3=parameters[3],
            param4=Value(value),
            corner_rad=parameters[5],
            rotation=parameters[6],
        )

    def duplicate_across_layers(self, layers) -> bool:
        """Duplicate across layer a primitive object.

        Parameters:

        layers: list
            list of str, with layer names

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        for layer in layers:
            if layer in self._pedb.stackup.layers:
                duplicate_rectangle = self.create(
                    layout=self._pedb.active_layout,
                    layer=layer,
                    net=self.net.name,
                    param1=self.center[0],
                    param2=self.center[1],
                    param3=self.width,
                    param4=self.height,
                    rep_type="center_width_height",
                    corner_rad=self.corner_radius,
                    rotation=self.rotation,
                )
                if duplicate_rectangle:
                    from pyedb.grpc.database.primitive.polygon import Polygon

                    for void in self.voids:
                        duplicate_void = Polygon.create(
                            layout=self._pedb.active_layout,
                            layer=layer,
                            net=self.net.name,
                            polygon_data=void.polygon_data,
                        )
                        duplicate_rectangle.add_void(duplicate_void)
            else:
                return False
        return True
