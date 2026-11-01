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

"""Immutable layout snapshots, independent of EDB, Qt and OpenGL. Coordinates are millimeters."""

from dataclasses import dataclass
from functools import cached_property
import math

Point = tuple[float, float]
Ring = tuple[Point, ...]
Bounds = tuple[float, float, float, float]


def union_bounds(bounds) -> Bounds | None:
    """Return the enclosing rectangle for a sequence of bounds, or None if empty."""
    if not bounds:
        return None
    return (
        min(b[0] for b in bounds),
        min(b[1] for b in bounds),
        max(b[2] for b in bounds),
        max(b[3] for b in bounds),
    )


def clean_ring(points) -> Ring:
    """Validate a contour and remove duplicate adjacent/closing vertices."""
    result = []
    for x, y in points:
        point = (float(x), float(y))
        if not all(math.isfinite(v) for v in point):
            raise ValueError("Contour coordinates must be finite.")
        if not result or point != result[-1]:
            result.append(point)
    if len(result) > 1 and result[0] == result[-1]:
        result.pop()
    if len(set(result)) < 3:
        raise ValueError("A contour requires at least three distinct points.")
    return tuple(result)


@dataclass(frozen=True)
class SceneLayer:
    """Layer name and display-space RGBA color in the range zero to one."""

    name: str
    color: tuple[float, float, float, float]

    def __post_init__(self):
        color = tuple(float(v) for v in self.color)
        if len(color) != 4 or any(not math.isfinite(v) or not 0 <= v <= 1 for v in color):
            raise ValueError("Layer color must contain four finite values between zero and one.")
        object.__setattr__(self, "color", color)


@dataclass(frozen=True)
class ScenePolygon:
    """One source object's exterior and independent subtractive holes."""

    object_id: int
    layer: str
    net: str | None
    exterior: Ring
    holes: tuple[Ring, ...] = ()
    component: str | None = None
    component_layer: str | None = None
    component_side: str = "top"
    pin_name: str | None = None
    category: str = "zone"

    def __post_init__(self):
        object.__setattr__(self, "exterior", clean_ring(self.exterior))
        object.__setattr__(self, "holes", tuple(clean_ring(ring) for ring in self.holes))
        _validate_pin_owner(self)
        if self.category not in {"zone", "trace", "pad"}:
            raise ValueError("Polygon category must be zone, trace or pad.")
        if self.component is not None and self.category == "zone":
            object.__setattr__(self, "category", "pad")

    @cached_property
    def bounds(self) -> Bounds:
        x, y = zip(*self.exterior)
        return min(x), min(y), max(x), max(y)


def _point(point):
    result = tuple(float(v) for v in point)
    if len(result) != 2 or not all(math.isfinite(v) for v in result):
        raise ValueError("Coordinates must contain two finite values.")
    return result


def _validate_pin_owner(item):
    if item.component is None:
        return
    if not isinstance(item.component, str) or not item.component:
        raise ValueError("A pin requires a component reference.")
    if item.component_side not in {"top", "bottom"}:
        raise ValueError("Pin component side must be top or bottom.")
    if item.component_layer is None:
        object.__setattr__(item, "component_layer", item.layer)


