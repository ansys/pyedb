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


"""Layout viewer unit tests; they require no OpenGL context or EDB license."""

import math
import os
import subprocess
import sys
from types import SimpleNamespace
from unittest.mock import Mock

from ansys.edb.core.geometry.point_data import PointData
from ansys.edb.core.utility.value import Value as CoreValue
import numpy as np
import pytest

from pyedb.generic.geometry_operators import GeometryOperators
from pyedb.grpc.database.primitive.primitive import Primitive
from pyedb.viewer import (
    LayoutScene,
    SceneComponent,
    SceneLayer,
    SceneObjectInfo,
    ScenePad,
    ScenePolygon,
    SceneTrace,
    launch_viewer,
    scene_from_edb,
)
from pyedb.viewer.adapters import grpc_stream
from pyedb.viewer.adapters.grpc_stream import centerline_length
from pyedb.viewer.camera import Camera
from pyedb.viewer.mesh import prepare_scene, split_coordinates
from pyedb.viewer.picking import PickIndex, inspector_rows

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


pytestmark = [pytest.mark.unit, pytest.mark.no_licence, pytest.mark.grpc]

def rectangle(x0=0, y0=0, x1=10, y1=10):
    return ((x0, y0), (x1, y0), (x1, y1), (x0, y1))


class _PolygonData:
    """Core ``PolygonData`` fake that counts boundary reads."""

    def __init__(self, ring, error=None):
        self.ring, self.error, self.reads = ring, error, 0

    @property
    def points(self):
        self.reads += 1
        if self.error is not None:
            raise self.error
        return [SimpleNamespace(is_arc=False, x=_value(x), y=_value(y)) for x, y in self.ring]


def _enum(name):
    return SimpleNamespace(name=name.upper())


def _primitive(
    object_id=1,
    layer="TOP",
    net="GND",
    ring=None,
    *,
    type="polygon",
    contour_error=None,
    end_cap1=None,
    end_cap2=None,
    corner_style=None,
    **kwargs,
):
    """Fake an ``ansys.edb.core`` primitive as returned by ``layout.core.primitives``."""
    values = dict(
        id=object_id,
        edb_uid=object_id,
        layer=SimpleNamespace(name=layer),
        net=SimpleNamespace(name=net, is_null=net is None),
        primitive_type=_enum(type),
        is_void=False,
        is_negative=False,
        voids=[],
        polygon_data=_PolygonData(rectangle(0, 0, 0.01, 0.02) if ring is None else ring, contour_error),
    )
    if end_cap1 is not None:
        values["get_end_cap_style"] = lambda: (_enum(end_cap1), _enum(end_cap2))
    if corner_style is not None:
        values["corner_style"] = _enum(corner_style)
    values.update(kwargs)
    return SimpleNamespace(**values)


class _Layout:
    """Fake pyedb layout exposing core primitives and padstack instances."""

    def __init__(self, primitives, padstack_instances=()):
        self.primitives = primitives
        self.padstack_instances = list(padstack_instances)

    @property
    def core(self):
        return SimpleNamespace(primitives=self.primitives, padstack_instances=self.padstack_instances)


def _edb(primitives):
    layers = {"TOP": SimpleNamespace(color=(255, 128, 0)), "BOTTOM": SimpleNamespace(color=(0, 128, 255))}
    return SimpleNamespace(
        grpc=True,
        stackup=SimpleNamespace(layers=layers, signal_layers=layers),
        layout=_Layout(primitives),
        nets=SimpleNamespace(nets={"GND": None}),
        active_cell=SimpleNamespace(name="Board"),
    )


def _value(value):
    """Fake a core ``Value`` exposing ``double``."""
    return SimpleNamespace(double=value)


def _point(x, y):
    return SimpleNamespace(x=_value(x), y=_value(y))


def _arc(start, end, center=None, ccw=True):
    return SimpleNamespace(
        start=_point(*start),
        end=_point(*end),
        center=_point(*(center or start)),
        is_segment=lambda: center is None,
        is_ccw=lambda: ccw,
    )


def _pad(shape="circle", parameters=(0.002,), **kwargs):
    values = dict(shape=shape, parameters_values=parameters, offset_x=0, offset_y=0, rotation=0)
    values.update(kwargs)
    return SimpleNamespace(**values)


def _geometry_type(shape):
    """Core ``PadGeometryType`` for a shape name; unknown names get a stand-in enum member."""
    from ansys.edb.core.definition.padstack_def_data import PadGeometryType

    name = f"PADGEOMTYPE_{shape.upper()}"
    return getattr(PadGeometryType, name, None) or SimpleNamespace(name=name)


def _core_polygon(points=(), without_arcs=None):
    """Fake core ``PolygonData``; the adapter recognizes polygon pads by this type."""
    from ansys.edb.core.geometry.polygon_data import PolygonData as CorePolygonData

    class _CorePolygon(CorePolygonData):
        def __init__(self):
            self._points = list(points)
            if without_arcs is not None:
                self.without_arcs = without_arcs

        @property
        def points(self):
            return self._points

    return _CorePolygon()


class _PadstackData:
    """Fake core ``PadstackDefData`` answering ``get_pad_parameters`` from per-layer ``_pad`` specs."""

    def __init__(self, spec):
        self.spec = spec

    @property
    def layer_names(self):
        return list(self.spec.pad_by_layer)

    @property
    def layer_ids(self):
        return self.spec.layer_ids

    def get_pad_parameters(self, layer_name, pad_type):
        from ansys.edb.core.definition.padstack_def_data import PadGeometryType, PadType

        spec = self.spec
        if pad_type == PadType.HOLE:
            if not spec.hole_diameter:
                return ()
            offsets = (_value(spec.hole_offset_x), _value(spec.hole_offset_y), _value(0.0))
            return PadGeometryType.PADGEOMTYPE_CIRCLE, [_value(spec.hole_diameter)], *offsets
        pad = spec.pad_by_layer.get(layer_name)
        if pad is None or pad.shape == "no_shape":
            return ()
        offsets = (_value(pad.offset_x), _value(pad.offset_y), _value(pad.rotation))
        if pad.shape == "polygon":
            return pad.polygon_data, *offsets
        return _geometry_type(pad.shape), [_value(v) for v in pad.parameters_values], *offsets


class _CoreComponent:
    """Fake core ``ComponentGroup`` read from a ``_component`` spec.

    Missing spec attributes raise ``RuntimeError``, as a failing gRPC property read would.
    """

    is_null = False

    def __init__(self, owner):
        self.owner = owner

    def _read(self, name):
        try:
            return getattr(self.owner, name)
        except AttributeError:
            raise RuntimeError(f"{name} unavailable") from None

    @property
    def edb_uid(self):
        return self._read("id")

    @property
    def name(self):
        return self._read("name")

    @property
    def transform(self):
        return self._read("core").transform

    @property
    def placement_layer(self):
        return SimpleNamespace(name=self._read("placement_layer"))

    @property
    def component_property(self):
        return SimpleNamespace(enabled=self._read("is_enabled"))


