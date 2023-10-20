import pytest
from mock import PropertyMock, patch, MagicMock
from pyedb.legacy.edb_core.padstack import EdbPadstacks

pytestmark = [pytest.mark.unit, pytest.mark.no_licence]

class TestClass:
    @pytest.fixture(autouse=True)
    def init(self):
        self.padstacks = EdbPadstacks(MagicMock())

    # for padstack_def in list(self.definitions.values()):
    #         if padstack_def.hole_plating_ratio <= minimum_value_to_replace:
    #             padstack_def.hole_plating_ratio = default_plating_ratio
    #             self._logger.info(
    #                 "Padstack definition with zero plating ratio, defaulting to 20%".format(padstack_def.name)
    #             )
    # def test_132_via_plating_ratio_check(self):
    #     assert self.edbapp.padstacks.check_and_fix_via_plating()
        # minimum_value_to_replace=0.0, default_plating_ratio=0.2

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
