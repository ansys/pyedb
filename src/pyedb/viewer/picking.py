# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT

"""Detached object picking: spatial broad phase and geometry-exact narrow phase."""

from dataclasses import dataclass, replace
import math

import numpy as np

from pyedb.viewer.scene import SceneJoin, SceneObjectInfo, ScenePad, SceneTrace, union_bounds


def _segment_distance(point, start, end):
    dx, dy = end[0] - start[0], end[1] - start[1]
    length = dx * dx + dy * dy
    t = max(0, min(1, ((point[0] - start[0]) * dx + (point[1] - start[1]) * dy) / length)) if length else 0
    return math.hypot(point[0] - start[0] - t * dx, point[1] - start[1] - t * dy)


def _ring_test(point, ring):
    # Rebase before products, preserving tiny geometry at large board offsets.
    values = np.asarray(ring, dtype=np.float64) - point
    a, b = values, np.roll(values, -1, axis=0)
    cross = (a[:, 1] > 0) != (b[:, 1] > 0)
    indices = np.flatnonzero(cross)
    inside = bool(
        np.count_nonzero(
            a[indices, 0] - a[indices, 1] * (b[indices, 0] - a[indices, 0]) / (b[indices, 1] - a[indices, 1]) > 0
        )
        % 2
    )
    delta = b - a
    length = np.einsum("ij,ij->i", delta, delta)
    t = np.clip(np.divide(-np.einsum("ij,ij->i", a, delta), length, out=np.zeros_like(length), where=length > 0), 0, 1)
    closest = a + t[:, None] * delta
    distance = float(np.sqrt(np.min(np.einsum("ij,ij->i", closest, closest))))
    return inside, distance


def _pad_distance(point, pad):
    dx, dy = point[0] - pad.center[0], point[1] - pad.center[1]
    if pad.shape == "circle":
        return math.hypot(dx, dy) - pad.size[0] / 2
    co, si = math.cos(pad.rotation), math.sin(pad.rotation)
    x, y = co * dx + si * dy, -si * dx + co * dy
    corner = 0 if pad.shape == "bullet" and x < 0 else pad.corner_radius
    x, y = abs(x) - pad.size[0] / 2 + corner, abs(y) - pad.size[1] / 2 + corner
    return math.hypot(max(x, 0), max(y, 0)) + min(max(x, y), 0) - corner


def _straight_trace_distance(point, item, radius):
    dx, dy = item.end[0] - item.start[0], item.end[1] - item.start[1]
    length = math.hypot(dx, dy)
    tx, ty = (dx / length, dy / length) if length else (1, 0)
    px, py = point[0] - item.start[0], point[1] - item.start[1]
    along, across = px * tx + py * ty, -px * ty + py * tx
    cap = item.end_caps[0] if along < 0 else item.end_caps[1]
    if along < 0 or along > length:
        end = -along if along < 0 else along - length
        if cap == "round":
            return math.hypot(end, across) - radius
        return max(abs(across) - radius, end - (radius if cap == "extended" else 0))
    return abs(across) - radius


def _arc_cap_distance(point, endpoint, tangent, cap, radius, index):
    px, py = point[0] - endpoint[0], point[1] - endpoint[1]
    if cap == "round":
        return math.hypot(px, py) - radius
    along = (px * tangent[0] + py * tangent[1]) * (-1 if index == 0 else 1)
    extension = radius if cap == "extended" else 0
    qx, qy = (
        abs(along - extension / 2) - extension / 2,
        abs(-px * tangent[1] + py * tangent[0]) - radius,
    )
    return math.hypot(max(qx, 0), max(qy, 0)) + min(max(qx, qy), 0)


def _arc_trace_distance(point, item, radius):
    angle = math.atan2(point[1] - item.center[1], point[0] - item.center[0])
    start = math.atan2(item.start[1] - item.center[1], item.start[0] - item.center[0])
    direction = 1 if item.sweep > 0 else -1
    sweep = (angle - start) * direction % math.tau
    radial = abs(math.dist(point, item.center) - math.dist(item.start, item.center)) - radius
    if abs(item.sweep) >= math.tau - 1e-12:
        return radial
    tangents = []
    for endpoint in (item.start, item.end):
        rx, ry = endpoint[0] - item.center[0], endpoint[1] - item.center[1]
        length = math.hypot(rx, ry)
        tangents.append((-ry / length * direction, rx / length * direction))
    caps = tuple(zip((item.start, item.end), tangents, item.end_caps))
    if sweep <= abs(item.sweep) + 1e-12:
        window = min(abs(item.sweep) / 2, math.pi / 2)
        for index, (endpoint, tangent, cap) in enumerate(caps):
            in_window = sweep <= window if index == 0 else sweep >= abs(item.sweep) - window
            if cap != "round" and in_window:
                along = ((point[0] - endpoint[0]) * tangent[0] + (point[1] - endpoint[1]) * tangent[1]) * (
                    -1 if index == 0 else 1
                )
                radial = max(radial, along - (radius if cap == "extended" else 0))
        return radial
    return min(
        _arc_cap_distance(point, endpoint, tangent, cap, radius, index)
        for index, (endpoint, tangent, cap) in enumerate(caps)
    )


