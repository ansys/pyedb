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

"""Build simulation setup configuration entries.

This module wraps HFSS, SIwave AC, and SIwave DC setup models with fluent
helpers for common adaptive and sweep configurations.
"""

from __future__ import annotations

from typing import List, Union

from pyedb.configuration.cfg_setup import (
    CfgFrequencies,
    CfgHFSSSetup,
    CfgSIwaveACSetup,
    CfgSIwaveDCSetup,
)


class FrequencySweepConfig(CfgSIwaveACSetup.CfgFrequencySweep):
    """Fluent builder for a frequency sweep.

    Inherits all fields from
    :class:`~pyedb.configuration.cfg_setup.CfgSIwaveACSetup.CfgFrequencySweep`.
    """

    model_config = {"populate_by_name": True, "extra": "allow"}

    def __init__(self, name: str, sweep_type: str = "interpolation", **kwargs):
        super().__init__(name=name, type=sweep_type, **kwargs)

    def add_linear_count_frequencies(self, start, stop, count):
        """Append a linear-count frequency range to the sweep."""
        self.frequencies.append(CfgFrequencies(start=start, stop=stop, increment=count, distribution="linear_count"))

    def add_log_count_frequencies(self, start, stop, count):
        """Append a logarithmic-count frequency range to the sweep."""
        self.frequencies.append(CfgFrequencies(start=start, stop=stop, increment=count, distribution="log_count"))

    def add_linear_scale_frequencies(self, start, stop, step):
        """Append a linear-step frequency range to the sweep."""
        self.frequencies.append(CfgFrequencies(start=start, stop=stop, increment=step, distribution="linear_scale"))

    def add_log_scale_frequencies(self, start, stop, step):
        """Append a logarithmic-step frequency range to the sweep."""
        self.frequencies.append(CfgFrequencies(start=start, stop=stop, increment=step, distribution="log_scale"))

    def add_single_frequency(self, freq):
        """Append a single-frequency point to the sweep."""
        self.frequencies.append(CfgFrequencies(start=freq, stop=freq, increment=1, distribution="single"))

    def to_dict(self) -> dict:
        """Serialize the frequency sweep.

        Returns
        -------
        dict
            Dictionary containing the configured sweep settings.
        """
        return self.model_dump(exclude_none=True)


class HfssSetupConfig(CfgHFSSSetup):
    """Fluent builder for an HFSS setup.

    Inherits all fields from :class:`~pyedb.configuration.cfg_setup.CfgHFSSSetup`.
    """

    model_config = {"populate_by_name": True, "extra": "allow"}

    def __init__(self, name: str, **kwargs):
        super().__init__(name=name, **kwargs)
        # reset multi_freq adapt_frequencies to empty — defaults in the root model are 2 preset entries
        self.multi_frequency_adaptive_solution.adapt_frequencies = []

    def set_single_frequency_adaptive(self, freq, max_passes: int = 20, max_delta=0.02):
        """Configure single-frequency adaptive refinement."""
        self.adapt_type = "single"
        self.single_frequency_adaptive_solution = CfgHFSSSetup.CfgSingleFrequencyAdaptiveSolution(
            adaptive_frequency=freq, max_passes=max_passes, max_delta=max_delta
        )

    def set_broadband_adaptive(self, low_freq, high_freq, max_passes: int = 20, max_delta=0.02):
        """Configure broadband adaptive refinement."""
        self.adapt_type = "broadband"
        self.broadband_adaptive_solution = CfgHFSSSetup.CfgBroadbandAdaptiveSolution(
            low_frequency=low_freq, high_frequency=high_freq, max_passes=max_passes, max_delta=max_delta
        )

    def add_multi_frequency_adaptive(self, freq, max_passes: int = 20, max_delta=0.02):
        """Append one adaptive point to a multi-frequency refinement setup."""
        self.adapt_type = "multi_frequencies"
        self.multi_frequency_adaptive_solution.adapt_frequencies.append(
            CfgHFSSSetup.CfgMultiFrequencyAdaptiveSolution.CfgAdaptFrequency(
                adaptive_frequency=freq, max_passes=max_passes, max_delta=max_delta
            )
        )

    def set_auto_mesh_operation(
        self,
        enabled: bool = True,
        trace_ratio_seeding: float = 3,
        signal_via_side_number: int = 12,
    ):
        """Configure automatic mesh settings for the HFSS setup."""
        self.auto_mesh_operation = CfgHFSSSetup.CfgAutoMeshOperation(
            enabled=enabled, trace_ratio_seeding=trace_ratio_seeding, signal_via_side_number=signal_via_side_number
        )

    def add_length_mesh_operation(
        self,
        name: str,
        nets_layers_list: dict,
        max_length=None,
        max_elements=None,
        restrict_length: bool = True,
        refine_inside: bool = False,
    ):
        """Append a length-based mesh operation to the HFSS setup."""
        mo = CfgHFSSSetup.CfgLengthMeshOperation(
            name=name,
            nets_layers_list=nets_layers_list,
            restrict_length=restrict_length,
            refine_inside=refine_inside,
        )
        if max_length is not None:
            mo.max_length = max_length
        if max_elements is not None:
            mo.max_elements = max_elements
        self.mesh_operations.append(mo)

    def add_frequency_sweep(
        self,
        name: str,
        sweep_type: str = "interpolation",
        **kwargs,
    ) -> FrequencySweepConfig:
        """Add a frequency sweep to the HFSS setup.

        Returns
        -------
        FrequencySweepConfig
            Newly created sweep configuration.
        """
        sw = FrequencySweepConfig(name=name, sweep_type=sweep_type, **kwargs)
        self.freq_sweep.append(sw)
        return sw

    def to_dict(self) -> dict:
        """Serialize the HFSS setup.

        Returns
        -------
        dict
            Dictionary containing the configured HFSS setup settings.
        """
        d = self.model_dump(exclude_none=True)
        # omit mesh_operations key when empty
        if not self.mesh_operations:
            d.pop("mesh_operations", None)
        return d


