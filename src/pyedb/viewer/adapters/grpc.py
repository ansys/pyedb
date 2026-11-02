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

from collections import Counter
import math

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


def _names(value):
    return None if value is None else {value} if isinstance(value, str) else set(value)


def _conductor_names(edb):
    """Use stackup order/types, never conventional TOP/BOTTOM layer names."""
    signals = set(edb.stackup.signal_layers)
    return tuple(
        name
        for name, layer in edb.stackup.layers.items()
        if name in signals or getattr(layer, "type", None) in {"signal", "conducting"}
    )


def _component_sides(edb, diagnostics):
    names = _conductor_names(edb)
    if not names:
        return {}
    sides = {names[0]: "top"}
    if len(names) > 1:
        sides[names[-1]] = "bottom"
    else:
        # A single conductor can explicitly belong to the back surface. If no
        # association is supplied, the sole layer is the front of the stackup.
        core = getattr(edb.stackup.layers[names[0]], "core", None)
        if core is not None:
            try:
                association = getattr(core, "top_bottom_association", None)
                if getattr(association, "name", None) == "BOTTOM_ASSOCIATED":
                    sides[names[0]] = "bottom"
            except Exception as exc:
                diagnostics.append(f"Layer {names[0]}: side association unavailable ({exc}); using stackup order.")
    return sides


def _contour(primitive, arc_segments, chord_error=None):
    from pyedb.viewer.adapters.grpc_stream import contour_from_message, primitive_polygon_message

    message = primitive_polygon_message(getattr(primitive, "core", None))
    if message is not None:
        return contour_from_message(message, arc_segments, chord_error)
    if chord_error is None:
        coordinates = primitive.points(arc_segments=arc_segments)
    else:
        coordinates = primitive.points(arc_segments=arc_segments, chord_error=chord_error / 1000)
    if coordinates is None:
        raise ValueError("No polygon boundary available.")
    x, y = coordinates
    if len(x) != len(y):
        raise ValueError("Boundary X and Y arrays have different lengths.")
    return tuple((float(px) * 1000.0, float(py) * 1000.0) for px, py in zip(x, y))


def _number(value):
    try:
        return float(value.value)
    except AttributeError:
        return float(value)


def _xy(point):
    return _number(point.x) * 1000, _number(point.y) * 1000


def _tangent(trace, end=False):
    if trace.center is None:
        x, y = (b - a for a, b in zip(trace.start, trace.end))
    else:
        point = trace.end if end else trace.start
        sign = 1 if trace.sweep > 0 else -1
        x, y = -(point[1] - trace.center[1]) * sign, (point[0] - trace.center[0]) * sign
    length = math.hypot(x, y)
    return (x / length, y / length) if length else (1, 0)


def _trace_geometry(primitive, layer, net):
    """Preserve source lines/arcs and add only constant-size join geometry."""
    arcs = primitive.core.center_line.arc_data
    if not arcs:
        raise ValueError("Empty path center line.")
    get_caps = getattr(primitive.core, "get_end_cap_style", None)
    caps = (
        tuple(cap.name.lower() for cap in get_caps())
        if callable(get_caps)
        else (primitive.end_cap1, primitive.end_cap2)
    )
    if any(cap not in {"flat", "round", "extended"} for cap in caps):
        raise ValueError(f"Unsupported path caps: {caps}.")
    round_join = primitive.corner_style == "round"
    width = float(primitive.width) * 1000
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


def _rotate(point, angle):
    c, s = math.cos(angle), math.sin(angle)
    return c * point[0] - s * point[1], s * point[0] + c * point[1]


