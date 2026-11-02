# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT

import math

import pytest

from pyedb.viewer import LayoutScene, SceneLayer, SceneObjectInfo, ScenePad, ScenePolygon, SceneTrace
from pyedb.viewer.adapters.grpc_stream import centerline_length
from pyedb.viewer.picking import PickIndex, inspector_rows

pytestmark = [pytest.mark.unit, pytest.mark.no_licence]


def test_interaction_colors_are_reserved_and_visible_on_white():
    from pyedb.viewer.colors import HIGHLIGHT_KEYLINE_COLOR, HOVER_COLOR, NET_COLORS, SELECTION_COLOR

    assert HOVER_COLOR != SELECTION_COLOR
    for color in (HOVER_COLOR, SELECTION_COLOR, HIGHLIGHT_KEYLINE_COLOR):
        assert color not in NET_COLORS
        linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in color]
        luminance = sum(v * weight for v, weight in zip(linear, (0.2126, 0.7152, 0.0722)))
        assert 1.05 / (luminance + 0.05) >= 3


def rectangle(x0, y0, x1, y1):
    return ((x0, y0), (x1, y0), (x1, y1), (x0, y1))


def picking_scene():
    layers = (SceneLayer("TOP", (0.9, 0.4, 0.1, 1)), SceneLayer("BOTTOM", (0.1, 0.3, 0.8, 1)))
    return LayoutScene(
        layers,
        (
            ScenePolygon(1, "TOP", "GND", rectangle(-5, -5, 5, 5), (rectangle(-1, -1, 1, 1),)),
            ScenePolygon(2, "BOTTOM", "LOWER", rectangle(-5, -5, 5, 5)),
        ),
        traces=(SceneTrace(3, "TOP", "DATA_SIGNAL", (-2, 2), (2, 2), 0.8),),
        pads=(
            ScenePad(4, "TOP", "VIA_NET", (3, -2), (1, 1), hole_radius=0.2),
            ScenePad(4, "BOTTOM", "VIA_NET", (3, -2), (0.8, 0.8), hole_radius=0.2),
            ScenePad(5, "TOP", "PAD_NET", (-3, -2), (1.4, 0.8), "rectangle", component="U1", pin_name="A7"),
        ),
        object_info=(
            SceneObjectInfo(3, "trace", "DATA_SIGNAL", width=0.8, length=4, name="line_1"),
            SceneObjectInfo(4, "via", "VIA_NET", drill_diameter=0.4, start_layer="TOP", stop_layer="BOTTOM", name="V1"),
            SceneObjectInfo(5, "pad", "PAD_NET", component="U1", pin_name="A7"),
        ),
    )


@pytest.mark.parametrize(
    "point, kind, object_id", [((0, 2), "trace", 3), ((3, -2), "via", 4), ((-3, -2), "pad", 5), ((0, 4), "zone", 1)]
)
def test_picks_source_objects_and_not_bounding_boxes(point, kind, object_id):
    index = PickIndex(picking_scene())
    hit = index.pick(point, 100, {"TOP"})
    assert hit.key == (kind, object_id)
    assert hit.layer == "TOP"
    assert index.pick(point, 100, {"TOP"}, net="NO_SUCH_NET") is None
    assert index.pick(point, 100, {"TOP"}, opacity=0) is None


def test_zone_voids_visibility_and_physical_via_span():
    index = PickIndex(picking_scene())
    assert index.pick((0, 0), 100, {"TOP"}) is None
    assert index.pick((0, 0), 100, {"TOP", "BOTTOM"}).key == ("zone", 2)
    hit = index.pick((3, -2), 100, {"BOTTOM"})
    assert hit.key == ("via", 4) and hit.layer == "BOTTOM"
    rows = dict(inspector_rows(hit))
    assert rows["Name"] == "V1"
    assert rows["From layer"] == "TOP" and rows["To layer"] == "BOTTOM"
    assert rows["Drill diameter"] == "0.4000 mm"
    assert rows["Via diameter"] == "0.8000 mm"


def test_inspector_reports_trace_and_pin_properties_from_source():
    index = PickIndex(picking_scene())
    assert dict(inspector_rows(index.pick((0, 2), 100, {"TOP"}))) == {
        "Name": "line_1",
        "Signal": "DATA_SIGNAL",
        "Width": "0.8000 mm",
        "Length": "4.0000 mm",
        "Layer": "TOP",
    }
    assert dict(inspector_rows(index.pick((-3, -2), 100, {"TOP"}))) == {
        "Net": "PAD_NET",
        "Component": "U1",
        "Pin": "A7",
        "Layer": "TOP",
    }


def test_exact_hits_win_over_nearby_objects_and_layer_order_reverses():
    scene = LayoutScene(
        (SceneLayer("TOP", (1, 0, 0, 1)), SceneLayer("BOTTOM", (0, 0, 1, 1))),
        (),
        traces=(SceneTrace(1, "TOP", "A", (0, 0), (2, 0), 0.2), SceneTrace(2, "BOTTOM", "B", (0, 0), (2, 0), 0.2)),
        pads=(ScenePad(3, "TOP", "C", (1, 0.4), (0.2, 0.2)),),
    )
    index = PickIndex(scene)
    assert index.pick((1, 0), 10, {"TOP", "BOTTOM"}).key == ("trace", 1)
    assert index.pick((1, 0), 10, {"TOP", "BOTTOM"}, mirror=True).key == ("trace", 2)


