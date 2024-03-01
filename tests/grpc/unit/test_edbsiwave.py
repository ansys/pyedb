import os

from mock import Mock
import pytest

from pyedb.dotnet.edb_core.siwave import EdbSiwave

pytestmark = [pytest.mark.unit, pytest.mark.no_licence, pytest.mark.legacy]


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self):
        self.edb = Mock()
        self.edb.edbpath = os.path.join(os.path.expanduser("~"), "fake_edb.aedb")
        self.siwave = EdbSiwave(self.edb)

    def test_siwave_add_syz_analsyis(self):
        """Add a sywave AC analysis."""
        assert self.siwave.add_siwave_syz_analysis()
