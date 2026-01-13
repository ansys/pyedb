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

from typing import TYPE_CHECKING

from ansys.edb.core.geometry.point_data import PointData as GrpcPointData
from ansys.edb.core.terminal.point_terminal import PointTerminal as GrpcPointTerminal
from ansys.edb.core.terminal.terminal import BoundaryType as GrpcBoundaryType

if TYPE_CHECKING:
    from pyedb.grpc.database.layers.stackup_layer import StackupLayer
from pyedb.grpc.database.utility.value import Value

mapping_boundary_type = {
    "port": GrpcBoundaryType.PORT,
    "dc_terminal": GrpcBoundaryType.DC_TERMINAL,
    "voltage_probe": GrpcBoundaryType.VOLTAGE_PROBE,
    "voltage_source": GrpcBoundaryType.VOLTAGE_SOURCE,
    "current_source": GrpcBoundaryType.CURRENT_SOURCE,
    "rlc": GrpcBoundaryType.RLC,
    "pec": GrpcBoundaryType.PEC,
}
from pyedb.grpc.database.terminal.terminal import Terminal


class PointTerminal(Terminal):
    """Manages point terminal properties."""

    def __init__(self, pedb, edb_object):
        super().__init__(pedb, edb_object)

    @classmethod
    def create(cls, layout, net, layer, name, point):
        """Create a point terminal.

        Parameters
        ----------
        layout : :class: <``Layout` pyedb.grpc.database.layout.layout.Layout>
            Layout object associated with the terminal.
        net : Net
            :class: `Net` <pyedb.grpc.database.net.net.Net> object associated with the terminal.
        name : str
            Terminal name.
        point : [float, float]
            [x,y] location of the terminal.
        layer : str
            Layer name.
        net : :class: <``Net` pyedb.grpc.database.net.net.Net>, optional
            Net object associated with the terminal. If None, the terminal will be
            associated with the ground net.

        Returns
        -------
        PointTerminal
            Point terminal object.
        """
        if isinstance(point, list):
            point = GrpcPointData([Value(i) for i in point])
        if isinstance(net, str):
            net = layout._pedb.nets[net]
        if isinstance(layer, str):
            layer = layout._pedb.stackup.layers[layer]
        core_terminal = GrpcPointTerminal.create(
            layout=layout.core, net=net.core, layer=layer.core, name=name, point=point
        )
        return cls(layout._pedb, core_terminal)

    @property
    def is_reference_terminal(self) -> bool:
        """Whether the terminal is a reference terminal.

        Returns
        -------
        bool
            True if the terminal is a reference terminal, False otherwise.

        """
        return self.core.is_reference_terminal

    @property
    def point(self) -> tuple[float, float]:
        """Terminal point.

        Returns
        -------
        tuple[float, float]

        """
        return self.core.point.x.value, self.core.point.y.value

    @property
    def location(self) -> tuple[float, float]:
        """Terminal position.

        Returns
        -------
        tuple[float, float] : (x,y])

        """
        return Value(self.core.point.x), Value(self.core.point.y)

    @location.setter
    def location(self, value):
        if not isinstance(value, list):
            return
        value = [Value(i) for i in value]
        self.core.point = GrpcPointData(value)

    @property
    def reference_layer(self):
        """Reference layer of the terminal.

        Returns
        -------
        :class:`Layer <pyedb.grpc.database.layer.layer.Layer>`
        """
        try:
            return self.core.reference_layer.name
        except AttributeError:
            self._pedb.logger.error("Cannot determine terminal layer")
            return None

    @reference_layer.setter
    def reference_layer(self, value):
        from ansys.edb.core.layer.layer import Layer as GrpcLayer

        if isinstance(value, GrpcLayer):
            self.core.reference_layer = value
        if isinstance(value, str):
            self.core.reference_layer = self._pedb.stackup.layers[value]

    @property
    def layer(self):
        """Layer that the point terminal is placed on."""
        return self.core.layer

    @layer.setter
    def layer(self, value):
        self.core.layer = value
