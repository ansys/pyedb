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

from pyedb.dotnet.database.cell.terminal.edge_terminal import EdgeTerminal
from pyedb.dotnet.database.cell.terminal.terminal import Terminal
from pyedb.dotnet.database.general import convert_py_list_to_net_list


class BundleTerminal(Terminal):
    """Manages bundle terminal properties.

    Parameters
    ----------
    pedb : pyedb.edb.Edb
        EDB object from the ``Edblib`` library.
    edb_object : Ansys.Ansoft.Edb.Cell.Terminal.BundleTerminal
        BundleTerminal instance from EDB.
    """

    def __init__(self, pedb, edb_object):
        super().__init__(pedb, edb_object)

    @property
    def terminals(self):
        """Get terminals belonging to this excitation."""
        return [EdgeTerminal(self._pedb, i) for i in list(self._edb_object.GetTerminals())]

    def decouple(self):
        """Ungroup a bundle of terminals."""
        return self._edb_object.Ungroup()

    @classmethod
    def create(cls, pedb, name, terminals):
        terminal_list = [pedb.terminals[i]._edb_object for i in terminals]
        edb_list = convert_py_list_to_net_list(terminal_list, pedb._edb.Cell.Terminal.Terminal)
        _edb_boundle_terminal = pedb._edb.Cell.Terminal.BundleTerminal.Create(edb_list)
        if _edb_boundle_terminal.IsNull():  # pragma no cover
            raise ValueError(f"Failed to create bundle terminal: {name}.")
        _edb_boundle_terminal.SetName(name)
        pos, neg = list(_edb_boundle_terminal.GetTerminals())
        pos.SetName(name + ":T1")
        neg.SetName(name + ":T2")
        return pedb.terminals[name]
