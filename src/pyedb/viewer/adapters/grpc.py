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

"""Read geometry once through the public gRPC layout API."""

from __future__ import annotations

from collections import Counter
import logging
import math
import traceback
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any, Callable, Iterable, Iterator

from ansys.edb.core.database import ProductIdType
from ansys.edb.core.definition.padstack_def_data import (
    PadGeometryType as CorePadGeometryType,
    PadType as CorePadType,
)
from ansys.edb.core.geometry.polygon_data import PolygonData as CorePolygonData
from ansys.edb.core.layer.layer import Layer as CoreLayer
from ansys.edb.core.primitive.padstack_instance import PadstackInstance as CorePadstackInstance
from ansys.edb.core.primitive.primitive import Primitive as CorePrimitive
from ansys.edb.core.session import StubAccessor, StubType

from pyedb.misc.utilities import arc_segment_count
from pyedb.viewer.progress import progress_items
from pyedb.viewer.scene import (
    LayoutScene,
    SceneComponent,
    SceneJoin,
    SceneLayer,
    SceneObjectInfo,
    ScenePad,
    ScenePolygon,
    SceneTrace,
    union_bounds,
)

if TYPE_CHECKING:
    from ansys.edb.core.definition.padstack_def_data import PadstackDefData
    from ansys.edb.core.geometry.point_data import PointData
    from ansys.edb.core.hierarchy.component_group import ComponentGroup
    from ansys.edb.core.primitive.padstack_instance import PadstackInstance
    from ansys.edb.core.primitive.primitive import Primitive

    from pyedb.grpc.edb import Edb
    from pyedb.viewer.scene import Point, Ring

    Progress = Callable[[str, int, int], None]
    Placement = tuple[Callable[[Point], Point], Callable[[Point], Point], float]
    PadTemplate = tuple[str, tuple[Any, ...], Point, float]
    HoleProfile = tuple[str, float, float, float, float]
    PinOwner = dict[str, Any]
    ComponentBasis = tuple[tuple[Point, Point], Point]
    PadstackDefinition = tuple[PadstackDefData, dict[str, SimpleNamespace], float, Point]
    ScenePrimitives = tuple[list[ScenePolygon], list[SceneTrace], list[SceneJoin], list[ScenePad]]

_logger = logging.getLogger(__name__)


class _Diagnostics(list):
    """A diagnostics list that also remembers whether debug mode is enabled."""

    def __init__(self, debug: bool = False) -> None:
        super().__init__()
        self.debug = debug


_UNSET: Any = object()


def _record_exception(diagnostics: list[str], message: str, exc: BaseException) -> None:
    """Record a caught exception.

    In normal mode, append only ``message`` and let the caller keep going
    (best-effort capture). In debug mode, additionally append the full
    traceback, log it, and re-raise so a debugger/pytest stops at the real
    failure. A marker on the exception prevents duplicate logging when it
    passes through nested ``except`` blocks on its way out.
    """
    if not getattr(diagnostics, "debug", False):
        diagnostics.append(message)
        return
    if not getattr(exc, "_viewer_diagnostics_logged", False):
        diagnostics.append(message)
        diagnostics.append(traceback.format_exc())
        _logger.exception(message)
        exc._viewer_diagnostics_logged = True
    raise exc


def _names(value: str | Iterable[str] | None) -> set[str] | None:
    return None if value is None else {value} if isinstance(value, str) else set(value)


def _conductor_names(edb: Edb, layout_layers: dict[str, Any] | None = None) -> tuple[str, ...]:
    """Use stackup order/types, never conventional TOP/BOTTOM layer names.

    ``edb.stackup.layers`` fetches and wraps every stackup layer from the EDB
    server, so callers that already hold that dictionary should pass it in
    via ``layout_layers`` instead of triggering another round of server calls.
    """
    signals = set(edb.stackup.signal_layers)
    layers = edb.stackup.layers if layout_layers is None else layout_layers
    return tuple(
        name
        for name, layer in layers.items()
        if name in signals or getattr(layer, "type", None) in {"signal", "conducting"}
    )


def _component_sides(edb: Edb, diagnostics: list[str], layout_layers: dict[str, Any] | None = None) -> dict[str, str]:
    layout_layers = edb.stackup.layers if layout_layers is None else layout_layers
    names = _conductor_names(edb, layout_layers)
    if not names:
        return {}
    sides = {names[0]: "top"}
    if len(names) > 1:
        sides[names[-1]] = "bottom"
    else:
        # A single conductor can explicitly belong to the back surface. If no
        # association is supplied, the sole layer is the front of the stackup.
        core = getattr(layout_layers[names[0]], "core", None)
        if core is not None:
            try:
                association = getattr(core, "top_bottom_association", None)
                if getattr(association, "name", None) == "BOTTOM_ASSOCIATED":
                    sides[names[0]] = "bottom"
            except Exception as exc:
                _record_exception(
                    diagnostics, f"Layer {names[0]}: side association unavailable ({exc}); using stackup order.", exc
                )
    return sides


def _contour(primitive: Primitive, arc_segments: int, chord_error: float | None = None) -> Ring:
    from pyedb.viewer.adapters.grpc_stream import contour_from_points

    return contour_from_points(primitive.polygon_data.points, arc_segments, chord_error)


def _xy(point: PointData) -> Point:
    return point.x.double * 1000, point.y.double * 1000


def _tangent(trace: SceneTrace, end: bool = False) -> Point:
    if trace.center is None:
        x, y = (b - a for a, b in zip(trace.start, trace.end))
    else:
        point = trace.end if end else trace.start
        sign = 1 if trace.sweep > 0 else -1
        x, y = -(point[1] - trace.center[1]) * sign, (point[0] - trace.center[0]) * sign
    length = math.hypot(x, y)
    return (x / length, y / length) if length else (1, 0)


