# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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
    def __init__(
        self,
        pdata=None,
        path_lib=None,
        spice_dict=None,
        name: str = "",
        component_definition: str = "",
        file_path: str = "",
        sub_circuit_name: str = "",
        apply_to_all: bool = True,
        components=None,
        terminal_pairs=None,
        **kwargs,
    ):
        if not hasattr(pdata, "_pedb") and isinstance(pdata, str):
            spice_dict = {
                "name": pdata,
                "component_definition": path_lib,
                "file_path": spice_dict if isinstance(spice_dict, str) else file_path,
                "sub_circuit_name": sub_circuit_name,
                "apply_to_all": apply_to_all,
                "components": list(components or []),
                "terminal_pairs": terminal_pairs,
            }
            pdata = None
            path_lib = None
        else:
            spice_dict = dict(spice_dict or {})
        spice_dict.update(
            {
                k: v
                for k, v in {
                    "name": name,
                    "component_definition": component_definition,
                    "file_path": file_path,
                    "sub_circuit_name": sub_circuit_name,
                    "apply_to_all": apply_to_all,
                    "components": components,
                    "terminal_pairs": terminal_pairs,
                }.items()
                if v not in [None, ""] or k == "apply_to_all"
            }
        )
        spice_dict.update(kwargs)
        self._pedb = getattr(pdata, "_pedb", None)
        self.path_libraries = path_lib
        self._spice_dict = spice_dict
        self.name = self._spice_dict.get("name", "")
        self.component_definition = self._spice_dict.get("component_definition", "")
        self.file_path = str(self._spice_dict.get("file_path", "") or "")
        self.sub_circuit_name = self._spice_dict.get("sub_circuit_name", "")
        self.apply_to_all = self._spice_dict.get("apply_to_all", True)
        components = self._spice_dict.get("components", [])
        if isinstance(components, str):
            components = [components]
        self.components = list(components or [])
        self.terminal_pairs = self._spice_dict.get("terminal_pairs", None)

    def to_dict(self) -> dict:
        """Serialize the SPICE model assignment."""
        data = {
            "name": self.name,
            "component_definition": self.component_definition,
            "file_path": self.file_path,
            "sub_circuit_name": self.sub_circuit_name,
            "apply_to_all": self.apply_to_all,
            "components": self.components,
        }
        if self.terminal_pairs is not None:
            data["terminal_pairs"] = self.terminal_pairs
        return data

    def apply(self):
        """Apply Spice model on layout."""
        if self._pedb is None:
            return self.to_dict()
        if not Path(self.file_path).anchor:
            fpath = str(Path(self.path_libraries or "") / self.file_path)
        else:
            fpath = self.file_path

        comps = self._pedb.components.definitions[self.component_definition].components
        if self.apply_to_all:
            for ref_des, comp in comps.items():
                comp.assign_spice_model(fpath, self.name, self.sub_circuit_name, self.terminal_pairs)
        else:
            for ref_des, comp in comps.items():
                if ref_des in self.components:
                    comp.assign_spice_model(fpath, self.name, self.sub_circuit_name, self.terminal_pairs)


class CfgSpiceModels:
    """Collect SPICE model assignments for serialization."""

    def __init__(self, pdata=None, data=None, path_lib=None):
        self._pdata = pdata
        self.path_libraries = path_lib
        self.models = [CfgSpiceModel(pdata, path_lib, spice_model) for spice_model in (data or [])]

    def add(
        self,
        name: str,
        component_definition: str,
        file_path: str,
        sub_circuit_name: str = "",
        apply_to_all: bool = True,
        components=None,
        terminal_pairs=None,
    ):
        """Add a SPICE model assignment."""
        model = CfgSpiceModel(
            self._pdata,
            self.path_libraries,
            name=name,
            component_definition=component_definition,
            file_path=file_path,
            sub_circuit_name=sub_circuit_name,
            apply_to_all=apply_to_all,
            components=components or [],
            terminal_pairs=terminal_pairs,
        )
        self.models.append(model)
        return model

    def to_list(self):
        """Serialize all configured SPICE model assignments."""
        return [model.to_dict() for model in self.models]

