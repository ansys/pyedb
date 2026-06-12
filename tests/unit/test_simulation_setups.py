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

"""Unit tests for SimulationSetups container class (no EDB license required)."""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from pyedb.grpc.database.simulation_setups import SimulationSetups

pytestmark = [pytest.mark.unit, pytest.mark.grpc]


class TestDistributionFullNameAliases:
    """Verify that CoreDistribution accepts full human-readable names written by AEDT internal tools.

    pintopinsetup and other AEDT-internal tools write the full English name (e.g. 'Linear')
    into the frequency_string field of an EDB sweep.  ansys-edb-core parses that field with
    ``Distribution[name]``; without the aliases that lookup raised a KeyError.
    """

    @pytest.mark.parametrize(
        "alias,expected_name",
        [
            ("Linear", "LIN"),
            ("LinearCount", "LINC"),
            ("Linear Count", "LINC"),
            ("LogScale", "DEC"),
            ("Log Scale", "DEC"),
            ("Decade", "DEC"),
            ("Exponential", "ESTP"),
            ("OctaveCount", "OCT"),
            ("Octave Count", "OCT"),
        ],
    )
    def test_full_name_alias_resolves(self, alias, expected_name):
        """Distribution[alias] must resolve to the correct enum member without raising KeyError."""
        from pyedb.grpc.database.simulation_setup.sweep_data import CoreDistribution

        member = CoreDistribution[alias]
        assert member.name == expected_name

    def test_abbreviated_names_unchanged(self):
        """The original abbreviated names (LIN, DEC, …) must still work after patching."""
        from pyedb.grpc.database.simulation_setup.sweep_data import CoreDistribution

        for name in ("LIN", "LINC", "DEC", "ESTP", "OCT"):
            assert CoreDistribution[name].name == name

    def test_aliases_do_not_shadow_existing_members(self):
        """setdefault must not replace a pre-existing member with an alias."""
        from pyedb.grpc.database.simulation_setup.sweep_data import CoreDistribution

        # LIN is a real member; it must still be the canonical object
        assert CoreDistribution["LIN"] is CoreDistribution.LIN

    def test_invalid_distribution_name_still_raises(self):
        """Unknown distribution names that are neither abbreviated nor aliased must still raise KeyError."""
        from pyedb.grpc.database.simulation_setup.sweep_data import CoreDistribution

        with pytest.raises(KeyError):
            _ = CoreDistribution["NotADistribution"]


def _make_setup_stub(name: str, type_name: str):
    """Return a minimal stub that mimics a gRPC SimulationSetup object."""
    stub = SimpleNamespace()
    stub.name = name
    stub.type = SimpleNamespace(name=type_name)
    return stub


def _make_pedb(setups_list=None, existing_setups_names=None):
    """Build a minimal mock pedb object."""
    pedb = MagicMock()
    # active_cell.simulation_setups is no longer used by SimulationSetups properties;
    # _raw_simulation_setups() is called instead. We leave it accessible for fallback.
    pedb.active_cell.simulation_setups = setups_list if setups_list is not None else []
    # setups property used by create() duplicate check
    pedb.setups = {name: MagicMock() for name in (existing_setups_names or [])}
    pedb.active_cell.get_product_property.return_value = SimpleNamespace(value="")
    return pedb


def _patch_raw(ss, setups_list):
    """Patch _raw_simulation_setups on a SimulationSetups instance."""
    return patch.object(ss, "_raw_simulation_setups", return_value=setups_list if setups_list is not None else [])


class TestHfssProperty:
    def test_returns_empty_dict_when_no_setups(self):
        pedb = _make_pedb()
        ss = SimulationSetups(pedb)
        with _patch_raw(ss, []):
            assert ss.hfss == {}

    def test_returns_empty_dict_when_setups_is_none(self):
        pedb = _make_pedb()
        ss = SimulationSetups(pedb)
        with _patch_raw(ss, []):
            assert ss.hfss == {}

    def test_filters_none_entries_from_grpc_list(self):
        # _raw_simulation_setups already filters Nones; empty list maps to empty dict
        pedb = _make_pedb()
        ss = SimulationSetups(pedb)
        with _patch_raw(ss, []):
            assert ss.hfss == {}

    def test_returns_only_hfss_setups(self):
        stub_hfss = _make_setup_stub("setup_hfss", "hfss")
        stub_si = _make_setup_stub("setup_si", "si_wave")
        pedb = _make_pedb()

        with patch(
            "pyedb.grpc.database.simulation_setups.HfssSimulationSetup",
            side_effect=lambda pedb, s: SimpleNamespace(name=s.name),
        ):
            ss = SimulationSetups(pedb)
            with _patch_raw(ss, [stub_hfss, stub_si]):
                result = ss.hfss

        assert "setup_hfss" in result
        assert "setup_si" not in result

    def test_ignores_setup_with_none_type(self):
        stub = SimpleNamespace(name="bad", type=None)
        pedb = _make_pedb()
        ss = SimulationSetups(pedb)
        with _patch_raw(ss, [stub]):
            assert ss.hfss == {}


