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

from typing import Any, Dict, List, Optional, Set, Tuple, Union
import warnings

from ansys.edb.core.net.net_class import NetClass as GrpcNetClass

from pyedb.common.nets import CommonNets
from pyedb.generic.general_methods import generate_unique_name
from pyedb.grpc.database.net.net import Net
from pyedb.grpc.database.net.net_class import NetClass
from pyedb.grpc.database.primitive.bondwire import Bondwire
from pyedb.grpc.database.primitive.path import Path
from pyedb.grpc.database.primitive.polygon import Polygon
from pyedb.misc.utilities import compute_arc_points


class Nets(CommonNets):
    """Manages EDB methods for nets management accessible from `Edb.nets` property.

        Examples
        --------
    >>> from pyedb import Edb

    >>> # Initialize EDB session
    >>> edbapp = Edb(edbversion="2025.2")

    >>> # Access Nets class
    >>> nets = edbapp.nets

    >>> # =================
    >>> # Property examples
    >>> # =================

    >>> # Get all nets dictionary
    >>> all_nets = nets.nets
    >>> print("All nets:", list(all_nets.keys()))

    >>> # Get net names list
    >>> net_names = nets.netlist
    >>> print("Net names:", net_names)

    >>> # Get signal nets
    >>> signal_nets = nets.signal
    >>> print("Signal nets:", list(signal_nets.keys()))

    >>> # Get power/ground nets
    >>> power_nets = nets.power
    >>> print("Power nets:", list(power_nets.keys()))

    >>> # Get nets by components
    >>> nets_by_comps = nets.nets_by_components
    >>> print("Nets by components:", nets_by_comps)

    >>> # Get components by nets
    >>> comps_by_nets = nets.components_by_nets
    >>> print("Components by nets:", comps_by_nets)

    >>> # ===============
    >>> # Method examples
    >>> # ===============

    >>> # Get net by name
    >>> net_obj = nets["GND"]
    >>> print(f"Net object: {net_obj.name}")

    >>> # Check net existence
    >>> if "PCIe_RX" in nets:
    >>>    print("PCIe_RX exists")

    >>> # Identify eligible power nets
    >>> eligible_pwr = nets.eligible_power_nets(threshold=0.25)
    >>> print("Eligible power nets:", [net.name for net in eligible_pwr])

    >>> # Generate extended nets (deprecated)
    >>> nets.generate_extended_nets(resistor_below=5, inductor_below=0.5, capacitor_above=0.1)

    >>> # Classify nets
    >>> nets.classify_nets(power_nets=["VDD_CPU", "VDD_MEM"], signal_nets=["PCIe_TX", "ETH_RX"])

    >>> # Check power/ground status
    >>> is_power = nets.is_power_gound_net(["VDD_CPU", "PCIe_TX"])
    >>> print("Is power net:", is_power)

    >>> # Get DC-connected nets
    >>> dc_connected = nets.get_dcconnected_net_list(ground_nets=["GND"], res_value=0.002)
        print("DC-connected nets:", dc_connected)

    >>> # Get power tree
    >>> comp_list, columns, net_group = nets.get_powertree(power_net_name="VDD_CPU", ground_nets=["GND"])
    >>> print("Power tree components:", comp_list)

    >>> # Find net by name
    >>> found_net = nets.get_net_by_name("PCIe_TX")
    >>> print(f"Found net: {found_net.name}")

    >>> # Delete nets
    >>> deleted = nets.delete(["Unused_Net", "Test_Net"])
    >>> print("Deleted nets:", deleted)

    >>> # Find or create net
    >>> new_net = nets.find_or_create_net(net_name="New_Net")
    >>> print(f"Created net: {new_net.name}")

    >>> # Check net-component association
    >>> in_component = nets.is_net_in_component("U1", "VDD_CPU")
    >>> print("Net in component:", in_component)

    >>> # Find and fix disjoint nets (deprecated)
    >>> fixed_nets = nets.find_and_fix_disjoint_nets(net_list=["PCIe_TX"], clean_disjoints_less_than=1e-6)
    >>> print("Fixed nets:", fixed_nets)

    >>> # Merge net polygons
    >>> merged = nets.merge_nets_polygons(["VDD_CPU", "VDD_MEM"])
    >>> print("Polygons merged:", merged)

        # Close EDB session
    >>> edbapp.close()
    """

    def __getitem__(self, name: str) -> Net:
        """Get a net by name.

        Parameters
        ----------
        name : str
            Name of the net to retrieve.

        Returns
        -------
        pyedb.grpc.database.net.net.Net
            Net object if found, otherwise None.

        Examples
        --------
        >>> gnd_net = edb_nets["GND"]
        >>> print(gnd_net.name)
        """
        return Net.find_by_name(self._active_layout, name)

    def __contains__(self, name: str) -> bool:
        """Check if a net exists in the layout.

        Parameters
        ----------
        name : str
            Name of the net to check.

        Returns
        -------
        bool
            True if the net exists, False otherwise.

        Examples
        --------
        >>> if "PCIe_RX" in edb_nets:
        >>>     print("Net exists")
        """
        return name in self.nets

    def __init__(self, p_edb: Any) -> None:
        """Initialize the Nets class."""
        CommonNets.__init__(self, p_edb)
        self._nets_by_comp_dict: Dict[str, List[str]] = {}
        self._comps_by_nets_dict: Dict[str, List[str]] = {}

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
    def nets(self) -> Dict[str, Net]:
        """All nets in the layout.

        Returns
        -------
        dict[str, pyedb.grpc.database.net.net.Net]
            Dictionary of net names to Net objects.

         Examples
        --------
        >>> all_nets = edb_nets.nets
        >>> for net_name, net_obj in all_nets.items():
        ...     print(net_name, net_obj.is_power_ground)
        """
        return {i.name: i for i in self._pedb.layout.nets}

    @property
    def netlist(self) -> List[str]:
        """List of all net names.

        Returns
        -------
        list[str]
            Names of all nets in the layout.

        Examples
        --------
        >>> net_names = edb_nets.netlist
        >>> print("Total nets:", len(net_names))
        """
        return list(self.nets.keys())

    @property
    def signal(self) -> Dict[str, Net]:
        """Signal nets in the layout.

        Returns
        -------
        dict[str, pyedb.grpc.database.net.net.Net]
            Dictionary of signal net names to Net objects.

        Examples
        --------
        >>> signal_nets = edb_nets.signal
        >>> print("Signal nets:", list(signal_nets.keys()))
        """
        nets = {}
        for net, value in self.nets.items():
            if not value.is_power_ground:
                nets[net] = value
        return nets

    @property
    def power(self) -> Dict[str, Net]:
        """Power and ground nets in the layout.

        Returns
        -------
        dict[str, pyedb.grpc.database.net.net.Net]
            Dictionary of power/ground net names to Net objects.

        Examples
        --------
        >>> power_nets = edb_nets.power
        >>> print("Power nets:", list(power_nets.keys()))
        """
        nets = {}
        for net, value in self.nets.items():
            if value.is_power_ground:
                nets[net] = value
        return nets

    def eligible_power_nets(self, threshold: float = 0.3) -> List[Net]:
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

        Examples
        --------
        >>> eligible_pwr = edb_nets.eligible_power_nets(threshold=0.25)
        >>> print([net.name for net in eligible_pwr])
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
    def nets_by_components(self) -> Dict[str, List[str]]:
        """Mapping of components to their associated nets.

        Returns
        -------
        dict[str, list[str]]
            Dictionary mapping component names to list of net names.

        Examples
        --------
        >>> nets_by_comps = edb_nets.nets_by_components
        >>> print("U1 nets:", nets_by_comps.get("U1", []))
        """
        for comp, i in self._pedb.components.instances.items():
            self._nets_by_comp_dict[comp] = i.nets
        return self._nets_by_comp_dict

    @property
    def components_by_nets(self) -> Dict[str, List[str]]:
        """Mapping of nets to their associated components.

        Returns
        -------
        dict[str, list[str]]
            Dictionary mapping net names to list of component names.

        Examples
        --------
        >>> comps_by_nets = edb_nets.components_by_nets
        >>> print("Components on GND:", comps_by_nets.get("GND", []))
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
        resistor_below: Union[int, float] = 10,
        inductor_below: Union[int, float] = 1,
        capacitor_above: Union[int, float] = 1,
        exception_list: Optional[List[str]] = None,
        include_signal: bool = True,
        include_power: bool = True,
    ) -> List[Any]:
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

        Examples
        --------
        >>> edb_nets.generate_extended_nets(resistor_below=5, inductor_below=0.5, capacitor_above=0.1)
        """
        warnings.warn("Use new method :func:`edb.extended_nets.generate_extended_nets` instead.", DeprecationWarning)
        self._pedb.extended_nets.generate_extended_nets(
            resistor_below, inductor_below, capacitor_above, exception_list, include_signal, include_power
        )

    @staticmethod
    def _get_points_for_plot(my_net_points: List[Any]) -> Tuple[List[float], List[float]]:
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

    def classify_nets(
        self, power_nets: Optional[Union[str, List[str]]] = None, signal_nets: Optional[Union[str, List[str]]] = None
    ) -> bool:
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

        Examples
        --------
        >>> edb_nets.classify_nets(power_nets=["VDD_CPU", "VDD_MEM"], signal_nets=["PCIe_TX", "ETH_RX"])
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

    def is_power_gound_net(self, netname_list: Union[str, List[str]]) -> bool:
        """Check if any net in a list is a power/ground net.

        Parameters
        ----------
        netname_list : str | list[str]
            Net name or list of net names to check.

        Returns
        -------
        bool
            True if any net is power/ground, False otherwise.

        Examples
        --------
        >>> is_power = edb_nets.is_power_gound_net(["VDD_CPU", "PCIe_TX"])
        >>> print("Contains power net:", is_power)
        """
        if isinstance(netname_list, str):
            netname_list = [netname_list]
        power_nets_names = list(self.power.keys())
        for netname in netname_list:
            if netname in power_nets_names:
                return True
        return False

    def get_dcconnected_net_list(self, ground_nets: List[str] = ["GND"], res_value: float = 0.001) -> List[Set[str]]:
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

        Examples
        --------
        >>> dc_connected = edb_nets.get_dcconnected_net_list(ground_nets=["GND"], res_value=0.002)
        >>> for net_group in dc_connected:
        ...     print("Connected nets:", net_group)
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

    def get_powertree(
        self, power_net_name: str, ground_nets: List[str]
    ) -> Tuple[List[List[str]], List[str], List[str]]:
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

        Examples
        --------
        >>> comp_list, columns, net_group = edb_nets.get_powertree(power_net_name="VDD_CPU", ground_nets=["GND"])
        >>> print("Power tree components:", comp_list)
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

    def get_net_by_name(self, net_name: str) -> Optional[Net]:
        """Find a net by name.

        Parameters
        ----------
        net_name : str
            Name of the net to find.

        Returns
        -------
        pyedb.grpc.database.net.net.Net
            Net object if found, otherwise None.

        Examples
        --------
        >>> found_net = edb_nets.get_net_by_name("PCIe_TX")
        >>> if found_net:
        ...     print("Net found:", found_net.name)
        """
        edb_net = Net.find_by_name(self._active_layout, net_name)
        if edb_net is not None:
            return edb_net

    def delete(self, netlist: Union[str, List[str]]) -> List[str]:
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
        >>> deleted_nets = database.nets.delete(["Net1", "Net2"])
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

    def find_or_create_net(
        self, net_name: str = "", start_with: str = "", contain: str = "", end_with: str = ""
    ) -> Union[Net, List[Net]]:
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

        Examples
        --------
        >>> # Create new net
        >>> new_net = edb_nets.find_or_create_net(net_name="New_Net")
        >>>
        >>> # Find existing net
        >>> existing_net = edb_nets.find_or_create_net(net_name="GND")
        >>>
        >>> # Find nets starting with "VDD"
        >>> vdd_nets = edb_nets.find_or_create_net(start_with="VDD")
        >>>
        >>> # Find nets ending with "_P"
        >>> pos_nets = edb_nets.find_or_create_net(end_with="_P")
        """
        if not net_name and not start_with and not contain and not end_with:
            net_name = generate_unique_name("NET_")
            net = Net.create(self._active_layout, net_name)
            return net
        else:
            if not start_with and not contain and not end_with:
                net = Net.find_by_name(layout=self._active_layout, name=net_name)
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

    def is_net_in_component(self, component_name: str, net_name: str) -> bool:
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

        Examples
        --------
        >>> in_component = edb_nets.is_net_in_component("U1", "VDD_CPU")
        >>> print("Net in component:", in_component)
        """
        if component_name not in self._pedb.components.instances:
            return False
        for net in self._pedb.components.instances[component_name].nets:
            if net_name == net:
                return True
        return False

    def find_and_fix_disjoint_nets(
        self,
        net_list: Optional[List[str]] = None,
        keep_only_main_net: bool = False,
        clean_disjoints_less_than: float = 0.0,
        order_by_area: bool = False,
    ) -> List[str]:
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

        Examples
        --------
        >>> fixed_nets = edb_nets.find_and_fix_disjoint_nets(net_list=["PCIe_TX"], clean_disjoints_less_than=1e-6)
        >>> print("Fixed nets:", fixed_nets)
        """

        warnings.warn("Use new function :func:`edb.layout_validation.disjoint_nets` instead.", DeprecationWarning)
        return self._pedb.layout_validation.disjoint_nets(
            net_list, keep_only_main_net, clean_disjoints_less_than, order_by_area
        )

    def merge_nets_polygons(self, net_names_list: Union[str, List[str]]) -> bool:
        """Merge polygons for specified nets on each layer.

        Parameters
        ----------
        net_names_list : str | list[str]
            Net name or list of net names.

        Returns
        -------
        bool
            True if successful, False otherwise.

        Examples
        --------
        >>> merged = edb_nets.merge_nets_polygons(["VDD_CPU", "VDD_MEM"])
        >>> print("Merge successful:", merged)
        """
        if isinstance(net_names_list, str):
            net_names_list = [net_names_list]
        return self._pedb.modeler.unite_polygons_on_layer(net_names_list=net_names_list)


class NetClasses:
    """Net classes management.

    This class provides access to net classes in the EDB layout.
    It allows for operations like retrieving nets, adding/removing nets,
    and checking if a net is part of a net class.

    Examples
    --------
    >>> from pyedb import Edb
    >>> edb = Edb(myedb, edbversion="2025.1")
    >>> net_classes = edb.net_classes
    """

    def __init__(self, pedb):
        self._pedb = pedb
        self._net_classes = pedb.active_layout.net_classes

    def __getitem__(self, name: str) -> NetClass:
        """Get a net by name.

        Parameters
        ----------
        name : str
            Name of the net to retrieve.

        """
        return self.items[name]

    @property
    def items(self) -> Dict[str, NetClass]:
        """Extended nets.

        Returns
        -------
        Dict[str, :class:`pyedb.grpc.database.nets.nets_class.NetClass`]
            Dictionary of extended nets.
        """
        return {i.name: i for i in self._pedb.layout.net_classes}

    def create(self, name, net) -> Union[bool, NetClass]:
        """Create a new net class.

        Parameters
        ----------
        name : str
            Name of the net class.
        net : str, list
           Name of the nets to be added into this net class.

        Returns
        -------
        :class:`pyedb.dotnet.database.edb_data.nets_data.EDBNetClassData` `False` if net name already exists.
        """
        if name in self.items:
            self._pedb.logger.error("{} already exists.".format(name))
            return False
        grpc_net_class = GrpcNetClass.create(self._pedb.active_layout.core, name)
        if isinstance(net, str):
            net = [net]
        for i in net:
            grpc_net_class.add_net(self._pedb.nets[i].core)
        net_class = NetClass(self._pedb, grpc_net_class)
        self.items[name] = net_class
        return net_class
