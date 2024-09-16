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

from ansys.edb.core.net.extended_net import ExtendedNet as GrpcExtendedNet

from pyedb.grpc.edb_core.nets.net import Net


class ExtendedNet(GrpcExtendedNet):
    """Manages EDB functionalities for a primitives.
    It Inherits EDB Object properties.
    """

    def __init__(self, pedb, edb_object=None):
        super().__init__(self, edb_object)
        self._pedb = pedb
        self.components = self._pedb.components
        self.primitive = self._pedb.modeler
        self.nets = self._pedb.nets

    @property
    def nets(self):
        """Nets dictionary."""
        return {net.name: Net(self._app, net) for net in self.nets}

    @property
    def components(self):
        """Dictionary of components."""
        comps = {}
        for _, obj in self.nets.items():
            comps.update(obj.components)
        return comps

    @property
    def rlc(self):
        """Dictionary of RLC components."""
        return {
            name: comp for name, comp in self.components.items() if comp.type in ["inductor", "resistor", "capacitor"]
        }

    @property
    def serial_rlc(self):
        """Dictionary of serial RLC components."""
        res = {}
        nets = self.nets
        for comp_name, comp_obj in self.components.items():
            if comp_obj.type not in ["resistor", "inductor", "capacitor"]:
                continue
            if set(comp_obj.nets).issubset(set(nets)):
                res[comp_name] = comp_obj
        return res

    @property
    def shunt_rlc(self):
        """Dictionary of shunt RLC components."""
        res = {}
        nets = self.nets
        for comp_name, comp_obj in self.components.items():
            if comp_obj.type not in ["resistor", "inductor", "capacitor"]:
                continue
            if not set(comp_obj.nets).issubset(set(nets)):
                res[comp_name] = comp_obj
        return res
