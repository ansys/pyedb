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

import pytest

from pyedb.configuration.cfg_s_parameter_models import CfgSParameterModel, CfgSParameters
from pyedb.configuration.cfg_setup import (
    CfgHFSSSetup,
    CfgSetupAC,
    CfgSetups,
    CfgSIwaveACSetup,
    CfgSIwaveDCSetup,
)

pytestmark = [pytest.mark.unit, pytest.mark.no_licence, pytest.mark.legacy]

# alias so tests read naturally
FrequencySweep = CfgSetupAC.CfgFrequencySweep
FrequencySweepConfig = CfgSetupAC.CfgFrequencySweep
# Attach to_dict as a convenience method for standalone use in tests
if not hasattr(FrequencySweepConfig, "to_dict"):
    FrequencySweepConfig.to_dict = lambda self: self.model_dump()


class TestCfgSParameterModel:
    def test_basic(self):
        m = CfgSParameterModel(name="model1", component_definition="CAP_100nF", file_path="/path/c.s2p")
        assert m.name == "model1"
        assert m.component_definition == "CAP_100nF"
        assert m.file_path == "/path/c.s2p"

    def test_with_components(self):
        m = CfgSParameterModel(
            name="m1", component_definition="DEF", file_path="f.s2p", apply_to_all=False, components=["C1", "C2"]
        )
        assert m.apply_to_all is False
        assert m.components == ["C1", "C2"]

    def test_reference_net_per_component(self):
        m = CfgSParameterModel(
            name="m1", component_definition="DEF", file_path="f.s2p", reference_net_per_component={"C1": "GND1"}
        )
        assert m.reference_net_per_component == {"C1": "GND1"}

    def test_pin_order(self):
        m = CfgSParameterModel(name="m1", component_definition="DEF", file_path="f.s2p", pin_order=["1", "2"])
        assert m.pin_order == ["1", "2"]

    def test_pin_order_none_by_default(self):
        m = CfgSParameterModel(name="m1", component_definition="DEF", file_path="f.s2p")
        assert m.pin_order is None


class TestCfgSParameters:
    def test_empty(self):
        sc = CfgSParameters(pedb=None, data=[])
        assert sc.models == []

    def test_instantiation_with_data(self):
        sc = CfgSParameters(
            pedb=None,
            data=[{"name": "m1", "component_definition": "DEF", "file_path": "f.s2p"}],
        )
        assert len(sc.models) == 1
        assert sc.models[0].name == "m1"


