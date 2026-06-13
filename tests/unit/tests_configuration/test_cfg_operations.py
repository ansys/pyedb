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

from unittest.mock import MagicMock, patch

import pytest

from pyedb.configuration.cfg_data import CfgData
from pyedb.configuration.cfg_operations import CfgAutoIdentifyNets, CfgCutout, CfgOperations
from pyedb.configuration.configuration import Configuration

pytestmark = [pytest.mark.unit, pytest.mark.no_licence, pytest.mark.legacy]


def _make_configuration():
    """Return a ``Configuration`` instance wired to a minimal mock EDB."""
    mock_pedb = MagicMock()
    # get_materials iterates over this – keep it empty so no real material logic runs
    mock_pedb.materials.materials.items.return_value = []
    cfg_inst = Configuration.__new__(Configuration)
    cfg_inst._pedb = mock_pedb
    cfg_inst.data = {}
    cfg_inst._s_parameter_library = ""
    cfg_inst._spice_model_library = ""
    cfg_inst.cfg_data = CfgData(mock_pedb)
    return cfg_inst


class TestCfgAutoIdentifyNets:
    def test_defaults(self):
        a = CfgAutoIdentifyNets()
        assert a.enabled is False
        assert a.resistor_below == 100
        assert a.inductor_below == 1
        assert a.capacitor_above == "10nF"

    def test_custom_values(self):
        a = CfgAutoIdentifyNets(enabled=True, resistor_below=50, inductor_below=2, capacitor_above="1uF")
        assert a.enabled is True
        assert a.resistor_below == 50
        assert a.capacitor_above == "1uF"