@dataclass(frozen=True)
class SceneTrace:
    """Analytic line or circular arc, with independent start/end caps.

    A nonzero sweep (radians, positive counterclockwise) selects an arc about
    ``center``. Geometry stays analytic at every zoom level.
    """

    object_id: int
    layer: str
    net: str | None
    start: Point
    end: Point
    width: float
    center: Point | None = None
    sweep: float = 0.0
    end_caps: tuple[str, str] = ("round", "round")

    def __post_init__(self):
        object.__setattr__(self, "start", _point(self.start))
        object.__setattr__(self, "end", _point(self.end))
        object.__setattr__(self, "end_caps", tuple(self.end_caps))
        if not math.isfinite(self.width) or self.width <= 0:
            raise ValueError("Trace width must be positive and finite.")
        if len(self.end_caps) != 2 or any(cap not in {"round", "flat", "extended"} for cap in self.end_caps):
            raise ValueError("Trace caps must be round, flat or extended.")
        if not math.isfinite(self.sweep) or abs(self.sweep) > math.tau + 1e-10:
            raise ValueError("Arc sweep must be finite and at most one revolution.")
        if self.center is not None:
            object.__setattr__(self, "center", _point(self.center))
            if not self.sweep or math.dist(self.center, self.start) == 0:
                raise ValueError("An arc requires a nonzero radius and sweep.")
            radius = math.dist(self.center, self.start)
            angle = math.atan2(self.start[1] - self.center[1], self.start[0] - self.center[0]) + self.sweep
            expected = (self.center[0] + radius * math.cos(angle), self.center[1] + radius * math.sin(angle))
            tolerance = max(radius * 1e-6, *(math.ulp(v) * 4 for v in (*self.start, *self.end, *self.center)))
            if math.dist(expected, self.end) > tolerance:
                raise ValueError("Arc endpoint does not match its center and sweep.")
        elif self.sweep:
            raise ValueError("An arc sweep requires a center.")

    @cached_property
    def bounds(self) -> Bounds:
        radius = self.width / 2
        if self.center is None:
            # Square caps at diagonal angles can extend by sqrt(2) * radius.
            padding = radius * (math.sqrt(2) if "extended" in self.end_caps else 1)
            return (
                min(self.start[0], self.end[0]) - padding,
                min(self.start[1], self.end[1]) - padding,
                max(self.start[0], self.end[0]) + padding,
                max(self.start[1], self.end[1]) + padding,
            )
        arc_radius = math.dist(self.start, self.center)
        start_angle = math.atan2(self.start[1] - self.center[1], self.start[0] - self.center[0])
        direction = 1 if self.sweep > 0 else -1
        points = [self.start, self.end]
        for angle in (0, math.pi / 2, math.pi, math.pi * 1.5):
            if ((angle - start_angle) * direction) % math.tau <= abs(self.sweep) + 1e-12:
                points.append(
                    (self.center[0] + arc_radius * math.cos(angle), self.center[1] + arc_radius * math.sin(angle))
                )
        x, y = zip(*points)
        padding = radius * (math.sqrt(2) if "extended" in self.end_caps else 1)
        return min(x) - padding, min(y) - padding, max(x) + padding, max(y) + padding


@dataclass(frozen=True)
class ScenePad:
    """An SDF pad and its optional circular drill, in world coordinates.

    Shapes are circle, rectangle, rounded rectangle (``oval``) and bullet; size is the
    full width/height, rotation is in radians, and drill position is independent
    of the pad's offset/rotation. One record belongs to one physical layer.
    Component pins retain their owner, placement layer/side and pin name so their
    boundaries can be emphasized independently of same-colored copper.
    """

    object_id: int
    layer: str
    net: str | None
    center: Point
    size: Point
    shape: str = "circle"
    rotation: float = 0.0
    corner_radius: float = 0.0
    hole_radius: float = 0.0
    hole_center: Point | None = None
    component: str | None = None
    component_layer: str | None = None
    component_side: str = "top"
    pin_name: str | None = None

    def __post_init__(self):
        object.__setattr__(self, "center", _point(self.center))
        object.__setattr__(self, "size", _point(self.size))
        object.__setattr__(self, "hole_center", _point(self.center if self.hole_center is None else self.hole_center))
        if self.shape not in {"circle", "rectangle", "oval", "bullet"}:
            raise ValueError("Unsupported SDF pad shape.")
        if min(self.size) <= 0 or not all(
            math.isfinite(v) for v in (self.rotation, self.corner_radius, self.hole_radius)
        ):
            raise ValueError("Pad dimensions must be positive and finite.")
        if not 0 <= self.corner_radius <= min(self.size) / 2 or self.hole_radius < 0:
            raise ValueError("Invalid pad corner or drill radius.")
        if self.shape == "circle" and self.size[0] != self.size[1]:
            raise ValueError("A circular pad requires equal width and height.")
        _validate_pin_owner(self)

    @cached_property
    def bounds(self) -> Bounds:
        c, s = abs(math.cos(self.rotation)), abs(math.sin(self.rotation))
        x, y = self.center
        if self.shape == "circle":
            rx = ry = self.size[0] / 2
        else:
            rx, ry = (c * self.size[0] + s * self.size[1]) / 2, (s * self.size[0] + c * self.size[1]) / 2
        hx, hy = self.hole_center
        r = self.hole_radius
        return min(x - rx, hx - r), min(y - ry, hy - r), max(x + rx, hx + r), max(y + ry, hy + r)


