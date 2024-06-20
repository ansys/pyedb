# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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

from pyedb.configuration.cfg_common import CfgBase
from pyedb.dotnet.edb_core.definition.package_def import PackageDef


class CfgPackage(CfgBase):
    """Configuration package class."""

    # Attributes cannot be set to package definition class or don't exist in package definition class.
    protected_attributes = ["apply_to_all", "components", "extent_bounding_box", "component_definition"]

    def __init__(self, **kwargs):
        self.name = kwargs.get("name", None)
        self.component_definition = kwargs.get("component_definition", None)
        self.maximum_power = kwargs.get("maximum_power", None)
        self.therm_cond = kwargs.get("therm_cond", None)
        self.theta_jb = kwargs.get("theta_jb", None)
        self.theta_jc = kwargs.get("theta_jc", None)
        self.height = kwargs.get("height", None)
        self.apply_to_all = kwargs.get("apply_to_all", None)
        self.components = kwargs.get("components", [])
        self.extent_bounding_box = kwargs.get("extent_bounding_box", None)
        self._heatsink = CfgHeatSink(**kwargs["heatsink"]) if "heatsink" in kwargs else None

    @property
    def heatsink(self):
        return self._heatsink

    @heatsink.setter
    def heatsink(self, value):
        self._heatsink = value


class CfgHeatSink(CfgBase):
    """Configuration heat sink class."""

    def __init__(self, **kwargs):
        self.fin_base_height = kwargs.get("fin_base_height", None)
        self.fin_height = kwargs.get("fin_height", None)
        self.fin_orientation = kwargs.get("fin_orientation", None)
        self.fin_spacing = kwargs.get("fin_spacing", None)
        self.fin_thickness = kwargs.get("fin_thickness", None)


class CfgPackageDefinitions:
    def __init__(self, pedb, data):
        self._pedb = pedb
        self.packages = [CfgPackage(**package) for package in data]

    def apply(self):
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
                for attr, value in attrs.items():
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

    def get_data_from_db(self):
        package_definitions = []

        for pkg_name, pkg_obj in self._pedb.definitions.package.items():
            pkg = {}
            pkg_attrs = [i for i in dir(pkg_obj) if not i.startswith("_")]
            pkg_attrs = {i for i in pkg_attrs if i in CfgPackage().__dict__}
            for pkg_attr_name in pkg_attrs:
                pkg[pkg_attr_name] = getattr(pkg_obj, pkg_attr_name)

            hs_obj = pkg_obj.heatsink
            if hs_obj:
                hs = {}
                hs_attrs = [i for i in dir(hs_obj) if not i.startswith("_")]
                hs_attrs = [i for i in hs_attrs if i in CfgHeatSink().__dict__]
                for hs_attr_name in hs_attrs:
                    hs[hs_attr_name] = getattr(hs_obj, hs_attr_name)
                pkg["heatsink"] = hs
            package_definitions.append(pkg)

        return package_definitions
