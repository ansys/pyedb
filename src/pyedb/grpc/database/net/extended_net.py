# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyedb.grpc.database.net.net import Net
from ansys.edb.core.net.extended_net import ExtendedNet as GrpcExtendedNet


class ExtendedNets:
    def __init__(self, pedb):
        self._pedb = pedb

    @property
    def items(self) -> dict[str, any]:
        """Extended nets.

        Returns
        -------
        Dict[str, :class:`ExtendedNet <pyedb.grpc.database.net.extended_net.ExtendedNet>`]
            Dictionary of extended nets.
        """
        nets = {}
        for extended_net in self._pedb.layout.extended_nets:
            nets[extended_net.name] = ExtendedNet(self._pedb, extended_net.core)
        return nets

    def create(self, name, net):
        """Create a new Extended net.

        Parameters
        ----------
        name : str
            Name of the extended net.
        net : str, list
           Name of the nets to be added into this extended net.

        Returns
        -------
        :class:`ExtendedNet <pyedb.grpc.database.net.extended_net.ExtendedNet>`
            Created ExtendedNet object.
        """
        if name in self.items:
            self._pedb.logger.error("{} already exists.".format(name))
            return False
        extended_net = ExtendedNet.create(self._pedb.layout, name)
        if isinstance(net, str):
            net = [net]
        for i in net:
            extended_net.core.add_net(self._pedb.nets.nets[i].core)
        return self.items[name]

    def auto_identify_signal(self, resistor_below=10, inductor_below=1, capacitor_above=1e-9, exception_list=None):
        # type: (int | float, int | float, int |float, list) -> list[ExtendedNet]
        """Get extended signal net and associated components.

        Parameters
        ----------
        resistor_below : int, float, optional
            Threshold for the resistor value. Search the extended net across resistors that
            have a value lower than the threshold.
        inductor_below : int, float, optional
            Threshold for the inductor value. Search the extended net across inductances
            that have a value lower than the threshold.
        capacitor_above : int, float, optional
            Threshold for the capacitor value. Search the extended net across capacitors
            that have a value higher than the threshold.
        exception_list : list, optional
            List of components to bypass when performing threshold checks. Components
            in the list are considered as serial components. The default is ``None``.

        Returns
        -------
        List[:class:`ExtendedNet <pyedb.grpc.database.net.extended_net.ExtendedNet>`]
            List of all extended nets.

        Examples
        --------
        >>> from pyedb import Edb
        >>> app = Edb()
        >>> app.extended_nets.auto_identify_signal()
        """
        return self.generate_extended_nets(resistor_below, inductor_below, capacitor_above, exception_list, True, True)

    def auto_identify_power(self, resistor_below=10, inductor_below=1, capacitor_above=1, exception_list=None):
        # type: (int | float, int | float, int |float, list) -> list
        """Get all extended power nets and their associated components.

        Parameters
        ----------
        resistor_below : int, float, optional
            Threshold for the resistor value. Search the extended net across resistors that
            have a value lower than the threshold.
        inductor_below : int, float, optional
            Threshold for the inductor value. Search the extended net across inductances that
            have a value lower than the threshold.
        capacitor_above : int, float, optional
            Threshold for the capacitor value. Search the extended net across capacitors that
            have a value higher than the threshold.
        exception_list : list, optional
            List of components to bypass when performing threshold checks. Components
            in the list are considered as serial components. The default is ``None``.

        Returns
        -------
        List[:class:`ExtendedNet <pyedb.grpc.database.net.extended_net.ExtendedNet>`]
            List of all extended nets and their associated components.

        Examples
        --------
        >>> from pyedb import Edb
        >>> app = Edb()
        >>> app.extended_nets.auto_identify_power()
        """
        return self.generate_extended_nets(resistor_below, inductor_below, capacitor_above, exception_list, True, True)

    def generate_extended_nets(
        self,
        resistor_below=10,
        inductor_below=1,
        capacitor_above=1,
        exception_list=None,
        include_signal=True,
        include_power=True,
    ):
        # type: (int | float, int | float, int |float, list, bool, bool) -> list[ExtendedNet]
        """Get extended net and associated components.

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
        List[:class:`ExtendedNet <pyedb.grpc.database.net.extended_net.ExtendedNet>`]
            List of all extended nets.

        Examples
        --------
        >>> from pyedb import Edb
        >>> app = Edb()
        >>> app.nets.get_extended_nets()
        """
        if exception_list is None:
            exception_list = []
        _extended_nets = []
        _nets = self._pedb.nets.nets
        all_nets = list(_nets.keys())[:]
        net_dicts = (
            self._pedb.nets._comps_by_nets_dict
            if self._pedb.nets._comps_by_nets_dict
            else (self._pedb.nets.components_by_nets)
        )
        comp_dict = (
            self._pedb.nets._nets_by_comp_dict
            if self._pedb.nets._nets_by_comp_dict
            else (self._pedb.nets.nets_by_components)
        )

        def get_net_list(net_name, _net_list):
            comps = []
            if net_name in net_dicts:
                comps = net_dicts[net_name]

            for vals in comps:
                refdes = vals
                cmp = self._pedb.components.instances[refdes]
                if cmp.type not in ["inductor", "resistor", "capacitor"]:
                    continue
                if not cmp.enabled:
                    continue
                val_value = cmp.rlc_values
                if refdes in exception_list:
                    pass
                elif cmp.type == "inductor":
                    if val_value[1] is None:
                        continue
                    elif not val_value[1] < inductor_below:
                        continue
                elif cmp.type == "resistor":
                    if val_value[0] is None:
                        continue
                    elif not val_value[0] < resistor_below:
                        continue
                elif cmp.type == "capacitor":
                    if val_value[2] is None:
                        continue
                    elif not val_value[2] > capacitor_above:
                        continue
                else:
                    continue
                for net in comp_dict[refdes]:
                    if net not in _net_list:
                        _net_list.append(net)
                        get_net_list(net, _net_list)

        while len(all_nets) > 0:
            new_ext = [all_nets[0]]
            get_net_list(new_ext[0], new_ext)
            all_nets = [i for i in all_nets if i not in new_ext]
            _extended_nets.append(new_ext)

            if len(new_ext) > 1:
                i = new_ext[0]
                for i in new_ext:
                    if not i.lower().startswith("unnamed"):
                        break

                is_power = False
                for i in new_ext:
                    is_power = is_power or _nets[i].is_power_ground

                if is_power:
                    if include_power:
                        ext_net = ExtendedNet.create(self._pedb.layout, i)
                        ext_net.core.add_net(self._pedb.nets.nets[i].core)
                        for net in new_ext:
                            ext_net.core.add_net(self._pedb.nets.nets[net].core)
                    else:  # pragma: no cover
                        pass
                else:
                    if include_signal:
                        ext_net = ExtendedNet.create(self._pedb.layout, i)
                        ext_net.core.add_net(self._pedb.nets.nets[i].core)
                        for net in new_ext:
                            ext_net.core.add_net(self._pedb.nets.nets[net].core)
                    else:  # pragma: no cover
                        pass

        return _extended_nets


