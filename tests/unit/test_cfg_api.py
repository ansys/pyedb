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

import copy
import json
import tempfile
from unittest.mock import MagicMock

import pytest

from pyedb.configuration.cfg_api import (
    BoundariesConfig,
    BundleTerminal,
    ComponentConfig,
    ComponentsConfig,
    CutoutConfig,
    DiffWavePortConfig,
    EdbConfigBuilder,
    EdgePortConfig,
    EdgeTerminal,
    FrequencySweepConfig,
    GeneralConfig,
    HeatSinkConfig,
    HfssSetupConfig,
    LayerConfig,
    MaterialConfig,
    ModelerConfig,
    NetsConfig,
    OperationsConfig,
    PackageDefinitionConfig,
    PackageDefinitionsConfig,
    PadstackDefinitionConfig,
    PadstackInstanceConfig,
    PadstackInstanceTerminal,
    PadstacksConfig,
    PinGroupConfig,
    PinGroupsConfig,
    PinGroupTerminal,
    PinPairModel,
    PointTerminal,
    PortConfig,
    PortsConfig,
    ProbeConfig,
    ProbesConfig,
    SetupsConfig,
    SIwaveACSetupConfig,
    SIwaveDCSetupConfig,
    SourceConfig,
    SourcesConfig,
    SParameterModelConfig,
    SParameterModelsConfig,
    SpiceModelConfig,
    SpiceModelsConfig,
    StackupConfig,
    TerminalInfo,
    TerminalsConfig,
    VariablesConfig,
)

pytestmark = [pytest.mark.unit, pytest.mark.no_licence, pytest.mark.legacy]


# ---------------------------------------------------------------------------
# GeneralConfig
# ---------------------------------------------------------------------------


class TestGeneralConfig:
    def test_defaults(self):
        g = GeneralConfig()
        assert g.spice_model_library == ""
        assert g.s_parameter_library == ""
        assert g.anti_pads_always_on is None
        assert g.suppress_pads is None

    def test_to_dict_empty(self):
        assert GeneralConfig().to_dict() == {}

    def test_to_dict_partial(self):
        g = GeneralConfig()
        g.spice_model_library = "/spice"
        d = g.to_dict()
        assert d == {"spice_model_library": "/spice"}

    def test_to_dict_full(self):
        g = GeneralConfig()
        g.spice_model_library = "/spice"
        g.s_parameter_library = "/snp"
        g.anti_pads_always_on = True
        g.suppress_pads = False
        d = g.to_dict()
        assert d["spice_model_library"] == "/spice"
        assert d["s_parameter_library"] == "/snp"
        assert d["anti_pads_always_on"] is True
        assert d["suppress_pads"] is False

    def test_anti_pads_false_preserved(self):
        g = GeneralConfig()
        g.anti_pads_always_on = False
        d = g.to_dict()
        # False (bool) must be kept – not omitted
        assert "anti_pads_always_on" in d
        assert d["anti_pads_always_on"] is False


# ---------------------------------------------------------------------------
# MaterialConfig
# ---------------------------------------------------------------------------


class TestMaterialConfig:
    def test_name_only(self):
        m = MaterialConfig("copper")
        d = m.to_dict()
        assert d == {"name": "copper"}

    def test_conductivity(self):
        m = MaterialConfig("copper", conductivity=5.8e7)
        d = m.to_dict()
        assert d["conductivity"] == 5.8e7

    def test_dielectric_props(self):
        m = MaterialConfig("fr4", permittivity=4.4, dielectric_loss_tangent=0.02)
        d = m.to_dict()
        assert d["permittivity"] == 4.4
        assert d["dielectric_loss_tangent"] == 0.02

    def test_all_known_properties(self):
        props = {
            "conductivity": 1e6,
            "dielectric_loss_tangent": 0.01,
            "magnetic_loss_tangent": 0.001,
            "mass_density": 8960,
            "permittivity": 4.4,
            "permeability": 1.0,
            "poisson_ratio": 0.34,
            "specific_heat": 385,
            "thermal_conductivity": 401,
            "youngs_modulus": 110e9,
            "thermal_expansion_coefficient": 17e-6,
            "dc_conductivity": 1e5,
            "dc_permittivity": 4.0,
            "dielectric_model_frequency": 1e9,
            "loss_tangent_at_frequency": 0.01,
            "permittivity_at_frequency": 4.3,
        }
        m = MaterialConfig("mat", **props)
        d = m.to_dict()
        for key, val in props.items():
            assert d[key] == val


# ---------------------------------------------------------------------------
# LayerConfig
# ---------------------------------------------------------------------------


class TestLayerConfig:
    def test_name_only(self):
        layer = LayerConfig("top")
        d = layer.to_dict()
        assert d == {"name": "top"}

    def test_signal_layer(self):
        layer = LayerConfig("top", type="signal", material="copper", thickness="35um")
        d = layer.to_dict()
        assert d["type"] == "signal"
        assert d["material"] == "copper"
        assert d["thickness"] == "35um"

    def test_set_huray_roughness(self):
        layer = LayerConfig("top")
        layer.set_huray_roughness("0.1um", "2.9")
        d = layer.to_dict()
        assert d["roughness"]["enabled"] is True
        assert d["roughness"]["top"]["model"] == "huray"
        assert d["roughness"]["top"]["nodule_radius"] == "0.1um"
        assert d["roughness"]["top"]["surface_ratio"] == "2.9"

    def test_set_huray_roughness_partial_surfaces(self):
        layer = LayerConfig("top")
        layer.set_huray_roughness("0.1um", "2.9", top=True, bottom=False, side=False)
        d = layer.to_dict()
        assert "top" in d["roughness"]
        assert "bottom" not in d["roughness"]
        assert "side" not in d["roughness"]

    def test_set_groisse_roughness(self):
        layer = LayerConfig("inner1")
        layer.set_groisse_roughness(0.3e-6)
        d = layer.to_dict()
        assert d["roughness"]["top"]["model"] == "groisse"
        assert d["roughness"]["top"]["roughness"] == 0.3e-6

    def test_set_etching(self):
        layer = LayerConfig("top")
        layer.set_etching(factor=0.4, etch_power_ground_nets=True)
        d = layer.to_dict()
        assert d["etching"]["factor"] == 0.4
        assert d["etching"]["etch_power_ground_nets"] is True
        assert d["etching"]["enabled"] is True


# ---------------------------------------------------------------------------
# StackupConfig
# ---------------------------------------------------------------------------


class TestStackupConfig:
    def test_empty(self):
        s = StackupConfig()
        assert s.to_dict() == {}

    def test_add_material(self):
        s = StackupConfig()
        mat = s.add_material("copper", conductivity=5.8e7)
        assert isinstance(mat, MaterialConfig)
        d = s.to_dict()
        assert len(d["materials"]) == 1
        assert d["materials"][0]["name"] == "copper"

    def test_add_layer(self):
        s = StackupConfig()
        s.add_layer("top", type="signal", material="copper", thickness="35um")
        d = s.to_dict()
        assert d["layers"][0]["name"] == "top"

    def test_add_signal_layer_convenience(self):
        s = StackupConfig()
        lyr = s.add_signal_layer("sig_top")
        d = s.to_dict()
        assert d["layers"][0]["type"] == "signal"
        assert d["layers"][0]["fill_material"] == "FR4_epoxy"

    def test_add_dielectric_layer_convenience(self):
        s = StackupConfig()
        lyr = s.add_dielectric_layer("diel_1")
        d = s.to_dict()
        assert d["layers"][0]["type"] == "dielectric"
        assert d["layers"][0]["material"] == "FR4_epoxy"

    def test_layer_order_preserved(self):
        s = StackupConfig()
        s.add_signal_layer("top")
        s.add_dielectric_layer("diel")
        s.add_signal_layer("bot")
        names = [l["name"] for l in s.to_dict()["layers"]]
        assert names == ["top", "diel", "bot"]

    def test_multiple_materials(self):
        s = StackupConfig()
        s.add_material("copper", conductivity=5.8e7)
        s.add_material("fr4", permittivity=4.4)
        d = s.to_dict()
        assert len(d["materials"]) == 2


# ---------------------------------------------------------------------------
# NetsConfig
# ---------------------------------------------------------------------------


class TestNetsConfig:
    def test_empty(self):
        n = NetsConfig()
        assert n.to_dict() == {}

    def test_signal_nets(self):
        n = NetsConfig()
        n.add_signal_nets(["SIG1", "SIG2"])
        d = n.to_dict()
        assert d["signal_nets"] == ["SIG1", "SIG2"]
        assert "power_ground_nets" not in d

    def test_power_ground_nets(self):
        n = NetsConfig()
        n.add_power_ground_nets(["VDD", "GND"])
        d = n.to_dict()
        assert d["power_ground_nets"] == ["VDD", "GND"]

    def test_accumulates(self):
        n = NetsConfig()
        n.add_signal_nets(["A"])
        n.add_signal_nets(["B", "C"])
        assert n.to_dict()["signal_nets"] == ["A", "B", "C"]


