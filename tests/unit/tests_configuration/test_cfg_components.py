# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.no_licence, pytest.mark.legacy]


from unittest.mock import MagicMock

import pytest

from pyedb.configuration.cfg_components import (
    CfgComponent,
    CfgComponents,
    CfgPinPairModel,
    _height_from_diameter,
    _smallest_pin_pad_size,
)


class TestHeightFromDiameter:
    def test_um(self):
        assert _height_from_diameter("150um") == "100um"

    def test_mm(self):
        result = _height_from_diameter("0.15mm")
        assert "mm" in result

    def test_no_unit_defaults_to_um(self):
        result = _height_from_diameter("150")
        assert "um" in result

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            _height_from_diameter("bad_value")


class TestSmallestPinPadSize:
    def _make_comp(self, pins):
        comp = MagicMock()
        comp.pins = {str(i): p for i, p in enumerate(pins)}
        return comp

    def _make_pin(self, bbox):
        p = MagicMock()
        p.bounding_box = bbox
        return p

    def test_single_valid_pin(self):
        pin = self._make_pin(((0, 0), (100e-6, 50e-6)))
        comp = self._make_comp([pin])
        assert _smallest_pin_pad_size(comp) == pytest.approx(50e-6)

    def test_no_bbox_skipped(self):
        pin = MagicMock(spec=[])  # no bounding_box attr
        comp = self._make_comp([pin])
        assert _smallest_pin_pad_size(comp) is None

    def test_empty_bbox_skipped(self):
        pin = self._make_pin(None)
        comp = self._make_comp([pin])
        assert _smallest_pin_pad_size(comp) is None

    def test_zero_size_skipped(self):
        pin = self._make_pin(((0, 0), (0, 0)))
        comp = self._make_comp([pin])
        assert _smallest_pin_pad_size(comp) is None

    def test_picks_smallest(self):
        p1 = self._make_pin(((0, 0), (200e-6, 200e-6)))
        p2 = self._make_pin(((0, 0), (50e-6, 50e-6)))
        comp = self._make_comp([p1, p2])
        assert _smallest_pin_pad_size(comp) == pytest.approx(50e-6)


class TestCfgPinPairModel:
    def test_minimal(self):
        m = CfgPinPairModel(first_pin="1", second_pin="2")
        assert m.first_pin == "1"
        assert m.resistance is None
        assert m.is_parallel is False

    def test_all_fields(self):
        m = CfgPinPairModel(
            first_pin="1",
            second_pin="2",
            resistance="100ohm",
            inductance="1nH",
            capacitance="10nF",
            is_parallel=True,
            resistance_enabled=True,
            inductance_enabled=True,
            capacitance_enabled=True,
        )
        d = m.model_dump()
        assert d["resistance"] == "100ohm"
        assert d["is_parallel"] is True
        assert d["capacitance_enabled"] is True


