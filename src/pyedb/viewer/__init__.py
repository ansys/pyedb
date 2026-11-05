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

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from pyedb.viewer.picking import PickedObject
from pyedb.viewer.scene import (
    LayoutScene,
    SceneComponent,
    SceneJoin,
    SceneLayer,
    SceneObjectInfo,
    ScenePad,
    ScenePolygon,
    SceneTrace,
)

if TYPE_CHECKING:
    from pyedb.viewer.qt.window import LayoutWindow

__all__ = [
    "LayoutScene",
    "PickedObject",
    "SceneComponent",
    "SceneLayer",
    "SceneObjectInfo",
    "ScenePad",
    "ScenePolygon",
    "SceneTrace",
    "SceneJoin",
    "launch_viewer",
    "scene_from_edb",
]


def scene_from_edb(
    edb: Any,
    layers: str | list[str] | None = None,
    nets: str | list[str] | None = None,
    arc_segments: int | None = None,
    *,
    progress: Callable[[str, int, int], None] | None = None,
    analytic_traces: bool = True,
    exact_component_bounds: bool = False,
    chord_error: float = 0.002,
    preview: Callable[..., Any] | None = None,
    debug: bool = False,
) -> LayoutScene:
    """Capture detached millimeter-based geometry.

    ``progress(stage, completed, total)`` optionally reports completed items in
    the current stage. A zero total means the amount of work is not yet known.
    When ``debug`` is True, exceptions caught during capture are logged with a
    full traceback and re-raised immediately instead of being recorded as a
    diagnostic note and skipped.
    """
    from pyedb.viewer.adapters.grpc import scene_from_edb as extract

    return extract(
        edb,
        layers=layers,
        nets=nets,
        arc_segments=arc_segments,
        progress=progress,
        analytic_traces=analytic_traces,
        exact_component_bounds=exact_component_bounds,
        chord_error=chord_error,
        preview=preview,
        debug=debug,
    )


def launch_viewer(
    edb: Any = None,
    *,
    scene: LayoutScene | None = None,
    layers: str | list[str] | None = None,
    nets: str | list[str] | None = None,
    arc_segments: int | None = None,
    block: bool | None = None,
    color_by_net: bool = True,
    plot_components: bool = True,
    annotate_component_names: bool = True,
    plot_components_on_both_side: bool = True,
    plot_outlines: bool = True,
    analytic_traces: bool = False,
    exact_component_bounds: bool = False,
    chord_error: float = 0.002,
    progressive: bool = True,
    debug: bool = False,
    backend: str | None = None,
) -> LayoutWindow:
    """Open an interactive Qt RHI layout window.

    Parameters
    ----------
    edb : pyedb.grpc.edb.Edb, optional
        Existing gRPC session. Its lifetime remains controlled by the caller.
        Capture runs in one background worker with progress in the viewer canvas.
    scene : LayoutScene, optional
        Detached scene to display instead of reading an EDB session.
    layers, nets : str or list[str], optional
        Names to include when capturing an EDB layout.
    arc_segments : int, optional
        Select fixed subdivisions per EDB arc. By default use adaptive chords.
        Providing this parameter overrides ``chord_error``.
    chord_error : float, optional
        Maximum chord sagitta in millimeters. Default is 0.002 mm. Segment
        counts adapt to radius and total sweep, with at most 10 degrees per chord.
    progressive : bool, optional
        Display the current layer first, then remaining copper, pads and
        components. Default is True. One progress indicator remains until complete.
    analytic_traces : bool, optional
        Preserve analytic traces for precision at deep zoom. Default is False:
        read source path contours to reduce remote geometry-property requests.
    exact_component_bounds : bool, optional
        Read exact component envelopes from EDB. Default is False: reuse pad
        bounds and estimate copper-free footprints from pin positions.
    block : bool, optional
        Run the Qt event loop. By default, run it only when this call creates
        QApplication. With an existing application, return the window directly.
    color_by_net : bool, optional
        Use PyEDB's existing network palette instead of layer colors. Default is True.
    plot_components : bool, optional
        Show component envelopes derived from captured pads, with source bounds
        as a fallback. Default is True.
    annotate_component_names : bool, optional
        Show readable, nonoverlapping reference names. Default is True.
    plot_components_on_both_side : bool, optional
        Show components on all visible placement layers. Default is True.
        Set False to restrict them to the current view side.
    plot_outlines : bool, optional
        Draw an opaque net-colored outline, one screen pixel wide, around every
        shape. Default is True. It can also be toggled from the View menu.
    debug : bool, optional
        When True, exceptions caught during capture are logged with a full
        traceback and re-raised immediately instead of being recorded as a
        diagnostic note and skipped. Default is False.

    backend : str, optional
        Rendering API: "auto", "vulkan", "d3d11", or "metal". Defaults to
        PYEDB_VIEWER_BACKEND or "auto": Direct3D 11 on Windows, Vulkan on
        Linux, Metal on macOS. OpenGL is not supported.

    Returns
    -------
    pyedb.viewer.qt.window.LayoutWindow
        Viewer window. Keep a reference when displaying the window without
        blocking. Use its signals and methods to interact with the view.
    """
    if (edb is None) == (scene is None):
        raise ValueError("Provide exactly one of edb or scene.")
    try:
        from pyedb.viewer.qt.app import show_scene
    except ImportError as exc:
        raise ImportError("The layout viewer requires optional dependencies: pip install 'pyedb[viewer]'.") from exc
    options: dict[str, Any] = {}
    if scene is None:
        from pathlib import Path

        from pyedb.viewer.capture import SourceCapture

        def load(
            progress: Callable[[str, int, int], None] | None, preview: Callable[..., Any] | None = None
        ) -> LayoutScene:
            return scene_from_edb(
                edb,
                layers=layers,
                nets=nets,
                arc_segments=arc_segments,
                progress=progress,
                analytic_traces=analytic_traces,
                exact_component_bounds=exact_component_bounds,
                chord_error=chord_error,
                preview=preview,
                debug=debug,
            )

        options["title"] = Path(str(getattr(edb, "edbpath", None) or "EDB layout")).stem
        options["loader"] = SourceCapture(load, progressive=progressive)
    return show_scene(
        scene,
        block=block,
        backend=backend,
        color_by_net=color_by_net,
        plot_components=plot_components,
        annotate_component_names=annotate_component_names,
        plot_components_on_both_side=plot_components_on_both_side,
        plot_outlines=plot_outlines,
        **options,
    )
