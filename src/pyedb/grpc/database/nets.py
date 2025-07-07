# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
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

from typing import Dict, List, Optional, Set, Tuple, Union
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

    This class provides comprehensive net management functionality including:
    - Net retrieval and classification
    - Power/ground net identification
    - Extended net generation
    - Net validation and fixing
    - Component-net relationship management

    Examples
    --------
    >>> from pyedb import Edb
    >>> edbapp = Edb(edbversion="2025.2")
    >>> nets = edbapp.nets

    >>> # Get all nets
    >>> all_nets = nets.nets
    >>> print("Total nets:", len(all_nets))

    >>> # Get specific net
    >>> gnd_net = nets["GND"]
    >>> print(f"GND net: {gnd_net.name}")

    >>> # Classify nets
    >>> nets.classify_nets(
    ...     power_nets=["VDD_CPU", "VDD_MEM"],
    ...     signal_nets=["PCIe_TX", "ETH_RX"]
    ... )
    """

    def __init__(self, p_edb) -> None:
        """Initialize the Nets class.

        Parameters
        ----------
        p_edb : pyedb.Edb
            The EDB instance.
        """
        super().__init__(p_edb)
        self._nets_by_comp_dict: Dict[str, List[str]] = {}
        self._comps_by_nets_dict: Dict[str, List[str]] = {}

    # Properties for accessing EDB internals
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

    # Net access methods
    def __getitem__(self, name: str) -> Net:
        """Get a net by name.

        Parameters
        ----------
        name : str
            Name of the net to retrieve.

        Returns
        -------
        Net
            Net object if found, otherwise None.

        Examples
        --------
        >>> gnd_net = nets["GND"]
        >>> print(gnd_net.name)
        """
        return Net(self._pedb, Net.find_by_name(self._active_layout, name))

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
        >>> if "PCIe_RX" in nets:
        ...     print("Net exists")
        """
        return name in self.nets

    # Net collection properties
    @property
    def nets(self) -> Dict[str, Net]:
        """All nets in the layout.

        Returns
        -------
        Dict[str, Net]
            Dictionary of net names to Net objects.

        Examples
        --------
        >>> all_nets = nets.nets
        >>> for net_name, net_obj in all_nets.items():
        ...     print(net_name, net_obj.is_power_ground)
        """
        return {net.name: net for net in self._pedb.layout.nets}

    @property
    def netlist(self) -> List[str]:
        """List of all net names.

        Returns
        -------
        List[str]
            Names of all nets in the layout.

        Examples
        --------
        >>> net_names = nets.netlist
        >>> print("Total nets:", len(net_names))
        """
        return list(self.nets.keys())

    @property
    def signal(self) -> Dict[str, Net]:
        """Signal nets in the layout.

        Returns
        -------
        Dict[str, Net]
            Dictionary of signal net names to Net objects.

        Examples
        --------
        >>> signal_nets = nets.signal
        >>> print("Signal nets:", list(signal_nets.keys()))
        """
        return {net_name: net_obj for net_name, net_obj in self.nets.items() if not net_obj.is_power_ground}

    @property
    def power(self) -> Dict[str, Net]:
        """Power and ground nets in the layout.

        Returns
        -------
        Dict[str, Net]
            Dictionary of power/ground net names to Net objects.

        Examples
        --------
        >>> power_nets = nets.power
        >>> print("Power nets:", list(power_nets.keys()))
        """
        return {net_name: net_obj for net_name, net_obj in self.nets.items() if net_obj.is_power_ground}

    @property
    def nets_by_components(self) -> Dict[str, List[str]]:
        """Mapping of components to their associated nets.

        Returns
        -------
        Dict[str, List[str]]
            Dictionary mapping component names to list of net names.

        Examples
        --------
        >>> nets_by_comps = nets.nets_by_components
        >>> print("U1 nets:", nets_by_comps.get("U1", []))
        """
        self._nets_by_comp_dict = {
            comp_name: comp_obj.nets for comp_name, comp_obj in self._pedb.components.instances.items()
        }
        return self._nets_by_comp_dict

    @property
    def components_by_nets(self) -> Dict[str, List[str]]:
        """Mapping of nets to their associated components.

        Returns
        -------
        Dict[str, List[str]]
            Dictionary mapping net names to list of component names.

        Examples
        --------
        >>> comps_by_nets = nets.components_by_nets
        >>> print("Components on GND:", comps_by_nets.get("GND", []))
        """
        self._comps_by_nets_dict.clear()
        for comp_name, comp_obj in self._pedb.components.instances.items():
            for net_name in comp_obj.nets:
                self._comps_by_nets_dict.setdefault(net_name, []).append(comp_name)
        return self._comps_by_nets_dict

    # Net analysis methods
    def eligible_power_nets(self, threshold: float = 0.3) -> List[Net]:
        """Identify nets eligible for power/ground classification based on area ratio.

        Uses the same algorithm implemented in SIwave.

        Parameters
        ----------
        threshold : float, optional
            Area ratio threshold. Nets with plane area ratio above this value are
            considered power/ground nets. Default is 0.3.

        Returns
        -------
        List[Net]
            List of nets eligible as power/ground nets.

        Examples
        --------
        >>> eligible_pwr = nets.eligible_power_nets(threshold=0.25)
        >>> print([net.name for net in eligible_pwr])
        """
        pwr_gnd_nets = []

        for net in self._layout.nets:
            total_plane_area = 0.0
            total_trace_area = 0.0

            for primitive in net.primitives:
                if isinstance(primitive, Bondwire):
                    continue

                if isinstance(primitive, (Path, Polygon)):
                    total_plane_area += primitive.polygon_data.area()

            if total_plane_area == 0.0:
                continue

            # If no trace area, consider as power/ground
            if total_trace_area == 0.0:
                pwr_gnd_nets.append(Net(self._pedb, net))
                continue

            # Check area ratio
            total_area = total_plane_area + total_trace_area
            if total_area > 0.0 and (total_plane_area / total_area) > threshold:
                pwr_gnd_nets.append(Net(self._pedb, net))

        return pwr_gnd_nets

    def classify_nets(
        self, power_nets: Optional[Union[str, List[str]]] = None, signal_nets: Optional[Union[str, List[str]]] = None
    ) -> bool:
        """Reassign net classifications as power/ground or signal.

        Parameters
        ----------
        power_nets : str or List[str], optional
            Nets to classify as power/ground.
        signal_nets : str or List[str], optional
            Nets to classify as signal.

        Returns
        -------
        bool
            True if successful, False otherwise.

        Examples
        --------
        >>> nets.classify_nets(
        ...     power_nets=["VDD_CPU", "VDD_MEM"],
        ...     signal_nets=["PCIe_TX", "ETH_RX"]
        ... )
        """
        power_nets = self._normalize_net_list(power_nets)
        signal_nets = self._normalize_net_list(signal_nets)

        # Set power/ground nets
        for net_name in power_nets:
            if net_name in self.nets:
                self.nets[net_name].is_power_ground = True

        # Set signal nets
        for net_name in signal_nets:
            if net_name in self.nets:
                self.nets[net_name].is_power_ground = False

        return True

    def is_power_ground_net(self, netname_list: Union[str, List[str]]) -> bool:
        """Check if any net in a list is a power/ground net.

        Parameters
        ----------
        netname_list : str or List[str]
            Net name or list of net names to check.

        Returns
        -------
        bool
            True if any net is power/ground, False otherwise.

        Examples
        --------
        >>> is_power = nets.is_power_ground_net(["VDD_CPU", "PCIe_TX"])
        >>> print("Contains power net:", is_power)
        """
        netname_list = self._normalize_net_list(netname_list)
        power_net_names = set(self.power.keys())

        return any(net_name in power_net_names for net_name in netname_list)

    # DC connectivity analysis
    def get_dcconnected_net_list(self, ground_nets: List[str] = None, res_value: float = 0.001) -> List[Set[str]]:
        """Get nets connected to DC through inductors and low-value resistors.

        Parameters
        ----------
        ground_nets : List[str], optional
            Ground net names. Default is ["GND"].
        res_value : float, optional
            Resistance threshold value. Default is 0.001 ohms.

        Returns
        -------
        List[Set[str]]
            List of sets of connected nets.

        Examples
        --------
        >>> dc_connected = nets.get_dcconnected_net_list(
        ...     ground_nets=["GND"],
        ...     res_value=0.002
        ... )
        >>> for net_group in dc_connected:
        ...     print("Connected nets:", net_group)
        """
        if ground_nets is None:
            ground_nets = ["GND"]

        ground_nets_set = set(ground_nets)
        temp_list = []

        # Process inductors
        for comp_obj in self._pedb.components.inductors.values():
            if comp_obj.numpins == 2:
                nets = set(comp_obj.nets)
                if not nets.intersection(ground_nets_set):
                    temp_list.append(nets)

        # Process low-value resistors
        for comp_obj in self._pedb.components.resistors.values():
            if comp_obj.numpins == 2 and comp_obj.res_value <= res_value:
                nets = set(comp_obj.nets)
                if not nets.intersection(ground_nets_set):
                    temp_list.append(nets)

        return self._merge_connected_sets(temp_list)

    def get_powertree(
        self, power_net_name: str, ground_nets: List[str]
    ) -> Tuple[List[List[str]], List[str], List[str]]:
        """Retrieve power tree for a given power net.

        Parameters
        ----------
        power_net_name : str
            Name of the power net.
        ground_nets : List[str]
            List of ground net names.

        Returns
        -------
        Tuple[List[List[str]], List[str], List[str]]
            (component_list, component_list_columns, net_group)

        Examples
        --------
        >>> comp_list, columns, net_group = nets.get_powertree(
        ...     power_net_name="VDD_CPU",
        ...     ground_nets=["GND"]
        ... )
        >>> print("Power tree components:", comp_list)
        """
        # Find DC-connected net group
        net_group = [power_net_name]
        for ng in self.get_dcconnected_net_list(ground_nets):
            if power_net_name in ng:
                net_group.extend(ng)
                break

        # Build component list
        component_list = []
        rats = self._pedb.components.get_rats()

        for net_name in net_group:
            for rat in rats:
                if net_name in rat["net_name"]:
                    for i, net in enumerate(rat["net_name"]):
                        if net == net_name:
                            component_list.append([rat["refdes"][i], rat["pin_name"][i], net_name])

        # Add component details
        for component_data in component_list:
            refdes = component_data[0]
            comp_obj = self._pedb.components._cmp[refdes]

            component_data.extend(
                [
                    comp_obj.type,
                    comp_obj.partname,
                    "-".join(
                        [
                            pin.name
                            for pin in self._pedb.components.get_pin_from_component(
                                component=refdes, net_name=component_data[2]
                            )
                        ]
                    ),
                ]
            )

        columns = ["refdes", "pin_name", "net_name", "component_type", "component_partname", "pin_list"]

        return component_list, columns, net_group

    # Net management methods
    def get_net_by_name(self, net_name: str) -> Optional[Net]:
        """Find a net by name.

        Parameters
        ----------
        net_name : str
            Name of the net to find.

        Returns
        -------
        Net or None
            Net object if found, otherwise None.

        Examples
        --------
        >>> found_net = nets.get_net_by_name("PCIe_TX")
        >>> if found_net:
        ...     print("Net found:", found_net.name)
        """
        edb_net = Net.find_by_name(self._active_layout, net_name)
        return edb_net if edb_net is not None else None

    def delete(self, netlist: Union[str, List[str]]) -> List[str]:
        """Delete one or more nets from the layout.

        Parameters
        ----------
        netlist : str or List[str]
            Net name or list of net names to delete.

        Returns
        -------
        List[str]
            Names of nets that were deleted.

        Examples
        --------
        >>> deleted_nets = nets.delete(["Net1", "Net2"])
        >>> print("Deleted nets:", deleted_nets)
        """
        netlist = self._normalize_net_list(netlist)

        # Delete primitives and padstack instances
        self._pedb.modeler.delete_primitives(netlist)
        self._pedb.padstacks.delete_padstack_instances(netlist)

        # Delete nets
        nets_deleted = []
        for net_obj in self._pedb.nets.nets.values():
            if net_obj.name in netlist:
                net_obj.delete()
                nets_deleted.append(net_obj.name)

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
        Net or List[Net]
            Net object or list of matching net objects.

        Examples
        --------
        >>> # Create new net
        >>> new_net = nets.find_or_create_net(net_name="New_Net")
        >>>
        >>> # Find existing net
        >>> existing_net = nets.find_or_create_net(net_name="GND")
        >>>
        >>> # Find nets starting with "VDD"
        >>> vdd_nets = nets.find_or_create_net(start_with="VDD")
        """
        # Create new net if no criteria provided
        if not any([net_name, start_with, contain, end_with]):
            net_name = generate_unique_name("NET_")
            return Net.create(self._active_layout, net_name)

        # Find or create by exact name
        if net_name and not any([start_with, contain, end_with]):
            net = Net.find_by_name(self._active_layout, net_name)
            if net.is_null:
                net = Net.create(self._active_layout, net_name)
            return net

        # Find by criteria
        return self._find_nets_by_criteria(start_with, contain, end_with)

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
        >>> in_component = nets.is_net_in_component("U1", "VDD_CPU")
        >>> print("Net in component:", in_component)
        """
        if component_name not in self._pedb.components.instances:
            return False

        component_nets = self._pedb.components.instances[component_name].nets
        return net_name in component_nets

    def merge_nets_polygons(self, net_names_list: Union[str, List[str]]) -> bool:
        """Merge polygons for specified nets on each layer.

        Parameters
        ----------
        net_names_list : str or List[str]
            Net name or list of net names.

        Returns
        -------
        bool
            True if successful, False otherwise.

        Examples
        --------
        >>> merged = nets.merge_nets_polygons(["VDD_CPU", "VDD_MEM"])
        >>> print("Merge successful:", merged)
        """
        net_names_list = self._normalize_net_list(net_names_list)
        return self._pedb.modeler.unite_polygons_on_layer(net_names_list=net_names_list)

    # Deprecated methods
    def generate_extended_nets(
        self,
        resistor_below: Union[int, float] = 10,
        inductor_below: Union[int, float] = 1,
        capacitor_above: Union[int, float] = 1,
        exception_list: Optional[List[str]] = None,
        include_signal: bool = True,
        include_power: bool = True,
    ) -> List:
        """Generate extended nets based on component thresholds.

        .. deprecated:: pyedb 0.30.0
            Use :func:`pyedb.grpc.extended_nets.generate_extended_nets` instead.
        """
        warnings.warn(
            "Use new method :func:`edb.extended_nets.generate_extended_nets` instead.", DeprecationWarning, stacklevel=2
        )
        return self._pedb.extended_nets.generate_extended_nets(
            resistor_below, inductor_below, capacitor_above, exception_list, include_signal, include_power
        )

    def find_and_fix_disjoint_nets(
        self,
        net_list: Optional[List[str]] = None,
        keep_only_main_net: bool = False,
        clean_disjoints_less_than: float = 0.0,
        order_by_area: bool = False,
    ) -> List:
        """Find and fix disjoint nets.

        .. deprecated:: pyedb 0.30.0
            Use :func:`edb.layout_validation.disjoint_nets` instead.
        """
        warnings.warn(
            "Use new function :func:`edb.layout_validation.disjoint_nets` instead.", DeprecationWarning, stacklevel=2
        )
        return self._pedb.layout_validation.disjoint_nets(
            net_list, keep_only_main_net, clean_disjoints_less_than, order_by_area
        )

    # Utility methods
    def _normalize_net_list(self, nets: Optional[Union[str, List[str]]]) -> List[str]:
        """Normalize net input to a list of strings.

        Parameters
        ----------
        nets : str, List[str], or None
            Net name(s) to normalize.

        Returns
        -------
        List[str]
            Normalized list of net names.
        """
        if nets is None:
            return []
        elif isinstance(nets, str):
            return [nets]
        else:
            return nets

    def _merge_connected_sets(self, sets_list: List[Set[str]]) -> List[Set[str]]:
        """Merge intersecting sets into connected components.

        Parameters
        ----------
        sets_list : List[Set[str]]
            List of sets to merge.

        Returns
        -------
        List[Set[str]]
            List of merged connected sets.
        """
        result = []

        while sets_list:
            current_set = sets_list.pop(0)
            intersection_found = False

            for other_set in sets_list:
                if current_set.intersection(other_set):
                    other_set.update(current_set)
                    intersection_found = True
                    break

            if not intersection_found:
                result.append(current_set)

        return result

    def _find_nets_by_criteria(self, start_with: str, contain: str, end_with: str) -> List[Net]:
        """Find nets matching the given criteria.

        Parameters
        ----------
        start_with : str
            String that net names should start with.
        contain : str
            String that net names should contain.
        end_with : str
            String that net names should end with.

        Returns
        -------
        List[Net]
            List of matching nets.
        """
        matching_nets = []

        for net_name, net_obj in self.nets.items():
            net_name_lower = net_name.lower()

            # Check all criteria
            if start_with and not net_name_lower.startswith(start_with.lower()):
                continue
            if contain and contain.lower() not in net_name_lower:
                continue
            if end_with and not net_name_lower.endswith(end_with.lower()):
                continue

            matching_nets.append(net_obj)

        return matching_nets

    @staticmethod
    def _get_points_for_plot(my_net_points) -> Tuple[List[float], List[float]]:
        """Get points for plotting.

        Parameters
        ----------
        my_net_points : list
            List of points defining the net.

        Returns
        -------
        Tuple[List[float], List[float]]
            X and Y coordinates of the points.
        """
        x_coords = []
        y_coords = []

        for i, point in enumerate(my_net_points):
            if not point.is_arc:
                x_coords.append(point.x.value)
                y_coords.append(point.y.value)
            else:
                # Handle arc points
                arc_h = point.arc_height.value
                p1 = [my_net_points[i - 1].x.value, my_net_points[i - 1].y.value]

                if i + 1 < len(my_net_points):
                    p2 = [my_net_points[i + 1].X.ToDouble(), my_net_points[i + 1].Y.ToDouble()]
                else:
                    p2 = [my_net_points[0].X.ToDouble(), my_net_points[0].Y.ToDouble()]

                x_arc, y_arc = compute_arc_points(p1, p2, arc_h)
                x_coords.extend(x_arc)
                y_coords.extend(y_arc)

        return x_coords, y_coords
