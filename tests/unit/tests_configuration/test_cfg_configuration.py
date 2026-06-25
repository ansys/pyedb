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

import json
from unittest.mock import MagicMock

import pytest
import toml

from pyedb.configuration.cfg_common import CfgBase, CfgVariables
from pyedb.configuration.cfg_data import CfgData
from pyedb.configuration.cfg_package_definition import CfgHeatSink
from pyedb.configuration.cfg_ports_sources import CfgTerminalInfo as TerminalInfo
from pyedb.configuration.cfg_terminals import CfgTerminals

EdbConfigBuilder = CfgData
VariablesConfig = CfgVariables
TerminalsConfig = CfgTerminals
HeatSinkConfig = CfgHeatSink

pytestmark = [pytest.mark.unit, pytest.mark.no_licence, pytest.mark.legacy]


class TestVariablesConfig:
    def test_numeric_value(self):
        v = VariablesConfig()
        v.add("via_diam", 0.2)
        assert v.variables[0].value == 0.2


class TestEdbConfigBuilder:
    def _full_builder(self) -> EdbConfigBuilder:
        cfg = EdbConfigBuilder()

        # general
        cfg.general.spice_model_library = "/models/spice"
        cfg.general.s_parameter_library = "/models/snp"
        cfg.general.anti_pads_always_on = False
        cfg.general.suppress_pads = True

        # stackup
        cfg.stackup.add_material("copper", conductivity=5.8e7)
        cfg.stackup.add_material("fr4", permittivity=4.4, dielectric_loss_tangent=0.02)
        cfg.stackup.add_signal_layer("top", material="copper", fill_material="fr4", thickness="35um")
        cfg.stackup.add_dielectric_layer("diel1", material="fr4", thickness="100um")
        cfg.stackup.add_signal_layer("bot", material="copper", fill_material="fr4", thickness="35um")

        # nets
        cfg.nets.add_signal_nets(["DDR4_DQ0", "DDR4_DQ1", "CLK"])
        cfg.nets.add_power_ground_nets(["VDD", "VCC", "GND"])

        # components
        r1 = cfg.components.add("R1", part_type="resistor", enabled=True)
        r1.add_pin_pair_rlc("1", "2", resistance="100ohm", resistance_enabled=True)
        c1 = cfg.components.add("C1", part_type="capacitor")
        c1.add_pin_pair_rlc("1", "2", capacitance="100nF", capacitance_enabled=True)
        u1 = cfg.components.add("U1", part_type="ic")
        u1.set_ic_die_properties("flip_chip", orientation="chip_down")
        u1.set_solder_ball_properties("cylinder", "150um", "100um")
        u1.set_port_properties(reference_height="50um")

        # padstacks
        cfg.padstacks.add_definition("via_0.2", material="copper", hole_plating_thickness="25um")
        inst = cfg.padstacks.add_instance(name="v1", net_name="GND", layer_range=["top", "bot"])
        inst.set_backdrill("L3", "0.25mm", drill_from_bottom=True)

        # pin groups
        cfg.pin_groups.add("pg_VDD", "U1", net="VDD")
        cfg.pin_groups.add("pg_GND", "U1", pins=["A1", "A2", "B1"])

        # ports
        cfg.ports.add_circuit_port("port_U1", {"pin_group": "pg_VDD"}, {"pin_group": "pg_GND"}, impedance=50)
        cfg.ports.add_wave_port("wport1", "trace1", [0.001, 0.002], horizontal_extent_factor=6)
        cfg.ports.add_coax_port("coax1", padstack="v1")  # padstack shortcut
        cfg.ports.add_diff_wave_port(
            "diff1",
            {"primitive_name": "tp", "point_on_edge": [0, 0]},
            {"primitive_name": "tn", "point_on_edge": [0, 1e-4]},
        )

        # sources
        cfg.sources.add_current_source("isrc1", {"pin_group": "pg_VDD"}, {"pin_group": "pg_GND"}, magnitude=0.5)
        cfg.sources.add_voltage_source("vsrc1", {"net": "VDD"}, {"net": "GND"}, magnitude=1.0)

        # probes
        cfg.probes.add("probe1", {"net": "DDR4_DQ0"}, {"net": "GND"})

        # setups – HFSS broadband (inline sweep syntax)
        hfss = cfg.setups.add_hfss_setup(name="hfss_bb")
        hfss.set_broadband_adaptive("1GHz", "20GHz", max_passes=20, max_delta=0.02)
        hfss.set_auto_mesh_operation(enabled=True)
        hfss.add_length_mesh_operation("mesh1", {"DDR4_DQ0": ["top"]}, max_length="0.5mm")
        # inline: start/stop/step_or_count/distribution instead of chaining
        hfss.add_frequency_sweep(
            "sweep1",
            start="1GHz",
            stop="20GHz",
            step_or_count=100,
            distribution="linear_count",
        )
        # chained (still works): add second range on same sweep
        s1 = hfss.add_frequency_sweep("sweep1b")
        s1.add_linear_count_frequencies("1GHz", "20GHz", 100)
        s1.add_single_frequency("5GHz")

        # setups – HFSS single
        hfss2 = cfg.setups.add_hfss_setup(name="hfss_single")
        hfss2.set_single_frequency_adaptive("5GHz", max_passes=15)

        # setups – HFSS multi-freq
        hfss3 = cfg.setups.add_hfss_setup(name="hfss_multi")
        hfss3.add_multi_frequency_adaptive("2GHz")
        hfss3.add_multi_frequency_adaptive("10GHz")

        # setups – SIwave AC (inline sweep syntax)
        siw = cfg.setups.add_siwave_ac_setup(name="siw_ac", si_slider_position=2, pi_slider_position=1)
        siw.add_frequency_sweep(
            "siw_sw1",
            start="1kHz",
            stop="1GHz",
            step_or_count=100,
            distribution="log_count",
        )

        # setups – SIwave DC
        cfg.setups.add_siwave_dc_setup(name="siw_dc", dc_slider_position=1, export_dc_thermal_data=True)

        # boundaries
        cfg.boundaries.set_radiation_boundary()
        cfg.boundaries.set_air_box_extents(0.15, truncate_at_ground=True)

        # operations
        cfg.operations.add_cutout(
            signal_nets=["DDR4_DQ0", "CLK"],
            reference_nets=["GND"],
            extent_type="ConvexHull",
            expansion_size=0.002,
            auto_identify_nets_enabled=True,
        )
        cfg.operations.generate_auto_hfss_regions = True

        # s-parameters
        cfg.s_parameters.add("cap_model", "CAP_100nF", "/snp/cap.s2p", reference_net="GND")
        cfg.s_parameters.add(
            "res_model", "RES_100OHM", "/snp/res.s2p", apply_to_all=False, components=["R1"], reference_net="GND"
        )

        # spice models
        cfg.spice_models.add("ic_spice", "IC_U1", "/spice/ic.sp", sub_circuit_name="IC_TOP")

        # variables
        cfg.variables.add("trace_width", "0.15mm", "Default trace width")
        cfg.variables.add("via_diameter", 0.2)

        # modeler
        cfg.modeler.add_trace("trace1", "top", "0.15mm", net_name="DDR4_DQ0", path=[[0, 0], [0.01, 0]])
        cfg.modeler.add_rectangular_plane(
            "bot", "gnd_plane", "GND", lower_left_point=[-0.05, -0.05], upper_right_point=[0.05, 0.05]
        )
        cfg.modeler.add_circular_plane("top", "via_plane", "VDD", radius="0.5mm", position=[0, 0])
        cfg.modeler.add_polygon_plane("bot", "poly1", "VCC", points=[[0, 0], [0.01, 0], [0.01, 0.01], [0, 0.01]])
        cfg.modeler.delete_primitives_by_layer(["old_layer"])
        cfg.modeler.delete_primitives_by_net(["old_net"])

        return cfg

    # -- top-level keys --
    def test_all_sections_present(self):
        cfg = self._full_builder()
        d = cfg.to_dict()
        expected = {
            "general",
            "stackup",
            "nets",
            "components",
            "padstacks",
            "pin_groups",
            "ports",
            "sources",
            "probes",
            "setups",
            "boundaries",
            "operations",
            "s_parameters",
            "spice_models",
            "variables",
            "modeler",
        }
        assert expected == set(d.keys())

    # -- general --
    def test_general_content(self):
        d = self._full_builder().to_dict()
        assert d["general"]["spice_model_library"] == "/models/spice"
        assert d["general"]["anti_pads_always_on"] is False

    # -- stackup --
    def test_stackup_materials(self):
        d = self._full_builder().to_dict()
        material_names = [m["name"] for m in d["stackup"]["materials"]]
        assert "copper" in material_names
        assert "fr4" in material_names

    def test_stackup_layers_order(self):
        d = self._full_builder().to_dict()
        names = [l["name"] for l in d["stackup"]["layers"]]
        assert names == ["top", "diel1", "bot"]

    # -- nets --
    def test_nets_signal(self):
        d = self._full_builder().to_dict()
        assert "DDR4_DQ0" in d["nets"]["signal_nets"]
        assert "CLK" in d["nets"]["signal_nets"]

    def test_nets_power(self):
        d = self._full_builder().to_dict()
        assert "GND" in d["nets"]["power_ground_nets"]

    # -- components --
    def test_components_count(self):
        d = self._full_builder().to_dict()
        assert len(d["components"]) == 3

    def test_component_r1(self):
        d = self._full_builder().to_dict()
        r1 = next(c for c in d["components"] if c["reference_designator"] == "R1")
        assert r1["pin_pair_model"][0]["resistance"] == "100ohm"

    def test_component_u1_ic(self):
        d = self._full_builder().to_dict()
        u1 = next(c for c in d["components"] if c["reference_designator"] == "U1")
        assert u1["ic_die_properties"]["type"] == "flip_chip"
        assert u1["solder_ball_properties"]["shape"] == "cylinder"

    # -- padstacks --
    def test_padstack_definition(self):
        d = self._full_builder().to_dict()
        defn = d["padstacks"]["definitions"][0]
        assert defn["name"] == "via_0.2"
        assert defn["material"] == "copper"

    def test_padstack_instance_backdrill(self):
        d = self._full_builder().to_dict()
        inst = d["padstacks"]["instances"][0]
        assert inst["name"] == "v1"
        assert "from_bottom" in inst["backdrill_parameters"]

    # -- pin groups --
    def test_pin_groups(self):
        d = self._full_builder().to_dict()
        names = [pg["name"] for pg in d["pin_groups"]]
        assert "pg_VDD" in names
        assert "pg_GND" in names

    # -- ports --
    def test_ports_types(self):
        d = self._full_builder().to_dict()
        types = {p["type"] for p in d["ports"]}
        assert types == {"circuit", "wave_port", "coax", "diff_wave_port"}

    def test_circuit_port_impedance(self):
        d = self._full_builder().to_dict()
        cp = next(p for p in d["ports"] if p["type"] == "circuit")
        assert cp["impedance"] == 50

    # -- sources --
    def test_sources(self):
        d = self._full_builder().to_dict()
        types = {s["type"] for s in d["sources"]}
        assert types == {"current", "voltage"}

    def test_current_source_magnitude(self):
        d = self._full_builder().to_dict()
        isrc = next(s for s in d["sources"] if s["type"] == "current")
        assert isrc["magnitude"] == 0.5

    # -- probes --
    def test_probes(self):
        d = self._full_builder().to_dict()
        assert len(d["probes"]) == 1
        assert d["probes"][0]["name"] == "probe1"

    # -- setups --
    def test_setup_types(self):
        d = self._full_builder().to_dict()
        types = [s["type"] for s in d["setups"]]
        assert types.count("hfss") == 3
        assert "siwave_ac" in types
        assert "siwave_dc" in types

    def test_hfss_broadband_setup(self):
        d = self._full_builder().to_dict()
        bb = next(s for s in d["setups"] if s["name"] == "hfss_bb")
        assert bb["adapt_type"] == "broadband"
        assert bb["broadband_adaptive_solution"]["low_frequency"] == "1GHz"

    def test_hfss_mesh_operation(self):
        d = self._full_builder().to_dict()
        bb = next(s for s in d["setups"] if s["name"] == "hfss_bb")
        assert len(bb["mesh_operations"]) == 1
        assert bb["mesh_operations"][0]["name"] == "mesh1"

    def test_hfss_frequency_sweep(self):
        d = self._full_builder().to_dict()
        bb = next(s for s in d["setups"] if s["name"] == "hfss_bb")
        # hfss_bb now has two sweeps: "sweep1" (inline) and "sweep1b" (chained)
        assert len(bb["freq_sweep"]) == 2
        # inline sweep has the single linear_count range
        inline_sw = next(sw for sw in bb["freq_sweep"] if sw["name"] == "sweep1")
        assert inline_sw["frequencies"][0]["distribution"] == "linear_count"
        assert inline_sw["frequencies"][0]["increment"] == 100

    def test_hfss_multi_freq(self):
        d = self._full_builder().to_dict()
        mf = next(s for s in d["setups"] if s["name"] == "hfss_multi")
        assert mf["adapt_type"] == "multi_frequencies"
        assert len(mf["multi_frequency_adaptive_solution"]["adapt_frequencies"]) == 2

    def test_siwave_dc_thermal_export(self):
        d = self._full_builder().to_dict()
        dc = next(s for s in d["setups"] if s["type"] == "siwave_dc")
        assert dc["dc_ir_settings"]["export_dc_thermal_data"] is True

    # -- boundaries --
    def test_boundaries(self):
        d = self._full_builder().to_dict()
        assert d["boundaries"]["use_open_region"] is True
        assert d["boundaries"]["open_region_type"] == "radiation"
        assert d["boundaries"]["truncate_air_box_at_ground"] is True

    # -- operations --
    def test_operations_cutout(self):
        d = self._full_builder().to_dict()
        assert "cutout" in d["operations"]
        assert "DDR4_DQ0" in d["operations"]["cutout"]["signal_nets"]

    def test_operations_auto_hfss(self):
        d = self._full_builder().to_dict()
        assert d["operations"]["generate_auto_hfss_regions"] is True

    # -- s-parameters --
    def test_s_parameters(self):
        d = self._full_builder().to_dict()
        assert len(d["s_parameters"]) == 2
        names = [m["name"] for m in d["s_parameters"]]
        assert "cap_model" in names

    # -- spice models --
    def test_spice_models(self):
        d = self._full_builder().to_dict()
        assert len(d["spice_models"]) == 1
        assert d["spice_models"][0]["sub_circuit_name"] == "IC_TOP"

    # -- variables --
    def test_variables(self):
        d = self._full_builder().to_dict()
        values = {v["name"]: v["value"] for v in d["variables"]}
        assert values["trace_width"] == "0.15mm"
        assert values["via_diameter"] == 0.2

    # -- modeler --
    def test_modeler_traces(self):
        d = self._full_builder().to_dict()
        assert d["modeler"]["traces"][0]["name"] == "trace1"

    def test_modeler_planes(self):
        d = self._full_builder().to_dict()
        types = {p["type"] for p in d["modeler"]["planes"]}
        assert types == {"rectangle", "circle", "polygon"}

    def test_modeler_primitives_to_delete(self):
        d = self._full_builder().to_dict()
        prim = d["modeler"]["primitives_to_delete"]
        assert "old_layer" in prim["layer_name"]
        assert "old_net" in prim["net_name"]

    def test_inline_sweep_round_trip(self, tmp_path):
        """Inline add_frequency_sweep survives JSON round-trip correctly."""
        cfg = EdbConfigBuilder()
        hfss = cfg.setups.add_hfss_setup(name="h1")
        hfss.set_broadband_adaptive("1GHz", "20GHz")
        hfss.add_frequency_sweep(
            "sweep1",
            start="1GHz",
            stop="20GHz",
            step_or_count=200,
            distribution="linear_count",
            enforce_passivity=False,
            use_q3d_for_dc=True,
        )
        path = tmp_path / "inline_sweep.json"
        cfg.to_json(str(path))
        cfg2 = EdbConfigBuilder.from_json(str(path))
        d = cfg2.to_dict()
        freqs = d["setups"][0]["freq_sweep"][0]["frequencies"]
        assert freqs[0]["distribution"] == "linear_count"
        assert freqs[0]["increment"] == 200

    def test_inline_sweep_siwave_round_trip(self, tmp_path):
        """SIwave AC inline sweep round-trip."""
        cfg = EdbConfigBuilder()
        siw = cfg.setups.add_siwave_ac_setup(name="siw1", si_slider_position=2)
        siw.add_frequency_sweep(
            "sw1",
            start="1kHz",
            stop="1GHz",
            step_or_count=50,
            distribution="log_count",
        )
        path = tmp_path / "siw_sweep.json"
        cfg.to_json(str(path))
        cfg2 = EdbConfigBuilder.from_json(str(path))
        freqs = cfg2.to_dict()["setups"][0]["freq_sweep"][0]["frequencies"]
        assert freqs[0]["distribution"] == "log_count"
        assert freqs[0]["increment"] == 50


