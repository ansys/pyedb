import pytest

from pyedb.dotnet.edb_core.edb_data.sources import Source

pytestmark = [pytest.mark.unit, pytest.mark.no_licence, pytest.mark.legacy]


class TestClass:
    # @pytest.fixture(autouse=True)
    # def init(self,local_scratch,):
    #     self.local_scratch = local_scratch

    def test_source_change_values(self):
        """Create source and change its values"""
        source = Source()
        source.l_value = 1e-9
        assert source.l_value == 1e-9
        source.r_value = 1.3
        assert source.r_value == 1.3
        source.c_value = 1e-13
        assert source.c_value == 1e-13
        source.create_physical_resistor = True
        assert source.create_physical_resistor
