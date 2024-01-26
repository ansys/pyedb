from pyedb.configuration.data.component_data import Component
from pyedb.configuration.data.port_data import Port
from pyedb.configuration.data.source_data import Source
from pyedb.configuration.data.simulation_setup import SimulationSetup
from pyedb.configuration.data.stackup_data import Stackup


class Configuration:
    def __init__(self):
        self.components = [Component]
        self.ports = [Port]
        self.sources = [Source]
        self.simulation_setups = [SimulationSetup]
        self.stackup = Stackup()
