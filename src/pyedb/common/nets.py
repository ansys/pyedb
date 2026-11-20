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

import math
import time
from typing import TYPE_CHECKING

import numpy as np

from pyedb.generic.constants import CSS4_COLORS

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

# Angles used to approximate round pads and vias (32 segments, closed ring).
_CIRCLE_ANGLES = np.linspace(0.0, 2.0 * np.pi, 33)
_CIRCLE_COS = np.cos(_CIRCLE_ANGLES)
_CIRCLE_SIN = np.sin(_CIRCLE_ANGLES)


# Color of the vias (opaque).
_VIA_COLOR = (0.85, 0.65, 0.13)

_DATA_WIDTH_LINE_COLLECTION = None


def _data_width_line_collection():
    """Return the ``LineCollection`` subclass drawing lines with a width given in data units.

    The class is created on first use to avoid importing matplotlib when pyedb is imported.
    """
    global _DATA_WIDTH_LINE_COLLECTION
    if _DATA_WIDTH_LINE_COLLECTION is None:
        from matplotlib.collections import LineCollection

        class DataWidthLineCollection(LineCollection):
            """Line collection whose line width is given in data units (e.g. meters)."""

            def __init__(self, segments, data_width, **kwargs):
                super().__init__(segments, **kwargs)
                self.data_width = data_width

            def draw(self, renderer):
                # Pixels covered by one data unit. The mean of the two directions is used so the width is
                # reasonable also if the aspect ratio of the axes is not equal.
                origin, unit_x, unit_y = self.axes.transData.transform([(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)])
                pixels_per_unit = 0.5 * (np.hypot(*(unit_x - origin)) + np.hypot(*(unit_y - origin)))
                self.set_linewidth(self.data_width * pixels_per_unit / renderer.points_to_pixels(1.0))
                super().draw(renderer)

        _DATA_WIDTH_LINE_COLLECTION = DataWidthLineCollection
    return _DATA_WIDTH_LINE_COLLECTION


