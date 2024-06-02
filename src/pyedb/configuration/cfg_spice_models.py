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

from pathlib import Path


class CfgSpiceModel:
    def __init__(self, pdata, path_lib, spice_dict):
        self._pedb = pdata._pedb
        self.path_libraries = path_lib
        self._spice_dict = spice_dict
        self.name = self._spice_dict.get("name", "")
        self.component_definition = self._spice_dict.get("component_definition", "")
        self.file_path = self._spice_dict.get("file_path", "")
        self.sub_circuit_name = self._spice_dict.get("sub_circuit_name", "")
        self.apply_to_all = self._spice_dict.get("apply_to_all", True)
        self.components = list(self._spice_dict.get("components", []))

    def apply(self):
        """Apply Spice model on layout."""
        if not Path(self.file_path).anchor:
            fpath = str(Path(self.path_libraries) / self.file_path)
            comps = self._pedb.components.definitions[self.component_definition].components
            if self.apply_to_all:
                for ref_des, comp in comps.items():
                    comp.assign_spice_model(fpath, self.name, self.sub_circuit_name)
            else:
                for ref_des, comp in comps.items():
                    if ref_des in self.components:
                        comp.assign_spice_model(fpath, self.name, self.sub_circuit_name)
