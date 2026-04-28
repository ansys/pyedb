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

"""Stackup builder API.

Data models:
  :class:`~pyedb.configuration.cfg_stackup.CfgMaterial`
  :class:`~pyedb.configuration.cfg_stackup.CfgLayer`
  :class:`~pyedb.configuration.cfg_stackup.CfgStackup`
  :class:`~pyedb.configuration.cfg_stackup.CfgHurayRoughnessModel`
  :class:`~pyedb.configuration.cfg_stackup.CfgGroisseRoughnessModel`
  :class:`~pyedb.configuration.cfg_stackup.CfgRoughnessModel`
  :class:`~pyedb.configuration.cfg_stackup.EtchingModel`
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
    **kwargs
        Any field accepted by :class:`~pyedb.configuration.cfg_stackup.CfgMaterial`
        (conductivity, permittivity, dielectric_loss_tangent, …).
    """

    def __init__(self, name: str, **kwargs):
        self._model = CfgMaterial(name=name, **kwargs)

    def to_dict(self) -> dict:
        """Return dict excluding ``None`` values."""
        return self._model.model_dump(exclude_none=True)


class LayerConfig:
    """Fluent builder for a single stackup layer.

    Wraps :class:`~pyedb.configuration.cfg_stackup.CfgLayer`.

    Parameters
    ----------
    name : str
    **kwargs
        Any field accepted by :class:`~pyedb.configuration.cfg_stackup.CfgLayer`.
    """

    def __init__(self, name: str, **kwargs):
        self._model = CfgLayer(name=name, **kwargs)

    def set_huray_roughness(
        self,
        nodule_radius: Union[str, float],
        surface_ratio: Union[str, float],
        enabled: bool = True,
        top: bool = True,
        bottom: bool = True,
        side: bool = True,
    ):
        """Configure Huray roughness on selected surfaces.

        Parameters
        ----------
        nodule_radius : str or float  e.g. ``"0.1um"``
        surface_ratio : str or float
        enabled : bool
        top, bottom, side : bool  which surfaces to apply to
        """
        huray = CfgHurayRoughnessModel(nodule_radius=nodule_radius, surface_ratio=surface_ratio)
        self._model.roughness = CfgRoughnessModel(
            enabled=enabled,
            top=huray if top else None,
            bottom=huray if bottom else None,
            side=huray if side else None,
        )

    def set_groisse_roughness(
        self,
        roughness_value: Union[str, float],
        enabled: bool = True,
        top: bool = True,
        bottom: bool = True,
        side: bool = True,
    ):
        """Configure Groisse roughness on selected surfaces."""
        groisse = CfgGroisseRoughnessModel(roughness=roughness_value)
        self._model.roughness = CfgRoughnessModel(
            enabled=enabled,
            top=groisse if top else None,
            bottom=groisse if bottom else None,
            side=groisse if side else None,
        )

    def set_etching(
        self,
        factor: Union[float, str] = 0.5,
        etch_power_ground_nets: bool = False,
        enabled: bool = True,
    ):
        """Configure the etching model."""
        self._model.etching = EtchingModel(
            factor=factor,
            etch_power_ground_nets=etch_power_ground_nets,
            enabled=enabled,
        )

    def to_dict(self) -> dict:
        return self._model.model_dump(exclude_none=True)


class StackupConfig:
    """Fluent builder for the ``stackup`` configuration section.

    Wraps :class:`~pyedb.configuration.cfg_stackup.CfgStackup`.
    """

    def __init__(self):
        self._model = CfgStackup()

    def add_material(self, name: str, **kwargs) -> MaterialConfig:
        """Add a material definition.

        Parameters
        ----------
        name : str
        **kwargs
            Material properties (conductivity, permittivity, etc.)

        Returns
        -------
        MaterialConfig
        """
        cfg = MaterialConfig(name, **kwargs)
        self._model.materials.append(cfg._model)
        return cfg

    def add_layer(self, name: str, **kwargs) -> LayerConfig:
        """Append a layer.

        Parameters
        ----------
        name : str
        **kwargs
            Layer attributes (type, material, fill_material, thickness, …)

        Returns
        -------
        LayerConfig
        """
        cfg = LayerConfig(name, **kwargs)
        self._model.layers.append(cfg._model)
        return cfg

    def add_signal_layer(
        self,
        name: str,
        material: str = "copper",
        fill_material: str = "FR4_epoxy",
        thickness: Union[str, float] = "35um",
    ) -> LayerConfig:
        """Convenience: add a signal layer."""
        return self.add_layer(name, type="signal", material=material, fill_material=fill_material, thickness=thickness)

    def add_dielectric_layer(
        self,
        name: str,
        material: str = "FR4_epoxy",
        thickness: Union[str, float] = "100um",
    ) -> LayerConfig:
        """Convenience: add a dielectric layer."""
        return self.add_layer(name, type="dielectric", material=material, thickness=thickness)

    def to_dict(self) -> dict:
        d = self._model.model_dump(exclude_none=True)
        # exclude empty lists from the output (matches previous behaviour)
        return {k: v for k, v in d.items() if v != []}
