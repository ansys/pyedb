# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT

"""A canvas-owned, nonmodal property card for the picked source object."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from pyedb.viewer.picking import inspector_rows
from pyedb.viewer.qt.icons import workspace_icon
from pyedb.viewer.qt.theme import COLORS

if TYPE_CHECKING:
    from pyedb.viewer.picking import PickHit


class ObjectInspector(QFrame):
    cleared = Signal()

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setObjectName("objectInspector")
        self.setAccessibleName("Picked object properties")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 12, 14)
        layout.setSpacing(10)
        heading = QHBoxLayout()
        self.title = QLabel(self)
        self.title.setObjectName("propertyTitle")
        heading.addWidget(self.title, 1)
        self.close_button = QToolButton(self)
        self.close_button.setFixedSize(28, 28)
        self.close_button.setAccessibleName("Clear picked object")
        self.close_button.setToolTip("Clear selection (Esc)")
        self.close_button.clicked.connect(self.cleared)
        self.apply_theme(COLORS)
        heading.addWidget(self.close_button)
        layout.addLayout(heading)
        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.body = QWidget()
        self.body.setObjectName("propertyBody")
        self.rows = QGridLayout(self.body)
        self.rows.setContentsMargins(0, 0, 4, 0)
        self.rows.setHorizontalSpacing(14)
        self.rows.setVerticalSpacing(8)
        self.rows.setColumnStretch(1, 1)
        self.scroll.setWidget(self.body)
        layout.addWidget(self.scroll)
        shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        shortcut.activated.connect(self.cleared)
        self.values = {}
        self._stacked = False
        self.hide()

    def apply_theme(self, colors: Mapping[str, str]) -> None:
        self.setStyleSheet(f"""
            QFrame#objectInspector {{ background: {colors["panel"]}; border: 1px solid {colors["border"]};
                                     border-radius: 10px; }}
            QLabel {{ background: transparent; border: none; color: {colors["text"]}; font-size: 13px; }}
            QLabel#propertyTitle {{ font-size: 15px; font-weight: 600; }}
            QLabel[propertyRole="key"] {{ color: {colors["muted"]}; }}
            QScrollArea {{ background: transparent; border: none; }}
            QWidget#propertyBody {{ background: transparent; }}
        """)
        self.close_button.setIcon(workspace_icon("close", colors["text"]))

    def set_hit(self, hit: PickHit) -> None:
        self.values = dict(inspector_rows(hit))
        self.title.setText(hit.object.info.kind.capitalize())
        self._build_rows(min(340, self.parentWidget().width() - 24) < 260)
        self.setAccessibleDescription("; ".join(f"{name}: {text}" for name, text in self.values.items()))

    def _build_rows(self, stacked: bool) -> None:
        self._stacked = stacked
        while self.rows.count():
            item = self.rows.takeAt(0)
            if item.widget() is not None:
                item.widget().hide()
                item.widget().deleteLater()
        self.rows.setColumnStretch(0, 1 if stacked else 0)
        self.rows.setColumnStretch(1, 0 if stacked else 1)
        for row, (name, text) in enumerate(self.values.items()):
            label, value = QLabel(name, self.body), QLabel(text, self.body)
            label.setProperty("propertyRole", "key")
            value.setTextFormat(Qt.TextFormat.PlainText)
            value.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.TextSelectableByKeyboard
            )
            value.setWordWrap(True)
            value.setMinimumWidth(0)
            value.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
            value.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            if name == "Length":
                value.setToolTip("Source trace centerline length, including arcs; excludes end-cap extensions.")
            elif name == "Via diameter":
                value.setToolTip("Copper pad diameter on the picked layer.")
            elif name == "Drill diameter":
                value.setToolTip("Drill diameter; for slotted drills, the larger slot dimension.")
            value.setAccessibleName(name)
            label.setBuddy(value)
            self.rows.addWidget(label, row * 2 if stacked else row, 0, alignment=Qt.AlignmentFlag.AlignTop)
            self.rows.addWidget(value, row * 2 + 1 if stacked else row, 0 if stacked else 1)
            label.show()
            value.show()
        self.layout().activate()

    def fit_canvas(self, width: int, height: int) -> None:
        self.setFixedWidth(max(120, min(340, width - 24)))
        if (self.width() < 260) != self._stacked:
            self._build_rows(self.width() < 260)
        self.rows.activate()
        body_height = self.body.heightForWidth(self.width() - 32)
        if body_height < 0:
            body_height = self.body.sizeHint().height()
        self.scroll.setFixedHeight(max(24, min(body_height + 4, height - 84)))
        self.adjustSize()
