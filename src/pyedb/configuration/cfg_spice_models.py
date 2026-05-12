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
from typing import Any, List, Optional

from pydantic import Field, PrivateAttr, model_validator

from pyedb.configuration.cfg_common import CfgBaseModel, serialize_list


class CfgSpiceModel(CfgBaseModel):
    """Represent one SPICE subcircuit model assignment."""

    model_config = {"populate_by_name": True, "extra": "ignore", "arbitrary_types_allowed": True}

    def __init__(self, name: str = "", component_definition: str = "", file_path: str = "", **kwargs):
        if name:
            kwargs["name"] = name
        if component_definition:
            kwargs["component_definition"] = component_definition
        if file_path:
            kwargs["file_path"] = file_path
        super().__init__(**kwargs)

    name: str = ""
    component_definition: str = ""
    file_path: str = ""
    sub_circuit_name: str = ""
    apply_to_all: bool = True
    components: List[Any] = Field(default_factory=list)
    terminal_pairs: Optional[Any] = None

    # Runtime-only inputs (excluded from serialization)
    pedb: Optional[Any] = Field(default=None, exclude=True, repr=False)
    path_lib: Optional[str] = Field(default=None, exclude=True, repr=False)

    # Runtime-only attributes stored as Pydantic private fields
    _pedb: Any = PrivateAttr(default=None)
    _path_libraries: Optional[str] = PrivateAttr(default=None)

    @model_validator(mode="before")
    @classmethod
    def _normalise_inputs(cls, values):
        if not isinstance(values, dict):
            return values
        # Handle spice_dict merge (from JSON loading or explicit kwarg)
        spice_dict = values.pop("spice_dict", None)
        merged = dict(spice_dict or {})
        for key in ("name", "component_definition", "file_path", "sub_circuit_name"):
            val = values.pop(key, None)
            if val:
                merged[key] = val
        # apply_to_all=False must be honoured
        apply_to_all = values.pop("apply_to_all", merged.get("apply_to_all", True))
        merged.setdefault("apply_to_all", apply_to_all)
        if not apply_to_all:
            merged["apply_to_all"] = apply_to_all
        components = values.pop("components", None)
        if components is not None:
            merged["components"] = components
        terminal_pairs = values.pop("terminal_pairs", None)
        if terminal_pairs is not None:
            merged["terminal_pairs"] = terminal_pairs
        # carry through any remaining keys (e.g. pedb, path_lib)
        merged.update(values)
        # Normalise components to a list
        raw_components = merged.get("components", [])
        if isinstance(raw_components, str):
            raw_components = [raw_components]
        elif not isinstance(raw_components, (list, tuple, set)):
            raw_components = [raw_components] if raw_components else []
        merged["components"] = list(raw_components)
        return merged

    def model_post_init(self, __context: Any) -> None:
        """Set private runtime attributes from excluded fields."""
        if self.pedb is not None:
            self._pedb = self.pedb
        if self.path_lib is not None:
            self._path_libraries = self.path_lib

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
            fpath = str(Path(self._path_libraries or "") / self.file_path)
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
        self.models = [
            CfgSpiceModel(pedb=getattr(pdata, "_pedb", None), path_lib=path_lib, spice_dict=spice_model)
            for spice_model in (data or [])
        ]

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
            pedb=getattr(self._pdata, "_pedb", None),
            path_lib=self.path_libraries,
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
