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

"""Opt-in real OpenGL pixel tests: set PYEDB_VIEWER_GL_TESTS=1 on a desktop."""

import os

import pytest

pytestmark = [
    pytest.mark.integration,
    pytest.mark.no_licence,
    pytest.mark.skipif(os.environ.get("PYEDB_VIEWER_GL_TESTS") != "1", reason="Requires an OpenGL 3.3 desktop"),
]


def test_on_demand_layers_queue_retry_and_close_without_reuploading_ready_buffers():
    import threading
    import time

    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication

    from pyedb.viewer import LayoutScene, SceneLayer, ScenePolygon
    from pyedb.viewer.qt.app import show_scene

    app = QApplication.instance() or QApplication([])
    layers = tuple(SceneLayer(name, (1, 0.5, 0, 1)) for name in ("TOP", "BOTTOM", "INNER", "LAST"))
    entered, finish = threading.Event(), threading.Event()

    class Source:
        def __init__(self):
            self.calls = []
            self.released = False
            self.fail_inner = True

        def load_layer(self, name=None, *, progress=None, preview=None):
            assert threading.current_thread() is not threading.main_thread()
            name = name or "TOP"
            self.calls.append(name)
            progress("Reading polygons", 0, 0)
            if name in {"BOTTOM", "LAST"}:
                entered.set()
                assert finish.wait(5), "The GUI stopped processing events"
            if name == "INNER" and self.fail_inner:
                self.fail_inner = False
                raise RuntimeError("Read failed")
            polygon = ScenePolygon(len(self.calls), name, "GND", ((0, 0), (1, 0), (1, 1), (0, 1)))
            return name, LayoutScene(layers, (polygon,), net_names=("GND", "HIDDEN_NET"))

        def release_source(self):
            self.released = True

    def until(predicate):
        deadline = time.monotonic() + 6
        while not predicate() and time.monotonic() < deadline:
            QTest.qWait(10)
        assert predicate()

    source = Source()
    window = show_scene(layer_source=source, block=False)
    try:
        canvas = window.canvas
        canvas.grabFramebuffer()
        assert source.calls == ["TOP"]
        assert "HIDDEN_NET" in window.network_panel.names
        top_renderer = canvas.renderer.layer_renderers["TOP"]
        top_buffer = top_renderer.vbo
        top_uploads = top_renderer.upload_count
        canvas.camera.pan(12, 8)
        camera = canvas.camera.center_x, canvas.camera.center_y, canvas.camera.scale
        window.layer_list.item(1).setCheckState(Qt.CheckState.Checked)
        until(entered.is_set)
        window._request_layer("BOTTOM")
        window.layer_list.item(2).setCheckState(Qt.CheckState.Checked)
        window.layer_list.item(2).setCheckState(Qt.CheckState.Unchecked)
        assert window.canvas.loading.isVisible()
        assert not source.released
        finish.set()
        until(lambda: window.layer_states["BOTTOM"] == "ready" and not window._capturing)
        canvas.grabFramebuffer()
        assert source.calls == ["TOP", "BOTTOM"]
        assert window.layer_states["INNER"] == "unloaded"
        assert (canvas.camera.center_x, canvas.camera.center_y, canvas.camera.scale) == camera
        assert top_renderer.vbo == top_buffer and top_renderer.upload_count == top_uploads
        window.layer_list.item(1).setCheckState(Qt.CheckState.Unchecked)
        window.layer_list.item(1).setCheckState(Qt.CheckState.Checked)
        assert source.calls == ["TOP", "BOTTOM"]
        window.layer_list.item(2).setCheckState(Qt.CheckState.Checked)
        until(lambda: window.layer_states["INNER"] == "failed")
        assert canvas.error is None and not canvas.loading.isVisible()
        window.layer_list.item(2).setCheckState(Qt.CheckState.Unchecked)
        window.layer_list.item(2).setCheckState(Qt.CheckState.Checked)
        until(lambda: window.layer_states["INNER"] == "ready")
        entered.clear()
        finish.clear()
        window.layer_list.item(3).setCheckState(Qt.CheckState.Checked)
        until(entered.is_set)
        window.close()
        assert not window.isVisible() and not source.released
        finish.set()
        until(lambda: source.released)
        assert not window._layer_queue
    finally:
        finish.set()
        window.close()
        app.processEvents()


def test_incremental_layer_buffers_match_complete_scene_pixels():
    from dataclasses import replace

    import numpy as np
    from PySide6.QtGui import QImage
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication

    from pyedb.viewer import LayoutScene, SceneComponent, SceneLayer, ScenePad, ScenePolygon
    from pyedb.viewer.mesh import prepare_scene
    from pyedb.viewer.qt.canvas import LayoutView

    app = QApplication.instance() or QApplication([])
    layers = (SceneLayer("TOP", (1, 0, 0, 1)), SceneLayer("BOTTOM", (0, 0, 1, 1)))
    ring = ((-2, -2), (2, -2), (2, 2), (-2, 2))
    hole = ((-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5))
    polygons = tuple(ScenePolygon(i, layer.name, f"N{i}", ring, (hole,)) for i, layer in enumerate(layers))
    pads = tuple(ScenePad(10, layer.name, "N0", (1, 1), (0.5, 0.5), hole_radius=0.1) for layer in layers)
    components = (
        SceneComponent(20, "U1", "TOP", ("N0",), (0.7, 0.7, 1.3, 1.3)),
        SceneComponent(21, "U2", "BOTTOM", ("N0",), (0.7, 0.7, 1.3, 1.3), "bottom"),
    )
    scene = LayoutScene(layers, polygons, pads=pads, net_names=("N0", "N1"), components=components)
    view = LayoutView(scene)
    view.resize(400, 400)
    view.visible_layers = {layer.name for layer in layers}
    view.show_grid = False
    try:
        view.set_prepared(prepare_scene(scene))
        view.show()
        QTest.qWait(150)
        image = view.grabFramebuffer().convertToFormat(QImage.Format.Format_RGBA8888)
        expected = np.frombuffer(image.constBits(), dtype=np.uint8).copy()
        view.cleanup()
        view._pending_upload = False
        for layer in layers:
            part = replace(
                scene,
                polygons=tuple(p for p in polygons if p.layer == layer.name),
                pads=tuple(p for p in pads if p.layer == layer.name),
                components=tuple(component for component in components if component.layer == layer.name),
            )
            view.set_layer_prepared(layer.name, prepare_scene(part))
        actual = view.grabFramebuffer().convertToFormat(image.format())
        assert view.error is None
        np.testing.assert_array_equal(np.frombuffer(actual.constBits(), dtype=np.uint8), expected)
    finally:
        view.cleanup()
        view.close()
        app.processEvents()


def test_initial_layer_close_drains_source_and_initial_error_propagates():
    import threading

    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication, QWidget

    from pyedb.viewer import LayoutScene, SceneLayer
    from pyedb.viewer.qt.app import show_scene
    from pyedb.viewer.qt.window import LayoutWindow

    app = QApplication.instance() or QApplication([])
    # An embedded host must remain open, preventing Qt's last-window quit from
    # masking a missing close signal in the initial capture's local event loop.
    host = QWidget()
    host.show()
    finish = threading.Event()

    class Source:
        released = False

        def load_layer(self, *args, **kwargs):
            assert finish.wait(3)
            assert not self.released
            return "TOP", LayoutScene((SceneLayer("TOP", (1, 0, 0, 1)),), ())

        def release_source(self):
            self.released = True

    source = Source()

    def close_during_load():
        for candidate in app.topLevelWidgets():
            if isinstance(candidate, LayoutWindow) and candidate.isVisible():
                candidate.close()
                assert not source.released
        finish.set()

    QTimer.singleShot(50, close_during_load)
    try:
        window = show_scene(layer_source=source, block=False)
        assert source.released and not window._capturing and not window.isVisible()

        class Broken(Source):
            def load_layer(self, *args, **kwargs):
                raise RuntimeError("Initial layer unavailable")

        broken = Broken()
        with pytest.raises(RuntimeError, match="Initial layer unavailable"):
            show_scene(layer_source=broken, block=False)
        assert broken.released
    finally:
        finish.set()
        host.close()
        app.processEvents()


