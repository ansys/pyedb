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

from ansys.edb.core.hierarchy.group import Group as CoreGroup


class Group:
    """Represents a group.
    Parameters
    ----------
    pedb
        The parent EDB instance.
    core
        The core group object.
    """

    def __init__(self, pedb, core):
        self.core = core
        self._pedb = pedb

    @classmethod
    def create(cls, pedb, name: str) -> "Group":
        """Create a group.

        Parameters
        ----------
        pedb
            Edb to create the group in.
        name : str
            Name of the group.

        Returns
        -------
        Group
            Group created.
        """
        return Group(pedb, CoreGroup.create(pedb.layout.core, name))

    @property
    def name(self):
        """Component part name.

        Returns
        -------
        str
            Component part name.
        """
        return self.core.name

    @name.setter
    def name(self, name):  # pragma: no cover
        """Set component part name."""
        self.core.name = name

    @property
    def placement_layer(self) -> str:
        """Placement layer name.

        Returns
        -------
        str
           Placement layer name.
        """
        return self.core.placement_layer.name

    @placement_layer.setter
    def placement_layer(self, value):
        """Set placement layer.

        Parameters
        ----------
        value : str
            Name of the placement layer.
        """
        self.core.placement_layer = self._pedb.stackup.layers[value].core

    @property
    def location(self) -> tuple:
        """Group center.

        Returns
        -------
        List
            [x, y].

        """
        location = self.core.location
        return self._pedb.value(location[0]), location[1].value

    @location.setter
    def location(self, value: tuple | list):
        """Set group center.

        Parameters
        ----------
        value : tuple or list
            [x, y] coordinates.
        """
        self.core.location = self._pedb.value(value[0]), self._pedb.value(value[1])

    # noqa: W293
    @property
    def id(self):
        """Group id.

        Returns
        -------
        group Id : int


        """
        return self.core.edb_uid
