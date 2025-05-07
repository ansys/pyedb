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

from pyedb.configuration.cfg_components import CfgComponent
from pyedb.configuration.cfg_padstacks import CfgPadstackDefinition, CfgPadstackInstance
from pyedb.dotnet.database.edb_data.padstacks_data import EDBPadstack


class CfgTrace:
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", "")
        self.layer = kwargs["layer"]
        self.path = kwargs["path"]
        self.width = kwargs["width"]
        self.net_name = kwargs.get("net_name", "")
        self.start_cap_style = kwargs.get("start_cap_style", "round")
        self.end_cap_style = kwargs.get("end_cap_style", "round")
        self.corner_style = kwargs.get("corner_style", "sharp")


class CfgPlane:
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", "")
        self.layer = kwargs["layer"]
        self.net_name = kwargs.get("net_name", "")
        self.type = kwargs.get("type", "rectangle")

        # rectangle
        self.lower_left_point = kwargs.get("lower_left_point", [])
        self.upper_right_point = kwargs.get("upper_right_point", [])
        self.corner_radius = kwargs.get("corner_radius", 0)
        self.rotation = kwargs.get("rotation", 0)
        self.voids = kwargs.get("voids", [])

        # polygon
        self.points = kwargs.get("points", [])


class CfgModeler:
    """Manage configuration general settings."""

    class Grpc:
        def __init__(self, parent):
            self.parent = parent
            self._pedb = parent._pedb

        def set_parameter_to_edb(self):
            from ansys.edb.core.definition.padstack_def import (
                PadstackDef as GrpcPadstackDef,
            )
            from ansys.edb.core.definition.padstack_def_data import (
                PadstackDefData as GrpcPadstackDefData,
            )

            from pyedb.grpc.database.definition.padstack_def import PadstackDef

            if self.parent.traces:
                for t in self.parent.traces:
                    obj = self._pedb.modeler.create_trace(
                        path_list=t.path,
                        layer_name=t.layer,
                        net_name=t.net_name,
                        width=t.width,
                        start_cap_style=t.start_cap_style,
                        end_cap_style=t.end_cap_style,
                        corner_style=t.corner_style,
                    )
                    obj.aedt_name = t.name

            if self.parent.padstack_defs:
                for p in self.parent.padstack_defs:
                    pdata = GrpcPadstackDefData.create()
                    pdef = GrpcPadstackDef.create(self._pedb.active_db, p.name)
                    pdef.data = pdata
                    pdef = PadstackDef(self._pedb, pdef)
                    p.pyedb_obj = pdef
                    p.api.set_parameters_to_edb()

            if self.parent.padstack_instances:
                for p in self.parent.padstack_instances:
                    p_inst = self._pedb.padstacks.place(
                        via_name=p.name,
                        net_name=p.net_name,
                        position=p.position,
                        definition_name=p.definition,
                    )
                    p.pyedb_obj = p_inst
                    p.api.set_parameters_to_edb()

            if self.parent.planes:
                for p in self.parent.planes:
                    if p.type == "rectangle":
                        obj = self._pedb.modeler.create_rectangle(
                            layer_name=p.layer,
                            net_name=p.net_name,
                            lower_left_point=p.lower_left_point,
                            upper_right_point=p.upper_right_point,
                            corner_radius=p.corner_radius,
                            rotation=p.rotation,
                        )
                        obj.aedt_name = p.name
                    elif p.type == "polygon":
                        obj = self._pedb.modeler.create_polygon(
                            points=p.points, layer_name=p.layer, net_name=p.net_name
                        )
                        obj.aedt_name = p.name

                    for v in p.voids:
                        for i in self._pedb.layout.primitives:
                            if i.aedt_name == v:
                                self._pedb.modeler.add_void(obj, i)

            if self.parent.components:
                pedb_p_inst = self._pedb.padstacks.instances_by_name
                for c in self.parent.components:
                    obj = self._pedb.components.create(
                        [pedb_p_inst[i] for i in c.pins],
                        component_name=c.reference_designator,
                        placement_layer=c.placement_layer,
                        component_part_name=c.definition,
                    )
                    c.pyedb_obj = obj
                    c.api.set_parameters_to_edb()

        def delete_primitives(self):
            primitives = self._pedb.layout.find_primitive(**self.parent.primitives_to_delete)
            for i in primitives:
                i.delete()

    class DotNet(Grpc):
        def __init__(self, parent):
            super().__init__(parent)

        def set_parameter_to_edb(self):
            if self.parent.traces:
                for t in self.parent.traces:
                    obj = self._pedb.modeler.create_trace(
                        path_list=t.path,
                        layer_name=t.layer,
                        net_name=t.net_name,
                        width=t.width,
                        start_cap_style=t.start_cap_style,
                        end_cap_style=t.end_cap_style,
                        corner_style=t.corner_style,
                    )
                    obj.aedt_name = t.name

            if self.parent.padstack_defs:
                for p in self.parent.padstack_defs:
                    pdata = self._pedb._edb.Definition.PadstackDefData.Create()
                    pdef = self._pedb._edb.Definition.PadstackDef.Create(self._pedb.active_db, p.name)
                    pdef.SetData(pdata)
                    pdef = EDBPadstack(pdef, self._pedb.padstacks)
                    p.pyedb_obj = pdef
                    p.api.set_parameters_to_edb()

            if self.parent.padstack_instances:
                for p in self.parent.padstack_instances:
                    p_inst = self._pedb.padstacks.place(
                        via_name=p.name,
                        net_name=p.net_name,
                        position=p.position,
                        definition_name=p.definition,
                        rotation=p.rotation if p.rotation is not None else 0,
                    )
                    p.pyedb_obj = p_inst
                    p.api.set_parameters_to_edb()

            if self.parent.planes:
                for p in self.parent.planes:
                    if p.type == "rectangle":
                        obj = self._pedb.modeler.create_rectangle(
                            layer_name=p.layer,
                            net_name=p.net_name,
                            lower_left_point=p.lower_left_point,
                            upper_right_point=p.upper_right_point,
                            corner_radius=p.corner_radius,
                            rotation=p.rotation,
                        )
                        obj.aedt_name = p.name
                    elif p.type == "polygon":
                        obj = self._pedb.modeler.create_polygon(
                            main_shape=p.points, layer_name=p.layer, net_name=p.net_name
                        )
                        obj.aedt_name = p.name

                    for v in p.voids:
                        for i in self._pedb.layout.primitives:
                            if i.aedt_name == v:
                                self._pedb.modeler.add_void(obj, i)

            if self.parent.components:
                pedb_p_inst = self._pedb.padstacks.instances_by_name
                for c in self.parent.components:
                    obj = self._pedb.components.create(
                        [pedb_p_inst[i] for i in c.pins],
                        component_name=c.reference_designator,
                        placement_layer=c.placement_layer,
                        component_part_name=c.definition,
                    )
                    c.pyedb_obj = obj
                    c.api.set_parameters_to_edb()

    def __init__(self, pedb, data):
        self._pedb = pedb
        if self._pedb.grpc:
            self.api = self.Grpc(self)
        else:
            self.api = self.DotNet(self)
        self.traces = [CfgTrace(**i) for i in data.get("traces", [])]
        self.padstack_defs = [
            CfgPadstackDefinition(self._pedb, None, **i) for i in data.get("padstack_definitions", [])
        ]
        self.padstack_instances = [
            CfgPadstackInstance(self._pedb, None, **i) for i in data.get("padstack_instances", [])
        ]
        self.planes = [CfgPlane(**i) for i in data.get("planes", [])]
        self.components = [CfgComponent(self._pedb, None, **i) for i in data.get("components", [])]
        self.primitives_to_delete = data.get("primitives_to_delete", {"layer_name": [], "name": [], "net_name": []})

    def apply(self):
        self.api.set_parameter_to_edb()
        self.api.delete_primitives()