class TestCfgHFSSSetup:
    def test_defaults(self):
        h = CfgHFSSSetup(name="setup1")
        d = h.model_dump()
        assert d["name"] == "setup1"
        assert d["type"] == "hfss"
        assert d["adapt_type"] == "single"

    def test_no_mesh_ops_key_when_empty(self):
        h = CfgHFSSSetup(name="s")
        d = h.model_dump(exclude_none=True, exclude_defaults=True)
        assert "mesh_operations" not in d

    def test_set_single_frequency_adaptive(self):
        h = CfgHFSSSetup(name="setup1")
        h.set_single_frequency_adaptive("5GHz", max_passes=15, max_delta=0.01)
        d = h.model_dump()
        assert d["adapt_type"] == "single"
        sfa = d["single_frequency_adaptive_solution"]
        assert sfa["adaptive_frequency"] == "5GHz"
        assert sfa["max_passes"] == 15
        assert sfa["max_delta"] == 0.01

    def test_set_broadband_adaptive(self):
        h = CfgHFSSSetup(name="setup1")
        h.set_broadband_adaptive("1GHz", "20GHz", max_passes=25)
        d = h.model_dump()
        assert d["adapt_type"] == "broadband"
        bba = d["broadband_adaptive_solution"]
        assert bba["low_frequency"] == "1GHz"
        assert bba["high_frequency"] == "20GHz"
        assert bba["max_passes"] == 25

    def test_add_multi_frequency_adaptive(self):
        h = CfgHFSSSetup(name="setup1")
        h.add_multi_frequency_adaptive("1GHz", max_passes=20, max_delta=0.02)
        h.add_multi_frequency_adaptive("10GHz")
        d = h.model_dump()
        assert d["adapt_type"] == "multi_frequencies"
        adapt = d["multi_frequency_adaptive_solution"]["adapt_frequencies"]
        assert len(adapt) == 2
        assert adapt[0]["adaptive_frequency"] == "1GHz"

    def test_adaptive_method_chaining(self):
        h = CfgHFSSSetup(name="setup1")
        result = h.set_broadband_adaptive("1GHz", "20GHz").set_auto_mesh_operation(enabled=True)
        assert result is h

    def test_set_auto_mesh_operation(self):
        h = CfgHFSSSetup(name="setup1")
        h.set_auto_mesh_operation(enabled=True, trace_ratio_seeding=4)
        d = h.model_dump()
        assert d["auto_mesh_operation"]["enabled"] is True
        assert d["auto_mesh_operation"]["trace_ratio_seeding"] == 4

    def test_add_length_mesh_operation(self):
        h = CfgHFSSSetup(name="setup1")
        h.add_length_mesh_operation("mesh1", {"SIG": ["top"]}, max_length="0.5mm")
        d = h.model_dump()
        assert len(d["mesh_operations"]) == 1
        assert d["mesh_operations"][0]["name"] == "mesh1"
        assert d["mesh_operations"][0]["max_length"] == "0.5mm"

    def test_add_length_mesh_operation_all_params(self):
        h = CfgHFSSSetup(name="setup1")
        h.add_length_mesh_operation(
            "mesh2",
            {"CLK": ["top", "L2"]},
            max_length="0.3mm",
            max_elements=500,
            restrict_length=False,
            refine_inside=True,
        )
        mo = h.model_dump()["mesh_operations"][0]
        assert mo["max_elements"] == 500
        assert mo["restrict_length"] is False
        assert mo["refine_inside"] is True

    def test_add_frequency_sweep(self):
        h = CfgHFSSSetup(name="setup1")
        sweep = h.add_frequency_sweep("sweep1")
        assert isinstance(sweep, FrequencySweep)
        d = h.model_dump()
        assert len(d["freq_sweep"]) == 1
        assert d["freq_sweep"][0]["name"] == "sweep1"

    def test_add_frequency_sweep_inline_linear_count(self):
        h = CfgHFSSSetup(name="setup1")
        h.add_frequency_sweep("sweep1", start="1GHz", stop="20GHz", step_or_count=200, distribution="linear_count")
        freqs = h.model_dump()["freq_sweep"][0]["frequencies"]
        assert len(freqs) == 1
        assert freqs[0]["distribution"] == "linear_count"
        assert freqs[0]["start"] == "1GHz"
        assert freqs[0]["stop"] == "20GHz"
        assert freqs[0]["increment"] == 200

    def test_add_frequency_sweep_inline_log_count(self):
        h = CfgHFSSSetup(name="setup1")
        h.add_frequency_sweep(name="sweep2", start="1MHz", stop="10GHz", step_or_count=100, distribution="log_count")
        freqs = h.model_dump()["freq_sweep"][0]["frequencies"]
        assert freqs[0]["distribution"] == "log_count"

    def test_add_frequency_sweep_inline_linear_scale(self):
        h = CfgHFSSSetup(name="setup1")
        h.add_frequency_sweep(
            name="sweep3", start="0Hz", stop="1GHz", step_or_count="10MHz", distribution="linear_scale"
        )
        freqs = h.model_dump()["freq_sweep"][0]["frequencies"]
        assert freqs[0]["distribution"] == "linear_scale"

    def test_add_frequency_sweep_inline_log_scale(self):
        h = CfgHFSSSetup(name="setup1")
        h.add_frequency_sweep(name="sweep4", start="1kHz", stop="1GHz", step_or_count=1, distribution="log_scale")
        assert h.model_dump()["freq_sweep"][0]["frequencies"][0]["distribution"] == "log_scale"

    def test_add_frequency_sweep_inline_single(self):
        h = CfgHFSSSetup(name="setup1")
        h.add_frequency_sweep("sw", start="5GHz", distribution="single")
        freqs = h.model_dump()["freq_sweep"][0]["frequencies"]
        assert freqs[0]["distribution"] == "single"
        assert freqs[0]["start"] == "5GHz"

    def test_add_frequency_sweep_inline_distribution_alias(self):
        h = CfgHFSSSetup(name="setup1")
        h.add_frequency_sweep("sw", start="1GHz", stop="10GHz", step_or_count=50, distribution="logcount")
        assert h.model_dump()["freq_sweep"][0]["frequencies"][0]["distribution"] == "log_count"

    def test_add_frequency_sweep_inline_distribution_alias_spaces(self):
        h = CfgHFSSSetup(name="setup1")
        h.add_frequency_sweep("sw", start="1GHz", stop="10GHz", step_or_count=50, distribution="log count")
        assert h.model_dump()["freq_sweep"][0]["frequencies"][0]["distribution"] == "log_count"

    def test_add_frequency_sweep_no_inline_when_start_none(self):
        h = CfgHFSSSetup(name="setup1")
        h.add_frequency_sweep("sweep5")
        assert h.model_dump()["freq_sweep"][0]["frequencies"] == []

    def test_add_prebuilt_frequency_sweep(self):
        h = CfgHFSSSetup(name="setup1")
        sweep = FrequencySweep(
            name="sweep_prebuilt",
            frequencies=["LIN 0.05GHz 0.2GHz 0.01GHz"],
            enforce_passivity=False,
        )
        returned = h.add_frequency_sweep(sweep)
        assert returned is sweep
        d = h.model_dump()
        assert d["freq_sweep"][0]["name"] == "sweep_prebuilt"
        assert d["freq_sweep"][0]["frequencies"] == ["LIN 0.05GHz 0.2GHz 0.01GHz"]

    def test_add_frequency_sweep_with_all_flags(self):
        h = CfgHFSSSetup(name="setup1")
        sw = h.add_frequency_sweep(
            name="sw",
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
        d = sw.model_dump()
        assert d["type"] == "discrete"
        assert d["use_q3d_for_dc"] is True
        assert d["hfss_solver_region_setup_name"] == "hfss_s"

    def test_multiple_sweeps(self):
        h = CfgHFSSSetup(name="setup1")
        h.add_frequency_sweep("s1")
        h.add_frequency_sweep("s2", sweep_type="discrete")
        assert len(h.model_dump()["freq_sweep"]) == 2


class TestCfgSIwaveACSetup:
    def test_defaults(self):
        s = CfgSIwaveACSetup(name="sw_ac")
        d = s.model_dump()
        assert d["type"] == "siwave_ac"
        assert d["si_slider_position"] == 1
        assert d["pi_slider_position"] == 1
        assert d["use_si_settings"] is True

    def test_custom_sliders(self):
        s = CfgSIwaveACSetup(name="sw_ac", si_slider_position=2, pi_slider_position=0)
        d = s.model_dump()
        assert d["si_slider_position"] == 2
        assert d["pi_slider_position"] == 0

    def test_use_pi_settings(self):
        s = CfgSIwaveACSetup(name="sw_ac", use_si_settings=False)
        assert s.model_dump()["use_si_settings"] is False

    def test_add_frequency_sweep(self):
        s = CfgSIwaveACSetup(name="sw_ac")
        sw = s.add_frequency_sweep("sw1")
        assert isinstance(sw, FrequencySweep)
        assert s.model_dump()["freq_sweep"][0]["name"] == "sw1"

    def test_add_frequency_sweep_inline(self):
        s = CfgSIwaveACSetup(name="sw_ac")
        s.add_frequency_sweep(name="sw2", start="1kHz", stop="1GHz", step_or_count=100, distribution="log_count")
        freqs = s.model_dump()["freq_sweep"][0]["frequencies"]
        assert freqs[0]["distribution"] == "log_count"
        assert freqs[0]["increment"] == 100

    def test_add_frequency_sweep_inline_linear_scale(self):
        s = CfgSIwaveACSetup(name="sw_ac")
        s.add_frequency_sweep(
            name="sw3", start="100kHz", stop="1GHz", step_or_count="100kHz", distribution="linear_scale"
        )
        freqs = s.model_dump()["freq_sweep"][0]["frequencies"]
        assert freqs[0]["distribution"] == "linear_scale"

    def test_add_frequency_sweep_inline_distribution_alias(self):
        s = CfgSIwaveACSetup(name="sw_ac")
        s.add_frequency_sweep("sw", start="1kHz", stop="1GHz", step_or_count=100, distribution="logcount")
        assert s.model_dump()["freq_sweep"][0]["frequencies"][0]["distribution"] == "log_count"

    def test_add_frequency_sweep_with_flags(self):
        s = CfgSIwaveACSetup(name="sw_ac")
        sw = s.add_frequency_sweep(
            name="sw4",
            start="1kHz",
            stop="1GHz",
            step_or_count=50,
            distribution="log_count",
            compute_dc_point=True,
            enforce_passivity=False,
            adv_dc_extrapolation=True,
        )
        d = sw.model_dump()
        assert d["compute_dc_point"] is True
        assert d["enforce_passivity"] is False
        assert d["adv_dc_extrapolation"] is True

    def test_add_frequency_sweep_no_inline_empty_frequencies(self):
        s = CfgSIwaveACSetup(name="sw_ac")
        sw = s.add_frequency_sweep("sw5")
        assert sw.model_dump()["frequencies"] == []

    def test_add_prebuilt_frequency_sweep(self):
        s = CfgSIwaveACSetup(name="sw_ac")
        sweep = FrequencySweep(
            name="sw_prebuilt",
            frequencies=["LINC 0.01GHz 0.02GHz 11"],
            use_hfss_solver_regions=True,
        )
        returned = s.add_frequency_sweep(sweep)
        assert returned is sweep
        assert s.model_dump()["freq_sweep"][0]["name"] == "sw_prebuilt"
        assert s.model_dump()["freq_sweep"][0]["frequencies"] == ["LINC 0.01GHz 0.02GHz 11"]


class TestCfgSIwaveDCSetup:
    def test_defaults(self):
        s = CfgSIwaveDCSetup(name="sw_dc")
        d = s.model_dump()
        assert d["type"] == "siwave_dc"
        assert d["dc_slider_position"] == 1
        assert d["dc_ir_settings"]["export_dc_thermal_data"] is False

    def test_custom(self):
        s = CfgSIwaveDCSetup(name="sw_dc", dc_slider_position=2, export_dc_thermal_data=True)
        d = s.model_dump()
        assert d["dc_slider_position"] == 2
        assert d["dc_ir_settings"]["export_dc_thermal_data"] is True


class TestCfgSetups:
    def test_empty(self):
        assert CfgSetups().setups == []

    def test_add_hfss_setup(self):
        sc = CfgSetups()
        h = sc.add_hfss_setup(name="h1")
        assert isinstance(h, CfgHFSSSetup)
        assert sc.setups[0].model_dump()["type"] == "hfss"

    def test_add_hfss_setup_adapt_type(self):
        sc = CfgSetups()
        h = sc.add_hfss_setup(name="h1", adapt_type="broadband")
        assert h.model_dump()["adapt_type"] == "broadband"

    def test_add_siwave_ac(self):
        sc = CfgSetups()
        s = sc.add_siwave_ac_setup(name="sw_ac")
        assert isinstance(s, CfgSIwaveACSetup)
        assert sc.setups[0].model_dump()["type"] == "siwave_ac"

    def test_add_siwave_ac_all_params(self):
        sc = CfgSetups()
        s = sc.add_siwave_ac_setup(name="sw_ac", si_slider_position=2, pi_slider_position=0, use_si_settings=False)
        d = s.model_dump()
        assert d["si_slider_position"] == 2
        assert d["pi_slider_position"] == 0
        assert d["use_si_settings"] is False

    def test_add_siwave_dc(self):
        sc = CfgSetups()
        s = sc.add_siwave_dc_setup(name="sw_dc")
        assert isinstance(s, CfgSIwaveDCSetup)
        assert sc.setups[0].model_dump()["type"] == "siwave_dc"

    def test_add_siwave_dc_all_params(self):
        sc = CfgSetups()
        s = sc.add_siwave_dc_setup(name="sw_dc", dc_slider_position=2, export_dc_thermal_data=True)
        d = s.model_dump()
        assert d["dc_slider_position"] == 2
        assert d["dc_ir_settings"]["export_dc_thermal_data"] is True

    def test_mixed_setups(self):
        sc = CfgSetups()
        sc.add_hfss_setup(name="h1")
        sc.add_siwave_ac_setup(name="ac1")
        sc.add_siwave_dc_setup(name="dc1")
        types = [s.model_dump()["type"] for s in sc.setups]
        assert types == ["hfss", "siwave_ac", "siwave_dc"]

    def test_inline_sweep_in_full_setup(self):
        sc = CfgSetups()
        hfss = sc.add_hfss_setup(name="hfss1")
        hfss.set_broadband_adaptive("1GHz", "20GHz")
        hfss.add_frequency_sweep(
            name="sweep1", start="1GHz", stop="20GHz", step_or_count=200, distribution="linear_count"
        )
        d = sc.setups[0].model_dump()
        assert d["freq_sweep"][0]["frequencies"][0]["distribution"] == "linear_count"
        assert d["freq_sweep"][0]["frequencies"][0]["increment"] == 200


class TestFrequencySweepConfig:
    def test_all_params_explicit(self):
        """Every FrequencySweepConfig constructor param is explicit — no **kwargs."""
        fs = FrequencySweepConfig(
            name="sw",
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
        fs = FrequencySweepConfig(name="sweep1")
        fs.add_linear_count_frequencies("1GHz", "10GHz", 100)
        freqs = fs.to_dict()["frequencies"]
        assert len(freqs) == 1
        assert freqs[0]["distribution"] == "linear_count"
        assert freqs[0]["increment"] == 100

    def test_log_count(self):
        fs = FrequencySweepConfig(name="sweep2")
        fs.add_log_count_frequencies("1MHz", "1GHz", 50)
        assert fs.to_dict()["frequencies"][0]["distribution"] == "log_count"

    def test_linear_scale(self):
        fs = FrequencySweepConfig(name="sweep3")
        fs.add_linear_scale_frequencies("0Hz", "1GHz", "10MHz")
        assert fs.to_dict()["frequencies"][0]["distribution"] == "linear_scale"

    def test_log_scale(self):
        fs = FrequencySweepConfig(name="sweep4")
        fs.add_log_scale_frequencies("1kHz", "1GHz", "1octave")
        assert fs.to_dict()["frequencies"][0]["distribution"] == "log_scale"

    def test_single_frequency(self):
        fs = FrequencySweepConfig(name="sweep5")
        fs.add_single_frequency("5GHz")
        freqs = fs.to_dict()["frequencies"]
        assert freqs[0]["distribution"] == "single"
        assert freqs[0]["start"] == "5GHz"

    def test_multiple_frequency_ranges(self):
        fs = FrequencySweepConfig(name="sweep6")
        fs.add_linear_count_frequencies("1GHz", "5GHz", 50)
        fs.add_log_count_frequencies("5GHz", "20GHz", 50)
        assert len(fs.to_dict()["frequencies"]) == 2

    def test_method_chaining(self):
        """All add_*_frequencies methods return self for chaining."""
        fs = FrequencySweepConfig(name="sw")
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
