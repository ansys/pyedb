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


class CfgOperations:
    def __init__(self, pdata, operation_dict=None):
        self._pedb = pdata._pedb
        self.cutout = None
        if operation_dict:
            self._operation_dict = operation_dict
            cutout_dict = self._operation_dict.get("cutout", None)
            if isinstance(cutout_dict, dict):
                self.cutout = CfgCutout(self._pedb, cutout_dict)

    def apply(self):
        if self.cutout:
            return self.cutout.apply()


class CfgCutoutExtentType(Enum):
    BBOX = 0
    CONFORMAL = 1
    CONVEX_HULL = 2


class CfgCutout:
    def __init__(self, pedb, cutout_dict=None):
        self._pedb = pedb
        self._cutout_dict = cutout_dict
        self.signal_list = []
        self.reference_list = []
        self.extent_type = None
        self.expansion_size = None
        self.use_round_corner = None
        self.output_aedb_path = None
        self.open_cutout_at_end = None
        self.use_pyaedt_cutout = None
        self.number_of_threads = 4
        self.use_pyaedt_extent_computing = True
        self.extent_defeature = None
        self.remove_single_pin_components = None
        self.custom_extent = None
        self.custom_extent_units = None
        self.include_partial_instances = None
        self.keep_voids = True
        self.check_terminals = None
        self.include_pingroups = None
        self.expansion_factor = None
        self.maximum_iterations = None
        self.preserve_components_with_model = None
        self.simple_pad_check = None
        self.keep_lines_as_path = None
        if self._cutout_dict:
            self.__update()

    def __update(self):
        self.signal_list = self._cutout_dict.get("signal_list", [])
        self.reference_list = self._cutout_dict.get("reference_list", [])
        self.__map_extent_type(self._cutout_dict.get("extent_type", None))
        self.expansion_size = self._cutout_dict.get("expansion_size", None)
        self.use_round_corner = self._cutout_dict.get("use_round_corner", None)
        self.output_aedb_path = self._cutout_dict.get("output_aedb_path", None)
        self.open_cutout_at_end = self._cutout_dict.get("open_cutout_at_end", None)
        self.use_pyaedt_cutout = self._cutout_dict.get("use_pyaedt_cutout", None)
        self.number_of_threads = self._cutout_dict.get("use_pyaedt_cutout", 4)
        self.use_pyaedt_extent_computing = self._cutout_dict.get("use_pyaedt_extent_computing", None)
        self.extent_defeature = self._cutout_dict.get("extent_defeature", None)
        self.remove_single_pin_components = self._cutout_dict.get("remove_single_pin_components", None)
        self.custom_extent = self._cutout_dict.get("custom_extent", None)
        self.custom_extent_units = self._cutout_dict.get("custom_extent_units", None)
        self.include_partial_instances = self._cutout_dict.get("include_partial_instances", None)
        self.keep_voids = self._cutout_dict.get("keep_voids", None)
        self.check_terminals = self._cutout_dict.get("check_terminals", None)
        self.include_pingroups = self._cutout_dict.get("include_pingroups", None)
        self.expansion_factor = self._cutout_dict.get("expansion_factor", None)
        self.maximum_iterations = self._cutout_dict.get("maximum_iterations", None)

    def __map_extent_type(self, extent_type):
        if extent_type == "ConvexHull":
            self.extent_type = CfgCutoutExtentType.CONVEX_HULL
        elif extent_type == "BBox":
            self.extent_type = CfgCutoutExtentType.BBOX
        elif extent_type == "Conformal":
            self.extent_type = CfgCutoutExtentType.CONFORMAL
        elif extent_type is None:
            return
        else:
            self.extent_type = CfgCutoutExtentType.CONVEX_HULL

    def apply(self):
        cutout_dict = self.__dict__
        edb = self._pedb
        del cutout_dict["_pedb"]
        del cutout_dict["_cutout_dict"]
        if cutout_dict["extent_type"] == CfgCutoutExtentType.CONVEX_HULL:
            cutout_dict["extent_type"] = "ConvexHull"
        elif cutout_dict["extent_type"] == CfgCutoutExtentType.CONFORMAL:
            cutout_dict["extent_type"] = "Conformal"
        elif cutout_dict["extent_type"] == CfgCutoutExtentType.BBOX:
            cutout_dict["extent_type"] = "BBox"
        return edb.cutout(**cutout_dict)
