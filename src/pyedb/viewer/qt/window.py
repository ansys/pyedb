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

"""Native desktop controls around the GPU layout canvas."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from concurrent.futures import Future, ThreadPoolExecutor
from typing import TYPE_CHECKING
import weakref

from PySide6.QtCore import QObject, QRunnable, QSignalBlocker, QSize, Qt, QThreadPool, QTimer, Signal, Slot
from PySide6.QtGui import QAction, QCloseEvent, QFont, QResizeEvent
from PySide6.QtWidgets import (
    QComboBox,
    QDockWidget,
    QHBoxLayout,
    QLabel,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QSizePolicy,
    QSlider,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from pyedb.viewer.mesh import prepare_scene
from pyedb.viewer.progress import throttle_progress
from pyedb.viewer.qt.canvas import LayoutView
from pyedb.viewer.qt.icons import workspace_icon
from pyedb.viewer.qt.navigation import NavigationCapsule
from pyedb.viewer.qt.panels import ElidedLabel, LayerPanel, NetworkPanel
from pyedb.viewer.qt.theme import COLORS, apply_viewer_theme
from pyedb.viewer.scene import union_bounds

if TYPE_CHECKING:
    from pyedb.viewer.mesh import PreparedScene
    from pyedb.viewer.picking import PickedObject
    from pyedb.viewer.scene import LayoutScene


class _PreparationSignals(QObject):
    ready = Signal(object)
    failed = Signal(object)
    scene_ready = Signal(object)
    preview_ready = Signal(object, object)
    progress = Signal(str, int, int)


class _Prepare(QRunnable):
    def __init__(
        self,
        scene: LayoutScene,
        loader: Callable[..., LayoutScene] | None = None,
        *,
        previews=True,
        incremental=False,
        previous=None,
    ) -> None:
        super().__init__()
        self.scene = scene
        self.loader = loader
        self.previews = previews
        self.incremental = incremental
        self.previous = previous
        self.result = None
        self.preview_scene = self.preview_prepared = None
        self._preview_executor: ThreadPoolExecutor | None = None
        self._preview_jobs: list[Future[None]] = []
        self.signals = _PreparationSignals()

    @Slot()
    def run(self) -> None:
        try:
            progress = throttle_progress(self.signals.progress.emit)
            if self.loader is not None:
                # Only immutable geometry enters the CPU worker. The EDB
                # session remains on this single source-reading thread.
                with ThreadPoolExecutor(max_workers=1, thread_name_prefix="pyedb-mesh") as executor:
                    self._preview_executor = executor
                    if self.previews and hasattr(self.loader, "set_preview"):
                        self.loader.set_preview(self._queue_preview)
                    try:
                        if getattr(self.loader, "changes", None) is not None:
                            self.result = self.loader.capture(progress, previous=self.scene, full=not self.incremental)
                            self.scene = self.result.scene
                        else:
                            self.scene = self.loader(progress)
                    finally:
                        if hasattr(self.loader, "release_source"):
                            self.loader.release_source()
                    # Flush all previews before publishing the final snapshot;
                    # a delayed preview must never replace the finished scene.
                    for job in self._preview_jobs:
                        job.result()
                self._preview_executor = None
                progress("Rendering layout", 0, 0)
                _ = self.scene.bounds  # Cache derived bounds off the GUI thread.
                self.signals.scene_ready.emit(self.scene)
            mesh = (self.preview_scene, self.preview_prepared) if self.preview_prepared is not None else None
            if self.result is not None and self.result.patch is not None and self.previous is not None:
                from pyedb.viewer.incremental import prepare_incremental

                prepared = prepare_incremental(
                    self.scene, self.previous[0], self.previous[1], self.result.patch, self.result.changed
                )
            else:
                prepared = prepare_scene(self.scene, progress=progress, polygon_mesh=mesh)
            self.signals.ready.emit(prepared)
        except Exception as exc:
            self.signals.failed.emit(exc)

    def _queue_preview(self, scene: LayoutScene) -> None:
        if len(self._preview_jobs) >= 2:
            self._preview_jobs.pop(0).result()
        self._preview_jobs.append(self._preview_executor.submit(self._preview, scene))

    def _preview(self, scene: LayoutScene) -> None:
        _ = scene.bounds  # Cache derived bounds off the GUI thread.
        previous = (self.preview_scene, self.preview_prepared) if self.preview_prepared is not None else None
        prepared = prepare_scene(scene, polygon_mesh=previous)
        self.preview_scene = scene
        self.preview_prepared = prepared
        self.signals.preview_ready.emit(scene, self.preview_prepared)


class _ScriptSignals(QObject):
    finished = Signal(object)
    failed = Signal(object)


class _Script(QRunnable):
    def __init__(self, callback, args, kwargs):
        super().__init__()
        self.callback, self.args, self.kwargs = callback, args, kwargs
        self.signals = _ScriptSignals()

    @Slot()
    def run(self):
        try:
            result = self.callback(*self.args, **self.kwargs)
        except Exception as exc:
            self.signals.failed.emit(exc)
        else:
            self.signals.finished.emit(result)


class LayoutWindow(QMainWindow):
    """Layout viewer window.

    Signals report user interaction to application code; the public methods drive
    the view. Call methods on the GUI thread. Picked objects are detached
    ``PickedObject`` values and never query EDB.
    """

    scene_ready = Signal(object)
    scene_failed = Signal(object)
    refresh_finished = Signal(object)
    refresh_failed = Signal(object)
    script_finished = Signal(object)
    script_failed = Signal(object)
    _source_changed = Signal(int)
    object_selected = Signal(object)
    selection_cleared = Signal()
    object_hovered = Signal(object)
    net_changed = Signal(object)
    visible_layers_changed = Signal(object)

    def __init__(
        self,
        scene: LayoutScene,
        parent: QWidget | None = None,
        *,
        color_by_net: bool = True,
        plot_components: bool = True,
        annotate_component_names: bool = True,
        plot_components_on_both_side: bool = True,
        plot_outlines: bool = True,
        loader: Callable[..., LayoutScene] | None = None,
        backend: str | None = None,
        live: bool = False,
        refresh_interval: int = 50,
    ) -> None:
        super().__init__(parent)
        self._capturing = loader is not None
        self._capture_error = None
        self._has_preview = False
        self._close_after_capture = False
        self._source = loader if getattr(loader, "changes", None) is not None else None
        self._busy = True
        self._refreshing = False
        self._pending_refresh = False
        self._pending_full_refresh = False
        self._closed = False
        self._next_scene = None
        self._script = None
        self._unsubscribe = None
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setSingleShot(True)
        self._refresh_timer.setInterval(refresh_interval)
        self._refresh_timer.timeout.connect(self._start_refresh)
        self._source_changed.connect(self._queue_source_refresh)
        if live and self._source is not None:
            reference = weakref.ref(self)

            def changed(revision):
                window = reference()
                if window is not None and not window._closed:
                    window._source_changed.emit(revision)

            self._unsubscribe = self._source.changes.subscribe(changed)
        apply_viewer_theme(self)
        self.setWindowTitle(f"{scene.title} — PyEDB Layout Viewer")
        self.resize(1280, 800)
        self.setMinimumSize(640, 400)
        self.canvas = LayoutView(scene, self, backend=backend)
        self.canvas.setMinimumWidth(180)
        self.canvas.color_by_net = color_by_net
        self.canvas.show_components = plot_components
        self.canvas.annotate_component_names = annotate_component_names
        self.canvas.components_on_both_sides = plot_components_on_both_side
        self.canvas.show_outlines = plot_outlines
        self.setCentralWidget(self.canvas)
        self._build_toolbar(scene)
        self._build_layers(scene)
        self._build_networks(scene)
        self.coordinates = QLabel("X: —   Y: —   mm")
        self.coordinates.setObjectName("coordinateReadout")
        self.coordinates.setProperty("role", "muted")
        coordinates_font = QFont("Consolas")
        coordinates_font.setPixelSize(11)
        self.coordinates.setFont(coordinates_font)
        self.coordinates.setMinimumWidth(220)
        self.statusBar().setSizeGripEnabled(False)
        self.statusBar().setMinimumHeight(30)
        self.engine_badge = QLabel({"d3d11": "Direct3D 11", "vulkan": "Vulkan", "metal": "Metal"}[self.canvas.backend])
        self.engine_badge.setProperty("role", "engine")
        self.engine_badge.setToolTip("Qt RHI layout renderer")
        self.statusBar().addPermanentWidget(self.engine_badge)
        self.statusBar().addPermanentWidget(self.coordinates)
        self.statusBar().showMessage("Preparing layout…")
        self._stats_summary = "Preparing layout…"
        self._compact_stats = self._stats_summary
        self._render_error = None
        self.canvas.position_changed.connect(self._position_changed)
        self.canvas.rendering_failed.connect(self._rendering_failed)
        self.canvas.selection_changed.connect(self._selection_changed)
        self.canvas.hover_changed.connect(self.object_hovered)
        if self._capturing:
            self.canvas.set_progress("Reading polygons", 0, 0)
            self.layer_panel.empty_notice.setText("Loading layers…")
            self.layer_panel.summary.setText("Loading layer information…")
            self.layer_panel.setEnabled(False)
            self.network_panel.setEnabled(False)
        self._preparation = _Prepare(scene, loader)
        self._preparation.signals.ready.connect(self._prepared)
        self._preparation.signals.scene_ready.connect(self._scene_loaded)
        self._preparation.signals.preview_ready.connect(self._scene_preview)
        self._preparation.signals.failed.connect(self._load_failed)
        self._preparation.signals.progress.connect(self.canvas.set_progress)
        QThreadPool.globalInstance().start(self._preparation)

    @Slot(object)
    def _scene_loaded(self, scene: LayoutScene) -> None:
        self._capturing = False
        if self._refreshing:
            self._next_scene = scene
            return
        self._display_scene(scene, preserve_view=self._has_preview)
        self.scene_ready.emit(scene)

    @Slot(object, object)
    def _scene_preview(self, scene: LayoutScene, prepared: PreparedScene) -> None:
        if self._close_after_capture:
            return
        self._display_scene(scene, preserve_view=self._has_preview)
        self._has_preview = True
        self.canvas.set_prepared(prepared, final=False)

    def _display_scene(self, scene: LayoutScene, preserve_view: bool = False) -> None:
        previous_scene = self.canvas.scene
        visible = self.canvas.visible_layers
        selected_net = self.canvas.net
        search = self.network_panel.search.text() if preserve_view else ""
        self.canvas.scene = scene
        self.canvas.visible_layers = (
            visible.intersection(layer.name for layer in scene.layers)
            if preserve_view
            else {scene.layers[0].name}
            if scene.layers
            else set()
        )
        self.setWindowTitle(f"{scene.title} — PyEDB Layout Viewer")
        self.project_title.setText(scene.title)
        if not preserve_view or scene.layers != previous_scene.layers:
            self._set_layer_panel(scene)
        network_names = sorted(
            {item.net for item in scene.geometry if item.net is not None}
            | {net for component in scene.components for net in component.nets}
        )
        rebuild_networks = not preserve_view or network_names != self.network_panel.names
        if rebuild_networks:
            self._set_network_panel(scene)
        if preserve_view and rebuild_networks:
            with QSignalBlocker(self.network_list):
                self.canvas.net = None
                for index in range(self.network_list.count()):
                    if self.network_list.item(index).data(Qt.ItemDataRole.UserRole) == selected_net:
                        self.network_list.setCurrentRow(index)
                        self.canvas.net = selected_net
                        break
            self.network_panel._selection_changed(self.network_list.currentRow())
            self.network_panel.search.setText(search)
            if self.canvas.net != selected_net:
                self.net_changed.emit(self.canvas.net)
        has_components = bool(scene.components) or any(getattr(item, "component", None) for item in scene.geometry)
        sides = {component.side for component in scene.components}
        sides.update(item.component_side for item in scene.geometry if getattr(item, "component", None))
        self._components_separator.setVisible(has_components)
        self.components_action.setVisible(has_components)
        self.component_names_action.setVisible(bool(scene.components))
        self.both_sides_action.setVisible(len(sides) > 1)
        self.search_action.setEnabled(bool(self.network_panel.names))
        self.navigation.has_geometry = scene.bounds is not None
        for action in (self.fit_action, self.zoom_in_action, self.zoom_out_action):
            action.setEnabled(self.navigation.has_geometry)
        self.navigation.setVisible(self.navigation.has_geometry)
        self.navigation.reposition()
        if not preserve_view:
            self.canvas.fit_all()

    @Slot(object)
    def _load_failed(self, error: BaseException) -> None:
        capturing = self._capturing
        self._capturing = False
        if self._refreshing:
            # Keep the previous, usable snapshot on a refresh failure.
            self.statusBar().showMessage(f"Layout refresh failed: {error}")
            self.refresh_failed.emit(error)
        else:
            self.canvas.fail(error)
        if capturing and not self._refreshing:
            self._capture_error = error
            self.scene_failed.emit(error)
        self._finish_preparation()

    def refresh(self) -> None:
        """Asynchronously recapture the EDB session, preserving the current view.

        Repeated requests during a capture are merged into one subsequent
        refresh. ``refresh_finished(scene)`` fires after geometry and picking
        are prepared; ``refresh_failed(error)`` leaves the old snapshot intact.
        Call on the GUI thread while the Qt event loop is running.
        """
        if self._closed:
            raise RuntimeError("The layout viewer is closed.")
        if self._source is None:
            raise RuntimeError("Refresh requires a viewer opened from an EDB session.")
        if self._source.changes.closed:
            raise RuntimeError("The source EDB session is closed.")
        self._pending_refresh = True
        self._pending_full_refresh = True
        self._refresh_timer.stop()
        if not self._busy:
            self._start_refresh()

    def batch_update(self):
        """Group geometry edits into one notification and exclude viewer reads.

        Use as a context manager on the modeling thread. This batches updates;
        it does not roll back EDB edits if an exception occurs.
        """
        if self._closed or self._source is None:
            raise RuntimeError("Batch updates require an open EDB-backed viewer.")
        return self._source.changes.batch()

    def stop_live(self) -> None:
        """Unsubscribe automatic updates; manual refresh remains available."""
        if self._unsubscribe is not None:
            self._unsubscribe()
            self._unsubscribe = None
        self._refresh_timer.stop()
        self._pending_refresh = False
        self._pending_full_refresh = False

    @Slot(int)
    def _queue_source_refresh(self, revision: int) -> None:
        if self._closed or self._unsubscribe is None:
            return
        if self._source.changes.closed:
            self.stop_live()
            return
        if revision <= self._source.revision:
            return
        self._pending_refresh = True
        if not self._busy and not self._refresh_timer.isActive():
            self._refresh_timer.start()

    @Slot()
    def _start_refresh(self) -> None:
        if self._closed or self._busy or not self._pending_refresh:
            return
        self._pending_refresh = False
        if self._source.changes.closed:
            self.stop_live()
            return
        self._busy = self._refreshing = self._capturing = True
        self._next_scene = None
        self._preparation = _Prepare(
            self.canvas.scene,
            self._source,
            previews=False,
            incremental=not self._pending_full_refresh,
            previous=(self.canvas.scene, self.canvas._prepared),
        )
        self._pending_full_refresh = False
        self._preparation.signals.ready.connect(self._prepared)
        self._preparation.signals.scene_ready.connect(self._scene_loaded)
        self._preparation.signals.failed.connect(self._load_failed)
        self.statusBar().showMessage("Refreshing layout…")
        QThreadPool.globalInstance().start(self._preparation)

    def _finish_preparation(self) -> None:
        self._busy = self._refreshing = False
        self._next_scene = None
        if self._close_after_capture:
            self.close()
        elif self._pending_refresh:
            self._refresh_timer.start()

    def run_script(self, callback: Callable, *args, **kwargs) -> None:
        """Run one modeling callback off the GUI thread, keeping rendering active.

        The callback may edit EDB and use ``batch_update()`` but must not access
        Qt widgets. Results/errors are emitted on ``script_finished`` and
        ``script_failed``. Run the Qt event loop after scheduling the callback.
        """
        if self._closed:
            raise RuntimeError("The layout viewer is closed.")
        if self._script is not None:
            raise RuntimeError("A modeling script is already running.")
        self._script = _Script(callback, args, kwargs)
        self._script.signals.finished.connect(self._script_finished)
        self._script.signals.failed.connect(self._script_failed)
        QThreadPool.globalInstance().start(self._script)

    @Slot(object)
    def _script_finished(self, result):
        self._script = None
        self.script_finished.emit(result)
        if self._close_after_capture:
            self.close()

    @Slot(object)
    def _script_failed(self, error):
        self._script = None
        self.statusBar().showMessage(f"Modeling script failed: {error}")
        self.script_failed.emit(error)
        if self._close_after_capture:
            self.close()

    def _build_toolbar(self, scene: LayoutScene) -> None:
        header = QToolBar("Workspace", self)
        header.setObjectName("workspaceHeader")
        header.setMovable(False)
        header.setFloatable(False)
        header.setFixedHeight(62)
        self.addToolBar(header)
        mark = QLabel()
        mark.setFixedSize(32, 32)
        mark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mark.setPixmap(workspace_icon("pcb", COLORS["accent"]).pixmap(QSize(27, 27)))
        header.addWidget(mark)
        brand = QLabel("PyEDB")
        brand.setProperty("role", "brand")
        header.addWidget(brand)
        header.addSeparator()
        project = QWidget()
        project.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        project_layout = QVBoxLayout(project)
        project_layout.setContentsMargins(0, 0, 12, 0)
        project_layout.setSpacing(2)
        caption = QLabel("LAYOUT WORKSPACE")
        caption.setProperty("role", "eyebrow")
        project_layout.addWidget(caption)
        self.project_title = ElidedLabel(scene.title)
        project_layout.addWidget(self.project_title)
        header.addWidget(project)
        self.view_options_button = QToolButton()
        self.view_options_button.setText("&View")
        self.view_options_button.setIcon(workspace_icon("settings"))
        self.view_options_button.setIconSize(QSize(17, 17))
        self.view_options_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.view_options_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.view_options_button.setAccessibleName("View options")
        self.view_options_button.setToolTip("Layers and component display options (Alt+V)")
        self.view_options_button.setMinimumHeight(34)
        header.addWidget(self.view_options_button)
        notes = QToolButton()
        notes.setIcon(workspace_icon("info", COLORS["muted"]))
        notes.setIconSize(QSize(18, 18))
        notes.setAccessibleName("Display notes")
        notes.setToolTip("Display notes and scene details")
        notes.setFixedSize(36, 36)
        notes.clicked.connect(self._show_notes)
        header.addWidget(notes)
        self.addToolBarBreak()
        toolbar = QToolBar("Display settings", self)
        toolbar.setObjectName("displayControls")
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setFixedHeight(52)
        self.addToolBar(toolbar)
        self.pick_action = QAction(workspace_icon("pick"), "Pick", self)
        self.pick_action.setCheckable(True)
        self.pick_action.setChecked(True)
        self.pick_action.setShortcut("P")
        self.pick_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.pick_action.setToolTip("Pick objects (P) · Click to inspect · Esc to clear")
        self.pick_action.toggled.connect(self.canvas.set_pick_enabled)
        self.canvas.addAction(self.pick_action)
        toolbar.addAction(self.pick_action)
        pick_button = toolbar.widgetForAction(self.pick_action)
        pick_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        pick_button.setAccessibleName("Pick objects")
        pick_button.setFixedHeight(36)
        pick_button.setMinimumWidth(82)
        toolbar.addSeparator()
        self.fit_action = QAction("Fit all", self)
        self.fit_action.setShortcut("F")
        self.fit_action.setToolTip("Fit all geometry (F)")
        self.fit_action.triggered.connect(self.canvas.fit_all)
        self.zoom_in_action = QAction("Zoom in", self)
        self.zoom_in_action.setToolTip("Zoom in (+)")
        self.zoom_in_action.triggered.connect(lambda: self.canvas.zoom(1.2))
        self.zoom_out_action = QAction("Zoom out", self)
        self.zoom_out_action.setToolTip("Zoom out (-)")
        self.zoom_out_action.triggered.connect(lambda: self.canvas.zoom(1 / 1.2))
        self.mirror_action = QAction("Back view", self)
        self.mirror_action.setCheckable(True)
        self.mirror_action.setShortcut("B")
        self.mirror_action.toggled.connect(self._mirror)
        for action in (self.fit_action, self.zoom_in_action, self.zoom_out_action, self.mirror_action):
            action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
            self.canvas.addAction(action)
        self.navigation = NavigationCapsule(self.canvas, self.fit_action, self.zoom_out_action, self.zoom_in_action)
        color_label = QLabel("Color")
        color_label.setProperty("role", "muted")
        color_label.setFixedHeight(36)
        self.color_mode = QComboBox()
        self.color_mode.setAccessibleName("Color mode")
        self.color_mode.addItem("Color by Layer", False)
        self.color_mode.addItem("Color by Net", True)
        self.color_mode.setCurrentIndex(int(self.canvas.color_by_net))
        self.color_mode.setMinimumWidth(145)
        self.color_mode.setFixedHeight(36)
        self.color_mode.currentIndexChanged.connect(self._color_changed)
        color_label.setBuddy(self.color_mode)
        opacity_group = QWidget()
        opacity_layout = QHBoxLayout(opacity_group)
        opacity_layout.setContentsMargins(0, 0, 0, 0)
        opacity_layout.setSpacing(10)
        opacity_label = QLabel("Opacity")
        opacity_label.setProperty("role", "muted")
        opacity_label.setFixedHeight(36)
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(round(self.canvas.opacity * 100))
        self.opacity_slider.setFixedWidth(100)
        self.opacity_slider.setFixedHeight(36)
        self.opacity_slider.setAccessibleName("Layer opacity")
        self.opacity_slider.setToolTip("Layer opacity, zero to one hundred percent")
        self.opacity_slider.valueChanged.connect(self._opacity_changed)
        opacity_label.setBuddy(self.opacity_slider)
        self.opacity_readout = QLabel(f"{self.opacity_slider.value()}%")
        self.opacity_readout.setProperty("role", "muted")
        self.opacity_readout.setFixedSize(35, 36)
        for widget in (opacity_label, self.opacity_slider, self.opacity_readout):
            opacity_layout.addWidget(widget)

        self.color_control = QWidget()
        color_row = QHBoxLayout(self.color_control)
        color_row.setContentsMargins(0, 0, 0, 0)
        color_row.setSpacing(10)
        color_row.addWidget(color_label)
        color_row.addWidget(self.color_mode)
        self.color_control.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.color_control.setFixedHeight(36)
        self.opacity_control = opacity_group
        self.opacity_control.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.opacity_control.setFixedHeight(36)
        controls = QWidget()
        controls.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        controls.setFixedHeight(36)
        row = QHBoxLayout(controls)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(28)
        row.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        row.addWidget(self.color_control)
        row.addWidget(self.opacity_control)
        row.addStretch()
        toolbar.addWidget(controls)

    def _build_layers(self, scene: LayoutScene) -> None:
        dock = QDockWidget("Layers", self)
        dock.setObjectName("layersDock")
        dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        dock.setMinimumWidth(210)
        self.layers_dock = dock
        self._set_layer_panel(scene)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)
        self.resizeDocks([dock], [258], Qt.Orientation.Horizontal)
        menu = self.menuBar().addMenu("&View")
        self.menuBar().hide()
        self.view_options_button.setMenu(menu)
        menu.addAction(dock.toggleViewAction())
        self.grid_action = QAction("Grid", self)
        self.grid_action.setCheckable(True)
        self.grid_action.setChecked(self.canvas.show_grid)
        self.grid_action.toggled.connect(lambda checked: self._display_option("show_grid", checked))
        menu.addAction(self.grid_action)
        self.outlines_action = QAction("Outlines", self)
        self.outlines_action.setCheckable(True)
        self.outlines_action.setChecked(self.canvas.show_outlines)
        self.outlines_action.toggled.connect(lambda checked: self._display_option("show_outlines", checked))
        menu.addAction(self.outlines_action)
        menu.addAction(self.mirror_action)
        has_components = bool(scene.components) or any(getattr(item, "component", None) for item in scene.geometry)
        sides = {component.side for component in scene.components}
        sides.update(item.component_side for item in scene.geometry if getattr(item, "component", None))
        self._components_separator = menu.addSeparator()
        self._components_separator.setVisible(has_components)
        for attribute, title, setting in (
            ("components_action", "Components", "show_components"),
            ("component_names_action", "Component names", "annotate_component_names"),
            ("both_sides_action", "Components on both sides", "components_on_both_sides"),
        ):
            action = QAction(title, self)
            if setting == "show_components":
                action.setToolTip("Show component envelopes and reference names")
            action.setCheckable(True)
            action.setVisible(has_components)
            if setting == "annotate_component_names":
                action.setVisible(bool(scene.components))
            elif setting == "components_on_both_sides":
                action.setVisible(len(sides) > 1)
            action.setChecked(getattr(self.canvas, setting))
            action.toggled.connect(lambda checked, setting=setting: self._display_option(setting, checked))
            setattr(self, attribute, action)
            menu.addAction(action)

    def _set_layer_panel(self, scene: LayoutScene) -> None:
        dock = self.layers_dock
        previous, header = dock.widget(), dock.titleBarWidget()
        self.layer_panel = LayerPanel(scene.layers, self.canvas.visible_layers, dock)
        self.layer_list = self.layer_panel.layer_list
        self.show_all_layers_button = self.layer_panel.show_all_button
        self.hide_all_layers_button = self.layer_panel.hide_all_button
        self.show_all_layers_button.clicked.connect(lambda: self._set_all_layers(True))
        self.hide_all_layers_button.clicked.connect(lambda: self._set_all_layers(False))
        self.layer_panel.close_button.clicked.connect(dock.hide)
        self.layer_list.itemChanged.connect(self._layer_changed)
        self.layer_panel.header.setParent(dock)
        dock.setTitleBarWidget(self.layer_panel.header)
        dock.setWidget(self.layer_panel)
        self._sync_layer_buttons()
        for widget in (previous, header):
            if widget is not None:
                widget.deleteLater()

    def _build_networks(self, scene: LayoutScene) -> None:
        dock = QDockWidget("Networks", self)
        dock.setObjectName("networksDock")
        dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        dock.setMinimumWidth(210)
        self.networks_dock = dock
        self._set_network_panel(scene)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
        self.resizeDocks([dock], [258], Qt.Orientation.Horizontal)
        menu = self.view_options_button.menu()
        menu.insertAction(self.grid_action, dock.toggleViewAction())
        self.search_action = QAction("Search networks", self)
        self.search_action.setShortcut("Ctrl+F")
        self.search_action.setEnabled(bool(self.network_panel.names))
        self.search_action.triggered.connect(self._focus_network_search)
        self.addAction(self.search_action)

    def _set_network_panel(self, scene: LayoutScene) -> None:
        dock = self.networks_dock
        previous, header = dock.widget(), dock.titleBarWidget()
        self.network_panel = NetworkPanel(scene, dock)
        self.network_list = self.network_panel.network_list
        self.network_list.currentRowChanged.connect(self._net_changed)
        self.network_panel.close_button.clicked.connect(dock.hide)
        self.network_panel.header.setParent(dock)
        dock.setTitleBarWidget(self.network_panel.header)
        dock.setWidget(self.network_panel)
        for widget in (previous, header):
            if widget is not None:
                widget.deleteLater()

    @Slot(object)
    def _prepared(self, prepared: PreparedScene) -> None:
        refreshing = self._refreshing
        if self._source is not None and self._preparation.result is not None:
            self._source.revision = self._preparation.result.revision
        if refreshing and not self._closed:
            self._display_scene(self._next_scene, preserve_view=any(True for _ in self.canvas.scene.geometry))
        self.canvas.set_prepared(prepared)
        if self.canvas.error:
            self._finish_preparation()
            return
        pin_count = len(
            {
                (batch.pin.component, batch.pin.object_id)
                for batch in prepared.pin_batches
                if batch.pin.layer == batch.pin.component_layer
            }
        )
        self._stats_summary = (
            f"Scene · {len(prepared.batches):,} copper areas · "
            f"{len(prepared.component_batches):,} components · {pin_count:,} pins"
        )
        self._compact_stats = f"Scene · {len(prepared.batches):,} areas · {pin_count:,} pins"
        self._refresh_status()
        if refreshing and not self._closed:
            self.refresh_finished.emit(self.canvas.scene)
        self._finish_preparation()

    @Slot(float, float)
    def _position_changed(self, x: float, y: float) -> None:
        self.coordinates.setText(f"X {x:.4f}   Y {y:.4f}  mm")

    @Slot(str)
    def _rendering_failed(self, error: str) -> None:
        self.engine_badge.setText("Renderer error")
        self.engine_badge.setStyleSheet(f"color: {COLORS['error']};")
        self.engine_badge.setToolTip(error)
        self._render_error = "Layout rendering failed. See the canvas for details."
        self._refresh_status()

    def _refresh_status(self) -> None:
        self.statusBar().showMessage(
            self._render_error or (self._compact_stats if self.width() < 900 else self._stats_summary)
        )

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        if hasattr(self, "_stats_summary"):
            self._refresh_status()

    def _mirror(self, checked: bool) -> None:
        self.canvas.camera.mirror = checked
        self.canvas.update()

    def _net_changed(self, index: int) -> None:
        item = self.network_list.item(index)
        previous = self.canvas.net
        self.canvas.net = item.data(Qt.ItemDataRole.UserRole) if item is not None else None
        self.canvas.update()
        if self.canvas.net != previous:
            self.net_changed.emit(self.canvas.net)

    def _color_changed(self, index: int) -> None:
        self.canvas.color_by_net = self.color_mode.itemData(index)
        self.canvas.update()

    def _display_option(self, setting: str, checked: bool) -> None:
        setattr(self.canvas, setting, checked)
        self.canvas.update()

    def _opacity_changed(self, value: int) -> None:
        self.canvas.opacity = value / 100.0
        self.opacity_readout.setText(f"{value}%")
        self.canvas.update()

    def _layer_changed(self, item: QListWidgetItem) -> None:
        previous = self.visible_layers
        if item.checkState() == Qt.CheckState.Checked:
            self.canvas.visible_layers.add(item.text())
        else:
            self.canvas.visible_layers.discard(item.text())
        self._sync_layer_buttons()
        self.canvas.update()
        if self.visible_layers != previous:
            self.visible_layers_changed.emit(self.visible_layers)

    def _set_all_layers(self, visible: bool) -> None:
        """Change the full layer selection atomically, with one canvas update."""
        self._apply_visible_layers({layer.name for layer in self.canvas.scene.layers} if visible else set())

    def _apply_visible_layers(self, names: Iterable[str]) -> None:
        previous = self.visible_layers
        with QSignalBlocker(self.layer_list):
            for index in range(self.layer_list.count()):
                item = self.layer_list.item(index)
                item.setCheckState(Qt.CheckState.Checked if item.text() in names else Qt.CheckState.Unchecked)
        self.canvas.visible_layers = set(names)
        self._sync_layer_buttons()
        self.canvas.update()
        if self.visible_layers != previous:
            self.visible_layers_changed.emit(self.visible_layers)

    @Slot(object)
    def _selection_changed(self, picked: PickedObject | None) -> None:
        if picked is None:
            self.selection_cleared.emit()
        else:
            self.object_selected.emit(picked)

    @property
    def selected_object(self) -> PickedObject | None:
        """The selected ``PickedObject``, or None."""
        return None if self.canvas.selection is None else self.canvas.selection.picked

    @property
    def selected_net(self) -> str | None:
        """The net filter name, or None when all networks are shown."""
        return self.canvas.net

    @property
    def visible_layers(self) -> tuple[str, ...]:
        """Visible layer names in stackup order."""
        return tuple(layer.name for layer in self.canvas.scene.layers if layer.name in self.canvas.visible_layers)

    def select_net(self, name: str | None) -> None:
        """Filter the view to a net; ``None`` shows all networks."""
        for row in range(self.network_list.count()):
            item = self.network_list.item(row)
            if item.data(Qt.ItemDataRole.UserRole) == name:
                if item.isHidden():
                    self.network_panel.search.clear()
                self.network_list.setCurrentRow(row)
                return
        raise ValueError(f"Unknown net {name!r}.")

    def set_visible_layers(self, names: str | Iterable[str]) -> None:
        """Show exactly the named layers."""
        names = {names} if isinstance(names, str) else set(names)
        unknown = names - {layer.name for layer in self.canvas.scene.layers}
        if unknown:
            raise ValueError(f"Unknown layers: {sorted(unknown)}.")
        self._apply_visible_layers(names)

    def select_object(self, object_id: int, kind: str | None = None, layer: str | None = None) -> PickedObject:
        """Select a trace, via, pad or zone by source object id. Returns its ``PickedObject``."""
        return self.canvas.select_object(object_id, kind, layer)

    def clear_selection(self) -> None:
        self.canvas.clear_selection()

    def fit_view(self) -> None:
        self.canvas.fit_all()

    def zoom_to_object(self, object_id: int, kind: str | None = None) -> None:
        self.canvas.zoom_to_bounds(self.canvas.find_object(object_id, kind).bounds)

    def zoom_to_net(self, name: str) -> None:
        bounds = union_bounds([item.bounds for item in self.canvas.scene.geometry if item.net == name])
        if bounds is None:
            raise ValueError(f"Unknown net {name!r}.")
        self.canvas.zoom_to_bounds(bounds)

    def _sync_layer_buttons(self) -> None:
        self.layer_panel.sync(self.canvas.visible_layers)

    def _focus_network_search(self) -> None:
        self.networks_dock.show()
        self.network_panel.search.setFocus()
        self.network_panel.search.selectAll()

    def _show_notes(self) -> None:
        notes = list(self.canvas.scene.diagnostics) or ["Scene supplied by caller. Coordinates are in millimeters."]
        prepared = self.canvas.renderer.prepared
        if prepared is not None:
            instance_count = sum(batch.instance_count for batch in prepared.sdf_batches) + len(
                prepared.component_batches
            )
            notes.insert(
                0,
                f"Geometry: {sum(b.outer_count + b.hole_count for b in prepared.batches) // 3:,} triangles, "
                f"{instance_count:,} GPU instances. "
                f"Geometry uploads: {self.canvas.renderer.upload_count}.",
            )
        QMessageBox.information(self, "Layout display notes", "\n\n".join(notes))

    def closeEvent(self, event: QCloseEvent) -> None:
        self._closed = True
        self.stop_live()
        if self._busy or self._script is not None:
            self._close_after_capture = True
            self.hide()
            event.ignore()
            return
        if self._source is not None:
            self._source.close()
            self._source = None
        self.canvas.cleanup()
        super().closeEvent(event)
