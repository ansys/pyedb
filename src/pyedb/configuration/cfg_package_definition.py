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

"""Build thermal package-definition configuration entries."""

from typing import Any, List, Optional

from pydantic import Field

from pyedb.configuration.cfg_common import CfgBaseModel
from pyedb.generic.settings import settings


class CfgHeatSink(CfgBaseModel):
    """Configuration heat sink class."""

    model_config = {"populate_by_name": True, "extra": "ignore"}

    fin_base_height: Optional[Any] = None
    fin_height: Optional[Any] = None
    fin_orientation: Optional[str] = None
    fin_spacing: Optional[Any] = None
    fin_thickness: Optional[Any] = None

    def get_attributes(self, exclude=None):
        """Return non-null attribute dict (CfgBase compatibility).

        Parameters
        ----------
        exclude : list, optional
            List of field names to exclude from the result.
        """
        return self.model_dump(exclude_none=True, exclude=set(exclude) if exclude else None)


class CfgPackage(CfgBaseModel):
    """Configuration package class."""

    model_config = {"populate_by_name": True, "extra": "ignore", "arbitrary_types_allowed": True}

    # Attributes cannot be set to package definition class or don't exist in package definition class.
    _protected_attributes: List[str] = [
        "name",
        "apply_to_all",
        "components",
        "extent_bounding_box",
        "component_definition",
    ]

    name: Optional[str] = None
    component_definition: Optional[str] = None
    apply_to_all: Optional[bool] = None
    components: List[str] = Field(default_factory=list)
    maximum_power: Optional[Any] = None
    thermal_conductivity: Optional[Any] = None
    theta_jb: Optional[Any] = None
    theta_jc: Optional[Any] = None
    height: Optional[Any] = None
    extent_bounding_box: Optional[Any] = None
    heatsink: Optional[CfgHeatSink] = None

    def get_attributes(self, exclude=None):
        """Return dict of non-null/non-protected attributes (CfgBase compatibility)."""
        protected = set(self._protected_attributes) | {"heatsink"}
        if exclude:
            protected.update(exclude if isinstance(exclude, list) else [exclude])
        return {k: v for k, v in self.model_dump(exclude_none=True).items() if k not in protected}

    def set_attributes(self, pedb_object):
        """Set non-protected attributes onto *pedb_object* (CfgBase compatibility)."""
        attrs = self.get_attributes()
        for attr, value in attrs.items():
            if attr not in dir(pedb_object):
                raise AttributeError(f"Invalid attribute '{attr}' in '{pedb_object}'")
            setattr(pedb_object, attr, value)

    def set_heatsink(
        self,
        fin_base_height=None,
        fin_height=None,
        fin_orientation=None,
        fin_spacing=None,
        fin_thickness=None,
    ):
        """Attach heat sink fin geometry to this package definition.

        Parameters
        ----------
        fin_base_height : str, optional
            Base height of the fin array, e.g. ``"0.5mm"``.
        fin_height : str, optional
            Fin height, e.g. ``"3mm"``.
        fin_orientation : str, optional
            Fin orientation: ``"x_oriented"`` or ``"y_oriented"``.
        fin_spacing : str, optional
            Center-to-center fin spacing, e.g. ``"1mm"``.
        fin_thickness : str, optional
            Fin thickness, e.g. ``"0.2mm"``.

        Returns
        -------
        CfgHeatSink
            The newly created heat sink object.

        Examples
        --------
        pkg.set_heatsink(
            fin_base_height="0.5mm",
            fin_height="3mm",
            fin_orientation="x_oriented",
            fin_spacing="1mm",
            fin_thickness="0.2mm"
        )
        """
        hs = CfgHeatSink(
            fin_base_height=fin_base_height,
            fin_height=fin_height,
            fin_orientation=fin_orientation,
            fin_spacing=fin_spacing,
            fin_thickness=fin_thickness,
        )
        object.__setattr__(self, "heatsink", hs)
        return hs


