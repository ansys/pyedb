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

"""Viewer geometry and navigation tests require no Qt context or EDB license."""

import math
import subprocess
import sys
from types import SimpleNamespace
from unittest.mock import Mock

import numpy as np
import pytest

from pyedb.viewer import (
    LayoutScene,
    SceneComponent,
    SceneLayer,
    ScenePad,
    ScenePolygon,
    SceneTrace,
    launch_viewer,
    scene_from_edb,
)
from pyedb.viewer.camera import Camera
from pyedb.viewer.mesh import prepare_scene, split_coordinates

pytestmark = [pytest.mark.unit, pytest.mark.no_licence]


def rectangle(x0=0, y0=0, x1=10, y1=10):
    return ((x0, y0), (x1, y0), (x1, y1), (x0, y1))


def test_snapshot_validates_and_detaches_mutable_contours():
    ring = list(rectangle())
    ring.extend([ring[-1], ring[0]])
    polygon = ScenePolygon(1, "TOP", "GND", ring)
    ring[0] = (999, 999)
    assert polygon.exterior == rectangle()
    assert polygon.bounds == (0, 0, 10, 10)
    with pytest.raises(ValueError, match="finite"):
        ScenePolygon(1, "TOP", None, ((0, 0), (1, 1), (float("nan"), 2)))
    with pytest.raises(ValueError, match="three"):
        ScenePolygon(1, "TOP", None, ((0, 0), (1, 1)))
    with pytest.raises(ValueError, match="belong"):
        LayoutScene((), (polygon,))


@pytest.mark.parametrize("mirror", [False, True])
def test_camera_zoom_keeps_pointer_anchor_and_pan_round_trips(mirror):
    camera = Camera(mirror=mirror)
    camera.resize(1200, 800)
    camera.fit((1000, 2000, 1100, 2050))
    anchor = camera.screen_to_world(187, 621)
    camera.zoom_at(187, 621, 1234)
    assert camera.screen_to_world(187, 621) == pytest.approx(anchor, abs=1e-10)
    assert camera.world_to_screen(*anchor) == pytest.approx((187, 621), abs=1e-7)
    camera.pan(27, -43)
    assert camera.world_to_screen(*anchor) == pytest.approx((214, 578), abs=1e-7)
    assert not camera.visible((-100, -100, -50, -50))


def test_empty_camera_and_scene():
    scene = LayoutScene((), ())
    assert scene.bounds is None
    camera = Camera()
    camera.resize(0, 0)
    camera.fit(scene.bounds)
    assert camera.width == camera.height == 1
    assert camera.scale > 0


def test_split_coordinates_preserve_submicrometer_detail_at_large_offsets():
    original = np.array([[1e9 + 0.0001, -1e9 - 0.0002], [1e9 + 0.0003, -1e9 - 0.0004]])
    split = split_coordinates(original)
    reconstructed = split[:, :2].astype(np.float64) + split[:, 2:].astype(np.float64)
    np.testing.assert_allclose(reconstructed, original, atol=1e-7, rtol=0)
    assert split[0, 0] == split[1, 0]  # A single float32 would lose this difference.
    assert split[0, 2] != split[1, 2]


def test_concave_exterior_and_holes_keep_independent_coverage():
    pytest.importorskip("mapbox_earcut")
    # Concave L has area 64; overlapping 9-unit holes are independent coverage.
    polygon = ScenePolygon(
        7,
        "TOP",
        "GND",
        ((0, 0), (10, 0), (10, 4), (4, 4), (4, 10), (0, 10)),
        (rectangle(0.5, 0.5, 3.5, 3.5), rectangle(1, 1, 4, 4)),
    )
    scene = LayoutScene((SceneLayer("TOP", (1, 0, 0, 1)),), (polygon,))
    mesh = prepare_scene(scene)
    batch = mesh.batches[0]
    coordinates = mesh.vertices[:, :2].astype(np.float64) + mesh.vertices[:, 2:].astype(np.float64)

    def area(indices):
        triangles = coordinates[indices.reshape(-1, 3)]
        a, b = triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0]
        return np.abs(a[:, 0] * b[:, 1] - a[:, 1] * b[:, 0]).sum() / 2

    assert area(mesh.indices[: batch.outer_count]) == pytest.approx(64)
    assert area(mesh.indices[batch.outer_count :]) == pytest.approx(18)
    assert batch.object_id == 7
    assert batch.net == "GND"


def _primitive(object_id=1, layer="TOP", net="GND", ring=None, **kwargs):
    points = rectangle(0, 0, 0.01, 0.02) if ring is None else ring
    values = dict(
        id=object_id,
        layer_name=layer,
        net_name=net,
        type="polygon",
        is_void=False,
        is_negative=False,
        voids=[],
        points=Mock(return_value=tuple(zip(*points))),
    )
    values.update(kwargs)
    return SimpleNamespace(**values)


def _edb(primitives):
    layers = {"TOP": SimpleNamespace(color=(255, 128, 0)), "BOTTOM": SimpleNamespace(color=(0, 128, 255))}
    return SimpleNamespace(
        grpc=True,
        stackup=SimpleNamespace(layers=layers, signal_layers=layers),
        layout=SimpleNamespace(primitives=primitives),
        nets=SimpleNamespace(nets={"GND": None}),
        active_cell=SimpleNamespace(name="Board"),
    )


def test_grpc_adapter_converts_units_owns_holes_and_honors_filters():
    hole = _primitive(ring=rectangle(0.001, 0.002, 0.003, 0.004))
    primitive = _primitive(voids=[hole])
    edb = _edb([primitive, _primitive(2, "BOTTOM"), _primitive(3, is_void=True)])
    scene = scene_from_edb(edb, layers="TOP", nets="GND", arc_segments=20)
    assert [layer.name for layer in scene.layers] == ["TOP"]
    assert len(scene.polygons) == 1
    assert scene.polygons[0].bounds == (0, 0, 10, 20)
    assert scene.polygons[0].holes == (rectangle(1, 2, 3, 4),)
    primitive.points.assert_called_once_with(arc_segments=20)
    hole.points.assert_called_once_with(arc_segments=20)
    primitive.net_name = "CHANGED"
    assert scene.polygons[0].net == "GND"
    assert not scene_from_edb(edb, layers=[]).polygons


