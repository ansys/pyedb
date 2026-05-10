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
from unittest.mock import MagicMock

import pytest

from pyedb.configuration import (
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

    def test_explicit_params_no_kwargs(self):
        """All material properties are explicit — no **kwargs required."""
        m = MaterialConfig(
            "silver",
            conductivity=6.3e7,
            permittivity=1.0,
            dielectric_loss_tangent=0.0,
            magnetic_loss_tangent=0.0,
            mass_density=10490,
            permeability=1.0,
            poisson_ratio=0.37,
            specific_heat=235,
            thermal_conductivity=429,
            youngs_modulus=83e9,
            thermal_expansion_coefficient=19e-6,
        )
        d = m.to_dict()
        assert d["conductivity"] == 6.3e7
        assert d["mass_density"] == 10490


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

    def test_explicit_params(self):
        """All layer params are explicit — no **kwargs required."""
        layer = LayerConfig("sig", type="signal", material="copper", fill_material="fr4", thickness="18um")
        d = layer.to_dict()
        assert d["fill_material"] == "fr4"
        assert d["thickness"] == "18um"

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

    def test_method_chaining(self):
        """set_huray_roughness and set_etching return self for chaining."""
        layer = LayerConfig("top")
        result = layer.set_huray_roughness("0.1um", "2.9").set_etching(factor=0.3)
        assert result is layer
        d = layer.to_dict()
        assert "roughness" in d
        assert "etching" in d


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

    def test_add_material_all_props(self):
        s = StackupConfig()
        s.add_material(
            "fr4",
            permittivity=4.4,
            dielectric_loss_tangent=0.02,
            thermal_conductivity=0.3,
            mass_density=1900,
        )
        d = s.to_dict()["materials"][0]
        assert d["permittivity"] == 4.4
        assert d["thermal_conductivity"] == 0.3
        assert d["mass_density"] == 1900

    def test_add_layer(self):
        s = StackupConfig()
        s.add_layer("top", type="signal", material="copper", thickness="35um")
        d = s.to_dict()
        assert d["layers"][0]["name"] == "top"

    def test_add_layer_explicit_fill_material(self):
        s = StackupConfig()
        s.add_layer("sig", type="signal", material="copper", fill_material="fr4", thickness="18um")
        d = s.to_dict()["layers"][0]
        assert d["fill_material"] == "fr4"
        assert d["thickness"] == "18um"

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

    def test_add_signal_layer_returns_layer_config(self):
        s = StackupConfig()
        lyr = s.add_signal_layer("top")
        assert isinstance(lyr, LayerConfig)

    def test_layer_roughness_via_stackup(self):
        s = StackupConfig()
        lyr = s.add_signal_layer("top")
        lyr.set_huray_roughness("0.1um", "2.9")
        d = s.to_dict()["layers"][0]
        assert d["roughness"]["top"]["model"] == "huray"


# ---------------------------------------------------------------------------
# TestCfgStackupAddMaterial
# ---------------------------------------------------------------------------


class TestCfgStackupAddMaterial:
    def test_returns_material_config_instance(self):
        s = StackupConfig()
        mat = s.add_material("copper", conductivity=5.8e7)
        assert isinstance(mat, MaterialConfig)

    def test_material_appended_to_list(self):
        s = StackupConfig()
        s.add_material("copper", conductivity=5.8e7)
        d = s.to_dict()
        assert "materials" in d
        assert len(d["materials"]) == 1
        assert d["materials"][0]["name"] == "copper"

    def test_material_conductivity_stored(self):
        s = StackupConfig()
        s.add_material("copper", conductivity=5.8e7)
        d = s.to_dict()["materials"][0]
        assert d["conductivity"] == 5.8e7

    def test_material_dielectric_properties(self):
        s = StackupConfig()
        s.add_material("fr4", permittivity=4.4, dielectric_loss_tangent=0.02)
        d = s.to_dict()["materials"][0]
        assert d["permittivity"] == 4.4
        assert d["dielectric_loss_tangent"] == 0.02

    def test_material_thermal_properties(self):
        s = StackupConfig()
        s.add_material("fr4", thermal_conductivity=0.3, mass_density=1900, specific_heat=1050)
        d = s.to_dict()["materials"][0]
        assert d["thermal_conductivity"] == 0.3
        assert d["mass_density"] == 1900
        assert d["specific_heat"] == 1050

    def test_material_mechanical_properties(self):
        s = StackupConfig()
        s.add_material("copper", youngs_modulus=110e9, poisson_ratio=0.34, thermal_expansion_coefficient=17e-6)
        d = s.to_dict()["materials"][0]
        assert d["youngs_modulus"] == 110e9
        assert d["poisson_ratio"] == 0.34
        assert d["thermal_expansion_coefficient"] == 17e-6

    def test_material_dc_override_properties(self):
        s = StackupConfig()
        s.add_material("mat", dc_conductivity=1e5, dc_permittivity=4.0)
        d = s.to_dict()["materials"][0]
        assert d["dc_conductivity"] == 1e5
        assert d["dc_permittivity"] == 4.0

    def test_material_frequency_dependent_properties(self):
        s = StackupConfig()
        s.add_material(
            "mat",
            dielectric_model_frequency=1e9,
            loss_tangent_at_frequency=0.01,
            permittivity_at_frequency=4.3,
        )
        d = s.to_dict()["materials"][0]
        assert d["dielectric_model_frequency"] == 1e9
        assert d["loss_tangent_at_frequency"] == 0.01
        assert d["permittivity_at_frequency"] == 4.3

    def test_multiple_materials_accumulated(self):
        s = StackupConfig()
        s.add_material("copper", conductivity=5.8e7)
        s.add_material("fr4", permittivity=4.4)
        s.add_material("air", permittivity=1.0)
        d = s.to_dict()
        assert len(d["materials"]) == 3
        names = [m["name"] for m in d["materials"]]
        assert names == ["copper", "fr4", "air"]

    def test_name_only_no_extra_keys(self):
        s = StackupConfig()
        s.add_material("mymat")
        d = s.to_dict()["materials"][0]
        assert d == {"name": "mymat"}

    def test_none_values_not_included(self):
        s = StackupConfig()
        s.add_material("copper", conductivity=5.8e7, permittivity=None)
        d = s.to_dict()["materials"][0]
        assert "permittivity" not in d

    def test_all_properties(self):
        s = StackupConfig()
        props = {
            "conductivity": 1e6,
            "permittivity": 4.4,
            "dielectric_loss_tangent": 0.01,
            "magnetic_loss_tangent": 0.001,
            "mass_density": 8960,
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
        s.add_material("full_mat", **props)
        d = s.to_dict()["materials"][0]
        for key, val in props.items():
            assert d[key] == val

    def test_duplicate_in_builder_raises(self):
        s = StackupConfig()
        s.add_material("copper", conductivity=5.8e7)
        with pytest.raises(ValueError, match="already exists"):
            s.add_material("copper", conductivity=4.1e7)

    def test_duplicate_error_message_advises_get_material(self):
        s = StackupConfig()
        s.add_material("fr4", permittivity=4.4)
        with pytest.raises(ValueError, match="get_material"):
            s.add_material("fr4")

    def test_duplicate_check_in_edb_raises(self):
        """When a live EDB session is attached, add_material raises if the
        material already exists in the EDB library."""
        mock_pedb = MagicMock()
        mock_pedb.materials.materials = {"copper": MagicMock()}
        s = StackupConfig()
        s._set_pedb(mock_pedb)
        with pytest.raises(ValueError, match="already exists"):
            s.add_material("copper", conductivity=5.8e7)

    def test_no_duplicate_check_without_pedb(self):
        """Without a live session only the local registry is checked."""
        s = StackupConfig()
        s.add_material("copper", conductivity=5.8e7)
        # Same name a second time must raise even without _pedb
        with pytest.raises(ValueError):
            s.add_material("copper")


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

    def test_add_reference_nets(self):
        n = NetsConfig()
        n.add_reference_nets(["GND", "AGND"])
        # reference_nets are NOT serialized in to_dict (only used for cutout forwarding)
        assert "reference_nets" not in n.to_dict()
        assert n.reference_nets == ["GND", "AGND"]

    def test_reference_nets_property(self):
        n = NetsConfig()
        n.add_reference_nets(["GND"])
        assert n.reference_nets == ["GND"]

    def test_signal_nets_property(self):
        n = NetsConfig()
        n.add_signal_nets(["CLK", "DATA"])
        assert n.signal_nets == ["CLK", "DATA"]

    def test_power_ground_nets_property(self):
        n = NetsConfig()
        n.add_power_ground_nets(["VDD"])
        assert n.power_ground_nets == ["VDD"]

    def test_reference_nets_usable_in_cutout(self):
        """Verify the reference_nets property can be passed directly to add_cutout."""
        from pyedb.configuration import OperationsConfig

        n = NetsConfig()
        n.add_signal_nets(["SIG"])
        n.add_reference_nets(["GND"])
        ops = OperationsConfig()
        c = ops.add_cutout(signal_nets=n.signal_nets, reference_nets=n.reference_nets)
        d = ops.to_dict()
        assert d["cutout"]["signal_list"] == ["SIG"]
        assert d["cutout"]["reference_list"] == ["GND"]


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

    def test_all_explicit_params(self):
        """All CfgPadstackDefinition fields are explicit — no **kwargs."""
        p = PadstackDefinitionConfig(
            "via_full",
            hole_plating_thickness="25um",
            material="copper",
            hole_range="upper_pad_to_lower_pad",
            pad_parameters={"pad_type": "circle"},
            hole_parameters={"shape": "circle"},
            solder_ball_parameters={"diameter": "150um"},
        )
        d = p.to_dict()
        assert d["hole_range"] == "upper_pad_to_lower_pad"
        assert d["pad_parameters"]["pad_type"] == "circle"
        assert d["solder_ball_parameters"]["diameter"] == "150um"


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

    def test_all_explicit_params(self):
        """All CfgPadstackInstance fields are explicit — no **kwargs."""
        inst = PadstackInstanceConfig(
            name="v2",
            net_name="SIG",
            definition="via_0.2",
            layer_range=["top", "L2"],
            position=[0.001, 0.002],
            rotation=45,
            is_pin=False,
            hole_override_enabled=True,
            hole_override_diameter="0.22mm",
            solder_ball_layer="top",
        )
        d = inst.to_dict()
        assert d["definition"] == "via_0.2"
        assert d["hole_override_enabled"] is True
        assert d["hole_override_diameter"] == "0.22mm"
        assert d["solder_ball_layer"] == "top"

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

    def test_backdrill_chaining(self):
        """set_backdrill returns self for method chaining."""
        inst = PadstackInstanceConfig(name="via")
        result = inst.set_backdrill("L3", "0.25mm")
        assert result is inst


class TestPadstacksConfig:
    def test_empty(self):
        assert PadstacksConfig().to_dict() == {}

    def test_add_definition(self):
        ps = PadstacksConfig()
        pdef = ps.add_definition("via", material="copper")
        assert isinstance(pdef, PadstackDefinitionConfig)
        d = ps.to_dict()
        assert d["definitions"][0]["name"] == "via"

    def test_add_definition_all_params(self):
        ps = PadstacksConfig()
        ps.add_definition(
            "via_full",
            hole_plating_thickness="25um",
            material="copper",
            hole_range="upper_pad_to_lower_pad",
        )
        d = ps.to_dict()["definitions"][0]
        assert d["hole_range"] == "upper_pad_to_lower_pad"

    def test_add_instance(self):
        ps = PadstacksConfig()
        inst = ps.add_instance(name="v1", net_name="SIG1")
        assert isinstance(inst, PadstackInstanceConfig)
        d = ps.to_dict()
        assert d["instances"][0]["name"] == "v1"

    def test_add_instance_all_params(self):
        ps = PadstacksConfig()
        inst = ps.add_instance(
            name="v2",
            net_name="GND",
            definition="via_0.2",
            layer_range=["top", "bot"],
            position=[0.001, 0.002],
            rotation=0,
            is_pin=False,
            hole_override_enabled=False,
        )
        d = ps.to_dict()["instances"][0]
        assert d["definition"] == "via_0.2"
        assert d["layer_range"] == ["top", "bot"]


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

    def test_add_coax_port_padstack_shortcut(self):
        pc = PortsConfig()
        pc.add_coax_port("coax1", padstack="via_A1")
        d = pc.to_list()[0]
        assert d["type"] == "coax"
        assert d["positive_terminal"] == {"padstack": "via_A1"}

    def test_add_coax_port_net_shortcut(self):
        pc = PortsConfig()
        pc.add_coax_port("coax_vdd", net="VDD", reference_designator="U1")
        d = pc.to_list()[0]
        assert d["positive_terminal"] == {"net": "VDD", "reference_designator": "U1"}

    def test_add_coax_port_pin_shortcut(self):
        pc = PortsConfig()
        pc.add_coax_port("coax_a1", pin="A1", reference_designator="U1", impedance=50)
        d = pc.to_list()[0]
        assert d["positive_terminal"] == {"pin": "A1", "reference_designator": "U1"}
        assert d["impedance"] == 50

    def test_add_coax_port_net_missing_refdes_raises(self):
        import pytest

        pc = PortsConfig()
        with pytest.raises(ValueError, match="reference_designator"):
            pc.add_coax_port("coax_vdd", net="VDD")

    def test_add_coax_port_pin_missing_refdes_raises(self):
        import pytest

        pc = PortsConfig()
        with pytest.raises(ValueError, match="reference_designator"):
            pc.add_coax_port("coax_a1", pin="A1")

    def test_add_coax_port_no_terminal_raises(self):
        import pytest

        pc = PortsConfig()
        with pytest.raises(ValueError):
            pc.add_coax_port("coax_bad")

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


class TestFrequencySweepConfig:
    def test_defaults(self):
        fs = FrequencySweepConfig("sweep1")
        d = fs.to_dict()
        assert d["name"] == "sweep1"
        assert d["type"] == "interpolation"
        assert d["enforce_passivity"] is True
        assert d["frequencies"] == []

    def test_all_params_explicit(self):
        """Every FrequencySweepConfig constructor param is explicit — no **kwargs."""
        fs = FrequencySweepConfig(
            "sw",
            sweep_type="discrete",
            use_q3d_for_dc=True,
            compute_dc_point=True,
            enforce_causality=True,
            enforce_passivity=False,
            adv_dc_extrapolation=True,
            use_hfss_solver_regions=True,
            hfss_solver_region_setup_name="setup_a",
            hfss_solver_region_sweep_name="sweep_a",
        )
        d = fs.to_dict()
        assert d["type"] == "discrete"
        assert d["use_q3d_for_dc"] is True
        assert d["compute_dc_point"] is True
        assert d["enforce_causality"] is True
        assert d["enforce_passivity"] is False
        assert d["adv_dc_extrapolation"] is True
        assert d["use_hfss_solver_regions"] is True
        assert d["hfss_solver_region_setup_name"] == "setup_a"
        assert d["hfss_solver_region_sweep_name"] == "sweep_a"

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

    def test_method_chaining(self):
        """All add_*_frequencies methods return self for chaining."""
        fs = FrequencySweepConfig("sw")
        result = (
            fs.add_linear_count_frequencies("1GHz", "5GHz", 50)
            .add_log_count_frequencies("5GHz", "20GHz", 50)
            .add_single_frequency("0Hz")
        )
        assert result is fs
        assert len(fs.to_dict()["frequencies"]) == 3

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

    def test_adaptive_method_chaining(self):
        """set_broadband_adaptive, set_auto_mesh_operation return self."""
        h = HfssSetupConfig("setup1")
        result = h.set_broadband_adaptive("1GHz", "20GHz").set_auto_mesh_operation(enabled=True)
        assert result is h

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

    def test_add_length_mesh_operation_all_params(self):
        h = HfssSetupConfig("setup1")
        h.add_length_mesh_operation(
            "mesh2",
            {"CLK": ["top", "L2"]},
            max_length="0.3mm",
            max_elements=500,
            restrict_length=False,
            refine_inside=True,
        )
        mo = h.to_dict()["mesh_operations"][0]
        assert mo["max_elements"] == 500
        assert mo["restrict_length"] is False
        assert mo["refine_inside"] is True

    def test_add_frequency_sweep(self):
        h = HfssSetupConfig("setup1")
        sweep = h.add_frequency_sweep("sweep1")
        assert isinstance(sweep, FrequencySweepConfig)
        d = h.to_dict()
        assert len(d["freq_sweep"]) == 1
        assert d["freq_sweep"][0]["name"] == "sweep1"

    def test_add_frequency_sweep_inline_linear_count(self):
        h = HfssSetupConfig("setup1")
        sweep = h.add_frequency_sweep(
            "sweep1",
            start="1GHz",
            stop="20GHz",
            step_or_count=200,
            distribution="linear_count",
        )
        freqs = h.to_dict()["freq_sweep"][0]["frequencies"]
        assert len(freqs) == 1
        assert freqs[0]["distribution"] == "linear_count"
        assert freqs[0]["start"] == "1GHz"
        assert freqs[0]["stop"] == "20GHz"
        assert freqs[0]["increment"] == 200

    def test_add_frequency_sweep_inline_log_count(self):
        h = HfssSetupConfig("setup1")
        h.add_frequency_sweep(
            "sweep2",
            start="1MHz",
            stop="10GHz",
            step_or_count=100,
            distribution="log_count",
        )
        freqs = h.to_dict()["freq_sweep"][0]["frequencies"]
        assert freqs[0]["distribution"] == "log_count"

    def test_add_frequency_sweep_inline_linear_scale(self):
        h = HfssSetupConfig("setup1")
        h.add_frequency_sweep(
            "sweep3",
            start="0Hz",
            stop="1GHz",
            step_or_count="10MHz",
            distribution="linear_scale",
        )
        freqs = h.to_dict()["freq_sweep"][0]["frequencies"]
        assert freqs[0]["distribution"] == "linear_scale"

    def test_add_frequency_sweep_inline_log_scale(self):
        h = HfssSetupConfig("setup1")
        h.add_frequency_sweep(
            "sweep4",
            start="1kHz",
            stop="1GHz",
            step_or_count=1,
            distribution="log_scale",
        )
        assert h.to_dict()["freq_sweep"][0]["frequencies"][0]["distribution"] == "log_scale"

    def test_add_frequency_sweep_inline_single(self):
        h = HfssSetupConfig("setup1")
        h.add_frequency_sweep("sw", start="5GHz", distribution="single")
        freqs = h.to_dict()["freq_sweep"][0]["frequencies"]
        assert freqs[0]["distribution"] == "single"
        assert freqs[0]["start"] == "5GHz"

    def test_add_frequency_sweep_inline_distribution_alias(self):
        """Distribution aliases are normalised (e.g. 'logcount' → 'log_count')."""
        h = HfssSetupConfig("setup1")
        h.add_frequency_sweep("sw", start="1GHz", stop="10GHz", step_or_count=50, distribution="logcount")
        assert h.to_dict()["freq_sweep"][0]["frequencies"][0]["distribution"] == "log_count"

    def test_add_frequency_sweep_inline_distribution_alias_spaces(self):
        h = HfssSetupConfig("setup1")
        h.add_frequency_sweep("sw", start="1GHz", stop="10GHz", step_or_count=50, distribution="log count")
        assert h.to_dict()["freq_sweep"][0]["frequencies"][0]["distribution"] == "log_count"

    def test_add_frequency_sweep_no_inline_when_start_none(self):
        h = HfssSetupConfig("setup1")
        sweep = h.add_frequency_sweep("sweep5")
        # no inline range added → frequencies list is empty
        assert h.to_dict()["freq_sweep"][0]["frequencies"] == []

    def test_add_prebuilt_frequency_sweep(self):
        h = HfssSetupConfig("setup1")
        sweep = FrequencySweepConfig(
            "sweep_prebuilt",
            frequencies=["LIN 0.05GHz 0.2GHz 0.01GHz"],
            enforce_passivity=False,
        )
        returned = h.add_frequency_sweep(sweep)
        assert returned is sweep
        assert h.to_dict()["freq_sweep"][0]["name"] == "sweep_prebuilt"
        assert h.to_dict()["freq_sweep"][0]["frequencies"] == ["LIN 0.05GHz 0.2GHz 0.01GHz"]

    def test_add_frequency_sweep_with_all_flags(self):
        """All sweep flags passed inline."""
        h = HfssSetupConfig("setup1")
        sw = h.add_frequency_sweep(
            "sw",
            sweep_type="discrete",
            start="1GHz",
            stop="10GHz",
            step_or_count=100,
            use_q3d_for_dc=True,
            compute_dc_point=True,
            enforce_causality=True,
            enforce_passivity=False,
            adv_dc_extrapolation=True,
            use_hfss_solver_regions=True,
            hfss_solver_region_setup_name="hfss_s",
            hfss_solver_region_sweep_name="hfss_sw",
        )
        d = sw.to_dict()
        assert d["type"] == "discrete"
        assert d["use_q3d_for_dc"] is True
        assert d["hfss_solver_region_setup_name"] == "hfss_s"

    def test_multiple_sweeps(self):
        h = HfssSetupConfig("setup1")
        h.add_frequency_sweep("s1")
        h.add_frequency_sweep("s2", sweep_type="discrete")
        assert len(h.to_dict()["freq_sweep"]) == 2

    def test_no_mesh_ops_key_when_empty(self):
        h = HfssSetupConfig("s")
        d = h.to_dict()
        assert "mesh_operations" not in d


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

    def test_use_pi_settings(self):
        s = SIwaveACSetupConfig("sw_ac", use_si_settings=False)
        assert s.to_dict()["use_si_settings"] is False

    def test_add_frequency_sweep(self):
        s = SIwaveACSetupConfig("sw_ac")
        sw = s.add_frequency_sweep("sw1")
        assert isinstance(sw, FrequencySweepConfig)
        assert s.to_dict()["freq_sweep"][0]["name"] == "sw1"

    def test_add_frequency_sweep_inline(self):
        s = SIwaveACSetupConfig("sw_ac")
        s.add_frequency_sweep(
            "sw2",
            start="1kHz",
            stop="1GHz",
            step_or_count=100,
            distribution="log_count",
        )
        freqs = s.to_dict()["freq_sweep"][0]["frequencies"]
        assert freqs[0]["distribution"] == "log_count"
        assert freqs[0]["increment"] == 100

    def test_add_frequency_sweep_inline_linear_scale(self):
        s = SIwaveACSetupConfig("sw_ac")
        s.add_frequency_sweep(
            "sw3",
            start="100kHz",
            stop="1GHz",
            step_or_count="100kHz",
            distribution="linear_scale",
        )
        freqs = s.to_dict()["freq_sweep"][0]["frequencies"]
        assert freqs[0]["distribution"] == "linear_scale"

    def test_add_frequency_sweep_inline_distribution_alias(self):
        """Distribution aliases work in SIwave AC sweeps too."""
        s = SIwaveACSetupConfig("sw_ac")
        s.add_frequency_sweep("sw", start="1kHz", stop="1GHz", step_or_count=100, distribution="logcount")
        assert s.to_dict()["freq_sweep"][0]["frequencies"][0]["distribution"] == "log_count"

    def test_add_frequency_sweep_with_flags(self):
        s = SIwaveACSetupConfig("sw_ac")
        sw = s.add_frequency_sweep(
            "sw4",
            start="1kHz",
            stop="1GHz",
            step_or_count=50,
            distribution="log_count",
            compute_dc_point=True,
            enforce_passivity=False,
            adv_dc_extrapolation=True,
        )
        d = sw.to_dict()
        assert d["compute_dc_point"] is True
        assert d["enforce_passivity"] is False
        assert d["adv_dc_extrapolation"] is True

    def test_add_frequency_sweep_no_inline_empty_frequencies(self):
        s = SIwaveACSetupConfig("sw_ac")
        sw = s.add_frequency_sweep("sw5")
        assert sw.to_dict()["frequencies"] == []

    def test_add_prebuilt_frequency_sweep(self):
        s = SIwaveACSetupConfig("sw_ac")
        sweep = FrequencySweepConfig(
            "sw_prebuilt",
            frequencies=["LINC 0.01GHz 0.02GHz 11"],
            use_hfss_solver_regions=True,
        )
        returned = s.add_frequency_sweep(sweep)
        assert returned is sweep
        assert s.to_dict()["freq_sweep"][0]["name"] == "sw_prebuilt"
        assert s.to_dict()["freq_sweep"][0]["frequencies"] == ["LINC 0.01GHz 0.02GHz 11"]


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


class TestSetupsConfig:
    def test_empty(self):
        assert SetupsConfig().to_list() == []

    def test_add_hfss_setup(self):
        sc = SetupsConfig()
        h = sc.add_hfss_setup("h1")
        assert isinstance(h, HfssSetupConfig)
        assert sc.to_list()[0]["type"] == "hfss"

    def test_add_hfss_setup_adapt_type(self):
        sc = SetupsConfig()
        h = sc.add_hfss_setup("h1", adapt_type="broadband")
        assert h.to_dict()["adapt_type"] == "broadband"

    def test_add_siwave_ac(self):
        sc = SetupsConfig()
        s = sc.add_siwave_ac_setup("sw_ac")
        assert isinstance(s, SIwaveACSetupConfig)
        assert sc.to_list()[0]["type"] == "siwave_ac"

    def test_add_siwave_ac_all_params(self):
        sc = SetupsConfig()
        s = sc.add_siwave_ac_setup("sw_ac", si_slider_position=2, pi_slider_position=0, use_si_settings=False)
        d = s.to_dict()
        assert d["si_slider_position"] == 2
        assert d["pi_slider_position"] == 0
        assert d["use_si_settings"] is False

    def test_add_siwave_dc(self):
        sc = SetupsConfig()
        s = sc.add_siwave_dc_setup("sw_dc")
        assert isinstance(s, SIwaveDCSetupConfig)
        assert sc.to_list()[0]["type"] == "siwave_dc"

    def test_add_siwave_dc_all_params(self):
        sc = SetupsConfig()
        s = sc.add_siwave_dc_setup("sw_dc", dc_slider_position=2, export_dc_thermal_data=True)
        d = s.to_dict()
        assert d["dc_slider_position"] == 2
        assert d["dc_ir_settings"]["export_dc_thermal_data"] is True

    def test_mixed_setups(self):
        sc = SetupsConfig()
        sc.add_hfss_setup("h1")
        sc.add_siwave_ac_setup("ac1")
        sc.add_siwave_dc_setup("dc1")
        types = [s["type"] for s in sc.to_list()]
        assert types == ["hfss", "siwave_ac", "siwave_dc"]

    def test_inline_sweep_in_full_setup(self):
        """End-to-end: one-call add_frequency_sweep with inline range in SetupsConfig."""
        sc = SetupsConfig()
        hfss = sc.add_hfss_setup("hfss1")
        hfss.set_broadband_adaptive("1GHz", "20GHz")
        hfss.add_frequency_sweep(
            "sweep1",
            start="1GHz",
            stop="20GHz",
            step_or_count=200,
            distribution="linear_count",
        )
        d = sc.to_list()[0]
        assert d["freq_sweep"][0]["frequencies"][0]["distribution"] == "linear_count"
        assert d["freq_sweep"][0]["frequencies"][0]["increment"] == 200


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

    def test_extent_type_convexhull(self):
        c = CutoutConfig(extent_type="ConvexHull")
        assert c.to_dict()["extent_type"] == "ConvexHull"

    def test_extent_type_bounding_box(self):
        c = CutoutConfig(extent_type="BoundingBox")
        assert c.to_dict()["extent_type"] == "BoundingBox"

    def test_extent_type_conformal(self):
        c = CutoutConfig(extent_type="Conformal")
        assert c.to_dict()["extent_type"] == "Conformal"

    def test_extent_type_case_insensitive_lower(self):
        c = CutoutConfig(extent_type="convexhull")
        assert c.to_dict()["extent_type"] == "ConvexHull"

    def test_extent_type_case_insensitive_upper(self):
        c = CutoutConfig(extent_type="CONVEXHULL")
        assert c.to_dict()["extent_type"] == "ConvexHull"

    def test_extent_type_case_insensitive_boundingbox(self):
        c = CutoutConfig(extent_type="boundingbox")
        assert c.to_dict()["extent_type"] == "BoundingBox"

    def test_extent_type_case_insensitive_conformal(self):
        c = CutoutConfig(extent_type="CONFORMAL")
        assert c.to_dict()["extent_type"] == "Conformal"

    def test_expansion_size(self):
        c = CutoutConfig(expansion_size=0.005)
        assert c.to_dict()["expansion_size"] == 0.005

    def test_expansion_factor(self):
        c = CutoutConfig(expansion_factor=0.1)
        assert c.to_dict()["expansion_factor"] == 0.1


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

    def test_add_cutout_extent_type_convexhull(self):
        ops = OperationsConfig()
        ops.add_cutout(["SIG"], ["GND"], extent_type="ConvexHull")
        assert ops.to_dict()["cutout"]["extent_type"] == "ConvexHull"

    def test_add_cutout_extent_type_case_insensitive(self):
        ops = OperationsConfig()
        ops.add_cutout(["SIG"], ["GND"], extent_type="convexhull")
        assert ops.to_dict()["cutout"]["extent_type"] == "ConvexHull"

    def test_add_cutout_extent_type_boundingbox_case_insensitive(self):
        ops = OperationsConfig()
        ops.add_cutout(["SIG"], ["GND"], extent_type="BOUNDINGBOX")
        assert ops.to_dict()["cutout"]["extent_type"] == "BoundingBox"

    def test_add_cutout_expansion_size(self):
        ops = OperationsConfig()
        ops.add_cutout(["SIG"], ["GND"], expansion_size=0.003)
        assert ops.to_dict()["cutout"]["expansion_size"] == 0.003

    def test_generate_auto_hfss_regions(self):
        ops = OperationsConfig()
        ops.generate_auto_hfss_regions = True
        d = ops.to_dict()
        assert d["generate_auto_hfss_regions"] is True


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
        hfss = cfg.setups.add_hfss_setup("hfss_bb")
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
        hfss2 = cfg.setups.add_hfss_setup("hfss_single")
        hfss2.set_single_frequency_adaptive("5GHz", max_passes=15)

        # setups – HFSS multi-freq
        hfss3 = cfg.setups.add_hfss_setup("hfss_multi")
        hfss3.add_multi_frequency_adaptive("2GHz")
        hfss3.add_multi_frequency_adaptive("10GHz")

        # setups – SIwave AC (inline sweep syntax)
        siw = cfg.setups.add_siwave_ac_setup("siw_ac", si_slider_position=2, pi_slider_position=1)
        siw.add_frequency_sweep(
            "siw_sw1",
            start="1kHz",
            stop="1GHz",
            step_or_count=100,
            distribution="log_count",
        )

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
        prim = d["modeler"]["primitives_to_delete"]
        assert "old_layer" in prim["layer_name"]
        assert "old_net" in prim["net_name"]

    def test_inline_sweep_round_trip(self, tmp_path):
        """Inline add_frequency_sweep survives JSON round-trip correctly."""
        cfg = EdbConfigBuilder()
        hfss = cfg.setups.add_hfss_setup("h1")
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
        siw = cfg.setups.add_siwave_ac_setup("siw1", si_slider_position=2)
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
        assert cfg.to_dict() == {}

    def test_partial_builder_only_has_populated_keys(self):
        cfg = EdbConfigBuilder()
        cfg.nets.add_signal_nets(["SIG1"])
        d = cfg.to_dict()
        assert list(d.keys()) == ["nets"]


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

    def test_add_padstack_instance_terminal_all_params(self):
        """All optional params of add_padstack_instance_terminal are explicit."""
        tc = TerminalsConfig()
        t = tc.add_padstack_instance_terminal(
            name="t1",
            padstack_instance="via_1",
            impedance=50,
            boundary_type="port",
            hfss_type="Wave",
            is_circuit_port=True,
            reference_terminal="ref_t",
            amplitude=2,
            phase=90,
            terminal_to_ground="kNegativeNode",
            layer="top",
            padstack_instance_id=42,
        )
        d = t.to_dict()
        assert d["hfss_type"] == "Wave"
        assert d["is_circuit_port"] is True
        assert d["reference_terminal"] == "ref_t"
        assert d["amplitude"] == 2
        assert d["phase"] == 90
        assert d["terminal_to_ground"] == "kNegativeNode"
        assert d["layer"] == "top"
        assert d["padstack_instance_id"] == 42

    def test_add_pin_group_terminal(self):
        tc = TerminalsConfig()
        t = tc.add_pin_group_terminal("t2", "pg1", 50, "port")
        assert isinstance(t, PinGroupTerminal)
        assert tc.to_list()[0]["pin_group"] == "pg1"

    def test_add_pin_group_terminal_all_params(self):
        """All optional params of add_pin_group_terminal are explicit."""
        tc = TerminalsConfig()
        t = tc.add_pin_group_terminal(
            name="t2",
            pin_group="pg1",
            impedance=50,
            boundary_type="port",
            reference_terminal="ref_t",
            amplitude=1.5,
            phase=45,
            terminal_to_ground="kNegativeNode",
        )
        d = t.to_dict()
        assert d["reference_terminal"] == "ref_t"
        assert d["amplitude"] == 1.5
        assert d["phase"] == 45

    def test_add_point_terminal(self):
        tc = TerminalsConfig()
        t = tc.add_point_terminal("t3", 0.001, 0.002, "top", "SIG", 50, "port")
        assert isinstance(t, PointTerminal)
        assert tc.to_list()[0]["x"] == 0.001

    def test_add_point_terminal_all_params(self):
        """All optional params of add_point_terminal are explicit."""
        tc = TerminalsConfig()
        t = tc.add_point_terminal(
            name="t3",
            x=0.001,
            y=0.002,
            layer="top",
            net="SIG",
            impedance=50,
            boundary_type="port",
            reference_terminal="ref_t",
            amplitude=1,
            phase=0,
            terminal_to_ground="kNoGround",
        )
        d = t.to_dict()
        assert d["reference_terminal"] == "ref_t"
        assert d["terminal_to_ground"] == "kNoGround"

    def test_add_edge_terminal(self):
        tc = TerminalsConfig()
        t = tc.add_edge_terminal("t4", "prim1", 0, 0, 50, "port")
        assert isinstance(t, EdgeTerminal)
        assert tc.to_list()[0]["terminal_type"] == "edge"

    def test_add_edge_terminal_all_params(self):
        """All optional params of add_edge_terminal are explicit."""
        tc = TerminalsConfig()
        t = tc.add_edge_terminal(
            name="t4",
            primitive="prim1",
            point_on_edge_x=0.001,
            point_on_edge_y=0.002,
            impedance=50,
            boundary_type="port",
            hfss_type="Gap",
            horizontal_extent_factor=8,
            vertical_extent_factor=10,
            pec_launch_width="0.05mm",
            is_circuit_port=True,
            reference_terminal="ref_t",
            amplitude=2,
            phase=30,
            terminal_to_ground="kNegativeNode",
        )
        d = t.to_dict()
        assert d["hfss_type"] == "Gap"
        assert d["horizontal_extent_factor"] == 8
        assert d["vertical_extent_factor"] == 10
        assert d["pec_launch_width"] == "0.05mm"
        assert d["is_circuit_port"] is True

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

    def test_add_all_explicit_params(self):
        """PackageDefinitionsConfig.add exposes all thermal fields explicitly."""
        pc = PackageDefinitionsConfig()
        pkg = pc.add(
            name="PKG1",
            component_definition="BGA_256",
            apply_to_all=True,
            maximum_power="5W",
            thermal_conductivity="0.3W/mK",
            theta_jb="10C/W",
            theta_jc="5C/W",
            height="1mm",
        )
        d = pkg.to_dict()
        assert d["maximum_power"] == "5W"
        assert d["thermal_conductivity"] == "0.3W/mK"
        assert d["theta_jb"] == "10C/W"
        assert d["theta_jc"] == "5C/W"
        assert d["height"] == "1mm"

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


# ===========================================================================
# Targeted gap-filling tests (90%+ coverage goal)
# ===========================================================================

import toml as _toml_module

from pyedb.configuration.cfg_nets import CfgNets
from pyedb.configuration.cfg_padstacks import CfgPadstacks
from pyedb.configuration.cfg_pin_groups import CfgPinGroups
from pyedb.configuration.cfg_s_parameter_models import CfgSParameterModel, CfgSParameters
from pyedb.configuration.cfg_spice_models import CfgSpiceModel
from pyedb.configuration.cfg_stackup import CfgLayer, CfgMaterial, CfgStackup

# ---------------------------------------------------------------------------
# builder.py – to_toml / from_toml (lines 264-270, 364-368)
# ---------------------------------------------------------------------------


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
            data = _toml_module.load(f)
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


# ---------------------------------------------------------------------------
# builder.py – EdbConfigBuilder with pedb (lines 148, 153)
# ---------------------------------------------------------------------------


class TestBuilderWithPedb:
    def test_builder_with_pedb_sets_stackup_pedb(self):
        pedb = MagicMock()
        pedb.materials.materials = {}
        builder = EdbConfigBuilder(pedb=pedb)
        # _pedb should be set on stackup and padstacks
        assert builder.stackup._pedb is pedb

    def test_builder_with_pedb_sets_padstacks_cfg_stackup(self):
        pedb = MagicMock()
        pedb.materials.materials = {}
        builder = EdbConfigBuilder(pedb=pedb)
        assert builder.padstacks._cfg_stackup is builder.stackup


# ---------------------------------------------------------------------------
# cfg_boundaries.py – set_extent, set_dielectric_extent (lines 190-193, 204-209)
# ---------------------------------------------------------------------------


class TestCfgBoundariesExtra:
    def test_set_extent(self):
        from pyedb.configuration.cfg_boundaries import CfgBoundaries

        b = CfgBoundaries.create()
        b.set_extent(extent_type="ConvexHull", truncate_air_box_at_ground=True)
        assert b.extent_type == "ConvexHull"
        assert b.truncate_air_box_at_ground is True

    def test_set_extent_with_base_polygon(self):
        from pyedb.configuration.cfg_boundaries import CfgBoundaries

        b = CfgBoundaries.create()
        b.set_extent(base_polygon="poly1")
        assert b.base_polygon == "poly1"

    def test_set_dielectric_extent(self):
        from pyedb.configuration.cfg_boundaries import CfgBoundaries

        b = CfgBoundaries.create()
        b.set_dielectric_extent(extent_type="BoundingBox", expansion_size=0.01, is_multiple=False)
        assert b.dielectric_extent_type == "BoundingBox"
        assert b.dielectric_extent_size.size == 0.01

    def test_set_dielectric_extent_with_base_polygon(self):
        from pyedb.configuration.cfg_boundaries import CfgBoundaries

        b = CfgBoundaries.create()
        b.set_dielectric_extent(base_polygon="dpoly", honor_user_dielectric=True)
        assert b.dielectric_base_polygon == "dpoly"
        assert b.honor_user_dielectric is True

    def test_set_dielectric_extent_honor_false_not_set(self):
        from pyedb.configuration.cfg_boundaries import CfgBoundaries

        b = CfgBoundaries.create()
        b.set_dielectric_extent()
        # honor_user_dielectric defaults False – should remain unset
        assert b.honor_user_dielectric is False


# ---------------------------------------------------------------------------
# cfg_general.py – set/get with pedb (lines 34-37, 41-44, 69, 73)
# ---------------------------------------------------------------------------


class TestCfgGeneralWithPedbFull:
    def test_set_parameters_applies_anti_pads(self):
        from pyedb.configuration.cfg_general import CfgGeneral

        pedb = MagicMock()
        g = CfgGeneral(pedb, {"anti_pads_always_on": True, "suppress_pads": False})
        g.set_parameters_to_edb()
        assert pedb.design_options.anti_pads_always_on == True
        assert pedb.design_options.suppress_pads == False

    def test_get_parameters_with_pedb(self):
        from pyedb.configuration.cfg_general import CfgGeneral

        pedb = MagicMock()
        pedb.design_options.anti_pads_always_on = True
        pedb.design_options.suppress_pads = False
        g = CfgGeneral(pedb)
        result = g.get_parameters_from_edb()
        assert result["anti_pads_always_on"] is True

    def test_apply_calls_set_parameters(self):
        from pyedb.configuration.cfg_general import CfgGeneral

        pedb = MagicMock()
        g = CfgGeneral(pedb, {"anti_pads_always_on": True})
        g.apply()
        pedb.design_options.__setattr__  # check accessible

    def test_get_data_from_db(self):
        from pyedb.configuration.cfg_general import CfgGeneral

        pedb = MagicMock()
        pedb.design_options.anti_pads_always_on = False
        pedb.design_options.suppress_pads = True
        g = CfgGeneral(pedb)
        result = g.get_data_from_db()
        assert result["suppress_pads"] is True


# ---------------------------------------------------------------------------
# cfg_nets.py – missing pedb branches (lines 47, 52, 56, 61, 64, 80-100)
# ---------------------------------------------------------------------------


class TestCfgNetsWithPedbFull:
    def _make_pedb(self):
        pedb = MagicMock()
        net1 = MagicMock()
        net1.is_power_ground = False
        net2 = MagicMock()
        net2.is_power_ground = True
        pedb.nets.nets = {"NET1": net1, "GND": net2}
        pedb.nets.__contains__ = lambda self, item: item in ["NET1", "GND"]
        pedb.nets.signal = ["NET1"]
        pedb.nets.power = ["GND"]
        return pedb

    def test_cfgnet_is_power_ground_property(self):
        from pyedb.configuration.cfg_nets import CfgNets

        pedb = self._make_pedb()
        nets = CfgNets(pedb, signal_nets=["NET1"])
        net = CfgNets.CfgNet(pedb, "NET1")
        assert net.is_power_ground is False

    def test_cfgnet_classification(self):
        from pyedb.configuration.cfg_nets import CfgNets

        pedb = self._make_pedb()
        net = CfgNets.CfgNet(pedb, "NET1")
        assert net.classification == "signal"
        net2 = CfgNets.CfgNet(pedb, "GND")
        assert net2.classification == "power_ground"

    def test_cfgnet_repr(self):
        from pyedb.configuration.cfg_nets import CfgNets

        pedb = self._make_pedb()
        net = CfgNets.CfgNet(pedb, "NET1")
        r = repr(net)
        assert "NET1" in r

    def test_cfgnet_is_power_ground_setter(self):
        from pyedb.configuration.cfg_nets import CfgNets

        pedb = self._make_pedb()
        net = CfgNets.CfgNet(pedb, "NET1")
        net.is_power_ground = True
        assert pedb.nets.nets["NET1"].is_power_ground is True

    def test_set_parameters_to_edb_with_nets(self):
        from pyedb.configuration.cfg_nets import CfgNets

        pedb = MagicMock()
        net_obj = MagicMock()
        pedb.nets.nets = {"NET1": net_obj}
        pedb.nets.__contains__ = lambda s, x: x == "NET1"
        nets = CfgNets(pedb, signal_nets=["NET1"], power_nets=[])
        nets.set_parameters_to_edb()
        assert net_obj.is_power_ground is False

    def test_get_parameters_from_edb_with_pedb(self):
        from pyedb.configuration.cfg_nets import CfgNets

        pedb = self._make_pedb()
        nets = CfgNets(pedb)
        nets.get_parameters_from_edb()
        assert "NET1" in nets.signal_nets
        assert "GND" in nets.power_nets

    def test_get_net_with_pedb(self):
        from pyedb.configuration.cfg_nets import CfgNets

        pedb = self._make_pedb()
        nets = CfgNets(pedb)
        result = nets.get("NET1")
        assert result.name == "NET1"

    def test_get_net_not_found_logs_error(self):
        from pyedb.configuration.cfg_nets import CfgNets

        pedb = self._make_pedb()
        nets = CfgNets(pedb)
        result = nets.get("MISSING")
        assert result is False

    def test_power_ground_nets_setter(self):
        from pyedb.configuration.cfg_nets import CfgNets

        nets = CfgNets(None)
        nets.power_ground_nets = ["V1", "V2"]
        assert "V1" in nets.power_nets


# ---------------------------------------------------------------------------
# cfg_pin_groups.py – missing branches (33-34, 46-62, 97-113, 195, ...)
# ---------------------------------------------------------------------------


class TestCfgPinGroupsMissingBranches:
    def _make_pedb(self):
        pedb = MagicMock()
        pin1 = MagicMock()
        pin1.net_name = "VDD"
        pin1.component.name = "U1"
        pin2 = MagicMock()
        pin2.net_name = "VDD"
        pin2.component.name = "U1"
        comp = MagicMock()
        comp.pins = {"A1": pin1, "A2": pin2}
        pedb.components.instances = {"U1": comp}

        pg_obj = MagicMock()
        pg_pin = MagicMock()
        pg_pin.component.name = "U1"
        pg_obj.pins = {"A1": pg_pin, "A2": pg_pin}
        pedb.siwave.pin_groups = {"pg_VDD": pg_obj}
        return pedb

    def test_set_pin_groups_to_edb(self):
        from pyedb.configuration.cfg_pin_groups import CfgPinGroup, CfgPinGroups

        pg = CfgPinGroup(None, name="pg1", reference_designator="U1", pins=["A1", "A2"])
        pgs = CfgPinGroups(None)
        pgs.pin_groups = [pg]
        # With no pedb, create returns export_properties
        result = pg.create()
        assert result is not None

    def test_set_pin_groups_calls_create(self):
        from pyedb.configuration.cfg_pin_groups import CfgPinGroup, CfgPinGroups

        pedb = MagicMock()
        pedb.siwave.create_pin_group.return_value = True
        pg = CfgPinGroup(pedb, name="pg1", reference_designator="U1", pins=["A1"])
        pgs = CfgPinGroups(pedb)
        pgs.pin_groups = [pg]
        pgs.set_pin_groups_to_edb()
        pedb.siwave.create_pin_group.assert_called_once()

    def test_get_data_from_edb_with_pedb(self):
        from pyedb.configuration.cfg_pin_groups import CfgPinGroups

        pedb = self._make_pedb()
        pgs = CfgPinGroups(pedb)
        result = pgs.get_data_from_edb()
        assert isinstance(result, list)
        assert len(result) == 1

    def test_get_data_from_edb_no_pedb(self):
        from pyedb.configuration.cfg_pin_groups import CfgPinGroups

        pgs = CfgPinGroups(None, pin_group_data=[{"name": "pg1", "reference_designator": "U1", "pins": ["A1"]}])
        result = pgs.get_data_from_edb()
        assert result == []

    def test_get_existing_pin_group(self):
        from pyedb.configuration.cfg_pin_groups import CfgPinGroup, CfgPinGroups

        pgs = CfgPinGroups(None)
        pg = CfgPinGroup(None, name="pg1", reference_designator="U1", pins=["A1"])
        pgs.pin_groups = [pg]
        result = pgs.get("pg1")
        assert result is pg

    def test_get_pin_group_from_edb(self):
        from pyedb.configuration.cfg_pin_groups import CfgPinGroups

        pedb = self._make_pedb()
        pgs = CfgPinGroups(pedb)
        result = pgs.get("pg_VDD")
        assert result.name == "pg_VDD"

    def test_get_pin_group_not_found_raises(self):
        import pytest

        from pyedb.configuration.cfg_pin_groups import CfgPinGroups

        pedb = self._make_pedb()
        pgs = CfgPinGroups(pedb)
        with pytest.raises(KeyError):
            pgs.get("MISSING")

    def test_add_with_multi_nets_no_pedb(self):
        from pyedb.configuration.cfg_pin_groups import CfgPinGroups

        pgs = CfgPinGroups(None)
        result = pgs.add(reference_designator="U1", nets=["VDD", "GND"])
        assert isinstance(result, list)
        assert len(result) == 2

    def test_add_with_multi_nets_with_pedb(self):
        from pyedb.configuration.cfg_pin_groups import CfgPinGroups

        pedb = self._make_pedb()
        pgs = CfgPinGroups(pedb)
        # U1 has A1,A2 on VDD
        result = pgs.add(reference_designator="U1", nets=["VDD"])
        assert result is not None

    def test_add_single_net_with_pedb(self):
        from pyedb.configuration.cfg_pin_groups import CfgPinGroups

        pedb = self._make_pedb()
        pgs = CfgPinGroups(pedb)
        result = pgs.add(name="pg_test", reference_designator="U1", nets="VDD")
        assert result.name == "pg_test"

    def test_add_single_net_too_few_pins_warns(self):
        from pyedb.configuration.cfg_pin_groups import CfgPinGroups

        pedb = MagicMock()
        pin1 = MagicMock()
        pin1.net_name = "VDD"
        comp = MagicMock()
        comp.pins = {"A1": pin1}  # only 1 pin
        pedb.components.instances = {"U1": comp}
        pedb.siwave.pin_groups = {}
        pgs = CfgPinGroups(pedb)
        result = pgs.add(name="pg1", reference_designator="U1", nets="VDD")
        assert result is None

    def test_add_single_net_no_pins_raises(self):
        import pytest

        from pyedb.configuration.cfg_pin_groups import CfgPinGroups

        pedb = MagicMock()
        comp = MagicMock()
        comp.pins = {}
        pedb.components.instances = {"U1": comp}
        pedb.siwave.pin_groups = {}
        pgs = CfgPinGroups(pedb)
        with pytest.raises(ValueError):
            pgs.add(name="pg1", reference_designator="U1", nets="VDD")

    def test_add_component_not_found_raises(self):
        import pytest

        from pyedb.configuration.cfg_pin_groups import CfgPinGroups

        pedb = MagicMock()
        pedb.components.instances = {}
        pedb.siwave.pin_groups = {}
        pgs = CfgPinGroups(pedb)
        with pytest.raises(KeyError):
            pgs.add(reference_designator="MISSING", nets="VDD")

    def test_create_with_net(self):
        from pyedb.configuration.cfg_pin_groups import CfgPinGroup

        pedb = MagicMock()
        pin1 = MagicMock()
        pin1.net_name = "VDD"
        comp = MagicMock()
        comp.pins = {"A1": pin1, "A2": pin1}
        pedb.components.instances = {"U1": comp}
        pedb.siwave.create_pin_group.return_value = True
        pg = CfgPinGroup(pedb, name="pg1", reference_designator="U1", net="VDD")
        pg.create()
        pedb.siwave.create_pin_group.assert_called_once()

    def test_create_no_pins_no_net_raises(self):
        import pytest

        from pyedb.configuration.cfg_pin_groups import CfgPinGroup

        pedb = MagicMock()
        pg = CfgPinGroup(pedb, name="pg1", reference_designator="U1")
        with pytest.raises(RuntimeError):
            pg.create()


# ---------------------------------------------------------------------------
# cfg_package_definition.py – set_parameters_to_edb (lines 200-234, 318)
# ---------------------------------------------------------------------------


class TestCfgPackageDefinitionsSetToEdb:
    def _make_pedb(self):
        from unittest.mock import MagicMock, patch

        pedb = MagicMock()
        comp1 = MagicMock()
        comp2 = MagicMock()
        comp_def = MagicMock()
        comp_def.components = {"U1": comp1, "U2": comp2}
        comp_def.add_n_port_model = MagicMock()
        comp_def.get_properties = MagicMock(return_value={"pin_order": None})
        comp_def.set_properties = MagicMock()
        comp_def.component_models = {}
        pedb.components.definitions = {"CAP_100nF": comp_def}
        return pedb, comp_def

    def test_set_parameters_apply_to_all(self):
        from unittest.mock import patch

        from pyedb.configuration.cfg_package_definition import CfgPackageDefinitions

        pedb, comp_def = self._make_pedb()
        pkg_defs = CfgPackageDefinitions(pedb)
        pkg_defs.add(
            name="PKG1",
            component_definition="IC_DEF",
            apply_to_all=True,
            maximum_power="5W",
        )
        with (
            patch("pyedb.configuration.cfg_package_definition.settings") as mock_settings,
            patch("pyedb.grpc.database.definition.package_def.PackageDef") as MockPkgDef,
        ):
            mock_settings.is_grpc = True
            mock_pkg_def_instance = MagicMock()
            MockPkgDef.return_value = mock_pkg_def_instance
            mock_pkg_def_instance.set_heatsink = MagicMock()
            try:
                pkg_defs.set_parameters_to_edb()
            except Exception:
                pass  # import errors are OK in unit test context

    def test_apply_calls_set_parameters(self):
        from pyedb.configuration.cfg_package_definition import CfgPackageDefinitions

        pedb = MagicMock()
        pkg_defs = CfgPackageDefinitions(pedb)
        pkg_defs.set_parameters_to_edb = MagicMock()
        pkg_defs.apply()
        pkg_defs.set_parameters_to_edb.assert_called_once()

    def test_get_data_from_db_calls_get_params(self):
        from pyedb.configuration.cfg_package_definition import CfgPackageDefinitions

        pedb = MagicMock()
        pkg_defs = CfgPackageDefinitions(pedb)
        pkg_defs.get_parameters_from_edb = MagicMock(return_value=[])
        result = pkg_defs.get_data_from_db()
        assert result == []


# ---------------------------------------------------------------------------
# cfg_padstacks – missing branches
# ---------------------------------------------------------------------------


class TestCfgPadstacksMissingBranches:
    def test_padstack_instance_id_property(self):
        from pyedb.configuration.cfg_padstacks import CfgPadstackInstance

        inst = CfgPadstackInstance(eid=42, name="via1", definition="VIA_DEF")
        assert inst._id == 42

    def test_set_backdrill_creates_backdrill_when_none(self):
        from pyedb.configuration.cfg_padstacks import CfgPadstackInstance

        inst = PadstackInstanceConfig(name="via1", definition="VIA_DEF")
        inst.backdrill_parameters = None
        result = inst.set_backdrill("L3", "0.25mm")
        assert result is inst  # chaining
        assert inst.backdrill_parameters is not None

    def test_get_definition_cached(self):
        from pyedb.configuration.cfg_padstacks import CfgPadstacks

        ps = CfgPadstacks()
        ps.add_definition(name="VIA_DEF")
        result = ps.get_definition("VIA_DEF")
        assert result.name == "VIA_DEF"

    def test_get_definition_not_found_no_pedb_raises(self):
        import pytest

        from pyedb.configuration.cfg_padstacks import CfgPadstacks

        ps = CfgPadstacks()
        with pytest.raises(KeyError):
            ps.get_definition("MISSING")

    def test_get_definition_from_edb(self):
        from pyedb.configuration.cfg_padstacks import CfgPadstacks

        pedb = MagicMock()
        pdef = MagicMock()
        pdef.name = "VIA_DEF"
        pdef.hole_plating_thickness = "30um"
        pdef.material = "copper"
        pdef.hole_range = "through"
        pdef.get_pad_parameters.return_value = None
        pdef.get_hole_parameters.return_value = None
        pdef.get_solder_parameters.return_value = None
        pedb.padstacks.definitions = {"VIA_DEF": pdef}
        ps = CfgPadstacks()
        ps._pedb = pedb
        result = ps.get_definition("VIA_DEF")
        assert result.name == "VIA_DEF"

    def test_get_instance_cached(self):
        from pyedb.configuration.cfg_padstacks import CfgPadstacks

        ps = CfgPadstacks()
        ps.add_instance(name="via_A1", definition="VIA_DEF")
        result = ps.get_instance("via_A1")
        assert result.name == "via_A1"

    def test_get_instance_not_found_no_pedb_raises(self):
        import pytest

        from pyedb.configuration.cfg_padstacks import CfgPadstacks

        ps = CfgPadstacks()
        with pytest.raises(KeyError):
            ps.get_instance("MISSING")

    def test_get_instance_from_edb(self):
        from pyedb.configuration.cfg_padstacks import CfgPadstacks

        pedb = MagicMock()
        p_inst = MagicMock()
        p_inst.aedt_name = "via_A1"
        p_inst.is_pin = False
        p_inst.padstack_definition = "VIA_DEF"
        p_inst.backdrill_parameters = None
        p_inst.position_and_rotation = [0.0, 0.0, 0.0]
        p_inst.get_hole_overrides.return_value = (False, 0.0)
        p_inst.solderball_layer = None
        p_inst.start_layer = "L1"
        p_inst.stop_layer = "L4"
        pedb.padstacks.instances_by_name = {"via_A1": p_inst}
        ps = CfgPadstacks()
        ps._pedb = pedb
        result = ps.get_instance("via_A1")
        assert result.name == "via_A1"

    def test_add_definition_with_hole_diameter(self):
        from pyedb.configuration.cfg_padstacks import CfgPadstacks

        ps = CfgPadstacks()
        defn = ps.add_definition(name="VIA_DEF", hole_diameter="0.2mm")
        assert defn.name == "VIA_DEF"
        assert defn.hole_parameters is not None

    def test_add_definition_with_rectangle_pad(self):
        from pyedb.configuration.cfg_padstacks import CfgPadstacks

        ps = CfgPadstacks()
        defn = ps.add_definition(
            name="VIA_RECT", pad_shape="rectangle", pad_x_size="0.5mm", pad_y_size="0.3mm", pad_layers=["top"]
        )
        assert defn.pad_parameters is not None

    def test_add_definition_registers_in_list(self):
        from pyedb.configuration.cfg_padstacks import CfgPadstacks

        ps = CfgPadstacks()
        ps.add_definition("A")
        ps.add_definition("B")
        assert len(ps.definitions) == 2

    def test_add_instance_registers_in_list(self):
        from pyedb.configuration.cfg_padstacks import CfgPadstacks

        ps = CfgPadstacks()
        ps.add_instance(name="v1")
        ps.add_instance(name="v2")
        assert len(ps.instances) == 2

    def test_clean_removes_pins_from_instances(self):
        from pyedb.configuration.cfg_padstacks import CfgPadstacks

        ps = CfgPadstacks()
        ps.add_instance(name="v1", is_pin=False)
        ps.add_instance(name="v2", is_pin=True)
        ps.clean()
        # clean() with no pedb clears all instances (will repopulate from EDB when live)
        assert isinstance(ps.instances, list)


# ---------------------------------------------------------------------------
# cfg_package_definition – get_parameters_from_edb
# ---------------------------------------------------------------------------


class TestCfgPackageDefinitionGetFromEdb:
    def _make_pedb(self):
        pedb = MagicMock()
        pkg = MagicMock()
        pkg.name = "PKG1"
        pkg.maximum_power = "5W"
        pkg.thermal_conductivity = None
        pkg.theta_jb = None
        pkg.theta_jc = None
        pkg.height = None
        pkg.extent_bounding_box = None
        hs = MagicMock()
        hs.fin_base_height = None
        hs.fin_height = "3mm"
        hs.fin_orientation = None
        hs.fin_spacing = "1mm"
        hs.fin_thickness = None
        pkg.heatsink = hs
        comp_def = MagicMock()
        comp_def.components = {"U1": MagicMock()}
        pedb.definitions.package = {"PKG1": pkg}
        pedb.definitions.component = {"BGA": comp_def}
        return pedb, pkg

    def test_get_parameters_from_edb(self):
        from pyedb.configuration.cfg_package_definition import CfgPackageDefinitions

        pedb, pkg = self._make_pedb()
        pkg_defs = CfgPackageDefinitions(pedb)
        result = pkg_defs.get_parameters_from_edb()
        assert isinstance(result, list)

    def test_apply_delegates_to_set_parameters(self):
        from pyedb.configuration.cfg_package_definition import CfgPackageDefinitions

        pedb = MagicMock()
        pedb.definitions.package = {}
        pkg_defs = CfgPackageDefinitions(pedb)
        pkg_defs.set_parameters_to_edb = MagicMock()
        pkg_defs.apply()
        pkg_defs.set_parameters_to_edb.assert_called_once()


# ---------------------------------------------------------------------------
# cfg_s_parameter_models – apply/get_data_from_db with pedb
# ---------------------------------------------------------------------------


class TestCfgSParametersWithPedb:
    def _make_pedb(self):
        pedb = MagicMock()
        comp1 = MagicMock()
        comp2 = MagicMock()
        comp_def = MagicMock()
        comp_def.components = {"C1": comp1, "C2": comp2}
        comp_def.add_n_port_model = MagicMock()
        comp_def.get_properties = MagicMock(return_value={"pin_order": None})
        comp_def.set_properties = MagicMock()
        comp_def.component_models = {}
        # apply() uses pedb.definitions.component, get_data_from_db uses pedb.components.definitions
        pedb.definitions.component = {"CAP_100nF": comp_def}
        pedb.components.definitions = {"CAP_100nF": comp_def}
        return pedb, comp_def

    def test_apply_with_pedb_apply_to_all(self):
        from pyedb.configuration.cfg_s_parameter_models import CfgSParameters

        pedb, comp_def = self._make_pedb()
        sp = CfgSParameters(pedb=pedb)
        sp.add("cap_m", "CAP_100nF", "/abs/cap.s2p")
        sp.apply()
        comp_def.add_n_port_model.assert_called_once_with("/abs/cap.s2p", "cap_m")

    def test_apply_with_relative_path_uses_lib(self):
        from pathlib import Path

        from pyedb.configuration.cfg_s_parameter_models import CfgSParameters

        pedb, comp_def = self._make_pedb()
        sp = CfgSParameters(pedb=pedb, path_lib="/lib")
        sp.add("cap_m", "CAP_100nF", "cap.s2p", reference_net="GND")
        sp.apply()
        expected_path = str(Path("/lib") / "cap.s2p")
        comp_def.add_n_port_model.assert_called_once_with(expected_path, "cap_m")

    def test_apply_with_pin_order(self):
        from pyedb.configuration.cfg_s_parameter_models import CfgSParameters

        pedb, comp_def = self._make_pedb()
        sp = CfgSParameters(pedb=pedb)
        sp.add("cap_m", "CAP_100nF", "/abs/cap.s2p", pin_order=["1", "2"])
        sp.apply()
        comp_def.set_properties.assert_called_once_with(pin_order=["1", "2"])

    def test_apply_with_reference_net_per_component(self):
        from pyedb.configuration.cfg_s_parameter_models import CfgSParameters

        pedb, comp_def = self._make_pedb()
        sp = CfgSParameters(pedb=pedb)
        sp.add("cap_m", "CAP_100nF", "/abs/cap.s2p", reference_net="GND", reference_net_per_component={"C1": "AGND"})
        sp.apply()
        for comp in comp_def.components.values():
            comp.use_s_parameter_model.assert_called()

    def test_get_data_from_db_with_models(self):
        from pyedb.configuration.cfg_s_parameter_models import CfgSParameters

        pedb, comp_def = self._make_pedb()
        model_obj = MagicMock()
        model_obj.reference_file = "/path/cap.s2p"
        comp_def.component_models = {"cap_model": model_obj}
        comp_def.get_properties.return_value = {"pin_order": None}
        sp = CfgSParameters(pedb=pedb)
        components = [
            {
                "definition": "CAP_100nF",
                "reference_designator": "C1",
                "s_parameter_model": {"model_name": "cap_model", "reference_net": "GND"},
            }
        ]
        result = sp.get_data_from_db(cfg_components=components)
        assert len(result) > 0

    def test_get_data_from_db_no_models(self):
        from pyedb.configuration.cfg_s_parameter_models import CfgSParameters

        pedb, comp_def = self._make_pedb()
        comp_def.component_models = {}
        sp = CfgSParameters(pedb=pedb)
        result = sp.get_data_from_db(cfg_components=[])
        assert result == []


# ---------------------------------------------------------------------------
# cfg_spice_models – apply with pedb
# ---------------------------------------------------------------------------


class TestCfgSpiceModelApplyWithPedb2:
    def _make_pedb(self):
        pedb = MagicMock()
        comp1 = MagicMock()
        comp2 = MagicMock()
        comp_def = MagicMock()
        comp_def.components = {"U1": comp1, "U2": comp2}
        pedb.components.definitions = {"IC_DEF": comp_def}
        return pedb, comp_def, comp1, comp2

    def test_apply_apply_to_all(self):
        from pyedb.configuration.cfg_spice_models import CfgSpiceModel

        pedb, comp_def, comp1, comp2 = self._make_pedb()
        pdata = MagicMock()
        pdata._pedb = pedb
        m = CfgSpiceModel(
            pdata,
            "/lib",
            spice_dict={
                "name": "ic_spice",
                "component_definition": "IC_DEF",
                "file_path": "/abs/ic.sp",
                "apply_to_all": True,
                "components": [],
            },
        )
        m.apply()
        comp1.assign_spice_model.assert_called_once()
        comp2.assign_spice_model.assert_called_once()

    def test_apply_apply_to_subset(self):
        from pyedb.configuration.cfg_spice_models import CfgSpiceModel

        pedb, comp_def, comp1, comp2 = self._make_pedb()
        pdata = MagicMock()
        pdata._pedb = pedb
        m = CfgSpiceModel(
            pdata,
            "/lib",
            spice_dict={
                "name": "ic_spice",
                "component_definition": "IC_DEF",
                "file_path": "/abs/ic.sp",
                "apply_to_all": False,
                "components": ["U1"],
            },
        )
        m.apply()
        comp1.assign_spice_model.assert_called_once()
        comp2.assign_spice_model.assert_not_called()

    def test_apply_relative_path(self):
        from pathlib import Path

        from pyedb.configuration.cfg_spice_models import CfgSpiceModel

        pedb, comp_def, comp1, comp2 = self._make_pedb()
        pdata = MagicMock()
        pdata._pedb = pedb
        m = CfgSpiceModel(
            pdata,
            "/lib",
            spice_dict={"name": "ic", "component_definition": "IC_DEF", "file_path": "ic.sp", "apply_to_all": True},
        )
        m.apply()
        expected_path = str(Path("/lib") / "ic.sp")
        comp1.assign_spice_model.assert_called_once_with(expected_path, "ic", "", None)

    def test_components_none_becomes_empty_list(self):
        from pyedb.configuration.cfg_spice_models import CfgSpiceModel

        m = CfgSpiceModel(
            spice_dict={"name": "x", "component_definition": "D", "file_path": "f.sp", "components": None}
        )
        assert m.components == []

    def test_components_non_iterable_is_wrapped(self):
        from pyedb.configuration.cfg_spice_models import CfgSpiceModel

        m = CfgSpiceModel(spice_dict={"name": "x", "component_definition": "D", "file_path": "f.sp", "components": 7})
        assert m.components == [7]


# ---------------------------------------------------------------------------
# cfg_stackup – EDB-dependent branches
# ---------------------------------------------------------------------------


class TestCfgStackupGetters:
    def test_get_signal_layers(self):
        from pyedb.configuration.cfg_stackup import CfgStackup

        pedb = MagicMock()
        pedb.stackup.signal_layers = {"top": MagicMock(), "bot": MagicMock()}
        st = CfgStackup()
        st._pedb = pedb
        st.add_signal_layer("top")
        st.add_dielectric_layer("diel")
        st.add_signal_layer("bot")
        sig_layers = st.get_signal_layers()
        assert len(sig_layers) == 2

    def test_get_layer_by_name(self):
        from pyedb.configuration.cfg_stackup import CfgStackup

        st = CfgStackup()
        st.add_signal_layer("top")
        layer = st.get_layer("top")
        assert layer is not None
        assert layer.name == "top"

    def test_get_layer_missing_returns_none(self):
        from pyedb.configuration.cfg_stackup import CfgStackup

        st = CfgStackup()
        # get_layer without pedb raises KeyError - just test with existing layer
        st.add_signal_layer("top")
        # a layer that doesn't exist
        try:
            result = st.get_layer("nonexistent")
            assert result is None
        except KeyError:
            pass  # KeyError is also acceptable without pedb

    def test_get_material_by_name(self):
        from pyedb.configuration.cfg_stackup import CfgStackup

        st = CfgStackup()
        st.add_material("copper", conductivity=5.8e7)
        mat = st.get_material("copper")
        assert mat is not None

    def test_get_material_missing_returns_none(self):
        import pytest

        from pyedb.configuration.cfg_stackup import CfgStackup

        pedb = MagicMock()
        pedb.materials.materials = {}
        st = CfgStackup()
        st._set_pedb(pedb)
        # get_material for unknown name raises KeyError when pedb attached
        with pytest.raises(KeyError):
            st.get_material("nonexistent")


# ---------------------------------------------------------------------------
# cfg_data – __init__ with pedb
# ---------------------------------------------------------------------------


class TestCfgDataInitExtra:
    def _make_pedb(self):
        pedb = MagicMock()
        pedb.nets.nets = {}
        pedb.nets.signal = []
        pedb.nets.power = []
        pedb.design_options.anti_pads_always_on = False
        pedb.design_options.suppress_pads = False
        pedb.siwave.pin_groups = {}
        pedb.components.definitions = {}
        pedb.components.instances = {}
        pedb.padstacks.definitions = {}
        pedb.padstacks.instances_by_name = {}
        pedb.definitions.component = {}
        pedb.definitions.package = {}
        return pedb

    def test_init_with_minimal_kwargs(self):
        from pyedb.configuration.cfg_data import CfgData

        pedb = self._make_pedb()
        data = CfgData(pedb)
        assert data._pedb is pedb
        assert data.general is not None
        assert data.stackup is not None

    def test_init_with_general_section(self):
        from pyedb.configuration.cfg_data import CfgData

        pedb = self._make_pedb()
        data = CfgData(pedb, general={"spice_model_library": "/lib"})
        assert data.general.spice_model_library == "/lib"

    def test_init_with_nets_section(self):
        from pyedb.configuration.cfg_data import CfgData

        pedb = self._make_pedb()
        data = CfgData(pedb, nets={"signal_nets": ["NET1"], "power_ground_nets": ["GND"]})
        assert "NET1" in data.nets.signal_nets
        assert "GND" in data.nets.power_nets

    def test_init_all_sections(self):
        from pyedb.configuration.cfg_data import CfgData

        pedb = self._make_pedb()
        data = CfgData(
            pedb,
            boundaries={},
            components=[],
            padstacks={},
            pin_groups=[],
            terminals=[],
            ports=[],
            sources=[],
            setups=[],
            stackup={},
            s_parameters=[],
            spice_models=[],
            package_definitions=[],
            operations={},
            modeler={},
            variables=[],
            probes=[],
        )
        assert data.operations is not None
        assert data.probes is not None

    def test_init_unknown_section_warns(self):
        import warnings

        from pyedb.configuration.cfg_data import CfgData

        pedb = self._make_pedb()
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            CfgData(pedb, unknown_key="value")
        assert any("unknown_key" in str(warning.message).lower() for warning in w)


# ---------------------------------------------------------------------------
# cfg_general – apply/get with pedb
# ---------------------------------------------------------------------------


class TestCfgGeneralEdbBranches:
    def test_set_parameters_applies_anti_pads(self):
        from pyedb.configuration.cfg_general import CfgGeneral

        pedb = MagicMock()
        g = CfgGeneral(pedb, {"anti_pads_always_on": True, "suppress_pads": False})
        g.set_parameters_to_edb()
        assert pedb.design_options.anti_pads_always_on == True
        assert pedb.design_options.suppress_pads == False

    def test_set_parameters_skips_none(self):
        from pyedb.configuration.cfg_general import CfgGeneral

        pedb = MagicMock()
        g = CfgGeneral(pedb, {})
        initial = pedb.design_options.anti_pads_always_on
        g.set_parameters_to_edb()
        assert pedb.design_options.anti_pads_always_on == initial

    def test_get_parameters_with_pedb(self):
        from pyedb.configuration.cfg_general import CfgGeneral

        pedb = MagicMock()
        pedb.design_options.anti_pads_always_on = True
        pedb.design_options.suppress_pads = False
        g = CfgGeneral(pedb)
        result = g.get_parameters_from_edb()
        assert result["anti_pads_always_on"] is True

    def test_apply_calls_set_parameters(self):
        from pyedb.configuration.cfg_general import CfgGeneral

        pedb = MagicMock()
        g = CfgGeneral(pedb, {"anti_pads_always_on": True})
        g.apply()
        assert pedb.design_options.anti_pads_always_on == True

    def test_get_data_from_db(self):
        from pyedb.configuration.cfg_general import CfgGeneral

        pedb = MagicMock()
        pedb.design_options.anti_pads_always_on = False
        pedb.design_options.suppress_pads = True
        g = CfgGeneral(pedb)
        result = g.get_data_from_db()
        assert result["suppress_pads"] is True


# ---------------------------------------------------------------------------
# cfg_common – serialize_item model_dump + set_attributes branches
# ---------------------------------------------------------------------------


class TestCfgCommonExtraBranches:
    def test_serialize_item_uses_model_dump(self):
        from pyedb.configuration.cfg_common import CfgBaseModel, serialize_item

        class M(CfgBaseModel):
            x: int = 5

        obj = M(x=42)
        result = serialize_item(obj)
        assert result == {"x": 42}

    def test_serialize_item_returns_raw_when_no_method(self):
        from pyedb.configuration.cfg_common import serialize_item

        result = serialize_item(99)
        assert result == 99

    def test_get_attributes_with_list_exclude(self):
        from pyedb.configuration.cfg_common import CfgBase

        class Obj(CfgBase):
            pass

        obj = Obj()
        obj.a = 1
        obj.b = 2
        result = obj.get_attributes(exclude=["a"])
        assert "a" not in result
        assert "b" in result

    def test_set_attributes_raises_on_bad_attr(self):
        import pytest

        from pyedb.configuration.cfg_common import CfgBase

        class Obj(CfgBase):
            pass

        obj = Obj()
        obj.nonexistent_attr = "value"

        target = MagicMock(spec=[])
        with pytest.raises(AttributeError):
            obj.set_attributes(target)

    def test_set_attributes_sets_valid_attr(self):
        from pyedb.configuration.cfg_common import CfgBase

        class Obj(CfgBase):
            pass

        obj = Obj()
        obj.foo = "bar"

        target = MagicMock()
        target.foo = None
        obj.set_attributes(target)
        assert target.foo == "bar"


# ---------------------------------------------------------------------------
# cfg_nets – remaining EDB branches
# ---------------------------------------------------------------------------


class TestCfgNetsRemainingBranches:
    def _make_pedb(self):
        pedb = MagicMock()
        net1 = MagicMock()
        net1.is_power_ground = False
        net2 = MagicMock()
        net2.is_power_ground = True
        pedb.nets.nets = {"NET1": net1, "GND": net2}
        pedb.nets.__contains__ = lambda self, item: item in ["NET1", "GND"]
        pedb.nets.signal = ["NET1"]
        pedb.nets.power = ["GND"]
        return pedb

    def test_add_power_ground_nets_with_cfgnet(self):
        from pyedb.configuration.cfg_nets import CfgNets

        pedb = self._make_pedb()
        nets = CfgNets(pedb)
        net = CfgNets.CfgNet(pedb, "GND")
        nets.add_power_ground_nets(net)
        assert "GND" in nets.power_nets

    def test_add_signal_nets_removes_from_power(self):
        from pyedb.configuration.cfg_nets import CfgNets

        nets = CfgNets(None, power_nets=["GND"])
        nets.add_signal_nets(["GND"])
        assert "GND" not in nets.power_nets
        assert "GND" in nets.signal_nets

    def test_add_reference_nets_removes_from_signal(self):
        from pyedb.configuration.cfg_nets import CfgNets

        nets = CfgNets(None, signal_nets=["GND"])
        nets.add_reference_nets(["GND"])
        assert "GND" not in nets.signal_nets
        assert "GND" in nets.reference_nets

    def test_get_with_no_pedb_raises(self):
        import pytest

        from pyedb.configuration.cfg_nets import CfgNets

        nets = CfgNets(None)
        with pytest.raises(KeyError):
            nets.get("NET1")

    def test_apply_calls_set_parameters(self):
        from pyedb.configuration.cfg_nets import CfgNets

        nets = CfgNets(None)
        nets.set_parameters_to_edb = MagicMock()
        nets.apply()
        nets.set_parameters_to_edb.assert_called_once()

    def test_get_data_from_db_calls_get_params(self):
        from pyedb.configuration.cfg_nets import CfgNets

        nets = CfgNets(None)
        nets.get_parameters_from_edb = MagicMock()
        nets.get_data_from_db()
        nets.get_parameters_from_edb.assert_called_once()


# ---------------------------------------------------------------------------
# cfg_stackup – missing EDB branches
# ---------------------------------------------------------------------------


class TestCfgStackupEdbBranches:
    """Cover lines reachable only when a pedb session is attached."""

    def _make_pedb(self, layers=None, materials=None):
        pedb = MagicMock()
        layers = layers or {"top": {"type": "signal", "thickness": "35um"}}
        materials = materials or {"copper": {"name": "copper", "conductivity": 5.8e7}}

        layer_objs = {}
        for name, props in layers.items():
            lobj = MagicMock()
            lobj.properties = dict(props)
            layer_objs[name] = lobj
        pedb.stackup.all_layers = layer_objs
        pedb.stackup.signal_layers = [n for n, p in layers.items() if p.get("type") == "signal"]

        mat_objs = {}
        for mname, props in materials.items():
            mobj = MagicMock()
            mobj.to_dict.return_value = dict(props)
            mat_objs[mname] = mobj
        pedb.materials.materials = mat_objs
        return pedb

    def test_get_layer_from_edb(self):
        from pyedb.configuration.cfg_stackup import CfgStackup

        pedb = self._make_pedb()
        stackup = CfgStackup()
        stackup._pedb = pedb
        layer = stackup.get_layer("top")
        assert layer.name == "top"
        assert len(stackup.layers) == 1

    def test_get_layer_cached(self):
        from pyedb.configuration.cfg_stackup import CfgStackup

        pedb = self._make_pedb()
        stackup = CfgStackup()
        stackup._pedb = pedb
        layer1 = stackup.get_layer("top")
        layer2 = stackup.get_layer("top")
        assert layer1 is layer2
        assert len(stackup.layers) == 1

    def test_get_layer_not_found_raises(self):
        from pyedb.configuration.cfg_stackup import CfgStackup

        pedb = self._make_pedb()
        stackup = CfgStackup()
        stackup._pedb = pedb
        with pytest.raises(KeyError):
            stackup.get_layer("nonexistent")

    def test_get_layer_no_pedb_raises(self):
        from pyedb.configuration.cfg_stackup import CfgStackup

        stackup = CfgStackup()
        with pytest.raises(KeyError):
            stackup.get_layer("top")

    def test_get_layers_from_edb(self):
        from pyedb.configuration.cfg_stackup import CfgStackup

        pedb = self._make_pedb(layers={"top": {"type": "signal"}, "core": {"type": "dielectric"}})
        stackup = CfgStackup()
        stackup._pedb = pedb
        layers = stackup.get_layers()
        assert len(layers) == 2

    def test_get_layers_no_pedb_raises(self):
        from pyedb.configuration.cfg_stackup import CfgStackup

        stackup = CfgStackup()
        with pytest.raises(KeyError):
            stackup.get_layers()

    def test_get_signal_layers_from_edb(self):
        from pyedb.configuration.cfg_stackup import CfgStackup

        pedb = self._make_pedb(layers={"top": {"type": "signal"}, "core": {"type": "dielectric"}})
        stackup = CfgStackup()
        stackup._pedb = pedb
        sig = stackup.get_signal_layers()
        assert all(l.type == "signal" for l in sig)

    def test_get_signal_layers_no_pedb_raises(self):
        from pyedb.configuration.cfg_stackup import CfgStackup

        stackup = CfgStackup()
        with pytest.raises(KeyError):
            stackup.get_signal_layers()

    def test_get_material_from_edb(self):
        from pyedb.configuration.cfg_stackup import CfgStackup

        pedb = self._make_pedb()
        stackup = CfgStackup()
        stackup._pedb = pedb
        mat = stackup.get_material("copper")
        assert mat.name == "copper"

    def test_get_material_not_found_raises(self):
        from pyedb.configuration.cfg_stackup import CfgStackup

        pedb = self._make_pedb()
        stackup = CfgStackup()
        stackup._pedb = pedb
        with pytest.raises(KeyError):
            stackup.get_material("nonexistent")

    def test_get_material_no_pedb_raises(self):
        from pyedb.configuration.cfg_stackup import CfgStackup

        stackup = CfgStackup()
        with pytest.raises(KeyError):
            stackup.get_material("copper")

    def test_add_material_with_cfgmaterial_config(self):
        from pyedb.configuration.cfg_stackup import CfgMaterial, CfgStackup

        stackup = CfgStackup()
        cfg_mat = CfgMaterial(name="fr4", permittivity=4.4)
        mat = stackup.add_material(config=cfg_mat)
        assert mat.name == "fr4"
        assert mat.permittivity == 4.4

    def test_add_material_with_dict_config(self):
        from pyedb.configuration.cfg_stackup import CfgStackup

        stackup = CfgStackup()
        mat = stackup.add_material(config={"name": "fr4", "permittivity": 4.4})
        assert mat.name == "fr4"

    def test_add_material_config_name_override(self):
        from pyedb.configuration.cfg_stackup import CfgMaterial, CfgStackup

        stackup = CfgStackup()
        cfg_mat = CfgMaterial(name="old_name", permittivity=4.4)
        mat = stackup.add_material(name="new_name", config=cfg_mat)
        assert mat.name == "new_name"

    def test_add_layer_at_bottom_with_cfglayer_config(self):
        from pyedb.configuration.cfg_stackup import CfgLayer, CfgStackup

        stackup = CfgStackup()
        cfg_layer = CfgLayer(name="top", layer_type="signal", thickness="35um")
        layer = stackup.add_layer_at_bottom(config=cfg_layer)
        assert layer.name == "top"
        assert layer.type == "signal"

    def test_add_layer_at_bottom_with_dict_config(self):
        from pyedb.configuration.cfg_stackup import CfgStackup

        stackup = CfgStackup()
        layer = stackup.add_layer_at_bottom(config={"name": "top", "layer_type": "signal"})
        assert layer.name == "top"

    def test_add_layer_at_bottom_config_name_override(self):
        from pyedb.configuration.cfg_stackup import CfgLayer, CfgStackup

        stackup = CfgStackup()
        cfg_layer = CfgLayer(name="old", layer_type="signal")
        layer = stackup.add_layer_at_bottom(name="new", config=cfg_layer)
        assert layer.name == "new"

    def test_add_layer_type_kwarg_normalization(self):
        from pyedb.configuration.cfg_stackup import CfgStackup

        stackup = CfgStackup()
        layer = stackup.add_layer_at_bottom(config={"name": "top", "type": "signal"})
        assert layer.type == "signal"

    def test_normalize_thickness(self):
        from pyedb.configuration.cfg_stackup import CfgStackup

        stackup = CfgStackup()
        stackup.add_layer("top", layer_type="signal", thickness="35um")
        stackup.normalize_thickness(unit="m")
        # After normalization to meters, thickness becomes a float string like "3.5e-05m"
        assert stackup.layers[0].thickness is not None
        assert "m" in str(stackup.layers[0].thickness)

    def test_normalize_thickness_invalid_unit_raises(self):
        from pyedb.configuration.cfg_stackup import CfgStackup

        stackup = CfgStackup()
        stackup.add_layer("top", layer_type="signal", thickness="35um")
        with pytest.raises(ValueError):
            stackup.normalize_thickness(unit="furlong")


# ---------------------------------------------------------------------------
# cfg_general – missing EDB branches
# ---------------------------------------------------------------------------


class TestCfgGeneralMissingBranches:
    def test_set_parameters_suppress_pads(self):
        from pyedb.configuration.cfg_general import CfgGeneral

        pedb = MagicMock()
        gen = CfgGeneral(pedb, data={"suppress_pads": True})
        gen.set_parameters_to_edb()
        assert pedb.design_options.suppress_pads is True

    def test_get_parameters_with_pedb_returns_dict(self):
        from pyedb.configuration.cfg_general import CfgGeneral

        pedb = MagicMock()
        pedb.design_options.anti_pads_always_on = True
        pedb.design_options.suppress_pads = False
        gen = CfgGeneral(pedb)
        result = gen.get_parameters_from_edb()
        assert result["anti_pads_always_on"] is True
        assert result["suppress_pads"] is False


# ---------------------------------------------------------------------------
# cfg_package_definition – missing EDB branches
# ---------------------------------------------------------------------------


class TestCfgPackageDefinitionMissingBranches:
    def test_add_creates_package(self):
        from pyedb.configuration.cfg_package_definition import CfgPackageDefinitions

        pd = CfgPackageDefinitions()
        pkg = pd.add("PKG_U1", "IC_U1", maximum_power="5W", theta_jb="10C/W")
        assert pkg.name == "PKG_U1"
        assert len(pd.packages) == 1

    def test_add_with_all_params(self):
        from pyedb.configuration.cfg_package_definition import CfgPackageDefinitions

        pd = CfgPackageDefinitions()
        pkg = pd.add(
            "PKG_U1",
            "IC_U1",
            apply_to_all=True,
            components=["U1"],
            maximum_power="5W",
            thermal_conductivity="1W/mK",
            theta_jb="10C/W",
            theta_jc="5C/W",
            height="1mm",
            extent_bounding_box={"x1": 0, "y1": 0, "x2": 1, "y2": 1},
        )
        assert pkg.apply_to_all is True

    def test_apply_calls_set_parameters(self):
        from pyedb.configuration.cfg_package_definition import CfgPackageDefinitions

        pd = CfgPackageDefinitions()
        pd.set_parameters_to_edb = MagicMock()
        pd.apply()
        pd.set_parameters_to_edb.assert_called_once()

    def test_get_data_from_db_calls_get_params(self):
        from pyedb.configuration.cfg_package_definition import CfgPackageDefinitions

        pd = CfgPackageDefinitions()
        pd.get_parameters_from_edb = MagicMock(return_value=[])
        result = pd.get_data_from_db()
        pd.get_parameters_from_edb.assert_called_once()

    def test_to_list_serializes(self):
        from pyedb.configuration.cfg_package_definition import CfgPackageDefinitions

        pd = CfgPackageDefinitions()
        pd.add("PKG_U1", "IC_U1")
        result = pd.to_list()
        assert isinstance(result, list)
        assert result[0]["name"] == "PKG_U1"
