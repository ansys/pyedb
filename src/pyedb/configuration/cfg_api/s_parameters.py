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

"""Build ``s_parameters`` configuration entries.

This module defines lightweight builders for assigning Touchstone models to
component definitions.
"""

from __future__ import annotations

from typing import Dict, List, Optional


class SParameterModelConfig:
    """Represent one S-parameter model assignment."""

    def __init__(
        self,
        name: str,
        component_definition: str,
        file_path: str,
        reference_net: str = "",
        apply_to_all: bool = True,
        components: Optional[List[str]] = None,
        reference_net_per_component: Optional[Dict[str, str]] = None,
        pin_order: Optional[List] = None,
    ):
        """Initialize an S-parameter model assignment.

        Parameters
        ----------
        name : str
            Model assignment name.
        component_definition : str
            Component definition this model is assigned to.
        file_path : str
            Path to the S-parameter file.
        reference_net : str, optional
            Reference net used by the model.
        apply_to_all : bool, default: True
            Whether to apply the model to all matching components.
        components : list of str, optional
            Explicit list of component reference designators to apply to.
        reference_net_per_component : dict, optional
            Per-component reference net overrides.
        pin_order : list, optional
            Pin ordering for port mapping.

        """
        self.name = name
        self.component_definition = component_definition
        self.file_path = file_path
        self.reference_net = reference_net
        self.apply_to_all = apply_to_all
        self.components = components or []
        self.reference_net_per_component = reference_net_per_component or {}
        self.pin_order = pin_order

    def to_dict(self) -> dict:
        """Serialize the S-parameter model assignment.

        Returns
        -------
        dict
            Dictionary matching the schema used by the ``s_parameters``
            configuration list.

        """
        data = {
            "name": self.name,
            "component_definition": self.component_definition,
            "file_path": self.file_path,
            "reference_net": self.reference_net,
            "apply_to_all": self.apply_to_all,
            "components": self.components,
        }
        if self.reference_net_per_component:
            data["reference_net_per_component"] = self.reference_net_per_component
        if self.pin_order is not None:
            data["pin_order"] = self.pin_order
        return data


class SParametersConfig:
    """Fluent builder for the ``s_parameters`` configuration list."""

    def __init__(self):
        """Initialize the S-parameters configuration."""
        self._models: List[SParameterModelConfig] = []

    def add(
        self,
        name: str,
        component_definition: str,
        file_path: str,
        reference_net: str = "",
        apply_to_all: bool = True,
        components: Optional[List[str]] = None,
        reference_net_per_component: Optional[Dict[str, str]] = None,
        pin_order: Optional[List] = None,
    ) -> SParameterModelConfig:
        """Add an S-parameter model assignment.

        Parameters
        ----------
        name : str
            Configuration entry name.
        component_definition : str
            Component definition to bind the model to.
        file_path : str
            Path to the Touchstone model.
        reference_net : str, default: ""
            Global reference net for the model.
        apply_to_all : bool, default: True
            Whether the model applies to all matching components.
        components : list[str], optional
            Explicit component instances to target when ``apply_to_all`` is
            disabled.
        reference_net_per_component : dict[str, str], optional
            Per-component reference-net overrides.
        pin_order : list, optional
            Optional explicit pin order mapping.

        Returns
        -------
        SParameterModelConfig
            Newly created assignment.

        """
        m = SParameterModelConfig(
            name=name,
            component_definition=component_definition,
            file_path=file_path,
            reference_net=reference_net,
            apply_to_all=apply_to_all,
            components=components,
            reference_net_per_component=reference_net_per_component,
            pin_order=pin_order,
        )
        self._models.append(m)
        return m

    def to_list(self) -> List[dict]:
        """Serialize all configured S-parameter model assignments.

        Returns
        -------
        list[dict]
            Model definitions in insertion order.

        """
        return [m.to_dict() for m in self._models]


SParameterModelsConfig = SParametersConfig
