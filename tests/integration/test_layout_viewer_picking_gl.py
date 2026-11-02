# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT

"""Native click/inspector tests and resident-mask highlight pixel checks."""

import gc
import os
import time

import numpy as np
import pytest

pytestmark = [
    pytest.mark.integration,
    pytest.mark.no_licence,
    pytest.mark.skipif(os.environ.get("PYEDB_VIEWER_GL_TESTS") != "1", reason="Requires desktop OpenGL"),
]


@pytest.fixture(autouse=True)
def _collect_gl_garbage():
    # Free cyclic Qt/GL garbage between tests, not mid-way through another test's native window creation.
    yield
    gc.collect()


def _pixels(view):
    from PySide6.QtGui import QImage

    image = view.grabFramebuffer().convertToFormat(QImage.Format.Format_RGBA8888)
    return np.frombuffer(image.constBits(), dtype=np.uint8).reshape(image.height(), image.width(), 4).copy()


def test_click_highlight_properties_clear_and_no_geometry_uploads():
    from PySide6.QtCore import QPoint, Qt
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication

    from pyedb.viewer.demo import demo_scene
    from pyedb.viewer.mesh import prepare_scene
    from pyedb.viewer.qt.canvas import LayoutView

    app = QApplication.instance() or QApplication([])
    scene = demo_scene()
    view = LayoutView(scene)
    view.show_grid = view.show_components = view.show_outlines = False
    view.opacity = 1
    view.resize(800, 600)
    view.set_prepared(prepare_scene(scene))
    view.show()
    try:
        QTest.qWait(100)
        original = _pixels(view)
        uploads = view.renderer.upload_count
        buffers = view.renderer.vbo, view.renderer.ebo, view.renderer.sdf.vbo

        def click(point):
            x, y = view.camera.world_to_screen(*point)
            QTest.mouseClick(view, Qt.MouseButton.LeftButton, pos=QPoint(round(x), round(y)))
            QTest.qWait(20)
            view.grabFramebuffer()

        click((35, -14))
        assert view.selection.key == ("trace", 50)
        assert view.inspector.isVisible() and view.inspector.parent() is view
        assert view.inspector.values["Signal"] == "SIGNAL"
        assert view.inspector.values["Width"] == "0.6500 mm"
        assert view.inspector.values["Length"] == "14.0000 mm"
        selected = _pixels(view)
        changed = np.any(original[:, :, :3] != selected[:, :, :3], axis=2)
        from pyedb.viewer.colors import SELECTION_COLOR

        selected_color = np.asarray(SELECTION_COLOR) * 255
        colored = np.max(np.abs(selected[:, :, :3].astype(float) - selected_color), axis=2) < 28
        assert np.count_nonzero(changed & colored) > 15
        assert view.inspector.geometry().right() < view.width()
        assert view.inspector.geometry().bottom() < view.height()

        click((28, -14))
        assert view.selection.key == ("via", 70)
        assert view.inspector.values["Net"] == "SIGNAL"
        assert view.inspector.values["From layer"] == "TOP"
        assert view.inspector.values["To layer"] == "BOTTOM"
        before = _pixels(view)
        x, y = view.camera.world_to_screen(28, -14)
        ratio = view.devicePixelRatioF()
        px, py = round(x * ratio), round(y * ratio)
        np.testing.assert_array_equal(before[py, px], original[py, px])

        click((-33, 20))
        assert view.selection.key == ("pad", 110)
        assert view.inspector.values["Component"] == "J1"
        assert view.inspector.values["Pin"] == "1"
        click((-40, 0))
        assert view.selection.key == ("zone", 3)
        assert view.inspector.values["Net"] == "GND"
        with_zone = _pixels(view)
        x, y = view.camera.world_to_screen(0, 5)
        np.testing.assert_array_equal(
            with_zone[round(y * ratio), round(x * ratio)], original[round(y * ratio), round(x * ratio)]
        )
        QTest.keyClick(view, Qt.Key.Key_Escape)
        assert view.selection is None and view.inspector.isHidden()
        np.testing.assert_array_equal(_pixels(view), original)
        assert view.renderer.upload_count == uploads
        assert (view.renderer.vbo, view.renderer.ebo, view.renderer.sdf.vbo) == buffers
        assert view.error is None
    finally:
        view.cleanup()
        view.close()
        app.processEvents()


def test_electric_hover_and_raspberry_selection_use_resident_geometry():
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication

    from pyedb.viewer.demo import demo_scene
    from pyedb.viewer.mesh import prepare_scene
    from pyedb.viewer.qt.canvas import LayoutView

    app = QApplication.instance() or QApplication([])
    scene = demo_scene()
    view = LayoutView(scene)
    view.resize(800, 600)
    view.show_grid = view.show_components = view.show_outlines = False
    view.opacity = 1
    view.set_prepared(prepare_scene(scene))
    view.show()
    try:
        QTest.qWait(100)
        original = _pixels(view)
        view.hover = view._pick_index.pick((28, -14), view.camera.scale, view.visible_layers)
        hover = _pixels(view)
        changed = np.any(original[:, :, :3] != hover[:, :, :3], axis=2)
        from pyedb.viewer.colors import HOVER_COLOR

        hover_color = np.asarray(HOVER_COLOR) * 255
        colored = np.max(np.abs(hover[:, :, :3].astype(float) - hover_color), axis=2) < 28
        assert np.count_nonzero(changed & colored) > 5
        view.hover = None
        view.visible_layers = {"BOTTOM"}
        x, y = view.camera.world_to_screen(28, -14)
        view.pick_at(x, y)
        assert view.selection.layer == "BOTTOM"
        view.net = "DATA"
        view.grabFramebuffer()
        assert view.selection is None and view.inspector.isHidden()
        assert view.error is None
    finally:
        view.cleanup()
        view.close()
        app.processEvents()