class TestCfgCutout:
    def test_defaults(self):
        c = CfgCutout()
        assert c.extent_type == "ConvexHull"
        assert c.expansion_size == 0.002
        assert c.number_of_threads == 1
        assert c.custom_extent_units == "meter"
        assert c.expansion_factor == 0

    def test_signal_and_reference_nets(self):
        c = CfgCutout(signal_nets=["SIG"], reference_nets=["GND"])
        assert c.signal_nets == ["SIG"]
        assert c.reference_nets == ["GND"]

    def test_legacy_signal_list_alias(self):
        """signal_list key is accepted via AliasChoices."""
        c = CfgCutout.model_validate({"signal_list": ["SIG"], "reference_list": ["GND"]})
        assert c.signal_nets == ["SIG"]
        assert c.reference_nets == ["GND"]

    def test_extent_type_none(self):
        c = CfgCutout(extent_type=None)
        assert c.extent_type is None

    def test_extent_type_unknown_passthrough(self):
        """Unknown extent_type values pass through unchanged."""
        c = CfgCutout(extent_type="MyCustomExtent")
        assert c.extent_type == "MyCustomExtent"

    def test_extent_type_all_aliases(self):
        for value, expected in [
            ("convexhull", "ConvexHull"),
            ("convex_hull", "ConvexHull"),
            ("conforming", "Conformal"),
            ("conformal", "Conformal"),
            ("bounding", "BoundingBox"),
            ("boundingbox", "BoundingBox"),
            ("bounding_box", "BoundingBox"),
        ]:
            c = CfgCutout(extent_type=value)
            assert c.extent_type == expected, f"{value!r} → expected {expected!r}, got {c.extent_type!r}"

    def test_auto_identify_nets_default(self):
        c = CfgCutout()
        assert c.auto_identify_nets is not None
        assert c.auto_identify_nets.enabled is False

    def test_auto_identify_nets_from_flat_kwargs(self):
        """Flat kwargs are used to build auto_identify_nets via model_validator."""
        c = CfgCutout.model_validate(
            {"auto_identify_nets_enabled": True, "resistor_below": 50, "inductor_below": 2, "capacitor_above": "1uF"}
        )
        assert c.auto_identify_nets.enabled is True
        assert c.auto_identify_nets.resistor_below == 50

    def test_auto_identify_nets_explicit_skips_validator(self):
        """When auto_identify_nets is already present, the flat-kwargs validator is skipped."""
        ain = CfgAutoIdentifyNets(enabled=True, resistor_below=200)
        c = CfgCutout(auto_identify_nets=ain)
        assert c.auto_identify_nets.resistor_below == 200

    def test_model_dump_excludes_none(self):
        c = CfgCutout(signal_nets=["SIG"])
        d = c.model_dump()
        assert "custom_extent" not in d
        assert "signal_nets" in d

    def test_model_dump_explicit_include_none(self):
        c = CfgCutout(signal_nets=["SIG"])
        d = c.model_dump(exclude_none=False)
        assert "custom_extent" in d

    def test_nets(self):
        c = CfgCutout(signal_nets=["SIG1"], reference_nets=["GND"])
        d = c.model_dump(exclude_none=True)
        assert d["signal_nets"] == ["SIG1"]
        assert d["reference_nets"] == ["GND"]

    def test_auto_identify_nets(self):
        c = CfgCutout(auto_identify_nets_enabled=True, resistor_below=200)
        d = c.model_dump(exclude_none=True)
        assert d["auto_identify_nets"]["enabled"] is True
        assert d["auto_identify_nets"]["resistor_below"] == 200

    def test_extent_type_convexhull(self):
        c = CfgCutout(extent_type="ConvexHull")
        assert c.model_dump(exclude_none=True)["extent_type"] == "ConvexHull"

    def test_extent_type_bounding_box(self):
        c = CfgCutout(extent_type="BoundingBox")
        assert c.model_dump(exclude_none=True)["extent_type"] == "BoundingBox"

    def test_extent_type_conformal(self):
        c = CfgCutout(extent_type="Conformal")
        assert c.model_dump(exclude_none=True)["extent_type"] == "Conformal"

    def test_extent_type_case_insensitive_lower(self):
        c = CfgCutout(extent_type="convexhull")
        assert c.model_dump(exclude_none=True)["extent_type"] == "ConvexHull"

    def test_extent_type_case_insensitive_upper(self):
        c = CfgCutout(extent_type="CONVEXHULL")
        assert c.model_dump(exclude_none=True)["extent_type"] == "ConvexHull"

    def test_extent_type_case_insensitive_boundingbox(self):
        c = CfgCutout(extent_type="boundingbox")
        assert c.model_dump(exclude_none=True)["extent_type"] == "BoundingBox"

    def test_extent_type_case_insensitive_conformal(self):
        c = CfgCutout(extent_type="CONFORMAL")
        assert c.model_dump(exclude_none=True)["extent_type"] == "Conformal"

    def test_expansion_size(self):
        c = CfgCutout(expansion_size=0.005)
        assert c.model_dump(exclude_none=True)["expansion_size"] == 0.005

    def test_expansion_factor(self):
        c = CfgCutout(expansion_factor=0.1)
        assert c.model_dump(exclude_none=True)["expansion_factor"] == 0.1


class TestOperationsConfig:
    def test_empty(self):
        d = CfgOperations().model_dump()
        assert d.get("cutout") is None
        assert d["generate_auto_hfss_regions"] is False

    def test_add_cutout(self):
        ops = CfgOperations()
        c = ops.add_cutout(signal_nets=["SIG1"], reference_nets=["GND"])
        assert isinstance(c, CfgCutout)
        d = ops.model_dump()
        assert "cutout" in d
        assert d["cutout"]["signal_nets"] == ["SIG1"]

    def test_add_cutout_extent_type_convexhull(self):
        ops = CfgOperations()
        ops.add_cutout(signal_nets=["SIG"], reference_nets=["GND"], extent_type="ConvexHull")
        assert ops.model_dump(exclude_none=True)["cutout"]["extent_type"] == "ConvexHull"

    def test_add_cutout_extent_type_case_insensitive(self):
        ops = CfgOperations()
        ops.add_cutout(signal_nets=["SIG"], reference_nets=["GND"], extent_type="convexhull")
        assert ops.model_dump(exclude_none=True)["cutout"]["extent_type"] == "ConvexHull"

    def test_add_cutout_extent_type_boundingbox_case_insensitive(self):
        ops = CfgOperations()
        ops.add_cutout(signal_nets=["SIG"], reference_nets=["GND"], extent_type="BOUNDINGBOX")
        assert ops.model_dump(exclude_none=True)["cutout"]["extent_type"] == "BoundingBox"

    def test_add_cutout_expansion_size(self):
        ops = CfgOperations()
        ops.add_cutout(signal_nets=["SIG"], reference_nets=["GND"], expansion_size=0.003)
        assert ops.model_dump(exclude_none=True)["cutout"]["expansion_size"] == 0.003

    def test_generate_auto_hfss_regions(self):
        ops = CfgOperations()
        ops.generate_auto_hfss_regions = True
        d = ops.model_dump(exclude_none=True)
        assert d["generate_auto_hfss_regions"] is True

    def test_add_cutout_auto_identify_nets(self):
        ops = CfgOperations()
        ops.add_cutout(
            signal_nets=["SIG"],
            reference_nets=["GND"],
            auto_identify_nets_enabled=True,
            resistor_below=50,
            inductor_below=2,
            capacitor_above="1uF",
        )
        ain = ops.cutout.auto_identify_nets
        assert ain.enabled is True
        assert ain.resistor_below == 50
        assert ain.capacitor_above == "1uF"

    def test_add_cutout_returns_cutout(self):
        ops = CfgOperations()
        result = ops.add_cutout()
        assert result is ops.cutout

    def test_model_dump_excludes_none_by_default(self):
        ops = CfgOperations()
        ops.add_cutout(signal_nets=["SIG"])
        d = ops.model_dump()
        assert "reference_nets" not in d["cutout"]