def _trace_geometry(primitive: Primitive, layer: str, net: str | None) -> tuple[list[SceneTrace], list[SceneJoin]]:
    """Preserve source lines/arcs and add only constant-size join geometry."""
    arcs = primitive.center_line.arc_data
    if not arcs:
        raise ValueError("Empty path center line.")
    caps = tuple(cap.name.lower() for cap in primitive.get_end_cap_style())
    if any(cap not in {"flat", "round", "extended"} for cap in caps):
        raise ValueError(f"Unsupported path caps: {caps}.")
    round_join = primitive.corner_style.name.lower() == "round"
    width = primitive.width.double * 1000
    object_id = primitive.id
    traces, joins = [], []
    for index, arc in enumerate(arcs):
        start, end = _xy(arc.start), _xy(arc.end)
        if start == end and arc.is_segment():
            continue
        center, sweep = None, 0.0
        if not arc.is_segment():
            center = _xy(arc.center)
            a = math.atan2(start[1] - center[1], start[0] - center[0])
            b = math.atan2(end[1] - center[1], end[0] - center[0])
            sweep = (b - a) % math.tau if arc.is_ccw() else -((a - b) % math.tau)
            if sweep == 0:
                sweep = math.tau if arc.is_ccw() else -math.tau
        traces.append(
            SceneTrace(
                object_id,
                layer,
                net,
                start,
                end,
                width,
                center,
                sweep,
                (
                    caps[0] if index == 0 else "round",
                    caps[1] if index == len(arcs) - 1 else "round",
                ),
            )
        )
    if not traces:
        raise ValueError("Path has no nonzero segments.")
    if not round_join:
        for before, after in zip(traces, traces[1:]):
            tx, ty = _tangent(before, end=True)
            ux, uy = _tangent(after)
            turn = tx * uy - ty * ux
            if abs(turn) < 1e-12:
                continue
            x, y = before.end
            r = width * (-0.5 if turn > 0 else 0.5)
            p = (x - ty * r, y + tx * r)
            q = (x - uy * r, y + ux * r)
            divisor = 1 + tx * ux + ty * uy
            if divisor < 1e-8:
                raise ValueError("Nearly reversing sharp path corner requires source boundary coverage.")
            tip = (x - (ty + uy) * r / divisor, y + (tx + ux) * r / divisor)
            joins.append(SceneJoin(object_id, layer, net, (before.end, p, tip, q)))
    return traces, joins


def _rotate(point: Point, angle: float) -> Point:
    c, s = math.cos(angle), math.sin(angle)
    return c * point[0] - s * point[1], s * point[0] + c * point[1]


def _nsided_polygon_points(size: float, num_sides: float) -> Ring:
    """Return a regular polygon's vertices; ``size`` is the circumscribed diameter."""
    sides = max(3, int(round(num_sides)))
    radius = size / 2
    return tuple(
        (radius * math.cos(i * math.tau / sides), radius * math.sin(i * math.tau / sides)) for i in range(sides)
    )


def _thermal_relief_outline(round_outer: bool, inner: float, isolation_gap: float, arc_segments: int) -> Ring:
    """Approximate a thermal-relief pad's outer boundary.

    ``round45``/``round90``/``square45``/``square90`` pads connect an inner pad to
    surrounding copper through spokes whose exact placement depends on the anti-pad
    geometry, which is not available from the padstack definition alone. The spokes
    themselves are therefore not modeled; only the plain circular or square outline
    reachable by the pad (``inner`` plus ``isolation_gap`` on each side) is rendered.
    """
    radius = inner / 2 + isolation_gap
    if round_outer:
        return tuple(
            (radius * math.cos(i * math.tau / arc_segments), radius * math.sin(i * math.tau / arc_segments))
            for i in range(arc_segments)
        )
    return ((radius, radius), (-radius, radius), (-radius, -radius), (radius, -radius))


def _placement(
    instance: PadstackInstance,
    component_cache: dict[int, ComponentBasis],
    component: ComponentGroup | bool | None = None,
    component_id: int | None = None,
) -> Placement:
    get_position = getattr(instance, "get_position_and_rotation", None)
    if callable(get_position):
        state = tuple(value.double for value in get_position())
        position = tuple(v * 1000 for v in state[:2])
        rotation = state[2]
    else:
        position = tuple(float(v) * 1000 for v in instance.position)
        rotation = float(instance.rotation)
    basis = ((1, 0), (0, 1))
    component = False if component is None else component
    if component:
        key = component.edb_uid if component_id is None else component_id
        if key not in component_cache:
            from ansys.edb.core.geometry.point_data import PointData

            transform = component.transform
            if transform.is_null:
                component_cache[key] = basis, (0.0, 0.0)
            else:
                from pyedb.viewer.adapters.grpc_stream import transform_basis_points

                points = transform_basis_points(transform)
                if points is None:
                    points = [transform.transform_point(PointData(p)) for p in ((0, 0), (1, 0), (0, 1))]
                origin, x, y = points
                ox, oy = origin.x.double, origin.y.double
                component_cache[key] = (
                    ((x.x.double - ox, x.y.double - oy), (y.x.double - ox, y.y.double - oy)),
                    (ox * 1000, oy * 1000),
                )
        basis, origin = component_cache[key]
        if callable(get_position):
            px, py = position
            position = (
                origin[0] + basis[0][0] * px + basis[1][0] * py,
                origin[1] + basis[0][1] * px + basis[1][1] * py,
            )

    def vector(point: Point) -> Point:
        x, y = _rotate(point, rotation)
        return basis[0][0] * x + basis[1][0] * y, basis[0][1] * x + basis[1][1] * y

    def world(point: Point) -> Point:
        x, y = vector(point)
        return position[0] + x, position[1] + y

    scale = math.hypot(*basis[0])
    return world, vector, scale


def _pad_template(pad: SimpleNamespace, arc_segments: int, chord_error: float | None = None) -> PadTemplate | None:
    shape = pad.shape
    if shape in {"no_shape", "geometry", "no_geometry"}:
        return None
    offset = (float(pad.offset_x) * 1000, float(pad.offset_y) * 1000)
    rotation = float(pad.rotation)
    if shape == "polygon":
        if chord_error is not None:
            from pyedb.grpc.database.primitive.primitive import Primitive

            x, y = Primitive._get_points_for_plot(
                None, pad.polygon_data.points, arc_segments, chord_error=chord_error / 1000
            )

            return shape, tuple((px * 1000, py * 1000) for px, py in zip(x, y)), offset, rotation
        polygon = pad.polygon_data.without_arcs(max_arc_angle=math.tau / arc_segments, max_points=arc_segments)
        return shape, tuple(_xy(p) for p in polygon.points), offset, rotation
    if shape == "nsided_polygon":
        # ``num_sides`` is a plain count, not a length, and must not be unit-scaled.
        size, num_sides = pad.parameters_values or (0.0, 0)
        return "polygon", _nsided_polygon_points(float(size) * 1000, float(num_sides)), offset, rotation
    values = tuple(float(v) * 1000 for v in (pad.parameters_values or ()))
    if shape in {"round45", "round90", "square45", "square90"}:
        inner, _channel_width, isolation_gap = values
        ring = _thermal_relief_outline(shape.startswith("round"), inner, isolation_gap, arc_segments)
        return "polygon", ring, offset, rotation
    if shape not in {"circle", "square", "rectangle", "oval", "bullet"}:
        raise ValueError(f"Unsupported pad shape {shape!r}.")
    return shape, values, offset, rotation


