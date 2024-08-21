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

from pyedb.dotnet.edb_core.cell.terminal.terminal import Terminal
from pyedb.dotnet.edb_core.edb_data.padstacks_data import EDBPadstackInstance
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
        edb_padstack_instance = self._edb_object.GetParameters()
        if edb_padstack_instance[0]:
            return EDBPadstackInstance(edb_padstack_instance[1], self._pedb).position
        return False

    def create(self, padstack_instance, name=None, layer=None, is_ref=False):
        """Create an edge terminal.

        Parameters
        ----------
        prim_id : int
            Primitive ID.
        point_on_edge : list
            Coordinate of the point to define the edge terminal.
            The point must be on the target edge but not on the two
            ends of the edge.
        terminal_name : str, optional
            Name of the terminal. The default is ``None``, in which case the
            default name is assigned.
        is_ref : bool, optional
            Whether it is a reference terminal. The default is ``False``.

        Returns
        -------
        Edb.Cell.Terminal.EdgeTerminal
        """
        if not name:
            pin_name = padstack_instance._edb_object.GetName()
            refdes = padstack_instance.component.refdes
            name = "{}_{}".format(refdes, pin_name)
            name = generate_unique_name(name)

        if not layer:
            layer = padstack_instance.start_layer

        layer_obj = self._pedb.stackup.signal_layers[layer]

        terminal = self._edb.cell.terminal.PadstackInstanceTerminal.Create(
            self._pedb.active_layout,
            padstack_instance.net.net_object,
            name,
            padstack_instance._edb_object,
            layer_obj._edb_layer,
            isRef=is_ref,
        )
        terminal = PadstackInstanceTerminal(self._pedb, terminal)

        return terminal if not terminal.is_null else False

    def _get_parameters(self):
        """Gets the parameters of the padstack instance terminal."""
        _, padstack_inst, layer_obj = self._edb_object.GetParameters()
        return padstack_inst, layer_obj

    @property
    def padstack_instance(self):
        p_inst, _ = self._get_parameters()
        return self._pedb.layout.find_object_by_id(p_inst.GetId())
