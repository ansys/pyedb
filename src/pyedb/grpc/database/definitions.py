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

from ansys.edb.core.geometry.polygon_data import PolygonData as GrpcPolygonData

from pyedb.grpc.database.definition.component_def import ComponentDef
from pyedb.grpc.database.definition.package_def import PackageDef


class Definitions:
    def __init__(self, pedb):
        self._pedb = pedb

    @property
    def component(self):
        """Component definitions"""
        return {l.name: ComponentDef(self._pedb, l) for l in self._pedb.active_db.component_defs}

    @property
    def package(self):
        """Package definitions."""
        return {l.name: PackageDef(self._pedb, l) for l in self._pedb.active_db.package_defs}

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
        if not name in self.package:
            package_def = PackageDef.create(self._pedb.active_db, name=name)
            if component_part_name in self.component:
                definition = self.component[component_part_name]
                if not boundary_points and not definition.is_null:
                    package_def.exterior_boundary = GrpcPolygonData(
                        points=list(definition.components.values())[0].bounding_box
                    )
            if boundary_points:
                package_def.exterior_boundary = GrpcPolygonData(points=boundary_points)
            return PackageDef(self._pedb, package_def)
        return False
