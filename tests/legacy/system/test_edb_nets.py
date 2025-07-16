# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Tests related to Edb nets
"""

import os

import pytest

from pyedb.generic.design_types import Edb
from tests.conftest import desktop_version, local_path, test_subfolder

pytestmark = [pytest.mark.system, pytest.mark.legacy]


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, local_scratch, target_path, target_path2, target_path4):
        self.local_scratch = local_scratch
        self.target_path = target_path
        self.target_path2 = target_path2
        self.target_path4 = target_path4

    def test_nets_queries(self, edb_examples):
        """Evaluate nets queries"""
        # Done
        edbapp = edb_examples.get_si_verse()
        assert len(edbapp.nets.netlist) > 0
        signalnets = edbapp.nets.signal
        assert not signalnets[list(signalnets.keys())[0]].is_power_ground
        assert len(list(signalnets[list(signalnets.keys())[0]].primitives)) > 0
        assert len(signalnets) > 2

        powernets = edbapp.nets.power
        assert len(powernets) > 2
        assert powernets["AVCC_1V3"].is_power_ground
        powernets["AVCC_1V3"].is_power_ground = False
        assert not powernets["AVCC_1V3"].is_power_ground
        powernets["AVCC_1V3"].is_power_ground = True
        assert powernets["AVCC_1V3"].name == "AVCC_1V3"
        assert powernets["AVCC_1V3"].is_power_ground
        assert len(list(powernets["AVCC_1V3"].components.keys())) > 0
        assert len(powernets["AVCC_1V3"].primitives) > 0

        assert edbapp.nets.find_or_create_net("GND")
        assert edbapp.nets.find_or_create_net(start_with="gn")
        assert edbapp.nets.find_or_create_net(start_with="g", end_with="d")
        assert edbapp.nets.find_or_create_net(end_with="d")
        assert edbapp.nets.find_or_create_net(contain="usb")
        assert not edbapp.nets.nets["AVCC_1V3"].extended_net
        edbapp.extended_nets.auto_identify_power()
        assert edbapp.nets.nets["AVCC_1V3"].extended_net
        edbapp.close()

    def test_nets_get_power_tree(self, edb_examples):
        """Evaluate nets get powertree."""
        # Done
        edbapp = edb_examples.get_si_verse()
        OUTPUT_NET = "5V"
        GROUND_NETS = ["GND", "PGND"]
        (
            component_list,
            component_list_columns,
            net_group,
        ) = edbapp.nets.get_powertree(OUTPUT_NET, GROUND_NETS)
        assert component_list
        assert component_list_columns
        assert net_group
        edbapp.close()

    def test_nets_delete(self, edb_examples):
        """Delete a net."""
        # Done
        edbapp = edb_examples.get_si_verse()
        assert "JTAG_TCK" in edbapp.nets.nets
        edbapp.nets.nets["JTAG_TCK"].delete()
        assert "JTAG_TCK" not in edbapp.nets.nets
        edbapp.close()

    def test_nets_classify_nets(self, edb_examples):
        """Reassign power based on list of nets."""
        # Done
        edbapp = edb_examples.get_si_verse()
        assert "SFPA_SDA" in edbapp.nets.signal
        assert "SFPA_SCL" in edbapp.nets.signal
        assert "SFPA_VCCR" in edbapp.nets.power

        assert edbapp.nets.classify_nets(["SFPA_SDA", "SFPA_SCL"], ["SFPA_VCCR"])
        assert "SFPA_SDA" in edbapp.nets.power
        assert "SFPA_SDA" not in edbapp.nets.signal
        assert "SFPA_SCL" in edbapp.nets.power
        assert "SFPA_SCL" not in edbapp.nets.signal
        assert "SFPA_VCCR" not in edbapp.nets.power
        assert "SFPA_VCCR" in edbapp.nets.signal

        assert edbapp.nets.classify_nets(["SFPA_VCCR"], ["SFPA_SDA", "SFPA_SCL"])
        assert "SFPA_SDA" in edbapp.nets.signal
        assert "SFPA_SCL" in edbapp.nets.signal
        assert "SFPA_VCCR" in edbapp.nets.power
        edbapp.close()

    def test_nets_arc_data(self, edb_examples):
        """Evaluate primitive arc data."""
        # Done
        edbapp = edb_examples.get_si_verse()
        assert len(edbapp.nets.nets["1.2V_DVDDL"].primitives[0].arcs) > 0
        assert edbapp.nets.nets["1.2V_DVDDL"].primitives[0].arcs[0].start
        assert edbapp.nets.nets["1.2V_DVDDL"].primitives[0].arcs[0].end
        assert edbapp.nets.nets["1.2V_DVDDL"].primitives[0].arcs[0].height
        edbapp.close()

    @pytest.mark.slow
    def test_nets_dc_shorts(self, edb_examples):
        # TODO get_connected_object return empty list.
        edbapp = edb_examples.get_si_verse()
        # dc_shorts = edbapp.layout_validation.dc_shorts()
        # assert dc_shorts
        # edbapp.nets.nets["DDR4_A0"].name = "DDR4$A0"
        # edbapp.layout_validation.illegal_net_names(True)
        # edbapp.layout_validation.illegal_rlc_values(True)
        #
        # # assert len(dc_shorts) == 20
        # assert ["SFPA_Tx_Fault", "PCIe_Gen4_CLKREQ_L"] in dc_shorts
        # assert ["VDD_DDR", "GND"] in dc_shorts
        # assert len(edbapp.nets["DDR4_DM3"].find_dc_short()) > 0
        # edbapp.nets["DDR4_DM3"].find_dc_short(True)
        # assert len(edbapp.nets["DDR4_DM3"].find_dc_short()) == 0
        edbapp.close()

    def test_nets_eligible_power_nets(self, edb_examples):
        """Evaluate eligible power nets."""
        # Done
        edbapp = edb_examples.get_si_verse()
        assert "GND" in [i.name for i in edbapp.nets.eligible_power_nets()]
        edbapp.close()

    def test_nets_merge_polygon(self):
        """Convert paths from net into polygons."""
        # Done
        source_path = os.path.join(local_path, "example_models", test_subfolder, "test_merge_polygon.aedb")
        target_path = os.path.join(self.local_scratch.path, "test_merge_polygon", "test.aedb")
        self.local_scratch.copyfolder(source_path, target_path)
        edbapp = Edb(edbpath=target_path, edbversion=desktop_version)
        assert edbapp.nets.merge_nets_polygons(["net1", "net2"])
        edbapp.close()

    def test_layout_auto_parametrization_0(self, edb_examples):
        # Done
        edbapp = edb_examples.get_si_verse()
        parameters = edbapp.auto_parametrize_design(
            layers=True,
            layer_filter="1_Top",
            materials=False,
            via_holes=False,
            pads=False,
            antipads=False,
            traces=False,
            use_relative_variables=False,
            open_aedb_at_end=False,
        )
        assert "$1_Top_value" in parameters
        edbapp.close_edb()

    def test_layout_auto_parametrization_1(self, edb_examples):
        # Done
        edbapp = edb_examples.get_si_verse()
        edbapp.auto_parametrize_design(
            layers=True, materials=False, via_holes=False, pads=False, antipads=False, traces=False, via_offset=False
        )
        assert len(list(edbapp.variables.keys())) == len(list(edbapp.stackup.layers.keys()))
        edbapp.close()

    def test_layout_auto_parametrization_2(self, edb_examples):
        # Done
        edbapp = edb_examples.get_si_verse()
        edbapp.auto_parametrize_design(
            layers=False,
            materials=True,
            via_holes=False,
            pads=False,
            antipads=False,
            traces=False,
            material_filter=["copper"],
            expand_voids_size=0.0001,
            expand_polygons_size=0.0001,
            via_offset=True,
        )
        assert "via_offset_x" in edbapp.variables
        assert "$sigma_copper_delta" in edbapp.variables
        edbapp.close()

    def test_layout_auto_parametrization_3(self, edb_examples):
        # Done
        edbapp = edb_examples.get_si_verse()
        edbapp.auto_parametrize_design(
            layers=False, materials=True, via_holes=False, pads=False, antipads=False, traces=False
        )
        assert len(list(edbapp.variables.values())) == 13
        edbapp.close_edb()

    def test_layout_auto_parametrization_4(self, edb_examples):
        # Done
        edbapp = edb_examples.get_si_verse()
        edbapp.auto_parametrize_design(
            layers=False, materials=False, via_holes=True, pads=False, antipads=False, traces=False
        )
        assert len(list(edbapp.variables.values())) == 3
        edbapp.close()

    def test_layout_auto_parametrization_5(self, edb_examples):
        # Done
        edbapp = edb_examples.get_si_verse()
        edbapp.auto_parametrize_design(
            layers=False, materials=False, via_holes=False, pads=True, antipads=False, traces=False
        )
        assert len(list(edbapp.variables.values())) == 5
        edbapp.close_edb()

    def test_layout_auto_parametrization_6(self, edb_examples):
        # Done
        edbapp = edb_examples.get_si_verse()
        edbapp.auto_parametrize_design(
            layers=False, materials=False, via_holes=False, pads=False, antipads=True, traces=False
        )
        assert len(list(edbapp.variables.values())) == 2
        edbapp.close_edb()

    def test_layout_auto_parametrization_7(self, edb_examples):
        # Done
        edbapp = edb_examples.get_si_verse()
        edbapp.auto_parametrize_design(
            layers=False,
            materials=False,
            via_holes=False,
            pads=False,
            antipads=False,
            traces=True,
            trace_net_filter=["SFPA_Tx_Fault", "SFPA_Tx_Disable", "SFPA_SDA", "SFPA_SCL", "SFPA_Rx_LOS"],
        )
        assert len(list(edbapp.variables.keys())) == 3
        edbapp.close_edb()