class TestEdbConfigBuilderJson:
    def _simple_builder(self) -> EdbConfigBuilder:
        cfg = EdbConfigBuilder()
        cfg.general.anti_pads_always_on = True
        cfg.nets.add_signal_nets(["SIG"])
        return cfg

    def test_to_json_creates_file(self, tmp_path):
        cfg = self._simple_builder()
        output = tmp_path / "config.json"
        result = cfg.to_json(str(output))
        assert output.exists()
        assert output.stat().st_size > 0

    def test_to_json_valid_json(self, tmp_path):
        cfg = self._simple_builder()
        output = tmp_path / "config.json"
        cfg.to_json(str(output))
        with open(output) as f:
            data = json.load(f)
        assert "general" in data
        assert "nets" in data

    def test_from_json_round_trip(self, tmp_path):
        cfg = self._simple_builder()
        path = tmp_path / "config.json"
        cfg.to_json(str(path))
        cfg2 = EdbConfigBuilder.from_json(str(path))
        assert cfg.to_dict() == cfg2.to_dict()

    def test_to_json_creates_parent_dirs(self, tmp_path):
        cfg = self._simple_builder()
        output = tmp_path / "nested" / "dir" / "config.json"
        cfg.to_json(str(output))
        assert output.exists()


class TestEdbConfigBuilderEmpty:
    def test_empty_builder_produces_empty_dict(self):
        cfg = EdbConfigBuilder()
        d = cfg.to_dict()
        # always-present sections with empty/default values
        assert set(d.keys()) <= {"stackup", "nets", "boundaries", "operations"}

    def test_partial_builder_only_has_populated_keys(self):
        cfg = EdbConfigBuilder()
        cfg.nets.add_signal_nets(["SIG1"])
        d = cfg.to_dict()
        assert "nets" in d
        assert "SIG1" in d["nets"]["signal_nets"]


