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
        type: Literal["discrete", "interpolation"]
        frequencies: list[CfgFrequencies | str] = Field(list(), description="List of frequency definitions or strings")

        use_q3d_for_dc: bool = Field(False, description="Use Q3D for DC analysis. Only applicable for HFSS setup.")
        compute_dc_point: bool = Field(False, description="AC/DC Merge checkbox in GUI.")
        enforce_causality: bool = False
        enforce_passivity: bool = True
        adv_dc_extrapolation: bool = False

        use_hfss_solver_regions: bool = Field(False)
        hfss_solver_region_setup_name: str | None = "<default>"
        hfss_solver_region_sweep_name: str | None = "<default>"

        def add_frequencies(self, freq: CfgFrequencies):
            self.frequencies.append(freq)

    freq_sweep: list[CfgFrequencySweep] | None = list()

    def add_frequency_sweep(self, sweep: CfgFrequencySweep):
        self.freq_sweep.append(sweep)


class CfgSIwaveACSetup(CfgSetupAC):
    type: str = "siwave_ac"
    use_si_settings: bool = Field(True, description="Use SI-Wave AC settings")
    si_slider_position: int = Field(1, description="SI slider position. Options are 0-speed, 1-balanced, 2-accuracy.")
    pi_slider_position: int = Field(1, description="PI Slider position. Options are 0-speed, 1-balanced, 2-accuracy.")


class CfgSIwaveDCSetup(CfgSetupDC):
    class CfgDCIRSettings(CfgBaseModel):
        export_dc_thermal_data: bool = Field(False, description="Whether to export DC thermal data.")

    type: str = "siwave_dc"
    dc_slider_position: int | str
    dc_ir_settings: CfgDCIRSettings | None = None


class CfgHFSSSetup(CfgSetupAC):
    class CfgSingleFrequencyAdaptiveSolution(CfgBaseModel):
        adaptive_frequency: float | str = Field("5GHz", description="Frequency for single frequency adaptation.")
        max_passes: int = Field(20, description="Maximum number of adaptation passes.")
        max_delta: float | str = Field("0.02",
                                       description="Maximum delta S for convergence in single frequency adaptation.")

    class CfgBroadbandAdaptiveSolution(CfgBaseModel):
        low_frequency: float | str = Field("1GHz", description="Low frequency for broadband adaptation.")
        high_frequency: float | str = Field("10GHz", description="High frequency for broadband.")
        max_passes: int = Field(20, description="Maximum number of adaptation passes.")
        max_delta: float | str = Field("0.02", description="Maximum delta S for convergence in broadband adaptation.")

    class CfgAutoMeshOperation(CfgBaseModel):
        enabled: bool = False
        trace_ratio_seeding: float = 3
        signal_via_side_number: int = 12
        power_ground_via_side_number: int = 6

    class CfgMultiFrequencyAdaptiveSolution(CfgBaseModel):
        class CfgAdaptFrequency(CfgBaseModel):
            adaptive_frequency: float | str = Field("5GHz", description="Frequency for single frequency adaptation.")
            max_passes: int = Field(20, description="Maximum number of adaptation passes.")
            max_delta: float | str = Field("0.02",
                                           description="Maximum delta S for convergence in single frequency adaptation.")

        adapt_frequencies: list[CfgAdaptFrequency] = Field(
            default=[CfgAdaptFrequency(adaptive_frequency="1GHz"), CfgAdaptFrequency(adaptive_frequency="10GHz")],
            description="List of frequencies for multi-frequency adaptation.")

        def add_adaptive_frequency(self, frequency: Union[float, str], max_passes: int, max_delta: Union[float, str]):
            adapt_freq = CfgHFSSSetup.CfgMultiFrequencyAdaptiveSolution.CfgAdaptFrequency(
                adaptive_frequency=frequency,
                max_passes=max_passes,
                max_delta=max_delta,
            )
            self.adapt_frequencies.append(adapt_freq)

    class CfgLengthMeshOperation(CfgBaseModel):
        """Mesh operation export/import payload."""
        mesh_operation_type: str = Field("length",
                                         validation_alias=AliasChoices("type"),
                                         description="Type of mesh operation, e.g., length.")

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
    # adapt_frequencies: list[CfgAdaptFrequency] = Field(default_factory=list, description="List of frequencies for single/multi_frequencies adaptation.")

    auto_mesh_operation: CfgAutoMeshOperation | None = CfgAutoMeshOperation()
    mesh_operations: list[CfgLengthMeshOperation] | None = list()

    def add_length_mesh_operation(self, mesh_op: CfgLengthMeshOperation):
        self.mesh_operations.append(mesh_op)


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
        if config:
            hfss_setup = config
        else:
            hfss_setup = CfgHFSSSetup.model_validate(kwargs)
        self.setups.append(hfss_setup)
        return hfss_setup

    def add_siwave_ac_setup(self, config: CfgSIwaveACSetup = None, **kwargs):
        if config:
            siwave_ac_setup = config
        else:
            siwave_ac_setup = CfgSIwaveACSetup.model_validate(kwargs)
        self.setups.append(siwave_ac_setup)
        return siwave_ac_setup

    def add_siwave_dc_setup(self, config: CfgSIwaveDCSetup = None, **kwargs):
        if config:
            siwave_dc_setup = config
        else:
            siwave_dc_setup = CfgSIwaveDCSetup.model_validate(kwargs)
        self.setups.append(siwave_dc_setup)
        return siwave_dc_setup
