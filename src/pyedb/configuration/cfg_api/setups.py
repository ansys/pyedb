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

Typical usage
-------------
>>> hfss = cfg.setups.add_hfss_setup("hfss1")
>>> hfss.set_broadband_adaptive("1GHz", "20GHz")
>>> sweep = hfss.add_frequency_sweep("sweep1")
>>> sweep.add_linear_count_frequencies("1GHz", "20GHz", 100)

>>> siw_ac = cfg.setups.add_siwave_ac_setup("siw_ac", si_slider_position=2)
>>> siw_ac.add_frequency_sweep("sw1").add_log_count_frequencies("1kHz", "1GHz", 100)

>>> cfg.setups.add_siwave_dc_setup("siw_dc", dc_slider_position=1)
"""

from __future__ import annotations

from typing import Dict, List, Optional, Union

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

    Parameters
    ----------
    name : str
        Sweep name, unique within the parent setup.
    sweep_type : str, default: ``"interpolation"``
        Sweep solution type.  Accepted values:

        * ``"interpolation"`` – fast interpolating sweep (default).
        * ``"discrete"``      – solve at every frequency point.
    use_q3d_for_dc : bool, default: ``False``
        Use Q3D for the DC point.  Applicable only inside an HFSS setup.
    compute_dc_point : bool, default: ``False``
        Enable the AC/DC merge (DC point) option.
    enforce_causality : bool, default: ``False``
        Enforce causality in the frequency sweep.
    enforce_passivity : bool, default: ``True``
        Enforce passivity in the frequency sweep.
    adv_dc_extrapolation : bool, default: ``False``
        Enable advanced DC extrapolation.
    use_hfss_solver_regions : bool, default: ``False``
        Use HFSS solver regions in the sweep.
    hfss_solver_region_setup_name : str or None, default: ``"<default>"``
        Name of the HFSS solver-region setup to reference.
    hfss_solver_region_sweep_name : str or None, default: ``"<default>"``
        Name of the HFSS solver-region sweep to reference.
    """

    model_config = {"populate_by_name": True, "extra": "allow"}

    def __init__(
        self,
        name: str,
        sweep_type: str = "interpolation",
        use_q3d_for_dc: bool = False,
        compute_dc_point: bool = False,
        enforce_causality: bool = False,
        enforce_passivity: bool = True,
        adv_dc_extrapolation: bool = False,
        use_hfss_solver_regions: bool = False,
        hfss_solver_region_setup_name: Optional[str] = "<default>",
        hfss_solver_region_sweep_name: Optional[str] = "<default>",
    ):
        super().__init__(
            name=name,
            type=sweep_type,
            use_q3d_for_dc=use_q3d_for_dc,
            compute_dc_point=compute_dc_point,
            enforce_causality=enforce_causality,
            enforce_passivity=enforce_passivity,
            adv_dc_extrapolation=adv_dc_extrapolation,
            use_hfss_solver_regions=use_hfss_solver_regions,
            hfss_solver_region_setup_name=hfss_solver_region_setup_name,
            hfss_solver_region_sweep_name=hfss_solver_region_sweep_name,
        )

    def add_linear_count_frequencies(
        self,
        start: Union[float, str],
        stop: Union[float, str],
        count: Union[int, str],
    ) -> "FrequencySweepConfig":
        """Append a linear-count frequency range to the sweep.

        Parameters
        ----------
        start : float or str
            Start frequency, e.g. ``"1GHz"`` or ``1e9``.
        stop : float or str
            Stop frequency, e.g. ``"20GHz"`` or ``2e10``.
        count : int or str
            Number of frequency points between *start* and *stop*.

        Returns
        -------
        FrequencySweepConfig
            *self*, for method chaining.
        """
        self.frequencies.append(
            CfgFrequencies(start=start, stop=stop, increment=count, distribution="linear_count")
        )
        return self

    def add_log_count_frequencies(
        self,
        start: Union[float, str],
        stop: Union[float, str],
        count: Union[int, str],
    ) -> "FrequencySweepConfig":
        """Append a logarithmic-count frequency range to the sweep.

        Parameters
        ----------
        start : float or str
            Start frequency, e.g. ``"1kHz"`` or ``1e3``.
        stop : float or str
            Stop frequency, e.g. ``"1GHz"`` or ``1e9``.
        count : int or str
            Number of frequency points per decade.

        Returns
        -------
        FrequencySweepConfig
            *self*, for method chaining.
        """
        self.frequencies.append(
            CfgFrequencies(start=start, stop=stop, increment=count, distribution="log_count")
        )
        return self

    def add_linear_scale_frequencies(
        self,
        start: Union[float, str],
        stop: Union[float, str],
        step: Union[float, str],
    ) -> "FrequencySweepConfig":
        """Append a linear-step frequency range to the sweep.

        Parameters
        ----------
        start : float or str
            Start frequency.
        stop : float or str
            Stop frequency.
        step : float or str
            Frequency step size, e.g. ``"100MHz"``.

        Returns
        -------
        FrequencySweepConfig
            *self*, for method chaining.
        """
        self.frequencies.append(
            CfgFrequencies(start=start, stop=stop, increment=step, distribution="linear_scale")
        )
        return self

    def add_log_scale_frequencies(
        self,
        start: Union[float, str],
        stop: Union[float, str],
        step: Union[float, str],
    ) -> "FrequencySweepConfig":
        """Append a logarithmic-step frequency range to the sweep.

        Parameters
        ----------
        start : float or str
            Start frequency.
        stop : float or str
            Stop frequency.
        step : float or str
            Frequency step (logarithmic scale).

        Returns
        -------
        FrequencySweepConfig
            *self*, for method chaining.
        """
        self.frequencies.append(
            CfgFrequencies(start=start, stop=stop, increment=step, distribution="log_scale")
        )
        return self

    def add_single_frequency(self, freq: Union[float, str]) -> "FrequencySweepConfig":
        """Append a single-frequency point to the sweep.

        Parameters
        ----------
        freq : float or str
            Frequency value, e.g. ``"5GHz"`` or ``5e9``.

        Returns
        -------
        FrequencySweepConfig
            *self*, for method chaining.
        """
        self.frequencies.append(
            CfgFrequencies(start=freq, stop=freq, increment=1, distribution="single")
        )
        return self

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

    Parameters
    ----------
    name : str
        Setup name, unique within the design.
    adapt_type : str, default: ``"single"``
        Adaptive refinement strategy.  Accepted values:

        * ``"single"``           – refine at one frequency (default).
        * ``"broadband"``        – refine across a low/high frequency pair.
        * ``"multi_frequencies"``– refine at an arbitrary list of frequencies.
    """

    model_config = {"populate_by_name": True, "extra": "allow"}

    def __init__(self, name: str, adapt_type: str = "single"):
        """Initialize an HFSS setup configuration.

        Parameters
        ----------
        name : str
            Setup name.
        adapt_type : str, default: ``"single"``
            Adaptive refinement strategy (``"single"``, ``"broadband"``, or
            ``"multi_frequencies"``).
        """
        super().__init__(name=name, adapt_type=adapt_type)
        self.multi_frequency_adaptive_solution.adapt_frequencies = []

    def set_single_frequency_adaptive(
        self,
        freq: Union[float, str] = "5GHz",
        max_passes: int = 20,
        max_delta: Union[float, str] = 0.02,
    ) -> "HfssSetupConfig":
        """Configure single-frequency adaptive refinement.

        Parameters
        ----------
        freq : float or str, default: ``"5GHz"``
            Adaptive frequency, e.g. ``"5GHz"`` or ``5e9``.
        max_passes : int, default: ``20``
            Maximum number of adaptive passes.
        max_delta : float or str, default: ``0.02``
            Maximum delta-S convergence criterion (e.g. ``0.02`` = 2 %).

        Returns
        -------
        HfssSetupConfig
            *self*, for method chaining.
        """
        self.adapt_type = "single"
        self.single_frequency_adaptive_solution = CfgHFSSSetup.CfgSingleFrequencyAdaptiveSolution(
            adaptive_frequency=freq, max_passes=max_passes, max_delta=max_delta
        )
        return self

    def set_broadband_adaptive(
        self,
        low_freq: Union[float, str] = "1GHz",
        high_freq: Union[float, str] = "10GHz",
        max_passes: int = 20,
        max_delta: Union[float, str] = 0.02,
    ) -> "HfssSetupConfig":
        """Configure broadband adaptive refinement.

        Parameters
        ----------
        low_freq : float or str, default: ``"1GHz"``
            Low frequency of the broadband adaptation range.
        high_freq : float or str, default: ``"10GHz"``
            High frequency of the broadband adaptation range.
        max_passes : int, default: ``20``
            Maximum number of adaptive passes.
        max_delta : float or str, default: ``0.02``
            Maximum delta-S convergence criterion.

        Returns
        -------
        HfssSetupConfig
            *self*, for method chaining.
        """
        self.adapt_type = "broadband"
        self.broadband_adaptive_solution = CfgHFSSSetup.CfgBroadbandAdaptiveSolution(
            low_frequency=low_freq, high_frequency=high_freq, max_passes=max_passes, max_delta=max_delta
        )
        return self

    def add_multi_frequency_adaptive(
        self,
        freq: Union[float, str],
        max_passes: int = 20,
        max_delta: Union[float, str] = 0.02,
    ) -> "HfssSetupConfig":
        """Append one adaptive point to a multi-frequency refinement setup.

        Can be called multiple times to build the list of adaptive frequencies.

        Parameters
        ----------
        freq : float or str
            Adaptive frequency, e.g. ``"5GHz"`` or ``5e9``.
        max_passes : int, default: ``20``
            Maximum number of adaptive passes at this frequency.
        max_delta : float or str, default: ``0.02``
            Maximum delta-S convergence criterion at this frequency.

        Returns
        -------
        HfssSetupConfig
            *self*, for method chaining.
        """
        self.adapt_type = "multi_frequencies"
        self.multi_frequency_adaptive_solution.adapt_frequencies.append(
            CfgHFSSSetup.CfgMultiFrequencyAdaptiveSolution.CfgAdaptFrequency(
                adaptive_frequency=freq, max_passes=max_passes, max_delta=max_delta
            )
        )
        return self

    def set_auto_mesh_operation(
        self,
        enabled: bool = True,
        trace_ratio_seeding: float = 3.0,
        signal_via_side_number: int = 12,
    ) -> "HfssSetupConfig":
        """Configure automatic mesh seeding for the HFSS setup.

        Parameters
        ----------
        enabled : bool, default: ``True``
            Whether to enable the automatic mesh operation.
        trace_ratio_seeding : float, default: ``3.0``
            Ratio used for trace mesh seeding (elements per wavelength along
            trace width).
        signal_via_side_number : int, default: ``12``
            Number of mesh facets per signal-via circumference.

        Returns
        -------
        HfssSetupConfig
            *self*, for method chaining.
        """
        self.auto_mesh_operation = CfgHFSSSetup.CfgAutoMeshOperation(
            enabled=enabled,
            trace_ratio_seeding=trace_ratio_seeding,
            signal_via_side_number=signal_via_side_number,
        )
        return self

    def add_length_mesh_operation(
        self,
        name: str,
        nets_layers_list: Dict[str, list],
        max_length: Optional[Union[float, str]] = "1mm",
        max_elements: Optional[Union[int, str]] = 1000,
        restrict_length: bool = True,
        refine_inside: bool = False,
    ) -> "HfssSetupConfig":
        """Append a length-based mesh operation to the HFSS setup.

        Parameters
        ----------
        name : str
            Unique name for this mesh operation.
        nets_layers_list : dict[str, list]
            Mapping of net names to the layers on which the operation applies,
            e.g. ``{"DDR4_DQ0": ["top"], "CLK": ["top", "L2"]}``.
        max_length : float or str, default: ``"1mm"``
            Maximum element edge length (supports unit strings, e.g.
            ``"0.5mm"``).  Ignored when *restrict_length* is ``False``.
        max_elements : int or str, default: ``1000``
            Maximum number of mesh elements within the region.
        restrict_length : bool, default: ``True``
            Enforce *max_length* as an upper bound on element size.
        refine_inside : bool, default: ``False``
            Refine mesh elements that are inside the region boundary as well.

        Returns
        -------
        HfssSetupConfig
            *self*, for method chaining.
        """
        mo = CfgHFSSSetup.CfgLengthMeshOperation(
            name=name,
            nets_layers_list=nets_layers_list,
            max_length=max_length,
            max_elements=max_elements,
            restrict_length=restrict_length,
            refine_inside=refine_inside,
        )
        self.mesh_operations.append(mo)
        return self

    def add_frequency_sweep(
        self,
        name: str,
        sweep_type: str = "interpolation",
        use_q3d_for_dc: bool = False,
        compute_dc_point: bool = False,
        enforce_causality: bool = False,
        enforce_passivity: bool = True,
        adv_dc_extrapolation: bool = False,
        use_hfss_solver_regions: bool = False,
        hfss_solver_region_setup_name: Optional[str] = "<default>",
        hfss_solver_region_sweep_name: Optional[str] = "<default>",
    ) -> FrequencySweepConfig:
        """Add a frequency sweep to the HFSS setup.

        Parameters
        ----------
        name : str
            Sweep name, unique within this setup.
        sweep_type : str, default: ``"interpolation"``
            Sweep type: ``"interpolation"`` or ``"discrete"``.
        use_q3d_for_dc : bool, default: ``False``
            Use Q3D solver for the DC point.
        compute_dc_point : bool, default: ``False``
            Enable the AC/DC merge (DC point) option.
        enforce_causality : bool, default: ``False``
            Enforce causality in the sweep.
        enforce_passivity : bool, default: ``True``
            Enforce passivity in the sweep.
        adv_dc_extrapolation : bool, default: ``False``
            Enable advanced DC extrapolation.
        use_hfss_solver_regions : bool, default: ``False``
            Solve using HFSS solver regions.
        hfss_solver_region_setup_name : str or None, default: ``"<default>"``
            HFSS solver-region setup name.
        hfss_solver_region_sweep_name : str or None, default: ``"<default>"``
            HFSS solver-region sweep name.

        Returns
        -------
        FrequencySweepConfig
            Newly created sweep builder (supports method chaining for adding
            frequency ranges).
        """
        sw = FrequencySweepConfig(
            name=name,
            sweep_type=sweep_type,
            use_q3d_for_dc=use_q3d_for_dc,
            compute_dc_point=compute_dc_point,
            enforce_causality=enforce_causality,
            enforce_passivity=enforce_passivity,
            adv_dc_extrapolation=adv_dc_extrapolation,
            use_hfss_solver_regions=use_hfss_solver_regions,
            hfss_solver_region_setup_name=hfss_solver_region_setup_name,
            hfss_solver_region_sweep_name=hfss_solver_region_sweep_name,
        )
        self.freq_sweep.append(sw)
        return sw

    def to_dict(self) -> dict:
        """Serialize the HFSS setup.

        Returns
        -------
        dict
            Dictionary containing the configured HFSS setup settings.
            Empty ``mesh_operations`` lists are omitted.
        """
        d = self.model_dump(exclude_none=True)
        if not self.mesh_operations:
            d.pop("mesh_operations", None)
        return d


class SIwaveACSetupConfig(CfgSIwaveACSetup):
    """Fluent builder for a SIwave AC setup.

    Inherits all fields from :class:`~pyedb.configuration.cfg_setup.CfgSIwaveACSetup`.

    Parameters
    ----------
    name : str
        Setup name, unique within the design.
    si_slider_position : int, default: ``1``
        SI accuracy slider position.

        * ``0`` – Speed
        * ``1`` – Balanced (default)
        * ``2`` – Accuracy
    pi_slider_position : int, default: ``1``
        PI accuracy slider position (same scale as *si_slider_position*).
    use_si_settings : bool, default: ``True``
        When ``True`` the SI slider governs solver accuracy; when ``False``
        the PI slider is used instead.
    """

    model_config = {"populate_by_name": True, "extra": "allow"}

    def __init__(
        self,
        name: str,
        si_slider_position: int = 1,
        pi_slider_position: int = 1,
        use_si_settings: bool = True,
    ):
        """Initialize a SIwave AC setup configuration.

        Parameters
        ----------
        name : str
            Setup name.
        si_slider_position : int, default: ``1``
            SI solver accuracy slider (0 = Speed, 1 = Balanced, 2 = Accuracy).
        pi_slider_position : int, default: ``1``
            PI solver accuracy slider (0 = Speed, 1 = Balanced, 2 = Accuracy).
        use_si_settings : bool, default: ``True``
            Use SI-Wave SI settings when ``True``, PI settings when ``False``.
        """
        super().__init__(
            name=name,
            si_slider_position=si_slider_position,
            pi_slider_position=pi_slider_position,
            use_si_settings=use_si_settings,
        )

    def add_frequency_sweep(
        self,
        name: str,
        sweep_type: str = "interpolation",
        use_q3d_for_dc: bool = False,
        compute_dc_point: bool = False,
        enforce_causality: bool = False,
        enforce_passivity: bool = True,
        adv_dc_extrapolation: bool = False,
        use_hfss_solver_regions: bool = False,
        hfss_solver_region_setup_name: Optional[str] = "<default>",
        hfss_solver_region_sweep_name: Optional[str] = "<default>",
    ) -> FrequencySweepConfig:
        """Add a frequency sweep to the SIwave AC setup.

        Parameters
        ----------
        name : str
            Sweep name, unique within this setup.
        sweep_type : str, default: ``"interpolation"``
            Sweep type: ``"interpolation"`` or ``"discrete"``.
        use_q3d_for_dc : bool, default: ``False``
            Use Q3D solver for the DC point.
        compute_dc_point : bool, default: ``False``
            Enable the AC/DC merge (DC point) option.
        enforce_causality : bool, default: ``False``
            Enforce causality in the sweep.
        enforce_passivity : bool, default: ``True``
            Enforce passivity in the sweep.
        adv_dc_extrapolation : bool, default: ``False``
            Enable advanced DC extrapolation.
        use_hfss_solver_regions : bool, default: ``False``
            Solve using HFSS solver regions.
        hfss_solver_region_setup_name : str or None, default: ``"<default>"``
            HFSS solver-region setup name.
        hfss_solver_region_sweep_name : str or None, default: ``"<default>"``
            HFSS solver-region sweep name.

        Returns
        -------
        FrequencySweepConfig
            Newly created sweep builder (supports method chaining for adding
            frequency ranges).
        """
        sw = FrequencySweepConfig(
            name=name,
            sweep_type=sweep_type,
            use_q3d_for_dc=use_q3d_for_dc,
            compute_dc_point=compute_dc_point,
            enforce_causality=enforce_causality,
            enforce_passivity=enforce_passivity,
            adv_dc_extrapolation=adv_dc_extrapolation,
            use_hfss_solver_regions=use_hfss_solver_regions,
            hfss_solver_region_setup_name=hfss_solver_region_setup_name,
            hfss_solver_region_sweep_name=hfss_solver_region_sweep_name,
        )
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

    Parameters
    ----------
    name : str
        Setup name, unique within the design.
    dc_slider_position : int, default: ``1``
        DC solver accuracy slider.

        * ``0`` – Speed
        * ``1`` – Balanced (default)
        * ``2`` – Accuracy
    export_dc_thermal_data : bool, default: ``False``
        Export DC thermal (loss) data after the DC solve.
    """

    model_config = {"populate_by_name": True, "extra": "allow"}

    def __init__(
        self,
        name: str,
        dc_slider_position: Union[int, str] = 1,
        export_dc_thermal_data: bool = False,
    ):
        """Initialize a SIwave DC setup configuration.

        Parameters
        ----------
        name : str
            Setup name.
        dc_slider_position : int or str, default: ``1``
            DC solver accuracy slider (0 = Speed, 1 = Balanced, 2 = Accuracy).
        export_dc_thermal_data : bool, default: ``False``
            Whether to export DC thermal (loss) data after solving.
        """
        dc_ir = CfgSIwaveDCSetup.CfgDCIRSettings(export_dc_thermal_data=export_dc_thermal_data)
        super().__init__(name=name, dc_slider_position=dc_slider_position, dc_ir_settings=dc_ir)

    def to_dict(self) -> dict:
        """Serialize the SIwave DC setup.

        Returns
        -------
        dict
            Dictionary containing the configured SIwave DC setup settings.
        """
        return self.model_dump(exclude_none=True)


