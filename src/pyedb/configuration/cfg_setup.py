"""
        Add a new frequency definition to the frequencies list.

        Keyword arguments are passed to the CfgFrequencies constructor.
        """"""
                Add a new frequency definition to the frequencies list.
        
                Keyword arguments are passed to the CfgFrequencies constructor.
                """# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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

from pydantic import BaseModel, Field, AliasChoices


class CfgFrequencies(BaseModel):
    start: float|str = Field(..., description="Start frequency in Hz")
    stop: float|str = Field(..., description="Stop frequency in Hz")
    increment: int|str = Field("50Hz", validation_alias=AliasChoices("points", "samples", "step"))
    distribution: Literal["linear_step", "log_step", "single", "linear_count", "log_count"] = "linear_step"


class CfgFrequencySweep(BaseModel):
    name: str
    type: Literal["discrete", "interpolation"]
    frequencies : list[CfgFrequencies|str] = Field(list(), description="List of frequency definitions or strings")

    def add_frequencies(self, freq: CfgFrequencies):
        self.frequencies.append(freq)


class CfgSetup(BaseModel):

    name: str
    type: str

    freq_sweep : list[CfgFrequencySweep]|None = list()

    def add_frequency_sweep(self, sweep: CfgFrequencySweep):
        self.freq_sweep.append(sweep)

    def _to_dict_setup(self):
        return {
            "name": self.name,
            "type": self.type,
        }


class CfgSIwaveACSetup(CfgSetup):
    def set_parameters_to_edb(self):
        if self.name in self.pedb.setups:
            raise "Setup {} already existing. Editing it.".format(self.name)

        edb_setup = self.pedb.create_siwave_syz_setup(name=self.name)
        if self.si_slider_position is not None:
            edb_setup.si_slider_position = self.si_slider_position
        else:
            edb_setup.pi_slider_position = self.pi_slider_position
        self.apply_freq_sweep(edb_setup)

    def retrieve_parameters_from_edb(self):
        self.use_si_settings = self.pyedb_obj.use_si_settings
        self.si_slider_position = self.pyedb_obj.si_slider_position
        self.pi_slider_position = self.pyedb_obj.pi_slider_position

    def __init__(self, pedb, pyedb_obj, **kwargs):
        super().__init__(pedb, pyedb_obj, **kwargs)
        self.type = "siwave_ac"
        self.use_si_settings = kwargs.get("use_si_settings", True)
        self.si_slider_position = kwargs.get("si_slider_position", 1)
        self.pi_slider_position = kwargs.get("pi_slider_position", 1)

    def to_dict(self):
        temp = self._to_dict_setup()
        temp.update(
            {
                "use_si_settings": self.use_si_settings,
                "si_slider_position": self.si_slider_position,
                "pi_slider_position": self.pi_slider_position,
            }
        )
        return temp


class CfgSIwaveDCSetup(CfgSetup):
    def retrieve_parameters_from_edb(self):
        self.dc_slider_position = self.pyedb_obj.dc_settings.dc_slider_position
        dc_ir_settings = dict()
        dc_ir_settings["export_dc_thermal_data"] = self.pyedb_obj.dc_ir_settings.export_dc_thermal_data
        self.dc_ir_settings = dc_ir_settings

    def set_parameters_to_edb(self):
        edb_setup = self.pedb.create_siwave_dc_setup(name=self.name, dc_slider_position=self.dc_slider_position)
        edb_setup.dc_settings.dc_slider_position = self.dc_slider_position
        dc_ir_settings = self.dc_ir_settings
        edb_setup.dc_ir_settings.export_dc_thermal_data = dc_ir_settings.get("export_dc_thermal_data", False)

    def __init__(self, pedb, pyedb_obj, **kwargs):
        super().__init__(pedb, pyedb_obj, **kwargs)
        self.type = "siwave_dc"
        self.dc_slider_position = kwargs.get("dc_slider_position")
        self.dc_ir_settings = kwargs.get("dc_ir_settings", {})

    def to_dict(self):
        temp = self._to_dict_setup()
        temp.update({"dc_slider_position": self.dc_slider_position, "dc_ir_settings": self.dc_ir_settings})
        return temp


class CfgHFSSSetup(CfgSetup):
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
    f_adapt: float|str
    max_num_passes: int
    max_mag_delta_s: float|str

    auto_mesh_operation: CfgAutoMeshOperation|None = None
    mesh_operations: list[CfgMeshOperation]|None = list()

    def add_mesh_operation(self, **kwargs):
        mesh_op = CfgHFSSSetup.CfgMeshOperation(**kwargs)
        self.mesh_operations.append(mesh_op)

    def to_dict(self):
        temp = self._to_dict_setup()
        temp.update(
            {
                "f_adapt": self.f_adapt,
                "max_num_passes": self.max_num_passes,
                "max_mag_delta_s": self.max_mag_delta_s,
                "mesh_operations": self.mesh_operations,
                "freq_sweep": self.freq_sweep,
            }
        )
        return temp


class CfgSetups(BaseModel):

    setups : list[CfgHFSSSetup| CfgSIwaveACSetup| CfgSIwaveDCSetup]|None = list()

    def retrieve_parameters_from_edb(self):
        self.setups = []
        for _, setup in self._pedb.setups.items():
            if setup.type == "hfss":
                hfss = CfgHFSSSetup(self._pedb, setup, name=setup.name)
                hfss.retrieve_parameters_from_edb()
                self.setups.append(hfss)
            elif setup.type == "siwave_dc":
                siwave_dc = CfgSIwaveDCSetup(self._pedb, setup, name=setup.name)
                siwave_dc.retrieve_parameters_from_edb()
                self.setups.append(siwave_dc)
            elif setup.type == "siwave_ac":
                siwave_ac = CfgSIwaveACSetup(self._pedb, setup, name=setup.name)
                siwave_ac.retrieve_parameters_from_edb()
                self.setups.append(siwave_ac)



    def apply(self):
        for s in self.setups:
            s.set_parameters_to_edb()

    def to_dict(self):
        return [i.to_dict() for i in self.setups]
