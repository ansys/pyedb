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
from copy import deepcopy as copy
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TypedDict, Union

from pyedb.configuration.cfg_components import CfgComponent
from pyedb.configuration.cfg_padstacks import CfgPadstackDefinition, CfgPadstackInstance


@dataclass
class CfgTrace:
    name: str
    layer: str
    path: List[List[Union[float, str]]]
    width: str
    net_name: str
    start_cap_style: str
    end_cap_style: str
    corner_style: str
    incremental_path: List[List[Union[float, str]]]


@dataclass
class CfgPlane:
    name: str = ""
    layer: str = ""
    net_name: str = ""
    type: str = "rectangle"

    # rectangle
    lower_left_point: List[Union[float, str]] = field(default_factory=list)
    upper_right_point: List[Union[float, str]] = field(default_factory=list)
    corner_radius: Union[float, str] = 0
    rotation: Union[float, str] = 0
    voids: List[Any] = field(default_factory=list)

    # polygon
    points: List[List[float]] = field(default_factory=list)

    # circle
    radius: Union[float, str] = 0
    position: List[float] = field(default_factory=lambda: [0, 0])


class PrimitivesToDeleteDict(TypedDict, total=False):
    layer_name: List[str]
    name: List[str]
    net_name: List[str]


@dataclass
class CfgModeler:
    """Manage configuration general settings."""

    traces: List[CfgTrace] = field(default_factory=list)
    planes: List[CfgPlane] = field(default_factory=list)

    def __init__(self, pedb, data: Dict):
        self._pedb = pedb
        self.traces = []
        self.planes = []

        self.padstack_defs = [CfgPadstackDefinition.create(**i) for i in data.get("padstack_definitions", [])]
        self.padstack_instances = [CfgPadstackInstance.create(**i) for i in data.get("padstack_instances", [])]

        self.components = [CfgComponent(pedb, None, **i) for i in data.get("components", [])]
        self.primitives_to_delete: PrimitivesToDeleteDict = data.get(
            "primitives_to_delete", {"layer_name": [], "name": [], "net_name": []}
        )

        for trace_data in data.get("traces", []):
            self.add_trace(**trace_data)

        for plane_data in data.get("planes", []):
            plane_data = copy(plane_data)
            shape = plane_data.pop("type")
            if shape == "rectangle":
                self.add_rectangular_plane(**plane_data)
            elif shape == "circle":
                self.add_circular_plane(**plane_data)
            elif shape == "polygon":
                self.add_polygon_plane(**plane_data)

    def add_trace(
        self,
        layer: str,
        width: str,
        name: str,
        net_name: str = "",
        start_cap_style: str = "round",
        end_cap_style: str = "round",
        corner_style: str = "sharp",
        path: Optional[Any] = None,
        incremental_path: Optional[Any] = None,
    ):
        """Add a trace from a dictionary of parameters."""

        trace_obj = CfgTrace(
            name,
            layer,
            path,
            width,
            net_name,
            start_cap_style,
            end_cap_style,
            corner_style,
            incremental_path,
        )
        self.traces.append(trace_obj)
        return name

    def add_rectangular_plane(
        self,
        layer: str,
        name: str = "",
        net_name: str = "",
        lower_left_point: List[float] = "",
        upper_right_point: List[float] = "",
        corner_radius: float = 0,
        rotation: float = 0,
        voids: Optional[List[Any]] = "",
    ):
        plane_obj = CfgPlane(
            name=name,
            layer=layer,
            net_name=net_name,
            type="rectangle",
            lower_left_point=lower_left_point,
            upper_right_point=upper_right_point,
            corner_radius=corner_radius,
            rotation=rotation,
            voids=voids,
        )
        self.planes.append(plane_obj)
        return name

    def add_circular_plane(
        self,
        layer: str,
        name: str = "",
        net_name: str = "",
        corner_radius: float = 0,
        rotation: float = 0,
        voids: Optional[List[Any]] = "",
        radius: Union[float, str] = 0,
        position: List[Union[float, str]] = "",
    ):
        plane_obj = CfgPlane(
            name=name,
            layer=layer,
            net_name=net_name,
            type="circle",
            corner_radius=corner_radius,
            rotation=rotation,
            voids=voids,
            radius=radius,
            position=position,
        )
        self.planes.append(plane_obj)
        return name

    def add_polygon_plane(
        self,
        layer: str,
        name: str = "",
        net_name: str = "",
        corner_radius: float = 0,
        rotation: float = 0,
        voids: Optional[List[Any]] = "",
        points: List[List[float]] = "",
    ):
        plane_obj = CfgPlane(
            name=name,
            layer=layer,
            net_name=net_name,
            type="polygon",
            corner_radius=corner_radius,
            rotation=rotation,
            voids=voids,
            points=points,
        )
        self.planes.append(plane_obj)
        return name
