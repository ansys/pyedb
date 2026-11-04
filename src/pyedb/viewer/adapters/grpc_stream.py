# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT

"""Geometry helpers working on public ``ansys.edb.core`` objects."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Iterable, Sequence

from ansys.edb.core.geometry.polygon_data import PolygonData as CorePolygonData
from ansys.edb.core.utility.transform import Transform as CoreTransform
import grpc

from pyedb.generic.geometry_operators import GeometryOperators
from pyedb.misc.utilities import compute_arc_points

if TYPE_CHECKING:
    from ansys.edb.core.geometry.point_data import PointData
    from ansys.edb.core.primitive.path import Path

    from pyedb.viewer.scene import Ring

    DecodedPoint = tuple[float | None, float | None, float | None]


def _decode(points: Iterable[PointData]) -> list[DecodedPoint]:
    """Return ``(x, y, arc_height)`` tuples; arc markers have ``x``/``y`` set to ``None``."""
    decoded = []
    for point in points:
        if point.is_arc:
            decoded.append((None, None, point.arc_height.double))
        else:
            decoded.append((point.x.double, point.y.double, None))
    return decoded


def _tessellate(points: Sequence[DecodedPoint], arc_segments: int, chord_error: float | None) -> Ring:
    x, y = [], []
    error = None if chord_error is None else chord_error / 1000
    for index, (px, py, height) in enumerate(points):
        if height is None:
            x.append(px)
            y.append(py)
        else:
            start, end = points[index - 1][:2], points[(index + 1) % len(points)][:2]
            if error is None:
                ax, ay = compute_arc_points(start, end, height, arc_segments)
            else:
                ax, ay = compute_arc_points(start, end, height, arc_segments, chord_error=error)
            x.extend(ax)
            y.extend(ay)
    if not x:
        raise ValueError("No polygon boundary available.")
    x, y = GeometryOperators.orient_polygon(x, y, clockwise=True)
    return tuple((px * 1000, py * 1000) for px, py in zip(x, y))


def contour_from_points(points: Iterable[PointData], arc_segments: int, chord_error: float | None = None) -> Ring:
    """Tessellate core ``PointData`` items, including arc-height markers."""
    return _tessellate(_decode(points), arc_segments, chord_error)


def centerline_length(polygon_data: CorePolygonData) -> float:
    """Return a core centerline's length in mm, evaluating circular arcs exactly."""
    points = _decode(polygon_data.points)
    if len(points) < 2:
        return 0.0
    if polygon_data.is_closed and points[-1] != points[0]:
        points.append(points[0])
    length, index = 0.0, 1
    while index < len(points):
        start, end = points[index - 1], points[index]
        if end[2] is not None:
            if index + 1 >= len(points):
                raise ValueError("An arc requires an endpoint.")
            height = abs(end[2])
            chord = math.dist(start[:2], points[index + 1][:2])
            if height == 0:
                length += chord
            else:
                radius = chord * chord / (8 * height) + height / 2
                length += radius * 4 * math.atan2(2 * height, chord)
            index += 2
        else:
            length += math.dist(start[:2], end[:2])
            index += 1
    return length * 1000


def trace_dimensions(path: Path) -> tuple[float, float]:
    """Return a core path's width and centerline length in mm."""
    return path.width.double * 1000, centerline_length(path.center_line)


def transform_basis_points(transform: CoreTransform) -> list[PointData] | None:
    """Transform an affine basis in one native call instead of three RPCs."""
    if not isinstance(transform, CoreTransform):
        return None
    triangle = CorePolygonData(points=[(0, 0), (1, 0), (0, 1)])
    try:
        points = transform.transform_polygon(triangle).points
    except NotImplementedError:
        return None
    except grpc.RpcError as error:
        if error.code() == grpc.StatusCode.UNIMPLEMENTED:
            return None
        raise
    # Preserve the point-based fallback for an SDK returning a closed ring.
    return points if len(points) == 3 else None
