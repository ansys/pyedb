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
"""Build HFSS and SIwave setup entries for configuration payloads."""

from typing import List, Literal, Optional, Union

from pydantic import AliasChoices, Field

from pyedb.configuration.cfg_common import CfgBaseModel


_DISTRIBUTION_ALIASES = {
    "linear_count": "linear_count",
    "linearcount": "linear_count",
    "linear count": "linear_count",
    "log_count": "log_count",
    "logcount": "log_count",
    "log count": "log_count",
    "linear_scale": "linear_scale",
    "linearscale": "linear_scale",
    "linear scale": "linear_scale",
    "log_scale": "log_scale",
    "logscale": "log_scale",
    "log scale": "log_scale",
    "single": "single",
}


def _add_inline_range(sweep, start, stop, step_or_count, distribution: str):
    dist = _DISTRIBUTION_ALIASES.get(str(distribution).lower().replace("-", "_"), distribution)
    if dist == "single":
        sweep.frequencies.append(CfgFrequencies(start=start, stop=start, increment=1, distribution="single"))
    else:
        sweep.frequencies.append(CfgFrequencies(start=start, stop=stop, increment=step_or_count, distribution=dist))


class CfgFrequencies(CfgBaseModel):
    """Represent one frequency range or single-point sweep segment."""

    start: float | str = Field(..., description="Start frequency in Hz")
    stop: float | str = Field(..., description="Stop frequency in Hz")
    increment: int | str = Field(..., validation_alias=AliasChoices("increment", "points", "samples", "step"))
    distribution: Literal[
        "linear_scale", "log_scale", "single", "linear_count", "log_count", "linear scale", "log scale", "linear count"
    ] = Field(
        ..., description="Frequency distribution type, e.g., linear_step, log_step, single, linear_count, log_count"
    )


class CfgSetupDC(CfgBaseModel):
    """Base class for DC-style setup payloads."""

    name: str


