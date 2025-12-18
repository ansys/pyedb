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

import re
from typing import Any, List, Optional, Union

from ansys.edb.core.database import ProductIdType as GrpcProductIdType

from pyedb.generic.general_methods import generate_unique_name
from pyedb.grpc.database.primitive.padstack_instance import PadstackInstance

# from pyedb.grpc.database.primitive.primitive import Primitive


class LayoutValidation:
    """Manages all layout validation capabilities"""

    def __init__(self, pedb: Any) -> None:
        self._pedb = pedb
        self._layout_instance = self._pedb.layout_instance

    def dc_shorts(self, net_list: Optional[Union[str, List[str]]] = None, fix: bool = False) -> List[List[str]]:
        """Find DC shorts on layout.

        Parameters
        ----------
        net_list : str or list[str], optional
            List of nets.
        fix : bool, optional
            If `True`, rename all the nets. (default)
            If `False`, only report dc shorts.

        Returns
        -------
        List[List[str, str]]
            [[net name, net name]].

        Examples
        --------
        >>> edb = Edb("edb_file")
        >>> # Find shorts without fixing
        >>> shorts = edb.layout_validation.dc_shorts()
        >>>
        >>> # Find and fix shorts on specific nets
        >>> fixed_shorts = edb.layout_validation.dc_shorts(net_list=["GND", "VCC"], fix=True)
        """
        if not net_list:
            net_list = list(self._pedb.nets.nets.keys())
        elif isinstance(net_list, str):
            net_list = [net_list]
        _objects_list = {}
        _padstacks_list = {}
        for prim in self._pedb.modeler.primitives:
            n_name = prim.net_name
            if n_name in _objects_list:
                _objects_list[n_name].append(prim)
            else:
                _objects_list[n_name] = [prim]
        for pad in list(self._pedb.padstacks.instances.values()):
            n_name = pad.net_name
            if n_name in _padstacks_list:
                _padstacks_list[n_name].append(pad)
            else:
                _padstacks_list[n_name] = [pad]
        dc_shorts = []
        all_shorted_nets = []
        for net in net_list:
            if net in all_shorted_nets:
                continue
            objs = []
            for i in _objects_list.get(net, []):
                objs.append(i)
            for i in _padstacks_list.get(net, []):
                objs.append(i)
            if not len(objs):
                self._pedb.nets[net].delete()
                continue

            connected_objs = objs[0].get_connected_objects()
            connected_objs.append(objs[0])
            net_dc_shorts = [obj for obj in connected_objs]
            all_shorted_nets.append(net)
            if net_dc_shorts:
                dc_nets = list(set([obj.net.name for obj in net_dc_shorts]))
                dc_nets = [i for i in dc_nets if i != net]
                for dc in dc_nets:
                    if dc:
                        dc_shorts.append([net, dc])
                        all_shorted_nets.append(dc)
                if fix:
                    temp = []
                    for i in net_dc_shorts:
                        temp.append(i.net.name)
                    temp_key = set(temp)
                    temp_count = {temp.count(i): i for i in temp_key}
                    temp_count = dict(sorted(temp_count.items()))
                    while True:
                        temp_name = list(temp_count.values()).pop()
                        if not temp_name.lower().startswith("unnamed"):
                            break
                        elif temp_name.lower():
                            break
                        elif len(temp) == 0:
                            break
                    rename_shorts = [i for i in net_dc_shorts if i.net.name != temp_name]
                    for i in rename_shorts:
                        i.net = self._pedb.nets.nets[temp_name]
        return dc_shorts

    def disjoint_nets(
        self,
        net_list: Optional[Union[str, List[str]]] = None,
        keep_only_main_net: bool = False,
        clean_disjoints_less_than: float = 0.0,
        order_by_area: bool = False,
        keep_disjoint_pins: bool = False,
    ) -> List[str]:
        """Find and fix disjoint nets from a given netlist.

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
        keep_disjoint_pins : bool, optional
            Whether if delete disjoints pins not connected to any other primitive or not. Default is ``False``.

        Returns
        -------
        List
            New nets created.

        Examples
        --------
        >>> edb = Edb("edb_file")
        >>> # Find disjoint nets on all nets
        >>> new_nets = edb.layout_validation.disjoint_nets()
        >>>
        >>> # Clean disjoints on specific nets with advanced options
        >>> cleaned = edb.layout_validation.disjoint_nets(
        ...     net_list=["GND"],
        ...     keep_only_main_net=True,
        ...     clean_disjoints_less_than=1e-6,
        ...     order_by_area=True
        ... ))
        """
        timer_start = self._pedb.logger.reset_timer()

        if not net_list:
            net_list = list(self._pedb.nets.keys())
        elif isinstance(net_list, str):
            net_list = [net_list]
        _objects_list = {}
        _padstacks_list = {}
        for prim in self._pedb.modeler.primitives:
            if not prim.net.is_null:
                n_name = prim.net.name
                if n_name in _objects_list:
                    _objects_list[n_name].append(prim)
                else:
                    _objects_list[n_name] = [prim]
        for pad in list(self._pedb.padstacks.instances.values()):
            if not pad.net.is_null:
                n_name = pad.net_name
                if n_name in _padstacks_list:
                    _padstacks_list[n_name].append(pad)
                else:
                    _padstacks_list[n_name] = [pad]
        new_nets = []
        disjoints_objects = []
        self._pedb.logger.reset_timer()
        for net in net_list:
            net_groups = []
            obj_dict = {}
            for i in _objects_list.get(net, []):
                obj_dict[i.id] = i
            for i in _padstacks_list.get(net, []):
                obj_dict[i.id] = i
            objs = list(obj_dict.values())
            l = len(objs)
            while l > 0:
                l1 = self._layout_instance.get_connected_objects(objs[0].layout_object_instance, False)
                l1.append(objs[0].id)
                repetition = False
                for net_list in net_groups:
                    if set(l1).intersection(net_list):
                        net_groups.append([i for i in l1 if i not in net_list])
                        repetition = True
                if not repetition:
                    net_groups.append(l1)
                objs = [i for i in objs if i.id not in l1]
                l = len(objs)
            if len(net_groups) > 1:

                def area_calc(elem):
                    sum = 0
                    for el in elem:
                        try:
                            if el.layout_obj.obj_type.value == 0:
                                if not el.is_void:
                                    sum += el.area()
                        except Exception as e:
                            self._pedb._logger.warning(
                                f"A(n) {type(e).__name__} error occurred while calculating area "
                                f"for element {elem} - Default value of 0 is used: {str(e)}"
                            )
                    return sum

                if order_by_area:
                    areas = [area_calc(i) for i in net_groups]
                    sorted_list = [x for _, x in sorted(zip(areas, net_groups), reverse=True)]
                else:
                    sorted_list = sorted(net_groups, key=len, reverse=True)
                for disjoints in sorted_list[1:]:
                    if keep_only_main_net:
                        for geo in disjoints:
                            try:
                                obj_dict[geo].delete()
                            except KeyError:
                                pass
                    elif len(disjoints) == 1 and (
                        clean_disjoints_less_than
                        and "area" in dir(obj_dict[disjoints[0]])
                        and obj_dict[disjoints[0]].area() < clean_disjoints_less_than
                    ):
                        try:
                            obj_dict[disjoints[0]].delete()
                        except KeyError:
                            pass
                    elif (
                        len(disjoints) == 1
                        and not keep_disjoint_pins
                        and isinstance(obj_dict[disjoints[0]], PadstackInstance)
                    ):
                        try:
                            obj_dict[disjoints[0]].delete()
                        except KeyError:
                            pass

                    else:
                        new_net_name = generate_unique_name(net, n=6)
                        net_obj = self._pedb.nets.find_or_create_net(new_net_name)
                        if net_obj:
                            new_nets.append(net_obj.name)
                            for geo in disjoints:
                                try:
                                    obj_dict[geo].net_name = net_obj.name
                                except KeyError:
                                    pass
                            disjoints_objects.extend(disjoints)
        self._pedb._logger.info("Found {} objects in {} new nets.".format(len(disjoints_objects), len(new_nets)))
        self._pedb._logger.info_timer("Disjoint Cleanup Completed.", timer_start)

        return new_nets

    def fix_self_intersections(self, net_list: Optional[Union[str, List[str]]] = None) -> bool:
        """Find and fix self intersections from a given netlist.

        Parameters
        ----------
        net_list : str, list, optional
            List of nets on which check disjoints. If `None` is provided then the algorithm will loop on all nets.

        Returns
        -------
        bool

        Examples
        --------
        >>> edb = Edb("edb_file")
        >>> # Fix self-intersections on all nets
        >>> edb.layout_validation.fix_self_intersections()
        >>>
        >>> # Fix self-intersections on specific nets
        >>> edb.layout_validation.fix_self_intersections(net_list=["RF_line"])
        """
        if not net_list:
            net_list = list(self._pedb.nets.nets.keys())
        elif isinstance(net_list, str):
            net_list = [net_list]
        new_prims = []
        for prim in self._pedb.modeler.polygons:
            if prim.net_name in net_list:
                new_prims.extend(prim.fix_self_intersections())
        if new_prims:
            self._pedb.logger.info("Self-intersections detected and removed.")
        else:
            self._pedb.logger.info("Self-intersection not found.")
        return True

    def illegal_net_names(self, fix: bool = False) -> None:
        """Find and fix illegal net names.

        Examples
        --------
        >>> edb = Edb("edb_file")
        >>> # Identify illegal net names
        >>> edb.layout_validation.illegal_net_names()
        >>>
        >>> # Find and automatically fix illegal names
        >>> edb.layout_validation.illegal_net_names(fix=True)
        """
        pattern = r"[\(\)\\\/:;*?<>\'\"|`~$]"

        nets = self._pedb.nets.nets

        renamed_nets = []
        for net, val in nets.items():
            if re.findall(pattern, net):
                renamed_nets.append(net)
                if fix:
                    new_name = re.sub(pattern, "_", net)
                    val.name = new_name

        self._pedb.logger.info("Found {} illegal net names.".format(len(renamed_nets)))
        return

    def illegal_rlc_values(self, fix: bool = False) -> List[str]:
        """Find and fix RLC illegal values.

        Examples
        --------
        >>> edb = Edb("edb_file")
        >>> # Identify components with illegal RLC values
        >>> bad_components = edb.layout_validation.illegal_rlc_values()
        >>>
        >>> # Automatically fix invalid inductor values
        >>> edb.layout_validation.illegal_rlc_values(fix=True)
        """
        inductors = self._pedb.components.inductors

        temp = []
        for k, v in inductors.items():
            model = v.component_property.model
            if not len(model.pin_pairs()):  # pragma: no cover
                temp.append(k)
                if fix:
                    v.rlc_values = [0, 1, 0]
        self._pedb.logger.info(f"Found {len(temp)} inductors have no value.")
        return temp

    def padstacks_no_name(self, fix: bool = False) -> None:
        """Identify and fix padstacks without names.

        Examples
        --------
        >>> edb = Edb("edb_file")
        >>> # Report unnamed padstacks
        >>> edb.layout_validation.padstacks_no_name()
        >>>
        >>> # Automatically assign names to unnamed padstacks
        >>> edb.layout_validation.padstacks_no_name(fix=True)
        """
        pds = list(self._pedb.layout.padstack_instances.values())
        counts = 0
        via_count = 1
        for obj in pds:
            name = obj.core.get_product_property(GrpcProductIdType.DESIGNER, 11)
            name = str(name).strip("'")
            if name == "":
                counts += 1
                if fix:
                    if not obj.component:
                        obj.set_product_property(GrpcProductIdType.DESIGNER, 11, f"Via{via_count}")
                        via_count = via_count + 1
                    else:
                        obj.set_product_property(
                            GrpcProductIdType.DESIGNER, 11, f"{obj.component.name}-{obj.component_pin}"
                        )
        self._pedb.logger.info(f"Found {counts}/{len(pds)} padstacks have no name.")