def _mapped_layers(
    instance: PadstackInstance,
    edb: Edb,
    definition: PadstackDefData,
    layers: list[str],
    cache: dict[Any, dict[str, str]],
    layout_layers: dict[str, Any] | None = None,
    name: str | None = None,
) -> dict[str, str]:
    """Resolve explicit definition-to-layout mappings, including permuted names."""
    layer_map = getattr(instance, "layer_map", None)
    if layer_map is None or layer_map.is_null:
        return {layer: layer for layer in layers}
    key = (name or instance.padstack_def.name, layer_map.msg.SerializeToString(), tuple(layers))
    if key not in cache:
        data = definition
        names = dict(zip(data.layer_ids, data.layer_names))
        mapped = {}
        for layer in layers:
            source_layers = edb.stackup.layers if layout_layers is None else layout_layers
            ids = layer_map.get_mapping_backward(source_layers[layer].id)
            candidates = [names[layer_id] for layer_id in ids if layer_id in names]
            if len(candidates) > 1:
                raise ValueError(f"Ambiguous padstack layer mapping on {layer}.")
            mapped[layer] = candidates[0] if candidates else layer
        cache[key] = mapped
    return cache[key]


def _padstack_instance_name(instance: PadstackInstance) -> str | None:
    """Return the AEDT display name of a raw padstack instance, mirroring ``PadstackInstance.name``."""
    name = getattr(instance, "name", None)
    if name:
        return name
    try:
        value = instance.get_product_property(ProductIdType.DESIGNER, 11)
    except Exception:
        return None
    return str(value).strip("'") if value else None


def _resolve_component(raw_component: ComponentGroup | None) -> ComponentGroup | bool:
    """Return the raw component, or ``False`` when the instance has no component."""
    if raw_component is None or getattr(raw_component, "is_null", True):
        return False
    return raw_component


def _component_is_enabled(component: ComponentGroup) -> bool:
    """Mirror ``Component.is_enabled`` by reading the raw component property directly."""
    comp_prop = getattr(component, "component_property", None)
    return getattr(comp_prop, "enabled", True)


def _component_placement_layer_name(component: ComponentGroup) -> str:
    """Mirror ``Component.placement_layer`` (a layer name) without a pyedb wrapper."""
    layer = getattr(component, "placement_layer", None)
    return getattr(layer, "name", layer)


def _pin_owner(
    instance: PadstackInstance,
    sides: dict[str, str],
    cache: dict[int, PinOwner | None],
    component: ComponentGroup | bool | None = None,
    component_id: int | None = None,
    instance_name: str | None = _UNSET,
) -> PinOwner:
    """Keep component-pin ownership separate from the physical copper pad layer."""
    if not getattr(instance, "is_layout_pin", False):
        return {}
    component = False if component is None else component
    if not component:
        return {}
    component_id = component.edb_uid if component_id is None else component_id
    if component_id not in cache:
        layer = _component_placement_layer_name(component)
        cache[component_id] = (
            dict(component=component.name, component_layer=layer, component_side=sides[layer])
            if _component_is_enabled(component) and layer in sides
            else None
        )
    owner = cache[component_id]
    if owner is None:
        return {}
    if instance_name is _UNSET:
        instance_name = _padstack_instance_name(instance)
    return dict(owner, pin_name=instance_name)


_PADSTACK_INSTANCE_STUB = StubAccessor(StubType.padstack_instance)
_PRIMITIVE_STUB = StubAccessor(StubType.primitive)


def _cached_name(obj: Any, cache: dict[int, str]) -> str:  # noqa: ANN401
    """Read ``obj.name`` once per server object; ``.id`` is the local handle, not a server call."""
    key = getattr(obj, "id", None)
    if not isinstance(key, int) or not key:
        return obj.name
    name = cache.get(key)
    if name is None:
        name = cache[key] = obj.name
    return name


def _primitive_layer_name(primitive: Primitive, layer_names: dict[int, str] | None) -> str:
    """Return the primitive's layer name without ``Layer.cast()`` and repeated name calls."""
    if layer_names is not None and isinstance(primitive, CorePrimitive):
        msg = _PRIMITIVE_STUB.__get__().GetLayer(primitive.msg)
        if msg.id:
            name = layer_names.get(msg.id)
            if name is None:
                name = layer_names[msg.id] = CoreLayer(msg).name
            return name
    return primitive.layer.name


def _layer_names_by_id(layout_layers: dict[str, Any]) -> dict[int, str]:
    """Seed the layer ID-to-name cache from stackup layers already in memory (``.id`` is local)."""
    names = {}
    for name, layer in layout_layers.items():
        layer_id = getattr(layer, "id", None)
        if isinstance(layer_id, int) and layer_id:
            names[layer_id] = name
    return names


def _layer_range_names(instance: PadstackInstance, layer_names: dict[int, str] | None) -> tuple[str, str] | None:
    """Return the instance's ``(first, last)`` layer names, or ``None`` when it has no range.

    ``PadstackInstance.get_layer_range()`` casts both layers to their concrete
    type and every ``.name`` read is another server call (7 calls per
    instance). On a real core instance, read the range message once and
    resolve names from ``layer_names``, an ID-to-name cache shared across
    instances; other objects fall back to the public API.
    """
    if layer_names is not None and type(instance) is CorePadstackInstance:
        params = _PADSTACK_INSTANCE_STUB.__get__().GetLayerRange(instance.msg)
        result = []
        for msg in (params.top_layer, params.bottom_layer):
            if not msg.id:
                return None
            name = layer_names.get(msg.id)
            if name is None:
                name = layer_names[msg.id] = CoreLayer(msg).name
            result.append(name)
        return result[0], result[1]
    layer_range = instance.get_layer_range()
    if not layer_range:
        return None
    first, last = (layer.name for layer in layer_range)
    return first, last


def _padstack_layers(
    instance: PadstackInstance,
    selected_layers: set[str],
    conductors: tuple[str, ...],
    extended_ranges: bool,
    layer_names: dict[int, str] | None = None,
) -> list[str]:
    """Include conducting layers within the instance's physical span."""
    instance_layers = None
    get_range = getattr(instance, "get_layer_range", None)
    if callable(get_range):
        layer_range = _layer_range_names(instance, layer_names)
        if not layer_range:
            return []
        first, last = layer_range
        if first in conductors and last in conductors:
            start, stop = sorted((conductors.index(first), conductors.index(last)))
            instance_layers = conductors[start : stop + 1]
    elif extended_ranges:
        first, last = getattr(instance, "start_layer", None), getattr(instance, "stop_layer", None)
        if first in conductors and last in conductors:
            start, stop = sorted((conductors.index(first), conductors.index(last)))
            instance_layers = conductors[start : stop + 1]
    return [name for name in (instance_layers or ()) if name in selected_layers]


def _pad_parameter_value(data: PadstackDefData, layer_name: str | None, pad_type: CorePadType) -> list[Any] | None:
    """Read raw pad parameters, normalizing the polygon variant to a consistent 5-item layout."""
    try:
        p_val = data.get_pad_parameters(layer_name, pad_type)
    except Exception:
        return None
    if not p_val:
        return None
    if isinstance(p_val[0], CorePolygonData):
        p_val = [CorePadGeometryType.PADGEOMTYPE_POLYGON, *p_val]
    return p_val