class CfgSetupAC(CfgSetupDC):
    """Base class for AC-style setup payloads with frequency sweeps."""

    class CfgFrequencySweep(CfgBaseModel):
        name: str
        type: Literal["discrete", "interpolation", "interpolating"]
        frequencies: list[CfgFrequencies | str] = Field(list(), description="List of frequency definitions or strings")

        use_q3d_for_dc: bool = Field(False, description="Use Q3D for DC analysis. Only applicable for HFSS setup.")
        compute_dc_point: bool = Field(False, description="AC/DC Merge checkbox in GUI.")
        enforce_causality: bool = False
        enforce_passivity: bool = True
        adv_dc_extrapolation: bool = False

        use_hfss_solver_regions: bool = Field(False)
        hfss_solver_region_setup_name: str | None = "<default>"
        hfss_solver_region_sweep_name: str | None = "<default>"

        def __init__(
            self,
            name: str,
            sweep_type: str = "interpolation",
            frequencies=None,
            use_q3d_for_dc: bool = False,
            compute_dc_point: bool = False,
            enforce_causality: bool = False,
            enforce_passivity: bool = True,
            adv_dc_extrapolation: bool = False,
            use_hfss_solver_regions: bool = False,
            hfss_solver_region_setup_name: str | None = "<default>",
            hfss_solver_region_sweep_name: str | None = "<default>",
            **kwargs,
        ):
            sweep_type = kwargs.pop("type", sweep_type)
            super().__init__(
                name=name,
                type=sweep_type,
                frequencies=list(frequencies or []),
                use_q3d_for_dc=use_q3d_for_dc,
                compute_dc_point=compute_dc_point,
                enforce_causality=enforce_causality,
                enforce_passivity=enforce_passivity,
                adv_dc_extrapolation=adv_dc_extrapolation,
                use_hfss_solver_regions=use_hfss_solver_regions,
                hfss_solver_region_setup_name=hfss_solver_region_setup_name,
                hfss_solver_region_sweep_name=hfss_solver_region_sweep_name,
                **kwargs,
            )

        def add_frequencies(self, freq: CfgFrequencies):
            """Append a pre-built :class:`CfgFrequencies` range to this sweep.

            Parameters
            ----------
            freq : CfgFrequencies
                Fully constructed frequency-range object to append.
            """
            self.frequencies.append(freq)

        def add_linear_count_frequencies(self, start, stop, count):
            """Append a linear-count frequency range to this sweep.

            Parameters
            ----------
            start : str or float
                Start frequency, e.g. ``"1GHz"`` or ``1e9``.
            stop : str or float
                Stop frequency, e.g. ``"20GHz"`` or ``20e9``.
            count : int
                Number of evenly spaced frequency points.

            Returns
            -------
            CfgFrequencySweep
                *self* — enables method chaining.

            Examples
            --------
            >>> sw = hfss.add_frequency_sweep("sw")
            >>> sw.add_linear_count_frequencies("1GHz", "10GHz", 100)
            """
            self.frequencies.append(CfgFrequencies(start=start, stop=stop, increment=count, distribution="linear_count"))
            return self

        def add_log_count_frequencies(self, start, stop, count):
            """Append a logarithmic-count frequency range to this sweep.

            Parameters
            ----------
            start : str or float
                Start frequency, e.g. ``"1MHz"``.
            stop : str or float
                Stop frequency, e.g. ``"1GHz"``.
            count : int
                Number of frequency points distributed on a log scale.

            Returns
            -------
            CfgFrequencySweep
                *self* — enables method chaining.
            """
            self.frequencies.append(CfgFrequencies(start=start, stop=stop, increment=count, distribution="log_count"))
            return self

        def add_linear_scale_frequencies(self, start, stop, step):
            """Append a linear-step frequency range to this sweep.

            Parameters
            ----------
            start : str or float
                Start frequency, e.g. ``"0Hz"``.
            stop : str or float
                Stop frequency, e.g. ``"1GHz"``.
            step : str or float
                Step size between consecutive points, e.g. ``"10MHz"``.

            Returns
            -------
            CfgFrequencySweep
                *self* — enables method chaining.
            """
            self.frequencies.append(CfgFrequencies(start=start, stop=stop, increment=step, distribution="linear_scale"))
            return self

        def add_log_scale_frequencies(self, start, stop, step):
            """Append a logarithmic-step frequency range to this sweep.

            Parameters
            ----------
            start : str or float
                Start frequency.
            stop : str or float
                Stop frequency.
            step : str or float
                Decade step size.

            Returns
            -------
            CfgFrequencySweep
                *self* — enables method chaining.
            """
            self.frequencies.append(CfgFrequencies(start=start, stop=stop, increment=step, distribution="log_scale"))
            return self

        def add_single_frequency(self, freq):
            """Append a single discrete frequency point to this sweep.

            Parameters
            ----------
            freq : str or float
                Frequency value, e.g. ``"5GHz"`` or ``5e9``.

            Returns
            -------
            CfgFrequencySweep
                *self* — enables method chaining.

            Examples
            --------
            >>> sw.add_single_frequency("0Hz")
            """
            self.frequencies.append(CfgFrequencies(start=freq, stop=freq, increment=1, distribution="single"))
            return self

        def to_dict(self) -> dict:
            """Serialize this sweep to a plain dictionary.

            Returns
            -------
            dict
                Sweep payload with ``None`` values excluded.
            """
            return self.model_dump(exclude_none=True)

    freq_sweep: list[CfgFrequencySweep] | None = list()

    def add_frequency_sweep(self, sweep: CfgFrequencySweep):
        """Append a pre-built frequency sweep to this setup.

        Parameters
        ----------
        sweep : CfgFrequencySweep
            Fully constructed sweep object.
        """
        self.freq_sweep.append(sweep)


