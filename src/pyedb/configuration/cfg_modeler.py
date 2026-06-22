# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

from typing import Optional

from pydantic import Field

from pyedb.configuration.cfg_common import CfgBaseModel
from pyedb.configuration.cfg_components import CfgComponent
from pyedb.configuration.cfg_padstacks import CfgPadstackDefinition, CfgPadstackInstance


class CfgTrace(CfgBaseModel):
    """Represent one trace primitive scheduled for creation."""

    model_config = {"populate_by_name": True, "extra": "ignore"}

    name: str
    layer: str
    path: list[list[float | int | str]] = Field(default_factory=list)
    width: str
    net_name: str = ""
    start_cap_style: str = "round"
    end_cap_style: str = "round"
    corner_style: str = "sharp"
    incremental_path: list[list[float | int | str]] = Field(default_factory=list)


class CfgPlane(CfgBaseModel):
    """Represent one plane primitive scheduled for creation."""

    model_config = {"populate_by_name": True, "extra": "ignore"}

    name: str = ""
    layer: str = ""
    net_name: str = ""
    type: str = "rectangle"

    # rectangle
    lower_left_point: list[float | int | str] = Field(default_factory=list)
    upper_right_point: list[float | int | str] = Field(default_factory=list)
    corner_radius: float | int | str = 0
    rotation: float | int | str = 0
    voids: list = Field(default_factory=list)

    # polygon
    points: list[list[float | int | str]] = Field(default_factory=list)

    # circle
    radius: float | int | str = 0
    position: list[float | int | str] = Field(default_factory=lambda: [0, 0])


