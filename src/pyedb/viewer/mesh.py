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

"""Prepare exterior/hole coverage and split-coordinate GPU data, independent of Qt."""

from dataclasses import dataclass
import math

import numpy as np

from pyedb.viewer.scene import Bounds, SceneComponent, ScenePad, ScenePolygon, SceneTrace, union_bounds

# Ten vec4 attributes, all per-instance. Coordinates retain their low parts.
SDF_STRIDE = 40
SDF_CHUNK_SIZE = 256


def split_coordinates(values):
    """Pack double coordinates as [x_high, y_high, x_low, y_low] float32 vertices."""
    values = np.asarray(values, dtype=np.float64)
    high = values.astype(np.float32)
    low = (values - high.astype(np.float64)).astype(np.float32)
    return np.ascontiguousarray(np.concatenate((high, low), axis=-1), dtype=np.float32)


@dataclass(frozen=True)
class MeshBatch:
    object_id: int
    layer: str
    net: str | None
    bounds: Bounds
    index_start: int
    outer_count: int
    hole_count: int
    category: str = "zone"


@dataclass(frozen=True)
class PreparedScene:
    vertices: np.ndarray
    indices: np.ndarray
    batches: tuple[MeshBatch, ...]
    instances: np.ndarray
    sdf_batches: tuple
    nets: tuple
    component_batches: tuple = ()
    pin_batches: tuple = ()


@dataclass(frozen=True)
class ComponentBatch:
    component: SceneComponent
    instance_start: int


@dataclass(frozen=True)
class PinBatch:
    """Pin ownership linked to an existing analytic packet or custom copper mesh."""

    pin: ScenePad | ScenePolygon
    instance_start: int | None
    instance_count: int = 1


@dataclass(frozen=True)
class SdfBatch:
    layer: str
    bounds: Bounds
    instance_start: int
    instance_count: int
    has_drills: bool
    category: str


def _sdf_packet(item, net_id):
    packet = np.zeros(SDF_STRIDE, dtype=np.float32)
    packet[12:20] = split_coordinates([item.bounds[:2], item.bounds[2:]]).reshape(-1)
    packet[27] = net_id
    if isinstance(item, SceneTrace):
        packet[:12] = split_coordinates([item.start, item.end, item.center or item.start]).reshape(-1)
        packet[20] = item.width
        packet[24] = int(item.center is not None)
        packet[25:27] = [{"flat": 0, "round": 1, "extended": 2}[cap] for cap in item.end_caps]
        if item.center is not None:
            packet[22] = math.atan2(item.start[1] - item.center[1], item.start[0] - item.center[0])
            packet[23] = item.sweep
            packet[30] = math.dist(item.start, item.center)
            packet[31] = math.dist(item.start, item.center) - float(packet[30])
        else:
            length = math.dist(item.start, item.end)
            tangent = tuple((b - a) / length for a, b in zip(item.start, item.end)) if length else (1.0, 0.0)
            packet[36:40] = split_coordinates([tangent])[0]
    elif isinstance(item, ScenePad):
        packet[:4] = split_coordinates([item.center])[0]
        packet[20:23] = (*item.size, item.rotation)
        packet[24] = 2 if item.shape == "circle" else 3
        if item.shape == "circle" and math.dist(item.center, item.hole_center) + item.size[0] / 2 <= item.hole_radius:
            packet[25] = -1  # Drill-only record: do not leave a spurious antialiased copper rim.
        packet[28:30] = item.corner_radius, item.hole_radius
        packet[31] = int(item.shape == "bullet")
        packet[32:36] = split_coordinates([item.hole_center])[0]
        packet[36:40] = (
            item.size[0] - float(packet[20]),
            item.size[1] - float(packet[21]),
            item.hole_radius - float(packet[29]),
            0,
        )
    elif isinstance(item, SceneComponent):
        x0, y0, x1, y1 = item.bounds
        packet[:4] = split_coordinates([[x0 + (x1 - x0) / 2, y0 + (y1 - y0) / 2]])[0]
        packet[20:22] = x1 - x0, y1 - y0
        packet[24] = 5  # Screen-width component envelope, independent of copper material.
    else:
        packet[:12] = split_coordinates(item.points[:3]).reshape(-1)
        if len(item.points) == 4:
            packet[32:36] = split_coordinates(item.points[3:])[0]
        packet[24] = 4
        packet[25] = len(item.points)
    return packet