class ExtendedNet:
    """Manages EDB functionalities for a primitives.
    It Inherits EDB Object properties.
    """

    def __init__(self, pedb, edb_object):
        self.core = edb_object
        self._pedb = pedb

    @classmethod
    def create(cls, layout, name):
        """Create a extended net.

        Parameters
        ----------
        layout : :class: <``Layout` pyedb.grpc.database.layout.layout.Layout>
            Layout object associated with the extended net.
        name : str
            Name of the extended net.

        Returns
        -------
        ExtendedNet
            Extended net object.
        """
        core_extended_net = GrpcExtendedNet.create(layout.core, name)
        return cls(layout._pedb, core_extended_net)

    @property
    def name(self):
        """Extended net name.

        Returns
        -------
        str
            Extended net name.
        """
        return self.core.name

    @name.setter
    def name(self, value):
        self.core.name = value

    @property
    def nets(self) -> dict[str, Net]:
        """Nets dictionary.

        Returns
        -------
        Dict[str, :class:`Net <pyedb.grpc.database.net.net.Net>`]
            Dict[net name, Net object].
        """
        from pyedb.grpc.database.net.net import Net

        return {net.name: Net(self._pedb, net) for net in self.core.nets}

    @property
    def components(self) -> dict[str, any]:
        """Dictionary of components.

        Returns
        -------
        Dict[str, :class:`Component <pyedb.grpc.database.hierarchy.component.Component>`].
            Dict[net name, Component object].
        """
        comps = {}
        for _, obj in self.nets.items():
            comps.update(obj.components)
        return comps

    @property
    def rlc(self) -> dict[str, any]:
        """Dictionary of RLC components.

        Returns
        -------
        Dict[str, :class:`Component <pyedb.grpc.database.hierarchy.component.Component>`].
            Dict[net name, Component object].
        """
        return {
            name: comp for name, comp in self.components.items() if comp.type in ["inductor", "resistor", "capacitor"]
        }

    @property
    def serial_rlc(self) -> dict[str, any]:
        """Dictionary of serial RLC components.

        Returns
        -------
        Dict[str, :class:`Component <pyedb.grpc.database.hierarchy.component.Component>`].
            Dict[net name, Component object].

        """
        res = {}
        nets = self.nets
        for comp_name, comp_obj in self.components.items():
            if comp_obj.type not in ["resistor", "inductor", "capacitor"]:
                continue
            if set(list(nets.keys())).issubset(comp_obj.nets):
                res[comp_name] = comp_obj
        return res

    @property
    def shunt_rlc(self) -> dict[str, any]:
        """Dictionary of shunt RLC components.

        Returns
        -------
        Dict[str, :class:`Component <pyedb.grpc.database.hierarchy.component.Component>`].
            Dict[net name, Component object].

        """
        res = {}
        nets = self.nets
        for comp_name, comp_obj in self.components.items():
            if comp_obj.type not in ["resistor", "inductor", "capacitor"]:
                continue
            if not set(list(nets.keys())).issubset(comp_obj.nets):
                res[comp_name] = comp_obj
        return res
