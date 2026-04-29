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
"""Build the ``stackup`` configuration section.

This module wraps stackup-related configuration models with fluent helpers for
materials, layers, roughness, and etching definitions.
"""

from typing import List, Optional, Union

from pydantic import BaseModel, Field


class CfgMaterialPropertyThermalModifier(BaseModel):
    property_name: str
    basic_quadratic_c1: float = 0
    basic_quadratic_c2: float = 0
    basic_quadratic_temperature_reference: float = 22
    advanced_quadratic_lower_limit: float = -273.15
    advanced_quadratic_upper_limit: float = 1000
    advanced_quadratic_auto_calculate: bool = True
    advanced_quadratic_lower_constant: float = 1
    advanced_quadratic_upper_constant: float = 1


class MaterialProperties(BaseModel):
    """Store material properties."""

    conductivity: Optional[Union[str, float]] = None
    dielectric_loss_tangent: Optional[Union[str, float]] = None
    magnetic_loss_tangent: Optional[Union[str, float]] = None
    mass_density: Optional[Union[str, float]] = None
    permittivity: Optional[Union[str, float]] = None
    permeability: Optional[Union[str, float]] = None
    poisson_ratio: Optional[Union[str, float]] = None
    specific_heat: Optional[Union[str, float]] = None
    thermal_conductivity: Optional[Union[str, float]] = None
    youngs_modulus: Optional[Union[str, float]] = None
    thermal_expansion_coefficient: Optional[Union[str, float]] = None
    dc_conductivity: Optional[Union[str, float]] = None
    dc_permittivity: Optional[Union[str, float]] = None
    dielectric_model_frequency: Optional[Union[str, float]] = None
    loss_tangent_at_frequency: Optional[Union[str, float]] = None
    permittivity_at_frequency: Optional[Union[str, float]] = None


class CfgMaterial(MaterialProperties):
    name: Optional[str] = None
    thermal_modifiers: Optional[list[CfgMaterialPropertyThermalModifier]] = None

    def __init__(
        self,
        name: str | None = None,
        conductivity: Optional[Union[str, float]] = None,
        permittivity: Optional[Union[str, float]] = None,
        dielectric_loss_tangent: Optional[Union[str, float]] = None,
        magnetic_loss_tangent: Optional[Union[str, float]] = None,
        mass_density: Optional[Union[str, float]] = None,
        permeability: Optional[Union[str, float]] = None,
        poisson_ratio: Optional[Union[str, float]] = None,
        specific_heat: Optional[Union[str, float]] = None,
        thermal_conductivity: Optional[Union[str, float]] = None,
        youngs_modulus: Optional[Union[str, float]] = None,
        thermal_expansion_coefficient: Optional[Union[str, float]] = None,
        dc_conductivity: Optional[Union[str, float]] = None,
        dc_permittivity: Optional[Union[str, float]] = None,
        dielectric_model_frequency: Optional[Union[str, float]] = None,
        loss_tangent_at_frequency: Optional[Union[str, float]] = None,
        permittivity_at_frequency: Optional[Union[str, float]] = None,
        thermal_modifiers: Optional[list[CfgMaterialPropertyThermalModifier]] = None,
        **kwargs,
    ):
        super().__init__(
            name=name,
            conductivity=conductivity,
            permittivity=permittivity,
            dielectric_loss_tangent=dielectric_loss_tangent,
            magnetic_loss_tangent=magnetic_loss_tangent,
            mass_density=mass_density,
            permeability=permeability,
            poisson_ratio=poisson_ratio,
            specific_heat=specific_heat,
            thermal_conductivity=thermal_conductivity,
            youngs_modulus=youngs_modulus,
            thermal_expansion_coefficient=thermal_expansion_coefficient,
            dc_conductivity=dc_conductivity,
            dc_permittivity=dc_permittivity,
            dielectric_model_frequency=dielectric_model_frequency,
            loss_tangent_at_frequency=loss_tangent_at_frequency,
            permittivity_at_frequency=permittivity_at_frequency,
            thermal_modifiers=thermal_modifiers,
            **kwargs,
        )

    def to_dict(self) -> dict:
        """Serialize the material, excluding ``None`` values."""
        return self.model_dump(exclude_none=True)


class CfgHurayRoughnessModel(BaseModel):
    model: str = "huray"
    nodule_radius: Optional[str | float | int] = None  # e.g., '0.1um'
    surface_ratio: Optional[str | float | int] = None  # e.g., '1'
    model_config = {"extra": "forbid"}


class CfgGroisseRoughnessModel(BaseModel):
    model: str = "groisse"
    roughness: Optional[str | float | int] = None

    model_config = {"extra": "forbid"}


