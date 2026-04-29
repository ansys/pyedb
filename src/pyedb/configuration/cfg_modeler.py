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
"""Build geometry-creation and cleanup entries for the ``modeler`` section."""

from copy import deepcopy as copy
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TypedDict, Union

from pyedb.configuration.cfg_components import CfgComponent
from pyedb.configuration.cfg_padstacks import CfgPadstackDefinition, CfgPadstackInstance


@dataclass
class CfgTrace:
    """Represent one trace primitive scheduled for creation."""

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
    """Represent one plane primitive scheduled for creation."""

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
    position: List[Union[float, str]] = field(default_factory=lambda: [0, 0])


class PrimitivesToDeleteDict(TypedDict, total=False):
    """Typed mapping of primitives queued for deletion by selector."""

    layer_name: List[str]
    name: List[str]
    net_name: List[str]


@dataclass
class CfgModeler:
    """Collect geometry and modeler operations for serialization."""

    traces: List[CfgTrace] = field(default_factory=list)
    planes: List[CfgPlane] = field(default_factory=list)

    def __init__(self, pedb=None, data: Dict | None = None):
        data = data or {}
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
        name: str,
        layer: str,
        width: str,
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
            path or [],
            width,
            net_name,
            start_cap_style,
            end_cap_style,
            corner_style,
            incremental_path or [],
        )
        self.traces.append(trace_obj)
        return trace_obj

    def add_rectangular_plane(
        self,
        layer: str,
        name: str = "",
        net_name: str = "",
        lower_left_point: Optional[List[float]] = None,
        upper_right_point: Optional[List[float]] = None,
        corner_radius: float = 0,
        rotation: float = 0,
        voids: Optional[List[Any]] = None,
    ):
        """Add a rectangular copper plane.

        Parameters
        ----------
        layer : str
            Layer name on which to create the rectangle.
        name : str, optional
            Primitive AEDT name.
        net_name : str, optional
            Net name for the plane.
        lower_left_point : list of float, optional
            ``[x, y]`` lower-left corner in metres.
        upper_right_point : list of float, optional
            ``[x, y]`` upper-right corner in metres.
        corner_radius : float, optional
            Corner rounding radius.  Default is ``0``.
        rotation : float, optional
            Rotation in degrees.  Default is ``0``.
        voids : list, optional
            Void cutout descriptors.

        Returns
        -------
        CfgPlane
            The newly created plane object.

        Examples
        --------
        >>> cfg.modeler.add_rectangular_plane(
        ...     "bot",
        ...     "gnd_plane",
        ...     "GND",
        ...     lower_left_point=[-0.05, -0.05],
        ...     upper_right_point=[0.05, 0.05],
        ... )
        """
        plane_obj = CfgPlane(
            name=name,
            layer=layer,
            net_name=net_name,
            type="rectangle",
            lower_left_point=lower_left_point or [],
            upper_right_point=upper_right_point or [],
            corner_radius=corner_radius,
            rotation=rotation,
            voids=voids or [],
        )
        self.planes.append(plane_obj)
        return plane_obj

    def add_circular_plane(
        self,
        layer: str,
        name: str = "",
        net_name: str = "",
        corner_radius: float = 0,
        rotation: float = 0,
        voids: Optional[List[Any]] = None,
        radius: Union[float, str] = 0,
        position: Optional[List[Union[float, str]]] = None,
    ):
        """Add a circular copper plane.

        Parameters
        ----------
        layer : str
            Layer on which to place the circle.
        name : str, optional
            Primitive AEDT name.
        net_name : str, optional
            Net name.
        corner_radius : float, optional
            Unused for circles; kept for API symmetry.  Default is ``0``.
        rotation : float, optional
            Rotation in degrees.  Default is ``0``.
        voids : list, optional
            Void cutout descriptors.
        radius : float or str, optional
            Circle radius, e.g. ``"1mm"``.  Default is ``0``.
        position : list of float, optional
            ``[x, y]`` centre position in metres.  Default is ``[0, 0]``.

        Returns
        -------
        CfgPlane
            The newly created plane object.
        """
        plane_obj = CfgPlane(
            name=name,
            layer=layer,
            net_name=net_name,
            type="circle",
            corner_radius=corner_radius,
            rotation=rotation,
            voids=voids or [],
            radius=radius,
            position=position or [0, 0],
        )
        self.planes.append(plane_obj)
        return plane_obj

    def add_polygon_plane(
        self,
        layer: str,
        name: str = "",
        net_name: str = "",
        corner_radius: float = 0,
        rotation: float = 0,
        voids: Optional[List[Any]] = None,
        points: Optional[List[List[float]]] = None,
    ):
        """Add a polygon copper plane.

        Parameters
        ----------
        layer : str
            Layer on which to place the polygon.
        name : str, optional
            Primitive AEDT name.
        net_name : str, optional
            Net name.
        corner_radius : float, optional
            Corner rounding radius.  Default is ``0``.
        rotation : float, optional
            Rotation in degrees.  Default is ``0``.
        voids : list, optional
            Void cutout descriptors.
        points : list of list of float, optional
            Ordered ``[x, y]`` vertex coordinates in metres.

        Returns
        -------
        CfgPlane
            The newly created plane object.

        Examples
        --------
        >>> cfg.modeler.add_polygon_plane(
        ...     "top",
        ...     "sig_poly",
        ...     "SIG",
        ...     points=[[0, 0], [0.01, 0], [0.01, 0.005], [0, 0.005]],
        ... )
        """
        plane_obj = CfgPlane(
            name=name,
            layer=layer,
            net_name=net_name,
            type="polygon",
            corner_radius=corner_radius,
            rotation=rotation,
            voids=voids or [],
            points=points or [],
        )
        self.planes.append(plane_obj)
        return plane_obj

    def add_padstack_definition(
        self,
        name: str,
        hole_plating_thickness=None,
        material=None,
        hole_range=None,
        pad_parameters=None,
        hole_parameters=None,
        solder_ball_parameters=None,
    ):
        """Add a modeler padstack definition."""
        obj = CfgPadstackDefinition.create(
            name=name,
            hole_plating_thickness=hole_plating_thickness,
            hole_material=material,
            hole_range=hole_range,
            pad_parameters=pad_parameters,
            hole_parameters=hole_parameters,
            solder_ball_parameters=solder_ball_parameters,
        )
        self.padstack_defs.append(obj)
        return obj

    def add_padstack_instance(self, **kwargs):
        """Add a modeler padstack instance."""
        obj = CfgPadstackInstance.create(**kwargs)
        self.padstack_instances.append(obj)
        return obj

    def add_component(
        self,
        reference_designator: str,
        part_type: Optional[str] = None,
        enabled: Optional[bool] = None,
        definition: Optional[str] = None,
        placement_layer: Optional[str] = None,
        pins: Optional[List[str]] = None,
    ):
        """Add a component instance to the modeler section."""
        comp = CfgComponent(
            self._pedb,
            None,
            reference_designator=reference_designator,
            part_type=part_type,
            enabled=enabled,
            definition=definition,
            placement_layer=placement_layer,
            pins=pins or [],
        )
        self.components.append(comp)
        return comp

    def delete_primitives_by_layer(self, layer_names: List[str]):
        """Schedule all primitives on the given layers for deletion."""
        self.primitives_to_delete.setdefault("layer_name", []).extend(layer_names)

    def delete_primitives_by_name(self, primitive_names: List[str]):
        """Schedule primitives with the given names for deletion."""
        self.primitives_to_delete.setdefault("name", []).extend(primitive_names)

    def delete_primitives_by_net(self, net_names: List[str]):
        """Schedule all primitives on the given nets for deletion."""
        self.primitives_to_delete.setdefault("net_name", []).extend(net_names)

    def to_dict(self) -> dict:
        """Serialize the modeler configuration."""
        data: dict = {}
        if self.traces:
            data["traces"] = [vars(t) for t in self.traces]
        if self.planes:
            data["planes"] = [vars(p) for p in self.planes]
        if self.padstack_defs:
            data["padstack_definitions"] = [p.model_dump(exclude_none=True) for p in self.padstack_defs]
        if self.padstack_instances:
            data["padstack_instances"] = [
                p.model_dump(exclude_none=True, by_alias=False) for p in self.padstack_instances
            ]
        if self.components:
            data["components"] = [c.to_dict() for c in self.components]
        if any(v for v in self.primitives_to_delete.values()):
            data["primitives_to_delete"] = self.primitives_to_delete
        return data