class _Via:
    """Fake core ``PadstackInstance`` exposing what ``layout.core.padstack_instances`` returns.

    Plain spec attributes (``position``, ``layer_range_names``, ``definition``, ``component`` …)
    stay mutable so tests can adjust them; the core API is derived from them on each read.
    """

    def __init__(self, object_id=9, **kwargs):
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
            is_pin=False,
            name=None,
            layer_map=None,
            get_hole_overrides=lambda: (False, _value(0)),
        )
        values.update(kwargs)
        self.__dict__.update(values)

    @property
    def edb_uid(self):
        return self.id

    @property
    def net(self):
        return SimpleNamespace(name=self.net_name, is_null=not self.net_name)

    @property
    def is_layout_pin(self):
        return self.is_pin

    @property
    def padstack_def(self):
        return SimpleNamespace(name=self.padstack_definition, data=_PadstackData(self.definition))

    @property
    def component(self):
        owner = self.__dict__["component"]
        return SimpleNamespace(is_null=True) if owner is None else _CoreComponent(owner)

    @component.setter
    def component(self, owner):
        self.__dict__["component"] = owner

    def get_layer_range(self):
        names = self.layer_range_names
        return (SimpleNamespace(name=names[0]), SimpleNamespace(name=names[-1])) if names else ()

    def get_position_and_rotation(self):
        return _value(self.position[0]), _value(self.position[1]), _value(self.rotation)


def _via(object_id=9, **kwargs):
    return _Via(object_id, **kwargs)


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


def _hole_only(geom_type, params):
    """``get_pad_parameters`` stand-in returning only a hole, as ``get_hole_parameters`` does internally."""
    from ansys.edb.core.definition.padstack_def_data import PadType

    def get_pad_parameters(layer_name, pad_type):
        if pad_type != PadType.HOLE:
            return ()
        return geom_type, [_value(v) for v in params], _value(0.0), _value(0.0), _value(0.0)

    return get_pad_parameters


@pytest.fixture
def window():
    pytest.importorskip("PySide6")
    pytest.importorskip("mapbox_earcut")
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication

    from pyedb.viewer.demo import demo_scene
    from pyedb.viewer.qt.window import LayoutWindow

    app = QApplication.instance() or QApplication([])
    window = LayoutWindow(demo_scene())
    for _ in range(100):
        if window.canvas._pick_index is not None:
            break
        QTest.qWait(50)
    assert window.canvas._pick_index is not None
    yield window
    window.canvas.cleanup()
    window.close()
    app.processEvents()


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


def _centerline(points, closed=False):
    from types import SimpleNamespace

    from ansys.edb.core.geometry.point_data import PointData

    return SimpleNamespace(points=[PointData(point) for point in points], is_closed=closed)


class TestSceneModel:
    def test_snapshot_validates_and_detaches_mutable_contours(self):
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

    def test_empty_camera_and_scene(self):
        scene = LayoutScene((), ())
        assert scene.bounds is None
        camera = Camera()
        camera.resize(0, 0)
        camera.fit(scene.bounds)
        assert camera.width == camera.height == 1
        assert camera.scale > 0

    def test_scene_import_does_not_load_optional_gui_or_triangulator(self):
        code = (
            "import sys; import pyedb.viewer; "
            "assert not any(x in sys.modules for x in ('PySide6', 'OpenGL', 'mapbox_earcut'))"
        )
        result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
        assert result.returncode == 0, result.stderr

    def test_launch_requires_exactly_one_source(self):
        with pytest.raises(ValueError, match="exactly one"):
            launch_viewer()
        with pytest.raises(ValueError, match="exactly one"):
            launch_viewer(_edb([]), scene=LayoutScene((), ()))

    def test_sdf_scene_validation_and_pad_only_bounds(self):
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


class TestCamera:
    @pytest.mark.parametrize("mirror", [False, True])
    def test_camera_zoom_keeps_pointer_anchor_and_pan_round_trips(self, mirror):
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

    def test_split_coordinates_preserve_submicrometer_detail_at_large_offsets(self):
        original = np.array([[1e9 + 0.0001, -1e9 - 0.0002], [1e9 + 0.0003, -1e9 - 0.0004]])
        split = split_coordinates(original)
        reconstructed = split[:, :2].astype(np.float64) + split[:, 2:].astype(np.float64)
        np.testing.assert_allclose(reconstructed, original, atol=1e-7, rtol=0)
        assert split[0, 0] == split[1, 0]  # A single float32 would lose this difference.
        assert split[0, 2] != split[1, 2]

    @pytest.mark.parametrize("mirror", [False, True])
    def test_fit_padding_keeps_board_clear_of_floating_navigation(self, mirror):
        camera = Camera(mirror=mirror)
        camera.resize(800, 600)
        camera.fit((-20, -10, 20, 10), padding=(20, 20, 20, 100))
        a, b = camera.world_to_screen(-20, -10), camera.world_to_screen(20, 10)
        assert 20 <= min(a[0], b[0]) < max(a[0], b[0]) <= 780
        assert 20 <= min(a[1], b[1]) < max(a[1], b[1]) <= 500


