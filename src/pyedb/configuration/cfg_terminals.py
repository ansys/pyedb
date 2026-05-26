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

"""Build explicit low-level terminal entries for configuration payloads."""

from typing import Literal

from pydantic import Field

from pyedb.configuration.cfg_common import CfgBaseModel


class CfgTerminalInfo:
    """Factory for terminal-location descriptors used in port/source definitions."""

    @staticmethod
    def from_pin(pin: str, reference_designator: str | None = None) -> dict:
        """Return a pin-based terminal descriptor.

        Parameters
        ----------
        pin : str
            Pin name.
        reference_designator : str, optional
            Component reference designator.

        Returns
        -------
        dict
        """
        d = {"pin": pin}
        if reference_designator is not None:
            d["reference_designator"] = reference_designator
        return d

    @staticmethod
    def from_net(net: str, reference_designator: str | None = None) -> dict:
        """Return a net-based terminal descriptor.

        Parameters
        ----------
        net : str
            Net name.
        reference_designator : str, optional
            Component reference designator.

        Returns
        -------
        dict
        """
        d = {"net": net}
        if reference_designator is not None:
            d["reference_designator"] = reference_designator
        return d

    @staticmethod
    def from_pin_group(pin_group: str) -> dict:
        """Return a pin-group-based terminal descriptor.

        Parameters
        ----------
        pin_group : str
            Pin group name.

        Returns
        -------
        dict
        """
        return {"pin_group": pin_group}

    @staticmethod
    def from_padstack(padstack: str) -> dict:
        """Return a padstack-instance-based terminal descriptor.

        Parameters
        ----------
        padstack : str
            Padstack instance name.

        Returns
        -------
        dict
        """
        return {"padstack": padstack}

    @staticmethod
    def from_coordinates(layer: str, x: float | int | str, y: float | int | str, net: str) -> dict:
        """Return a coordinate-based terminal descriptor.

        Parameters
        ----------
        layer : str
            Layer name.
        x : float, int, or str
            X coordinate.
        y : float, int, or str
            Y coordinate.
        net : str
            Net name.

        Returns
        -------
        dict
        """
        return {"coordinates": {"layer": layer, "point": [x, y], "net": net}}

    @staticmethod
    def from_nearest_pin(reference_net: str, search_radius: str = "5mm") -> dict:
        """Return a nearest-pin terminal descriptor.

        Parameters
        ----------
        reference_net : str
            Reference net name used to find the nearest pin.
        search_radius : str, optional
            Search radius, default is ``"5mm"``.

        Returns
        -------
        dict
        """
        return {"nearest_pin": {"reference_net": reference_net, "search_radius": search_radius}}


class CfgTerminal(CfgBaseModel):
    """Base class for explicit terminal definitions."""

    model_config = {"populate_by_name": True, "extra": "ignore"}

    name: str
    impedance: float | int | str
    is_circuit_port: bool = False
    reference_terminal: str | None = None
    amplitude: float | int | str | None = 1
    phase: float | int | str | None = 0
    terminal_to_ground: (
        Literal[
            "kNoGround",
            "kNegative",
            "kNegativeNode",
            "kPositive",
            "kPositiveNode",
            "no_ground",
            "negative",
            "positive",
        ]
        | None
    ) = "kNoGround"
    boundary_type: Literal[
        "PortBoundary",
        "PecBoundary",
        "RlcBoundary",
        "kCurrentSource",
        "kVoltageSource",
        "kNexximGround",
        "kNexximPort",
        "kDcTerminal",
        "kVoltageProbe",
        "InvalidBoundary",
        "port",
        "dc_terminal",
        "voltage_probe",
        "voltage_source",
        "current_source",
        "rlc",
        "pec",
    ]
    hfss_type: Literal["Wave", "Gap", None] = None


class CfgPadstackInstanceTerminal(CfgTerminal):
    """Represent a terminal created from a named padstack instance."""

    terminal_type: str = "padstack_instance"
    padstack_instance: str | None = None
    padstack_instance_id: int | None = None
    layer: str | None = None


class CfgPinGroupTerminal(CfgTerminal):
    """Represent a terminal created from a named pin group."""

    terminal_type: str = "pin_group"
    is_circuit_port: bool = True
    hfss_type: Literal["Wave", "Gap", None] = None
    pin_group: str


