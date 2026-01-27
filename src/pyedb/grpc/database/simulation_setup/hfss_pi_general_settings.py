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
    HFSSPIGeneralSettings as GrpcHFSSPIGeneralSettings,
    HFSSPIModelType as GrpcHFSSPIModelType,
    HFSSPISimulationPreference as GrpcHFSSPISimulationPreference,
    SurfaceRoughnessModel as GrpcSurfaceRoughnessModel,
)

_mapping_model_type = {
    "pcb": GrpcHFSSPIModelType.PCB,
    "rdl": GrpcHFSSPIModelType.RDL,
    "package": GrpcHFSSPIModelType,
}
_mapping_simulation_preference = {
    "balanced": GrpcHFSSPISimulationPreference.BALANCED,
    "accuracy": GrpcHFSSPISimulationPreference.ACCURACY,
}

_mapping_surface_roughness = {
    "exponential": GrpcSurfaceRoughnessModel.EXPONENTIAL,
    "hammerstad": GrpcSurfaceRoughnessModel.HAMMERSTAD,
    "": GrpcSurfaceRoughnessModel.NONE,
}


class HFSSPIGeneralSettings:
    """PyEDB HFSS PI general settings class."""

    def __init__(self, pedb, core: "GrpcHFSSPIGeneralSettings"):
        self.core = core
        self._pedb = pedb

    @property
    def include_enhanced_bondwire_modeling(self) -> bool:
        """Flag indicating whether to include enhanced bondwire modeling.

        Returns
        -------
        bool
            True if include enhanced bondwire modeling is enabled, False otherwise.

        """
        return self.core.include_enhanced_bondwire_modeling

    @include_enhanced_bondwire_modeling.setter
    def include_enhanced_bondwire_modeling(self, value: bool):
        self.core.include_enhanced_bondwire_modeling = value

    @property
    def min_plane_area_to_mesh(self) -> str:
        """(General Mode Only) The minimum plane area to mesh.

        Returns
        -------
        str
            Minimum plane area to mesh as a string with units (e.g., "0.1mm2").

        """
        return self.core.min_plane_area_to_mesh

    @min_plane_area_to_mesh.setter
    def min_plane_area_to_mesh(self, value: str):
        self.core.min_plane_area_to_mesh = value

    @property
    def min_void_area_to_mesh(self) -> str:
        """(General Mode Only) The minimum void area to mesh.

        Returns
        -------
        str
            Minimum void area to mesh as a string with units (e.g., "0.1mm2").

        """
        return self.core.min_void_area_to_mesh

    @min_void_area_to_mesh.setter
    def min_void_area_to_mesh(self, value: str):
        self.core.min_void_area_to_mesh = value

    @property
    def model_type(self) -> str:
        """Get the model type.

        Returns
        -------
        str
            The model type.

        """
        for key, val in _mapping_model_type.items():
            if val == self.core.model_type:
                return key
        return "unknown"  # Fallback in case of an unmapped type

    @model_type.setter
    def model_type(self, value: str):
        if value.lower() in _mapping_model_type:
            self.core.model_type = _mapping_model_type[value.lower()]
        else:
            raise ValueError(f"Invalid model type: {value}. Valid options are: {list(_mapping_model_type.keys())}")

    @property
    def perform_erc(self) -> bool:
        """(General Mode Only) Flag indicating whether to perform error checking while generating the solver input file.

        Returns
        -------
        bool
            True if perform ERC is enabled, False otherwise.

        """
        return self.core.perform_erc

    @perform_erc.setter
    def perform_erc(self, value: bool):
        self.core.perform_erc = value

    @property
    def rms_surface_roughness(self) -> str:
        """The RMS surface roughness.

        Returns
        -------
        str
            RMS surface roughness as a string with units (e.g., "0.5um").

        """
        return self.core.rms_surface_roughness

    @rms_surface_roughness.setter
    def rms_surface_roughness(self, value: str):
        self.core.rms_surface_roughness = value

    @property
    def simulation_preference(self) -> str:
        """Get the simulation preference.

        Returns
        -------
        str
            The simulation preference.

        """
        for key, val in _mapping_simulation_preference.items():
            if val == self.core.simulation_preference:
                return key
        return "unknown"  # Fallback in case of an unmapped type

    @simulation_preference.setter
    def simulation_preference(self, value: str):
        if value.lower() in _mapping_simulation_preference:
            self.core.simulation_preference = _mapping_simulation_preference[value.lower()]
        else:
            raise ValueError(
                f"Invalid simulation preference: {value}. "
                f"Valid options are: {list(_mapping_simulation_preference.keys())}"
            )

    @property
    def snap_length_threshold(self) -> str:
        """(General Mode Only) The snap length threshold.

        Returns
        -------
        str
            Snap length threshold as a string with units (e.g., "0.1mm").

        """
        return self.core.snap_length_threshold

    @snap_length_threshold.setter
    def snap_length_threshold(self, value: str):
        self.core.snap_length_threshold = value

    @property
    def surface_roughness_model(self) -> str:
        """Get the surface roughness model.

        Returns
        -------
        str
            The surface roughness model.

        """
        for key, val in _mapping_surface_roughness.items():
            if val == self.core.surface_roughness_model:
                return key
        return "unknown"  # Fallback in case of an unmapped type

    @surface_roughness_model.setter
    def surface_roughness_model(self, value: str):
        if value.lower() in _mapping_surface_roughness:
            self.core.surface_roughness_model = _mapping_surface_roughness[value.lower()]
        else:
            raise ValueError(
                f"Invalid surface roughness model: {value}. "
                f"Valid options are: {list(_mapping_surface_roughness.keys())}"
            )
