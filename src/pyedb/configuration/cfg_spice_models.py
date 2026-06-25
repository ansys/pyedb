# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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
from typing import Any, Optional

from pydantic import Field, PrivateAttr, model_validator

from pyedb.configuration.cfg_common import CfgBaseModel


class CfgSpiceModel(CfgBaseModel):
    """Represent one SPICE subcircuit model assignment."""

    model_config = {"populate_by_name": True, "extra": "ignore", "arbitrary_types_allowed": True}

    name: str = ""
    component_definition: str = ""
    file_path: str = ""
    sub_circuit_name: str = ""
    apply_to_all: bool = True
    components: list = Field(default_factory=list)
    terminal_pairs: Optional[Any] = None

    # Runtime-only inputs (excluded from serialization)
    pedb: Optional[Any] = Field(default=None, exclude=True, repr=False)
    path_lib: Optional[str] = Field(default=None, exclude=True, repr=False)

    # Runtime-only attributes stored as Pydantic private fields
    _pedb: Any = PrivateAttr(default=None)
    _path_libraries: Optional[str] = PrivateAttr(default=None)

    @model_validator(mode="before")
    @staticmethod
    def _normalise_inputs(values):
        if not isinstance(values, dict):
            return values
        merged = dict(values)
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

    def apply(self):
        """Apply Spice model on layout."""
        if self._pedb is None:
            return self.model_dump(exclude_none=True)
        if not Path(self.file_path).anchor:
            if self._path_libraries:
                base = Path(self._path_libraries)
            else:
                base = Path(self._pedb.edbpath).parent
            fpath = str(base / self.file_path)
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
            CfgSpiceModel(pedb=getattr(pdata, "_pedb", None), path_lib=path_lib, **spice_model)
            for spice_model in (data or [])
        ]

    def to_list(self):
        """Serialize all SPICE models to a list of dictionaries."""
        return [m.model_dump(exclude_none=True) for m in self.models]

    def get_data_from_db(self, cfg_components):
        """Read SPICE model assignments from EDB by inspecting components.

        Groups components that share the same SPICE model (by model name,
        component definition, file path, and sub-circuit) into a single
        ``spice_models`` entry suitable for round-trip export.

        Parameters
        ----------
        cfg_components : list of dict
            Per-component dictionaries already retrieved by
            :class:`CfgComponents.retrieve_parameters_from_edb`. Components
            assigned a SPICE model carry the data under the ``spice_model``
            key.

        Returns
        -------
        list of dict
            JSON-serializable SPICE model assignment entries.
        """
        if self._pdata is None and not self.models:
            return [m.model_dump(exclude_none=True) for m in self.models]

        # Rebuild from EDB to make the export reflect the live design state
        # (avoids duplicating entries previously loaded from a JSON config).
        self.models = []

        # Group components by (model_name, definition, file_path, sub_circuit)
        grouped = {}
        for comp in cfg_components or []:
            sm = comp.get("spice_model")
            if not sm:
                continue
            key = (
                sm.get("model_name", ""),
                comp.get("definition", ""),
                sm.get("model_path", ""),
                sm.get("sub_circuit", ""),
            )
            entry = grouped.setdefault(
                key,
                {
                    "name": key[0],
                    "component_definition": key[1],
                    "file_path": key[2],
                    "sub_circuit_name": key[3],
                    "apply_to_all": False,
                    "components": [],
                    "terminal_pairs": sm.get("terminal_pairs"),
                },
            )
            ref_des = comp.get("reference_designator")
            if ref_des and ref_des not in entry["components"]:
                entry["components"].append(ref_des)

        # Build CfgSpiceModel entries from grouped data.
        for entry in grouped.values():
            self.models.append(
                CfgSpiceModel(
                    pedb=getattr(self._pdata, "_pedb", None),
                    path_lib=self.path_libraries,
                    name=entry["name"],
                    component_definition=entry["component_definition"],
                    file_path=entry["file_path"],
                    sub_circuit_name=entry["sub_circuit_name"],
                    apply_to_all=entry["apply_to_all"],
                    components=entry["components"],
                    terminal_pairs=entry["terminal_pairs"],
                )
            )
        return [m.model_dump(exclude_none=True) for m in self.models]

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
