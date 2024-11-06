# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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

from __future__ import absolute_import  # noreorder

import math
import os
import time
import warnings

from pyedb.generic.constants import CSS4_COLORS
from pyedb.generic.general_methods import generate_unique_name
from pyedb.grpc.edb_core.nets.net import Net
from pyedb.grpc.edb_core.primitive.bondwire import Bondwire
from pyedb.grpc.edb_core.primitive.path import Path
from pyedb.grpc.edb_core.primitive.polygon import Polygon
from pyedb.misc.utilities import compute_arc_points
from pyedb.modeler.geometry_operators import GeometryOperators


class Nets(object):
    """Manages EDB methods for nets management accessible from `Edb.nets` property.

    Examples
    --------
    >>> from pyedb import Edb
    >>> edbapp = Edb("myaedbfolder", edbversion="2021.2")
    >>> edb_nets = edbapp.nets
    """

    def __getitem__(self, name):
        """Get  a net from the Edb project.

        Parameters
        ----------
        name : str, int

        Returns
        -------
        :class:` :class:`pyedb.dotnet.edb_core.edb_data.nets_data.EDBNetsData`

        """
        return self._pedb.layout.find_net_by_name(name)

    def __contains__(self, name):
        """Determine if a net is named ``name`` or not.

        Parameters
        ----------
        name : str

        Returns
        -------
        bool
            ``True`` when one of the net is named ``name``, ``False`` otherwise.

        """
        return name in self.nets

    def __init__(self, p_edb):
        self._pedb = p_edb
        self._nets_by_comp_dict = {}
        self._comps_by_nets_dict = {}

    @property
    def _edb(self):
        """ """
        return self._pedb

    @property
    def _active_layout(self):
        """ """
        return self._pedb.active_layout

    @property
    def _layout(self):
        """ """
        return self._pedb.layout

    @property
    def _cell(self):
        """ """
        return self._pedb.cell

    @property
    def db(self):
        """Db object."""
        return self._pedb.active_db

    @property
    def _logger(self):
        """Edb logger."""
        return self._pedb.logger

    @property
    def nets(self):
        """Nets.

        Returns
        -------
        dict[str, :class:`pyedb.dotnet.edb_core.edb_data.nets_data.EDBNetsData`]
            Dictionary of nets.
        """
        return {i.name: i for i in self._pedb.layout.nets}

    @property
    def netlist(self):
        """Return the cell netlist.

        Returns
        -------
        list
            Net names.
        """
        return list(self.nets.keys())

    @property
    def signal(self):
        """Signal nets.

        Returns
        -------
        dict[str, :class:`pyedb.dotnet.edb_core.edb_data.EDBNetsData`]
            Dictionary of signal nets.
        """
        nets = {}
        for net, value in self.nets.items():
            if not value.is_power_ground:
                nets[net] = value
        return nets

    @property
    def power(self):
        """Power nets.

        Returns
        -------
        dict[str, :class:`pyedb.dotnet.edb_core.edb_data.EDBNetsData`]
            Dictionary of power nets.
        """
        nets = {}
        for net, value in self.nets.items():
            if value.is_power_ground:
                nets[net] = value
        return nets

    def eligible_power_nets(self, threshold=0.3):
        """Return a list of nets calculated by area to be eligible for PWR/Ground net classification.
            It uses the same algorithm implemented in SIwave.

        Parameters
        ----------
        threshold : float, optional
           Area ratio used by the ``get_power_ground_nets`` method.

        Returns
        -------
        list of  :class:`pyedb.dotnet.edb_core.edb_data.EDBNetsData`
        """
        pwr_gnd_nets = []
        for net in self._layout.nets[:]:
            total_plane_area = 0.0
            total_trace_area = 0.0
            for primitive in net.primitives:
                primitive = primitive
                if isinstance(primitive, Bondwire):
                    continue
                if isinstance(primitive, Path) or isinstance(primitive, Polygon):
                    total_plane_area += primitive.polygon_data.area()
            if total_plane_area == 0.0:
                continue
            if total_trace_area == 0.0:
                pwr_gnd_nets.append(Net(self._pedb, net))
                continue
            if total_plane_area > 0.0 and total_trace_area > 0.0:
                if total_plane_area / (total_plane_area + total_trace_area) > threshold:
                    pwr_gnd_nets.append(Net(self._pedb, net))
        return pwr_gnd_nets

    @property
    def nets_by_components(self):
        # type: () -> dict
        """Get all nets for each component instance."""
        for comp, i in self._pedb.components.instances.items():
            self._nets_by_comp_dict[comp] = i.nets
        return self._nets_by_comp_dict

    @property
    def components_by_nets(self):
        # type: () -> dict
        """Get all component instances grouped by nets."""
        for comp, i in self._pedb.components.instances.items():
            for n in i.nets:
                if n in self._comps_by_nets_dict:
                    self._comps_by_nets_dict[n].append(comp)
                else:
                    self._comps_by_nets_dict[n] = [comp]
        return self._comps_by_nets_dict

    def generate_extended_nets(
        self,
        resistor_below=10,
        inductor_below=1,
        capacitor_above=1,
        exception_list=None,
        include_signal=True,
        include_power=True,
    ):
        # type: (int | float, int | float, int |float, list, bool, bool) -> list
        """Get extended net and associated components.

        . deprecated:: pyedb 0.30.0
        Use :func:`pyedb.grpc.extended_nets.generate_extended_nets` instead.

        Parameters
        ----------
        resistor_below : int, float, optional
            Threshold of resistor value. Search extended net across resistors which has value lower than the threshold.
        inductor_below : int, float, optional
            Threshold of inductor value. Search extended net across inductances which has value lower than the
            threshold.
        capacitor_above : int, float, optional
            Threshold of capacitor value. Search extended net across capacitors which has value higher than the
            threshold.
        exception_list : list, optional
            List of components to bypass when performing threshold checks. Components
            in the list are considered as serial components. The default is ``None``.
        include_signal : str, optional
            Whether to generate extended signal nets. The default is ``True``.
        include_power : str, optional
            Whether to generate extended power nets. The default is ``True``.

        Returns
        -------
        list
            List of all extended nets.

        Examples
        --------
        >>> from pyedb import Edb
        >>> app = Edb()
        >>> app.nets.get_extended_nets()
        """
        warnings.warn("Use new method :func:`edb.extended_nets.generate_extended_nets` instead.", DeprecationWarning)
        self._pedb.extended_nets.generate_extended_nets(
            resistor_below, inductor_below, capacitor_above, exception_list, include_signal, include_power
        )

    @staticmethod
    def _get_points_for_plot(self, my_net_points):
        """
        Get the points to be plotted.
        """
        # fmt: off
        x = []
        y = []
        for i, point in enumerate(my_net_points):
            if not point.is_arc:
                x.append(point.x.value)
                y.append(point.y.value)
            else:
                arc_h = point.arc_height.value
                p1 = [my_net_points[i - 1].x.value, my_net_points[i - 1].y.value]
                if i + 1 < len(my_net_points):
                    p2 = [my_net_points[i + 1].X.ToDouble(), my_net_points[i + 1].Y.ToDouble()]
                else:
                    p2 = [my_net_points[0].X.ToDouble(), my_net_points[0].Y.ToDouble()]
                x_arc, y_arc = compute_arc_points(p1, p2, arc_h)
                x.extend(x_arc)
                y.extend(y_arc)
                # i += 1
        # fmt: on
        return x, y

    def get_plot_data(
        self,
        nets=None,
        layers=None,
        color_by_net=False,
        outline=None,
        plot_components_on_top=False,
        plot_components_on_bottom=False,
    ):
        """Return List of points for Matplotlib 2D Chart.

        Parameters
        ----------
        nets : str, list, optional
            Name of the net or list of nets to plot. If `None` (default value) all nets will be plotted.
        layers : str, list, optional
            Name of the layers to include in the plot. If `None` all the signal layers will be considered.
        color_by_net : bool, optional
            If ``True``  the plot will be colored by net.
            If ``False`` the plot will be colored by layer. (default)
        outline : list, optional
            List of points of the outline to plot.
        plot_components_on_top : bool, optional
            If ``True``  the components placed on top layer are plotted.
            If ``False`` the components are not plotted. (default)
            If nets and/or layers is specified, only the components belonging to the specified nets/layers are plotted.
        plot_components_on_bottom : bool, optional
            If ``True``  the components placed on bottom layer are plotted.
            If ``False`` the components are not plotted. (default)
            If nets and/or layers is specified, only the components belonging to the specified nets/layers are plotted.

        Returns
        -------
        List, str: list of data to be used in plot.
            In case of remote session it will be returned a string that could be converted \
            to list using ast.literal_eval().
        """
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
        objects_lists = []
        label_colors = {}
        n_label = 0
        max_labels = 10

        if outline:
            xt = [i[0] for i in outline]
            yt = [i[1] for i in outline]
            xc, yc = GeometryOperators.orient_polygon(xt, yt, clockwise=True)
            vertices = [(i, j) for i, j in zip(xc, yc)]
            codes = [2 for _ in vertices]
            codes[0] = 1
            vertices.append((0, 0))
            codes.append(79)
            objects_lists.append([vertices, codes, "b", "Outline", 1.0, 1.5, "contour"])
            n_label += 1
        top_layer = list(self._pedb.stackup.signal_layers.keys())[0]
        bottom_layer = list(self._pedb.stackup.signal_layers.keys())[-1]
        if plot_components_on_top or plot_components_on_bottom:
            nc = 0
            for comp in self._pedb.components.instances.values():
                if not comp.enabled:
                    continue
                net_names = comp.nets
                if nets and not any([i in nets for i in net_names]):
                    continue
                layer_name = comp.placement_layer
                if layer_name not in layers:
                    continue
                if plot_components_on_top and layer_name == top_layer:
                    component_color = (184 / 255, 115 / 255, 51 / 255)  # this is the color used in AEDT
                    label = "Component on top layer"
                elif plot_components_on_bottom and layer_name == bottom_layer:
                    component_color = (41 / 255, 171 / 255, 135 / 255)  # 41, 171, 135
                    label = "Component on bottom layer"
                else:
                    continue
                cbb = comp.bounding_box
                x = [cbb[0], cbb[0], cbb[2], cbb[2]]
                y = [cbb[1], cbb[3], cbb[3], cbb[1]]
                vertices = [(i, j) for i, j in zip(x, y)]
                codes = [2 for _ in vertices]
                codes[0] = 1
                vertices.append((0, 0))
                codes.append(79)
                if label not in label_colors:
                    label_colors[label] = component_color
                    objects_lists.append([vertices, codes, label_colors[label], label, 1.0, 2.0, "contour"])
                    n_label += 1
                else:
                    objects_lists.append([vertices, codes, label_colors[label], None, 1.0, 2.0, "contour"])
                nc += 1
            self._logger.debug(f"Plotted {nc} component(s)")

        for path in self._pedb.modeler.paths:
            if path.is_void:
                continue
            net_name = path.net.name
            layer_name = path.layer.name
            if nets and (net_name not in nets or layer_name not in layers):
                continue
            try:
                x, y = path.points()
            except ValueError:
                x = None
            if not x:
                continue
            create_label = False
            if not color_by_net:
                label = "Layer " + layer_name
                if label not in label_colors:
                    try:
                        color = path.layer.color
                        c = (
                            float(color.Item1 / 255),
                            float(color.Item2 / 255),
                            float(color.Item3 / 255),
                        )
                    except:
                        c = list(CSS4_COLORS.keys())[color_index]
                        color_index += 1
                        if color_index >= len(CSS4_COLORS):
                            color_index = 0
                    label_colors[label] = c
                    create_label = True
            else:
                label = "Net " + net_name
                if label not in label_colors:
                    label_colors[label] = list(CSS4_COLORS.keys())[color_index]
                    color_index += 1
                    if color_index >= len(CSS4_COLORS):
                        color_index = 0
                    create_label = True

            if create_label and n_label <= max_labels:
                objects_lists.append([x, y, label_colors[label], label, 0.4, "fill"])
                n_label += 1
            else:
                objects_lists.append([x, y, label_colors[label], None, 0.4, "fill"])

        for poly in self._pedb.modeler.polygons:
            if poly.is_void:
                continue
            net_name = poly.net_name
            layer_name = poly.layer_name
            if nets and (net_name != "" and net_name not in nets or layer_name not in layers):
                continue
            xt, yt = poly.points()
            if not xt:
                continue
            x, y = GeometryOperators.orient_polygon(xt, yt, clockwise=True)
            vertices = [(i, j) for i, j in zip(x, y)]
            codes = [2 for _ in vertices]
            codes[0] = 1
            vertices.append((0, 0))
            codes.append(79)

            for void in poly.voids:
                xvt, yvt = void.points()
                if xvt:
                    xv, yv = GeometryOperators.orient_polygon(xvt, yvt, clockwise=False)
                    tmpV = [(i, j) for i, j in zip(xv, yv)]
                    vertices.extend(tmpV)
                    tmpC = [2 for _ in tmpV]
                    tmpC[0] = 1
                    codes.extend(tmpC)
                    vertices.append((0, 0))
                    codes.append(79)

            create_label = False
            if not color_by_net:
                label = "Layer " + layer_name
                if label not in label_colors:
                    try:
                        color = poly.layer.color
                        c = (
                            float(color.Item1 / 255),
                            float(color.Item2 / 255),
                            float(color.Item3 / 255),
                        )
                    except:
                        c = list(CSS4_COLORS.keys())[color_index]
                        color_index += 1
                        if color_index >= len(CSS4_COLORS):
                            color_index = 0
                    label_colors[label] = c
                    create_label = True
            else:
                label = "Net " + net_name
                if label not in label_colors:
                    label_colors[label] = list(CSS4_COLORS.keys())[color_index]
                    color_index += 1
                    if color_index >= len(CSS4_COLORS):
                        color_index = 0
                    create_label = True

            if create_label and n_label <= max_labels:
                if layer_name == "Outline":
                    objects_lists.append([vertices, codes, label_colors[label], label, 1.0, 2.0, "contour"])
                else:
                    objects_lists.append([vertices, codes, label_colors[label], label, 0.4, "path"])
                n_label += 1
            else:
                if layer_name == "Outline":
                    objects_lists.append([vertices, codes, label_colors[label], None, 1.0, 2.0, "contour"])
                else:
                    objects_lists.append([vertices, codes, label_colors[label], None, 0.4, "path"])

        for circle in self._pedb.modeler.circles:
            if circle.is_void:
                continue
            net_name = circle.net.name
            layer_name = circle.layer.name
            if nets and (net_name not in nets or layer_name not in layers):
                continue
            x, y = circle.points
            if not x:
                continue
            create_label = False
            if not color_by_net:
                label = "Layer " + layer_name
                if label not in label_colors:
                    try:
                        color = circle.layer.color
                        c = (
                            float(color.Item1 / 255),
                            float(color.Item2 / 255),
                            float(color.Item3 / 255),
                        )
                    except:
                        c = list(CSS4_COLORS.keys())[color_index]
                        color_index += 1
                        if color_index >= len(CSS4_COLORS):
                            color_index = 0
                    label_colors[label] = c
                    create_label = True
            else:
                label = "Net " + net_name
                if label not in label_colors:
                    label_colors[label] = list(CSS4_COLORS.keys())[color_index]
                    color_index += 1
                    if color_index >= len(CSS4_COLORS):
                        color_index = 0
                    create_label = True

            if create_label and n_label <= max_labels:
                objects_lists.append([x, y, label_colors[label], label, 0.4, "fill"])
                n_label += 1
            else:
                objects_lists.append([x, y, label_colors[label], None, 0.4, "fill"])

        for rect in self._pedb.modeler.rectangles:
            if rect.is_void:
                continue
            net_name = rect.net_name
            layer_name = rect.layer_name
            if nets and (net_name not in nets or layer_name not in layers):
                continue
            x, y = rect.points
            if not x:
                continue
            create_label = False
            if not color_by_net:
                label = "Layer " + layer_name
                if label not in label_colors:
                    try:
                        color = rect.layer.color
                        c = (
                            float(color.Item1 / 255),
                            float(color.Item2 / 255),
                            float(color.Item3 / 255),
                        )
                    except:
                        c = list(CSS4_COLORS.keys())[color_index]
                        color_index += 1
                        if color_index >= len(CSS4_COLORS):
                            color_index = 0
                    label_colors[label] = c
                    create_label = True
            else:
                label = "Net " + net_name
                if label not in label_colors:
                    label_colors[label] = list(CSS4_COLORS.keys())[color_index]
                    color_index += 1
                    if color_index >= len(CSS4_COLORS):
                        color_index = 0
                    create_label = True

            if create_label and n_label <= max_labels:
                objects_lists.append([x, y, label_colors[label], label, 0.4, "fill"])
                n_label += 1
            else:
                objects_lists.append([x, y, label_colors[label], None, 0.4, "fill"])

        end_time = time.time() - start_time
        self._logger.info("Nets Point Generation time %s seconds", round(end_time, 3))
        if os.getenv("PYAEDT_SERVER_AEDT_PATH", None):
            return str(objects_lists)
        else:
            return objects_lists

    def classify_nets(self, power_nets=None, signal_nets=None):
        """Reassign power/ground or signal nets based on list of nets.

        Parameters
        ----------
        power_nets : str, list, optional
            List of power nets to assign. Default is `None`.
        signal_nets : str, list, optional
            List of signal nets to assign. Default is `None`.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if isinstance(power_nets, str):
            power_nets = []
        elif not power_nets:
            power_nets = []
        if isinstance(signal_nets, str):
            signal_nets = []
        elif not signal_nets:
            signal_nets = []
        for net in power_nets:
            if net in self.nets:
                self.nets[net].is_power_ground = True
        for net in signal_nets:
            if net in self.nets:
                self.nets[net].is_power_ground = False
        return True

    def plot_shapely(
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
            List of points of the outline to plot.
        size : tuple, int, optional
            Image size in pixel (width, height). Default value is ``(6000, 3000)``
        plot_components : bool, optional
            If ``True``  the components placed on top layer are plotted.
            If ``False`` the components are not plotted. (default)
            If nets and/or layers is specified, only the components belonging to the specified nets/layers are plotted.

        show : bool, optional
            Whether to show the plot or not. Default is `True`.
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
            LineString,
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
        layers_elevation = {}
        for k in layers:
            layers_elevation[k] = self._pedb.stackup.signal_layers[k].lower_elevation
        color_index = 0
        label_colors = {}
        if outline:
            poly = Polygon(outline)
            plot_polygon(poly.boundary, add_points=False, color=(1, 0, 0))
        # else:
        #     stats = self._pedb.get_statistics()
        #     bbox = stats.layout.size
        #     bbox = self._pedb.edbutils.HfssUtilities.GetBBox(self._pedb.active_layout)
        #     x1 = bbox.Item1.X.ToDouble()
        #     x2 = bbox.Item2.X.ToDouble()
        #     y1 = bbox.Item1.Y.ToDouble()
        #     y2 = bbox.Item2.Y.ToDouble()
        #     p = [(x1, y1), (x1, y2), (x2, y2), (x2, y1), (x1, y1)]
        #     p = mirror_poly(p)
        #     poly = LinearRing(p)
        #     plot_line(poly, add_points=False, color=(0.7, 0, 0), linewidth=4)
        layer_colors = {i: k.color for i, k in self._pedb.stackup.layers.items()}
        top_layer = list(self._pedb.stackup.signal_layers.keys())[0]
        bottom_layer = list(self._pedb.stackup.signal_layers.keys())[-1]
        lines = []
        top_comps = []
        bottom_comps = []
        defs_copy = {}
        if plot_components:
            nc = 0
            defs_copy = {i: j for i, j in self._pedb.padstacks.definitions.items()}

            for comp in self._pedb.components.instances.values():
                if not comp.enabled:
                    continue
                net_names = comp.nets
                if nets and not any([i in nets for i in net_names]):
                    continue
                layer_name = comp.placement_layer.name
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
                    pdef = defs_copy[pinst.padstack_def.name]
                    p_b_l = {i: j for i, j in pdef.pad_by_layer.items()}
                    pinst_net_name = pinst.net_name
                    if top_view and top_layer in p_b_l and pinst_net_name in nets:
                        try:
                            # shape = p_b_l[top_layer].shape
                            # if shape == "Circle":
                            if "CIRCLE" in p_b_l[top_layer][0].name:
                                poly = Point(pinst.position)
                                top_comps.append(poly.buffer(p_b_l[top_layer][0][1].value / 2))
                            elif "RECTANGLE" in p_b_l[top_layer][0].name:
                                px, py = pinst.position
                                w, h = [val.value for val in p_b_l[top_layer][1]]
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
                                        (float(p_b_l[top_layer][4].value) + pinst.rotation + comp.rotation)
                                        / math.pi
                                        * 180,
                                    )
                                )
                        except KeyError:
                            pass
                    elif not top_view and bottom_layer in p_b_l and pinst.net_name in nets:
                        try:
                            # shape = p_b_l[bottom_layer].shape
                            # if shape == "Circle":
                            if "CIRCLE" in p_b_l[bottom_layer][0].name:
                                x, y = pinst.position
                                poly = Point(-x, y)
                                bottom_comps.append(poly.buffer(p_b_l[bottom_layer][1][0].value / 2))
                            elif "RECTANGLE" in p_b_l[bottom_layer][0].name:
                                px, py = pinst.position
                                w, h = [val.value for val in p_b_l[bottom_layer][1]]
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
                                        -(float(p_b_l[bottom_layer][4].value) + pinst.rotation + comp.rotation)
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
            if prim.primitive_type == "path":
                line = prim.center_line
                line = mirror_poly(line)
                poly = LineString(line).buffer(prim.width / 2)
            else:
                xt, yt = prim.points()
                p1 = [(i, j) for i, j in zip(xt[::-1], yt[::-1])]
                p1 = mirror_poly(p1)

                holes = []
                for void in prim.voids:
                    xvt, yvt = void.points()
                    h1 = mirror_poly([(i, j) for i, j in zip(xvt, yvt)])
                    holes.append(h1)
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
                color_index += 1
                if color_index >= len(CSS4_COLORS):
                    color_index = 0
                for prim in prims:
                    create_poly(prim, polys, lines)
                if polys:
                    ob = MultiPolygon(polys)
                    plot_polygon(
                        ob, ax=ax, color=label_colors[label], add_points=False, alpha=0.7, label=label, edgecolor="none"
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
                        edgecolor="none",
                    )
                if lines:
                    ob = MultiLineString(p)
                    plot_line(ob, ax=ax, add_points=False, color=label_colors[label], linewidth=1, label=label)
                alpha = alpha + delta_alpha

        if plot_vias:
            polys = []
            if not defs_copy:
                defs_copy = {i: j for i, j in self._pedb.padstacks.definitions.items()}

            for pinst in self._pedb.padstacks.instances.values():
                if pinst.is_pin:
                    continue
                pdef = defs_copy[pinst.padstack_def.name]
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
                    # shape = pad_value.shape
                    if "CIRCLE" in pad_value[0].name:
                        # if shape == "Circle":
                        x, y = pinst.position
                        if top_view:
                            poly = Point(pinst.position)
                        else:
                            poly = Point(-x, y)
                        polys.append(poly.buffer(p_b_l[top_layer][1][0].value / 2))
                    elif "RECTANGLE" in pad_value[0].name:
                        px, py = pinst.position
                        w, h = [val.value for val in pad_value[1]]
                        poly = [
                            [px - w / 2, py - h / 2],
                            [px - w / 2, py + h / 2],
                            [px + w / 2, py + h / 2],
                            [px + w / 2, py - h / 2],
                        ]
                        poly = Polygon(mirror_poly(poly))
                        polys.append(
                            affinity.rotate(
                                poly, (float(pad_value[4].value) + pinst.rotation + comp.rotation) / math.pi * 180
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
        if save_plot:
            plt.savefig(save_plot)
        elif show:
            plt.show()
        end_time = time.time() - start_time
        self._logger.info(f"Plot Generation time {round(end_time, 3)}")

    def plot(
        self,
        nets=None,
        layers=None,
        color_by_net=False,
        show_legend=True,
        save_plot=None,
        outline=None,
        size=(2000, 1000),
        plot_components_on_top=False,
        plot_components_on_bottom=False,
        show=True,
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
            List of points of the outline to plot.
        size : tuple, int, optional
            Image size in pixel (width, height). Default value is ``(2000, 1000)``
        plot_components_on_top : bool, optional
            If ``True``  the components placed on top layer are plotted.
            If ``False`` the components are not plotted. (default)
            If nets and/or layers is specified, only the components belonging to the specified nets/layers are plotted.
        plot_components_on_bottom : bool, optional
            If ``True``  the components placed on bottom layer are plotted.
            If ``False`` the components are not plotted. (default)
            If nets and/or layers is specified, only the components belonging to the specified nets/layers are plotted.
        show : bool, optional
            Whether to show the plot or not. Default is `True`.
        """
        from pyedb.generic.plot import plot_matplotlib

        object_lists = self.get_plot_data(
            nets,
            layers,
            color_by_net,
            outline,
            plot_components_on_top,
            plot_components_on_bottom,
        )

        if isinstance(size, int):  # pragma: no cover
            board_size_x, board_size_y = self._pedb.get_statistics().layout_size
            fig_size_x = size
            fig_size_y = board_size_y * fig_size_x / board_size_x
            size = (fig_size_x, fig_size_y)

        plot_matplotlib(
            plot_data=object_lists,
            size=size,
            show_legend=show_legend,
            xlabel="X (m)",
            ylabel="Y (m)",
            title=self._pedb.active_cell.name,
            save_plot=save_plot,
            axis_equal=True,
            show=show,
        )

    def is_power_gound_net(self, netname_list):
        """Determine if one of the  nets in a list is power or ground.

        Parameters
        ----------
        netname_list : list
            List of net names.

        Returns
        -------
        bool
            ``True`` when one of the net names is ``"power"`` or ``"ground"``, ``False`` otherwise.
        """
        if isinstance(netname_list, str):
            netname_list = [netname_list]
        power_nets_names = list(self.power.keys())
        for netname in netname_list:
            if netname in power_nets_names:
                return True
        return False

    def get_dcconnected_net_list(self, ground_nets=["GND"], res_value=0.001):
        """Get the nets connected to the direct current through inductors.

        .. note::
           Only inductors are considered.

        Parameters
        ----------
        ground_nets : list, optional
            List of ground nets. The default is ``["GND"]``.

        Returns
        -------
        list
            List of nets connected to DC through inductors.
        """
        temp_list = []
        for _, comp_obj in self._pedb.components.inductors.items():
            numpins = comp_obj.numpins

            if numpins == 2:
                nets = comp_obj.nets
                if not set(nets).intersection(set(ground_nets)):
                    temp_list.append(set(nets))
                else:
                    pass
        for _, comp_obj in self._pedb.components.resistors.items():
            numpins = comp_obj.numpins

            if numpins == 2 and self._pedb._decompose_variable_value(comp_obj.res_value) <= res_value:
                nets = comp_obj.nets
                if not set(nets).intersection(set(ground_nets)):
                    temp_list.append(set(nets))
                else:
                    pass
        dcconnected_net_list = []

        while not not temp_list:
            s = temp_list.pop(0)
            interseciton_flag = False
            for i in temp_list:
                if not not s.intersection(i):
                    i.update(s)
                    interseciton_flag = True

            if not interseciton_flag:
                dcconnected_net_list.append(s)

        return dcconnected_net_list

    def get_powertree(self, power_net_name, ground_nets):
        """Retrieve the power tree.

        Parameters
        ----------
        power_net_name : str
            Name of the power net.
        ground_nets :


        Returns
        -------

        """
        flag_in_ng = False
        net_group = []
        for ng in self.get_dcconnected_net_list(ground_nets):
            if power_net_name in ng:
                flag_in_ng = True
                net_group.extend(ng)
                break

        if not flag_in_ng:
            net_group.append(power_net_name)

        component_list = []
        rats = self._pedb.components.get_rats()
        for net in net_group:
            for el in rats:
                if net in el["net_name"]:
                    i = 0
                    for n in el["net_name"]:
                        if n == net:
                            df = [el["refdes"][i], el["pin_name"][i], net]
                            component_list.append(df)
                        i += 1

        component_type = []
        for el in component_list:
            refdes = el[0]
            comp_type = self._pedb.components._cmp[refdes].type
            component_type.append(comp_type)
            el.append(comp_type)

            comp_partname = self._pedb.components._cmp[refdes].partname
            el.append(comp_partname)
            pins = self._pedb.components.get_pin_from_component(component=refdes, net_name=el[2])
            el.append("-".join([i.name for i in pins]))

        component_list_columns = [
            "refdes",
            "pin_name",
            "net_name",
            "component_type",
            "component_partname",
            "pin_list",
        ]
        return component_list, component_list_columns, net_group

    def get_net_by_name(self, net_name):
        """Find a net by name."""
        edb_net = Net.find_by_name(self._active_layout, net_name)
        if edb_net is not None:
            return edb_net

    def delete(self, netlist):
        """Delete one or more nets from EDB.

        Parameters
        ----------
        netlist : str or list
            One or more nets to delete.

        Returns
        -------
        list
            List of nets that were deleted.

        Examples
        --------

        >>> deleted_nets = edb_core.nets.delete(["Net1","Net2"])
        """
        if isinstance(netlist, str):
            netlist = [netlist]

        self._pedb.modeler.delete_primitives(netlist)
        self._pedb.padstacks.delete_padstack_instances(netlist)

        nets_deleted = []

        for i in self._pedb.nets.nets.values():
            if i.name in netlist:
                i.delete()
                nets_deleted.append(i.name)
        return nets_deleted

    def find_or_create_net(self, net_name="", start_with="", contain="", end_with=""):
        """Find or create the net with the given name in the layout.

        Parameters
        ----------
        net_name : str, optional
            Name of the net to find or create. The default is ``""``.

        start_with : str, optional
            All net name starting with the string. Not case-sensitive.

        contain : str, optional
            All net name containing the string. Not case-sensitive.

        end_with : str, optional
            All net name ending with the string. Not case-sensitive.

        Returns
        -------
        object
            Net Object.
        """
        if not net_name and not start_with and not contain and not end_with:
            net_name = generate_unique_name("NET_")
            net = Net.create(self._active_layout, net_name)
            return net
        else:
            if not start_with and not contain and not end_with:
                net = Net.find_by_name(self._active_layout, net_name)
                if net.is_null:
                    net = Net.create(self._active_layout, net_name)
                return net
            elif start_with:
                nets_found = [self.nets[net] for net in list(self.nets.keys()) if net.lower().startswith(start_with)]
                return nets_found
            elif start_with and end_with:
                nets_found = [
                    self.nets[net]
                    for net in list(self.nets.keys())
                    if net.lower().startswith(start_with) and net.lower().endswith(end_with)
                ]
                return nets_found
            elif start_with and contain and end_with:
                nets_found = [
                    self.nets[net].net_object
                    for net in list(self.nets.keys())
                    if net.lower().startswith(start_with) and net.lower().endswith(end_with) and contain in net.lower()
                ]
                return nets_found
            elif start_with and contain:
                nets_found = [
                    self.nets[net]
                    for net in list(self.nets.keys())
                    if net.lower().startswith(start_with) and contain in net.lower()
                ]
                return nets_found
            elif contain and end_with:
                nets_found = [
                    self.nets[net]
                    for net in list(self.nets.keys())
                    if net.lower().endswith(end_with) and contain in net.lower()
                ]
                return nets_found
            elif end_with and not start_with and not contain:
                nets_found = [self.nets[net] for net in list(self.nets.keys()) if net.lower().endswith(end_with)]
                return nets_found
            elif contain and not start_with and not end_with:
                nets_found = [self.nets[net] for net in list(self.nets.keys()) if contain in net.lower()]
                return nets_found

    def is_net_in_component(self, component_name, net_name):
        """Check if a net belongs to a component.

        Parameters
        ----------
        component_name : str
            Name of the component.
        net_name : str
            Name of the net.

        Returns
        -------
        bool
            ``True`` if the net is found in component pins.

        """
        if component_name not in self._pedb.components.instances:
            return False
        for net in self._pedb.components.instances[component_name].nets:
            if net_name == net:
                return True
        return False

    def find_and_fix_disjoint_nets(
        self, net_list=None, keep_only_main_net=False, clean_disjoints_less_than=0.0, order_by_area=False
    ):
        """Find and fix disjoint nets from a given netlist.

        .. deprecated::
           Use new property :func:`edb.layout_validation.disjoint_nets` instead.

        Parameters
        ----------
        net_list : str, list, optional
            List of nets on which check disjoints. If `None` is provided then the algorithm will loop on all nets.
        keep_only_main_net : bool, optional
            Remove all secondary nets other than principal one (the one with more objects in it). Default is `False`.
        clean_disjoints_less_than : bool, optional
            Clean all disjoint nets with area less than specified area in square meters. Default is `0.0` to disable it.
        order_by_area : bool, optional
            Whether if the naming order has to be by number of objects (fastest) or area (slowest but more accurate).
            Default is ``False``.

        Returns
        -------
        List
            New nets created.

        Examples
        --------

        >>> renamed_nets = edb_core.nets.find_and_fix_disjoint_nets(["GND","Net2"])
        """
        warnings.warn("Use new function :func:`edb.layout_validation.disjoint_nets` instead.", DeprecationWarning)
        return self._pedb.layout_validation.disjoint_nets(
            net_list, keep_only_main_net, clean_disjoints_less_than, order_by_area
        )

    def merge_nets_polygons(self, net_names_list):
        """Convert paths from net into polygons, evaluate all connected polygons and perform the merge.

        Parameters
        ----------
        net_names_list : str or list[str]
            Net name of list of net name.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        if isinstance(net_names_list, str):
            net_names_list = [net_names_list]
        return self._pedb.modeler.unite_polygons_on_layer(net_names_list=net_names_list)
