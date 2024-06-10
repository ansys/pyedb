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

from pyedb.dotnet.edb_core.cell.layout_obj import Connectable


class Primitive(Connectable):
    """Manages EDB functionalities for a primitives.
    It Inherits EDB Object properties.

    Examples
    --------
    >>> from pyedb import Edb
    >>> edb = Edb(myedb, edbversion="2021.2")
    >>> edb_prim = edb.modeler.primitives[0]
    >>> edb_prim.is_void # Class Property
    >>> edb_prim.IsVoid() # EDB Object Property
    """

    def __init__(self, pedb, edb_object):
        super().__init__(pedb, edb_object)
        self._app = self._pedb
        self._core_stackup = pedb.stackup
        self._core_net = pedb.nets
        self.primitive_object = self._edb_object

    @property
    def type(self):
        """Return the type of the primitive.
        Allowed outputs are ``"Circle"``, ``"Rectangle"``,``"Polygon"``,``"Path"`` or ``"Bondwire"``.

        Returns
        -------
        str
        """
        try:
            return self._edb_object.GetPrimitiveType().ToString()
        except AttributeError:  # pragma: no cover
            return ""

    @property
    def net_name(self):
        """Get or Set the primitive net name.

        Returns
        -------
        str
        """
        return self.net.GetName()

    @net_name.setter
    def net_name(self, name):
        if isinstance(name, str):
            net = self._app.nets.nets[name].net_object
            self.primitive_object.SetNet(net)
        else:
            try:
                if isinstance(name, str):
                    self.net = name
                elif isinstance(name, NetDotNet):
                    self.net = name.name
            except:  # pragma: no cover
                self._app.logger.error("Failed to set net name.")

    @property
    def layer(self):
        """Get the primitive edb layer object."""
        try:
            layer_name = self.primitive_object.GetLayer().GetName()
            return self._pedb.stackup.layers[layer_name]
        except (KeyError, AttributeError):  # pragma: no cover
            return None

    @property
    def layer_name(self):
        """Get or Set the primitive layer name.

        Returns
        -------
        str
        """
        try:
            return self.layer.name
        except (KeyError, AttributeError):  # pragma: no cover
            return None

    @layer_name.setter
    def layer_name(self, val):
        layer_list = list(self._core_stackup.layers.keys())
        if isinstance(val, str) and val in layer_list:
            layer = self._core_stackup.layers[val]._edb_layer
            if layer:
                self.primitive_object.SetLayer(layer)
            else:
                raise AttributeError("Layer {} not found.".format(val))
        elif isinstance(val, type(self._core_stackup.layers[layer_list[0]])):
            try:
                self.primitive_object.SetLayer(val._edb_layer)
            except:
                raise AttributeError("Failed to assign new layer on primitive.")
        else:
            raise AttributeError("Invalid input value")

    @property
    def is_void(self):
        """Either if the primitive is a void or not.

        Returns
        -------
        bool
        """
        try:
            return self._edb_object.IsVoid()
        except AttributeError:  # pragma: no cover
            return None

    def get_connected_objects(self):
        """Get connected objects.

        Returns
        -------
        list
        """
        return self._pedb.get_connected_objects(self._layout_obj_instance)