class CfgSIwaveACSetup(CfgSetupAC):
    """Represent one SIwave AC setup entry."""

    type: str = "siwave_ac"
    use_si_settings: bool = Field(True, description="Use SI-Wave AC settings")
    si_slider_position: int = Field(1, description="SI slider position. Options are 0-speed, 1-balanced, 2-accuracy.")
    pi_slider_position: int = Field(1, description="PI Slider position. Options are 0-speed, 1-balanced, 2-accuracy.")

    def __init__(
        self,
        name: str,
        si_slider_position: int = 1,
        pi_slider_position: int = 1,
        use_si_settings: bool = True,
        **kwargs,
    ):
        super().__init__(
            name=name,
            si_slider_position=si_slider_position,
            pi_slider_position=pi_slider_position,
            use_si_settings=use_si_settings,
            **kwargs,
        )

    def add_frequency_sweep(
        self,
        name: CfgSetupAC.CfgFrequencySweep | str,
        sweep_type: str = "interpolation",
        start=None,
        stop=None,
        step_or_count=None,
        distribution: str = "linear_count",
        **kwargs,
    ):
        """Add a frequency sweep to this SIwave AC setup.

        Parameters
        ----------
        name : CfgFrequencySweep or str
            Either a pre-built :class:`CfgFrequencySweep` object (round-trip
            use) or a name string for a new sweep.
        sweep_type : str, optional
            Sweep interpolation type.  Accepted values: ``"interpolation"``
            (default) or ``"discrete"``.
        start : str or float, optional
            Inline range start frequency, e.g. ``"1kHz"``.  When provided,
            *stop* and *step_or_count* are also required.
        stop : str or float, optional
            Inline range stop frequency, e.g. ``"1GHz"``.
        step_or_count : str, float, or int, optional
            Point count (for ``"linear_count"`` / ``"log_count"``) or step
            size (for ``"linear_scale"`` / ``"log_scale"``).
        distribution : str, optional
            Frequency distribution.  Default is ``"linear_count"``.
            Accepted values and aliases:

            * ``"linear_count"`` / ``"linearcount"`` / ``"linear count"``
            * ``"log_count"`` / ``"logcount"`` / ``"log count"``
            * ``"linear_scale"`` / ``"linearscale"`` / ``"linear scale"``
            * ``"log_scale"`` / ``"logscale"`` / ``"log scale"``
            * ``"single"``
        **kwargs
            Additional keyword arguments forwarded to
            :class:`CfgFrequencySweep` when *name* is a string.

        Returns
        -------
        CfgFrequencySweep
            The newly created (or passed-through) sweep object.

        Examples
        --------
        Inline (single call):

        >>> siwave_ac.add_frequency_sweep(
        ...     "sw1",
        ...     start="1kHz", stop="1GHz", step_or_count=100,
        ...     distribution="log_count",
        ... )

        Chained ranges:

        >>> sw = siwave_ac.add_frequency_sweep("sw2", sweep_type="interpolation")
        >>> sw.add_linear_count_frequencies("1MHz", "500MHz", 50)
        """
        if isinstance(name, self.CfgFrequencySweep):
            sweep = name
        else:
            sweep = self.CfgFrequencySweep(name=name, sweep_type=sweep_type, **kwargs)
        if start is not None and not isinstance(name, self.CfgFrequencySweep):
            _add_inline_range(sweep, start, stop, step_or_count, distribution)
        self.freq_sweep.append(sweep)
        return sweep

    def to_dict(self) -> dict:
        """Serialize this SIwave AC setup to a plain dictionary.

        Returns
        -------
        dict
            Setup payload with ``None`` values excluded.
        """
        return self.model_dump(exclude_none=True)


class CfgSIwaveDCSetup(CfgSetupDC):
    """Represent one SIwave DC setup entry."""

    class CfgDCIRSettings(CfgBaseModel):
        export_dc_thermal_data: bool = Field(False, description="Whether to export DC thermal data.")

    type: str = "siwave_dc"
    dc_slider_position: int | str
    dc_ir_settings: CfgDCIRSettings | None = None

    def __init__(self, name: str, dc_slider_position: int | str = 1, export_dc_thermal_data: bool = False, **kwargs):
        dc_ir_settings = kwargs.pop("dc_ir_settings", None)
        super().__init__(
            name=name,
            dc_slider_position=dc_slider_position,
            dc_ir_settings=dc_ir_settings or self.CfgDCIRSettings(export_dc_thermal_data=export_dc_thermal_data),
            **kwargs,
        )

    def to_dict(self) -> dict:
        """Serialize this SIwave DC setup to a plain dictionary.

        Returns
        -------
        dict
            Setup payload with ``None`` values excluded.
        """
        return self.model_dump(exclude_none=True)