class TestConfigurationExportPreservesExistingCutout:
    """Regression tests for the export bug where get_operations() silently
    overwrote a correctly-populated cutout configuration, losing reference_nets,
    expansion_size and expansion_factor.

    Fix: ``get_data_from_db(operations=True)`` now skips ``get_operations()``
    when ``cfg_data.operations.cutout`` is already set.
    """

    def test_export_keeps_signal_nets(self):
        """Signal nets from the original cutout config survive export."""
        cfg_inst = _make_configuration()
        cfg_inst.cfg_data.operations.add_cutout(
            signal_nets=["PCIe_RX0_P", "PCIe_RX0_N"],
            reference_nets=["GND"],
            expansion_size=3e-3,
            expansion_factor=0.5,
        )
        data = cfg_inst.get_data_from_db(operations=True)
        assert set(data["operations"]["cutout"]["signal_nets"]) == {"PCIe_RX0_P", "PCIe_RX0_N"}

    def test_export_keeps_reference_nets(self):
        """Reference nets must not be empty when the cutout was configured explicitly."""
        cfg_inst = _make_configuration()
        cfg_inst.cfg_data.operations.add_cutout(
            signal_nets=["SIG"],
            reference_nets=["GND"],
        )
        data = cfg_inst.get_data_from_db(operations=True)
        assert data["operations"]["cutout"]["reference_nets"] == ["GND"]

    def test_export_reference_nets_not_mixed_into_signal_nets(self):
        """GND must not appear in signal_nets after export."""
        cfg_inst = _make_configuration()
        cfg_inst.cfg_data.operations.add_cutout(
            signal_nets=["SIG1", "SIG2"],
            reference_nets=["GND"],
        )
        data = cfg_inst.get_data_from_db(operations=True)
        assert "GND" not in data["operations"]["cutout"]["signal_nets"]

    def test_export_keeps_expansion_size(self):
        """Custom expansion_size is preserved in the exported JSON."""
        cfg_inst = _make_configuration()
        cfg_inst.cfg_data.operations.add_cutout(
            signal_nets=["SIG"],
            reference_nets=["GND"],
            expansion_size=3e-3,
        )
        data = cfg_inst.get_data_from_db(operations=True)
        assert data["operations"]["cutout"]["expansion_size"] == pytest.approx(3e-3)

    def test_export_keeps_expansion_factor(self):
        """Custom expansion_factor is preserved in the exported JSON."""
        cfg_inst = _make_configuration()
        cfg_inst.cfg_data.operations.add_cutout(
            signal_nets=["SIG"],
            reference_nets=["GND"],
            expansion_factor=0.5,
        )
        data = cfg_inst.get_data_from_db(operations=True)
        assert data["operations"]["cutout"]["expansion_factor"] == pytest.approx(0.5)

    def test_export_does_not_call_get_operations_when_cutout_set(self):
        """get_operations() must NOT be called when cutout is already configured."""
        cfg_inst = _make_configuration()
        cfg_inst.cfg_data.operations.add_cutout(signal_nets=["SIG"], reference_nets=["GND"])
        with patch.object(cfg_inst, "get_operations") as mock_get_ops:
            cfg_inst.get_data_from_db(operations=True)
        mock_get_ops.assert_not_called()

    def test_export_calls_get_operations_when_no_cutout_set(self):
        """get_operations() IS called when no cutout has been configured yet."""
        cfg_inst = _make_configuration()
        # cutout is None by default – so get_operations() should be triggered
        with patch.object(cfg_inst, "get_operations") as mock_get_ops:
            cfg_inst.get_data_from_db(operations=True)
        mock_get_ops.assert_called_once()