# ---------------------------------------------------------------------------
# PinPairModel
# ---------------------------------------------------------------------------


class TestPinPairModel:
    def test_basic(self):
        pp = PinPairModel("1", "2", resistance="100ohm", resistance_enabled=True)
        d = pp.to_dict()
        assert d["first_pin"] == "1"
        assert d["second_pin"] == "2"
        assert d["resistance"] == "100ohm"
        assert d["resistance_enabled"] is True

    def test_defaults(self):
        pp = PinPairModel("A", "B")
        d = pp.to_dict()
        assert d["is_parallel"] is False
        assert d["inductance_enabled"] is False


# ---------------------------------------------------------------------------
# ComponentConfig
# ---------------------------------------------------------------------------


class TestComponentConfig:
    def test_minimal(self):
        c = ComponentConfig("U1")
        d = c.to_dict()
        assert d == {"reference_designator": "U1"}

    def test_with_type_and_enabled(self):
        c = ComponentConfig("R1", part_type="resistor", enabled=False)
        d = c.to_dict()
        assert d["part_type"] == "resistor"
        assert d["enabled"] is False

    def test_pin_pair_rlc(self):
        c = ComponentConfig("R1")
        c.add_pin_pair_rlc("1", "2", resistance="1kohm", resistance_enabled=True)
        d = c.to_dict()
        assert len(d["pin_pair_model"]) == 1
        assert d["pin_pair_model"][0]["resistance"] == "1kohm"

    def test_multiple_pin_pair_rlc(self):
        c = ComponentConfig("C1")
        c.add_pin_pair_rlc("1", "2", capacitance="100nF", capacitance_enabled=True)
        c.add_pin_pair_rlc("2", "3", resistance="10ohm", resistance_enabled=True)
        d = c.to_dict()
        assert len(d["pin_pair_model"]) == 2

    def test_s_parameter_model(self):
        c = ComponentConfig("U1")
        c.set_s_parameter_model("model1", "/path/to/model.s2p", "GND")
        d = c.to_dict()
        assert d["s_parameter_model"]["model_name"] == "model1"
        assert d["s_parameter_model"]["reference_net"] == "GND"

    def test_spice_model(self):
        c = ComponentConfig("U2")
        c.set_spice_model("ic_spice", "/path/ic.sp", "IC_SUB")
        d = c.to_dict()
        assert d["spice_model"]["model_name"] == "ic_spice"
        assert d["spice_model"]["sub_circuit"] == "IC_SUB"

    def test_netlist_model(self):
        c = ComponentConfig("Q1")
        c.set_netlist_model(".subckt Q1 ...")
        d = c.to_dict()
        assert d["netlist_model"]["netlist"] == ".subckt Q1 ..."

    def test_ic_die_properties_no_die(self):
        c = ComponentConfig("U1")
        c.set_ic_die_properties("no_die")
        d = c.to_dict()
        assert d["ic_die_properties"]["type"] == "no_die"

    def test_ic_die_properties_flip_chip(self):
        c = ComponentConfig("U1")
        c.set_ic_die_properties("flip_chip", orientation="chip_down")
        d = c.to_dict()
        assert d["ic_die_properties"]["type"] == "flip_chip"
        assert d["ic_die_properties"]["orientation"] == "chip_down"

    def test_ic_die_properties_wire_bond(self):
        c = ComponentConfig("U1")
        c.set_ic_die_properties("wire_bond", orientation="chip_up", height="200um")
        d = c.to_dict()
        assert d["ic_die_properties"]["height"] == "200um"

    def test_solder_ball_cylinder(self):
        c = ComponentConfig("U1")
        c.set_solder_ball_properties("cylinder", "150um", "100um")
        d = c.to_dict()
        assert d["solder_ball_properties"]["shape"] == "cylinder"
        assert d["solder_ball_properties"]["diameter"] == "150um"

    def test_solder_ball_spheroid(self):
        c = ComponentConfig("U1")
        c.set_solder_ball_properties("spheroid", "150um", "100um", mid_diameter="130um")
        d = c.to_dict()
        assert d["solder_ball_properties"]["mid_diameter"] == "130um"

    def test_port_properties(self):
        c = ComponentConfig("U1")
        c.set_port_properties(reference_height="50um", reference_size_auto=False)
        d = c.to_dict()
        assert d["port_properties"]["reference_height"] == "50um"
        assert d["port_properties"]["reference_size_auto"] is False


# ---------------------------------------------------------------------------
# ComponentsConfig
# ---------------------------------------------------------------------------


class TestComponentsConfig:
    def test_add_returns_component_config(self):
        cc = ComponentsConfig()
        comp = cc.add("R1", part_type="resistor")
        assert isinstance(comp, ComponentConfig)

    def test_to_list(self):
        cc = ComponentsConfig()
        cc.add("R1", part_type="resistor", enabled=True)
        cc.add("C1", part_type="capacitor")
        lst = cc.to_list()
        assert len(lst) == 2
        assert lst[0]["reference_designator"] == "R1"

    def test_empty(self):
        assert ComponentsConfig().to_list() == []


# ---------------------------------------------------------------------------
# PadstackDefinitionConfig
# ---------------------------------------------------------------------------


class TestPadstackDefinitionConfig:
    def test_minimal(self):
        p = PadstackDefinitionConfig("via_0.2")
        d = p.to_dict()
        assert d == {"name": "via_0.2"}

    def test_with_properties(self):
        p = PadstackDefinitionConfig("via", hole_plating_thickness="25um", material="copper")
        d = p.to_dict()
        assert d["hole_plating_thickness"] == "25um"
        assert d["material"] == "copper"


# ---------------------------------------------------------------------------
# PadstackInstanceConfig
# ---------------------------------------------------------------------------


class TestPadstackInstanceConfig:
    def test_minimal(self):
        inst = PadstackInstanceConfig(name="via_1", net_name="GND")
        d = inst.to_dict()
        assert d["name"] == "via_1"
        assert d["net_name"] == "GND"

    def test_layer_range(self):
        inst = PadstackInstanceConfig(layer_range=["top", "bot"])
        d = inst.to_dict()
        assert d["layer_range"] == ["top", "bot"]

    def test_backdrill(self):
        inst = PadstackInstanceConfig(name="via_bd")
        inst.set_backdrill("L4", "0.3mm", drill_from_bottom=True)
        d = inst.to_dict()
        assert d["backdrill_parameters"]["from_bottom"]["drill_to_layer"] == "L4"

    def test_backdrill_with_stub(self):
        inst = PadstackInstanceConfig(name="via_bd2")
        inst.set_backdrill("L4", "0.3mm", stub_length="0.05mm", drill_from_bottom=False)
        d = inst.to_dict()
        assert "from_top" in d["backdrill_parameters"]
        assert d["backdrill_parameters"]["from_top"]["stub_length"] == "0.05mm"


# ---------------------------------------------------------------------------
# PadstacksConfig
# ---------------------------------------------------------------------------


class TestPadstacksConfig:
    def test_empty(self):
        assert PadstacksConfig().to_dict() == {}

    def test_add_definition(self):
        ps = PadstacksConfig()
        pdef = ps.add_definition("via", material="copper")
        assert isinstance(pdef, PadstackDefinitionConfig)
        d = ps.to_dict()
        assert d["definitions"][0]["name"] == "via"

    def test_add_instance(self):
        ps = PadstacksConfig()
        inst = ps.add_instance(name="v1", net_name="SIG1")
        assert isinstance(inst, PadstackInstanceConfig)
        d = ps.to_dict()
        assert d["instances"][0]["name"] == "v1"


# ---------------------------------------------------------------------------
# PinGroupConfig / PinGroupsConfig
# ---------------------------------------------------------------------------


class TestPinGroupConfig:
    def test_with_pins(self):
        pg = PinGroupConfig("pg1", "U1", pins=["A1", "A2"])
        d = pg.to_dict()
        assert d["pins"] == ["A1", "A2"]
        assert "net" not in d

    def test_with_net(self):
        pg = PinGroupConfig("pg2", "U1", net="VDD")
        d = pg.to_dict()
        assert d["net"] == "VDD"
        assert "pins" not in d


