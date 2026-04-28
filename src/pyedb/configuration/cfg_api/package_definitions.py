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

"""Build thermal ``package_definitions`` configuration entries."""

from __future__ import annotations

from typing import List, Optional, Union


class HeatSinkConfig:
    """Store heat-sink properties for a package definition."""

    def __init__(
        self,
        fin_base_height: Optional[Union[str, float]] = None,
        fin_height: Optional[Union[str, float]] = None,
        fin_orientation: Optional[str] = None,
        fin_spacing: Optional[Union[str, float]] = None,
        fin_thickness: Optional[Union[str, float]] = None,
    ):
        """Initialize heat-sink configuration.

        Parameters
        ----------
        fin_base_height : str or float, optional
        fin_height : str or float, optional
        fin_orientation : str, optional
        fin_spacing : str or float, optional
        fin_thickness : str or float, optional

        """
        self.fin_base_height = fin_base_height
        self.fin_height = fin_height
        self.fin_orientation = fin_orientation
        self.fin_spacing = fin_spacing
        self.fin_thickness = fin_thickness

    def to_dict(self) -> dict:
        """Serialize non-null heat-sink properties.

        Returns
        -------
        dict
            Heat-sink settings suitable for the ``heatsink`` sub-section.
        """
        return {k: v for k, v in self.__dict__.items() if v is not None}


class PackageDefinitionConfig:
    """Represent one thermal package definition entry."""

    def __init__(
        self,
        name: str,
        component_definition: str,
        apply_to_all: Optional[bool] = None,
        components: Optional[List[str]] = None,
        maximum_power=None,
        thermal_conductivity=None,
        theta_jb=None,
        theta_jc=None,
        height=None,
        extent_bounding_box=None,
        heatsink: Optional[HeatSinkConfig] = None,
    ):
        self.name = name
        self.component_definition = component_definition
        self.apply_to_all = apply_to_all
        self.components = components or []
        self.maximum_power = maximum_power
        self.thermal_conductivity = thermal_conductivity
        self.theta_jb = theta_jb
        self.theta_jc = theta_jc
        self.height = height
        self.extent_bounding_box = extent_bounding_box
        self.heatsink: Optional[HeatSinkConfig] = heatsink

    def set_heatsink(
        self,
        fin_base_height=None,
        fin_height=None,
        fin_orientation=None,
        fin_spacing=None,
        fin_thickness=None,
    ) -> HeatSinkConfig:
        """Attach heat-sink properties to the package definition.

        Returns
        -------
        HeatSinkConfig
            Newly created heat-sink configuration object.
        """
        self.heatsink = HeatSinkConfig(
            fin_base_height=fin_base_height,
            fin_height=fin_height,
            fin_orientation=fin_orientation,
            fin_spacing=fin_spacing,
            fin_thickness=fin_thickness,
        )
        return self.heatsink

    def to_dict(self) -> dict:
        """Serialize the package definition.

        Returns
        -------
        dict
            Dictionary ready for inclusion in the
            ``package_definitions`` configuration list.
        """
        data: dict = {"name": self.name, "component_definition": self.component_definition}
        for k in (
            "apply_to_all",
            "maximum_power",
            "thermal_conductivity",
            "theta_jb",
            "theta_jc",
            "height",
            "extent_bounding_box",
        ):
            val = getattr(self, k)
            if val is not None:
                data[k] = val
        if self.components:
            data["components"] = self.components
        if self.heatsink is not None:
            hs = self.heatsink.to_dict()
            if hs:
                data["heatsink"] = hs
        return data


class PackageDefinitionsConfig:
    """Fluent builder for the ``package_definitions`` configuration list."""

    def __init__(self):
        self._packages: List[PackageDefinitionConfig] = []

    def add(
        self,
        name: str,
        component_definition: str,
        apply_to_all: Optional[bool] = None,
        components: Optional[List[str]] = None,
        **kwargs,
    ) -> PackageDefinitionConfig:
        """Add a package definition entry.

        Parameters
        ----------
        name : str
            Package definition name.
        component_definition : str
            Target component definition.
        apply_to_all : bool, optional
            Whether the package applies to all matching components.
        components : list[str], optional
            Explicit component instances to target.
        **kwargs
            Additional thermal properties forwarded to
            :class:`PackageDefinitionConfig`.

        Returns
        -------
        PackageDefinitionConfig
            Newly created package definition.
        """
        pkg = PackageDefinitionConfig(
            name=name,
            component_definition=component_definition,
            apply_to_all=apply_to_all,
            components=components,
            **kwargs,
        )
        self._packages.append(pkg)
        return pkg

    def to_list(self) -> List[dict]:
        """Serialize all configured package definitions.

        Returns
        -------
        list[dict]
            Package definitions in insertion order.
        """
        return [p.to_dict() for p in self._packages]
