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

from ansys.edb.core.simulation_setup.hfss_pi_simulation_settings import (
    HFSSPIGeneralSettings as CoreHFSSPIGeneralSettings,
    HFSSPIModelType as CoreHFSSPIModelType,
)

_mapping_model_type = {
    "pcb": CoreHFSSPIModelType.PCB,
    "rdl": CoreHFSSPIModelType.RDL,
    "package": CoreHFSSPIModelType.PACKAGE,
}


class HFSSPIGeneralSettings:
    """PyEDB HFSS PI general settings class."""

    def __init__(self, pedb, core: "CoreHFSSPIGeneralSettings"):
        self.core = core
        self._pedb = pedb

    @property
    def mesh_region_name(self) -> str:
        """
        Mesh region name.

        Returns
        -------
        str
            Mesh region name.

        """
        return self.core.mesh_region_name

    @mesh_region_name.setter
    def mesh_region_name(self, value: str):
        self.core.mesh_region_name = value

    @property
    def model_type(self) -> str:
        """
        Model type.

        Returns
        -------
        str
            Model type, possible values are "pcb", "rdl", and "package".

        """
        return self.core.model_type.name.lower()

    @model_type.setter
    def model_type(self, value: str):
        if value.lower() not in _mapping_model_type:
            raise ValueError(f"Invalid model type: {value}. Valid options are: {list(_mapping_model_type.keys())}")
        self.core.model_type = _mapping_model_type[value.lower()]

    @property
    def use_auto_mesh_region(self) -> bool:
        """
        Flag indicating if auto mesh regions are used.

        Returns
        -------
        bool
            True if auto mesh region is used, False otherwise.

        """
        return self.core.use_auto_mesh_region

    @use_auto_mesh_region.setter
    def use_auto_mesh_region(self, value: bool):
        self.core.use_auto_mesh_region = value

    @property
    def use_mesh_region(self) -> bool:
        """
        Flag indicating if mesh region is used.

        Returns
        -------
        bool
            True if mesh region is used, False otherwise.

        """
        return self.core.use_mesh_region

    @use_mesh_region.setter
    def use_mesh_region(self, value: bool):
        self.core.use_mesh_region = value