class TestPinGroupsConfig:
    def test_empty(self):
        assert PinGroupsConfig().to_list() == []

    def test_add(self):
        pgs = PinGroupsConfig()
        pg = pgs.add("pg1", "U1", net="VDD")
        assert isinstance(pg, PinGroupConfig)
        lst = pgs.to_list()
        assert len(lst) == 1
        assert lst[0]["name"] == "pg1"

    def test_multiple(self):
        pgs = PinGroupsConfig()
        pgs.add("pg1", "U1", pins=["A1"])
        pgs.add("pg2", "U2", net="GND")
        assert len(pgs.to_list()) == 2


# ---------------------------------------------------------------------------
# PortConfig / EdgePortConfig / DiffWavePortConfig
# ---------------------------------------------------------------------------


class TestPortConfig:
    def test_circuit_port(self):
        p = PortConfig("p1", "circuit", {"pin_group": "pg1"}, {"net": "GND"})
        d = p.to_dict()
        assert d["type"] == "circuit"
        assert d["positive_terminal"] == {"pin_group": "pg1"}
        assert d["negative_terminal"] == {"net": "GND"}

    def test_coax_no_neg_terminal(self):
        p = PortConfig("coax1", "coax", {"padstack": "via_1"})
        d = p.to_dict()
        assert "negative_terminal" not in d

    def test_impedance(self):
        p = PortConfig("p1", "circuit", {"net": "SIG"}, impedance=50)
        assert p.to_dict()["impedance"] == 50

    def test_distributed(self):
        p = PortConfig("p1", "circuit", {"net": "SIG"}, distributed=True)
        assert p.to_dict()["distributed"] is True


class TestEdgePortConfig:
    def test_wave_port(self):
        ep = EdgePortConfig("wp1", "wave_port", "trace1", [0.001, 0.002])
        d = ep.to_dict()
        assert d["type"] == "wave_port"
        assert d["primitive_name"] == "trace1"
        assert d["point_on_edge"] == [0.001, 0.002]
        assert d["horizontal_extent_factor"] == 5

    def test_gap_port(self):
        ep = EdgePortConfig("gp1", "gap_port", "trace2", [0.003, 0.004], horizontal_extent_factor=3)
        d = ep.to_dict()
        assert d["horizontal_extent_factor"] == 3


class TestDiffWavePortConfig:
    def test_diff_wave_port(self):
        dp = DiffWavePortConfig(
            "diff1",
            {"primitive_name": "trace_p", "point_on_edge": [0, 0]},
            {"primitive_name": "trace_n", "point_on_edge": [0, 1e-4]},
        )
        d = dp.to_dict()
        assert d["type"] == "diff_wave_port"
        assert d["positive_terminal"]["primitive_name"] == "trace_p"


# ---------------------------------------------------------------------------
# PortsConfig
# ---------------------------------------------------------------------------


class TestPortsConfig:
    def test_empty(self):
        assert PortsConfig().to_list() == []

    def test_add_circuit_port(self):
        pc = PortsConfig()
        p = pc.add_circuit_port("p1", {"net": "SIG"}, {"net": "GND"})
        assert isinstance(p, PortConfig)
        lst = pc.to_list()
        assert lst[0]["type"] == "circuit"

    def test_add_coax_port(self):
        pc = PortsConfig()
        pc.add_coax_port("coax1", {"padstack": "v1"})
        assert pc.to_list()[0]["type"] == "coax"

    def test_add_wave_port(self):
        pc = PortsConfig()
        pc.add_wave_port("wp1", "prim1", [0.001, 0.002])
        assert pc.to_list()[0]["type"] == "wave_port"

    def test_add_gap_port(self):
        pc = PortsConfig()
        pc.add_gap_port("gp1", "prim2", [0.003, 0.004])
        assert pc.to_list()[0]["type"] == "gap_port"

    def test_add_diff_wave_port(self):
        pc = PortsConfig()
        pc.add_diff_wave_port(
            "diff1",
            {"primitive_name": "tp", "point_on_edge": [0, 0]},
            {"primitive_name": "tn", "point_on_edge": [0, 1e-4]},
        )
        assert pc.to_list()[0]["type"] == "diff_wave_port"

    def test_multiple_ports(self):
        pc = PortsConfig()
        pc.add_circuit_port("p1", {"net": "A"}, {"net": "GND"})
        pc.add_coax_port("p2", {"padstack": "v1"})
        pc.add_wave_port("p3", "t1", [0, 0])
        assert len(pc.to_list()) == 3


# ---------------------------------------------------------------------------
# SourceConfig / SourcesConfig
# ---------------------------------------------------------------------------


class TestSourceConfig:
    def test_current_source(self):
        s = SourceConfig("isrc1", "current", {"pin": "A1"}, {"net": "GND"}, magnitude=0.001)
        d = s.to_dict()
        assert d["type"] == "current"
        assert d["magnitude"] == 0.001

    def test_voltage_source(self):
        s = SourceConfig("vsrc1", "voltage", {"net": "VDD"}, {"net": "GND"}, magnitude=1.0)
        d = s.to_dict()
        assert d["type"] == "voltage"

    def test_impedance(self):
        s = SourceConfig("s1", "current", {"pin": "A"}, {"pin": "B"}, impedance=50)
        assert s.to_dict()["impedance"] == 50


class TestSourcesConfig:
    def test_empty(self):
        assert SourcesConfig().to_list() == []

    def test_add_current_source(self):
        sc = SourcesConfig()
        s = sc.add_current_source("isrc", {"net": "VDD"}, {"net": "GND"})
        assert isinstance(s, SourceConfig)
        assert sc.to_list()[0]["type"] == "current"

    def test_add_voltage_source(self):
        sc = SourcesConfig()
        sc.add_voltage_source("vsrc", {"net": "VDD"}, {"net": "GND"})
        assert sc.to_list()[0]["type"] == "voltage"

    def test_multiple_sources(self):
        sc = SourcesConfig()
        sc.add_current_source("i1", {"pin": "A"}, {"pin": "B"})
        sc.add_voltage_source("v1", {"pin": "C"}, {"pin": "D"})
        assert len(sc.to_list()) == 2


# ---------------------------------------------------------------------------
# ProbeConfig / ProbesConfig
# ---------------------------------------------------------------------------


class TestProbeConfig:
    def test_probe(self):
        p = ProbeConfig("probe1", {"net": "SIG"}, {"net": "GND"})
        d = p.to_dict()
        assert d["name"] == "probe1"
        assert d["type"] == "probe"
        assert d["positive_terminal"] == {"net": "SIG"}

    def test_reference_designator(self):
        p = ProbeConfig("probe2", {"pin": "A1"}, {"pin": "A2"}, reference_designator="U1")
        assert p.to_dict()["reference_designator"] == "U1"


class TestProbesConfig:
    def test_empty(self):
        assert ProbesConfig().to_list() == []

    def test_add(self):
        pc = ProbesConfig()
        probe = pc.add("pr1", {"net": "SIG"}, {"net": "GND"})
        assert isinstance(probe, ProbeConfig)
        assert pc.to_list()[0]["name"] == "pr1"


# ---------------------------------------------------------------------------
# FrequencySweepConfig
# ---------------------------------------------------------------------------


class TestFrequencySweepConfig:
    def test_defaults(self):
        fs = FrequencySweepConfig("sweep1")
        d = fs.to_dict()
        assert d["name"] == "sweep1"
        assert d["type"] == "interpolation"
        assert d["enforce_passivity"] is True
        assert d["frequencies"] == []

    def test_linear_count(self):
        fs = FrequencySweepConfig("sweep1")
        fs.add_linear_count_frequencies("1GHz", "10GHz", 100)
        freqs = fs.to_dict()["frequencies"]
        assert len(freqs) == 1
        assert freqs[0]["distribution"] == "linear_count"
        assert freqs[0]["increment"] == 100

    def test_log_count(self):
        fs = FrequencySweepConfig("sweep2")
        fs.add_log_count_frequencies("1MHz", "1GHz", 50)
        assert fs.to_dict()["frequencies"][0]["distribution"] == "log_count"

    def test_linear_scale(self):
        fs = FrequencySweepConfig("sweep3")
        fs.add_linear_scale_frequencies("0Hz", "1GHz", "10MHz")
        assert fs.to_dict()["frequencies"][0]["distribution"] == "linear_scale"

    def test_log_scale(self):
        fs = FrequencySweepConfig("sweep4")
        fs.add_log_scale_frequencies("1kHz", "1GHz", "1octave")
        assert fs.to_dict()["frequencies"][0]["distribution"] == "log_scale"

    def test_single_frequency(self):
        fs = FrequencySweepConfig("sweep5")
        fs.add_single_frequency("5GHz")
        freqs = fs.to_dict()["frequencies"]
        assert freqs[0]["distribution"] == "single"
        assert freqs[0]["start"] == "5GHz"

    def test_multiple_frequency_ranges(self):
        fs = FrequencySweepConfig("sweep6")
        fs.add_linear_count_frequencies("1GHz", "5GHz", 50)
        fs.add_log_count_frequencies("5GHz", "20GHz", 50)
        assert len(fs.to_dict()["frequencies"]) == 2

    def test_flags(self):
        fs = FrequencySweepConfig(
            "sweep7",
            enforce_causality=True,
            enforce_passivity=False,
            use_q3d_for_dc=True,
            compute_dc_point=True,
        )
        d = fs.to_dict()
        assert d["enforce_causality"] is True
        assert d["enforce_passivity"] is False
        assert d["use_q3d_for_dc"] is True
        assert d["compute_dc_point"] is True