def test_loading_progress_keeps_event_loop_live_and_propagates_errors():
    import threading

    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication, QDialog

    from pyedb.viewer.demo import demo_scene
    from pyedb.viewer.qt.app import show_scene
    from pyedb.viewer.qt.loading import LoadingPanel
    from pyedb.viewer.qt.window import LayoutWindow

    app = QApplication.instance() or QApplication([])
    heartbeat = threading.Event()
    timer = QTimer()
    timer.setInterval(10)
    observed = []

    def observe():
        windows = [w for w in app.topLevelWidgets() if isinstance(w, LayoutWindow) and w.isVisible()]
        if windows and windows[0].canvas.loading.isVisible():
            observed.append((windows[0], windows[0].canvas.loading))
            heartbeat.set()

    timer.timeout.connect(observe)
    timer.start()
    scene = demo_scene()

    def loader(progress):
        assert threading.current_thread() is not threading.main_thread()
        progress("Reading pads and vias", 40, 100)
        assert heartbeat.wait(2), "The GUI event loop stopped during extraction"
        return scene

    try:
        window = show_scene(loader=loader, block=False)
        assert window.canvas.scene is scene
        assert observed and all(w is window and panel is window.canvas.loading for w, panel in observed)
        assert not any(isinstance(w, QDialog) and w.isVisible() for w in app.topLevelWidgets())
        assert window.layer_list.count() == len(scene.layers)
        assert window.network_panel.names
        window.canvas.grabFramebuffer()
        window.close()

        def broken(progress):
            raise RuntimeError("Source unavailable")

        with pytest.raises(RuntimeError, match="Source unavailable"):
            show_scene(loader=broken, block=False)
        panel = LoadingPanel()
        panel.set_progress("Reading pads and vias", 40, 100)
        assert panel.bar.value() == 40
        assert panel.percent.text() == "40%"
        panel.set_progress("Discovering geometry", 0, 0)
        assert panel.bar.minimum() == panel.bar.maximum() == 0
        assert panel.percent.text() == ""
        panel.close()
    finally:
        timer.stop()
        app.processEvents()


def test_standalone_extraction_keeps_default_blocking_lifecycle():
    import subprocess
    import sys
    import textwrap

    code = textwrap.dedent("""
        from types import SimpleNamespace
        from PySide6.QtCore import QTimer, QMetaObject, QObject, Slot, Qt
        from PySide6.QtWidgets import QApplication
        import pyedb.viewer as viewer
        from pyedb.viewer.demo import demo_scene
        from pyedb.viewer.qt.window import LayoutWindow

        ticks = []
        def finish():
            ticks.append(any(isinstance(w, LayoutWindow) and w.isVisible()
                             for w in QApplication.topLevelWidgets()))
            QApplication.instance().quit()
        class Stopper(QObject):
            @Slot()
            def schedule(self):
                QTimer.singleShot(200, finish)
        stopper = Stopper()
        def capture(*args, **kwargs):
            QMetaObject.invokeMethod(stopper, 'schedule', Qt.ConnectionType.QueuedConnection)
            return demo_scene()
        viewer.scene_from_edb = capture
        window = viewer.launch_viewer(SimpleNamespace(), on_demand=False)
        assert ticks == [True], 'Standalone event loop returned before its timer'
        assert window.canvas.error is None
        window.close()
    """)
    completed = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=20)
    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_solid_polygon_network_colors_share_one_draw_across_interleaved_source_layers():
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication

    from pyedb.viewer import LayoutScene, SceneLayer, ScenePolygon
    from pyedb.viewer.colors import net_color
    from pyedb.viewer.mesh import prepare_scene
    from pyedb.viewer.qt.canvas import LayoutView

    def rect(left, right):
        return ((left, -2), (right, -2), (right, 2), (left, 2))

    scene = LayoutScene(
        (SceneLayer("TOP", (1, 1, 1, 1)), SceneLayer("BOTTOM", (1, 1, 1, 1))),
        (
            ScenePolygon(1, "TOP", "A", rect(-8, -2)),
            ScenePolygon(2, "BOTTOM", "C", rect(-1, 1)),
            ScenePolygon(3, "TOP", "B", rect(2, 8)),
        ),
    )
    app = QApplication.instance() or QApplication([])
    view = LayoutView(scene)
    view.show_grid = view.show_components = False
    view.opacity = 1
    view.resize(640, 480)
    view.set_prepared(prepare_scene(scene))
    view.show()
    try:
        QTest.qWait(100)
        frame = view.grabFramebuffer()
        for position, net_id in ((-5, 1), (5, 2)):
            x, y = view.camera.world_to_screen(position, 0)
            pixel = frame.pixelColor(round(x * view.devicePixelRatioF()), round(y * view.devicePixelRatioF()))
            assert (pixel.red(), pixel.green(), pixel.blue()) == pytest.approx(
                tuple(round(c * 255) for c in net_color(net_id)), abs=1
            )
        assert view.renderer.draw_calls == 1
        assert view.error is None
    finally:
        view.cleanup()
        view.close()
        app.processEvents()


def test_progressive_loading_displays_copper_before_completion_and_preserves_view():
    import threading
    from types import SimpleNamespace

    from PySide6.QtCore import QTimer
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication

    from pyedb.viewer import LayoutScene, SceneLayer, ScenePad, ScenePolygon
    from pyedb.viewer.capture import SourceCapture
    from pyedb.viewer.qt.app import show_scene
    from pyedb.viewer.qt.window import LayoutWindow

    app = QApplication.instance() or QApplication([])
    layers = (SceneLayer("TOP", (1, 0, 0, 1)),)
    polygon = ScenePolygon(1, "TOP", "GND", ((0, 0), (5, 0), (5, 5), (0, 5)))
    copper = LayoutScene(layers, (polygon,), net_names=("GND",))
    complete = LayoutScene(layers, (polygon,), pads=(ScenePad(2, "TOP", "GND", (1, 1), (1, 1)),), net_names=("GND",))
    resume = threading.Event()
    observed = []

    def read(progress, preview=None):
        preview(copper)
        progress("Reading pads and vias", 1, 2)
        assert resume.wait(3), "Copper was not displayed while capture was still running"
        preview(copper)  # A later copper wave must preserve the user's camera.
        return complete

    def observe():
        for widget in app.topLevelWidgets():
            if (
                isinstance(widget, LayoutWindow)
                and widget.isVisible()
                and widget._has_preview
                and widget.canvas.renderer.prepared is not None
                and not widget.canvas._pending_upload
                and not observed
            ):
                canvas = widget.canvas
                canvas.camera.zoom_at(100, 100, 2)
                observed.append(
                    (widget, canvas.loading, canvas.camera.center_x, canvas.camera.center_y, canvas.camera.scale)
                )
                assert not canvas._loading_complete
                resume.set()

    timer = QTimer()
    timer.setInterval(10)
    timer.timeout.connect(observe)
    timer.start()
    window = None
    try:
        loader = SourceCapture(read)
        window = show_scene(loader=loader, block=False)
        QTest.qWait(100)
        window.canvas.grabFramebuffer()
        assert observed[0][:2] == (window, window.canvas.loading)
        assert (window.canvas.camera.center_x, window.canvas.camera.center_y, window.canvas.camera.scale) == observed[
            0
        ][2:]
        assert window.canvas._loading_complete
        assert window.canvas.loading.isHidden()
        assert window.canvas.renderer.prepared.vertices is window._preparation.preview_prepared.vertices
    finally:
        resume.set()
        timer.stop()
        if window is not None:
            window.close()
        app.processEvents()


def test_progressive_mesh_append_uploads_only_new_tail_data(monkeypatch):
    from unittest.mock import Mock

    from OpenGL import GL
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication

    from pyedb.viewer import LayoutScene, SceneLayer, ScenePolygon
    from pyedb.viewer.mesh import prepare_scene
    from pyedb.viewer.qt.canvas import LayoutView

    layers = (SceneLayer("TOP", (1, 0, 0, 1)),)
    first = ScenePolygon(1, "TOP", "A", ((0, 0), (2, 0), (2, 2), (0, 2)))
    second = ScenePolygon(2, "TOP", "B", ((3, 0), (5, 0), (5, 2), (3, 2)))
    preview = LayoutScene(layers, (first,), net_names=("A", "B"))
    complete = LayoutScene(layers, (first, second), net_names=preview.net_names)
    base = prepare_scene(preview)
    appended = prepare_scene(complete, polygon_mesh=(preview, base))
    app = QApplication.instance() or QApplication([])
    view = LayoutView(preview)
    view.show_grid = view.show_components = False
    view.resize(640, 480)
    view.set_prepared(base)
    view.show()
    try:
        QTest.qWait(100)
        view.grabFramebuffer()
        allocation = Mock(wraps=GL.glBufferData)
        updates = Mock(wraps=GL.glBufferSubData)
        monkeypatch.setattr(GL, "glBufferData", allocation)
        monkeypatch.setattr(GL, "glBufferSubData", updates)
        view.scene = complete
        view.fit_all()
        view.set_prepared(appended)
        view.grabFramebuffer()
        assert not any(call.args[1] > 0 for call in allocation.call_args_list)
        assert {call.args[1] for call in updates.call_args_list} == {
            base.vertices.nbytes,
            base.indices.nbytes,
            base.vertex_nets.nbytes,
        }
        assert view.error is None
    finally:
        view.cleanup()
        view.close()
        app.processEvents()


