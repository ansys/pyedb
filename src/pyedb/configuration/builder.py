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
    """Top-level programmatic builder for a pyedb configuration.

    Use this class to construct any part of an EDB configuration payload in
    Python before writing it to JSON/TOML or passing it directly to
    :meth:`~pyedb.configuration.configuration.Configuration.run`.

    Each attribute exposes a dedicated section builder with fluent helper
    methods.  Empty sections are omitted when the payload is serialized via
    :meth:`to_dict`.

    Examples
    --------
    Standalone construction:

    >>> from pyedb.configuration import EdbConfigBuilder
    >>> cfg = EdbConfigBuilder()
    >>> cfg.general.anti_pads_always_on = False
    >>> cfg.nets.add_signal_nets(["SIG1", "CLK"])
    >>> cfg.to_json("my_config.json")

    From an open EDB session (recommended):

    >>> cfg = edb.configuration.create_config_builder()
    >>> cfg.general.anti_pads_always_on = False
    >>> edb.configuration.run(cfg)

    Attributes
    ----------
    general : GeneralConfig
        Global library paths and design flags.
    stackup : StackupConfig
        Materials and layer definitions.
    nets : NetsConfig
        Signal and power/ground net classification.
    components : ComponentsConfig
        Component model and package configuration.
    padstacks : PadstacksConfig
        Padstack definitions and instances.
    pin_groups : PinGroupsConfig
        Named pin-group creation.
    terminals : TerminalsConfig
        Explicit low-level terminal objects.
    ports : PortsConfig
        Port excitations.
    sources : SourcesConfig
        Current and voltage source excitations.
    probes : ProbesConfig
        Voltage probes.
    setups : SetupsConfig
        HFSS and SIwave simulation setup entries.
    boundaries : BoundariesConfig
        Open-region and extent configuration.
    operations : OperationsConfig
        Cutout and auto HFSS-region operations.
    s_parameters : SParameterModelsConfig
        S-parameter model assignments by component definition.
    spice_models : SpiceModelsConfig
        SPICE model assignments.
    package_definitions : PackageDefinitionsConfig
        Thermal package definitions.
    variables : VariablesConfig
        Design and project variables.
    modeler : ModelerConfig
        Geometry creation and cleanup.
    """

    def __init__(self, pedb=None):
        """Initialize all section builders with empty state.

        Parameters
        ----------
        pedb : Edb, optional
            Active EDB session.  When supplied the following lookup methods
            can resolve objects directly from the live database:

            * ``components.get(refdes)`` — retrieve an existing component.
            * ``stackup.get_layer(name)`` — retrieve an existing layer.
            * ``stackup.get_material(name)`` — retrieve an existing material.
            * ``nets.get(net_name)`` — retrieve net classification info.
            * ``padstacks.get_definition(name)`` — retrieve a padstack definition.
            * ``padstacks.get_instance(name)`` — retrieve a padstack instance.
            * ``pin_groups.get(name)`` — retrieve an existing pin group.
            * ``setups.get(name)`` — retrieve a registered setup by name.

            The recommended way to obtain a session-aware builder is
            ``edb.configuration.create_config_builder()``.
        """
        self._pedb = pedb
        self.general = CfgGeneral()
        self.stackup = CfgStackup()
        if pedb is not None:
            self.stackup._set_pedb(pedb)
        self.nets = CfgNets(pedb=pedb)
        self.components = CfgComponents(pedb=pedb)
        self.padstacks = CfgPadstacks.create(pedb=pedb)
        self.pin_groups = CfgPinGroups(pedb=pedb)
        self.terminals = CfgTerminals(terminals=[])
        self.ports = CfgPorts(pedb=pedb)
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
        """Serialize the full configuration to a plain Python dictionary.

        Only sections that contain at least one value are included;
        empty sections (``{}``, ``[]``, ``None``) are silently omitted.

        Returns
        -------
        dict
            Configuration payload keyed by section name
            (``"general"``, ``"stackup"``, … ).

        Examples
        --------
        >>> cfg = EdbConfigBuilder()
        >>> cfg.nets.add_signal_nets(["SIG"])
        >>> cfg.to_dict()
        {'nets': {'signal_nets': ['SIG']}}
        """
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
        """Write the configuration to a JSON file.

        Parameters
        ----------
        file_path : str or Path
            Destination file path.  The ``.json`` extension is expected;
            parent directories are created automatically.
        indent : int, optional
            JSON indentation level.  Default is ``4``.

        Returns
        -------
        Path
            Resolved path of the written file.

        Examples
        --------
        >>> cfg.to_json("my_project_config.json")
        """
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as fh:
            json.dump(self.to_dict(), fh, indent=indent)
        return file_path

    def to_toml(self, file_path: Union[str, Path]) -> Path:
        """Write the configuration to a TOML file.

        Parameters
        ----------
        file_path : str or Path
            Destination file path.  Parent directories are created
            automatically.

        Returns
        -------
        Path
            Resolved path of the written file.

        Raises
        ------
        ImportError
            If the ``toml`` package is not installed.

        Examples
        --------
        >>> cfg.to_toml("my_project_config.toml")
        """
        if not _TOML_AVAILABLE:
            raise ImportError("The 'toml' package is required to write TOML files. Install it with: pip install toml")
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as fh:
            toml.dump(self.to_dict(), fh)
        return file_path

    @classmethod
    def from_dict(cls, data: dict) -> "EdbConfigBuilder":
        """Create an :class:`EdbConfigBuilder` from an existing config dictionary.

        Parameters
        ----------
        data : dict
            Raw configuration dictionary, typically the result of
            ``json.load`` or ``toml.load``.  Unknown keys are ignored.

        Returns
        -------
        EdbConfigBuilder
            Populated builder instance.

        Examples
        --------
        >>> cfg = EdbConfigBuilder.from_dict({"nets": {"signal_nets": ["CLK"]}})
        >>> cfg.nets.signal_nets
        ['CLK']
        """
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
        """Load an :class:`EdbConfigBuilder` from a JSON file.

        Parameters
        ----------
        file_path : str or Path
            Path to a valid JSON configuration file.

        Returns
        -------
        EdbConfigBuilder
            Populated builder instance.

        Examples
        --------
        >>> cfg = EdbConfigBuilder.from_json("base_config.json")
        >>> cfg.general.suppress_pads = True
        >>> cfg.to_json("modified_config.json")
        """
        with open(file_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return cls.from_dict(data)

    @classmethod
    def from_toml(cls, file_path: Union[str, Path]) -> "EdbConfigBuilder":
        """Load an :class:`EdbConfigBuilder` from a TOML file.

        Parameters
        ----------
        file_path : str or Path
            Path to a valid TOML configuration file.

        Returns
        -------
        EdbConfigBuilder
            Populated builder instance.

        Raises
        ------
        ImportError
            If the ``toml`` package is not installed.

        Examples
        --------
        >>> cfg = EdbConfigBuilder.from_toml("base_config.toml")
        """
        if not _TOML_AVAILABLE:
            raise ImportError("The 'toml' package is required to read TOML files. Install it with: pip install toml")
        with open(file_path, "r", encoding="utf-8") as fh:
            data = toml.load(fh)
        return cls.from_dict(data)