@dataclass(frozen=True)
class PickObject:
    key: tuple[str, int]
    info: SceneObjectInfo
    items: tuple
    bounds: tuple


@dataclass(frozen=True)
class PickHit:
    object: PickObject
    item: object
    distance: float

    @property
    def key(self):
        return self.object.key

    @property
    def layer(self):
        return self.item.layer


@dataclass
class _Node:
    bounds: np.ndarray
    indices: np.ndarray | None = None
    left: object = None
    right: object = None


class PickIndex:
    """One tree entry per physical object, retaining exact per-layer pad shapes."""

    def __init__(self, scene):
        self.scene = scene
        metadata = {info.object_id: info for info in scene.object_info}
        grouped = {}
        for item in scene.geometry:
            info = metadata.get(item.object_id)
            kind = (
                info.kind
                if info is not None
                else (
                    "trace"
                    if isinstance(item, (SceneTrace, SceneJoin)) or getattr(item, "category", None) == "trace"
                    else "pad"
                    if getattr(item, "component", None)
                    else "via"
                    if isinstance(item, ScenePad) and item.hole_radius > 0
                    else "pad"
                    if isinstance(item, ScenePad) or getattr(item, "category", None) == "pad"
                    else "zone"
                )
            )
            grouped.setdefault((kind, item.object_id), []).append(item)
        objects = []
        for key, items in grouped.items():
            kind, object_id = key
            first = items[0]
            info = metadata.get(object_id)
            if info is None:
                traces = [item for item in items if isinstance(item, SceneTrace)]
                layers = [layer.name for layer in scene.layers if any(item.layer == layer.name for item in items)]
                info = SceneObjectInfo(
                    object_id,
                    kind,
                    first.net,
                    width=traces[0].width if traces else None,
                    length=sum(
                        math.dist(t.start, t.center) * abs(t.sweep) if t.center else math.dist(t.start, t.end)
                        for t in traces
                    )
                    if traces
                    else None,
                    drill_diameter=2 * first.hole_radius if isinstance(first, ScenePad) else None,
                    start_layer=layers[0],
                    stop_layer=layers[-1],
                    component=getattr(first, "component", None),
                    pin_name=getattr(first, "pin_name", None),
                )
            elif kind == "trace" and (info.width is None or info.length is None):
                traces = [item for item in items if isinstance(item, SceneTrace)]
                if traces:
                    info = replace(
                        info,
                        width=traces[0].width if info.width is None else info.width,
                        length=sum(
                            math.dist(t.start, t.center) * abs(t.sweep) if t.center else math.dist(t.start, t.end)
                            for t in traces
                        )
                        if info.length is None
                        else info.length,
                    )
            objects.append(PickObject(key, info, tuple(items), union_bounds([item.bounds for item in items])))
        self.objects = tuple(objects)
        self.by_key = {item.key: item for item in objects}
        self.bounds = np.asarray([item.bounds for item in objects], dtype=np.float64).reshape(-1, 4)
        self.root = self._build(np.arange(len(objects))) if objects else None
        self.last_candidates = 0
        self._hole_bounds = {}
        # Large zone void lists are indexed off the GUI thread along with the BVH.
        for polygon in scene.polygons:
            if polygon.holes:
                self._hole_bounds[id(polygon)] = np.asarray(
                    [
                        (
                            min(p[0] for p in ring),
                            min(p[1] for p in ring),
                            max(p[0] for p in ring),
                            max(p[1] for p in ring),
                        )
                        for ring in polygon.holes
                    ]
                )

    def _build(self, indices):
        boxes = self.bounds[indices]
        bounds = np.r_[boxes[:, :2].min(axis=0), boxes[:, 2:].max(axis=0)]
        if len(indices) <= 16:
            return _Node(bounds, indices)
        axis = int(np.argmax(bounds[2:] - bounds[:2]))
        centers = boxes[:, axis] + boxes[:, axis + 2]
        middle = len(indices) // 2
        ordered = indices[np.argpartition(centers, middle)]
        return _Node(bounds, left=self._build(ordered[:middle]), right=self._build(ordered[middle:]))

    def _distance(self, point, item, tolerance, min_radius=0):
        if isinstance(item, ScenePad):
            # A drill is selectable as part of its source via/pin.
            return min(
                _pad_distance(point, item),
                math.dist(point, item.hole_center) - item.hole_radius if item.hole_radius else math.inf,
            )
        if isinstance(item, SceneTrace):
            radius = max(item.width / 2, min_radius)
            if item.center is None:
                return _straight_trace_distance(point, item, radius)
            return _arc_trace_distance(point, item, radius)
        if isinstance(item, SceneJoin):
            inside, distance = _ring_test(point, item.points)
            return -distance if inside else distance
        inside, distance = _ring_test(point, item.exterior)
        holes = self._hole_bounds.get(id(item))
        if holes is not None:
            x, y = point
            candidates = np.flatnonzero(
                (holes[:, 0] <= x + tolerance)
                & (holes[:, 2] >= x - tolerance)
                & (holes[:, 1] <= y + tolerance)
                & (holes[:, 3] >= y - tolerance)
            )
            for index in candidates:
                in_hole, edge = _ring_test(point, item.holes[index])
                distance = min(distance, edge)
                if in_hole:
                    inside = False
        return -distance if inside else distance

    def pick(self, point, scale, visible_layers, *, net=None, opacity=1, mirror=False, pixels=5):
        if self.root is None or scale <= 0 or opacity <= 0:
            return None
        tolerance = pixels / scale
        x, y = point
        candidates, nodes = [], [self.root]
        while nodes:
            node = nodes.pop()
            box = node.bounds
            if box[0] > x + tolerance or box[2] < x - tolerance or box[1] > y + tolerance or box[3] < y - tolerance:
                continue
            if node.indices is not None:
                boxes = self.bounds[node.indices]
                mask = (
                    (boxes[:, 0] <= x + tolerance)
                    & (boxes[:, 2] >= x - tolerance)
                    & (boxes[:, 1] <= y + tolerance)
                    & (boxes[:, 3] >= y - tolerance)
                )
                candidates.extend(node.indices[mask])
            else:
                nodes.extend((node.left, node.right))
        self.last_candidates = len(candidates)
        layer_rank = {
            layer.name: (i if mirror else len(self.scene.layers) - i) for i, layer in enumerate(self.scene.layers)
        }
        ranks = {"zone": 0, "trace": 1, "pad": 2, "via": 3}
        hits = []
        for index in candidates:
            obj = self.objects[index]
            for sequence, item in enumerate(obj.items):
                if item.layer not in visible_layers or (net is not None and item.net != net):
                    continue
                distance = self._distance(point, item, tolerance, 0.5 / scale)
                if distance <= tolerance:
                    rank = (ranks[obj.info.kind], layer_rank[item.layer], int(index), sequence)
                    hits.append((distance, rank, PickHit(obj, item, distance)))
        exact = [hit for hit in hits if hit[0] <= 0]
        if exact:
            return max(exact, key=lambda hit: hit[1])[2]
        return min(hits, key=lambda hit: (hit[0], tuple(-v for v in hit[1])))[2] if hits else None


