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

from ansys.edb.core.net.net import Net as GrpcNet
from ansys.edb.core.primitive.primitive import PrimitiveType as GrpcPrimitiveType

from pyedb.grpc.database.primitive.bondwire import Bondwire
from pyedb.grpc.database.primitive.circle import Circle
from pyedb.grpc.database.primitive.padstack_instance import PadstackInstance
from pyedb.grpc.database.primitive.path import Path
from pyedb.grpc.database.primitive.polygon import Polygon
from pyedb.grpc.database.primitive.rectangle import Rectangle


class Net(GrpcNet):
    """Manages EDB functionalities for a primitives.
    It Inherits EDB Object properties.

    Examples
    --------
    >>> from pyedb import Edb
    >>> edb = Edb(myedb, edbversion="2021.2")
    >>> edb_net = edb.nets.nets["GND"]
    >>> edb_net.name # Class Property
    >>> edb_net.name # EDB Object Property
    """

    def __init__(self, pedb, raw_net):
        super().__init__(raw_net.msg)
        self._pedb = pedb
        self._core_components = pedb.components
        self._core_primitive = pedb.modeler
        self._edb_object = raw_net

    @property
    def primitives(self):
        """Primitives that belongs to the net.

        Returns
        -------
        List[:class:`Primitive <pyedb.grpc.database.primitive.primitive.Primitive>`].
            List of Primitive object.

        """
        primitives = []
        for primitive in super().primitives:
            if primitive.primitive_type == GrpcPrimitiveType.PATH:
                primitives.append(Path(self._pedb, primitive))
            elif primitive.primitive_type == GrpcPrimitiveType.POLYGON:
                primitives.append(Polygon(self._pedb, primitive))
            elif primitive.primitive_type == GrpcPrimitiveType.CIRCLE:
                primitives.append(Circle(self._pedb, primitive))
            elif primitive.primitive_type == GrpcPrimitiveType.RECTANGLE:
                primitives.append(Rectangle(self._pedb, primitive))
            elif primitive.primitive_type == GrpcPrimitiveType.BONDWIRE:
                primitives.append(Bondwire(self._pedb, primitive))
        return primitives

    @property
    def padstack_instances(self):
        """Padstack instance which belong to net.

        Returns
        -------
        List[:class:`PadstackInstance <pyedb.grpc.database.primitive.padstack_instance.PadstackInstance>`]
            LIst of PadstackInstance object.

        """
        return [PadstackInstance(self._pedb, i) for i in super().padstack_instances]

    @property
    def components(self):
        """Components connected to net.

        Returns
        -------
        Dict[str, :class:`Component <pyedb.grpc.database.hierarchy.component.Component>`]
        """
        components = {}
        for padstack_instance in self.padstack_instances:
            component = padstack_instance.component
            if component:
                try:
                    components[component.name] = component
                except:
                    pass
        return components

    def find_dc_short(self, fix=False):
        """Find DC-shorted nets.

        Parameters
        ----------
        fix : bool, optional
            If `True`, rename all the nets. (default)
            If `False`, only report dc shorts.

        Returns
        -------
        List[List[str, str]]
            [[net name, net name]].
        """
        return self._pedb.layout_validation.dc_shorts(self.name, fix)

    def plot(
        self, layers=None, show_legend=True, save_plot=None, outline=None, size=(2000, 1000), show=True, title=None
    ):
        """Plot a net to Matplotlib 2D chart.

        Parameters
        ----------
        layers : str, list, optional
            Name of the layers to include in the plot. If `None` all the signal layers will be considered.
        show_legend : bool, optional
            If `True` the legend is shown in the plot. (default)
            If `False` the legend is not shown.
        save_plot : str, optional
            If a path is specified the plot will be saved in this location.
            If ``save_plot`` is provided, the ``show`` parameter is ignored.
        outline : list, optional
            List of points of the outline to plot.
        size : tuple, optional
            Image size in pixel (width, height).
        show : bool, optional
            Whether to show the plot or not. Default is ``True``.
        title : str, optional
            Plot title. If value is ``None`` the project name is assigned by default. Default value is ``None``.
        """

        self._pedb.nets.plot(
            self.name,
            layers=layers,
            show_legend=show_legend,
            save_plot=save_plot,
            outline=outline,
            size=size,
            show=show,
            plot_components=True,
            plot_vias=True,
            title=None,
        )

    def get_smallest_trace_width(self):
        """Retrieve the smallest trace width from paths.

        Returns
        -------
        float
            Trace smallest width.
        """

        current_value = 1e10
        paths = [prim for prim in self.primitives if prim.primitive_type == GrpcPrimitiveType.PATH]
        for path in paths:
            if path.width < current_value:
                current_value = path.width
        return current_value

    @property
    def extended_net(self):
        """Get extended net and associated components.

        Returns
        -------
        :class:`ExtendedNet <pyedb.grpc.database.net.extended_net.ExtendedNet>`

        Examples
        --------
        >>> from pyedb import Edb
        >>> app = Edb()
        >>> app.nets["BST_V3P3_S5"].extended_net
        """
        if self.name in self._pedb.extended_nets.items:
            return self._pedb.extended_nets.items[self.name]
        else:
            return None
