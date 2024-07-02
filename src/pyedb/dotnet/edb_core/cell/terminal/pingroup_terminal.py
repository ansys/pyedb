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


class PinGroupTerminal(Terminal):
    """Manages pin group terminal properties."""

    def __init__(self, pedb, edb_object=None):
        super().__init__(pedb, edb_object)

    def create(self, name, net_name, pin_group_name, is_ref=False):
        """Create a pin group terminal.

        Parameters
        ----------
        name : str
            Name of the terminal.
        net_name : str
            Name of the net.
        pin_group_name : str,
            Name of the pin group.
        is_ref : bool, optional
            Whether it is a reference terminal. The default is ``False``.

        Returns
        -------
        :class:`pyedb.dotnet.edb_core.edb_data.terminals.PinGroupTerminal`
        """
        net_obj = self._pedb.edb_api.cell.net.find_by_name(self._pedb.active_layout, net_name)
        term = self._pedb.edb_api.cell.terminal.PinGroupTerminal.Create(
            self._pedb.active_layout,
            net_obj.api_object,
            name,
            self._pedb.siwave.pin_groups[pin_group_name]._edb_object,
            is_ref,
        )
        term = PinGroupTerminal(self._pedb, term)
        return term if not term.is_null else False

    def pin_group(self):
        """Gets the pin group the terminal refers to."""
        name = self._edb_object.GetPinGroup().GetName()
        return self._pedb.siwave.pin_groups[name]
