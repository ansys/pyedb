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

from typing import List, Literal, Optional, Union

from pydantic import Field

from pyedb.configuration.cfg_common import CfgBaseModel


class CfgTerminal(CfgBaseModel):
    """Base class for explicit terminal definitions."""

    name: str
    impedance: Union[float, int, str]
    is_circuit_port: bool
    reference_terminal: Optional[str] = None
    amplitude: Optional[Union[float, int, str]] = 1
    phase: Optional[Union[float, int, str]] = 0
    terminal_to_ground: Literal[
        "kNoGround",
        "kNegative",
        "kNegativeNode",
        "kPositive",
        "kPositiveNode",
        "no_ground",
        "negative",
        "positive",
    ] | None = (
        "kNoGround"
    )
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
    hfss_type: Literal["Wave", "Gap", None]


class CfgPadstackInstanceTerminal(CfgTerminal):
    """Represent a terminal created from a named padstack instance."""

    terminal_type: str = "padstack_instance"
    padstack_instance: str
    padstack_instance_id: Optional[int] = None
    layer: Optional[Union[str, None]] = None

    def __init__(
        self,
        name: str,
        padstack_instance: str,
        impedance: Union[float, int, str],
        boundary_type,
        hfss_type=None,
        is_circuit_port: bool = False,
        reference_terminal: Optional[str] = None,
        amplitude: Optional[Union[float, int, str]] = 1,
        phase: Optional[Union[float, int, str]] = 0,
        terminal_to_ground="kNoGround",
        layer=None,
        padstack_instance_id=None,
        **kwargs,
    ):
        super().__init__(
            name=name,
            impedance=impedance,
            is_circuit_port=is_circuit_port,
            reference_terminal=reference_terminal,
            amplitude=amplitude,
            phase=phase,
            terminal_to_ground=terminal_to_ground,
            boundary_type=boundary_type,
            hfss_type=hfss_type,
            padstack_instance=padstack_instance,
            padstack_instance_id=padstack_instance_id,
            layer=layer,
            **kwargs,
        )

    def to_dict(self) -> dict:
        return self.model_dump(exclude_none=True)


class CfgPinGroupTerminal(CfgTerminal):
    """Represent a terminal created from a named pin group."""

    terminal_type: str = "pin_group"
    is_circuit_port: bool = True
    pin_group: str

    def __init__(
        self,
        name: str,
        pin_group: str,
        impedance: Union[float, int, str],
        boundary_type,
        reference_terminal: Optional[str] = None,
        amplitude: Optional[Union[float, int, str]] = 1,
        phase: Optional[Union[float, int, str]] = 0,
        terminal_to_ground="kNoGround",
        **kwargs,
    ):
        kwargs.pop("is_circuit_port", None)
        kwargs.pop("hfss_type", None)
        super().__init__(
            name=name,
            pin_group=pin_group,
            impedance=impedance,
            is_circuit_port=True,
            boundary_type=boundary_type,
            reference_terminal=reference_terminal,
            amplitude=amplitude,
            phase=phase,
            terminal_to_ground=terminal_to_ground,
            hfss_type=None,
            **kwargs,
        )

    def to_dict(self) -> dict:
        return self.model_dump(exclude_none=True)


class CfgPointTerminal(CfgTerminal):
    """Represent a terminal placed at explicit XY coordinates."""

    terminal_type: str = "point"
    x: Union[float, int, str]
    y: Union[float, int, str]
    layer: str
    net: str

    def __init__(
        self,
        name: str,
        x: Union[float, int, str],
        y: Union[float, int, str],
        layer: str,
        net: str,
        impedance: Union[float, int, str],
        boundary_type,
        reference_terminal: Optional[str] = None,
        amplitude: Optional[Union[float, int, str]] = 1,
        phase: Optional[Union[float, int, str]] = 0,
        terminal_to_ground="kNoGround",
        **kwargs,
    ):
        kwargs.pop("is_circuit_port", None)
        kwargs.pop("hfss_type", None)
        super().__init__(
            name=name,
            x=x,
            y=y,
            layer=layer,
            net=net,
            impedance=impedance,
            is_circuit_port=True,
            boundary_type=boundary_type,
            reference_terminal=reference_terminal,
            amplitude=amplitude,
            phase=phase,
            terminal_to_ground=terminal_to_ground,
            hfss_type=None,
            **kwargs,
        )

    def to_dict(self) -> dict:
        return self.model_dump(exclude_none=True)