class TestTerminalInfo:
    def test_pin_with_refdes(self):
        t = TerminalInfo.pin("A1", reference_designator="U1")
        assert t == {"pin": "A1", "reference_designator": "U1"}

    def test_net_with_refdes(self):
        t = TerminalInfo.net("VDD", reference_designator="U1")
        assert t["reference_designator"] == "U1"


class TestTerminalsConfig:
    def test_mixed_terminals(self):
        tc = TerminalsConfig()
        tc.add_padstack_instance_terminal("t1", "via_1", 50, "port", None)
        tc.add_pin_group_terminal("t2", "pg1", 50, "port")
        tc.add_bundle_terminal("bundle1", ["t1", "t2"])
        types = [t["terminal_type"] for t in tc.model_dump(exclude_none=True)["terminals"]]
        assert types == ["padstack_instance", "pin_group", "bundle"]

    def test_terminals_in_builder(self):
        cfg = EdbConfigBuilder()
        cfg.terminals.add_padstack_instance_terminal("pt1", "v1", 50, "port", None)
        d = cfg.to_dict()
        assert "terminals" in d
        assert d["terminals"][0]["name"] == "pt1"

    def test_terminals_round_trip(self, tmp_path):
        cfg = EdbConfigBuilder()
        cfg.terminals.add_padstack_instance_terminal("pt1", "v1", 50, "port", "Wave")
        path = tmp_path / "cfg.json"
        cfg.to_json(str(path))
        cfg2 = EdbConfigBuilder.from_json(str(path))
        assert cfg.to_dict() == cfg2.to_dict()


