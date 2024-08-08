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


from enum import Enum


class CfgPadstacks:
    """Padstack data class."""

    def __init__(self, pdata, padstack_dict=None):
        self._pedb = pdata._pedb
        self.definitions = []
        self.instances = []
        self._padstack_dict = padstack_dict
        if self._padstack_dict:
            if self._padstack_dict.get("definitions", ""):
                self._definitions_dict = self._padstack_dict.get("definitions", "")
                self.definitions = [Definition(pdata, definition) for definition in self._definitions_dict]
            if self._padstack_dict.get("instances", None):
                self._instances_dict = self._padstack_dict.get("instances", "")
                self.instances = [Instance(pdata, inst) for inst in self._instances_dict]

    def apply(self):
        """Apply padstack definition and instances on layout."""
        for definition in self.definitions:
            definition.apply()
        for instance in self.instances:
            instance.apply()


class Definition:
    """Padstack definition data class."""

    def __init__(self, pdata, definition_dict):
        self._pedb = pdata._pedb
        self._definition_dict = definition_dict
        self.name = self._definition_dict.get("name", None)
        self.hole_diameter = self._definition_dict.get("hole_diameter", None)
        self.hole_plating_thickness = self._definition_dict.get("hole_plating_thickness", None)
        self.hole_material = self._definition_dict.get("hole_material", None)
        self.hole_range = self._definition_dict.get("hole_range", None)

    def apply(self):
        """Apply padstack definition on layout."""
        padstack_defs = self._pedb.padstacks.definitions
        pdef = padstack_defs[self.name]
        if self.hole_diameter:
            pdef.hole_diameter = self.hole_diameter
        if self.hole_plating_thickness:
            pdef.hole_plating_thickness = self.hole_plating_thickness
        if self.hole_material:
            pdef.material = self.hole_material
        if self.hole_range:
            pdef.hole_range = self.hole_range


class Instance:
    """Instance data class."""

    def __init__(self, pdata, instances_dict):
        self._pedb = pdata._pedb
        self._instances_dict = instances_dict
        self.name = self._instances_dict.get("name", "")
        self.backdrill_top = None
        self.backdrill_bottom = None
        self._update_backdrill()

    def _update_backdrill(self):
        if "backdrill_top" in self._instances_dict:
            self.backdrill_top = self.BackDrill()
            self.backdrill_top.type = self.backdrill_top.BackDrillType.TOP
            backdrill_top_dict = self._instances_dict["backdrill_top"]
            self.backdrill_top.drill_to_layer = backdrill_top_dict.get("drill_to_layer", "")
            self.backdrill_top.drill_diameter = backdrill_top_dict.get("drill_diameter", "")
            self.backdrill_top.stub_length = backdrill_top_dict.get("stub_length", "")
        if "backdrill_bottom" in self._instances_dict:
            self.backdrill_bottom = self.BackDrill()
            backdrill_bottom_dict = self._instances_dict["backdrill_bottom"]
            self.backdrill_bottom.drill_to_layer = backdrill_bottom_dict.get("drill_to_layer", "")
            self.backdrill_bottom.drill_diameter = backdrill_bottom_dict.get("drill_diameter", "")
            self.backdrill_bottom.stub_length = backdrill_bottom_dict.get("stub_length", "")

    class BackDrill:
        """Backdrill data class."""

        def __init__(self):
            self.type = self.BackDrillType.BOTTOM
            self.drill_to_layer = ""
            self.drill_diameter = ""
            self.stub_length = ""

        class BackDrillType(Enum):
            TOP = 0
            BOTTOM = 1

    def apply(self):
        """Apply padstack instance on layout."""
        padstack_instances = self._pedb.padstacks.instances_by_name
        inst = padstack_instances[self.name]
        if self.backdrill_top:
            inst.set_backdrill_top(
                self.backdrill_top.drill_to_layer, self.backdrill_top.drill_diameter, self.backdrill_top.stub_length
            )
        if self.backdrill_bottom:
            inst.set_backdrill_bottom(
                self.backdrill_bottom.drill_to_layer,
                self.backdrill_bottom.drill_diameter,
                self.backdrill_bottom.stub_length,
            )
