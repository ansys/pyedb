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

from typing import List, Literal, Optional, Union

from pydantic import BaseModel


class CfgBase(BaseModel):
    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
    }


class CfgTerminal(CfgBase):
    name: str
    impedance: Union[float, int, str]
    is_circuit_port: bool
    reference_terminal: Optional[str] = None
    amplitude: Optional[Union[float, int, str]] = 1
    phase: Optional[Union[float, int, str]] = 0
    terminal_to_ground: Optional[Literal["kNoGround", "kNegative", "kPositive"]] = "kNoGround"
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
    ]
    hfss_type: Literal["Wave", "Gap", None]


class CfgPadstackInstanceTerminal(CfgTerminal):
    terminal_type: str = "padstack_instance"
    padstack_instance: str
    padstack_instance_id: Optional[int] = None
    layer: Optional[Union[str, None]] = None


class CfgPinGroupTerminal(CfgTerminal):
    terminal_type: str = "pin_group"
    is_circuit_port: bool = True
    pin_group: str


class CfgPointTerminal(CfgTerminal):
    terminal_type: str = "point"
    x: Union[float, int, str]
    y: Union[float, int, str]
    layer: str
    net: str


class CfgEdgeTerminal(CfgTerminal):
    terminal_type: str = "edge"
    name: str
    primitive: str
    point_on_edge_x: Union[float, int, str]
    point_on_edge_y: Union[float, int, str]
    horizontal_extent_factor: Union[int, str]
    vertical_extent_factor: Union[int, str]
    pec_launch_width: Union[int, str]


class CfgBundleTerminal(CfgBase):
    terminal_type: str = "bundle"
    terminals: List[str]
    name: str


class CfgTerminals(CfgBase):
    terminals: List[
        Union[
            CfgPadstackInstanceTerminal, CfgPinGroupTerminal, CfgPointTerminal, CfgEdgeTerminal, CfgBundleTerminal, dict
        ]
    ]

    @classmethod
    def create(cls, terminals: List[dict]):
        manager = cls(terminals=[])
        for i in terminals:
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
        padstack_instance,
        name,
        impedance,
        is_circuit_port,
        boundary_type,
        hfss_type,
        reference_terminal=None,
        amplitude=1,
        phase=0,
        terminal_to_ground="kNoGround",
        padstack_instance_id=None,
        layer=None,
    ):
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

    def add_pin_group_terminal(
        self,
        pin_group,
        name,
        impedance,
        boundary_type,
        reference_terminal=None,
        amplitude=1,
        phase=0,
        terminal_to_ground="kNoGround",
    ):
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

    def add_point_terminal(
        self,
        x,
        y,
        layer,
        name,
        impedance,
        boundary_type,
        net,
        reference_terminal=None,
        amplitude=1,
        phase=0,
        terminal_to_ground="kNoGround",
    ):
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

    def add_edge_terminal(
        self,
        name,
        impedance,
        is_circuit_port,
        boundary_type,
        primitive,
        point_on_edge_x,
        point_on_edge_y,
        horizontal_extent_factor=6,
        vertical_extent_factor=8,
        pec_launch_width="0.02mm",
        reference_terminal=None,
        amplitude=1,
        phase=0,
        terminal_to_ground="kNoGround",
    ):
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
            hfss_type="Wave",
        )
        self.terminals.append(terminal)

    def add_bundle_terminal(
        self,
        terminals,
        name,
    ):
        terminal = CfgBundleTerminal(
            terminals=terminals,
            name=name,
        )
        self.terminals.append(terminal)