class Bondwire(Primitive):
    """Class representing a bondwire object."""

    def __init__(self, pedb, edb_object=None, **kwargs):
        super().__init__(self, pedb, edb_object)
        if self._edb_object is None:
            self._edb_object = self.__create(**kwargs)

    def __create(
        self,
        layout,
        bondwire_type,
        definition_name,
        placement_layer,
        width,
        material,
        start_context,
        start_layer_name,
        start_x,
        start_y,
        end_context,
        end_layer_name,
        end_x,
        end_y,
        net,
    ):
        """Create a bondwire object.

        Parameters
        ----------
        layout : :class:`Layout <ansys.edb.layout.Layout>`
            Layout this bondwire will be in.
        bondwire_type : :class:`BondwireType`
            Type of bondwire: kAPDBondWire or kJDECBondWire types.
        definition_name : str
            Bondwire definition name.
        placement_layer : str
            Layer name this bondwire will be on.
        width : :class:`Value <ansys.edb.utility.Value>`
            Bondwire width.
        material : str
            Bondwire material name.
        start_context : :class:`CellInstance <ansys.edb.hierarchy.CellInstance>`
            Start context: None means top level.
        start_layer_name : str
            Name of start layer.
        start_x : :class:`Value <ansys.edb.utility.Value>`
            X value of start point.
        start_y : :class:`Value <ansys.edb.utility.Value>`
            Y value of start point.
        end_context : :class:`CellInstance <ansys.edb.hierarchy.CellInstance>`
            End context: None means top level.
        end_layer_name : str
            Name of end layer.
        end_x : :class:`Value <ansys.edb.utility.Value>`
            X value of end point.
        end_y : :class:`Value <ansys.edb.utility.Value>`
            Y value of end point.
        net : str or :class:`Net <ansys.edb.net.Net>` or None
            Net of the Bondwire.

        Returns
        -------
        :class:`pyedb.dotnet.edb_core.dotnet.primitive.BondwireDotNet`
            Bondwire object created.
        """
        return self._pedb._edb.Cell.Primitive.Bondwire.Create(
                layout,
                net,
                bondwire_type,
                definition_name,
                placement_layer,
                width,
                material,
                start_context,
                start_layer_name,
                start_x,
                start_y,
                end_context,
                end_layer_name,
                end_x,
                end_y,
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
        return self._edb_object.GetType()

    @type.setter
    def type(self, bondwire_type):
        self._edb_object.SetType(bondwire_type)

    @property
    def cross_section_type(self):
        """:class:`BondwireCrossSectionType`: Bondwire-cross-section-type of a bondwire object."""
        return self._edb_object.GetCrossSectionType()

    @cross_section_type.setter
    def cross_section_type(self, bondwire_type):
        self._edb_object.SetCrossSectionType(bondwire_type)

    @property
    def cross_section_height(self):
        """:class:`Value <ansys.edb.utility.Value>`: Bondwire-cross-section height of a bondwire object."""
        return self._edb_object.GetCrossSectionHeight()

    @cross_section_height.setter
    def cross_section_height(self, height):
        self._edb_object.SetCrossSectionHeight(height)

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

    def get_traj(self):
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
        return self._edb_object.GetTraj()

    def set_traj(self, x1, y1, x2, y2):
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
        self._edb_object.SetTraj(x1, y1, x2, y2)

    @property
    def width(self):
        """:class:`Value <ansys.edb.utility.Value>`: Width of a bondwire object."""
        return self._edb_object.GetWidthValue()

    @width.setter
    def width(self, width):
        self._edb_object.SetWidthValue(width)

    def get_start_elevation(self, start_context):
        """Get the start elevation layer of a bondwire object.

        Parameters
        ----------
        start_context : :class:`CellInstance <ansys.edb.hierarchy.CellInstance>`
            Start cell context of the bondwire.

        Returns
        -------
        :class:`Layer <ansys.edb.layer.Layer>`
            Start context of the bondwire.
        """
        return self._edb_object.GetStartElevation(start_context)

    def set_start_elevation(self, start_context, layer):
        """Set the start elevation of a bondwire.

        Parameters
        ----------
        start_context : :class:`CellInstance <ansys.edb.hierarchy.CellInstance>`
            Start cell context of the bondwire. None means top level.
        layer : str or :class:`Layer <ansys.edb.layer.Layer>`
            Start layer of the bondwire.
        """
        self._edb_object.SetStartElevation(start_context, layer)

    def get_end_elevation(self, end_context):
        """Get the end elevation layer of a bondwire object.

        Parameters
        ----------
        end_context : :class:`CellInstance <ansys.edb.hierarchy.CellInstance>`
            End cell context of the bondwire.

        Returns
        -------
        :class:`Layer <ansys.edb.layer.Layer>`
            End context of the bondwire.
        """
        return self._edb_object.GetEndElevation(end_context)

    def set_end_elevation(self, end_context, layer):
        """Set the end elevation of a bondwire.

        Parameters
        ----------
        end_context : :class:`CellInstance <ansys.edb.hierarchy.CellInstance>`
            End cell context of the bondwire. None means top level.
        layer : str or :class:`Layer <ansys.edb.layer.Layer>`
            End layer of the bondwire.
        """
        self._edb_object.SetEndElevation(end_context, layer)