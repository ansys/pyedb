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

import os

from ansys.edb.core.definition.component_def import ComponentDef as GrpcComponentDef


class EDBComponentDef(GrpcComponentDef):
    """Manages EDB functionalities for component definitions.

    Parameters
    ----------
    pedb : :class:`pyedb.edb`
        Inherited AEDT object.
    edb_object : object
        Edb ComponentDef Object
    """

    def __init__(self, pedb):
        super().__init__(self.msg)
        self._pedb = pedb

    @property
    def part_name(self):
        """Retrieve component definition name."""
        return self.name

    @part_name.setter
    def part_name(self, name):
        self.name = name

    @property
    def type(self):
        """Retrieve the component definition type.

        Returns
        -------
        str
        """
        return self.definition_type.name.lower()

    @property
    def components(self):
        """Get the list of components belonging to this component definition.

        Returns
        -------
        dict of :class:`EDBComponent`
        """
        from ansys.edb.core.hierarchy.component_group import (
            ComponentGroup as GrpcComponentGroup,
        )

        from pyedb.dotnet.edb_core.cell.hierarchy.component import EDBComponent

        comp_list = [
            EDBComponent(self._pedb, l)
            for l in GrpcComponentGroup.find_by_def(self._pedb.active_layout, self.part_name)
        ]
        return {comp.refdes: comp for comp in comp_list}

    def assign_rlc_model(self, res=None, ind=None, cap=None, is_parallel=False):
        """Assign RLC to all components under this part name.

        Parameters
        ----------
        res : int, float
            Resistance. Default is ``None``.
        ind : int, float
            Inductance. Default is ``None``.
        cap : int, float
            Capacitance. Default is ``None``.
        is_parallel : bool, optional
            Whether it is parallel or series RLC component.
        """
        for comp in list(self.components.values()):
            res, ind, cap = res, ind, cap
            comp.assign_rlc_model(res, ind, cap, is_parallel)
        return True

    def assign_s_param_model(self, file_path, model_name=None, reference_net=None):
        """Assign S-parameter to all components under this part name.

        Parameters
        ----------
        file_path : str
            File path of the S-parameter model.
        name : str, optional
            Name of the S-parameter model.

        Returns
        -------

        """
        for comp in list(self.components.values()):
            comp.assign_s_param_model(file_path, model_name, reference_net)
        return True

    def assign_spice_model(self, file_path, model_name=None):
        """Assign Spice model to all components under this part name.

        Parameters
        ----------
        file_path : str
            File path of the Spice model.
        name : str, optional
            Name of the Spice model.

        Returns
        -------

        """
        for comp in list(self.components.values()):
            comp.assign_spice_model(file_path, model_name)
        return True

    @property
    def reference_file(self):
        return [model.reference_file for model in self.component_models]

    @property
    def component_models(self):
        return {model.name: model for model in self.component_models}

    def add_n_port_model(self, fpath, name=None):
        from ansys.edb.core.definition.component_model import (
            NPortComponentModel as GrpcNPortComponentModel,
        )

        if not name:
            name = os.path.splitext(os.path.basename(fpath)[0])
        n_port_comp_model = GrpcNPortComponentModel.create(name)
        n_port_comp_model.reference_file = fpath
        self.add_component_model(n_port_comp_model)

    def create(self, name):
        from ansys.edb.core.layout.cell import Cell as GrpcCell
        from ansys.edb.core.layout.cell import CellType as GrpcCellType

        footprint_cell = GrpcCell.create(self._pedb.active_db, GrpcCellType.FOOTPRINT_CELL, name)
        edb_object = GrpcComponentDef.create(self._pedb.active_db, name, footprint_cell)
        return EDBComponentDef(self._pedb, edb_object)