def scene_network_names(scene):
    """Share stable network palette IDs between the renderer and workspace lists."""
    names = dict.fromkeys(net for net in scene.net_names if net)
    names.update(dict.fromkeys(sorted({item.net for item in scene.geometry if item.net})))
    names.update(dict.fromkeys(sorted({net for component in scene.components for net in component.nets if net})))
    return (None, *names)


def _prepare_sdf(scene):
    nets = scene_network_names(scene)
    net_ids = {net: index for index, net in enumerate(nets)}
    packets, batches, pin_batches = [], [], []
    by_layer = {}
    for collection, category in ((scene.traces, "trace"), (scene.joins, "trace"), (scene.pads, "pad")):
        for item in collection:
            by_layer.setdefault((item.layer, category), []).append(item)
    for (layer, category), items in by_layer.items():
        # Spatial chunks keep culling useful without issuing a draw per object.
        # Keep the component-placement pads contiguous for their overlay pass,
        # while retaining spatial order within ordinary copper and pin groups.
        items.sort(
            key=lambda item: (
                bool(getattr(item, "component", None)),
                bool(getattr(item, "component", None)) and getattr(item, "component_layer", layer) != layer,
                item.bounds[0],
                item.bounds[1],
            )
        )
        for start in range(0, len(items), SDF_CHUNK_SIZE):
            chunk = items[start : start + SDF_CHUNK_SIZE]
            bounds = [item.bounds for item in chunk]
            batches.append(
                SdfBatch(
                    layer,
                    union_bounds(bounds),
                    len(packets),
                    len(chunk),
                    any(getattr(item, "hole_radius", 0) > 0 for item in chunk),
                    category,
                )
            )
            for item in chunk:
                if getattr(item, "component", None):
                    pin_batches.append(PinBatch(item, len(packets)))
                packets.append(_sdf_packet(item, net_ids.get(item.net, 0)))
    # Custom pins need only their existing copper mesh and ownership metadata.
    # No auxiliary contour geometry is generated for pin borders.
    for polygon in scene.polygons:
        if not polygon.component:
            continue
        pin_batches.append(PinBatch(polygon, None, 0))
    component_batches = []
    for component in sorted(scene.components, key=lambda component: component.layer):
        component_batches.append(ComponentBatch(component, len(packets)))
        packets.append(_sdf_packet(component, 0))
    instances = np.ascontiguousarray(packets, dtype=np.float32).reshape(-1, SDF_STRIDE)
    return instances, tuple(batches), nets, tuple(component_batches), tuple(pin_batches)


def prepare_scene(scene):
    """Triangulate each ring independently; holes are subtracted with GPU stencil.

    Hole coverage is a union, even for overlapping holes. It must never be
    submitted as ordinary filled geometry.
    """
    if scene.polygons:
        try:
            import mapbox_earcut
        except ImportError as exc:
            raise ImportError("Triangulation requires: pip install 'pyedb[viewer]'.") from exc
    vertices, indices, batches = [], [], []
    vertex_count = index_count = 0
    for polygon in scene.polygons:
        start = index_count
        counts = []
        for ring in (polygon.exterior, *polygon.holes):
            coordinates = np.asarray(ring, dtype=np.float64)
            # Rebase for triangulation as well, avoiding large absolute-coordinate cancellation.
            local = coordinates - coordinates[0]
            triangles = mapbox_earcut.triangulate_float64(local, np.array([len(ring)], dtype=np.uint32))
            if not len(triangles):
                raise ValueError(f"Primitive {polygon.object_id}: contour cannot be triangulated.")
            if vertex_count + len(ring) > np.iinfo(np.uint32).max:
                raise ValueError("Layout exceeds the uint32 vertex index limit.")
            vertices.append(split_coordinates(coordinates))
            indices.append(triangles + np.uint32(vertex_count))
            vertex_count += len(ring)
            index_count += len(triangles)
            counts.append(len(triangles))
        batches.append(
            MeshBatch(
                polygon.object_id,
                polygon.layer,
                polygon.net,
                polygon.bounds,
                start,
                counts[0],
                sum(counts[1:]),
                polygon.category,
            )
        )
    instances, sdf_batches, nets, component_batches, pin_batches = _prepare_sdf(scene)
    return PreparedScene(
        np.concatenate(vertices) if vertices else np.empty((0, 4), dtype=np.float32),
        np.concatenate(indices) if indices else np.empty(0, dtype=np.uint32),
        tuple(batches),
        instances,
        sdf_batches,
        nets,
        component_batches,
        pin_batches,
    )
