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

"""Native workspace panels with explicit state, search and keyboard navigation."""

from __future__ import annotations

from collections.abc import Container, Sequence
from typing import TYPE_CHECKING

from PySide6.QtCore import QRectF, QSignalBlocker, QSize, Qt
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPaintEvent, QPen, QPixmap, QResizeEvent
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from pyedb.viewer.colors import net_color
from pyedb.viewer.mesh import scene_network_names
from pyedb.viewer.qt.icons import workspace_icon
from pyedb.viewer.qt.theme import COLORS

if TYPE_CHECKING:
    from pyedb.viewer.scene import LayoutScene, SceneLayer


class ElidedLabel(QLabel):
    """Preserve a full accessible project name without forcing a wide window."""

    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.setTextFormat(Qt.TextFormat.PlainText)
        self.setToolTip(text)
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.setMinimumWidth(70)

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setPen(self.palette().color(self.foregroundRole()))
        text = self.fontMetrics().elidedText(self.text(), Qt.TextElideMode.ElideRight, self.width())
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, text)
        painter.end()


def layer_swatch(color: Sequence[float]) -> QIcon:
    pixmap = QPixmap(28, 28)
    pixmap.setDevicePixelRatio(2)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(QPen(QColor(COLORS["muted"]), 0.7))
    painter.setBrush(QColor.fromRgbF(*color))
    painter.drawRoundedRect(QRectF(1, 1, 12, 12), 3, 3)
    painter.end()
    return QIcon(pixmap)


def _panel_header(
    parent: QWidget, object_name: str, title_text: str, panel_name: str
) -> tuple[QFrame, QLabel, QToolButton]:
    """Build a panel heading with a count badge and a close control."""
    header = QFrame(parent)
    header.setObjectName(object_name)
    header.setFixedHeight(56)
    heading = QHBoxLayout(header)
    heading.setContentsMargins(16, 14, 12, 14)
    title = QLabel(title_text, header)
    title.setProperty("role", "heading")
    title.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    heading.addWidget(title)
    heading.addStretch()
    counter = QLabel(header)
    counter.setProperty("role", "badge")
    counter.setFixedHeight(26)
    heading.addWidget(counter)
    close_button = QToolButton(header)
    close_button.setIcon(workspace_icon("close", COLORS["muted"]))
    close_button.setIconSize(QSize(14, 14))
    close_button.setFixedSize(28, 28)
    close_button.setAccessibleName(f"Hide {panel_name} panel")
    close_button.setToolTip(f"Hide {panel_name} panel · restore from View")
    heading.addWidget(close_button)
    return header, counter, close_button


class LayerPanel(QWidget):
    """Stackup visibility controls without a search field."""

    def __init__(
        self, layers: Sequence[SceneLayer], visible_layers: Container[str], parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setObjectName("layerPanel")
        self.header, self.counter, self.close_button = _panel_header(self, "layerHeader", "Layers", "layers")
        self.counter.setAccessibleName("Visible layer count")
        self.counter.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 14, 12, 0)
        layout.setSpacing(10)
        bulk = QHBoxLayout()
        bulk.setSpacing(8)
        self.show_all_button = QPushButton("Show all", self)
        self.hide_all_button = QPushButton("Hide all", self)
        self.show_all_button.setAccessibleName("Show all layers")
        self.hide_all_button.setAccessibleName("Hide all layers")
        self.show_all_button.setToolTip("Show every layer")
        self.hide_all_button.setToolTip("Hide every layer")
        for button in (self.show_all_button, self.hide_all_button):
            button.setMinimumHeight(32)
            bulk.addWidget(button)
        layout.addLayout(bulk)
        self.eyebrow = QLabel("STACKUP ORDER", self)
        self.eyebrow.setProperty("role", "eyebrow")
        layout.addWidget(self.eyebrow)
        self.layer_list = QListWidget(self)
        self.layer_list.setObjectName("layerList")
        self.layer_list.setAccessibleName("Visible layout layers")
        self.layer_list.setIconSize(QSize(14, 14))
        self.layer_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.layer_list.setTextElideMode(Qt.TextElideMode.ElideRight)
        self.layer_list.setMinimumHeight(0)
        for layer in layers:
            item = QListWidgetItem(layer_swatch(layer.color), layer.name)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked if layer.name in visible_layers else Qt.CheckState.Unchecked)
            item.setToolTip(layer.name + " · Space to toggle visibility")
            item.setSizeHint(QSize(0, 40))
            self.layer_list.addItem(item)
        layout.addWidget(self.layer_list, 1)
        self.empty_notice = QLabel(self)
        self.empty_notice.setProperty("role", "muted")
        self.empty_notice.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_notice.setWordWrap(True)
        self.empty_notice.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Ignored)
        layout.addWidget(self.empty_notice, 1)
        footer = QFrame(self)
        self.footer = footer
        footer.setObjectName("layerFooter")
        footer_layout = QVBoxLayout(footer)
        footer_layout.setContentsMargins(4, 12, 4, 14)
        footer_layout.setSpacing(7)
        self.summary = QLabel(footer)
        self.summary.setProperty("role", "muted")
        footer_layout.addWidget(self.summary)
        hint = QLabel("Space   Toggle selected layer", footer)
        hint.setProperty("role", "muted")
        footer_layout.addWidget(hint)
        layout.addWidget(footer)
        self.sync(visible_layers)
        self.layer_list.setVisible(bool(layers))
        self.empty_notice.setVisible(not layers)
        self.empty_notice.setText("No layers yet\nThis layout snapshot is empty.")

    def sync(self, visible_layers: Container[str]) -> None:
        count = self.layer_list.count()
        checked = sum(self.layer_list.item(i).text() in visible_layers for i in range(count))
        self.counter.setText(f"{checked} / {count}")
        self.summary.setText(f"{checked} of {count} layers visible" if count else "No layers in this snapshot")
        self.show_all_button.setEnabled(checked < count)
        self.hide_all_button.setEnabled(checked > 0)
        with QSignalBlocker(self.layer_list):
            for index in range(count):
                item = self.layer_list.item(index)
                visible = item.text() in visible_layers
                item.setForeground(QColor(COLORS["text"] if visible else COLORS["muted"]))
                font = QFont(self.font())
                font.setWeight(QFont.Weight.Medium if visible else QFont.Weight.Normal)
                item.setFont(font)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self.footer.setVisible(self.height() >= 320)
        self.eyebrow.setVisible(self.height() >= 260)


