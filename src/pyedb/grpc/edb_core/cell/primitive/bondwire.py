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

from ansys.edb.core.primitive.primitive import (
    BondwireCrossSectionType as GrpcBondwireCrossSectionType,
)
from ansys.edb.core.primitive.primitive import Bondwire as GrpcBondWire
from ansys.edb.core.primitive.primitive import BondwireType as GrpcBondWireType
from ansys.edb.core.utility.value import Value as GrpcValue


class Bondwire(GrpcBondWire):
    """Class representing a bond-wire object."""

    def __init__(self):
        super().__init__(self.msg)

    def __create(self, **kwargs):
        return Bondwire.create(
            self._pedb.layout._edb_object,
            kwargs.get("net"),
            self._bondwire_type[kwargs.get("bondwire_type")],
            kwargs.get("definition_name"),
            kwargs.get("placement_layer"),
            kwargs.get("width"),
            kwargs.get("material"),
            kwargs.get("start_context"),
            kwargs.get("start_layer_name"),
            kwargs.get("start_x"),
            kwargs.get("start_y"),
            kwargs.get("end_context"),
            kwargs.get("end_layer_name"),
            kwargs.get("end_x"),
            kwargs.get("end_y"),
        )

    @property
    def type(self):
        """str: Bondwire-type of a bondwire object. Supported values for setter: `"apd"`, `"jedec4"`, `"jedec5"`,
        `"num_of_type"`"""
        return self.type.name.lower()

    @type.setter
    def type(self, bondwire_type):
        mapping = {
            "apd": GrpcBondWireType.APD,
            "jedec4": GrpcBondWireType.JEDEC4,
            "jedec5": GrpcBondWireType.JEDEC5,
            "num_of_type": GrpcBondWireType.NUM_OF_TYPE,
        }
        self.type = mapping[bondwire_type]

    @property
    def cross_section_type(self):
        """str: Bondwire-cross-section-type of a bondwire object. Supported values for setter: `"round",
        `"rectangle"`"""
        return self.cross_section_type.name

    @cross_section_type.setter
    def cross_section_type(self, bondwire_type):
        mapping = {"round": GrpcBondwireCrossSectionType.ROUND, "rectangle": GrpcBondwireCrossSectionType.RECTANGLE}
        self.cross_section_type = mapping[bondwire_type]

    @property
    def cross_section_height(self):
        """float: Bondwire-cross-section height of a bondwire object."""
        return self.cross_section_height.value

    @cross_section_height.setter
    def cross_section_height(self, height):
        self.cross_section_height = GrpcValue(height)

    def get_trajectory(self):
        """Get trajectory parameters of a bondwire object.

        Returns
        -------
        tuple[float, float, float, float]

        Returns a tuple of the following format:
        **(x1, y1, x2, y2)**
        **x1** : X value of the start point.
        **y1** : Y value of the start point.
        **x1** : X value of the end point.
        **y1** : Y value of the end point.
        """
        return [i.value for i in self.get_trajectory()]

    def set_trajectory(self, x1, y1, x2, y2):
        """Set the parameters of the trajectory of a bondwire.

        Parameters
        ----------
        x1 : float
            X value of the start point.
        y1 : float
            Y value of the start point.
        x2 : float
            X value of the end point.
        y2 : float
            Y value of the end point.
        """
        values = [GrpcValue(i) for i in [x1, y1, x2, y2]]
        self.set_trajectory(*values)

    @property
    def width(self):
        """:class:`Value <ansys.edb.utility.Value>`: Width of a bondwire object."""
        return self.width.value

    @width.setter
    def width(self, width):
        self.width = GrpcValue(width)
