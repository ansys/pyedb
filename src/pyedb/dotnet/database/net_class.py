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

from __future__ import absolute_import  # noreorder

import re

from pyedb.dotnet.database.edb_data.nets_data import (
    EDBDifferentialPairData,
    EDBExtendedNetData,
    EDBNetClassData,
)


class EdbCommon:
    def __init__(self, pedb):
        self._pedb = pedb

    @property
    def _layout(self):
        """Get layout.

        Returns
        -------
        """
        return self._pedb.layout

    @property
    def _logger(self):
        """EDB logger."""
        return self._pedb.logger

    def __getitem__(self, name):
        """Get  a net from the EDB project.

        Parameters
        ----------
        name : str, int
            Name or ID of the net.

        Returns
        -------
        :class:` :class:`pyedb.dotnet.database.edb_data.nets_data.EDBExtendedNetsData`

        """
        if name in self.items:
            return self.items[name]
        self._pedb.logger.error("Component or definition not found.")


class EdbNetClasses(EdbCommon, object):
    """Manages EDB methods for managing nets accessible from the ``Edb.net_classes`` property.

    Examples
    --------
    >>> from pyedb import Edb
    >>> edbapp = Edb("myaedbfolder", edbversion="2021.2")
    >>> edb_nets = edbapp.net_classes
    """

    def __init__(self, p_edb):
        super().__init__(p_edb)

    @property
    def items(self):
        """Extended nets.

        Returns
        -------
        dict[str, :class:`pyedb.dotnet.database.edb_data.nets_data.EDBDifferentialPairData`]
            Dictionary of extended nets.
        """
        temp = {}
        for i in self._layout.net_classes:
            temp[i.name] = i
        return temp

    def create(self, name, net):
        # type: (str, str|list)->EDBNetClassData
        """Create a new net class.

        Parameters
        ----------
        name : str
            Name of the net class.
        net : str, list
           Name of the nets to be added into this net class.

        Returns
        -------
        :class:`pyedb.dotnet.database.edb_data.nets_data.EDBNetClassData`
        """
        if name in self.items:
            self._pedb.logger.error("{} already exists.".format(name))
            return False

        temp = EDBNetClassData(self._pedb)
        api_obj = temp.api_create(name)
        if isinstance(net, str):
            net = [net]
        for i in net:
            api_obj.add_net(i)

        return self.items[name]


