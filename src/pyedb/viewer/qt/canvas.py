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

"""Embeddable, on-demand OpenGL canvas with cursor-anchored navigation."""

from PySide6.QtCore import Qt, QTimer, Signal, Slot
from PySide6.QtGui import QSurfaceFormat
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QLabel

from pyedb.viewer.camera import Camera
from pyedb.viewer.qt.loading import LoadingPanel
from pyedb.viewer.qt.renderer import Renderer
from pyedb.viewer.qt.theme import COLORS


def layout_surface_format():
    """Return the core OpenGL format required by the layout canvas."""
    surface = QSurfaceFormat()
    surface.setVersion(3, 3)
    surface.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
    surface.setDepthBufferSize(24)
    surface.setStencilBufferSize(8)
    surface.setSamples(4)
    return surface


class LayoutView(QOpenGLWidget):
    """Display a detached scene inside an existing QApplication.

    Call ``set_prepared`` with ``prepare_scene(scene)`` to supply geometry.
    The standalone LayoutWindow does this asynchronously.
    """

    position_changed = Signal(float, float)
    rendering_failed = Signal(str)

    def __init__(self, scene, parent=None):
        super().__init__(parent)
        self.setFormat(layout_surface_format())
        self.scene = scene
        self.camera = Camera()
        self.renderer = Renderer()
        self.visible_layers = {scene.layers[0].name} if scene.layers else set()
        self.opacity = 0.75
        self.color_by_net = True
        self.show_grid = True
        self.show_components = True
        self.annotate_component_names = True
        self.components_on_both_sides = True
        self.fit_padding = (0, 0, 0, 0)
        self.net = None
        self.error = None
        self._prepared = None
        self._layer_prepared = {}
        self._pending_layers = set()
        self._pending_upload = False
        self._drag_position = None
        self._drag_button = Qt.MouseButton.NoButton
        self._fitted = False
        self._loading_complete = True
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAccessibleName("PCB layout canvas")
        self.setToolTip("Left/middle/right drag: pan · Wheel: zoom · F: fit · Arrow keys: pan · +/-: zoom")
        self.loading = LoadingPanel(self)
        self.loading.hide()
        self.message = QLabel(self)
        self.message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message.setWordWrap(True)
        self.message.setStyleSheet(
            f"background: {COLORS['panel']}; color: {COLORS['text']}; border: 1px solid {COLORS['border']}; "
            "border-radius: 12px; padding: 20px;"
        )
        self.message.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.message.hide()

    @Slot(str, int, int)
    def set_progress(self, stage, current, total):
        if not self.error:
            if stage == "Rendering layout" and total:
                total += 1  # The first upload/draw completes the display stage.
            self.loading.set_progress(stage, current, total)

    def set_prepared(self, prepared, *, final=True):
        self._prepared = prepared
        self._loading_complete = final
        self._pending_upload = True
        if not final:
            self.loading.set_compact()
            self._position_loading()
        if not self.error:
            self.message.setVisible(not bool(prepared.batches or len(prepared.instances)))
            self.message.setText("No geometry matches this layout selection.")
        self.update()

    def begin_layer_loading(self, name=None):
        self._loading_complete = False
        self.loading.clock.restart()
        if self._prepared is not None:
            self.loading.set_compact()
        self.loading.setAccessibleDescription(f"Loading layer {name}" if name else "Loading initial layer")
        self.set_progress("Reading polygons", 0, 0)
        self._position_loading()
        self._show_loading()

    def set_layer_prepared(self, name, prepared, *, final=True):
        self._layer_prepared[name] = prepared
        self._pending_layers.add(name)
        self._prepared = prepared
        self._pending_upload = True
        self._loading_complete = final
        if not final:
            self.loading.set_compact()
            self._position_loading()
        self.message.setVisible(
            not any(
                part.batches or len(part.instances) or part.component_batches for part in self._layer_prepared.values()
            )
        )
        self.message.setText("No geometry matches this layout selection.")
        self.update()

    def fail(self, error):
        self.error = str(error)
        self.loading.hide()
        self.message.setText(f"Layout viewer unavailable\n\n{self.error}")
        self.message.show()
        self.rendering_failed.emit(self.error)

    def initializeGL(self):
        try:
            self.renderer.initialize()
            self.context().aboutToBeDestroyed.connect(self.cleanup)
            self._pending_upload = self._prepared is not None
            self._pending_layers = set(self._layer_prepared)
        except Exception as exc:
            self.renderer.release()
            self.fail(exc)

    def paintGL(self):
        if self.error:
            return
        try:
            # A closed window can be shown again with the same Qt context.
            if not self.renderer.program:
                self.renderer.initialize()
                self._pending_upload = self._prepared is not None
                self._pending_layers = set(self._layer_prepared)
            if self._pending_upload:
                if self._layer_prepared:
                    for name in self._pending_layers:
                        self.renderer.upload_layer(name, self._layer_prepared[name])
                    self._pending_layers.clear()
                else:
                    self.renderer.upload(self._prepared)
                self._pending_upload = False
            self.renderer.draw(
                self.scene,
                self.camera,
                self.visible_layers,
                self.opacity,
                self.net,
                self.devicePixelRatioF(),
                self.color_by_net,
                show_components=self.show_components,
                components_on_both_sides=self.components_on_both_sides,
                annotate_component_names=self.annotate_component_names,
                show_grid=self.show_grid,
            )
            if (self.renderer.prepared is not None or self.renderer.layer_renderers) and self._loading_complete:
                self.loading.hide()
        except Exception as exc:
            self.fail(exc)

    def resizeGL(self, width, height):
        # QOpenGLWidget's GL dimensions may be physical pixels on high-DPI displays.
        # Navigation and shader projection consistently use logical widget pixels.
        self.camera.resize(self.width(), self.height())
        if not self._fitted:
            self.fit_all()
            self._fitted = True

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.message.setGeometry(20, max(20, self.height() // 2 - 55), max(1, self.width() - 40), 110)
        self._position_loading()

    def _position_loading(self):
        width = min(380, max(1, self.width() - 32))
        height = self.loading.sizeHint().height()
        y = 16 if self.loading.compact else max(16, (self.height() - height) // 2)
        self.loading.setGeometry((self.width() - width) // 2, y, width, height)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(100, self._check_context)
        QTimer.singleShot(150, self._show_loading)

    def _show_loading(self):
        if self.isVisible() and (self._prepared is None or not self._loading_complete) and not self.error:
            self.loading.show()
            self.loading.raise_()

    def _check_context(self):
        if self.isVisible() and not self.isValid() and not self.error:
            self.fail("Could not create an OpenGL 3.3 context. Check the desktop graphics driver.")

    def fit_all(self):
        self.camera.resize(self.width(), self.height())
        self.camera.fit(self.scene.bounds, padding=self.fit_padding)
        self.update()

    def zoom(self, factor):
        self.camera.zoom_at(self.width() / 2, self.height() / 2, factor)
        self.update()

    def wheelEvent(self, event):
        steps = event.angleDelta().y() / 120.0
        if not steps:
            steps = event.pixelDelta().y() / 40.0
        self.camera.zoom_at(event.position().x(), event.position().y(), 1.2 ** max(-10.0, min(10.0, steps)))
        self.update()
        event.accept()

    def mousePressEvent(self, event):
        self.setFocus()
        if event.button() in (Qt.MouseButton.LeftButton, Qt.MouseButton.MiddleButton, Qt.MouseButton.RightButton):
            if self._drag_position is None:
                self._drag_position = event.position()
                self._drag_button = event.button()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        dragging = self._drag_position is not None and bool(event.buttons() & self._drag_button)
        if dragging:
            delta = event.position() - self._drag_position
            self.camera.pan(delta.x(), delta.y())
            self._drag_position = event.position()
            self.update()
        elif self._drag_position is not None:
            self._end_pan()
        self.position_changed.emit(*self.camera.screen_to_world(event.position().x(), event.position().y()))
        if dragging:
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == self._drag_button:
            self._end_pan()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def _end_pan(self):
        self._drag_position = None
        self._drag_button = Qt.MouseButton.NoButton
        self.unsetCursor()

    def focusOutEvent(self, event):
        self._end_pan()
        super().focusOutEvent(event)

    def hideEvent(self, event):
        self._end_pan()
        super().hideEvent(event)

    def keyPressEvent(self, event):
        pans = {Qt.Key.Key_Left: (60, 0), Qt.Key.Key_Right: (-60, 0), Qt.Key.Key_Up: (0, 60), Qt.Key.Key_Down: (0, -60)}
        if event.key() in pans:
            self.camera.pan(*pans[event.key()])
            self.update()
        elif event.key() in (Qt.Key.Key_Plus, Qt.Key.Key_Equal):
            self.zoom(1.2)
        elif event.key() == Qt.Key.Key_Minus:
            self.zoom(1 / 1.2)
        elif event.key() in (Qt.Key.Key_F, Qt.Key.Key_Home):
            self.fit_all()
        else:
            super().keyPressEvent(event)
            return
        event.accept()

    def cleanup(self):
        if self.context() is None or not self.renderer.program:
            return
        self.makeCurrent()
        try:
            self.renderer.release()
            self._pending_upload = self._prepared is not None
        finally:
            self.doneCurrent()
