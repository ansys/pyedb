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

from pyedb.viewer.scene import LayoutScene, SceneComponent, SceneJoin, SceneLayer, ScenePad, ScenePolygon, SceneTrace


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


def _contour(primitive, arc_segments):
    coordinates = primitive.points(arc_segments=arc_segments)
    if coordinates is None:
        raise ValueError("No polygon boundary available.")
    x, y = coordinates
    if len(x) != len(y):
        raise ValueError("Boundary X and Y arrays have different lengths.")
    return tuple((float(px) * 1000.0, float(py) * 1000.0) for px, py in zip(x, y))


def _number(value):
    return float(value.value if hasattr(value, "value") else value)


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


def _trace_geometry(primitive):
    """Preserve source lines/arcs and add only constant-size join geometry."""
    arcs = primitive.core.center_line.arc_data
    if not arcs:
        raise ValueError("Empty path center line.")
    caps = primitive.end_cap1, primitive.end_cap2
    if any(cap not in {"flat", "round", "extended"} for cap in caps):
        raise ValueError(f"Unsupported path caps: {caps}.")
    round_join = primitive.corner_style == "round"
    width = float(primitive.width) * 1000
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
                primitive.id,
                primitive.layer_name,
                primitive.net_name,
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
            joins.append(SceneJoin(primitive.id, primitive.layer_name, primitive.net_name, (before.end, p, tip, q)))
    return traces, joins


def _rotate(point, angle):
    c, s = math.cos(angle), math.sin(angle)
    return c * point[0] - s * point[1], s * point[0] + c * point[1]


def _placement(instance, component_cache):
    position = tuple(float(v) * 1000 for v in instance.position)
    rotation = float(instance.rotation)
    basis = ((1, 0), (0, 1))
    component = instance.component
    if component:
        key = component.id
        if key not in component_cache:
            from ansys.edb.core.geometry.point_data import PointData

            transform = component.core.transform
            if transform.is_null:
                component_cache[key] = basis
            else:
                origin, x, y = [transform.transform_point(PointData(p)) for p in ((0, 0), (1, 0), (0, 1))]
                ox, oy = _number(origin.x), _number(origin.y)
                component_cache[key] = ((_number(x.x) - ox, _number(x.y) - oy), (_number(y.x) - ox, _number(y.y) - oy))
        basis = component_cache[key]

    def vector(point):
        x, y = _rotate(point, rotation)
        return basis[0][0] * x + basis[1][0] * y, basis[0][1] * x + basis[1][1] * y

    def world(point):
        x, y = vector(point)
        return position[0] + x, position[1] + y

    scale = math.hypot(*basis[0])
    return world, vector, scale


def _pad_template(pad, arc_segments):
    shape = pad.shape
    if shape in {"no_shape", "geometry", "no_geometry"}:
        return None
    offset = (float(pad.offset_x) * 1000, float(pad.offset_y) * 1000)
    rotation = float(pad.rotation)
    if shape == "polygon":
        polygon = pad.polygon_data.without_arcs(max_arc_angle=math.tau / arc_segments, max_points=arc_segments)
        return shape, tuple(_xy(p) for p in polygon.points), offset, rotation
    values = tuple(float(v) * 1000 for v in (pad.parameters_values or ()))
    if shape not in {"circle", "square", "rectangle", "oval", "bullet"}:
        raise ValueError(f"Unsupported pad shape {shape!r}.")
    return shape, values, offset, rotation


def _mapped_layers(instance, edb, definition, layers, cache):
    """Resolve explicit definition-to-layout mappings, including permuted names."""
    layer_map = getattr(instance, "layer_map", None)
    if layer_map is None or layer_map.is_null:
        return {layer: layer for layer in layers}
    key = (instance.padstack_definition, layer_map.msg.SerializeToString(), tuple(layers))
    if key not in cache:
        data = definition.core.data
        names = dict(zip(data.layer_ids, data.layer_names))
        mapped = {}
        for layer in layers:
            ids = layer_map.get_mapping_backward(edb.stackup.layers[layer].id)
            candidates = [names[layer_id] for layer_id in ids if layer_id in names]
            if len(candidates) > 1:
                raise ValueError(f"Ambiguous padstack layer mapping on {layer}.")
            mapped[layer] = candidates[0] if candidates else layer
        cache[key] = mapped
    return cache[key]