class SetupsConfig:
    """Fluent builder for the ``setups`` configuration list.

    Add one or more simulation setups of any type.  The list is serialized
    in insertion order by :meth:`to_list`.

    Examples
    --------
    >>> hfss = cfg.setups.add_hfss_setup("hfss1")
    >>> hfss.set_broadband_adaptive("1GHz", "20GHz")
    >>> hfss.add_frequency_sweep("sw1").add_linear_count_frequencies("1GHz", "20GHz", 100)

    >>> siw = cfg.setups.add_siwave_ac_setup("siw_ac", si_slider_position=2)
    >>> siw.add_frequency_sweep("sw1").add_log_count_frequencies("1kHz", "1GHz", 100)

    >>> cfg.setups.add_siwave_dc_setup("siw_dc", dc_slider_position=1)
    """

    def __init__(self):
        """Initialize an empty setups list."""
        self._setups: List = []

    def add_hfss_setup(
        self,
        name: str,
        adapt_type: str = "single",
    ) -> HfssSetupConfig:
        """Add an HFSS setup and return its builder.

        Use the returned :class:`HfssSetupConfig` to configure adaptive
        settings, mesh operations, and frequency sweeps.

        Parameters
        ----------
        name : str
            Setup name, unique within the design.
        adapt_type : str, default: ``"single"``
            Initial adaptive refinement strategy.  Can be changed later by
            calling :meth:`~HfssSetupConfig.set_single_frequency_adaptive`,
            :meth:`~HfssSetupConfig.set_broadband_adaptive`, or
            :meth:`~HfssSetupConfig.add_multi_frequency_adaptive`.

            Accepted values:

            * ``"single"``            – refine at one frequency (default).
            * ``"broadband"``         – refine across a low/high pair.
            * ``"multi_frequencies"`` – refine at multiple frequencies.

        Returns
        -------
        HfssSetupConfig
            Newly created HFSS setup builder.

        Examples
        --------
        >>> hfss = cfg.setups.add_hfss_setup("hfss1")
        >>> hfss.set_broadband_adaptive("1GHz", "20GHz", max_passes=15)
        >>> hfss.set_auto_mesh_operation(enabled=True)
        >>> hfss.add_length_mesh_operation("mo1", {"CLK": ["top"]}, max_length="0.5mm")
        >>> hfss.add_frequency_sweep("sweep1").add_linear_count_frequencies("1GHz", "20GHz", 200)
        """
        setup = HfssSetupConfig(name=name, adapt_type=adapt_type)
        self._setups.append(setup)
        return setup

    def add_siwave_ac_setup(
        self,
        name: str,
        si_slider_position: int = 1,
        pi_slider_position: int = 1,
        use_si_settings: bool = True,
    ) -> SIwaveACSetupConfig:
        """Add a SIwave AC (SYZ) setup and return its builder.

        Use the returned :class:`SIwaveACSetupConfig` to add frequency sweeps.

        Parameters
        ----------
        name : str
            Setup name, unique within the design.
        si_slider_position : int, default: ``1``
            SI solver accuracy slider (0 = Speed, 1 = Balanced, 2 = Accuracy).
        pi_slider_position : int, default: ``1``
            PI solver accuracy slider (0 = Speed, 1 = Balanced, 2 = Accuracy).
        use_si_settings : bool, default: ``True``
            When ``True`` the SI slider governs solver accuracy; when ``False``
            the PI slider is used.

        Returns
        -------
        SIwaveACSetupConfig
            Newly created SIwave AC setup builder.

        Examples
        --------
        >>> siw = cfg.setups.add_siwave_ac_setup("siw_ac", si_slider_position=2)
        >>> siw.add_frequency_sweep("sw1").add_log_count_frequencies("1kHz", "1GHz", 100)
        """
        setup = SIwaveACSetupConfig(
            name=name,
            si_slider_position=si_slider_position,
            pi_slider_position=pi_slider_position,
            use_si_settings=use_si_settings,
        )
        self._setups.append(setup)
        return setup

    def add_siwave_dc_setup(
        self,
        name: str,
        dc_slider_position: Union[int, str] = 1,
        export_dc_thermal_data: bool = False,
    ) -> SIwaveDCSetupConfig:
        """Add a SIwave DC (IR-drop) setup and return its builder.

        Parameters
        ----------
        name : str
            Setup name, unique within the design.
        dc_slider_position : int or str, default: ``1``
            DC solver accuracy slider (0 = Speed, 1 = Balanced, 2 = Accuracy).
        export_dc_thermal_data : bool, default: ``False``
            Whether to export DC thermal (loss) data after solving.

        Returns
        -------
        SIwaveDCSetupConfig
            Newly created SIwave DC setup builder.

        Examples
        --------
        >>> cfg.setups.add_siwave_dc_setup("siw_dc", dc_slider_position=2, export_dc_thermal_data=True)
        """
        setup = SIwaveDCSetupConfig(
            name=name,
            dc_slider_position=dc_slider_position,
            export_dc_thermal_data=export_dc_thermal_data,
        )
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
