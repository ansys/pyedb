# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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
from pyedb.generic.general_methods import generate_unique_name


class PadstackInstanceTerminal(Terminal):
    """Manages bundle terminal properties."""

    def __init__(self, pedb, edb_object):
        super().__init__(pedb, edb_object)

    @property
    def position(self):
        """Return terminal position.
        Returns
        -------
        Position [x,y] : [float, float]

        """
        from pyedb.dotnet.database.edb_data.padstacks_data import EDBPadstackInstance

        edb_padstack_instance = self._edb_object.GetParameters()
        if edb_padstack_instance[0]:
            return EDBPadstackInstance(edb_padstack_instance[1], self._pedb).position
        return False

    @property
    def location(self):
        """Location of the padstack instance."""
        return self.position

    @classmethod
    def create(cls, edb, padstack_instance, name=None, layer=None, is_ref=False):
        """Create an edge terminal.

        Parameters
        ----------
        edb : pyedb.dotnet.DotNet.DotNet
        name : str, optional
            Name of the terminal. The default is ``None``, in which case the
        padstack_instance : PadstackInstance object
        layer : str, optional
            Layer name for the terminal. The default is ``None``, in which case the
            start layer of the padstack instance will be used.
        is_ref : bool, optional
            Whether the terminal is a reference terminal. The default is ``False``.

        Returns
        -------
        Edb.Cell.Terminal.EdgeTerminal

        """
        if not name:
            pin_name = padstack_instance.name
            refdes = padstack_instance.component_name
            name = "{}_{}".format(refdes, pin_name)
            name = generate_unique_name(name)

        if not layer:
            layer = padstack_instance.start_layer

        layer_obj = edb.stackup.signal_layers[layer]

        terminal = edb._edb.Cell.Terminal.PadstackInstanceTerminal.Create(
            edb.active_layout,
            padstack_instance.net.net_object,
            name,
            padstack_instance.core,
            layer_obj.core,
            isRef=is_ref,
        )
        terminal = PadstackInstanceTerminal(edb, terminal)
        if terminal.is_null:
            msg = f"Failed to create terminal. "
            if name in edb.terminals:
                msg += f"Terminal {name} already exists."
            raise Exception(msg)
        else:
            return terminal

    def _get_parameters(self):
        """Gets the parameters of the padstack instance terminal."""
        _, padstack_inst, layer_obj = self._edb_object.GetParameters()
        return padstack_inst, layer_obj

    @property
    def padstack_instance(self):
        p_inst, _ = self._get_parameters()
        return self._pedb.layout.find_object_by_id(p_inst.GetId())

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
