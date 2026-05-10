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

"""Build SPICE model assignment entries for configuration payloads."""

from pathlib import Path

from pyedb.configuration.cfg_common import serialize_list


class CfgSpiceModel:
    """Represent one SPICE subcircuit model assignment."""

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
        # Legacy positional-arg call: CfgSpiceModel(name_str, comp_def_str, file_path_str, ...)
        # Detect by checking whether pdata is a plain string (not an EDB session).
        if isinstance(pdata, str) and not hasattr(pdata, "_pedb"):
            name = pdata
            component_definition = path_lib or component_definition
            file_path = spice_dict if isinstance(spice_dict, str) else file_path
            pdata = None
            path_lib = None
            spice_dict = None

        # Merge dict-based input (from JSON loading) with explicit keyword args.
        merged = dict(spice_dict or {})
        explicit = {
            "name": name,
            "component_definition": component_definition,
            "file_path": file_path,
            "sub_circuit_name": sub_circuit_name,
            "apply_to_all": apply_to_all,
            "components": components,
            "terminal_pairs": terminal_pairs,
        }
        for k, v in explicit.items():
            if v not in (None, "") or k == "apply_to_all":
                merged[k] = v
        merged.update(kwargs)

        self._pedb = getattr(pdata, "_pedb", None)
        self.path_libraries = path_lib
        self.name = merged.get("name", "")
        self.component_definition = merged.get("component_definition", "")
        self.file_path = str(merged.get("file_path", "") or "")
        self.sub_circuit_name = merged.get("sub_circuit_name", "")
        self.apply_to_all = merged.get("apply_to_all", True)
        raw_components = merged.get("components", [])
        if isinstance(raw_components, str):
            raw_components = [raw_components]
        elif raw_components is None:
            raw_components = []
        elif not isinstance(raw_components, (list, tuple, set)):
            raw_components = [raw_components]
        self.components = list(raw_components)
        self.terminal_pairs = merged.get("terminal_pairs", None)

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
        return serialize_list(self.models)
