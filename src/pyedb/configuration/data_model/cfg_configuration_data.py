from dataclasses import dataclass
import json

from dataclasses_json import dataclass_json

from pyedb.configuration.data_model.cfg_boundaries_data import CfgBoundaries
from pyedb.configuration.data_model.cfg_components_data import CfgComponents
from pyedb.configuration.data_model.cfg_general_data import CfgGeneral
from pyedb.configuration.data_model.cfg_nets_data import CfgNets
from pyedb.configuration.data_model.cfg_operations_data import CfgOperations
from pyedb.configuration.data_model.cfg_package_definition_data import (
    CfgPackageDefinitions,
)
from pyedb.configuration.data_model.cfg_padsatck_data import CfgPadStacks
from pyedb.configuration.data_model.cfg_pingroup_data import CfgPinGroups
from pyedb.configuration.data_model.cfg_ports_sources_data import CfgPorts, CfgSources
from pyedb.configuration.data_model.cfg_s_parameter_models_data import CfgSparameters
from pyedb.configuration.data_model.cfg_setup_data import CfgSetups
from pyedb.configuration.data_model.cfg_spice_models_data import CfgSpiceModels
from pyedb.configuration.data_model.cfg_stackup_data import CfgStackup


@dataclass_json
@dataclass
class Configuration:
    def __init__(self, pedb):
        self._pedb = pedb

    general: CfgGeneral = None
    boundaries: CfgBoundaries = None
    nets: CfgNets = None
    components: CfgComponents = None
    pin_groups: CfgPinGroups = None
    sources: CfgSources = None
    ports: CfgPorts = None
    setups: CfgSetups = None
    stackup: CfgStackup = None
    padstacks: CfgPadStacks = None
    s_parameters: CfgSparameters = None
    spice_models: CfgSpiceModels = None
    package_definitions: CfgPackageDefinitions = None
    operations: CfgOperations = None

    # TODO check for variables
    # TODO modeler
    # TODO probes

    def load_file(self, file_path):
        with open(file_path, "r") as file:
            data = json.load(file)
            self._pedb.configuration.components = CfgComponents(self._pedb).from_dict(data)
            self._pedb.configuration.general = CfgGeneral().from_dict(data)
            self._pedb.configuration.boundaries = CfgBoundaries().from_dict(data)
            self._pedb.configuration.nets = CfgNets.from_dict(data)
            self._pedb.configuration.pin_groups = CfgPinGroups().from_dict(data)
            self._pedb.configuration.sources = CfgSources.from_dict(data)
            self._pedb.configuration.ports = CfgPorts().from_dict(data)
            self._pedb.configuration.setups = CfgSetups().from_dict(data)
            self._pedb.configuration.stackup = CfgStackup().from_dict(data)
            self._pedb.configuration.padstacks = CfgPadStacks().from_dict(data)
            self._pedb.configuration.s_parameters = CfgSparameters().from_dict(data)
            self._pedb.configuration.spice_models = CfgSpiceModels().from_dict(data)
            self._pedb.configuration.package_definitions = CfgPackageDefinitions().from_dict(data)
            self._pedb.configuration.operations = CfgOperations().from_dict(data)

    def load_from_layout(self, filter=None):
        if not self.components:
            if not self._pedb.load_configuration_from_layout(filter=filter):
                raise ("Failed importing components from layout with configuration.", Exception)
