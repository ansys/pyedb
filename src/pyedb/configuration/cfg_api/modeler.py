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

"""Build the ``modeler`` configuration section.

The builders in this module define primitive geometry, padstack content,
component instances, and cleanup requests for geometry-driven configuration
workflows.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Union

if TYPE_CHECKING:
    from pyedb.configuration.cfg_api.components import ComponentConfig


class ModelerConfig:
    """Collect geometry and modeler operations for serialization."""

    def __init__(self):
        """Initialize the modeler configuration."""
        self._traces: List[dict] = []
        self._planes: List[dict] = []
        self._padstack_definitions: List[dict] = []
        self._padstack_instances: List[dict] = []
        self._component_configs: List = []
        self._primitives_to_delete: dict = {"layer_name": [], "name": [], "net_name": []}

    def add_trace(
        self,
        name: str,
        layer: str,
        width: Union[str, float],
        net_name: str = "",
        path: Optional[List] = None,
        incremental_path: Optional[List] = None,
        start_cap_style: str = "round",
        end_cap_style: str = "round",
        corner_style: str = "sharp",
    ) -> dict:
        """Add a trace primitive.

        Returns
        -------
        dict
            Stored trace dictionary.
        """
        t = {
            "name": name,
            "layer": layer,
            "width": width,
            "net_name": net_name,
            "path": path or [],
            "incremental_path": incremental_path or [],
            "start_cap_style": start_cap_style,
            "end_cap_style": end_cap_style,
            "corner_style": corner_style,
        }
        self._traces.append(t)
        return t

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
    ) -> dict:
        """Add a rectangular plane primitive.

        Returns
        -------
        dict
            Stored plane dictionary.
        """
        p = {
            "type": "rectangle",
            "name": name,
            "layer": layer,
            "net_name": net_name,
            "lower_left_point": lower_left_point or [],
            "upper_right_point": upper_right_point or [],
            "corner_radius": corner_radius,
            "rotation": rotation,
            "voids": voids or [],
        }
        self._planes.append(p)
        return p

    def add_circular_plane(
        self,
        layer: str,
        name: str = "",
        net_name: str = "",
        radius: Union[float, str] = 0,
        position: Optional[List[float]] = None,
        voids: Optional[List] = None,
    ) -> dict:
        """Add a circular plane primitive.

        Returns
        -------
        dict
            Stored plane dictionary.
        """
        p = {
            "type": "circle",
            "name": name,
            "layer": layer,
            "net_name": net_name,
            "radius": radius,
            "position": position or [0, 0],
            "voids": voids or [],
        }
        self._planes.append(p)
        return p

    def add_polygon_plane(
        self,
        layer: str,
        name: str = "",
        net_name: str = "",
        points: Optional[List[List[float]]] = None,
        voids: Optional[List] = None,
    ) -> dict:
        """Add a polygon plane primitive.

        Returns
        -------
        dict
            Stored plane dictionary.
        """
        p = {
            "type": "polygon",
            "name": name,
            "layer": layer,
            "net_name": net_name,
            "points": points or [],
            "voids": voids or [],
        }
        self._planes.append(p)
        return p

    def add_padstack_definition(self, name: str, **kwargs):
        """Add a modeler padstack definition.

        Parameters
        ----------
        name : str
            Padstack definition name.
        **kwargs
            Additional padstack definition fields.
        """
        data = {"name": name}
        data.update(kwargs)
        self._padstack_definitions.append(data)

    def add_padstack_instance(self, **kwargs):
        """Add a modeler padstack instance.

        Parameters
        ----------
        **kwargs
            Padstack instance fields.
        """
        self._padstack_instances.append(kwargs)

    def add_component(
        self,
        reference_designator: str,
        part_type: Optional[str] = None,
        enabled: Optional[bool] = None,
        definition: Optional[str] = None,
        placement_layer: Optional[str] = None,
    ) -> "ComponentConfig":
        """Add a component instance to the modeler section.

        Returns
        -------
        ComponentConfig
            Newly created component builder.
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

    def delete_primitives_by_layer(self, layer_names: List[str]):
        """Schedule primitives on the given layers for deletion."""
        self._primitives_to_delete["layer_name"].extend(layer_names)

    def delete_primitives_by_name(self, primitive_names: List[str]):
        """Schedule primitives with the given names for deletion."""
        self._primitives_to_delete["name"].extend(primitive_names)

    def delete_primitives_by_net(self, net_names: List[str]):
        """Schedule primitives on the given nets for deletion."""
        self._primitives_to_delete["net_name"].extend(net_names)

    def to_dict(self) -> dict:
        """Serialize the modeler configuration.

        Returns
        -------
        dict
            Dictionary containing only populated modeler subsections.
        """
        data: dict = {}
        if self._traces:
            data["traces"] = self._traces
        if self._planes:
            data["planes"] = self._planes
        if self._padstack_definitions:
            data["padstack_definitions"] = self._padstack_definitions
        if self._padstack_instances:
            data["padstack_instances"] = self._padstack_instances
        if self._component_configs:
            data["components"] = [c.to_dict() for c in self._component_configs]
        if any(v for v in self._primitives_to_delete.values()):
            data["primitives_to_delete"] = self._primitives_to_delete
        return data
