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
from pyedb.dotnet.edb_core.general import convert_py_list_to_net_list


class EdgeTerminal(Terminal):
    def __init__(self, pedb, edb_object):
        super().__init__(pedb, edb_object)

    def couple_ports(self, port):
        """Create a bundle wave port.

        Parameters
        ----------
        port : :class:`dotnet.edb_core.ports.WavePort`, :class:`dotnet.edb_core.ports.GapPort`, list, optional
            Ports to be added.

        Returns
        -------
        :class:`dotnet.edb_core.ports.BundleWavePort`

        """
        if not isinstance(port, (list, tuple)):
            port = [port]
        temp = [self._edb_object]
        temp.extend([i._edb_object for i in port])
        edb_list = convert_py_list_to_net_list(temp, self._edb.cell.terminal.Terminal)
        _edb_bundle_terminal = self._edb.cell.terminal.BundleTerminal.Create(edb_list)
        return self._pedb.ports[self.name]