class TestSiwaveProperty:
    def test_returns_empty_dict_when_no_setups(self):
        pedb = _make_pedb()
        ss = SimulationSetups(pedb)
        with _patch_raw(ss, []):
            assert ss.siwave == {}

    def test_returns_only_siwave_setups(self):
        stub_si = _make_setup_stub("setup_si", "si_wave")
        stub_hfss = _make_setup_stub("setup_hfss", "hfss")
        pedb = _make_pedb()

        with patch(
            "pyedb.grpc.database.simulation_setups.SiwaveSimulationSetup",
            side_effect=lambda pedb, s: SimpleNamespace(name=s.name),
        ):
            ss = SimulationSetups(pedb)
            with _patch_raw(ss, [stub_si, stub_hfss]):
                result = ss.siwave

        assert "setup_si" in result
        assert "setup_hfss" not in result


class TestSiwaveDcirProperty:
    def test_returns_empty_dict_when_no_setups(self):
        pedb = _make_pedb()
        ss = SimulationSetups(pedb)
        with _patch_raw(ss, []):
            assert ss.siwave_dcir == {}

    def test_returns_only_dcir_setups(self):
        stub_dcir = _make_setup_stub("setup_dcir", "si_wave_dcir")
        stub_other = _make_setup_stub("setup_other", "hfss")
        pedb = _make_pedb()

        with patch(
            "pyedb.grpc.database.simulation_setups.SIWaveDCIRSimulationSetup",
            side_effect=lambda pedb, s: SimpleNamespace(name=s.name),
        ):
            ss = SimulationSetups(pedb)
            with _patch_raw(ss, [stub_dcir, stub_other]):
                result = ss.siwave_dcir

        assert "setup_dcir" in result
        assert "setup_other" not in result


class TestRaptorXProperty:
    def test_returns_empty_dict_when_no_setups(self):
        pedb = _make_pedb()
        ss = SimulationSetups(pedb)
        with _patch_raw(ss, []):
            assert ss.raptor_x == {}

    def test_returns_only_raptorx_setups(self):
        stub_rx = _make_setup_stub("setup_rx", "raptor_x")
        pedb = _make_pedb()

        with patch(
            "pyedb.grpc.database.simulation_setups.RaptorXSimulationSetup",
            side_effect=lambda pedb, s: SimpleNamespace(name=s.name),
        ):
            ss = SimulationSetups(pedb)
            with _patch_raw(ss, [stub_rx]):
                result = ss.raptor_x

        assert "setup_rx" in result


class TestQ3dProperty:
    def test_returns_empty_dict_when_no_setups(self):
        pedb = _make_pedb()
        ss = SimulationSetups(pedb)
        with _patch_raw(ss, []):
            assert ss.q3d == {}

    def test_returns_only_q3d_setups(self):
        stub_q3d = _make_setup_stub("setup_q3d", "q3d_sim")
        pedb = _make_pedb()

        with patch(
            "pyedb.grpc.database.simulation_setups.Q3DSimulationSetup",
            side_effect=lambda pedb, s: SimpleNamespace(name=s.name),
        ):
            ss = SimulationSetups(pedb)
            with _patch_raw(ss, [stub_q3d]):
                result = ss.q3d

        assert "setup_q3d" in result


