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
                self.definitions = [Definition(**definition) for definition in self._definitions_dict]
            if self._padstack_dict.get("instances", None):
                self._instances_dict = self._padstack_dict.get("instances", "")
                self.instances = [Instance(pdata, inst) for inst in self._instances_dict]

    def apply(self):
        """Apply padstack definition and instances on layout."""
        padstack_defs_layout = self._pedb.padstacks.definitions
        for pdef in self.definitions:
            pdef_layout = padstack_defs_layout[pdef.name]
            if pdef.hole_diameter:
                pdef_layout.hole_diameter = pdef.hole_diameter
            if pdef.hole_plating_thickness:
                pdef_layout.hole_plating_thickness = pdef.hole_plating_thickness
            if pdef.hole_material:
                pdef_layout.material = pdef.hole_material
            if pdef.hole_range:
                pdef_layout.hole_range = pdef.hole_range
            if pdef.pads:
                for p in pdef.pads:
                    pad = pdef_layout.pad_by_layer[p.layer]
                    pad.shape = p.SHAPE_MAPPING[p.shape]
                    pad.diameter = p.diameter
        for instance in self.instances:
            instance.apply()


class CfgPad:
    SHAPE_MAPPING = {
        "circle": "Circle",
        "square": "Square",
        "rectangle": "Rectangle",
        "oval": "Oval",
        "bullet": "Bullet",
        "nsidedpolygon": "NSidedPolygon",
        "polygon": "Polygon",
        "round45": "Round45",
        "round90": "Round90",
        "square45": "Square45",
        "square90": "Square90",
    }

    def __init__(self, **kwargs):
        self.layer = kwargs["layer"]
        self.shape = kwargs["shape"]
        self.diameter = kwargs["diameter"]


class Definition:
    """Padstack definition data class."""

    def __init__(self, **kwargs):
        self.name = kwargs.get("name", None)
        self.hole_diameter = kwargs.get("hole_diameter", None)
        self.hole_plating_thickness = kwargs.get("hole_plating_thickness", None)
        self.hole_material = kwargs.get("hole_material", None)
        self.hole_range = kwargs.get("hole_range", None)
        self.pads = [CfgPad(**i) for i in kwargs.get("pads", [])]


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
