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

"""Aggregate configuration section objects into one runtime data container."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Union
import warnings

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


class CfgData:
    """Runtime container and programmatic builder for pyedb configuration.

    Can be instantiated **with or without** a live EDB session.  When
    `pedb` is `None` the object works as a standalone builder for
    constructing configuration payloads in Python.

    Parameters
    ----------
    pedb : Edb, optional
        Live EDB session.  When supplied, section objects can resolve
        existing database objects via `get` helpers.
    **kwargs
        Configuration section data.  Recognised keys: `general`,
        `boundaries`, `nets`, `components`, `padstacks`,
        `pin_groups`, `terminals`, `ports`, `sources`, `setups`,
        `stackup`, `s_parameters`, `spice_models`,
        `package_definitions`, `operations`, `modeler`, `variables`,
        `probes`.  Unknown keys trigger a `UserWarning`.

    Examples
    --------
    Standalone construction (no EDB session):

    from pyedb.configuration.cfg_data import CfgData
    cfg = CfgData()
    cfg.nets.add_signal_nets(["SIG1", "CLK"])
    cfg.to_json("my_config.json")

    From an open EDB session (recommended):

    cfg = edb.configuration.create_config_builder()
    cfg.general.anti_pads_always_on = False
    edb.configuration.run(cfg)

    Attributes
    ----------
    general : CfgGeneral
        Global library paths and design flags.
    stackup : CfgStackup
        Materials and layer definitions.
    nets : CfgNets
        Signal and power/ground net classification.
    components : CfgComponents
        Component model and package configuration.
    padstacks : CfgPadstacks
        Padstack definitions and instances.
    pin_groups : CfgPinGroups
        Named pin-group creation.
    terminals : CfgTerminals
        Explicit low-level terminal objects.
    ports : CfgPorts
        Port excitations.
    sources : CfgSources
        Current and voltage source excitations.
    probes : CfgProbes
        Voltage probes.
    setups : CfgSetups
        HFSS and SIwave simulation setup entries.
    boundaries : CfgBoundaries
        Open-region and extent configuration.
    operations : CfgOperations
        Cutout and auto HFSS-region operations.
    s_parameters : CfgSParameters
        S-parameter model assignments by component definition.
    spice_models : CfgSpiceModels
        SPICE model assignments.
    package_definitions : CfgPackageDefinitions
        Thermal package definitions.
    variables : CfgVariables
        Design and project variables.
    modeler : CfgModeler
        Geometry creation and cleanup.
    """

    _KNOWN_SECTIONS = frozenset(
        {
            "general",
            "boundaries",
            "nets",
            "components",
            "padstacks",
            "pin_groups",
            "terminals",
            "ports",
            "sources",
            "setups",
            "stackup",
            "s_parameters",
            "spice_models",
            "package_definitions",
            "operations",
            "modeler",
            "variables",
            "probes",
        }
    )

    def __init__(self, pedb=None, **kwargs):
        unknown = set(kwargs) - self._KNOWN_SECTIONS
        if unknown:
            warnings.warn(
                f"Unknown configuration section(s) will be ignored: {sorted(unknown)}",
                UserWarning,
                stacklevel=2,
            )

        self._pedb = pedb
        general = kwargs.get("general", {})
        boundaries = kwargs.get("boundaries", {})
        nets = kwargs.get("nets", {})

        self.general = CfgGeneral(pedb, general) if general else CfgGeneral(pedb)

        self.boundaries = CfgBoundaries.create(**boundaries)

        self.nets = CfgNets(
            pedb=pedb,
            signal_nets=nets.get("signal_nets", []),
            power_nets=nets.get("power_ground_nets", []),
        )

        self.components = CfgComponents(pedb=pedb, components_data=kwargs.get("components", []))

        self.padstacks = CfgPadstacks.create(pedb=pedb, **kwargs.get("padstacks", {}))

        self.pin_groups = CfgPinGroups(pedb=pedb, pin_group_data=kwargs.get("pin_groups", []))

        self.terminals = CfgTerminals.create(terminals=kwargs.get("terminals", []))

        self.ports = CfgPorts(pedb=pedb, ports_data=kwargs.get("ports", []))

        self.sources = CfgSources(pedb=pedb, sources_data=kwargs.get("sources", []))

        self.setups = CfgSetups.create(setups=kwargs.get("setups", []))

        self.stackup = CfgStackup(**kwargs.get("stackup", {}))
        if pedb is not None:
            self.stackup._set_pedb(pedb)

        self.s_parameters = CfgSParameters(
            pedb=pedb,
            data=kwargs.get("s_parameters", []),
            path_lib=general.get("s_parameter_library", "") if isinstance(general, dict) else "",
        )

        self.spice_models = CfgSpiceModels(
            pdata=self if pedb else None,
            data=kwargs.get("spice_models", []),
            path_lib=general.get("spice_model_library", "") if isinstance(general, dict) else None,
        )

        self.package_definitions = CfgPackageDefinitions(pedb=pedb, data=kwargs.get("package_definitions", []))
        self.operations = CfgOperations(**kwargs.get("operations", {}))

        self.modeler = CfgModeler(pedb=pedb, data=kwargs.get("modeler", {}))

        self.variables = CfgVariables(variables=kwargs.get("variables", []))

        self.probes = CfgProbes(pedb=pedb, data=kwargs.get("probes", []))

        if pedb is not None:
            self.padstacks._set_cfg_stackup(self.stackup)

    def __repr__(self) -> str:  # pragma: no cover
        d = self.to_dict()
        sections = ", ".join(d.keys()) if d else "<empty>"
        return f"CfgData(sections=[{sections}])"

    def _serialized_sections(self):
        """Yield serialized section payloads in export order."""
        yield "general", {k: v for k, v in self.general.model_dump(exclude_none=True).items() if v != ""}
        yield "stackup", self.stackup.model_dump(exclude_none=True)
        yield "nets", self.nets.to_dict()
        yield "components", self.components.to_list()
        yield "padstacks", self.padstacks.model_dump(exclude_none=True, exclude_defaults=True, by_alias=False)
        yield "pin_groups", self.pin_groups.export_properties()
        yield "terminals", self.terminals.model_dump(exclude_none=True)["terminals"]
        yield "ports", self.ports.export_properties()
        yield "sources", self.sources.export_properties()
        yield "probes", self.probes.to_list()
        yield "setups", self.setups.model_dump(exclude_none=True)["setups"]
        yield "boundaries", self.boundaries.model_dump(exclude_none=True)
        yield "operations", self.operations.model_dump(exclude_none=True)
        yield "s_parameters", self.s_parameters.to_list()
        yield "spice_models", self.spice_models.to_list()
        yield "package_definitions", self.package_definitions.to_list()
        yield "variables", self.variables.model_dump(exclude_none=True)["variables"]
        yield "modeler", self.modeler.to_dict()

    def to_dict(self) -> dict:
        """Serialize the full configuration to a plain Python dictionary.

        Only sections that contain at least one value are included;
        empty sections (`{}`, `[]`, `None`) are silently omitted.

        Returns
        -------
        dict
            Configuration payload keyed by section name.

        Examples
        --------
        cfg = CfgData()
        cfg.nets.add_signal_nets(["SIG"])
        cfg.to_dict()
        """
        return {key: value for key, value in self._serialized_sections() if value not in ({}, [], None)}

    def to_json(self, file_path: Union[str, Path], indent: int = 4) -> Path:
        """Write the configuration to a JSON file.

        Parameters
        ----------
        file_path : str or Path
            Destination file path.
        indent : int, optional
            JSON indentation level.  Default is `4`.

        Returns
        -------
        Path
            Resolved path of the written file.

        Examples
        --------
        cfg.to_json("my_project_config.json")
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
            Destination file path.

        Returns
        -------
        Path
            Resolved path of the written file.

        Raises
        ------
        ImportError
            If the `toml` package is not installed.

        Examples
        --------
        cfg.to_toml("my_project_config.toml")
        """
        if not _TOML_AVAILABLE:
            raise ImportError("The 'toml' package is required to write TOML files. Install it with: pip install toml")
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as fh:
            toml.dump(self.to_dict(), fh)
        return file_path

    @classmethod
    def from_dict(cls, data: dict, pedb=None) -> "CfgData":
        """Create a :class:`CfgData` from an existing config dictionary.

        Parameters
        ----------
        data : dict
            Raw configuration dictionary.
        pedb : Edb, optional
            Live EDB session.

        Returns
        -------
        CfgData
            Populated instance.

        Examples
        --------
        cfg = CfgData.from_dict({"nets": {"signal_nets": ["CLK"]}})
        cfg.nets.signal_nets
        """
        return cls(pedb=pedb, **data)

    @classmethod
    def from_json(cls, file_path: Union[str, Path], pedb=None) -> "CfgData":
        """Load a :class:`CfgData` from a JSON file.

        Parameters
        ----------
        file_path : str or Path
            Path to a valid JSON configuration file.
        pedb : Edb, optional
            Live EDB session.

        Returns
        -------
        CfgData
            Populated instance.

        Examples
        --------
        cfg = CfgData.from_json("base_config.json")
        cfg.general.suppress_pads = True
        cfg.to_json("modified_config.json")
        """
        with open(file_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return cls.from_dict(data, pedb=pedb)

    @classmethod
    def from_toml(cls, file_path: Union[str, Path], pedb=None) -> "CfgData":
        """Load a :class:`CfgData` from a TOML file.

        Parameters
        ----------
        file_path : str or Path
            Path to a valid TOML configuration file.
        pedb : Edb, optional
            Live EDB session.

        Returns
        -------
        CfgData
            Populated instance.

        Raises
        ------
        ImportError
            If the `toml` package is not installed.

        Examples
        --------
        cfg = CfgData.from_toml("base_config.toml")
        """
        if not _TOML_AVAILABLE:
            raise ImportError("The 'toml' package is required to read TOML files. Install it with: pip install toml")
        with open(file_path, "r", encoding="utf-8") as fh:
            data = toml.load(fh)
        return cls.from_dict(data, pedb=pedb)