def test_pick_tool_and_drag_threshold_do_not_conflict_with_navigation():
    from PySide6.QtCore import QPointF, Qt
    from PySide6.QtGui import QMouseEvent
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication

    from pyedb.viewer.demo import demo_scene
    from pyedb.viewer.qt.app import show_scene

    app = QApplication.instance() or QApplication([])
    window = show_scene(scene=demo_scene(), block=False)
    try:
        deadline = time.monotonic() + 5
        while window.canvas._prepared is None and time.monotonic() < deadline:
            QTest.qWait(10)
        view = window.canvas
        view.grabFramebuffer()
        assert window.pick_action.isChecked()
        x, y = view.camera.world_to_screen(35, -14)
        start = QPointF(x, y)
        center = view.camera.center_x, view.camera.center_y
        press = QMouseEvent(
            QMouseEvent.Type.MouseButtonPress,
            start,
            start,
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
        view.mousePressEvent(press)
        tiny = start + QPointF(2, 1)
        view.mouseMoveEvent(
            QMouseEvent(
                QMouseEvent.Type.MouseMove,
                tiny,
                tiny,
                Qt.MouseButton.NoButton,
                Qt.MouseButton.LeftButton,
                Qt.KeyboardModifier.NoModifier,
            )
        )
        assert (view.camera.center_x, view.camera.center_y) == center
        end = start + QPointF(30, 20)
        view.mouseMoveEvent(
            QMouseEvent(
                QMouseEvent.Type.MouseMove,
                end,
                end,
                Qt.MouseButton.NoButton,
                Qt.MouseButton.LeftButton,
                Qt.KeyboardModifier.NoModifier,
            )
        )
        view.mouseReleaseEvent(
            QMouseEvent(
                QMouseEvent.Type.MouseButtonRelease,
                end,
                end,
                Qt.MouseButton.LeftButton,
                Qt.MouseButton.NoButton,
                Qt.KeyboardModifier.NoModifier,
            )
        )
        assert (view.camera.center_x, view.camera.center_y) != center
        assert view.selection is None
        QTest.keyClick(view, Qt.Key.Key_P)
        assert not window.pick_action.isChecked() and not view.pick_enabled
        QTest.keyClick(view, Qt.Key.Key_P)
        assert view.pick_enabled
        view.pick_at(*view.camera.world_to_screen(35, -14))
        view.grabFramebuffer()
        QTest.keyClick(view.inspector.close_button, Qt.Key.Key_Escape)
        assert view.selection is None
    finally:
        window.close()
        app.processEvents()


def test_property_card_switches_immediately_and_stacks_on_narrow_canvas():
    from PySide6.QtWidgets import QApplication, QLabel

    from pyedb.viewer.demo import demo_scene
    from pyedb.viewer.mesh import prepare_scene
    from pyedb.viewer.qt.canvas import LayoutView

    app = QApplication.instance() or QApplication([])
    scene = demo_scene()
    view = LayoutView(scene)
    view.resize(800, 600)
    view.set_prepared(prepare_scene(scene))
    view.show()
    try:
        view.grabFramebuffer()
        view.pick_at(*view.camera.world_to_screen(35, -14))
        view.pick_at(*view.camera.world_to_screen(-33, 20))
        visible_text = {label.text() for label in view.inspector.body.findChildren(QLabel) if not label.isHidden()}
        assert "Component" in visible_text and "J1" in visible_text and "1" in visible_text
        assert not {"Signal", "Width", "Length"}.intersection(visible_text)
        view.resize(220, 240)
        view.camera.resize(220, 240)
        view.fit_all()
        view.pick_at(*view.camera.world_to_screen(28, -14))
        view.grabFramebuffer()
        assert view.inspector._stacked
        assert view.inspector.geometry().right() < view.width()
        assert view.inspector.geometry().bottom() < view.height()
        assert view.inspector.scroll.verticalScrollBar().maximum() > 0
    finally:
        view.cleanup()
        view.close()
        app.processEvents()


def test_selection_rebinds_to_complete_progressive_snapshot():
    from dataclasses import replace

    from PySide6.QtWidgets import QApplication

    from pyedb.viewer.demo import demo_scene
    from pyedb.viewer.mesh import prepare_scene
    from pyedb.viewer.qt.canvas import LayoutView

    app = QApplication.instance() or QApplication([])
    scene = demo_scene()
    preview = replace(scene, pads=(), components=())
    view = LayoutView(preview)
    view.resize(800, 600)
    first = prepare_scene(preview)
    view.set_prepared(first, final=False)
    view.show()
    try:
        view.grabFramebuffer()
        view.pick_at(*view.camera.world_to_screen(35, -14))
        assert view.selection.key == ("trace", 50)
        original = view.selection.object
        view.scene = scene
        complete = prepare_scene(scene, polygon_mesh=(preview, first))
        view.set_prepared(complete)
        view.grabFramebuffer()
        assert view.selection.key == ("trace", 50)
        assert view.selection.object is not original
        assert view.selection.object is complete.picking.by_key["trace", 50]
        assert view.inspector.values["Length"] == "14.0000 mm"
        assert view.error is None
    finally:
        view.cleanup()
        view.close()
        app.processEvents()
