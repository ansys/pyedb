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
import grpc
import pytest

from pyedb.generic.geometry_operators import GeometryOperators
from pyedb.grpc.database.primitive.primitive import Primitive
from pyedb.grpc.database.utility.value import value_as_float
from pyedb.viewer.adapters import grpc_prefetch, grpc_primitives, grpc_stream

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


def test_prefetched_geometry_uses_latest_matching_response():
    message = prefetched(7, square())
    latest = PolygonDataMessage(coords=[0, 0, 0.002, 0, 0.002, 0.002, 0, 0.002])
    message.cache.cache.extend(prefetched(7, latest).cache.cache)
    # A later entry for a different object must still be ignored.
    message.cache.cache.extend(prefetched(7, square(), request_id=99).cache.cache)
    assert grpc_stream.prefetched_polygon(message) == latest


def test_component_basis_uses_one_polygon_call_and_preserves_point_fallback(monkeypatch):
    from ansys.edb.core.geometry.point_data import PointData

    transform = object.__new__(grpc_stream.CoreTransform)
    points = [PointData((1, 2)), PointData((1, 1)), PointData((0, 2))]
    calls = []

    def apply(self, triangle):
        calls.append([(point.x.value, point.y.value) for point in triangle.points])
        return SimpleNamespace(points=points)

    monkeypatch.setattr(grpc_stream.CoreTransform, "transform_polygon", apply)
    assert grpc_stream.transform_basis_points(transform) is points
    assert calls == [[(0, 0), (1, 0), (0, 1)]]
    assert grpc_stream.transform_basis_points(object()) is None
    points.append(PointData((1, 2)))
    assert grpc_stream.transform_basis_points(transform) is None


def test_component_basis_keeps_legacy_path_when_batch_rpc_is_unsupported(monkeypatch):
    class Unsupported(grpc_stream.grpc.RpcError):
        def code(self):
            return grpc_stream.grpc.StatusCode.UNIMPLEMENTED

    transform = object.__new__(grpc_stream.CoreTransform)
    monkeypatch.setattr(grpc_stream.CoreTransform, "transform_polygon", Mock(side_effect=Unsupported()))
    assert grpc_stream.transform_basis_points(transform) is None


@pytest.mark.parametrize(
    "core_type, kind",
    [
        (grpc_stream.CorePath, grpc_stream.StubType.path),
        (grpc_stream.CorePolygon, grpc_stream.StubType.polygon),
        (grpc_stream.CoreRectangle, grpc_stream.StubType.rectangle),
    ],
)
def test_root_contours_use_typed_getter_without_point_or_value_models(monkeypatch, core_type, kind):
    from pyedb.viewer.adapters.grpc import _contour

    request = EDBObjMessage(id=11)
    core = object.__new__(core_type)
    monkeypatch.setattr(core_type, "msg", property(lambda self: request))
    getter = Mock(return_value=square())
    routed = []

    def accessor(stub_type):
        routed.append(stub_type)
        return SimpleNamespace(__get__=lambda: SimpleNamespace(GetPolygonData=getter))

    monkeypatch.setattr(grpc_stream, "StubAccessor", accessor)
    primitive = SimpleNamespace(core=core, points=Mock(side_effect=AssertionError("No point wrappers needed")))
    assert _contour(primitive, 8, 0.01) == grpc_stream.contour_from_message(square(), 8, 0.01)
    assert routed == [kind]
    getter.assert_called_once_with(request)
    primitive.points.assert_not_called()


def test_unknown_core_type_preserves_points_fallback_without_rpc(monkeypatch):
    from pyedb.viewer.adapters.grpc import _contour

    accessor = Mock(side_effect=AssertionError("Unsupported types must keep their original getter"))
    monkeypatch.setattr(grpc_stream, "StubAccessor", accessor)
    primitive = SimpleNamespace(core=object(), points=Mock(return_value=([0, 0.001, 0], [0, 0, 0.001])))
    assert _contour(primitive, 8, 0.01) == ((0, 0), (1, 0), (0, 1))
    primitive.points.assert_called_once_with(arc_segments=8, chord_error=0.00001)


def test_pad_metadata_uses_snapshot_layer_ids_and_raw_pose_values(monkeypatch):
    from ansys.api.edb.v1.padstack_instance_pb2 import (
        PadstackInstLayerRangeMessage,
        PadstackInstPositionAndRotationMessage,
    )

    from pyedb.viewer.adapters.grpc import _padstack_layers, _placement

    request = EDBObjMessage(id=11)
    core = object.__new__(grpc_stream.CorePadstackInstance)
    monkeypatch.setattr(grpc_stream.CorePadstackInstance, "msg", property(lambda self: request))
    span = PadstackInstLayerRangeMessage(top_layer=EDBObjMessage(id=101), bottom_layer=EDBObjMessage(id=103))
    pose = PadstackInstPositionAndRotationMessage()
    pose.position.x.text = "0.001"
    pose.position.y.constant.real = 0.002
    pose.rotation.constant.real = 0
    stub = SimpleNamespace(GetLayerRange=Mock(return_value=span), GetPositionAndRotation=Mock(return_value=pose))
    monkeypatch.setattr(grpc_stream, "StubAccessor", lambda kind: SimpleNamespace(__get__=lambda: stub))
    instance = SimpleNamespace(core=core, component=None)
    names = {101: "FRONT", 102: "INNER", 103: "BACK"}
    layers = ("FRONT", "INNER", "BACK")
    assert _padstack_layers(instance, {"INNER", "BACK"}, layers, False, names) == ["INNER", "BACK"]
    assert _placement(instance, {})[0]((0, 0)) == (1, 2)
    stub.GetLayerRange.assert_called_once_with(request)
    stub.GetPositionAndRotation.assert_called_once_with(request)
    assert grpc_stream.padstack_span(core, {101: "FRONT"}) is None