@pytest.mark.parametrize("offset, span", [(0.0, 20.0), (1e9, 0.001)])
def test_stencil_hole_union_and_resident_geometry(offset, span):
    pytest.importorskip("PySide6")
    pytest.importorskip("OpenGL")
    pytest.importorskip("mapbox_earcut")
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication

    from pyedb.viewer import LayoutScene, SceneLayer, ScenePolygon
    from pyedb.viewer.mesh import prepare_scene
    from pyedb.viewer.qt.canvas import LayoutView

    def rect(x0, y0, x1, y1):
        return tuple(
            (offset + x * span / 20, -offset + y * span / 20) for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))
        )

    scene = LayoutScene(
        (SceneLayer("TOP", (1, 0, 0, 1)), SceneLayer("BOTTOM", (0, 0, 1, 1))),
        (
            ScenePolygon(1, "BOTTOM", "GND", rect(-10, -10, 10, 10)),
            ScenePolygon(2, "TOP", "SIGNAL", rect(-9, -9, 9, 9), (rect(-5, -5, 1, 5), rect(-1, -5, 5, 5))),
            # A later solid must not inherit the preceding polygon's stencil mask.
            ScenePolygon(3, "TOP", "SIGNAL", rect(6, 6, 8, 8)),
        ),
    )
    app = QApplication.instance() or QApplication([])
    view = LayoutView(scene)
    view.show_grid = False  # Exact geometry fixtures exclude the decorative grid.
    view.visible_layers = {layer.name for layer in scene.layers}
    view.color_by_net = False  # This fixture verifies exact source-layer colors.
    view.components_on_both_sides = False  # Exercise current-face filtering explicitly.
    view.resize(640, 480)
    view.opacity = 1
    view.set_prepared(prepare_scene(scene))
    view.show()
    try:
        QTest.qWait(200)
        app.processEvents()
        assert view.isValid(), "No usable OpenGL context"
        assert view.error is None, view.error
        image = view.grabFramebuffer()
        assert not image.isNull()

        def color(x, y, frame=image):
            px, py = view.camera.world_to_screen(offset + x * span / 20, -offset + y * span / 20)
            ratio = view.devicePixelRatioF()
            pixel = frame.pixelColor(round(px * ratio), round(py * ratio))
            return pixel.red(), pixel.green(), pixel.blue()

        assert color(0, 0) == (0, 0, 255)  # Overlapping hole union exposes the lower layer.
        assert color(-3, 0) == (0, 0, 255)
        assert color(3, 0) == (0, 0, 255)
        assert color(7, 0) == (255, 0, 0)
        assert color(7, 7) == (255, 0, 0)
        uploads = view.renderer.upload_count
        view.opacity = 0.5
        frame = view.grabFramebuffer()
        assert color(7, 0, frame) == pytest.approx((191, 64, 128), abs=1)
        view.opacity = 1
        view.net = "GND"
        assert color(7, 0, view.grabFramebuffer()) == (0, 0, 255)
        view.net = None
        view.camera.mirror = True
        assert color(7, 0, view.grabFramebuffer()) == (0, 0, 255)
        view.camera.mirror = False
        view.camera.pan(12, -8)
        view.zoom(1.25)
        view.visible_layers.remove("TOP")
        frame = view.grabFramebuffer()
        assert color(7, 0, frame) == (0, 0, 255)
        assert view.renderer.upload_count == uploads == 1
        assert view.renderer.draw_calls == 1
        view.visible_layers.clear()
        frame = view.grabFramebuffer()
        assert color(0, 0, frame) != (0, 0, 255)
    finally:
        view.cleanup()
        view.close()
        app.processEvents()


@pytest.mark.parametrize("color_by_net", [False, True])
def test_drill_only_layer_remains_visible_without_other_geometry_or_net_matches(color_by_net, monkeypatch):
    from unittest.mock import Mock

    from OpenGL import GL
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication

    from pyedb.viewer import LayoutScene, SceneLayer, ScenePad
    from pyedb.viewer.mesh import prepare_scene
    from pyedb.viewer.qt.canvas import LayoutView

    scene = LayoutScene(
        tuple(SceneLayer(name, (1, 0, 0, 1)) for name in ("TOP", "INNER", "BOTTOM", "OUTSIDE")),
        (),
        pads=(
            ScenePad(1, "TOP", "VIA_ONLY", (0, 0), (4, 4), hole_radius=1),
            ScenePad(1, "INNER", "VIA_ONLY", (0, 0), (2, 2), hole_radius=1),
            ScenePad(1, "BOTTOM", "VIA_ONLY", (0, 0), (4, 4), hole_radius=1),
        ),
    )
    app = QApplication.instance() or QApplication([])
    view = LayoutView(scene)
    view.resize(400, 400)
    view.show_grid = False
    view.color_by_net = color_by_net
    view.set_prepared(prepare_scene(scene))
    view.show()
    try:
        QTest.qWait(70)
        view.grabFramebuffer()
        upload = Mock(wraps=GL.glBufferData)
        monkeypatch.setattr(GL, "glBufferData", upload)

        def pixel(x=0):
            frame = view.grabFramebuffer()
            px, py = view.camera.world_to_screen(x, 0)
            ratio = view.devicePixelRatioF()
            color = frame.pixelColor(round(px * ratio), round(py * ratio))
            return color.red(), color.green(), color.blue()

        for layer in ("TOP", "INNER", "BOTTOM"):
            view.visible_layers = {layer}
            for mirror in (False, True):
                view.camera.mirror = mirror
                for net in (None, "VIA_ONLY"):
                    view.net = net
                    assert pixel() == (153, 153, 153)
            if layer == "INNER":
                assert pixel(1.5) == (255, 255, 255)  # No invented annulus.
        view.visible_layers = {"OUTSIDE"}
        assert pixel() == (255, 255, 255)  # Drill does not extend beyond its span.
        view.visible_layers = {"INNER"}
        view.net = "OTHER"
        assert pixel() == (255, 255, 255)
        view.net = "VIA_ONLY"
        view.opacity = 0.1
        assert pixel() == (153, 153, 153)  # Bore remains distinguishable at low copper opacity.
        view.opacity = 0
        assert pixel() == (255, 255, 255)
        assert view.renderer.upload_count == 1
        assert view.error is None, view.error
        upload.assert_not_called()
    finally:
        view.cleanup()
        view.close()
        app.processEvents()


def test_window_worker_controls_and_resource_recreation():
    pytest.importorskip("PySide6")
    pytest.importorskip("OpenGL")
    pytest.importorskip("mapbox_earcut")
    import time

    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication

    from pyedb.viewer import launch_viewer
    from pyedb.viewer.demo import demo_scene

    app = QApplication.instance() or QApplication([])
    window = launch_viewer(scene=demo_scene())
    try:
        assert QApplication.instance() is app
        deadline = time.monotonic() + 5
        while window.canvas.renderer.prepared is None and not window.canvas.error and time.monotonic() < deadline:
            QTest.qWait(20)
        canvas = window.canvas
        assert canvas.error is None, canvas.error
        assert canvas.renderer.prepared is not None
        initial_uploads = canvas.renderer.upload_count
        assert canvas.color_by_net is True
        assert canvas.components_on_both_sides is True
        window.color_mode.setCurrentIndex(0)
        assert canvas.color_by_net is False
        window.color_mode.setFocus()
        QTest.keyClick(window.color_mode, Qt.Key.Key_End)
        assert canvas.color_by_net is True
        window.components_action.setChecked(False)
        window.component_names_action.setChecked(False)
        window.both_sides_action.setChecked(True)
        assert not canvas.show_components
        assert not canvas.annotate_component_names
        assert canvas.components_on_both_sides
        window.components_action.setChecked(True)
        window.component_names_action.setChecked(True)
        window.both_sides_action.setChecked(False)
        window.layer_list.item(0).setCheckState(Qt.CheckState.Unchecked)
        assert "TOP" not in canvas.visible_layers
        window.network_list.setCurrentRow(1)
        assert canvas.net == window.network_list.item(1).data(Qt.ItemDataRole.UserRole)
        QTest.keyClick(canvas, Qt.Key.Key_Right)
        canvas.grabFramebuffer()
        assert canvas.renderer.upload_count == initial_uploads
        window.close()
        assert canvas.renderer.program == 0
        window.show()
        QTest.qWait(100)
        canvas.grabFramebuffer()
        assert canvas.error is None, canvas.error
        assert canvas.renderer.upload_count == initial_uploads + 1
    finally:
        window.close()
        app.processEvents()


