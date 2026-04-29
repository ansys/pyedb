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

"""Provide the top-level programmatic configuration builder."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Union

try:
    import toml

    _TOML_AVAILABLE = True
except ImportError:  # pragma: no cover
    toml = None
    _TOML_AVAILABLE = False

from pyedb.configuration.cfg_boundaries import CfgBoundaries
from pyedb.configuration.cfg_common import CfgVariables
from pyedb.configuration.cfg_components import CfgComponents
from pyedb.configuration.cfg_general import CfgGeneral
from pyedb.configuration.cfg_modeler import CfgModeler
from pyedb.configuration.cfg_nets import CfgNets
from pyedb.configuration.cfg_operations import CfgOperations
from pyedb.configuration.cfg_package_definition import CfgPackageDefinitions
from pyedb.configuration.cfg_padstacks import CfgPadstacks
from pyedb.configuration.cfg_pin_groups import CfgPinGroups
from pyedb.configuration.cfg_ports_sources import CfgPorts, CfgProbes, CfgSources
from pyedb.configuration.cfg_s_parameter_models import CfgSParameters
from pyedb.configuration.cfg_setup import CfgSetups
from pyedb.configuration.cfg_spice_models import CfgSpiceModels
from pyedb.configuration.cfg_stackup import CfgStackup
from pyedb.configuration.cfg_terminals import CfgTerminals


class _DictProxy:
    """Wrap a raw dictionary with a ``to_dict`` method."""

    def __init__(self, data: dict):
        self._data = data

    def to_dict(self) -> dict:
        """Return the wrapped dictionary unchanged."""
        return self._data


class EdbConfigBuilder:
    """Top-level programmatic builder for a pyedb configuration."""

    def __init__(self):
        """Initialize all section builders with empty state."""
        self.general = CfgGeneral()
        self.stackup = CfgStackup()
        self.nets = CfgNets()
        self.components = CfgComponents()
        self.padstacks = CfgPadstacks.create()
        self.pin_groups = CfgPinGroups()
        self.terminals = CfgTerminals(terminals=[])
        self.ports = CfgPorts()
        self.sources = CfgSources()
        self.probes = CfgProbes()
        self.setups = CfgSetups()
        self.boundaries = CfgBoundaries.create()
        self.operations = CfgOperations()
        self.s_parameters = CfgSParameters()
        self.spice_models = CfgSpiceModels()
        self.package_definitions = CfgPackageDefinitions()
        self.variables = CfgVariables()
        self.modeler = CfgModeler()

    def __repr__(self) -> str:  # pragma: no cover
        d = self.to_dict()
        sections = ", ".join(d.keys()) if d else "<empty>"
        return f"EdbConfigBuilder(sections=[{sections}])"

    def to_dict(self) -> dict:
        """Serialize the configuration to a plain Python dictionary."""
        data: dict = {}

        for key, value in (
            ("general", self.general.to_dict()),
            ("stackup", self.stackup.to_dict()),
            ("nets", self.nets.to_dict()),
            ("components", self.components.to_list()),
            ("padstacks", self.padstacks.to_dict()),
            ("pin_groups", self.pin_groups.to_list()),
            ("terminals", self.terminals.to_list()),
            ("ports", self.ports.to_list()),
            ("sources", self.sources.to_list()),
            ("probes", self.probes.to_list()),
            ("setups", self.setups.to_list()),
            ("boundaries", self.boundaries.to_dict()),
            ("operations", self.operations.to_dict()),
            ("s_parameters", self.s_parameters.to_list()),
            ("spice_models", self.spice_models.to_list()),
            ("package_definitions", self.package_definitions.to_list()),
            ("variables", self.variables.to_list()),
            ("modeler", self.modeler.to_dict()),
        ):
            if value not in ({}, [], None):
                data[key] = value
        return data

    def to_json(self, file_path: Union[str, Path], indent: int = 4) -> Path:
        """Write the configuration to a JSON file."""
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as fh:
            json.dump(self.to_dict(), fh, indent=indent)
        return file_path

    def to_toml(self, file_path: Union[str, Path]) -> Path:
        """Write the configuration to a TOML file."""
        if not _TOML_AVAILABLE:
            raise ImportError("The 'toml' package is required to write TOML files. Install it with: pip install toml")
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as fh:
            toml.dump(self.to_dict(), fh)
        return file_path

    @classmethod
    def from_dict(cls, data: dict) -> "EdbConfigBuilder":
        """Create an :class:`EdbConfigBuilder` from an existing config dictionary."""
        builder = cls()
        builder.general = CfgGeneral(data=data.get("general", {}))
        builder.stackup = CfgStackup(**data.get("stackup", {}))
        builder.nets = CfgNets(
            signal_nets=data.get("nets", {}).get("signal_nets", []),
            power_nets=data.get("nets", {}).get("power_ground_nets", []),
        )
        builder.components = CfgComponents(components_data=data.get("components", []))
        builder.padstacks = CfgPadstacks.create(**data.get("padstacks", {}))
        builder.pin_groups = CfgPinGroups(pingroup_data=data.get("pin_groups", []))
        builder.terminals = CfgTerminals.create(data.get("terminals", []))
        builder.ports = CfgPorts(ports_data=data.get("ports", []))
        builder.sources = CfgSources(sources_data=data.get("sources", []))
        builder.probes = CfgProbes(data=data.get("probes", []))
        builder.setups = CfgSetups.create(data.get("setups", []))
        builder.boundaries = CfgBoundaries.create(**data.get("boundaries", {}))
        builder.operations = CfgOperations(**data.get("operations", {}))
        builder.s_parameters = CfgSParameters(data=data.get("s_parameters", []))
        builder.spice_models = CfgSpiceModels(data=data.get("spice_models", []))
        builder.package_definitions = CfgPackageDefinitions(data=data.get("package_definitions", []))
        builder.variables = CfgVariables(variables=data.get("variables", []))
        builder.modeler = CfgModeler(data=data.get("modeler", {}))
        return builder

    @classmethod
    def from_json(cls, file_path: Union[str, Path]) -> "EdbConfigBuilder":
        """Load from a JSON file."""
        with open(file_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return cls.from_dict(data)

    @classmethod
    def from_toml(cls, file_path: Union[str, Path]) -> "EdbConfigBuilder":
        """Load from a TOML file."""
        if not _TOML_AVAILABLE:
            raise ImportError("The 'toml' package is required to read TOML files. Install it with: pip install toml")
        with open(file_path, "r", encoding="utf-8") as fh:
            data = toml.load(fh)
        return cls.from_dict(data)
