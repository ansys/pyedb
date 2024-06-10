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

    It inherits EDB Object properties.

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

        Expected output is among ``"Circle"``, ``"Rectangle"``,``"Polygon"``,``"Path"`` or ``"Bondwire"``.

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
        """Get the primitive net name.

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
        """Get the primitive layer name.

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