def test_grpc_adapter_records_failed_geometry_and_rejects_bad_inputs():
    edb = _edb([_primitive(points=Mock(side_effect=ValueError("broken contour"))), _primitive(2, type="text")])
    scene = scene_from_edb(edb)
    assert not scene.polygons
    assert any("Primitive 1: broken contour" in message for message in scene.diagnostics)
    assert any("text" in message for message in scene.diagnostics)
    with pytest.raises(ValueError, match="Unknown layers"):
        scene_from_edb(edb, layers="missing")
    with pytest.raises(ValueError, match="Unknown nets"):
        scene_from_edb(edb, nets="missing")
    with pytest.raises(ValueError, match="arc_segments"):
        scene_from_edb(edb, arc_segments=0)
    edb.grpc = False
    with pytest.raises(ValueError, match="gRPC"):
        scene_from_edb(edb)


def test_extraction_progress_counts_filtered_and_void_primitives():
    events = []
    edb = _edb([_primitive(), _primitive(2, "BOTTOM"), _primitive(3, is_void=True)])
    scene = scene_from_edb(edb, layers="TOP", progress=lambda *event: events.append(event))
    assert len(scene.polygons) == 1
    assert ("Reading polygons", 3, 3) in events
    assert events[0] == ("Reading polygons", 0, 0)
    assert {stage for stage, _, _ in events} == {"Reading polygons"}


def test_progressive_extraction_prioritizes_visible_layer_and_preserves_layer_order():
    bottom_first = _primitive(1, "BOTTOM")
    top = _primitive(2, "TOP")
    bottom_second = _primitive(3, "BOTTOM")
    previews = []
    complete = scene_from_edb(_edb([bottom_first, top, bottom_second]), preview=previews.append)
    assert len(previews) == 2
    assert [polygon.object_id for polygon in previews[0].polygons] == [2]
    assert [polygon.object_id for polygon in previews[1].polygons] == [2, 1, 3]
    assert complete.polygons == previews[-1].polygons
    assert previews[0].layers == complete.layers


def test_preparation_progress_preserves_gpu_buffers_and_completes_each_stage():
    from pyedb.viewer.demo import demo_scene

    scene = demo_scene()
    events = []
    prepared = prepare_scene(scene, progress=lambda *event: events.append(event))
    reference = prepare_scene(scene)
    for name in ("vertices", "indices", "instances"):
        np.testing.assert_array_equal(getattr(prepared, name), getattr(reference, name))
    for stage in ("Rendering layout",):
        completed = [(current, total) for name, current, total in events if name == stage]
        assert completed[0][0] == 0
        assert completed[-1][0] == completed[-1][1]
        assert all(a[0] <= b[0] for a, b in zip(completed, completed[1:]))
    assert events[-1][0] == "Rendering layout"
    assert events[-1][1] == events[-1][2]


def test_adapter_preserves_path_fallback_circle_coverage_and_skip_diagnostics():
    path = _primitive(type="path", end_cap1="unsupported", end_cap2="round", core=SimpleNamespace(center_line=None))
    circle = _primitive(2, type="circle", get_parameters=lambda: (0.003, 0.004, 0.001))
    holed_circle = _primitive(3, type="circle", voids=[_primitive(ring=rectangle(0.001, 0.001, 0.002, 0.002))])
    scene = scene_from_edb(
        _edb(
            [
                path,
                circle,
                holed_circle,
                _primitive(4, is_negative=True),
                _primitive(5, type="text"),
                _primitive(6, type="text"),
                _primitive(7, type="text", is_void=True),
                _primitive(8, "BOTTOM", type="text"),
            ]
        ),
        layers="TOP",
    )
    assert not scene.traces and not scene.joins
    assert [polygon.category for polygon in scene.polygons] == ["trace", "pad"]
    assert scene.polygons[0].exterior == rectangle(0, 0, 10, 20)
    assert scene.polygons[1].holes == (rectangle(1, 1, 2, 2),)
    assert len(scene.pads) == 1
    assert scene.pads[0].center == (3, 4) and scene.pads[0].size == (2, 2)
    circle.points.assert_not_called()
    assert scene.diagnostics[0].startswith("Path 1: using source boundary coverage")
    assert scene.diagnostics[1:3] == ("Skipped 1 negative primitive object(s).", "Skipped 2 text object(s).")