class TestComponentConfig:
    def test_minimal(self):
        c = CfgComponent("U1")
        d = c.to_dict()
        assert d == {"reference_designator": "U1"}

    def test_with_type_and_enabled(self):
        c = CfgComponent(_pedb="R1", part_type="resistor", enabled=False)
        d = c.to_dict()
        assert d["part_type"] == "resistor"
        assert d["enabled"] is False

    def test_enabled_true(self):
        c = CfgComponent("U1", part_type="ic", enabled=True)
        assert c.to_dict()["enabled"] is True

    def test_definition_and_placement_layer(self):
        c = CfgComponent("U1", definition="BGA_256", placement_layer="1_Top")
        d = c.to_dict()
        assert d["definition"] == "BGA_256"
        assert d["placement_layer"] == "1_Top"

    def test_pins(self):
        c = CfgComponent("U1", pins=["1", "2", "3"])
        assert c.to_dict()["pins"] == ["1", "2", "3"]

    def test_empty_pins_not_in_dict(self):
        c = CfgComponent("U1")
        assert "pins" not in c.to_dict()

    def test_pin_pair_rlc(self):
        c = CfgComponent("R1")
        c.add_pin_pair_rlc(first_pin="1", second_pin="2", resistance="1kohm", resistance_enabled=True)
        d = c.to_dict()
        assert len(d["pin_pair_model"]) == 1
        assert d["pin_pair_model"][0]["resistance"] == "1kohm"

    def test_pin_pair_rlc_all_fields(self):
        c = CfgComponent("R1")
        c.add_pin_pair_rlc(
            first_pin="1",
            second_pin="2",
            resistance="100ohm",
            inductance="1nH",
            capacitance="10nF",
            is_parallel=True,
            resistance_enabled=True,
            inductance_enabled=True,
            capacitance_enabled=True,
        )
        pp = c.to_dict()["pin_pair_model"][0]
        assert pp["is_parallel"] is True
        assert pp["inductance_enabled"] is True

    def test_multiple_pin_pair_rlc(self):
        c = CfgComponent("C1")
        c.add_pin_pair_rlc(first_pin="1", second_pin="2", capacitance="100nF", capacitance_enabled=True)
        c.add_pin_pair_rlc(first_pin="2", second_pin="3", resistance="10ohm", resistance_enabled=True)
        assert len(c.to_dict()["pin_pair_model"]) == 2

    def test_s_parameter_model(self):
        c = CfgComponent("U1")
        c.set_s_parameter_model(model_name="model1", model_path="/path/to/model.s2p", reference_net="GND")
        d = c.to_dict()
        assert d["s_parameter_model"]["model_name"] == "model1"
        assert d["s_parameter_model"]["reference_net"] == "GND"

    def test_spice_model(self):
        c = CfgComponent("U2")
        c.set_spice_model(model_name="ic_spice", model_path="/path/ic.sp", sub_circuit="IC_SUB")
        d = c.to_dict()
        assert d["spice_model"]["model_name"] == "ic_spice"
        assert d["spice_model"]["sub_circuit"] == "IC_SUB"

    def test_spice_model_terminal_pairs(self):
        c = CfgComponent("U2")
        c.set_spice_model("m", "/f.sp", terminal_pairs=[("1", "a"), ("2", "b")])
        assert c.spice_model["terminal_pairs"] == [("1", "a"), ("2", "b")]

    def test_spice_model_default_terminal_pairs(self):
        c = CfgComponent("U2")
        c.set_spice_model("m", "/f.sp")
        assert c.spice_model["terminal_pairs"] == []

    def test_netlist_model(self):
        c = CfgComponent("Q1")
        c.set_netlist_model(".subckt Q1 ...")
        d = c.to_dict()
        assert d["netlist_model"]["netlist"] == ".subckt Q1 ..."

    def test_ic_die_properties_default_not_in_dict(self):
        """Default ic_die {'type': 'no_die'} must be omitted when not explicitly set."""
        c = CfgComponent("U1")
        assert "ic_die_properties" not in c.to_dict()

    def test_ic_die_properties_no_die_explicit(self):
        c = CfgComponent("U1")
        c.set_ic_die_properties("no_die")
        d = c.to_dict()
        assert d["ic_die_properties"]["type"] == "no_die"

    def test_ic_die_properties_flip_chip(self):
        c = CfgComponent("U1")
        c.set_ic_die_properties(die_type="flip_chip", orientation="chip_down")
        d = c.to_dict()
        assert d["ic_die_properties"]["type"] == "flip_chip"
        assert d["ic_die_properties"]["orientation"] == "chip_down"

    def test_ic_die_properties_wire_bond(self):
        c = CfgComponent("U1")
        c.set_ic_die_properties(die_type="wire_bond", orientation="chip_up", height="200um")
        d = c.to_dict()
        assert d["ic_die_properties"]["height"] == "200um"

    def test_ic_die_no_height_when_not_wire_bond(self):
        c = CfgComponent("U1")
        c.set_ic_die_properties(die_type="flip_chip", orientation="chip_down", height="100um")
        assert "height" not in c.to_dict()["ic_die_properties"]

    def test_solder_ball_cylinder(self):
        c = CfgComponent("U1")
        c.set_solder_ball_properties(shape="cylinder", diameter="150um", height="100um")
        d = c.to_dict()
        assert d["solder_ball_properties"]["shape"] == "cylinder"
        assert d["solder_ball_properties"]["diameter"] == "150um"

    def test_solder_ball_height_auto_derived(self):
        """Height is derived as 2/3 * diameter when not provided."""
        c = CfgComponent("U1")
        c.set_solder_ball_properties(shape="cylinder", diameter="150um")
        assert c.solder_ball_properties["height"] == "100um"

    def test_solder_ball_diameter_default_when_no_pedb(self):
        """Diameter defaults to '150um' when no pedb and no diameter given."""
        c = CfgComponent("U1")
        c.set_solder_ball_properties()
        assert c.solder_ball_properties["diameter"] == "150um"

    def test_solder_ball_spheroid(self):
        c = CfgComponent("U1")
        c.set_solder_ball_properties(shape="spheroid", diameter="150um", height="100um", mid_diameter="130um")
        d = c.to_dict()
        assert d["solder_ball_properties"]["mid_diameter"] == "130um"

    def test_solder_ball_spheroid_mid_diameter_defaults_to_diameter(self):
        c = CfgComponent("U1")
        c.set_solder_ball_properties(shape="spheroid", diameter="150um", height="100um")
        assert c.solder_ball_properties["mid_diameter"] == "150um"

    def test_solder_ball_with_pedb_auto_size(self):
        """When pedb is attached and component exists, diameter is taken from pin pad size."""
        mock_pin = MagicMock()
        mock_pin.bounding_box = ((0, 0), (200e-6, 200e-6))
        mock_comp = MagicMock()
        mock_comp.pins = {"1": mock_pin}
        mock_pedb = MagicMock()
        mock_pedb.components.instances.get.return_value = mock_comp
        c = CfgComponent(mock_pedb, reference_designator="U1")
        c.set_solder_ball_properties(shape="cylinder")
        assert c.solder_ball_properties["diameter"] != "150um"

    def test_port_properties(self):
        c = CfgComponent("U1")
        c.set_port_properties(reference_height="50um", reference_size_auto=False)
        d = c.to_dict()
        assert d["port_properties"]["reference_height"] == "50um"
        assert d["port_properties"]["reference_size_auto"] is False

    def test_port_properties_defaults(self):
        c = CfgComponent("U1")
        c.set_port_properties()
        pp = c.port_properties
        assert pp["reference_height"] == "0"
        assert pp["reference_size_auto"] is True
        assert pp["reference_size_x"] == "0"
        assert pp["reference_size_y"] == "0"

    def test_set_parameters_to_edb_no_obj(self):
        """set_parameters_to_edb is a no-op when pyedb_obj is None."""
        c = CfgComponent("U1")
        c.set_parameters_to_edb()  # must not raise

    def test_retrieve_parameters_from_edb_no_obj(self):
        """retrieve_parameters_from_edb is a no-op when pyedb_obj is None."""
        c = CfgComponent("U1")
        c.retrieve_parameters_from_edb()  # must not raise

    def test_ic_die_properties_no_die(self):
        c = CfgComponent("U1")
        c.set_ic_die_properties("no_die")
        d = c.to_dict()
        assert d["ic_die_properties"]["type"] == "no_die"


