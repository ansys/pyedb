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

"""S-parameter models builder API.

Data model: :class:`CfgSParameterModels` (pydantic root defined here).
The runtime class :class:`~pyedb.configuration.cfg_s_parameter_models.CfgSParameters`
requires a live EDB connection; this API layer owns the pure-data pydantic models
and serialises to plain dicts that the runtime class can consume.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from pyedb.configuration.cfg_common import CfgBaseModel


class CfgSParameterModelData(CfgBaseModel):
    """Pydantic data model for a single S-parameter model entry."""

    name: str
    component_definition: str
    file_path: str
    reference_net: str = ""
    apply_to_all: bool = False
    components: List[str] = Field(default_factory=list)
    reference_net_per_component: Dict[str, str] = Field(default_factory=dict)
    pin_order: Optional[List] = None

    model_config = {"populate_by_name": True, "extra": "ignore"}


class CfgSParameterModels(BaseModel):
    """Root pydantic model for the ``s_parameters`` configuration list."""

    s_parameter_models: List[CfgSParameterModelData] = Field(default_factory=list)

    def add(
        self,
        name: str,
        component_definition: str,
        file_path: str,
        reference_net: str = "",
        apply_to_all: bool = False,
        components: Optional[List[str]] = None,
        reference_net_per_component: Optional[Dict[str, str]] = None,
        pin_order: Optional[List] = None,
    ) -> CfgSParameterModelData:
        entry = CfgSParameterModelData(
            name=name,
            component_definition=component_definition,
            file_path=file_path,
            reference_net=reference_net,
            apply_to_all=apply_to_all,
            components=components or [],
            reference_net_per_component=reference_net_per_component or {},
            pin_order=pin_order,
        )
        self.s_parameter_models.append(entry)
        return entry


class SParametersConfig:
    """Fluent builder for the ``s_parameters`` configuration list.

    Wraps :class:`CfgSParameterModels`.

    Examples
    --------
    >>> cfg.s_parameters.add(
    ...     name="U1_model",
    ...     component_definition="COMP_DEF",
    ...     file_path="models/u1.s4p",
    ...     reference_net="GND",
    ... )
    """

    def __init__(self):
        self._model = CfgSParameterModels()

    def add(
        self,
        name: str,
        component_definition: str,
        file_path: str,
        reference_net: str = "",
        apply_to_all: bool = False,
        components: Optional[List[str]] = None,
        reference_net_per_component: Optional[Dict[str, str]] = None,
        pin_order: Optional[List] = None,
    ) -> CfgSParameterModelData:
        """Add an S-parameter model entry.

        Returns
        -------
        CfgSParameterModelData
        """
        return self._model.add(
            name=name,
            component_definition=component_definition,
            file_path=file_path,
            reference_net=reference_net,
            apply_to_all=apply_to_all,
            components=components,
            reference_net_per_component=reference_net_per_component,
            pin_order=pin_order,
        )

    def to_list(self) -> List[dict]:
        """Serialise to a list of dicts consumable by
        :class:`~pyedb.configuration.cfg_s_parameter_models.CfgSParameters`."""
        return [m.model_dump(exclude_none=True) for m in self._model.s_parameter_models]


#: Backward-compatible alias
SParameterModelsConfig = SParametersConfig
SParameterModelConfig = CfgSParameterModelData
