# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT

"""Read void geometry from streamed protobufs without building unused models."""

import sys

from ansys.api.edb.v1.edb_messages_pb2 import EDBObjMessage
from ansys.api.edb.v1.polygon_data_pb2 import PolygonDataMessage
from ansys.edb.core.geometry.polygon_data import PolygonData as CorePolygonData
from ansys.edb.core.primitive.padstack_instance import PadstackInstance as CorePadstackInstance
from ansys.edb.core.primitive.path import Path as CorePath
from ansys.edb.core.primitive.polygon import Polygon as CorePolygon
from ansys.edb.core.primitive.primitive import Primitive as CorePrimitive
from ansys.edb.core.primitive.rectangle import Rectangle as CoreRectangle
from ansys.edb.core.session import StubAccessor, StubType
from ansys.edb.core.utility.io_manager import get_cache
from ansys.edb.core.utility.transform import Transform as CoreTransform
from ansys.edb.core.utility.value import Value as CoreValue
import grpc

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
    # Geometry is normally the last response. Last-to-first also matches SDK
    # cache insertion semantics when a response for the same target repeats.
    for entry in reversed(message.cache.cache):
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


def primitive_polygon_message(core):
    """Read the same typed SDK getter without constructing point/value models.

    The SDK interceptor and current session still handle transport, property
    prefetch and expressions. Unsupported primitive types use the normal API.
    """
    if isinstance(core, CorePath):
        kind = StubType.path
    elif isinstance(core, CorePolygon):
        kind = StubType.polygon
    elif isinstance(core, CoreRectangle):
        kind = StubType.rectangle
    else:
        return None
    message = StubAccessor(kind).__get__().GetPolygonData(core.msg)
    return message if isinstance(message, PolygonDataMessage) else None


def padstack_span(core, layer_names):
    """Resolve span handles against this capture's stackup, without layer casts."""
    if not isinstance(core, CorePadstackInstance) or not layer_names:
        return None
    message = StubAccessor(StubType.padstack_instance).__get__().GetLayerRange(core.msg)
    first, last = layer_names.get(message.top_layer.id), layer_names.get(message.bottom_layer.id)
    return (first, last) if first is not None and last is not None else None


def padstack_pose(core):
    """Evaluate the SDK pose response directly, including parameter expressions."""
    if not isinstance(core, CorePadstackInstance):
        return None
    message = StubAccessor(StubType.padstack_instance).__get__().GetPositionAndRotation(core.msg)
    return _number(message.position.x), _number(message.position.y), _number(message.rotation)


def padstack_component(core, components):
    """Reuse a current capture's component wrappers by exact server handle."""
    if not isinstance(core, CorePadstackInstance) or components is None:
        return None
    message = StubAccessor(StubType.connectable).__get__().GetComponent(core.msg)
    if message.id == 0:
        return False
    return components.get(message.id)


def transform_basis_points(transform):
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
