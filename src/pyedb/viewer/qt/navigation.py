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

"""A compact floating navigation capsule, independent of the GL drawing pass."""

from __future__ import annotations

from collections.abc import Mapping
from string import Template
from typing import TYPE_CHECKING

from PySide6.QtCore import QEvent, QObject, QSize, Qt
from PySide6.QtGui import (
    QAction,
    QColor,
    QIcon,
    QMouseEvent,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QWheelEvent,
)
from PySide6.QtWidgets import QFrame, QGraphicsDropShadowEffect, QHBoxLayout, QToolButton

from pyedb.viewer.qt.icons import layer_icon_path
from pyedb.viewer.qt.theme import COLORS

if TYPE_CHECKING:
    from pyedb.viewer.qt.canvas import LayoutView


_CAPSULE_STYLE = Template("""
    QFrame#navigationCapsule {
        background: $surface;
        border: 1px solid $border;
        border-radius: 28px;
    }
    QFrame#navigationCapsule QToolButton {
        color: $text;
        background: transparent;
        border: 1px solid transparent;
        border-radius: 22px;
        padding: 0px;
        font-size: 12px;
    }
    QFrame#navigationCapsule QToolButton:hover { background: $hover; }
    QFrame#navigationCapsule QToolButton:pressed { background: $hover; }
    QFrame#navigationCapsule QToolButton:checked { background: $accent_surface; }
    QFrame#navigationCapsule QToolButton:focus { border-color: $accent; }
    QFrame#navigationCapsule QToolButton:disabled { color: $disabled; }
    QFrame#navigationCapsule QFrame#navigationDivider {
        background: $border;
        border: none;
    }
""")


def navigation_icon(name: str, color: str | None = None) -> QIcon:
    """Draw a small consistent vector icon at double density."""
    pixmap = QPixmap(40, 40)
    pixmap.setDevicePixelRatio(2)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(
        QPen(
            QColor(color or COLORS["text"]),
            1.6,
            Qt.PenStyle.SolidLine,
            Qt.PenCapStyle.RoundCap,
            Qt.PenJoinStyle.RoundJoin,
        )
    )
    try:
        if name == "fit":
            path = QPainterPath()
            for x, y, dx, dy in ((3, 3, 1, 1), (17, 3, -1, 1), (3, 17, 1, -1), (17, 17, -1, -1)):
                path.moveTo(x, y + dy * 4)
                path.lineTo(x, y)
                path.lineTo(x + dx * 4, y)
            painter.drawPath(path)
        elif name in {"minus", "plus"}:
            painter.drawLine(4, 10, 16, 10)
            if name == "plus":
                painter.drawLine(10, 4, 10, 16)
        else:
            painter.drawPath(layer_icon_path(layer_count=3))
    finally:
        painter.end()
    return QIcon(pixmap)


class NavigationCapsule(QFrame):
    """Keep navigation over the canvas, with keyboard focus and explicit hit areas."""

    def __init__(
        self, canvas: LayoutView, fit_action: QAction, zoom_out_action: QAction, zoom_in_action: QAction
    ) -> None:
        super().__init__(canvas)
        self.canvas = canvas
        self.has_geometry = canvas.scene.bounds is not None
        self.setObjectName("navigationCapsule")
        self.setAccessibleName("Canvas navigation")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        row = QHBoxLayout(self)
        row.setContentsMargins(6, 6, 6, 6)
        row.setSpacing(2)
        self.fit_button = self._button(fit_action, "fit", "Fit all")
        self.zoom_out_button = self._button(zoom_out_action, "minus", "Zoom out")
        self.zoom_in_button = self._button(zoom_in_action, "plus", "Zoom in")
        for button in (self.fit_button, self.zoom_out_button, self.zoom_in_button):
            row.addWidget(button)
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(24)
        self.shadow.setOffset(0, 4)
        self.setGraphicsEffect(self.shadow)
        self.apply_theme(COLORS)
        for action in (fit_action, zoom_out_action, zoom_in_action):
            action.setEnabled(self.has_geometry)
        self.setVisible(self.has_geometry)
        canvas.installEventFilter(self)
        self.reposition()

    def apply_theme(self, colors: Mapping[str, str]) -> None:
        self.setStyleSheet(_CAPSULE_STYLE.substitute(colors))
        self.shadow.setColor(QColor(colors["shadow"]))
        for button, icon in ((self.fit_button, "fit"), (self.zoom_out_button, "minus"), (self.zoom_in_button, "plus")):
            button.defaultAction().setIcon(navigation_icon(icon, colors["text"]))

    def _button(self, action: QAction, icon: str, name: str) -> QToolButton:
        action.setIcon(navigation_icon(icon))
        button = QToolButton(self)
        button.setDefaultAction(action)
        button.setAccessibleName(name)
        button.setIconSize(QSize(20, 20))
        button.setFixedSize(44, 44)
        button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        return button

    def reposition(self) -> None:
        self.adjustSize()
        self.move(max(8, (self.canvas.width() - self.width()) // 2), max(8, self.canvas.height() - self.height() - 20))
        self.canvas.fit_padding = (16, 16, 16, self.height() + 36) if self.has_geometry else (0, 0, 0, 0)
        self.raise_()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched is self.canvas and event.type() in (QEvent.Type.Resize, QEvent.Type.Show):
            self.reposition()
        return super().eventFilter(watched, event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        event.accept()

    def wheelEvent(self, event: QWheelEvent) -> None:
        event.accept()
