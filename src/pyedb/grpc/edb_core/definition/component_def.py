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

from pyedb.dotnet.edb_core.definition.component_model import NPortComponentModel
from pyedb.dotnet.edb_core.utilities.obj_base import ObjBase


class EDBComponentDef(ObjBase):
    """Manages EDB functionalities for component definitions.

    Parameters
    ----------
    pedb : :class:`pyedb.edb`
        Inherited AEDT object.
    edb_object : object
        Edb ComponentDef Object
    """

    def __init__(self, pedb, edb_object=None):
        super().__init__(pedb, edb_object)
        self._pedb = pedb

    @property
    def _comp_model(self):
        return list(self._edb_object.GetComponentModels())  # pragma: no cover

    @property
    def part_name(self):
        """Retrieve component definition name."""
        return self._edb_object.GetName()

    @part_name.setter
    def part_name(self, name):
        self._edb_object.SetName(name)

    @property
    def type(self):
        """Retrieve the component definition type.

        Returns
        -------
        str
        """
        num = len(set(comp.type for refdes, comp in self.components.items()))
        if num == 0:  # pragma: no cover
            return None
        elif num == 1:
            return list(self.components.values())[0].type
        else:
            return "mixed"  # pragma: no cover

    @type.setter
    def type(self, value):
        for comp in list(self.components.values()):
            comp.type = value

    @property
    def components(self):
        """Get the list of components belonging to this component definition.

        Returns
        -------
        dict of :class:`EDBComponent`
        """
        from pyedb.dotnet.edb_core.cell.hierarchy.component import EDBComponent

        comp_list = [
            EDBComponent(self._pedb, l)
            for l in self._pedb.edb_api.cell.hierarchy.component.FindByComponentDef(
                self._pedb.active_layout, self.part_name
            )
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
        ref_files = []
        for comp_model in self._comp_model:
            model_type = str(comp_model.GetComponentModelType())
            if model_type == "NPortComponentModel" or model_type == "DynamicLinkComponentModel":
                ref_files.append(comp_model.GetReferenceFile())
        return ref_files

    @property
    def component_models(self):
        temp = {}
        for i in list(self._edb_object.GetComponentModels()):
            temp_type = i.ToString().split(".")[0]
            if temp_type == "NPortComponentModel":
                edb_object = NPortComponentModel(self._pedb, i)
                temp[edb_object.name] = edb_object
        return temp

    def _add_component_model(self, value):
        self._edb_object.AddComponentModel(value._edb_object)

    def add_n_port_model(self, fpath, name=None):
        if not name:
            name = os.path.splitext(os.path.basename(fpath)[0])

        from pyedb.dotnet.edb_core.definition.component_model import NPortComponentModel

        edb_object = self._pedb.definition.NPortComponentModel.Create(name)
        n_port_comp_model = NPortComponentModel(self._pedb, edb_object)
        n_port_comp_model.reference_file = fpath

        self._add_component_model(n_port_comp_model)

    def create(self, name):
        cell_type = self._pedb.edb_api.cell.CellType.FootprintCell
        footprint_cell = self._pedb._active_cell.cell.Create(self._pedb.active_db, cell_type, name)
        edb_object = self._pedb.edb_api.definition.ComponentDef.Create(self._pedb.active_db, name, footprint_cell)
        return EDBComponentDef(self._pedb, edb_object)
