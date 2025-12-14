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

from ansys.edb.core.primitive.bondwire import (
    Bondwire as GrpcBondWire,
    BondwireCrossSectionType as GrpcBondwireCrossSectionType,
    BondwireType as GrpcBondWireType,
)

from pyedb.grpc.database.utility.value import Value


class Bondwire:
    """Class representing a bond-wire object."""

    def __init__(self, _pedb, edb_object):
        self.core = edb_object
        self._pedb = _pedb

    @classmethod
    def create(
        cls,
        layout,
        definition_name: str,
        placement_layer: str,
        start_layer_name: str,
        start_x: float,
        start_y: float,
        end_layer_name: str,
        end_x: float,
        end_y: float,
        net: str,
        material: str = "copper",
        bondwire_type: str = "jedec4",
        width=30e-6,
        start_cell_inst=None,
        end_cell_inst=None,
    ) -> "Bondwire":
        """Create a bondwire object.

        Parameters
        ----------
        layout : :class: <Layout `pyedb.grpc.database.layout.layout.Layout`>
            Layout object associated with the bondwire.
        bondwire_type : str, optional
            Type of bondwire. Supported values are `"jedec4"`, `"jedec5"`, and `"apd"`. Default is `"jedec4"`.
        definition_name : str
            Definition name of the bondwire. Default is an empty string.
        placement_layer : str
            Placement layer name of the bondwire.
        width : float, optional
            Width of the bondwire. Default is 30um.
        material : str, optional
            Material of the bondwire. Default is "copper".
        start_layer_name : str, optional
            Start layer name of the bondwire. Default is None.
        start_x : float, optional
            X-coordinate of the start point of the bondwire. Default is 0.0.
        start_y : float, optional
            Y-coordinate of the start point of the bondwire. Default is 0.0.
        end_layer_name : str, optional
            End layer name of the bondwire. Default is None.
        end_x : float, optional
            X-coordinate of the end point of the bondwire. Default is 0.0.
        end_y : float, optional
            Y-coordinate of the end point of the bondwire. Default is 0.0.
        net : :class: <Net `pyedb.grpc.database.net.net.Net`>,
            Net object associated with the bondwire. Default is None.
        start_cell_inst : :class: <Component `pyedb.grpc.database.hierarchy.component
            .Component`>, optional
            Start cell instance context for the bondwire. Default is None.
        end_cell_inst : :class: <Component
            `pyedb.grpc.database.hierarchy.component.Component`>, optional
            End cell instance context for the bondwire. Default is None.


        Returns
        -------
        Bondwire
            The created bondwire object.

        """
        if bondwire_type == "jedec4":
            bondwire_type = GrpcBondWireType.JEDEC4
        elif bondwire_type == "jedec5":
            bondwire_type = GrpcBondWireType.JEDEC5
        elif bondwire_type == "apd":
            bondwire_type = GrpcBondWireType.APD
        else:
            bondwire_type = GrpcBondWireType.JEDEC4
        if material not in layout._pedb.materials.materials:
            layout._pedb.materials.add_conductor_material(material)
            layout._pedb.logger("Material {material} not found. Added to the material library.")
        core_bondwire = GrpcBondWire.create(
            layout=layout.core,
            bondwire_type=bondwire_type,
            definition_name=definition_name,
            placement_layer=placement_layer,
            width=Value(width),
            material=material,
            start_layer_name=start_layer_name,
            start_x=Value(start_x),
            start_y=Value(start_y),
            end_layer_name=end_layer_name,
            end_x=Value(end_x),
            end_y=Value(end_y),
            net=net,
            end_context=end_cell_inst,
            start_context=start_cell_inst,
        )

        return cls(layout._pedb, core_bondwire)

    @property
    def id(self):
        return self.core.edb_uid

    @property
    def edb_uid(self):
        return self.core.edb_uid

    @property
    def material(self):
        """Bondwire material

        Returns
        -------
        str
            Material name.

        """
        return self.core.get_material().value

    @material.setter
    def material(self, value):
        self.core.set_material(value)

    @property
    def type(self):
        """str: Bondwire-type of a bondwire object. Supported values for setter: `"apd"`, `"jedec4"`, `"jedec5"`,
        `"num_of_type"`"""
        return self.core.type.name.lower()

    @type.setter
    def type(self, bondwire_type):
        mapping = {
            "apd": GrpcBondWireType.APD,
            "jedec4": GrpcBondWireType.JEDEC4,
            "jedec5": GrpcBondWireType.JEDEC5,
            "num_of_type": GrpcBondWireType.NUM_OF_TYPE,
        }
        self.core.type = mapping[bondwire_type]

    @property
    def cross_section_type(self):
        """str: Bondwire-cross-section-type of a bondwire object. Supported values for setter: `"round",
        `"rectangle"`

        Returns
        -------
        str
            cross section type.
        """
        return self.core.cross_section_type.name.lower()

    @cross_section_type.setter
    def cross_section_type(self, cross_section_type):
        mapping = {"round": GrpcBondwireCrossSectionType.ROUND, "rectangle": GrpcBondwireCrossSectionType.RECTANGLE}
        self.core.cross_section_type = mapping[cross_section_type]

    @property
    def cross_section_height(self):
        """float: Bondwire-cross-section height of a bondwire object.

        Returns
        -------
        float
            Cross section height.
        """
        return Value(self.core.cross_section_height)

    @cross_section_height.setter
    def cross_section_height(self, cross_section_height):
        self.core.cross_section_height = Value(cross_section_height)

    @property
    def width(self):
        """:class:`Value <ansys.edb.utility.Value>`: Width of a bondwire object.

        Returns
        -------
        float
            Width value.
        """
        return Value(self.core.width)

    @width.setter
    def width(self, width):
        self.core.width = Value(width)

    def get_material(self):
        """Get the bondwire material.

        Returns
        -------
        str
            Material name.
        """
        return self.core.get_material().value

    def set_material(self, material):
        """Set the bondwire material.

        Parameters
        ----------
        material : str
            Material name.
        """
        self.core.set_material(material)

    def get_definition_name(self) -> str:
        """Get the bondwire definition name.

        Returns
        -------
        str
            Definition name.
        """
        return self.core.get_definition_name()

    def set_definition_name(self, definition_name):
        """Set the bondwire definition name.

        Parameters
        ----------
        definition_name : str
            Definition name.
        """
        self.core.set_definition_name(definition_name)
