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

from pyedb.configuration.cfg_common import CfgBase
from pyedb.generic.settings import settings


class CfgPackage(CfgBase):
    """Configuration package class."""

    # Attributes cannot be set to package definition class or don't exist in package definition class.
    protected_attributes = ["name", "apply_to_all", "components", "extent_bounding_box", "component_definition"]

    def __init__(
        self,
        name=None,
        component_definition=None,
        apply_to_all=None,
        components=None,
        maximum_power=None,
        thermal_conductivity=None,
        theta_jb=None,
        theta_jc=None,
        height=None,
        extent_bounding_box=None,
        heatsink=None,
        **kwargs,
    ):
        self.name = name if name is not None else kwargs.get("name", None)
        self.component_definition = (
            component_definition if component_definition is not None else kwargs.get("component_definition", None)
        )
        self.maximum_power = maximum_power if maximum_power is not None else kwargs.get("maximum_power", None)
        self.thermal_conductivity = (
            thermal_conductivity if thermal_conductivity is not None else kwargs.get("thermal_conductivity", None)
        )
        self.theta_jb = theta_jb if theta_jb is not None else kwargs.get("theta_jb", None)
        self.theta_jc = theta_jc if theta_jc is not None else kwargs.get("theta_jc", None)
        self.height = height if height is not None else kwargs.get("height", None)
        self.apply_to_all = apply_to_all if apply_to_all is not None else kwargs.get("apply_to_all", None)
        self.components = components if components is not None else kwargs.get("components", [])
        self.extent_bounding_box = (
            extent_bounding_box if extent_bounding_box is not None else kwargs.get("extent_bounding_box", None)
        )
        heatsink_data = heatsink if heatsink is not None else kwargs.get("heatsink")
        self._heatsink = CfgHeatSink(**heatsink_data) if isinstance(heatsink_data, dict) and heatsink_data else None

    @property
    def heatsink(self):
        """CfgHeatSink or None: Heat-sink geometry attached to this package."""
        return self._heatsink

    @heatsink.setter
    def heatsink(self, value):
        """Set the heat-sink geometry.

        Parameters
        ----------
        value : CfgHeatSink or None
        """
        self._heatsink = value

    def set_heatsink(
        self,
        fin_base_height=None,
        fin_height=None,
        fin_orientation=None,
        fin_spacing=None,
        fin_thickness=None,
    ):
        """Attach heat-sink fin geometry to this package definition.

        Parameters
        ----------
        fin_base_height : str, optional
            Base height of the fin array, e.g. ``"0.5mm"``.
        fin_height : str, optional
            Fin height, e.g. ``"3mm"``.
        fin_orientation : str, optional
            Fin orientation: ``"x_oriented"`` or ``"y_oriented"``.
        fin_spacing : str, optional
            Centre-to-centre fin spacing, e.g. ``"1mm"``.
        fin_thickness : str, optional
            Fin thickness, e.g. ``"0.2mm"``.

        Returns
        -------
        CfgHeatSink
            The newly created heat-sink object.

        Examples
        --------
        >>> pkg.set_heatsink(
        ...     fin_base_height="0.5mm",
        ...     fin_height="3mm",
        ...     fin_orientation="x_oriented",
        ...     fin_spacing="1mm",
        ...     fin_thickness="0.2mm",
        ... )
        """
        self.heatsink = CfgHeatSink(
            fin_base_height=fin_base_height,
            fin_height=fin_height,
            fin_orientation=fin_orientation,
            fin_spacing=fin_spacing,
            fin_thickness=fin_thickness,
        )
        return self.heatsink

    def to_dict(self) -> dict:
        """Serialize the package definition."""
        data = {
            "name": self.name,
            "component_definition": self.component_definition,
        }
        for key in (
            "apply_to_all",
            "maximum_power",
            "thermal_conductivity",
            "theta_jb",
            "theta_jc",
            "height",
            "extent_bounding_box",
        ):
            value = getattr(self, key)
            if value not in [None, [], {}]:
                data[key] = value
        if self.components:
            data["components"] = self.components
        if self.heatsink is not None:
            hs = self.heatsink.to_dict()
            if hs:
                data["heatsink"] = hs
        return data


class CfgHeatSink(CfgBase):
    """Configuration heat sink class."""

    def __init__(self, **kwargs):
        self.fin_base_height = kwargs.get("fin_base_height", None)
        self.fin_height = kwargs.get("fin_height", None)
        self.fin_orientation = kwargs.get("fin_orientation", None)
        self.fin_spacing = kwargs.get("fin_spacing", None)
        self.fin_thickness = kwargs.get("fin_thickness", None)

    def to_dict(self) -> dict:
        """Serialize non-null heat-sink properties."""
        return self.get_attributes()


class CfgPackageDefinitions:
    """Manage thermal package definitions for the ``package_definitions`` section."""

    def get_parameter_from_edb(self):
        """Read thermal package definitions from the open EDB design.

        Returns
        -------
        list of dict
            Serialized package definition payloads.
        """
        package_definitions = []
        for pkg_name, pkg_obj in self._pedb.definitions.package.items():
            pkg = {}
            pkg_attrs = [i for i in dir(pkg_obj) if not i.startswith("_")]
            pkg_attrs = {i for i in pkg_attrs if i in CfgPackage().__dict__}
            for pkg_attr_name in pkg_attrs:
                pkg[pkg_attr_name] = getattr(pkg_obj, pkg_attr_name)
            hs_obj = pkg_obj.heat_sink
            if hs_obj:
                hs = {}
                hs_attrs = [i for i in dir(hs_obj) if not i.startswith("_")]
                hs_attrs = [i for i in hs_attrs if i in CfgHeatSink().__dict__]
                for hs_attr_name in hs_attrs:
                    hs[hs_attr_name] = getattr(hs_obj, hs_attr_name)
                pkg["heatsink"] = hs
            package_definitions.append(pkg)

        return package_definitions

    def set_parameter_to_edb(self):
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
                attrs = pkg.heatsink.get_attributes()
                package_def.set_heatsink(**attrs)

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

    def __init__(self, pedb=None, data=None):
        self._pedb = pedb
        self.packages = [CfgPackage(**package) for package in (data or [])]

    def add(
        self,
        name,
        component_definition,
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
        >>> pkg = cfg.package_definitions.add(
        ...     "PKG_U1",
        ...     component_definition="IC_U1",
        ...     apply_to_all=True,
        ...     maximum_power="5W",
        ...     theta_jb="10C/W",
        ...     theta_jc="5C/W",
        ...     height="1mm",
        ... )
        >>> pkg.set_heatsink(fin_base_height="0.5mm", fin_height="3mm")
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
        self.set_parameter_to_edb()

    def get_data_from_db(self):
        """Read package definitions from EDB (alias for :meth:`get_parameter_from_edb`).

        Returns
        -------
        list of dict
        """
        return self.get_parameter_from_edb()

    def to_list(self):
        """Serialize all configured package definitions.

        Returns
        -------
        list of dict
        """
        return [p.to_dict() for p in self.packages]