class CommonNets:
    def __init__(self, _pedb):
        self._pedb = _pedb

    # ------------------------------------------------------------------------------------------------------------------
    # Plot helpers
    #
    # Geometry is handled as plain numpy arrays. A "polygon" is a tuple ``(exterior, holes)`` where ``exterior`` is a
    # closed ``(n, 2)`` array oriented counter-clockwise and ``holes`` is a list of closed arrays oriented clockwise.
    # Such an orientation is required to render holes when everything is drawn as one compound matplotlib path.
    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def _ring(x, y, sign, ccw):
        """Return a closed ``(n, 2)`` ring, mirrored if ``sign`` is ``-1`` and with the requested orientation.

        Returns ``None`` if the ring has less than 3 points.
        """
        if len(x) < 3:
            return None
        ring = np.empty((len(x) + 1, 2))
        ring[:-1, 0] = x
        ring[:-1, 1] = y
        if sign < 0:
            ring[:-1, 0] *= -1.0
        px = ring[:-1, 0]
        py = ring[:-1, 1]
        # Twice the signed area (shoelace formula): positive for a counter-clockwise ring.
        area = np.dot(px, np.roll(py, -1)) - np.dot(py, np.roll(px, -1))
        if (area > 0) != ccw:
            ring[:-1] = ring[-2::-1]
        ring[-1] = ring[0]
        return ring

    @staticmethod
    def _polygons_path(polygons):
        """Merge polygons in a single compound matplotlib ``Path``."""
        from matplotlib.path import Path

        rings = []
        for exterior, holes in polygons:
            rings.append(exterior)
            rings.extend(holes)
        vertices = np.concatenate(rings)
        codes = np.full(len(vertices), Path.LINETO, dtype=Path.code_type)
        starts = np.cumsum([0] + [len(ring) for ring in rings[:-1]])
        codes[starts] = Path.MOVETO
        return Path(vertices, codes), vertices

    @staticmethod
    def _add_polygons(ax, polygons, bounds, color=None, facecolor=None, edgecolor=None, alpha=None, label=None):
        """Draw polygons as a single compound path.

        Polygons are added with ``Axes.add_artist`` and the data limits are updated by the caller from ``bounds``.
        ``Axes.add_patch`` (used by ``shapely.plotting``) recomputes the limits of the patch segment by segment in
        Python, which takes most of the plot time on large layouts.
        """
        from matplotlib import colors
        from matplotlib.patches import PathPatch

        path, vertices = CommonNets._polygons_path(polygons)
        rgba = colors.to_rgba("C0" if color is None else color)
        if facecolor is None:
            facecolor = rgba[:3] + (0.3,)
        if edgecolor is None:
            edgecolor = rgba
        ax.add_artist(PathPatch(path, facecolor=facecolor, edgecolor=edgecolor, alpha=alpha, label=label))
        bounds.append(vertices)

    @staticmethod
    def _add_lines(ax, lines, bounds, color, linewidth, label=None):
        """Draw a list of ``(n, 2)`` polylines as one line collection (see :meth:`_add_polygons`)."""
        from matplotlib.collections import LineCollection

        ax.add_artist(LineCollection(lines, colors=[color], linewidths=linewidth, label=label))
        bounds.append(np.concatenate(lines))

    @staticmethod
    def _add_strokes(ax, strokes, bounds, color, alpha=None, label=None):
        """Draw paths as thick lines whose width is expressed in data units.

        Parameters
        ----------
        strokes : list
            List of ``(points, width, end_cap, corner_style)``.

        Notes
        -----
        Paths with the same width and styles are drawn by the same collection. The line width is converted from data
        units to points every time the collection is drawn (see :func:`_data_width_line_collection`), so it stays
        correct when the figure is zoomed, resized or saved with a different resolution.
        """
        cap_styles = {"flat": "butt", "round": "round", "extended": "projecting"}
        join_styles = {"round": "round", "miter": "miter", "sharp": "miter"}
        groups = {}
        for line, width, end_cap, corner_style in strokes:
            key = (width, cap_styles.get(end_cap, "round"), join_styles.get(corner_style, "round"))
            groups.setdefault(key, []).append(line)
        collection_class = _data_width_line_collection()
        for (width, cap_style, join_style), lines in groups.items():
            ax.add_artist(
                collection_class(
                    lines,
                    width,
                    colors=[color],
                    alpha=alpha,
                    capstyle=cap_style,
                    joinstyle=join_style,
                    label=label,
                    # Same z-order as the polygons (a ``LineCollection`` has 2 by default) so that the layers are
                    # stacked in the order they are drawn.
                    zorder=1,
                )
            )
            all_points = np.concatenate(lines)
            bounds.append(np.array([all_points.min(axis=0) - width / 2, all_points.max(axis=0) + width / 2]))

    def _get_pad_data(self, pinst, layer_name, definitions_cache, pad_cache):
        """Return ``(shape, parameters, rotation)`` of the pad of a padstack instance on a layer.

        Pad information is cached by padstack definition name and layer. A design usually has thousands of
        padstack instances but only a few padstack definitions, so this avoids a large number of backend calls.

        Returns
        -------
        tuple or None
            ``(shape, parameters, rotation)`` with ``shape`` lower case, ``parameters`` a list of floats and
            ``rotation`` in radians. ``None`` if the padstack has no pad on the layer.
        """
        def_name = pinst.padstack_definition
        key = (def_name, layer_name)
        if key in pad_cache:
            return pad_cache[key]
        data = None
        try:
            pdef = definitions_cache.get(def_name)
            if pdef is None:
                pdef = pinst.definition
                definitions_cache[def_name] = pdef
            pad = pdef.pad_by_layer.get(layer_name)
            if pad is not None:
                params = pad.parameters_values
                if params:
                    data = (
                        str(pad.shape).lower(),
                        [float(v) for v in params],
                        float(pad.rotation),
                    )
        except (KeyError, TypeError, ValueError, AttributeError):
            data = None
        pad_cache[key] = data
        return data

    @staticmethod
    def _build_pad(pad_data, x, y, rotation, sign):
        """Create the polygon of a pad.

        Parameters
        ----------
        pad_data : tuple
            ``(shape, parameters, rotation)`` as returned by :meth:`_get_pad_data`.
        x, y : float
            Pad position.
        rotation : float
            Rotation of the instance (and component) in radians, added to the pad rotation.
        sign : int
            ``1`` for top view, ``-1`` for bottom view (mirrored).

        Returns
        -------
        tuple or None
            Polygon ``(exterior, holes)``. ``None`` if the pad shape is not supported.
        """
        shape, params, pad_rotation = pad_data
        cx = sign * x
        if shape == "circle":
            radius = params[0] / 2
            ring = np.column_stack((cx + radius * _CIRCLE_COS, y + radius * _CIRCLE_SIN))
            return ring, []
        if shape in ("rectangle", "square"):
            w = params[0]
            h = params[1] if shape == "rectangle" and len(params) > 1 else w
            angle = sign * (pad_rotation + rotation)
            cos_a, sin_a = math.cos(angle), math.sin(angle)
            corners = np.array(
                [[-w / 2, -h / 2], [w / 2, -h / 2], [w / 2, h / 2], [-w / 2, h / 2], [-w / 2, -h / 2]], dtype=float
            )
            ring = corners @ np.array([[cos_a, sin_a], [-sin_a, cos_a]])
            ring[:, 0] += cx
            ring[:, 1] += y
            return ring, []
        return None

    def _collect_components(
        self,
        net_filter,
        layer_set,
        top_layer,
        bottom_layer,
        top_view,
        both_sides,
        annotate,
        component_colors,
        definitions_cache,
        pad_cache,
    ):
        """Collect pads, outlines and annotations of the components to plot."""
        sign = 1 if top_view else -1
        pads = {True: [], False: []}
        outlines = {True: [], False: []}
        annotations = []
        count = 0
        for comp in self._pedb.components.instances.values():
            if not comp.is_enabled:
                continue
            layer_name = comp.placement_layer
            if layer_name not in layer_set:
                continue
            if layer_name == top_layer:
                is_top = True
            elif layer_name == bottom_layer:
                is_top = False
            else:
                continue
            if not both_sides and is_top != top_view:
                continue

            # Query the pins only once: the net of each pin is used both to filter the component and its pads.
            pins = [(pin, pin.net_name) for pin in comp.pins.values()]
            if net_filter is not None and not any(net in net_filter for _, net in pins):
                continue

            comp_rotation = float(comp.rotation)
            for pin, pin_net in pins:
                if net_filter is not None and pin_net not in net_filter:
                    continue
                pad_data = self._get_pad_data(pin, layer_name, definitions_cache, pad_cache)
                if pad_data is None:
                    continue
                x, y = pin.position
                pad = self._build_pad(pad_data, float(x), float(y), float(pin.rotation) + comp_rotation, sign)
                if pad is not None:
                    pads[is_top].append(pad)

            bbox = comp.bounding_box
            outlines[is_top].append(
                np.array(
                    [
                        [sign * bbox[0], bbox[1]],
                        [sign * bbox[0], bbox[3]],
                        [sign * bbox[2], bbox[3]],
                        [sign * bbox[2], bbox[1]],
                        [sign * bbox[0], bbox[1]],
                    ]
                )
            )
            count += 1

            if annotate:
                width = abs(bbox[2] - bbox[0])
                height = abs(bbox[3] - bbox[1])
                angle = math.degrees(comp_rotation) % 180
                annotations.append(
                    dict(
                        text=comp.name,
                        xy=(sign * (bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2),
                        color=component_colors[is_top],
                        size=6 if width * height < 6e-6 else 10,
                        rotation=90 if math.isclose(angle, 90, abs_tol=1e-6) else 0,
                    )
                )
        return pads, outlines, annotations, count

    def _primitive_geometry(self, prim, sign, net_filter, layer_set, check_layer, paths_as_lines):
        """Convert a primitive to the geometry to draw.

        Returns
        -------
        tuple or None
            ``("plane", (exterior, holes))`` for a polygon, ``("trace", (exterior, holes))`` for any other primitive
            or, for a path drawn as a thick line, ``("stroke", (points, width, end_cap, corner_style))``.
            ``None`` if the primitive must not be plotted.
        """
        if prim.is_void:
            return None
        if net_filter is not None and prim.net_name not in net_filter:
            return None
        if check_layer and prim.layer_name not in layer_set:
            return None
        if paths_as_lines:
            # Only the gRPC paths provide ``stroke_data``. Paths have no voids.
            stroke_data = getattr(prim, "stroke_data", None)
            stroke = stroke_data() if stroke_data is not None else None
            if stroke is not None:
                line = np.column_stack((stroke["x"], stroke["y"]))
                line[:, 0] *= sign
                return "stroke", (line, stroke["width"], stroke["end_cap"], stroke["corner_style"])
        # Skip the (slow) orientation done by the gRPC backend: the orientation is set in ``_ring``.
        kwargs = {"orient": False} if self._pedb.grpc else {}
        points = prim.points(**kwargs)
        if not points:
            return None
        exterior = self._ring(points[0], points[1], sign, ccw=True)
        if exterior is None:
            return None
        holes = []
        for void in prim.voids:
            void_points = void.points(arc_segments=3, **kwargs)
            if not void_points:
                continue
            hole = self._ring(void_points[0], void_points[1], sign, ccw=False)
            if hole is not None:
                holes.append(hole)
        # Polygons (planes) are drawn semi-transparent, everything else (paths, ...) is drawn opaque.
        return ("plane" if prim.type == "polygon" else "trace"), (exterior, holes)

    def _outline_layer_extent(self, outline_prims, sign):
        """Return the extent ``[[x_min, y_min], [x_max, y_max]]`` of the primitives of the Outline layer.

        Returns ``None`` if there are no such primitives.
        """
        kwargs = {"orient": False} if self._pedb.grpc else {}
        vertices = []
        for prim in outline_prims:
            if prim.is_void:
                continue
            points = prim.points(**kwargs)
            if points:
                vertices.append(np.column_stack(points))
        if not vertices:
            return None
        vertices = np.concatenate(vertices)
        vertices[:, 0] *= sign
        return np.array([vertices.min(axis=0), vertices.max(axis=0)])

    def plot(
        self,
        nets: str | list[str] = None,
        layers: str | list[str] = None,
        color_by_net: bool = False,
        show_legend: bool = True,
        save_plot: str = None,
        outline: list[list[float]] = None,
        size: list | tuple = (6000, 3000),
        plot_components: bool = True,
        top_view: bool = True,
        show: bool = True,
        annotate_component_names: bool = True,
        plot_vias: bool = False,
        title: str = None,
        outline_width: int = 4,
        plot_components_on_both_side: bool = False,
        component_top_color: tuple = (0, 0, 0),
        component_bottom_color: tuple = (41 / 255, 41 / 255, 41 / 255),
        paths_as_lines: bool = False,
        plane_alpha: float = 0.5,
        **kwargs,
    ) -> tuple["Figure", "Axes"] | None:
        """Plot a Net to Matplotlib 2D Chart.

        Parameters
        ----------
        nets : str, list, optional
            Name of the net or list of nets to plot. If ``None`` all nets will be plotted.
        layers : str, list, optional
            Name of the layers to include in the plot. If ``None`` all the signal layers will be considered.
        color_by_net : bool, optional
            If ``True``  the plot will be colored by net.
            If ``False`` the plot will be colored by layer. (default)
        show_legend : bool, optional
            If ``True`` the legend is shown in the plot. (default)
            If ``False`` the legend is not shown.
        save_plot : str, optional
            If a path is specified the plot will be saved in this location.
            If ``save_plot`` is provided, the ``show`` parameter is ignored.
        outline : list, optional
            List of points of the outline to plot. If ``None`` a red frame is drawn around the primitives of the
            ``Outline`` layer or, if the design has no ``Outline`` layer primitives, around the plotted objects.
        size : tuple, int, optional
            Image size in pixel (width, height). If an integer is provided the height is half of the width.
            Default value is ``(6000, 3000)``. Smaller values make the plot generation faster.
        plot_components : bool, optional
            If ``True``  the components placed on top layer are plotted. (default)
            If ``False`` the components are not plotted.
            This may impact in the plot computation time.
            If nets and/or layers is specified, only the components belonging to the specified nets/layers are plotted.
        top_view : bool, optional
            Whether if use top view or bottom view. Components will be visible only for the highest layer in the view.
        show : bool, optional
            Whether to show the plot or not. Default is `True`.
        annotate_component_names: bool, optional
            Whether to add the component names to the plot or not. Default is ``True``.
        plot_vias : bool, optional
            Whether to plot vias (circular and rectangular) or not. This may impact in the plot computation time.
            Default is ``False``.
        title : str, optional
            Specify the default plot title. Is value is ``None`` the project name is assigned by default. Default value
            is ``None``.
        outline_width : int, optional
            Line width of the outline. Default is ``4``.
        plot_components_on_both_side : bool, optional
            Whether to plot the components of both the top and the bottom layer. Default is ``False``.
        component_top_color : tuple, optional
            RGB color used for the components placed on the top layer. Default is black.
        component_bottom_color : tuple, optional
            RGB color used for the components placed on the bottom layer.
        paths_as_lines : bool, optional
            Whether to draw the paths as thick lines (center line and width) instead of the polygon computed by
            the server. This is faster on designs with many paths and produces much lighter figures, but it is an
            approximation: paths with different or clipped end caps are still drawn as polygons, the mitre limit
            of the corners is the one of matplotlib, and overlapping traces are blended twice when the layer
            transparency is applied. The axes use an equal aspect ratio so the width is not distorted. Only
            available with the gRPC backend. Default is ``False``.
        plane_alpha : float, optional
            Opacity (``0`` transparent, ``1`` opaque) of the polygons (planes). Paths, other primitives, component
            pads and vias are always opaque. Layers are drawn from the farthest to the nearest to the viewer and all
            the planes are drawn before the traces, so the nets of every layer remain visible. Default is ``0.5``.

        Returns
        -------
        (fig, ax)
            Matplotlib figure and axes.
        """
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            raise ImportError(
                "Matplotlib library is required for plotting. "
                "Please install it using 'pip install pyedb[graphics]' or 'pip install matplotlib'."
            )
        from matplotlib.patches import Patch

        if "plot_components_on_top" in kwargs and top_view:
            plot_components = kwargs["plot_components_on_top"]
        if "plot_components_on_bottom" in kwargs and not top_view:
            plot_components = kwargs["plot_components_on_bottom"]

        start_time = time.time()
        sign = 1 if top_view else -1

        # Net and layer filters. A set gives O(1) membership tests in the per-pin and per-primitive loops.
        if isinstance(nets, str):
            nets = [nets]
        net_filter = set(nets) if nets else None
        if isinstance(layers, str):
            layers = [layers]
        signal_layers = list(self._pedb.stackup.signal_layers.keys())
        if not layers:
            layers = signal_layers
        layers = list(layers)
        layer_set = set(layers)
        top_layer = signal_layers[0]
        bottom_layer = signal_layers[-1]
        component_colors = {True: component_top_color, False: component_bottom_color}

        css_colors = list(CSS4_COLORS.keys())
        color_state = {"index": 0}

        def next_css_color():
            color = css_colors[color_state["index"]]
            color_state["index"] = (color_state["index"] + 1) % len(css_colors)
            return color

        # Padstack data is cached by definition: thousands of pins share few definitions.
        definitions_cache = {}
        pad_cache = {}

        # --------------------------------------------------------------------------------------------------------------
        # Gather the geometry (all the backend access is done here).
        # --------------------------------------------------------------------------------------------------------------
        # The frame is the outline given by the user. Otherwise it is computed after the geometry is gathered, from
        # the Outline layer or, if the design has no Outline layer, from the extent of the objects to plot.
        outline_ring = None
        if outline:
            outline_ring = np.asarray(outline, dtype=float)
            outline_ring = np.vstack((outline_ring, outline_ring[:1]))
        prims_by_layer = None

        comp_pads = {True: [], False: []}
        comp_outlines = {True: [], False: []}
        annotations = []
        if plot_components:
            comp_pads, comp_outlines, annotations, comp_count = self._collect_components(
                net_filter,
                layer_set,
                top_layer,
                bottom_layer,
                top_view,
                plot_components_on_both_side,
                annotate_component_names,
                component_colors,
                definitions_cache,
                pad_cache,
            )
            self._logger.debug("Plotted {} component(s)".format(comp_count))

        # Layer colors: the stackup color or, if it is not available, a CSS color.
        layer_colors = {}
        for name, stackup_layer in self._pedb.stackup.layers.items():
            try:
                color = stackup_layer.color
                layer_colors[name] = (float(color[0] / 255), float(color[1] / 255), float(color[2] / 255))
            except (TypeError, IndexError):
                layer_colors[name] = next_css_color()

        def layer_color(layer_name):
            if layer_name not in layer_colors:
                layer_colors[layer_name] = next_css_color()
            return layer_colors[layer_name]

        # Each artist is ``(label, color, planes, traces, outlines, strokes)``.
        artists = []
        if color_by_net:
            nets_dict = self._pedb.nets.nets
            for net in nets if nets else nets_dict.keys():
                if net not in nets_dict:
                    continue
                planes = []
                traces = []
                lines = []
                strokes = []
                for prim in nets_dict[net].primitives:
                    geometry = self._primitive_geometry(
                        prim, sign, net_filter, layer_set, check_layer=True, paths_as_lines=paths_as_lines
                    )
                    if geometry is None:
                        continue
                    kind, data = geometry
                    if kind == "stroke":
                        strokes.append(data)
                    elif "Outline" in layer_set and prim.layer_name == "Outline":
                        lines.append(data[0])
                    elif kind == "plane":
                        planes.append(data)
                    else:
                        traces.append(data)
                if planes or traces or lines or strokes:
                    artists.append(("Net " + net, next_css_color(), planes, traces, lines, strokes))
        else:
            prims_by_layer = dict(self._pedb.layout.primitives_by_layer.items())
            # Layers are drawn from the farthest to the nearest to the viewer, so that the nearest is on top.
            # The stackup order goes from the top layer to the bottom layer.
            if top_view:
                prims_by_layer = {layer: prims_by_layer[layer] for layer in reversed(list(prims_by_layer.keys()))}
            for layer, prims in prims_by_layer.items():
                if layer not in layer_set:
                    continue
                planes = []
                traces = []
                lines = []
                strokes = []
                for prim in prims:
                    # The layer is known here: the primitives are already grouped by layer.
                    geometry = self._primitive_geometry(
                        prim, sign, net_filter, layer_set, check_layer=False, paths_as_lines=paths_as_lines
                    )
                    if geometry is None:
                        continue
                    kind, data = geometry
                    if kind == "stroke":
                        strokes.append(data)
                    elif layer == "Outline":
                        lines.append(data[0])
                    elif kind == "plane":
                        planes.append(data)
                    else:
                        traces.append(data)
                if planes or traces or lines or strokes:
                    artists.append(("Layer " + layer, layer_color(layer), planes, traces, lines, strokes))

        via_polys = []
        if plot_vias:
            ordered_layers = layers if top_view else layers[::-1]
            for pinst in self._pedb.padstacks.instances.values():
                if pinst.is_pin:
                    continue
                if net_filter is not None and pinst.net_name not in net_filter:
                    continue
                pad_data = None
                for layer in ordered_layers:
                    pad_data = self._get_pad_data(pinst, layer, definitions_cache, pad_cache)
                    if pad_data is not None:
                        break
                if pad_data is None:
                    continue
                x, y = pinst.position
                pad = self._build_pad(pad_data, float(x), float(y), float(pinst.rotation), sign)
                if pad is not None:
                    via_polys.append(pad)

        outline_extent = None
        if outline_ring is None:
            if prims_by_layer is None:
                prims_by_layer = self._pedb.layout.primitives_by_layer
            outline_extent = self._outline_layer_extent(prims_by_layer.get("Outline", []), sign)

        # --------------------------------------------------------------------------------------------------------------
        # Draw.
        # --------------------------------------------------------------------------------------------------------------
        dpi = 100.0
        if isinstance(size, (int, float)):
            size = (size, size / 2)
        fig = plt.figure(figsize=(size[0] / dpi, size[1] / dpi))
        ax = fig.add_subplot(1, 1, 1)
        bounds = []  # vertices of everything that is drawn, used to set the data limits once.
        legend_handles = []

        if outline_ring is not None:
            self._add_lines(ax, [outline_ring], bounds, (0.7, 0, 0), outline_width)

        # Planes first, then traces, pads and vias: everything but the planes is opaque, so the nets of every layer
        # are visible through the semi-transparent planes whatever the number of layers above them.
        for label, color, planes, traces, lines, strokes in artists:
            if planes:
                self._add_polygons(ax, planes, bounds, facecolor=color, edgecolor="none", alpha=plane_alpha)
            legend_handles.append(Patch(facecolor=color, label=label))
        for label, color, planes, traces, lines, strokes in artists:
            if traces:
                self._add_polygons(ax, traces, bounds, facecolor=color, edgecolor="none")
            if strokes:
                self._add_strokes(ax, strokes, bounds, color)
            if lines:
                self._add_lines(ax, lines, bounds, color, 1)
        # The artists are drawn from the farthest layer: list the legend entries in stackup order.
        if top_view and not color_by_net:
            legend_handles.reverse()

        for is_top in (True, False):
            if comp_pads[is_top]:
                pad_layer = top_layer if is_top else bottom_layer
                self._add_polygons(
                    ax,
                    comp_pads[is_top],
                    bounds,
                    facecolor=layer_color(pad_layer),
                    edgecolor=component_colors[is_top],
                )
        if via_polys:
            self._add_polygons(ax, via_polys, bounds, facecolor=_VIA_COLOR, edgecolor="none")

        for is_top in (True, False):
            if comp_outlines[is_top]:
                self._add_lines(ax, comp_outlines[is_top], bounds, component_colors[is_top], 1)
        for annotation in annotations:
            ax.annotate(
                annotation["text"],
                annotation["xy"],
                va="center",
                ha="center",
                color=annotation["color"],
                size=annotation["size"],
                rotation=annotation["rotation"],
            )

        if outline_ring is None:
            # Frame drawn last: the extent of the Outline layer or, without it, the extent of what has been drawn.
            if outline_extent is None and bounds:
                all_vertices = np.concatenate(bounds)
                outline_extent = np.array([all_vertices.min(axis=0), all_vertices.max(axis=0)])
            if outline_extent is not None:
                (x1, y1), (x2, y2) = outline_extent
                frame = np.array([[x1, y1], [x1, y2], [x2, y2], [x2, y1], [x1, y1]], dtype=float)
                self._add_lines(ax, [frame], bounds, (0.7, 0, 0), outline_width)

        # Data limits are set once from the collected vertices.
        if bounds:
            all_vertices = np.concatenate(bounds)
            ax.update_datalim([all_vertices.min(axis=0), all_vertices.max(axis=0)])
            ax.autoscale_view()
        if paths_as_lines:
            # The width of the paths is a length in data units: x and y must have the same scale.
            ax.set_aspect("equal")

        # Hide grid lines and axes.
        ax.grid(False)
        ax.set_axis_off()
        ax.set_xticks([])
        ax.set_yticks([])
        if not title:
            if not self._pedb.grpc:
                title = self._pedb.active_cell.GetName()
            else:
                title = self._pedb.active_cell.name
        message = f"Edb Top View {title}" if top_view else f"Edb Bottom View {title}"
        ax.set_title(message, size=20)
        if show_legend and legend_handles:
            ax.legend(handles=legend_handles, loc="upper left", fontsize="x-large")
        if save_plot:
            fig.savefig(save_plot)
        elif show:
            plt.show()
        end_time = time.time() - start_time
        self._logger.info(f"Plot Generation time {round(end_time, 3)}")
        return fig, ax