class TestHeatSinkConfig:
    def test_partial(self):
        hs = HeatSinkConfig(fin_height="3mm", fin_spacing="1mm")
        d = hs.model_dump(exclude_none=True)
        assert d["fin_height"] == "3mm"
        assert d["fin_spacing"] == "1mm"
        assert "fin_base_height" not in d

    def test_full(self):
        hs = HeatSinkConfig(
            fin_base_height="0.5mm",
            fin_height="3mm",
            fin_orientation="x_oriented",
            fin_spacing="1mm",
            fin_thickness="0.2mm",
        )
        d = hs.model_dump(exclude_none=True)
        assert len(d) == 5


class TestPackageDefinitionsConfig:
    def test_in_builder(self):
        cfg = EdbConfigBuilder()
        pkg = cfg.package_definitions.add("PKG1", "BGA_256", apply_to_all=True)
        pkg.maximum_power = "5W"
        pkg.set_heatsink(fin_height="3mm")
        d = cfg.to_dict()
        assert "package_definitions" in d
        assert d["package_definitions"][0]["heatsink"]["fin_height"] == "3mm"


class TestBuilderTomlRoundTrip:
    def test_to_toml_creates_file(self, tmp_path):
        cfg = EdbConfigBuilder()
        cfg.general.suppress_pads = True
        cfg.nets.add_signal_nets(["CLK"])
        path = tmp_path / "config.toml"
        result = cfg.to_toml(str(path))
        assert path.exists()
        assert path.stat().st_size > 0

    def test_to_toml_valid_toml(self, tmp_path):
        cfg = EdbConfigBuilder()
        cfg.general.anti_pads_always_on = False
        cfg.nets.add_power_ground_nets(["GND"])
        path = tmp_path / "config.toml"
        cfg.to_toml(str(path))
        with open(path) as f:
            data = toml.load(f)
        assert "general" in data
        assert "nets" in data

    def test_from_toml_round_trip(self, tmp_path):
        cfg = EdbConfigBuilder()
        cfg.general.suppress_pads = True
        cfg.nets.add_signal_nets(["CLK"])
        cfg.stackup.add_material("copper", conductivity=5.8e7)
        path = tmp_path / "config.toml"
        cfg.to_toml(str(path))
        cfg2 = EdbConfigBuilder.from_toml(str(path))
        assert cfg.to_dict() == cfg2.to_dict()

    def test_to_toml_creates_parent_dirs(self, tmp_path):
        cfg = EdbConfigBuilder()
        cfg.nets.add_signal_nets(["SIG"])
        path = tmp_path / "sub" / "dir" / "config.toml"
        cfg.to_toml(str(path))
        assert path.exists()

    def test_to_toml_returns_path(self, tmp_path):
        cfg = EdbConfigBuilder()
        cfg.nets.add_signal_nets(["SIG"])
        path = tmp_path / "config.toml"
        result = cfg.to_toml(str(path))
        from pathlib import Path

        assert isinstance(result, Path)