def inspector_rows(hit):
    """User-facing source properties; never derive trace length from copper perimeter."""
    info, item = hit.object.info, hit.item
    mm = lambda value: "—" if value is None else f"{value:.4f} mm"
    rows = [("Signal" if info.kind == "trace" else "Net", info.net or "Unassigned")]
    if info.name or (info.kind in {"via", "trace", "zone", "pad"} and not info.pin_name):
        rows.insert(0, ("Name", info.name or "—"))
    if info.kind == "trace":
        rows += [("Width", mm(info.width)), ("Length", mm(info.length))]
    elif info.kind == "via":
        diameter = item.size[0] if isinstance(item, ScenePad) and item.shape == "circle" else None
        pad_size = (
            ("Via pad size", f"{item.size[0]:.4f} × {item.size[1]:.4f} mm")
            if isinstance(item, ScenePad) and item.shape != "circle"
            else ("Via diameter", mm(diameter))
        )
        rows += [
            pad_size,
            ("Drill diameter", mm(info.drill_diameter)),
            ("From layer", info.start_layer or "—"),
            ("To layer", info.stop_layer or "—"),
        ]
    elif info.kind == "pad":
        rows += [("Component", info.component or "—"), ("Pin", info.pin_name or "—")]
    rows.append(("Layer", item.layer))
    return rows
