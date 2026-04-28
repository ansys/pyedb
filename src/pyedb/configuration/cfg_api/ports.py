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

from typing import List, Literal, Optional, Union


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
        self._ports: List[Any] = []

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
        positive_terminal: dict,
        reference_designator: Optional[str] = None,
        impedance: Optional[Union[float, str]] = None,
    ) -> PortConfig:
        """Add a coaxial port.

        Parameters
        ----------
        name : str
            Port name.
        positive_terminal : dict
            Positive terminal specifier.
        reference_designator : str, optional
            Component reference designator used to disambiguate the terminal.
        impedance : float or str, optional
            Port impedance.

        Returns
        -------
        PortConfig
            Newly created coaxial port entry.
        """
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
