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

"""Optional interactive layout viewer. Importing this module does not load Qt."""

from pyedb.viewer.scene import LayoutScene, SceneComponent, SceneJoin, SceneLayer, ScenePad, ScenePolygon, SceneTrace

__all__ = [
    "LayoutScene",
    "SceneComponent",
    "SceneLayer",
    "ScenePad",
    "ScenePolygon",
    "SceneTrace",
    "SceneJoin",
    "launch_viewer",
    "scene_from_edb",
]


def scene_from_edb(edb, layers=None, nets=None, arc_segments=32):
    """Capture a gRPC EDB layout as independent, millimeter-based scene data."""
    from pyedb.viewer.adapters.grpc import scene_from_edb as extract

    return extract(edb, layers=layers, nets=nets, arc_segments=arc_segments)


def launch_viewer(
    edb=None,
    *,
    scene=None,
    layers=None,
    nets=None,
    arc_segments=32,
    block=None,
    color_by_net=True,
    plot_components=True,
    annotate_component_names=True,
    plot_components_on_both_side=True,
):
    """Open an interactive OpenGL layout window.

    Parameters
    ----------
    edb : pyedb.grpc.edb.Edb, optional
        Existing gRPC session. Its lifetime remains controlled by the caller.
    scene : LayoutScene, optional
        Detached scene to display instead of reading an EDB session.
    layers, nets : str or list[str], optional
        Names to include when capturing an EDB layout.
    arc_segments : int, optional
        Number of segments per EDB arc. Default is 32.
    block : bool, optional
        Run the Qt event loop. By default, run it only when this call creates
        QApplication. With an existing application, return the window directly.
    color_by_net : bool, optional
        Use PyEDB's existing network palette instead of layer colors. Default is True.
    plot_components : bool, optional
        Show component bounding boxes, as in ``edb.nets.plot``. Default is True.
    annotate_component_names : bool, optional
        Show readable, nonoverlapping reference names. Default is True.
    plot_components_on_both_side : bool, optional
        Show components on all visible placement layers. Default is True.
        Set False to restrict them to the current view side.

    Returns
    -------
    pyedb.viewer.qt.window.LayoutWindow
        Keep a reference when displaying the window without blocking.
    """
    if (edb is None) == (scene is None):
        raise ValueError("Provide exactly one of edb or scene.")
    try:
        from pyedb.viewer.qt.app import show_scene
    except ImportError as exc:
        raise ImportError("The layout viewer requires optional dependencies: pip install 'pyedb[viewer]'.") from exc
    if scene is None:
        scene = scene_from_edb(edb, layers=layers, nets=nets, arc_segments=arc_segments)
    return show_scene(
        scene,
        block=block,
        color_by_net=color_by_net,
        plot_components=plot_components,
        annotate_component_names=annotate_component_names,
        plot_components_on_both_side=plot_components_on_both_side,
    )
