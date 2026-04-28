# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Build low-level terminal configuration entries.

This module provides explicit terminal builders plus factory helpers for the
terminal-specifier dictionaries accepted by ports, sources, and probes.
"""

from __future__ import annotations

from typing import List, Optional, Union


class PadstackInstanceTerminal:
    """Represent a terminal attached to a padstack instance."""

    def __init__(
        self,
        name: str,
        padstack_instance: str,
        impedance: Union[float, str],
        boundary_type: str,
        hfss_type: Optional[str],
        is_circuit_port: bool = False,
        reference_terminal: Optional[str] = None,
        amplitude: Union[float, str] = 1,
        phase: Union[float, str] = 0,
        terminal_to_ground: str = "kNoGround",
        layer: Optional[str] = None,
        padstack_instance_id: Optional[int] = None,
    ):
        self.terminal_type = "padstack_instance"
        self.name = name
        self.padstack_instance = padstack_instance
        self.impedance = impedance
        self.boundary_type = boundary_type
        self.hfss_type = hfss_type
        self.is_circuit_port = is_circuit_port
        self.reference_terminal = reference_terminal
        self.amplitude = amplitude
        self.phase = phase
        self.terminal_to_ground = terminal_to_ground
        self.layer = layer
        self.padstack_instance_id = padstack_instance_id

    def to_dict(self) -> dict:
        """Serialize the padstack-instance terminal.

        Returns
        -------
        dict
            Dictionary ready for inclusion in the ``terminals`` list.
        """
        d = {
            "terminal_type": self.terminal_type,
            "name": self.name,
            "padstack_instance": self.padstack_instance,
            "impedance": self.impedance,
            "boundary_type": self.boundary_type,
            "is_circuit_port": self.is_circuit_port,
            "amplitude": self.amplitude,
            "phase": self.phase,
            "terminal_to_ground": self.terminal_to_ground,
        }
        if self.hfss_type is not None:
            d["hfss_type"] = self.hfss_type
        if self.reference_terminal is not None:
            d["reference_terminal"] = self.reference_terminal
        if self.layer is not None:
            d["layer"] = self.layer
        if self.padstack_instance_id is not None:
            d["padstack_instance_id"] = self.padstack_instance_id
        return d


class PinGroupTerminal:
    """Represent a terminal attached to a pin group."""

    def __init__(
        self,
        name: str,
        pin_group: str,
        impedance: Union[float, str],
        boundary_type: str,
        reference_terminal: Optional[str] = None,
        amplitude: Union[float, str] = 1,
        phase: Union[float, str] = 0,
        terminal_to_ground: str = "kNoGround",
    ):
        self.terminal_type = "pin_group"
        self.name = name
        self.pin_group = pin_group
        self.impedance = impedance
        self.boundary_type = boundary_type
        self.is_circuit_port = True
        self.reference_terminal = reference_terminal
        self.amplitude = amplitude
        self.phase = phase
        self.terminal_to_ground = terminal_to_ground

    def to_dict(self) -> dict:
        """Serialize the pin-group terminal.

        Returns
        -------
        dict
            Dictionary ready for inclusion in the ``terminals`` list.
        """
        d = {
            "terminal_type": self.terminal_type,
            "name": self.name,
            "pin_group": self.pin_group,
            "impedance": self.impedance,
            "boundary_type": self.boundary_type,
            "is_circuit_port": self.is_circuit_port,
            "amplitude": self.amplitude,
            "phase": self.phase,
            "terminal_to_ground": self.terminal_to_ground,
        }
        if self.reference_terminal is not None:
            d["reference_terminal"] = self.reference_terminal
        return d


class PointTerminal:
    """Represent a point terminal defined by coordinates."""

    def __init__(
        self,
        name: str,
        x: Union[float, str],
        y: Union[float, str],
        layer: str,
        net: str,
        impedance: Union[float, str],
        boundary_type: str,
        reference_terminal: Optional[str] = None,
        amplitude: Union[float, str] = 1,
        phase: Union[float, str] = 0,
        terminal_to_ground: str = "kNoGround",
    ):
        self.terminal_type = "point"
        self.name = name
        self.x = x
        self.y = y
        self.layer = layer
        self.net = net
        self.impedance = impedance
        self.boundary_type = boundary_type
        self.is_circuit_port = True
        self.reference_terminal = reference_terminal
        self.amplitude = amplitude
        self.phase = phase
        self.terminal_to_ground = terminal_to_ground

    def to_dict(self) -> dict:
        """Serialize the point terminal.

        Returns
        -------
        dict
            Dictionary ready for inclusion in the ``terminals`` list.
        """
        d = {
            "terminal_type": self.terminal_type,
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "layer": self.layer,
            "net": self.net,
            "impedance": self.impedance,
            "boundary_type": self.boundary_type,
            "is_circuit_port": self.is_circuit_port,
            "amplitude": self.amplitude,
            "phase": self.phase,
            "terminal_to_ground": self.terminal_to_ground,
        }
        if self.reference_terminal is not None:
            d["reference_terminal"] = self.reference_terminal
        return d


class EdgeTerminal:
    """Represent an edge terminal for wave or gap boundaries."""

    def __init__(
        self,
        name: str,
        primitive: str,
        point_on_edge_x: Union[float, str],
        point_on_edge_y: Union[float, str],
        impedance: Union[float, str],
        boundary_type: str,
        hfss_type: str = "Wave",
        horizontal_extent_factor: Union[int, str] = 6,
        vertical_extent_factor: Union[int, str] = 8,
        pec_launch_width: str = "0.02mm",
        is_circuit_port: bool = False,
        reference_terminal: Optional[str] = None,
        amplitude: Union[float, str] = 1,
        phase: Union[float, str] = 0,
        terminal_to_ground: str = "kNoGround",
    ):
        self.terminal_type = "edge"
        self.name = name
        self.primitive = primitive
        self.point_on_edge_x = point_on_edge_x
        self.point_on_edge_y = point_on_edge_y
        self.impedance = impedance
        self.boundary_type = boundary_type
        self.hfss_type = hfss_type
        self.horizontal_extent_factor = horizontal_extent_factor
        self.vertical_extent_factor = vertical_extent_factor
        self.pec_launch_width = pec_launch_width
        self.is_circuit_port = is_circuit_port
        self.reference_terminal = reference_terminal
        self.amplitude = amplitude
        self.phase = phase
        self.terminal_to_ground = terminal_to_ground

    def to_dict(self) -> dict:
        """Serialize the edge terminal.

        Returns
        -------
        dict
            Dictionary ready for inclusion in the ``terminals`` list.
        """
        d = {
            "terminal_type": self.terminal_type,
            "name": self.name,
            "primitive": self.primitive,
            "point_on_edge_x": self.point_on_edge_x,
            "point_on_edge_y": self.point_on_edge_y,
            "impedance": self.impedance,
            "boundary_type": self.boundary_type,
            "hfss_type": self.hfss_type,
            "horizontal_extent_factor": self.horizontal_extent_factor,
            "vertical_extent_factor": self.vertical_extent_factor,
            "pec_launch_width": self.pec_launch_width,
            "is_circuit_port": self.is_circuit_port,
            "amplitude": self.amplitude,
            "phase": self.phase,
            "terminal_to_ground": self.terminal_to_ground,
        }
        if self.reference_terminal is not None:
            d["reference_terminal"] = self.reference_terminal
        return d


class BundleTerminal:
    """Represent a terminal bundle such as a differential pair."""

    def __init__(self, name: str, terminals: List[str]):
        self.terminal_type = "bundle"
        self.name = name
        self.terminals = terminals

    def to_dict(self) -> dict:
        """Serialize the bundle terminal.

        Returns
        -------
        dict
            Dictionary ready for inclusion in the ``terminals`` list.
        """
        return {"terminal_type": self.terminal_type, "name": self.name, "terminals": self.terminals}


class TerminalInfo:
    """Create terminal-specifier dictionaries for higher-level builders."""

    @staticmethod
    def pin(pin_name: str, reference_designator: Optional[str] = None) -> dict:
        """Build a pin terminal specifier."""
        d: dict = {"pin": pin_name}
        if reference_designator:
            d["reference_designator"] = reference_designator
        return d

    @staticmethod
    def net(net_name: str, reference_designator: Optional[str] = None) -> dict:
        """Build a net terminal specifier."""
        d: dict = {"net": net_name}
        if reference_designator:
            d["reference_designator"] = reference_designator
        return d

    @staticmethod
    def pin_group(pin_group_name: str) -> dict:
        """Build a pin-group terminal specifier."""
        return {"pin_group": pin_group_name}

    @staticmethod
    def padstack(padstack_instance_name: str) -> dict:
        """Build a padstack terminal specifier."""
        return {"padstack": padstack_instance_name}

    @staticmethod
    def coordinates(layer: str, x: Union[float, str], y: Union[float, str], net: str) -> dict:
        """Build a coordinate-based terminal specifier."""
        return {"coordinates": {"layer": layer, "point": [x, y], "net": net}}

    @staticmethod
    def nearest_pin(reference_net: str, search_radius: Union[str, float] = "5mm") -> dict:
        """Build a nearest-pin terminal specifier."""
        return {"nearest_pin": {"reference_net": reference_net, "search_radius": search_radius}}


class TerminalsConfig:
    """Fluent builder for the ``terminals`` configuration list."""

    def __init__(self):
        self._terminals: List = []

    def add_padstack_instance_terminal(
        self,
        name,
        padstack_instance,
        impedance,
        boundary_type,
        hfss_type,
        **kwargs,
    ) -> PadstackInstanceTerminal:
        """Add a padstack-instance terminal."""
        t = PadstackInstanceTerminal(
            name=name,
            padstack_instance=padstack_instance,
            impedance=impedance,
            boundary_type=boundary_type,
            hfss_type=hfss_type,
            **kwargs,
        )
        self._terminals.append(t)
        return t

    def add_pin_group_terminal(
        self,
        name,
        pin_group,
        impedance,
        boundary_type,
        **kwargs,
    ) -> PinGroupTerminal:
        """Add a pin-group terminal."""
        t = PinGroupTerminal(
            name=name,
            pin_group=pin_group,
            impedance=impedance,
            boundary_type=boundary_type,
            **kwargs,
        )
        self._terminals.append(t)
        return t

    def add_point_terminal(
        self,
        name,
        x,
        y,
        layer,
        net,
        impedance,
        boundary_type,
        **kwargs,
    ) -> PointTerminal:
        """Add a coordinate-defined point terminal."""
        t = PointTerminal(
            name=name,
            x=x,
            y=y,
            layer=layer,
            net=net,
            impedance=impedance,
            boundary_type=boundary_type,
            **kwargs,
        )
        self._terminals.append(t)
        return t

    def add_edge_terminal(
        self,
        name,
        primitive,
        point_on_edge_x,
        point_on_edge_y,
        impedance,
        boundary_type,
        **kwargs,
    ) -> EdgeTerminal:
        """Add an edge terminal."""
        t = EdgeTerminal(
            name=name,
            primitive=primitive,
            point_on_edge_x=point_on_edge_x,
            point_on_edge_y=point_on_edge_y,
            impedance=impedance,
            boundary_type=boundary_type,
            **kwargs,
        )
        self._terminals.append(t)
        return t

    def add_bundle_terminal(self, name: str, terminals: List[str]) -> BundleTerminal:
        """Add a bundle terminal."""
        t = BundleTerminal(name=name, terminals=terminals)
        self._terminals.append(t)
        return t

    def to_list(self) -> List[dict]:
        """Serialize all configured terminals.

        Returns
        -------
        list[dict]
            Terminal definitions in insertion order.
        """
        result = []
        for t in self._terminals:
            if hasattr(t, "to_dict"):
                result.append(t.to_dict())
            else:
                result.append(t)
        return result
