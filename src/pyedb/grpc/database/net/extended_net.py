# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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
    from pyedb.grpc.database.hierarchy.component import Component
    from pyedb.grpc.database.net.net import Net
from ansys.edb.core.net.extended_net import ExtendedNet as CoreExtendedNet

from pyedb.generic.constants import decompose_variable_value, unit_converter


class ExtendedNets:
    def __init__(self, pedb):
        self._pedb = pedb

    @property
    def items(self) -> dict[str, ExtendedNet]:
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
            self._pedb.logger.error(f"{name} already exists.")
            return False
        extended_net = ExtendedNet.create(self._pedb.layout, name)
        if isinstance(net, str):
            net = [net]
        for i in net:
            extended_net.core.add_net(self._pedb.nets.nets[i].core)
        return self.items[name]

    def auto_identify_signal(
        self,
        resistor_below: int | float = 10,
        inductor_below: int | float = 1,
        capacitor_above: int | float = 1e-9,
        exception_list: list | None = None,
    ):
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

        return self.generate_extended_nets(
            resistor_below,
            inductor_below,
            capacitor_above,
            exception_list,
            include_signal=True,
            include_power=False,
        )

    def auto_identify_power(
        self,
        resistor_below: int | float = 10,
        inductor_below: int | float = 1,
        capacitor_above: int | float = 1,
        exception_list: list | None = None,
    ):
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

        return self.generate_extended_nets(
            resistor_below,
            inductor_below,
            capacitor_above,
            exception_list,
            include_signal=False,
            include_power=True,
        )

    def generate_extended_nets(
        self,
        resistor_below: int | float = 10,
        inductor_below: int | float = 1e-6,
        capacitor_above: int | float = 1e-9,
        exception_list: list | None = None,
        include_signal: bool = True,
        include_power: bool = True,
    ):
        """Get extended nets and associated components.

        Parameters
        ----------
        resistor_below : int, float, optional
            Threshold of resistor value. Extended nets are searched across resistors
            with values lower than this threshold. Default value is `10 ohms`
        inductor_below : int, float, optional
            Threshold of inductor value. Extended nets are searched across inductors
            with values lower than this threshold. Default value is `1uH`
        capacitor_above : int, float, optional
            Threshold of capacitor value. Extended nets are searched across capacitors
            with values higher than this threshold. Default value is `1nF`
        exception_list : list, optional
            List of components to bypass when performing threshold checks. Components
            in the list are considered as serial components. The default is ``None``.
        include_signal : bool, optional
            Whether to generate extended signal nets. The default is ``True``.
        include_power : bool, optional
            Whether to generate extended power nets. The default is ``True``.

        Returns
        -------
        list[list[str]]
            List of generated extended net groups.

        Examples
        --------
        >>> from pyedb import Edb
        >>> app = Edb()
        >>> app.nets.generate_extended_nets()
        """
        exception_set = set(exception_list or [])

        extended_nets = []
        nets = self._pedb.nets.nets
        remaining_nets = set(nets)

        net_dicts = (
            self._pedb.nets._comps_by_nets_dict
            if self._pedb.nets._comps_by_nets_dict
            else self._pedb.nets.components_by_nets
        )
        comp_dict = (
            self._pedb.nets._nets_by_comp_dict
            if self._pedb.nets._nets_by_comp_dict
            else self._pedb.nets.nets_by_components
        )

        cap, unit = decompose_variable_value(capacitor_above)
        capacitor_above = unit_converter(
            values=cap,
            unit_system="Capacitance",
            input_units=unit if unit else "F",
            output_units="F",
        )

        ind, unit = decompose_variable_value(inductor_below)
        inductor_below = unit_converter(
            values=ind,
            unit_system="Inductance",
            input_units=unit if unit else "H",
            output_units="H",
        )

        res, unit = decompose_variable_value(resistor_below)
        resistor_below = unit_converter(
            values=res,
            unit_system="Resistance",
            input_units=unit if unit else "ohm",
            output_units="ohm",
        )

        def component_passes_threshold(refdes):
            """Return True when the component should be traversed."""
            cmp = self._pedb.components.instances.get(refdes)
            if not cmp:
                return False

            if cmp.type not in {"inductor", "resistor", "capacitor"}:
                return False

            if not cmp.enabled:
                return False

            if refdes in exception_set:
                return True

            r_value, l_value, c_value = cmp.rlc_values[0] if isinstance(cmp.rlc_values[0], list) else cmp.rlc_values

            if cmp.type == "inductor":
                return l_value is not None and l_value < inductor_below

            if cmp.type == "resistor":
                return r_value is not None and r_value < resistor_below

            if cmp.type == "capacitor":
                return c_value is not None and float(c_value) > capacitor_above

            return False

        def collect_connected_nets(start_net):
            """Collect all nets connected through qualifying R/L/C components."""
            collected = []
            visited = set()
            stack = [start_net]

            while stack:
                net_name = stack.pop()

                if net_name in visited:
                    continue

                visited.add(net_name)
                collected.append(net_name)

                for refdes in net_dicts.get(net_name, []):
                    if not component_passes_threshold(refdes):
                        continue

                    for connected_net in comp_dict.get(refdes, []):
                        if connected_net not in visited:
                            stack.append(connected_net)

            return collected

        def get_representative_net(net_group):
            """Return a deterministic non-unnamed net, or the first net if all are unnamed."""
            sorted_group = sorted(net_group)

            for net_name in sorted_group:
                if not net_name.lower().startswith("unnamed"):
                    return net_name

            return sorted_group[0]

        while remaining_nets:
            start_net = sorted(remaining_nets)[0]
            net_group = collect_connected_nets(start_net)

            remaining_nets.difference_update(net_group)

            if len(net_group) <= 1:
                continue

            is_power = any(nets[net_name].is_power_ground for net_name in net_group)

            if is_power and not include_power:
                continue

            if not is_power and not include_signal:
                continue

            representative_net = get_representative_net(net_group)

            if representative_net in self.items:
                extended_nets.append(net_group)
                continue

            ext_net = ExtendedNet.create(self._pedb.layout, representative_net)

            for net_name in net_group:
                ext_net.core.add_net(nets[net_name].core)

            extended_nets.append(net_group)

        return extended_nets


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
        core_extended_net = CoreExtendedNet.create(layout.core, name)
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
    def components(self) -> dict[str, Component]:
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