def _pad_param(
    data: PadstackDefData, layer_name: str | None, pad_type: CorePadType = CorePadType.REGULAR_PAD
) -> SimpleNamespace:
    """Local, read-only stand-in for ``PadProperties`` built directly from raw pad parameters."""
    p_val = _pad_parameter_value(data, layer_name, pad_type)
    if p_val is None:
        return SimpleNamespace(
            shape="no_shape", offset_x=0.0, offset_y=0.0, rotation=0.0, polygon_data=None, parameters_values=None
        )
    geom_type, params = p_val[0], p_val[1]
    polygon = params if isinstance(params, CorePolygonData) else None
    # ``NSIDED_POLYGON`` would otherwise collide with ``POLYGON`` once reduced to its last
    # underscore-separated word, even though it carries size/side-count parameters, not polygon data.
    if geom_type == CorePadGeometryType.PADGEOMTYPE_NSIDED_POLYGON:
        shape = "nsided_polygon"
    else:
        shape = geom_type.name.split("_")[-1].lower()
    return SimpleNamespace(
        shape=shape,
        offset_x=p_val[2].double,
        offset_y=p_val[3].double,
        rotation=p_val[4].double,
        polygon_data=polygon,
        parameters_values=None if polygon is not None else [v.double for v in params],
    )


def _hole_param(data: PadstackDefData) -> SimpleNamespace:
    """Hole geometry; ``get_hole_parameters()`` is ``get_pad_parameters(None, PadType.HOLE)``."""
    return _pad_param(data, None, CorePadType.HOLE)


def _hole_diameter(hole: SimpleNamespace) -> float | None:
    """Effective circular drill diameter of a hole, or ``None`` when absent or polygonal."""
    values = hole.parameters_values
    if hole.shape in {"no_shape", "geometry"} or not values:
        return None
    if hole.shape in {"rectangle", "oval", "bullet"}:
        return max(values[0], values[1])
    # Circle/square/nsided-polygon/thermal shapes lead with diameter, size or inner size.
    return values[0]


_THERMAL_RELIEF_SHAPES = {"round45", "round90", "square45", "square90"}


