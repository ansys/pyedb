# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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
from unittest.mock import MagicMock, Mock, patch
import warnings

import pytest

pytest.importorskip("pyedb.dotnet.database.siwave", reason="Requires .NET runtime")
from pyedb.dotnet.database.siwave import EdbSiwave

pytestmark = [pytest.mark.unit, pytest.mark.no_licence, pytest.mark.legacy]


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, tmpdir):
        self.edb = Mock()
        self.edb.edbpath = os.path.join(tmpdir, "fake_edb.aedb")
        self.siwave = EdbSiwave(self.edb)

    def test_siwave_add_syz_analsyis(self):
        """Add a sywave AC analysis."""
        assert self.siwave.add_siwave_syz_analysis()


@pytest.mark.grpc
def _make_grpc_siwave():
    """Return a Siwave (grpc) instance with a mocked pedb."""
    from pyedb.grpc.database.siwave import Siwave

    pedb = MagicMock()
    pedb.logger = MagicMock()
    return Siwave(pedb)


@pytest.mark.grpc
class TestGrpcSiwaveUnit:
    """Unit tests for grpc Siwave that can run without a live EDB server."""

    def test_edb_property(self):
        """_edb returns pedb."""
        siwave = _make_grpc_siwave()
        assert siwave._edb is siwave._pedb

    def test_logger_property(self):
        """_logger returns pedb.logger."""
        siwave = _make_grpc_siwave()
        assert siwave._logger is siwave._pedb.logger

    def test_active_layout_property(self):
        """_active_layout delegates to pedb.active_layout."""
        siwave = _make_grpc_siwave()
        assert siwave._active_layout is siwave._pedb.active_layout

    def test_layout_property(self):
        """_layout delegates to pedb.layout."""
        siwave = _make_grpc_siwave()
        assert siwave._layout is siwave._pedb.layout

    def test_cell_property(self):
        """_cell delegates to pedb.active_cell."""
        siwave = _make_grpc_siwave()
        assert siwave._cell is siwave._pedb.active_cell

    def test_db_property(self):
        """_db delegates to pedb.active_db."""
        siwave = _make_grpc_siwave()
        assert siwave._db is siwave._pedb.active_db

    def test_ports_property(self):
        """ports delegates to pedb.ports."""
        siwave = _make_grpc_siwave()
        mock_ports = {"p1": MagicMock()}
        siwave._pedb.ports = mock_ports
        assert siwave.ports is mock_ports

    def test_sources_property(self):
        """sources delegates to pedb.sources."""
        siwave = _make_grpc_siwave()
        mock_sources = {"s1": MagicMock()}
        siwave._pedb.sources = mock_sources
        assert siwave.sources is mock_sources

    def test_probes_property(self):
        """probes delegates to pedb.probes."""
        siwave = _make_grpc_siwave()
        mock_probes = {"pr1": MagicMock()}
        siwave._pedb.probes = mock_probes
        assert siwave.probes is mock_probes

    def test_pin_groups_property(self):
        """pin_groups delegates to pedb.excitation_manager.pin_groups."""
        siwave = _make_grpc_siwave()
        mock_pgs = {"pg1": MagicMock()}
        siwave._pedb.excitation_manager.pin_groups = mock_pgs
        assert siwave.pin_groups is mock_pgs

    def test_excitations_deprecated_returns_ports(self):
        """excitations (deprecated) returns ports."""
        siwave = _make_grpc_siwave()
        mock_ports = {"p1": MagicMock()}
        siwave._pedb.ports = mock_ports
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = siwave.excitations
        assert result is mock_ports

    def test_create_exec_file_creates_file(self, tmp_path):
        """create_exec_file creates an .exec file with AC option."""
        siwave = _make_grpc_siwave()
        aedb_path = str(tmp_path / "design.aedb")
        siwave._pedb.edbpath = aedb_path
        result = siwave.create_exec_file(add_ac=True)
        assert result.endswith(".exec")
        with open(result) as f:
            content = f.read()
        assert "ExecAcSim" in content
        assert "SaveSiw" in content

    def test_create_exec_file_dc_option(self, tmp_path):
        """create_exec_file creates an .exec file with DC option."""
        siwave = _make_grpc_siwave()
        aedb_path = str(tmp_path / "design.aedb")
        siwave._pedb.edbpath = aedb_path
        result = siwave.create_exec_file(add_dc=True)
        with open(result) as f:
            content = f.read()
        assert "ExecDcSim" in content

    def test_create_exec_file_syz_option(self, tmp_path):
        """create_exec_file creates an .exec file with SYZ option."""
        siwave = _make_grpc_siwave()
        aedb_path = str(tmp_path / "design.aedb")
        siwave._pedb.edbpath = aedb_path
        result = siwave.create_exec_file(add_syz=True)
        with open(result) as f:
            content = f.read()
        assert "ExecSyzSim" in content

    def test_create_exec_file_overwrites_existing(self, tmp_path):
        """create_exec_file removes an existing .exec file before creating."""
        siwave = _make_grpc_siwave()
        aedb_path = str(tmp_path / "design.aedb")
        siwave._pedb.edbpath = aedb_path
        # Create first file
        siwave.create_exec_file(add_ac=True)
        # Create again — should not raise
        result = siwave.create_exec_file(add_dc=True)
        with open(result) as f:
            content = f.read()
        assert "ExecDcSim" in content
        assert "ExecAcSim" not in content

    def test_create_impedance_crosstalk_scan_returns_config(self):
        """create_impedance_crosstalk_scan returns a SiwaveScanConfig."""
        from pyedb.misc.siw_feature_config.xtalk_scan.scan_config import SiwaveScanConfig

        siwave = _make_grpc_siwave()
        with patch("pyedb.grpc.database.siwave.SiwaveScanConfig") as mock_cls:
            mock_cls.return_value = MagicMock(spec=SiwaveScanConfig)
            result = siwave.create_impedance_crosstalk_scan("impedance")
        mock_cls.assert_called_once_with(siwave._pedb, "impedance")

    def test_add_siwave_dc_analysis_calls_create_dcir_setup(self):
        """add_siwave_dc_analysis delegates to simulation_setups.create_siwave_dcir_setup."""
        siwave = _make_grpc_siwave()
        mock_setup = MagicMock()
        siwave._pedb.simulation_setups.create_siwave_dcir_setup.return_value = mock_setup
        # We call create_exec_file internally so we need a real edbpath
        siwave._pedb.edbpath = "/tmp/design.aedb"
        with patch.object(siwave, "create_exec_file"):
            result = siwave.add_siwave_dc_analysis(name="dc_setup")
        siwave._pedb.simulation_setups.create_siwave_dcir_setup.assert_called_once_with(name="dc_setup")
        assert result is mock_setup

    def test_icepak_use_minimal_comp_defaults_getter(self):
        """icepak_use_minimal_comp_defaults returns value from product property."""
        from ansys.edb.core.database import ProductIdType as CoreProductIdType

        siwave = _make_grpc_siwave()
        mock_val = MagicMock()
        mock_val.value = True
        siwave._pedb.active_cell.get_product_property.return_value = mock_val
        result = siwave.icepak_use_minimal_comp_defaults
        siwave._pedb.active_cell.get_product_property.assert_called_once_with(CoreProductIdType.SIWAVE, 422)
        assert result is True

    def test_icepak_component_file_getter(self):
        """icepak_component_file returns value from product property."""
        from ansys.edb.core.database import ProductIdType as CoreProductIdType

        siwave = _make_grpc_siwave()
        mock_val = MagicMock()
        mock_val.value = "/path/to/component.xml"
        siwave._pedb.active_cell.get_product_property.return_value = mock_val
        result = siwave.icepak_component_file
        siwave._pedb.active_cell.get_product_property.assert_called_once_with(CoreProductIdType.SIWAVE, 420)
        assert result == "/path/to/component.xml"

    def test_deprecated_create_terminal_on_pins_delegates(self):
        """_create_terminal_on_pins delegates to excitation_manager."""
        siwave = _make_grpc_siwave()
        source = MagicMock()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            siwave._create_terminal_on_pins(source)
        siwave._pedb.excitation_manager._create_terminal_on_pins.assert_called_once_with(source)

    def test_deprecated_create_circuit_port_on_pin_delegates(self):
        """create_circuit_port_on_pin delegates to excitation_manager."""
        siwave = _make_grpc_siwave()
        pos_pin, neg_pin = MagicMock(), MagicMock()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            siwave.create_circuit_port_on_pin(pos_pin, neg_pin)
        siwave._pedb.excitation_manager.create_circuit_port_on_pin.assert_called_once()

    def test_deprecated_create_voltage_source_on_pin_delegates(self):
        """create_voltage_source_on_pin delegates to excitation_manager."""
        siwave = _make_grpc_siwave()
        pos_pin, neg_pin = MagicMock(), MagicMock()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            siwave.create_voltage_source_on_pin(pos_pin, neg_pin, voltage_value=3.3)
        siwave._pedb.excitation_manager.create_voltage_source_on_pin.assert_called_once()

    def test_deprecated_create_current_source_on_pin_delegates(self):
        """create_current_source_on_pin delegates to excitation_manager."""
        siwave = _make_grpc_siwave()
        pos_pin, neg_pin = MagicMock(), MagicMock()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            siwave.create_current_source_on_pin(pos_pin, neg_pin, current_value=0.1)
        siwave._pedb.excitation_manager.create_current_source_on_pin.assert_called_once()

    def test_deprecated_create_resistor_on_pin_delegates(self):
        """create_resistor_on_pin delegates to excitation_manager."""
        siwave = _make_grpc_siwave()
        pos_pin, neg_pin = MagicMock(), MagicMock()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            siwave.create_resistor_on_pin(pos_pin, neg_pin, rvalue=100)
        siwave._pedb.excitation_manager.create_resistor_on_pin.assert_called_once()

    def test_deprecated_create_pin_group_delegates(self):
        """create_pin_group delegates to components."""
        siwave = _make_grpc_siwave()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            siwave.create_pin_group("U1", ["1", "2"], group_name="pg1")
        siwave._pedb.components.create_pin_group.assert_called_once_with("U1", ["1", "2"], "pg1")

    def test_deprecated_create_pin_group_on_net_delegates(self):
        """create_pin_group_on_net delegates to components."""
        siwave = _make_grpc_siwave()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            siwave.create_pin_group_on_net("U1", "GND", group_name="pg_gnd")
        siwave._pedb.components.create_pin_group_on_net.assert_called_once_with("U1", "GND", "pg_gnd")