def test_pad_component_reuses_only_exact_current_session_handles(monkeypatch):
    request = EDBObjMessage(id=11)
    core = object.__new__(grpc_stream.CorePadstackInstance)
    monkeypatch.setattr(grpc_stream.CorePadstackInstance, "msg", property(lambda self: request))
    response = EDBObjMessage(id=101)
    getter = Mock(return_value=response)
    monkeypatch.setattr(
        grpc_stream, "StubAccessor", lambda kind: SimpleNamespace(__get__=lambda: SimpleNamespace(GetComponent=getter))
    )
    component = object()
    assert grpc_stream.padstack_component(core, {101: component}) is component
    assert grpc_stream.padstack_component(core, {102: component}) is None
    response.id = 0
    assert grpc_stream.padstack_component(core, {}) is False
    getter.reset_mock()
    assert grpc_stream.padstack_component(core, None) is None
    getter.assert_not_called()


def test_bulk_pad_packets_match_scalar_precision_shapes_drills_and_networks():
    import numpy as np

    from pyedb.viewer.mesh import SDF_STRIDE, _sdf_packet, _write_pad_packets
    from pyedb.viewer.scene import ScenePad

    rng = np.random.default_rng(42)
    items = []
    for index in range(513):
        shape = ("circle", "rectangle", "oval", "bullet")[index % 4]
        center = tuple(rng.uniform(-1e8, 1e8, 2))
        size = tuple(rng.uniform(0.00001, 20, 2))
        if shape == "circle":
            size = (size[0],) * 2
        items.append(
            ScenePad(
                index,
                "TOP",
                None if index % 2 else "GND",
                center,
                size,
                shape,
                rotation=float(rng.uniform(-10, 10)),
                corner_radius=min(size) / 4,
                hole_radius=float(rng.uniform(0, 20)),
                hole_center=(center[0] + 0.001, center[1]),
            )
        )
    net_ids = {None: 0, "GND": 345}
    expected = np.asarray([_sdf_packet(item, net_ids[item.net]) for item in items])
    actual = np.zeros((len(items), SDF_STRIDE), dtype=np.float32)
    _write_pad_packets(items, net_ids, actual)
    assert actual.tobytes() == expected.tobytes()


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


def test_writable_sessions_never_open_extra_prefetch_channel(monkeypatch):
    create = Mock()
    monkeypatch.setattr(grpc_prefetch.core_session, "create_channel", create)
    assert grpc_prefetch.PadInstances(SimpleNamespace(isreadonly=False, version="2026.1"), [])._open() is None
    create.assert_not_called()


@pytest.mark.parametrize("version", ["2025.2", "2024.1", "", None])
def test_old_or_unknown_servers_never_open_concurrent_getter_channel(monkeypatch, version):
    create = Mock()
    monkeypatch.setattr(grpc_prefetch.core_session, "create_channel", create)
    assert grpc_prefetch.PadInstances(SimpleNamespace(isreadonly=True, version=version), [])._open() is None
    create.assert_not_called()


def test_supported_local_server_keeps_prefetch_transport(monkeypatch):
    session = SimpleNamespace(shared_memory=False, ip_address="localhost", transport_mode="insecure", port_num=50055)
    monkeypatch.setattr(grpc_prefetch.core_session.MOD, "current_session", session)
    monkeypatch.setattr(grpc_prefetch, "get_cache", lambda: object())
    create = Mock(return_value=object())
    monkeypatch.setattr(grpc_prefetch.core_session, "create_channel", create)
    reader = grpc_prefetch.PadInstances(SimpleNamespace(isreadonly=True, version="2026.1"), [])
    assert reader._open() is create.return_value
    create.assert_called_once_with(transport_mode="insecure", host="localhost", port=50055)


