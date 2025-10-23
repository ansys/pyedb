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

from __future__ import absolute_import  # noreorder

import warnings

from pyedb.common.nets import CommonNets
from pyedb.dotnet.database.edb_data.nets_data import EDBNetsData
from pyedb.generic.general_methods import generate_unique_name
from pyedb.misc.utilities import compute_arc_points


class EdbNets(CommonNets):
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
        :class:` :class:`pyedb.dotnet.database.edb_data.nets_data.EDBNetsData`

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
        CommonNets.__init__(self, p_edb)
        self._nets_by_comp_dict = {}
        self._comps_by_nets_dict = {}

    @property
    def _edb(self):
        """ """
        return self._pedb.core

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
        dict[str, :class:`pyedb.dotnet.database.edb_data.nets_data.EDBNetsData`]
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
    def signal_nets(self):
        """Signal nets.

        .. deprecated:: 0.6.62
           Use :func:`signal` instead.

        Returns
        -------
        dict[str, :class:`pyedb.dotnet.database.edb_data.EDBNetsData`]
            Dictionary of signal nets.
        """
        warnings.warn("Use :func:`signal` instead.", DeprecationWarning)
        return self.signal

    @property
    def power_nets(self):
        """Power nets.

        .. deprecated:: 0.6.62
           Use :func:`power` instead.

        Returns
        -------
        dict[str, :class:`pyedb.dotnet.database.edb_data.EDBNetsData`]
            Dictionary of power nets.
        """
        warnings.warn("Use :func:`power` instead.", DeprecationWarning)
        return self.power

    @property
    def signal(self):
        """Signal nets.

        Returns
        -------
        dict[str, :class:`pyedb.dotnet.database.edb_data.EDBNetsData`]
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
        dict[str, :class:`pyedb.dotnet.database.edb_data.EDBNetsData`]
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
        list of  :class:`pyedb.dotnet.database.edb_data.EDBNetsData`
        """
        pwr_gnd_nets = []
        for net in self._layout.nets[:]:
            total_plane_area = 0.0
            total_trace_area = 0.0
            for primitive in net.primitives:
                primitive = primitive._edb_object
                if primitive.GetPrimitiveType() == self._edb.Cell.Primitive.PrimitiveType.Bondwire:
                    continue
                if primitive.GetPrimitiveType() != self._edb.Cell.Primitive.PrimitiveType.Path:
                    total_plane_area += float(primitive.GetPolygonData().Area())
                else:
                    total_trace_area += float(primitive.GetPolygonData().Area())
            if total_plane_area == 0.0:
                continue
            if total_trace_area == 0.0:
                pwr_gnd_nets.append(EDBNetsData(net.api_object, self._pedb))
                continue
            if total_plane_area > 0.0 and total_trace_area > 0.0:
                if total_plane_area / (total_plane_area + total_trace_area) > threshold:
                    pwr_gnd_nets.append(EDBNetsData(net.api_object, self._pedb))
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
        if exception_list is None:
            exception_list = []
        _extended_nets = []
        _nets = self.nets
        all_nets = list(_nets.keys())[:]
        net_dicts = self._comps_by_nets_dict if self._comps_by_nets_dict else self.components_by_nets
        comp_dict = self._nets_by_comp_dict if self._nets_by_comp_dict else self.nets_by_components

        def get_net_list(net_name, _net_list):
            comps = []
            if net_name in net_dicts:
                comps = net_dicts[net_name]

            for vals in comps:
                refdes = vals
                cmp = self._pedb.components.instances[refdes]
                is_enabled = cmp.is_enabled
                if not is_enabled:
                    continue
                val_type = cmp.type
                if val_type not in ["Inductor", "Resistor", "Capacitor"]:
                    continue

                val_value = cmp.rlc_values
                if refdes in exception_list:
                    pass
                elif val_type == "Inductor":
                    if val_value[1] is None:
                        continue
                    elif (
                        not self._pedb.edb_value(val_value[1]).ToDouble()
                        <= self._pedb.edb_value(inductor_below).ToDouble()
                    ):
                        continue
                elif val_type == "Resistor":
                    if val_value[0] is None:
                        continue
                    elif (
                        not self._pedb.edb_value(val_value[0]).ToDouble()
                        <= self._pedb.edb_value(resistor_below).ToDouble()
                    ):
                        continue
                elif val_type == "Capacitor":
                    if val_value[2] is None:
                        continue
                    elif (
                        not self._pedb.edb_value(val_value[2]).ToDouble()
                        >= self._pedb.edb_value(capacitor_above).ToDouble()
                    ):
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
                        self._pedb.extended_nets.create(i, new_ext)
                    else:  # pragma: no cover
                        pass
                else:
                    if include_signal:
                        self._pedb.extended_nets.create(i, new_ext)
                    else:  # pragma: no cover
                        pass

        return _extended_nets

    def _get_points_for_plot(self, my_net_points):
        """
        Get the points to be plot
        """
        # fmt: off
        x = []
        y = []
        for i, point in enumerate(my_net_points):
            # point = my_net_points[i]
            if not point.IsArc():
                x.append(point.X.ToDouble())
                y.append(point.Y.ToDouble())
                # i += 1
            else:
                arc_h = point.GetArcHeight().ToDouble()
                p1 = [my_net_points[i - 1].X.ToDouble(), my_net_points[i - 1].Y.ToDouble()]
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
                self.nets[net].net_object.SetIsPowerGround(True)
        for net in signal_nets:
            if net in self.nets:
                self.nets[net].net_object.SetIsPowerGround(False)
        return True

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
        power_nets_names = list(self.power_nets.keys())
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
            pins = self._pedb.components.get_pin_from_component(component=refdes, netName=el[2])
            el.append("-".join([i.GetName() for i in pins]))

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

        edb_net = self._edb.Cell.Net.FindByName(self._active_layout, net_name)
        if not edb_net.IsNull():
            return self._pedb.pedb_class.database.edb_data.nets_data.EDBNetsData(edb_net, self._pedb)

    def delete_nets(self, netlist):
        """Delete one or more nets from EDB.

        .. deprecated:: 0.6.62
           Use :func:`delete` method instead.

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

        >>> deleted_nets = database.nets.delete(["Net1", "Net2"])
        """
        warnings.warn("Use :func:`delete` method instead.", DeprecationWarning)
        return self.delete(netlist=netlist)

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

        >>> deleted_nets = database.nets.delete(["Net1", "Net2"])
        """
        if isinstance(netlist, str):
            netlist = [netlist]

        self._pedb.modeler.delete_primitives(netlist)
        self._pedb.padstacks.delete_padstack_instances(netlist)

        nets_deleted = []

        for i in self._pedb.nets.nets.values():
            if i.name in netlist:
                i.net_object.Delete()
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
            self._edb.Cell.Net.Create(self._active_layout, net_name)
            return self.nets[net_name]
        else:
            if not start_with and not contain and not end_with:
                net = self._edb.Cell.Net.FindByName(self._active_layout, net_name)
                if net.IsNull():
                    net = self._edb.Cell.Net.Create(self._active_layout, net_name)
                return self.nets[net_name]
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
                    self.nets[net]
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

        >>> renamed_nets = database.nets.find_and_fix_disjoint_nets(["GND", "Net2"])
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
