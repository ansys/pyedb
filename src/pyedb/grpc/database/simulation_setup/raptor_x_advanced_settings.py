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
# FITNE SS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ansys.edb.core.simulation_setup.raptor_x_simulation_settings import (
        RaptorXAdvancedSettings as GrpcRaptorXAdvancedSettings,
    )


class RaptorXAdvancedSettings:
    """Raptor X advanced settings class."""

    def __init__(self, pedb, core: "GrpcRaptorXAdvancedSettings"):
        self.core = core
        self._pedb = pedb

    @property
    def advanced_options(self) -> dict[str, list[str]]:
        """Get advanced options as a dictionary."""
        return self.core.advanced_options

    @property
    def auto_removal_sliver_poly(self) -> float:
        """Automatic sliver polygon removal tolerance."""
        return self.core.auto_removal_sliver_poly

    @auto_removal_sliver_poly.setter
    def auto_removal_sliver_poly(self, value: float):
        """Set automatic sliver polygon removal tolerance."""
        self.core.auto_removal_sliver_poly = value

    @property
    def cells_per_wavelength(self) -> int:
        """Number of cells that fit under each wavelength."""
        return self.core.cells_per_wavelength

    @cells_per_wavelength.setter
    def cells_per_wavelength(self, value: int):
        """Set number of cells that fit under each wavelength."""
        self.core.cells_per_wavelength = value

    @property
    def edge_mesh(self) -> float:
        """Thickness and width of the exterior conductor filament."""
        return self._pedb.value(self.core.edge_mesh)

    @edge_mesh.setter
    def edge_mesh(self, value: float):
        """Set thickness and width of the exterior conductor filament."""
        self.core.edge_mesh = str(self._pedb.value(value))

    @property
    def eliminate_slit_per_holes(self) -> float:
        """Threshold for strain or thermal relief slits and hole polygon areas."""
        return self.core.eliminate_slit_per_holes

    @eliminate_slit_per_holes.setter
    def eliminate_slit_per_holes(self, value: float):
        """Set threshold for strain or thermal relief slits and hole polygon areas."""
        self.core.eliminate_slit_per_holes = value

    @property
    def mesh_frequency(self) -> float:
        """Frequency at which the mesh is generated."""
        return self._pedb.value(self.core.mesh_frequency)

    @mesh_frequency.setter
    def mesh_frequency(self, value: float):
        """Set frequency at which the mesh is generated."""
        self.core.mesh_frequency = str(self._pedb.value(value))

    @property
    def net_settings_options(self) -> dict[str, list[str]]:
        """Get net settings options as a dictionary."""
        return self.core.net_settings_options

    @net_settings_options.setter
    def net_settings_options(self, value: dict[str, list[str]]):
        """Set net settings options as a dictionary."""
        self.core.net_settings_options = value

    @property
    def override_shrink_factor(self) -> float:
        """Override shrink factor for polygon edges."""
        return self.core.override_shrink_factor

    @override_shrink_factor.setter
    def override_shrink_factor(self, value: float):
        self.core.override_shrink_factor = value

    @property
    def plane_projection_factor(self) -> float:
        """Plane projection factor for reducing the mesh complexity of large metal planes."""
        return self.core.plane_projection_factor

    @plane_projection_factor.setter
    def plane_projection_factor(self, value: float):
        self.core.plane_projection_factor = value

    @property
    def use_accelerate_via_extraction(self) -> bool:
        """Flag indicating if neighboring vias are simplified/merged."""
        return self.core.use_accelerate_via_extraction

    @use_accelerate_via_extraction.setter
    def use_accelerate_via_extraction(self, value: bool):
        self.core.use_accelerate_via_extraction = value

    @property
    def use_auto_removal_sliver_poly(self) -> bool:
        """Flag indicating if slight misaligned overlapping polygons are to be automatically aligned."""
        return self.core.use_auto_removal_sliver_poly

    @use_auto_removal_sliver_poly.setter
    def use_auto_removal_sliver_poly(self, value: bool):
        self.core.use_auto_removal_sliver_poly = value

    @property
    def use_cells_per_wavelength(self) -> bool:
        """Flag indicating if cells per wavelength are used."""
        return self.core.use_cells_per_wavelength

    @use_cells_per_wavelength.setter
    def use_cells_per_wavelength(self, value: bool):
        self.core.use_cells_per_wavelength = value

    @property
    def use_edge_mesh(self) -> bool:
        """Flag indicating if edge mesh is used."""
        return self.core.use_edge_mesh

    @use_edge_mesh.setter
    def use_edge_mesh(self, value: bool):
        self.core.use_edge_mesh = value

    @property
    def use_eliminate_slit_per_holes(self) -> bool:
        """Flag indicating if elimination of slits and holes is used."""
        return self.core.use_eliminate_slit_per_holes

    @use_eliminate_slit_per_holes.setter
    def use_eliminate_slit_per_holes(self, value: bool):
        self.core.use_eliminate_slit_per_holes = value

    @property
    def use_enable_advanced_cap_effects(self) -> bool:
        """Flag indicating if capacitance-related effects such as conformal dielectrics are applied."""
        return self.core.use_enable_advanced_cap_effects

    @use_enable_advanced_cap_effects.setter
    def use_enable_advanced_cap_effects(self, value: bool):
        self.core.use_enable_advanced_cap_effects = value

    @property
    def use_enable_etch_transform(self) -> bool:
        """Flag indicating if layout is "pre-distorted" based on foundry rules."""
        return self.core.use_enable_etch_transform

    @use_enable_etch_transform.setter
    def use_enable_etch_transform(self, value: bool):
        self.core.use_enable_etch_transform = value

    @property
    def defuse_enable_hybrid_extraction(self) -> bool:
        """Flag indicating if the modeler is to split the layout into two parts in an attempt to decrease
        the complexity."""
        return self.core.defuse_enable_hybrid_extraction

    @defuse_enable_hybrid_extraction.setter
    def defuse_enable_hybrid_extraction(self, value: bool):
        self.core.defuse_enable_hybrid_extraction = value

    @property
    def use_enable_substrate_network_extraction(self) -> bool:
        """Flag indicating if modeling of substrate coupling effects is enabled using equivalent distributed RC
        networks."""
        return self.core.use_enable_substrate_network_extraction

    @use_enable_substrate_network_extraction.setter
    def use_enable_substrate_network_extraction(self, value: bool):
        self.core.use_enable_substrate_network_extraction = value

    @property
    def use_extract_floating_metals_dummy(self) -> bool:
        """Flag indicating if floating metals are modeled as dummy fills."""
        return self.core.use_extract_floating_metals_dummy

    @use_extract_floating_metals_dummy.setter
    def use_extract_floating_metals_dummy(self, value: bool):
        self.core.use_extract_floating_metals_dummy = value

    @property
    def use_extract_floating_metals_floating(self) -> bool:
        """Flag indicating if floating metals are modeled as floating nets."""
        return self.core.use_extract_floating_metals_floating

    @use_extract_floating_metals_floating.setter
    def use_extract_floating_metals_floating(self, value: bool):
        self.core.use_extract_floating_metals_floating = value

    @property
    def use_lde(self) -> bool:
        """Flag indicating if variations in resistivity are taken into account."""
        return self.core.use_lde

    @use_lde.setter
    def use_lde(self, value: bool):
        self.core.use_lde = value

    @property
    def use_mesh_frequency(self) -> bool:
        """Flag indicating if mesh frequency is used."""
        return self.core.use_mesh_frequency

    @use_mesh_frequency.setter
    def use_mesh_frequency(self, value: bool):
        self.core.use_mesh_frequency = value

    @property
    def use_override_shrink_factor(self) -> bool:
        """Flag indicating if override shrink factor is used."""
        return self.core.use_override_shrink_factor

    @use_override_shrink_factor.setter
    def use_override_shrink_factor(self, value: bool):
        self.core.use_override_shrink_factor = value

    @property
    def use_plane_projection_factor(self) -> bool:
        """Flag indicating if plane projection factor is used."""
        return self.core.use_plane_projection_factor

    @use_plane_projection_factor.setter
    def use_plane_projection_factor(self, value: bool):
        self.core.use_plane_projection_factor = value

    @property
    def use_relaxed_z_axis(self) -> bool:
        """Flag indicating if simplified meshing is used along the z axis."""
        return self.core.use_relaxed_z_axis

    @use_relaxed_z_axis.setter
    def use_relaxed_z_axis(self, value: bool):
        self.core.use_relaxed_z_axis = value
