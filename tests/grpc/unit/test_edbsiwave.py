import os
import pytest
from mock import Mock

try:
    from pyedb.grpc.siwave import EdbSiwave
except ImportError:
    def pytest_collection_modifyitems(items, config):
        for item in items:
            item.add_marker(pytest.mark.xfail)

pytestmark = [pytest.mark.unit, pytest.mark.no_licence, pytest.mark.grpc]

class TestClass:
    @pytest.fixture(autouse=True)
    def init(self):
        self.edb = Mock()
        self.edb.edbpath = os.path.join(os.path.expanduser("~"), "fake_edb.aedb")
        self.siwave = EdbSiwave(self.edb)

    def test_siwave_add_syz_analsyis(self):
        """Add a sywave AC analysis."""
        assert self.siwave.add_siwave_syz_analysis()
