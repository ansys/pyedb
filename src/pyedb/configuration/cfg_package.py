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

from pyedb.dotnet.edb_core.definition.package_def import PackageDef


class CfgPackage:
    """Configuration package class."""

    def __init__(self, pdata, package_dict=None):
        self._pedb = pdata._pedb
        self._package_dict = package_dict
        self.name = None
        self.component_definition = None
        self.maximum_power = None
        self.therm_cond = None
        self.theta_jb = None
        self.theta_jc = None
        self.height = None
        self.heatsink = CfgHeatSink(self._pedb)
        self.apply_to_all = None
        self.components = []
        self.extent_bounding_box = None
        if self._package_dict:
            self.name = self._package_dict.get("name", None)
            self.component_definition = self._package_dict.get("component_definition", None)
            self.maximum_power = self._package_dict.get("maximum_power", None)
            self.therm_cond = self._package_dict.get("therm_cond", None)
            self.theta_jb = self._package_dict.get("theta_jb", None)
            self.theta_jc = self._package_dict.get("theta_jc", None)
            self.height = self._package_dict.get("height", None)
            heat_sink_dict = self._package_dict.get("heatsink", None)
            if isinstance(heat_sink_dict, dict):
                self.heatsink = CfgHeatSink(self._pedb, heat_sink_dict)
            self.apply_to_all = self._package_dict.get("apply_to_all", None)
            self.components = self._package_dict.get("components", [])
            self.extent_bounding_box = self._package_dict.get("extent_bounding_box", None)

    def apply(self):
        if self.name in self._pedb.definitions.package:
            self._pedb.definitions.package[self.name].delete()
        if self.extent_bounding_box:
            package_def = PackageDef(self._pedb, name=self.name, extent_bounding_box=self.extent_bounding_box)
        else:
            package_def = PackageDef(self._pedb, name=self.name, component_part_name=self.component_definition)
        package_def.maximum_power = self.maximum_power
        package_def.therm_cond = self.therm_cond
        package_def.theta_jb = self.theta_jb
        package_def.theta_jc = self.theta_jc
        package_def.height = self.height

        if self.heatsink:
            package_def.set_heatsink(
                self.heatsink.fin_base_height,
                self.heatsink.fin_height,
                self.heatsink.fin_orientation.name.lower(),
                self.heatsink.fin_spacing,
                self.heatsink.fin_thickness,
            )
        comp_def = self._pedb.definitions.component[self.component_definition]
        comp_list = dict()
        if self.apply_to_all:
            comp_list.update(
                {refdes: comp for refdes, comp in comp_def.components.items() if refdes not in self.components}
            )
        else:
            comp_list.update(
                {refdes: comp for refdes, comp in comp_def.components.items() if refdes in self.components}
            )
        for _, i in comp_list.items():
            i.package_def = self.name


class CfgHeatSink:
    """Configuration heat sink class."""

    def __init__(self, pedb, heat_sink_dict=None):
        self._pedb = pedb
        self._heat_sink_dict = heat_sink_dict
        self.fin_base_height = None
        self.fin_height = None
        self.fin_orientation = None
        self.fin_spacing = None
        self.fin_thickness = None
        if self._heat_sink_dict:
            self.fin_base_height = self._heat_sink_dict.get("fin_base_height", None)
            self.fin_height = self._heat_sink_dict.get("fin_height", None)
            fin_orientation = self._heat_sink_dict.get("fin_orientation", None)
            if fin_orientation:
                self.__map_fin_orientation(fin_orientation)
            self.fin_spacing = self._heat_sink_dict.get("fin_spacing", None)
            self.fin_thickness = self._heat_sink_dict.get("fin_thickness", None)

    def __map_fin_orientation(self, fin_orientation):
        if fin_orientation == "x_oriented":
            self.fin_orientation = FinOrientation.X_ORIENTED
        elif fin_orientation == "y_oriented":
            self.fin_orientation = FinOrientation.Y_ORIENTED
        elif fin_orientation == "other_oriented":
            self.fin_orientation = FinOrientation.OTHER_ORIENTED


class FinOrientation(Enum):
    X_ORIENTED = 0
    Y_ORIENTED = 1
    OTHER_ORIENTED = 2
