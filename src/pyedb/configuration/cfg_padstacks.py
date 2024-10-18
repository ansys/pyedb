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

from pyedb.configuration.cfg_common import CfgBase


class CfgPadstacks:
    """Padstack data class."""

    def __init__(self, pedb, padstack_dict=None):
        self._pedb = pedb
        self.definitions = []
        self.instances = []
        if padstack_dict:
            for pdef in padstack_dict.get("definitions", []):
                self.definitions.append(Definition(**pdef))
            for inst in padstack_dict.get("instances", []):
                self.instances.append(Instance(**inst))

    def apply(self):
        """Apply padstack definition and instances on layout."""
        if self.definitions:
            padstack_defs_layout = self._pedb.padstacks.definitions
            for pdef in self.definitions:
                pdef_layout = padstack_defs_layout[pdef.name]
                pdef_layout.set_properties(**pdef.get_attributes())
        if self.instances:
            instances_layout = self._pedb.padstacks.instances_by_name
            for inst in self.instances:
                inst_layout = instances_layout[inst.name]
                data = dict()
                data["backdrill_parameters"] = inst.backdrill_parameters
                data["hole_override_enabled"] = inst.hole_override_enabled
                data["hole_override_diameter"] = inst.hole_override_diameter
                inst_layout.properties = data

    def get_data_from_db(self):
        self.definitions = []
        for pdef_name, pdef in self._pedb.padstacks.definitions.items():
            self.definitions.append(
                Definition(
                    name=pdef_name,
                    hole_plating_thickness=pdef.hole_plating_thickness,
                    hole_material=pdef.material,
                    hole_range=pdef.hole_range,
                    pad_parameters=pdef.pad_parameters,
                    hole_parameters=pdef.hole_parameters,
                )
            )
        data = {}
        definitions = []
        for i in self.definitions:
            definitions.append(i.get_attributes())
        data["definitions"] = definitions

        for obj in self._pedb.layout.padstack_instances:
            temp = obj.properties
            self.instances.append(
                Instance(
                    name=temp["name"],
                    definition=temp["definition"],
                    backdrill_parameters=temp["backdrill_parameters"],
                    id=temp["id"],
                    position=temp["position"],
                    rotation=temp["rotation"],
                    hole_override_enabled=temp["hole_override_enabled"],
                    hole_override_diameter=temp["hole_override_diameter"],
                )
            )
        instances = []
        for i in self.instances:
            instances.append(i.get_attributes("id"))
        data["instances"] = instances
        return data


class Definition(CfgBase):
    """Padstack definition data class."""

    def __init__(self, **kwargs):
        self.name = kwargs.get("name", None)
        self.hole_plating_thickness = kwargs.get("hole_plating_thickness", None)
        self.material = kwargs.get("hole_material", None)
        self.hole_range = kwargs.get("hole_range", None)
        self.pad_parameters = kwargs.get("pad_parameters", None)
        self.hole_parameters = kwargs.get("hole_parameters", None)


class Instance(CfgBase):
    """Instance data class."""

    def __init__(self, **kwargs):
        self.name = kwargs["name"]
        self.definition = kwargs.get("definition", None)
        self.backdrill_parameters = kwargs.get("backdrill_parameters", None)
        self.id = kwargs.get("id", None)
        self.position = kwargs.get("position", [])
        self.rotation = kwargs.get("rotation", None)
        self.hole_override_enabled = kwargs.get("hole_override_enabled", None)
        self.hole_override_diameter = kwargs.get("hole_override_diameter", None)