def test_primitive_prefetch_discards_only_known_unused_metadata():
    message = prefetched(1, square())
    message.cache.cache.add(service_name="ansys.api.edb.v1.PrimitiveService", rpc_method_name="GetHfssProp")
    message.cache.cache.add(service_name="ansys.api.edb.v1.ConnectableService", rpc_method_name="GetComponent")
    message.cache.cache.add(service_name="ansys.api.edb.v1.FutureService", rpc_method_name="GetHfssProp")
    message.cache.cache.add(service_name="ansys.api.edb.v1.PathService", rpc_method_name="GetData")
    assert grpc_primitives._discard_unused_prefetch(message) == 2
    assert [(item.service_name, item.rpc_method_name) for item in message.cache.cache] == [
        ("ansys.api.edb.v1.PolygonService", "GetPolygonData"),
        ("ansys.api.edb.v1.FutureService", "GetHfssProp"),
        ("ansys.api.edb.v1.PathService", "GetData"),
    ]
    assert grpc_stream.prefetched_polygon(message) == square()


@pytest.mark.parametrize("fail", [False, True])
def test_primitive_reader_uses_sdk_factory_and_drains_stream_on_failure(monkeypatch, fail):
    consumed = []
    core = object.__new__(grpc_primitives.CoreLayout)
    monkeypatch.setattr(grpc_primitives.CoreLayout, "msg", property(lambda self: EDBObjMessage(id=99)))

    def stream(request):
        assert request.target.id == 99
        assert request.type == grpc_primitives.LayoutObjType.PRIMITIVE.value
        for number in range(3):
            consumed.append(number)
            message = EDBObjMessage(id=number + 1)
            message.cache.cache.add(service_name="ansys.api.edb.v1.PrimitiveService", rpc_method_name="GetOwner")
            yield EDBObjCollectionMessage(items=[message])

    def create(message, kind):
        assert not message.cache.cache
        if fail:
            raise ValueError("Invalid primitive")
        return message.id

    monkeypatch.setattr(grpc_primitives.core_session.MOD, "current_session", SimpleNamespace(shared_memory=False))
    monkeypatch.setattr(grpc_primitives, "get_cache", lambda: object())
    monkeypatch.setattr(
        grpc_primitives,
        "StubAccessor",
        lambda kind: SimpleNamespace(__get__=lambda: SimpleNamespace(StreamItems=stream)),
    )
    monkeypatch.setattr(grpc_primitives, "create_lyt_obj", create)
    layout = SimpleNamespace(core=core, _wrap_primitive=lambda value: None if value == 2 else value)
    reader = grpc_primitives.PrimitiveReader(SimpleNamespace(isreadonly=True, layout=layout))
    if fail:
        with pytest.raises(ValueError, match="Invalid primitive"):
            reader.read()
    else:
        assert reader.read() == [1, 3]
        assert reader.discarded == 3
    assert consumed == [0, 1, 2]


@pytest.mark.parametrize(
    "writable, shared_memory, caching", [(True, False, True), (False, True, True), (False, False, False)]
)
def test_primitive_reader_keeps_normal_api_for_other_session_modes(monkeypatch, writable, shared_memory, caching):
    core = object.__new__(grpc_primitives.CoreLayout)
    source = [object()]
    monkeypatch.setattr(
        grpc_primitives.core_session.MOD, "current_session", SimpleNamespace(shared_memory=shared_memory)
    )
    monkeypatch.setattr(grpc_primitives, "get_cache", lambda: object() if caching else None)
    reader = grpc_primitives.PrimitiveReader(
        SimpleNamespace(isreadonly=not writable, layout=SimpleNamespace(core=core, primitives=source))
    )
    assert reader.read() is source


@pytest.mark.parametrize(
    "code", [None, grpc.StatusCode.UNIMPLEMENTED, grpc.StatusCode.UNAVAILABLE, grpc.StatusCode.DEADLINE_EXCEEDED]
)
def test_prefetch_failure_drains_reads_without_inserting_partial_responses(monkeypatch, caplog, code):
    class RpcFailure(grpc.RpcError):
        def code(self):
            return code

    cache = SimpleNamespace(add=Mock())
    monkeypatch.setattr(grpc_prefetch, "get_cache", lambda: cache)
    error = ValueError("Unsupported") if code is None else RpcFailure("RPC failed")
    failure = Mock(side_effect=error)
    completion = Mock(return_value=EDBObjMessage())
    stub = SimpleNamespace(
        GetLayerMap=SimpleNamespace(future=lambda *a, **kw: SimpleNamespace(result=failure)),
        GetHoleOverrides=SimpleNamespace(future=lambda *a, **kw: SimpleNamespace(result=completion)),
    )
    reader = grpc_prefetch.PadInstances(SimpleNamespace(), [])
    batch = [SimpleNamespace(core=SimpleNamespace(id=1))]
    with caplog.at_level("DEBUG", logger=grpc_prefetch.__name__):
        if code in {grpc.StatusCode.UNAVAILABLE, grpc.StatusCode.DEADLINE_EXCEEDED}:
            with pytest.raises(RpcFailure) as caught:
                reader._prefetch(stub, batch)
            assert caught.value is error
        else:
            reader._prefetch(stub, batch)
    assert reader.disabled
    assert failure.call_count == 2
    completion.assert_called_once_with()
    cache.add.assert_not_called()
    assert "Padstack 1: draining GetLayerMap failed" in caplog.text
