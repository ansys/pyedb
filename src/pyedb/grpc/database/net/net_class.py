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

from __future__ import annotations

from typing import TYPE_CHECKING

from ansys.edb.core.net.net_class import NetClass as GrpcNetClass

if TYPE_CHECKING:
    from pyedb.grpc.database.net.net import Net


class NetClass(GrpcNetClass):
    """Manages EDB functionalities for a primitives.
    It inherits EDB Object properties.

    Examples
    --------
    >>> from pyedb import Edb
    >>> edb = Edb(myedb, edbversion="2025.1")
    >>> edb.net_classes
    """

    def __init__(self, pedb, net_class):
        super().__init__(net_class.msg)
        self._pedb = pedb

    @property
    def nets(self):
        """Net list.

        Returns
        -------
        List[:class:`Net <pyedb.grpc.database.net.net.Net>`].
            List of Net object.
        """
        from pyedb.grpc.database.net.net import Net

        return [Net(self._pedb, i) for i in super().nets]

    def add_net(self, net):
        """Add a net to the net class.

        Returns
        -------
        bool
        """
        if isinstance(net, str):
            from pyedb.grpc.database.net.net import Net

            net = Net.find_by_name(self._pedb.active_layout, name=net)
        if isinstance(net, Net) and not net.is_null:
            self.add_net(net)
            return True
        return False

    def contains_net(self, net) -> bool:
        """
        Determine if a net exists in the net class.

        Parameters
        ----------
        net : str or Net
            The net to check. This can be a string representing the net name or a `Net` object.

        Returns
        -------
        bool
            True if the net exists in the net class, False otherwise.

        """

        if isinstance(net, str):
            net = Net.find_by_name(self._pedb.active_layout, name=net)
        return super().contains_net(net)

    def remove_net(self, net):
        """Remove net.

        Returns
        -------
        bool
        """

        if isinstance(net, str):
            net = Net.find_by_name(self._pedb.active_layout, name=net)
        if isinstance(net, Net) and not net.is_null:
            self.remove_net(net)
            return True
        return False
