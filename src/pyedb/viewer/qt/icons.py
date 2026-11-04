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

"""Small consistent, locally drawn icons for the native workspace chrome."""

from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap

from pyedb.viewer.qt.theme import COLORS


def layer_icon_path(layer_count: int = 2) -> QPainterPath:
    """Build the shared stacked-layer outline at its original logical size."""
    path = QPainterPath()
    path.moveTo(10, 3)
    path.lineTo(17, 7)
    path.lineTo(10, 11)
    path.lineTo(3, 7)
    path.closeSubpath()
    for y in range(11, 11 + 4 * (layer_count - 1), 4):
        path.moveTo(3, y)
        path.lineTo(10, y + 4)
        path.lineTo(17, y)
    return path


def workspace_icon(name: str, color: str | None = None) -> QIcon:
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
        if name == "pick":
            path = QPainterPath()
            path.moveTo(4, 2)
            for x, y in ((4, 15), (8, 11), (11, 17), (14, 15), (11, 10), (17, 9)):
                path.lineTo(x, y)
            path.closeSubpath()
            painter.drawPath(path)
        elif name == "search":
            painter.drawEllipse(QRectF(3, 3, 10, 10))
            painter.drawLine(12, 12, 17, 17)
        elif name == "close":
            painter.drawLine(5, 5, 15, 15)
            painter.drawLine(15, 5, 5, 15)
        elif name == "info":
            painter.drawEllipse(QRectF(2.5, 2.5, 15, 15))
            painter.drawLine(10, 9, 10, 14)
            painter.drawPoint(10, 6)
        elif name == "settings":
            for y, knob in ((5, 7), (10, 13), (15, 8)):
                painter.drawLine(3, y, knob - 2, y)
                painter.drawLine(knob + 2, y, 17, y)
                painter.drawEllipse(QRectF(knob - 2, y - 2, 4, 4))
        elif name == "pcb":
            painter.drawRoundedRect(QRectF(4, 4, 12, 12), 2, 2)
            painter.drawLine(8, 4, 8, 10)
            painter.drawLine(8, 10, 13, 10)
            painter.drawLine(13, 10, 13, 16)
            for x in (7, 13):
                painter.drawLine(x, 1, x, 4)
                painter.drawLine(x, 16, x, 19)
            painter.drawLine(1, 7, 4, 7)
            painter.drawLine(16, 13, 19, 13)
        else:
            painter.drawPath(layer_icon_path())
    finally:
        painter.end()
    return QIcon(pixmap)
