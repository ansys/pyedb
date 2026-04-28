# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""SPICE models builder API.

Data model: :class:`CfgSpiceModels` (pydantic root defined here).
The runtime class :class:`~pyedb.configuration.cfg_spice_models.CfgSpiceModel`
requires a live EDB connection; this API layer owns the pure-data pydantic
models and serialises to plain dicts that the runtime class can consume.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from pyedb.configuration.cfg_common import CfgBaseModel


class CfgSpiceModelData(CfgBaseModel):
    """Pydantic data model for a single SPICE model entry."""

    name: str
    component_definition: str
    file_path: str
    sub_circuit_name: str = ""
    apply_to_all: bool = True
    components: List[str] = Field(default_factory=list)
    terminal_pairs: Optional[List] = None

    model_config = {"populate_by_name": True, "extra": "ignore"}


class CfgSpiceModels(BaseModel):
    """Root pydantic model for the ``spice_models`` configuration list."""

    spice_models: List[CfgSpiceModelData] = Field(default_factory=list)

    def add(
        self,
        name: str,
        component_definition: str,
        file_path: str,
        sub_circuit_name: str = "",
        apply_to_all: bool = True,
        components: Optional[List[str]] = None,
        terminal_pairs: Optional[List] = None,
    ) -> CfgSpiceModelData:
        entry = CfgSpiceModelData(
            name=name,
            component_definition=component_definition,
            file_path=file_path,
            sub_circuit_name=sub_circuit_name,
            apply_to_all=apply_to_all,
            components=components or [],
            terminal_pairs=terminal_pairs,
        )
        self.spice_models.append(entry)
        return entry


class SpiceModelsConfig:
    """Fluent builder for the ``spice_models`` configuration list.

    Wraps :class:`CfgSpiceModels`.

    Examples
    --------
    >>> cfg.spice_models.add(
    ...     name="R_model",
    ...     component_definition="RES_DEF",
    ...     file_path="models/res.lib",
    ...     sub_circuit_name="RES",
    ... )
    """

    def __init__(self):
        self._model = CfgSpiceModels()

    def add(
        self,
        name: str,
        component_definition: str,
        file_path: str,
        sub_circuit_name: str = "",
        apply_to_all: bool = True,
        components: Optional[List[str]] = None,
        terminal_pairs: Optional[List] = None,
    ) -> CfgSpiceModelData:
        """Add a SPICE model entry.

        Returns
        -------
        CfgSpiceModelData
        """
        return self._model.add(
            name=name,
            component_definition=component_definition,
            file_path=file_path,
            sub_circuit_name=sub_circuit_name,
            apply_to_all=apply_to_all,
            components=components,
            terminal_pairs=terminal_pairs,
        )

    def to_list(self) -> List[dict]:
        """Serialise to a list of dicts consumable by
        :class:`~pyedb.configuration.cfg_spice_models.CfgSpiceModel`."""
        return [m.model_dump(exclude_none=True) for m in self._model.spice_models]


#: Backward-compatible alias
SpiceModelConfig = CfgSpiceModelData
