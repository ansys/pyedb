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

"""Build port configuration entries.

This module defines builders for circuit, coaxial, wave, gap, and differential
wave ports used in the ``ports`` configuration list.
"""

from __future__ import annotations

from typing import List, Optional, Union


class PortConfig:
    """Circuit / coax port definition.

    Parameters
    ----------
    name : str
    port_type : str
        ``"circuit"`` or ``"coax"``.
    positive_terminal : dict
        Terminal specifier dict, e.g. ``{"pin": "A1"}`` or ``{"pin_group": "pg1"}`` or
        ``{"net": "SIG"}``.
    negative_terminal : dict, optional
    reference_designator : str, optional
    impedance : float or str, optional
    distributed : bool

    """

    def __init__(
        self,
        name: str,
        port_type: str,
        positive_terminal: dict,
        negative_terminal: Optional[dict] = None,
        reference_designator: Optional[str] = None,
        impedance: Optional[Union[float, str]] = None,
        distributed: bool = False,
    ):
        """Initialize a port configuration.

        Parameters
        ----------
        name : str
            Port name.
        port_type : str
            ``"circuit"`` or ``"coax"``.
        positive_terminal : dict
            Positive terminal specifier.
        negative_terminal : dict, optional
            Negative terminal specifier.
        reference_designator : str, optional
            Component reference designator.
        impedance : float or str, optional
            Port impedance.
        distributed : bool, default: False
            Whether the port is distributed.

        """
        self.name = name
        self.type = port_type
        self.positive_terminal = positive_terminal
        self.negative_terminal = negative_terminal
        self.reference_designator = reference_designator
        self.impedance = impedance
        self.distributed = distributed

    def to_dict(self) -> dict:
        """Serialize the port definition.

        Returns
        -------
        dict
            Dictionary ready for inclusion in the ``ports`` configuration list.

        """
        data: dict = {"name": self.name, "type": self.type, "positive_terminal": self.positive_terminal}
        if self.negative_terminal:
            data["negative_terminal"] = self.negative_terminal
        if self.reference_designator:
            data["reference_designator"] = self.reference_designator
        if self.impedance is not None:
            data["impedance"] = self.impedance
        if self.distributed:
            data["distributed"] = self.distributed
        return data


class EdgePortConfig:
    """Edge (wave/gap) port definition.

    Parameters
    ----------
    name : str
    port_type : str
        ``"wave_port"`` or ``"gap_port"``.
    primitive_name : str
        Name of the primitive to place the port on.
    point_on_edge : list of float
        [x, y] point on the edge.
    horizontal_extent_factor : float
    vertical_extent_factor : float
    pec_launch_width : str

    """

    def __init__(
        self,
        name: str,
        port_type: str,
        primitive_name: str,
        point_on_edge: List[float],
        horizontal_extent_factor: float = 5,
        vertical_extent_factor: float = 3,
        pec_launch_width: str = "0.01mm",
    ):
        """Initialize an edge port configuration.

        Parameters
        ----------
        name : str
            Port name.
        port_type : str
            ``"wave_port"`` or ``"gap_port"``.
        primitive_name : str
            Name of the primitive to place the port on.
        point_on_edge : list of float
            ``[x, y]`` point used to locate the edge.
        horizontal_extent_factor : float, default: 5
            Horizontal extent factor.
        vertical_extent_factor : float, default: 3
            Vertical extent factor.
        pec_launch_width : str, default: "0.01mm"
            PEC launch width.

        """
        self.name = name
        self.type = port_type
        self.primitive_name = primitive_name
        self.point_on_edge = point_on_edge
        self.horizontal_extent_factor = horizontal_extent_factor
        self.vertical_extent_factor = vertical_extent_factor
        self.pec_launch_width = pec_launch_width

    def to_dict(self) -> dict:
        """Serialize the edge-port definition.

        Returns
        -------
        dict
            Dictionary ready for inclusion in the ``ports`` configuration list.

        """
        return {
            "name": self.name,
            "type": self.type,
            "primitive_name": self.primitive_name,
            "point_on_edge": self.point_on_edge,
            "horizontal_extent_factor": self.horizontal_extent_factor,
            "vertical_extent_factor": self.vertical_extent_factor,
            "pec_launch_width": self.pec_launch_width,
        }


