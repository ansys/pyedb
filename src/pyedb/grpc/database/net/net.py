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

from typing import Union

from ansys.edb.core.net.net import Net as GrpcNet
from ansys.edb.core.primitive.primitive import PrimitiveType as GrpcPrimitiveType

from pyedb.grpc.database.primitive.bondwire import Bondwire
from pyedb.grpc.database.primitive.circle import Circle
from pyedb.grpc.database.primitive.padstack_instance import PadstackInstance
from pyedb.grpc.database.primitive.path import Path
from pyedb.grpc.database.primitive.polygon import Polygon
from pyedb.grpc.database.primitive.rectangle import Rectangle


class Net(GrpcNet):
    """Manages EDB functionalities for net objects and their primitives.

    Inherits properties from EDB objects and provides additional functionality
    specific to nets.

    Parameters
    ----------
    pedb : :class:`pyedb.Edb`
        Main EDB object.
    raw_net :
        Raw net object from gRPC.

    Examples
    --------
    >>> from pyedb import Edb
    >>> edb = Edb(myedb, edbversion="2021.2")
    >>> edb_net = edb.nets["GND"]
    >>> edb_net.name
    'GND'
    """

    def __init__(self, pedb, raw_net):
        super().__init__(raw_net.msg)
        self._pedb = pedb
        self._core_components = pedb.components
        self._core_primitive = pedb.modeler
        self._edb_object = raw_net

    @property
    def primitives(self) -> list[Union[Path, Polygon, Circle, Rectangle, Bondwire]]:
        """All primitives belonging to this net.

        Returns
        -------
        list
            List of primitive objects which can be one of:
            - :class:`Path <pyedb.grpc.database.primitive.path.Path>`
            - :class:`Polygon <pyedb.grpc.database.primitive.polygon.Polygon>`
            - :class:`Circle <pyedb.grpc.database.primitive.circle.Circle>`
            - :class:`Rectangle <pyedb.grpc.database.primitive.rectangle.Rectangle>`
            - :class:`Bondwire <pyedb.grpc.database.primitive.bondwire.Bondwire>`
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
    def padstack_instances(self) -> list[PadstackInstance]:
        """All padstack instances belonging to this net.

        Returns
        -------
        list of :class:`PadstackInstance <pyedb.grpc.database.primitive.padstack_instance.PadstackInstance>`
            Padstack instances associated with the net.
        """
        return [PadstackInstance(self._pedb, i) for i in super().padstack_instances]

    @property
    def components(self) -> dict[str, any]:
        """Components connected to this net.

        Returns
        -------
        dict
            Dictionary of components keyed by component name, with values as
            :class:`Component <pyedb.grpc.database.hierarchy.component.Component>` objects.
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

    def find_dc_short(self, fix=False) -> list[list[str, str]]:
        """Find DC-shorted nets connected to this net.

        Parameters
        ----------
        fix : bool, optional
            Whether to automatically rename nets to resolve shorts.
            Default: ``False`` (only report shorts).

        Returns
        -------
        list[list[str]]
            List of shorted net pairs in the format [[net_name1, net_name2], ...].
        """
        return self._pedb.layout_validation.dc_shorts(self.name, fix)

    def plot(
        self, layers=None, show_legend=True, save_plot=None, outline=None, size=(2000, 1000), show=True, title=None
    ):
        """Plot the net using Matplotlib.

        Parameters
        ----------
        layers : str or list[str], optional
            Layer name(s) to include. If ``None``, uses all signal layers.
        show_legend : bool, optional
            Enable legend display. Default: ``True``.
        save_plot : str, optional
            Full path to save the plot image. If specified, overrides ``show``.
        outline : list, optional
            Outline points for plot boundary.
        size : tuple, optional
            Image dimensions in pixels (width, height). Default: (2000, 1000).
        show : bool, optional
            Display the plot. Default: ``True``.
        title : str, optional
            Plot title. Uses net name if ``None``. Default: ``None``.
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
            title=title,
        )

    def get_smallest_trace_width(self) -> float:
        """Get the minimum trace width from path primitives in this net.

        Returns
        -------
        float
            Smallest width found in database units. Returns 1e10 if no paths exist.
        """
        current_value = 1e10
        paths = [prim for prim in self.primitives if prim.primitive_type == GrpcPrimitiveType.PATH]
        for path in paths:
            if path.width < current_value:
                current_value = path.width
        return current_value

    @property
    def extended_net(self):
        """Extended net associated with this net.

        Returns
        -------
        :class:`ExtendedNet <pyedb.grpc.database.net.extended_net.ExtendedNet>` or None
            Extended net object if exists, otherwise ``None``.

        Examples
        --------
        >>> edb.nets["BST_V3P3_S5"].extended_net
        """
        if self.name in self._pedb.extended_nets.items:
            return self._pedb.extended_nets.items[self.name]
        else:
            return None
