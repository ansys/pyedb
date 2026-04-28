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

"""Package definitions builder API.

Data models: :class:`CfgHeatSinkData`, :class:`CfgPackageData`,
:class:`CfgPackageDefinitionsModel` (pydantic roots defined here).
The runtime class :class:`~pyedb.configuration.cfg_package_definition.CfgPackageDefinitions`
requires a live EDB connection; this API layer owns the pure-data pydantic
models and serialises to plain dicts that the runtime class can consume.
"""

from __future__ import annotations

from typing import List, Optional, Union

from pydantic import BaseModel, Field

from pyedb.configuration.cfg_common import CfgBaseModel


class CfgHeatSinkData(CfgBaseModel):
    """Pydantic data model for heat-sink properties.

    Mirrors :class:`~pyedb.configuration.cfg_package_definition.CfgHeatSink`.
    """

    fin_base_height: Optional[Union[str, float]] = None
    fin_height: Optional[Union[str, float]] = None
    fin_orientation: Optional[str] = None
    fin_spacing: Optional[Union[str, float]] = None
    fin_thickness: Optional[Union[str, float]] = None

    model_config = {"populate_by_name": True, "extra": "ignore"}


class CfgPackageData(CfgBaseModel):
    """Pydantic data model for a single package definition entry.

    Mirrors :class:`~pyedb.configuration.cfg_package_definition.CfgPackage`.
    """

    name: str
    component_definition: str
    apply_to_all: Optional[bool] = None
    components: List[str] = Field(default_factory=list)
    maximum_power: Optional[float] = None
    thermal_conductivity: Optional[float] = None
    theta_jb: Optional[float] = None
    theta_jc: Optional[float] = None
    height: Optional[Union[str, float]] = None
    extent_bounding_box: Optional[object] = None
    heatsink: Optional[CfgHeatSinkData] = None

    model_config = {"populate_by_name": True, "extra": "ignore"}

    def set_heatsink(
        self,
        fin_base_height: Optional[Union[str, float]] = None,
        fin_height: Optional[Union[str, float]] = None,
        fin_orientation: Optional[str] = None,
        fin_spacing: Optional[Union[str, float]] = None,
        fin_thickness: Optional[Union[str, float]] = None,
    ) -> CfgHeatSinkData:
        """Configure heat-sink properties and return the model."""
        self.heatsink = CfgHeatSinkData(
            fin_base_height=fin_base_height,
            fin_height=fin_height,
            fin_orientation=fin_orientation,
            fin_spacing=fin_spacing,
            fin_thickness=fin_thickness,
        )
        return self.heatsink


class CfgPackageDefinitionsModel(BaseModel):
    """Root pydantic model for the ``package_definitions`` configuration list."""

    packages: List[CfgPackageData] = Field(default_factory=list)

    def add(
        self,
        name: str,
        component_definition: str,
        apply_to_all: Optional[bool] = None,
        components: Optional[List[str]] = None,
        **kwargs,
    ) -> CfgPackageData:
        pkg = CfgPackageData(
            name=name,
            component_definition=component_definition,
            apply_to_all=apply_to_all,
            components=components or [],
            **kwargs,
        )
        self.packages.append(pkg)
        return pkg


class PackageDefinitionsConfig:
    """Fluent builder for the ``package_definitions`` configuration list.

    Wraps :class:`CfgPackageDefinitionsModel`.

    Examples
    --------
    >>> pkg = cfg.package_definitions.add("PKG1", "COMP_DEF", apply_to_all=True)
    >>> pkg.set_heatsink(fin_height="2mm", fin_spacing="0.5mm")
    """

    def __init__(self):
        self._model = CfgPackageDefinitionsModel()

    def add(
        self,
        name: str,
        component_definition: str,
        apply_to_all: Optional[bool] = None,
        components: Optional[List[str]] = None,
        **kwargs,
    ) -> CfgPackageData:
        """Add a package definition.

        Returns
        -------
        CfgPackageData
        """
        return self._model.add(
            name=name,
            component_definition=component_definition,
            apply_to_all=apply_to_all,
            components=components,
            **kwargs,
        )

    def to_list(self) -> List[dict]:
        """Serialise to a list of dicts consumable by
        :class:`~pyedb.configuration.cfg_package_definition.CfgPackageDefinitions`."""
        return [p.model_dump(exclude_none=True) for p in self._model.packages]


#: Backward-compatible aliases
HeatSinkConfig = CfgHeatSinkData
PackageDefinitionConfig = CfgPackageData

