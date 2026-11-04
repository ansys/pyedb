# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT

"""Compact, accessible loading feedback shared by extraction and preparation."""

from __future__ import annotations

from PySide6.QtCore import QElapsedTimer, Qt, QTimer, Slot
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QProgressBar, QVBoxLayout, QWidget

from pyedb.viewer.qt.theme import COLORS


class LoadingPanel(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("loadingPanel")
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAccessibleName("Layout loading progress")
        self.setStyleSheet(f"""
            QFrame#loadingPanel {{ background: {COLORS["panel"]}; border: 1px solid {COLORS["border"]};
                border-radius: 12px; }}
            QLabel {{ background: transparent; border: none; color: {COLORS["text"]}; font-size: 13px; }}
            QLabel#loadingTitle {{ font-size: 18px; font-weight: 600; }}
            QLabel#loadingStage {{ color: {COLORS["muted"]}; }}
            QLabel#loadingDetail, QLabel#loadingElapsed {{ color: {COLORS["muted"]}; font-size: 12px; }}
            QLabel#loadingPercent {{ color: {COLORS["accent"]}; font-weight: 600; }}
            QProgressBar {{ background: {COLORS["surface"]}; border: none; border-radius: 3px; }}
            QProgressBar::chunk {{ background: {COLORS["accent"]}; border-radius: 3px; }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 22)
        layout.setSpacing(12)
        self.title = QLabel("Loading layout", self)
        self.title.setObjectName("loadingTitle")
        layout.addWidget(self.title)
        row = QHBoxLayout()
        self.stage = QLabel("Rendering layout", self)
        self.stage.setObjectName("loadingStage")
        self.stage.setWordWrap(True)
        self.percent = QLabel(self)
        self.percent.setObjectName("loadingPercent")
        self.percent.setMinimumWidth(38)
        self.percent.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        row.addWidget(self.stage, 1)
        row.addWidget(self.percent)
        layout.addLayout(row)
        self.bar = QProgressBar(self)
        self.bar.setAccessibleName("Current loading stage")
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(6)
        self.bar.setRange(0, 0)
        layout.addWidget(self.bar)
        footer = QHBoxLayout()
        self.detail = QLabel("Discovering geometry…", self)
        self.detail.setObjectName("loadingDetail")
        self.elapsed = QLabel("0:00", self)
        self.elapsed.setObjectName("loadingElapsed")
        footer.addWidget(self.detail, 1)
        footer.addWidget(self.elapsed)
        layout.addLayout(footer)
        self.clock = QElapsedTimer()
        self.clock.start()
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._elapsed)
        self.timer.start()
        self.compact = False

    def set_compact(self) -> None:
        self.compact = True
        self.title.hide()
        self.layout().setContentsMargins(16, 12, 16, 12)
        self.layout().setSpacing(8)

    @Slot(str, int, int)
    def set_progress(self, stage: str, current: int, total: int) -> None:
        self.stage.setText(stage)
        self.bar.setAccessibleDescription(stage)
        if total > 0:
            current = max(0, min(current, total))
            percent = current * 100 // total
            self.bar.setRange(0, 100)
            self.bar.setValue(percent)
            self.percent.setText(f"{percent}%")
            self.detail.setText(f"{current:,} / {total:,} items")
        else:
            self.bar.setRange(0, 0)
            self.percent.clear()
            self.detail.setText("Working…")
        self._elapsed()

    def _elapsed(self) -> None:
        minutes, seconds = divmod(self.clock.elapsed() // 1000, 60)
        self.elapsed.setText(f"{minutes}:{seconds:02}")