class CfgHFSSSetup(CfgSetupAC):
    """Represent one HFSS setup entry with adaptive and sweep settings."""

    class CfgSingleFrequencyAdaptiveSolution(CfgBaseModel):
        adaptive_frequency: float | str = Field("5GHz", description="Frequency for single frequency adaptation.")
        max_passes: int = Field(20, description="Maximum number of adaptation passes.")
        max_delta: float | str = Field(
            "0.02", description="Maximum delta S for convergence in single frequency adaptation."
        )

    class CfgBroadbandAdaptiveSolution(CfgBaseModel):
        low_frequency: float | str = Field("1GHz", description="Low frequency for broadband adaptation.")
        high_frequency: float | str = Field("10GHz", description="High frequency for broadband.")
        max_passes: int = Field(20, description="Maximum number of adaptation passes.")
        max_delta: float | str = Field("0.02", description="Maximum delta S for convergence in broadband adaptation.")

    class CfgAutoMeshOperation(CfgBaseModel):
        enabled: bool = False
        trace_ratio_seeding: float = 3
        signal_via_side_number: int = 12

    class CfgMultiFrequencyAdaptiveSolution(CfgBaseModel):
        class CfgAdaptFrequency(CfgBaseModel):
            adaptive_frequency: float | str = Field("5GHz", description="Frequency for single frequency adaptation.")
            max_passes: int = Field(20, description="Maximum number of adaptation passes.")
            max_delta: float | str = Field(
                "0.02", description="Maximum delta S for convergence in single frequency adaptation."
            )

        adapt_frequencies: list[CfgAdaptFrequency] = Field(
            default_factory=list,
            description="List of frequencies for multi-frequency adaptation.",
        )

        def add_adaptive_frequency(self, frequency: Union[float, str], max_passes: int, max_delta: Union[float, str]):
            adapt_freq = CfgHFSSSetup.CfgMultiFrequencyAdaptiveSolution.CfgAdaptFrequency(
                adaptive_frequency=frequency,
                max_passes=max_passes,
                max_delta=max_delta,
            )
            self.adapt_frequencies.append(adapt_freq)

    class CfgLengthMeshOperation(CfgBaseModel):
        """Mesh operation export/import payload."""

        mesh_operation_type: str = Field(
            "length", validation_alias=AliasChoices("type"), description="Type of mesh operation, e.g., length."
        )

        name: str = Field(..., description="Mesh operation name.")
        max_elements: int | str | None = Field(1000, description="Maximum number of elements.")
        max_length: float | str | None = Field("1mm", description="Maximum element length (supports units).")
        restrict_length: bool | None = Field(True, description="Whether to restrict the maximum length.")
        refine_inside: bool | None = Field(False, description="Whether to refine inside the region.")
        nets_layers_list: dict[str, list] = Field(
            ...,
            description="Mapping of nets to layers (or backend-specific structure).",
        )

    type: str = "hfss"
    adapt_type: Literal["broadband", "single", "multi_frequencies"] = Field(
        "single", description="Adaptation type, e.g., broadband, single, multi_frequencies."
    )
    single_frequency_adaptive_solution: Optional[CfgSingleFrequencyAdaptiveSolution] = Field(
        default_factory=CfgSingleFrequencyAdaptiveSolution
    )
    broadband_adaptive_solution: Optional[CfgBroadbandAdaptiveSolution] = Field(
        default_factory=CfgBroadbandAdaptiveSolution
    )
    multi_frequency_adaptive_solution: Optional[CfgMultiFrequencyAdaptiveSolution] = Field(
        default_factory=CfgMultiFrequencyAdaptiveSolution
    )
    # adapt_frequencies: list[CfgAdaptFrequency] = Field(default_factory=list, description="List of frequencies for
    # single/multi_frequencies adaptation.")

    auto_mesh_operation: CfgAutoMeshOperation | None = CfgAutoMeshOperation()
    mesh_operations: list[CfgLengthMeshOperation] | None = list()

    def __init__(self, name: str, adapt_type: Literal["broadband", "single", "multi_frequencies"] = "single", **kwargs):
        super().__init__(name=name, adapt_type=adapt_type, **kwargs)

    def set_single_frequency_adaptive(self, freq: float | str = "5GHz", max_passes: int = 20, max_delta: float | str = 0.02):
        """Configure single-frequency adaptive meshing.

        Sets :attr:`adapt_type` to ``"single"`` and replaces the current
        single-frequency solution settings.

        Parameters
        ----------
        freq : str or float, optional
            Adaptive frequency, e.g. ``"5GHz"``.  Default is ``"5GHz"``.
        max_passes : int, optional
            Maximum number of adaptive passes.  Default is ``20``.
        max_delta : str or float, optional
            Convergence criterion (maximum delta-S).  Default is ``0.02``.

        Returns
        -------
        CfgHFSSSetup
            *self* — enables method chaining.

        Examples
        --------
        >>> hfss.set_single_frequency_adaptive("10GHz", max_passes=15, max_delta=0.01)
        """
        self.adapt_type = "single"
        self.single_frequency_adaptive_solution = self.CfgSingleFrequencyAdaptiveSolution(
            adaptive_frequency=freq,
            max_passes=max_passes,
            max_delta=max_delta,
        )
        return self

    def set_broadband_adaptive(
        self,
        low_freq: float | str = "1GHz",
        high_freq: float | str = "10GHz",
        max_passes: int = 20,
        max_delta: float | str = 0.02,
    ):
        """Configure broadband adaptive meshing.

        Sets :attr:`adapt_type` to ``"broadband"`` and replaces the current
        broadband solution settings.

        Parameters
        ----------
        low_freq : str or float, optional
            Lower adaptive frequency, e.g. ``"1GHz"``.  Default is ``"1GHz"``.
        high_freq : str or float, optional
            Upper adaptive frequency, e.g. ``"10GHz"``.  Default is
            ``"10GHz"``.
        max_passes : int, optional
            Maximum number of adaptive passes.  Default is ``20``.
        max_delta : str or float, optional
            Convergence criterion (maximum delta-S).  Default is ``0.02``.

        Returns
        -------
        CfgHFSSSetup
            *self* — enables method chaining.

        Examples
        --------
        >>> hfss.set_broadband_adaptive("1GHz", "20GHz", max_passes=25, max_delta=0.01)
        """
        self.adapt_type = "broadband"
        self.broadband_adaptive_solution = self.CfgBroadbandAdaptiveSolution(
            low_frequency=low_freq,
            high_frequency=high_freq,
            max_passes=max_passes,
            max_delta=max_delta,
        )
        return self

    def add_multi_frequency_adaptive(self, freq: float | str, max_passes: int = 20, max_delta: float | str = 0.02):
        """Append one adaptive point to multi-frequency adaptive meshing.

        Calling this method sets :attr:`adapt_type` to
        ``"multi_frequencies"``.  Call it multiple times to add several
        adaptive frequency points.

        Parameters
        ----------
        freq : str or float
            Adaptive frequency to add, e.g. ``"5GHz"``.
        max_passes : int, optional
            Maximum passes for this frequency.  Default is ``20``.
        max_delta : str or float, optional
            Convergence criterion.  Default is ``0.02``.

        Returns
        -------
        CfgHFSSSetup
            *self* — enables method chaining.

        Examples
        --------
        >>> hfss.add_multi_frequency_adaptive("5GHz")
        >>> hfss.add_multi_frequency_adaptive("10GHz", max_passes=30)
        """
        self.adapt_type = "multi_frequencies"
        self.multi_frequency_adaptive_solution.adapt_frequencies.append(
            self.CfgMultiFrequencyAdaptiveSolution.CfgAdaptFrequency(
                adaptive_frequency=freq,
                max_passes=max_passes,
                max_delta=max_delta,
            )
        )
        return self

    def set_auto_mesh_operation(
        self,
        enabled: bool = True,
        trace_ratio_seeding: float = 3.0,
        signal_via_side_number: int = 12,
    ):
        """Configure the automatic mesh-seeding operation.

        Parameters
        ----------
        enabled : bool, optional
            Enable automatic mesh seeding.  Default is ``True``.
        trace_ratio_seeding : float, optional
            Ratio of trace width used for seeding element size.  Default is
            ``3.0``.
        signal_via_side_number : int, optional
            Number of mesh segments per signal-via circumference.  Default is
            ``12``.

        Returns
        -------
        CfgHFSSSetup
            *self* — enables method chaining.

        Examples
        --------
        >>> hfss.set_auto_mesh_operation(enabled=True, trace_ratio_seeding=4.0)
        """
        self.auto_mesh_operation = self.CfgAutoMeshOperation(
            enabled=enabled,
            trace_ratio_seeding=trace_ratio_seeding,
            signal_via_side_number=signal_via_side_number,
        )
        return self

    def add_length_mesh_operation(
        self,
        mesh_op: CfgLengthMeshOperation | str = None,
        nets_layers_list: dict[str, list] = None,
        max_length: float | str | None = "1mm",
        max_elements: int | str | None = 1000,
        restrict_length: bool | None = True,
        refine_inside: bool | None = False,
        name: str = None,
    ):
        """Append a length-based mesh operation to this HFSS setup.

        Accepts a pre-built :class:`CfgLengthMeshOperation` payload or
        individual keyword arguments to build one inline.

        Parameters
        ----------
        mesh_op : CfgLengthMeshOperation or str, optional
            Pre-built mesh-operation object **or** a name string (legacy
            positional use).  When *None*, a new operation is constructed
            from the remaining parameters.
        nets_layers_list : dict[str, list], optional
            Mapping from net name to a list of layer names on which to apply
            the operation, e.g. ``{"SIG": ["top", "bot"]}``.
        max_length : str or float, optional
            Maximum element edge length.  Supports unit strings such as
            ``"0.5mm"``.  Default is ``"1mm"``.
        max_elements : int or str, optional
            Maximum number of mesh elements in the seeded region.  Default is
            ``1000``.
        restrict_length : bool, optional
            Whether to enforce the *max_length* constraint.  Default is
            ``True``.
        refine_inside : bool, optional
            Whether to refine inside vias.  Default is ``False``.
        name : str, optional
            Operation name.  Required when building inline.

        Returns
        -------
        CfgHFSSSetup
            *self* — enables method chaining.

        Examples
        --------
        >>> hfss.add_length_mesh_operation(
        ...     name="mesh_sig",
        ...     nets_layers_list={"SIG": ["top"]},
        ...     max_length="0.5mm",
        ... )
        """
        if isinstance(mesh_op, str):
            name = mesh_op
            mesh_op = None
        if mesh_op is None:
            mesh_op = self.CfgLengthMeshOperation(
                mesh_operation_type="length",
                name=name,
                nets_layers_list=nets_layers_list,
                max_length=max_length,
                max_elements=max_elements,
                restrict_length=restrict_length,
                refine_inside=refine_inside,
            )
        self.mesh_operations.append(mesh_op)
        return self

    def add_frequency_sweep(
        self,
        name: CfgSetupAC.CfgFrequencySweep | str,
        sweep_type: str = "interpolation",
        start=None,
        stop=None,
        step_or_count=None,
        distribution: str = "linear_count",
        **kwargs,
    ):
        """Add a frequency sweep to this HFSS setup.

        Parameters
        ----------
        name : CfgFrequencySweep or str
            Either a pre-built :class:`CfgFrequencySweep` object (round-trip
            use) or a name string for a new sweep.
        sweep_type : str, optional
            Sweep interpolation type.  ``"interpolation"`` (default) or
            ``"discrete"``.
        start : str or float, optional
            Inline range start frequency, e.g. ``"1GHz"``.  When supplied,
            *stop* and *step_or_count* are also required.
        stop : str or float, optional
            Inline range stop frequency.
        step_or_count : str, float, or int, optional
            Point count (``"linear_count"``, ``"log_count"``) or step size
            (``"linear_scale"``, ``"log_scale"``).
        distribution : str, optional
            Frequency distribution for the inline range.  Default is
            ``"linear_count"``.
        **kwargs
            Extra keyword arguments forwarded to :class:`CfgFrequencySweep`
            (e.g. ``enforce_passivity``, ``adv_dc_extrapolation``, …).

        Returns
        -------
        CfgFrequencySweep
            The newly created (or passed-through) sweep object.

        Examples
        --------
        Inline — single call describes a complete sweep:

        >>> hfss.add_frequency_sweep(
        ...     "sweep1",
        ...     start="1GHz", stop="20GHz", step_or_count=100,
        ...     distribution="linear_count",
        ...     enforce_passivity=True,
        ... )

        Chained — add multiple ranges to one sweep:

        >>> sw = hfss.add_frequency_sweep("sweep2", sweep_type="interpolation")
        >>> sw.add_linear_count_frequencies("1GHz", "10GHz", 100)
        >>> sw.add_single_frequency("0Hz")
        """
        if isinstance(name, self.CfgFrequencySweep):
            sweep = name
        else:
            sweep = self.CfgFrequencySweep(name=name, sweep_type=sweep_type, **kwargs)
        if start is not None and not isinstance(name, self.CfgFrequencySweep):
            _add_inline_range(sweep, start, stop, step_or_count, distribution)
        self.freq_sweep.append(sweep)
        return sweep

    def to_dict(self) -> dict:
        """Serialize this HFSS setup to a plain dictionary.

        Returns
        -------
        dict
            Setup payload.  Empty ``mesh_operations`` list is excluded.
        """
        d = self.model_dump(exclude_none=True)
        if not self.mesh_operations:
            d.pop("mesh_operations", None)
        return d


