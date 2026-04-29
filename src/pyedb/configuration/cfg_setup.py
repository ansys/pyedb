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
    start: float | str = Field(..., description="Start frequency in Hz")
    stop: float | str = Field(..., description="Stop frequency in Hz")
    increment: int | str = Field(..., validation_alias=AliasChoices("increment", "points", "samples", "step"))
    distribution: Literal[
        "linear_scale", "log_scale", "single", "linear_count", "log_count", "linear scale", "log scale", "linear count"
    ] = Field(
        ..., description="Frequency distribution type, e.g., linear_step, log_step, single, linear_count, log_count"
    )


class CfgSetupDC(CfgBaseModel):
    name: str


class CfgSetupAC(CfgSetupDC):
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
            self.frequencies.append(freq)

        def add_linear_count_frequencies(self, start, stop, count):
            self.frequencies.append(CfgFrequencies(start=start, stop=stop, increment=count, distribution="linear_count"))
            return self

        def add_log_count_frequencies(self, start, stop, count):
            self.frequencies.append(CfgFrequencies(start=start, stop=stop, increment=count, distribution="log_count"))
            return self

        def add_linear_scale_frequencies(self, start, stop, step):
            self.frequencies.append(CfgFrequencies(start=start, stop=stop, increment=step, distribution="linear_scale"))
            return self

        def add_log_scale_frequencies(self, start, stop, step):
            self.frequencies.append(CfgFrequencies(start=start, stop=stop, increment=step, distribution="log_scale"))
            return self

        def add_single_frequency(self, freq):
            self.frequencies.append(CfgFrequencies(start=freq, stop=freq, increment=1, distribution="single"))
            return self

        def to_dict(self) -> dict:
            return self.model_dump(exclude_none=True)

    freq_sweep: list[CfgFrequencySweep] | None = list()

    def add_frequency_sweep(self, sweep: CfgFrequencySweep):
        self.freq_sweep.append(sweep)


class CfgSIwaveACSetup(CfgSetupAC):
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
        name: str,
        sweep_type: str = "interpolation",
        start=None,
        stop=None,
        step_or_count=None,
        distribution: str = "linear_count",
        **kwargs,
    ):
        sweep = self.CfgFrequencySweep(name=name, sweep_type=sweep_type, **kwargs)
        if start is not None:
            _add_inline_range(sweep, start, stop, step_or_count, distribution)
        self.freq_sweep.append(sweep)
        return sweep

    def to_dict(self) -> dict:
        return self.model_dump(exclude_none=True)


class CfgSIwaveDCSetup(CfgSetupDC):
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
        return self.model_dump(exclude_none=True)


class CfgHFSSSetup(CfgSetupAC):
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
        self.adapt_type = "broadband"
        self.broadband_adaptive_solution = self.CfgBroadbandAdaptiveSolution(
            low_frequency=low_freq,
            high_frequency=high_freq,
            max_passes=max_passes,
            max_delta=max_delta,
        )
        return self

    def add_multi_frequency_adaptive(self, freq: float | str, max_passes: int = 20, max_delta: float | str = 0.02):
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
        name: str,
        sweep_type: str = "interpolation",
        start=None,
        stop=None,
        step_or_count=None,
        distribution: str = "linear_count",
        **kwargs,
    ):
        sweep = self.CfgFrequencySweep(name=name, sweep_type=sweep_type, **kwargs)
        if start is not None:
            _add_inline_range(sweep, start, stop, step_or_count, distribution)
        self.freq_sweep.append(sweep)
        return sweep

    def to_dict(self) -> dict:
        d = self.model_dump(exclude_none=True)
        if not self.mesh_operations:
            d.pop("mesh_operations", None)
        return d


class CfgSetups(CfgBaseModel):
    setups: List[Union[CfgHFSSSetup, CfgSIwaveACSetup, CfgSIwaveDCSetup]] = Field(
        default_factory=list, description="List of simulation setups."
    )

    @classmethod
    def create(cls, setups: List[dict]):
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
        """Serialize all configured setups."""
        result = []
        for setup in self.setups:
            if hasattr(setup, "to_dict"):
                result.append(setup.to_dict())
            else:
                result.append(setup.model_dump(exclude_none=True))
        return result

