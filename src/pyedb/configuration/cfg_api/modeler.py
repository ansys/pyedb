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

"""Modeler configuration builder API.

Data models: :class:`CfgTraceData`, :class:`CfgPlaneData`,
:class:`CfgPrimitivesToDelete`, :class:`CfgModelerData` (pydantic roots
defined here).
The runtime class :class:`~pyedb.configuration.cfg_modeler.CfgModeler`
requires a live EDB connection; this API layer owns the pure-data pydantic
models and serialises to plain dicts that the runtime class can consume.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

from pyedb.configuration.cfg_common import CfgBaseModel

if TYPE_CHECKING:
    from pyedb.configuration.cfg_api.components import ComponentConfig


class CfgTraceData(CfgBaseModel):
    """Pydantic data model for a routed trace."""

    name: str
    layer: str
    width: Union[str, float]
    net_name: str = ""
    path: List[List[Union[float, str]]] = Field(default_factory=list)
    incremental_path: List[List[Union[float, str]]] = Field(default_factory=list)
    start_cap_style: str = "round"
    end_cap_style: str = "round"
    corner_style: str = "sharp"

    model_config = {"populate_by_name": True, "extra": "ignore"}


class CfgPlaneData(CfgBaseModel):
    """Pydantic data model for a copper plane (rectangle, circle, or polygon)."""

    name: str = ""
    layer: str
    net_name: str = ""
    type: Literal["rectangle", "circle", "polygon"] = "rectangle"

    # rectangle
    lower_left_point: List[Union[float, str]] = Field(default_factory=list)
    upper_right_point: List[Union[float, str]] = Field(default_factory=list)
    corner_radius: Union[float, str] = 0
    rotation: Union[float, str] = 0
    voids: List[Any] = Field(default_factory=list)

    # polygon
    points: List[List[float]] = Field(default_factory=list)

    # circle
    radius: Union[float, str] = 0
    position: List[float] = Field(default_factory=lambda: [0, 0])

    model_config = {"populate_by_name": True, "extra": "ignore"}


class CfgPrimitivesToDelete(CfgBaseModel):
    """Pydantic data model for primitives-to-delete filter."""

    layer_name: List[str] = Field(default_factory=list)
    name: List[str] = Field(default_factory=list)
    net_name: List[str] = Field(default_factory=list)

    model_config = {"populate_by_name": True, "extra": "ignore"}


class CfgModelerData(BaseModel):
    """Root pydantic model for the ``modeler`` configuration section."""

    traces: List[CfgTraceData] = Field(default_factory=list)
    planes: List[CfgPlaneData] = Field(default_factory=list)
    padstack_definitions: List[Dict] = Field(default_factory=list)
    padstack_instances: List[Dict] = Field(default_factory=list)
    components: List[Dict] = Field(default_factory=list)
    primitives_to_delete: CfgPrimitivesToDelete = Field(default_factory=CfgPrimitivesToDelete)


class ModelerConfig:
    """Fluent builder for the ``modeler`` configuration section.

    Wraps :class:`CfgModelerData`.

    Examples
    --------
    >>> cfg.modeler.add_trace("T1", layer="TOP", width="100um", path=[[0,0],[1e-3,0]])
    >>> cfg.modeler.add_rectangular_plane("GND_PLANE", layer="BOT", net_name="GND")
    """

    def __init__(self):
        self._model = CfgModelerData()
        # keep a typed list for ComponentConfig objects (serialise on demand)
        self._component_configs: List["ComponentConfig"] = []

    # ── traces ────────────────────────────────────────────────────────────

    def add_trace(
        self,
        name: str,
        layer: str,
        width: Union[str, float],
        net_name: str = "",
        path: Optional[List[List[Union[float, str]]]] = None,
        incremental_path: Optional[List[List[Union[float, str]]]] = None,
        start_cap_style: str = "round",
        end_cap_style: str = "round",
        corner_style: str = "sharp",
    ) -> CfgTraceData:
        """Add a routed trace.

        Returns
        -------
        CfgTraceData
        """
        trace = CfgTraceData(
            name=name,
            layer=layer,
            width=width,
            net_name=net_name,
            path=path or [],
            incremental_path=incremental_path or [],
            start_cap_style=start_cap_style,
            end_cap_style=end_cap_style,
            corner_style=corner_style,
        )
        self._model.traces.append(trace)
        return trace

    # ── planes ────────────────────────────────────────────────────────────

    def add_rectangular_plane(
        self,
        layer: str,
        name: str = "",
        net_name: str = "",
        lower_left_point: Optional[List] = None,
        upper_right_point: Optional[List] = None,
        corner_radius: Union[float, str] = 0,
        rotation: Union[float, str] = 0,
        voids: Optional[List] = None,
    ) -> CfgPlaneData:
        """Add a rectangular copper plane."""
        plane = CfgPlaneData(
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
        self._model.planes.append(plane)
        return plane

    def add_circular_plane(
        self,
        layer: str,
        name: str = "",
        net_name: str = "",
        radius: Union[float, str] = 0,
        position: Optional[List[float]] = None,
        voids: Optional[List] = None,
    ) -> CfgPlaneData:
        """Add a circular copper plane."""
        plane = CfgPlaneData(
            name=name,
            layer=layer,
            net_name=net_name,
            type="circle",
            radius=radius,
            position=position or [0, 0],
            voids=voids or [],
        )
        self._model.planes.append(plane)
        return plane

    def add_polygon_plane(
        self,
        layer: str,
        name: str = "",
        net_name: str = "",
        points: Optional[List[List[float]]] = None,
        voids: Optional[List] = None,
    ) -> CfgPlaneData:
        """Add a polygon copper plane."""
        plane = CfgPlaneData(
            name=name,
            layer=layer,
            net_name=net_name,
            type="polygon",
            points=points or [],
            voids=voids or [],
        )
        self._model.planes.append(plane)
        return plane

    # ── padstacks ─────────────────────────────────────────────────────────

    def add_padstack_definition(self, name: str, **kwargs):
        """Add a padstack definition."""
        data = {"name": name}
        data.update(kwargs)
        self._model.padstack_definitions.append(data)

    def add_padstack_instance(self, **kwargs):
        """Add a padstack instance."""
        self._model.padstack_instances.append(kwargs)

    # ── components ────────────────────────────────────────────────────────

    def add_component(
        self,
        reference_designator: str,
        part_type: Optional[str] = None,
        enabled: Optional[bool] = None,
        definition: Optional[str] = None,
        placement_layer: Optional[str] = None,
    ) -> "ComponentConfig":
        """Add a component via the modeler section.

        Returns
        -------
        ComponentConfig
        """
        from pyedb.configuration.cfg_api.components import ComponentConfig

        comp = ComponentConfig(
            reference_designator=reference_designator,
            part_type=part_type,
            enabled=enabled,
            definition=definition,
            placement_layer=placement_layer,
        )
        self._component_configs.append(comp)
        return comp

    # ── primitives to delete ──────────────────────────────────────────────

    def delete_primitives_by_layer(self, layer_names: List[str]):
        """Mark primitives on given layers for deletion."""
        self._model.primitives_to_delete.layer_name.extend(layer_names)

    def delete_primitives_by_name(self, primitive_names: List[str]):
        """Mark primitives with given names for deletion."""
        self._model.primitives_to_delete.name.extend(primitive_names)

    def delete_primitives_by_net(self, net_names: List[str]):
        """Mark primitives on given nets for deletion."""
        self._model.primitives_to_delete.net_name.extend(net_names)

    # ── serialise ─────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """Serialise to a dict consumable by
        :class:`~pyedb.configuration.cfg_modeler.CfgModeler`."""
        # flush ComponentConfig objects into the pydantic model
        self._model.components = [c.to_dict() for c in self._component_configs]

        data = self._model.model_dump(exclude_none=True)

        # drop empty primitives_to_delete
        ptd = data.get("primitives_to_delete", {})
        if not any(ptd.values()):
            data.pop("primitives_to_delete", None)

        return data