def _pin_owner(instance, sides, cache):
    """Keep component-pin ownership separate from the physical copper pad layer."""
    if not getattr(instance, "is_pin", False):
        return {}
    component = instance.component
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


def _padstacks(edb, selected_layers, selected_nets, arc_segments, diagnostics):
    pads, polygons = [], []
    definitions, templates, component_cache, mapping_cache = {}, {}, {}, {}
    pin_components = {}
    sides = _component_sides(edb, diagnostics)
    conductors = _conductor_names(edb)
    extended_ranges = bool(set(conductors).difference(edb.stackup.signal_layers))
    manager = getattr(edb, "padstacks", None)
    if manager is None:
        return pads, polygons
    for instance in manager.instances.values():
        try:
            net = instance.net_name
            if selected_nets is not None and net not in selected_nets:
                continue
            instance_layers = None
            if extended_ranges:
                first, last = getattr(instance, "start_layer", None), getattr(instance, "stop_layer", None)
                if first in conductors and last in conductors:
                    start, stop = sorted((conductors.index(first), conductors.index(last)))
                    instance_layers = conductors[start : stop + 1]
            if instance_layers is None:
                instance_layers = instance.layer_range_names
            layers = [name for name in instance_layers if name in selected_layers]
            if not layers:
                continue
            name = instance.padstack_definition
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
            definition, by_layer, hole_radius, hole_offset = definitions[name]
            mapped = _mapped_layers(instance, edb, definition, layers, mapping_cache)
            enabled, diameter = instance.get_hole_overrides()
            if enabled:
                hole_radius = _number(diameter) * 500
            world, vector, scale = _placement(instance, component_cache)
            try:
                pin_owner = _pin_owner(instance, sides, pin_components)
            except Exception as exc:
                diagnostics.append(f"Padstack {instance.id}: component pin metadata unavailable ({exc}).")
                pin_owner = {}
            hole_center = world(hole_offset)
            for layer in layers:
                try:
                    definition_layer = mapped[layer]
                    key = (name, definition_layer)
                    if key not in templates:
                        pad = by_layer.get(definition_layer, by_layer.get("Default"))
                        templates[key] = None if pad is None else _pad_template(pad, arc_segments)
                    template = templates[key]
                    if template is None:
                        # Keep nonfunctional pads absent while retaining drill marks.
                        if hole_radius > 0:
                            pads.append(
                                ScenePad(
                                    instance.id,
                                    layer,
                                    net,
                                    hole_center,
                                    (hole_radius * 2 * scale,) * 2,
                                    hole_radius=hole_radius * scale,
                                )
                            )
                        continue
                    shape, dimensions, offset, rotation = template
                    if shape == "polygon":
                        ring = tuple(
                            world(tuple(a + b for a, b in zip(_rotate(p, rotation), offset))) for p in dimensions
                        )
                        holes = ()
                        if hole_radius > 0:
                            holes = (
                                tuple(
                                    (
                                        hole_center[0] + hole_radius * scale * math.cos(i * math.tau / arc_segments),
                                        hole_center[1] + hole_radius * scale * math.sin(i * math.tau / arc_segments),
                                    )
                                    for i in range(arc_segments)
                                ),
                            )
                            pads.append(
                                ScenePad(
                                    instance.id,
                                    layer,
                                    net,
                                    hole_center,
                                    (hole_radius * 2 * scale,) * 2,
                                    hole_radius=hole_radius * scale,
                                )
                            )
                        polygons.append(ScenePolygon(instance.id, layer, net, ring, holes, category="pad", **pin_owner))
                        continue
                    center = world(offset)
                    axis = vector(_rotate((1, 0), rotation))
                    angle = math.atan2(axis[1], axis[0])
                    size = (dimensions[0],) * 2 if shape in {"circle", "square"} else dimensions[:2]
                    corner = dimensions[2] if shape in {"oval", "bullet"} else 0
                    corner = min(corner, min(size) / 2)
                    pads.append(
                        ScenePad(
                            instance.id,
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
                except Exception as exc:
                    diagnostics.append(f"Padstack {instance.id}, layer {layer}: {exc}")
        except Exception as exc:
            diagnostics.append(f"Padstack {instance.id}: {exc}")
    return pads, polygons


def _components(edb, selected_layers, selected_nets, diagnostics):
    """Capture exactly the component envelopes/names used by CommonNets.plot."""
    manager = getattr(edb, "components", None)
    if manager is None:
        return ()
    sides = _component_sides(edb, diagnostics)
    if not sides:
        return ()
    net_filter = set(edb.nets.nets) if selected_nets is None else selected_nets
    result = []
    for reference, component in manager.instances.items():
        try:
            if not component.is_enabled:
                continue
            layer = component.placement_layer
            if layer not in selected_layers or layer not in sides:
                continue
            nets = tuple(component.nets)
            if (selected_nets is not None or net_filter) and not net_filter.intersection(nets):
                continue
            bounds = tuple(float(v) * 1000 for v in component.bounding_box)
            result.append(SceneComponent(component.id, component.name, layer, nets, bounds, sides[layer]))
        except Exception as exc:
            diagnostics.append(f"Component {reference}: {exc}")
    return tuple(result)


def scene_from_edb(edb, layers=None, nets=None, arc_segments=32):
    """Capture analytic traces, per-layer pads and zone contours in millimeters."""
    if not edb.grpc:
        raise ValueError("The interactive layout viewer currently supports only the gRPC backend.")
    if isinstance(arc_segments, bool) or not isinstance(arc_segments, int) or arc_segments < 3:
        raise ValueError("arc_segments must be an integer of at least three.")
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
    scene_layers = []
    for name, layer in source_layers.items():
        if name in selected_layers:
            color = tuple(float(v) / 255.0 for v in layer.color[:3])
            scene_layers.append(SceneLayer(name, (*color, 1.0)))
    polygons, diagnostics, traces, joins, pads = [], [], [], [], []
    skipped = Counter()
    for primitive in edb.layout.primitives:
        if primitive.is_void:
            continue
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
        try:
            if primitive_type == "path" and not primitive.voids:
                try:
                    path_traces, path_joins = _trace_geometry(primitive)
                    traces.extend(path_traces)
                    joins.extend(path_joins)
                    continue
                except Exception as exc:
                    diagnostics.append(f"Path {primitive.id}: using source boundary coverage ({exc}).")
            if primitive_type == "circle" and not primitive.voids:
                x, y, radius = (float(v) * 1000 for v in primitive.get_parameters())
                pads.append(ScenePad(primitive.id, layer_name, net_name, (x, y), (radius * 2,) * 2))
                continue
            polygons.append(
                ScenePolygon(
                    object_id=primitive.id,
                    layer=layer_name,
                    net=net_name,
                    exterior=_contour(primitive, arc_segments),
                    holes=tuple(_contour(void, arc_segments) for void in primitive.voids),
                    category="trace" if primitive_type == "path" else "pad" if primitive_type == "circle" else "zone",
                )
            )
        except Exception as exc:
            diagnostics.append(f"Primitive {primitive.id}: {exc}")
    diagnostics.extend(f"Skipped {count} {kind} object(s)." for kind, count in sorted(skipped.items()))
    via_pads, via_polygons = _padstacks(edb, selected_layers, selected_nets, arc_segments, diagnostics)
    pads.extend(via_pads)
    polygons.extend(via_polygons)
    components = _components(edb, selected_layers, selected_nets, diagnostics)
    diagnostics.append(
        "GPU copper and component envelopes/references; arbitrary text, 3D bodies and bondwires are not displayed."
    )
    return LayoutScene(
        tuple(scene_layers),
        tuple(polygons),
        edb.active_cell.name,
        tuple(diagnostics),
        traces=tuple(traces),
        pads=tuple(pads),
        joins=tuple(joins),
        net_names=tuple(edb.nets.nets),
        components=components,
    )
