# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT

"""Core-geometry helper correctness contracts."""

from types import SimpleNamespace
from unittest.mock import Mock

from ansys.edb.core.geometry.point_data import PointData
from ansys.edb.core.utility.value import Value as CoreValue
import pytest

from pyedb.generic.geometry_operators import GeometryOperators
from pyedb.grpc.database.primitive.primitive import Primitive
from pyedb.grpc.database.utility.value import value_as_float
from pyedb.viewer.adapters import grpc_stream

pytestmark = [pytest.mark.unit, pytest.mark.grpc, pytest.mark.no_licence]


@pytest.mark.parametrize("height", [-0.0002, 0.0002])
@pytest.mark.parametrize("error", [None, 0.01])
def test_core_point_contours_match_primitive_plot_points(height, error):
    points = [PointData((0, 0)), PointData(height), PointData((0.001, 0)), PointData((0.001, 0.001))]
    points.append(PointData((0, 0.001)))
    x, y = Primitive._get_points_for_plot(None, points, 8, chord_error=None if error is None else error / 1000)
    x, y = GeometryOperators.orient_polygon(x, y, clockwise=True)
    reference = tuple((a * 1000, b * 1000) for a, b in zip(x, y))
    assert grpc_stream.contour_from_points(points, 8, error) == reference


@pytest.mark.parametrize("height", [-0.0002, 0.0002])
def test_core_point_arcs_stay_within_their_chord_bounds(height):
    contour = grpc_stream.contour_from_points([PointData((0, 0)), PointData(height), PointData((0.001, 0))], 8, 0.01)
    assert len(contour) > 3
    assert all(abs(value) <= 1 for point in contour for value in point)


def test_component_basis_uses_one_polygon_call_and_preserves_point_fallback(monkeypatch):
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


def test_contour_reads_polygon_data_points():
    from pyedb.viewer.adapters.grpc import _contour

    points = [
        SimpleNamespace(is_arc=False, x=CoreValue(x), y=CoreValue(y)) for x, y in [(0, 0), (0.001, 0), (0, 0.001)]
    ]
    primitive = SimpleNamespace(polygon_data=SimpleNamespace(points=points))
    assert _contour(primitive, 8, 0.01) == ((0, 1), (1, 0), (0, 0))


def test_pad_metadata_uses_core_layer_range_and_pose():
    from pyedb.viewer.adapters.grpc import _padstack_layers, _placement

    core = SimpleNamespace(
        get_layer_range=Mock(return_value=(SimpleNamespace(name="INNER"), SimpleNamespace(name="BACK"))),
        get_position_and_rotation=Mock(return_value=(CoreValue(0.001), CoreValue(0.002), CoreValue(0))),
    )
    instance = SimpleNamespace(core=core, component=None)
    layers = ("FRONT", "INNER", "BACK")
    assert _padstack_layers(instance, {"INNER", "BACK"}, layers, False) == ["INNER", "BACK"]
    assert _placement(instance, {})[0]((0, 0)) == (1, 2)
    core.get_layer_range.assert_called_once_with()
    core.get_position_and_rotation.assert_called_once_with()


def test_pad_component_reuses_only_current_capture_components():
    from pyedb.viewer.adapters.grpc import _padstack_component

    group = SimpleNamespace(is_null=False, id=101)
    instance = SimpleNamespace(core=SimpleNamespace(component=group))
    component = object()
    assert _padstack_component(instance, {101: component}) is component
    assert _padstack_component(instance, {102: component}) is None
    assert _padstack_component(instance, None) is None
    group.is_null = True
    assert _padstack_component(instance, {}) is False
    assert _padstack_component(SimpleNamespace(), {}) is None


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


def test_numeric_conversion_does_not_evaluate_constants():
    class RecordedValue(CoreValue):
        @property
        def value(self):
            raise AssertionError("A constant must not trigger evaluation")

    assert value_as_float(RecordedValue(0.25)) == 0.25
    with pytest.raises(TypeError):
        value_as_float(CoreValue(complex(0.25, 1)))


@pytest.mark.parametrize(
    "kind, prop, expected",
    [
        ("PATH", "'Trace_A'", "Trace_A"),
        ("PATH", "", "line_42"),
        ("POLYGON", None, "poly_42"),
        ("RECTANGLE", "''", "rect_42"),
        ("CIRCLE", RuntimeError("no property"), "circle_42"),
    ],
)
def test_primitive_name_uses_aedt_name_with_default_fallback(kind, prop, expected):
    from pyedb.viewer.adapters.grpc import _primitive_name

    getter = Mock(side_effect=prop) if isinstance(prop, Exception) else Mock(return_value=prop)
    if prop is None:
        getter = Mock(side_effect=AttributeError("unset"))
    primitive = SimpleNamespace(get_product_property=getter, primitive_type=SimpleNamespace(name=kind), id=42)
    assert _primitive_name(primitive) == expected
