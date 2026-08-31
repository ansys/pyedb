# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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
    from pyedb.grpc.database.layout.layout import Layout
    from pyedb.grpc.database.net.net import Net
import re

from ansys.edb.core.net.differential_pair import (
    DifferentialPair as CoreDifferentialPair,
)


class DifferentialPairs:
    """DifferentialPairs class manages EDB functionalities for differential pairs."""

    def __init__(self, pedb):
        self._pedb = pedb

    @property
    def items(self) -> dict[str, DifferentialPair]:
        """Extended nets.

        Returns
        -------
        dict[str, :class:`pyedb.dotnet.database.edb_data.nets_data.EDBDifferentialPairData`]
            Dictionary of extended nets.
        """
        return {diff_pair.name: diff_pair for diff_pair in self._pedb.layout.differential_pairs}

    def create(self, name: str, net_p: str, net_n: str) -> DifferentialPair | bool:
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
        CoreDifferentialPair.create(layout=self._pedb.layout.core, name=name, pos_net=net_p, neg_net=net_n)
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
        >>> edbapp = Edb("myaedbfolder", edbversion="2026.1")
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

    def find_by_name(self, name: str) -> DifferentialPair | None:
        """Find a differential pair by name.

        Parameters
        ----------
        name : str
            Name of the differential pair.

        Returns
        -------
        :class:`pyedb.grpc.database.net.differential_pair.DifferentialPair` or `None`
            Differential pair object.
        """
        diff_pair = CoreDifferentialPair.find_by_name(self._pedb.layout.core, name)
        if diff_pair is not None:
            return DifferentialPair(self._pedb, diff_pair)
        raise ValueError(f"Differential pair {name!r} does not exist.")


class DifferentialPair:
    """Manages EDB functionalities for differential pair."""

    def __init__(self, pedb, edb_object):
        self.core = edb_object
        self._pedb = pedb

    @property
    def description(self) -> str:
        """Description of the differential pair."""
        return self.core.description

    @description.setter
    def description(self, value: str):
        """Set the description of the differential pair."""
        self.core.description = value

    @property
    def differential_pair(self) -> tuple[Net, Net]:
        """Differential pair Net objects. This property is also used to add or replace nets using the setter method."""
        from pyedb.grpc.database.net.net import Net

        nets = self.core.differential_pair
        return Net(self._pedb, nets[0]), Net(self._pedb, nets[1])

    @differential_pair.setter
    def differential_pair(self, value: tuple[Net, Net]):
        """Set the differential pair Net objects."""
        if not isinstance(value, tuple) or len(value) != 2:
            raise ValueError("Differential pair must be a tuple of two Net objects.")

        resolved_nets = []
        for net in value:
            if isinstance(net, str):
                net_name = net
                net = self._pedb.nets.nets.get(net_name)
                if net is None:
                    raise ValueError(f"Net {net_name!r} does not exist.")
            resolved_nets.append(net)
        self.core.differential_pair = tuple(net.core for net in resolved_nets)

    @property
    def id(self) -> int:
        """ID of the differential pair."""
        return self.core.id

    @property
    def is_null(self) -> bool:
        """Check if the differential pair is null."""
        return self.core.is_null

    @property
    def is_power_ground(self) -> bool:
        """Check if the differential pair is a power or ground pair."""
        return self.core.is_power_ground

    @property
    def layout(self) -> Layout:
        """Layout object."""
        return self._pedb.layout

    @property
    def name(self) -> str:
        """Name of the differential pair."""
        return self.core.name

    @name.setter
    def name(self, value: str):
        """Set the name of the differential pair."""
        self.core.name = value

    @property
    def positive_net(self) -> Net:
        """Positive Net."""
        from pyedb.grpc.database.net.net import Net

        return Net(self._pedb, self.core.positive_net)

    @property
    def negative_net(self) -> Net:
        """Negative Net."""
        from pyedb.grpc.database.net.net import Net

        return Net(self._pedb, self.core.negative_net)

    def delete(self) -> None:
        """Delete the differential pair.

        Returns
        -------
        None
        """
        return self.core.delete()