def _rounded_outline(shape: str, size_x: float, size_y: float, corner: float, arc_segments: int) -> Ring:
    """Local outline of a rectangle, oval (all corners rounded) or bullet (+X side rounded), centered at origin."""
    hx, hy = size_x / 2, size_y / 2
    radius = min(corner, hx, hy)
    if shape == "rectangle" or radius <= 0:
        return ((hx, hy), (-hx, hy), (-hx, -hy), (hx, -hy))
    steps = max(2, arc_segments // 4)

    def arc(cx: float, cy: float, start: float) -> list[Point]:
        return [
            (
                cx + radius * math.cos(start + i * math.pi / 2 / steps),
                cy + radius * math.sin(start + i * math.pi / 2 / steps),
            )
            for i in range(steps + 1)
        ]

    ring = arc(hx - radius, hy - radius, 0.0)
    ring += arc(-hx + radius, hy - radius, math.pi / 2) if shape == "oval" else [(-hx, hy), (-hx, -hy)]
    if shape == "oval":
        ring += arc(-hx + radius, -hy + radius, math.pi)
    ring += arc(hx - radius, -hy + radius, 3 * math.pi / 2)
    return tuple(ring)


def _hole_profile(hole: SimpleNamespace) -> HoleProfile | None:
    """Return a noncircular hole profile ``(shape, size_x, size_y, corner, rotation)`` in mm, else ``None``."""
    if hole.shape not in {"rectangle", "oval", "bullet"}:
        return None
    values = hole.parameters_values
    corner = 0.0 if hole.shape == "rectangle" else values[2] * 1000
    return hole.shape, values[0] * 1000, values[1] * 1000, corner, hole.rotation


def _padstack_definition(
    instance: PadstackInstance,
    definitions: dict[Any, Any],
    diagnostics: list[str],
    name: str | None = None,
    padstack_def: Any = None,
) -> PadstackDefinition:
    """Cache pad and drill data shared by instances of a definition, read directly from raw core."""
    padstack_def = instance.padstack_def if padstack_def is None else padstack_def
    name = name or padstack_def.name
    if name not in definitions:
        data = padstack_def.data
        hole = _hole_param(data)
        diameter = _hole_diameter(hole)
        if hole.shape == "polygon":
            diagnostics.append(f"Padstack definition {name}: polygonal drill profile is not displayed.")
        by_layer = {layer: _pad_param(data, layer) for layer in data.layer_names}
        if any(pad.shape in _THERMAL_RELIEF_SHAPES for pad in by_layer.values()):
            diagnostics.append(
                f"Padstack definition {name}: round45/round90/square45/square90 pads are approximated as a "
                "plain circle/square outline; thermal-relief spokes are not rendered."
            )
        definitions[name] = (
            data,
            by_layer,
            float(diameter or 0) * 500,
            (hole.offset_x * 1000, hole.offset_y * 1000),
        )
        definitions[("hole_profile", name)] = _hole_profile(hole)
    return definitions[name]


def _cached_pad_template(
    name: str,
    definition_layer: str,
    by_layer: dict[str, SimpleNamespace],
    templates: dict[Any, PadTemplate | None],
    arc_segments: int,
    chord_error: float | None = None,
) -> PadTemplate | None:
    """Cache each definition layer's geometry, including absent copper."""
    key = (name, definition_layer, chord_error)
    if key not in templates:
        pad = by_layer.get(definition_layer, by_layer.get("Default"))
        templates[key] = None if pad is None else _pad_template(pad, arc_segments, chord_error)
    return templates[key]


def _append_padstack_geometry(
    instance: PadstackInstance,
    layer: str,
    net: str | None,
    template: PadTemplate | None,
    placement: Placement,
    hole_radius: float,
    hole_center: Point,
    arc_segments: int,
    pin_owner: PinOwner,
    geometry: tuple[list[ScenePad], list[ScenePolygon]],
    chord_error: float | None = None,
    *,
    object_id: int | None = None,
    hole_profile: HoleProfile | None = None,
    hole_offset: Point = (0.0, 0.0),
) -> None:
    """Place a layer's copper and retain independent drill coverage.

    A noncircular ``hole_profile`` is cut out of the copper as a polygon hole, since analytic pads only
    support circular drills.
    """
    world, vector, scale = placement
    pads, polygons = geometry
    object_id = instance.edb_uid if object_id is None else object_id
    if hole_profile is not None and template is not None and hole_radius > 0:
        shape, dimensions, offset, rotation = template
        if shape == "polygon":
            outline = dimensions
        elif shape in {"circle", "square", "rectangle", "oval", "bullet"}:
            if shape == "circle":
                outline = tuple(
                    (
                        dimensions[0] / 2 * math.cos(i * math.tau / arc_segments),
                        dimensions[0] / 2 * math.sin(i * math.tau / arc_segments),
                    )
                    for i in range(arc_segments)
                )
            elif shape == "square":
                outline = _rounded_outline("rectangle", dimensions[0], dimensions[0], 0, arc_segments)
            else:
                corner = dimensions[2] if shape in {"oval", "bullet"} else 0
                outline = _rounded_outline(shape, dimensions[0], dimensions[1], corner, arc_segments)
        else:
            outline = None
        if outline is not None:
            ring = tuple(world(tuple(a + b for a, b in zip(_rotate(p, rotation), offset))) for p in outline)
            h_shape, size_x, size_y, corner, h_rotation = hole_profile
            hole_ring = tuple(
                world(tuple(a + b for a, b in zip(_rotate(p, h_rotation), hole_offset)))
                for p in _rounded_outline(h_shape, size_x, size_y, corner, arc_segments)
            )
            polygons.append(ScenePolygon(object_id, layer, net, ring, (hole_ring,), category="pad", **pin_owner))
            return
    if template is None:
        # Keep nonfunctional pads absent while retaining drill marks.
        if hole_radius > 0:
            pads.append(
                ScenePad(
                    object_id,
                    layer,
                    net,
                    hole_center,
                    (hole_radius * 2 * scale,) * 2,
                    hole_radius=hole_radius * scale,
                )
            )
        return
    shape, dimensions, offset, rotation = template
    if shape == "polygon":
        ring = tuple(world(tuple(a + b for a, b in zip(_rotate(p, rotation), offset))) for p in dimensions)
        holes = ()
        if hole_radius > 0:
            segments = (
                arc_segments if chord_error is None else arc_segment_count(hole_radius * scale, math.tau, chord_error)
            )
            holes = (
                tuple(
                    (
                        hole_center[0] + hole_radius * scale * math.cos(i * math.tau / segments),
                        hole_center[1] + hole_radius * scale * math.sin(i * math.tau / segments),
                    )
                    for i in range(segments)
                ),
            )
            pads.append(
                ScenePad(
                    object_id,
                    layer,
                    net,
                    hole_center,
                    (hole_radius * 2 * scale,) * 2,
                    hole_radius=hole_radius * scale,
                )
            )
        polygons.append(ScenePolygon(object_id, layer, net, ring, holes, category="pad", **pin_owner))
        return
    center = world(offset)
    axis = vector(_rotate((1, 0), rotation))
    angle = math.atan2(axis[1], axis[0])
    size = (dimensions[0],) * 2 if shape in {"circle", "square"} else dimensions[:2]
    corner = dimensions[2] if shape in {"oval", "bullet"} else 0
    corner = min(corner, min(size) / 2)
    pads.append(
        ScenePad(
            object_id,
            layer,
            net,
            center,
            tuple(v * scale for v in size),
            "rectangle" if shape == "square" else shape,
            angle,
            corner * scale,
            hole_radius * scale,
            hole_center,
            **pin_owner,
        )
    )


def _padstack_pin_owner(
    instance: PadstackInstance,
    sides: dict[str, str],
    cache: dict[int, PinOwner | None],
    component: ComponentGroup | bool | None,
    diagnostics: list[str],
    component_id: int | None = None,
    instance_name: str | None = _UNSET,
) -> PinOwner:
    """Retain padstack geometry when optional component-pin metadata is unavailable."""
    try:
        return _pin_owner(instance, sides, cache, component, component_id, instance_name)
    except Exception as exc:
        _record_exception(diagnostics, f"Padstack {instance.edb_uid}: component pin metadata unavailable ({exc}).", exc)
        return {}


def _readonly_components(edb: Edb) -> dict[int, Any] | None:
    """Index existing component wrappers for read-only padstack capture."""
    component_manager = getattr(edb, "components", None)
    return (
        {
            component.core.edb_uid: component
            for component in component_manager.instances.values()
            if getattr(getattr(component, "core", None), "edb_uid", None)
        }
        if component_manager is not None and getattr(edb, "isreadonly", False)
        else None
    )


def _padstack_component(
    raw_component: ComponentGroup | None, components: dict[int, Any] | None, component_id: int | None = None
) -> Any:  # noqa: ANN401
    """Reuse a capture's component wrapper; ``False`` means the instance has no component."""
    if components is None or raw_component is None:
        return None
    if raw_component.is_null:
        return False
    return components.get(raw_component.edb_uid if component_id is None else component_id)


def _padstack_object_info(
    instance: PadstackInstance,
    object_id: int,
    component: ComponentGroup | bool | None,
    net: str,
    hole_radius: float,
    placement: Placement,
    span: list[str],
    object_info: dict[int, SceneObjectInfo] | None,
    diagnostics: list[str],
    reference: str | None = _UNSET,
    instance_name: str | None = _UNSET,
) -> None:
    """Capture optional inspector properties without discarding valid geometry."""
    if object_info is not None:
        try:
            if reference is _UNSET:
                reference = getattr(component, "name", None) if component else None
            if instance_name is _UNSET:
                instance_name = _padstack_instance_name(instance)
            object_info[object_id] = SceneObjectInfo(
                object_id,
                "pad" if component or hole_radius == 0 else "via",
                net,
                drill_diameter=hole_radius * placement[2] * 2,
                start_layer=span[0],
                stop_layer=span[-1],
                component=reference,
                pin_name=instance_name if component else None,
                name=None if component else instance_name,
            )
        except Exception as exc:
            _record_exception(diagnostics, f"Padstack {object_id}: inspection properties unavailable ({exc}).", exc)


def _record_padstack_geometry(
    component_geometry: dict[Any, Any] | None,
    object_id: int,
    component: ComponentGroup | bool | None,
    net: str,
    placement: Placement,
    pads: list[ScenePad],
    polygons: list[ScenePolygon],
    component_id: int | None = None,
) -> None:
    """Accumulate pin envelopes for the component pass, including copper-free pins."""
    if component_geometry is not None:
        bounds = union_bounds([item.bounds for item in (*pads, *polygons)])
        approximate = bounds is None
        if approximate:
            x, y = placement[0]((0, 0))
            bounds = (x, y, x, y)
        instance_geometry = {"bounds": bounds, "nets": {net} if net else set(), "approximate": approximate}
        component_geometry.setdefault("instances", {})[object_id] = instance_geometry
        if component:
            record = component_geometry.setdefault(
                component.edb_uid if component_id is None else component_id,
                {"bounds": bounds, "nets": set(), "approximate": False},
            )
            record["bounds"] = union_bounds([record["bounds"], bounds])
            record["nets"].update(instance_geometry["nets"])
            record["approximate"] |= approximate


def _padstacks(
    edb: Edb,
    selected_layers: set[str],
    selected_nets: set[str] | None,
    arc_segments: int,
    diagnostics: list[str],
    progress: Progress | None = None,
    component_geometry: dict[Any, Any] | None = None,
    chord_error: float | None = None,
    object_info: dict[int, SceneObjectInfo] | None = None,
    layout_layers: dict[str, Any] | None = None,
) -> tuple[list[ScenePad], list[ScenePolygon]]:
    pads, polygons = [], []
    definitions, templates, component_cache, mapping_cache = {}, {}, {}, {}
    pin_components = {}
    layout_layers = edb.stackup.layers if layout_layers is None else layout_layers
    sides = _component_sides(edb, diagnostics, layout_layers)
    conductors = _conductor_names(edb, layout_layers)
    extended_ranges = bool(set(conductors).difference(edb.stackup.signal_layers))
    core_layout = getattr(getattr(edb, "layout", None), "core", None)
    if core_layout is None:
        return pads, polygons
    component_objects = _readonly_components(edb)
    layer_names = _layer_names_by_id(layout_layers)
    net_names, component_names, definition_names = {}, {}, {}
    for instance in progress_items(lambda: core_layout.padstack_instances, progress, "Reading pads and vias"):
        try:
            object_id = instance.edb_uid
            # Fetch .net once: it is a separate GetNet round-trip to the EDB server.
            instance_net = instance.net
            net = "" if getattr(instance_net, "is_null", False) else _cached_name(instance_net, net_names)
            if selected_nets is not None and net not in selected_nets:
                continue
            span = _padstack_layers(instance, set(conductors), conductors, extended_ranges, layer_names)
            layers = [layer for layer in span if layer in selected_layers]
            if not layers:
                continue
            padstack_def = instance.padstack_def
            name = _cached_name(padstack_def, definition_names)
            definition, by_layer, hole_radius, hole_offset = _padstack_definition(
                instance, definitions, diagnostics, name, padstack_def
            )
            mapped = _mapped_layers(instance, edb, definition, layers, mapping_cache, layout_layers, name)
            enabled, diameter = instance.get_hole_overrides()
            hole_profile = definitions.get(("hole_profile", name))
            if enabled:
                hole_radius = diameter.double * 500
                hole_profile = None
            raw_component = getattr(instance, "component", None)
            # Read the component's persistent ID once; every helper below keys on it.
            component_id = (
                raw_component.edb_uid
                if raw_component is not None and not getattr(raw_component, "is_null", True)
                else None
            )
            component = _padstack_component(raw_component, component_objects, component_id)
            if component is None:
                component = _resolve_component(raw_component)
            elif component is not False:
                # Readonly-mode cache stores wrapped Component objects; normalize to raw core.
                component = getattr(component, "core", component)
            if not component:
                component_id = None
            placement = _placement(instance, component_cache, component, component_id)
            reference = instance_name = _UNSET
            if object_info is not None:
                # Shared by the pin owner and the inspector entry; on failure each helper retries and reports.
                try:
                    instance_name = _padstack_instance_name(instance)
                    if component:
                        if component_id is None:
                            reference = getattr(component, "name", None)
                        else:
                            if component_id not in component_names:
                                component_names[component_id] = getattr(component, "name", None)
                            reference = component_names[component_id]
                except Exception:
                    pass
            pin_owner = _padstack_pin_owner(
                instance, sides, pin_components, component, diagnostics, component_id, instance_name
            )
            hole_center = placement[0](hole_offset)
            _padstack_object_info(
                instance,
                object_id,
                component,
                net,
                hole_radius,
                placement,
                span,
                object_info,
                diagnostics,
                reference,
                instance_name,
            )
            pad_start, polygon_start = len(pads), len(polygons)
            for layer in layers:
                try:
                    scale_bound = math.ceil(placement[2] * 1e9) / 1e9
                    local_error = None if chord_error is None else chord_error / scale_bound
                    template = _cached_pad_template(name, mapped[layer], by_layer, templates, arc_segments, local_error)
                    _append_padstack_geometry(
                        instance,
                        layer,
                        net,
                        template,
                        placement,
                        hole_radius,
                        hole_center,
                        arc_segments,
                        pin_owner,
                        (pads, polygons),
                        chord_error,
                        object_id=object_id,
                        hole_profile=hole_profile,
                        hole_offset=hole_offset,
                    )
                except Exception as exc:
                    _record_exception(diagnostics, f"Padstack {object_id}, layer {layer}: {exc}", exc)
            _record_padstack_geometry(
                component_geometry,
                object_id,
                component,
                net,
                placement,
                pads[pad_start:],
                polygons[polygon_start:],
                component_id,
            )
        except Exception as exc:
            _record_exception(diagnostics, f"Padstack {instance.edb_uid}: {exc}", exc)
    return pads, polygons


def _components(
    edb: Edb,
    selected_layers: set[str],
    selected_nets: set[str] | None,
    diagnostics: list[str],
    progress: Progress | None = None,
    component_geometry: dict[Any, Any] | None = None,
    layout_layers: dict[str, Any] | None = None,
) -> tuple[SceneComponent, ...]:
    """Reuse captured pad envelopes, falling back to source bounds when needed."""
    manager = getattr(edb, "components", None)
    if manager is None:
        return ()
    sides = _component_sides(edb, diagnostics, layout_layers)
    if not sides:
        return ()
    net_filter = set(edb.nets.nets) if selected_nets is None else selected_nets
    result = []
    approximate_count = 0
    for reference, component in progress_items(manager.instances.items, progress, "Reading components"):
        try:
            if not component.is_enabled:
                continue
            layer = component.placement_layer
            if layer not in selected_layers or layer not in sides:
                continue
            captured = (component_geometry or {}).get(component.id) if selected_nets is None else None
            if captured is None and selected_nets is None and component_geometry:
                # Some component pads are not marked as layout pins and their
                # instance.component getter is null. Membership still identifies
                # them, without constructing a full-board layout instance.
                by_id = component_geometry.get("instances", {})
                members = getattr(getattr(component, "core", None), "members", ())
                records = [by_id[member.edb_uid] for member in members if member.edb_uid in by_id]
                if records:
                    captured = {
                        "bounds": union_bounds([record["bounds"] for record in records]),
                        "nets": set().union(*(record["nets"] for record in records)),
                        "approximate": any(record["approximate"] for record in records),
                    }
            nets = tuple(sorted(captured["nets"])) if captured is not None else tuple(component.nets)
            if (selected_nets is not None or net_filter) and not net_filter.intersection(nets):
                continue
            bounds = (
                captured["bounds"] if captured is not None else tuple(float(v) * 1000 for v in component.bounding_box)
            )
            if captured is not None and captured.get("approximate", False):
                # Copper-free SMT pins still locate the footprint. A modest
                # display margin avoids a full-board layout-instance build.
                x0, y0, x1, y1 = bounds
                margin = max(max(x1 - x0, y1 - y0) * 0.1, 0.05)
                bounds = x0 - margin, y0 - margin, x1 + margin, y1 + margin
                approximate_count += 1
            result.append(SceneComponent(component.id, component.name, layer, nets, bounds, sides[layer]))
        except Exception as exc:
            _record_exception(diagnostics, f"Component {reference}: {exc}", exc)
    if approximate_count:
        diagnostics.append(f"{approximate_count} component envelopes estimated from pin positions for fast display.")
    return tuple(result)


def _scene_filters(
    edb: Edb,
    layers: str | Iterable[str] | None,
    nets: str | Iterable[str] | None,
    layout_layers: dict[str, Any] | None = None,
) -> tuple[set[str], set[str] | None]:
    """Normalize filters and reject names outside the source layout."""
    selected_layers, selected_nets = _names(layers), _names(nets)
    source_layers = edb.stackup.layers if layout_layers is None else layout_layers
    if selected_layers is None:
        selected_layers = set(_conductor_names(edb, source_layers))
    unknown = selected_layers.difference(source_layers)
    if unknown:
        raise ValueError(f"Unknown layers: {', '.join(sorted(unknown))}")
    if selected_nets is not None:
        unknown = selected_nets.difference(edb.nets.nets)
        if unknown:
            raise ValueError(f"Unknown nets: {', '.join(sorted(unknown))}")
    return selected_layers, selected_nets


def _selected_primitives(
    edb: Edb,
    selected_layers: set[str],
    selected_nets: set[str] | None,
    skipped: Counter[str],
    progress: Progress | None = None,
    priority_layer: str | None = None,
    layer_names: dict[int, str] | None = None,
    source_primitives=None,
) -> Iterator[tuple[Primitive, str, str, str]]:
    """Filter source primitives and count unsupported copper geometry."""
    net_names = {}

    def load() -> list[tuple[Primitive, Any, str | None, bool | None]]:
        # Keep the resolved net object instead of re-fetching it later: each
        # ``.net`` access is a separate GetNet round-trip to the EDB server.
        source = []
        for primitive in edb.layout.core.primitives if source_primitives is None else source_primitives:
            net = primitive.net
            if not net.is_null:
                source.append((primitive, net))
        if priority_layer is None:
            return [(primitive, net, None, None) for primitive, net in source]
        records = []
        for primitive, net in source:
            void = primitive.is_void
            records.append((primitive, net, None if void else _primitive_layer_name(primitive, layer_names), void))
        records.sort(key=lambda item: item[2] != priority_layer)
        return records

    for primitive, net, layer_name, void in progress_items(load, progress, "Reading polygons"):
        if void is None:
            void = primitive.is_void
        if void:
            continue
        if layer_name is None:
            layer_name = _primitive_layer_name(primitive, layer_names)
        if layer_name not in selected_layers:
            continue
        net_name = _cached_name(net, net_names)
        if selected_nets is not None and net_name not in selected_nets:
            continue
        primitive_type = primitive.primitive_type.name.lower()
        if primitive_type not in {"polygon", "rectangle", "circle", "path"}:
            skipped[primitive_type] += 1
            continue
        if primitive.is_negative:
            skipped["negative primitive"] += 1
            continue
        yield primitive, primitive_type, layer_name, net_name


_PRIMITIVE_NAME_PREFIX = {"path": "line", "rectangle": "rect", "polygon": "poly", "bondwire": "bwr"}


def _primitive_name(primitive: Primitive, primitive_type: str | None = None) -> str:
    """Return the AEDT display name, falling back to its default ``<type>_<uid>`` without writing it back."""
    try:
        name = primitive.get_product_property(ProductIdType.DESIGNER, 1).strip("'")
    except Exception:
        name = ""
    if not name:
        kind = primitive.primitive_type.name.lower() if primitive_type is None else primitive_type
        name = f"{_PRIMITIVE_NAME_PREFIX.get(kind, kind)}__{primitive.edb_uid}"
    return name


def _primitives(
    edb: Edb,
    selected_layers: set[str],
    selected_nets: set[str] | None,
    arc_segments: int,
    diagnostics: list[str],
    progress: Progress | None = None,
    analytic_traces: bool = True,
    chord_error: float | None = None,
    on_preview: Callable[[list[ScenePolygon], list[SceneTrace], list[SceneJoin], list[ScenePad]], None] | None = None,
    priority_layer: str | None = None,
    object_info: dict[int, SceneObjectInfo] | None = None,
    layer_names: dict[int, str] | None = None,
    source_primitives=None,
) -> ScenePrimitives:
    """Capture analytic geometry with source contours as a fallback."""
    polygons, traces, joins, pads = [], [], [], []
    skipped = Counter()
    published = False
    for primitive, primitive_type, layer_name, net_name in _selected_primitives(
        edb, selected_layers, selected_nets, skipped, progress, priority_layer, layer_names, source_primitives
    ):
        if on_preview is not None and not published and layer_name != priority_layer:
            on_preview(polygons, traces, joins, pads)
            published = True
        try:
            object_id = primitive.id
            if object_info is not None:
                kind = "trace" if primitive_type == "path" else "pad" if primitive_type == "circle" else "zone"
                name = _primitive_name(primitive, primitive_type)
                info = SceneObjectInfo(object_id, kind, net_name, name=name)
                if kind == "trace":
                    from pyedb.viewer.adapters.grpc_stream import trace_dimensions

                    try:
                        width, length = trace_dimensions(primitive)
                        info = SceneObjectInfo(object_id, kind, net_name, width=width, length=length, name=name)
                    except Exception as exc:
                        _record_exception(
                            diagnostics, f"Trace {primitive.id}: inspection properties unavailable ({exc}).", exc
                        )
                object_info[object_id] = info
            has_voids = getattr(primitive, "has_voids", None)
            voids = primitive.voids if has_voids is None else None
            has_voids = bool(voids) if has_voids is None else has_voids
            if primitive_type == "path" and not has_voids and analytic_traces:
                try:
                    path_traces, path_joins = _trace_geometry(primitive, layer_name, net_name)
                    traces.extend(path_traces)
                    joins.extend(path_joins)
                    continue
                except Exception as exc:
                    _record_exception(diagnostics, f"Path {primitive.id}: using source boundary coverage ({exc}).", exc)
            if primitive_type == "circle" and not has_voids:
                x, y, radius = (v.double * 1000 for v in primitive.get_parameters())
                pads.append(ScenePad(object_id, layer_name, net_name, (x, y), (radius * 2,) * 2))
                continue
            polygons.append(
                ScenePolygon(
                    object_id=object_id,
                    layer=layer_name,
                    net=net_name,
                    exterior=_contour(primitive, arc_segments, chord_error),
                    holes=(
                        tuple(
                            _contour(void, arc_segments, chord_error)
                            for void in (primitive.voids if voids is None else voids)
                        )
                        if has_voids
                        else ()
                    ),
                    category="trace" if primitive_type == "path" else "pad" if primitive_type == "circle" else "zone",
                )
            )
        except Exception as exc:
            _record_exception(diagnostics, f"Primitive {primitive.id}: {exc}", exc)
    diagnostics.extend(f"Skipped {count} {kind} object(s)." for kind, count in sorted(skipped.items()))
    return polygons, traces, joins, pads


def scene_patch_from_edb(
    edb, delta, previous, *, nets=None, arc_segments=None, analytic_traces=False, chord_error=0.002, progress=None
):
    """Read only notified copper handles; never enumerate the layout or its nets.

    Layer metadata comes from the accepted snapshot. Changes with global or
    unknown dependencies are routed to full capture before reaching here.
    Incremental extraction is strict: a failed object must not silently erase
    its previously displayed geometry.
    """
    diagnostics = _Diagnostics(debug=True)
    from pyedb.grpc.database.layout_changes import PadstackSource

    vias = tuple(source.core for _, source in delta.upserts if isinstance(source, PadstackSource))
    primitives = tuple(source for _, source in delta.upserts if not isinstance(source, PadstackSource))
    info = {}
    polygons, traces, joins, pads = _primitives(
        edb,
        {layer.name for layer in previous.layers},
        _names(nets),
        arc_segments or 8,
        diagnostics,
        progress,
        analytic_traces,
        chord_error if arc_segments is None else None,
        object_info=info,
        source_primitives=primitives,
    )
    if vias:
        # Read small stackup metadata, but never enumerate board pads or
        # components. Component-owned pins use the full-capture fallback.
        layout_layers = edb.stackup.layers
        isolated = SimpleNamespace(
            stackup=SimpleNamespace(layers=layout_layers, signal_layers=edb.stackup.signal_layers),
            layout=SimpleNamespace(core=SimpleNamespace(padstack_instances=vias)),
            components=None,
            isreadonly=False,
        )
        via_pads, via_polygons = _padstacks(
            isolated,
            {layer.name for layer in previous.layers},
            _names(nets),
            arc_segments or 8,
            diagnostics,
            progress,
            None,
            chord_error if arc_segments is None else None,
            info,
            layout_layers,
        )
        pads.extend(via_pads)
        polygons.extend(via_polygons)
    return LayoutScene(
        previous.layers,
        tuple(polygons),
        previous.title,
        tuple(diagnostics),
        traces=tuple(traces),
        joins=tuple(joins),
        pads=tuple(pads),
        object_info=tuple(info.values()),
    )


def scene_from_edb(
    edb: Edb,
    layers: str | Iterable[str] | None = None,
    nets: str | Iterable[str] | None = None,
    arc_segments: int | None = None,
    *,
    progress: Progress | None = None,
    analytic_traces: bool = True,
    exact_component_bounds: bool = False,
    chord_error: float | None = 0.002,
    preview: Callable[[LayoutScene], None] | None = None,
    debug: bool = False,
) -> LayoutScene:
    """Capture analytic traces, per-layer pads and zone contours in millimeters.

    When ``debug`` is True, any exception caught internally while inspecting
    layout objects is logged with a full traceback and re-raised immediately
    instead of being recorded as a diagnostic note and skipped.
    """
    if not edb.grpc:
        raise ValueError("The interactive layout viewer currently supports only the gRPC backend.")
    if arc_segments is not None and (
        isinstance(arc_segments, bool) or not isinstance(arc_segments, int) or arc_segments < 3
    ):
        raise ValueError("arc_segments must be an integer of at least three.")
    if arc_segments is None:
        if (
            isinstance(chord_error, bool)
            or not isinstance(chord_error, (int, float))
            or not math.isfinite(chord_error)
            or chord_error <= 0
        ):
            raise ValueError("chord_error must be a positive finite number in millimeters.")
        arc_segments = 8  # Only a fallback count; adaptive chords determine the actual tessellation.
    else:
        chord_error = None
    if progress is not None:
        progress("Reading polygons", 0, 0)
    # Fetch once: edb.stackup.layers wraps every stackup layer from the EDB
    # server, so every helper below reuses this instead of refetching it.
    layout_layers = edb.stackup.layers
    selected_layers, selected_nets = _scene_filters(edb, layers, nets, layout_layers)
    scene_layers = []
    for name, layer in layout_layers.items():
        if name in selected_layers:
            color = tuple(float(v) / 255.0 for v in layer.color[:3])
            scene_layers.append(SceneLayer(name, (*color, 1.0)))
    diagnostics = _Diagnostics(debug=debug)
    object_info = {}
    net_names = tuple(edb.nets.nets)
    title = edb.active_cell.name

    def publish(
        polygons: list[ScenePolygon], traces: list[SceneTrace], joins: list[SceneJoin], pads: list[ScenePad]
    ) -> None:
        if preview is not None and (polygons or traces or pads):
            preview(
                LayoutScene(
                    tuple(scene_layers),
                    tuple(polygons),
                    title,
                    traces=tuple(traces),
                    pads=tuple(pads),
                    joins=tuple(joins),
                    net_names=net_names,
                    object_info=tuple(object_info.values()),
                )
            )

    priority_layer = scene_layers[0].name if preview is not None and scene_layers else None
    polygons, traces, joins, pads = _primitives(
        edb,
        selected_layers,
        selected_nets,
        arc_segments,
        diagnostics,
        progress,
        analytic_traces,
        chord_error,
        publish if priority_layer is not None else None,
        priority_layer,
        object_info,
        _layer_names_by_id(layout_layers),
    )
    publish(polygons, traces, joins, pads)
    component_geometry = None if exact_component_bounds else {}
    via_pads, via_polygons = _padstacks(
        edb,
        selected_layers,
        selected_nets,
        arc_segments,
        diagnostics,
        progress,
        component_geometry,
        chord_error,
        object_info,
        layout_layers,
    )
    pads.extend(via_pads)
    polygons.extend(via_polygons)
    components = _components(
        edb, selected_layers, selected_nets, diagnostics, progress, component_geometry, layout_layers
    )
    diagnostics.append(
        "GPU copper and component envelopes/references; arbitrary text, 3D bodies and bondwires are not displayed."
    )
    return LayoutScene(
        tuple(scene_layers),
        tuple(polygons),
        title,
        tuple(diagnostics),
        traces=tuple(traces),
        pads=tuple(pads),
        joins=tuple(joins),
        net_names=net_names,
        components=components,
        object_info=tuple(object_info.values()),
    )