def _placement(instance, component_cache, component=None):
    from pyedb.viewer.adapters.grpc_stream import padstack_pose

    get_position = getattr(getattr(instance, "core", None), "get_position_and_rotation", None)
    if callable(get_position):
        state = padstack_pose(instance.core)
        if state is None:
            state = get_position()
        position = tuple(_number(v) * 1000 for v in state[:2])
        rotation = _number(state[2])
    else:
        position = tuple(float(v) * 1000 for v in instance.position)
        rotation = float(instance.rotation)
    basis = ((1, 0), (0, 1))
    component = instance.component if component is None else component
    if component:
        key = component.id
        if key not in component_cache:
            from ansys.edb.core.geometry.point_data import PointData

            transform = component.core.transform
            if transform.is_null:
                component_cache[key] = basis, (0.0, 0.0)
            else:
                from pyedb.viewer.adapters.grpc_stream import transform_basis_points

                points = transform_basis_points(transform)
                if points is None:
                    points = [transform.transform_point(PointData(p)) for p in ((0, 0), (1, 0), (0, 1))]
                origin, x, y = points
                ox, oy = _number(origin.x), _number(origin.y)
                component_cache[key] = (
                    ((_number(x.x) - ox, _number(x.y) - oy), (_number(y.x) - ox, _number(y.y) - oy)),
                    (ox * 1000, oy * 1000),
                )
        basis, origin = component_cache[key]
        if callable(get_position):
            px, py = position
            position = (
                origin[0] + basis[0][0] * px + basis[1][0] * py,
                origin[1] + basis[0][1] * px + basis[1][1] * py,
            )

    def vector(point):
        x, y = _rotate(point, rotation)
        return basis[0][0] * x + basis[1][0] * y, basis[0][1] * x + basis[1][1] * y

    def world(point):
        x, y = vector(point)
        return position[0] + x, position[1] + y

    scale = math.hypot(*basis[0])
    return world, vector, scale


def _pad_template(pad, arc_segments, chord_error=None):
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
    values = tuple(float(v) * 1000 for v in (pad.parameters_values or ()))
    if shape not in {"circle", "square", "rectangle", "oval", "bullet"}:
        raise ValueError(f"Unsupported pad shape {shape!r}.")
    return shape, values, offset, rotation


def _mapped_layers(instance, edb, definition, layers, cache, layout_layers=None, name=None):
    """Resolve explicit definition-to-layout mappings, including permuted names."""
    layer_map = getattr(instance, "layer_map", None)
    if layer_map is None or layer_map.is_null:
        return {layer: layer for layer in layers}
    key = (name or instance.padstack_definition, layer_map.msg.SerializeToString(), tuple(layers))
    if key not in cache:
        data = definition.core.data
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


def _pin_owner(instance, sides, cache, component=None):
    """Keep component-pin ownership separate from the physical copper pad layer."""
    if not getattr(instance, "is_pin", False):
        return {}
    component = instance.component if component is None else component
    if not component:
        return {}
    if component.id not in cache:
        layer = component.placement_layer
        cache[component.id] = (
            dict(component=component.name, component_layer=layer, component_side=sides[layer])
            if component.is_enabled and layer in sides
            else None
        )
    owner = cache[component.id]
    return dict(owner, pin_name=instance.name) if owner is not None else {}


def _padstack_layers(instance, selected_layers, conductors, extended_ranges, layer_names=None):
    """Include conducting layers within the instance's physical span."""
    instance_layers = None
    core = getattr(instance, "core", None)
    get_range = getattr(core, "get_layer_range", None)
    if callable(get_range):
        # layer_range_names rebuilds the entire signal-layer collection for
        # every instance. The snapshot already owns that ordered collection.
        from pyedb.viewer.adapters.grpc_stream import padstack_span

        span = padstack_span(core, layer_names)
        if span is None:
            layer_range = get_range()
            if not layer_range:
                return []
            span = tuple(layer.name for layer in layer_range)
        first, last = span
        if first in conductors and last in conductors:
            start, stop = sorted((conductors.index(first), conductors.index(last)))
            instance_layers = conductors[start : stop + 1]
    elif extended_ranges:
        first, last = getattr(instance, "start_layer", None), getattr(instance, "stop_layer", None)
        if first in conductors and last in conductors:
            start, stop = sorted((conductors.index(first), conductors.index(last)))
            instance_layers = conductors[start : stop + 1]
    if instance_layers is None:
        instance_layers = instance.layer_range_names
    return [name for name in instance_layers if name in selected_layers]


