import pytest
from mock import Mock
from pyedb.legacy.edb_core.siwave import EdbSiwave

pytestmark = [pytest.mark.unit, pytest.mark.no_licence, pytest.mark.legacy]

class TestClass:
    @pytest.fixture(autouse=True)
    def init(self):
        self.siwave = EdbSiwave(Mock())

    def test_siwave_add_syz_analsyis(self):
        """Add a sywave AC analysis."""
        assert self.siwave.add_siwave_syz_analysis()
