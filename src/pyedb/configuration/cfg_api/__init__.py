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
"""cfg_api package – programmatic pyedb configuration builder.

Import :class:`EdbConfigBuilder` and any helpers you need directly from here::

   >>> from pyedb.configuration.cfg_api import EdbConfigBuilder, TerminalInfo
"""
from __future__ import annotations

from pyedb.configuration.cfg_api.general import GeneralConfig  # noqa: F401
from pyedb.configuration.cfg_api.stackup import LayerConfig, MaterialConfig, StackupConfig  # noqa: F401
from pyedb.configuration.cfg_api.nets import NetsConfig  # noqa: F401
from pyedb.configuration.cfg_api.components import ComponentConfig, ComponentsConfig, PinPairModel  # noqa: F401
from pyedb.configuration.cfg_api.padstacks import PadstackDefinitionConfig, PadstackInstanceConfig, PadstacksConfig  # noqa: F401
from pyedb.configuration.cfg_api.pin_groups import PinGroupConfig, PinGroupsConfig  # noqa: F401
from pyedb.configuration.cfg_api.terminals import (  # noqa: F401
    BundleTerminal,
    EdgeTerminal,
    PadstackInstanceTerminal,
    PinGroupTerminal,
    PointTerminal,
    TerminalInfo,
    TerminalsConfig,
)
from pyedb.configuration.cfg_api.ports import DiffWavePortConfig, EdgePortConfig, PortConfig, PortsConfig  # noqa: F401
from pyedb.configuration.cfg_api.sources import SourceConfig, SourcesConfig  # noqa: F401
from pyedb.configuration.cfg_api.probes import ProbeConfig, ProbesConfig  # noqa: F401
from pyedb.configuration.cfg_api.setups import (  # noqa: F401
    FrequenciesConfig,
    FrequencySweepConfig,
    HfssSetupConfig,
    SIwaveACSetupConfig,
    SIwaveDCSetupConfig,
    SetupsConfig,
)
from pyedb.configuration.cfg_api.boundaries import BoundariesConfig  # noqa: F401
from pyedb.configuration.cfg_api.operations import CutoutConfig, OperationsConfig  # noqa: F401
from pyedb.configuration.cfg_api.s_parameters import SParameterModelConfig, SParameterModelsConfig, SParametersConfig  # noqa: F401
from pyedb.configuration.cfg_api.spice_models import SpiceModelConfig, SpiceModelsConfig  # noqa: F401
from pyedb.configuration.cfg_api.package_definitions import HeatSinkConfig, PackageDefinitionConfig, PackageDefinitionsConfig  # noqa: F401
from pyedb.configuration.cfg_api.variables import VariablesConfig  # noqa: F401
from pyedb.configuration.cfg_api.modeler import ModelerConfig  # noqa: F401
from pyedb.configuration.cfg_api._builder import EdbConfigBuilder  # noqa: F401

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
    "FrequenciesConfig",
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
