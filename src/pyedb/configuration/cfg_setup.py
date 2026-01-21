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

from pydantic import AliasChoices, BaseModel, Field


class CfgFrequencies(BaseModel):
    start: float | str = Field(..., description="Start frequency in Hz")
    stop: float | str = Field(..., description="Stop frequency in Hz")
    increment: int | str = Field("50Hz", validation_alias=AliasChoices("points", "samples", "step"))
    distribution: Literal[
        "linear_step", "log_step", "single", "linear_count", "log_count", "linear scale", "log scale", "linear count"
    ] = Field(
        ..., description="Frequency distribution type, e.g., linear_step, log_step, single, linear_count, log_count"
    )


class CfgFrequencySweep(BaseModel):
    name: str
    type: Literal["discrete", "interpolation"]
    frequencies: list[CfgFrequencies | str] = Field(list(), description="List of frequency definitions or strings")

    use_q3d_for_dc: bool = Field(False, description="Use Q3D for DC analysis. Only applicable for HFSS setup.")
    compute_dc_point: bool = False
    enforce_causality: bool = False
    enforce_passivity: bool = True
    adv_dc_extrapolation: bool = False

    def add_frequencies(self, freq: CfgFrequencies):
        self.frequencies.append(freq)


class CfgSetupDC(BaseModel):
    name: str


class CfgSetupAC(CfgSetupDC):
    freq_sweep: list[CfgFrequencySweep] | None = list()

    def add_frequency_sweep(self, sweep: CfgFrequencySweep):
        self.freq_sweep.append(sweep)


class CfgSIwaveACSetup(CfgSetupAC):
    type: str = "siwave_ac"
    use_si_settings: bool = Field(True, description="Use SI-Wave AC settings")
    si_slider_position: int = Field(1, description="SI slider position. Options are 0-speed, 1-balanced, 2-accuracy.")
    pi_slider_position: int = Field(1, description="PI Slider position. Options are 0-speed, 1-balanced, 2-accuracy.")


class CfgSIwaveDCSetup(CfgSetupDC):
    class CfgDCIRSettings(BaseModel):
        export_dc_thermal_data: bool = Field(False, description="Whether to export DC thermal data.")

    type: str = "siwave_dc"
    dc_slider_position: int | str
    dc_ir_settings: CfgDCIRSettings | None = None


class CfgHFSSSetup(CfgSetupAC):
    class CfgAutoMeshOperation(BaseModel):
        trace_ratio_seeding: float
        signal_via_side_number: int
        power_ground_via_side_number: int

    class CfgMeshOperation(BaseModel):
        """Mesh operation export/import payload."""

        name: str = Field(..., description="Mesh operation name.")
        type: str | None = Field(None, description="Mesh operation type identifier.")
        max_elements: int | str | None = Field(1000, description="Maximum number of elements.")
        max_length: float | str | None = Field("1mm", description="Maximum element length (supports units).")
        restrict_length: bool | None = Field(True, description="Whether to restrict the maximum length.")
        refine_inside: bool | None = Field(False, description="Whether to refine inside the region.")
        nets_layers_list: dict[str, list] = Field(
            ...,
            description="Mapping of nets to layers (or backend-specific structure).",
        )

    type: str = "hfss"
    f_adapt: float | str
    max_num_passes: int
    max_mag_delta_s: float | str

    auto_mesh_operation: CfgAutoMeshOperation | None = None
    mesh_operations: list[CfgMeshOperation] | None = list()

    def add_mesh_operation(self, **kwargs):
        mesh_op = CfgHFSSSetup.CfgMeshOperation(**kwargs)
        self.mesh_operations.append(mesh_op)