class CfgRoughnessModel(BaseModel):
    enabled: Optional[bool] = False
    top: CfgHurayRoughnessModel | CfgGroisseRoughnessModel | None = None
    bottom: CfgHurayRoughnessModel | CfgGroisseRoughnessModel | None = None
    side: CfgHurayRoughnessModel | CfgGroisseRoughnessModel | None = None

    model_config = {"extra": "forbid"}


class EtchingModel(BaseModel):
    factor: Optional[Union[float, str]] = 0.5
    etch_power_ground_nets: Optional[bool] = False
    enabled: Optional[bool] = False


class CfgLayer(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    material: Optional[str] = None
    fill_material: Optional[str] = None
    thickness: Optional[Union[float, str]] = None
    roughness: Optional[CfgRoughnessModel] = None
    etching: Optional[EtchingModel] = None

    def __init__(
        self,
        name: str | None = None,
        type: Optional[str] = None,
        material: Optional[str] = None,
        fill_material: Optional[str] = None,
        thickness: Optional[Union[str, float]] = None,
        roughness: Optional[CfgRoughnessModel] = None,
        etching: Optional[EtchingModel] = None,
        **kwargs,
    ):
        super().__init__(
            name=name,
            type=type,
            material=material,
            fill_material=fill_material,
            thickness=thickness,
            roughness=roughness,
            etching=etching,
            **kwargs,
        )

    def set_huray_roughness(
        self,
        nodule_radius: Union[str, float],
        surface_ratio: Union[str, float],
        enabled: bool = True,
        top: bool = True,
        bottom: bool = True,
        side: bool = True,
    ) -> "CfgLayer":
        """Configure Huray roughness on selected surfaces."""
        huray = CfgHurayRoughnessModel(nodule_radius=nodule_radius, surface_ratio=surface_ratio)
        self.roughness = CfgRoughnessModel(
            enabled=enabled,
            top=huray if top else None,
            bottom=huray if bottom else None,
            side=huray if side else None,
        )
        return self

    def set_groisse_roughness(
        self,
        roughness_value: Union[str, float],
        enabled: bool = True,
        top: bool = True,
        bottom: bool = True,
        side: bool = True,
    ) -> "CfgLayer":
        """Configure Groisse roughness on selected surfaces."""
        groisse = CfgGroisseRoughnessModel(roughness=roughness_value)
        self.roughness = CfgRoughnessModel(
            enabled=enabled,
            top=groisse if top else None,
            bottom=groisse if bottom else None,
            side=groisse if side else None,
        )
        return self

    def set_etching(
        self,
        factor: Union[float, str] = 0.5,
        etch_power_ground_nets: bool = False,
        enabled: bool = True,
    ) -> "CfgLayer":
        """Configure the etching model."""
        self.etching = EtchingModel(
            factor=factor,
            etch_power_ground_nets=etch_power_ground_nets,
            enabled=enabled,
        )
        return self

    def to_dict(self) -> dict:
        """Serialize the layer definition."""
        return self.model_dump(exclude_none=True)


class CfgStackup(BaseModel):
    materials: List[CfgMaterial] = Field(default_factory=list)
    layers: List[CfgLayer] = Field(default_factory=list)

    def add_material(self, name, **kwargs):
        mat = CfgMaterial(name=name, **kwargs)
        self.materials.append(mat)
        return mat

    def add_layer(
        self,
        name,
        type: Optional[str] = None,
        material: Optional[str] = None,
        fill_material: Optional[str] = None,
        thickness: Optional[Union[str, float]] = None,
    ):
        """Append a layer definition."""
        return self.add_layer_at_bottom(
            name,
            type=type,
            material=material,
            fill_material=fill_material,
            thickness=thickness,
        )

    def add_layer_at_bottom(self, name, **kwargs):
        layer = CfgLayer(name=name, **kwargs)
        self.layers.append(layer)
        return layer

    def add_signal_layer(
        self,
        name: str,
        material: str = "copper",
        fill_material: str = "FR4_epoxy",
        thickness: Union[str, float] = "35um",
    ):
        """Add a signal layer with conductor defaults."""
        return self.add_layer(name, type="signal", material=material, fill_material=fill_material, thickness=thickness)

    def add_dielectric_layer(
        self,
        name: str,
        material: str = "FR4_epoxy",
        thickness: Union[str, float] = "100um",
    ):
        """Add a dielectric layer with common defaults."""
        return self.add_layer(name, type="dielectric", material=material, thickness=thickness)

    def to_dict(self) -> dict:
        """Serialize the configured stackup."""
        d = self.model_dump(exclude_none=True)
        return {k: v for k, v in d.items() if v != []}
