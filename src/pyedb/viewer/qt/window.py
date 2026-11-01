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

from PySide6.QtCore import QObject, QRunnable, QSignalBlocker, QSize, Qt, QThreadPool, Signal, Slot
from PySide6.QtGui import QAction, QFont
from PySide6.QtWidgets import (
    QComboBox,
    QDockWidget,
    QHBoxLayout,
    QLabel,
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
from pyedb.viewer.qt.canvas import LayoutView
from pyedb.viewer.qt.icons import workspace_icon
from pyedb.viewer.qt.navigation import NavigationCapsule
from pyedb.viewer.qt.panels import ElidedLabel, LayerPanel, NetworkPanel
from pyedb.viewer.qt.theme import COLORS, apply_viewer_theme


class _PreparationSignals(QObject):
    ready = Signal(object)
    failed = Signal(str)


class _Prepare(QRunnable):
    def __init__(self, scene):
        super().__init__()
        self.scene = scene
        self.signals = _PreparationSignals()

    @Slot()
    def run(self):
        try:
            self.signals.ready.emit(prepare_scene(self.scene))
        except Exception as exc:
            self.signals.failed.emit(str(exc))


class LayoutWindow(QMainWindow):
    def __init__(
        self,
        scene,
        parent=None,
        *,
        color_by_net=True,
        plot_components=True,
        annotate_component_names=True,
        plot_components_on_both_side=True,
    ):
        super().__init__(parent)
        apply_viewer_theme(self)
        self.setWindowTitle(f"{scene.title} — PyEDB Layout Viewer")
        self.resize(1280, 800)
        self.setMinimumSize(640, 400)
        self.canvas = LayoutView(scene, self)
        self.canvas.setMinimumWidth(180)
        self.canvas.color_by_net = color_by_net
        self.canvas.show_components = plot_components
        self.canvas.annotate_component_names = annotate_component_names
        self.canvas.components_on_both_sides = plot_components_on_both_side
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
        self.engine_badge = QLabel("●  OpenGL")
        self.engine_badge.setProperty("role", "engine")
        self.engine_badge.setToolTip("OpenGL layout renderer")
        self.statusBar().addPermanentWidget(self.engine_badge)
        self.statusBar().addPermanentWidget(self.coordinates)
        self.statusBar().showMessage("Preparing layout…")
        self._stats_summary = "Preparing layout…"
        self._compact_stats = self._stats_summary
        self._render_error = None
        self.canvas.position_changed.connect(self._position_changed)
        self.canvas.rendering_failed.connect(self._rendering_failed)
        self._preparation = _Prepare(scene)
        self._preparation.signals.ready.connect(self._prepared)
        self._preparation.signals.failed.connect(self.canvas.fail)
        QThreadPool.globalInstance().start(self._preparation)

    def _build_toolbar(self, scene):
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

    def _build_layers(self, scene):
        dock = QDockWidget("Layers", self)
        dock.setObjectName("layersDock")
        dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        dock.setMinimumWidth(210)
        self.layers_dock = dock
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
        menu.addAction(self.mirror_action)
        has_components = bool(scene.components) or any(getattr(item, "component", None) for item in scene.geometry)
        sides = {component.side for component in scene.components}
        sides.update(item.component_side for item in scene.geometry if getattr(item, "component", None))
        menu.addSeparator().setVisible(has_components)
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

    def _build_networks(self, scene):
        dock = QDockWidget("Networks", self)
        dock.setObjectName("networksDock")
        dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        dock.setMinimumWidth(210)
        self.networks_dock = dock
        self.network_panel = NetworkPanel(scene, dock)
        self.network_list = self.network_panel.network_list
        self.network_list.currentRowChanged.connect(self._net_changed)
        self.network_panel.close_button.clicked.connect(dock.hide)
        self.network_panel.header.setParent(dock)
        dock.setTitleBarWidget(self.network_panel.header)
        dock.setWidget(self.network_panel)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
        self.resizeDocks([dock], [258], Qt.Orientation.Horizontal)
        menu = self.view_options_button.menu()
        menu.insertAction(self.grid_action, dock.toggleViewAction())
        search_action = QAction("Search networks", self)
        search_action.setShortcut("Ctrl+F")
        search_action.setEnabled(bool(self.network_panel.names))
        search_action.triggered.connect(self._focus_network_search)
        self.addAction(search_action)

    @Slot(object)
    def _prepared(self, prepared):
        self.canvas.set_prepared(prepared)
        if self.canvas.error:
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

    @Slot(float, float)
    def _position_changed(self, x, y):
        self.coordinates.setText(f"X {x:.4f}   Y {y:.4f}  mm")

    @Slot(str)
    def _rendering_failed(self, error):
        self.engine_badge.setText("OpenGL error")
        self.engine_badge.setStyleSheet(f"color: {COLORS['error']};")
        self.engine_badge.setToolTip(error)
        self._render_error = "Layout rendering failed. See the canvas for details."
        self._refresh_status()

    def _refresh_status(self):
        self.statusBar().showMessage(
            self._render_error or (self._compact_stats if self.width() < 900 else self._stats_summary)
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "_stats_summary"):
            self._refresh_status()

    def _mirror(self, checked):
        self.canvas.camera.mirror = checked
        self.canvas.update()

    def _net_changed(self, index):
        item = self.network_list.item(index)
        self.canvas.net = item.data(Qt.ItemDataRole.UserRole) if item is not None else None
        self.canvas.update()

    def _color_changed(self, index):
        self.canvas.color_by_net = self.color_mode.itemData(index)
        self.canvas.update()

    def _display_option(self, setting, checked):
        setattr(self.canvas, setting, checked)
        self.canvas.update()

    def _opacity_changed(self, value):
        self.canvas.opacity = value / 100.0
        self.opacity_readout.setText(f"{value}%")
        self.canvas.update()

    def _layer_changed(self, item):
        if item.checkState() == Qt.CheckState.Checked:
            self.canvas.visible_layers.add(item.text())
        else:
            self.canvas.visible_layers.discard(item.text())
        self._sync_layer_buttons()
        self.canvas.update()

    def _set_all_layers(self, visible):
        """Change the full layer selection atomically, with one canvas update."""
        state = Qt.CheckState.Checked if visible else Qt.CheckState.Unchecked
        with QSignalBlocker(self.layer_list):
            for index in range(self.layer_list.count()):
                self.layer_list.item(index).setCheckState(state)
        self.canvas.visible_layers = (
            {self.layer_list.item(index).text() for index in range(self.layer_list.count())} if visible else set()
        )
        self._sync_layer_buttons()
        self.canvas.update()

    def _sync_layer_buttons(self):
        self.layer_panel.sync(self.canvas.visible_layers)

    def _focus_network_search(self):
        self.networks_dock.show()
        self.network_panel.search.setFocus()
        self.network_panel.search.selectAll()

    def _show_notes(self):
        notes = list(self.canvas.scene.diagnostics) or ["Scene supplied by caller. Coordinates are in millimeters."]
        prepared = self.canvas.renderer.prepared
        if prepared is not None:
            notes.insert(
                0,
                f"Geometry: {len(prepared.indices) // 3:,} triangles, {len(prepared.instances):,} GPU instances. "
                f"Geometry uploads: {self.canvas.renderer.upload_count}.",
            )
        QMessageBox.information(self, "Layout display notes", "\n\n".join(notes))

    def closeEvent(self, event):
        self.canvas.cleanup()
        super().closeEvent(event)