class TestGrpcAdapter:
    def test_grpc_adapter_reads_core_primitives_and_skips_unassigned_nets(self):
        primitive = _primitive()
        scene = scene_from_edb(_edb([primitive, _primitive(2, net=None)]), layers="TOP", arc_segments=20)
        assert [polygon.object_id for polygon in scene.polygons] == [primitive.id]

    def test_grpc_adapter_converts_units_owns_holes_and_honors_filters(self):
        hole = _primitive(ring=rectangle(0.001, 0.002, 0.003, 0.004))
        primitive = _primitive(voids=[hole])
        edb = _edb([primitive, _primitive(2, "BOTTOM"), _primitive(3, is_void=True)])
        scene = scene_from_edb(edb, layers="TOP", nets="GND", arc_segments=20)
        assert [layer.name for layer in scene.layers] == ["TOP"]
        assert len(scene.polygons) == 1
        assert scene.polygons[0].bounds == (0, 0, 10, 20)
        assert scene.polygons[0].holes == (rectangle(1, 2, 3, 4)[::-1],)
        assert primitive.polygon_data.reads == 1
        assert hole.polygon_data.reads == 1
        primitive.net.name = "CHANGED"
        assert scene.polygons[0].net == "GND"
        assert not scene_from_edb(edb, layers=[]).polygons

    def test_grpc_adapter_records_failed_geometry_and_rejects_bad_inputs(self):
        edb = _edb([_primitive(contour_error=ValueError("broken contour")), _primitive(2, type="text")])
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

    def test_extraction_progress_counts_filtered_and_void_primitives(self):
        events = []
        edb = _edb([_primitive(), _primitive(2, "BOTTOM"), _primitive(3, is_void=True)])
        scene = scene_from_edb(edb, layers="TOP", progress=lambda *event: events.append(event))
        assert len(scene.polygons) == 1
        assert ("Reading polygons", 3, 3) in events
        assert events[0] == ("Reading polygons", 0, 0)
        polygon_events = [event for event in events if event[0] == "Reading polygons"]
        assert events[: len(polygon_events)] == polygon_events
        # The layout has no padstack instances, so the pad stage reports no work.
        assert {event for event in events if event[0] != "Reading polygons"} == {("Reading pads and vias", 0, 0)}

    def test_progressive_extraction_prioritizes_visible_layer_and_preserves_layer_order(self):
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

    def test_adapter_preserves_path_fallback_circle_coverage_and_skip_diagnostics(self):
        path = _primitive(type="path", end_cap1="unsupported", end_cap2="round", center_line=None)
        circle = _primitive(2, type="circle", get_parameters=lambda: tuple(map(_value, (0.003, 0.004, 0.001))))
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
        assert scene.polygons[0].exterior == rectangle(0, 0, 10, 20)[::-1]
        assert scene.polygons[1].holes == (rectangle(1, 1, 2, 2)[::-1],)
        assert len(scene.pads) == 1
        assert scene.pads[0].center == (3, 4) and scene.pads[0].size == (2, 2)
        assert circle.polygon_data.reads == 0
        assert scene.diagnostics[0].startswith("Trace 1: inspection properties unavailable")
        assert scene.diagnostics[1].startswith("Path 1: using source boundary coverage")
        assert scene.diagnostics[2:4] == ("Skipped 1 negative primitive object(s).", "Skipped 2 text object(s).")

    def test_edb_view_layout_delegates_without_opening_a_session(self, monkeypatch):
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
            plot_outlines=True,
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
            plot_outlines=False,
        )
        assert launch.call_args.kwargs["plot_components"] is False
        assert launch.call_args.kwargs["annotate_component_names"] is False
        assert launch.call_args.kwargs["plot_components_on_both_side"] is False
        assert launch.call_args.kwargs["plot_outlines"] is False
        assert launch.call_args.kwargs["color_by_net"] is False

    def test_adapter_retains_analytic_paths_caps_and_sharp_joins(self):
        path = _primitive(
            type="path",
            width=_value(0.001),
            end_cap1="flat",
            end_cap2="extended",
            corner_style="sharp",
            center_line=SimpleNamespace(
                arc_data=[
                    _arc((0, 0), (0.005, 0)),
                    _arc((0.005, 0), (0.005, 0.005)),
                ]
            ),
        )
        curved = _primitive(
            2,
            type="path",
            width=_value(0.0005),
            end_cap1="round",
            end_cap2="round",
            corner_style="round",
            center_line=SimpleNamespace(
                arc_data=[
                    _arc((0.005, 0), (0, 0.005), (0, 0)),
                ]
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
        assert path.polygon_data.reads == 0
        assert curved.polygon_data.reads == 0

    def test_path_segments_reuse_source_metadata(self):
        reads = {"layer": 0, "net": 0}

        class CountedPath(SimpleNamespace):
            def __getattribute__(self, name):
                if name in reads:
                    reads[name] += 1
                return super().__getattribute__(name)

        path = CountedPath(
            **vars(
                _primitive(
                    type="path",
                    width=_value(0.001),
                    end_cap1="round",
                    end_cap2="round",
                    corner_style="round",
                    center_line=SimpleNamespace(
                        arc_data=[_arc((i * 0.001, 0), ((i + 1) * 0.001, 0)) for i in range(20)]
                    ),
                )
            )
        )
        scene = scene_from_edb(_edb([path]))
        assert len(scene.traces) == 20
        # One net read for the unassigned-net filter and one for its name, regardless of segment count.
        assert reads == {"layer": 1, "net": 2}

    def test_grpc_polygon_data_wraps_core_or_returns_none(self):
        from pyedb.grpc.database.primitive.primitive import Primitive

        class Source:
            @property
            def polygon_data(self):
                return self

        source = Source()
        primitive = Primitive(None, SimpleNamespace(cast=lambda: source))
        assert primitive.polygon_data.core is source
        primitive.core = SimpleNamespace(cast=lambda: SimpleNamespace())
        assert primitive.polygon_data is None

    def test_fast_path_contours_avoid_analytic_remote_properties(self):
        path = _primitive(type="path", has_voids=False)
        scene = scene_from_edb(_edb([path]), analytic_traces=False)
        assert not scene.traces
        assert len(scene.polygons) == 1
        assert scene.polygons[0].category == "trace"
        assert path.polygon_data.reads == 1

    def test_each_viewer_capture_reads_the_current_source_and_releases_it(self):
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

    def test_primitives_without_voids_do_not_enumerate_an_empty_remote_collection(self):
        class SolidPath(SimpleNamespace):
            @property
            def voids(self):
                raise AssertionError("No remote void collection is needed")

        values = vars(
            _primitive(
                type="path",
                has_voids=False,
                width=_value(0.001),
                end_cap1="round",
                end_cap2="round",
                corner_style="round",
                center_line=SimpleNamespace(arc_data=[_arc((0, 0), (0.001, 0))]),
            )
        )
        del values["voids"]
        scene = scene_from_edb(_edb([SolidPath(**values)]))
        assert len(scene.traces) == 1

    @pytest.mark.grpc
    def test_contour_reads_polygon_data_points(self):
        from pyedb.viewer.adapters.grpc import _contour

        points = [
            SimpleNamespace(is_arc=False, x=CoreValue(x), y=CoreValue(y)) for x, y in [(0, 0), (0.001, 0), (0, 0.001)]
        ]
        primitive = SimpleNamespace(polygon_data=SimpleNamespace(points=points))
        assert _contour(primitive, 8, 0.01) == ((0, 1), (1, 0), (0, 0))

    @pytest.mark.grpc
    @pytest.mark.parametrize(
        "kind, prop, expected",
        [
            ("PATH", "'Trace_A'", "Trace_A"),
            ("PATH", "", "line__42"),
            ("POLYGON", None, "poly__42"),
            ("RECTANGLE", "''", "rect__42"),
            ("CIRCLE", RuntimeError("no property"), "circle__42"),
        ],
    )
    def test_primitive_name_uses_aedt_name_with_default_fallback(self, kind, prop, expected):
        from pyedb.viewer.adapters.grpc import _primitive_name

        getter = Mock(side_effect=prop) if isinstance(prop, Exception) else Mock(return_value=prop)
        if prop is None:
            getter = Mock(side_effect=AttributeError("unset"))
        primitive = SimpleNamespace(
            get_product_property=getter, primitive_type=SimpleNamespace(name=kind), id=42, edb_uid=42
        )
        assert _primitive_name(primitive) == expected


class TestTessellation:
    @pytest.mark.parametrize("height", [0.0002, -0.0002])
    def test_grpc_contour_tessellation_evaluates_values_before_interpolating(self, monkeypatch, height):
        from ansys.edb.core.utility.value import Value as CoreValue

        from pyedb.grpc.database.primitive.primitive import Primitive
        from pyedb.misc.utilities import compute_arc_points

        points = [
            SimpleNamespace(is_arc=False, x=CoreValue(0.0), y=CoreValue(0.0)),
            SimpleNamespace(is_arc=True, arc_height=CoreValue(height)),
            SimpleNamespace(is_arc=False, x=CoreValue(0.001), y=CoreValue(0.0)),
        ]

        def interpolate(start, end, sagitta, count):
            assert all(type(float(value)) is float for value in (*start, *end, sagitta))
            return compute_arc_points(start, end, sagitta, count)

        monkeypatch.setattr("pyedb.grpc.database.primitive.primitive.compute_arc_points", interpolate)
        x, y = Primitive._get_points_for_plot(None, points, 32)
        expected_x, expected_y = compute_arc_points([0.0, 0.0], [0.001, 0.0], height, 32)
        assert x == pytest.approx([0.0, *expected_x, 0.001])
        assert y == pytest.approx([0.0, *expected_y, 0.0])

    @pytest.mark.parametrize("radius", [0.02, 0.2, 2.0, 20.0])
    @pytest.mark.parametrize("sweep", [0.01, math.pi / 2, math.pi, math.tau * 0.9])
    @pytest.mark.parametrize("direction", [-1, 1])
    def test_adaptive_chords_bound_error_for_radius_and_total_sweep(self, radius, sweep, direction):
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

    def test_adaptive_chords_grow_with_radius_and_angle_without_oversampling_flat_arcs(self):
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
    def test_adaptive_chord_error_validation(self, error):
        with pytest.raises(ValueError, match="chord_error"):
            scene_from_edb(_edb([]), chord_error=error)

    def test_centerline_length_uses_analytic_arc_not_contour_perimeter(self):
        h = 0.001 * (1 - math.sqrt(0.5))
        assert centerline_length(_centerline([(0.001, 0), h, (0, 0.001), (0, 0.003)])) == pytest.approx(math.pi / 2 + 2)
        assert centerline_length(_centerline([(0.001, 0), -h, (0, 0.001), (0, 0.003)])) == pytest.approx(
            math.pi / 2 + 2
        )
        assert centerline_length(_centerline([(0, 0), (0.003, 0.004)])) == pytest.approx(5)
        assert centerline_length(_centerline([(0, 0), (0.003, 0)], closed=True)) == pytest.approx(6)

    def test_trace_dimensions_extract_width_and_analytic_centerline(self):
        from types import SimpleNamespace

        from ansys.edb.core.utility.value import Value as CoreValue

        from pyedb.viewer.adapters import grpc_stream

        path = SimpleNamespace(width=CoreValue(0.00025), center_line=_centerline([(0, 0), (0.003, 0.004)]))
        width, length = grpc_stream.trace_dimensions(path)
        assert width == pytest.approx(0.25)
        assert length == pytest.approx(5.0)

    @pytest.mark.grpc
    @pytest.mark.parametrize("height", [-0.0002, 0.0002])
    @pytest.mark.parametrize("error", [None, 0.01])
    def test_core_point_contours_match_primitive_plot_points(self, height, error):
        points = [PointData((0, 0)), PointData(height), PointData((0.001, 0)), PointData((0.001, 0.001))]
        points.append(PointData((0, 0.001)))
        x, y = Primitive._get_points_for_plot(None, points, 8, chord_error=None if error is None else error / 1000)
        x, y = GeometryOperators.orient_polygon(x, y, clockwise=True)
        reference = tuple((a * 1000, b * 1000) for a, b in zip(x, y))
        assert grpc_stream.contour_from_points(points, 8, error) == reference

    @pytest.mark.grpc
    @pytest.mark.parametrize("height", [-0.0002, 0.0002])
    def test_core_point_arcs_stay_within_their_chord_bounds(self, height):
        contour = grpc_stream.contour_from_points(
            [PointData((0, 0)), PointData(height), PointData((0.001, 0))], 8, 0.01
        )
        assert len(contour) > 3
        assert all(abs(value) <= 1 for point in contour for value in point)


class TestPadstacks:
    def test_adapter_extracts_per_layer_via_pads_offset_rotation_drill_and_filters(self):
        via = _via()
        edb = _edb([])
        edb.layout.padstack_instances = [via]
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

    def test_padstack_span_uses_core_layer_range_without_reenumerating_signal_layers(self):
        via = _via()
        via.get_layer_range = Mock(return_value=(SimpleNamespace(name="BOTTOM"), SimpleNamespace(name="TOP")))
        edb = _edb([])
        edb.layout.padstack_instances = [via]
        scene = scene_from_edb(edb)
        assert [pad.layer for pad in scene.pads] == ["TOP", "BOTTOM"]
        via.get_layer_range.assert_called_once_with()
        assert len(scene_from_edb(edb, layers="BOTTOM").pads) == 1

    def test_via_default_pad_blind_span_hole_override_and_missing_geometry_diagnostics(self):
        via = _via(
            layer_range_names=["TOP"],
            get_hole_overrides=lambda: (True, _value(0.0004)),
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
        edb.layout.padstack_instances = [via, bad]
        scene = scene_from_edb(edb)
        assert len(scene.pads) == 1
        assert scene.pads[0].layer == "TOP"
        assert scene.pads[0].hole_radius == 0.2
        assert any("Padstack 10, layer TOP: Unsupported" in note for note in scene.diagnostics)

    def test_via_retains_drill_on_layers_without_copper_pads_or_other_net_geometry(self):
        via = _via(layer_range_names=["TOP", "INNER", "BOTTOM"])
        edb = _edb([])
        edb.stackup.layers = {
            "TOP": SimpleNamespace(color=(255, 0, 0)),
            "INNER": SimpleNamespace(color=(0, 255, 0)),
            "BOTTOM": SimpleNamespace(color=(0, 0, 255)),
        }
        edb.stackup.signal_layers = edb.stackup.layers
        edb.layout.padstack_instances = [via]
        scene = scene_from_edb(edb, layers="INNER", nets="GND")
        assert not scene.polygons and not scene.traces
        assert len(scene.pads) == 1
        pad = scene.pads[0]
        assert pad.layer == "INNER" and pad.net == "GND"
        assert pad.size == (1, 1) and pad.hole_radius == 0.5
        packet = prepare_scene(scene).instances[0]
        assert packet[25] == -1  # No fabricated copper annulus on a nonfunctional layer.
        assert packet[29] == 0.5  # The physical bore remains independently renderable.

    def test_explicit_padstack_layer_mapping_uses_definition_layer_ids(self):
        via = _via()
        via.definition.layer_ids = [1, 2]
        via.layer_map = SimpleNamespace(
            is_null=False,
            msg=SimpleNamespace(SerializeToString=lambda: b"map"),
            get_mapping_backward=lambda layer_id: [2] if layer_id == 100 else [1],
        )
        edb = _edb([])
        edb.stackup.layers["TOP"].id = 100
        edb.stackup.layers["BOTTOM"].id = 101
        edb.layout.padstack_instances = [via]
        scene = scene_from_edb(edb)
        assert scene.pads[0].layer == "TOP"
        assert scene.pads[0].shape == "rectangle"
        assert scene.pads[1].shape == "circle"
        assert scene.pads[1].center == pytest.approx((10, 21))

    @pytest.mark.parametrize("hole_diameter", [0, 0.001])
    def test_polygon_pad_templates_are_cached_and_preserve_placement_drills_and_pin_ownership(self, hole_diameter):
        polygon = _core_polygon(
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
            _via(
                i,
                definition=definition,
                layer_range_names=["TOP"],
                rotation=0,
                is_pin=True,
                name=str(i),
                component=owner,
            )
            for i in (9, 10)
        ]
        edb = _edb([])
        edb.layout.padstack_instances = pins
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

    def test_invalid_polygon_pad_retains_drill_and_continues_to_next_layer(self):
        via = _via()
        via.definition.pad_by_layer["TOP"] = _pad(
            "polygon",
            polygon_data=_core_polygon(
                points=[SimpleNamespace(is_arc=False, x=0.0, y=0.0), SimpleNamespace(is_arc=False, x=1.0, y=1.0)],
                without_arcs=lambda **kwargs: SimpleNamespace(points=[_point(0, 0), _point(1, 1)]),
            ),
        )
        edb = _edb([])
        edb.layout.padstack_instances = [via]
        scene = scene_from_edb(edb)
        assert not scene.polygons
        assert [pad.layer for pad in scene.pads] == ["TOP", "BOTTOM"]
        assert scene.pads[0].size == (1, 1) and scene.pads[0].hole_radius == 0.5
        assert scene.pads[1].shape == "rectangle"
        assert "Padstack 9, layer TOP: A contour requires at least three distinct points." in scene.diagnostics

    def test_nsided_polygon_points_returns_a_regular_polygon(self):
        from pyedb.viewer.adapters.grpc import _nsided_polygon_points

        ring = _nsided_polygon_points(size=2.0, num_sides=6)
        assert len(ring) == 6
        for x, y in ring:
            assert math.hypot(x, y) == pytest.approx(1.0)
        # Vertices spaced evenly by a full turn over the side count.
        angles = [math.atan2(y, x) for x, y in ring]
        assert angles[0] == pytest.approx(0.0)
        assert (angles[1] - angles[0]) % math.tau == pytest.approx(math.tau / 6)
        # Fewer than 3 requested sides still yields a valid polygon.
        assert len(_nsided_polygon_points(size=1.0, num_sides=1)) == 3

    def test_thermal_relief_outline_builds_round_and_square_boundaries(self):
        from pyedb.viewer.adapters.grpc import _thermal_relief_outline

        round_ring = _thermal_relief_outline(True, inner=1.0, isolation_gap=0.5, arc_segments=16)
        assert len(round_ring) == 16
        for x, y in round_ring:
            assert math.hypot(x, y) == pytest.approx(1.0)  # inner / 2 + isolation_gap

        square_ring = _thermal_relief_outline(False, inner=1.0, isolation_gap=0.5, arc_segments=16)
        assert square_ring == ((1.0, 1.0), (-1.0, 1.0), (-1.0, -1.0), (1.0, -1.0))

    def test_pad_template_builds_nsided_polygon_ring_without_scaling_side_count(self):
        from pyedb.viewer.adapters.grpc import _pad_template

        pad = _pad("nsided_polygon", parameters=(0.002, 6))
        shape, ring, offset, rotation = _pad_template(pad, arc_segments=12)
        assert shape == "polygon"
        assert len(ring) == 6  # Not 6000: num_sides must not be unit-scaled like a length.
        for x, y in ring:
            assert math.hypot(x, y) == pytest.approx(1.0)  # size (0.002 -> 2 after *1000) / 2
        assert offset == (0, 0)
        assert rotation == 0

    @pytest.mark.parametrize(
        "shape,round_outer",
        [("round45", True), ("round90", True), ("square45", False), ("square90", False)],
    )
    def test_pad_template_builds_thermal_relief_ring_for_all_variants(self, shape, round_outer):
        from pyedb.viewer.adapters.grpc import _pad_template

        pad = _pad(shape, parameters=(0.001, 0.0002, 0.0003))
        result = _pad_template(pad, arc_segments=8)
        assert result[0] == "polygon"
        ring = result[1]
        expected_radius = (0.001 * 1000) / 2 + 0.0003 * 1000
        if round_outer:
            assert len(ring) == 8
            for x, y in ring:
                assert math.hypot(x, y) == pytest.approx(expected_radius)
        else:
            assert len(ring) == 4
            for x, y in ring:
                assert abs(x) == pytest.approx(expected_radius)
                assert abs(y) == pytest.approx(expected_radius)

    def test_pad_template_treats_invalid_geometry_like_no_shape(self):
        from pyedb.viewer.adapters.grpc import _pad_template

        assert _pad_template(_pad("geometry"), arc_segments=12) is None

    def test_raw_pad_properties_names_nsided_polygon_without_colliding_with_polygon(self):
        from ansys.edb.core.definition.padstack_def_data import PadGeometryType

        from pyedb.viewer.adapters.grpc import _pad_param

        data = SimpleNamespace(
            get_pad_parameters=Mock(
                return_value=(
                    PadGeometryType.PADGEOMTYPE_NSIDED_POLYGON,
                    [_value(0.002), _value(6)],
                    _value(0.0),
                    _value(0.0),
                    _value(0.0),
                )
            )
        )
        pad = _pad_param(data, "TOP")
        assert pad.shape == "nsided_polygon"
        assert pad.polygon_data is None
        assert pad.parameters_values == [0.002, 6]

    @pytest.mark.parametrize(
        "geom_type_name,hole_params,expected_diameter",
        [
            ("PADGEOMTYPE_CIRCLE", [0.002], 0.002),
            ("PADGEOMTYPE_SQUARE", [0.003], 0.003),
            ("PADGEOMTYPE_RECTANGLE", [0.001, 0.004], 0.004),
            ("PADGEOMTYPE_OVAL", [0.004, 0.001, 0.0005], 0.004),
            ("PADGEOMTYPE_BULLET", [0.001, 0.0025, 0.0005], 0.0025),
            ("PADGEOMTYPE_NSIDED_POLYGON", [0.0015, 6], 0.0015),
            ("PADGEOMTYPE_ROUND45", [0.0012, 0.0002, 0.0003], 0.0012),
            ("PADGEOMTYPE_ROUND90", [0.0012, 0.0002, 0.0003], 0.0012),
            ("PADGEOMTYPE_SQUARE45", [0.0012, 0.0002, 0.0003], 0.0012),
            ("PADGEOMTYPE_SQUARE90", [0.0012, 0.0002, 0.0003], 0.0012),
        ],
    )
    def test_padstack_definition_computes_hole_diameter_per_geometry_type(
        self, geom_type_name, hole_params, expected_diameter
    ):
        from ansys.edb.core.definition.padstack_def_data import PadGeometryType

        from pyedb.viewer.adapters.grpc import _padstack_definition

        geom_type = getattr(PadGeometryType, geom_type_name)
        data = SimpleNamespace(
            get_pad_parameters=Mock(side_effect=_hole_only(geom_type, hole_params)),
            layer_names=["TOP"],
        )
        instance = SimpleNamespace(padstack_def=SimpleNamespace(name="via", data=data))
        diagnostics = []
        _data, _by_layer, hole_radius_scaled, _hole_offset = _padstack_definition(instance, {}, diagnostics)
        # _padstack_definition stores diameter * 500 (i.e. radius * 1000 scale).
        assert hole_radius_scaled == pytest.approx(expected_diameter * 500)
        assert not diagnostics

    @pytest.mark.parametrize("geom_type_name", ["PADGEOMTYPE_NO_GEOMETRY", "PADGEOMTYPE_INVALID_GEOMETRY"])
    def test_padstack_definition_no_hole_for_missing_or_invalid_geometry(self, geom_type_name):
        from ansys.edb.core.definition.padstack_def_data import PadGeometryType

        from pyedb.viewer.adapters.grpc import _padstack_definition

        geom_type = getattr(PadGeometryType, geom_type_name)
        data = SimpleNamespace(
            get_pad_parameters=Mock(side_effect=_hole_only(geom_type, [])),
            layer_names=["TOP"],
        )
        instance = SimpleNamespace(padstack_def=SimpleNamespace(name="via", data=data))
        diagnostics = []
        _data, _by_layer, hole_radius_scaled, _hole_offset = _padstack_definition(instance, {}, diagnostics)
        assert hole_radius_scaled == 0
        assert not diagnostics

    def test_padstack_definition_flags_thermal_relief_approximation(self):
        from ansys.edb.core.definition.padstack_def_data import PadGeometryType, PadType

        from pyedb.viewer.adapters.grpc import _padstack_definition

        def get_pad_parameters(layer_name, pad_type):
            if pad_type != PadType.REGULAR_PAD:
                return ()
            return (
                PadGeometryType.PADGEOMTYPE_ROUND90,
                [_value(0.0012), _value(0.0002), _value(0.0003)],
                _value(0.0),
                _value(0.0),
                _value(0.0),
            )

        data = SimpleNamespace(
            get_pad_parameters=Mock(side_effect=get_pad_parameters),
            layer_names=["TOP"],
        )
        instance = SimpleNamespace(padstack_def=SimpleNamespace(name="via", data=data))
        diagnostics = []
        _padstack_definition(instance, {}, diagnostics)
        assert any("thermal-relief spokes are not rendered" in message for message in diagnostics)

    def test_noncircular_hole_is_cut_out_with_its_true_shape(self):
        from pyedb.viewer.adapters.grpc import _append_padstack_geometry, _hole_profile

        def hole(shape):
            return SimpleNamespace(shape=shape, parameters_values=[0.004, 0.002, 0.0005], rotation=0.0)

        profile = _hole_profile(hole("rectangle"))
        assert profile == pytest.approx(("rectangle", 4.0, 2.0, 0.0, 0.0))
        assert _hole_profile(hole("circle")) is None
        placement = (lambda p: p, lambda v: v, 1.0)
        pads, polygons = [], []
        _append_padstack_geometry(
            SimpleNamespace(edb_uid=1),
            "TOP",
            "GND",
            ("circle", (10.0,), (0.0, 0.0), 0.0),
            placement,
            2.0,
            (0.0, 0.0),
            16,
            {},
            (pads, polygons),
            hole_profile=profile,
        )
        assert not pads and len(polygons) == 1
        xs, ys = zip(*polygons[0].holes[0])
        assert (max(xs), max(ys)) == pytest.approx((2.0, 1.0))
        # Oval holes keep their rounded ends: more than four vertices, extent still the full size.
        oval = _hole_profile(hole("oval"))
        pads, polygons = [], []
        _append_padstack_geometry(
            SimpleNamespace(edb_uid=1),
            "TOP",
            "GND",
            ("rectangle", (10.0, 8.0), (0.0, 0.0), 0.0),
            placement,
            2.0,
            (0.0, 0.0),
            16,
            {},
            (pads, polygons),
            hole_profile=oval,
        )
        assert len(polygons[0].holes[0]) > 4

    @pytest.mark.grpc
    def test_pad_metadata_uses_core_layer_range_and_pose(self):
        from pyedb.viewer.adapters.grpc import _padstack_layers, _placement

        layer_range = Mock(return_value=(SimpleNamespace(name="INNER"), SimpleNamespace(name="BACK")))
        pose = Mock(return_value=(CoreValue(0.001), CoreValue(0.002), CoreValue(0)))
        instance = SimpleNamespace(get_layer_range=layer_range, get_position_and_rotation=pose, component=None)
        layers = ("FRONT", "INNER", "BACK")
        assert _padstack_layers(instance, {"INNER", "BACK"}, layers, False) == ["INNER", "BACK"]
        assert _placement(instance, {})[0]((0, 0)) == (1, 2)
        layer_range.assert_called_once_with()
        pose.assert_called_once_with()


class TestComponents:
    def test_component_pad_offsets_follow_mirrored_component_basis(self):
        # Core pin positions are component-local; this transform mirrors about the Y axis.
        via = _via(rotation=0, position=(-0.010, 0.020))

        def transform_point(point):
            return _point(-point.x.value, point.y.value)

        transform = SimpleNamespace(is_null=False, transform_point=transform_point)
        via.component = SimpleNamespace(id=42, core=SimpleNamespace(transform=transform))
        edb = _edb([])
        edb.layout.padstack_instances = [via]
        scene = scene_from_edb(edb)
        assert len(scene.pads) == 2
        assert scene.pads[0].center == (9, 20)
        assert scene.pads[0].hole_center == (10, 20)
        assert scene.pads[1].rotation == pytest.approx(math.pi)

    def test_fast_component_envelopes_reuse_all_owned_pads_even_when_not_layout_pins(self):
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
        edb.layout.padstack_instances = [via]
        edb.components = SimpleNamespace(instances={"U1": component})
        scene = scene_from_edb(edb)
        assert len(scene.components) == 1
        assert scene.components[0].bounds == pytest.approx((9, 18, 11, 22))
        assert scene.components[0].nets == ("GND",)

    def test_fast_component_envelopes_estimate_copper_free_footprints_without_layout_instance(self):
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
        edb.layout.padstack_instances = [first, second]
        edb.components = SimpleNamespace(instances={"U1": component})
        scene = scene_from_edb(edb)
        assert len(scene.components) == 1
        assert scene.components[0].bounds == pytest.approx((9.8, 19.8, 12.2, 20.2))
        assert any("estimated" in message for message in scene.diagnostics)

    def test_pad_positions_reuse_one_component_transform_and_one_pose_read(self):
        from pyedb.viewer.adapters.grpc import _placement

        transform = SimpleNamespace(
            is_null=False,
            transform_point=Mock(side_effect=lambda point: _point(0.01 - point.y.value, 0.02 + point.x.value)),
        )
        component = SimpleNamespace(edb_uid=7, transform=transform)
        first = SimpleNamespace(get_position_and_rotation=Mock(return_value=tuple(map(_value, (0.001, 0.002, 0)))))
        second = SimpleNamespace(get_position_and_rotation=Mock(return_value=tuple(map(_value, (0.003, 0.004, 0)))))
        cache = {}
        world, vector, scale = _placement(first, cache, component)
        assert world((0, 0)) == pytest.approx((8, 21))
        assert vector((1, 0)) == pytest.approx((0, 1))
        assert scale == pytest.approx(1)
        assert _placement(second, cache, component)[0]((0, 0)) == pytest.approx((6, 23))
        assert transform.transform_point.call_count == 3
        first.get_position_and_rotation.assert_called_once()
        second.get_position_and_rotation.assert_called_once()

    def test_exact_component_envelopes_remain_available(self):
        component = _component(core=SimpleNamespace(transform=SimpleNamespace(is_null=True)))
        via = _via(component=component)
        edb = _edb([])
        edb.layout.padstack_instances = [via]
        edb.components = SimpleNamespace(instances={"U1": component})
        exact = scene_from_edb(edb, exact_component_bounds=True)
        assert exact.components[0].bounds == (1, 2, 4, 6)

    def test_components_match_plot_envelopes_and_capture_filters_without_double_rotation(self):
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

    def test_component_only_scene_bounds_resident_packet_and_compound_network_visibility(self):
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

    def test_component_pin_capture_keeps_owner_name_side_and_physical_pad_layer(self):
        owner = _component("U1", "TOP", id=42, core=SimpleNamespace(transform=SimpleNamespace(is_null=True)))
        pin = _via(9, is_pin=True, name="A1", component=owner)
        edb = _edb([])
        edb.layout.padstack_instances = [pin]
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

    def test_pin_annotation_failure_does_not_drop_its_physical_copper(self):
        owner = SimpleNamespace(id=42, core=SimpleNamespace(transform=SimpleNamespace(is_null=True)))
        pin = _via(9, is_pin=True, name="1", component=owner)
        edb = _edb([])
        edb.layout.padstack_instances = [pin]
        scene = scene_from_edb(edb)
        assert len(scene.pads) == 2
        assert all(p.component is None for p in scene.pads)
        assert any("component pin metadata unavailable" in note for note in scene.diagnostics)

    def test_custom_conductor_names_include_back_components_and_single_layer_associations(self):
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
            layer_range_names=["metal_1"],
            definition=SimpleNamespace(
                pad_by_layer={"Default": _pad()}, hole_diameter=0, hole_offset_x=0, hole_offset_y=0
            ),
        )
        edb.layout.padstack_instances = [pin]
        scene = scene_from_edb(edb)
        assert [layer.name for layer in scene.layers] == ["metal_1"]
        assert scene.components[0].side == "bottom"
        assert scene.pads[0].component_side == "bottom"
        assert scene.pads[0].layer == "metal_1"
        edb.components.instances = {}
        edb.layout.padstack_instances = []
        assert not scene_from_edb(edb).components

    @pytest.mark.grpc
    def test_component_basis_uses_one_polygon_call_and_preserves_point_fallback(self, monkeypatch):
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

    @pytest.mark.grpc
    def test_component_basis_keeps_legacy_path_when_batch_rpc_is_unsupported(self, monkeypatch):
        class Unsupported(grpc_stream.grpc.RpcError):
            def code(self):
                return grpc_stream.grpc.StatusCode.UNIMPLEMENTED

        transform = object.__new__(grpc_stream.CoreTransform)
        monkeypatch.setattr(grpc_stream.CoreTransform, "transform_polygon", Mock(side_effect=Unsupported()))
        assert grpc_stream.transform_basis_points(transform) is None

    @pytest.mark.grpc
    def test_pad_component_reuses_only_current_capture_components(self):
        from pyedb.viewer.adapters.grpc import _padstack_component

        group = SimpleNamespace(is_null=False, edb_uid=101)
        component = object()
        assert _padstack_component(group, {101: component}) is component
        assert _padstack_component(group, {102: component}) is None
        assert _padstack_component(group, None) is None
        group.is_null = True
        assert _padstack_component(group, {}) is False
        assert _padstack_component(None, {}) is None


class TestMeshPreparation:
    def test_concave_exterior_and_holes_keep_independent_coverage(self):
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

    def test_preparation_progress_preserves_gpu_buffers_and_completes_each_stage(self):
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

    def test_sdf_packets_preserve_positions_and_batch_by_layer_without_triangulation(self, monkeypatch):
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

    def test_net_colors_use_pyedb_palette_and_stay_stable_when_filtering(self):
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

    def test_progressive_preparation_reuses_unchanged_mesh_but_adds_pads(self):
        polygon = ScenePolygon(1, "TOP", "GND", rectangle())
        preview = LayoutScene((SceneLayer("TOP", (1, 0, 0, 1)),), (polygon,), net_names=("GND",))
        complete = LayoutScene(
            preview.layers,
            preview.polygons,
            pads=(ScenePad(2, "TOP", "GND", (5, 5), (1, 1)),),
            net_names=preview.net_names,
        )
        mesh = prepare_scene(preview)
        prepared = prepare_scene(complete, polygon_mesh=(preview, mesh))
        assert prepared.vertices is mesh.vertices
        assert prepared.indices is mesh.indices
        assert prepared.vertex_nets is mesh.vertex_nets
        assert len(prepared.instances) == 1

    def test_progressive_preparation_appends_new_polygons_with_correct_indices_and_network_ids(self):
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

    def test_unassigned_sdf_geometry_retains_zero_net_material(self):
        scene = LayoutScene(
            (SceneLayer("TOP", (1, 0, 0, 1)),), (), traces=(SceneTrace(1, "TOP", "", (0, 0), (1, 0), 1),)
        )
        prepared = prepare_scene(scene)
        assert prepared.nets == (None,)
        assert prepared.instances[0, 27] == 0

    def test_pin_packets_reuse_copper_geometry_without_extra_border_instances(self):
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

    @pytest.mark.grpc
    def test_bulk_pad_packets_match_scalar_precision_shapes_drills_and_networks(self):
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


class TestPicking:
    def test_interaction_colors_are_reserved_and_visible_on_white(self):
        from pyedb.viewer.colors import HIGHLIGHT_KEYLINE_COLOR, HOVER_COLOR, NET_COLORS, SELECTION_COLOR

        assert HOVER_COLOR != SELECTION_COLOR
        for color in (HOVER_COLOR, SELECTION_COLOR, HIGHLIGHT_KEYLINE_COLOR):
            assert color not in NET_COLORS
            linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in color]
            luminance = sum(v * weight for v, weight in zip(linear, (0.2126, 0.7152, 0.0722)))
            assert 1.05 / (luminance + 0.05) >= 3

    @pytest.mark.parametrize(
        "point, kind, object_id", [((0, 2), "trace", 3), ((3, -2), "via", 4), ((-3, -2), "pad", 5), ((0, 4), "zone", 1)]
    )
    def test_picks_source_objects_and_not_bounding_boxes(self, point, kind, object_id):
        index = PickIndex(picking_scene())
        hit = index.pick(point, 100, {"TOP"})
        assert hit.key == (kind, object_id)
        assert hit.layer == "TOP"
        assert index.pick(point, 100, {"TOP"}, net="NO_SUCH_NET") is None
        assert index.pick(point, 100, {"TOP"}, opacity=0) is None

    def test_zone_voids_visibility_and_physical_via_span(self):
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

    def test_exact_hits_win_over_nearby_objects_and_layer_order_reverses(self):
        scene = LayoutScene(
            (SceneLayer("TOP", (1, 0, 0, 1)), SceneLayer("BOTTOM", (0, 0, 1, 1))),
            (),
            traces=(SceneTrace(1, "TOP", "A", (0, 0), (2, 0), 0.2), SceneTrace(2, "BOTTOM", "B", (0, 0), (2, 0), 0.2)),
            pads=(ScenePad(3, "TOP", "C", (1, 0.4), (0.2, 0.2)),),
        )
        index = PickIndex(scene)
        assert index.pick((1, 0), 10, {"TOP", "BOTTOM"}).key == ("trace", 1)
        assert index.pick((1, 0), 10, {"TOP", "BOTTOM"}, mirror=True).key == ("trace", 2)

    def test_rotated_pad_and_analytic_arc_do_not_pick_their_empty_bounding_box(self):
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

    def test_spatial_index_limits_candidates_and_shares_via_layer_entries(self):
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

    def test_flat_and_extended_trace_caps_have_distinct_exact_hit_regions(self):
        for cap, expected in (("flat", False), ("extended", True), ("round", True)):
            scene = LayoutScene(
                (SceneLayer("TOP", (1, 0, 0, 1)),),
                (),
                traces=(SceneTrace(1, "TOP", "N", (0, 0), (2, 0), 1, end_caps=(cap, cap)),),
            )
            assert bool(PickIndex(scene).pick((-0.2, 0), 1000, {"TOP"}, pixels=0)) == expected

    def test_arc_flat_cap_and_metadata_fallback_keep_centerline_semantics(self):
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


class TestInspector:
    def test_inspector_reports_trace_and_pin_properties_from_source(self):
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

    def test_nonround_via_reports_actual_pad_size_instead_of_invented_diameter(self):
        scene = LayoutScene(
            (SceneLayer("TOP", (1, 0, 0, 1)),),
            (),
            pads=(ScenePad(1, "TOP", "N", (0, 0), (2, 1), "rectangle", hole_radius=0.2),),
        )
        rows = dict(inspector_rows(PickIndex(scene).pick((0, 0), 100, {"TOP"})))
        assert rows["Via pad size"] == "2.0000 × 1.0000 mm"
        assert "Via diameter" not in rows
        assert rows["Drill diameter"] == "0.4000 mm"


class TestWindowApi:
    def test_select_object_emits_and_exposes_detached_identity(self, window):
        events = []
        window.object_selected.connect(events.append)
        picked = window.select_object(50, kind="trace")
        assert events == [picked]
        assert picked.kind == "trace" and picked.object_id == 50 and picked.net == "SIGNAL"
        assert window.selected_object == picked
        assert window.select_object(70).kind == "via"
        assert [e.object_id for e in events] == [50, 70]

    def test_select_object_is_idempotent_and_clear_emits_once(self, window):
        selected, cleared = [], []
        window.object_selected.connect(selected.append)
        window.selection_cleared.connect(lambda: cleared.append(True))
        window.select_object(50)
        window.select_object(50)
        assert len(selected) == 1
        window.clear_selection()
        window.clear_selection()
        assert cleared == [True]
        assert window.selected_object is None

    def test_select_object_errors(self, window):
        with pytest.raises(ValueError, match="Unknown object"):
            window.select_object(999999)
        with pytest.raises(ValueError, match="Unknown object"):
            window.select_object(50, kind="via")
        with pytest.raises(ValueError, match="no geometry on layer"):
            window.select_object(50, layer="missing")
        assert window.selected_object is None

    def test_select_net_filters_and_reports_changes(self, window):
        changes = []
        window.net_changed.connect(changes.append)
        window.select_net("GND")
        assert window.selected_net == "GND" and changes == ["GND"]
        window.select_net("GND")
        assert changes == ["GND"]
        window.select_net(None)
        assert window.selected_net is None and changes == ["GND", None]
        with pytest.raises(ValueError, match="Unknown net"):
            window.select_net("missing")

    def test_set_visible_layers_updates_panel_and_reports_once(self, window):
        names = [layer.name for layer in window.canvas.scene.layers]
        changes = []
        window.visible_layers_changed.connect(changes.append)
        window.set_visible_layers(names)
        assert window.visible_layers == tuple(names)
        window.set_visible_layers(names[-1])
        assert window.visible_layers == (names[-1],)
        checked = [window.layer_list.item(i).checkState().name for i in range(window.layer_list.count())]
        assert checked.count("Checked") == 1
        assert changes[-1] == (names[-1],)
        count = len(changes)
        window.set_visible_layers([names[-1]])
        assert len(changes) == count
        with pytest.raises(ValueError, match="Unknown layers"):
            window.set_visible_layers(["missing"])
        assert window.visible_layers == (names[-1],)

    def test_user_layer_toggle_reports_change(self, window):
        changes = []
        window.visible_layers_changed.connect(changes.append)
        window.set_visible_layers([])
        item = window.layer_list.item(0)
        item.setCheckState(item.checkState().Checked)
        assert changes[-1] == (item.text(),)

    def test_zoom_helpers_move_camera(self, window):
        window.canvas.resize(800, 600)
        window.fit_view()
        fitted = window.canvas.camera.scale
        window.zoom_to_object(50, "trace")
        assert window.canvas.camera.scale > fitted
        window.zoom_to_net("GND")
        assert window.canvas.camera.scale > 0
        with pytest.raises(ValueError, match="Unknown net"):
            window.zoom_to_net("missing")
        with pytest.raises(ValueError, match="Unknown object"):
            window.zoom_to_object(999999)

    def test_selection_before_display_is_rejected(self):
        pytest.importorskip("PySide6")
        from PySide6.QtWidgets import QApplication

        from pyedb.viewer.demo import demo_scene
        from pyedb.viewer.qt.canvas import LayoutView

        QApplication.instance() or QApplication([])
        view = LayoutView(demo_scene())
        with pytest.raises(RuntimeError, match="still loading"):
            view.select_object(50)


class TestCliAndTheme:
    def test_cli_defaults_to_network_colors_and_can_request_layer_colors(self, monkeypatch):
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

    def test_workspace_theme_has_readable_text_and_interaction_contrast(self):
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