class TestComponentsConfig:
    def test_empty(self):
        assert CfgComponents().to_list() == []

    def test_add_returns_component_config(self):
        cc = CfgComponents()
        comp = cc.add(reference_designator="R1", part_type="resistor")
        assert isinstance(comp, CfgComponent)

    def test_add_all_params(self):
        cc = CfgComponents()
        comp = cc.add("U1", part_type="ic", enabled=True, definition="BGA", placement_layer="1_Top")
        assert comp.definition == "BGA"
        assert comp.placement_layer == "1_Top"
        assert comp.enabled is True

    def test_to_list(self):
        cc = CfgComponents()
        cc.add(reference_designator="R1", part_type="resistor", enabled=True)
        cc.add(reference_designator="C1", part_type="capacitor")
        lst = cc.to_list()
        assert len(lst) == 2
        assert lst[0]["reference_designator"] == "R1"

    def test_clean(self):
        cc = CfgComponents()
        cc.add("R1")
        cc.clean()
        assert cc.components == []

    def test_get_cached(self):
        """get() returns existing component without querying EDB."""
        cc = CfgComponents()
        comp = cc.add("R1", part_type="resistor")
        result = cc.get("R1")
        assert result is comp

    def test_get_raises_without_pedb(self):
        cc = CfgComponents()
        with pytest.raises(KeyError):
            cc.get("R1")

    def test_get_raises_when_not_found(self):
        mock_pedb = MagicMock()
        mock_pedb.components.instances = {}
        cc = CfgComponents(pedb=mock_pedb)
        with pytest.raises(KeyError):
            cc.get("MISSING")

    def test_retrieve_parameters_from_edb_without_pedb(self):
        cc = CfgComponents()
        cc.add("R1")
        result = cc.retrieve_parameters_from_edb()
        # clean() is called first, then no pedb → returns serialized list of components at that moment
        assert isinstance(result, list)

    def test_retrieve_parameters_from_edb_clears_first(self):
        cc = CfgComponents()
        cc.add("R1")
        cc.retrieve_parameters_from_edb()
        assert len(cc.components) == 0  # clean() was called, no pedb to reload from

    def test_get_data_from_db_without_pedb(self):
        cc = CfgComponents()
        result = cc.get_data_from_db()
        assert result == []  # clean() wipes components, no pedb to reload

    def test_init_from_components_data(self):
        data = [{"reference_designator": "R1", "part_type": "resistor"}]
        cc = CfgComponents(components_data=data)
        assert len(cc.components) == 1
        assert cc.components[0].reference_designator == "R1"


