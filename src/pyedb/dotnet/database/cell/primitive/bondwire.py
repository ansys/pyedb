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

from pyedb.dotnet.database.cell.primitive.primitive import Primitive


class Bondwire(Primitive):
    """Class representing a bondwire object."""

    def __init__(self, pedb, edb_object=None, **kwargs):
        super().__init__(pedb, edb_object)
        if self._edb_object is None:
            self._edb_object = self.__create(**kwargs)

    def __create(self, **kwargs):
        return self._pedb._edb.Cell.Primitive.Bondwire.Create(
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

    def get_material(self, evaluated=True):
        """Get material of the bondwire.

        Parameters
        ----------
        evaluated : bool, optional
            True if an evaluated material name is wanted.

        Returns
        -------
        str
            Material name.
        """
        return self._edb_object.GetMaterial(evaluated)

    def set_material(self, material):
        """Set the material of a bondwire.

        Parameters
        ----------
        material : str
            Material name.
        """
        self._edb_object.SetMaterial(material)

    @property
    def type(self):
        """:class:`BondwireType`: Bondwire-type of a bondwire object."""

        type_name = self._edb_object.GetType()
        return [i for i, j in self._bondwire_type.items() if j == type_name][0]

    @type.setter
    def type(self, bondwire_type):
        self._edb_object.SetType(self._bondwire_type[bondwire_type])

    @property
    def cross_section_type(self):
        """:class:`BondwireCrossSectionType`: Bondwire-cross-section-type of a bondwire object."""
        cs_type = self._edb_object.GetCrossSectionType()
        return [i for i, j in self._bondwire_cross_section_type.items() if j == cs_type][0]

    @cross_section_type.setter
    def cross_section_type(self, bondwire_type):
        self._edb_object.SetCrossSectionType(self._bondwire_cross_section_type[bondwire_type])

    @property
    def cross_section_height(self):
        """:class:`Value <ansys.edb.utility.Value>`: Bondwire-cross-section height of a bondwire object."""
        return self._edb_object.GetCrossSectionHeight().ToDouble()

    @cross_section_height.setter
    def cross_section_height(self, height):
        self._edb_object.SetCrossSectionHeight(self._pedb.edb_value(height))

    def get_definition_name(self, evaluated=True):
        """Get definition name of a bondwire object.

        Parameters
        ----------
        evaluated : bool, optional
            True if an evaluated (in variable namespace) material name is wanted.

        Returns
        -------
        str
            Bondwire name.
        """
        return self._edb_object.GetDefinitionName(evaluated)

    def set_definition_name(self, definition_name):
        """Set the definition name of a bondwire.

        Parameters
        ----------
        definition_name : str
            Bondwire name to be set.
        """
        self._edb_object.SetDefinitionName(definition_name)

    def get_trajectory(self):
        """Get trajectory parameters of a bondwire object.

        Returns
        -------
        tuple[
            :class:`Value <ansys.edb.utility.Value>`,
            :class:`Value <ansys.edb.utility.Value>`,
            :class:`Value <ansys.edb.utility.Value>`,
            :class:`Value <ansys.edb.utility.Value>`
        ]

            Returns a tuple of the following format:

            **(x1, y1, x2, y2)**

            **x1** : X value of the start point.

            **y1** : Y value of the start point.

            **x1** : X value of the end point.

            **y1** : Y value of the end point.
        """
        return [i.ToDouble() for i in self._edb_object.GetTrajectory() if not isinstance(i, bool)]

    def set_trajectory(self, x1, y1, x2, y2):
        """Set the parameters of the trajectory of a bondwire.

        Parameters
        ----------
        x1 : :class:`Value <ansys.edb.utility.Value>`
            X value of the start point.
        y1 : :class:`Value <ansys.edb.utility.Value>`
            Y value of the start point.
        x2 : :class:`Value <ansys.edb.utility.Value>`
            X value of the end point.
        y2 : :class:`Value <ansys.edb.utility.Value>`
            Y value of the end point.
        """
        values = [self._pedb.edb_value(i) for i in [x1, y1, x2, y2]]
        self._edb_object.SetTrajectory(*values)

    @property
    def width(self):
        """:class:`Value <ansys.edb.utility.Value>`: Width of a bondwire object."""
        return self._edb_object.GetWidth().ToDouble()

    @width.setter
    def width(self, width):
        self._edb_object.SetWidth(self._pedb.edb_value(width))

    def set_start_elevation(self, layer, start_context=None):
        """Set the start elevation of a bondwire.

        Parameters
        ----------
        start_context : :class:`CellInstance <ansys.edb.hierarchy.CellInstance>`
            Start cell context of the bondwire. None means top level.
        layer : str or :class:`Layer <ansys.edb.layer.Layer>`
            Start layer of the bondwire.
        """
        self._edb_object.SetStartElevation(start_context, layer)

    def set_end_elevation(self, layer, end_context=None):
        """Set the end elevation of a bondwire.

        Parameters
        ----------
        end_context : :class:`CellInstance <ansys.edb.hierarchy.CellInstance>`
            End cell context of the bondwire. None means top level.
        layer : str or :class:`Layer <ansys.edb.layer.Layer>`
            End layer of the bondwire.
        """
        self._edb_object.SetEndElevation(end_context, layer)