class TestHfsspiProperty:
    def test_returns_empty_dict_when_no_setups(self):
        pedb = _make_pedb()
        ss = SimulationSetups(pedb)
        with _patch_raw(ss, []):
            assert ss.hfss_pi == {}

    def test_returns_only_hfss_pi_setups(self):
        stub_pi = _make_setup_stub("setup_hfss_pi", "hfss_pi")
        stub_other = _make_setup_stub("setup_other", "hfss")
        pedb = _make_pedb()

        with patch(
            "pyedb.grpc.database.simulation_setups.HFSSPISimulationSetup",
            side_effect=lambda pedb, s: SimpleNamespace(name=s.name),
        ):
            ss = SimulationSetups(pedb)
            with _patch_raw(ss, [stub_pi, stub_other]):
                result = ss.hfss_pi

        assert "setup_hfss_pi" in result
        assert "setup_other" not in result

    def test_ignores_none_type_setup(self):
        stub = SimpleNamespace(name="bad", type=None)
        pedb = _make_pedb()
        ss = SimulationSetups(pedb)
        with _patch_raw(ss, [stub]):
            assert ss.hfss_pi == {}


class TestSiwaveCpaProperty:
    def test_returns_empty_dict_when_no_cpa_name(self):
        pedb = _make_pedb()
        pedb.active_cell.get_product_property.return_value = SimpleNamespace(value="")
        ss = SimulationSetups(pedb)
        assert ss.siwave_cpa == {}

    def test_creates_cpa_setup_when_name_present(self):
        pedb = _make_pedb()
        pedb.active_cell.get_product_property.return_value = SimpleNamespace(value="my_cpa")

        fake_cpa = SimpleNamespace(name="my_cpa")
        with patch(
            "pyedb.grpc.database.simulation_setups.SIWaveCPASimulationSetup",
            return_value=fake_cpa,
        ):
            ss = SimulationSetups(pedb)
            result = ss.siwave_cpa

        assert "my_cpa" in result

    def test_does_not_duplicate_existing_cpa_setup(self):
        pedb = _make_pedb()
        pedb.active_cell.get_product_property.return_value = SimpleNamespace(value="my_cpa")

        fake_cpa = SimpleNamespace(name="my_cpa")
        ss = SimulationSetups(pedb)
        ss._siwave_cpa_setup["my_cpa"] = fake_cpa

        with patch(
            "pyedb.grpc.database.simulation_setups.SIWaveCPASimulationSetup",
        ) as mock_cpa_cls:
            result = ss.siwave_cpa

        mock_cpa_cls.assert_not_called()
        assert "my_cpa" in result


class TestSetupsProperty:
    def test_merges_all_solver_dicts(self):
        pedb = _make_pedb()
        pedb.active_cell.get_product_property.return_value = SimpleNamespace(value="")
        ss = SimulationSetups(pedb)
        with _patch_raw(ss, []):
            result = ss.setups
        assert isinstance(result, dict)

    def test_setups_contains_hfss_and_siwave(self):
        stub_hfss = _make_setup_stub("my_hfss", "hfss")
        stub_si = _make_setup_stub("my_si", "si_wave")
        pedb = _make_pedb()
        pedb.active_cell.get_product_property.return_value = SimpleNamespace(value="")

        fake_hfss = SimpleNamespace(name="my_hfss")
        fake_si = SimpleNamespace(name="my_si")

        with (
            patch(
                "pyedb.grpc.database.simulation_setups.HfssSimulationSetup",
                side_effect=lambda p, s: fake_hfss if s.name == "my_hfss" else None,
            ),
            patch(
                "pyedb.grpc.database.simulation_setups.SiwaveSimulationSetup",
                side_effect=lambda p, s: fake_si if s.name == "my_si" else None,
            ),
        ):
            ss = SimulationSetups(pedb)
            with _patch_raw(ss, [stub_hfss, stub_si]):
                result = ss.setups

        assert "my_hfss" in result
        assert "my_si" in result