def _padstack_definition(instance, definitions, diagnostics, name=None):
    """Cache pad and drill data shared by instances of a definition."""
    name = name or instance.padstack_definition
    if name not in definitions:
        definition = instance.definition
        diameter = definition.hole_diameter
        if diameter is None:
            diagnostics.append(f"Padstack definition {name}: noncircular drill profile is not displayed.")
        definitions[name] = (
            definition,
            definition.pad_by_layer,
            float(diameter or 0) * 500,
            (float(definition.hole_offset_x) * 1000, float(definition.hole_offset_y) * 1000),
        )
    return definitions[name]


def _cached_pad_template(name, definition_layer, by_layer, templates, arc_segments, chord_error=None):
    """Cache each definition layer's geometry, including absent copper."""
    key = (name, definition_layer, chord_error)
    if key not in templates:
        pad = by_layer.get(definition_layer, by_layer.get("Default"))
        templates[key] = None if pad is None else _pad_template(pad, arc_segments, chord_error)
    return templates[key]


def _append_padstack_geometry(
    instance,
    layer,
    net,
    template,
    placement,
    hole_radius,
    hole_center,
    arc_segments,
    pin_owner,
    geometry,
    chord_error=None,
    *,
    object_id=None,
):
    """Place a layer's copper and retain independent drill coverage."""
    world, vector, scale = placement
    pads, polygons = geometry
    object_id = instance.id if object_id is None else object_id
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


def _padstack_pin_owner(instance, sides, cache, component, diagnostics):
    """Retain padstack geometry when optional component-pin metadata is unavailable."""
    try:
        return _pin_owner(instance, sides, cache, component)
    except Exception as exc:
        diagnostics.append(f"Padstack {instance.id}: component pin metadata unavailable ({exc}).")
        return {}


def _readonly_components(edb):
    """Index existing component wrappers for read-only padstack capture."""
    component_manager = getattr(edb, "components", None)
    return (
        {
            component.core.id: component
            for component in component_manager.instances.values()
            if getattr(getattr(component, "core", None), "id", None)
        }
        if component_manager is not None and getattr(edb, "isreadonly", False)
        else None
    )


def _padstack_object_info(instance, object_id, component, net, hole_radius, placement, span, object_info, diagnostics):
    """Capture optional inspector properties without discarding valid geometry."""
    if object_info is not None:
        try:
            reference = getattr(component, "name", None) if component else None
            object_info[object_id] = SceneObjectInfo(
                object_id,
                "pad" if component or hole_radius == 0 else "via",
                net,
                drill_diameter=hole_radius * placement[2] * 2,
                start_layer=span[0],
                stop_layer=span[-1],
                component=reference,
                pin_name=getattr(instance, "name", None) if component else None,
            )
        except Exception as exc:
            diagnostics.append(f"Padstack {object_id}: inspection properties unavailable ({exc}).")


def _record_padstack_geometry(component_geometry, object_id, component, net, placement, pads, polygons):
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
                component.id, {"bounds": bounds, "nets": set(), "approximate": False}
            )
            record["bounds"] = union_bounds([record["bounds"], bounds])
            record["nets"].update(instance_geometry["nets"])
            record["approximate"] |= approximate