class TestGetOperationsNetsClassification:
    """Regression tests for the get_operations() bug where all nets were
    lumped into signal_nets with reference_nets always set to [].

    Fix: nets are now split using ``net_obj.is_power_ground``.
    """

    def _make_net_mock(self, name, is_power_ground, layer_name="Signal_Layer"):
        net = MagicMock()
        net.is_power_ground = is_power_ground
        prim = MagicMock()
        prim.layer.name = layer_name
        net.primitives = [prim]
        return name, net

    def _setup_configuration_with_nets(self, nets_spec):
        """Build a Configuration whose mock EDB has a pyedb_cutout layer and
        the nets described by *nets_spec*: list of (name, is_power_ground).
        """
        cfg_inst = _make_configuration()
        mock_pedb = cfg_inst._pedb

        # Simulate a pyedb_cutout layer being present
        mock_pedb.stackup.all_layers = {"pyedb_cutout": MagicMock()}

        # A single polygon on the cutout layer (custom_extent)
        poly = MagicMock()
        poly.polygon_data.points = [[0, 0], [1, 0], [1, 1], [0, 1]]
        mock_pedb.layout.find_primitive.return_value = [poly]

        # Build the nets dict
        nets = {}
        for name, is_pg in nets_spec:
            _, net_obj = self._make_net_mock(name, is_pg)
            nets[name] = net_obj
        mock_pedb.nets.nets = nets

        return cfg_inst

    def test_signal_net_goes_to_signal_nets(self):
        cfg_inst = self._setup_configuration_with_nets([("SIG1", False), ("GND", True)])
        cfg_inst.get_operations()
        assert "SIG1" in cfg_inst.cfg_data.operations.cutout.signal_nets

    def test_power_ground_net_goes_to_reference_nets(self):
        cfg_inst = self._setup_configuration_with_nets([("SIG1", False), ("GND", True)])
        cfg_inst.get_operations()
        assert "GND" in cfg_inst.cfg_data.operations.cutout.reference_nets

    def test_power_ground_net_not_in_signal_nets(self):
        cfg_inst = self._setup_configuration_with_nets([("SIG1", False), ("GND", True)])
        cfg_inst.get_operations()
        assert "GND" not in cfg_inst.cfg_data.operations.cutout.signal_nets

    def test_signal_net_not_in_reference_nets(self):
        cfg_inst = self._setup_configuration_with_nets([("SIG1", False), ("GND", True)])
        cfg_inst.get_operations()
        assert "SIG1" not in cfg_inst.cfg_data.operations.cutout.reference_nets

    def test_reference_nets_not_empty_when_power_ground_present(self):
        """reference_nets must not be an empty list when GND-class nets exist."""
        cfg_inst = self._setup_configuration_with_nets([("SIG", False), ("PWR", True), ("GND", True)])
        cfg_inst.get_operations()
        assert cfg_inst.cfg_data.operations.cutout.reference_nets  # non-empty

    def test_nets_on_cutout_layer_excluded(self):
        """Nets whose only primitive lives on the pyedb_cutout layer are excluded."""
        cfg_inst = _make_configuration()
        mock_pedb = cfg_inst._pedb
        mock_pedb.stackup.all_layers = {"pyedb_cutout": MagicMock()}
        poly = MagicMock()
        poly.polygon_data.points = []
        mock_pedb.layout.find_primitive.return_value = [poly]

        # Create one normal net and one net whose primitive is on pyedb_cutout
        sig_net = MagicMock()
        sig_net.is_power_ground = False
        sig_prim = MagicMock()
        sig_prim.layer.name = "Signal_Layer"
        sig_net.primitives = [sig_prim]

        cutout_net = MagicMock()
        cutout_net.is_power_ground = False
        cut_prim = MagicMock()
        cut_prim.layer.name = "pyedb_cutout"
        cutout_net.primitives = [cut_prim]

        mock_pedb.nets.nets = {"SIG": sig_net, "CUTOUT_OUTLINE": cutout_net}

        cfg_inst.get_operations()
        assert "CUTOUT_OUTLINE" not in cfg_inst.cfg_data.operations.cutout.signal_nets
        assert "SIG" in cfg_inst.cfg_data.operations.cutout.signal_nets

    def test_no_pyedb_cutout_layer_leaves_cutout_none(self):
        """When pyedb_cutout layer is absent, get_operations() is a no-op."""
        cfg_inst = _make_configuration()
        cfg_inst._pedb.stackup.all_layers = {"top": MagicMock(), "bot": MagicMock()}
        cfg_inst.get_operations()
        assert cfg_inst.cfg_data.operations.cutout is None


