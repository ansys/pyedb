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

import warnings

from pyedb.common.nets import CommonNets
from pyedb.generic.general_methods import generate_unique_name
from pyedb.grpc.database.net.net import Net
from pyedb.grpc.database.primitive.bondwire import Bondwire
from pyedb.grpc.database.primitive.path import Path
from pyedb.grpc.database.primitive.polygon import Polygon
from pyedb.misc.utilities import compute_arc_points


class Nets(CommonNets):
    """Manages EDB methods for nets management accessible from `Edb.nets` property.

    Examples
    --------
    >>> from pyedb import Edb
    >>> edbapp = Edb("myaedbfolder", edbversion="2021.2")
    >>> edb_nets = edbapp.nets
    """

    def __getitem__(self, name):
        """Get a net by name.

        Parameters
        ----------
        name : str
            Name of the net to retrieve.

        Returns
        -------
        pyedb.grpc.database.net.net.Net
            Net object if found, otherwise None.
        """
        return Net(self._pedb, Net.find_by_name(self._active_layout, name))

    def __contains__(self, name):
        """Check if a net exists in the layout.

        Parameters
        ----------
        name : str
            Name of the net to check.

        Returns
        -------
        bool
            True if the net exists, False otherwise.
        """
        return name in self.nets

    def __init__(self, p_edb):
        """Initialize the Nets class."""
        CommonNets.__init__(self, p_edb)
        self._nets_by_comp_dict = {}
        self._comps_by_nets_dict = {}

    @property
    def _edb(self):
        """EDB object."""
        return self._pedb

    @property
    def _active_layout(self):
        """Active layout."""
        return self._pedb.active_layout

    @property
    def _layout(self):
        """Current layout."""
        return self._pedb.layout

    @property
    def _cell(self):
        """Current cell."""
        return self._pedb.cell

    @property
    def db(self):
        """Database object."""
        return self._pedb.active_db

    @property
    def _logger(self):
        """Logger instance."""
        return self._pedb.logger

    @property
    def nets(self):
        """All nets in the layout.

        Returns
        -------
        dict[str, pyedb.grpc.database.net.net.Net]
            Dictionary of net names to Net objects.
        """
        return {i.name: i for i in self._pedb.layout.nets}

    @property
    def netlist(self):
        """List of all net names.

        Returns
        -------
        list[str]
            Names of all nets in the layout.
        """
        return list(self.nets.keys())

    @property
    def signal(self):
        """Signal nets in the layout.

        Returns
        -------
        dict[str, pyedb.grpc.database.net.net.Net]
            Dictionary of signal net names to Net objects.
        """
        nets = {}
        for net, value in self.nets.items():
            if not value.is_power_ground:
                nets[net] = value
        return nets

    @property
    def power(self):
        """Power and ground nets in the layout.

        Returns
        -------
        dict[str, pyedb.grpc.database.net.net.Net]
            Dictionary of power/ground net names to Net objects.
        """
        nets = {}
        for net, value in self.nets.items():
            if value.is_power_ground:
                nets[net] = value
        return nets

    def eligible_power_nets(self, threshold=0.3):
        """Identify nets eligible for power/ground classification based on area ratio.

        Uses the same algorithm implemented in SIwave.

        Parameters
        ----------
        threshold : float, optional
            Area ratio threshold. Nets with plane area ratio above this value are
            considered power/ground nets.

        Returns
        -------
        list[pyedb.grpc.database.net.net.Net]
            List of nets eligible as power/ground nets.
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
        """Mapping of components to their associated nets.

        Returns
        -------
        dict[str, list[str]]
            Dictionary mapping component names to list of net names.
        """
        for comp, i in self._pedb.components.instances.items():
            self._nets_by_comp_dict[comp] = i.nets
        return self._nets_by_comp_dict

    @property
    def components_by_nets(self):
        """Mapping of nets to their associated components.

        Returns
        -------
        dict[str, list[str]]
            Dictionary mapping net names to list of component names.
        """
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
        """Generate extended nets based on component thresholds.

        .. deprecated:: pyedb 0.30.0
            Use :func:`pyedb.grpc.extended_nets.generate_extended_nets` instead.

        Parameters
        ----------
        resistor_below : int | float, optional
            Resistor threshold value. Components below this value are considered.
        inductor_below : int | float, optional
            Inductor threshold value. Components below this value are considered.
        capacitor_above : int | float, optional
            Capacitor threshold value. Components above this value are considered.
        exception_list : list, optional
            List of components to bypass during threshold checks.
        include_signal : bool, optional
            Whether to include signal nets in extended net generation.
        include_power : bool, optional
            Whether to include power nets in extended net generation.

        Returns
        -------
        list
            List of generated extended nets.
        """
        warnings.warn("Use new method :func:`edb.extended_nets.generate_extended_nets` instead.", DeprecationWarning)
        self._pedb.extended_nets.generate_extended_nets(
            resistor_below, inductor_below, capacitor_above, exception_list, include_signal, include_power
        )

    @staticmethod
    def _get_points_for_plot(my_net_points):
        """Get points for plotting.

        Parameters
        ----------
        my_net_points : list
            List of points defining the net.

        Returns
        -------
        tuple
            X and Y coordinates of the points.
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

    def classify_nets(self, power_nets=None, signal_nets=None):
        """Reassign net classifications as power/ground or signal.

        Parameters
        ----------
        power_nets : str | list[str], optional
            Nets to classify as power/ground.
        signal_nets : str | list[str], optional
            Nets to classify as signal.

        Returns
        -------
        bool
            True if successful, False otherwise.
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

    def is_power_gound_net(self, netname_list):
        """Check if any net in a list is a power/ground net.

        Parameters
        ----------
        netname_list : str | list[str]
            Net name or list of net names to check.

        Returns
        -------
        bool
            True if any net is power/ground, False otherwise.
        """
        if isinstance(netname_list, str):
            netname_list = [netname_list]
        power_nets_names = list(self.power.keys())
        for netname in netname_list:
            if netname in power_nets_names:
                return True
        return False

    def get_dcconnected_net_list(self, ground_nets=["GND"], res_value=0.001):
        """Get nets connected to DC through inductors and low-value resistors.

        Parameters
        ----------
        ground_nets : tuple, optional
            Ground net names. Default is ("GND",).
        res_value : float, optional
            Resistance threshold value. Default is 0.001 ohms.

        Returns
        -------
        list[set]
            List of sets of connected nets.
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

            if numpins == 2 and comp_obj.res_value <= res_value:
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
        """Retrieve power tree for a given power net.

        Parameters
        ----------
        power_net_name : str
            Name of the power net.
        ground_nets : list
            List of ground net names.

        Returns
        -------
        tuple
            (component_list, component_list_columns, net_group)
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
        """Find a net by name.

        Parameters
        ----------
        net_name : str
            Name of the net to find.

        Returns
        -------
        pyedb.grpc.database.net.net.Net
            Net object if found, otherwise None.
        """
        edb_net = Net.find_by_name(self._active_layout, net_name)
        if edb_net is not None:
            return edb_net

    def delete(self, netlist):
        """Delete one or more nets from the layout.

        Parameters
        ----------
        netlist : str | list[str]
            Net name or list of net names to delete.

        Returns
        -------
        list[str]
            Names of nets that were deleted.

        Examples
        --------
        >>> deleted_nets = database.nets.delete(["Net1","Net2"])
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
        """Find or create a net based on given criteria.

        Parameters
        ----------
        net_name : str, optional
            Exact name of the net to find or create.
        start_with : str, optional
            Find nets starting with this string.
        contain : str, optional
            Find nets containing this string.
        end_with : str, optional
            Find nets ending with this string.

        Returns
        -------
        pyedb.grpc.database.net.net.Net | list[pyedb.grpc.database.net.net.Net]
            Net object or list of matching net objects.
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
            True if the net is found in the component, False otherwise.
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
        """Find and fix disjoint nets.

        .. deprecated:: pyedb 0.30.0
            Use :func:`edb.layout_validation.disjoint_nets` instead.

        Parameters
        ----------
        net_list : list[str], optional
            List of nets to check. Checks all nets if None.
        keep_only_main_net : bool, optional
            Keep only the main net segment if True.
        clean_disjoints_less_than : float, optional
            Clean disjoint nets smaller than this area (in m²).
        order_by_area : bool, optional
            Order naming by area instead of object count.

        Returns
        -------
        list
            New ne

            New nets created.

        """

        warnings.warn("Use new function :func:`edb.layout_validation.disjoint_nets` instead.", DeprecationWarning)
        return self._pedb.layout_validation.disjoint_nets(
            net_list, keep_only_main_net, clean_disjoints_less_than, order_by_area
        )

    def merge_nets_polygons(self, net_names_list):
        """Merge polygons for specified nets on each layer.

        Parameters
        ----------
        net_names_list : str | list[str]
            Net name or list of net names.

        Returns
        -------
        bool
            True if successful, False otherwise.
        """
        if isinstance(net_names_list, str):
            net_names_list = [net_names_list]
        return self._pedb.modeler.unite_polygons_on_layer(net_names_list=net_names_list)
