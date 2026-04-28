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
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Simulation setups builder API."""

from __future__ import annotations

from typing import List, Optional, Union


class FrequencySweepConfig:
    """Builder for a single frequency sweep."""

    def __init__(
        self,
        name: str,
        sweep_type: str = "interpolation",
        enforce_causality: bool = False,
        enforce_passivity: bool = True,
        adv_dc_extrapolation: bool = False,
        use_q3d_for_dc: bool = False,
        compute_dc_point: bool = False,
    ):
        self.name = name
        self.type = sweep_type
        self.enforce_causality = enforce_causality
        self.enforce_passivity = enforce_passivity
        self.adv_dc_extrapolation = adv_dc_extrapolation
        self.use_q3d_for_dc = use_q3d_for_dc
        self.compute_dc_point = compute_dc_point
        self.frequencies: List[dict] = []

    def add_linear_count_frequencies(self, start, stop, count):
        self.frequencies.append({"distribution": "linear_count", "start": start, "stop": stop, "increment": count})

    def add_log_count_frequencies(self, start, stop, count):
        self.frequencies.append({"distribution": "log_count", "start": start, "stop": stop, "increment": count})

    def add_linear_scale_frequencies(self, start, stop, step):
        self.frequencies.append({"distribution": "linear_scale", "start": start, "stop": stop, "increment": step})

    def add_log_scale_frequencies(self, start, stop, step):
        self.frequencies.append({"distribution": "log_scale", "start": start, "stop": stop, "increment": step})

    def add_single_frequency(self, freq):
        self.frequencies.append({"distribution": "single", "start": freq, "stop": freq, "increment": 1})

    def to_dict(self) -> dict:
        d = {
            "name": self.name,
            "type": self.type,
            "enforce_causality": self.enforce_causality,
            "enforce_passivity": self.enforce_passivity,
            "adv_dc_extrapolation": self.adv_dc_extrapolation,
            "use_q3d_for_dc": self.use_q3d_for_dc,
            "compute_dc_point": self.compute_dc_point,
            "frequencies": self.frequencies,
        }
        return d


class HfssSetupConfig:
    """Builder for an HFSS simulation setup."""

    def __init__(self, name: str, **kwargs):
        self.name = name
        self.type = "hfss"
        self.adapt_type = "single"
        self._single_freq = {"adaptive_frequency": "5GHz", "max_passes": 20, "max_delta": "0.02"}
        self._broadband = {"low_frequency": "1GHz", "high_frequency": "10GHz", "max_passes": 20, "max_delta": "0.02"}
        self._multi_freqs: List[dict] = []
        self._auto_mesh = {"enabled": False, "trace_ratio_seeding": 3, "signal_via_side_number": 12}
        self._mesh_ops: List[dict] = []
        self._sweeps: List[FrequencySweepConfig] = []
        # apply any extra kwargs as attributes
        for k, v in kwargs.items():
            setattr(self, k, v)

    def set_single_frequency_adaptive(self, freq, max_passes: int = 20, max_delta=0.02):
        self.adapt_type = "single"
        self._single_freq = {"adaptive_frequency": freq, "max_passes": max_passes, "max_delta": max_delta}

    def set_broadband_adaptive(self, low_freq, high_freq, max_passes: int = 20, max_delta=0.02):
        self.adapt_type = "broadband"
        self._broadband = {"low_frequency": low_freq, "high_frequency": high_freq, "max_passes": max_passes, "max_delta": max_delta}

    def add_multi_frequency_adaptive(self, freq, max_passes: int = 20, max_delta=0.02):
        self.adapt_type = "multi_frequencies"
        self._multi_freqs.append({"adaptive_frequency": freq, "max_passes": max_passes, "max_delta": max_delta})

    def set_auto_mesh_operation(self, enabled: bool = True, trace_ratio_seeding: float = 3, signal_via_side_number: int = 12):
        self._auto_mesh = {"enabled": enabled, "trace_ratio_seeding": trace_ratio_seeding, "signal_via_side_number": signal_via_side_number}

    def add_length_mesh_operation(self, name: str, nets_layers_list: dict, max_length=None, max_elements=None, restrict_length: bool = True, refine_inside: bool = False):
        mo = {"name": name, "mesh_operation_type": "length", "nets_layers_list": nets_layers_list, "restrict_length": restrict_length, "refine_inside": refine_inside}
        if max_length is not None:
            mo["max_length"] = max_length
        if max_elements is not None:
            mo["max_elements"] = max_elements
        self._mesh_ops.append(mo)

    def add_frequency_sweep(self, name: str, sweep_type: str = "interpolation", **kwargs) -> FrequencySweepConfig:
        sw = FrequencySweepConfig(name, sweep_type=sweep_type, **kwargs)
        self._sweeps.append(sw)
        return sw

    def to_dict(self) -> dict:
        d: dict = {"name": self.name, "type": self.type, "adapt_type": self.adapt_type}
        d["single_frequency_adaptive_solution"] = self._single_freq
        d["broadband_adaptive_solution"] = self._broadband
        d["multi_frequency_adaptive_solution"] = {"adapt_frequencies": self._multi_freqs}
        d["auto_mesh_operation"] = self._auto_mesh
        if self._mesh_ops:
            d["mesh_operations"] = self._mesh_ops
        if self._sweeps:
            d["freq_sweep"] = [sw.to_dict() for sw in self._sweeps]
        return d


class SIwaveACSetupConfig:
    """Builder for a SIwave AC simulation setup."""

    def __init__(self, name: str, si_slider_position: int = 1, pi_slider_position: int = 1, use_si_settings: bool = True, **kwargs):
        self.name = name
        self.type = "siwave_ac"
        self.si_slider_position = si_slider_position
        self.pi_slider_position = pi_slider_position
        self.use_si_settings = use_si_settings
        self._sweeps: List[FrequencySweepConfig] = []

    def add_frequency_sweep(self, name: str, sweep_type: str = "interpolation", **kwargs) -> FrequencySweepConfig:
        sw = FrequencySweepConfig(name, sweep_type=sweep_type, **kwargs)
        self._sweeps.append(sw)
        return sw

    def to_dict(self) -> dict:
        d: dict = {
            "name": self.name,
            "type": self.type,
            "si_slider_position": self.si_slider_position,
            "pi_slider_position": self.pi_slider_position,
            "use_si_settings": self.use_si_settings,
        }
        if self._sweeps:
            d["freq_sweep"] = [sw.to_dict() for sw in self._sweeps]
        return d


class SIwaveDCSetupConfig:
    """Builder for a SIwave DC simulation setup."""

    def __init__(self, name: str, dc_slider_position: Union[int, str] = 1, export_dc_thermal_data: bool = False, **kwargs):
        self.name = name
        self.type = "siwave_dc"
        self.dc_slider_position = dc_slider_position
        self.export_dc_thermal_data = export_dc_thermal_data

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.type,
            "dc_slider_position": self.dc_slider_position,
            "dc_ir_settings": {"export_dc_thermal_data": self.export_dc_thermal_data},
        }


class SetupsConfig:
    """Fluent builder for the ``setups`` configuration list."""

    def __init__(self):
        self._setups: List = []

    def add_hfss_setup(self, name: str, **kwargs) -> HfssSetupConfig:
        setup = HfssSetupConfig(name, **kwargs)
        self._setups.append(setup)
        return setup

    def add_siwave_ac_setup(self, name: str, **kwargs) -> SIwaveACSetupConfig:
        setup = SIwaveACSetupConfig(name, **kwargs)
        self._setups.append(setup)
        return setup

    def add_siwave_dc_setup(self, name: str, **kwargs) -> SIwaveDCSetupConfig:
        setup = SIwaveDCSetupConfig(name, **kwargs)
        self._setups.append(setup)
        return setup

    def to_list(self) -> List[dict]:
        result = []
        for s in self._setups:
            if hasattr(s, "to_dict"):
                result.append(s.to_dict())
            else:
                result.append(dict(s))
        return result