def _padstacks(
    edb,
    selected_layers,
    selected_nets,
    arc_segments,
    diagnostics,
    progress=None,
    component_geometry=None,
    chord_error=None,
    object_info=None,
):
    from pyedb.viewer.adapters.grpc_prefetch import PadInstances
    from pyedb.viewer.adapters.grpc_stream import padstack_component

    pads, polygons = [], []
    definitions, templates, component_cache, mapping_cache = {}, {}, {}, {}
    pin_components = {}
    sides = _component_sides(edb, diagnostics)
    conductors = _conductor_names(edb)
    extended_ranges = bool(set(conductors).difference(edb.stackup.signal_layers))
    layout_layers = edb.stackup.layers
    layer_names = {
        layer.core.id: name
        for name, layer in layout_layers.items()
        if getattr(getattr(layer, "core", None), "id", None)
    }
    manager = getattr(edb, "padstacks", None)
    if manager is None:
        return pads, polygons
    component_objects = _readonly_components(edb)
    for instance in progress_items(
        lambda: PadInstances(edb, manager.instances.values()), progress, "Reading pads and vias"
    ):
        try:
            object_id = instance.id
            net = instance.net_name
            if selected_nets is not None and net not in selected_nets:
                continue
            span = _padstack_layers(instance, set(conductors), conductors, extended_ranges, layer_names)
            layers = [layer for layer in span if layer in selected_layers]
            if not layers:
                continue
            name = instance.padstack_definition
            definition, by_layer, hole_radius, hole_offset = _padstack_definition(
                instance, definitions, diagnostics, name
            )
            mapped = _mapped_layers(instance, edb, definition, layers, mapping_cache, layout_layers, name)
            enabled, diameter = instance.get_hole_overrides()
            if enabled:
                hole_radius = _number(diameter) * 500
            component = padstack_component(getattr(instance, "core", None), component_objects)
            if component is None:
                component = instance.component
            placement = _placement(instance, component_cache, component)
            pin_owner = _padstack_pin_owner(instance, sides, pin_components, component, diagnostics)
            hole_center = placement[0](hole_offset)
            _padstack_object_info(
                instance, object_id, component, net, hole_radius, placement, span, object_info, diagnostics
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
                    )
                except Exception as exc:
                    diagnostics.append(f"Padstack {instance.id}, layer {layer}: {exc}")
            _record_padstack_geometry(
                component_geometry, object_id, component, net, placement, pads[pad_start:], polygons[polygon_start:]
            )
        except Exception as exc:
            diagnostics.append(f"Padstack {instance.id}: {exc}")
    return pads, polygons


def _components(edb, selected_layers, selected_nets, diagnostics, progress=None, component_geometry=None):
    """Reuse captured pad envelopes, falling back to source bounds when needed."""
    manager = getattr(edb, "components", None)
    if manager is None:
        return ()
    sides = _component_sides(edb, diagnostics)
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
            diagnostics.append(f"Component {reference}: {exc}")
    if approximate_count:
        diagnostics.append(f"{approximate_count} component envelopes estimated from pin positions for fast display.")
    return tuple(result)


def _scene_filters(edb, layers, nets):
    """Normalize filters and reject names outside the source layout."""
    selected_layers, selected_nets = _names(layers), _names(nets)
    source_layers = edb.stackup.layers
    if selected_layers is None:
        selected_layers = set(_conductor_names(edb))
    unknown = selected_layers.difference(source_layers)
    if unknown:
        raise ValueError(f"Unknown layers: {', '.join(sorted(unknown))}")
    if selected_nets is not None:
        unknown = selected_nets.difference(edb.nets.nets)
        if unknown:
            raise ValueError(f"Unknown nets: {', '.join(sorted(unknown))}")
    return selected_layers, selected_nets


def _selected_primitives(edb, selected_layers, selected_nets, skipped, progress=None, priority_layer=None):
    """Filter source primitives and count unsupported copper geometry."""

    def load():
        from pyedb.viewer.adapters.grpc_primitives import PrimitiveReader

        source = PrimitiveReader(edb).read()
        if priority_layer is None:
            return [(primitive, None, None) for primitive in source]
        records = []
        for primitive in source:
            void = primitive.is_void
            records.append((primitive, None if void else primitive.layer_name, void))
        records.sort(key=lambda item: item[1] != priority_layer)
        return records

    for primitive, layer_name, void in progress_items(load, progress, "Reading polygons"):
        if void is None:
            void = primitive.is_void
        if void:
            continue
        if layer_name is None:
            layer_name = primitive.layer_name
        if layer_name not in selected_layers:
            continue
        net_name = primitive.net_name
        if selected_nets is not None and net_name not in selected_nets:
            continue
        primitive_type = primitive.type
        if primitive_type not in {"polygon", "rectangle", "circle", "path"}:
            skipped[primitive_type] += 1
            continue
        if primitive.is_negative:
            skipped["negative primitive"] += 1
            continue
        yield primitive, primitive_type, layer_name, net_name


