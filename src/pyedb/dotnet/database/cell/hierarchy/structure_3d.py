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

from pyedb.dotnet.database.edb_data.nets_data import NetDotNet


class Structure3D:
    def __init__(self, pedb, core):
        self._pedb = pedb
        self.core = core

    @classmethod
    def create(cls, edb, name: str) -> "Structure3D":
        core = edb._edb.Cell.Hierarchy.Structure3D.Create(edb.layout.core, name)
        return Structure3D(pedb=edb, core=core)

    def delete(self):
        self.core.Delete()

    @property
    def id(self) -> int:
        return self.core.GetId()

    @property
    def location(self) -> tuple[float, float]:
        location = self.core.GetLocation()
        return location[1], location[2]

    @location.setter
    def location(self, location: tuple[float, float]):
        if isinstance(location, tuple) or isinstance(location, list):
            self.core.SetLocation(location[0], location[1])

    @property
    def name(self) -> str:
        return self.core.GetName()

    @name.setter
    def name(self, name: str):
        self.core.SetName(name)

    @property
    def material(self) -> str:
        return self.core.GetMaterial()

    @material.setter
    def material(self, material: str):
        self.core.SetMaterial(material)

    @property
    def net(self) -> NetDotNet:
        return self.core.GetNet().GetName()

    @net.setter
    def net(self, net: str):
        net = self._pedb.nets.find_or_create_net(net)
        self.core.SetNet(net.api_object)
