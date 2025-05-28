from dataclasses import dataclass

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


@dataclass
class Configuration:
    general = CfgGeneral()
    boundaries = CfgBoundaries()
    nets = CfgNets()
    components = CfgComponents()
    pin_groups = CfgPinGroups()
    sources: CfgSources
    ports: CfgPorts
    setups: CfgSetups
    stackup: CfgStackup
    padstacks: CfgPadStacks
    s_parameters: CfgSparameters
    spice_models: CfgSpiceModels
    package_definitions: CfgPackageDefinitions
    operations: CfgOperations
    # TODO check for variables
    # TODO modeler
    # TODO probes
