# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Build the ``stackup`` configuration section.

This module wraps the stackup-related configuration models with fluent builders
for materials, layers, roughness, and etching definitions.

Typical usage
-------------
>>> cfg.stackup.add_material("copper", conductivity=5.8e7)
>>> cfg.stackup.add_material("fr4", permittivity=4.4, dielectric_loss_tangent=0.02)
>>> layer = cfg.stackup.add_signal_layer("top", material="copper", fill_material="fr4", thickness="35um")
>>> layer.set_huray_roughness("0.1um", "1.0")
>>> cfg.stackup.add_dielectric_layer("diel1", material="fr4", thickness="100um")
"""

from __future__ import annotations

from typing import List, Optional, Union

from pyedb.configuration.cfg_stackup import (
    CfgGroisseRoughnessModel,
    CfgHurayRoughnessModel,
    CfgLayer,
    CfgMaterial,
    CfgRoughnessModel,
    CfgStackup,
    EtchingModel,
)


class MaterialConfig:
    """Fluent builder for a single stackup material.

    Wraps :class:`~pyedb.configuration.cfg_stackup.CfgMaterial`.

    Parameters
    ----------
    name : str
        Material name.
    conductivity : str or float, optional
        Electrical conductivity in S/m (e.g. ``5.8e7`` for copper).
    permittivity : str or float, optional
        Relative permittivity (dielectric constant).
    dielectric_loss_tangent : str or float, optional
        Dielectric loss tangent.
    magnetic_loss_tangent : str or float, optional
        Magnetic loss tangent.
    mass_density : str or float, optional
        Mass density in kg/m³.
    permeability : str or float, optional
        Relative permeability.
    poisson_ratio : str or float, optional
        Poisson's ratio (mechanical).
    specific_heat : str or float, optional
        Specific heat capacity in J/(kg·K).
    thermal_conductivity : str or float, optional
        Thermal conductivity in W/(m·K).
    youngs_modulus : str or float, optional
        Young's modulus in Pa (mechanical).
    thermal_expansion_coefficient : str or float, optional
        Coefficient of thermal expansion (CTE) in 1/K.
    dc_conductivity : str or float, optional
        DC conductivity override.
    dc_permittivity : str or float, optional
        DC permittivity override.
    dielectric_model_frequency : str or float, optional
        Reference frequency for the frequency-dependent dielectric model.
    loss_tangent_at_frequency : str or float, optional
        Loss tangent at *dielectric_model_frequency*.
    permittivity_at_frequency : str or float, optional
        Permittivity at *dielectric_model_frequency*.
    """

    def __init__(
        self,
        name: str,
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
    ):
        props = {k: v for k, v in locals().items() if k != "self" and v is not None}
        self._model = CfgMaterial(**props)

    def to_dict(self) -> dict:
        """Serialize the material, excluding ``None`` values.

        Returns
        -------
        dict
            Material properties dictionary.
        """
        return self._model.model_dump(exclude_none=True)


class LayerConfig:
    """Fluent builder for a single stackup layer.

    Wraps :class:`~pyedb.configuration.cfg_stackup.CfgLayer`.

    Parameters
    ----------
    name : str
        Layer name.
    type : str, optional
        Layer type: ``"signal"`` or ``"dielectric"``.
    material : str, optional
        Conductor (signal) or dielectric material name.
    fill_material : str, optional
        Fill material name (signal layers only).
    thickness : str or float, optional
        Layer thickness, e.g. ``"35um"`` or ``35e-6``.
    """

    def __init__(
        self,
        name: str,
        type: Optional[str] = None,
        material: Optional[str] = None,
        fill_material: Optional[str] = None,
        thickness: Optional[Union[str, float]] = None,
    ):
        """Initialize a layer configuration.

        Parameters
        ----------
        name : str
            Layer name.
        type : str, optional
            Layer type: ``"signal"`` or ``"dielectric"``.
        material : str, optional
            Conductor or dielectric material name.
        fill_material : str, optional
            Fill material for signal layers.
        thickness : str or float, optional
            Layer thickness, e.g. ``"35um"``.
        """
        self._model = CfgLayer(
            name=name,
            type=type,
            material=material,
            fill_material=fill_material,
            thickness=thickness,
        )

    def set_huray_roughness(
        self,
        nodule_radius: Union[str, float],
        surface_ratio: Union[str, float],
        enabled: bool = True,
        top: bool = True,
        bottom: bool = True,
        side: bool = True,
    ) -> "LayerConfig":
        """Configure Huray roughness on selected surfaces.

        Parameters
        ----------
        nodule_radius : str or float
            Nodule radius, e.g. ``"0.1um"``.
        surface_ratio : str or float
            Surface ratio (dimensionless).
        enabled : bool, default: ``True``
            Whether the roughness model is enabled.
        top : bool, default: ``True``
            Apply the model to the top surface.
        bottom : bool, default: ``True``
            Apply the model to the bottom surface.
        side : bool, default: ``True``
            Apply the model to side walls.

        Returns
        -------
        LayerConfig
            *self*, for method chaining.
        """
        huray = CfgHurayRoughnessModel(nodule_radius=nodule_radius, surface_ratio=surface_ratio)
        self._model.roughness = CfgRoughnessModel(
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
    ) -> "LayerConfig":
        """Configure Groisse roughness on selected surfaces.

        Parameters
        ----------
        roughness_value : str or float
            Groisse roughness value, e.g. ``"0.5um"``.
        enabled : bool, default: ``True``
            Whether the roughness model is enabled.
        top : bool, default: ``True``
            Apply the model to the top surface.
        bottom : bool, default: ``True``
            Apply the model to the bottom surface.
        side : bool, default: ``True``
            Apply the model to side walls.

        Returns
        -------
        LayerConfig
            *self*, for method chaining.
        """
        groisse = CfgGroisseRoughnessModel(roughness=roughness_value)
        self._model.roughness = CfgRoughnessModel(
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
    ) -> "LayerConfig":
        """Configure the etching model.

        Parameters
        ----------
        factor : float or str, default: ``0.5``
            Etching factor (ratio of trapezoidal undercut).
        etch_power_ground_nets : bool, default: ``False``
            Whether power and ground nets are etched as well.
        enabled : bool, default: ``True``
            Whether the etching model is enabled.

        Returns
        -------
        LayerConfig
            *self*, for method chaining.
        """
        self._model.etching = EtchingModel(
            factor=factor,
            etch_power_ground_nets=etch_power_ground_nets,
            enabled=enabled,
        )
        return self

    def to_dict(self) -> dict:
        """Serialize the layer definition.

        Returns
        -------
        dict
            Dictionary containing only populated layer properties.
        """
        return self._model.model_dump(exclude_none=True)


class StackupConfig:
    """Fluent builder for the ``stackup`` configuration section.

    Wraps :class:`~pyedb.configuration.cfg_stackup.CfgStackup`.

    Examples
    --------
    >>> cfg.stackup.add_material("copper", conductivity=5.8e7)
    >>> cfg.stackup.add_material("fr4", permittivity=4.4, dielectric_loss_tangent=0.02)
    >>> top = cfg.stackup.add_signal_layer("top", material="copper", fill_material="fr4", thickness="35um")
    >>> top.set_huray_roughness("0.1um", "1.0")
    >>> cfg.stackup.add_dielectric_layer("diel1", material="fr4", thickness="100um")
    """

    def __init__(self):
        """Initialize the stackup configuration."""
        self._model = CfgStackup()

    def add_material(
        self,
        name: str,
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
    ) -> MaterialConfig:
        """Add a material definition.

        Parameters
        ----------
        name : str
            Material name.
        conductivity : str or float, optional
            Electrical conductivity in S/m (e.g. ``5.8e7`` for copper).
        permittivity : str or float, optional
            Relative permittivity (dielectric constant).
        dielectric_loss_tangent : str or float, optional
            Dielectric loss tangent.
        magnetic_loss_tangent : str or float, optional
            Magnetic loss tangent.
        mass_density : str or float, optional
            Mass density in kg/m³.
        permeability : str or float, optional
            Relative permeability.
        poisson_ratio : str or float, optional
            Poisson's ratio.
        specific_heat : str or float, optional
            Specific heat capacity in J/(kg·K).
        thermal_conductivity : str or float, optional
            Thermal conductivity in W/(m·K).
        youngs_modulus : str or float, optional
            Young's modulus in Pa.
        thermal_expansion_coefficient : str or float, optional
            Coefficient of thermal expansion in 1/K.
        dc_conductivity : str or float, optional
            DC conductivity override.
        dc_permittivity : str or float, optional
            DC permittivity override.
        dielectric_model_frequency : str or float, optional
            Reference frequency for a frequency-dependent dielectric model.
        loss_tangent_at_frequency : str or float, optional
            Loss tangent at *dielectric_model_frequency*.
        permittivity_at_frequency : str or float, optional
            Permittivity at *dielectric_model_frequency*.

        Returns
        -------
        MaterialConfig
            Newly created material builder.
        """
        cfg = MaterialConfig(
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
        )
        self._model.materials.append(cfg._model)
        return cfg

    def add_layer(
        self,
        name: str,
        type: Optional[str] = None,
        material: Optional[str] = None,
        fill_material: Optional[str] = None,
        thickness: Optional[Union[str, float]] = None,
    ) -> LayerConfig:
        """Append a layer.

        Parameters
        ----------
        name : str
            Layer name.
        type : str, optional
            Layer type: ``"signal"`` or ``"dielectric"``.
        material : str, optional
            Material name.
        fill_material : str, optional
            Fill material name (signal layers only).
        thickness : str or float, optional
            Layer thickness, e.g. ``"35um"``.

        Returns
        -------
        LayerConfig
            Newly created layer builder; supports roughness and etching calls.
        """
        cfg = LayerConfig(name=name, type=type, material=material, fill_material=fill_material, thickness=thickness)
        self._model.layers.append(cfg._model)
        return cfg

    def add_signal_layer(
        self,
        name: str,
        material: str = "copper",
        fill_material: str = "FR4_epoxy",
        thickness: Union[str, float] = "35um",
    ) -> LayerConfig:
        """Add a signal layer with conductor defaults.

        Parameters
        ----------
        name : str
            Layer name.
        material : str, default: ``"copper"``
            Conductor material name.
        fill_material : str, default: ``"FR4_epoxy"``
            Fill dielectric material name.
        thickness : str or float, default: ``"35um"``
            Layer thickness.

        Returns
        -------
        LayerConfig
            Newly created layer builder.
        """
        return self.add_layer(name, type="signal", material=material, fill_material=fill_material, thickness=thickness)

    def add_dielectric_layer(
        self,
        name: str,
        material: str = "FR4_epoxy",
        thickness: Union[str, float] = "100um",
    ) -> LayerConfig:
        """Add a dielectric layer with common defaults.

        Parameters
        ----------
        name : str
            Layer name.
        material : str, default: ``"FR4_epoxy"``
            Dielectric material name.
        thickness : str or float, default: ``"100um"``
            Layer thickness.

        Returns
        -------
        LayerConfig
            Newly created layer builder.
        """
        return self.add_layer(name, type="dielectric", material=material, thickness=thickness)

    def to_dict(self) -> dict:
        """Serialize the configured stackup.

        Returns
        -------
        dict
            Stackup dictionary with empty lists omitted.
        """
        d = self._model.model_dump(exclude_none=True)
        return {k: v for k, v in d.items() if v != []}
