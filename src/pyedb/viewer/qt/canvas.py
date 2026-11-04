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

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QEvent, QLineF, Qt, QTimer, Signal, Slot
from PySide6.QtGui import (
    QFocusEvent,
    QHideEvent,
    QKeyEvent,
    QMouseEvent,
    QResizeEvent,
    QShowEvent,
    QSurfaceFormat,
    QWheelEvent,
)
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QLabel, QWidget

from pyedb.viewer.camera import Camera
from pyedb.viewer.picking import PickHit
from pyedb.viewer.qt.inspector import ObjectInspector
from pyedb.viewer.qt.loading import LoadingPanel
from pyedb.viewer.qt.renderer import Renderer
from pyedb.viewer.qt.theme import COLORS

if TYPE_CHECKING:
    from pyedb.viewer.mesh import PreparedScene
    from pyedb.viewer.picking import PickedObject, PickObject
    from pyedb.viewer.scene import Bounds, LayoutScene


def layout_surface_format() -> QSurfaceFormat:
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
    selection_changed = Signal(object)
    hover_changed = Signal(object)

    def __init__(self, scene: LayoutScene, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFormat(layout_surface_format())
        self.scene = scene
        self.camera = Camera()
        self.renderer = Renderer()
        self.visible_layers = {scene.layers[0].name} if scene.layers else set()
        self.opacity = 0.75
        self.color_by_net = True
        self.show_grid = True
        self.show_outlines = True
        self.show_components = True
        self.annotate_component_names = True
        self.components_on_both_sides = True
        self.fit_padding = (0, 0, 0, 0)
        self.net = None
        self.error = None
        self._prepared = None
        self._pending_upload = False
        self._drag_position = None
        self._drag_button = Qt.MouseButton.NoButton
        self._press_position = None
        self._dragging = False
        self.pick_enabled = True
        self.selection = self.hover = None
        self._notified_selection = self._notified_hover = None
        self._selection_anchor = None
        self._pick_index = None
        self._hover_position = None
        self._hover_timer = QTimer(self)
        self._hover_timer.setSingleShot(True)
        self._hover_timer.setInterval(24)
        self._hover_timer.timeout.connect(self._pick_hover)
        self._fitted = False
        self._loading_complete = True
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAccessibleName("PCB layout canvas")
        self.setToolTip("Click: inspect · Drag: pan · Wheel: zoom · Esc: clear · P: pick tool · F: fit")
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
        self.inspector = ObjectInspector(self)
        self.inspector.cleared.connect(self.clear_selection)

    @Slot(str, int, int)
    def set_progress(self, stage: str, current: int, total: int) -> None:
        if not self.error:
            if stage == "Rendering layout" and total:
                total += 1  # The first upload/draw completes the display stage.
            self.loading.set_progress(stage, current, total)

    def set_prepared(self, prepared: PreparedScene, *, final: bool = True) -> None:
        self._pick_index = getattr(prepared, "picking", None)
        self.hover = None
        self._notify_hover()
        if self.selection is not None:
            obj = self._pick_index.by_key.get(self.selection.key) if self._pick_index is not None else None
            if obj is not None:
                item = next((item for item in obj.items if item.layer == self.selection.layer), obj.items[0])
                self.selection = PickHit(obj, item, 0)
                self.inspector.set_hit(self.selection)
            else:
                self.clear_selection()
        self._notify_selection()
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

    def fail(self, error: object) -> None:
        self.error = str(error)
        self.loading.hide()
        self.message.setText(f"Layout viewer unavailable\n\n{self.error}")
        self.message.show()
        self.rendering_failed.emit(self.error)

    def initializeGL(self) -> None:
        try:
            self.renderer.initialize()
            self.context().aboutToBeDestroyed.connect(self.cleanup)
            self._pending_upload = self._prepared is not None
        except Exception as exc:
            self.renderer.release()
            self.fail(exc)

    def paintGL(self) -> None:
        if self.error:
            return
        try:
            # A closed window can be shown again with the same Qt context.
            if not self.renderer.program:
                self.renderer.initialize()
                self._pending_upload = self._prepared is not None
            if self._pending_upload:
                self.renderer.upload(self._prepared)
                self._pending_upload = False
            if self.selection is not None and not self._hit_visible(self.selection):
                self.clear_selection()
            elif self.selection is not None and self.selection.layer not in self.visible_layers:
                item = next(item for item in self.selection.object.items if item.layer in self.visible_layers)
                self.selection = PickHit(self.selection.object, item, 0)
                self.inspector.set_hit(self.selection)
            if self.hover is not None and not self._hit_visible(self.hover):
                self.hover = None
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
                selection=self.selection,
                hover=self.hover,
                show_outlines=self.show_outlines,
            )
            self._position_inspector()
            if self.renderer.prepared is not None and self._loading_complete:
                self.loading.hide()
        except Exception as exc:
            self.fail(exc)

    def resizeGL(self, width: int, height: int) -> None:
        # QOpenGLWidget's GL dimensions may be physical pixels on high-DPI displays.
        # Navigation and shader projection consistently use logical widget pixels.
        self.camera.resize(self.width(), self.height())
        if not self._fitted:
            self.fit_all()
            self._fitted = True

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self.message.setGeometry(20, max(20, self.height() // 2 - 55), max(1, self.width() - 40), 110)
        self._position_loading()
        if hasattr(self, "inspector"):
            self._position_inspector()

    def _position_loading(self) -> None:
        width = min(380, max(1, self.width() - 32))
        height = self.loading.sizeHint().height()
        y = 16 if self.loading.compact else max(16, (self.height() - height) // 2)
        self.loading.setGeometry((self.width() - width) // 2, y, width, height)

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        QTimer.singleShot(100, self._check_context)
        QTimer.singleShot(150, self._show_loading)

    def _show_loading(self) -> None:
        if self.isVisible() and (self._prepared is None or not self._loading_complete) and not self.error:
            self.loading.show()
            self.loading.raise_()

    def _check_context(self) -> None:
        if self.isVisible() and not self.isValid() and not self.error:
            self.fail("Could not create an OpenGL 3.3 context. Check the desktop graphics driver.")

    def fit_all(self) -> None:
        self.camera.resize(self.width(), self.height())
        self.camera.fit(self.scene.bounds, padding=self.fit_padding)
        self.update()

    def zoom_to_bounds(self, bounds: Bounds) -> None:
        """Fit world bounds with a margin, so tiny objects are not zoomed to the limit."""
        x0, y0, x1, y1 = bounds
        margin = max(0.25 * max(x1 - x0, y1 - y0), 0.05)
        self.camera.resize(self.width(), self.height())
        self.camera.fit((x0 - margin, y0 - margin, x1 + margin, y1 + margin), padding=self.fit_padding)
        self._position_inspector()
        self.update()

    def zoom(self, factor: float) -> None:
        self.camera.zoom_at(self.width() / 2, self.height() / 2, factor)
        self.update()

    def wheelEvent(self, event: QWheelEvent) -> None:
        self._clear_hover()
        steps = event.angleDelta().y() / 120.0
        if not steps:
            steps = event.pixelDelta().y() / 40.0
        self.camera.zoom_at(event.position().x(), event.position().y(), 1.2 ** max(-10.0, min(10.0, steps)))
        self.update()
        event.accept()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.setFocus()
        if event.button() in (Qt.MouseButton.LeftButton, Qt.MouseButton.MiddleButton, Qt.MouseButton.RightButton):
            if self._drag_position is None:
                self._drag_position = event.position()
                self._press_position = event.position()
                self._drag_button = event.button()
                self._dragging = event.button() != Qt.MouseButton.LeftButton or not self.pick_enabled
            self._clear_hover()
            if self._dragging:
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        dragging = self._drag_position is not None and bool(event.buttons() & self._drag_button)
        if dragging:
            if not self._dragging and QLineF(self._press_position, event.position()).length() > 4:
                self._dragging = True
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
            if self._dragging:
                delta = event.position() - self._drag_position
                self.camera.pan(delta.x(), delta.y())
                self._drag_position = event.position()
                self.update()
        elif self._drag_position is not None:
            self._end_pan()
        elif self.pick_enabled:
            self._hover_position = event.position()
            if not self._hover_timer.isActive():
                self._hover_timer.start()
        self.position_changed.emit(*self.camera.screen_to_world(event.position().x(), event.position().y()))
        if dragging:
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == self._drag_button:
            click = self.pick_enabled and event.button() == Qt.MouseButton.LeftButton and not self._dragging
            self._end_pan()
            if click:
                self.pick_at(event.position().x(), event.position().y())
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def _end_pan(self) -> None:
        self._drag_position = None
        self._drag_button = Qt.MouseButton.NoButton
        self._press_position = None
        self._dragging = False
        if self.pick_enabled:
            self.unsetCursor()
        else:
            self.setCursor(Qt.CursorShape.OpenHandCursor)

    def focusOutEvent(self, event: QFocusEvent) -> None:
        self._end_pan()
        super().focusOutEvent(event)

    def hideEvent(self, event: QHideEvent) -> None:
        self._end_pan()
        super().hideEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.clear_selection()
            self._clear_hover()
            event.accept()
            return
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

    def _hit_visible(self, hit: PickHit) -> bool:
        return self.opacity > 0 and any(
            item.layer in self.visible_layers and (self.net is None or item.net == self.net)
            for item in hit.object.items
        )

    def _hit(self, x: float, y: float) -> PickHit | None:
        if self._pick_index is None or not self.pick_enabled:
            return None
        return self._pick_index.pick(
            self.camera.screen_to_world(x, y),
            self.camera.scale,
            self.visible_layers,
            net=self.net,
            opacity=self.opacity,
            mirror=self.camera.mirror,
        )

    def pick_at(self, x: float, y: float) -> PickHit | None:
        """Pick in logical canvas pixels; no EDB access or geometry upload."""
        self._clear_hover()
        self.selection = self._hit(x, y)
        if self.selection is None:
            self.clear_selection()
        else:
            self._selection_anchor = self.camera.screen_to_world(x, y)
            self.inspector.set_hit(self.selection)
            self._position_inspector()
        self.update()
        self._notify_selection()
        return self.selection

    def clear_selection(self) -> None:
        self.selection = None
        self._selection_anchor = None
        self.inspector.hide()
        self.update()
        self._notify_selection()

    def find_object(self, object_id: int, kind: str | None = None) -> PickObject:
        """Return the picking object for a source object id, or raise ``ValueError``."""
        if self._pick_index is None:
            raise RuntimeError("The layout is still loading; objects can be selected once it is displayed.")
        by_key = self._pick_index.by_key
        kinds = (kind,) if kind is not None else ("trace", "via", "pad", "zone")
        matches = [by_key[(k, object_id)] for k in kinds if (k, object_id) in by_key]
        if not matches:
            raise ValueError(f"Unknown object id {object_id!r}" + (f" of kind {kind!r}." if kind else "."))
        if len(matches) > 1:
            raise ValueError(f"Object id {object_id!r} is ambiguous; specify kind.")
        return matches[0]

    def select_object(self, object_id: int, kind: str | None = None, layer: str | None = None) -> PickedObject:
        """Select an object as if it had been picked. Returns the ``PickedObject``."""
        obj = self.find_object(object_id, kind)
        if layer is None:
            item = next((item for item in obj.items if item.layer in self.visible_layers), obj.items[0])
        else:
            item = next((item for item in obj.items if item.layer == layer), None)
            if item is None:
                raise ValueError(f"Object {object_id!r} has no geometry on layer {layer!r}.")
        self._clear_hover()
        self.selection = PickHit(obj, item, 0.0)
        x0, y0, x1, y1 = item.bounds
        self._selection_anchor = ((x0 + x1) / 2, (y0 + y1) / 2)
        self.inspector.set_hit(self.selection)
        self._position_inspector()
        self.update()
        self._notify_selection()
        return self.selection.picked

    def _notify_selection(self) -> None:
        picked = None if self.selection is None else self.selection.picked
        if picked != self._notified_selection:
            self._notified_selection = picked
            self.selection_changed.emit(picked)

    def _notify_hover(self) -> None:
        picked = None if self.hover is None else self.hover.picked
        if picked != self._notified_hover:
            self._notified_hover = picked
            self.hover_changed.emit(picked)

    def _clear_hover(self) -> None:
        self._hover_timer.stop()
        self.hover = None
        self.update()
        self._notify_hover()

    def _pick_hover(self) -> None:
        if self._hover_position is not None and self._drag_position is None and self.underMouse():
            position = self._hover_position
            hit = self._hit(position.x(), position.y())
            if (None if hit is None else (hit.key, hit.layer)) != (
                None if self.hover is None else (self.hover.key, self.hover.layer)
            ):
                self.hover = hit
                self.update()
                self._notify_hover()
            self.setCursor(Qt.CursorShape.PointingHandCursor if hit is not None else Qt.CursorShape.ArrowCursor)

    def _position_inspector(self) -> None:
        if self.selection is None or self._selection_anchor is None:
            self.inspector.hide()
            return
        x, y = self.camera.world_to_screen(*self._selection_anchor)
        if not (0 <= x <= self.width() and 0 <= y <= self.height()):
            self.inspector.hide()
            return
        self.inspector.fit_canvas(self.width(), self.height())
        x += 16
        y += 16
        if x + self.inspector.width() > self.width() - 12:
            x -= self.inspector.width() + 32
        self.inspector.move(
            int(max(12, min(x, self.width() - self.inspector.width() - 12))),
            int(max(12, min(y, self.height() - self.inspector.height() - 12))),
        )
        self.inspector.show()
        self.inspector.raise_()

    def set_pick_enabled(self, enabled: bool) -> None:
        self.pick_enabled = enabled
        self._clear_hover()
        self._end_pan()

    def leaveEvent(self, event: QEvent) -> None:
        self._clear_hover()
        super().leaveEvent(event)

    def cleanup(self) -> None:
        if self.context() is None or not self.renderer.program:
            return
        self.makeCurrent()
        try:
            self.renderer.release()
            self._pending_upload = self._prepared is not None
        finally:
            self.doneCurrent()
