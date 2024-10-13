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


class CfgRlcModel(CfgBase):
    def __init__(self, **kwargs):
        self.resistance = kwargs.get("resistance", None)
        self.inductance = kwargs.get("inductance", None)
        self.capacitance = kwargs.get("capacitance", None)
        self.type = kwargs.get("type", None)
        self.p1 = kwargs.get("p1", None)
        self.p2 = kwargs.get("p2", None)


class CfgComponent(CfgBase):
    def __init__(self, **kwargs):
        self.enabled = kwargs.get("enabled", None)
        self.reference_designator = kwargs.get("reference_designator", None)
        self.definition = kwargs.get("definition", None)
        self.type = kwargs["part_type"].lower() if kwargs.get("part_type") else None
        self.port_properties = kwargs.get("port_properties", {})
        self.solder_ball_properties = kwargs.get("solder_ball_properties", {})
        self.ic_die_properties = kwargs.get("ic_die_properties", {})
        self.pin_pair_model = kwargs.get("pin_pair_model", None)
        self.spice_model = kwargs.get("spice_model", None)
        self.s_parameter_model = kwargs.get("s_parameter_model", None)


class CfgComponents:
    def __init__(self, pedb, components_data):
        self._pedb = pedb
        self.components = [CfgComponent(**comp) for comp in components_data]

    def apply(self):
        comps_in_db = self._pedb.components
        for comp in self.components:
            c_db = comps_in_db.instances[comp.reference_designator]
            if comp.definition:
                c_db.definition = comp.definition
            if comp.type:
                c_db.type = comp.type
            if comp.solder_ball_properties:
                c_db.solder_ball_properties = comp.solder_ball_properties
            if comp.port_properties:
                c_db.port_properties = comp.port_properties
            if comp.ic_die_properties:
                c_db.ic_die_properties = comp.ic_die_properties
            if comp.pin_pair_model:
                c_db.model_properties = {"pin_pair_model": comp.pin_pair_model}
            if comp.spice_model:
                c_db.model_properties = {"spice_model": comp.spice_model}
            if comp.s_parameter_model:
                c_db.model_properties = {"s_parameter_model": comp.s_parameter_model}

    def _load_data_from_db(self):
        self.components = []
        comps_in_db = self._pedb.components
        for _, comp in comps_in_db.instances.items():
            cfg_comp = CfgComponent(
                enabled=comp.enabled,
                reference_designator=comp.name,
                part_type=comp.type,
                pin_pair_model=comp.model_properties.get("pin_pair_model"),
                spice_model=comp.model_properties.get("spice_model"),
                s_parameter_model=comp.model_properties.get("s_parameter_model"),
                definition=comp.component_def,
                location=comp.location,
                placement_layer=comp.placement_layer,
                solder_ball_properties=comp.solder_ball_properties,
                ic_die_properties=comp.ic_die_properties,
                port_properties=comp.port_properties,
            )
            self.components.append(cfg_comp)

    def get_data_from_db(self):
        self._load_data_from_db()
        data = []
        for comp in self.components:
            data.append(comp.get_attributes())
        return data
