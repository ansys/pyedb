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

"""
This module contains these classes: `EdbLayout` and `Shape`.
"""
from pyedb.dotnet.edb_core.cell.primitive import Bondwire
from pyedb.dotnet.edb_core.edb_data.nets_data import EDBNetsData
from pyedb.dotnet.edb_core.edb_data.padstacks_data import EDBPadstackInstance
from pyedb.dotnet.edb_core.edb_data.sources import PinGroup
from pyedb.dotnet.edb_core.general import convert_py_list_to_net_list
from pyedb.dotnet.edb_core.layout import EdbLayout


class Layout(EdbLayout):
    def __init__(self, pedb, edb_object):
        super().__init__(pedb)
        self._edb_object = edb_object

    @property
    def nets(self):
        """Nets.

        Returns
        -------
        dict[str, :class:`pyedb.dotnet.edb_core.edb_data.nets_data.EDBNetsData`]
            Dictionary of nets.
        """

        temp = {}
        for net in self._edb_object.Nets:
            n = EDBNetsData(net, self._pedb)
            temp[n.name] = n
        return temp

    @property
    def bondwires(self):
        """Bondwires.

        Returns
        -------
        list :
            List of bondwires.
        """
        return [
            Bondwire(self._pedb, i)
            for i in self._edb_object.Primitives
            if i.GetPrimitiveType().ToString() == "Bondwire"
        ]

    @property
    def padstack_instances(self):
        """Get all padstack instances in a list."""
        return [EDBPadstackInstance(i, self._pedb) for i in self._edb_object.PadstackInstances]

    def create_bondwire(
        self,
        definition_name,
        placement_layer,
        width,
        material,
        start_layer_name,
        start_x,
        start_y,
        end_layer_name,
        end_x,
        end_y,
        net,
        bondwire_type="jedec4",
    ):
        """Create a bondwire object.

        Parameters
        ----------
        bondwire_type : :class:`BondwireType`
            Type of bondwire: kAPDBondWire or kJDECBondWire types.
        definition_name : str
            Bondwire definition name.
        placement_layer : str
            Layer name this bondwire will be on.
        width : :class:`Value <ansys.edb.utility.Value>`
            Bondwire width.
        material : str
            Bondwire material name.
        start_layer_name : str
            Name of start layer.
        start_x : :class:`Value <ansys.edb.utility.Value>`
            X value of start point.
        start_y : :class:`Value <ansys.edb.utility.Value>`
            Y value of start point.
        end_layer_name : str
            Name of end layer.
        end_x : :class:`Value <ansys.edb.utility.Value>`
            X value of end point.
        end_y : :class:`Value <ansys.edb.utility.Value>`
            Y value of end point.
        net : str or :class:`Net <ansys.edb.net.Net>` or None
            Net of the Bondwire.

        Returns
        -------
        :class:`pyedb.dotnet.edb_core.dotnet.primitive.BondwireDotNet`
            Bondwire object created.
        """
        return Bondwire(
            pedb=self._pedb,
            bondwire_type=bondwire_type,
            definition_name=definition_name,
            placement_layer=placement_layer,
            width=self._pedb.edb_value(width),
            material=material,
            start_layer_name=start_layer_name,
            start_x=self._pedb.edb_value(start_x),
            start_y=self._pedb.edb_value(start_y),
            end_layer_name=end_layer_name,
            end_x=self._pedb.edb_value(end_x),
            end_y=self._pedb.edb_value(end_y),
            net=self.nets[net]._edb_object,
        )

    def find_object_by_id(self, value: int):
        """Find a Connectable object by Database ID.

        Parameters
        ----------
        value : int
        """
        obj = self._pedb._edb.Cell.Connectable.FindById(self._edb_object, value)
        if obj.GetObjType().ToString() == "PadstackInstance":
            return EDBPadstackInstance(obj, self._pedb)

    def create_pin_group(self, name: str, pins_by_id: list[int] = None, pins_by_aedt_name: list[str] = None):
        """Create a PinGroup.

        Parameters
        name : str,
            Name of the PinGroup.
        pins_by_id : list[int] or None
            List of pins by ID.
        pins_by_aedt_name : list[str] or None
            List of pins by AEDT name.
        """
        pins = []

        if pins_by_id is not None:
            for p in pins_by_id:
                pins.append(self.find_object_by_id(p._edb_object))
        else:
            p_inst = self.padstack_instances
            while True:
                p = p_inst.pop(0)
                if p.aedt_name in pins_by_aedt_name:
                    pins.append(p._edb_object)
                    pins_by_aedt_name.remove(p.aedt_name)
                if len(pins_by_aedt_name) == 0:
                    break

        obj = self._edb.cell.hierarchy.pin_group.Create(self._edb_object, name, convert_py_list_to_net_list(pins))
        return PinGroup(name, obj, self._pedb)