# ---------------------------------------------------------------------------
# HfssSetupConfig
# ---------------------------------------------------------------------------


class TestHfssSetupConfig:
    def test_defaults(self):
        h = HfssSetupConfig("setup1")
        d = h.to_dict()
        assert d["name"] == "setup1"
        assert d["type"] == "hfss"
        assert d["adapt_type"] == "single"

    def test_set_single_frequency_adaptive(self):
        h = HfssSetupConfig("setup1")
        h.set_single_frequency_adaptive("5GHz", max_passes=15, max_delta=0.01)
        d = h.to_dict()
        assert d["adapt_type"] == "single"
        sfa = d["single_frequency_adaptive_solution"]
        assert sfa["adaptive_frequency"] == "5GHz"
        assert sfa["max_passes"] == 15
        assert sfa["max_delta"] == 0.01

    def test_set_broadband_adaptive(self):
        h = HfssSetupConfig("setup1")
        h.set_broadband_adaptive("1GHz", "20GHz", max_passes=25)
        d = h.to_dict()
        assert d["adapt_type"] == "broadband"
        bba = d["broadband_adaptive_solution"]
        assert bba["low_frequency"] == "1GHz"
        assert bba["high_frequency"] == "20GHz"
        assert bba["max_passes"] == 25

    def test_add_multi_frequency_adaptive(self):
        h = HfssSetupConfig("setup1")
        h.add_multi_frequency_adaptive("1GHz", max_passes=20, max_delta=0.02)
        h.add_multi_frequency_adaptive("10GHz")
        d = h.to_dict()
        assert d["adapt_type"] == "multi_frequencies"
        adapt = d["multi_frequency_adaptive_solution"]["adapt_frequencies"]
        assert len(adapt) == 2
        assert adapt[0]["adaptive_frequency"] == "1GHz"

    def test_set_auto_mesh_operation(self):
        h = HfssSetupConfig("setup1")
        h.set_auto_mesh_operation(enabled=True, trace_ratio_seeding=4)
        d = h.to_dict()
        assert d["auto_mesh_operation"]["enabled"] is True
        assert d["auto_mesh_operation"]["trace_ratio_seeding"] == 4

    def test_add_length_mesh_operation(self):
        h = HfssSetupConfig("setup1")
        h.add_length_mesh_operation("mesh1", {"SIG": ["top"]}, max_length="0.5mm")
        d = h.to_dict()
        assert len(d["mesh_operations"]) == 1
        assert d["mesh_operations"][0]["name"] == "mesh1"
        assert d["mesh_operations"][0]["max_length"] == "0.5mm"

    def test_add_frequency_sweep(self):
        h = HfssSetupConfig("setup1")
        sweep = h.add_frequency_sweep("sweep1")
        assert isinstance(sweep, FrequencySweepConfig)
        d = h.to_dict()
        assert len(d["freq_sweep"]) == 1
        assert d["freq_sweep"][0]["name"] == "sweep1"

    def test_multiple_sweeps(self):
        h = HfssSetupConfig("setup1")
        h.add_frequency_sweep("s1")
        h.add_frequency_sweep("s2", sweep_type="discrete")
        assert len(h.to_dict()["freq_sweep"]) == 2

    def test_no_mesh_ops_key_when_empty(self):
        h = HfssSetupConfig("s")
        d = h.to_dict()
        assert "mesh_operations" not in d


# ---------------------------------------------------------------------------
# SIwaveACSetupConfig
# ---------------------------------------------------------------------------


class TestSIwaveACSetupConfig:
    def test_defaults(self):
        s = SIwaveACSetupConfig("sw_ac")
        d = s.to_dict()
        assert d["type"] == "siwave_ac"
        assert d["si_slider_position"] == 1
        assert d["pi_slider_position"] == 1
        assert d["use_si_settings"] is True

    def test_custom_sliders(self):
        s = SIwaveACSetupConfig("sw_ac", si_slider_position=2, pi_slider_position=0)
        d = s.to_dict()
        assert d["si_slider_position"] == 2
        assert d["pi_slider_position"] == 0

    def test_add_frequency_sweep(self):
        s = SIwaveACSetupConfig("sw_ac")
        sw = s.add_frequency_sweep("sw1")
        assert isinstance(sw, FrequencySweepConfig)
        assert s.to_dict()["freq_sweep"][0]["name"] == "sw1"


# ---------------------------------------------------------------------------
# SIwaveDCSetupConfig
# ---------------------------------------------------------------------------


class TestSIwaveDCSetupConfig:
    def test_defaults(self):
        s = SIwaveDCSetupConfig("sw_dc")
        d = s.to_dict()
        assert d["type"] == "siwave_dc"
        assert d["dc_slider_position"] == 1
        assert d["dc_ir_settings"]["export_dc_thermal_data"] is False

    def test_custom(self):
        s = SIwaveDCSetupConfig("sw_dc", dc_slider_position=2, export_dc_thermal_data=True)
        d = s.to_dict()
        assert d["dc_slider_position"] == 2
        assert d["dc_ir_settings"]["export_dc_thermal_data"] is True


# ---------------------------------------------------------------------------
# SetupsConfig
# ---------------------------------------------------------------------------


class TestSetupsConfig:
    def test_empty(self):
        assert SetupsConfig().to_list() == []

    def test_add_hfss_setup(self):
        sc = SetupsConfig()
        h = sc.add_hfss_setup("h1")
        assert isinstance(h, HfssSetupConfig)
        assert sc.to_list()[0]["type"] == "hfss"

    def test_add_siwave_ac(self):
        sc = SetupsConfig()
        s = sc.add_siwave_ac_setup("sw_ac")
        assert isinstance(s, SIwaveACSetupConfig)
        assert sc.to_list()[0]["type"] == "siwave_ac"

    def test_add_siwave_dc(self):
        sc = SetupsConfig()
        s = sc.add_siwave_dc_setup("sw_dc")
        assert isinstance(s, SIwaveDCSetupConfig)
        assert sc.to_list()[0]["type"] == "siwave_dc"

    def test_mixed_setups(self):
        sc = SetupsConfig()
        sc.add_hfss_setup("h1")
        sc.add_siwave_ac_setup("ac1")
        sc.add_siwave_dc_setup("dc1")
        types = [s["type"] for s in sc.to_list()]
        assert types == ["hfss", "siwave_ac", "siwave_dc"]


# ---------------------------------------------------------------------------
# BoundariesConfig
# ---------------------------------------------------------------------------


class TestBoundariesConfig:
    def test_empty(self):
        assert BoundariesConfig().to_dict() == {}

    def test_radiation_boundary(self):
        b = BoundariesConfig()
        b.set_radiation_boundary()
        d = b.to_dict()
        assert d["use_open_region"] is True
        assert d["open_region_type"] == "radiation"

    def test_pml_boundary(self):
        b = BoundariesConfig()
        b.set_pml_boundary("5GHz", radiation_level=20, is_pml_visible=True)
        d = b.to_dict()
        assert d["open_region_type"] == "pml"
        assert d["operating_freq"] == "5GHz"
        assert d["radiation_level"] == 20
        assert d["is_pml_visible"] is True

    def test_air_box_extents(self):
        b = BoundariesConfig()
        b.set_air_box_extents(0.15, truncate_at_ground=True, sync=True)
        d = b.to_dict()
        assert d["air_box_horizontal_extent"]["size"] == 0.15
        assert d["truncate_air_box_at_ground"] is True
        assert d["sync_air_box_vertical_extent"] is True

    def test_air_box_asymmetric_vertical(self):
        b = BoundariesConfig()
        b.set_air_box_extents(
            0.1,
            positive_vertical_size=0.2,
            negative_vertical_size=0.05,
        )
        d = b.to_dict()
        assert d["air_box_positive_vertical_extent"]["size"] == 0.2
        assert d["air_box_negative_vertical_extent"]["size"] == 0.05

    def test_manual_attributes(self):
        b = BoundariesConfig()
        b.dielectric_extent_type = "ConvexHull"
        b.honor_user_dielectric = True
        d = b.to_dict()
        assert d["dielectric_extent_type"] == "ConvexHull"
        # honor_user_dielectric is only emitted when True
        assert d["honor_user_dielectric"] is True

    def test_honor_user_dielectric_default_not_emitted(self):
        b = BoundariesConfig()
        # Default is False → should not appear in the serialised dict
        assert "honor_user_dielectric" not in b.to_dict()