class CfgSetups(CfgBaseModel):
    """Collect all configured HFSS and SIwave setup entries."""

    setups: List[Union[CfgHFSSSetup, CfgSIwaveACSetup, CfgSIwaveDCSetup]] = Field(
        default_factory=list, description="List of simulation setups."
    )

    @classmethod
    def create(cls, setups: List[dict]):
        """Reconstruct a :class:`CfgSetups` instance from a list of setup dictionaries.

        Parameters
        ----------
        setups : list of dict
            Raw setup payload dictionaries.  Each dictionary must contain a
            ``"type"`` key (``"hfss"``, ``"siwave_ac"``, ``"siwave_syz"``, or
            ``"siwave_dc"``).

        Returns
        -------
        CfgSetups
            Populated setups collection.

        Raises
        ------
        ValueError
            If an unknown ``"type"`` value is encountered.
        """
        manager = cls()
        for stp in setups:
            setup_type = stp.get("type", "hfss").lower()
            if setup_type == "hfss":
                if "f_adapt" in stp:
                    # Backward compatibility for single frequency adaptation using "f_adapt" key
                    f_adatp = stp.pop("f_adapt")
                    max_passes = stp.pop("max_num_passes", 20)
                    max_delta = stp.pop("max_mag_delta_s", "0.02")

                    hfs = manager.add_hfss_setup(CfgHFSSSetup.model_validate(stp))
                    hfs.single_frequency_adaptive_solution.adaptive_frequency = f_adatp
                    hfs.single_frequency_adaptive_solution.max_passes = max_passes
                    hfs.single_frequency_adaptive_solution.max_delta = max_delta
                else:
                    manager.add_hfss_setup(CfgHFSSSetup.model_validate(stp))

            elif setup_type in ["siwave_ac", "siwave_syz"]:
                manager.add_siwave_ac_setup(CfgSIwaveACSetup.model_validate(stp))
            elif setup_type == "siwave_dc":
                manager.add_siwave_dc_setup(CfgSIwaveDCSetup.model_validate(stp))
            else:
                raise ValueError(f"Unknown setup type: {setup_type}")
        return manager

    def add_hfss_setup(self, config: CfgHFSSSetup = None, **kwargs):
        """Create and register an HFSS setup.

        Parameters
        ----------
        config : CfgHFSSSetup or str, optional
            Pre-built setup object, a name string (legacy positional argument),
            or *None* to construct a new setup from *kwargs*.
        **kwargs
            Keyword arguments forwarded to :class:`CfgHFSSSetup` when *config*
            is *None*.  Common parameters:

            - ``name`` *(str, required)* — setup name.
            - ``adapt_type`` *(str)* — ``"single"`` | ``"broadband"`` |
              ``"multi_frequencies"``.  Default is ``"single"``.

        Returns
        -------
        CfgHFSSSetup
            The newly created (or registered) setup object.

        Examples
        --------
        >>> hfss = cfg.setups.add_hfss_setup("hfss_1", adapt_type="broadband")
        >>> hfss.set_broadband_adaptive("1GHz", "20GHz")
        """
        if isinstance(config, str):
            kwargs = dict(kwargs)
            kwargs["name"] = config
            config = None
        if config:
            hfss_setup = config
        else:
            hfss_setup = CfgHFSSSetup(**kwargs)
        self.setups.append(hfss_setup)
        return hfss_setup

    def add_siwave_ac_setup(self, config: CfgSIwaveACSetup = None, **kwargs):
        """Create and register a SIwave AC setup.

        Parameters
        ----------
        config : CfgSIwaveACSetup or str, optional
            Pre-built setup object, a name string, or *None* to construct
            from *kwargs*.
        **kwargs
            Keyword arguments forwarded to :class:`CfgSIwaveACSetup`.
            Common parameters:

            - ``name`` *(str, required)* — setup name.
            - ``si_slider_position`` *(int)* — SI accuracy: 0=Speed,
              1=Balanced (default), 2=Accuracy.
            - ``pi_slider_position`` *(int)* — PI accuracy slider.
            - ``use_si_settings`` *(bool)* — ``True`` activates SI slider.

        Returns
        -------
        CfgSIwaveACSetup
            The newly created (or registered) setup object.

        Examples
        --------
        >>> siw = cfg.setups.add_siwave_ac_setup("siw_ac", si_slider_position=2)
        >>> siw.add_frequency_sweep("sw1", start="1kHz", stop="1GHz", step_or_count=100)
        """
        if isinstance(config, str):
            kwargs = dict(kwargs)
            kwargs["name"] = config
            config = None
        if config:
            siwave_ac_setup = config
        else:
            siwave_ac_setup = CfgSIwaveACSetup(**kwargs)
        self.setups.append(siwave_ac_setup)
        return siwave_ac_setup

    def add_siwave_dc_setup(self, config: CfgSIwaveDCSetup = None, **kwargs):
        """Create and register a SIwave DC setup.

        Parameters
        ----------
        config : CfgSIwaveDCSetup or str, optional
            Pre-built setup object, a name string, or *None* to construct
            from *kwargs*.
        **kwargs
            Keyword arguments forwarded to :class:`CfgSIwaveDCSetup`.
            Common parameters:

            - ``name`` *(str, required)* — setup name.
            - ``dc_slider_position`` *(int)* — DC accuracy: 0=Speed,
              1=Balanced (default), 2=Accuracy.
            - ``export_dc_thermal_data`` *(bool)* — export IR-drop thermal
              data after solving.

        Returns
        -------
        CfgSIwaveDCSetup
            The newly created (or registered) setup object.

        Examples
        --------
        >>> cfg.setups.add_siwave_dc_setup("siw_dc", dc_slider_position=1, export_dc_thermal_data=True)
        """
        if isinstance(config, str):
            kwargs = dict(kwargs)
            kwargs["name"] = config
            if "export_dc_thermal_data" in kwargs and "dc_ir_settings" not in kwargs:
                kwargs["dc_ir_settings"] = CfgSIwaveDCSetup.CfgDCIRSettings(
                    export_dc_thermal_data=kwargs.pop("export_dc_thermal_data")
                )
            config = None
        if config:
            siwave_dc_setup = config
        else:
            siwave_dc_setup = CfgSIwaveDCSetup(**kwargs)
        self.setups.append(siwave_dc_setup)
        return siwave_dc_setup

    def to_list(self):
        """Serialize all configured setups to a list of dictionaries.

        Returns
        -------
        list of dict
            Each element is the ``to_dict()`` payload of the corresponding
            setup object.
        """
        result = []
        for setup in self.setups:
            if hasattr(setup, "to_dict"):
                result.append(setup.to_dict())
            else:
                result.append(setup.model_dump(exclude_none=True))
        return result