class NetworkPanel(QWidget):
    """A searchable single-network selector, parallel to the layer panel."""

    def __init__(self, scene: LayoutScene, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("networkPanel")
        self.header, self.counter, self.close_button = _panel_header(self, "networkHeader", "Networks", "network")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 14, 12, 0)
        layout.setSpacing(10)
        self.search = QLineEdit(self)
        self.search.setPlaceholderText("Search networks…")
        self.search.setAccessibleName("Search networks")
        self.search.setToolTip("Search network names (Ctrl+F)")
        self.search.setClearButtonEnabled(True)
        self.search.addAction(workspace_icon("search", COLORS["muted"]), QLineEdit.ActionPosition.LeadingPosition)
        self.search.setMinimumHeight(36)
        layout.addWidget(self.search)
        caption = QLabel("SELECT A NETWORK", self)
        caption.setProperty("role", "eyebrow")
        layout.addWidget(caption)
        self.network_list = QListWidget(self)
        self.network_list.setObjectName("networkList")
        self.network_list.setAccessibleName("Visible network")
        self.network_list.setIconSize(QSize(14, 14))
        self.network_list.setMinimumHeight(0)
        self.network_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.network_list.setTextElideMode(Qt.TextElideMode.ElideRight)
        self.names = sorted(
            {item.net for item in scene.geometry if item.net is not None}
            | {net for component in scene.components for net in component.nets}
        )
        ids = {net: index for index, net in enumerate(scene_network_names(scene))}
        all_item = QListWidgetItem(workspace_icon("layers", COLORS["muted"]), "All networks")
        all_item.setData(Qt.ItemDataRole.UserRole, None)
        all_item.setSizeHint(QSize(0, 40))
        self.network_list.addItem(all_item)
        for net in self.names:
            color = net_color(ids.get(net, 0)) or (0.5, 0.5, 0.5)
            item = QListWidgetItem(layer_swatch((*color, 1)), net or "Unassigned")
            item.setData(Qt.ItemDataRole.UserRole, net)
            item.setToolTip(net or "Unassigned")
            item.setSizeHint(QSize(0, 36))
            self.network_list.addItem(item)
        self.network_list.setCurrentRow(0)
        self.network_list.currentRowChanged.connect(self._selection_changed)
        layout.addWidget(self.network_list, 1)
        footer = QFrame(self)
        footer.setObjectName("networkFooter")
        footer_layout = QVBoxLayout(footer)
        footer_layout.setContentsMargins(4, 12, 4, 14)
        self.summary = ElidedLabel("All networks", footer)
        self.summary.setProperty("role", "muted")
        footer_layout.addWidget(self.summary)
        layout.addWidget(footer)
        self.search.textChanged.connect(self._filter)
        self.search.setEnabled(bool(self.names))
        self._filter("")

    def _filter(self, query: str) -> None:
        query = query.strip().casefold()
        matches = 0
        with QSignalBlocker(self.network_list):
            for row in range(1, self.network_list.count()):
                item = self.network_list.item(row)
                match = query in item.text().casefold()
                item.setHidden(not match)
                matches += int(match)
        self.counter.setText(f"{matches} / {len(self.names)}" if query else str(len(self.names)))

    def _selection_changed(self, row: int) -> None:
        item = self.network_list.item(row)
        text = item.text() if item is not None else "All networks"
        self.summary.setText(text)
        self.summary.setToolTip(text)