# ---------------------------------------------------------------------------
# CutoutConfig / OperationsConfig
# ---------------------------------------------------------------------------


class TestCutoutConfig:
    def test_defaults(self):
        c = CutoutConfig()
        d = c.to_dict()
        assert d["extent_type"] == "ConvexHull"
        assert d["expansion_size"] == 0.002

    def test_nets(self):
        c = CutoutConfig(signal_nets=["SIG1"], reference_nets=["GND"])
        d = c.to_dict()
        assert d["signal_list"] == ["SIG1"]
        assert d["reference_list"] == ["GND"]

    def test_auto_identify_nets(self):
        c = CutoutConfig(auto_identify_nets_enabled=True, resistor_below=200)
        d = c.to_dict()
        assert d["auto_identify_nets"]["enabled"] is True
        assert d["auto_identify_nets"]["resistor_below"] == 200


class TestOperationsConfig:
    def test_empty(self):
        assert OperationsConfig().to_dict() == {}

    def test_add_cutout(self):
        ops = OperationsConfig()
        c = ops.add_cutout(["SIG1"], ["GND"])
        assert isinstance(c, CutoutConfig)
        d = ops.to_dict()
        assert "cutout" in d
        assert d["cutout"]["signal_list"] == ["SIG1"]

    def test_generate_auto_hfss_regions(self):
        ops = OperationsConfig()
        ops.generate_auto_hfss_regions = True
        d = ops.to_dict()
        assert d["generate_auto_hfss_regions"] is True


# ---------------------------------------------------------------------------
# SParameterModelConfig / SParameterModelsConfig
# ---------------------------------------------------------------------------


class TestSParameterModelConfig:
    def test_basic(self):
        m = SParameterModelConfig("model1", "CAP_100nF", "/path/c.s2p")
        d = m.to_dict()
        assert d["name"] == "model1"
        assert d["component_definition"] == "CAP_100nF"
        assert d["file_path"] == "/path/c.s2p"
        assert d["apply_to_all"] is True

    def test_with_components(self):
        m = SParameterModelConfig("m1", "DEF", "f.s2p", apply_to_all=False, components=["C1", "C2"])
        d = m.to_dict()
        assert d["apply_to_all"] is False
        assert d["components"] == ["C1", "C2"]

    def test_reference_net_per_component(self):
        m = SParameterModelConfig("m1", "DEF", "f.s2p", reference_net_per_component={"C1": "GND1"})
        d = m.to_dict()
        assert d["reference_net_per_component"] == {"C1": "GND1"}

    def test_pin_order(self):
        m = SParameterModelConfig("m1", "DEF", "f.s2p", pin_order=["1", "2"])
        assert m.to_dict()["pin_order"] == ["1", "2"]

    def test_no_pin_order_key_when_none(self):
        m = SParameterModelConfig("m1", "DEF", "f.s2p")
        assert "pin_order" not in m.to_dict()


class TestSParameterModelsConfig:
    def test_empty(self):
        assert SParameterModelsConfig().to_list() == []

    def test_add(self):
        sc = SParameterModelsConfig()
        m = sc.add("model1", "CAP", "f.s2p")
        assert isinstance(m, SParameterModelConfig)
        assert sc.to_list()[0]["name"] == "model1"


# ---------------------------------------------------------------------------
# SpiceModelConfig / SpiceModelsConfig
# ---------------------------------------------------------------------------


class TestSpiceModelConfig:
    def test_basic(self):
        s = SpiceModelConfig("ic_spice", "IC_U1", "/ic.sp")
        d = s.to_dict()
        assert d["name"] == "ic_spice"
        assert d["component_definition"] == "IC_U1"
        assert d["apply_to_all"] is True

    def test_sub_circuit(self):
        s = SpiceModelConfig("ic", "IC_DEF", "ic.sp", sub_circuit_name="IC_SUB")
        assert s.to_dict()["sub_circuit_name"] == "IC_SUB"

    def test_components_list(self):
        s = SpiceModelConfig("ic", "DEF", "ic.sp", apply_to_all=False, components=["U1", "U2"])
        d = s.to_dict()
        assert d["apply_to_all"] is False
        assert d["components"] == ["U1", "U2"]

    def test_terminal_pairs(self):
        s = SpiceModelConfig("ic", "DEF", "ic.sp", terminal_pairs=[["1", "2"]])
        assert s.to_dict()["terminal_pairs"] == [["1", "2"]]


class TestSpiceModelsConfig:
    def test_empty(self):
        assert SpiceModelsConfig().to_list() == []

    def test_add(self):
        sc = SpiceModelsConfig()
        m = sc.add("sp1", "DEF", "f.sp")
        assert isinstance(m, SpiceModelConfig)
        assert sc.to_list()[0]["name"] == "sp1"


# ---------------------------------------------------------------------------
# VariablesConfig
# ---------------------------------------------------------------------------


class TestVariablesConfig:
    def test_empty(self):
        assert VariablesConfig().to_list() == []

    def test_add(self):
        v = VariablesConfig()
        v.add("trace_w", "0.1mm", "Trace width")
        lst = v.to_list()
        assert lst[0] == {"name": "trace_w", "value": "0.1mm", "description": "Trace width"}

    def test_numeric_value(self):
        v = VariablesConfig()
        v.add("via_diam", 0.2)
        assert v.to_list()[0]["value"] == 0.2

    def test_multiple(self):
        v = VariablesConfig()
        v.add("a", 1)
        v.add("b", 2)
        assert len(v.to_list()) == 2


# ---------------------------------------------------------------------------
# ModelerConfig
# ---------------------------------------------------------------------------


class TestModelerConfig:
    def test_empty(self):
        assert ModelerConfig().to_dict() == {}

    def test_add_trace(self):
        m = ModelerConfig()
        m.add_trace("t1", "top", "0.15mm", net_name="SIG1", path=[[0, 0], [0.01, 0]])
        d = m.to_dict()
        assert len(d["traces"]) == 1
        t = d["traces"][0]
        assert t["name"] == "t1"
        assert t["layer"] == "top"
        assert t["width"] == "0.15mm"
        assert t["net_name"] == "SIG1"

    def test_add_rectangular_plane(self):
        m = ModelerConfig()
        m.add_rectangular_plane(
            "GND_L", "gnd_rect", "GND", lower_left_point=[-0.05, -0.05], upper_right_point=[0.05, 0.05]
        )
        d = m.to_dict()
        plane = d["planes"][0]
        assert plane["type"] == "rectangle"
        assert plane["net_name"] == "GND"

    def test_add_circular_plane(self):
        m = ModelerConfig()
        m.add_circular_plane("L1", "circle1", "GND", radius="0.5mm", position=[0.01, 0.02])
        d = m.to_dict()
        assert d["planes"][0]["type"] == "circle"
        assert d["planes"][0]["radius"] == "0.5mm"

    def test_add_polygon_plane(self):
        m = ModelerConfig()
        m.add_polygon_plane("L2", "poly1", "VDD", points=[[0, 0], [0.01, 0], [0.01, 0.01], [0, 0.01]])
        d = m.to_dict()
        assert d["planes"][0]["type"] == "polygon"
        assert len(d["planes"][0]["points"]) == 4

    def test_padstack_definition(self):
        m = ModelerConfig()
        m.add_padstack_definition("via_0.2", material="copper")
        d = m.to_dict()
        assert d["padstack_definitions"][0]["name"] == "via_0.2"

    def test_padstack_instance(self):
        m = ModelerConfig()
        m.add_padstack_instance(name="v1", net_name="GND")
        d = m.to_dict()
        assert d["padstack_instances"][0]["name"] == "v1"

    def test_delete_primitives_by_layer(self):
        m = ModelerConfig()
        m.delete_primitives_by_layer(["old_layer1", "old_layer2"])
        d = m.to_dict()
        assert d["primitives_to_delete"]["layer_name"] == ["old_layer1", "old_layer2"]

    def test_delete_primitives_by_name(self):
        m = ModelerConfig()
        m.delete_primitives_by_name(["prim1", "prim2"])
        assert m.to_dict()["primitives_to_delete"]["name"] == ["prim1", "prim2"]

    def test_delete_primitives_by_net(self):
        m = ModelerConfig()
        m.delete_primitives_by_net(["old_net"])
        assert m.to_dict()["primitives_to_delete"]["net_name"] == ["old_net"]


