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

"""Application lifecycle, separate from EDB session ownership."""

from importlib import import_module
import threading

# Import dependencies before creating QApplication, producing actionable errors.
from PySide6.QtCore import QCoreApplication, Qt, QThread
from PySide6.QtGui import QSurfaceFormat
from PySide6.QtWidgets import QApplication

from pyedb.viewer.qt.canvas import layout_surface_format
from pyedb.viewer.qt.window import LayoutWindow

# Check triangulation support before creating QApplication.
import_module("mapbox_earcut")

_application = None


def show_scene(
    scene,
    block=None,
    color_by_net=True,
    plot_components=True,
    annotate_component_names=True,
    plot_components_on_both_side=True,
):
    """Create a native window, reusing the host application's event loop if present."""
    global _application
    if threading.current_thread() is not threading.main_thread():
        raise RuntimeError("Launch the layout viewer on the main GUI thread.")
    existing = QCoreApplication.instance()
    if existing is not None and not isinstance(existing, QApplication):
        raise RuntimeError("The layout viewer requires QApplication; an incompatible QCoreApplication already exists.")
    owns_application = existing is None
    if owns_application:
        # Required before QApplication on platforms such as macOS when sharing
        # core-profile contexts. Embedded hosts should set this themselves.
        QSurfaceFormat.setDefaultFormat(layout_surface_format())
    _application = QApplication([]) if owns_application else existing
    if owns_application:
        _application.setStyle("Fusion")
        hints = _application.styleHints()
        if hasattr(hints, "setColorScheme"):
            hints.setColorScheme(Qt.ColorScheme.Light)
    if QThread.currentThread() != _application.thread():
        raise RuntimeError("Launch the layout viewer on the QApplication thread.")
    if block is None:
        block = owns_application
    if block and QThread.currentThread().loopLevel() > 0:
        raise RuntimeError("A Qt event loop is already running. Launch the viewer with block=False.")
    window = LayoutWindow(
        scene,
        color_by_net=color_by_net,
        plot_components=plot_components,
        annotate_component_names=annotate_component_names,
        plot_components_on_both_side=plot_components_on_both_side,
    )
    # Keep QApplication alive for the lifetime of non-blocking standalone windows.
    window._application = _application
    window.show()
    if block:
        _application.exec()
    return window