class SIwaveACSetupConfig(CfgSIwaveACSetup):
    """Fluent builder for a SIwave AC setup.

    Inherits all fields from :class:`~pyedb.configuration.cfg_setup.CfgSIwaveACSetup`.
    """

    model_config = {"populate_by_name": True, "extra": "allow"}

    def __init__(self, name: str, **kwargs):
        super().__init__(name=name, **kwargs)

    def add_frequency_sweep(
        self,
        name: str,
        sweep_type: str = "interpolation",
        **kwargs,
    ) -> FrequencySweepConfig:
        """Add a frequency sweep to the SIwave AC setup.

        Returns
        -------
        FrequencySweepConfig
            Newly created sweep configuration.
        """
        sw = FrequencySweepConfig(name=name, sweep_type=sweep_type, **kwargs)
        self.freq_sweep.append(sw)
        return sw

    def to_dict(self) -> dict:
        """Serialize the SIwave AC setup.

        Returns
        -------
        dict
            Dictionary containing the configured SIwave AC setup settings.
        """
        return self.model_dump(exclude_none=True)


class SIwaveDCSetupConfig(CfgSIwaveDCSetup):
    """Fluent builder for a SIwave DC setup.

    Inherits all fields from :class:`~pyedb.configuration.cfg_setup.CfgSIwaveDCSetup`.
    """

    model_config = {"populate_by_name": True, "extra": "allow"}

    def __init__(
        self,
        name: str,
        dc_slider_position: Union[int, str] = 1,
        export_dc_thermal_data: bool = False,
        **kwargs,
    ):
        dc_ir = CfgSIwaveDCSetup.CfgDCIRSettings(export_dc_thermal_data=export_dc_thermal_data)
        super().__init__(name=name, dc_slider_position=dc_slider_position, dc_ir_settings=dc_ir, **kwargs)

    def to_dict(self) -> dict:
        """Serialize the SIwave DC setup.

        Returns
        -------
        dict
            Dictionary containing the configured SIwave DC setup settings.
        """
        return self.model_dump(exclude_none=True)


class SetupsConfig:
    """Fluent builder for the ``setups`` configuration list."""

    def __init__(self):
        self._setups: List = []

    def add_hfss_setup(self, name: str, **kwargs) -> HfssSetupConfig:
        """Add an HFSS setup.

        Returns
        -------
        HfssSetupConfig
            Newly created HFSS setup.
        """
        setup = HfssSetupConfig(name=name, **kwargs)
        self._setups.append(setup)
        return setup

    def add_siwave_ac_setup(self, name: str, **kwargs) -> SIwaveACSetupConfig:
        """Add a SIwave AC setup.

        Returns
        -------
        SIwaveACSetupConfig
            Newly created SIwave AC setup.
        """
        setup = SIwaveACSetupConfig(name=name, **kwargs)
        self._setups.append(setup)
        return setup

    def add_siwave_dc_setup(self, name: str, **kwargs) -> SIwaveDCSetupConfig:
        """Add a SIwave DC setup.

        Returns
        -------
        SIwaveDCSetupConfig
            Newly created SIwave DC setup.
        """
        setup = SIwaveDCSetupConfig(name=name, **kwargs)
        self._setups.append(setup)
        return setup

    def to_list(self) -> List[dict]:
        """Serialize all configured setups.

        Returns
        -------
        list[dict]
            Setup definitions in insertion order.
        """
        result = []
        for s in self._setups:
            if hasattr(s, "to_dict"):
                result.append(s.to_dict())
            else:
                result.append(dict(s))
        return result