class CfgModeler:
    """Collect geometry and modeler operations for serialization."""

    def __init__(self, pedb=None, data: dict | None = None):
        data = data or {}
        self._pedb = pedb
        self.traces = []
        self.planes = []

        self.padstack_defs = [CfgPadstackDefinition.create(**i) for i in data.get("padstack_definitions", [])]
        self.padstack_instances = [CfgPadstackInstance.create(**i) for i in data.get("padstack_instances", [])]

        self.components = [CfgComponent(pedb, None, **i) for i in data.get("components", [])]
        self.primitives_to_delete: dict[str, list[str]] = data.get(
            "primitives_to_delete", {"layer_name": [], "name": [], "net_name": []}
        )

        for trace_data in data.get("traces", []):
            self.add_trace(**trace_data)

        for plane_data in data.get("planes", []):
            plane_obj = CfgPlane.model_validate(plane_data)
            self.planes.append(plane_obj)

    def add_trace(
        self,
        name: str,
        layer: str,
        width: str,
        net_name: str = "",
        start_cap_style: str = "round",
        end_cap_style: str = "round",
        corner_style: str = "sharp",
        path: Optional[list[list[float | int | str]]] = None,
        incremental_path: Optional[list[list[float | int | str]]] = None,
    ):
        """Add a trace to the modeler configuration.

        Exactly one of *path* or *incremental_path* should be supplied.

        Parameters
        ----------
        name : str
            AEDT name assigned to the created trace primitive.
        layer : str
            Layer name on which to create the trace, e.g. ``"1_Top"``.
        width : str
            Trace width including units, e.g. ``"0.1mm"`` or ``"100um"``.
        net_name : str, optional
            Net the trace belongs to, e.g. ``"SIG"``.  Default is ``""``.
        start_cap_style : str, optional
            Start-cap termination style.  Accepted values: ``"round"``
            (default), ``"extended"``, ``"flat"``.
        end_cap_style : str, optional
            End-cap termination style.  Same options as *start_cap_style*.
            Default is ``"round"``.
        corner_style : str, optional
            Corner bend style.  Accepted values: ``"sharp"`` (default),
            ``"round"``, ``"mitered"``.
        path : list of [x, y], optional
            Ordered list of absolute ``[x, y]`` waypoints in metres that define
            the trace route, e.g. ``[[0, 0], [0.01, 0], [0.01, 0.005]]``.
            Use this when absolute coordinates are known.
        incremental_path : list of [x, y], optional
            Ordered list of ``[x, y]`` waypoints where the first point is
            absolute and subsequent points are added incrementally via
            :meth:`pyedb.modeler.Path.add_point`.  Use this for step-by-step
            construction.  Mutually exclusive with *path*.

        Returns
        -------
        CfgTrace
            The newly created trace descriptor object.

        Examples
        --------
        Absolute path:

        cfg.modeler.add_trace(
            name="trace_clk",
            layer="1_Top",
            width="0.1mm",
            net_name="CLK",
            path=[[0.0, 0.0], [0.005, 0.0], [0.005, 0.003]]
        )

        Incremental path:

            cfg.modeler.add_trace(
                name="trace_sig",
                layer="1_Top",
                width="0.1mm",
                net_name="SIG",
                incremental_path=[[0.0, 0.0], [0.005, 0.0]]
            )
        """
        trace_obj = CfgTrace(
            name=name,
            layer=layer,
            path=path or [],
            width=width,
            net_name=net_name,
            start_cap_style=start_cap_style,
            end_cap_style=end_cap_style,
            corner_style=corner_style,
            incremental_path=incremental_path or [],
        )
        self.traces.append(trace_obj)
        return trace_obj

    def _add_plane(self, **kwargs) -> "CfgPlane":
        """Create and register a :class:`CfgPlane` from keyword arguments."""
        plane_obj = CfgPlane(**kwargs)
        self.planes.append(plane_obj)
        return plane_obj

    def add_rectangular_plane(
        self,
        layer: str,
        name: str = "",
        net_name: str = "",
        lower_left_point: Optional[list[float | int]] = None,
        upper_right_point: Optional[list[float | int]] = None,
        corner_radius: float = 0,
        rotation: float | int = 0,
        voids: Optional[list] = None,
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
        cfg.modeler.add_rectangular_plane(
            "bot",
            "gnd_plane",
            "GND",
            lower_left_point=[-0.05, -0.05],
            upper_right_point=[0.05, 0.05]
        )
        """
        return self._add_plane(
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

    def add_circular_plane(
        self,
        layer: str,
        name: str = "",
        net_name: str = "",
        corner_radius: float | int = 0,
        rotation: float | int = 0,
        voids: Optional[list] = None,
        radius: float | int | str = 0,
        position: Optional[list[float | int | str]] = None,
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
        return self._add_plane(
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

    def add_polygon_plane(
        self,
        layer: str,
        name: str = "",
        net_name: str = "",
        corner_radius: float | int = 0,
        rotation: float | int = 0,
        voids: Optional[list] = None,
        points: Optional[list[list[float | int]]] = None,
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
        cfg.modeler.add_polygon_plane(
            "top",
            "sig_poly",
            "SIG",
            points=[[0, 0], [0.01, 0], [0.01, 0.005], [0, 0.005]]
        )
        """
        return self._add_plane(
            name=name,
            layer=layer,
            net_name=net_name,
            type="polygon",
            corner_radius=corner_radius,
            rotation=rotation,
            voids=voids or [],
            points=points or [],
        )

    def delete_primitives_by_layer(self, layer_names: list[str]):
        """Schedule all primitives on the given layers for deletion."""
        self.primitives_to_delete.setdefault("layer_name", []).extend(layer_names)

    def delete_primitives_by_name(self, primitive_names: list[str]):
        """Schedule primitives with the given names for deletion."""
        self.primitives_to_delete.setdefault("name", []).extend(primitive_names)

    def delete_primitives_by_net(self, net_names: list[str]):
        """Schedule all primitives on the given nets for deletion."""
        self.primitives_to_delete.setdefault("net_name", []).extend(net_names)

    def to_dict(self) -> dict:
        """Serialize modeler configuration to a plain dictionary."""
        data = {}
        if self.traces:
            data["traces"] = [t.model_dump(exclude_none=True) for t in self.traces]
        if self.planes:
            data["planes"] = [p.model_dump(exclude_none=True) for p in self.planes]
        if self.padstack_defs:
            data["padstack_definitions"] = [d.model_dump(exclude_none=True, by_alias=False) for d in self.padstack_defs]
        if self.padstack_instances:
            data["padstack_instances"] = [
                i.model_dump(exclude_none=True, by_alias=False) for i in self.padstack_instances
            ]
        if self.components:
            data["components"] = [c.to_dict() for c in self.components]
        prim_del = {k: v for k, v in self.primitives_to_delete.items() if v}
        if prim_del:
            data["primitives_to_delete"] = prim_del
        return data
