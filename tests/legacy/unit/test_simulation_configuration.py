import os

import pytest

from pyedb.dotnet.edb_core.edb_data.simulation_configuration import (
    SimulationConfiguration,
)
from pyedb.generic.constants import SourceType

pytestmark = [pytest.mark.unit, pytest.mark.no_licence, pytest.mark.legacy]


class TestClass:
    @pytest.fixture(autouse=True)
    def init(
        self,
        local_scratch,
    ):
        self.local_scratch = local_scratch

    def test_simulation_configuration_export_import(self):
        """Export and import simulation file."""
        sim_config = SimulationConfiguration()
        assert sim_config.output_aedb is None
        sim_config.output_aedb = os.path.join(self.local_scratch.path, "test.aedb")
        assert sim_config.output_aedb == os.path.join(self.local_scratch.path, "test.aedb")
        json_file = os.path.join(self.local_scratch.path, "test.json")
        sim_config._filename = json_file
        sim_config.arc_angle = "90deg"
        assert sim_config.export_json(json_file)

        test_0import = SimulationConfiguration()
        assert test_0import.import_json(json_file)
        assert test_0import.arc_angle == "90deg"
        assert test_0import._filename == json_file

    def test_simulation_configuration_add_rlc(self):
        """Add voltage source."""
        sim_config = SimulationConfiguration()
        sim_config.add_rlc(
            "test",
            r_value=1.5,
            c_value=1e-13,
            l_value=1e-10,
            positive_node_net="test_0net",
            positive_node_component="U2",
            negative_node_net="neg_net",
            negative_node_component="U2",
        )
        assert sim_config.sources
        assert sim_config.sources[0].source_type == SourceType.Rlc
        assert sim_config.sources[0].r_value == 1.5
        assert sim_config.sources[0].l_value == 1e-10
        assert sim_config.sources[0].c_value == 1e-13
