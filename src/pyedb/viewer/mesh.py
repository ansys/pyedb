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

from __future__ import annotations

from dataclasses import dataclass, replace
import math
from typing import Any, Callable, Iterator, Sequence

import numpy as np

from pyedb.viewer.scene import (
    Bounds,
    LayoutScene,
    SceneComponent,
    SceneJoin,
    ScenePad,
    ScenePolygon,
    SceneTrace,
    union_bounds,
)

ProgressCallback = Callable[[str, int, int], None]
SdfItem = SceneTrace | SceneJoin | ScenePad | SceneComponent

# Ten vec4 attributes, all per-instance. Coordinates retain their low parts.
SDF_STRIDE = 40
SDF_CHUNK_SIZE = 256


def split_coordinates(values: Any) -> np.ndarray:
    """Pack double coordinates as [x_high, y_high, x_low, y_low] float32 vertices."""
    values = np.asarray(values, dtype=np.float64)
    width = values.shape[-1]
    split = np.empty((*values.shape[:-1], width * 2), dtype=np.float32)
    split[..., :width] = values
    np.subtract(values, split[..., :width], out=split[..., width:])
    return split


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
    # Consecutive boundary rings (exterior first) starting at ``vertex_start``.
    vertex_start: int = 0
    ring_sizes: tuple[int, ...] = ()


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
    vertex_nets: np.ndarray | None = None
    mesh_parent_id: int = 0
    picking: object = None
    sdf_sources: np.ndarray | None = None
    outlines: Any = None
    dead_rows: int = 0
    update_count: int = 0
    dead_bytes: int = 0
    sdf_ranges: Any = None


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


def _sdf_packet(item: SdfItem, net_id: int) -> np.ndarray:
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


def scene_network_names(scene: LayoutScene) -> tuple[str | None, ...]:
    """Share stable network palette IDs between the renderer and workspace lists."""
    names = dict.fromkeys(net for net in scene.net_names if net)
    names.update(dict.fromkeys(sorted({item.net for item in scene.geometry if item.net})))
    names.update(dict.fromkeys(sorted({net for component in scene.components for net in component.nets if net})))
    return (None, *names)


def _write_pad_packets(items: Sequence[ScenePad], net_ids: dict[str | None, int], packets: np.ndarray) -> None:
    """Fill validated pads in bulk, keeping the scalar packet's float residuals."""
    packets[:, :4] = split_coordinates([item.center for item in items])
    bounds = np.asarray([item.bounds for item in items], dtype=np.float64)
    packets[:, 12:16] = split_coordinates(bounds[:, :2])
    packets[:, 16:20] = split_coordinates(bounds[:, 2:])
    dimensions = np.asarray([(*item.size, item.rotation) for item in items], dtype=np.float64)
    packets[:, 20:23] = dimensions
    packets[:, 24] = [2 if item.shape == "circle" else 3 for item in items]
    packets[:, 25] = [
        -int(item.shape == "circle" and math.dist(item.center, item.hole_center) + item.size[0] / 2 <= item.hole_radius)
        for item in items
    ]
    packets[:, 27] = [net_ids.get(item.net, 0) for item in items]
    radii = np.asarray([(item.corner_radius, item.hole_radius) for item in items], dtype=np.float64)
    packets[:, 28:30] = radii
    packets[:, 31] = [int(item.shape == "bullet") for item in items]
    packets[:, 32:36] = split_coordinates([item.hole_center for item in items])
    packets[:, 36:38] = dimensions[:, :2] - packets[:, 20:22]
    packets[:, 38] = radii[:, 1] - packets[:, 29]


def _sdf_chunks(scene: LayoutScene) -> Iterator[tuple[str, str, list[SdfItem]]]:
    """Group analytic copper by layer and ownership, then split spatial chunks."""
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
            yield layer, category, items[start : start + SDF_CHUNK_SIZE]


