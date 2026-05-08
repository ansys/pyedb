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

from typing import Any, List, Optional, Union

from pydantic import BaseModel, Field


class CfgMaterialPropertyThermalModifier(BaseModel):
    """Represent one thermal modifier applied to a material property."""

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
    """Represent one material entry in the ``stackup`` section."""

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
    """Represent a Huray surface-roughness model."""

    model: str = "huray"
    nodule_radius: Optional[str | float | int] = None  # e.g., '0.1um'
    surface_ratio: Optional[str | float | int] = None  # e.g., '1'
    model_config = {"extra": "forbid"}


class CfgGroisseRoughnessModel(BaseModel):
    """Represent a Groisse surface-roughness model."""

    model: str = "groisse"
    roughness: Optional[str | float | int] = None

    model_config = {"extra": "forbid"}


class CfgRoughnessModel(BaseModel):
    """Collect top, bottom, and side roughness models for a layer."""

    enabled: Optional[bool] = False
    top: CfgHurayRoughnessModel | CfgGroisseRoughnessModel | None = None
    bottom: CfgHurayRoughnessModel | CfgGroisseRoughnessModel | None = None
    side: CfgHurayRoughnessModel | CfgGroisseRoughnessModel | None = None

    model_config = {"extra": "forbid"}


class EtchingModel(BaseModel):
    """Represent trapezoidal etching settings for a conductor layer."""

    factor: Optional[Union[float, str]] = 0.5
    etch_power_ground_nets: Optional[bool] = False
    enabled: Optional[bool] = False