class TestCreate:
    def _make_setup(self, name):
        return SimpleNamespace(name=name)

    def test_create_hfss_setup(self):
        pedb = _make_pedb()
        ss = SimulationSetups(pedb)
        fake_setup = self._make_setup("hfss_setup")
        with patch(
            "pyedb.grpc.database.simulation_setups.HfssSimulationSetup.create",
            return_value=fake_setup,
        ):
            result = ss.create(name="hfss_setup", solver="hfss")
        assert result is fake_setup

    def test_create_siwave_setup(self):
        pedb = _make_pedb()
        ss = SimulationSetups(pedb)
        fake_setup = self._make_setup("siwave_setup")
        with patch(
            "pyedb.grpc.database.simulation_setups.SiwaveSimulationSetup.create",
            return_value=fake_setup,
        ):
            result = ss.create(name="siwave_setup", solver="siwave")
        assert result is fake_setup

    def test_create_siwave_dcir_setup(self):
        pedb = _make_pedb()
        ss = SimulationSetups(pedb)
        fake_setup = self._make_setup("dcir_setup")
        with patch(
            "pyedb.grpc.database.simulation_setups.SIWaveDCIRSimulationSetup.create",
            return_value=fake_setup,
        ):
            result = ss.create(name="dcir_setup", solver="siwave_dcir")
        assert result is fake_setup

    def test_create_raptor_x_setup(self):
        pedb = _make_pedb()
        ss = SimulationSetups(pedb)
        fake_setup = self._make_setup("rx_setup")
        with patch(
            "pyedb.grpc.database.simulation_setups.RaptorXSimulationSetup.create",
            return_value=fake_setup,
        ):
            result = ss.create(name="rx_setup", solver="raptor_x")
        assert result is fake_setup

    def test_create_q3d_setup(self):
        pedb = _make_pedb()
        ss = SimulationSetups(pedb)
        fake_setup = self._make_setup("q3d_setup")
        with patch(
            "pyedb.grpc.database.simulation_setups.Q3DSimulationSetup.create",
            return_value=fake_setup,
        ):
            result = ss.create(name="q3d_setup", solver="q3d")
        assert result is fake_setup

    def test_create_hfss_pi_setup(self):
        pedb = _make_pedb()
        ss = SimulationSetups(pedb)
        fake_setup = self._make_setup("pi_setup")
        with patch(
            "pyedb.grpc.database.simulation_setups.HFSSPISimulationSetup.create",
            return_value=fake_setup,
        ):
            result = ss.create(name="pi_setup", solver="hfss_pi")
        assert result is fake_setup

    def test_create_falls_back_to_hfss_for_unknown_solver(self):
        """Unknown solver should fall back to HFSS."""
        pedb = _make_pedb()
        ss = SimulationSetups(pedb)
        fake_setup = self._make_setup("unknown_setup")
        with patch(
            "pyedb.grpc.database.simulation_setups.HfssSimulationSetup.create",
            return_value=fake_setup,
        ):
            result = ss.create(name="unknown_setup", solver="not_a_solver")
        assert result is fake_setup

    def test_create_returns_none_if_name_already_exists(self):
        """Duplicate setup name should return None and log an error."""
        pedb = _make_pedb(existing_setups_names=["existing_setup"])
        ss = SimulationSetups(pedb)
        result = ss.create(name="existing_setup", solver="hfss")
        assert result is None
        pedb.logger.error.assert_called_once()

    def test_create_auto_generates_name_when_none(self):
        pedb = _make_pedb()
        ss = SimulationSetups(pedb)
        fake_setup = MagicMock()
        with patch(
            "pyedb.grpc.database.simulation_setups.HfssSimulationSetup.create",
            return_value=fake_setup,
        ):
            result = ss.create(name=None, solver="hfss")
        assert result is fake_setup


class TestRawSimulationSetups:
    def test_falls_back_to_public_api_when_stub_not_accessible(self):
        """If the private Cell stub is not accessible, fall back to active_cell.simulation_setups."""
        pedb = _make_pedb()
        stub_hfss = _make_setup_stub("setup_hfss", "hfss")
        # Make the private stub access raise AttributeError (simulating missing attr)
        cell_mock = MagicMock()
        del cell_mock._Cell__stub  # ensure attribute is missing
        cell_mock.simulation_setups = [stub_hfss]
        pedb.active_cell = cell_mock

        ss = SimulationSetups(pedb)
        result = ss._raw_simulation_setups()
        assert len(result) == 1
        assert result[0].name == "setup_hfss"

    def test_falls_back_and_filters_none_from_public_api(self):
        pedb = _make_pedb()
        stub_hfss = _make_setup_stub("setup_hfss", "hfss")
        cell_mock = MagicMock()
        del cell_mock._Cell__stub
        cell_mock.simulation_setups = [None, stub_hfss]
        pedb.active_cell = cell_mock

        ss = SimulationSetups(pedb)
        result = ss._raw_simulation_setups()
        assert len(result) == 1