# ---------------------------------------------------------------------------
# EdbConfigBuilder – integration / round-trip
# ---------------------------------------------------------------------------


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
        cfg.ports.add_coax_port("coax1", {"padstack": "v1"})
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

        # setups – HFSS broadband
        hfss = cfg.setups.add_hfss_setup("hfss_bb")
        hfss.set_broadband_adaptive("1GHz", "20GHz", max_passes=20, max_delta=0.02)
        hfss.set_auto_mesh_operation(enabled=True)
        hfss.add_length_mesh_operation("mesh1", {"DDR4_DQ0": ["top"]}, max_length="0.5mm")
        s1 = hfss.add_frequency_sweep("sweep1")
        s1.add_linear_count_frequencies("1GHz", "20GHz", 100)
        s1.add_single_frequency("5GHz")

        # setups – HFSS single
        hfss2 = cfg.setups.add_hfss_setup("hfss_single")
        hfss2.set_single_frequency_adaptive("5GHz", max_passes=15)

        # setups – HFSS multi-freq
        hfss3 = cfg.setups.add_hfss_setup("hfss_multi")
        hfss3.add_multi_frequency_adaptive("2GHz")
        hfss3.add_multi_frequency_adaptive("10GHz")

        # setups – SIwave AC
        siw = cfg.setups.add_siwave_ac_setup("siw_ac", si_slider_position=2, pi_slider_position=1)
        sw = siw.add_frequency_sweep("siw_sw1")
        sw.add_log_count_frequencies("1kHz", "1GHz", 100)

        # setups – SIwave DC
        cfg.setups.add_siwave_dc_setup("siw_dc", dc_slider_position=1, export_dc_thermal_data=True)

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
        assert len(bb["freq_sweep"]) == 1
        assert len(bb["freq_sweep"][0]["frequencies"]) == 2

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
        assert "DDR4_DQ0" in d["operations"]["cutout"]["signal_list"]

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
        ptd = d["modeler"]["primitives_to_delete"]
        assert "old_layer" in ptd["layer_name"]
        assert "old_net" in ptd["net_name"]


# ---------------------------------------------------------------------------
# EdbConfigBuilder – JSON serialisation
# ---------------------------------------------------------------------------


class TestEdbConfigBuilderJson:
    def _simple_builder(self) -> EdbConfigBuilder:
        cfg = EdbConfigBuilder()
        cfg.general.anti_pads_always_on = True
        cfg.nets.add_signal_nets(["SIG"])
        cfg.nets.add_power_ground_nets(["GND"])
        hfss = cfg.setups.add_hfss_setup("h1")
        hfss.set_broadband_adaptive("1GHz", "10GHz")
        s = hfss.add_frequency_sweep("sw1")
        s.add_linear_count_frequencies("1GHz", "10GHz", 50)
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
        assert "setups" in data

    def test_from_json_round_trip(self, tmp_path):
        cfg = self._simple_builder()
        path = tmp_path / "config.json"
        cfg.to_json(str(path))
        cfg2 = EdbConfigBuilder.from_json(str(path))
        assert cfg.to_dict() == cfg2.to_dict()

    def test_from_dict_round_trip(self):
        cfg = self._simple_builder()
        d = cfg.to_dict()
        cfg2 = EdbConfigBuilder.from_dict(d)
        assert cfg.to_dict() == cfg2.to_dict()

    def test_to_json_creates_parent_dirs(self, tmp_path):
        cfg = self._simple_builder()
        output = tmp_path / "nested" / "dir" / "config.json"
        cfg.to_json(str(output))
        assert output.exists()


# ---------------------------------------------------------------------------
# EdbConfigBuilder – empty builder produces empty dict
# ---------------------------------------------------------------------------


class TestEdbConfigBuilderEmpty:
    def test_empty_builder_produces_empty_dict(self):
        cfg = EdbConfigBuilder()
        assert cfg.to_dict() == {}

    def test_partial_builder_only_has_populated_keys(self):
        cfg = EdbConfigBuilder()
        cfg.nets.add_signal_nets(["SIG1"])
        d = cfg.to_dict()
        assert list(d.keys()) == ["nets"]


# ---------------------------------------------------------------------------
# TerminalInfo helpers
# ---------------------------------------------------------------------------


class TestTerminalInfo:
    def test_pin(self):
        t = TerminalInfo.pin("A1")
        assert t == {"pin": "A1"}

    def test_pin_with_refdes(self):
        t = TerminalInfo.pin("A1", reference_designator="U1")
        assert t == {"pin": "A1", "reference_designator": "U1"}

    def test_net(self):
        t = TerminalInfo.net("VDD")
        assert t == {"net": "VDD"}

    def test_net_with_refdes(self):
        t = TerminalInfo.net("VDD", reference_designator="U1")
        assert t["reference_designator"] == "U1"

    def test_pin_group(self):
        t = TerminalInfo.pin_group("pg1")
        assert t == {"pin_group": "pg1"}

    def test_padstack(self):
        t = TerminalInfo.padstack("via_001")
        assert t == {"padstack": "via_001"}

    def test_coordinates(self):
        t = TerminalInfo.coordinates("top", 0.001, 0.002, "SIG")
        assert t == {"coordinates": {"layer": "top", "point": [0.001, 0.002], "net": "SIG"}}

    def test_nearest_pin(self):
        t = TerminalInfo.nearest_pin("GND", search_radius="5mm")
        assert t == {"nearest_pin": {"reference_net": "GND", "search_radius": "5mm"}}

    def test_nearest_pin_default_radius(self):
        t = TerminalInfo.nearest_pin("GND")
        assert t["nearest_pin"]["search_radius"] == "5mm"


# ---------------------------------------------------------------------------
# TerminalsConfig + terminal types
# ---------------------------------------------------------------------------


class TestPadstackInstanceTerminal:
    def test_basic(self):
        t = PadstackInstanceTerminal("t1", "via_1", 50, "port", None)
        d = t.to_dict()
        assert d["terminal_type"] == "padstack_instance"
        assert d["name"] == "t1"
        assert d["padstack_instance"] == "via_1"
        assert d["impedance"] == 50
        assert d["boundary_type"] == "port"

    def test_optional_fields(self):
        t = PadstackInstanceTerminal(
            "t1",
            "via_1",
            50,
            "port",
            "Wave",
            is_circuit_port=True,
            reference_terminal="ref_t",
            layer="top",
            padstack_instance_id=42,
        )
        d = t.to_dict()
        assert d["hfss_type"] == "Wave"
        assert d["is_circuit_port"] is True
        assert d["reference_terminal"] == "ref_t"
        assert d["layer"] == "top"
        assert d["padstack_instance_id"] == 42


class TestPinGroupTerminal:
    def test_basic(self):
        t = PinGroupTerminal("t1", "pg_VDD", 50, "port")
        d = t.to_dict()
        assert d["terminal_type"] == "pin_group"
        assert d["pin_group"] == "pg_VDD"
        assert d["is_circuit_port"] is True

    def test_reference_terminal(self):
        t = PinGroupTerminal("t1", "pg_VDD", 50, "port", reference_terminal="ref_t")
        assert t.to_dict()["reference_terminal"] == "ref_t"


class TestPointTerminal:
    def test_basic(self):
        t = PointTerminal("t1", 0.001, 0.002, "top", "SIG", 50, "port")
        d = t.to_dict()
        assert d["terminal_type"] == "point"
        assert d["x"] == 0.001
        assert d["y"] == 0.002
        assert d["layer"] == "top"
        assert d["net"] == "SIG"

    def test_no_ref_terminal_key_when_none(self):
        t = PointTerminal("t1", 0, 0, "top", "SIG", 50, "port")
        assert "reference_terminal" not in t.to_dict()


class TestEdgeTerminal:
    def test_basic(self):
        t = EdgeTerminal("t1", "prim1", 0.001, 0.002, 50, "port")
        d = t.to_dict()
        assert d["terminal_type"] == "edge"
        assert d["primitive"] == "prim1"
        assert d["hfss_type"] == "Wave"
        assert d["horizontal_extent_factor"] == 6

    def test_custom_extent(self):
        t = EdgeTerminal("t1", "prim1", 0, 0, 50, "port", horizontal_extent_factor=8, vertical_extent_factor=10)
        d = t.to_dict()
        assert d["horizontal_extent_factor"] == 8
        assert d["vertical_extent_factor"] == 10


