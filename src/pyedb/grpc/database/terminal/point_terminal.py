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

from ansys.edb.core.geometry.point_data import PointData as GrpcPointData
from ansys.edb.core.terminal.point_terminal import PointTerminal as GrpcPointTerminal
from ansys.edb.core.utility.value import Value as GrpcValue


class PointTerminal(GrpcPointTerminal):
    """Manages point terminal properties."""

    def __init__(self, pedb, edb_object):
        super().__init__(edb_object.msg)
        self._pedb = pedb

    @property
    def location(self):
        """Terminal position.

        Returns
        -------
        [float, float] : [x,y]

        """
        return [self.point.x.value, self.point.y.value]

    @location.setter
    def location(self, value):
        if not isinstance(value, list):
            return
        value = [GrpcValue(i) for i in value]
        self.point = GrpcPointData(value)

    @property
    def layer(self):
        """Terminal layer.

        Returns
        -------
        :class:`StackupLayer <pyedb.grpc.database.layers.stackup_layer.StackupLayer>`

        """
        from pyedb.grpc.database.layers.stackup_layer import StackupLayer

        return StackupLayer(self._pedb, super().layer)

    @layer.setter
    def layer(self, value):
        if value in self._pedb.stackup.layers:
            super(PointTerminal, self.__class__).layer.__set__(self, value)

    @property
    def ref_terminal(self):
        """Reference terminal.

        Returns
        -------
        :class:`PointTerminal <pyedb.grpc.database.terminal.point_terminal.PointTerminal>`

        """
        return PointTerminal(self._pedb, self.reference_terminal)

    @ref_terminal.setter
    def ref_terminal(self, value):
        super().reference_terminal = value

    @property
    def reference_terminal(self):
        """Reference terminal.

        Returns
        -------
        :class:`PointTerminal <pyedb.grpc.database.terminal.point_terminal.PointTerminal>`

        """
        return PointTerminal(self._pedb, super().reference_terminal)

    @reference_terminal.setter
    def reference_terminal(self, value):
        super(PointTerminal, self.__class__).reference_terminal.__set__(self, value)

    @property
    def terminal_type(self):
        return "PointTerminal"

    @property
    def is_port(self):
        """Adding DotNet compatibility."""
        return True
