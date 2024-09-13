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

from ansys.edb.core.terminal.terminals import (
    PadstackInstanceTerminal as GrpcPadstackInstanceTerminal,
)

from pyedb.generic.general_methods import generate_unique_name


class PadstackInstanceTerminal(GrpcPadstackInstanceTerminal):
    """Manages bundle terminal properties."""

    def __init__(self, pedb):
        super().__init__(self.msg)
        self._pedb = pedb

    @property
    def position(self):
        """Return terminal position.
        Returns
        -------
        Position [x,y] : [float, float]
        """
        pos_x, pos_y, rotation = self.padstack_instance.get_position_and_rotation()
        return [pos_x.value, pos_y.value]

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
            pin_name = padstack_instance.name
            refdes = padstack_instance.component.refdes
            name = "{}_{}".format(refdes, pin_name)
            name = generate_unique_name(name)

        if not layer:
            layer = padstack_instance.start_layer

        layer_obj = self._pedb.stackup.signal_layers[layer]

        terminal = PadstackInstanceTerminal.create(
            layout=self._pedb.active_layout,
            net=padstack_instance.net,
            name=name,
            padstack_instance=padstack_instance,
            layer=layer_obj,
            isRef=is_ref,
        )
        # terminal = PadstackInstanceTerminal(self._pedb, terminal)
        if terminal.is_null:
            msg = f"Failed to create terminal. "
            if name in self._pedb.terminals:
                msg += f"Terminal {name} already exists."
            raise Exception(msg)
        else:
            return terminal

    @property
    def padstack_instance(self):
        p_inst, _ = self.params
        return p_inst

    @property
    def location(self):
        p_inst, _ = self.params
        pos_x, pos_y, _ = p_inst.get_position_and_rotation()
        return [pos_x.value, pos_y.value]
