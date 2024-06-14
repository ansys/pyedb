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


class CfgCutout(CfgBase):
    def __init__(self, **kwargs):
        self.signal_list = kwargs.get("signal_list")
        self.reference_list = kwargs.get("reference_list")
        self.extent_type = kwargs.get("extent_type")
        self.expansion_size = kwargs.get("expansion_size")
        self.use_round_corner = kwargs.get("use_round_corner")
        self.output_aedb_path = kwargs.get("output_aedb_path")
        self.open_cutout_at_end = kwargs.get("open_cutout_at_end")
        self.use_pyaedt_cutout = kwargs.get("use_pyaedt_cutout")
        self.number_of_threads = kwargs.get("number_of_threads")
        self.use_pyaedt_extent_computing = kwargs.get("use_pyaedt_extent_computing")
        self.extent_defeature = kwargs.get("extent_defeature")
        self.remove_single_pin_components = kwargs.get("remove_single_pin_components")
        self.custom_extent = kwargs.get("custom_extent")
        self.custom_extent_units = kwargs.get("custom_extent_units")
        self.include_partial_instances = kwargs.get("include_partial_instances")
        self.keep_voids = kwargs.get("keep_voids")
        self.check_terminals = kwargs.get("check_terminals")
        self.include_pingroups = kwargs.get("include_pingroups")
        self.expansion_factor = kwargs.get("expansion_factor")
        self.maximum_iterations = kwargs.get("maximum_iterations")
        self.preserve_components_with_model = kwargs.get("preserve_components_with_model")
        self.simple_pad_check = kwargs.get("simple_pad_check")
        self.keep_lines_as_path = kwargs.get("keep_lines_as_path")


class CfgOperations(CfgBase):
    def __init__(self, pedb, data):
        self._pedb = pedb
        self.op_cutout = CfgCutout(**data["cutout"]) if "cutout" in data else None

    def apply(self):
        """Imports operation information from JSON."""
        if self.op_cutout:
            self._pedb.cutout(**self.op_cutout.get_attributes())
