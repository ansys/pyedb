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

        Parameters
        ----------
        name : str
            Trace AEDT name.
        layer : str
            Layer on which to place the trace.
        width : str or float
            Trace width, e.g. ``"0.15mm"`` or ``150e-6``.
        net_name : str, default: ``""``
            Net name.
        path : list of [x, y], optional
            Absolute path point list, e.g. ``[[0, 0], [0.01, 0]]``.
        incremental_path : list of [dx, dy], optional
            Incremental path (use instead of *path* for relative placement).
        start_cap_style : str, default: ``"round"``
            Start cap style: ``"round"``, ``"flat"``, or ``"extended"``.
        end_cap_style : str, default: ``"round"``
            End cap style.
        corner_style : str, default: ``"sharp"``
            Corner style: ``"sharp"``, ``"round"``, or ``"mitered"``.

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

        Parameters
        ----------
        layer : str
            Layer on which to place the rectangle.
        name : str, default: ``""``
            AEDT name.
        net_name : str, default: ``""``
            Net name.
        lower_left_point : list of float, optional
            ``[x, y]`` lower-left corner in metres.
        upper_right_point : list of float, optional
            ``[x, y]`` upper-right corner in metres.
        corner_radius : float or str, default: ``0``
            Corner rounding radius.
        rotation : float or str, default: ``0``
            Rotation in degrees.
        voids : list of str, optional
            Names of primitives to use as cutouts (voids) in this plane.

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

        Parameters
        ----------
        layer : str
            Layer on which to place the circle.
        name : str, default: ``""``
            AEDT name.
        net_name : str, default: ``""``
            Net name.
        radius : float or str, default: ``0``
            Circle radius in metres.
        position : list of float, optional
            ``[x, y]`` centre position in metres.
        voids : list of str, optional
            Names of primitives to use as cutouts.

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

        Parameters
        ----------
        layer : str
            Layer on which to place the polygon.
        name : str, default: ``""``
            AEDT name.
        net_name : str, default: ``""``
            Net name.
        points : list of [x, y], optional
            Polygon vertices in metres.
        voids : list of str, optional
            Names of primitives to use as cutouts.

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

    def add_padstack_definition(
        self,
        name: str,
        hole_plating_thickness: Optional[Union[str, float]] = None,
        material: Optional[str] = None,
        hole_range: Optional[str] = None,
        pad_parameters: Optional[dict] = None,
        hole_parameters: Optional[dict] = None,
        solder_ball_parameters: Optional[dict] = None,
    ) -> dict:
        """Add a modeler padstack definition.

        Parameters
        ----------
        name : str
            Padstack definition name.
        hole_plating_thickness : str or float, optional
            Plating thickness, e.g. ``"25um"``.
        material : str, optional
            Hole conductor material name.
        hole_range : str, optional
            Layer range the hole spans.
        pad_parameters : dict, optional
            Raw pad-parameter dictionary.
        hole_parameters : dict, optional
            Raw hole-parameter dictionary.
        solder_ball_parameters : dict, optional
            Raw solder-ball parameter dictionary.

        Returns
        -------
        dict
            Stored definition dictionary.
        """
        data: dict = {"name": name}
        for key, val in {
            "hole_plating_thickness": hole_plating_thickness,
            "material": material,
            "hole_range": hole_range,
            "pad_parameters": pad_parameters,
            "hole_parameters": hole_parameters,
            "solder_ball_parameters": solder_ball_parameters,
        }.items():
            if val is not None:
                data[key] = val
        self._padstack_definitions.append(data)
        return data

    def add_padstack_instance(
        self,
        name: Optional[str] = None,
        net_name: Optional[str] = None,
        definition: Optional[str] = None,
        layer_range: Optional[List[str]] = None,
        position: Optional[List[Union[str, float]]] = None,
        rotation: Optional[Union[str, float]] = None,
        is_pin: bool = False,
        hole_override_enabled: Optional[bool] = None,
        hole_override_diameter: Optional[Union[str, float]] = None,
        solder_ball_layer: Optional[str] = None,
    ) -> dict:
        """Add a modeler padstack instance.

        Parameters
        ----------
        name : str, optional
            Instance AEDT name.
        net_name : str, optional
            Net name.
        definition : str, optional
            Padstack definition name.
        layer_range : list of str, optional
            ``[start_layer, stop_layer]``.
        position : list of str or float, optional
            ``[x, y]`` placement in metres.
        rotation : str or float, optional
            Rotation in degrees.
        is_pin : bool, default: ``False``
            Whether the instance is a component pin.
        hole_override_enabled : bool, optional
            Enable hole-size override.
        hole_override_diameter : str or float, optional
            Override drill diameter.
        solder_ball_layer : str, optional
            Layer on which the solder ball sits.

        Returns
        -------
        dict
            Stored instance dictionary.
        """
        data: dict = {}
        for key, val in {
            "name": name,
            "net_name": net_name,
            "definition": definition,
            "layer_range": layer_range,
            "position": position,
            "rotation": rotation,
            "is_pin": is_pin,
            "hole_override_enabled": hole_override_enabled,
            "hole_override_diameter": hole_override_diameter,
            "solder_ball_layer": solder_ball_layer,
        }.items():
            if val is not None:
                data[key] = val
        self._padstack_instances.append(data)
        return data

    def add_component(
        self,
        reference_designator: str,
        part_type: Optional[str] = None,
        enabled: Optional[bool] = None,
        definition: Optional[str] = None,
        placement_layer: Optional[str] = None,
        pins: Optional[List[str]] = None,
    ) -> "ComponentConfig":
        """Add a component instance to the modeler section.

        Parameters
        ----------
        reference_designator : str
            Component instance reference designator, e.g. ``"U1"``.
        part_type : str, optional
            Component part type (``"resistor"``, ``"capacitor"``, ``"ic"``, …).
        enabled : bool, optional
            Whether the component is enabled.
        definition : str, optional
            Component definition / part name.
        placement_layer : str, optional
            Layer on which the component is placed.
        pins : list of str, optional
            Explicit pin names used when the component is created from padstack
            instances (gRPC mode).

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
        if pins is not None:
            comp.pins = pins
        self._component_configs.append(comp)
        return comp

    def delete_primitives_by_layer(self, layer_names: List[str]):
        """Schedule all primitives on the given layers for deletion.

        Parameters
        ----------
        layer_names : list of str
            Layer names whose primitives should be removed.
        """
        self._primitives_to_delete["layer_name"].extend(layer_names)

    def delete_primitives_by_name(self, primitive_names: List[str]):
        """Schedule primitives with the given names for deletion.

        Parameters
        ----------
        primitive_names : list of str
            AEDT names of primitives to remove.
        """
        self._primitives_to_delete["name"].extend(primitive_names)

    def delete_primitives_by_net(self, net_names: List[str]):
        """Schedule all primitives on the given nets for deletion.

        Parameters
        ----------
        net_names : list of str
            Net names whose primitives should be removed.
        """
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