class CfgEdgeTerminal(CfgTerminal):
    """Represent a terminal attached to a primitive edge."""

    terminal_type: str = "edge"
    name: str
    primitive: str
    point_on_edge_x: Union[float, int, str]
    point_on_edge_y: Union[float, int, str]
    horizontal_extent_factor: Union[int, str]
    vertical_extent_factor: Union[int, str]
    pec_launch_width: Union[int, str]

    def __init__(
        self,
        name: str,
        primitive: str,
        point_on_edge_x: Union[float, int, str],
        point_on_edge_y: Union[float, int, str],
        impedance: Union[float, int, str],
        boundary_type,
        hfss_type="Wave",
        horizontal_extent_factor: Union[int, str] = 6,
        vertical_extent_factor: Union[int, str] = 8,
        pec_launch_width: Union[int, str] = "0.02mm",
        is_circuit_port: bool = False,
        reference_terminal: Optional[str] = None,
        amplitude: Optional[Union[float, int, str]] = 1,
        phase: Optional[Union[float, int, str]] = 0,
        terminal_to_ground="kNoGround",
        **kwargs,
    ):
        super().__init__(
            name=name,
            primitive=primitive,
            point_on_edge_x=point_on_edge_x,
            point_on_edge_y=point_on_edge_y,
            impedance=impedance,
            is_circuit_port=is_circuit_port,
            boundary_type=boundary_type,
            reference_terminal=reference_terminal,
            amplitude=amplitude,
            phase=phase,
            terminal_to_ground=terminal_to_ground,
            hfss_type=hfss_type,
            horizontal_extent_factor=horizontal_extent_factor,
            vertical_extent_factor=vertical_extent_factor,
            pec_launch_width=pec_launch_width,
            **kwargs,
        )

    def to_dict(self) -> dict:
        return self.model_dump(exclude_none=True)


class CfgBundleTerminal(CfgBaseModel):
    """Represent a bundle terminal built from other terminal names."""

    terminal_type: str = "bundle"
    terminals: List[str]
    name: str

    def __init__(self, name: str, terminals: List[str], **kwargs):
        super().__init__(name=name, terminals=terminals, **kwargs)

    def to_dict(self) -> dict:
        return self.model_dump(exclude_none=True)


class CfgTerminals(CfgBaseModel):
    """Collect low-level terminal definitions for serialization."""

    terminals: List[
        Union[
            CfgPadstackInstanceTerminal, CfgPinGroupTerminal, CfgPointTerminal, CfgEdgeTerminal, CfgBundleTerminal, dict
        ]
    ] = Field(default_factory=list)

    @classmethod
    def create(cls, terminals: List[dict]):
        """Reconstruct a :class:`CfgTerminals` instance from raw dictionaries.

        Parameters
        ----------
        terminals : list of dict
            Terminal payload dictionaries, each containing a ``terminal_type``
            key and the corresponding field values.

        Returns
        -------
        CfgTerminals
            Populated terminal collection.

        Raises
        ------
        ValueError
            If an unknown ``terminal_type`` value is encountered.
        """
        manager = cls(terminals=[])
        for i in terminals:
            i = dict(i)
            terminal_type = i.pop("terminal_type")
            if terminal_type == "padstack_instance":
                manager.add_padstack_instance_terminal(**i)
            elif terminal_type == "pin_group":
                manager.add_pin_group_terminal(**i)
            elif terminal_type == "point":
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
        name,
        padstack_instance,
        impedance,
        boundary_type,
        hfss_type=None,
        is_circuit_port=False,
        reference_terminal=None,
        amplitude=1,
        phase=0,
        terminal_to_ground="kNoGround",
        padstack_instance_id=None,
        layer=None,
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
        name,
        pin_group,
        impedance,
        boundary_type,
        reference_terminal=None,
        amplitude=1,
        phase=0,
        terminal_to_ground="kNoGround",
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
        >>> cfg.terminals.add_pin_group_terminal("t_vdd", "pg_VDD", 50, "port")
        """
        terminal = CfgPinGroupTerminal(
            pin_group=pin_group,
            name=name,
            impedance=impedance,
            is_circuit_port=True,
            boundary_type=boundary_type,
            reference_terminal=reference_terminal,
            amplitude=amplitude,
            phase=phase,
            terminal_to_ground=terminal_to_ground,
            hfss_type=None,
        )
        self.terminals.append(terminal)
        return terminal

    def add_point_terminal(
        self,
        name,
        x,
        y,
        layer,
        net,
        impedance,
        boundary_type,
        reference_terminal=None,
        amplitude=1,
        phase=0,
        terminal_to_ground="kNoGround",
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
            is_circuit_port=True,
            boundary_type=boundary_type,
            reference_terminal=reference_terminal,
            amplitude=amplitude,
            phase=phase,
            net=net,
            terminal_to_ground=terminal_to_ground,
            hfss_type=None,
        )
        self.terminals.append(terminal)
        return terminal

    def add_edge_terminal(
        self,
        name,
        primitive,
        point_on_edge_x,
        point_on_edge_y,
        impedance,
        boundary_type,
        hfss_type="Wave",
        horizontal_extent_factor=6,
        vertical_extent_factor=8,
        pec_launch_width="0.02mm",
        is_circuit_port=False,
        reference_terminal=None,
        amplitude=1,
        phase=0,
        terminal_to_ground="kNoGround",
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
        name,
        terminals,
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
        >>> cfg.terminals.add_bundle_terminal("bundle_demo", ["t_vdd", "t_gnd"])
        """
        terminal = CfgBundleTerminal(
            name=name,
            terminals=terminals,
        )
        self.terminals.append(terminal)
        return terminal

    def to_list(self):
        """Serialize all configured terminals.

        Returns
        -------
        list of dict
            Each element is the serialized dictionary for one terminal.
        """
        return [t.to_dict() if hasattr(t, "to_dict") else t for t in self.terminals]