# ---------------------------------------------------------------------------
# Vendor library model tests
# ---------------------------------------------------------------------------


class TestVendorLibraryModel:
    """Unit tests for CfgComponent.set_vendor_library_model() and the
    vendor_library_model field serialization / apply logic.

    All tests are license-free and rely entirely on ``unittest.mock``.
    """

    # ------------------------------------------------------------------
    # set_vendor_library_model – field population
    # ------------------------------------------------------------------

    def test_set_vendor_library_model_basic(self):
        """set_vendor_library_model() stores all mandatory fields correctly."""
        c = CfgComponent("C1", part_type="capacitor")
        c.set_vendor_library_model("Murata", "GRM15", "GRM155R71C104KA88", reference_net="GND")
        vlm = c.vendor_library_model
        assert vlm["vendor"] == "Murata"
        assert vlm["series"] == "GRM15"
        assert vlm["part_name"] == "GRM155R71C104KA88"
        assert vlm["reference_net"] == "GND"

    def test_set_vendor_library_model_default_reference_net(self):
        """reference_net defaults to 'GND' when not provided."""
        c = CfgComponent("C1")
        c.set_vendor_library_model("Murata", "GRM15", "GRM155R71C104KA88")
        assert c.vendor_library_model["reference_net"] == "GND"

    def test_set_vendor_library_model_with_cache_dir(self):
        """Optional touchstone_cache_dir is stored when given."""
        c = CfgComponent("C1")
        c.set_vendor_library_model("TDK", "C_MHZ", "C1608C0G1H103J080AA", touchstone_cache_dir="/tmp/snp")
        assert c.vendor_library_model["touchstone_cache_dir"] == "/tmp/snp"

    def test_set_vendor_library_model_no_cache_dir_key_when_none(self):
        """touchstone_cache_dir must not appear in the dict when not supplied."""
        c = CfgComponent("C1")
        c.set_vendor_library_model("Murata", "GRM15", "GRM155R71C104KA88")
        assert "touchstone_cache_dir" not in c.vendor_library_model

    def test_vendor_library_model_default_empty(self):
        """vendor_library_model is an empty dict on a freshly created component."""
        c = CfgComponent("C1")
        assert c.vendor_library_model == {}

    # ------------------------------------------------------------------
    # to_dict – serialization
    # ------------------------------------------------------------------

    def test_to_dict_includes_vendor_library_model(self):
        """to_dict() must contain vendor_library_model when set."""
        c = CfgComponent("C1", part_type="capacitor")
        c.set_vendor_library_model("Murata", "GRM15", "GRM155R71C104KA88", "GND")
        d = c.to_dict()
        assert "vendor_library_model" in d
        assert d["vendor_library_model"]["vendor"] == "Murata"
        assert d["vendor_library_model"]["part_name"] == "GRM155R71C104KA88"

    def test_to_dict_excludes_vendor_library_model_when_empty(self):
        """to_dict() must NOT include vendor_library_model when it is empty."""
        c = CfgComponent("C1")
        assert "vendor_library_model" not in c.to_dict()

    def test_to_dict_does_not_include_s_parameter_model_when_vendor_set(self):
        """Setting vendor_library_model must not pollute s_parameter_model."""
        c = CfgComponent("C1", part_type="capacitor")
        c.set_vendor_library_model("Murata", "GRM15", "GRM155R71C104KA88")
        d = c.to_dict()
        assert "s_parameter_model" not in d

    def test_round_trip_via_components_data(self):
        """CfgComponents can reconstruct a component with vendor_library_model from a dict."""
        data = [
            {
                "reference_designator": "C1",
                "part_type": "capacitor",
                "vendor_library_model": {
                    "vendor": "Murata",
                    "series": "GRM15",
                    "part_name": "GRM155R71C104KA88",
                    "reference_net": "GND",
                },
            }
        ]
        cc = CfgComponents(components_data=data)
        assert cc.components[0].vendor_library_model["vendor"] == "Murata"
        assert cc.components[0].vendor_library_model["part_name"] == "GRM155R71C104KA88"

    def test_round_trip_to_list(self):
        """to_list() preserves vendor_library_model through a round-trip."""
        cc = CfgComponents()
        c = cc.add("C1", part_type="capacitor")
        c.set_vendor_library_model("TDK", "C_MHZ", "C1608C0G1H103J080AA", "GND")
        lst = cc.to_list()
        assert lst[0]["vendor_library_model"]["vendor"] == "TDK"
        assert lst[0]["vendor_library_model"]["series"] == "C_MHZ"

    # ------------------------------------------------------------------
    # _set_vendor_library_model_to_edb – apply logic (fully mocked)
    # ------------------------------------------------------------------

    def _make_mock_pedb(self, part, vendor="Murata", series="GRM15", part_name="GRM155R71C104KA88", tmp_path=None):
        """Build a minimal mock pedb that serves ``get_vendor_libraries()``."""
        from pyedb.component_libraries.ansys_components import ComponentLib

        comp_lib = ComponentLib()
        comp_lib.capacitors = {vendor: {series: {part_name: part}}}
        comp_lib.inductors = {}

        mock_pedb = MagicMock()
        mock_pedb.components.get_vendor_libraries.return_value = comp_lib
        mock_pedb.edbpath = str(tmp_path or "/fake/design.aedb")
        return mock_pedb

    def test_apply_calls_write_touchstone(self, tmp_path):
        """_set_vendor_library_model_to_edb calls write_touchstone on the ComponentPart."""
        mock_part = MagicMock()
        snp_file = str(tmp_path / "GRM155R71C104KA88.s2p")
        mock_part.write_touchstone.return_value = snp_file

        mock_pedb = self._make_mock_pedb(mock_part, tmp_path=tmp_path)
        mock_pyedb_obj = MagicMock()

        c = CfgComponent(mock_pedb, mock_pyedb_obj, reference_designator="C1", part_type="capacitor")
        c.set_vendor_library_model("Murata", "GRM15", "GRM155R71C104KA88", "GND")
        c._set_vendor_library_model_to_edb()

        mock_part.write_touchstone.assert_called_once()
        written_path = mock_part.write_touchstone.call_args[0][0]
        assert "GRM155R71C104KA88" in written_path

    def test_apply_calls_assign_s_param_model(self, tmp_path):
        """assign_s_param_model is called with the exported Touchstone path."""
        mock_part = MagicMock()
        snp_file = str(tmp_path / "GRM155R71C104KA88.s2p")
        mock_part.write_touchstone.return_value = snp_file

        mock_pedb = self._make_mock_pedb(mock_part, tmp_path=tmp_path)
        mock_pyedb_obj = MagicMock()

        c = CfgComponent(mock_pedb, mock_pyedb_obj, reference_designator="C1", part_type="capacitor")
        c.set_vendor_library_model("Murata", "GRM15", "GRM155R71C104KA88", "GND")
        c._set_vendor_library_model_to_edb()

        mock_pyedb_obj.assign_s_param_model.assert_called_once_with(snp_file, "GRM155R71C104KA88", "GND")

    def test_apply_with_custom_cache_dir(self, tmp_path):
        """touchstone_cache_dir is used as the export directory when provided."""
        cache_dir = str(tmp_path / "my_cache")
        mock_part = MagicMock()
        mock_part.write_touchstone.return_value = str(tmp_path / "p.s2p")

        mock_pedb = self._make_mock_pedb(mock_part, tmp_path=tmp_path)
        mock_pyedb_obj = MagicMock()

        c = CfgComponent(mock_pedb, mock_pyedb_obj, reference_designator="C1", part_type="capacitor")
        c.set_vendor_library_model("Murata", "GRM15", "GRM155R71C104KA88", touchstone_cache_dir=cache_dir)
        c._set_vendor_library_model_to_edb()

        written_path = mock_part.write_touchstone.call_args[0][0]
        assert written_path.startswith(cache_dir)

    def test_apply_inductor_found_in_inductors(self, tmp_path):
        """Inductors are located from the inductors library section."""
        from pyedb.component_libraries.ansys_components import ComponentLib

        mock_part = MagicMock()
        snp_file = str(tmp_path / "LQW18AN4N7D00D.s2p")
        mock_part.write_touchstone.return_value = snp_file

        comp_lib = ComponentLib()
        comp_lib.capacitors = {}
        comp_lib.inductors = {"Murata": {"LQW18A": {"LQW18AN4N7D00D": mock_part}}}

        mock_pedb = MagicMock()
        mock_pedb.components.get_vendor_libraries.return_value = comp_lib
        mock_pedb.edbpath = str(tmp_path / "design.aedb")
        mock_pyedb_obj = MagicMock()

        c = CfgComponent(mock_pedb, mock_pyedb_obj, reference_designator="L1", part_type="inductor")
        c.set_vendor_library_model("Murata", "LQW18A", "LQW18AN4N7D00D", "GND")
        c._set_vendor_library_model_to_edb()

        mock_pyedb_obj.assign_s_param_model.assert_called_once_with(snp_file, "LQW18AN4N7D00D", "GND")

    def test_apply_missing_vendor_raises_key_error(self, tmp_path):
        """KeyError is raised when the requested vendor does not exist."""
        from pyedb.component_libraries.ansys_components import ComponentLib

        comp_lib = ComponentLib()
        comp_lib.capacitors = {}
        comp_lib.inductors = {}

        mock_pedb = MagicMock()
        mock_pedb.components.get_vendor_libraries.return_value = comp_lib
        mock_pedb.edbpath = str(tmp_path / "design.aedb")
        mock_pyedb_obj = MagicMock()

        c = CfgComponent(mock_pedb, mock_pyedb_obj, reference_designator="C1", part_type="capacitor")
        c.set_vendor_library_model("NonExistentVendor", "SomeSeries", "SomePart")
        with pytest.raises(KeyError, match="NonExistentVendor"):
            c._set_vendor_library_model_to_edb()

    def test_apply_missing_part_raises_key_error(self, tmp_path):
        """KeyError is raised when the requested part is not in the series."""
        from pyedb.component_libraries.ansys_components import ComponentLib

        comp_lib = ComponentLib()
        comp_lib.capacitors = {"Murata": {"GRM15": {"OTHER_PART": MagicMock()}}}
        comp_lib.inductors = {}

        mock_pedb = MagicMock()
        mock_pedb.components.get_vendor_libraries.return_value = comp_lib
        mock_pedb.edbpath = str(tmp_path / "design.aedb")
        mock_pyedb_obj = MagicMock()

        c = CfgComponent(mock_pedb, mock_pyedb_obj, reference_designator="C1", part_type="capacitor")
        c.set_vendor_library_model("Murata", "GRM15", "MISSING_PART")
        with pytest.raises(KeyError, match="MISSING_PART"):
            c._set_vendor_library_model_to_edb()

    def test_apply_empty_fields_raises_value_error(self, tmp_path):
        """ValueError is raised when vendor/series/part_name are empty strings."""
        mock_pedb = MagicMock()
        mock_pedb.edbpath = str(tmp_path / "design.aedb")
        mock_pyedb_obj = MagicMock()

        c = CfgComponent(mock_pedb, mock_pyedb_obj, reference_designator="C1")
        c.vendor_library_model = {"vendor": "", "series": "", "part_name": ""}
        with pytest.raises(ValueError, match="vendor_library_model requires"):
            c._set_vendor_library_model_to_edb()

    # ------------------------------------------------------------------
    # _set_model_properties_to_edb dispatch
    # ------------------------------------------------------------------

    def test_dispatch_uses_vendor_library_over_s_parameter(self, tmp_path):
        """vendor_library_model takes priority over s_parameter_model in dispatch."""
        from unittest.mock import patch

        mock_pedb = MagicMock()
        mock_pyedb_obj = MagicMock()

        c = CfgComponent(mock_pedb, mock_pyedb_obj, reference_designator="C1", part_type="capacitor")
        c.set_vendor_library_model("Murata", "GRM15", "GRM155R71C104KA88")
        c.s_parameter_model = {"model_name": "other", "model_path": "/f.s2p", "reference_net": "GND"}

        with patch.object(c, "_set_vendor_library_model_to_edb") as mock_vlm:
            c._set_model_properties_to_edb()
            mock_vlm.assert_called_once()
            mock_pyedb_obj.assign_s_param_model.assert_not_called()

    def test_dispatch_falls_through_to_s_parameter_when_no_vendor_model(self):
        """s_parameter_model is used when vendor_library_model is empty."""
        mock_pyedb_obj = MagicMock()
        c = CfgComponent(None, mock_pyedb_obj, reference_designator="C1")
        c.s_parameter_model = {"model_name": "m1", "model_path": "/f.s2p", "reference_net": "GND"}
        c._set_model_properties_to_edb()
        mock_pyedb_obj.assign_s_param_model.assert_called_once_with("/f.s2p", "m1", "GND")
