"""Tests related to Edb
"""

import pytest

pytestmark = pytest.mark.system

class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, edbapp, local_scratch, target_path, target_path2, target_path4):
        self.edbapp = edbapp
        self.local_scratch = local_scratch
        self.target_path = target_path
        self.target_path2 = target_path2
        self.target_path4 = target_path4

    def test_create_coax_port_on_component_from_hfss(self):
        """Create a coaxial port on a component from its pin."""
        assert self.edbapp.hfss.create_coax_port_on_component("U1", "DDR4_DQS0_P")

    def test_layout_bounding_box(self):
        """Evaluate layout bounding box"""
        assert len(self.edbapp.get_bounding_box()) == 2
        assert self.edbapp.get_bounding_box() == [[-0.01426004895, -0.00455000106], [0.15010507444, 0.08000000002]]
