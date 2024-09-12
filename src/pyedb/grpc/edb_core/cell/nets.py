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

from ansys.edb.core.net.differential_pair import (
    DifferentialPair as GrpcDifferentialPair,
)
from ansys.edb.core.net.extended_net import ExtendedNet as GrpcExtendedNet
from ansys.edb.core.net.net import Net as GrpcNet
from ansys.edb.core.net.net_class import NetClass as GrpcNetClass
from ansys.edb.core.primitive.primitive import PrimitiveType as GrpcPrimitiveType

from pyedb.grpc.edb_core.cell.primitive.primitive import Primitive

# from pyedb.dotnet.edb_core.dotnet.database import (
#    DifferentialPairDotNet,
#    ExtendedNetDotNet,
#    NetClassDotNet,
#    NetDotNet,
# )


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
        super().__init__(raw_net)
        self._pedb = pedb
        self._core_components = pedb.components
        self._core_primitive = pedb.modeler
        self._edb_object = raw_net

    @property
    def primitives(self):
        """Return the list of primitives that belongs to the net.

        Returns
        -------
        list of :class:`pyedb.dotnet.edb_core.edb_data.primitives_data.EDBPrimitives`
        """
        return [Primitive(self._pedb, prim) for prim in self.primitives]

    @property
    def padstack_instances(self):
        """Return the list of primitives that belongs to the net.

        Returns
        -------
        list of :class:`pyedb.dotnet.edb_core.edb_data.padstacks_data.EDBPadstackInstance`"""
        return [PadstackInstance(i, self._pedb) for i in self.padstack_instances]

    @property
    def components(self):
        """Return the list of components that touch the net.

        Returns
        -------
        dict[str, :class:`pyedb.dotnet.edb_core.cell.hierarchy.component.EDBComponent`]
        """
        return {cmp.name: Component(self._pedb, cmp) for cmp in self.components}

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
        self,
        layers=None,
        show_legend=True,
        save_plot=None,
        outline=None,
        size=(2000, 1000),
        show=True,
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
            Whether to show the plot or not. Default is `True`.
        """

        self._pedb.nets.plot(
            self.name,
            layers=layers,
            show_legend=show_legend,
            save_plot=save_plot,
            outline=outline,
            size=size,
            show=show,
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
            if path.width.value < current_value:
                current_value = path.width
        return current_value

    @property
    def extended_net(self):
        """Get extended net and associated components.

        Returns
        -------
        :class:` :class:`pyedb.dotnet.edb_core.edb_data.nets_data.EDBExtendedNetData`

        Examples
        --------
        >>> from pyedb import Edb
        >>> app = Edb()
        >>> app.nets["BST_V3P3_S5"].extended_net
        """
        return ExtendedNet(self._pedb, self.extended_net)


class NetClass(GrpcNetClass):
    """Manages EDB functionalities for a primitives.
    It inherits EDB Object properties.

    Examples
    --------
    >>> from pyedb import Edb
    >>> edb = Edb(myedb, edbversion="2021.2")
    >>> edb.net_classes
    """

    def __init__(self, core_app, raw_extended_net=None):
        super().__init__(raw_extended_net)
        self._app = core_app
        self._core_components = core_app.components
        self._core_primitive = core_app.modeler
        self._core_nets = core_app.nets


class ExtendedNet(GrpcExtendedNet):
    """Manages EDB functionalities for a primitives.
    It Inherits EDB Object properties.
    """

    def __init__(self, core_app, raw_extended_net=None):
        self._app = core_app
        self._core_components = core_app.components
        self._core_primitive = core_app.modeler
        self._core_nets = core_app.nets
        ExtendedNet.__init__(self, self._app, raw_extended_net)

    @property
    def nets(self):
        """Nets dictionary."""
        return {net.name: Net(self._app, net) for net in self.nets}

    @property
    def components(self):
        """Dictionary of components."""
        comps = {}
        for _, obj in self.nets.items():
            comps.update(obj.components)
        return comps

    @property
    def rlc(self):
        """Dictionary of RLC components."""
        return {
            name: comp for name, comp in self.components.items() if comp.type in ["Inductor", "Resistor", "Capacitor"]
        }

    @property
    def serial_rlc(self):
        """Dictionary of serial RLC components."""
        res = {}
        nets = self.nets
        for comp_name, comp_obj in self.components.items():
            if comp_obj.type not in ["Resistor", "Inductor", "Capacitor"]:
                continue
            if set(comp_obj.nets).issubset(set(nets)):
                res[comp_name] = comp_obj
        return res

    @property
    def shunt_rlc(self):
        """Dictionary of shunt RLC components."""
        res = {}
        nets = self.nets
        for comp_name, comp_obj in self.components.items():
            if comp_obj.type not in ["Resistor", "Inductor", "Capacitor"]:
                continue
            if not set(comp_obj.nets).issubset(set(nets)):
                res[comp_name] = comp_obj
        return res


class DifferentialPair(GrpcDifferentialPair):
    """Manages EDB functionalities for a primitive.
    It inherits EDB object properties.
    """

    def __init__(self, core_app, edb_object=None):
        super().__init__(edb_object)
        self._app = core_app
        self._core_components = core_app.components
        self._core_primitive = core_app.modeler
        self._core_nets = core_app.nets
        DifferentialPair.__init__(self, self._app, edb_object)

    @property
    def positive_net(self):
        """Positive Net."""
        return Net(self._app, self.positive_net)

    @property
    def negative_net(self):
        """Negative Net."""
        return Net(self._app, self.negative_net)
