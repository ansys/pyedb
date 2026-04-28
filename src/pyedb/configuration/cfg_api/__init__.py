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
Expose the programmatic configuration-builder API.

Import :class:`EdbConfigBuilder` together with the section builders you need to
assemble a complete pyedb configuration in Python before exporting it to a
dictionary, JSON file, or TOML file.

Examples
--------
>>> from pyedb.configuration.cfg_api import EdbConfigBuilder, TerminalInfo
>>> cfg = EdbConfigBuilder()
>>> cfg.nets.add_signal_nets(["SIG1"])
>>> cfg.ports.add_circuit_port(
...     "p1",
...     positive_terminal=TerminalInfo.net("SIG1"),
...     negative_terminal=TerminalInfo.nearest_pin("GND"),
... )

"""

from __future__ import annotations

from pyedb.configuration.cfg_api._builder import EdbConfigBuilder  # noqa: F401
from pyedb.configuration.cfg_api.boundaries import BoundariesConfig  # noqa: F401
from pyedb.configuration.cfg_api.components import ComponentConfig, ComponentsConfig, PinPairModel  # noqa: F401
from pyedb.configuration.cfg_api.general import GeneralConfig  # noqa: F401
from pyedb.configuration.cfg_api.modeler import ModelerConfig  # noqa: F401
from pyedb.configuration.cfg_api.nets import NetsConfig  # noqa: F401
from pyedb.configuration.cfg_api.operations import CutoutConfig, OperationsConfig  # noqa: F401
from pyedb.configuration.cfg_api.package_definitions import (  # noqa: F401
    HeatSinkConfig,
    PackageDefinitionConfig,
    PackageDefinitionsConfig,
)
from pyedb.configuration.cfg_api.padstacks import (  # noqa: F401
    PadstackDefinitionConfig,
    PadstackInstanceConfig,
    PadstacksConfig,
)
from pyedb.configuration.cfg_api.pin_groups import PinGroupConfig, PinGroupsConfig  # noqa: F401
from pyedb.configuration.cfg_api.ports import DiffWavePortConfig, EdgePortConfig, PortConfig, PortsConfig  # noqa: F401
from pyedb.configuration.cfg_api.probes import ProbeConfig, ProbesConfig  # noqa: F401
from pyedb.configuration.cfg_api.s_parameters import (  # noqa: F401
    SParameterModelConfig,
    SParameterModelsConfig,
    SParametersConfig,
)
from pyedb.configuration.cfg_api.setups import (  # noqa: F401
    FrequencySweepConfig,
    HfssSetupConfig,
    SetupsConfig,
    SIwaveACSetupConfig,
    SIwaveDCSetupConfig,
)
from pyedb.configuration.cfg_api.sources import SourceConfig, SourcesConfig  # noqa: F401
from pyedb.configuration.cfg_api.spice_models import SpiceModelConfig, SpiceModelsConfig  # noqa: F401
from pyedb.configuration.cfg_api.stackup import LayerConfig, MaterialConfig, StackupConfig  # noqa: F401
from pyedb.configuration.cfg_api.terminals import (  # noqa: F401
    BundleTerminal,
    EdgeTerminal,
    PadstackInstanceTerminal,
    PinGroupTerminal,
    PointTerminal,
    TerminalInfo,
    TerminalsConfig,
)
from pyedb.configuration.cfg_api.variables import VariablesConfig  # noqa: F401

__all__ = [
    "BoundariesConfig",
    "BundleTerminal",
    "ComponentConfig",
    "ComponentsConfig",
    "CutoutConfig",
    "DiffWavePortConfig",
    "EdbConfigBuilder",
    "EdgePortConfig",
    "EdgeTerminal",
    "FrequencySweepConfig",
    "GeneralConfig",
    "HeatSinkConfig",
    "HfssSetupConfig",
    "LayerConfig",
    "MaterialConfig",
    "ModelerConfig",
    "NetsConfig",
    "OperationsConfig",
    "PackageDefinitionConfig",
    "PackageDefinitionsConfig",
    "PadstackDefinitionConfig",
    "PadstackInstanceConfig",
    "PadstackInstanceTerminal",
    "PadstacksConfig",
    "PinGroupConfig",
    "PinGroupTerminal",
    "PinGroupsConfig",
    "PinPairModel",
    "PointTerminal",
    "PortConfig",
    "PortsConfig",
    "ProbeConfig",
    "ProbesConfig",
    "SIwaveACSetupConfig",
    "SIwaveDCSetupConfig",
    "SParameterModelConfig",
    "SParameterModelsConfig",
    "SParametersConfig",
    "SetupsConfig",
    "SourceConfig",
    "SourcesConfig",
    "SpiceModelConfig",
    "SpiceModelsConfig",
    "StackupConfig",
    "TerminalInfo",
    "TerminalsConfig",
    "VariablesConfig",
]
