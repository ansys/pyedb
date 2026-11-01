# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT

"""Streaming geometry and isolated getter-prefetch correctness contracts."""

import sys
from types import SimpleNamespace
from unittest.mock import Mock

from ansys.api.edb.v1.edb_messages_pb2 import EDBObjCollectionMessage, EDBObjMessage, ValueMessage
from ansys.api.edb.v1.polygon_data_pb2 import PolygonDataMessage
from ansys.edb.core.geometry.polygon_data import PolygonData
from ansys.edb.core.utility.value import Value as CoreValue
import pytest

from pyedb.generic.geometry_operators import GeometryOperators
from pyedb.grpc.database.primitive.primitive import Primitive
from pyedb.grpc.database.utility.value import value_as_float
from pyedb.viewer.adapters import grpc_prefetch, grpc_stream

pytestmark = [pytest.mark.unit, pytest.mark.grpc, pytest.mark.no_licence]


def square():
    return PolygonDataMessage(coords=[0, 0, 0.001, 0, 0.001, 0.001, 0, 0.001])


def prefetched(object_id, polygon, request_id=None):
    message = EDBObjMessage(id=object_id)
    entry = message.cache.cache.add(service_name="ansys.api.edb.v1.PolygonService", rpc_method_name="GetPolygonData")
    entry.request.any.Pack(EDBObjMessage(id=object_id if request_id is None else request_id))
    entry.response.any.Pack(polygon)
    return message


@pytest.mark.parametrize("height", [-0.0002, 0.0002])
@pytest.mark.parametrize("error", [None, 0.01])
def test_proto_contours_match_core_point_conversion(height, error):
    message = PolygonDataMessage()
    for x, y in ((0, 0), (height, sys.float_info.max), (0.001, 0), (0.001, 0.001), (0, 0.001)):
        point = message.points.add()
        point.x.constant.real = x
        point.y.constant.real = y
    core = PolygonData._from_msg(message)
    x, y = Primitive._get_points_for_plot(None, core.points, 8, chord_error=None if error is None else error / 1000)
    x, y = GeometryOperators.orient_polygon(x, y, clockwise=True)
    reference = tuple((a * 1000, b * 1000) for a, b in zip(x, y))
    assert grpc_stream.contour_from_message(message, 8, error) == reference


def test_prefetched_geometry_checks_object_identity_and_reuses_rings(monkeypatch):
    reader = grpc_stream.VoidReader(Mock(side_effect=AssertionError("No high-level models needed")), 8, 0.01)
    message = prefetched(7, square())
    result = reader._ring(SimpleNamespace(), message)
    assert len(result) == 4
    assert reader.prefetched == 1
    assert reader._ring(SimpleNamespace(), message) is result
    assert reader.cache_hits == 1
    assert grpc_stream.prefetched_polygon(prefetched(7, square(), request_id=99)) is None
    reader._fallback = Mock(return_value=result)
    monkeypatch.setattr(grpc_stream, "get_cache", lambda: SimpleNamespace(hijack_request=lambda *args: None))
    assert reader._ring(SimpleNamespace(), EDBObjMessage(id=8)) == result
    reader._fallback.assert_called_once()


def test_failed_contour_drains_stream_before_database_can_close(monkeypatch):
    consumed = []

    def stream():
        for number in range(3):
            consumed.append(number)
            yield EDBObjCollectionMessage(items=[EDBObjMessage(id=number + 1)])

    stub = SimpleNamespace(StreamVoids=lambda request: stream())
    monkeypatch.setattr(grpc_stream, "StubAccessor", lambda kind: SimpleNamespace(__get__=lambda: stub))
    reader = grpc_stream.VoidReader(Mock(), 8, 0.01)
    reader._ring = Mock(side_effect=ValueError("Invalid contour"))
    with pytest.raises(ValueError, match="Invalid contour"):
        list(reader._stream(SimpleNamespace(core=SimpleNamespace(msg=EDBObjMessage(id=99)))))
    assert consumed == [0, 1, 2]


def test_numeric_conversion_does_not_wrap_constants_or_evaluate_numeric_text():
    class RecordedValue(CoreValue):
        @property
        def value(self):
            raise AssertionError("A constant must not trigger evaluation")

    assert value_as_float(RecordedValue(ValueMessage(text="0.001"))) == 0.001
    constant = ValueMessage()
    constant.constant.real = 0.25
    assert value_as_float(RecordedValue(constant)) == 0.25
    constant.constant.imag = 1
    with pytest.raises(TypeError):
        value_as_float(CoreValue(constant))


def test_prefetch_submits_bounded_reads_before_waiting_and_inserts_on_capture_thread(monkeypatch):
    submissions = []
    count = 4

    class Method:
        def __init__(self, name):
            self.name = name

        def future(self, request, timeout):
            submissions.append((self.name, request.id))

            def result():
                assert len(submissions) == count * 2
                return EDBObjMessage(id=request.id)

            return SimpleNamespace(result=result)

    cache = SimpleNamespace(add=Mock())
    monkeypatch.setattr(grpc_prefetch, "get_cache", lambda: cache)
    batch = [SimpleNamespace(core=SimpleNamespace(id=index)) for index in range(1, count + 1)]
    iterator = grpc_prefetch.PadInstances(SimpleNamespace(isreadonly=True), batch, window=count)
    iterator._prefetch(SimpleNamespace(GetLayerMap=Method("map"), GetHoleOverrides=Method("override")), batch)
    assert iterator.prefetched == count
    assert not iterator.disabled
    assert cache.add.call_count == count * 2
    assert {call.args[1] for call in cache.add.call_args_list} == {"GetLayerMap", "GetHoleOverrides"}
    iterator._prefetch(SimpleNamespace(GetLayerMap=Method("map"), GetHoleOverrides=Method("override")), batch)
    assert len(submissions) == count * 2, "Loading another layer must reuse already fetched instance attributes"


def test_writable_sessions_never_open_extra_prefetch_channel(monkeypatch):
    create = Mock()
    monkeypatch.setattr(grpc_prefetch.core_session, "create_channel", create)
    assert grpc_prefetch.PadInstances(SimpleNamespace(isreadonly=False), [])._open() is None
    create.assert_not_called()


def test_prefetch_failure_falls_back_without_inserting_partial_responses(monkeypatch):
    cache = SimpleNamespace(add=Mock())
    monkeypatch.setattr(grpc_prefetch, "get_cache", lambda: cache)
    failure = Mock(side_effect=ValueError("Unsupported"))
    stub = SimpleNamespace(
        GetLayerMap=SimpleNamespace(future=lambda *a, **kw: SimpleNamespace(result=failure)),
        GetHoleOverrides=SimpleNamespace(future=lambda *a, **kw: SimpleNamespace(result=lambda: EDBObjMessage())),
    )
    reader = grpc_prefetch.PadInstances(SimpleNamespace(), [])
    reader._prefetch(stub, [SimpleNamespace(core=SimpleNamespace(id=1))])
    assert reader.disabled
    cache.add.assert_not_called()
