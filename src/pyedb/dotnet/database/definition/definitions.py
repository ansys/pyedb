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

from pyedb.dotnet.database.definition.component_def import EDBComponentDef
from pyedb.dotnet.database.definition.package_def import PackageDef
from pyedb.dotnet.database.definition.wirebond_def import ApdBondwireDef, Jedec4BondwireDef, Jedec5BondwireDefs


class Definitions:
    def __init__(self, pedb):
        self._pedb = pedb

    @property
    def component(self):
        """Component definitions"""
        return {l.GetName(): EDBComponentDef(self._pedb, l) for l in list(self._pedb.active_db.ComponentDefs)}

    @property
    def package(self):
        """Package definitions."""
        return {l.GetName(): PackageDef(self._pedb, l) for l in list(self._pedb.active_db.PackageDefs)}

    @property
    def jedec4_bondwire_defs(self):
        """Wirebond definitions."""
        objs = getattr(self._pedb.active_db, "Jedec4BondwireDefs", None)
        if not objs:
            return {}
        return {l.GetName(): Jedec4BondwireDef(self._pedb, l) for l in list(objs)}

    @property
    def jedec5_bondwire_defs(self):
        objs = getattr(self._pedb.active_db, "Jedec5BondwireDefs", None)
        if not objs:
            return {}
        return {l.GetName(): Jedec5BondwireDefs(self._pedb, l) for l in list(objs)}

    @property
    def apd_bondwire_defs(self):
        objs = getattr(self._pedb.active_db, "ApdBondwireDefs", None)
        if not objs:
            return {}
        return {l.GetName(): ApdBondwireDef(self._pedb, l) for l in list(objs)}

    def add_package_def(self, name, component_part_name=None, boundary_points=None):
        """Add a package definition.

        Parameters
        ----------
        name: str
            Name of the package definition.
        component_part_name : str, optional
            Part name of the component.
        boundary_points : list, optional
            Boundary points which define the shape of the package.

        Returns
        -------

        """
        package_def = PackageDef(
            self._pedb, name=name, component_part_name=component_part_name, extent_bounding_box=boundary_points
        )
        return package_def

    def create_jedec4_bondwire_def(self, name: str, top_to_die_distance: float = 30e-6):
        """Create a JEDEC 4 bondwire definition.

        Parameters
        ----------
        name : str
            Name of the bondwire definition.
        top_to_die_distance : float, optional
            Top to die distance in meters. The default is 30e-6.

        Returns
        -------
        Jedec4BondwireDef
            The created JEDEC 4 bondwire definition.
        """
        return Jedec4BondwireDef.create(self._pedb, name, top_to_die_distance)

    def create_jedec5_bondwire_def(self, name: str, top_to_die_distance: float = 30e-6):
        """Create a JEDEC 5 bondwire definition.

        Parameters
        ----------
        name : str
            Name of the bondwire definition.
        top_to_die_distance : float, optional
            Top to die distance in meters. The default is 30e-6.

        Returns
        -------
        Jedec5BondwireDef
            The created JEDEC 5 bondwire definition.
        """
        return Jedec5BondwireDefs.create(self._pedb, name, top_to_die_distance)

    def create_apd_bondwire_def(self, name: str, top_to_die_distance: float = 30e-6):
        """Create an APD bondwire definition.

        Parameters
        ----------
        name : str
            Name of the bondwire definition.
        top_to_die_distance : float, optional
            Top to die distance in meters. The default is 30e-6.

        Returns
        -------
        ApdBondwireDef
            The created APD bondwire definition.
        """
        return ApdBondwireDef.create(self._pedb, name, top_to_die_distance)