class TestBundleTerminal:
    def test_basic(self):
        t = BundleTerminal("bundle1", ["t1", "t2"])
        d = t.to_dict()
        assert d["terminal_type"] == "bundle"
        assert d["terminals"] == ["t1", "t2"]


class TestTerminalsConfig:
    def test_empty(self):
        assert TerminalsConfig().to_list() == []

    def test_add_padstack_instance_terminal(self):
        tc = TerminalsConfig()
        t = tc.add_padstack_instance_terminal("t1", "via_1", 50, "port", None)
        assert isinstance(t, PadstackInstanceTerminal)
        assert tc.to_list()[0]["name"] == "t1"

    def test_add_pin_group_terminal(self):
        tc = TerminalsConfig()
        t = tc.add_pin_group_terminal("t2", "pg1", 50, "port")
        assert isinstance(t, PinGroupTerminal)
        assert tc.to_list()[0]["pin_group"] == "pg1"

    def test_add_point_terminal(self):
        tc = TerminalsConfig()
        t = tc.add_point_terminal("t3", 0.001, 0.002, "top", "SIG", 50, "port")
        assert isinstance(t, PointTerminal)
        assert tc.to_list()[0]["x"] == 0.001

    def test_add_edge_terminal(self):
        tc = TerminalsConfig()
        t = tc.add_edge_terminal("t4", "prim1", 0, 0, 50, "port")
        assert isinstance(t, EdgeTerminal)
        assert tc.to_list()[0]["terminal_type"] == "edge"

    def test_add_bundle_terminal(self):
        tc = TerminalsConfig()
        t = tc.add_bundle_terminal("bundle1", ["t1", "t2"])
        assert isinstance(t, BundleTerminal)
        assert tc.to_list()[0]["terminals"] == ["t1", "t2"]

    def test_mixed_terminals(self):
        tc = TerminalsConfig()
        tc.add_padstack_instance_terminal("t1", "via_1", 50, "port", None)
        tc.add_pin_group_terminal("t2", "pg1", 50, "port")
        tc.add_bundle_terminal("bundle1", ["t1", "t2"])
        types = [t["terminal_type"] for t in tc.to_list()]
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


# ---------------------------------------------------------------------------
# HeatSinkConfig / PackageDefinitionConfig / PackageDefinitionsConfig
# ---------------------------------------------------------------------------


class TestHeatSinkConfig:
    def test_empty(self):
        hs = HeatSinkConfig()
        assert hs.to_dict() == {}

    def test_partial(self):
        hs = HeatSinkConfig(fin_height="3mm", fin_spacing="1mm")
        d = hs.to_dict()
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
        d = hs.to_dict()
        assert len(d) == 5


class TestPackageDefinitionConfig:
    def test_minimal(self):
        pkg = PackageDefinitionConfig("PKG1", "BGA_256")
        d = pkg.to_dict()
        assert d == {"name": "PKG1", "component_definition": "BGA_256"}

    def test_with_thermal_properties(self):
        pkg = PackageDefinitionConfig("PKG1", "BGA_256", maximum_power="5W", theta_jb="10C/W")
        d = pkg.to_dict()
        assert d["maximum_power"] == "5W"
        assert d["theta_jb"] == "10C/W"

    def test_with_heatsink(self):
        pkg = PackageDefinitionConfig("PKG1", "BGA_256")
        hs = pkg.set_heatsink(fin_height="3mm", fin_spacing="1mm")
        assert isinstance(hs, HeatSinkConfig)
        d = pkg.to_dict()
        assert "heatsink" in d
        assert d["heatsink"]["fin_height"] == "3mm"

    def test_apply_to_all(self):
        pkg = PackageDefinitionConfig("PKG1", "BGA", apply_to_all=True)
        d = pkg.to_dict()
        assert d["apply_to_all"] is True

    def test_explicit_components(self):
        pkg = PackageDefinitionConfig("PKG1", "BGA", apply_to_all=False, components=["U1", "U2"])
        d = pkg.to_dict()
        assert d["components"] == ["U1", "U2"]

    def test_empty_heatsink_not_emitted(self):
        pkg = PackageDefinitionConfig("PKG1", "BGA")
        # no set_heatsink call → no heatsink key
        assert "heatsink" not in pkg.to_dict()


class TestPackageDefinitionsConfig:
    def test_empty(self):
        assert PackageDefinitionsConfig().to_list() == []

    def test_add(self):
        pc = PackageDefinitionsConfig()
        pkg = pc.add("PKG1", "BGA_256", maximum_power="5W")
        assert isinstance(pkg, PackageDefinitionConfig)
        lst = pc.to_list()
        assert len(lst) == 1
        assert lst[0]["name"] == "PKG1"

    def test_multiple(self):
        pc = PackageDefinitionsConfig()
        pc.add("P1", "DEF1")
        pc.add("P2", "DEF2", theta_jc="5C/W")
        assert len(pc.to_list()) == 2

    def test_in_builder(self):
        cfg = EdbConfigBuilder()
        pkg = cfg.package_definitions.add("PKG1", "BGA_256", apply_to_all=True)
        pkg.maximum_power = "5W"
        pkg.set_heatsink(fin_height="3mm")
        d = cfg.to_dict()
        assert "package_definitions" in d
        assert d["package_definitions"][0]["heatsink"]["fin_height"] == "3mm"

    def test_round_trip(self, tmp_path):
        cfg = EdbConfigBuilder()
        pkg = cfg.package_definitions.add("PKG1", "BGA_256", apply_to_all=True)
        pkg.maximum_power = "5W"
        path = tmp_path / "pkg_cfg.json"
        cfg.to_json(str(path))
        cfg2 = EdbConfigBuilder.from_json(str(path))
        assert cfg.to_dict() == cfg2.to_dict()


# ---------------------------------------------------------------------------
# BoundariesConfig – new helpers (set_extent, set_dielectric_extent)
# ---------------------------------------------------------------------------


class TestBoundariesConfigExtras:
    def test_set_extent(self):
        b = BoundariesConfig()
        b.set_extent("ConvexHull", truncate_air_box_at_ground=True)
        d = b.to_dict()
        assert d["extent_type"] == "ConvexHull"
        assert d["truncate_air_box_at_ground"] is True

    def test_set_extent_with_polygon(self):
        b = BoundariesConfig()
        b.set_extent("Polygon", base_polygon="my_poly")
        d = b.to_dict()
        assert d["base_polygon"] == "my_poly"

    def test_set_dielectric_extent(self):
        b = BoundariesConfig()
        b.set_dielectric_extent("BoundingBox", expansion_size=0.001, is_multiple=False)
        d = b.to_dict()
        assert d["dielectric_extent_type"] == "BoundingBox"
        assert d["dielectric_extent_size"]["size"] == 0.001

    def test_set_dielectric_extent_honor(self):
        b = BoundariesConfig()
        b.set_dielectric_extent("Conformal", honor_user_dielectric=True)
        d = b.to_dict()
        assert d["honor_user_dielectric"] is True

    def test_set_dielectric_extent_polygon(self):
        b = BoundariesConfig()
        b.set_dielectric_extent("Polygon", base_polygon="diel_poly")
        assert b.to_dict()["dielectric_base_polygon"] == "diel_poly"


# ---------------------------------------------------------------------------
# ModelerConfig – add_component
# ---------------------------------------------------------------------------


class TestModelerConfigComponent:
    def test_add_component(self):
        m = ModelerConfig()
        comp = m.add_component("R1", part_type="resistor")
        assert isinstance(comp, ComponentConfig)
        d = m.to_dict()
        assert d["components"][0]["reference_designator"] == "R1"
        assert d["components"][0]["part_type"] == "resistor"

    def test_add_component_with_model(self):
        m = ModelerConfig()
        comp = m.add_component("R1")
        comp.add_pin_pair_rlc("1", "2", resistance="100ohm", resistance_enabled=True)
        d = m.to_dict()
        assert d["components"][0]["pin_pair_model"][0]["resistance"] == "100ohm"

    def test_modeler_round_trip_with_component(self, tmp_path):
        cfg = EdbConfigBuilder()
        comp = cfg.modeler.add_component("C1", part_type="capacitor")
        comp.add_pin_pair_rlc("1", "2", capacitance="10nF", capacitance_enabled=True)
        path = tmp_path / "mod_cfg.json"
        cfg.to_json(str(path))
        cfg2 = EdbConfigBuilder.from_json(str(path))
        assert cfg.to_dict() == cfg2.to_dict()


# ---------------------------------------------------------------------------
# EdbConfigBuilder – package_definitions and terminals in full integration
# ---------------------------------------------------------------------------


