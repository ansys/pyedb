# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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
import os
from pathlib import Path

import pytest

from tests.conftest import local_path, test_subfolder
from tests.system.base_test_class import BaseTestClass

pytestmark = [pytest.mark.unit, pytest.mark.legacy]


class TestClass(BaseTestClass):
    @pytest.mark.skipif(True, reason="Unstable test.")
    def test_create_custom_cutout_0(self, edb_examples):
        """Create custom cutout 0."""
        # Done
        edbapp = edb_examples.get_si_verse()
        output = str(Path(edb_examples.test_folder) / "cutout.aedb")
        assert edbapp.cutout(
            ["DDR4_DQS0_P", "DDR4_DQS0_N"],
            ["GND"],
            output_aedb_path=output,
            open_cutout_at_end=False,
            use_pyaedt_extent_computing=True,
            use_pyaedt_cutout=False,
        )
        # assert (Path(output) / "edb.def").exists()
        bounding = edbapp.get_bounding_box()
        assert bounding
        cutout_line_x = 41
        cutout_line_y = 30
        points = [[bounding[0][0], bounding[0][1]]]
        points.append([cutout_line_x, bounding[0][1]])
        points.append([cutout_line_x, cutout_line_y])
        points.append([bounding[0][0], cutout_line_y])
        points.append([bounding[0][0], bounding[0][1]])
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(True, reason="Unstable test.")
    def test_create_custom_cutout_1(self, edb_examples):
        """Create custom cutout 1."""
        # Done
        edbapp = edb_examples.get_si_verse()
        spice_path = os.path.join(local_path, "example_models", test_subfolder, "GRM32_DC0V_25degC.mod")
        assert edbapp.components.instances["R8"].assign_spice_model(spice_path)
        assert edbapp.nets.nets
        assert edbapp.cutout(
            signal_nets=["1V0"],
            reference_nets=[
                "GND",
                "LVDS_CH08_N",
                "LVDS_CH08_P",
                "LVDS_CH10_N",
                "LVDS_CH10_P",
                "LVDS_CH04_P",
                "LVDS_CH04_N",
            ],
            extent_type="Bounding",
            extent_defeature=0.001,
            preserve_components_with_model=True,
            keep_lines_as_path=True,
        )
        assert "A0_N" not in edbapp.nets.nets
        # assert isinstance(edbapp.layout_validation.disjoint_nets("GND", order_by_area=True), list)
        # assert isinstance(edbapp.layout_validation.disjoint_nets("GND", keep_only_main_net=True), list)
        # assert isinstance(edbapp.layout_validation.disjoint_nets("GND", clean_disjoints_less_than=0.005), list)
        assert edbapp.layout_validation.fix_self_intersections("PGND")
        assert edbapp.layout_validation.fix_self_intersections()
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(True, reason="Unstable test.")
    def test_create_custom_cutout_2(self, edb_examples):
        """Create custom cutout 2."""
        # Done
        edbapp = edb_examples.get_si_verse()
        bounding = edbapp.get_bounding_box()
        assert bounding
        cutout_line_x = 41
        cutout_line_y = 30
        points = [[bounding[0][0], bounding[0][1]]]
        points.append([cutout_line_x, bounding[0][1]])
        points.append([cutout_line_x, cutout_line_y])
        points.append([bounding[0][0], cutout_line_y])
        points.append([bounding[0][0], bounding[0][1]])

        assert edbapp.cutout(
            signal_nets=["1V0"],
            reference_nets=["GND"],
            extent_type="ConvexHull",
            custom_extent=points,
            simple_pad_check=False,
        )
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(True, reason="Unstable test.")
    def test_create_custom_cutout_3(self, edb_examples):
        """Create custom cutout 3."""
        # Done
        edbapp = edb_examples.get_si_verse()
        edbapp.components.create_port_on_component(
            "U1",
            ["5V"],
            reference_net="GND",
            port_type="circuit_port",
        )
        edbapp.components.create_port_on_component("U2", ["5V"], reference_net="GND")
        edbapp.hfss.create_voltage_source_on_net("U4", "5V", "U4", "GND")
        legacy_name = edbapp.edbpath
        assert edbapp.cutout(
            signal_nets=["5V"],
            reference_nets=["GND"],
            extent_type="ConvexHull",
            use_pyaedt_extent_computing=True,
            check_terminals=True,
        )
        assert edbapp.edbpath == legacy_name
        # assert edbapp.are_port_reference_terminals_connected(common_reference="GND")

        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(True, reason="Unstable test.")
    def test_create_custom_cutout_4(self, edb_examples):
        """Create custom cutout 4."""
        # Done
        edbapp = edb_examples.get_si_verse()
        edbapp.components.create_pingroup_from_pins(
            [i for i in list(edbapp.components.instances["U1"].pins.values()) if i.net_name == "GND"]
        )

        assert edbapp.cutout(
            signal_nets=["DDR4_DQS0_P", "DDR4_DQS0_N"],
            reference_nets=["GND"],
            extent_type="convex_hull",
            use_pyaedt_extent_computing=True,
            include_pingroups=True,
            check_terminals=True,
            expansion_factor="1mm",
        )
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(True, reason="Unstable test.")
    def test_create_custom_cutout_5(self, edb_examples):
        source_path = os.path.join(local_path, "example_models", test_subfolder, "MicrostripSpliGnd.aedb")

        edbapp = edb_examples.load_edb(source_path)

        assert edbapp.cutout(
            signal_nets=["trace_n"],
            reference_nets=["ground"],
            extent_type="Conformal",
            use_pyaedt_extent_computing=True,
            check_terminals=True,
            expansion_factor=2,
            include_voids_in_extents=True,
        )
        edbapp.close(terminate_rpc_session=False)

    @pytest.mark.skipif(True, reason="Unstable test.")
    def test_create_custom_cutout_6(self, edb_examples):
        source_path = os.path.join(local_path, "example_models", test_subfolder, "Multizone_GroundVoids.aedb")

        edbapp = edb_examples.load_edb(source_path)

        assert edbapp.cutout(
            signal_nets=["DIFF_N", "DIFF_P"],
            reference_nets=["GND"],
            extent_type="bounding_box",
            use_pyaedt_extent_computing=True,
            check_terminals=True,
            expansion_factor=3,
        )
        edbapp.close(terminate_rpc_session=False)