class TestCfgBase:
    """Unit tests for CfgBase helper methods (cfg_common.py)."""

    def _make_instance(self, **attrs):
        obj = CfgBase()
        for k, v in attrs.items():
            setattr(obj, k, v)
        return obj

    def test_get_attributes_basic(self):
        obj = self._make_instance(foo="bar", baz=42)
        d = obj.get_attributes()
        assert d["foo"] == "bar"
        assert d["baz"] == 42

    def test_get_attributes_excludes_none_and_empty(self):
        obj = self._make_instance(a=None, b=[], c={}, d="keep")
        d = obj.get_attributes()
        assert "a" not in d
        assert "b" not in d
        assert "c" not in d
        assert "d" in d

    def test_get_attributes_excludes_protected(self):
        obj = self._make_instance(pedb="session", foo="bar")
        d = obj.get_attributes()
        assert "pedb" not in d
        assert "foo" in d

    def test_get_attributes_excludes_private(self):
        obj = self._make_instance(foo="public")
        obj._private = "hidden"
        d = obj.get_attributes()
        assert "_private" not in d
        assert "foo" in d

    def test_get_attributes_extra_exclude_string(self):
        obj = self._make_instance(foo="bar", skip_me="x")
        d = obj.get_attributes(exclude="skip_me")
        assert "skip_me" not in d
        assert "foo" in d

    def test_get_attributes_extra_exclude_list(self):
        obj = self._make_instance(foo="bar", a="x", b="y")
        d = obj.get_attributes(exclude=["a", "b"])
        assert "a" not in d
        assert "b" not in d
        assert "foo" in d

    def test_set_attributes_applies_values(self):
        class Target:
            foo = None
            baz = None

        obj = self._make_instance(foo="bar", baz=42)
        t = Target()
        obj.set_attributes(t)
        assert t.foo == "bar"
        assert t.baz == 42

    def test_set_attributes_raises_on_unknown_attr(self):
        class Target:
            pass

        obj = self._make_instance(unknown_attr="x")
        t = Target()
        with pytest.raises(AttributeError, match="unknown_attr"):
            obj.set_attributes(t)