@dataclass(frozen=True)
class SceneJoin:
    """Convex analytic triangle/quad joining SDF trace segments without seams."""

    object_id: int
    layer: str
    net: str | None
    points: tuple[Point, ...]

    def __post_init__(self):
        object.__setattr__(self, "points", tuple(_point(p) for p in self.points))
        if len(self.points) not in (3, 4):
            raise ValueError("A join requires three or four points.")

    @cached_property
    def bounds(self) -> Bounds:
        x, y = zip(*self.points)
        return min(x), min(y), max(x), max(y)


@dataclass(frozen=True)
class SceneComponent:
    """PyEDB component bounding box and reference, already in board coordinates.

    Match ``nets.plot``: the envelope is axis-aligned and must not be rotated
    again. Nets describe membership of the whole component, rather than one pin.
    """

    object_id: int
    reference: str
    layer: str
    nets: tuple[str, ...]
    bounds: Bounds
    side: str = "top"

    def __post_init__(self):
        bounds = tuple(float(v) for v in self.bounds)
        if len(bounds) != 4 or not all(math.isfinite(v) for v in bounds):
            raise ValueError("Component bounds must contain four finite values.")
        if bounds[0] >= bounds[2] or bounds[1] >= bounds[3]:
            raise ValueError("Component bounds must have positive width and height.")
        if self.side not in {"top", "bottom"}:
            raise ValueError("Component side must be top or bottom.")
        if not self.reference:
            raise ValueError("A component requires a reference name.")
        object.__setattr__(self, "bounds", bounds)
        object.__setattr__(self, "nets", tuple(dict.fromkeys(self.nets)))

    def visible_on(self, visible_layers, mirror=False, net=None, both_sides=False):
        """Use the same layer, network and side selection for outlines and names."""
        return (
            self.layer in visible_layers
            and (both_sides or self.side == ("bottom" if mirror else "top"))
            and (net is None or net in self.nets)
        )


@dataclass(frozen=True)
class LayoutScene:
    """Detached snapshot; layer order is top to bottom, matching EDB stackup order."""

    layers: tuple[SceneLayer, ...]
    polygons: tuple[ScenePolygon, ...]
    title: str = "EDB layout"
    diagnostics: tuple[str, ...] = ()
    traces: tuple[SceneTrace, ...] = ()
    pads: tuple[ScenePad, ...] = ()
    joins: tuple[SceneJoin, ...] = ()
    net_names: tuple[str, ...] = ()
    components: tuple[SceneComponent, ...] = ()

    def __post_init__(self):
        object.__setattr__(self, "layers", tuple(self.layers))
        object.__setattr__(self, "polygons", tuple(self.polygons))
        object.__setattr__(self, "diagnostics", tuple(self.diagnostics))
        for name in ("traces", "pads", "joins", "net_names", "components"):
            object.__setattr__(self, name, tuple(getattr(self, name)))
        names = [layer.name for layer in self.layers]
        if len(names) != len(set(names)):
            raise ValueError("Scene layer names must be unique.")
        if any(item.layer not in names for item in self.geometry):
            raise ValueError("Every object must belong to a scene layer.")
        if any(component.layer not in names for component in self.components):
            raise ValueError("Every component must belong to a scene layer.")

    @property
    def geometry(self):
        """Iterate copper geometry; component envelopes are separate overlays."""
        from itertools import chain

        return chain(self.polygons, self.traces, self.pads, self.joins)

    @cached_property
    def bounds(self) -> Bounds | None:
        bounds = [item.bounds for item in self.geometry]
        bounds.extend(component.bounds for component in self.components)
        return union_bounds(bounds)
