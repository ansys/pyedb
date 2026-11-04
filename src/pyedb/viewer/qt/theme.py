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

"""Viewer-scoped chrome tokens; PCB materials and the host application are separate."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from PySide6.QtGui import QColor, QFont, QFontDatabase, QPalette
from PySide6.QtWidgets import QWidget

from pyedb.viewer.colors import viewer_theme

LIGHT_COLORS = {
    "window": "#f6f7fb",
    "panel": "#ffffff",
    "surface": "#eef1f7",
    "hover": "#e4e9f3",
    "border": "#d4dae5",
    "text": "#182337",
    "muted": "#52627a",
    "disabled": "#929eaf",
    "accent": "#6353c7",
    "accent_surface": "#ece8ff",
    "positive": "#197451",
    "error": "#b43e4e",
    "border_hover": "#b0bbcc",
    "border_disabled": "#e3e7ef",
    "input_hover": "#a9b5c8",
    "text_selection": "#e2dcff",
    "popup_border": "#bdc7d8",
    "menu_border": "#c4cddc",
    "selected_border": "#b8abe8",
    "indicator_border": "#7d8ca4",
    "groove": "#dce2ec",
    "scrollbar": "#c1cad9",
    "scrollbar_hover": "#9aa9bf",
    "shadow": "#2d182337",
    "chevron": "chevron.svg",
}

DARK_COLORS = {
    "window": "#0f141c",
    "panel": "#161c26",
    "surface": "#1f2632",
    "hover": "#2a3240",
    "border": "#2e3746",
    "text": "#e6eaf2",
    "muted": "#9aa6b8",
    "disabled": "#5d6878",
    "accent": "#8f80ff",
    "accent_surface": "#2c2650",
    "positive": "#4cc38a",
    "error": "#f07a8a",
    "border_hover": "#46536a",
    "border_disabled": "#232a35",
    "input_hover": "#4a576d",
    "text_selection": "#3d3570",
    "popup_border": "#3a4557",
    "menu_border": "#3a4557",
    "selected_border": "#5b4fb0",
    "indicator_border": "#7a879c",
    "groove": "#2e3746",
    "scrollbar": "#3a4557",
    "scrollbar_hover": "#56647a",
    "shadow": "#73000000",
    "chevron": "chevron_light.svg",
}

THEMES = {"light": LIGHT_COLORS, "dark": DARK_COLORS}
# Light tokens, the default theme.
COLORS = LIGHT_COLORS


def theme_colors(theme: str) -> dict[str, str]:
    """Return the chrome tokens of a viewer theme: ``"light"`` or ``"dark"``."""
    return THEMES[viewer_theme(theme)]


def apply_viewer_theme(window: QWidget, colors: Mapping[str, str] = LIGHT_COLORS) -> None:
    """Style this window without changing other windows in an embedded QApplication."""
    families = set(QFontDatabase.families())
    family = next(
        (name for name in ("Segoe UI Variable", "Segoe UI", "Inter", "Noto Sans") if name in families), "Sans Serif"
    )
    font = QFont(family)
    font.setPixelSize(13)
    window.setFont(font)
    palette = QPalette(window.palette())
    for role, token in (
        (QPalette.ColorRole.Window, "panel"),
        (QPalette.ColorRole.WindowText, "text"),
        (QPalette.ColorRole.Base, "window"),
        (QPalette.ColorRole.AlternateBase, "surface"),
        (QPalette.ColorRole.Text, "text"),
        (QPalette.ColorRole.Button, "surface"),
        (QPalette.ColorRole.ButtonText, "text"),
        (QPalette.ColorRole.Highlight, "accent_surface"),
        (QPalette.ColorRole.HighlightedText, "text"),
        (QPalette.ColorRole.PlaceholderText, "muted"),
        (QPalette.ColorRole.ToolTipBase, "surface"),
        (QPalette.ColorRole.ToolTipText, "text"),
    ):
        palette.setColor(role, QColor(colors[token]))
    for role in (QPalette.ColorRole.Text, QPalette.ColorRole.ButtonText, QPalette.ColorRole.WindowText):
        palette.setColor(QPalette.ColorGroup.Disabled, role, QColor(colors["disabled"]))
    window.setPalette(palette)
    assets = Path(__file__).with_name("assets")
    check = (assets / "check.svg").as_posix()
    chevron = (assets / colors["chevron"]).as_posix()
    c = colors
    window.setStyleSheet(f"""
        QMainWindow {{ background: {c["window"]}; }}
        QWidget {{ color: {c["text"]}; font-family: "{family}"; font-size: 13px; }}
        QLabel#coordinateReadout {{ font-family: "Consolas", monospace; font-size: 11px; }}
        QLabel {{ background: transparent; border: none; }}
        QLabel[role="muted"] {{ color: {c["muted"]}; font-size: 12px; }}
        QLabel[role="eyebrow"] {{ color: {c["muted"]}; font-size: 10px; font-weight: 600; }}
        QLabel[role="heading"] {{ font-size: 15px; font-weight: 600; }}
        QLabel[role="brand"] {{ font-size: 17px; font-weight: 600; }}
        QLabel[role="badge"] {{ background: {c["surface"]}; color: {c["muted"]};
            border: 1px solid {c["border"]}; border-radius: 7px; padding: 3px 7px; font-size: 11px; }}
        QLabel[role="engine"] {{ color: {c["positive"]}; padding: 2px 8px; font-size: 11px; font-weight: 600; }}
        QToolBar {{ background: {c["window"]}; border: none; spacing: 8px; padding: 6px 16px; }}
        QToolBar#workspaceHeader {{ border-bottom: 1px solid {c["border"]}; padding: 8px 16px; }}
        QToolBar#displayControls {{ border-bottom: 1px solid {c["border"]}; }}
        QToolBar::separator {{ background: {c["border"]}; width: 1px; margin: 8px 8px; }}
        QToolBar::handle {{ width: 0px; }}
        QToolButton {{ background: transparent; border: 1px solid transparent;
            border-radius: 7px; padding: 6px 9px; }}
        QToolButton:hover {{ background: {c["surface"]}; }}
        QToolButton:pressed {{ background: {c["hover"]}; }}
        QToolButton:checked {{ background: {c["accent_surface"]}; color: {c["text"]}; }}
        QToolButton:focus {{ border-color: {c["accent"]}; }}
        QToolButton:disabled {{ color: {c["disabled"]}; }}
        QToolButton::menu-indicator {{ image: none; width: 0px; }}
        QPushButton {{ background: {c["surface"]}; border: 1px solid {c["border"]};
            border-radius: 7px; padding: 6px 10px; font-size: 12px; }}
        QPushButton:hover {{ background: {c["hover"]}; border-color: {c["border_hover"]}; }}
        QPushButton:pressed {{ background: {c["accent_surface"]}; }}
        QPushButton:focus {{ border-color: {c["accent"]}; }}
        QPushButton:disabled {{ background: {c["panel"]}; color: {c["disabled"]};
            border-color: {c["border_disabled"]}; }}
        QLineEdit, QComboBox {{ background: {c["surface"]}; color: {c["text"]};
            border: 1px solid {c["border"]}; border-radius: 7px; padding: 7px 10px;
            selection-background-color: {c["text_selection"]}; }}
        QLineEdit:focus, QComboBox:focus {{ border-color: {c["accent"]}; }}
        QLineEdit:hover, QComboBox:hover {{ border-color: {c["input_hover"]}; }}
        QComboBox {{ padding-right: 28px; min-height: 18px; }}
        QComboBox::drop-down {{ border: none; width: 27px; }}
        QComboBox::down-arrow {{ image: url("{chevron}"); width: 12px; height: 12px; }}
        QComboBox QAbstractItemView {{ background: {c["panel"]}; color: {c["text"]};
            border: 1px solid {c["popup_border"]}; border-radius: 6px; padding: 4px;
            selection-background-color: {c["accent_surface"]}; outline: none; }}
        QComboBox QAbstractItemView::item {{ min-height: 28px; padding: 4px 8px; }}
        QDockWidget {{ background: {c["panel"]}; border: none; }}
        QMainWindow::separator {{ background: {c["border"]}; width: 1px; height: 1px; }}
        QMainWindow::separator:hover {{ background: {c["accent"]}; }}
        QWidget#layerPanel, QWidget#networkPanel, QFrame#layerHeader, QFrame#networkHeader {{
            background: {c["panel"]}; }}
        QFrame#layerHeader, QFrame#networkHeader {{ border-bottom: 1px solid {c["border"]}; }}
        QFrame#layerFooter, QFrame#networkFooter {{ border-top: 1px solid {c["border"]}; background: {c["panel"]}; }}
        QListWidget {{ background: {c["panel"]}; border: none; outline: none;
            padding: 2px; selection-background-color: {c["accent_surface"]}; }}
        QListWidget::item {{ border: 1px solid transparent; border-radius: 7px; padding: 7px 8px; }}
        QListWidget::item:hover {{ background: {c["surface"]}; }}
        QListWidget::item:selected {{ background: {c["accent_surface"]}; border-color: {c["selected_border"]}; }}
        QListWidget::item:focus {{ border-color: {c["accent"]}; }}
        QListWidget::indicator {{ width: 15px; height: 15px; border: 1px solid {c["indicator_border"]};
            border-radius: 4px; margin-right: 6px; background: {c["panel"]}; }}
        QListWidget::indicator:checked {{ background: {c["accent"]};
            border-color: {c["accent"]}; image: url("{check}"); }}
        QSlider::groove:horizontal {{ height: 4px; background: {c["groove"]}; border-radius: 2px; }}
        QSlider::sub-page:horizontal {{ background: {c["accent"]}; border-radius: 2px; }}
        QSlider::handle:horizontal {{ background: {c["text"]}; border: 2px solid {c["panel"]};
            width: 12px; height: 12px; margin: -6px 0; border-radius: 8px; }}
        QSlider::handle:horizontal:hover {{ background: {c["accent"]}; }}
        QSlider:focus {{ border: 1px solid {c["accent"]}; border-radius: 5px; }}
        QMenu {{ background: {c["panel"]}; color: {c["text"]}; border: 1px solid {c["menu_border"]};
            padding: 6px; }}
        QMenu::item {{ padding: 8px 28px 8px 12px; border-radius: 5px; }}
        QMenu::item:selected {{ background: {c["accent_surface"]}; }}
        QMenu::item:disabled {{ color: {c["disabled"]}; }}
        QMenu::separator {{ background: {c["border"]}; height: 1px; margin: 5px 8px; }}
        QMenu::indicator {{ width: 16px; height: 16px; margin-left: 4px; }}
        QMenu::indicator:checked {{ image: url("{check}"); background: {c["accent"]}; border-radius: 4px; }}
        QStatusBar {{ background: {c["window"]}; color: {c["muted"]};
            border-top: 1px solid {c["border"]}; font-size: 11px; }}
        QStatusBar::item {{ border: none; }}
        QScrollBar:vertical {{ background: transparent; width: 8px; margin: 3px 0; }}
        QScrollBar::handle:vertical {{ background: {c["scrollbar"]}; min-height: 28px; border-radius: 4px; }}
        QScrollBar::handle:vertical:hover {{ background: {c["scrollbar_hover"]}; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: transparent; }}
        QToolTip {{ background: {c["surface"]}; color: {c["text"]}; border: 1px solid {c["popup_border"]};
            padding: 6px 9px; }}
        QMessageBox {{ background: {c["panel"]}; }}
    """)
