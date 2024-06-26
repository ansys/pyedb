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

from pyedb import Edb
from tests.conftest import desktop_version, local_path
from tests.legacy.system.conftest import test_subfolder

pytestmark = [pytest.mark.system, pytest.mark.legacy]


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, legacy_edb_app, local_scratch, target_path, target_path2, target_path4):
        self.edbapp = legacy_edb_app
        self.local_scratch = local_scratch
        self.target_path = target_path
        self.target_path2 = target_path2
        self.target_path4 = target_path4

    def test_nets_queries(self):
        """Evaluate nets queries"""
        assert len(self.edbapp.nets.netlist) > 0
        signalnets = self.edbapp.nets.signal
        assert not signalnets[list(signalnets.keys())[0]].is_power_ground
        assert len(list(signalnets[list(signalnets.keys())[0]].primitives)) > 0
        assert len(signalnets) > 2

        powernets = self.edbapp.nets.power
        assert len(powernets) > 2
        assert powernets["AVCC_1V3"].is_power_ground
        powernets["AVCC_1V3"].is_power_ground = False
        assert not powernets["AVCC_1V3"].is_power_ground
        powernets["AVCC_1V3"].is_power_ground = True
        assert powernets["AVCC_1V3"].name == "AVCC_1V3"
        assert powernets["AVCC_1V3"].is_power_ground
        assert len(list(powernets["AVCC_1V3"].components.keys())) > 0
        assert len(powernets["AVCC_1V3"].primitives) > 0

        assert self.edbapp.nets.find_or_create_net("GND")
        assert self.edbapp.nets.find_or_create_net(start_with="gn")
        assert self.edbapp.nets.find_or_create_net(start_with="g", end_with="d")
        assert self.edbapp.nets.find_or_create_net(end_with="d")
        assert self.edbapp.nets.find_or_create_net(contain="usb")
        assert self.edbapp.nets["AVCC_1V3"].extended_net is None
        self.edbapp.extended_nets.auto_identify_power()
        assert self.edbapp.nets["AVCC_1V3"].extended_net

    def test_nets_get_power_tree(self):
        """Evaluate nets get powertree."""
        OUTPUT_NET = "5V"
        GROUND_NETS = ["GND", "PGND"]
        (
            component_list,
            component_list_columns,
            net_group,
        ) = self.edbapp.nets.get_powertree(OUTPUT_NET, GROUND_NETS)
        assert component_list
        assert component_list_columns
        assert net_group

    def test_nets_delete(self):
        """Delete a net."""
        assert "JTAG_TDI" in self.edbapp.nets
        self.edbapp.nets["JTAG_TCK"].delete()
        nets_deleted = self.edbapp.nets.delete("JTAG_TDI")
        assert "JTAG_TDI" in nets_deleted
        assert "JTAG_TDI" not in self.edbapp.nets

    def test_nets_classify_nets(self):
        """Reassign power based on list of nets."""
        assert "SFPA_SDA" in self.edbapp.nets.signal
        assert "SFPA_SCL" in self.edbapp.nets.signal
        assert "SFPA_VCCR" in self.edbapp.nets.power

        assert self.edbapp.nets.classify_nets(["SFPA_SDA", "SFPA_SCL"], ["SFPA_VCCR"])
        assert "SFPA_SDA" in self.edbapp.nets.power
        assert "SFPA_SDA" not in self.edbapp.nets.signal
        assert "SFPA_SCL" in self.edbapp.nets.power
        assert "SFPA_SCL" not in self.edbapp.nets.signal
        assert "SFPA_VCCR" not in self.edbapp.nets.power
        assert "SFPA_VCCR" in self.edbapp.nets.signal

        assert self.edbapp.nets.classify_nets(["SFPA_VCCR"], ["SFPA_SDA", "SFPA_SCL"])
        assert "SFPA_SDA" in self.edbapp.nets.signal
        assert "SFPA_SCL" in self.edbapp.nets.signal
        assert "SFPA_VCCR" in self.edbapp.nets.power

    def test_nets_arc_data(self):
        """Evaluate primitive arc data."""
        assert len(self.edbapp.nets["1.2V_DVDDL"].primitives[0].arcs) > 0
        assert self.edbapp.nets["1.2V_DVDDL"].primitives[0].arcs[0].start
        assert self.edbapp.nets["1.2V_DVDDL"].primitives[0].arcs[0].end
        assert self.edbapp.nets["1.2V_DVDDL"].primitives[0].arcs[0].height

    @pytest.mark.slow
    def test_nets_dc_shorts(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        dc_shorts = edbapp.layout_validation.dc_shorts()
        assert dc_shorts
        edbapp.nets.nets["DDR4_A0"].name = "DDR4$A0"
        edbapp.layout_validation.illegal_net_names(True)
        edbapp.layout_validation.illegal_rlc_values(True)

        # assert len(dc_shorts) == 20
        assert ["SFPA_Tx_Fault", "PCIe_Gen4_CLKREQ_L"] in dc_shorts
        assert ["VDD_DDR", "GND"] in dc_shorts
        assert len(edbapp.nets["DDR4_DM3"].find_dc_short()) > 0
        edbapp.nets["DDR4_DM3"].find_dc_short(True)
        assert len(edbapp.nets["DDR4_DM3"].find_dc_short()) == 0
        edbapp.close()

    def test_nets_eligible_power_nets(self):
        """Evaluate eligible power nets."""
        assert "GND" in [i.name for i in self.edbapp.nets.eligible_power_nets()]

    def test_nets_merge_polygon(self):
        """Convert paths from net into polygons."""
        source_path = os.path.join(local_path, "example_models", test_subfolder, "test_merge_polygon.aedb")
        target_path = os.path.join(self.local_scratch.path, "test_merge_polygon", "test.aedb")
        self.local_scratch.copyfolder(source_path, target_path)
        edbapp = Edb(target_path, desktop_version)
        assert edbapp.nets.merge_nets_polygons(["net1", "net2"])
        edbapp.close_edb()

    def test_layout_auto_parametrization(self):
        source_path = os.path.join(local_path, "example_models", test_subfolder, "ANSYS-HSD_V1.aedb")
        target_path = os.path.join(self.local_scratch.path, "test_auto_parameters", "test.aedb")
        self.local_scratch.copyfolder(source_path, target_path)
        edbapp = Edb(target_path, desktop_version)
        edbapp.auto_parametrize_design(
            layers=True,
            layer_filter="1_Top",
            materials=False,
            via_holes=False,
            pads=False,
            antipads=False,
            traces=False,
        )
        assert "$1_Top_thick" in edbapp.variables
        edbapp.auto_parametrize_design(
            layers=True, materials=False, via_holes=False, pads=False, antipads=False, traces=False
        )
        assert len(list(edbapp.variables.keys())) == len(list(edbapp.stackup.stackup_layers.keys()))
        edbapp.auto_parametrize_design(
            layers=False,
            materials=True,
            via_holes=False,
            pads=False,
            antipads=False,
            traces=False,
            material_filter=["copper"],
        )
        assert "$sigma_copper" in edbapp.variables
        edbapp.auto_parametrize_design(
            layers=False, materials=True, via_holes=False, pads=False, antipads=False, traces=False
        )
        assert len(list(edbapp.variables.values())) == 26
        edbapp.auto_parametrize_design(
            layers=False, materials=False, via_holes=True, pads=False, antipads=False, traces=False
        )
        assert len(list(edbapp.variables.values())) == 65
        edbapp.auto_parametrize_design(
            layers=False, materials=False, via_holes=False, pads=True, antipads=False, traces=False
        )
        assert len(list(edbapp.variables.values())) == 469
        edbapp.auto_parametrize_design(
            layers=False, materials=False, via_holes=False, pads=False, antipads=True, traces=False
        )
        assert len(list(edbapp.variables.values())) == 469
        edbapp.auto_parametrize_design(
            layers=False,
            materials=False,
            via_holes=False,
            pads=False,
            antipads=False,
            traces=True,
            trace_net_filter=["SFPA_Tx_Fault", "SFPA_Tx_Disable", "SFPA_SDA", "SFPA_SCL", "SFPA_Rx_LOS"],
        )
        assert len(list(edbapp.variables.keys())) == 474
        edbapp.auto_parametrize_design(
            layers=False, materials=False, via_holes=False, pads=False, antipads=False, traces=True
        )
        assert len(list(edbapp.variables.values())) == 2308
        edbapp.close_edb()