@pytest.mark.parametrize("button_name", ["LeftButton", "MiddleButton", "RightButton"])
@pytest.mark.parametrize("mirror", [False, True])
def test_mouse_drag_pans_canvas_and_keeps_geometry_resident(button_name, mirror):
    from PySide6.QtCore import QPoint, Qt
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication

    from pyedb.viewer import LayoutScene, SceneLayer, ScenePolygon
    from pyedb.viewer.mesh import prepare_scene
    from pyedb.viewer.qt.canvas import LayoutView

    scene = LayoutScene(
        (SceneLayer("TOP", (1, 0, 0, 1)),),
        (ScenePolygon(1, "TOP", "GND", ((0, 0), (10, 0), (10, 10), (0, 10))),),
    )
    app = QApplication.instance() or QApplication([])
    view = LayoutView(scene)
    view.show_grid = False  # Exact geometry fixtures exclude the decorative grid.
    view.visible_layers = {layer.name for layer in scene.layers}
    view.color_by_net = False  # This fixture verifies exact source-layer colors.
    view.components_on_both_sides = False  # Exercise current-face filtering explicitly.
    view.resize(640, 480)
    view.camera.mirror = mirror
    view.set_prepared(prepare_scene(scene))
    view.show()
    button = getattr(Qt.MouseButton, button_name)
    try:
        QTest.qWait(60)
        view.grabFramebuffer()
        assert view.error is None, view.error
        uploads = view.renderer.upload_count
        start = QPoint(320, 240)
        end = start + QPoint(43, -27)
        anchor = view.camera.screen_to_world(start.x(), start.y())
        QTest.mousePress(view, button, pos=start)
        QTest.mouseMove(view, end, delay=10)
        QTest.mouseRelease(view, button, pos=end)
        assert view.camera.world_to_screen(*anchor) == pytest.approx((end.x(), end.y()))
        assert view._drag_position is None
        assert view._drag_button == Qt.MouseButton.NoButton
        center = view.camera.center_x, view.camera.center_y
        QTest.mouseMove(view, end + QPoint(30, 20))
        assert (view.camera.center_x, view.camera.center_y) == center
        view.grabFramebuffer()
        assert view.renderer.upload_count == uploads == 1
        assert view.error is None, view.error
    finally:
        view.cleanup()
        view.close()
        app.processEvents()


@pytest.mark.parametrize("offset, unit", [(0.0, 1.0), (1e9, 0.0001)])
@pytest.mark.parametrize("samples", [0, 4])
def test_instanced_sdf_caps_arcs_vias_union_filters_and_residency(offset, unit, samples, monkeypatch):
    """Exercise actual shaders/FBOs, including SDF-only snapshots and deep zoom."""
    import math

    pytest.importorskip("PySide6")
    pytest.importorskip("OpenGL")
    from unittest.mock import Mock

    from OpenGL import GL
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication

    from pyedb.viewer import LayoutScene, SceneLayer, ScenePad, ScenePolygon, SceneTrace
    from pyedb.viewer.mesh import prepare_scene
    from pyedb.viewer.qt.canvas import LayoutView

    def point(x, y):
        return offset + x * unit, -offset + y * unit

    traces = [
        SceneTrace(index, "TOP", "SIGNAL", point(-8, -7), point(-2, -7), unit)
        for index in range(600)  # Overlaps must composite once, independent of count.
    ]
    for y, cap in ((-4, "flat"), (-1, "extended")):
        traces.append(SceneTrace(700, "TOP", "SIGNAL", point(-8, y), point(-2, y), unit, end_caps=(cap, cap)))
    traces.append(SceneTrace(701, "TOP", "SIGNAL", point(-3, 3), point(0, 6), unit, point(0, 3), -math.pi / 2))
    pads = (
        ScenePad(800, "TOP", "VIA", point(6, 4), (3 * unit,) * 2, hole_radius=0.55 * unit),
        ScenePad(801, "TOP", "PIN", point(5, -4), (4 * unit, 2 * unit), "rectangle", math.pi / 2),
    )
    layers = (SceneLayer("TOP", (1, 0, 0, 1)), SceneLayer("BOTTOM", (0, 0, 1, 1)))
    plane = ScenePolygon(
        1, "BOTTOM", "GND", tuple(point(x, y) for x, y in ((-10, -10), (10, -10), (10, 10), (-10, 10)))
    )
    scene = LayoutScene(layers, (plane,), traces=tuple(traces), pads=pads)
    app = QApplication.instance() or QApplication([])
    view = LayoutView(scene)
    view.show_grid = False  # Exact geometry fixtures exclude the decorative grid.
    view.visible_layers = {layer.name for layer in scene.layers}
    view.color_by_net = False  # This fixture verifies exact source-layer colors.
    view.components_on_both_sides = False  # Exercise current-face filtering explicitly.
    surface = view.format()
    surface.setSamples(samples)
    view.setFormat(surface)
    view.resize(800, 800)
    view.opacity = 1
    view.set_prepared(prepare_scene(scene))
    view.show()
    try:
        QTest.qWait(100)
        app.processEvents()
        assert view.isValid()
        assert view.error is None, view.error

        def color(frame, x, y):
            px, py = view.camera.world_to_screen(*point(x, y))
            ratio = view.devicePixelRatioF()
            pixel = frame.pixelColor(round(px * ratio), round(py * ratio))
            return pixel.red(), pixel.green(), pixel.blue()

        frame = view.grabFramebuffer()
        assert color(frame, -5, -7) == (255, 0, 0)
        assert color(frame, -8.3, -7) == (255, 0, 0)  # Round cap.
        assert color(frame, -8.8, -7) == (0, 0, 255)
        assert color(frame, -8.3, -4) == (0, 0, 255)  # Flat cap.
        assert color(frame, -8.3, -1) == (255, 0, 0)  # Extended cap.
        assert color(frame, -3 / math.sqrt(2), 3 + 3 / math.sqrt(2)) == (255, 0, 0)
        assert color(frame, 3, 3) == (0, 0, 255)  # Outside the arc's sweep.
        assert color(frame, 6.9, 4) == (255, 0, 0)
        assert color(frame, 6, 4) == pytest.approx((153, 153, 153), abs=1)  # Gray bore over a solid plane.
        assert color(frame, 5, -5.5) == (255, 0, 0)  # Rotated rectangular pin.
        assert color(frame, 6.5, -4) == (0, 0, 255)
        assert view.renderer.draw_calls <= 7
        uploads = view.renderer.upload_count
        buffer_data = Mock(wraps=GL.glBufferData)
        buffer_sub_data = Mock(wraps=GL.glBufferSubData)
        monkeypatch.setattr(GL, "glBufferData", buffer_data)
        monkeypatch.setattr(GL, "glBufferSubData", buffer_sub_data)

        from pyedb.viewer.colors import net_color

        view.color_by_net = True
        frame = view.grabFramebuffer()

        def network_rgb(name):
            return tuple(round(v * 255) for v in net_color(view.renderer.sdf.net_ids[name]))

        assert color(frame, -5, -7) == network_rgb("SIGNAL")
        assert color(frame, 6.9, 4) == network_rgb("VIA")
        assert color(frame, 5, -5.5) == network_rgb("PIN")
        assert color(frame, 9, 9) == network_rgb("GND")
        view.color_by_net = False
        view.opacity = 0.5
        frame = view.grabFramebuffer()
        assert color(frame, -5, -7) == pytest.approx((191, 64, 128), abs=1)
        view.opacity = 1
        view.net = "VIA"
        frame = view.grabFramebuffer()
        assert color(frame, 6.9, 4) == (255, 0, 0)
        assert color(frame, -5, -7) == pytest.approx((255, 255, 255), abs=1)
        view.net = None
        view.visible_layers.remove("TOP")
        assert color(view.grabFramebuffer(), 6, 4) == (0, 0, 255)  # Hidden via also hides its drill.
        view.visible_layers.add("TOP")
        view.camera.mirror = True
        assert color(view.grabFramebuffer(), -5, -7) == (0, 0, 255)
        view.camera.mirror = False
        view.camera.pan(8, -13)
        view.zoom(1.4)
        assert color(view.grabFramebuffer(), -5, -7) == (255, 0, 0)
        view.resize(960, 720)
        QTest.qWait(30)
        assert color(view.grabFramebuffer(), -5, -7) == (255, 0, 0)
        assert view.renderer.upload_count == uploads == 1
        buffer_data.assert_not_called()
        buffer_sub_data.assert_not_called()

        # No polygon/index data: the renderer must still draw via-only scenes.
        view.scene = LayoutScene(layers, (), pads=pads)
        view.set_prepared(prepare_scene(view.scene))
        assert color(view.grabFramebuffer(), 6.9, 4) == (255, 0, 0)
        assert not view.message.isVisible()
        assert view.error is None, view.error
    finally:
        view.cleanup()
        assert view.renderer.sdf.program == view.renderer.sdf.vbo == view.renderer.sdf.fbo == 0
        view.close()
        app.processEvents()


