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
        layout : :class:`Layout <ansys.edb.layout.Layout>`
            Layout this bondwire will be in.
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
        start_context : :class:`CellInstance <ansys.edb.hierarchy.CellInstance>`
            Start context: None means top level.
        start_layer_name : str
            Name of start layer.
        start_x : :class:`Value <ansys.edb.utility.Value>`
            X value of start point.
        start_y : :class:`Value <ansys.edb.utility.Value>`
            Y value of start point.
        end_context : :class:`CellInstance <ansys.edb.hierarchy.CellInstance>`
            End context: None means top level.
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
