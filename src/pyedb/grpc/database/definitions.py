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

from typing import Dict, List, Optional, Union

from ansys.edb.core.geometry.polygon_data import PolygonData as GrpcPolygonData

from pyedb.grpc.database.definition.component_def import ComponentDef
from pyedb.grpc.database.definition.package_def import PackageDef


class Definitions:
    def __init__(self, pedb) -> None:
        self._pedb = pedb

    @property
    def components(self) -> Dict[str, ComponentDef]:
        """Component definitions

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb()
        >>> component_defs = edb.definitions.component
        >>> for name, comp_def in component_defs.items():
        ...     print(f"Component: {name}, Part: {comp_def.part}")
        """
        return {l.name: ComponentDef(self._pedb, l) for l in self._pedb.active_db.component_defs}

    @property
    def packages(self) -> Dict[str, PackageDef]:
        """Package definitions.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb()
        >>> package_defs = edb.definitions.package
        >>> for name, pkg_def in package_defs.items():
        ...     print(f"Package: {name}, Boundary: {pkg_def.exterior_boundary}")
        """
        return {l.name: PackageDef(self._pedb, l) for l in self._pedb.active_db.package_defs}

    @property
    def apd_bondwires(self):
        """Get all APD bondwire definitions in this Database.

        Returns
        -------
        list[:class:`ApdBondwireDef <ansys.edb.definition.ApdBondwireDef>`]
        """
        from pyedb.grpc.database.definition.wirebond_def import ApdBondwireDef

        return {
            apd_def.name.value: ApdBondwireDef(self._pedb, apd_def)
            for apd_def in self._pedb.active_db.apd_bondwire_defs
        }

    @property
    def jedec4_bondwires(self):
        """Get all JEDEC4 bondwire definitions in this Database.

        Returns
        -------
        list[:class:`Jedec4BondwireDef <ansys.edb.definition.Jedec4BondwireDef>`]
        """
        from pyedb.grpc.database.definition.wirebond_def import Jedec4BondwireDef

        return {
            apd_def.name.value: Jedec4BondwireDef(self._pedb, apd_def)
            for apd_def in self._pedb.active_db.jedec4_bondwire_defs
        }

    @property
    def jedec5_bondwires(self):
        """Get all JEDEC5 bondwire definitions in this Database.

        Returns
        -------
        list[:class:`Jedec5BondwireDef <ansys.edb.definition.Jedec5BondwireDef>`]
        """
        from pyedb.grpc.database.definition.wirebond_def import Jedec5BondwireDef

        return {
            jedec5_def.name.value: Jedec5BondwireDef(self._pedb, jedec5_def)
            for jedec5_def in self._pedb.active_db.jedec5_bondwire_defs
        }

    def add_package_def(
        self, name: str, component_part_name: Optional[str] = None, boundary_points: Optional[List[List[float]]] = None
    ) -> Union[PackageDef, bool]:
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
        PackageDef object.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb()

        Example 1: Create package using component's bounding box
        >>> comp_def = edb.definitions.add_package_def("QFP64", "QFP64_COMPONENT")
        >>> if comp_def:  # Check if created successfully
        ...     print(f"Created package: {comp_def.name}")

        Example 2: Create package with custom boundary
        >>> boundary = [[0, 0], [10e-3, 0], [10e-3, 10e-3], [0, 10e-3]]
        >>> custom_pkg = edb.definitions.add_package_def("CustomIC", boundary_points=boundary)
        >>> if custom_pkg:
        ...     print(f"Custom package boundary: {custom_pkg.exterior_boundary}")
        """
        if not name in self.packages:
            package_def = PackageDef.create(self._pedb, name)
            if component_part_name in self.components:
                definition = self.components[component_part_name]
                if not boundary_points and not definition.is_null:
                    package_def.exterior_boundary = GrpcPolygonData(
                        points=list(definition.components.values())[0].bounding_box
                    )
            if boundary_points:
                package_def.exterior_boundary = GrpcPolygonData(points=boundary_points)
            return package_def
        return False
