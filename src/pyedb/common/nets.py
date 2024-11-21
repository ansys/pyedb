import math
import os
import time

import shapely

from pyedb.generic.constants import CSS4_COLORS


def is_notebook():
    """Check if pyaedt is running in Jupyter or not.

    Returns
    -------
    bool
    """
    try:
        shell = get_ipython().__class__.__name__
        if shell in ["ZMQInteractiveShell"]:  # pragma: no cover
            return True  # Jupyter notebook or qtconsole
        else:
            return False
    except NameError:
        return False  # Probably standard Python interpreter


def is_ipython():
    """Check if pyaedt is running in Jupyter or not.

    Returns
    -------
    bool
    """
    try:
        shell = get_ipython().__class__.__name__
        if shell in ["TerminalInteractiveShell", "SpyderShell"]:
            return True  # Jupyter notebook or qtconsole
        else:  # pragma: no cover
            return False
    except NameError:
        return False  # Probably standard Python interpreter


class CommonNets:
    def __init__(self, _pedb):
        self._pedb = _pedb

    def plot(
        self,
        nets=None,
        layers=None,
        color_by_net=False,
        show_legend=True,
        save_plot=None,
        outline=None,
        size=(6000, 3000),
        plot_components=True,
        top_view=True,
        show=True,
        annotate_component_names=True,
        plot_vias=False,
        include_outline=True,
        plot_edges=True,
        **kwargs,
    ):
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
            Add a customer outline from a list of points of the outline to plot.
        size : tuple, int, optional
            Image size in pixel (width, height). Default value is ``(6000, 3000)``
        top_view : bool, optional
            Whether if use top view or bottom view. Components will be visible only for the highest layer in the view.
        plot_components : bool, optional
            If ``True``  the components placed on top layer are plotted.
            If ``False`` the components are not plotted. (default).
            This may impact in the plot computation time.
            If nets and/or layers is specified, only the components belonging to the specified nets/layers are plotted.
        annotate_component_names: bool, optional
            Whether to add the component names to the plot or not. Default is ``True``.
        plot_vias : bool, optional
            Whether to plot vias (circular and rectangular) or not. This may impact in the plot computation time.
            Default is ``False``.
        show : bool, optional
            Whether to show the plot or not. Default is `True`.
        include_outline : bool, optional
            Whether to include the internal layout outline or not. Default is `True`.
        plot_edges : bool, optional
            Whether to plot polygon edges or not. Default is `True`.

        Returns
        -------
        (ax, fig)
            Matplotlib ax and figures.
        """

        if "plot_components_on_top" in kwargs and top_view:
            plot_components = kwargs["plot_components_on_top"]
        if "plot_components_on_bottom" in kwargs and not top_view:
            plot_components = kwargs["plot_components_on_bottom"]

        def mirror_poly(poly):
            sign = 1
            if not top_view:
                sign = -1
            return [[sign * i[0], i[1]] for i in poly]

        import matplotlib.pyplot as plt

        dpi = 100.0
        figsize = (size[0] / dpi, size[1] / dpi)

        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(1, 1, 1)
        from shapely import affinity
        from shapely.geometry import (
            LinearRing,
            MultiLineString,
            MultiPolygon,
            Point,
            Polygon,
        )
        from shapely.plotting import plot_line, plot_polygon

        start_time = time.time()
        if not nets:
            nets = list(self.nets.keys())
        if isinstance(nets, str):
            nets = [nets]
        if not layers:
            layers = list(self._pedb.stackup.signal_layers.keys())
        if isinstance(layers, str):
            layers = [layers]
        color_index = 0
        label_colors = {}
        edge_colors = {}
        if outline:
            poly = Polygon(outline)
            plot_line(poly.boundary, add_points=False, color=(0.7, 0, 0), linewidth=4)
        elif include_outline:
            prims = self._pedb.modeler.primitives_by_layer.get("Outline", [])
            if prims:
                for prim in prims:
                    if prim.is_void:
                        continue
                    xt, yt = prim.points()
                    p1 = [(i, j) for i, j in zip(xt[::-1], yt[::-1])]
                    p1 = mirror_poly(p1)
                    poly = LinearRing(p1)
                    plot_line(poly, add_points=False, color=(0.7, 0, 0), linewidth=4)
            else:
                bbox = self._pedb.hfss.get_layout_bounding_box()
                if not bbox:
                    return False, False
                x1 = bbox[0]
                x2 = bbox[2]
                y1 = bbox[1]
                y2 = bbox[3]
                p = [(x1, y1), (x1, y2), (x2, y2), (x2, y1), (x1, y1)]
                p = mirror_poly(p)
                poly = LinearRing(p)
                plot_line(poly, add_points=False, color=(0.7, 0, 0), linewidth=4)
        layer_colors = {i: k.color for i, k in self._pedb.stackup.layers.items()}
        top_layer = list(self._pedb.stackup.signal_layers.keys())[0]
        bottom_layer = list(self._pedb.stackup.signal_layers.keys())[-1]
        lines = []
        top_comps = []
        bottom_comps = []
        if plot_components:
            nc = 0

            for comp in self._pedb.components.instances.values():
                if not comp.is_enabled:
                    continue
                net_names = comp.nets
                if nets and not any([i in nets for i in net_names]):
                    continue
                layer_name = comp.placement_layer
                if layer_name not in layers:
                    continue
                if plot_components and top_view and layer_name == top_layer:
                    component_color = (0 / 255, 0 / 255, 0 / 255)  # this is the color used in AEDT
                    label = "Component on top layer"
                    label_colors[label] = component_color
                elif plot_components and not top_view and layer_name == bottom_layer:
                    component_color = (41 / 255, 41 / 255, 41 / 255)  # 41, 171, 135
                    label = "Component on bottom layer"
                    label_colors[label] = component_color
                else:
                    continue
                for pinst in comp.pins.values():
                    pdef = pinst.definition
                    p_b_l = {i: j for i, j in pdef.pad_by_layer.items()}
                    pinst_net_name = pinst.net_name
                    if top_view and top_layer in p_b_l and pinst_net_name in nets:
                        try:
                            shape = p_b_l[top_layer].shape
                            if shape.lower() == "circle":
                                poly = Point(pinst.position)
                                top_comps.append(poly.buffer(p_b_l[top_layer].parameters_values[0] / 2))
                            elif shape.lower() == "rectangle":
                                px, py = pinst.position
                                w, h = p_b_l[top_layer].parameters_values
                                poly = [
                                    [px - w / 2, py - h / 2],
                                    [px - w / 2, py + h / 2],
                                    [px + w / 2, py + h / 2],
                                    [px + w / 2, py - h / 2],
                                ]
                                poly = Polygon(poly)
                                top_comps.append(
                                    affinity.rotate(
                                        poly,
                                        (float(p_b_l[top_layer].rotation) + pinst.rotation + comp.rotation)
                                        / math.pi
                                        * 180,
                                    )
                                )
                        except KeyError:
                            pass
                    elif not top_view and bottom_layer in p_b_l and pinst.net_name in nets:
                        try:
                            shape = p_b_l[bottom_layer].shape
                            if shape == "Circle":
                                x, y = pinst.position
                                poly = Point(-x, y)
                                bottom_comps.append(poly.buffer(p_b_l[bottom_layer].parameters_values[0] / 2))
                            elif shape == "Rectangle":
                                px, py = pinst.position
                                w, h = p_b_l[bottom_layer].parameters_values
                                poly = [
                                    [px - w / 2, py - h / 2],
                                    [px - w / 2, py + h / 2],
                                    [px + w / 2, py + h / 2],
                                    [px + w / 2, py - h / 2],
                                ]
                                poly = Polygon(mirror_poly(poly))
                                bottom_comps.append(
                                    affinity.rotate(
                                        poly,
                                        -(float(p_b_l[bottom_layer].rotation) + pinst.rotation + comp.rotation)
                                        / math.pi
                                        * 180,
                                    )
                                )
                        except KeyError:
                            pass
                cbb = comp.bounding_box
                x = [cbb[0], cbb[0], cbb[2], cbb[2]]
                y = [cbb[1], cbb[3], cbb[3], cbb[1]]
                vertices = [(i, j) for i, j in zip(x, y)]
                vertices = mirror_poly(vertices)
                poly = Polygon(vertices)
                lines.append(poly.boundary)
                if annotate_component_names:
                    font_size = 6 if poly.area < 6e-6 else 10
                    ax.annotate(
                        comp.name,
                        (poly.centroid.x, poly.centroid.y),
                        va="center",
                        ha="center",
                        color=component_color,
                        size=font_size,
                        rotation=comp.rotation * 180 / math.pi,
                    )
            self._logger.debug("Plotted {} component(s)".format(nc))

        if top_comps:
            ob = MultiPolygon(top_comps)
            plot_polygon(ob, add_points=False, ax=ax)
        if bottom_comps:
            ob = MultiPolygon(bottom_comps)
            plot_polygon(ob, add_points=False, ax=ax)

        if lines:
            ob = MultiLineString(lines)
            plot_line(ob, ax=ax, add_points=False, color=(1, 0, 0), linewidth=1)

        def create_poly(prim, polys, lines):
            if prim.is_void:
                return
            net_name = prim.net_name
            layer_name = prim.layer_name
            if nets and (net_name not in nets or layer_name not in layers):
                return
            # if prim.primitive_type == "path":
            #     line = prim.center_line
            #     line = mirror_poly(line)
            #     poly = LineString(line).buffer(prim.width / 2)
            # else:
            xt, yt = prim.points()
            if len(xt) < 3:
                return
            p1 = [(i, j) for i, j in zip(xt[::-1], yt[::-1])]
            p1 = mirror_poly(p1)

            holes = []
            for void in prim.voids:
                xvt, yvt = void.points(arc_segments=3)
                if len(xvt) < 3:
                    continue
                h1 = mirror_poly([(i, j) for i, j in zip(xvt, yvt)])
                holes.append(h1)
            if len(holes) > 1:
                holes = shapely.union_all([Polygon(i) for i in holes])
                if isinstance(holes, MultiPolygon):
                    holes = [i.boundary for i in list(holes.geoms)]
                else:
                    holes = [holes.boundary]
            poly = Polygon(p1, holes)
            if layer_name == "Outline":
                if label_colors[label] in lines:
                    lines.append(poly.boundary)
            elif poly:
                polys.append(poly)
            return

        if color_by_net:
            for net in nets:
                prims = self._pedb.nets.nets[net].primitives
                polys = []
                lines = []
                if net not in nets:
                    continue
                label = "Net " + net
                label_colors[label] = list(CSS4_COLORS.keys())[color_index]
                try:
                    edge_colors[label] = [i * 0.5 for i in label_colors[label]]
                except TypeError:
                    edge_colors[label] = label_colors[label]
                color_index += 1
                if color_index >= len(CSS4_COLORS):
                    color_index = 0
                for prim in prims:
                    create_poly(prim, polys, lines)
                if polys:
                    ob = MultiPolygon(polys)
                    plot_polygon(
                        ob,
                        ax=ax,
                        color=label_colors[label],
                        add_points=False,
                        alpha=0.7,
                        label=label,
                        edgecolor="none" if not plot_edges else edge_colors[label],
                    )
                if lines:
                    ob = MultiLineString(p)
                    plot_line(ob, ax=ax, add_points=False, color=label_colors[label], linewidth=1, label=label)
        else:
            prims_by_layers_dict = {i: j for i, j in self._pedb.modeler.primitives_by_layer.items()}
            if not top_view:
                prims_by_layers_dict = {
                    i: prims_by_layers_dict[i] for i in reversed(self._pedb.modeler.primitives_by_layer.keys())
                }
            num_layers = len(layers)
            delta_alpha = 0.7 / num_layers
            alpha = 0.3
            for layer, prims in prims_by_layers_dict.items():
                polys = []
                lines = []
                if layer not in layers:
                    continue
                label = "Layer " + layer
                if label not in label_colors:
                    try:
                        color = layer_colors[layer]
                        c = (
                            float(color[0] / 255),
                            float(color[1] / 255),
                            float(color[2] / 255),
                        )
                    except:
                        c = list(CSS4_COLORS.keys())[color_index]
                        color_index += 1
                        if color_index >= len(CSS4_COLORS):
                            color_index = 0
                    label_colors[label] = c
                    try:
                        edge_colors[label] = [i * 0.5 for i in c]
                    except TypeError:
                        edge_colors[label] = label_colors[label]
                for prim in prims:
                    create_poly(prim, polys, lines)
                if polys:
                    ob = MultiPolygon(polys)
                    plot_polygon(
                        ob,
                        ax=ax,
                        color=label_colors[label],
                        add_points=False,
                        alpha=alpha,
                        label=label,
                        edgecolor="none" if not plot_edges else edge_colors[label],
                    )
                if lines:
                    ob = MultiLineString(p)
                    plot_line(ob, ax=ax, add_points=False, color=label_colors[label], linewidth=1, label=label)
                alpha = alpha + delta_alpha

        if plot_vias:
            polys = []

            for pinst in self._pedb.padstacks.instances.values():
                if pinst.is_pin:
                    continue
                pdef = pinst.definition
                p_b_l = {i: j for i, j in pdef.pad_by_layer.items()}
                pinst_net_name = pinst.net_name
                if top_view and pinst_net_name in nets:
                    for k in range(len(layers)):
                        if layers[k] in p_b_l.keys():
                            pad_value = p_b_l[layers[k]]
                            break
                elif not top_view and pinst_net_name in nets:
                    rev_layers = list(reversed(layers))
                    for k in range(len(rev_layers)):
                        if rev_layers[k] in p_b_l.keys():
                            pad_value = p_b_l[rev_layers[k]]
                            break
                else:
                    continue
                try:
                    shape = pad_value.shape
                    if shape.lower() == "circle":
                        x, y = pinst.position
                        if top_view:
                            poly = Point(pinst.position)
                        else:
                            poly = Point(-x, y)
                        polys.append(poly.buffer(p_b_l[top_layer].parameters_values[0] / 2))
                    elif shape.lower() == "rectangle":
                        px, py = pinst.position
                        w, h = pad_value.parameters_values
                        poly = [
                            [px - w / 2, py - h / 2],
                            [px - w / 2, py + h / 2],
                            [px + w / 2, py + h / 2],
                            [px + w / 2, py - h / 2],
                        ]
                        poly = Polygon(mirror_poly(poly))
                        polys.append(
                            affinity.rotate(
                                poly, (float(pad_value.rotation) + pinst.rotation + comp.rotation) / math.pi * 180
                            )
                        )
                except KeyError:
                    pass
            if polys:
                ob = MultiPolygon(polys)
                plot_polygon(ob, add_points=False, ax=ax, edgecolor="none")
        # Hide grid lines
        ax.grid(False)
        ax.set_axis_off()
        # Hide axes ticks
        ax.set_xticks([])
        ax.set_yticks([])
        message = "Edb Top View" if top_view else "Edb Bottom View"
        plt.title(message, size=20)
        if show_legend:
            plt.legend(loc="upper left", fontsize="x-large")
        end_time = time.time() - start_time
        self._logger.info(f"Plot Generation time {round(end_time, 3)}")
        if save_plot:
            plt.savefig(save_plot)
        if show:  # pragma: no cover
            if is_notebook():
                pass
            elif is_ipython() or "PYTEST_CURRENT_TEST" in os.environ:
                fig.show()
            else:
                plt.show()
        return fig, ax
