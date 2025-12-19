# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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

from pyedb.grpc.database.definition.component_pin import ComponentPin
from pyedb.grpc.database.hierarchy.component import Component


class ComponentDef:
    """Manages EDB functionalities for component definitions.

    Parameters
    ----------
    edb_object : object
        Edb ComponentDef Object
    """

    def __init__(self, pedb, edb_object):
        self.core = edb_object
        self._pedb = pedb

    @property
    def part_name(self) -> str:
        """Component definition name.

        Returns
        -------
        str
            Component part name.

        """
        return self.core.name

    @part_name.setter
    def part_name(self, name):
        self.core.name = name

    @property
    def type(self) -> str:
        """Component definition type.

        Returns
        -------
        str
            Component definition type.
        """
        if self.components:
            return list(self.components.values())[0].type
        else:
            return ""

    @type.setter
    def type(self, value):
        if value.lower() == "resistor":
            for _, component in self.components.items():
                component.type = "resistor"
        elif value.lower() == "inductor":
            for _, component in self.components.items():
                component.type = "inductor"
        elif value.lower() == "capacitor":
            for _, component in self.components.items():
                component.type = "capacitor"
        elif value.lower() == "ic":
            for _, component in self.components.items():
                component.type = "ic"
        elif value.lower() == "io":
            for _, component in self.components.items():
                component.type = "io"
        elif value.lower() == "other":
            for _, component in self.components.items():
                component.type = "other"
        else:
            return

    @property
    def components(self) -> dict[str, Component]:
        """Component instances belonging to the definition.

        Returns
        -------
        dict[str, :class:`Component <pyedb.grpc.database.hierarchy.component.Component>`]
        """
        from ansys.edb.core.hierarchy.component_group import ComponentGroup as GrpcComponent

        comp_list = [
            Component(self._pedb, l) for l in GrpcComponent.find_by_def(self._pedb.active_layout.core, self.part_name)
        ]
        return {comp.refdes: comp for comp in comp_list}

    @property
    def is_null(self) -> bool:
        """Check if the component definition is null.

        Returns
        -------
        bool
            True if the component definition is null, False otherwise.

        """
        return self.core.is_null

    @property
    def component_pins(self) -> list[ComponentPin]:
        """Component pins.

        Returns
        -------
        list[:class:`ComponentPin <pyedb.grpc.database.definition.component_pin.ComponentPin>`]

        """
        return [ComponentPin(pin) for pin in self.core.component_pins]

    @classmethod
    def find(cls, edb, name):
        """Find component definition by name.

        Parameters
        ----------
        edb : :class:`pyedb.grpc.edb.Edb`
            EDB database object.
        name : str
            Component definition name.

        Returns
        -------
        :class:`ComponentDef <pyedb.grpc.database.definition.component_def.ComponentDef>` or None
        """
        core_comp_def = GrpcComponentDef.find(edb.db, name)
        if not core_comp_def.is_null:
            return ComponentDef(edb, core_comp_def)
        return None

    @classmethod
    def create(cls, edb, name, fp=None):
        """Create a new component definition.

        Parameters
        ----------
        edb : :class:`pyedb.grpc.edb.Edb`
            EDB database object.
        name : str
            Component definition name.
        fp : str, optional
           Footprint cell name.

        Returns
        -------
        :class:`ComponentDef <pyedb.grpc.database.definition.component_def.ComponentDef>`
        """
        component_def = GrpcComponentDef.create(edb.db, name, fp)
        return ComponentDef(edb, component_def)

    def assign_rlc_model(self, res=None, ind=None, cap=None, is_parallel=False) -> bool:
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

        Returns
        -------
        bool

        """
        for comp in list(self.components.values()):
            res, ind, cap = res, ind, cap
            comp.assign_rlc_model(res, ind, cap, is_parallel)
        return True

    def assign_s_param_model(self, file_path, model_name=None, reference_net=None) -> bool:
        """Assign S-parameter to all components under this part name.

        Parameters
        ----------
        file_path : str
            File path of the S-parameter model.
        model_name : str, optional
            Name of the S-parameter model.

        reference_net : str, optional
            Name of the reference net.

        Returns
        -------
        bool

        """
        for comp in list(self.components.values()):
            comp.assign_s_param_model(file_path, model_name, reference_net)
        return True

    def assign_spice_model(self, file_path, model_name=None) -> bool:
        """Assign Spice model to all components under this part name.

        Parameters
        ----------
        file_path : str
            File path of the Spice model.
        model_name : str, optional
            Name of the Spice model.

        Returns
        -------
        bool
        """
        for comp in list(self.components.values()):
            comp.assign_spice_model(file_path, model_name)
        return True

    @property
    def reference_file(self) -> list[str]:
        """Model reference file.

        Returns
        -------
        list[str]
            List of reference files.

        """
        return [model.reference_file for model in self.component_models]

    @property
    def component_models(self):
        """Component models.

        Returns
        -------
        list[:class:`ComponentModel <ansys.edb.core.definition.component_model.ComponentModel>`]

        """
        return self.core.component_models

    @property
    def name(self):
        """Component definition name.

        Returns
        -------
        str
            Component definition name.

        """
        return self.core.name

    @name.setter
    def name(self, value):
        self.core.name = value

    def add_n_port_model(self, fpath, name=None):
        """Add N-port model.

        Returns
        -------
        Nport model : :class:`NPortComponentModel <ansys.edb.core.definition.component_model.NPortComponentModel>`

        """

        from ansys.edb.core.definition.component_model import (
            NPortComponentModel as GrpcNPortComponentModel,
        )

        if not name:
            name = os.path.splitext(os.path.basename(fpath)[0])
        model = [model for model in self.component_models if model.name == name]
        if model:
            raise RuntimeError(f"Model {name} already defined for component definition {self.name}")
        n_port_model = GrpcNPortComponentModel.create(name=name)
        n_port_model.reference_file = fpath
        self.core.add_component_model(n_port_model)
        return n_port_model

    def get_properties(self):
        data = {}
        temp = []
        for i in self.component_pins:
            temp.append(i.name)
        data["pin_order"] = temp
        return data

    def set_properties(self, **kwargs):
        pin_order = kwargs.get("pin_order")
        if pin_order:
            old = {i.name: i for i in self.component_pins}
            temp = [old[str(i)] for i in pin_order]
            self.core.reorder_pins(temp)