def test_rotated_pad_and_analytic_arc_do_not_pick_their_empty_bounding_box():
    scene = LayoutScene(
        (SceneLayer("TOP", (1, 0, 0, 1)),),
        (),
        traces=(SceneTrace(1, "TOP", "A", (1, 0), (0, 1), 0.1, (0, 0), math.pi / 2),),
        pads=(ScenePad(2, "TOP", "P", (5, 0), (2, 0.2), "rectangle", rotation=math.pi / 4),),
    )
    index = PickIndex(scene)
    assert index.pick((0.1, 0.1), 1000, {"TOP"}) is None
    assert index.pick((math.sqrt(0.5), math.sqrt(0.5)), 1000, {"TOP"}).key == ("trace", 1)
    assert index.pick((5.6, -0.6), 1000, {"TOP"}) is None
    assert index.pick((5.6, 0.6), 1000, {"TOP"}).key == ("pad", 2)


def test_spatial_index_limits_candidates_and_shares_via_layer_entries():
    scene = LayoutScene(
        (SceneLayer("TOP", (1, 0, 0, 1)),),
        (),
        pads=tuple(ScenePad(i, "TOP", "N", (i % 100 * 3, i // 100 * 3), (1, 1)) for i in range(10000)),
    )
    index = PickIndex(scene)
    assert index.pick((150, 150), 100, {"TOP"}).key == ("pad", 5050)
    assert index.last_candidates < 16
    shared = PickIndex(picking_scene())
    assert len(shared.by_key["via", 4].items) == 2


def _centerline(points, closed=False):
    from types import SimpleNamespace

    from ansys.edb.core.geometry.point_data import PointData

    return SimpleNamespace(points=[PointData(point) for point in points], is_closed=closed)


def test_centerline_length_uses_analytic_arc_not_contour_perimeter():
    h = 0.001 * (1 - math.sqrt(0.5))
    assert centerline_length(_centerline([(0.001, 0), h, (0, 0.001), (0, 0.003)])) == pytest.approx(math.pi / 2 + 2)
    assert centerline_length(_centerline([(0.001, 0), -h, (0, 0.001), (0, 0.003)])) == pytest.approx(math.pi / 2 + 2)
    assert centerline_length(_centerline([(0, 0), (0.003, 0.004)])) == pytest.approx(5)
    assert centerline_length(_centerline([(0, 0), (0.003, 0)], closed=True)) == pytest.approx(6)


def test_nonround_via_reports_actual_pad_size_instead_of_invented_diameter():
    scene = LayoutScene(
        (SceneLayer("TOP", (1, 0, 0, 1)),),
        (),
        pads=(ScenePad(1, "TOP", "N", (0, 0), (2, 1), "rectangle", hole_radius=0.2),),
    )
    rows = dict(inspector_rows(PickIndex(scene).pick((0, 0), 100, {"TOP"})))
    assert rows["Via pad size"] == "2.0000 × 1.0000 mm"
    assert "Via diameter" not in rows
    assert rows["Drill diameter"] == "0.4000 mm"


def test_flat_and_extended_trace_caps_have_distinct_exact_hit_regions():
    for cap, expected in (("flat", False), ("extended", True), ("round", True)):
        scene = LayoutScene(
            (SceneLayer("TOP", (1, 0, 0, 1)),),
            (),
            traces=(SceneTrace(1, "TOP", "N", (0, 0), (2, 0), 1, end_caps=(cap, cap)),),
        )
        assert bool(PickIndex(scene).pick((-0.2, 0), 1000, {"TOP"}, pixels=0)) == expected


def test_arc_flat_cap_and_metadata_fallback_keep_centerline_semantics():
    for cap, expected in (("flat", False), ("round", True), ("extended", True)):
        scene = LayoutScene(
            (SceneLayer("TOP", (1, 0, 0, 1)),),
            (),
            traces=(SceneTrace(1, "TOP", "N", (1, 0), (0, 1), 0.2, (0, 0), math.pi / 2, end_caps=(cap, cap)),),
            object_info=(SceneObjectInfo(1, "trace", "N"),),
        )
        index = PickIndex(scene)
        assert bool(index.pick((1, -0.05), 1000, {"TOP"}, pixels=0)) == expected
        assert index.by_key["trace", 1].info.length == pytest.approx(math.pi / 2)


def test_trace_dimensions_extract_width_and_analytic_centerline():
    from types import SimpleNamespace

    from ansys.edb.core.utility.value import Value as CoreValue

    from pyedb.viewer.adapters import grpc_stream

    path = SimpleNamespace(width=CoreValue(0.00025), center_line=_centerline([(0, 0), (0.003, 0.004)]))
    width, length = grpc_stream.trace_dimensions(path)
    assert width == pytest.approx(0.25)
    assert length == pytest.approx(5.0)
