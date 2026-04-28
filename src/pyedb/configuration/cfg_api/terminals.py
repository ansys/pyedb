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

"""Terminal builder API.

Data models (pydantic, no EDB dependency):
  :class:`~pyedb.configuration.cfg_terminals.CfgPadstackInstanceTerminal`
  :class:`~pyedb.configuration.cfg_terminals.CfgPinGroupTerminal`
  :class:`~pyedb.configuration.cfg_terminals.CfgPointTerminal`
  :class:`~pyedb.configuration.cfg_terminals.CfgEdgeTerminal`
  :class:`~pyedb.configuration.cfg_terminals.CfgBundleTerminal`

The root ``cfg_terminals`` module uses pydantic and has no EDB imports, so we
import those models directly and expose thin builder wrappers.
"""

from __future__ import annotations

from typing import List, Optional, Union

from pyedb.configuration.cfg_terminals import (
    CfgBundleTerminal,
    CfgEdgeTerminal,
    CfgPadstackInstanceTerminal,
    CfgPinGroupTerminal,
    CfgPointTerminal,
)


# Re-export the root terminal classes directly so users can import them from here
PadstackInstanceTerminal = CfgPadstackInstanceTerminal
PinGroupTerminal = CfgPinGroupTerminal
PointTerminal = CfgPointTerminal
EdgeTerminal = CfgEdgeTerminal
BundleTerminal = CfgBundleTerminal


class TerminalInfo:
    """Factory helpers for building terminal specifier dicts.

    These dicts are consumed by :class:`PortsConfig`, :class:`SourcesConfig`,
    and :class:`ProbesConfig` as *positive_terminal* / *negative_terminal*.
    Use these static methods for IDE auto-complete and to avoid typos.

    Examples
    --------
    >>> from pyedb.configuration.cfg_api import TerminalInfo
    >>> TerminalInfo.pin_group("pg_VDD")
    >>> TerminalInfo.nearest_pin("GND")
    >>> TerminalInfo.net("VDD", reference_designator="U1")
    >>> TerminalInfo.coordinates(layer="top", x=0.001, y=0.002, net="SIG")
    """

    @staticmethod
    def pin(pin_name: str, reference_designator: Optional[str] = None) -> dict:
        """Terminal on a specific component pin."""
        d: dict = {"pin": pin_name}
        if reference_designator:
            d["reference_designator"] = reference_designator
        return d

    @staticmethod
    def net(net_name: str, reference_designator: Optional[str] = None) -> dict:
        """Terminal on all component pins that belong to a net."""
        d: dict = {"net": net_name}
        if reference_designator:
            d["reference_designator"] = reference_designator
        return d

    @staticmethod
    def pin_group(pin_group_name: str) -> dict:
        """Terminal on a named pin group."""
        return {"pin_group": pin_group_name}

    @staticmethod
    def padstack(padstack_instance_name: str) -> dict:
        """Terminal on a padstack instance (coax / via port)."""
        return {"padstack": padstack_instance_name}

    @staticmethod
    def coordinates(layer: str, x: Union[float, str], y: Union[float, str], net: str) -> dict:
        """Terminal at an arbitrary XY coordinate on a layer."""
        return {"coordinates": {"layer": layer, "point": [x, y], "net": net}}

    @staticmethod
    def nearest_pin(reference_net: str, search_radius: Union[str, float] = "5mm") -> dict:
        """Negative terminal resolved to the nearest pin on a reference net."""
        return {"nearest_pin": {"reference_net": reference_net, "search_radius": search_radius}}


