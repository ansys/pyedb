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

"""SPICE models builder API."""

from __future__ import annotations

from typing import List, Optional


class SpiceModelConfig:
    """Single SPICE model entry."""

    def __init__(
        self,
        name: str,
        component_definition: str,
        file_path: str,
        sub_circuit_name: str = "",
        apply_to_all: bool = True,
        components: Optional[List[str]] = None,
        terminal_pairs: Optional[List] = None,
    ):
        self.name = name
        self.component_definition = component_definition
        self.file_path = file_path
        self.sub_circuit_name = sub_circuit_name
        self.apply_to_all = apply_to_all
        self.components = components or []
        self.terminal_pairs = terminal_pairs

    def to_dict(self) -> dict:
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


class SpiceModelsConfig:
    """Fluent builder for the ``spice_models`` configuration list."""

    def __init__(self):
        self._models: List[SpiceModelConfig] = []

    def add(
        self,
        name: str,
        component_definition: str,
        file_path: str,
        sub_circuit_name: str = "",
        apply_to_all: bool = True,
        components: Optional[List[str]] = None,
        terminal_pairs: Optional[List] = None,
    ) -> SpiceModelConfig:
        m = SpiceModelConfig(
            name=name,
            component_definition=component_definition,
            file_path=file_path,
            sub_circuit_name=sub_circuit_name,
            apply_to_all=apply_to_all,
            components=components,
            terminal_pairs=terminal_pairs,
        )
        self._models.append(m)
        return m

    def to_list(self) -> List[dict]:
        return [m.to_dict() for m in self._models]
