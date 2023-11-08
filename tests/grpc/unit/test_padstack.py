import pytest
from mock import PropertyMock, patch, MagicMock

try:
    from pyedb.grpc.padstack import EdbPadstacks
except ImportError:
    def pytest_collection_modifyitems(items, config):
        for item in items:
            item.add_marker(pytest.mark.xfail)

pytestmark = [pytest.mark.unit, pytest.mark.no_licence, pytest.mark.grpc]

class TestClass:
    @pytest.fixture(autouse=True)
    def init(self):
        self.padstacks = EdbPadstacks(MagicMock())

    @patch('pyedb.legacy.edb_core.padstack.EdbPadstacks.definitions', new_callable=PropertyMock)
    def test_padstack_plating_ratio_fixing(self, mock_definitions):
        """Fix hole plating ratio."""
        mock_definitions.return_value = {
            "definition_0": MagicMock(hole_plating_ratio = -0.1),
            "definition_1": MagicMock(hole_plating_ratio = 0.3)
        }
        assert self.padstacks["definition_0"].hole_plating_ratio == -0.1
        self.padstacks.check_and_fix_via_plating()
        assert self.padstacks["definition_0"].hole_plating_ratio == 0.2
        assert self.padstacks["definition_1"].hole_plating_ratio == 0.3
