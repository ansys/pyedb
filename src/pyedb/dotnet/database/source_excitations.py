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

from pyedb.dotnet.database.general import convert_py_list_to_net_list
from pyedb.generic.general_methods import generate_unique_name


class SourceExcitation:
    """Manage sources and excitations."""

    def __init__(self, pedb):
        self._pedb = pedb

    def create_padstack_instance_terminal(self, name="", padstack_instance_id=None, padstack_instance_name=None):
        pds = self._pedb.layout.find_padstack_instances(
            instance_id=padstack_instance_id,
            aedt_name=padstack_instance_name,
            component_name=None,
            component_pin_name=None,
        )
        if len(pds) == 0:
            raise ValueError(f"Padstack instance {padstack_instance_id} or {padstack_instance_name} not found.")
        else:
            pds = pds[0]

        _name = name if name else generate_unique_name(pds.aedt_name)
        terminal = pds.create_terminal(name=_name)
        if terminal.is_null:
            raise RuntimeError(
                f"Failed to create terminal. Input arguments: padstack_instance_id={padstack_instance_id}, "
                f"padstack_instance_name={padstack_instance_name}, name={name}."
            )
        return terminal

    def create_pin_group_terminal(self, pin_group, name=""):
        _name = name if name else generate_unique_name(pin_group)
        pg = self._pedb.siwave.pin_groups[pin_group]
        terminal = pg.create_terminal(name=_name)
        if terminal.is_null:
            raise RuntimeError(f"Failed to create terminal. Input arguments: pin_group={pin_group}, name={name}.")
        return terminal

    def create_point_terminal(self, x, y, layer, net, name=""):
        from pyedb.dotnet.database.cell.terminal.point_terminal import PointTerminal

        _name = name if name else f"point_{layer}_{x}_{y}"
        location = [x, y]
        point_terminal = PointTerminal(self._pedb)
        terminal = point_terminal.create(_name, net, location, layer)
        if terminal.is_null:
            raise RuntimeError(
                f"Failed to create terminal. Input arguments: x={x}, y={y}, layer={layer}, net={net}, name={name}."
            )
        return terminal

    def create_edge_terminal(self, primitive_name, x, y, name=""):
        from pyedb.dotnet.database.cell.terminal.edge_terminal import EdgeTerminal

        _name = name if name else f"{primitive_name}_{x}_{y}"

        pt = self._pedb.pedb_class.database.geometry.point_data.PointData.create_from_xy(self._pedb, x=x, y=y)
        primitive = self._pedb.layout.primitives_by_aedt_name[primitive_name]
        edge = self._pedb.core.Cell.Terminal.PrimitiveEdge.Create(primitive._edb_object, pt._edb_object)
        edge = convert_py_list_to_net_list(edge, self._pedb.core.Cell.Terminal.Edge)
        _terminal = self._pedb.core.Cell.Terminal.EdgeTerminal.Create(
            primitive._edb_object.GetLayout(),
            primitive._edb_object.GetNet(),
            _name,
            edge,
            isRef=False,
        )
        terminal = EdgeTerminal(self._pedb, _terminal)

        if terminal.is_null:
            raise RuntimeError(
                f"Failed to create terminal. Input arguments: primitive_name={primitive_name}, x={x}, y={y},"
                f" name={name}."
            )
        return terminal

    def create_bundle_terminal(self, terminals, name=""):
        from pyedb.dotnet.database.cell.terminal.bundle_terminal import BundleTerminal

        _name = name if name else f"{generate_unique_name('bundle')}"

        terminal = BundleTerminal.create(self._pedb, _name, terminals)
        bundle_term = terminal.terminals
        bundle_term[0].name = _name + ":T1"
        bundle_term[1].mame = _name + ":T2"
