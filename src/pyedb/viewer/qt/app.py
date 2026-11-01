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
from PySide6.QtCore import QCoreApplication, QEventLoop, Qt, QThread
from PySide6.QtGui import QSurfaceFormat
from PySide6.QtWidgets import QApplication

from pyedb.viewer.qt.canvas import layout_surface_format
from pyedb.viewer.qt.window import LayoutWindow
from pyedb.viewer.scene import LayoutScene

# Check triangulation support before creating QApplication.
import_module("mapbox_earcut")

_application = None


def _get_application():
    """Validate the GUI thread and initialize an application once."""
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
    return _application, owns_application


def show_scene(
    scene=None,
    block=None,
    color_by_net=True,
    plot_components=True,
    annotate_component_names=True,
    plot_components_on_both_side=True,
    *,
    loader=None,
    layer_source=None,
    title="EDB layout",
):
    """Create a native window, reusing the host application's event loop if present."""
    application, owns_application = _get_application()
    if block is None:
        block = owns_application
    if block and QThread.currentThread().loopLevel() > 0:
        raise RuntimeError("A Qt event loop is already running. Launch the viewer with block=False.")
    window = LayoutWindow(
        scene if scene is not None else LayoutScene((), (), title),
        color_by_net=color_by_net,
        plot_components=plot_components,
        annotate_component_names=annotate_component_names,
        plot_components_on_both_side=plot_components_on_both_side,
        loader=loader,
        layer_source=layer_source,
    )
    # Keep QApplication alive for the lifetime of non-blocking standalone windows.
    window._application = application
    window.scene_failed.connect(lambda error: window.close())
    window.show()
    if block:
        application.exec()
        # Explicit QApplication.quit() must also drain an active source read
        # before the CLI closes its database in finally.
        window.close()
        if window._capturing:
            loop = QEventLoop()
            window.closed.connect(loop.quit)
            loop.exec()
    elif (loader is not None or layer_source is not None) and window._capturing:
        # Preserve the caller-owned session lifetime for nonblocking launches:
        # return after capture, while this same window stays visible throughout.
        loop = QEventLoop()
        window.scene_ready.connect(loop.quit)
        window.scene_failed.connect(loop.quit)
        window.closed.connect(loop.quit)
        loop.exec()
    if window._capture_error is not None:
        raise window._capture_error
    return window