class TestCreateHfssSetup:
    def test_creates_without_sweep_when_freq_params_missing(self):
        pedb = _make_pedb()
        ss = SimulationSetups(pedb)
        fake_setup = MagicMock()
        fake_setup.add_sweep = MagicMock()
        with patch.object(ss, "create", return_value=fake_setup):
            result = ss.create_hfss_setup(name="my_hfss")
        assert result is fake_setup
        fake_setup.add_sweep.assert_not_called()

    def test_creates_with_sweep_when_freq_params_provided(self):
        pedb = _make_pedb()
        ss = SimulationSetups(pedb)
        fake_setup = MagicMock()
        with patch.object(ss, "create", return_value=fake_setup):
            ss.create_hfss_setup(
                name="my_hfss",
                start_freq=1e9,
                stop_freq=10e9,
                step_freq=1e8,
            )
        fake_setup.add_sweep.assert_called_once()

    def test_applies_kwargs_as_attributes(self):
        pedb = _make_pedb()
        ss = SimulationSetups(pedb)
        fake_setup = MagicMock(spec=[])
        with patch.object(ss, "create", return_value=fake_setup):
            ss.create_hfss_setup(name="my_hfss", my_custom_attr=42)
        assert fake_setup.my_custom_attr == 42


class TestCreateHfsspiSetup:
    def test_creates_without_sweep(self):
        pedb = _make_pedb()
        ss = SimulationSetups(pedb)
        fake_setup = MagicMock()
        fake_setup.add_sweep = MagicMock()
        with patch.object(ss, "create", return_value=fake_setup):
            result = ss.create_hfss_pi_setup(name="my_pi")
        assert result is fake_setup
        fake_setup.add_sweep.assert_not_called()

    def test_creates_with_sweep_when_freq_params_provided(self):
        pedb = _make_pedb()
        ss = SimulationSetups(pedb)
        fake_setup = MagicMock()
        with patch.object(ss, "create", return_value=fake_setup):
            ss.create_hfss_pi_setup(
                name="my_pi",
                start_freq=1e9,
                stop_freq=5e9,
                step_freq=1e8,
            )
        fake_setup.add_sweep.assert_called_once()

    def test_applies_kwargs_as_attributes(self):
        pedb = _make_pedb()
        ss = SimulationSetups(pedb)
        fake_setup = MagicMock(spec=[])
        with patch.object(ss, "create", return_value=fake_setup):
            ss.create_hfss_pi_setup(name="my_pi", extra_param="hello")
        assert fake_setup.extra_param == "hello"


class TestCreateSiwaveSetup:
    def test_creates_without_sweep(self):
        pedb = _make_pedb()
        ss = SimulationSetups(pedb)
        fake_setup = MagicMock()
        fake_setup.add_sweep = MagicMock()
        with patch.object(ss, "create", return_value=fake_setup):
            result = ss.create_siwave_setup(name="my_si")
        assert result is fake_setup
        fake_setup.add_sweep.assert_not_called()

    def test_creates_with_sweep_when_freq_params_provided(self):
        pedb = _make_pedb()
        ss = SimulationSetups(pedb)
        fake_setup = MagicMock()
        with patch.object(ss, "create", return_value=fake_setup):
            ss.create_siwave_setup(
                name="my_si",
                start_freq=1e6,
                stop_freq=1e9,
                step_freq=1e6,
            )
        fake_setup.add_sweep.assert_called_once()


class TestCreateSiwaveDcirSetup:
    def test_creates_dcir_setup(self):
        pedb = _make_pedb()
        ss = SimulationSetups(pedb)
        fake_setup = MagicMock()
        with patch.object(ss, "create", return_value=fake_setup):
            result = ss.create_siwave_dcir_setup(name="my_dcir")
        assert result is fake_setup

    def test_applies_kwargs_as_attributes(self):
        pedb = _make_pedb()
        ss = SimulationSetups(pedb)
        fake_setup = MagicMock(spec=[])
        with patch.object(ss, "create", return_value=fake_setup):
            ss.create_siwave_dcir_setup(name="my_dcir", foo="bar")
        assert fake_setup.foo == "bar"