class TerminalsConfig:
    """Fluent builder for the low-level ``terminals`` configuration list.

    Uses :class:`~pyedb.configuration.cfg_terminals.CfgTerminals` pydantic models
    internally.  For most workflows the high-level port / source configs create
    terminals implicitly; use this only for advanced HFSS workflows.

    Examples
    --------
    >>> cfg.terminals.add_padstack_instance_terminal(
    ...     name="t1", padstack_instance="via_001",
    ...     impedance=50, boundary_type="port", hfss_type=None)
    >>> cfg.terminals.add_pin_group_terminal(
    ...     name="t2", pin_group="pg_VDD",
    ...     impedance=50, boundary_type="port")
    """

    def __init__(self):
        self._terminals: List = []

    def add_padstack_instance_terminal(
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
    ) -> CfgPadstackInstanceTerminal:
        """Add a padstack-instance terminal (wraps :class:`~pyedb.configuration.cfg_terminals.CfgPadstackInstanceTerminal`)."""
        t = CfgPadstackInstanceTerminal(
            name=name,
            padstack_instance=padstack_instance,
            impedance=impedance,
            boundary_type=boundary_type,
            hfss_type=hfss_type,
            is_circuit_port=is_circuit_port,
            reference_terminal=reference_terminal,
            amplitude=amplitude,
            phase=phase,
            terminal_to_ground=terminal_to_ground,
            layer=layer,
            padstack_instance_id=padstack_instance_id,
        )
        self._terminals.append(t)
        return t

    def add_pin_group_terminal(
        self,
        name: str,
        pin_group: str,
        impedance: Union[float, str],
        boundary_type: str,
        reference_terminal: Optional[str] = None,
        amplitude: Union[float, str] = 1,
        phase: Union[float, str] = 0,
        terminal_to_ground: str = "kNoGround",
    ) -> CfgPinGroupTerminal:
        """Add a pin-group terminal (wraps :class:`~pyedb.configuration.cfg_terminals.CfgPinGroupTerminal`)."""
        t = CfgPinGroupTerminal(
            name=name,
            pin_group=pin_group,
            impedance=impedance,
            boundary_type=boundary_type,
            is_circuit_port=True,
            reference_terminal=reference_terminal,
            amplitude=amplitude,
            phase=phase,
            terminal_to_ground=terminal_to_ground,
        )
        self._terminals.append(t)
        return t

    def add_point_terminal(
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
    ) -> CfgPointTerminal:
        """Add a point (coordinate) terminal (wraps :class:`~pyedb.configuration.cfg_terminals.CfgPointTerminal`)."""
        t = CfgPointTerminal(
            name=name,
            x=x,
            y=y,
            layer=layer,
            net=net,
            impedance=impedance,
            boundary_type=boundary_type,
            is_circuit_port=True,
            reference_terminal=reference_terminal,
            amplitude=amplitude,
            phase=phase,
            terminal_to_ground=terminal_to_ground,
        )
        self._terminals.append(t)
        return t

    def add_edge_terminal(
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
    ) -> CfgEdgeTerminal:
        """Add an edge terminal (wraps :class:`~pyedb.configuration.cfg_terminals.CfgEdgeTerminal`)."""
        t = CfgEdgeTerminal(
            name=name,
            primitive=primitive,
            point_on_edge_x=point_on_edge_x,
            point_on_edge_y=point_on_edge_y,
            impedance=impedance,
            boundary_type=boundary_type,
            hfss_type=hfss_type,
            horizontal_extent_factor=horizontal_extent_factor,
            vertical_extent_factor=vertical_extent_factor,
            pec_launch_width=pec_launch_width,
            is_circuit_port=is_circuit_port,
            reference_terminal=reference_terminal,
            amplitude=amplitude,
            phase=phase,
            terminal_to_ground=terminal_to_ground,
        )
        self._terminals.append(t)
        return t

    def add_bundle_terminal(self, name: str, terminals: List[str]) -> CfgBundleTerminal:
        """Bundle terminals into a differential group (wraps :class:`~pyedb.configuration.cfg_terminals.CfgBundleTerminal`)."""
        t = CfgBundleTerminal(name=name, terminals=terminals)
        self._terminals.append(t)
        return t

    def to_list(self) -> List[dict]:
        result = []
        for t in self._terminals:
            if hasattr(t, "model_dump"):
                result.append(t.model_dump(exclude_none=True))
            elif hasattr(t, "to_dict"):
                result.append(t.to_dict())
            else:
                result.append(t)
        return result