def _write_sdf_chunk(
    chunk: Sequence[SdfItem],
    category: str,
    net_ids: dict[str | None, int],
    packets: np.ndarray,
    packet_count: int,
    sources: np.ndarray | None,
    pin_batches: list[PinBatch],
) -> None:
    for index, item in enumerate(chunk):
        if sources is not None:
            sources[packet_count + index] = id(item)
        if getattr(item, "component", None):
            pin_batches.append(PinBatch(item, packet_count + index))
    if category == "pad":
        _write_pad_packets(chunk, net_ids, packets)
    else:
        for index, item in enumerate(chunk):
            packets[index] = _sdf_packet(item, net_ids.get(item.net, 0))


def _prepare_sdf(
    scene: LayoutScene, progress: ProgressCallback | None = None, sources: np.ndarray | None = None
) -> tuple[np.ndarray, tuple[SdfBatch, ...], tuple[str | None, ...], tuple[ComponentBatch, ...], tuple[PinBatch, ...]]:
    nets = scene_network_names(scene)
    net_ids = {net: index for index, net in enumerate(nets)}
    batches, pin_batches = [], []
    total = len(scene.traces) + len(scene.joins) + len(scene.pads) + len(scene.components)
    instances = np.zeros((total, SDF_STRIDE), dtype=np.float32)
    packet_count = 0
    if progress is not None:
        progress("Preparing traces and pads", 0, total)
    for layer, category, chunk in _sdf_chunks(scene):
        batches.append(
            SdfBatch(
                layer,
                union_bounds([item.bounds for item in chunk]),
                packet_count,
                len(chunk),
                any(getattr(item, "hole_radius", 0) > 0 for item in chunk),
                category,
            )
        )
        _write_sdf_chunk(
            chunk,
            category,
            net_ids,
            instances[packet_count : packet_count + len(chunk)],
            packet_count,
            sources,
            pin_batches,
        )
        packet_count += len(chunk)
        if progress is not None:
            progress("Preparing traces and pads", packet_count, total)
    # Custom pins need only their existing copper mesh and ownership metadata.
    # No auxiliary contour geometry is generated for pin borders.
    for polygon in scene.polygons:
        if not polygon.component:
            continue
        pin_batches.append(PinBatch(polygon, None, 0))
    component_batches = []
    for component in sorted(scene.components, key=lambda component: component.layer):
        component_batches.append(ComponentBatch(component, packet_count))
        instances[packet_count] = _sdf_packet(component, 0)
        packet_count += 1
    if progress is not None:
        progress("Preparing traces and pads", total, total)
    return instances, tuple(batches), nets, tuple(component_batches), tuple(pin_batches)


def _pickable(prepared: PreparedScene, scene: LayoutScene, sources: np.ndarray) -> PreparedScene:
    from pyedb.viewer.incremental import outline_data
    from pyedb.viewer.picking import PickIndex

    sources.setflags(write=False)
    ranges = {}
    if len(sources):
        edges = np.flatnonzero(np.r_[True, sources[1:] != sources[:-1], True])
        for start, end in zip(edges[:-1], edges[1:]):
            if sources[start]:
                ranges.setdefault(int(sources[start]), []).append((int(start), int(end - start)))
    return replace(
        prepared, picking=PickIndex(scene), sdf_sources=sources, sdf_ranges=ranges, outlines=outline_data(prepared)
    )


def _can_reuse_polygons(scene: LayoutScene, previous: LayoutScene, mesh: PreparedScene) -> bool:
    return (
        len(previous.polygons) <= len(scene.polygons)
        and all(a is b for a, b in zip(previous.polygons, scene.polygons))
        and mesh.nets == scene_network_names(scene)
        and mesh.vertex_nets is not None
    )


def _reuse_polygon_buffers(
    scene: LayoutScene, previous: LayoutScene, mesh: PreparedScene
) -> tuple[np.ndarray, np.ndarray, tuple[MeshBatch, ...], np.ndarray]:
    """Retain existing polygon buffers and append only newly captured copper."""
    vertices, indices, batches, vertex_nets = mesh.vertices, mesh.indices, mesh.batches, mesh.vertex_nets
    additions = scene.polygons[len(previous.polygons) :]
    if additions:
        extra = prepare_scene(LayoutScene(scene.layers, additions, net_names=mesh.nets[1:]))
        if len(vertices) + len(extra.vertices) > np.iinfo(np.uint32).max:
            raise ValueError("Layout exceeds the uint32 vertex index limit.")
        indices = np.concatenate((indices, extra.indices + np.uint32(len(vertices))))
        vertices = np.concatenate((vertices, extra.vertices))
        vertex_nets = np.concatenate((vertex_nets, extra.vertex_nets))
        batches = batches + tuple(
            replace(
                batch,
                index_start=batch.index_start + len(mesh.indices),
                vertex_start=batch.vertex_start + len(mesh.vertices),
            )
            for batch in extra.batches
        )
    return vertices, indices, batches, vertex_nets


