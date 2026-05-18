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
from typing import Any

from pydantic import BaseModel
from pydantic import Field


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

    conductivity: str | float | None = None
    dielectric_loss_tangent: str | float | None = None
    magnetic_loss_tangent: str | float | None = None
    mass_density: str | float | None = None
    permittivity: str | float | None = None
    permeability: str | float | None = None
    poisson_ratio: str | float | None = None
    specific_heat: str | float | None = None
    thermal_conductivity: str | float | None = None
    youngs_modulus: str | float | None = None
    thermal_expansion_coefficient: str | float | None = None
    dc_conductivity: str | float | None = None
    dc_permittivity: str | float | None = None
    dielectric_model_frequency: str | float | None = None
    loss_tangent_at_frequency: str | float | None = None
    permittivity_at_frequency: str | float | None = None


class CfgMaterial(MaterialProperties):
    name: str | None = None
    thermal_modifiers: list[CfgMaterialPropertyThermalModifier] | None = None

    model_config = {"extra": "forbid"}


class CfgHurayRoughnessModel(BaseModel):
    model: str = "huray"
    nodule_radius: str | float | int | None = None  # e.g., '0.1um'
    surface_ratio: str | float | int | None = None  # e.g., '1'
    model_config = {"extra": "forbid"}


class CfgGroisseRoughnessModel(BaseModel):
    model: str = "groisse"
    roughness: str | float | int | None = None

    model_config = {"extra": "forbid"}


class CfgRoughnessModel(BaseModel):
    enabled: bool | None = False
    top: CfgHurayRoughnessModel | CfgGroisseRoughnessModel | None = None
    bottom: CfgHurayRoughnessModel | CfgGroisseRoughnessModel | None = None
    side: CfgHurayRoughnessModel | CfgGroisseRoughnessModel | None = None

    model_config = {"extra": "forbid"}


class EtchingModel(BaseModel):
    factor: float | str | None = 0.5
    etch_power_ground_nets: bool | None = False
    enabled: bool | None = False


class CfgLayer(BaseModel):
    name: str | None = None
    type: str | None = "signal"
    material: str | None = None
    fill_material: str | None = None
    thickness: float | str | None = None
    roughness: CfgRoughnessModel | None = None
    etching: EtchingModel | None = None
    color: tuple | None = None

    model_config = {"extra": "forbid"}


class CfgStackup(BaseModel):
    materials: list[CfgMaterial] = Field(default_factory=list)
    layers: list[CfgLayer] = Field(default_factory=list)

    def add_material(
        self,
        name: str | None = None,
        config: CfgMaterial | dict[str, Any] | None = None,
        **kwargs,
    ) -> CfgMaterial:
        """Add a material to the stackup using Pydantic validation.

        Parameters
        ----------
        name : str, optional
            Material name. If provided, it overrides the name from ``config``.
        config : CfgMaterial | dict, optional
            Material payload as a ``CfgMaterial`` instance or dictionary.

        Returns
        -------
        CfgMaterial
            The validated material object appended to ``materials``.

        """
        payload = {}
        if config is not None:
            if isinstance(config, CfgMaterial):
                # Convert to dict so kwargs/name can override deterministically.
                payload = config.model_dump(exclude_none=True)
            else:
                payload = dict(config)

        payload.update(kwargs)
        if name is not None:
            payload["name"] = name

        material = CfgMaterial.model_validate(payload)
        self.materials.append(material)
        return material

    def add_layer_at_bottom(
        self,
        name: str | None = None,
        config: CfgLayer | dict[str, Any] | None = None,
        **kwargs,
    ) -> CfgLayer:
        """Add a layer to the stackup using Pydantic validation.

        Parameters
        ----------
        name : str, optional
            Layer name. If provided, it overrides the name from ``config``.
        config : CfgLayer | dict, optional
            Layer payload as a ``CfgLayer`` instance or dictionary.
        **kwargs
            Extra layer attributes applied after ``config`` values.

        Returns
        -------
        CfgLayer
            The validated layer object appended to ``layers``.

        """
        payload = {}
        if config is not None:
            if isinstance(config, CfgLayer):
                payload = config.model_dump(exclude_none=True)
            else:
                payload = dict(config)

        if name is not None:
            payload["name"] = name

        payload.update(kwargs)
        layer = CfgLayer.model_validate(payload)
        self.layers.append(layer)
        return layer

    def normalize_thickness(self, unit="m"):
        if unit == "mm":
            multiplier = 1000
        elif unit == "cm":
            multiplier = 1e2
        elif unit == "um":
            multiplier = 1e6
        elif unit == "mil":
            multiplier = 1 / 0.0000254
        elif unit == "in":
            multiplier = 1 / 0.0254
        elif unit == "m":
            multiplier = 1
        else:
            raise ValueError(f"Unsupported unit: {unit}")
        for layer in self.layers:
            if isinstance(layer.thickness, str):
                if "um" in layer.thickness:
                    layer.thickness = float(layer.thickness.replace("um", "")) * 1e-6 * multiplier
                elif "mm" in layer.thickness:
                    layer.thickness = float(layer.thickness.replace("mm", "")) * 1e-3 * multiplier
                elif "cm" in layer.thickness:
                    layer.thickness = float(layer.thickness.replace("cm", "")) * 1e-2 * multiplier
                elif "mil" in layer.thickness:
                    layer.thickness = float(layer.thickness.replace("mil", "")) * 0.0000254 * multiplier
                elif "in" in layer.thickness:
                    layer.thickness = float(layer.thickness.replace("in", "")) * 0.0254 * multiplier
                elif "m" in layer.thickness:
                    layer.thickness = float(layer.thickness.replace("m", "")) * 1 * multiplier
            layer.thickness = f"{layer.thickness}{unit}"