def test_scene_import_does_not_load_optional_gui_or_triangulator():
    code = (
        "import sys; import pyedb.viewer; "
        "assert not any(x in sys.modules for x in ('PySide6', 'OpenGL', 'mapbox_earcut'))"
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_launch_requires_exactly_one_source():
    with pytest.raises(ValueError, match="exactly one"):
        launch_viewer()
    with pytest.raises(ValueError, match="exactly one"):
        launch_viewer(_edb([]), scene=LayoutScene((), ()))


def test_edb_view_layout_delegates_without_opening_a_session(monkeypatch):
    from pyedb.grpc.edb import Edb

    launch = Mock(return_value="window")
    monkeypatch.setattr("pyedb.viewer.launch_viewer", launch)
    edb = object()
    assert Edb.view_layout(edb, layers="TOP", block=False) == "window"
    launch.assert_called_once_with(
        edb,
        layers="TOP",
        nets=None,
        arc_segments=None,
        block=False,
        color_by_net=True,
        plot_components=True,
        annotate_component_names=True,
        plot_components_on_both_side=True,
        analytic_traces=False,
        exact_component_bounds=False,
        chord_error=0.002,
        progressive=True,
    )
    launch.reset_mock()
    Edb.view_layout(edb, block=False, color_by_net=True)
    assert launch.call_args.kwargs["color_by_net"] is True
    launch.reset_mock()
    Edb.view_layout(
        edb,
        color_by_net=False,
        plot_components=False,
        annotate_component_names=False,
        plot_components_on_both_side=False,
    )
    assert launch.call_args.kwargs["plot_components"] is False
    assert launch.call_args.kwargs["annotate_component_names"] is False
    assert launch.call_args.kwargs["plot_components_on_both_side"] is False
    assert launch.call_args.kwargs["color_by_net"] is False


def _point(x, y):
    return SimpleNamespace(x=x, y=y)


def _arc(start, end, center=None, ccw=True):
    return SimpleNamespace(
        start=_point(*start),
        end=_point(*end),
        center=_point(*(center or start)),
        is_segment=lambda: center is None,
        is_ccw=lambda: ccw,
    )


def test_adapter_retains_analytic_paths_caps_and_sharp_joins():
    path = _primitive(
        type="path",
        width=0.001,
        end_cap1="flat",
        end_cap2="extended",
        corner_style="sharp",
        core=SimpleNamespace(
            center_line=SimpleNamespace(
                arc_data=[
                    _arc((0, 0), (0.005, 0)),
                    _arc((0.005, 0), (0.005, 0.005)),
                ]
            )
        ),
    )
    curved = _primitive(
        2,
        type="path",
        width=0.0005,
        end_cap1="round",
        end_cap2="round",
        corner_style="round",
        core=SimpleNamespace(
            center_line=SimpleNamespace(
                arc_data=[
                    _arc((0.005, 0), (0, 0.005), (0, 0)),
                ]
            )
        ),
    )
    scene = scene_from_edb(_edb([path, curved]))
    assert not scene.polygons
    assert len(scene.traces) == 3
    assert len(scene.joins) == 1
    assert len(scene.joins[0].points) == 4  # A single quad has no internal antialias seam.
    assert scene.traces[0].end_caps == ("flat", "round")
    assert scene.traces[1].end_caps == ("round", "extended")
    assert scene.traces[0].width == 1
    assert scene.traces[2].center == (0, 0)
    assert scene.traces[2].sweep == pytest.approx(math.pi / 2)
    assert any((5.5, -0.5) in join.points for join in scene.joins)
    path.points.assert_not_called()
    curved.points.assert_not_called()


def test_path_segments_reuse_source_metadata():
    reads = {"layer_name": 0, "net_name": 0}

    class CountedPath(SimpleNamespace):
        def __getattribute__(self, name):
            if name in reads:
                reads[name] += 1
            return super().__getattribute__(name)

    path = CountedPath(
        **vars(
            _primitive(
                type="path",
                width=0.001,
                end_cap1="round",
                end_cap2="round",
                corner_style="round",
                core=SimpleNamespace(
                    center_line=SimpleNamespace(
                        arc_data=[_arc((i * 0.001, 0), ((i + 1) * 0.001, 0)) for i in range(20)]
                    )
                ),
            )
        )
    )
    scene = scene_from_edb(_edb([path]))
    assert len(scene.traces) == 20
    assert reads == {"layer_name": 1, "net_name": 1}


@pytest.mark.parametrize("height", [0.0002, -0.0002])
def test_grpc_contour_tessellation_evaluates_values_before_interpolating(monkeypatch, height):
    from ansys.edb.core.utility.value import Value as CoreValue

    from pyedb.grpc.database.primitive.primitive import Primitive
    from pyedb.misc.utilities import compute_arc_points

    points = [
        SimpleNamespace(is_arc=False, x=CoreValue(0.0), y=CoreValue(0.0)),
        SimpleNamespace(is_arc=True, arc_height=CoreValue(height)),
        SimpleNamespace(is_arc=False, x=CoreValue(0.001), y=CoreValue(0.0)),
    ]

    def interpolate(start, end, sagitta, count):
        assert all(type(value) is float for value in (*start, *end, sagitta))
        return compute_arc_points(start, end, sagitta, count)

    monkeypatch.setattr("pyedb.grpc.database.primitive.primitive.compute_arc_points", interpolate)
    x, y = Primitive._get_points_for_plot(None, points, 32)
    expected_x, expected_y = compute_arc_points([0.0, 0.0], [0.001, 0.0], height, 32)
    assert x == pytest.approx([0.0, *expected_x, 0.001])
    assert y == pytest.approx([0.0, *expected_y, 0.0])


def test_grpc_polygon_data_is_read_once():
    from pyedb.grpc.database.primitive.primitive import Primitive

    class Source:
        reads = 0

        @property
        def polygon_data(self):
            self.reads += 1
            return self

    source = Source()
    primitive = Primitive(None, SimpleNamespace(cast=lambda: source))
    assert primitive.polygon_data.core is source
    assert source.reads == 1
    primitive.core = SimpleNamespace(cast=lambda: SimpleNamespace())
    assert primitive.polygon_data is None


def _pad(shape="circle", parameters=(0.002,), **kwargs):
    values = dict(shape=shape, parameters_values=parameters, offset_x=0, offset_y=0, rotation=0)
    values.update(kwargs)
    return SimpleNamespace(**values)


def _via(object_id=9, **kwargs):
    definition = SimpleNamespace(
        pad_by_layer={"TOP": _pad(offset_x=0.001), "BOTTOM": _pad("rectangle", (0.004, 0.002))},
        hole_diameter=0.001,
        hole_offset_x=0,
        hole_offset_y=0,
    )
    values = dict(
        id=object_id,
        net_name="GND",
        layer_range_names=["TOP", "BOTTOM"],
        padstack_definition="via",
        definition=definition,
        position=(0.010, 0.020),
        rotation=math.pi / 2,
        component=None,
        get_hole_overrides=lambda: (False, 0),
    )
    values.update(kwargs)
    return SimpleNamespace(**values)


def test_adapter_extracts_per_layer_via_pads_offset_rotation_drill_and_filters():
    via = _via()
    edb = _edb([])
    edb.padstacks = SimpleNamespace(instances={via.id: via})
    top_only = scene_from_edb(edb, layers="TOP")
    info = next(info for info in top_only.object_info if info.object_id == via.id)
    assert info.kind == "via"
    assert (info.start_layer, info.stop_layer) == ("TOP", "BOTTOM")
    assert info.drill_diameter == pytest.approx(1.0)
    scene = scene_from_edb(edb)
    assert len(scene.pads) == 2
    top, bottom = scene.pads
    assert top.center == pytest.approx((10, 21))
    assert top.hole_center == (10, 20)
    assert top.hole_radius == 0.5
    assert bottom.shape == "rectangle"
    assert bottom.size == (4, 2)
    assert bottom.rotation == pytest.approx(math.pi / 2)
    assert scene.bounds == pytest.approx((9, 18, 11, 22))
    assert len(scene_from_edb(edb, layers="BOTTOM").pads) == 1
    assert not scene_from_edb(edb, nets=[]).pads
    assert not scene_from_edb(edb, layers=[]).pads
    via.position = (99, 99)
    assert top.center == pytest.approx((10, 21))


def test_padstack_span_uses_snapshot_stackup_without_reenumerating_signal_layers():
    via = _via(
        core=SimpleNamespace(get_layer_range=lambda: (SimpleNamespace(name="BOTTOM"), SimpleNamespace(name="TOP")))
    )
    del via.layer_range_names
    edb = _edb([])
    edb.padstacks = SimpleNamespace(instances={via.id: via})
    scene = scene_from_edb(edb)
    assert [pad.layer for pad in scene.pads] == ["TOP", "BOTTOM"]
    assert len(scene_from_edb(edb, layers="BOTTOM").pads) == 1


def test_via_default_pad_blind_span_hole_override_and_missing_geometry_diagnostics():
    via = _via(
        layer_range_names=["TOP"],
        get_hole_overrides=lambda: (True, 0.0004),
        definition=SimpleNamespace(
            pad_by_layer={"Default": _pad()}, hole_diameter=0.001, hole_offset_x=0, hole_offset_y=0
        ),
    )
    bad = _via(
        10,
        padstack_definition="bad",
        definition=SimpleNamespace(
            pad_by_layer={"TOP": _pad("unknown")},
            hole_diameter=0,
            hole_offset_x=0,
            hole_offset_y=0,
        ),
    )
    edb = _edb([])
    edb.padstacks = SimpleNamespace(instances={9: via, 10: bad})
    scene = scene_from_edb(edb)
    assert len(scene.pads) == 1
    assert scene.pads[0].layer == "TOP"
    assert scene.pads[0].hole_radius == 0.2
    assert any("Padstack 10, layer TOP: Unsupported" in note for note in scene.diagnostics)


def test_via_retains_drill_on_layers_without_copper_pads_or_other_net_geometry():
    via = _via(layer_range_names=["TOP", "INNER", "BOTTOM"])
    edb = _edb([])
    edb.stackup.layers = {
        "TOP": SimpleNamespace(color=(255, 0, 0)),
        "INNER": SimpleNamespace(color=(0, 255, 0)),
        "BOTTOM": SimpleNamespace(color=(0, 0, 255)),
    }
    edb.stackup.signal_layers = edb.stackup.layers
    edb.padstacks = SimpleNamespace(instances={via.id: via})
    scene = scene_from_edb(edb, layers="INNER", nets="GND")
    assert not scene.polygons and not scene.traces
    assert len(scene.pads) == 1
    pad = scene.pads[0]
    assert pad.layer == "INNER" and pad.net == "GND"
    assert pad.size == (1, 1) and pad.hole_radius == 0.5
    packet = prepare_scene(scene).instances[0]
    assert packet[25] == -1  # No fabricated copper annulus on a nonfunctional layer.
    assert packet[29] == 0.5  # The physical bore remains independently renderable.


def test_sdf_packets_preserve_positions_and_batch_by_layer_without_triangulation(monkeypatch):
    offset = 1e9
    traces = tuple(
        SceneTrace(i, "TOP", "SIGNAL", (offset + i * 0.01, offset), (offset + i * 0.01 + 0.001, offset), 0.0002)
        for i in range(600)
    )
    scene = LayoutScene((SceneLayer("TOP", (1, 0, 0, 1)),), (), traces=traces)
    monkeypatch.setitem(sys.modules, "mapbox_earcut", None)
    prepared = prepare_scene(scene)
    assert not len(prepared.indices)
    assert prepared.instances.shape == (600, 40)
    assert len(prepared.sdf_batches) == 3
    assert sum(b.instance_count for b in prepared.sdf_batches) == 600
    starts = prepared.instances[:, :2].astype(np.float64) + prepared.instances[:, 2:4].astype(np.float64)
    # A high/low float32 pair has about 48 significant bits (two double ULPs here).
    np.testing.assert_allclose(starts, [trace.start for trace in traces], rtol=0, atol=3e-7)
    assert scene.bounds[2] > offset + 5


def test_sdf_scene_validation_and_pad_only_bounds():
    with pytest.raises(ValueError, match="width"):
        SceneTrace(1, "TOP", None, (0, 0), (1, 0), -1)
    with pytest.raises(ValueError, match="caps"):
        SceneTrace(1, "TOP", None, (0, 0), (1, 0), 1, end_caps=("bad", "round"))
    with pytest.raises(ValueError, match="endpoint"):
        SceneTrace(1, "TOP", None, (1, 0), (1, 1), 1, (0, 0), math.pi)
    pad = ScenePad(1, "TOP", "VIA", (5, 6), (2, 2), hole_radius=0.5)
    scene = LayoutScene((SceneLayer("TOP", (1, 0, 0, 1)),), (), pads=[pad])
    assert scene.bounds == (4, 5, 6, 7)
    with pytest.raises(ValueError, match="belong"):
        LayoutScene((), (), pads=[pad])


def test_net_colors_use_pyedb_palette_and_stay_stable_when_filtering():
    from pyedb.generic.constants import CSS4_COLORS
    from pyedb.viewer.colors import NET_COLORS, net_color

    assert tuple(round(v * 255) for v in net_color(1)) == (0xD2, 0x69, 0x1E)
    assert net_color(0) is None
    assert len(NET_COLORS) == len(CSS4_COLORS)
    assert net_color(len(NET_COLORS) + 1) == net_color(1)
    edb = _edb([_primitive(net="SIGNAL")])
    edb.nets.nets = {"GND": None, "SIGNAL": None, "OTHER": None}
    all_nets = prepare_scene(scene_from_edb(edb))
    signal = prepare_scene(scene_from_edb(edb, nets="SIGNAL"))
    assert all_nets.nets == signal.nets == (None, "GND", "SIGNAL", "OTHER")


def test_explicit_padstack_layer_mapping_uses_definition_layer_ids():
    via = _via()
    via.definition.core = SimpleNamespace(data=SimpleNamespace(layer_ids=[1, 2], layer_names=["TOP", "BOTTOM"]))
    via.layer_map = SimpleNamespace(
        is_null=False,
        msg=SimpleNamespace(SerializeToString=lambda: b"map"),
        get_mapping_backward=lambda layer_id: [2] if layer_id == 100 else [1],
    )
    edb = _edb([])
    edb.stackup.layers["TOP"].id = 100
    edb.stackup.layers["BOTTOM"].id = 101
    edb.padstacks = SimpleNamespace(instances={9: via})
    scene = scene_from_edb(edb)
    assert scene.pads[0].layer == "TOP"
    assert scene.pads[0].shape == "rectangle"
    assert scene.pads[1].shape == "circle"
    assert scene.pads[1].center == pytest.approx((10, 21))


def test_component_pad_offsets_follow_mirrored_component_basis():
    via = _via(rotation=0)

    def transform_point(point):
        return _point(100 - point.x.value, 200 + point.y.value)

    transform = SimpleNamespace(is_null=False, transform_point=transform_point)
    via.component = SimpleNamespace(id=42, core=SimpleNamespace(transform=transform))
    edb = _edb([])
    edb.padstacks = SimpleNamespace(instances={9: via})
    scene = scene_from_edb(edb)
    assert len(scene.pads) == 2
    assert scene.pads[0].center == (9, 20)
    assert scene.pads[0].hole_center == (10, 20)
    assert scene.pads[1].rotation == pytest.approx(math.pi)


def test_fast_component_envelopes_reuse_all_owned_pads_even_when_not_layout_pins():
    class OwnedComponent(SimpleNamespace):
        @property
        def bounding_box(self):
            raise AssertionError("Must not build a board layout instance for captured pad envelopes")

    component = OwnedComponent(
        id=100,
        name="U1",
        placement_layer="TOP",
        is_enabled=True,
        core=SimpleNamespace(transform=SimpleNamespace(is_null=True)),
    )
    via = _via(component=component, is_pin=False)
    edb = _edb([])
    edb.padstacks = SimpleNamespace(instances={via.id: via})
    edb.components = SimpleNamespace(instances={"U1": component})
    scene = scene_from_edb(edb)
    assert len(scene.components) == 1
    assert scene.components[0].bounds == pytest.approx((9, 18, 11, 22))
    assert scene.components[0].nets == ("GND",)


def test_fast_component_envelopes_estimate_copper_free_footprints_without_layout_instance():
    class Component(SimpleNamespace):
        @property
        def bounding_box(self):
            raise AssertionError("Fast display must not request a board layout instance")

    component = Component(
        id=100,
        name="U1",
        placement_layer="TOP",
        is_enabled=True,
        core=SimpleNamespace(members=[SimpleNamespace(edb_uid=9), SimpleNamespace(edb_uid=10)]),
    )
    definition = SimpleNamespace(
        pad_by_layer={"Default": _pad("no_shape")}, hole_diameter=0, hole_offset_x=0, hole_offset_y=0
    )
    first = _via(9, definition=definition, position=(0.01, 0.02))
    second = _via(10, definition=definition, position=(0.012, 0.02))
    edb = _edb([])
    edb.padstacks = SimpleNamespace(instances={9: first, 10: second})
    edb.components = SimpleNamespace(instances={"U1": component})
    scene = scene_from_edb(edb)
    assert len(scene.components) == 1
    assert scene.components[0].bounds == pytest.approx((9.8, 19.8, 12.2, 20.2))
    assert any("estimated" in message for message in scene.diagnostics)


def test_fast_path_contours_avoid_analytic_remote_properties():
    path = _primitive(type="path", has_voids=False)
    scene = scene_from_edb(_edb([path]), analytic_traces=False)
    assert not scene.traces
    assert len(scene.polygons) == 1
    assert scene.polygons[0].category == "trace"
    path.points.assert_called_once_with(arc_segments=8, chord_error=0.000002)


@pytest.mark.parametrize("radius", [0.02, 0.2, 2.0, 20.0])
@pytest.mark.parametrize("sweep", [0.01, math.pi / 2, math.pi, math.tau * 0.9])
@pytest.mark.parametrize("direction", [-1, 1])
def test_adaptive_chords_bound_error_for_radius_and_total_sweep(radius, sweep, direction):
    from pyedb.misc.utilities import arc_segment_count, compute_arc_points

    error = 0.01
    count = arc_segment_count(radius, sweep, error)
    assert radius * (1 - math.cos(sweep / (2 * count))) <= error + 1e-12
    assert sweep / count <= math.pi / 18 + 1e-12
    start, end = (radius, 0), (radius * math.cos(sweep), radius * math.sin(sweep))
    sagitta = radius * (1 - math.cos(sweep / 2)) * direction
    x, y = compute_arc_points(start, end, sagitta, chord_error=error)
    assert len(x) == len(y) == count - 1
    assert all(math.isfinite(value) for value in (*x, *y))


def test_adaptive_chords_grow_with_radius_and_angle_without_oversampling_flat_arcs():
    from pyedb.misc.utilities import arc_segment_count

    assert arc_segment_count(10, math.pi, 0.01) > arc_segment_count(0.1, math.pi, 0.01)
    assert arc_segment_count(10, math.pi, 0.01) > arc_segment_count(10, 0.1, 0.01)
    assert arc_segment_count(1000, 0.0001, 0.01) == 1
    assert arc_segment_count(0.02, math.tau, 0.01) >= 36
    assert arc_segment_count(0.02, math.pi, 0.002) >= 18
    assert arc_segment_count(0.02, math.pi / 2, 0.002) >= 9
    with pytest.raises(ValueError, match="segment limit"):
        arc_segment_count(1e15, math.tau, 1e-12)


@pytest.mark.parametrize("error", [0, -1, float("nan"), float("inf"), True])
def test_adaptive_chord_error_validation(error):
    with pytest.raises(ValueError, match="chord_error"):
        scene_from_edb(_edb([]), chord_error=error)


def test_pad_positions_reuse_one_component_transform_and_one_pose_read():
    from pyedb.viewer.adapters.grpc import _placement

    transform = SimpleNamespace(
        is_null=False,
        transform_point=Mock(side_effect=lambda point: _point(0.01 - point.y.value, 0.02 + point.x.value)),
    )
    component = SimpleNamespace(id=7, core=SimpleNamespace(transform=transform))
    first = SimpleNamespace(
        core=SimpleNamespace(get_position_and_rotation=Mock(return_value=(0.001, 0.002, 0))), component=component
    )
    second = SimpleNamespace(
        core=SimpleNamespace(get_position_and_rotation=Mock(return_value=(0.003, 0.004, 0))), component=component
    )
    cache = {}
    world, vector, scale = _placement(first, cache)
    assert world((0, 0)) == pytest.approx((8, 21))
    assert vector((1, 0)) == pytest.approx((0, 1))
    assert scale == pytest.approx(1)
    assert _placement(second, cache)[0]((0, 0)) == pytest.approx((6, 23))
    assert transform.transform_point.call_count == 3
    first.core.get_position_and_rotation.assert_called_once()
    second.core.get_position_and_rotation.assert_called_once()


def test_progressive_preparation_reuses_unchanged_mesh_but_adds_pads():
    polygon = ScenePolygon(1, "TOP", "GND", rectangle())
    preview = LayoutScene((SceneLayer("TOP", (1, 0, 0, 1)),), (polygon,), net_names=("GND",))
    complete = LayoutScene(
        preview.layers, preview.polygons, pads=(ScenePad(2, "TOP", "GND", (5, 5), (1, 1)),), net_names=preview.net_names
    )
    mesh = prepare_scene(preview)
    prepared = prepare_scene(complete, polygon_mesh=(preview, mesh))
    assert prepared.vertices is mesh.vertices
    assert prepared.indices is mesh.indices
    assert prepared.vertex_nets is mesh.vertex_nets
    assert len(prepared.instances) == 1


def test_progressive_preparation_appends_new_polygons_with_correct_indices_and_network_ids():
    layers = (SceneLayer("TOP", (1, 0, 0, 1)),)
    polygon = ScenePolygon(1, "TOP", "GND", rectangle())
    preview = LayoutScene(layers, (polygon,), net_names=("GND", "PWR"))
    extra = ScenePolygon(2, "TOP", "PWR", rectangle(20, 0, 25, 5), category="pad")
    complete = LayoutScene(layers, (polygon, extra), net_names=preview.net_names)
    mesh = prepare_scene(preview)
    appended = prepare_scene(complete, polygon_mesh=(preview, mesh))
    reference = prepare_scene(complete)
    for name in ("vertices", "indices", "vertex_nets"):
        np.testing.assert_array_equal(getattr(appended, name), getattr(reference, name))
    assert appended.mesh_parent_id == id(mesh)
    assert appended.batches[1].index_start == len(mesh.indices)
    assert (appended.vertex_nets[len(mesh.vertices) :] == 2).all()


def test_each_viewer_capture_reads_the_current_source_and_releases_it():
    from pyedb.viewer.capture import SourceCapture
    from pyedb.viewer.demo import demo_scene

    first_scene, second_scene = demo_scene(), LayoutScene((), (), "Changed source")
    load = Mock(side_effect=[first_scene, second_scene])
    progress = Mock()
    first, second = SourceCapture(load), SourceCapture(load)
    preview = Mock()
    first.set_preview(preview)
    assert first(progress) is first_scene
    first.release_source()
    assert first.loader is first.preview is None
    assert second(progress) is second_scene
    assert load.call_count == 2
    load.assert_any_call(progress, preview=preview)


def test_exact_component_envelopes_remain_available():
    component = _component(core=SimpleNamespace(transform=SimpleNamespace(is_null=True)))
    via = _via(component=component)
    edb = _edb([])
    edb.padstacks = SimpleNamespace(instances={via.id: via})
    edb.components = SimpleNamespace(instances={"U1": component})
    exact = scene_from_edb(edb, exact_component_bounds=True)
    assert exact.components[0].bounds == (1, 2, 4, 6)


def test_primitives_without_voids_do_not_enumerate_an_empty_remote_collection():
    class SolidPath(SimpleNamespace):
        @property
        def voids(self):
            raise AssertionError("No remote void collection is needed")

    values = vars(
        _primitive(
            type="path",
            has_voids=False,
            width=0.001,
            end_cap1="round",
            end_cap2="round",
            corner_style="round",
            core=SimpleNamespace(center_line=SimpleNamespace(arc_data=[_arc((0, 0), (0.001, 0))])),
        )
    )
    del values["voids"]
    scene = scene_from_edb(_edb([SolidPath(**values)]))
    assert len(scene.traces) == 1


def test_unassigned_sdf_geometry_retains_zero_net_material():
    scene = LayoutScene((SceneLayer("TOP", (1, 0, 0, 1)),), (), traces=(SceneTrace(1, "TOP", "", (0, 0), (1, 0), 1),))
    prepared = prepare_scene(scene)
    assert prepared.nets == (None,)
    assert prepared.instances[0, 27] == 0


def _component(reference="U1", layer="TOP", nets=None, **kwargs):
    values = dict(
        id=100,
        name=reference,
        placement_layer=layer,
        is_enabled=True,
        nets=["GND", "SIGNAL"] if nets is None else nets,
        bounding_box=[0.001, 0.002, 0.004, 0.006],
        rotation=math.pi / 4,
    )
    values.update(kwargs)
    return SimpleNamespace(**values)


def test_components_match_plot_envelopes_and_capture_filters_without_double_rotation():
    top = _component()
    bottom = _component("R2", "BOTTOM", ["OTHER"], id=101)
    edb = _edb([])
    edb.nets.nets = {"GND": None, "SIGNAL": None, "OTHER": None}
    edb.components = SimpleNamespace(
        instances={
            "U1": top,
            "R2": bottom,
            "C1": _component("C1", is_enabled=False),
            "bad": _component("bad", bounding_box=[0, 0, 0, 1]),
        }
    )
    scene = scene_from_edb(edb)
    assert len(scene.components) == 2
    assert scene.components[0].bounds == (1, 2, 4, 6)  # Already in board coordinates, even at 45°.
    assert [c.side for c in scene.components] == ["top", "bottom"]
    assert scene.components[0].reference == "U1"
    assert any("Component bad" in note for note in scene.diagnostics)
    assert [c.reference for c in scene_from_edb(edb, layers="TOP").components] == ["U1"]
    assert [c.reference for c in scene_from_edb(edb, nets="OTHER").components] == ["R2"]
    assert not scene_from_edb(edb, nets=[]).components
    assert not scene_from_edb(edb, layers=[]).components
    top.nets.append("CHANGED")
    top.bounding_box[0] = 99
    assert scene.components[0].nets == ("GND", "SIGNAL")
    assert scene.components[0].bounds == (1, 2, 4, 6)


def test_component_only_scene_bounds_resident_packet_and_compound_network_visibility():
    component = SceneComponent(1, "U1", "TOP", ["A", "B"], [1e9, 1e9, 1e9 + 0.01, 1e9 + 0.02])
    scene = LayoutScene((SceneLayer("TOP", (1, 0, 0, 1)),), (), components=[component])
    assert scene.bounds == component.bounds
    prepared = prepare_scene(scene)
    assert prepared.instances.shape == (1, 40)
    assert not len(prepared.indices)
    assert prepared.instances[0, 24] == 5
    assert prepared.component_batches[0].component is component
    assert prepared.nets == (None, "A", "B")
    assert component.visible_on({"TOP"}, net="A")
    assert component.visible_on({"TOP"}, net="B")
    assert not component.visible_on({"TOP"}, net="C")
    assert not component.visible_on({"BOTTOM"})
    assert not component.visible_on({"TOP"}, mirror=True)
    assert component.visible_on({"TOP"}, mirror=True, both_sides=True)
    with pytest.raises(ValueError, match="component must belong"):
        LayoutScene((), (), components=[component])


def test_component_pin_capture_keeps_owner_name_side_and_physical_pad_layer():
    owner = _component("U1", "TOP", id=42, core=SimpleNamespace(transform=SimpleNamespace(is_null=True)))
    pin = _via(9, is_pin=True, name="A1", component=owner)
    edb = _edb([])
    edb.padstacks = SimpleNamespace(instances={9: pin})
    scene = scene_from_edb(edb)
    info = next(info for info in scene.object_info if info.object_id == pin.id)
    assert (info.kind, info.component, info.pin_name) == ("pad", "U1", "A1")
    assert len(scene.pads) == 2
    assert [p.layer for p in scene.pads] == ["TOP", "BOTTOM"]
    for pad in scene.pads:
        assert pad.component == "U1"
        assert pad.component_layer == "TOP"
        assert pad.component_side == "top"
        assert pad.pin_name == "A1"
    owner.is_enabled = False
    disabled = scene_from_edb(edb)
    assert len(disabled.pads) == 2  # Physical copper remains; component emphasis is disabled.
    assert all(p.component is None for p in disabled.pads)


def test_pin_annotation_failure_does_not_drop_its_physical_copper():
    owner = SimpleNamespace(id=42, core=SimpleNamespace(transform=SimpleNamespace(is_null=True)))
    pin = _via(9, is_pin=True, name="1", component=owner)
    edb = _edb([])
    edb.padstacks = SimpleNamespace(instances={9: pin})
    scene = scene_from_edb(edb)
    assert len(scene.pads) == 2
    assert all(p.component is None for p in scene.pads)
    assert any("component pin metadata unavailable" in note for note in scene.diagnostics)


@pytest.mark.parametrize("hole_diameter", [0, 0.001])
def test_polygon_pad_templates_are_cached_and_preserve_placement_drills_and_pin_ownership(hole_diameter):
    polygon = SimpleNamespace(
        without_arcs=Mock(
            return_value=SimpleNamespace(points=[_point(x, y) for x, y in rectangle(-0.001, -0.002, 0.001, 0.002)])
        )
    )
    definition = SimpleNamespace(
        pad_by_layer={
            "TOP": _pad("polygon", polygon_data=polygon, offset_x=0.001, offset_y=0.002, rotation=math.pi / 2)
        },
        hole_diameter=hole_diameter,
        hole_offset_x=0.0005,
        hole_offset_y=-0.0005,
    )
    owner = _component("U1", "TOP", id=42, core=SimpleNamespace(transform=SimpleNamespace(is_null=True)))
    pins = [
        _via(i, definition=definition, layer_range_names=["TOP"], rotation=0, is_pin=True, name=str(i), component=owner)
        for i in (9, 10)
    ]
    edb = _edb([])
    edb.padstacks = SimpleNamespace(instances={pin.id: pin for pin in pins})
    scene = scene_from_edb(edb, arc_segments=12)
    polygon.without_arcs.assert_called_once_with(max_arc_angle=math.tau / 12, max_points=12)
    assert len(scene.polygons) == 2
    for copper, pin in zip(scene.polygons, pins):
        np.testing.assert_allclose(copper.exterior, ((13, 21), (13, 23), (9, 23), (9, 21)))
        assert copper.category == "pad"
        assert (copper.component, copper.component_layer, copper.component_side, copper.pin_name) == (
            "U1",
            "TOP",
            "top",
            pin.name,
        )
        if hole_diameter:
            assert len(copper.holes) == 1 and len(copper.holes[0]) == 12
            assert copper.holes[0][0] == pytest.approx((11, 19.5))
        else:
            assert not copper.holes
    assert len(scene.pads) == (2 if hole_diameter else 0)
    for drill in scene.pads:
        assert drill.center == (10.5, 19.5)
        assert drill.hole_radius == 0.5
        assert drill.component is None


def test_invalid_polygon_pad_retains_drill_and_continues_to_next_layer():
    via = _via()
    via.definition.pad_by_layer["TOP"] = _pad(
        "polygon",
        polygon_data=SimpleNamespace(
            without_arcs=lambda **kwargs: SimpleNamespace(points=[_point(0, 0), _point(1, 1)]),
            points=[SimpleNamespace(is_arc=False, x=0.0, y=0.0), SimpleNamespace(is_arc=False, x=1.0, y=1.0)],
        ),
    )
    edb = _edb([])
    edb.padstacks = SimpleNamespace(instances={via.id: via})
    scene = scene_from_edb(edb)
    assert not scene.polygons
    assert [pad.layer for pad in scene.pads] == ["TOP", "BOTTOM"]
    assert scene.pads[0].size == (1, 1) and scene.pads[0].hole_radius == 0.5
    assert scene.pads[1].shape == "rectangle"
    assert "Padstack 9, layer TOP: A contour requires at least three distinct points." in scene.diagnostics


def test_pin_packets_reuse_copper_geometry_without_extra_border_instances():
    pad = ScenePad(1, "TOP", "GND", (1, 1), (2, 2), component="U1", pin_name="1")
    polygon = ScenePolygon(
        2, "TOP", "SIGNAL", rectangle(4, 0, 8, 4), (rectangle(5, 1, 7, 3),), component="U1", pin_name="2"
    )
    scene = LayoutScene((SceneLayer("TOP", (1, 0, 0, 1)),), (polygon,), pads=(pad,))
    prepared = prepare_scene(scene)
    assert len(prepared.pin_batches) == 2
    analytic, custom = prepared.pin_batches
    assert analytic.instance_count == 1
    assert analytic.instance_start == prepared.sdf_batches[0].instance_start
    assert custom.pin is polygon
    assert custom.instance_count == 0
    assert custom.instance_start is None
    assert len(prepared.instances) == 1  # Only the original analytic pad packet.
    assert prepared.batches[0].hole_count > 0
    with pytest.raises(ValueError, match="component reference"):
        ScenePad(3, "TOP", None, (0, 0), (1, 1), component="")


def test_custom_conductor_names_include_back_components_and_single_layer_associations():
    edb = _edb([_primitive(layer="Cu_back")])
    front = SimpleNamespace(type="signal", color=(255, 0, 0))
    back = SimpleNamespace(type="conducting", color=(0, 0, 255))
    edb.stackup.layers = {"Cu_front": front, "FR4": SimpleNamespace(type="dielectric"), "Cu_back": back}
    edb.stackup.signal_layers = {"Cu_front": front}
    edb.components = SimpleNamespace(instances={"U2": _component("U2", "Cu_back")})
    scene = scene_from_edb(edb)
    assert [layer.name for layer in scene.layers] == ["Cu_front", "Cu_back"]
    assert scene.polygons[0].layer == "Cu_back"
    assert scene.components[0].side == "bottom"
    assert scene.components[0].layer == "Cu_back"

    # The model need not have any signal layer, or layers named TOP/BOTTOM.
    metal = SimpleNamespace(
        type="conducting",
        color=(50, 150, 200),
        core=SimpleNamespace(top_bottom_association=SimpleNamespace(name="BOTTOM_ASSOCIATED")),
    )
    edb.stackup.layers = {"metal_1": metal}
    edb.stackup.signal_layers = {}
    edb.layout.primitives = []
    owner = _component("U2", "metal_1", core=SimpleNamespace(transform=SimpleNamespace(is_null=True)))
    edb.components.instances = {"U2": owner}
    pin = _via(
        9,
        is_pin=True,
        name="1",
        component=owner,
        layer_range_names=[],
        start_layer="metal_1",
        stop_layer="metal_1",
        definition=SimpleNamespace(pad_by_layer={"Default": _pad()}, hole_diameter=0, hole_offset_x=0, hole_offset_y=0),
    )
    edb.padstacks = SimpleNamespace(instances={9: pin})
    scene = scene_from_edb(edb)
    assert [layer.name for layer in scene.layers] == ["metal_1"]
    assert scene.components[0].side == "bottom"
    assert scene.pads[0].component_side == "bottom"
    assert scene.pads[0].layer == "metal_1"
    edb.components.instances = {}
    edb.padstacks.instances = {}
    assert not scene_from_edb(edb).components


@pytest.mark.parametrize("mirror", [False, True])
def test_fit_padding_keeps_board_clear_of_floating_navigation(mirror):
    camera = Camera(mirror=mirror)
    camera.resize(800, 600)
    camera.fit((-20, -10, 20, 10), padding=(20, 20, 20, 100))
    a, b = camera.world_to_screen(-20, -10), camera.world_to_screen(20, 10)
    assert 20 <= min(a[0], b[0]) < max(a[0], b[0]) <= 780
    assert 20 <= min(a[1], b[1]) < max(a[1], b[1]) <= 500


def test_cli_defaults_to_network_colors_and_can_request_layer_colors(monkeypatch):
    from pyedb.viewer.__main__ import main

    launch = Mock()
    monkeypatch.setattr("pyedb.viewer.launch_viewer", launch)
    for arguments, expected in (
        (["--demo"], True),
        (["--demo", "--color-by-net"], True),
        (["--demo", "--color-by-layer"], False),
    ):
        launch.reset_mock()
        main(arguments)
        assert launch.call_args.kwargs["color_by_net"] is expected


def test_workspace_theme_has_readable_text_and_interaction_contrast():
    pytest.importorskip("PySide6")
    from pyedb.viewer.qt.theme import COLORS

    def luminance(hex_color):
        rgb = [int(hex_color[i : i + 2], 16) / 255 for i in (1, 3, 5)]
        linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in rgb]
        return sum(value * weight for value, weight in zip(linear, (0.2126, 0.7152, 0.0722)))

    def contrast(a, b):
        low, high = sorted((luminance(a), luminance(b)))
        return (high + 0.05) / (low + 0.05)

    for background in ("window", "panel", "surface"):
        assert contrast(COLORS["text"], COLORS[background]) >= 4.5
        assert contrast(COLORS["muted"], COLORS[background]) >= 4.5
    assert contrast(COLORS["accent"], COLORS["panel"]) >= 3