def _prepare_polygon_buffers(
    scene: LayoutScene, progress: ProgressCallback | None, total_rings: int, total_items: int
) -> tuple[np.ndarray, np.ndarray, tuple[MeshBatch, ...], np.ndarray]:
    if scene.polygons:
        try:
            import mapbox_earcut
        except ImportError as exc:
            raise ImportError("Triangulation requires: pip install 'pyedb[viewer]'.") from exc
    vertices, indices, batches, vertex_nets = [], [], [], []
    net_ids = {net: index for index, net in enumerate(scene_network_names(scene))}
    polygon_groups = {}
    for polygon in scene.polygons:
        polygon_groups.setdefault((polygon.layer, polygon.category), []).append(polygon)
    vertex_count = index_count = 0
    completed_rings = 0
    if progress is not None:
        progress("Rendering layout", 0, total_items)
    for polygon in (polygon for group in polygon_groups.values() for polygon in group):
        start, vertex_start = index_count, vertex_count
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
            vertex_nets.append(np.full(len(ring), net_ids.get(polygon.net, 0), dtype=np.uint32))
            indices.append(triangles + np.uint32(vertex_count))
            vertex_count += len(ring)
            index_count += len(triangles)
            counts.append(len(triangles))
            completed_rings += 1
            if progress is not None and (completed_rings % 64 == 0 or completed_rings == total_rings):
                progress("Rendering layout", completed_rings, total_items)
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
                vertex_start,
                tuple(len(ring) for ring in (polygon.exterior, *polygon.holes)),
            )
        )

    return (
        np.concatenate(vertices) if vertices else np.empty((0, 4), dtype=np.float32),
        np.concatenate(indices) if indices else np.empty(0, dtype=np.uint32),
        tuple(batches),
        np.concatenate(vertex_nets) if vertex_nets else np.empty(0, dtype=np.uint32),
    )


def prepare_scene(
    scene: LayoutScene,
    *,
    progress: ProgressCallback | None = None,
    polygon_mesh: tuple[LayoutScene, PreparedScene] | None = None,
) -> PreparedScene:
    """Triangulate each ring independently; holes are subtracted with GPU stencil.

    Hole coverage is a union, even for overlapping holes. It must never be
    submitted as ordinary filled geometry.
    """
    total_sdf = len(scene.traces) + len(scene.joins) + len(scene.pads) + len(scene.components)
    sources = np.zeros(total_sdf, dtype=np.uintp)
    mesh_parent_id = 0
    if polygon_mesh is not None and _can_reuse_polygons(scene, *polygon_mesh):
        previous, mesh = polygon_mesh
        vertices, indices, batches, vertex_nets = _reuse_polygon_buffers(scene, previous, mesh)
        mesh_parent_id = id(mesh)
        total_rings = 0
        total_items = total_sdf + 1
    else:
        total_rings = sum(1 + len(polygon.holes) for polygon in scene.polygons)
        total_items = total_rings + total_sdf + 1
        vertices, indices, batches, vertex_nets = _prepare_polygon_buffers(scene, progress, total_rings, total_items)

    def sdf_progress(stage: str, current: int, total: int) -> None:
        progress("Rendering layout", total_rings + current, total_items)

    instances, sdf_batches, nets, component_batches, pin_batches = _prepare_sdf(
        scene, sdf_progress if progress is not None else None, sources
    )
    prepared = PreparedScene(
        vertices,
        indices,
        batches,
        instances,
        sdf_batches,
        nets,
        component_batches,
        pin_batches,
        vertex_nets,
        mesh_parent_id,
    )
    if progress is not None:
        progress("Rendering layout", total_items, total_items)
    return _pickable(prepared, scene, sources)