class TestCreateSiwaveCpaSetup:
    def test_creates_new_cpa_setup(self):
        pedb = _make_pedb()
        pedb.active_cell.get_product_property.return_value = SimpleNamespace(value="")
        ss = SimulationSetups(pedb)
        fake_cpa = SimpleNamespace(name="my_cpa")

        with patch(
            "pyedb.grpc.database.simulation_setups.SIWaveCPASimulationSetup.create",
            return_value=fake_cpa,
        ):
            result = ss.create_siwave_cpa_setup(name="my_cpa")

        assert result is fake_cpa
        assert "my_cpa" in ss._siwave_cpa_setup

    def test_returns_existing_cpa_setup_if_duplicate(self):
        pedb = _make_pedb()
        pedb.active_cell.get_product_property.return_value = SimpleNamespace(value="")
        ss = SimulationSetups(pedb)
        existing = SimpleNamespace(name="existing_cpa")
        ss._siwave_cpa_setup["existing_cpa"] = existing

        with patch("pyedb.grpc.database.simulation_setups.SIWaveCPASimulationSetup.create") as mock_create:
            result = ss.create_siwave_cpa_setup(name="existing_cpa")

        mock_create.assert_not_called()
        pedb.logger.error.assert_called_once()
        assert result is existing

    def test_auto_generates_name_when_none(self):
        pedb = _make_pedb()
        pedb.active_cell.get_product_property.return_value = SimpleNamespace(value="")
        ss = SimulationSetups(pedb)
        fake_cpa = SimpleNamespace(name="auto_name")

        with patch(
            "pyedb.grpc.database.simulation_setups.SIWaveCPASimulationSetup.create",
            return_value=fake_cpa,
        ):
            result = ss.create_siwave_cpa_setup(name=None)

        assert result is fake_cpa

    def test_applies_kwargs_as_attributes(self):
        pedb = _make_pedb()
        pedb.active_cell.get_product_property.return_value = SimpleNamespace(value="")
        ss = SimulationSetups(pedb)
        fake_cpa = MagicMock(spec=[])
        fake_cpa.name = "cpa_kw"

        with patch(
            "pyedb.grpc.database.simulation_setups.SIWaveCPASimulationSetup.create",
            return_value=fake_cpa,
        ):
            ss.create_siwave_cpa_setup(name="cpa_kw", my_kwarg="value")

        assert fake_cpa.my_kwarg == "value"


class TestCreateRaptorXSetup:
    def test_creates_without_sweep(self):
        pedb = _make_pedb()
        ss = SimulationSetups(pedb)
        fake_setup = MagicMock()
        fake_setup.add_sweep = MagicMock()
        with patch.object(ss, "create", return_value=fake_setup):
            result = ss.create_raptor_x_setup(name="my_rx")
        assert result is fake_setup
        fake_setup.add_sweep.assert_not_called()

    def test_creates_with_sweep_when_freq_params_provided(self):
        pedb = _make_pedb()
        ss = SimulationSetups(pedb)
        fake_setup = MagicMock()
        with patch.object(ss, "create", return_value=fake_setup):
            ss.create_raptor_x_setup(
                name="my_rx",
                start_freq=0,  # 0 is a valid start; condition checks `is not None`
                stop_freq=10e9,
                step_freq=1e8,
            )
        fake_setup.add_sweep.assert_called_once()

    def test_no_sweep_when_stop_freq_missing(self):
        pedb = _make_pedb()
        ss = SimulationSetups(pedb)
        fake_setup = MagicMock()
        fake_setup.add_sweep = MagicMock()
        with patch.object(ss, "create", return_value=fake_setup):
            ss.create_raptor_x_setup(name="my_rx", start_freq=1e9)
        fake_setup.add_sweep.assert_not_called()


class TestCreateQ3dSetup:
    def test_creates_without_sweep(self):
        pedb = _make_pedb()
        ss = SimulationSetups(pedb)
        fake_setup = MagicMock()
        fake_setup.add_sweep = MagicMock()
        with patch.object(ss, "create", return_value=fake_setup):
            result = ss.create_q3d_setup(name="my_q3d")
        assert result is fake_setup
        fake_setup.add_sweep.assert_not_called()

    def test_creates_with_sweep_when_freq_params_provided(self):
        pedb = _make_pedb()
        ss = SimulationSetups(pedb)
        fake_setup = MagicMock()
        with patch.object(ss, "create", return_value=fake_setup):
            ss.create_q3d_setup(
                name="my_q3d",
                start_freq=1e9,
                stop_freq=10e9,
                step_freq=1e8,
            )
        fake_setup.add_sweep.assert_called_once()

    def test_applies_kwargs_as_attributes(self):
        pedb = _make_pedb()
        ss = SimulationSetups(pedb)
        fake_setup = MagicMock(spec=[])
        with patch.object(ss, "create", return_value=fake_setup):
            ss.create_q3d_setup(name="my_q3d", custom_opt=True)
        assert fake_setup.custom_opt is True