class CfgPointTerminal(CfgTerminal):
    """Represent a terminal placed at explicit XY coordinates."""

    terminal_type: str = "point"
    is_circuit_port: bool = True
    hfss_type: Literal["Wave", "Gap", None] = None
    x: float | int | str
    y: float | int | str
    layer: str
    net: str


class CfgEdgeTerminal(CfgTerminal):
    """Represent a terminal attached to a primitive edge."""

    terminal_type: str = "edge"
    name: str
    primitive: str
    point_on_edge_x: float | int | str
    point_on_edge_y: float | int | str
    horizontal_extent_factor: int | str = 6
    vertical_extent_factor: int | str = 8
    pec_launch_width: int | str = "0.02mm"
    hfss_type: Literal["Wave", "Gap", None] = "Wave"


class CfgBundleTerminal(CfgBaseModel):
    """Represent a bundle terminal built from other terminal names."""

    model_config = {"populate_by_name": True, "extra": "ignore"}

    terminal_type: str = "bundle"
    terminals: list[str]
    name: str


class CfgTerminals(CfgBaseModel):
    """Collect low-level terminal definitions for serialization."""

    terminals: list[
        CfgPadstackInstanceTerminal
        | CfgPinGroupTerminal
        | CfgPointTerminal
        | CfgEdgeTerminal
        | CfgBundleTerminal
        | dict
    ] = Field(default_factory=list)

    @classmethod
    def create(cls, terminals: list[dict]):
        """Reconstruct a :class:`CfgTerminals` instance from raw dictionaries."""
        manager = cls(terminals=[])
        for i in terminals:
            i = dict(i)
            terminal_type = i.pop("terminal_type")
            # Remove fields that are fixed on each subclass and not accepted by add_* methods
            i.pop("is_circuit_port", None)
            if terminal_type == "padstack_instance":
                manager.add_padstack_instance_terminal(**i)
            elif terminal_type == "pin_group":
                i.pop("hfss_type", None)
                manager.add_pin_group_terminal(**i)
            elif terminal_type == "point":
                i.pop("hfss_type", None)
                manager.add_point_terminal(**i)
            elif terminal_type == "edge":
                manager.add_edge_terminal(**i)
            elif terminal_type == "bundle":
                manager.add_bundle_terminal(**i)
            else:  # pragma: no cover
                raise ValueError(f"Unknown terminal type: {terminal_type}")
        return manager

    def add_padstack_instance_terminal(
        self,
        name: str,
        padstack_instance: str | None = None,
        impedance: float | int | str = 50,
        boundary_type: Literal[
            "port",
            "dc_terminal",
            "voltage_probe",
            "voltage_source",
            "current_source",
            "rlc",
            "pec",
        ] = "port",
        hfss_type: Literal["Wave", "Gap"] | None = None,
        is_circuit_port: bool = False,
        reference_terminal: str | None = None,
        amplitude: float | int | str = 1,
        phase: float | int | str = 0,
        terminal_to_ground: Literal[
            "no_ground",
            "negative",
            "positive",
        ] = "no_ground",
        padstack_instance_id: int | None = None,
        layer: str | None = None,
    ):
        """Add a terminal created from a named padstack instance.

        Parameters
        ----------
        name : str
            Unique terminal name.
        padstack_instance : str
            AEDT name of the padstack instance.
        impedance : float, int, or str
            Terminal impedance.
        boundary_type : str
            Boundary type string (e.g. ``"PortBoundary"``).
        hfss_type : str, optional
            HFSS terminal type, e.g. ``"Wave"`` or ``"Gap"``.
        is_circuit_port : bool, optional
            Default is ``False``.
        reference_terminal : str, optional
            Name of the reference terminal this terminal is paired with.
        amplitude : float, int, or str, optional
            Default is ``1``.
        phase : float, int, or str, optional
            Default is ``0``.
        terminal_to_ground : str, optional
            Default is ``"kNoGround"``.
        padstack_instance_id : int, optional
            Internal padstack-instance integer ID.
        layer : str, optional
            Layer name override.

        Returns
        -------
        CfgPadstackInstanceTerminal
            The newly created terminal object.
        """
        terminal = CfgPadstackInstanceTerminal(
            padstack_instance=padstack_instance,
            name=name,
            impedance=impedance,
            is_circuit_port=is_circuit_port,
            boundary_type=boundary_type,
            reference_terminal=reference_terminal,
            amplitude=amplitude,
            phase=phase,
            terminal_to_ground=terminal_to_ground,
            layer=layer,
            hfss_type=hfss_type,
            padstack_instance_id=padstack_instance_id,
        )
        self.terminals.append(terminal)
        return terminal

    def add_pin_group_terminal(
        self,
        name: str,
        pin_group: str,
        impedance: float | int | str,
        boundary_type: Literal[
            "PortBoundary",
            "PecBoundary",
            "RlcBoundary",
            "kCurrentSource",
            "kVoltageSource",
            "kNexximGround",
            "kNexximPort",
            "kDcTerminal",
            "kVoltageProbe",
            "InvalidBoundary",
            "port",
            "dc_terminal",
            "voltage_probe",
            "voltage_source",
            "current_source",
            "rlc",
            "pec",
        ],
        reference_terminal: str | None = None,
        amplitude: float | int | str = 1,
        phase: float | int | str = 0,
        terminal_to_ground: Literal[
            "kNoGround",
            "kNegative",
            "kNegativeNode",
            "kPositive",
            "kPositiveNode",
            "no_ground",
            "negative",
            "positive",
        ] = "kNoGround",
    ):
        """Add a terminal created from a named pin group.

        Parameters
        ----------
        name : str
            Unique terminal name.
        pin_group : str
            Pin-group name, e.g. ``"pg_VDD"``.
        impedance : float, int, or str
            Terminal impedance.
        boundary_type : str
            Boundary type string.
        reference_terminal : str, optional
            Name of the paired reference terminal.
        amplitude : float, int, or str, optional
            Default is ``1``.
        phase : float, int, or str, optional
            Default is ``0``.
        terminal_to_ground : str, optional
            Default is ``"kNoGround"``.

        Returns
        -------
        CfgPinGroupTerminal
            The newly created terminal object.

        Examples
        --------
        cfg.terminals.add_pin_group_terminal("t_vdd", "pg_VDD", 50, "port")
        """
        terminal = CfgPinGroupTerminal(
            pin_group=pin_group,
            name=name,
            impedance=impedance,
            boundary_type=boundary_type,
            reference_terminal=reference_terminal,
            amplitude=amplitude,
            phase=phase,
            terminal_to_ground=terminal_to_ground,
        )
        self.terminals.append(terminal)
        return terminal

    def add_point_terminal(
        self,
        name: str,
        x: float | int | str,
        y: float | int | str,
        layer: str,
        net: str,
        impedance: float | int | str,
        boundary_type: Literal[
            "PortBoundary",
            "PecBoundary",
            "RlcBoundary",
            "kCurrentSource",
            "kVoltageSource",
            "kNexximGround",
            "kNexximPort",
            "kDcTerminal",
            "kVoltageProbe",
            "InvalidBoundary",
            "port",
            "dc_terminal",
            "voltage_probe",
            "voltage_source",
            "current_source",
            "rlc",
            "pec",
        ],
        reference_terminal: str | None = None,
        amplitude: float | int | str = 1,
        phase: float | int | str = 0,
        terminal_to_ground: Literal[
            "kNoGround",
            "kNegative",
            "kNegativeNode",
            "kPositive",
            "kPositiveNode",
            "no_ground",
            "negative",
            "positive",
        ] = "kNoGround",
    ):
        """Add a terminal placed at exact XY coordinates.

        Parameters
        ----------
        name : str
            Unique terminal name.
        x : float, int, or str
            X coordinate in metres.
        y : float, int, or str
            Y coordinate in metres.
        layer : str
            Layer name on which the terminal is placed.
        net : str
            Net name.
        impedance : float, int, or str
            Terminal impedance.
        boundary_type : str
            Boundary type string.
        reference_terminal : str, optional
            Paired reference terminal name.
        amplitude : float, int, or str, optional
            Default is ``1``.
        phase : float, int, or str, optional
            Default is ``0``.
        terminal_to_ground : str, optional
            Default is ``"kNoGround"``.

        Returns
        -------
        CfgPointTerminal
            The newly created terminal object.
        """
        terminal = CfgPointTerminal(
            x=x,
            y=y,
            layer=layer,
            name=name,
            impedance=impedance,
            boundary_type=boundary_type,
            reference_terminal=reference_terminal,
            amplitude=amplitude,
            phase=phase,
            net=net,
            terminal_to_ground=terminal_to_ground,
        )
        self.terminals.append(terminal)
        return terminal

    def add_edge_terminal(
        self,
        name: str,
        primitive: str,
        point_on_edge_x: float | int | str,
        point_on_edge_y: float | int | str,
        impedance: float | int | str,
        boundary_type: Literal[
            "PortBoundary",
            "PecBoundary",
            "RlcBoundary",
            "kCurrentSource",
            "kVoltageSource",
            "kNexximGround",
            "kNexximPort",
            "kDcTerminal",
            "kVoltageProbe",
            "InvalidBoundary",
            "port",
            "dc_terminal",
            "voltage_probe",
            "voltage_source",
            "current_source",
            "rlc",
            "pec",
        ],
        hfss_type: Literal["Wave", "Gap"] | None = "Wave",
        horizontal_extent_factor: int | str = 6,
        vertical_extent_factor: int | str = 8,
        pec_launch_width: str = "0.02mm",
        is_circuit_port: bool = False,
        reference_terminal: str | None = None,
        amplitude: float | int | str = 1,
        phase: float | int | str = 0,
        terminal_to_ground: Literal[
            "kNoGround",
            "kNegative",
            "kNegativeNode",
            "kPositive",
            "kPositiveNode",
            "no_ground",
            "negative",
            "positive",
        ] = "kNoGround",
    ):
        """Add a terminal attached to a primitive edge.

        Parameters
        ----------
        name : str
            Unique terminal name.
        primitive : str
            AEDT name of the hosting primitive.
        point_on_edge_x : float, int, or str
            X coordinate of the point on the edge.
        point_on_edge_y : float, int, or str
            Y coordinate of the point on the edge.
        impedance : float, int, or str
            Terminal impedance.
        boundary_type : str
            Boundary type string.
        hfss_type : str, optional
            ``"Wave"`` (default) or ``"Gap"``.
        horizontal_extent_factor : int or str, optional
            Default is ``6``.
        vertical_extent_factor : int or str, optional
            Default is ``8``.
        pec_launch_width : str, optional
            Default is ``"0.02mm"``.
        is_circuit_port : bool, optional
            Default is ``False``.
        reference_terminal : str, optional
            Paired reference terminal name.
        amplitude : float, int, or str, optional
            Default is ``1``.
        phase : float, int, or str, optional
            Default is ``0``.
        terminal_to_ground : str, optional
            Default is ``"kNoGround"``.

        Returns
        -------
        CfgEdgeTerminal
            The newly created terminal object.
        """
        terminal = CfgEdgeTerminal(
            name=name,
            impedance=impedance,
            is_circuit_port=is_circuit_port,
            boundary_type=boundary_type,
            reference_terminal=reference_terminal,
            amplitude=amplitude,
            phase=phase,
            terminal_to_ground=terminal_to_ground,
            primitive=primitive,
            point_on_edge_x=point_on_edge_x,
            point_on_edge_y=point_on_edge_y,
            horizontal_extent_factor=horizontal_extent_factor,
            vertical_extent_factor=vertical_extent_factor,
            pec_launch_width=pec_launch_width,
            hfss_type=hfss_type,
        )
        self.terminals.append(terminal)
        return terminal

    def add_bundle_terminal(
        self,
        name: str,
        terminals: list[str],
    ):
        """Add a bundle terminal that groups several existing terminals.

        Parameters
        ----------
        name : str
            Unique bundle name.
        terminals : list of str
            Names of the terminals to bundle, e.g.
            ``["t_vdd", "t_gnd"]``.

        Returns
        -------
        CfgBundleTerminal
            The newly created bundle-terminal object.

        Examples
        --------
        cfg.terminals.add_bundle_terminal("bundle_demo", ["t_vdd", "t_gnd"])
        """
        terminal = CfgBundleTerminal(
            name=name,
            terminals=terminals,
        )
        self.terminals.append(terminal)
        return terminal