class TestEdbConfigBuilderFull:
    def test_all_17_sections(self):
        cfg = EdbConfigBuilder()
        cfg.general.anti_pads_always_on = False
        cfg.stackup.add_material("copper", conductivity=5.8e7)
        cfg.nets.add_signal_nets(["SIG"])
        cfg.components.add("R1")
        cfg.padstacks.add_definition("via")
        cfg.pin_groups.add("pg1", "U1", net="GND")
        cfg.terminals.add_pin_group_terminal("t1", "pg1", 50, "port")
        cfg.ports.add_circuit_port("p1", TerminalInfo.pin_group("pg1"))
        cfg.sources.add_current_source("i1", TerminalInfo.net("VDD"), TerminalInfo.net("GND"))
        cfg.probes.add("pr1", TerminalInfo.net("SIG"), TerminalInfo.net("GND"))
        hfss = cfg.setups.add_hfss_setup("h1")
        hfss.set_broadband_adaptive("1GHz", "10GHz")
        cfg.boundaries.set_radiation_boundary()
        cfg.operations.add_cutout(["SIG"], ["GND"])
        cfg.s_parameters.add("m1", "CAP", "f.s2p")
        cfg.spice_models.add("sp1", "IC", "f.sp")
        cfg.package_definitions.add("PKG1", "BGA_256", apply_to_all=True)
        cfg.variables.add("x", 1)
        cfg.modeler.add_trace("t1", "top", "0.1mm")

        d = cfg.to_dict()
        expected_keys = {
            "general",
            "stackup",
            "nets",
            "components",
            "padstacks",
            "pin_groups",
            "terminals",
            "ports",
            "sources",
            "probes",
            "setups",
            "boundaries",
            "operations",
            "s_parameters",
            "spice_models",
            "package_definitions",
            "variables",
            "modeler",
        }
        assert expected_keys == set(d.keys())

    def test_terminal_info_in_ports(self):
        cfg = EdbConfigBuilder()
        cfg.ports.add_circuit_port(
            "p1",
            positive_terminal=TerminalInfo.pin_group("pg_VDD"),
            negative_terminal=TerminalInfo.nearest_pin("GND"),
        )
        d = cfg.to_dict()
        p = d["ports"][0]
        assert p["positive_terminal"] == {"pin_group": "pg_VDD"}
        assert p["negative_terminal"]["nearest_pin"]["reference_net"] == "GND"

    def test_terminal_info_coordinates_in_source(self):
        cfg = EdbConfigBuilder()
        cfg.sources.add_current_source(
            "isrc",
            positive_terminal=TerminalInfo.coordinates("top", 0.001, 0.002, "SIG"),
            negative_terminal=TerminalInfo.coordinates("top", 0.003, 0.004, "GND"),
        )
        d = cfg.to_dict()
        pos = d["sources"][0]["positive_terminal"]
        assert pos["coordinates"]["layer"] == "top"
        assert pos["coordinates"]["point"] == [0.001, 0.002]


# ---------------------------------------------------------------------------
# Configuration.load / run / create_config_builder bridge tests
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_configuration():
    """Return a MagicMock that replicates the Configuration.load / run /
    create_config_builder surface added in configuration.py."""
    cfg_data = MagicMock()
    cfg_data.data = {}

    mock = MagicMock()
    mock.data = {}
    mock.cfg_data = cfg_data
    mock._run_called = False
    mock._last_loaded_data = None

    def _load(config_file, append=True, apply_file=False, **kwargs):
        payload = config_file.to_dict() if isinstance(config_file, EdbConfigBuilder) else copy.deepcopy(config_file)
        mock._last_loaded_data = payload
        mock.cfg_data.data = payload
        if apply_file:
            mock._run_called = True
        return mock.cfg_data

    def _run(config=None, **kwargs):
        if config is not None:
            _load(config)
        mock._run_called = True
        return True

    def _create_config_builder():
        return EdbConfigBuilder()

    mock.load.side_effect = _load
    mock.run.side_effect = _run
    mock.create_config_builder.side_effect = _create_config_builder
    return mock


class TestConfigurationBridgeMethods:
    """Tests for the EdbConfigBuilder ↔ Configuration bridge."""

    def test_load_accepts_builder(self, mock_configuration):
        cfg = EdbConfigBuilder()
        cfg.general.anti_pads_always_on = False
        cfg.nets.add_signal_nets(["SIG"])

        mock_configuration.load(cfg)

        assert mock_configuration._last_loaded_data["general"]["anti_pads_always_on"] is False
        assert mock_configuration._last_loaded_data["nets"]["signal_nets"] == ["SIG"]

    def test_load_accepts_plain_dict(self, mock_configuration):
        mock_configuration.load({"nets": {"signal_nets": ["CLK"]}})
        assert mock_configuration._last_loaded_data["nets"]["signal_nets"] == ["CLK"]

    def test_load_builder_produces_same_payload_as_to_dict(self, mock_configuration):
        cfg = EdbConfigBuilder()
        cfg.general.s_parameter_library = "/models/snp"
        cfg.nets.add_power_ground_nets(["VDD", "GND"])

        mock_configuration.load(cfg)

        assert mock_configuration._last_loaded_data == cfg.to_dict()

    def test_load_apply_file_calls_run(self, mock_configuration):
        cfg = EdbConfigBuilder()
        cfg.general.suppress_pads = True

        mock_configuration.load(cfg, apply_file=True)

        assert mock_configuration._run_called is True

    def test_run_with_builder_loads_and_runs(self, mock_configuration):
        cfg = EdbConfigBuilder()
        cfg.nets.add_signal_nets(["DDR_DQ0"])

        result = mock_configuration.run(cfg)

        assert result is True
        assert mock_configuration._run_called is True
        assert mock_configuration._last_loaded_data["nets"]["signal_nets"] == ["DDR_DQ0"]

    def test_run_with_dict_loads_and_runs(self, mock_configuration):
        result = mock_configuration.run({"general": {"suppress_pads": True}})

        assert result is True
        assert mock_configuration._run_called is True
        assert mock_configuration._last_loaded_data["general"]["suppress_pads"] is True

    def test_run_without_config_uses_existing_cfg_data(self, mock_configuration):
        mock_configuration.load({"nets": {"signal_nets": ["PRE"]}})
        mock_configuration.run()

        assert mock_configuration._run_called is True
        assert mock_configuration.cfg_data.data["nets"]["signal_nets"] == ["PRE"]

    def test_run_config_none_does_not_load(self, mock_configuration):
        mock_configuration.run(config=None)

        assert mock_configuration._last_loaded_data is None
        assert mock_configuration._run_called is True

    def test_create_config_builder_returns_builder(self, mock_configuration):
        builder = mock_configuration.create_config_builder()
        assert isinstance(builder, EdbConfigBuilder)

    def test_create_config_builder_returns_fresh_instance(self, mock_configuration):
        b1 = mock_configuration.create_config_builder()
        b2 = mock_configuration.create_config_builder()
        assert b1 is not b2

    def test_create_config_builder_empty_on_creation(self, mock_configuration):
        builder = mock_configuration.create_config_builder()
        assert builder.to_dict() == {}

    def test_create_run_roundtrip(self, mock_configuration):
        cfg = mock_configuration.create_config_builder()
        cfg.general.anti_pads_always_on = True
        cfg.nets.add_signal_nets(["SIG1", "SIG2"])
        cfg.nets.add_power_ground_nets(["VDD", "GND"])

        mock_configuration.run(cfg)

        assert mock_configuration._run_called is True
        d = mock_configuration._last_loaded_data
        assert d["general"]["anti_pads_always_on"] is True
        assert set(d["nets"]["signal_nets"]) == {"SIG1", "SIG2"}
        assert set(d["nets"]["power_ground_nets"]) == {"VDD", "GND"}

    def test_create_builder_and_populate_all_major_sections(self, mock_configuration):
        cfg = mock_configuration.create_config_builder()

        cfg.general.spice_model_library = "/models"
        cfg.stackup.add_material("copper", conductivity=5.8e7)
        cfg.nets.add_signal_nets(["CLK"])
        cfg.components.add("R1")
        cfg.padstacks.add_definition("via")
        cfg.pin_groups.add("pg_GND", "U1", net="GND")
        cfg.variables.add("w", "0.15mm")
        hfss = cfg.setups.add_hfss_setup("setup1")
        hfss.set_single_frequency_adaptive("5GHz")

        d = cfg.to_dict()
        assert "general" in d
        assert "stackup" in d
        assert "nets" in d
        assert "components" in d
        assert "padstacks" in d
        assert "pin_groups" in d
        assert "variables" in d
        assert "setups" in d
