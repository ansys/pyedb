from dataclasses import dataclass
import json

from dataclasses_json import dataclass_json

from pyedb.configuration.data_model.cfg_boundaries_data import CfgBoundaries
from pyedb.configuration.data_model.cfg_components_data import CfgComponent
from pyedb.configuration.data_model.cfg_general_data import CfgGeneral
from pyedb.configuration.data_model.cfg_nets_data import CfgNets
from pyedb.configuration.data_model.cfg_operations_data import CfgOperations
from pyedb.configuration.data_model.cfg_package_definition_data import (
    CfgPackageDefinition,
)
from pyedb.configuration.data_model.cfg_padsatck_data import CfgPadStacks
from pyedb.configuration.data_model.cfg_pingroup_data import CfgPinGroup
from pyedb.configuration.data_model.cfg_ports_sources_data import CfgPort, CfgSource
from pyedb.configuration.data_model.cfg_s_parameter_models_data import CfgSparameter
from pyedb.configuration.data_model.cfg_setup_data import CfgSetup
from pyedb.configuration.data_model.cfg_spice_models_data import CfgSpiceModel
from pyedb.configuration.data_model.cfg_stackup_data import CfgStackup


@dataclass_json
@dataclass
class Configuration:
    def __init__(self, pedb):
        self._pedb = pedb

    general: CfgGeneral = None
    boundaries: CfgBoundaries = None
    nets: CfgNets = None
    components: list[CfgComponent] = None
    pin_groups: list[CfgPinGroup] = None
    sources: list[CfgSource] = None
    ports: list[CfgPort] = None
    setups: list[CfgSetup] = None
    stackup: CfgStackup = None
    padstacks: CfgPadStacks = None
    s_parameters: list[CfgSparameter] = None
    spice_models: list[CfgSpiceModel] = None
    package_definitions: list[CfgPackageDefinition] = None
    operations: CfgOperations = None

    # TODO check for variables
    # TODO modeler
    # TODO probes

    def load_file(self, file_path):
        with open(file_path, "r") as file:
            data = json.load(file)
            self._pedb.configuration.general = CfgGeneral().from_dict(data)
            self._pedb.configuration.boundaries = CfgBoundaries().from_dict(data)
            self._pedb.configuration.nets = CfgNets.from_dict(data)
            self._pedb.configuration.components = [CfgComponent().from_dict(cmp) for cmp in data.get("components", [])]
            self._pedb.configuration.pin_groups = [CfgPinGroup().from_dict(pg) for pg in data.get("pin_groups", [])]
            self._pedb.configuration.sources = [CfgSource().from_dict(src) for src in data.get("sources", [])]
            self._pedb.configuration.ports = [CfgPort().from_dict(port) for port in data.get("ports", [])]
            self._pedb.configuration.setups = [CfgSetup().from_dict(setup) for setup in data.get("setups", [])]
            self._pedb.configuration.stackup = CfgStackup().from_dict(data)
            self._pedb.configuration.padstacks = CfgPadStacks().from_dict(data)
            self._pedb.configuration.s_parameters = [
                CfgSparameter().from_dict(sp) for sp in data.get("s_parameters", [])
            ]
            self._pedb.configuration.spice_models = [
                CfgSpiceModel().from_dict(sp) for sp in data.get("spice_models", [])
            ]
            self._pedb.configuration.package_definitions = [
                CfgPackageDefinition().from_dict(pkg) for pkg in data.get("package_definitions", [])
            ]
            self._pedb.configuration.operations = CfgOperations().from_dict(data)

    def export_configuration_file(self, file_path):
        data = self._pedb.configuration.to_dict()
        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)

    def load_from_layout(self, filter=None):
        self._pedb.logger.info("Loading nets")
        self._pedb.nets.load_configuration_from_layout(filter=filter)

        self._pedb.logger.info("Loading components")
        self._pedb.components.load_configuration_from_layout(filter=filter)

        self._pedb.logger.info("Loading pin groups")
        self._pedb.layout.load_pingroup_configuration_from_layout()

        self._pedb.logger.info("Loading sources")
        self._pedb.source_excitation.load_sources_configuration_from_layout()

        self._pedb.logger.info("Loading ports")
        self._pedb.source_excitation.load_ports_configuration_from_layout()

        self._pedb.logger.info("Loading setups")
        self._pedb.load_simulation_setup_configuration_from_layout()

        self._pedb.logger.info("Loading stackup")
        self._pedb.stackup.load_configuration_from_layout()

        self._pedb.logger.info("Loading padstacks")
        self._pedb.padstacks.load_configuration_from_layout()
