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

import re

from pyedb.dotnet.database.edb_data.padstacks_data import EDBPadstackInstance
from pyedb.dotnet.database.edb_data.primitives_data import Primitive
from pyedb.generic.general_methods import generate_unique_name


class LayoutValidation:
    """Manages all layout validation capabilities"""

    def __init__(self, pedb):
        self._pedb = pedb

    def dc_shorts(self, net_list=None, fix=False):
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
        >>> dc_shorts = edb.layout_validation.dc_shorts()

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
                    rename_shorts = [i for i in net_dc_shorts if i._edb_object.GetNet().GetName() != temp_name]
                    for i in rename_shorts:
                        i._edb_object.SetNet(self._pedb.nets.nets[temp_name].net_obj)
                        # i.net = temp_name
        return dc_shorts

    def disjoint_nets(
        self,
        net_list=None,
        keep_only_main_net=False,
        clean_disjoints_less_than=0.0,
        order_by_area=False,
        keep_disjoint_pins=False,
    ):
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

        >>> renamed_nets = edb.layout_validation.disjoint_nets(["GND","Net2"])
        """
        timer_start = self._pedb._logger.reset_timer()

        if not net_list:
            net_list = list(self._pedb.nets.keys())
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
        for pad in list(self._pedb.layout.padstack_instances):
            n_name = pad.net_name
            if n_name in _padstacks_list:
                _padstacks_list[n_name].append(pad)
            else:
                _padstacks_list[n_name] = [pad]
        new_nets = []
        disjoints_objects = []
        self._pedb._logger.reset_timer()
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
                l1 = objs[0].get_connected_object_id_set()
                l1.append(objs[0].id)
                repetition = False
                for id_by_net in net_groups:
                    if set(l1).intersection(id_by_net):
                        net_groups.append([i for i in l1 if i not in id_by_net])
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
                            if isinstance(obj_dict[el], Primitive):
                                if not obj_dict[el].is_void:
                                    sum += obj_dict[el].area()
                        except:
                            pass
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
                        and isinstance(obj_dict[disjoints[0]], EDBPadstackInstance)
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

    def fix_self_intersections(self, net_list=None):
        """Find and fix self intersections from a given netlist.

        Parameters
        ----------
        net_list : str, list, optional
            List of nets on which check disjoints. If `None` is provided then the algorithm will loop on all nets.

        Returns
        -------
        bool
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
            self._pedb._logger.info("Self-intersections detected and removed.")
        else:
            self._pedb._logger.info("Self-intersection not found.")
        return True

    def illegal_net_names(self, fix=False):
        """Find and fix illegal net names."""
        pattern = r"[\(\)\\\/:;*?<>\'\"|`~$]"

        nets = self._pedb.nets.nets

        renamed_nets = []
        for net, val in nets.items():
            if re.findall(pattern, net):
                renamed_nets.append(net)
                if fix:
                    new_name = re.sub(pattern, "_", net)
                    val.name = new_name

        self._pedb._logger.info("Found {} illegal net names.".format(len(renamed_nets)))
        return

    def illegal_rlc_values(self, fix=False):
        """Find and fix RLC illegal values."""

        for name, objs in {
            "inductors": self._pedb.components.inductors,
            "resistors": self._pedb.components.resistors,
            "capacitors": self._pedb.components.capacitors,
        }.items():
            temp = []
            for k, v in objs.items():
                componentProperty = v.edbcomponent.GetComponentProperty()
                model = componentProperty.GetModel().Clone()
                pinpairs = model.PinPairs

                if not len(list(pinpairs)):  # pragma: no cover
                    temp.append(k)
                    if fix:
                        v.rlc_values = [0, 1, 0]

            self._pedb._logger.info(f"Found {len(temp)} {name} have no value.")
        return

    def padstacks_no_name(self, fix=False):
        """Find and fix padstacks without aedt_name."""
        pds = self._pedb.layout.padstack_instances
        counts = 0
        for obj in pds:
            if obj.aedt_name == "":
                counts += 1
                if fix:
                    obj.aedt_name = f"via_{obj.id}"
        self._pedb._logger.info(f"Found {counts}/{len(pds)} padstacks have no name.")
