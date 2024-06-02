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


class CfgSParameterModel:
    def __init__(self, pdata, path_lib, sparam_dict):
        self._pedb = pdata._pedb
        self.path_libraries = path_lib
        self._sparam_dict = sparam_dict
        self.name = self._sparam_dict.get("name", "")
        self.component_definition = self._sparam_dict.get("component_definition", "")
        self.file_path = self._sparam_dict.get("file_path", "")
        self.apply_to_all = self._sparam_dict.get("apply_to_all", False)
        self.components = self._sparam_dict.get("components", [])
        self.reference_net = self._sparam_dict.get("reference_net", "")
        self.reference_net_per_component = self._sparam_dict.get("reference_net_per_component", {})

    def apply(self):
        fpath = self.file_path
        if not Path(fpath).anchor:
            fpath = str(Path(self.path_libraries) / fpath)
        comp_def = self._pedb.definitions.component[self.component_definition]
        comp_def.add_n_port_model(fpath, self.name)
        comp_list = dict()
        if self.apply_to_all:
            comp_list.update(
                {refdes: comp for refdes, comp in comp_def.components.items() if refdes not in self.components}
            )
        else:
            comp_list.update(
                {refdes: comp for refdes, comp in comp_def.components.items() if refdes in self.components}
            )

        for refdes, comp in comp_list.items():
            if refdes in self.reference_net_per_component:
                ref_net = self.reference_net_per_component[refdes]
            else:
                ref_net = self.reference_net
            comp.use_s_parameter_model(self.name, reference_net=ref_net)