# ---------------------------------------------------------------------------
# Configuration.get_setups – gRPC path uses settings.general.adaptive_solution_type
# ---------------------------------------------------------------------------


@pytest.mark.grpc
class TestGetSetupsGrpcAdaptType:
    """Unit tests for Configuration.get_setups() in gRPC mode.

    These tests verify that get_setups() reads the adaptive solution type from
    ``setup.settings.general.adaptive_solution_type`` (the current non-deprecated
    property) and NOT from the deprecated ``setup.adaptive_settings.adapt_type``.

    Strategy: configure the mock so that accessing ``adaptive_settings.adapt_type``
    raises an AttributeError.  If the code still completes successfully, the fix
    is confirmed.
    """

    def _make_sweep_stub(self, name="sw1"):
        sw = MagicMock()
        sw.type = "interpolating"
        sw.frequency_string = ["LIN 0Hz 10GHz 10MHz"]
        sw.compute_dc_point = False
        sw.enforce_causality = False
        sw.enforce_passivity = True
        sw.adv_dc_extrapolation = False
        sw.use_hfss_solver_regions = False
        # Pydantic validates these as Optional[str]; must be None or a string
        sw.hfss_solver_region_setup_name = None
        sw.hfss_solver_region_sweep_name = None
        return {name: sw}

    def _make_hfss_setup_stub(self, adapt_type="single"):
        """Build a minimal mock HFSS setup for the gRPC path."""
        setup = MagicMock()
        setup.type = "hfss"
        setup.name = "HFSS_Setup_1"

        # The non-deprecated path that get_setups() should use
        setup.settings.general.adaptive_solution_type = adapt_type

        # Make the deprecated path raise so the test fails if it is accessed
        type(setup).adaptive_settings = property(
            lambda self: (_ for _ in ()).throw(AttributeError("adaptive_settings must not be accessed in gRPC mode"))
        )

        # Mesh operations and sweeps
        setup.mesh_operations = []
        setup.sweeps = self._make_sweep_stub()
        return setup

    def _make_configuration(self, setups_dict):
        """Build a Configuration instance with a mocked pedb."""
        from unittest.mock import MagicMock

        from pyedb.configuration.configuration import Configuration

        pedb = MagicMock()
        pedb.setups = setups_dict
        pedb.logger = MagicMock()
        cfg = Configuration.__new__(Configuration)
        cfg._pedb = pedb

        from pyedb.configuration.cfg_data import CfgData

        cfg.cfg_data = CfgData()
        return cfg

    def test_get_setups_single_adaptive_uses_settings_general(self):
        """Single-frequency adapt type is read via settings.general, not adaptive_settings."""
        from unittest.mock import patch

        from pyedb.configuration.configuration import Configuration

        setup = self._make_hfss_setup_stub(adapt_type="single")
        sfas = MagicMock()
        sfas.adaptive_frequency = "5GHz"
        sfas.max_passes = 10
        sfas.max_delta = "0.02"
        setup.settings.general.single_frequency_adaptive_solution = sfas

        cfg = self._make_configuration({"HFSS_Setup_1": setup})

        with patch("pyedb.configuration.configuration.settings") as mock_settings:
            mock_settings.is_grpc = True
            cfg.get_setups()  # must not raise AttributeError

        assert len(cfg.cfg_data.setups.setups) == 1
        saved = cfg.cfg_data.setups.setups[0]
        assert saved.adapt_type == "single"

    def test_get_setups_broadband_adaptive_uses_settings_general(self):
        """Broadband adapt type is read via settings.general, not adaptive_settings."""
        from unittest.mock import patch

        setup = self._make_hfss_setup_stub(adapt_type="broadband")
        bb = MagicMock()
        bb.low_frequency = "1GHz"
        bb.high_frequency = "20GHz"
        bb.max_delta = "0.02"
        bb.max_passes = 20
        setup.settings.general.broadband_adaptive_solution = bb

        cfg = self._make_configuration({"HFSS_Setup_1": setup})

        with patch("pyedb.configuration.configuration.settings") as mock_settings:
            mock_settings.is_grpc = True
            cfg.get_setups()

        saved = cfg.cfg_data.setups.setups[0]
        assert saved.adapt_type == "broadband"

    def test_get_setups_siwave_ac_not_affected(self):
        """SIwave AC setups follow a separate code path and must still be exported."""
        from unittest.mock import patch

        setup = MagicMock()
        setup.type = "siwave"
        setup.name = "SIWave_AC"
        setup.settings.general.use_si_settings = True
        setup.settings.general.si_slider_position = 1
        setup.settings.general.pi_slider_position = 1
        setup.sweeps = {}

        cfg = self._make_configuration({"SIWave_AC": setup})

        with patch("pyedb.configuration.configuration.settings") as mock_settings:
            mock_settings.is_grpc = True
            cfg.get_setups()

        assert len(cfg.cfg_data.setups.setups) == 1
        assert cfg.cfg_data.setups.setups[0].name == "SIWave_AC"
