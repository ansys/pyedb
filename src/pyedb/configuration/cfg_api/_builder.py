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

"""
Provide the top-level programmatic configuration builder.

This module gathers the section-specific builders exposed by ``cfg_api`` into a
single entry point that can serialize configuration data to dictionaries, JSON,
or TOML files.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Union

try:
    import toml

    _TOML_AVAILABLE = True
except ImportError:
    _TOML_AVAILABLE = False

from pyedb.configuration.cfg_api._utils import _DictProxy
from pyedb.configuration.cfg_api.boundaries import BoundariesConfig
from pyedb.configuration.cfg_api.components import ComponentsConfig
from pyedb.configuration.cfg_api.general import GeneralConfig
from pyedb.configuration.cfg_api.modeler import ModelerConfig
from pyedb.configuration.cfg_api.nets import NetsConfig
from pyedb.configuration.cfg_api.operations import OperationsConfig
from pyedb.configuration.cfg_api.package_definitions import PackageDefinitionsConfig
from pyedb.configuration.cfg_api.padstacks import PadstacksConfig
from pyedb.configuration.cfg_api.pin_groups import PinGroupsConfig
from pyedb.configuration.cfg_api.ports import PortsConfig
from pyedb.configuration.cfg_api.probes import ProbesConfig
from pyedb.configuration.cfg_api.s_parameters import SParameterModelsConfig
from pyedb.configuration.cfg_api.setups import (
    HfssSetupConfig,
    SetupsConfig,
)
from pyedb.configuration.cfg_api.sources import SourcesConfig
from pyedb.configuration.cfg_api.spice_models import SpiceModelsConfig
from pyedb.configuration.cfg_api.stackup import StackupConfig
from pyedb.configuration.cfg_api.terminals import TerminalsConfig
from pyedb.configuration.cfg_api.variables import VariablesConfig


class EdbConfigBuilder:
    """
    Top-level programmatic builder for a pyedb configuration.

    Instantiate this class, populate its sub-objects, and then either:

    * call :meth:`to_dict` to get a plain Python dictionary suitable for
      ``Configuration.load(cfg.to_dict(), apply_file=True)``;
    * call :meth:`to_json` / :meth:`to_toml` to write a config file.

    Sub-object attributes
    ---------------------
    general : GeneralConfig
        Paths (SPICE / S-param libraries) and design-level flags
        (``anti_pads_always_on``, ``suppress_pads``).
    stackup : StackupConfig
        Materials and layer definitions (signal, dielectric, roughness, etching).
    nets : NetsConfig
        Signal and power/ground net classification.
    components : ComponentsConfig
        Component models (RLC, S-parameter, SPICE, netlist), die & solder ball
        properties, port properties.
    padstacks : PadstacksConfig
        Padstack definitions and instances (including backdrill).
    pin_groups : PinGroupsConfig
        Named pin groups by explicit pin lists or net.
    terminals : TerminalsConfig
        Low-level EDB terminal objects (padstack-instance, pin-group, point,
        edge, bundle).  For most workflows, prefer using :class:`PortsConfig`
        and :class:`SourcesConfig` which create terminals implicitly.
    ports : PortsConfig
        Circuit, coax, wave, gap, and differential wave ports.
    sources : SourcesConfig
        Current and voltage sources.
    probes : ProbesConfig
        Voltage probes.
    setups : SetupsConfig
        HFSS, SIwave AC, and SIwave DC simulation setups with frequency sweeps
        and mesh operations.
    boundaries : BoundariesConfig
        HFSS open-region (radiation / PML), airbox extents, and dielectric
        extent settings.
    operations : OperationsConfig
        Post-processing operations (cutout, auto HFSS regions).
    s_parameters : SParameterModelsConfig
        N-port S-parameter model assignments to component definitions.
    spice_models : SpiceModelsConfig
        SPICE model assignments to component definitions.
    package_definitions : PackageDefinitionsConfig
        Thermal package definitions (maximum power, theta, heat sink fins).
    variables : VariablesConfig
        Design variables (name / value / description).
    modeler : ModelerConfig
        Traces, planes (rectangle / circle / polygon), padstack objects,
        per-modeler components, and primitives-to-delete.

    Quick-reference – terminal specifiers
    --------------------------------------
    Methods on :class:`PortsConfig`, :class:`SourcesConfig`, and
    :class:`ProbesConfig` accept *positive_terminal* / *negative_terminal*
    dicts.  Use :class:`TerminalInfo` factory methods instead of raw dicts:

    >>> from pyedb.configuration.cfg_api import EdbConfigBuilder, TerminalInfo
    >>> cfg = EdbConfigBuilder()
    >>> cfg.ports.add_circuit_port(
    ...     "p1",
    ...     positive_terminal=TerminalInfo.pin_group("pg_VDD"),
    ...     negative_terminal=TerminalInfo.pin_group("pg_GND"),
    ... )
    >>> cfg.sources.add_current_source(
    ...     "isrc1",
    ...     positive_terminal=TerminalInfo.net("VDD", reference_designator="U1"),
    ...     negative_terminal=TerminalInfo.nearest_pin("GND"),
    ... )

    Example – full workflow
    -----------------------
    >>> from pyedb.configuration.cfg_api import EdbConfigBuilder
    >>> cfg = EdbConfigBuilder()
    >>> cfg.general.anti_pads_always_on = False
    >>> cfg.stackup.add_material("copper", conductivity=5.8e7)
    >>> cfg.stackup.add_signal_layer("top", material="copper", thickness="35um")
    >>> cfg.nets.add_signal_nets(["SIG1", "SIG2"])
    >>> cfg.nets.add_power_ground_nets(["VDD", "GND"])
    >>> cfg.pin_groups.add("pg_VDD", "U1", net="VDD")
    >>> cfg.ports.add_circuit_port(
    ...     "p1", positive_terminal=TerminalInfo.pin_group("pg_VDD"), negative_terminal=TerminalInfo.nearest_pin("GND")
    ... )
    >>> hfss = cfg.setups.add_hfss_setup("my_hfss")
    >>> hfss.set_broadband_adaptive("1GHz", "10GHz")
    >>> sweep = hfss.add_frequency_sweep("sweep1")
    >>> sweep.add_linear_count_frequencies("1GHz", "10GHz", 100)
    >>> cfg.to_json("/path/to/config.json")
    >>> # Or apply directly:
    >>> # edb.configuration.load(cfg.to_dict(), apply_file=True)
    """

    def __init__(self):
        """Initialize all section builders with empty state."""
        self.general = GeneralConfig()
        self.stackup = StackupConfig()
        self.nets = NetsConfig()
        self.components = ComponentsConfig()
        self.padstacks = PadstacksConfig()
        self.pin_groups = PinGroupsConfig()
        self.terminals = TerminalsConfig()
        self.ports = PortsConfig()
        self.sources = SourcesConfig()
        self.probes = ProbesConfig()
        self.setups = SetupsConfig()
        self.boundaries = BoundariesConfig()
        self.operations = OperationsConfig()
        self.s_parameters = SParameterModelsConfig()
        self.spice_models = SpiceModelsConfig()
        self.package_definitions = PackageDefinitionsConfig()
        self.variables = VariablesConfig()
        self.modeler = ModelerConfig()

    def __repr__(self) -> str:  # pragma: no cover
        d = self.to_dict()
        sections = ", ".join(d.keys()) if d else "<empty>"
        return f"EdbConfigBuilder(sections=[{sections}])"

    def to_dict(self) -> dict:
        """
        Serialise the configuration to a plain Python dictionary.

        Returns
        -------
        dict
            Dictionary that can be passed directly to ``Configuration.load()``.

        """
        data: dict = {}

        general = self.general.to_dict()
        if general:
            data["general"] = general

        stackup = self.stackup.to_dict()
        if stackup:
            data["stackup"] = stackup

        nets = self.nets.to_dict()
        if nets:
            data["nets"] = nets

        components = self.components.to_list()
        if components:
            data["components"] = components

        padstacks = self.padstacks.to_dict()
        if padstacks:
            data["padstacks"] = padstacks

        pin_groups = self.pin_groups.to_list()
        if pin_groups:
            data["pin_groups"] = pin_groups

        terminals = self.terminals.to_list()
        if terminals:
            data["terminals"] = terminals

        ports = self.ports.to_list()
        if ports:
            data["ports"] = ports

        sources = self.sources.to_list()
        if sources:
            data["sources"] = sources

        probes = self.probes.to_list()
        if probes:
            data["probes"] = probes

        setups = self.setups.to_list()
        if setups:
            data["setups"] = setups

        boundaries = self.boundaries.to_dict()
        if boundaries:
            data["boundaries"] = boundaries

        operations = self.operations.to_dict()
        if operations:
            data["operations"] = operations

        s_params = self.s_parameters.to_list()
        if s_params:
            data["s_parameters"] = s_params

        spice = self.spice_models.to_list()
        if spice:
            data["spice_models"] = spice

        pkg_defs = self.package_definitions.to_list()
        if pkg_defs:
            data["package_definitions"] = pkg_defs

        variables = self.variables.to_list()
        if variables:
            data["variables"] = variables

        modeler = self.modeler.to_dict()
        if modeler:
            data["modeler"] = modeler

        return data

    def to_json(self, file_path: Union[str, Path], indent: int = 4) -> Path:
        """
        Write the configuration to a JSON file.

        Parameters
        ----------
        file_path : str or Path
            Destination path.
        indent : int
            JSON indentation level.

        Returns
        -------
        Path
            Resolved path of the written file.

        """
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as fh:
            json.dump(self.to_dict(), fh, indent=indent)
        return file_path

    def to_toml(self, file_path: Union[str, Path]) -> Path:
        """
        Write the configuration to a TOML file.

        Parameters
        ----------
        file_path : str or Path
            Destination path.

        Returns
        -------
        Path
            Resolved path of the written file.

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
        """
        Create an :class:`EdbConfigBuilder` from an existing config dictionary.

        This is primarily useful for reading an exported JSON/TOML config back
        into the programmatic API so it can be modified and re-exported.

        Parameters
        ----------
        data : dict
            Existing configuration dictionary.

        Returns
        -------
        EdbConfigBuilder
            Builder populated from ``data``.

        """
        builder = cls()

        # general
        for key, val in data.get("general", {}).items():
            if hasattr(builder.general, key):
                setattr(builder.general, key, val)

        # stackup
        for mat in data.get("stackup", {}).get("materials", []):
            mat = dict(mat)
            name = mat.pop("name")
            builder.stackup.add_material(name, **mat)
        for lyr in data.get("stackup", {}).get("layers", []):
            lyr = dict(lyr)
            name = lyr.pop("name")
            builder.stackup.add_layer(name, **lyr)

        # nets
        nets = data.get("nets", {})
        if nets.get("signal_nets"):
            builder.nets.add_signal_nets(nets["signal_nets"])
        if nets.get("power_ground_nets"):
            builder.nets.add_power_ground_nets(nets["power_ground_nets"])

        # components
        for comp in data.get("components", []):
            comp = dict(comp)
            refdes = comp.pop("reference_designator")
            c = builder.components.add(
                refdes,
                **{k: v for k, v in comp.items() if k in ("part_type", "enabled", "definition", "placement_layer")},
            )
            for key in (
                "pin_pair_model",
                "s_parameter_model",
                "spice_model",
                "netlist_model",
                "port_properties",
                "solder_ball_properties",
                "ic_die_properties",
            ):
                if comp.get(key):
                    setattr(c, key, comp[key])

        # padstacks
        for pdef in data.get("padstacks", {}).get("definitions", []):
            pdef = dict(pdef)
            name = pdef.pop("name")
            builder.padstacks.add_definition(name, **pdef)
        for pinst in data.get("padstacks", {}).get("instances", []):
            builder.padstacks.add_instance(**pinst)

        # pin_groups
        for pg in data.get("pin_groups", []):
            builder.pin_groups.add(**pg)

        # terminals
        for t in data.get("terminals", []):
            builder.terminals._terminals.append(_DictProxy(t))

        # ports
        for p in data.get("ports", []):
            builder.ports._ports.append(_DictProxy(p))

        # sources
        for s in data.get("sources", []):
            builder.sources._sources.append(_DictProxy(s))

        # probes
        for pr in data.get("probes", []):
            builder.probes._probes.append(_DictProxy(pr))

        # setups
        for stp in data.get("setups", []):
            stp_type = stp.get("type", "hfss")
            if stp_type == "hfss":
                h = builder.setups.add_hfss_setup(stp["name"])
                adapt = stp.get("adapt_type", "single")
                h.adapt_type = adapt
                if stp.get("single_frequency_adaptive_solution"):
                    sf = stp["single_frequency_adaptive_solution"]
                    h.single_frequency_adaptive_solution = HfssSetupConfig.CfgSingleFrequencyAdaptiveSolution(**sf)
                if stp.get("broadband_adaptive_solution"):
                    bb = stp["broadband_adaptive_solution"]
                    h.broadband_adaptive_solution = HfssSetupConfig.CfgBroadbandAdaptiveSolution(**bb)
                if stp.get("multi_frequency_adaptive_solution"):
                    mf = stp["multi_frequency_adaptive_solution"].get("adapt_frequencies", [])
                    h.multi_frequency_adaptive_solution.adapt_frequencies = [
                        (
                            HfssSetupConfig.CfgMultiFrequencyAdaptiveSolution.CfgAdaptFrequency(**f)
                            if isinstance(f, dict)
                            else f
                        )
                        for f in mf
                    ]
                if stp.get("auto_mesh_operation"):
                    h.auto_mesh_operation = HfssSetupConfig.CfgAutoMeshOperation(**stp["auto_mesh_operation"])
                for mo in stp.get("mesh_operations", []):
                    h.mesh_operations.append(
                        HfssSetupConfig.CfgLengthMeshOperation(**mo) if isinstance(mo, dict) else mo
                    )
                for sw in stp.get("freq_sweep", []):
                    sweep = h.add_frequency_sweep(sw["name"], sweep_type=sw.get("type", "interpolation"))
                    sweep.enforce_causality = sw.get("enforce_causality", False)
                    sweep.enforce_passivity = sw.get("enforce_passivity", True)
                    sweep.use_q3d_for_dc = sw.get("use_q3d_for_dc", False)
                    sweep.compute_dc_point = sw.get("compute_dc_point", False)
                    from pyedb.configuration.cfg_setup import CfgFrequencies

                    sweep.frequencies = [
                        CfgFrequencies(**f) if isinstance(f, dict) else f for f in sw.get("frequencies", [])
                    ]
            elif stp_type in ("siwave_ac", "siwave_syz"):
                s = builder.setups.add_siwave_ac_setup(
                    stp["name"],
                    si_slider_position=stp.get("si_slider_position", 1),
                    pi_slider_position=stp.get("pi_slider_position", 1),
                )
                for sw in stp.get("freq_sweep", []):
                    sweep = s.add_frequency_sweep(sw["name"], sweep_type=sw.get("type", "interpolation"))
                    from pyedb.configuration.cfg_setup import CfgFrequencies

                    sweep.frequencies = [
                        CfgFrequencies(**f) if isinstance(f, dict) else f for f in sw.get("frequencies", [])
                    ]
            elif stp_type == "siwave_dc":
                builder.setups.add_siwave_dc_setup(
                    stp["name"],
                    dc_slider_position=stp.get("dc_slider_position", 1),
                    export_dc_thermal_data=stp.get("dc_ir_settings", {}).get("export_dc_thermal_data", False),
                )

        # boundaries
        for k, v in data.get("boundaries", {}).items():
            setattr(builder.boundaries, k, v)

        # operations
        ops = data.get("operations", {})
        if "cutout" in ops:
            c = ops["cutout"]
            builder.operations._cutout = _DictProxy(c)
        if ops.get("generate_auto_hfss_regions"):
            builder.operations.generate_auto_hfss_regions = True

        # s_parameters
        for sp in data.get("s_parameters", []):
            builder.s_parameters._models.append(_DictProxy(sp))

        # spice_models
        for sm in data.get("spice_models", []):
            builder.spice_models._models.append(_DictProxy(sm))

        # package_definitions
        for pkg in data.get("package_definitions", []):
            builder.package_definitions._packages.append(_DictProxy(pkg))

        # variables
        for v in data.get("variables", []):
            builder.variables.add(v["name"], v["value"], v.get("description", ""))

        # modeler (pass-through – complex enough that direct proxy is fine)
        modeler_data = data.get("modeler", {})
        for trace in modeler_data.get("traces", []):
            builder.modeler._traces.append(trace)
        for plane in modeler_data.get("planes", []):
            builder.modeler._planes.append(plane)
        for pdef in modeler_data.get("padstack_definitions", []):
            builder.modeler._padstack_definitions.append(pdef)
        for pinst in modeler_data.get("padstack_instances", []):
            builder.modeler._padstack_instances.append(pinst)
        for comp in modeler_data.get("components", []):
            comp = dict(comp)
            refdes = comp.pop("reference_designator")
            c = builder.modeler.add_component(
                refdes,
                **{k: v for k, v in comp.items() if k in ("part_type", "enabled", "definition", "placement_layer")},
            )
            for key in (
                "pin_pair_model",
                "s_parameter_model",
                "spice_model",
                "netlist_model",
                "port_properties",
                "solder_ball_properties",
                "ic_die_properties",
            ):
                if comp.get(key):
                    setattr(c, key, comp[key])
        prim = modeler_data.get("primitives_to_delete", {})
        if prim.get("layer_name"):
            builder.modeler.delete_primitives_by_layer(prim["layer_name"])
        if prim.get("name"):
            builder.modeler.delete_primitives_by_name(prim["name"])
        if prim.get("net_name"):
            builder.modeler.delete_primitives_by_net(prim["net_name"])

        return builder

    @classmethod
    def from_json(cls, file_path: Union[str, Path]) -> "EdbConfigBuilder":
        """
        Load from a JSON file.

        Parameters
        ----------
        file_path : str or Path
            Path to a JSON configuration file.

        Returns
        -------
        EdbConfigBuilder
            Builder populated from the JSON file.

        """
        with open(file_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return cls.from_dict(data)

    @classmethod
    def from_toml(cls, file_path: Union[str, Path]) -> "EdbConfigBuilder":
        """
        Load from a TOML file.

        Parameters
        ----------
        file_path : str or Path
            Path to a TOML configuration file.

        Returns
        -------
        EdbConfigBuilder
            Builder populated from the TOML file.

        """
        if not _TOML_AVAILABLE:
            raise ImportError("The 'toml' package is required to read TOML files. Install it with: pip install toml")
        with open(file_path, "r", encoding="utf-8") as fh:
            data = toml.load(fh)
        return cls.from_dict(data)
