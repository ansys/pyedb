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

if TYPE_CHECKING:
    from pyedb.grpc.database.net.net import Net
import re

from ansys.edb.core.net.differential_pair import (
    DifferentialPair as GrpcDifferentialPair,
)


class DifferentialPairs:
    def __init__(self, pedb):
        self._pedb = pedb

    @property
    def items(self) -> dict[str, any]:
        """Extended nets.

        Returns
        -------
        dict[str, :class:`pyedb.dotnet.database.edb_data.nets_data.EDBDifferentialPairData`]
            Dictionary of extended nets.
        """
        diff_pairs = {}
        for diff_pair in self._pedb.layout.differential_pairs:
            diff_pairs[diff_pair.name] = DifferentialPair(self._pedb, diff_pair)
        return diff_pairs

    def create(self, name, net_p, net_n):
        # type: (str, str, str) -> DifferentialPair
        """

        Parameters
        ----------
        name : str
            Name of the differential pair.
        net_p : str
            Name of the positive net.
        net_n : str
            Name of the negative net.

        Returns
        -------
        :class:`pyedb.dotnet.database.edb_data.nets_data.EDBDifferentialPairData`
        """
        if name in self.items:
            self._pedb.logger.error("{} already exists.".format(name))
            return False
        GrpcDifferentialPair.create(layout=self._pedb.layout.core, name=name, pos_net=net_p, neg_net=net_n)
        return self.items[name]

    def auto_identify(self, positive_differentiator="_P", negative_differentiator="_N") -> list[str]:
        """Auto identify differential pairs by naming conversion.

        Parameters
        ----------
        positive_differentiator: str, optional
            Differentiator of the positive net. The default is ``"_P"``.
        negative_differentiator: str, optional
            Differentiator of the negative net. The default is ``"_N"``.

        Returns
        -------
        list
            A list containing identified differential pair names.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder", edbversion="2025.2")
        >>> edb_nets = edbapp.differential_pairs.auto_identify()
        """
        nets = self._pedb.nets.nets
        pos_net = []
        neg_net = []
        for name, _ in nets.items():
            if name.endswith(positive_differentiator):
                pos_net.append(name)
            elif name.endswith(negative_differentiator):
                neg_net.append(name)
            else:
                pass

        temp = []
        for p in pos_net:
            pattern_p = r"^(.+){}$".format(positive_differentiator)
            match_p = re.findall(pattern_p, p)[0]

            for n in neg_net:
                pattern_n = r"^(.+){}$".format(negative_differentiator)
                match_n = re.findall(pattern_n, n)[0]

                if match_p == match_n:
                    diff_name = "DIFF_{}".format(match_p)
                    self.create(diff_name, p, n)
                    temp.append(diff_name)
        return temp


class DifferentialPair(GrpcDifferentialPair):
    """Manages EDB functionalities for a primitive.
    It inherits EDB object properties.
    """

    def __init__(self, pedb, edb_object):
        super().__init__(edb_object.msg)
        self._pedb = pedb

    @property
    def positive_net(self) -> Net:
        """Positive Net."""
        from pyedb.grpc.database.net.net import Net

        return Net(self._pedb, super().positive_net)

    @property
    def negative_net(self) -> Net:
        """Negative Net."""
        from pyedb.grpc.database.net.net import Net

        return Net(self._pedb, super().negative_net)