class DiffWavePortConfig:
    """Differential wave port.

    Parameters
    ----------
    name : str
    positive_terminal : dict
        Must contain ``primitive_name`` and ``point_on_edge`` (plus optionally extent factors).
    negative_terminal : dict
        Same structure as *positive_terminal*.
    horizontal_extent_factor : float
    vertical_extent_factor : float
    pec_launch_width : str

    """

    def __init__(
        self,
        name: str,
        positive_terminal: dict,
        negative_terminal: dict,
        horizontal_extent_factor: float = 5,
        vertical_extent_factor: float = 3,
        pec_launch_width: str = "0.01mm",
    ):
        """Initialize a differential wave port configuration.

        Parameters
        ----------
        name : str
            Port name.
        positive_terminal : dict
            Positive edge-terminal specifier.
        negative_terminal : dict
            Negative edge-terminal specifier.
        horizontal_extent_factor : float, default: 5
            Horizontal extent factor.
        vertical_extent_factor : float, default: 3
            Vertical extent factor.
        pec_launch_width : str, default: "0.01mm"
            PEC launch width.

        """
        self.name = name
        self.positive_terminal = positive_terminal
        self.negative_terminal = negative_terminal
        self.horizontal_extent_factor = horizontal_extent_factor
        self.vertical_extent_factor = vertical_extent_factor
        self.pec_launch_width = pec_launch_width

    def to_dict(self) -> dict:
        """Serialize the differential wave-port definition.

        Returns
        -------
        dict
            Dictionary ready for inclusion in the ``ports`` configuration list.

        """
        return {
            "name": self.name,
            "type": "diff_wave_port",
            "positive_terminal": self.positive_terminal,
            "negative_terminal": self.negative_terminal,
            "horizontal_extent_factor": self.horizontal_extent_factor,
            "vertical_extent_factor": self.vertical_extent_factor,
            "pec_launch_width": self.pec_launch_width,
        }