class EdbExtendedNets(EdbCommon, object):
    """Manages EDB methods for managing nets accessible from the ``Edb.extended_nets`` property.

    Examples
    --------
    >>> from pyedb import Edb
    >>> edbapp = Edb("myaedbfolder", edbversion="2021.2")
    >>> edb_nets = edbapp.extended_nets
    """

    def __init__(self, p_edb):
        super().__init__(p_edb)

    @property
    def items(self):
        """Extended nets.

        Returns
        -------
        dict[str, :class:`pyedb.dotnet.database.edb_data.nets_data.EDBExtendedNetsData`]
            Dictionary of extended nets.
        """
        nets = {}
        for extended_net in self._pedb.layout.extended_nets:
            nets[extended_net.name] = extended_net
        return nets

    def create(self, name, net):
        # type: (str, str|list)->EDBExtendedNetData
        """Create a new Extended net.

        Parameters
        ----------
        name : str
            Name of the extended net.
        net : str, list
           Name of the nets to be added into this extended net.

        Returns
        -------
        :class:`pyedb.dotnet.database.edb_data.nets_data.EDBExtendedNetsData`
        """
        if name in self.items:
            self._pedb.logger.error("{} already exists.".format(name))
            return False

        extended_net = EDBExtendedNetData(self._pedb)
        api_extended_net = extended_net.api_create(name)
        if isinstance(net, str):
            net = [net]
        for i in net:
            api_extended_net.add_net(i)

        return self.items[name]

    def generate_extended_nets(
        self,
        resistor_below: int | float = 10,
        inductor_below: int | float = 1e-6,
        capacitor_above: int | float = 1e-9,
        exception_list: list | None = None,
        include_signal: bool = True,
        include_power: bool = True,
    ):
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
        include_signal : bool, optional
            Whether to generate extended signal nets. The default is ``True``.
        include_power : bool, optional
            Whether to generate extended power nets. The default is ``True``.

        Returns
        -------
        list
            List of all generated extended net groups.
        """

        def add_extended_net_if_valid(net_group):
            if self._is_valid_extended_net_group(net_group, include_signal, include_power):
                representative_net = self._get_representative_net(net_group)
                self._pedb.extended_nets.create(representative_net, net_group)
                extended_nets.append(net_group)

        extended_nets = []
        processed_nets = set()
        all_nets = list(self._pedb.nets.nets.keys())

        net_dicts = self._pedb.nets._comps_by_nets_dict or self._pedb.nets.components_by_nets
        comp_dict = self._pedb.nets._nets_by_comp_dict or self._pedb.nets.nets_by_components

        thresholds = self._get_extended_net_thresholds(
            resistor_below=resistor_below,
            inductor_below=inductor_below,
            capacitor_above=capacitor_above,
        )

        exceptions = set(exception_list or [])

        for net_name in all_nets:
            if net_name in processed_nets:
                continue

            net_group = self._get_extended_net_group(
                net_name=net_name,
                net_dicts=net_dicts,
                comp_dict=comp_dict,
                thresholds=thresholds,
                exceptions=exceptions,
            )

            processed_nets.update(net_group)
            add_extended_net_if_valid(net_group)

        return extended_nets

    def _get_extended_net_thresholds(
        self,
        resistor_below: int | float,
        inductor_below: int | float,
        capacitor_above: int | float,
    ):
        return {
            "Resistor": (
                0,
                self._pedb.edb_value(resistor_below).ToDouble(),
                lambda value, limit: value <= limit,
            ),
            "Inductor": (
                1,
                self._pedb.edb_value(inductor_below).ToDouble(),
                lambda value, limit: value <= limit,
            ),
            "Capacitor": (
                2,
                self._pedb.edb_value(capacitor_above).ToDouble(),
                lambda value, limit: value >= limit,
            ),
        }

    def _get_extended_net_group(
        self,
        net_name,
        net_dicts,
        comp_dict,
        thresholds,
        exceptions,
    ):
        net_group = []
        visited_nets = set()
        nets_to_visit = [net_name]

        while nets_to_visit:
            current_net = nets_to_visit.pop()

            if current_net in visited_nets:
                continue

            visited_nets.add(current_net)
            net_group.append(current_net)

            connected_nets = self._get_connected_nets_through_serial_components(
                current_net=current_net,
                net_dicts=net_dicts,
                comp_dict=comp_dict,
                thresholds=thresholds,
                exceptions=exceptions,
            )
            nets_to_visit.extend(connected_nets)

        return net_group

    def _get_connected_nets_through_serial_components(
        self,
        current_net,
        net_dicts,
        comp_dict,
        thresholds,
        exceptions,
    ):
        connected_nets = []

        for refdes in net_dicts.get(current_net, []):
            component = self._pedb.components.instances[refdes]

            if not self._is_serial_component_for_extended_net(refdes, component, thresholds, exceptions):
                continue

            connected_nets.extend(comp_dict.get(refdes, []))

        return connected_nets

    def _is_serial_component_for_extended_net(
        self,
        refdes,
        component,
        thresholds,
        exceptions,
    ):
        if not component.is_enabled:
            return False

        if component.type not in thresholds:
            return False

        if refdes in exceptions:
            return True

        return self._passes_extended_net_threshold(component, thresholds)

    def _passes_extended_net_threshold(self, component, thresholds):
        value_index, limit, comparator = thresholds[component.type]
        raw_value = component.rlc_values[value_index]

        if raw_value is None:
            return False

        value = self._pedb.edb_value(raw_value).ToDouble()
        return comparator(value, limit)

    def _is_valid_extended_net_group(
        self,
        net_group,
        include_signal: bool,
        include_power: bool,
    ):
        if len(net_group) <= 1:
            return False

        is_power = self._is_power_extended_net_group(net_group)

        if is_power:
            return include_power

        return include_signal

    def _is_power_extended_net_group(self, net_group):
        nets = self._pedb.nets.nets
        return any(nets[net].is_power_ground for net in net_group)

    def _get_representative_net(self, net_group):
        for net in net_group:
            if not net.lower().startswith("unnamed"):
                return net

        return net_group[0]

    def auto_identify_signal(self, resistor_below=10, inductor_below=1, capacitor_above=1e-9, exception_list=None):
        # type: (int | float, int | float, int |float, list) -> list
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
        list
            List of all extended nets.

        Examples
        --------
        >>> from pyedb import Edb
        >>> app = Edb()
        >>> app.extended_nets.auto_identify_signal()
        """
        return self._pedb.nets.generate_extended_nets(
            resistor_below, inductor_below, capacitor_above, exception_list, True, True
        )

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
        list
            List of all extended nets and their associated components.

        Examples
        --------
        >>> from pyedb import Edb
        >>> app = Edb()
        >>> app.extended_nets.auto_identify_power()
        """
        return self._pedb.nets.generate_extended_nets(
            resistor_below, inductor_below, capacitor_above, exception_list, True, True
        )

    def clean(self):
        """Remove all extended nets."""
        for net in self.items.values():
            net.delete()


class EdbDifferentialPairs(EdbCommon, object):
    """Manages EDB methods for managing nets accessible from the ``Edb.differential_pairs`` property.

    Examples
    --------
    >>> from pyedb import Edb
    >>> edbapp = Edb("myaedbfolder", edbversion="2021.2")
    >>> edb_nets = edbapp.differential_pairs.items
    >>> edb_nets = edbapp.differential_pairs["DQ4"]
    """

    def __init__(self, p_edb):
        super().__init__(p_edb)

    @property
    def items(self):
        """Extended nets.

        Returns
        -------
        dict[str, :class:`pyedb.dotnet.database.edb_data.nets_data.EDBDifferentialPairData`]
            Dictionary of extended nets.
        """
        diff_pairs = {}
        for diff_pair in self._layout.differential_pairs:
            diff_pairs[diff_pair.name] = diff_pair
        return diff_pairs

    def create(self, name, net_p, net_n):
        # type: (str, str, str) -> EDBDifferentialPairData
        """

        Parameters
        ----------
        name : str
            Name of the differential pair.
        net_p : str
            Name of the positive net.
        net_n : str
            Name of the negative net.

        Returns
        -------
        :class:`pyedb.dotnet.database.edb_data.nets_data.EDBDifferentialPairData`
        """
        if name in self.items:
            self._pedb.logger.error("{} already exists.".format(name))
            return False

        diff_pair = EDBDifferentialPairData(self._pedb)
        diff_pair.api_create(name)._api_set_differential_pair(net_p, net_n)

        return self.items[name]

    def auto_identify(self, positive_differentiator="_P", negative_differentiator="_N"):
        """Auto identify differential pairs by naming conversion.

        Parameters
        ----------
        positive_differentiator: str, optional
            Differentiator of the positive net. The default is ``"_P"``.
        negative_differentiator: str, optional
            Differentiator of the negative net. The default is ``"_N"``.

        Returns
        -------
        list
            A list containing identified differential pair names.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder", edbversion="2023.1")
        >>> edb_nets = edbapp.differential_pairs.auto_identify()
        """
        nets = self._pedb.nets.nets
        pos_net = []
        neg_net = []
        for name, _ in nets.items():
            if name.endswith(positive_differentiator):
                pos_net.append(name)
            elif name.endswith(negative_differentiator):
                neg_net.append(name)
            else:
                pass

        temp = []
        for p in pos_net:
            pattern_p = r"^(.+){}$".format(positive_differentiator)
            match_p = re.findall(pattern_p, p)[0]

            for n in neg_net:
                pattern_n = r"^(.+){}$".format(negative_differentiator)
                match_n = re.findall(pattern_n, n)[0]

                if match_p == match_n:
                    diff_name = "DIFF_{}".format(match_p)
                    self.create(diff_name, p, n)
                    temp.append(diff_name)
        return temp