def _primitives(
    edb,
    selected_layers,
    selected_nets,
    arc_segments,
    diagnostics,
    progress=None,
    analytic_traces=True,
    chord_error=None,
    on_preview=None,
    priority_layer=None,
    object_info=None,
):
    """Capture analytic geometry with source contours as a fallback."""
    from pyedb.viewer.adapters.grpc_stream import VoidReader

    polygons, traces, joins, pads = [], [], [], []
    read_voids = VoidReader(_contour, arc_segments, chord_error)
    skipped = Counter()
    published = False
    for primitive, primitive_type, layer_name, net_name in _selected_primitives(
        edb, selected_layers, selected_nets, skipped, progress, priority_layer
    ):
        if on_preview is not None and not published and layer_name != priority_layer:
            on_preview(polygons, traces, joins, pads)
            published = True
        try:
            object_id = primitive.id
            if object_info is not None:
                kind = "trace" if primitive_type == "path" else "pad" if primitive_type == "circle" else "zone"
                info = SceneObjectInfo(object_id, kind, net_name)
                if kind == "trace":
                    from pyedb.viewer.adapters.grpc_stream import trace_dimensions

                    try:
                        dimensions = trace_dimensions(getattr(primitive, "core", None))
                        if dimensions is not None:
                            info = SceneObjectInfo(object_id, kind, net_name, width=dimensions[0], length=dimensions[1])
                    except Exception as exc:
                        diagnostics.append(f"Trace {primitive.id}: inspection properties unavailable ({exc}).")
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
                    diagnostics.append(f"Path {primitive.id}: using source boundary coverage ({exc}).")
            if primitive_type == "circle" and not has_voids:
                x, y, radius = (float(v) * 1000 for v in primitive.get_parameters())
                pads.append(ScenePad(object_id, layer_name, net_name, (x, y), (radius * 2,) * 2))
                continue
            polygons.append(
                ScenePolygon(
                    object_id=object_id,
                    layer=layer_name,
                    net=net_name,
                    exterior=_contour(primitive, arc_segments, chord_error),
                    holes=(
                        tuple(_contour(void, arc_segments, chord_error) for void in voids)
                        if voids is not None
                        else tuple(read_voids(primitive))
                        if has_voids
                        else ()
                    ),
                    category="trace" if primitive_type == "path" else "pad" if primitive_type == "circle" else "zone",
                )
            )
        except Exception as exc:
            diagnostics.append(f"Primitive {primitive.id}: {exc}")
    diagnostics.extend(f"Skipped {count} {kind} object(s)." for kind, count in sorted(skipped.items()))
    return polygons, traces, joins, pads


def scene_from_edb(
    edb,
    layers=None,
    nets=None,
    arc_segments=None,
    *,
    progress=None,
    analytic_traces=True,
    exact_component_bounds=False,
    chord_error=0.002,
    preview=None,
):
    """Capture analytic traces, per-layer pads and zone contours in millimeters."""
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
    selected_layers, selected_nets = _scene_filters(edb, layers, nets)
    scene_layers = []
    for name, layer in edb.stackup.layers.items():
        if name in selected_layers:
            color = tuple(float(v) / 255.0 for v in layer.color[:3])
            scene_layers.append(SceneLayer(name, (*color, 1.0)))
    diagnostics = []
    object_info = {}
    net_names = tuple(edb.nets.nets)
    title = edb.active_cell.name

    def publish(polygons, traces, joins, pads):
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
    )
    pads.extend(via_pads)
    polygons.extend(via_polygons)
    components = _components(edb, selected_layers, selected_nets, diagnostics, progress, component_geometry)
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
