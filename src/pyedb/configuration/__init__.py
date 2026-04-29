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

"""Public configuration builders and aliases for :mod:`pyedb.configuration`."""

from pyedb.configuration.builder import EdbConfigBuilder  # noqa: F401
from pyedb.configuration.cfg_boundaries import CfgBoundaries as BoundariesConfig  # noqa: F401
from pyedb.configuration.cfg_common import CfgVariables as VariablesConfig  # noqa: F401
from pyedb.configuration.cfg_components import (  # noqa: F401
    CfgComponent as ComponentConfig,
    CfgComponents as ComponentsConfig,
    CfgPinPairModel as PinPairModel,
)
from pyedb.configuration.cfg_general import CfgGeneral as GeneralConfig  # noqa: F401
from pyedb.configuration.cfg_modeler import CfgModeler as ModelerConfig  # noqa: F401
from pyedb.configuration.cfg_nets import CfgNets as NetsConfig  # noqa: F401
from pyedb.configuration.cfg_operations import (  # noqa: F401
    CfgCutout as CutoutConfig,
    CfgOperations as OperationsConfig,
)
from pyedb.configuration.cfg_package_definition import (  # noqa: F401
    CfgHeatSink as HeatSinkConfig,
    CfgPackage as PackageDefinitionConfig,
    CfgPackageDefinitions as PackageDefinitionsConfig,
)
from pyedb.configuration.cfg_padstacks import (  # noqa: F401
    CfgPadstackDefinition as PadstackDefinitionConfig,
    CfgPadstackInstance as PadstackInstanceConfig,
    CfgPadstacks as PadstacksConfig,
)
from pyedb.configuration.cfg_pin_groups import (  # noqa: F401
    CfgPinGroup as PinGroupConfig,
    CfgPinGroups as PinGroupsConfig,
)
from pyedb.configuration.cfg_ports_sources import (  # noqa: F401
    CfgDiffWavePort as DiffWavePortConfig,
    CfgEdgePort as EdgePortConfig,
    CfgPort as PortConfig,
    CfgPorts as PortsConfig,
    CfgProbe as ProbeConfig,
    CfgProbes as ProbesConfig,
    CfgSource as SourceConfig,
    CfgSources as SourcesConfig,
    CfgTerminalInfo as TerminalInfo,
)
from pyedb.configuration.cfg_s_parameter_models import (  # noqa: F401
    CfgSParameterModel as SParameterModelConfig,
    CfgSParameters as SParameterModelsConfig,
)
from pyedb.configuration.cfg_setup import (  # noqa: F401
    CfgHFSSSetup as HfssSetupConfig,
    CfgSetupAC,
    CfgSetups as SetupsConfig,
    CfgSIwaveACSetup as SIwaveACSetupConfig,
    CfgSIwaveDCSetup as SIwaveDCSetupConfig,
)
from pyedb.configuration.cfg_spice_models import (  # noqa: F401
    CfgSpiceModel as SpiceModelConfig,
    CfgSpiceModels as SpiceModelsConfig,
)
from pyedb.configuration.cfg_stackup import (  # noqa: F401
    CfgLayer as LayerConfig,
    CfgMaterial as MaterialConfig,
    CfgStackup as StackupConfig,
)
from pyedb.configuration.cfg_terminals import (  # noqa: F401
    CfgBundleTerminal as BundleTerminal,
    CfgEdgeTerminal as EdgeTerminal,
    CfgPadstackInstanceTerminal as PadstackInstanceTerminal,
    CfgPinGroupTerminal as PinGroupTerminal,
    CfgPointTerminal as PointTerminal,
    CfgTerminals as TerminalsConfig,
)

FrequencySweepConfig = CfgSetupAC.CfgFrequencySweep
SParametersConfig = SParameterModelsConfig