class CfgPackageDefinitions:
    """Manage thermal package definitions for the ``package_definitions`` section."""

    def get_parameters_from_edb(self):
        """Read thermal package definitions from EDB."""
        package_definitions = []
        _pkg_field_names = set(CfgPackage.model_fields.keys())
        _hs_field_names = set(CfgHeatSink.model_fields.keys())
        for pkg_name, pkg_obj in self._pedb.definitions.package.items():
            pkg = {}
            pkg_attrs = [i for i in dir(pkg_obj) if not i.startswith("_")]
            pkg_attrs = {i for i in pkg_attrs if i in _pkg_field_names}
            for pkg_attr_name in pkg_attrs:
                pkg[pkg_attr_name] = getattr(pkg_obj, pkg_attr_name)
            hs_obj = pkg_obj.heat_sink
            if hs_obj:
                hs = {}
                hs_attrs = [i for i in dir(hs_obj) if not i.startswith("_")]
                hs_attrs = [i for i in hs_attrs if i in _hs_field_names]
                for hs_attr_name in hs_attrs:
                    hs[hs_attr_name] = getattr(hs_obj, hs_attr_name)
                pkg["heatsink"] = hs
            package_definitions.append(pkg)

        return package_definitions

    def set_parameters_to_edb(self):
        """Write all configured package definitions into the open EDB design."""
        if settings.is_grpc:
            from pyedb.grpc.database.definition.package_def import PackageDef
        else:
            from pyedb.dotnet.database.definition.package_def import PackageDef

        for pkg in self.packages:
            comp_def_from_db = self._pedb.definitions.component[pkg.component_definition]
            if pkg.name in self._pedb.definitions.package:
                self._pedb.definitions.package[pkg.name].delete()

            if pkg.extent_bounding_box:
                package_def = PackageDef(self._pedb, name=pkg.name, extent_bounding_box=pkg.extent_bounding_box)
            else:
                package_def = PackageDef(self._pedb, name=pkg.name, component_part_name=pkg.component_definition)
            pkg.set_attributes(package_def)

            if pkg.heatsink:
                package_def.set_heatsink(**pkg.heatsink.get_attributes())

            comp_list = dict()
            if pkg.apply_to_all:
                comp_list.update(
                    {
                        refdes: comp
                        for refdes, comp in comp_def_from_db.components.items()
                        if refdes not in pkg.components
                    }
                )
            else:
                comp_list.update(
                    {refdes: comp for refdes, comp in comp_def_from_db.components.items() if refdes in pkg.components}
                )
            for _, i in comp_list.items():
                i.package_def = pkg.name

    get_parameter_from_edb = get_parameters_from_edb
    set_parameter_to_edb = set_parameters_to_edb

    def __init__(self, pedb=None, data=None):
        self._pedb = pedb
        self.packages = [CfgPackage(**package) for package in (data or [])]

    def to_list(self):
        """Serialize all package definitions to a list of dictionaries."""
        return [p.model_dump(exclude_none=True) for p in self.packages]

    def add(
        self,
        name: str,
        component_definition: str,
        apply_to_all=None,
        components=None,
        maximum_power=None,
        thermal_conductivity=None,
        theta_jb=None,
        theta_jc=None,
        height=None,
        extent_bounding_box=None,
    ):
        """Add a thermal package definition entry.

        Parameters
        ----------
        name : str
            Package definition name, e.g. ``"PKG_U1"``.
        component_definition : str
            Component part-definition name.
        apply_to_all : bool, optional
            Assign the package to every matching component when ``True``.
        components : list of str, optional
            Specific reference designators to target when *apply_to_all* is
            ``False``.
        maximum_power : str, optional
            Maximum power dissipation, e.g. ``"5W"``.
        thermal_conductivity : str, optional
            Package thermal conductivity.
        theta_jb : str, optional
            Junction-to-board thermal resistance, e.g. ``"10C/W"``.
        theta_jc : str, optional
            Junction-to-case thermal resistance, e.g. ``"5C/W"``.
        height : str, optional
            Package height, e.g. ``"1mm"``.
        extent_bounding_box : dict, optional
            Custom bounding-box extent override.

        Returns
        -------
        CfgPackage
            The newly created package object.  Call
            :meth:`CfgPackage.set_heatsink` on it to add fin geometry.

        Examples
        --------
        pkg = cfg.package_definitions.add(
            "PKG_U1",
            component_definition="IC_U1",
            apply_to_all=True,
            maximum_power="5W",
            theta_jb="10C/W",
            theta_jc="5C/W",
            height="1mm",
        )
        pkg.set_heatsink(fin_base_height="0.5mm", fin_height="3mm")
        """
        pkg = CfgPackage(
            name=name,
            component_definition=component_definition,
            apply_to_all=apply_to_all,
            components=components or [],
            maximum_power=maximum_power,
            thermal_conductivity=thermal_conductivity,
            theta_jb=theta_jb,
            theta_jc=theta_jc,
            height=height,
            extent_bounding_box=extent_bounding_box,
        )
        self.packages.append(pkg)
        return pkg

    def apply(self):
        """Write all configured package definitions into the open EDB design."""
        self.set_parameters_to_edb()

    def get_data_from_db(self):
        """Read package definitions from EDB."""
        return self.get_parameters_from_edb()