class TestConfigurationExportJsonFile:
    """End-to-end tests that exercise ``Configuration.export()`` and verify
    the written JSON file contains the correct cutout parameters.

    This directly reproduces the user-reported bug:
    * ``reference_nets`` was exported as ``[]`` (GND moved to ``signal_nets``)
    * ``expansion_size`` / ``expansion_factor`` values were lost
    """

    def _make_export_configuration(self):
        """Configuration instance with enough mocking to call export()."""
        cfg_inst = _make_configuration()
        mock_pedb = cfg_inst._pedb
        # Stubs for paths called by get_data_from_db when flags other than
        # operations are False – most are never reached, but logger.info is.
        mock_pedb.logger.info.return_value = None
        return cfg_inst

    def _export_operations_only(self, cfg_inst, tmp_path):
        """Call export() with only operations=True, return parsed JSON dict."""
        import json as _json

        json_path = tmp_path / "cutout_config.json"
        cfg_inst.export(
            file_path=str(json_path),
            stackup=False,
            nets=False,
            pin_groups=False,
            ports=False,
            setups=False,
            operations=True,
            components=False,
            padstacks=False,
            boundaries=False,
            s_parameters=False,
            spice_models=False,
            variables=False,
            general=False,
            sources=False,
        )
        assert json_path.exists(), "export() must create the JSON file"
        with open(json_path, encoding="utf-8") as fh:
            return _json.load(fh)

    def test_json_signal_nets_correct(self, tmp_path):
        """signal_nets in the JSON must match what was passed to add_cutout()."""
        cfg_inst = self._make_export_configuration()
        cfg_inst.cfg_data.operations.add_cutout(
            signal_nets=["PCIe_Gen4_RX0_P", "PCIe_Gen4_RX0_N"],
            reference_nets=["GND"],
            expansion_size=3e-3,
        )
        data = self._export_operations_only(cfg_inst, tmp_path)
        assert set(data["operations"]["cutout"]["signal_nets"]) == {"PCIe_Gen4_RX0_P", "PCIe_Gen4_RX0_N"}

    def test_json_reference_nets_not_empty(self, tmp_path):
        """reference_nets must NOT be an empty list in the exported JSON."""
        cfg_inst = self._make_export_configuration()
        cfg_inst.cfg_data.operations.add_cutout(
            signal_nets=["SIG"],
            reference_nets=["GND"],
        )
        data = self._export_operations_only(cfg_inst, tmp_path)
        assert data["operations"]["cutout"]["reference_nets"] != []

    def test_json_reference_nets_value(self, tmp_path):
        """reference_nets in the JSON must equal the value passed to add_cutout()."""
        cfg_inst = self._make_export_configuration()
        cfg_inst.cfg_data.operations.add_cutout(
            signal_nets=["SIG"],
            reference_nets=["GND"],
        )
        data = self._export_operations_only(cfg_inst, tmp_path)
        assert data["operations"]["cutout"]["reference_nets"] == ["GND"]

    def test_json_gnd_not_in_signal_nets(self, tmp_path):
        """GND must not appear inside signal_nets in the exported JSON."""
        cfg_inst = self._make_export_configuration()
        cfg_inst.cfg_data.operations.add_cutout(
            signal_nets=["PCIe_Gen4_RX0_P", "PCIe_Gen4_RX0_N"],
            reference_nets=["GND"],
        )
        data = self._export_operations_only(cfg_inst, tmp_path)
        assert "GND" not in data["operations"]["cutout"]["signal_nets"]

    def test_json_multiple_reference_nets(self, tmp_path):
        """Multiple reference nets must all appear in the exported JSON."""
        cfg_inst = self._make_export_configuration()
        cfg_inst.cfg_data.operations.add_cutout(
            signal_nets=["SIG"],
            reference_nets=["GND", "AGND", "PGND"],
        )
        data = self._export_operations_only(cfg_inst, tmp_path)
        assert set(data["operations"]["cutout"]["reference_nets"]) == {"GND", "AGND", "PGND"}

    def test_json_expansion_size_written(self, tmp_path):
        """expansion_size must be present in the exported JSON."""
        cfg_inst = self._make_export_configuration()
        cfg_inst.cfg_data.operations.add_cutout(
            signal_nets=["SIG"],
            reference_nets=["GND"],
            expansion_size=3e-3,
        )
        data = self._export_operations_only(cfg_inst, tmp_path)
        assert "expansion_size" in data["operations"]["cutout"]

    def test_json_expansion_size_value(self, tmp_path):
        """expansion_size value in the JSON must match the configured value."""
        cfg_inst = self._make_export_configuration()
        cfg_inst.cfg_data.operations.add_cutout(
            signal_nets=["SIG"],
            reference_nets=["GND"],
            expansion_size=3e-3,
        )
        data = self._export_operations_only(cfg_inst, tmp_path)
        assert data["operations"]["cutout"]["expansion_size"] == pytest.approx(3e-3)

    def test_json_expansion_factor_written(self, tmp_path):
        """expansion_factor must be present in the exported JSON."""
        cfg_inst = self._make_export_configuration()
        cfg_inst.cfg_data.operations.add_cutout(
            signal_nets=["SIG"],
            reference_nets=["GND"],
            expansion_factor=0.5,
        )
        data = self._export_operations_only(cfg_inst, tmp_path)
        assert "expansion_factor" in data["operations"]["cutout"]

    def test_json_expansion_factor_value(self, tmp_path):
        """expansion_factor value in the JSON must match the configured value."""
        cfg_inst = self._make_export_configuration()
        cfg_inst.cfg_data.operations.add_cutout(
            signal_nets=["SIG"],
            reference_nets=["GND"],
            expansion_factor=0.5,
        )
        data = self._export_operations_only(cfg_inst, tmp_path)
        assert data["operations"]["cutout"]["expansion_factor"] == pytest.approx(0.5)

    def test_json_full_pcie_scenario(self, tmp_path):
        """Reproduce the user's exact cutout config and verify all fields in JSON."""
        SIGNAL_NETS = [
            "PCIe_Gen4_RX0_P",
            "PCIe_Gen4_RX0_N",
            "PCIe_Gen4_RX1_P",
            "PCIe_Gen4_RX1_N",
        ]
        REFERENCE_NET = "GND"

        cfg_inst = self._make_export_configuration()
        cfg_inst.cfg_data.operations.add_cutout(
            signal_nets=SIGNAL_NETS,
            reference_nets=[REFERENCE_NET],
            extent_type="ConvexHull",
            expansion_size=3e-3,
        )
        data = self._export_operations_only(cfg_inst, tmp_path)
        cutout = data["operations"]["cutout"]

        # signal nets
        assert set(cutout["signal_nets"]) == set(SIGNAL_NETS)
        # reference nets not empty and correct
        assert cutout["reference_nets"] == [REFERENCE_NET]
        # GND must not bleed into signal nets
        assert REFERENCE_NET not in cutout["signal_nets"]
        # expansion_size preserved
        assert cutout["expansion_size"] == pytest.approx(3e-3)
        # extent_type preserved
        assert cutout["extent_type"] == "ConvexHull"
