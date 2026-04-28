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

from ansys.edb.core.hierarchy.structure3d import Structure3D as CoreStructure3D


class Structure3D:
    """Class for storing structure 3D components."""

    def __init__(self, pedb, core):
        self._pedb = pedb
        self.core = core

    @classmethod
    def create(cls, edb, name: str) -> "Structure3D":
        """Create structure 3D component.

        Parameters
        ----------
        edb : EDB
            The EDB instance the structure 3D component belongs to.
        name : str
            The name of the structure 3D component.

        Returns
        -------
        Structure3D
            The created structure 3D component.

        """
        core = CoreStructure3D.create(edb.layout.core, name)
        return Structure3D(pedb=edb, core=core)

    def delete(self):
        """Delete structure 3D component."""
        self.core.delete()

    @property
    def id(self) -> int:
        """Return structure 3D component.

        Returns
        -------
        int
            The structure 3D component unique ID.

        """
        return self.core.edb_uid

    @property
    def location(self) -> tuple[float, float]:
        """"Return structure 3D component.

        Returns
        -------
        tuple[float, float]
            The structure 3D component location as a tuple of x and y coordinates.

        """
        return tuple([self._pedb._value_setter(val) for val in self.core.location])

    @location.setter
    def location(self, location: tuple[float, float]):
        self.core.location = tuple(location)

    @property
    def name(self) -> str:
        """"Return structure 3D component.

        Returns
        -------
        str
            The structure 3D component name.

        """
        return self.core.name

    @name.setter
    def name(self, name: str):
        self.core.name = name

    @property
    def material(self) -> str:
        """"Return structure 3D component.

        str
            The structure 3D component material.
        """
        return self.core.material

    @material.setter
    def material(self, material: str):
        self.core.material = material

    @property
    def net(self) -> str:
        """"Return structure 3D component net name

        Returns
        -------
        str
            The structure 3D component net name.

        """
        return self.core.net.name

    @net.setter
    def net(self, net: str):
        net = self._pedb.nets.find_or_create_net(net)
        self.core.net = net.core
