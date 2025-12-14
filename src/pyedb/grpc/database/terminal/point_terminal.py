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


class PointTerminal:
    """Manages point terminal properties."""

    def __init__(self, pedb, edb_object):
        self.core = edb_object
        self._pedb = pedb

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
    def name(self) -> str:
        """Terminal name.

        Returns
        -------
        str : terminal name.

        """
        return self.core.name

    @name.setter
    def name(self, value):
        self.core.name = value

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
    def boundary_type(self):
        """Boundary type.

        Returns
        -------
        str : boundary type.

        """
        return self.core.boundary_type.name.lower()

    @boundary_type.setter
    def boundary_type(self, value):
        if isinstance(value, str):
            value = mapping_boundary_type.get(value.lower(), None)
        if not isinstance(value, GrpcBoundaryType):
            raise ValueError("Value must be a string or BoundaryType enum.")
        self.core.boundary_type = value

    @property
    def location(self) -> tuple[float, float]:
        """Terminal position.

        Returns
        -------
        tuple[float, float] : (x,y])

        """
        return self.core.point

    @location.setter
    def location(self, value):
        if not isinstance(value, list):
            return
        value = [Value(i) for i in value]
        self.core.point = GrpcPointData(value)

    @property
    def layer(self) -> "StackupLayer":
        """Terminal layer.

        Returns
        -------
        :class:`StackupLayer <pyedb.grpc.database.layers.stackup_layer.StackupLayer>`

        """
        from pyedb.grpc.database.layers.stackup_layer import StackupLayer

        return StackupLayer(self._pedb, self.core.layer)

    @layer.setter
    def layer(self, value):
        if value in self._pedb.stackup.layers:
            self.core.layer = value

    @property
    def ref_terminal(self) -> "PointTerminal":
        """Reference terminal.

        Returns
        -------
        :class:`PointTerminal <pyedb.grpc.database.terminal.point_terminal.PointTerminal>`

        """
        return PointTerminal(self._pedb, self.reference_terminal)

    @ref_terminal.setter
    def ref_terminal(self, value):
        self.core.reference_terminal = value.core

    @property
    def reference_terminal(self) -> "PointTerminal":
        """Reference terminal.

        Returns
        -------
        :class:`PointTerminal <pyedb.grpc.database.terminal.point_terminal.PointTerminal>`

        """
        return PointTerminal(self._pedb, self.core.reference_terminal)

    @reference_terminal.setter
    def reference_terminal(self, value):
        self.core.reference_terminal = value.core

    @property
    def terminal_type(self) -> str:
        return "PointTerminal"

    @property
    def is_port(self) -> bool:
        """Adding DotNet compatibility."""
        return True