class PortsConfig:
    """Collect port definitions for serialization."""

    def __init__(self):
        """Initialize the ports configuration."""
        self._ports: List[Union[PortConfig, EdgePortConfig, dict]] = []

    def add_circuit_port(
        self,
        name: str,
        positive_terminal: dict,
        negative_terminal: Optional[dict] = None,
        reference_designator: Optional[str] = None,
        impedance: Optional[Union[float, str]] = None,
        distributed: bool = False,
    ) -> PortConfig:
        """Add a circuit port.

        Parameters
        ----------
        name : str
            Port name.
        positive_terminal : dict
            Positive terminal specifier.
        negative_terminal : dict, optional
            Negative terminal specifier.
        reference_designator : str, optional
            Component reference designator used to disambiguate the terminal.
        impedance : float or str, optional
            Port impedance.
        distributed : bool
            Whether the port is distributed.

        Returns
        -------
        PortConfig

        """
        port = PortConfig(
            name=name,
            port_type="circuit",
            positive_terminal=positive_terminal,
            negative_terminal=negative_terminal,
            reference_designator=reference_designator,
            impedance=impedance,
            distributed=distributed,
        )
        self._ports.append(port)
        return port

    def add_coax_port(
        self,
        name: str,
        positive_terminal: Optional[dict] = None,
        reference_designator: Optional[str] = None,
        impedance: Optional[Union[float, str]] = None,
        # ── convenience shortcuts ──────────────────────────────────────────
        padstack: Optional[str] = None,
        net: Optional[str] = None,
        pin: Optional[str] = None,
    ) -> PortConfig:
        """Add a coaxial (via) port.

        The positive terminal can be specified either via the generic
        *positive_terminal* dict **or** through one of the three convenience
        shortcuts (*padstack*, *net*, *pin*).  Exactly one of the four
        approaches must be supplied.

        Terminal types and their behaviour
        -----------------------------------
        ``padstack`` *(str)*
            Name of a single padstack instance.  Creates one coax port on
            that via.

            >>> cfg.ports.add_coax_port("p1", padstack="via_A1")

        ``net`` *(str)* + ``reference_designator`` *(str)*
            All pins of *net* on component *reference_designator*.  When the
            component has more than one matching pin the port is created as
            **distributed** (one coax port per pin, named
            ``<name>_<pin_name>``).

            >>> cfg.ports.add_coax_port(
            ...     "p_vdd", net="VDD", reference_designator="U1"
            ... )

        ``pin`` *(str)* + ``reference_designator`` *(str)*
            A single named pin on component *reference_designator*.

            >>> cfg.ports.add_coax_port(
            ...     "p_a1", pin="A1", reference_designator="U1"
            ... )

        ``positive_terminal`` *(dict)*
            Raw terminal specifier dict — use :class:`TerminalInfo` helpers to
            build it:

            * ``TerminalInfo.padstack("via_A1")``
            * ``TerminalInfo.net("VDD", reference_designator="U1")``
            * ``TerminalInfo.pin("A1", reference_designator="U1")``

        .. note::
           **Solder-ball geometry** (height, diameter, shape) is a
           *component* property, not a port property.  Configure it via
           ``cfg.components.add(refdes).set_solder_ball_properties(…)`` or
           the component section of the configuration file.

        Parameters
        ----------
        name : str
            Port name.
        positive_terminal : dict, optional
            Raw terminal specifier.  Ignored when *padstack*, *net*, or *pin*
            is supplied.
        reference_designator : str, optional
            Component reference designator.  Required when *net* or *pin* is
            used.
        impedance : float or str, optional
            Port impedance (default solver value when omitted).
        padstack : str, optional
            Padstack instance name shortcut.
        net : str, optional
            Net-name shortcut.  Requires *reference_designator*.
        pin : str, optional
            Pin-name shortcut.  Requires *reference_designator*.

        Returns
        -------
        PortConfig
            Newly created coaxial port entry.

        Raises
        ------
        ValueError
            When none of *positive_terminal*, *padstack*, *net*, or *pin* is
            supplied, or when *net* / *pin* is used without
            *reference_designator*.

        Examples
        --------
        Via padstack name:

        >>> cfg.ports.add_coax_port("coax_via", padstack="via_A1")

        All VDD pins on U1 (distributed):

        >>> cfg.ports.add_coax_port(
        ...     "coax_vdd", net="VDD", reference_designator="U1"
        ... )

        Single pin A1 on U1:

        >>> cfg.ports.add_coax_port(
        ...     "coax_a1", pin="A1", reference_designator="U1", impedance=50
        ... )

        Using TerminalInfo:

        >>> from pyedb.configuration.cfg_api import TerminalInfo
        >>> cfg.ports.add_coax_port(
        ...     "coax_pg",
        ...     positive_terminal=TerminalInfo.net("SIG", reference_designator="U1"),
        ... )

        """
        # Build positive_terminal from convenience shortcuts
        if padstack is not None:
            positive_terminal = {"padstack": padstack}
        elif net is not None:
            if not reference_designator:
                raise ValueError("'reference_designator' is required when 'net' is supplied.")
            positive_terminal = {"net": net, "reference_designator": reference_designator}
        elif pin is not None:
            if not reference_designator:
                raise ValueError("'reference_designator' is required when 'pin' is supplied.")
            positive_terminal = {"pin": pin, "reference_designator": reference_designator}
        elif positive_terminal is None:
            raise ValueError(
                "Provide one of: positive_terminal, padstack, net, or pin."
            )

        port = PortConfig(
            name=name,
            port_type="coax",
            positive_terminal=positive_terminal,
            reference_designator=reference_designator,
            impedance=impedance,
        )
        self._ports.append(port)
        return port

    def add_wave_port(
        self,
        name: str,
        primitive_name: str,
        point_on_edge: List[float],
        horizontal_extent_factor: float = 5,
        vertical_extent_factor: float = 3,
        pec_launch_width: str = "0.01mm",
    ) -> EdgePortConfig:
        """Add a wave port.

        Parameters
        ----------
        name : str
            Port name.
        primitive_name : str
            Primitive on which to create the port.
        point_on_edge : list of float
            ``[x, y]`` point used to locate the edge.
        horizontal_extent_factor : float
            Horizontal extent factor.
        vertical_extent_factor : float
            Vertical extent factor.
        pec_launch_width : str
            PEC launch width.

        Returns
        -------
        EdgePortConfig

        """
        port = EdgePortConfig(
            name=name,
            port_type="wave_port",
            primitive_name=primitive_name,
            point_on_edge=point_on_edge,
            horizontal_extent_factor=horizontal_extent_factor,
            vertical_extent_factor=vertical_extent_factor,
            pec_launch_width=pec_launch_width,
        )
        self._ports.append(port)
        return port

    def add_gap_port(
        self,
        name: str,
        primitive_name: str,
        point_on_edge: List[float],
        horizontal_extent_factor: float = 5,
        vertical_extent_factor: float = 3,
        pec_launch_width: str = "0.01mm",
    ) -> EdgePortConfig:
        """Add a gap port.

        Parameters
        ----------
        name : str
            Port name.
        primitive_name : str
            Primitive on which to create the port.
        point_on_edge : list of float
            ``[x, y]`` point used to locate the edge.
        horizontal_extent_factor : float, default: 5
            Horizontal extent factor.
        vertical_extent_factor : float, default: 3
            Vertical extent factor.
        pec_launch_width : str, default: "0.01mm"
            PEC launch width.

        Returns
        -------
        EdgePortConfig
            Newly created gap-port entry.

        """
        port = EdgePortConfig(
            name=name,
            port_type="gap_port",
            primitive_name=primitive_name,
            point_on_edge=point_on_edge,
            horizontal_extent_factor=horizontal_extent_factor,
            vertical_extent_factor=vertical_extent_factor,
            pec_launch_width=pec_launch_width,
        )
        self._ports.append(port)
        return port

    def add_diff_wave_port(
        self,
        name: str,
        positive_terminal: dict,
        negative_terminal: dict,
        horizontal_extent_factor: float = 5,
        vertical_extent_factor: float = 3,
        pec_launch_width: str = "0.01mm",
    ) -> DiffWavePortConfig:
        """Add a differential wave port.

        Parameters
        ----------
        name : str
            Port name.
        positive_terminal : dict
            Positive edge-terminal specifier.
        negative_terminal : dict
            Negative edge-terminal specifier.
        horizontal_extent_factor : float, default: 5
            Horizontal extent factor.
        vertical_extent_factor : float, default: 3
            Vertical extent factor.
        pec_launch_width : str, default: "0.01mm"
            PEC launch width.

        Returns
        -------
        DiffWavePortConfig
            Newly created differential wave-port entry.

        """
        port = DiffWavePortConfig(
            name=name,
            positive_terminal=positive_terminal,
            negative_terminal=negative_terminal,
            horizontal_extent_factor=horizontal_extent_factor,
            vertical_extent_factor=vertical_extent_factor,
            pec_launch_width=pec_launch_width,
        )
        self._ports.append(port)
        return port

    def to_list(self) -> List[dict]:
        """Serialize all configured ports.

        Returns
        -------
        list[dict]
            Port definitions in insertion order.

        """
        return [p.to_dict() for p in self._ports]
