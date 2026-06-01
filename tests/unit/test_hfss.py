# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
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

"""Unit tests for grpc/database/hfss.py — no license required."""

from unittest.mock import MagicMock, patch
import warnings

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.grpc]


def _make_hfss():
    """Create a Hfss instance with a mocked pedb."""
    from pyedb.grpc.database.hfss import Hfss

    pedb = MagicMock()
    pedb.logger = MagicMock()
    return Hfss(pedb)


@pytest.mark.grpc
class TestGrpcHfssUnit:
    """Unit tests for Hfss that can run without a live EDB server."""

    def test_hfss_logger_property(self):
        """_logger delegates to pedb.logger."""
        hfss = _make_hfss()
        assert hfss._logger is hfss._pedb.logger

    def test_hfss_edb_property(self):
        """_edb returns pedb."""
        hfss = _make_hfss()
        assert hfss._edb is hfss._pedb

    def test_hfss_active_layout_property(self):
        """_active_layout delegates to pedb.active_layout."""
        hfss = _make_hfss()
        assert hfss._active_layout is hfss._pedb.active_layout

    def test_hfss_layout_property(self):
        """_layout delegates to pedb.layout."""
        hfss = _make_hfss()
        assert hfss._layout is hfss._pedb.layout

    def test_hfss_cell_property(self):
        """_cell delegates to pedb.cell."""
        hfss = _make_hfss()
        assert hfss._cell is hfss._pedb.cell

    def test_hfss_db_property(self):
        """_db delegates to pedb.active_db."""
        hfss = _make_hfss()
        assert hfss._db is hfss._pedb.active_db

    def test_hfss_ports_property(self):
        """ports delegates to pedb.ports."""
        hfss = _make_hfss()
        mock_ports = {"p1": MagicMock()}
        hfss._pedb.ports = mock_ports
        assert hfss.ports is mock_ports

    def test_hfss_sources_property(self):
        """sources delegates to pedb.sources."""
        hfss = _make_hfss()
        mock_sources = {"s1": MagicMock()}
        hfss._pedb.sources = mock_sources
        assert hfss.sources is mock_sources

    def test_hfss_probes_property(self):
        """probes delegates to pedb.probes."""
        hfss = _make_hfss()
        mock_probes = {"pr1": MagicMock()}
        hfss._pedb.probes = mock_probes
        assert hfss.probes is mock_probes

    def test_hfss_excitations_deprecated_returns_ports(self):
        """excitations (deprecated) returns ports."""
        hfss = _make_hfss()
        mock_ports = {"p1": MagicMock()}
        hfss._pedb.ports = mock_ports
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = hfss.excitations
        assert result is mock_ports

    def test_hfss_extent_info_property(self):
        """hfss_extent_info creates an HfssExtentInfo with pedb."""
        from pyedb.grpc.database.utility.hfss_extent_info import HfssExtentInfo

        hfss = _make_hfss()
        with patch("pyedb.grpc.database.hfss.HfssExtentInfo") as mock_cls:
            mock_cls.return_value = MagicMock(spec=HfssExtentInfo)
            result = hfss.hfss_extent_info
        mock_cls.assert_called_once_with(hfss._pedb)

    def test_hfss_get_trace_width_for_traces_with_ports_returns_dict(self):
        """get_trace_width_for_traces_with_ports builds a dict from excitations_nets."""
        hfss = _make_hfss()
        net_mock = MagicMock()
        net_mock.get_smallest_trace_width.return_value = 0.0001
        hfss._pedb.excitations_nets = ["NET1", "NET2"]
        hfss._pedb.nets.nets = {"NET1": net_mock, "NET2": net_mock}
        result = hfss.get_trace_width_for_traces_with_ports()
        assert "NET1" in result
        assert "NET2" in result
        assert result["NET1"] == 0.0001

    def test_hfss_generate_auto_hfss_regions_calls_cell(self):
        """generate_auto_hfss_regions calls active_cell.generate_auto_hfss_regions."""
        hfss = _make_hfss()
        hfss.generate_auto_hfss_regions()
        hfss._pedb.active_cell.generate_auto_hfss_regions.assert_called_once()

    def test_hfss_add_setup_deprecated_delegates_to_simulation_setups(self):
        """add_setup (deprecated) delegates to simulation_setups.create_hfss_setup."""
        hfss = _make_hfss()
        hfss._pedb.simulation_setups.create_hfss_setup.return_value = MagicMock()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = hfss.add_setup(name="setup1")
        hfss._pedb.simulation_setups.create_hfss_setup.assert_called_once_with(
            "setup1", "linear", None, None, None, False
        )

    def test_hfss_get_layout_bounding_box_uses_active_layout_when_none(self):
        """get_layout_bounding_box uses active_layout when layout argument is None."""
        from unittest.mock import MagicMock, patch

        hfss = _make_hfss()

        mock_loi = MagicMock()
        mock_bbox_item = MagicMock()
        mock_loi.get_bbox.return_value = mock_bbox_item
        hfss._pedb.active_layout.layout_instance.query_layout_obj_instances.return_value = [mock_loi]

        pt_min = MagicMock()
        pt_min.x.value = 0.0
        pt_min.y.value = 0.0
        pt_max = MagicMock()
        pt_max.x.value = 0.001
        pt_max.y.value = 0.002

        with patch("pyedb.grpc.database.hfss.CorePolygonData") as mock_poly:
            mock_poly.bbox_of_polygons.return_value = (pt_min, pt_max)
            result = hfss.get_layout_bounding_box()

        assert result == [0.0, 0.0, 0.001, 0.002]

    def test_hfss_get_layout_bounding_box_digit_resolution(self):
        """get_layout_bounding_box rounds to digit_resolution."""
        from unittest.mock import MagicMock, patch

        hfss = _make_hfss()

        mock_loi = MagicMock()
        hfss._pedb.active_layout.layout_instance.query_layout_obj_instances.return_value = [mock_loi]

        pt_min = MagicMock()
        pt_min.x.value = 1.23456789
        pt_min.y.value = 2.34567891
        pt_max = MagicMock()
        pt_max.x.value = 3.45678912
        pt_max.y.value = 4.56789123

        with patch("pyedb.grpc.database.hfss.CorePolygonData") as mock_poly:
            mock_poly.bbox_of_polygons.return_value = (pt_min, pt_max)
            result = hfss.get_layout_bounding_box(digit_resolution=3)

        assert result == [round(1.23456789, 3), round(2.34567891, 3), round(3.45678912, 3), round(4.56789123, 3)]

    def test_hfss_get_layout_bounding_box_custom_layout(self):
        """get_layout_bounding_box accepts a custom layout argument."""
        from unittest.mock import MagicMock, patch

        hfss = _make_hfss()
        custom_layout = MagicMock()
        mock_loi = MagicMock()
        custom_layout.layout_instance.query_layout_obj_instances.return_value = [mock_loi]

        pt_min = MagicMock()
        pt_min.x.value = -0.001
        pt_min.y.value = -0.002
        pt_max = MagicMock()
        pt_max.x.value = 0.005
        pt_max.y.value = 0.006

        with patch("pyedb.grpc.database.hfss.CorePolygonData") as mock_poly:
            mock_poly.bbox_of_polygons.return_value = (pt_min, pt_max)
            result = hfss.get_layout_bounding_box(layout=custom_layout)

        # Verify active_layout was NOT used
        hfss._pedb.active_layout.layout_instance.query_layout_obj_instances.assert_not_called()
        assert result == [-0.001, -0.002, 0.005, 0.006]

    def test_hfss_create_edge_port_deprecated_delegates(self):
        """create_edge_port (deprecated) delegates to excitation_manager.create_edge_port."""
        hfss = _make_hfss()
        expected = MagicMock()
        hfss._pedb.excitation_manager.create_edge_port.return_value = expected
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = hfss.create_edge_port(
                location=[0, 0],
                primitive_name="prim1",
                name="port1",
                impedance=50,
                is_wave_port=True,
                horizontal_extent_factor=1,
                vertical_extent_factor=1,
                pec_launch_width=0.0001,
            )
        hfss._pedb.excitation_manager.create_edge_port.assert_called_once_with(
            location=[0, 0],
            primitive_name="prim1",
            name="port1",
            impedance=50,
            is_wave_port=True,
            horizontal_extent_factor=1,
            vertical_extent_factor=1,
            pec_launch_width=0.0001,
        )
        assert result is expected