@pytest.mark.parametrize("sweep", [-1.5, -0.5, 0.5, 1.5, 2.0])
def test_analytic_arc_minor_major_full_sweeps_and_solid_miter_join(sweep):
    import math

    pytest.importorskip("PySide6")
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication

    from pyedb.viewer import LayoutScene, SceneJoin, SceneLayer, SceneTrace
    from pyedb.viewer.mesh import prepare_scene
    from pyedb.viewer.qt.canvas import LayoutView

    angle = sweep * math.pi
    scene = LayoutScene(
        (SceneLayer("TOP", (1, 0, 0, 1)),),
        (),
        traces=(
            SceneTrace(1, "TOP", None, (3, 0), (3 * math.cos(angle), 3 * math.sin(angle)), 0.5, (0, 0), angle),
            SceneTrace(2, "TOP", None, (-3, -6), (0, -6), 2),
            SceneTrace(2, "TOP", None, (0, -6), (0, -4), 2),
        ),
        joins=(SceneJoin(2, "TOP", None, ((0, -6), (0, -7), (1, -7), (1, -6))),),
    )
    app = QApplication.instance() or QApplication([])
    view = LayoutView(scene)
    view.show_grid = False  # Exact geometry fixtures exclude the decorative grid.
    view.visible_layers = {layer.name for layer in scene.layers}
    view.color_by_net = False  # This fixture verifies exact source-layer colors.
    view.components_on_both_sides = False  # Exercise current-face filtering explicitly.
    view.resize(640, 640)
    view.opacity = 1
    view.set_prepared(prepare_scene(scene))
    view.show()
    try:
        QTest.qWait(40)
        frame = view.grabFramebuffer()
        assert view.error is None, view.error

        def rgb(x, y):
            px, py = view.camera.world_to_screen(x, y)
            ratio = view.devicePixelRatioF()
            pixel = frame.pixelColor(round(px * ratio), round(py * ratio))
            return pixel.red(), pixel.green(), pixel.blue()

        for quarter in (0.25, 0.75, 1.25, 1.75):
            t = quarter * math.pi
            phase = (t if sweep > 0 else -t) % math.tau
            assert (rgb(3 * math.cos(t), 3 * math.sin(t)) == (255, 0, 0)) == (phase < abs(angle))
        assert rgb(0.8, -6.8) == (255, 0, 0)  # Inside the miter, outside the round caps; no diagonal seam.
        assert rgb(1.3, -6.8) == (255, 255, 255)
    finally:
        view.cleanup()
        view.close()
        app.processEvents()


