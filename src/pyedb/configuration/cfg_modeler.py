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

from pyedb.dotnet.edb_core.edb_data.padstacks_data import (
    EDBPadstack,
    EDBPadstackInstance,
)


class CfgTrace:
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", "")
        self.layer = kwargs["layer"]
        self.path = kwargs["path"]
        self.width = kwargs["width"]
        self.net_name = kwargs.get("net_name", "")
        self.start_cap_style = kwargs.get("start_cap_style", "flat")
        self.end_cap_style = kwargs.get("end_cap_style", "flat")
        self.corner_style = kwargs.get("corner_style", "sharp")


class CfgModeler:
    """Manage configuration general settings."""

    def __init__(self, pedb, data):
        self._pedb = pedb
        self.traces = [CfgTrace(**i) for i in data.get("traces", [])]
        self.padstack_defs = data.get("padstack_definitions", [])
        self.padstack_instances = data.get("padstack_instances", [])
        self.planes = data.get("planes", [])

    def apply(self):
        if self.traces:
            for t in self.traces:
                self._pedb.modeler.create_trace(
                    path_list=t.path,
                    layer_name=t.layer,
                    net_name=t.net_name,
                    width=t.width,
                    start_cap_style=t.start_cap_style,
                    end_cap_style=t.end_cap_style,
                    corner_style=t.corner_style,
                )

        if self.padstack_defs:
            for p in self.padstack_defs:
                pdata = self._pedb._edb.Definition.PadstackDefData.Create()
                pdef = self._pedb._edb.Definition.PadstackDef.Create(self._pedb.active_db, p["name"])
                pdef.SetData(pdata)
                pdef = EDBPadstack(pdef, self._pedb.padstacks)
                pdef.properties = p

        if self.padstack_instances:
            for p in self.padstack_instances:
                p_inst = self._pedb.padstacks.place(
                    position=p["position"],
                    definition_name=p["definition"],
                )
                p_inst.properties = p
