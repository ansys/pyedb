# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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
from pyedb.configuration.cfg_spice_models import CfgSpiceModel
from pyedb.configuration.cfg_stackup import CfgStackup
from pyedb.configuration.cfg_terminals import CfgTerminals


class CfgData(object):
    """Manages configure data."""

    def __init__(self, pedb, **kwargs):
        self._pedb = pedb
        self.general = CfgGeneral(self._pedb, kwargs.get("general", {}))

        self.boundaries = CfgBoundaries.create(**kwargs.get("boundaries", {}))

        self.nets = CfgNets(
            self._pedb,
            kwargs.get("nets", {}).get("signal_nets", []),
            kwargs.get("nets", {}).get("power_ground_nets", []),
        )

        self.components = CfgComponents(self._pedb, components_data=kwargs.get("components", []))

        self.padstacks = CfgPadstacks.create(**kwargs.get("padstacks", {}))

        self.pin_groups = CfgPinGroups(self._pedb, pingroup_data=kwargs.get("pin_groups", []))

        self.terminals = CfgTerminals.create(terminals=kwargs.get("terminals", []))

        self.ports = CfgPorts(self._pedb, ports_data=kwargs.get("ports", []))

        self.sources = CfgSources(self._pedb, sources_data=kwargs.get("sources", []))

        self.setups = CfgSetups(self._pedb, setups_data=kwargs.get("setups", []))

        self.stackup = CfgStackup(**kwargs.get("stackup", {}))

        self.s_parameters = CfgSParameters(self._pedb, kwargs.get("s_parameters", []), self.general.s_parameter_library)

        self.spice_models = [
            CfgSpiceModel(self, self.general.spice_model_library, spice_model)
            for spice_model in kwargs.get("spice_models", [])
        ]

        self.package_definitions = CfgPackageDefinitions(self._pedb, data=kwargs.get("package_definitions", []))
        self.operations = CfgOperations(**kwargs.get("operations", {}))

        self.modeler = CfgModeler(self._pedb, data=kwargs.get("modeler", {}))

        self.variables = CfgVariables(variables=kwargs.get("variables", []))

        self.probes = CfgProbes(self._pedb, data=kwargs.get("probes", []))
