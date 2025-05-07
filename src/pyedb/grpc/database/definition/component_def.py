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

from pyedb.grpc.database.definition.component_pin import ComponentPin
from pyedb.grpc.database.hierarchy.component import Component


class ComponentDef(GrpcComponentDef):
    """Manages EDB functionalities for component definitions.

    Parameters
    ----------
    pedb : :class:`Edb <pyedb.grpc.edb.Edb>`
        Inherited AEDT object.
    edb_object : object
        Edb ComponentDef Object
    """

    def __init__(self, pedb, edb_object):
        super().__init__(edb_object.msg)
        self._pedb = pedb

    @property
    def part_name(self):
        """Component definition name.

        Returns
        -------
        str
            Component part name.

        """
        return self.name

    @part_name.setter
    def part_name(self, name):
        self.name = name

    @property
    def type(self):
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
    def components(self):
        """Component instances belonging to the definition.

        Returns
        -------
        Dict : [str, :class:`Component <pyedb.grpc.database.hierarchy.component.Component>`]
        """
        comp_list = [Component(self._pedb, l) for l in Component.find_by_def(self._pedb.active_layout, self.part_name)]
        return {comp.refdes: comp for comp in comp_list}

    @property
    def component_pins(self):
        """Component pins.

        Returns
        -------
        List[:class:`ComponentPin <pyedb.grpc.database.definition.component_pin.ComponentPin>`]

        """
        return [ComponentPin(self._pedb, pin) for pin in super().component_pins]

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

        Returns
        -------
        bool

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
        bool

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
        """Model reference file.

        Returns
        -------
        List[str]
            List of reference files.

        """
        return [model.reference_file for model in self.component_models]

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
        for model in self.component_models:
            if model.model_name == name:
                self._pedb.logger.error(f"Model {name} already defined for component definition {self.name}")
                return None
        model = [model for model in self.component_models if model.name == name]
        if not model:
            n_port_model = GrpcNPortComponentModel.create(name=name)
            n_port_model.reference_file = fpath
            self.add_component_model(n_port_model)
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
            self.reorder_pins(temp)