class CfgLayer(BaseModel):
    """Represent one signal or dielectric layer entry."""

    name: Optional[str] = None
    layer_type: Optional[str] = Field(None, alias="type")
    material: Optional[str] = None
    fill_material: Optional[str] = None
    thickness: Optional[Union[float, str]] = None
    roughness: Optional[CfgRoughnessModel] = None
    etching: Optional[EtchingModel] = None

    model_config = {"populate_by_name": True}

    @property
    def type(self) -> Optional[str]:
        """Alias for ``layer_type`` for backward compatibility."""
        return self.layer_type

    def __init__(
        self,
        name: str | None = None,
        layer_type: Optional[str] = None,
        material: Optional[str] = None,
        fill_material: Optional[str] = None,
        thickness: Optional[Union[str, float]] = None,
        roughness: Optional[CfgRoughnessModel] = None,
        etching: Optional[EtchingModel] = None,
        **kwargs,
    ):
        # Accept ``type`` as a back-compat alias passed via **kwargs.
        resolved_type = layer_type or kwargs.pop("type", None)
        super().__init__(
            name=name,
            layer_type=resolved_type,
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
        """Configure Huray surface roughness on selected surfaces.

        Parameters
        ----------
        nodule_radius : str or float
            Huray nodule radius, e.g. ``"0.1um"``.
        surface_ratio : str or float
            Huray surface ratio.
        enabled : bool, optional
            Enable roughness on this layer.  Default is ``True``.
        top : bool, optional
            Apply roughness to the top surface.  Default is ``True``.
        bottom : bool, optional
            Apply roughness to the bottom surface.  Default is ``True``.
        side : bool, optional
            Apply roughness to the side surfaces.  Default is ``True``.

        Returns
        -------
        CfgLayer
            *self* — enables method chaining.

        Examples
        --------
        >>> layer.set_huray_roughness("0.1um", "2.9", top=True, bottom=False)
        """
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
        """Configure Groisse surface roughness on selected surfaces.

        Parameters
        ----------
        roughness_value : str or float
            RMS roughness, e.g. ``0.3e-6`` (in metres).
        enabled : bool, optional
            Enable roughness.  Default is ``True``.
        top : bool, optional
            Default is ``True``.
        bottom : bool, optional
            Default is ``True``.
        side : bool, optional
            Default is ``True``.

        Returns
        -------
        CfgLayer
            *self* — enables method chaining.
        """
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
        """Configure trapezoidal etching on this conductor layer.

        Parameters
        ----------
        factor : float or str, optional
            Etch factor (ratio).  Default is ``0.5``.
        etch_power_ground_nets : bool, optional
            Apply etching to power/ground nets as well.  Default is ``False``.
        enabled : bool, optional
            Enable etching.  Default is ``True``.

        Returns
        -------
        CfgLayer
            *self* — enables method chaining.

        Examples
        --------
        >>> layer.set_etching(factor=0.4, etch_power_ground_nets=True)
        """
        self.etching = EtchingModel(
            factor=factor,
            etch_power_ground_nets=etch_power_ground_nets,
            enabled=enabled,
        )
        return self

    def to_dict(self) -> dict:
        """Serialize the layer definition."""
        return self.model_dump(exclude_none=True, by_alias=True)


class CfgStackup(BaseModel):
    """Collect stackup materials and layers for serialization."""

    materials: List[CfgMaterial] = Field(default_factory=list)
    layers: List[CfgLayer] = Field(default_factory=list)

    # Not serialized – holds a live EDB reference when built from a session.
    _pedb: object = None

    model_config = {"arbitrary_types_allowed": True}

    def _set_pedb(self, pedb):
        """Attach a live EDB session (called by EdbConfigBuilder)."""
        object.__setattr__(self, "_pedb", pedb)

    def get_layer(self, name: str) -> "CfgLayer":
        """Return the :class:`CfgLayer` for *name*, loading it from EDB if needed.

        If the layer has already been registered (via :meth:`add_signal_layer`,
        :meth:`add_dielectric_layer`, or :meth:`add_layer`) the cached entry is
        returned.  Otherwise the layer is looked up in the live EDB session and
        a new :class:`CfgLayer` is created from its current properties.

        Parameters
        ----------
        name : str
            Layer name, e.g. ``"top"`` or ``"diel1"``.

        Returns
        -------
        CfgLayer
            Layer builder pre-populated with current properties.

        Raises
        ------
        KeyError
            If the layer is not found in the builder registry or the EDB layout.

        Examples
        --------
        >>> cfg = edb.configuration.create_config_builder()
        >>> top = cfg.stackup.get_layer("top")
        >>> top.set_huray_roughness("0.1um", "2.9")
        >>> edb.configuration.run(cfg)
        """
        for layer in self.layers:
            if layer.name == name:
                return layer
        if self._pedb is None:
            raise KeyError(
                f"Layer '{name}' not found in the builder. "
                f"Attach an EDB session via edb.configuration.create_config_builder() to auto-load layers."
            )
        edb_layers = self._pedb.stackup.all_layers
        if name not in edb_layers:
            raise KeyError(f"Layer '{name}' not found in the EDB stackup.")
        props = edb_layers[name].properties
        layer = CfgLayer(name=name, **{k: v for k, v in props.items() if k != "name"})
        self.layers.append(layer)
        return layer

    def get_layers(self) -> list:
        """Return all stackup layers as :class:`CfgLayer` objects.

        Each layer in the live EDB session is loaded (if not already cached)
        and returned as a list of :class:`CfgLayer` instances.

        Returns
        -------
        list of CfgLayer
            All stackup layers in stack order.

        Raises
        ------
        KeyError
            If no EDB session is attached.

        Examples
        --------
        >>> cfg = edb.configuration.create_config_builder()
        >>> for layer in cfg.stackup.get_layers():
        ...     print(layer.name, layer.type)
        """
        if self._pedb is None:
            raise KeyError(
                "No EDB session is attached. "
                "Use edb.configuration.create_config_builder() to get a session-aware builder."
            )
        for name in self._pedb.stackup.all_layers:
            self.get_layer(name)  # populates self.layers cache via get_layer
        return list(self.layers)

    def get_signal_layers(self) -> list:
        """Return only the signal (metal) stackup layers as :class:`CfgLayer` objects.

        Queries the live EDB session for signal layers only, loads each into the
        cache via :meth:`get_layer`, and returns the filtered list.

        Returns
        -------
        list of CfgLayer
            Signal layers in stack order.

        Raises
        ------
        KeyError
            If no EDB session is attached.

        Examples
        --------
        >>> cfg = edb.configuration.create_config_builder()
        >>> for layer in cfg.stackup.get_signal_layers():
        ...     print(layer.name, layer.thickness)
        """
        if self._pedb is None:
            raise KeyError(
                "No EDB session is attached. "
                "Use edb.configuration.create_config_builder() to get a session-aware builder."
            )
        for name in self._pedb.stackup.signal_layers:
            self.get_layer(name)
        return [layer for layer in self.layers if layer.type == "signal"]

    def get_material(self, name: str) -> "CfgMaterial":
        """Return the :class:`CfgMaterial` for *name*, loading it from EDB if needed.

        If the material has already been registered via :meth:`add_material`
        the cached entry is returned.  Otherwise the material is looked up in
        the live EDB session and a new :class:`CfgMaterial` is created from its
        current properties.

        Parameters
        ----------
        name : str
            Material name, e.g. ``"copper"`` or ``"FR4_epoxy"``.

        Returns
        -------
        CfgMaterial
            Material builder pre-populated with current properties.

        Raises
        ------
        KeyError
            If the material is not found in the builder registry or the EDB database.

        Examples
        --------
        >>> cfg = edb.configuration.create_config_builder()
        >>> cu = cfg.stackup.get_material("copper")
        >>> cu.conductivity = 5.6e7
        >>> edb.configuration.run(cfg)
        """
        for mat in self.materials:
            if mat.name == name:
                return mat
        if self._pedb is None:
            raise KeyError(
                f"Material '{name}' not found in the builder. "
                f"Attach an EDB session via edb.configuration.create_config_builder() to auto-load materials."
            )
        edb_mats = self._pedb.materials.materials
        if name not in edb_mats:
            raise KeyError(f"Material '{name}' not found in the EDB material library.")
        mat_props = edb_mats[name].to_dict()
        mat = CfgMaterial(**mat_props)
        self.materials.append(mat)
        return mat

    def add_material(
        self,
        name: str | None = None,
        config: CfgMaterial | dict[str, Any] | None = None,
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
        thermal_modifiers=None,
        **kwargs,
    ) -> "CfgMaterial":
        """Add a material definition to the stackup.

        Parameters
        ----------
        name : str
            Material name, e.g. ``"copper"`` or ``"FR4_epoxy"``.
        conductivity : str or float, optional
            Electrical conductivity in S/m.
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
            Frequency for the dielectric model in Hz.
        loss_tangent_at_frequency : str or float, optional
            Loss tangent at the model frequency.
        permittivity_at_frequency : str or float, optional
            Permittivity at the model frequency.
        thermal_modifiers : list, optional
            List of thermal modifier definitions.

        Returns
        -------
        CfgMaterial
            The newly created material object.

        Examples
        --------
        >>> cfg.stackup.add_material("copper", conductivity=5.8e7)
        >>> cfg.stackup.add_material("fr4", permittivity=4.4, dielectric_loss_tangent=0.02)
        """
        # Support config parameter (dict or CfgMaterial) from main branch API
        if config is not None:
            if isinstance(config, CfgMaterial):
                payload = config.model_dump(exclude_none=True)
            else:
                payload = dict(config)
            payload.update(kwargs)
            if name is not None:
                payload["name"] = name
            kwargs = payload
            name = kwargs.pop("name", name)
            conductivity = kwargs.pop("conductivity", conductivity)
            permittivity = kwargs.pop("permittivity", permittivity)
            dielectric_loss_tangent = kwargs.pop("dielectric_loss_tangent", dielectric_loss_tangent)
            magnetic_loss_tangent = kwargs.pop("magnetic_loss_tangent", magnetic_loss_tangent)
            mass_density = kwargs.pop("mass_density", mass_density)
            permeability = kwargs.pop("permeability", permeability)
            poisson_ratio = kwargs.pop("poisson_ratio", poisson_ratio)
            specific_heat = kwargs.pop("specific_heat", specific_heat)
            thermal_conductivity = kwargs.pop("thermal_conductivity", thermal_conductivity)
            youngs_modulus = kwargs.pop("youngs_modulus", youngs_modulus)
            thermal_expansion_coefficient = kwargs.pop("thermal_expansion_coefficient", thermal_expansion_coefficient)
            dc_conductivity = kwargs.pop("dc_conductivity", dc_conductivity)
            dc_permittivity = kwargs.pop("dc_permittivity", dc_permittivity)
            dielectric_model_frequency = kwargs.pop("dielectric_model_frequency", dielectric_model_frequency)
            loss_tangent_at_frequency = kwargs.pop("loss_tangent_at_frequency", loss_tangent_at_frequency)
            permittivity_at_frequency = kwargs.pop("permittivity_at_frequency", permittivity_at_frequency)
            thermal_modifiers = kwargs.pop("thermal_modifiers", thermal_modifiers)

        # Check for duplicates in the local registry first.
        for _mat in self.materials:
            if _mat.name == name:
                raise ValueError(
                    f"Material '{name}' already exists in the builder. "
                    f"Use get_material('{name}') to retrieve and modify it instead."
                )
        # When a live EDB session is attached, also check the database.
        if self._pedb is not None:
            edb_mats = self._pedb.materials.materials
            if name in edb_mats:
                raise ValueError(
                    f"Material '{name}' already exists in the EDB material library. "
                    f"Use get_material('{name}') to retrieve and modify it instead."
                )

        props = dict(
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
        )
        # Merge any extra kwargs (e.g. from existing serialization round-trips)
        props.update(kwargs)
        # Drop None values so CfgMaterial does not complain about unknown None fields
        props = {k: v for k, v in props.items() if v is not None}
        mat = CfgMaterial(name=name, **props)
        self.materials.append(mat)
        return mat

    def add_layer(
        self,
        name,
        layer_type: Optional[str] = None,
        material: Optional[str] = None,
        fill_material: Optional[str] = None,
        thickness: Optional[Union[str, float]] = None,
        **kwargs,
    ):
        """Append a layer definition.

        Parameters
        ----------
        name : str
            Layer name.
        layer_type : str, optional
            Layer type: ``"signal"`` or ``"dielectric"``.
            Also accepted as ``type=`` for backwards compatibility.
        material : str, optional
            Layer material name.
        fill_material : str, optional
            Fill material for signal layers.
        thickness : str or float, optional
            Layer thickness, e.g. ``"35um"``.
        """
        # Accept legacy 'type=' spelling passed via **kwargs
        if layer_type is None and "type" in kwargs:
            layer_type = kwargs.pop("type")
        return self.add_layer_at_bottom(
            name,
            layer_type=layer_type,
            material=material,
            fill_material=fill_material,
            thickness=thickness,
            **kwargs,
        )

    def add_layer_at_bottom(self, name=None, config: CfgLayer | dict[str, Any] | None = None, **kwargs):
        """Append a layer to the bottom of the stackup.

        Parameters
        ----------
        name : str, optional
            Layer name. If provided, it overrides the name from ``config``.
        config : CfgLayer | dict, optional
            Layer payload as a ``CfgLayer`` instance or dictionary.
        **kwargs
            Optional layer properties forwarded to :class:`CfgLayer`
            (``layer_type`` or ``type``, ``material``, ``fill_material``,
            ``thickness``).

        Returns
        -------
        CfgLayer
            The newly created layer object.
        """
        if config is not None:
            if isinstance(config, CfgLayer):
                payload = config.model_dump(exclude_none=True)
            else:
                payload = dict(config)
            payload.update(kwargs)
            if name is not None:
                payload["name"] = name
            kwargs = payload
            name = kwargs.pop("name", name)
        # Normalise legacy 'type' kwarg to 'layer_type'
        if "type" in kwargs and "layer_type" not in kwargs:
            kwargs["layer_type"] = kwargs.pop("type")
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
        return self.add_layer(
            name, layer_type="signal", material=material, fill_material=fill_material, thickness=thickness
        )

    def add_dielectric_layer(
        self,
        name: str,
        material: str = "FR4_epoxy",
        thickness: Union[str, float] = "100um",
    ):
        """Add a dielectric layer with common defaults."""
        return self.add_layer(name, layer_type="dielectric", material=material, thickness=thickness)

    def to_dict(self) -> dict:
        """Serialize the configured stackup."""
        d = self.model_dump(exclude_none=True, by_alias=True)
        return {k: v for k, v in d.items() if v != []}

    def normalize_thickness(self, unit="m"):
        if unit == "m":
            multiplier = 1
        elif unit == "mm":
            multiplier = 1000
        elif unit == "um":
            multiplier = 1e6
        elif unit == "mil":
            multiplier = 1 / 0.0000254
        elif unit == "in":
            multiplier = 1 / 0.0254
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
