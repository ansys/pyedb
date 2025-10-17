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

from pyedb.dotnet.database.cell.terminal.terminal import Terminal


class PointTerminal(Terminal):
    """Manages point terminal properties."""

    def __init__(self, pedb, edb_object=None):
        super().__init__(pedb, edb_object)
        self._pedb = pedb

    def create(self, name, net, location, layer, is_ref=False):
        """Create a point terminal.

        Parameters
        ----------
        name : str
            Name of the terminal.
        net : str
            Name of the net.
        location : list
            Location of the terminal.
        layer : str
            Name of the layer.
        is_ref : bool, optional
            Whether it is a reference terminal.

        Returns
        -------
        :class:`pyedb.dotnet.database.edb_data.terminals.PointTerminal`
        """
        terminal = self._pedb.core.Cell.Terminal.PointTerminal.Create(
            self._pedb.active_layout,
            self._pedb.layout.find_net_by_name(net)._edb_object,
            name,
            self._pedb.point_data(*location),
            self._pedb.stackup[layer]._edb_layer,
            is_ref,
        )
        terminal = PointTerminal(self._pedb, terminal)
        if terminal.is_null:
            msg = f"Failed to create terminal. "
            if name in self._pedb.terminals:
                msg += f"Terminal {name} already exists."
            raise Exception(msg)
        else:
            return terminal

    @property
    def layer(self):
        """Get layer of the terminal."""
        _, _, layer = self._edb_object.GetParameters()
        return self._pedb.stackup.all_layers[layer.GetName()]

    @layer.setter
    def layer(self, value):
        layer = self._pedb.stackup.layers[value]._edb_layer
        point_data = self._pedb.point_data(*self.location)
        self._edb_object.SetParameters(point_data, layer)

    @property
    def location(self):
        """Location of the terminal."""

        _, point_data, _ = self._edb_object.GetParameters()
        return [point_data.X.ToDouble(), point_data.Y.ToDouble()]

    @location.setter
    def location(self, value):
        layer = self.layer
        self._edb_object.SetParameters(self._pedb.point_data(*value), layer._edb_object)
