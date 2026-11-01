# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT

"""Read void geometry from streamed protobufs without building unused models."""

import sys

from ansys.api.edb.v1.edb_messages_pb2 import EDBObjMessage
from ansys.api.edb.v1.polygon_data_pb2 import PolygonDataMessage
from ansys.edb.core.primitive.primitive import Primitive as CorePrimitive
from ansys.edb.core.session import StubAccessor, StubType
from ansys.edb.core.utility.io_manager import get_cache
from ansys.edb.core.utility.value import Value as CoreValue

from pyedb.generic.geometry_operators import GeometryOperators
from pyedb.grpc.database.primitive.primitive import Primitive
from pyedb.grpc.database.utility.value import value_as_float
from pyedb.misc.utilities import compute_arc_points


def _number(message):
    if not message.text and not message.constant.imag:
        return float(message.constant.real)
    return value_as_float(CoreValue(message))


def contour_from_message(message, arc_segments, chord_error=None):
    """Decode only numerical coordinates, preserving winding and arc semantics."""
    if message.coords:
        if len(message.coords) % 2:
            raise ValueError("Boundary X and Y arrays have different lengths.")
        iterator = iter(message.coords)
        points = [(float(x), float(y), None) for x, y in zip(iterator, iterator)]
    else:
        points = []
        for point in message.points:
            x, y = _number(point.x), _number(point.y)
            points.append((x, y, x if not point.y.text and y == sys.float_info.max else None))
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


def prefetched_polygon(message):
    """Use only a geometry response explicitly belonging to this object."""
    for entry in message.cache.cache:
        if entry.rpc_method_name != "GetPolygonData":
            continue
        if not entry.request.any.Is(EDBObjMessage.DESCRIPTOR) or not entry.response.any.Is(
            PolygonDataMessage.DESCRIPTOR
        ):
            continue
        target = EDBObjMessage()
        entry.request.any.Unpack(target)
        if target.id != message.id:
            continue
        polygon = PolygonDataMessage()
        entry.response.any.Unpack(polygon)
        return polygon
    return None


class VoidReader:
    """Keep one capture's immutable rings; fall back for unsupported encodings."""

    def __init__(self, contour, arc_segments, chord_error):
        self.contour = contour
        self.arc_segments, self.chord_error = arc_segments, chord_error
        self.rings = {}
        self.prefetched = self.cache_hits = self.fallbacks = 0

    def __call__(self, primitive):
        if not isinstance(getattr(primitive, "core", None), CorePrimitive) or get_cache() is None:
            return (self.contour(item, self.arc_segments, self.chord_error) for item in primitive.voids)
        return self._stream(primitive)

    def _fallback(self, primitive, message):
        core = CorePrimitive(message).cast()
        return self.contour(Primitive(primitive._pedb, core), self.arc_segments, self.chord_error)

    def _ring(self, primitive, message):
        if message.id in self.rings:
            self.cache_hits += 1
            return self.rings[message.id]
        polygon = prefetched_polygon(message)
        if polygon is not None:
            self.prefetched += 1
        else:
            request = EDBObjMessage(id=message.id)
            cached = get_cache().hijack_request("ansys.api.edb.v1.PolygonService", "GetPolygonData", request)
            if cached is not None and isinstance(cached.result(), PolygonDataMessage):
                polygon = cached.result()
                self.cache_hits += 1
        if polygon is not None:
            ring = contour_from_message(polygon, self.arc_segments, self.chord_error)
        else:
            self.fallbacks += 1
            ring = self._fallback(primitive, message)
        self.rings[message.id] = ring
        return ring

    def _stream(self, primitive):
        stub = StubAccessor(StubType.primitive).__get__()
        stream = stub.StreamVoids(primitive.core.msg)
        try:
            for batch in stream:
                for message in batch.items:
                    yield self._ring(primitive, message)
        finally:
            # Some older servers cannot close a database while a cancelled
            # stream is still serializing. Drain even after a bad contour.
            failing = sys.exc_info()[0] is not None
            try:
                for _ in stream:
                    pass
            except Exception:
                if not failing:
                    raise
