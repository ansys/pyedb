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

from pyedb.configuration.data_model.cfg_s_parameter_models_data import CfgSparameter
from pyedb.configuration.data_model.cfg_spice_models_data import CfgSpiceModel
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

    def load_s_parameters_models_from_layout(self) -> list[CfgSparameter]:
        """Load S-parameter component definition configuration.

        Returns
        -------
        list[CfgSparameter]
        """

        self._pedb.configuration.s_parameters = []
        for s_param in [cmp for ref, cmp in self.component.items() if cmp.component_models]:
            for model in s_param.component_models:
                if model.component_model_type.name == "N_PORT":
                    cfg_model = CfgSparameter()
                    cfg_model.component_definition = s_param.name
                    cfg_model.name = model.name
                    cfg_model.components = list(s_param.components.keys())
                    cfg_model.file_path = s_param.reference_file
                    cfg_model.apply_to_all = True
                    cfg_model.reference_net = ""
                    self._pedb.configuration.s_parameters.append(cfg_model)
        return self._pedb.configuration.s_parameters

    def load_spice_models_from_layout(self) -> list[CfgSpiceModel]:
        """Load Spice model component definition configuration.

        Returns
        -------
        list[CfgSpiceModel]
        """

        self._pedb.configuration.spice_models = []
        for spice in [cmp for ref, cmp in self.component.items() if cmp.component_models]:
            for model in spice.component_models:
                if model.component_model_type.name == "SPICE":
                    cfg_spice = CfgSpiceModel
                    cfg_spice.component_definition = spice.name
                    cfg_spice.name = model.name
                    cfg_spice.components = list(spice.components.keys())
                    cfg_spice.file_path = spice.reference_file
                    cfg_spice.apply_to_all = True
                    cfg_spice.reference_net = ""
                    cfg_spice.sub_circuit_name = model.name
                    self._pedb.configuration.spice_models.append(cfg_spice)
        return self._pedb.configuration.spice_models