def test_component_envelopes_labels_side_net_filters_and_residency(monkeypatch):
    """Component overlays and text must share filtering and keep GPU data resident."""
    from unittest.mock import Mock

    from OpenGL import GL
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication

    from pyedb.viewer import LayoutScene, SceneComponent, SceneLayer, ScenePolygon
    from pyedb.viewer.mesh import prepare_scene
    from pyedb.viewer.qt.canvas import LayoutView

    layers = (SceneLayer("TOP", (1, 0, 0, 1)), SceneLayer("BOTTOM", (0, 0, 1, 1)))
    ring = ((-10, -5), (10, -5), (10, 5), (-10, 5))
    components = (
        SceneComponent(10, "U1", "TOP", ("GND", "SIGNAL"), (-7, -2, -1, 2)),
        SceneComponent(11, "R2", "BOTTOM", ("BOTTOM_NET",), (1, -2, 7, 2), "bottom"),
    )
    scene = LayoutScene(
        layers, (ScenePolygon(1, "TOP", "GND", ring), ScenePolygon(2, "BOTTOM", "GND", ring)), components=components
    )
    app = QApplication.instance() or QApplication([])
    view = LayoutView(scene)
    view.show_grid = False  # Exact geometry fixtures exclude the decorative grid.
    view.visible_layers = {layer.name for layer in scene.layers}
    view.color_by_net = False  # This fixture verifies exact source-layer colors.
    view.components_on_both_sides = False  # Exercise current-face filtering explicitly.
    view.resize(800, 480)
    view.opacity = 1
    view.set_prepared(prepare_scene(scene))
    view.show()
    try:
        QTest.qWait(80)
        frame = view.grabFramebuffer()
        assert view.error is None, view.error
        assert view.renderer.labels.drawn_count == 1

        def patch(image, x, y, width=7, height=11):
            px, py = view.camera.world_to_screen(x, y)
            ratio = view.devicePixelRatioF()
            w, h = round(width * ratio), round(height * ratio)
            return image.copy(round(px * ratio) - w // 2, round(py * ratio) - h // 2, w, h)

        upload = Mock(wraps=GL.glBufferData)
        sub_upload = Mock(wraps=GL.glBufferSubData)
        monkeypatch.setattr(GL, "glBufferData", upload)
        monkeypatch.setattr(GL, "glBufferSubData", sub_upload)
        atlas = view.renderer.labels.texture
        view.show_components = False
        plain = view.grabFramebuffer()
        assert patch(frame, -7, 0) != patch(plain, -7, 0)  # Top envelope.
        assert patch(frame, 7, 0) == patch(plain, 7, 0)  # Bottom excluded in top view.
        assert patch(frame, -4, 0, 45, 28) != patch(plain, -4, 0, 45, 28)  # U1 reference.
        view.show_components = True
        view.annotate_component_names = False
        no_names = view.grabFramebuffer()
        assert patch(frame, -7, 0) == patch(no_names, -7, 0)
        assert patch(no_names, -4, 0, 45, 28) == patch(plain, -4, 0, 45, 28)
        assert view.renderer.labels.drawn_count == 0

        view.annotate_component_names = True
        view.net = "SIGNAL"  # The second net of U1 still selects the whole component.
        signal = view.grabFramebuffer()
        assert view.renderer.labels.drawn_count == 1
        view.show_components = False
        assert patch(signal, -7, 0) != patch(view.grabFramebuffer(), -7, 0)
        view.show_components = True
        view.net = "BOTTOM_NET"
        bottom_hidden = view.grabFramebuffer()
        assert view.renderer.labels.drawn_count == 0
        view.components_on_both_sides = True
        both = view.grabFramebuffer()
        assert patch(both, 7, 0) != patch(bottom_hidden, 7, 0)
        assert view.renderer.labels.drawn_count == 1

        view.net = None
        view.components_on_both_sides = False
        view.camera.mirror = True
        bottom = view.grabFramebuffer()
        view.show_components = False
        plain_bottom = view.grabFramebuffer()
        assert patch(bottom, 7, 0) != patch(plain_bottom, 7, 0)
        assert patch(bottom, -7, 0) == patch(plain_bottom, -7, 0)
        view.show_components = True
        view.camera.mirror = False
        view.color_by_net = True
        view.opacity = 0.4
        view.camera.pan(12, -9)
        view.zoom(1.1)
        view.visible_layers.remove("TOP")
        view.grabFramebuffer()
        assert view.renderer.labels.drawn_count == 0
        view.visible_layers.add("TOP")
        view.grabFramebuffer()
        assert view.renderer.labels.drawn_count == 1
        assert view.renderer.labels.texture == atlas
        assert view.renderer.upload_count == 1
        upload.assert_not_called()
        sub_upload.assert_not_called()

        # A component-only snapshot must render without an index buffer or copper batch.
        scene = LayoutScene(layers, (), components=components)
        view.scene = scene
        view.set_prepared(prepare_scene(scene))
        view.components_on_both_sides = True
        view.camera.fit(scene.bounds)
        frame = view.grabFramebuffer()
        # Both faces use opaque copper-brown ink, matching component outlines.
        for x in (-4, 4):
            crop = patch(frame, x, 0, 45, 28)
            ink = min(
                (crop.pixelColor(px, py) for px in range(crop.width()) for py in range(crop.height())),
                key=lambda color: color.red() + color.green() + color.blue(),
            )
            assert (ink.red(), ink.green(), ink.blue()) == pytest.approx((184, 115, 51), abs=3)
        assert view.error is None, view.error
        assert not view.message.isVisible()
    finally:
        view.cleanup()
        assert view.renderer.labels.program == view.renderer.labels.texture == view.renderer.labels.vbo == 0
        view.close()
        app.processEvents()


def test_component_pins_keep_copper_fill_without_extra_borders(monkeypatch):
    """Component annotations must not add borders or remove physical pin copper."""
    from unittest.mock import Mock

    from OpenGL import GL
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication

    from pyedb.viewer import LayoutScene, SceneComponent, SceneLayer, ScenePad, ScenePolygon
    from pyedb.viewer.mesh import prepare_scene
    from pyedb.viewer.qt.canvas import LayoutView

    layers = (SceneLayer("TOP", (1, 0, 0, 1)), SceneLayer("BOTTOM", (0, 0, 1, 1)))
    plane = ((-10, -6), (10, -6), (10, 6), (-10, 6))
    owner = dict(component="U1", component_layer="TOP", component_side="top")
    pads = (
        ScenePad(10, "TOP", "GND", (-5, -2), (2, 2), pin_name="1", **owner),
        ScenePad(11, "TOP", "SIGNAL", (0, -2), (3, 1), "rectangle", pin_name="2", **owner),
        ScenePad(12, "BOTTOM", "BOTTOM_NET", (5, -2), (2, 2), component="U2", component_side="bottom", pin_name="1"),
        ScenePad(13, "TOP", "GND", (5, 3), (2, 2)),  # A via/ordinary pad must not gain a pin outline.
    )
    custom = ScenePolygon(14, "TOP", "GND", ((-8, 1), (-6, 4), (-4, 1)), pin_name="3", **owner)
    scene = LayoutScene(
        layers,
        (ScenePolygon(1, "TOP", "GND", plane), ScenePolygon(2, "BOTTOM", "GND", plane), custom),
        pads=pads,
        components=(
            SceneComponent(100, "U1", "TOP", ("GND", "SIGNAL"), (-9, -5, 3, 5)),
            SceneComponent(101, "U2", "BOTTOM", ("BOTTOM_NET",), (3, -5, 8, 1), "bottom"),
        ),
    )
    app = QApplication.instance() or QApplication([])
    view = LayoutView(scene)
    view.show_grid = False  # Exact geometry fixtures exclude the decorative grid.
    view.visible_layers = {layer.name for layer in scene.layers}
    view.color_by_net = False  # This fixture verifies exact source-layer colors.
    view.components_on_both_sides = False  # Exercise current-face filtering explicitly.
    view.resize(900, 600)
    view.opacity = 1
    view.annotate_component_names = False
    view.set_prepared(prepare_scene(scene))
    view.show()
    try:
        QTest.qWait(80)
        frame = view.grabFramebuffer()
        assert view.error is None, view.error
        assert view.renderer.sdf.drawn_pin_count == 0

        def patch(image, x, y, span=5):
            px, py = view.camera.world_to_screen(x, y)
            ratio = view.devicePixelRatioF()
            width = round(span * ratio)
            return image.copy(round(px * ratio) - width // 2, round(py * ratio) - width // 2, width, width)

        upload = Mock(wraps=GL.glBufferData)
        sub_upload = Mock(wraps=GL.glBufferSubData)
        monkeypatch.setattr(GL, "glBufferData", upload)
        monkeypatch.setattr(GL, "glBufferSubData", sub_upload)
        view.show_components = False
        plain = view.grabFramebuffer()
        assert patch(frame, -6, -2) == patch(plain, -6, -2)  # No extra circle border.
        assert patch(frame, 0, -1.5) == patch(plain, 0, -1.5)  # No extra rectangle border.
        assert patch(frame, -5, -2) == patch(plain, -5, -2)  # Fill/color is untouched.
        assert patch(frame, 5, 4) == patch(plain, 5, 4)  # Ordinary pad is not a component pin.
        assert patch(frame, -7, 2.5) == patch(plain, -7, 2.5)  # No auxiliary custom-pad border.
        assert patch(frame, -7.8, 3.5) == patch(plain, -7.8, 3.5)  # No bounding-box substitute.
        assert view.renderer.sdf.drawn_pin_count == 0
        view.show_components = True
        view.net = "SIGNAL"
        signal = view.grabFramebuffer()
        pixel = patch(signal, 0, -2, span=1).pixelColor(0, 0)
        assert (pixel.red(), pixel.green(), pixel.blue()) == (255, 0, 0)
        assert view.renderer.sdf.drawn_pin_count == 0
        view.net = None
        view.camera.mirror = True
        bottom = view.grabFramebuffer()
        assert view.renderer.sdf.drawn_pin_count == 0
        view.show_components = False
        assert patch(bottom, 6, -2) == patch(view.grabFramebuffer(), 6, -2)
        view.show_components = True
        view.components_on_both_sides = True
        view.grabFramebuffer()
        assert view.renderer.sdf.drawn_pin_count == 0
        view.visible_layers.remove("BOTTOM")
        view.grabFramebuffer()
        assert view.renderer.sdf.drawn_pin_count == 0
        view.color_by_net = True
        view.opacity = 0.5
        view.camera.pan(8, -11)
        view.zoom(1.15)
        view.grabFramebuffer()
        assert view.error is None, view.error
        assert view.renderer.upload_count == 1
        upload.assert_not_called()
        sub_upload.assert_not_called()
    finally:
        view.cleanup()
        view.close()
        app.processEvents()


def test_custom_pin_voids_use_copper_stencil_without_extra_outlines():
    """Custom pin fill and overlapping holes remain intact without an annotation pass."""
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication

    from pyedb.viewer import LayoutScene, SceneLayer, ScenePolygon
    from pyedb.viewer.mesh import prepare_scene
    from pyedb.viewer.qt.canvas import LayoutView

    def rectangle(x0, y0, x1, y1):
        return ((x0, y0), (x1, y0), (x1, y1), (x0, y1))

    pin = ScenePolygon(
        2,
        "TOP",
        "GND",
        rectangle(-6, -3, 0, 3),
        (rectangle(-4, -1, -1, 1), rectangle(-3, -1, 1, 1)),
        component="U1",
        pin_name="1",
    )
    scene = LayoutScene((SceneLayer("TOP", (1, 0, 0, 1)),), (pin,))
    app = QApplication.instance() or QApplication([])
    view = LayoutView(scene)
    view.show_grid = False  # Exact geometry fixtures exclude the decorative grid.
    view.visible_layers = {layer.name for layer in scene.layers}
    view.color_by_net = False  # This fixture verifies exact source-layer colors.
    view.components_on_both_sides = False  # Exercise current-face filtering explicitly.
    view.resize(800, 480)
    view.opacity = 1
    view.set_prepared(prepare_scene(scene))
    view.show()
    try:
        QTest.qWait(60)
        frame = view.grabFramebuffer()
        assert view.error is None, view.error

        def patch(image, x, y):
            px, py = view.camera.world_to_screen(x, y)
            ratio = view.devicePixelRatioF()
            return image.copy(round(px * ratio) - 3, round(py * ratio) - 3, 7, 7)

        view.show_components = False
        plain = view.grabFramebuffer()
        assert frame == plain
        assert patch(frame, -6, 2) == patch(plain, -6, 2)
        assert patch(frame, -4, 0) == patch(plain, -4, 0)
        assert patch(frame, -3, 0) == patch(plain, -3, 0)  # Hidden by the first void.
        assert patch(frame, -1, 0) == patch(plain, -1, 0)  # Hidden by the second void.
        assert patch(frame, 0, 0) == patch(plain, 0, 0)  # Outer edge cut away by the void.
        assert patch(frame, 1, 0) == patch(plain, 1, 0)  # Void contour outside the pad bounds.
    finally:
        view.cleanup()
        view.close()
        app.processEvents()


def test_navigation_capsule_defaults_and_controls_keep_geometry_resident(monkeypatch):
    from unittest.mock import Mock

    from OpenGL import GL
    from PySide6.QtCore import QPoint, Qt
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication

    from pyedb.viewer import launch_viewer
    from pyedb.viewer.demo import demo_scene

    app = QApplication.instance() or QApplication([])
    window = launch_viewer(scene=demo_scene(), block=False)
    try:
        QTest.qWait(160)
        canvas, pill = window.canvas, window.navigation
        canvas.grabFramebuffer()
        assert canvas.error is None, canvas.error
        assert canvas.color_by_net is True
        assert canvas.components_on_both_sides is True
        assert window.color_mode.currentData() is True
        assert pill.isVisible()
        assert pill.parentWidget() is canvas
        assert abs(pill.geometry().center().x() - canvas.width() / 2) <= 1
        assert pill.geometry().bottom() < canvas.height()
        assert not hasattr(pill, "mirror_button")

        upload = Mock(wraps=GL.glBufferData)
        sub_upload = Mock(wraps=GL.glBufferSubData)
        monkeypatch.setattr(GL, "glBufferData", upload)
        monkeypatch.setattr(GL, "glBufferSubData", sub_upload)
        scale = canvas.camera.scale
        QTest.mouseClick(pill.zoom_in_button, Qt.MouseButton.LeftButton)
        assert canvas.camera.scale == pytest.approx(scale * 1.2)
        QTest.mouseClick(pill.zoom_out_button, Qt.MouseButton.LeftButton)
        assert canvas.camera.scale == pytest.approx(scale)
        canvas.camera.pan(100, 50)
        QTest.mouseClick(pill.fit_button, Qt.MouseButton.LeftButton)
        bounds = canvas.scene.bounds
        points = [canvas.camera.world_to_screen(*point) for point in (bounds[:2], bounds[2:])]
        assert max(point[1] for point in points) < pill.y()
        assert canvas._drag_position is None
        center = canvas.camera.center_x, canvas.camera.center_y
        QTest.mouseClick(pill, Qt.MouseButton.LeftButton, pos=QPoint(2, pill.height() // 2))
        assert canvas._drag_position is None
        assert (canvas.camera.center_x, canvas.camera.center_y) == center
        window.mirror_action.trigger()
        assert canvas.camera.mirror is True
        assert window.mirror_action.isChecked()
        canvas.setFocus()
        QTest.keyClick(canvas, Qt.Key.Key_B)
        assert canvas.camera.mirror is False
        window.resize(560, 420)
        QTest.qWait(30)
        assert pill.geometry().left() >= 0
        assert pill.geometry().right() < canvas.width()
        assert pill.geometry().bottom() < canvas.height()
        canvas.grabFramebuffer()
        assert canvas.error is None, canvas.error
        assert canvas.renderer.upload_count == 1
        upload.assert_not_called()
        sub_upload.assert_not_called()
    finally:
        window.close()
        app.processEvents()


@pytest.mark.parametrize("empty", [False, True])
def test_models_without_components_or_top_bottom_names_have_appropriate_controls(empty):
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication

    from pyedb.viewer import LayoutScene, SceneLayer, ScenePolygon, launch_viewer

    scene = (
        LayoutScene((), ())
        if empty
        else LayoutScene(
            (SceneLayer("metal_1", (1, 0, 0, 1)),),
            (ScenePolygon(1, "metal_1", "N1", ((0, 0), (10, 0), (10, 10), (0, 10))),),
        )
    )
    app = QApplication.instance() or QApplication([])
    window = launch_viewer(scene=scene, block=False)
    try:
        QTest.qWait(100)
        window.canvas.grabFramebuffer()
        assert window.canvas.error is None, window.canvas.error
        assert not window.components_action.isVisible()
        assert not window.component_names_action.isVisible()
        assert not window.both_sides_action.isVisible()
        assert window.canvas.color_by_net is True
        assert window.navigation.isVisible() is not empty
        assert window.fit_action.isEnabled() is not empty
        if not empty:
            assert window.layer_list.count() == 1
            assert window.layer_list.item(0).text() == "metal_1"
            window.mirror_action.trigger()
            assert window.canvas.camera.mirror is True
            window.canvas.grabFramebuffer()
            assert window.canvas.error is None, window.canvas.error
    finally:
        window.close()
        app.processEvents()


def test_both_sides_prioritize_current_face_when_reference_labels_overlap():
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication

    from pyedb.viewer import LayoutScene, SceneComponent, SceneLayer
    from pyedb.viewer.mesh import prepare_scene
    from pyedb.viewer.qt.canvas import LayoutView

    scene = LayoutScene(
        (SceneLayer("copper_a", (1, 0, 0, 1)), SceneLayer("copper_b", (0, 0, 1, 1))),
        (),
        components=(
            SceneComponent(1, "U_FRONT", "copper_a", ("GND",), (0, 0, 10, 10)),
            SceneComponent(2, "U_BACK", "copper_b", ("GND",), (-1, -1, 11, 11), "bottom"),
        ),
    )
    app = QApplication.instance() or QApplication([])
    view = LayoutView(scene)
    view.show_grid = False  # Exact geometry fixtures exclude the decorative grid.
    view.visible_layers = {layer.name for layer in scene.layers}
    view.resize(640, 480)
    view.set_prepared(prepare_scene(scene))
    view.show()
    try:
        QTest.qWait(60)
        for mirror, side in ((False, "top"), (True, "bottom")):
            view.camera.mirror = mirror
            view.grabFramebuffer()
            assert view.error is None, view.error
            labels = view.renderer.labels
            accepted = labels._visible(view.camera, view.visible_layers, None, both_sides=True)
            assert len(accepted) == labels.drawn_count == 1
            assert labels.records[accepted[0]][0].side == side
    finally:
        view.cleanup()
        view.close()
        app.processEvents()


@pytest.mark.parametrize("layer_count", [0, 1, 3])
def test_default_first_layer_and_bulk_visibility_buttons(layer_count, monkeypatch):
    """Bulk selection synchronizes the list in one repaint, without new GPU uploads."""
    from unittest.mock import Mock

    from OpenGL import GL
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication

    from pyedb.viewer import LayoutScene, SceneLayer, ScenePolygon, launch_viewer

    names = ["copper_first", "metal_middle", "copper_last"][:layer_count]
    layers = tuple(SceneLayer(name, (1, 0, 0, 1)) for name in names)
    polygons = tuple(ScenePolygon(i, name, "N1", ((0, 0), (10, 0), (10, 10), (0, 10))) for i, name in enumerate(names))
    app = QApplication.instance() or QApplication([])
    window = launch_viewer(scene=LayoutScene(layers, polygons), block=False)
    try:
        QTest.qWait(120)
        canvas = window.canvas
        canvas.grabFramebuffer()
        assert canvas.error is None, canvas.error
        assert canvas.visible_layers == ({names[0]} if names else set())
        assert [window.layer_list.item(i).checkState() for i in range(layer_count)] == (
            [Qt.CheckState.Checked] + [Qt.CheckState.Unchecked] * (layer_count - 1) if layer_count else []
        )
        assert window.show_all_layers_button.isEnabled() == (layer_count > 1)
        assert window.hide_all_layers_button.isEnabled() == (layer_count > 0)
        upload = Mock(wraps=GL.glBufferData)
        sub_upload = Mock(wraps=GL.glBufferSubData)
        update = Mock(wraps=canvas.update)
        monkeypatch.setattr(GL, "glBufferData", upload)
        monkeypatch.setattr(GL, "glBufferSubData", sub_upload)
        monkeypatch.setattr(canvas, "update", update)
        if names:
            QTest.mouseClick(window.hide_all_layers_button, Qt.MouseButton.LeftButton)
            assert canvas.visible_layers == set()
            assert all(window.layer_list.item(i).checkState() == Qt.CheckState.Unchecked for i in range(layer_count))
            update.assert_called_once()
            assert not window.hide_all_layers_button.isEnabled()
            assert window.show_all_layers_button.isEnabled()
            canvas.grabFramebuffer()
            assert canvas.renderer.draw_calls == 0

            update.reset_mock()
            QTest.mouseClick(window.show_all_layers_button, Qt.MouseButton.LeftButton)
            assert canvas.visible_layers == set(names)
            assert all(window.layer_list.item(i).checkState() == Qt.CheckState.Checked for i in range(layer_count))
            update.assert_called_once()
            assert not window.show_all_layers_button.isEnabled()
            assert window.hide_all_layers_button.isEnabled()
            canvas.grabFramebuffer()
            assert canvas.renderer.draw_calls > 0

            QTest.mouseClick(window.hide_all_layers_button, Qt.MouseButton.LeftButton)
            window.layer_list.item(0).setCheckState(Qt.CheckState.Checked)
            assert canvas.visible_layers == {names[0]}
            assert window.show_all_layers_button.isEnabled() == (layer_count > 1)
            assert window.hide_all_layers_button.isEnabled()
            canvas.grabFramebuffer()
        else:
            QTest.mouseClick(window.show_all_layers_button, Qt.MouseButton.LeftButton)
            QTest.mouseClick(window.hide_all_layers_button, Qt.MouseButton.LeftButton)
            update.assert_not_called()
        assert canvas.renderer.upload_count == 1
        upload.assert_not_called()
        sub_upload.assert_not_called()
    finally:
        window.close()
        app.processEvents()


def test_white_canvas_and_same_layer_zone_trace_pad_transparency(monkeypatch):
    from unittest.mock import Mock

    from OpenGL import GL
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication

    from pyedb.viewer import LayoutScene, SceneLayer, ScenePad, ScenePolygon, SceneTrace
    from pyedb.viewer.colors import net_color
    from pyedb.viewer.mesh import prepare_scene
    from pyedb.viewer.qt.canvas import LayoutView

    scene = LayoutScene(
        (SceneLayer("copper", (0, 0, 1, 1)),),
        (ScenePolygon(1, "copper", "zone", ((-5, -5), (5, -5), (5, 5), (-5, 5))),),
        traces=(SceneTrace(2, "copper", "trace", (-4, 0), (4, 0), 3),),
        pads=(ScenePad(3, "copper", "pad", (0, 0), (2, 2)),),
        net_names=("zone", "trace", "pad"),
    )
    app = QApplication.instance() or QApplication([])
    view = LayoutView(scene)
    view.show_grid = False  # Exact geometry fixtures exclude the decorative grid.
    view.resize(640, 480)
    view.set_prepared(prepare_scene(scene))
    view.show()
    try:
        QTest.qWait(60)
        view.grabFramebuffer()
        upload = Mock(wraps=GL.glBufferData)
        sub_upload = Mock(wraps=GL.glBufferSubData)
        monkeypatch.setattr(GL, "glBufferData", upload)
        monkeypatch.setattr(GL, "glBufferSubData", sub_upload)

        def rgb(image, x, y):
            px, py = view.camera.world_to_screen(x, y)
            pixel = image.pixelColor(round(px * view.devicePixelRatioF()), round(py * view.devicePixelRatioF()))
            return pixel.red(), pixel.green(), pixel.blue()

        def over(source, destination, alpha):
            return tuple(255 * source[i] * alpha + destination[i] * (1 - alpha) for i in range(3))

        for alpha in (0.25, 0.5, 1.0):
            view.opacity = alpha
            frame = view.grabFramebuffer()
            zone = over(net_color(1), (255, 255, 255), alpha)
            trace = over(net_color(2), zone, alpha)
            pad = over(net_color(3), trace, alpha)
            assert rgb(frame, 7, 4) == (255, 255, 255)
            assert rgb(frame, 4, 4) == pytest.approx(zone, abs=2)
            assert rgb(frame, 3, 0) == pytest.approx(trace, abs=2)
            assert rgb(frame, 0, 0) == pytest.approx(pad, abs=2)
        view.color_by_net = False
        assert rgb(view.grabFramebuffer(), 0, 0) == (0, 0, 255)
        assert view.renderer.upload_count == 1
        upload.assert_not_called()
        sub_upload.assert_not_called()
        assert view.error is None, view.error
    finally:
        view.cleanup()
        view.close()
        app.processEvents()


def test_workspace_search_theme_and_display_controls_preserve_scene_state(monkeypatch):
    from unittest.mock import Mock

    from OpenGL import GL
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QPalette
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication, QWidget

    from pyedb.viewer import launch_viewer
    from pyedb.viewer.demo import demo_scene

    app = QApplication.instance() or QApplication([])
    host = QWidget()
    original_palette = host.palette().color(QPalette.ColorRole.Window)
    original_app_style = app.styleSheet()
    window = launch_viewer(scene=demo_scene(), block=False)
    try:
        QTest.qWait(140)
        canvas = window.canvas
        canvas.grabFramebuffer()
        assert canvas.error is None, canvas.error
        assert host.palette().color(QPalette.ColorRole.Window) == original_palette
        assert app.styleSheet() == original_app_style
        assert not window.menuBar().isVisible()
        assert window.view_options_button.menu() is not None
        assert window.opacity_readout.text() == "75%"
        assert canvas.opacity == 0.75
        assert window.dockWidgetArea(window.layers_dock) == Qt.DockWidgetArea.LeftDockWidgetArea
        assert window.dockWidgetArea(window.networks_dock) == Qt.DockWidgetArea.RightDockWidgetArea
        assert not hasattr(window.layer_panel, "search")
        assert window.color_control.geometry().center().y() == window.opacity_control.geometry().center().y()
        assert window.layer_panel.counter.text() == "1 / 3"
        assert window.layer_panel.geometry().top() >= window.layer_panel.header.geometry().bottom()
        upload = Mock(wraps=GL.glBufferData)
        monkeypatch.setattr(GL, "glBufferData", upload)
        canvas.camera.pan(15, 9)
        position = canvas.camera.center_x, canvas.camera.center_y, canvas.camera.scale
        panel = window.network_panel
        search = panel.search
        canvas.setFocus()
        QTest.keyClick(canvas, Qt.Key.Key_F, Qt.KeyboardModifier.ControlModifier)
        assert search.hasFocus()
        QTest.keyClicks(search, "DATA")
        assert canvas.visible_layers == {"TOP"}
        assert not canvas.camera.mirror  # Typing B must not flip the view.
        assert canvas.net is None
        rows = [
            row
            for row in range(1, window.network_list.count())
            if window.network_list.item(row).data(Qt.ItemDataRole.UserRole) == "DATA"
        ]
        assert len(rows) == 1
        assert not window.network_list.item(rows[0]).isHidden()
        window.network_list.setCurrentRow(rows[0])
        assert canvas.net == "DATA"
        assert panel.summary.text() == "DATA"
        QTest.mouseClick(window.show_all_layers_button, Qt.MouseButton.LeftButton)
        assert canvas.visible_layers == {"TOP", "INNER1", "BOTTOM"}
        assert window.layer_panel.counter.text() == "3 / 3"
        search.clear()
        search.setFocus()
        QTest.keyClicks(search, "f")
        assert (canvas.camera.center_x, canvas.camera.center_y, canvas.camera.scale) == position
        assert panel.counter.text() == f"0 / {len(panel.names)}"
        assert canvas.net == "DATA"
        assert not window.network_list.item(0).isHidden()
        assert all(window.network_list.item(i).isHidden() for i in range(1, window.network_list.count()))
        search.clear()
        assert all(not window.layer_list.item(i).isHidden() for i in range(3))
        window.network_list.setCurrentRow(0)
        assert canvas.net is None
        window.opacity_slider.setValue(45)
        assert canvas.opacity == 0.45
        assert window.opacity_readout.text() == "45%"
        canvas.grabFramebuffer()
        assert canvas.renderer.upload_count == 1
        upload.assert_not_called()
    finally:
        window.close()
        host.close()
        app.processEvents()


def test_shader_grid_is_world_anchored_and_uses_no_navigation_uploads(monkeypatch):
    from unittest.mock import Mock

    from OpenGL import GL
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication

    from pyedb.viewer import LayoutScene, SceneLayer
    from pyedb.viewer.mesh import prepare_scene
    from pyedb.viewer.qt.canvas import LayoutView

    app = QApplication.instance() or QApplication([])
    scene = LayoutScene((SceneLayer("metal", (1, 0, 0, 1)),), ())
    view = LayoutView(scene)
    view.resize(640, 480)
    view.set_prepared(prepare_scene(scene))
    view.message.hide()
    view.show()
    try:
        QTest.qWait(60)
        view.camera.center_x, view.camera.center_y, view.camera.scale = 0.37, -0.23, 10
        view.grabFramebuffer()
        upload = Mock(wraps=GL.glBufferData)
        sub_upload = Mock(wraps=GL.glBufferSubData)
        monkeypatch.setattr(GL, "glBufferData", upload)
        monkeypatch.setattr(GL, "glBufferSubData", sub_upload)

        def rgb(image, x, y):
            px, py = view.camera.world_to_screen(x, y)
            # Sample the nearest line column across subpixel-antialiasing phases.
            ix, iy = int(px * view.devicePixelRatioF()), int(py * view.devicePixelRatioF())
            pixels = [image.pixelColor(ix + dx, iy) for dx in (-1, 0, 1)]
            pixel = min(pixels, key=lambda value: value.red() + value.green() + value.blue())
            return pixel.red(), pixel.green(), pixel.blue()

        frame = view.grabFramebuffer()
        major, minor = rgb(frame, 0, 0.7), rgb(frame, 2, 0.7)
        assert 196 <= major[0] < minor[0] < 250
        assert major[0] == major[1] and major[2] > major[0] + 10
        assert minor[0] == minor[1] and minor[2] > minor[0] + 5
        assert rgb(frame, 0.5, 0.7) == (255, 255, 255)
        view.camera.pan(37, -19)
        panned = rgb(view.grabFramebuffer(), 0, 0.7)
        assert panned[0] < 230 and panned[2] > panned[0] + 10
        view.camera.zoom_at(320, 240, 4)
        view.camera.mirror = True
        zoomed = rgb(view.grabFramebuffer(), 0, 0.7)
        assert zoomed[0] < 230 and zoomed[2] > zoomed[0] + 10
        view.show_grid = False
        assert rgb(view.grabFramebuffer(), 0, 0.7) == (255, 255, 255)
        assert view.renderer.upload_count == 1
        upload.assert_not_called()
        sub_upload.assert_not_called()
        assert view.error is None, view.error
    finally:
        view.cleanup()
        assert view.renderer.grid.program == view.renderer.grid.vao == 0
        view.close()
        app.processEvents()


def test_component_frame_uses_reference_copper_color_without_white_halo():
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication

    from pyedb.viewer import LayoutScene, SceneComponent, SceneLayer
    from pyedb.viewer.mesh import prepare_scene
    from pyedb.viewer.qt.canvas import LayoutView

    app = QApplication.instance() or QApplication([])
    scene = LayoutScene(
        (SceneLayer("metal", (1, 0, 0, 1)),), (), components=(SceneComponent(1, "U1", "metal", (), (-4, -2, 4, 2)),)
    )
    view = LayoutView(scene)
    view.show_grid = False
    surface = view.format()
    surface.setSamples(0)
    view.setFormat(surface)
    view.resize(640, 480)
    view.set_prepared(prepare_scene(scene))
    view.show()
    try:
        QTest.qWait(60)
        for opacity in (0.25, 1.0):
            view.opacity = opacity
            frame = view.grabFramebuffer()
            x, y = view.camera.world_to_screen(-4, 0)
            pixel = frame.pixelColor(round(x * view.devicePixelRatioF()), round(y * view.devicePixelRatioF()))
            assert (pixel.red(), pixel.green(), pixel.blue()) == pytest.approx((184, 115, 51), abs=1)
        assert view.error is None, view.error
    finally:
        view.cleanup()
        view.close()
        app.processEvents()
