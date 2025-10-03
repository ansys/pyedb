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

from pyedb.configuration.cfg_common import CfgBase
from pyedb.dotnet.database.general import pascal_to_snake, snake_to_pascal


class CfgComponent(CfgBase):
    def retrieve_model_properties_from_edb(self):
        c_p = self.pyedb_obj.component_property
        model = c_p.GetModel().Clone()

        if model.GetModelType().ToString() == "NetlistModel":
            self.netlist_model["netlist"] = model.GetNetlist()
        elif model.GetModelType().ToString() == "PinPairModel":
            temp = {}
            for i in model.PinPairs:
                temp["first_pin"] = i.FirstPin
                temp["second_pin"] = i.SecondPin
                rlc = model.GetPinPairRlc(i)
                temp["is_parallel"] = rlc.IsParallel
                temp["resistance"] = rlc.R.ToString()
                temp["resistance_enabled"] = rlc.REnabled
                temp["inductance"] = rlc.L.ToString()
                temp["inductance_enabled"] = rlc.LEnabled
                temp["capacitance"] = rlc.C.ToString()
                temp["capacitance_enabled"] = rlc.CEnabled
                self.pin_pair_model.append(temp)
        elif model.GetModelType().ToString() == "SParameterModel":
            self.s_parameter_model["reference_net"] = model.GetReferenceNet()
            self.s_parameter_model["model_name"] = model.GetComponentModelName()
        elif model.GetModelType().ToString() == "SPICEModel":
            self.spice_model["model_name"] = model.GetModelName()
            self.spice_model["model_path"] = model.GetModelPath()
            self.spice_model["sub_circuit"] = model.GetSubCkt()
            self.spice_model["terminal_pairs"] = [[i, j] for i, j in dict(model.GetTerminalPinPairs()).items()]

    def _set_ic_die_properties_to_edb(self):
        cp = self.pyedb_obj.component_property
        ic_die_prop = cp.GetDieProperty().Clone()
        die_type = self.ic_die_properties.get("type")
        ic_die_prop.SetType(getattr(self._pedb._edb.Definition.DieType, snake_to_pascal(die_type)))
        if not die_type == "no_die":
            orientation = self.ic_die_properties.get("orientation")
            if orientation:
                ic_die_prop.SetOrientation(
                    getattr(self._pedb._edb.Definition.DieOrientation, snake_to_pascal(orientation))
                )
            if die_type == "wire_bond":
                height = self.ic_die_properties.get("height")
                if height:
                    ic_die_prop.SetHeight(self._pedb.edb_value(height))
        cp.SetDieProperty(ic_die_prop)
        self.pyedb_obj.component_property = cp

    def _set_port_properties_to_edb(self):
        cp = self.pyedb_obj.component_property
        port_prop = cp.GetPortProperty().Clone()
        height = self.port_properties.get("reference_height")
        if height:
            port_prop.SetReferenceHeight(self._pedb.edb_value(height))
        reference_size_auto = self.port_properties.get("reference_size_auto")
        if reference_size_auto is not None:
            port_prop.SetReferenceSizeAuto(reference_size_auto)
        reference_size_x = self.port_properties.get("reference_size_x", 0)
        reference_size_y = self.port_properties.get("reference_size_y", 0)
        port_prop.SetReferenceSize(self._pedb.edb_value(reference_size_x), self._pedb.edb_value(reference_size_y))
        cp.SetPortProperty(port_prop)
        self.pyedb_obj.component_property = cp

    def _set_model_properties_to_edb(self):
        c_p = self.pyedb_obj.component_property
        if self.netlist_model:
            m = self._pedb._edb.Cell.Hierarchy.SParameterModel()
            m.SetNetlist(self.netlist_model["netlist"])
            c_p.SetModel(m)
            self.component_property = c_p
        elif self.pin_pair_model:
            m = self._pedb._edb.Cell.Hierarchy.PinPairModel()
            for i in self.pin_pair_model:
                p = self._pedb._edb.Utility.PinPair(str(i["first_pin"]), str(i["second_pin"]))
                res = i.get("resistance")
                if res is None:
                    # If resistance is not defined, set it to 0 and disable it
                    res = "0ohm"
                    en_res = False
                else:
                    # If resistance is defined, use the provided value and enabled status
                    res = i["resistance"]
                    en_res = i.get("resistance_enabled", True)
                ind = i.get("inductance")
                if ind is None:
                    # If inductance is not defined, set it to 0 and disable it
                    ind = "0nH"
                    en_ind = False
                else:
                    # If inductance is defined, use the provided value and enabled status
                    ind = i["inductance"]
                    en_ind = i.get("inductance_enabled", True)
                cap = i.get("capacitance")
                if cap is None:
                    # If capacitance is not defined, set it to 0 and disable it
                    cap = "0pF"
                    en_cap = False
                else:
                    # If capacitance is defined, use the provided value and enabled status
                    cap = i["capacitance"]
                    en_cap = i.get("capacitance_enabled", True)

                rlc = self._pedb._edb.Utility.Rlc(
                    self._pedb.edb_value(res),
                    en_res,
                    self._pedb.edb_value(ind),
                    en_ind,
                    self._pedb.edb_value(cap),
                    en_cap,
                    i.get("is_parallel", False),
                )
                m.SetPinPairRlc(p, rlc)
            c_p.SetModel(m)
            self.pyedb_obj.component_property = c_p
        elif self.s_parameter_model:
            m = self._pedb._edb.Cell.Hierarchy.SParameterModel()
            m.SetComponentModelName(self.s_parameter_model["model_name"])
            m.SetReferenceNet(self.s_parameter_model["reference_net"])
            c_p.SetModel(m)
            self.component_property = c_p
        elif self.spice_model:
            self.pyedb_obj.assign_spice_model(
                self.spice_model["model_path"],
                self.spice_model["model_name"],
                self.spice_model["sub_circuit"],
                self.spice_model["terminal_pairs"],
            )

    def _set_solder_ball_properties_to_edb(self):
        cp = self.pyedb_obj.component_property
        solder_ball_prop = cp.GetSolderBallProperty().Clone()
        shape = self.solder_ball_properties.get("shape")
        if shape:
            solder_ball_prop.SetShape(getattr(self._pedb._edb.Definition.SolderballShape, snake_to_pascal(shape)))
        else:
            return

        if shape == "cylinder":
            diameter = self.solder_ball_properties["diameter"]
            solder_ball_prop.SetDiameter(self._pedb.edb_value(diameter), self._pedb.edb_value(diameter))
        elif shape == "spheroid":
            diameter = self.solder_ball_properties["diameter"]
            mid_diameter = self.solder_ball_properties["mid_diameter"]
            solder_ball_prop.SetDiameter(self._pedb.edb_value(diameter), self._pedb.edb_value(mid_diameter))
        else:
            raise ValueError("Solderball shape must be either cylinder or spheroid")
        solder_ball_prop.SetHeight(self._pedb.edb_value(self.solder_ball_properties["height"]))
        solder_ball_prop.SetMaterialName(self.solder_ball_properties.get("material", "solder"))
        cp.SetSolderBallProperty(solder_ball_prop)
        self.pyedb_obj.component_property = cp

    def _retrieve_ic_die_properties_from_edb(self):
        temp = dict()
        cp = self.pyedb_obj.component_property

        ic_die_prop = cp.GetDieProperty().Clone()
        die_type = pascal_to_snake(ic_die_prop.GetType().ToString())
        temp["type"] = die_type
        if not die_type == "no_die":
            temp["orientation"] = pascal_to_snake(ic_die_prop.GetOrientation().ToString())
            if die_type == "wire_bond":
                temp["height"] = ic_die_prop.GetHeightValue().ToString()
        self.ic_die_properties = temp

    def _retrieve_solder_ball_properties_from_edb(self):
        temp = dict()
        cp = self.pyedb_obj.component_property
        solder_ball_prop = cp.GetSolderBallProperty().Clone()
        _, diam, mid_diam = solder_ball_prop.GetDiameterValue()
        height = solder_ball_prop.GetHeightValue().ToString()
        shape = solder_ball_prop.GetShape().ToString()
        material = solder_ball_prop.GetMaterialName()
        uses_solder_ball = solder_ball_prop.UsesSolderball()

        temp["uses_solder_ball"] = uses_solder_ball
        temp["shape"] = pascal_to_snake(shape)
        temp["diameter"] = diam.ToString()
        temp["mid_diameter"] = mid_diam.ToString()
        temp["height"] = height
        temp["material"] = material
        self.solder_ball_properties = temp

    def _retrieve_port_properties_from_edb(self):
        temp = dict()
        cp = self.pyedb_obj.component_property
        c_type = self.type.lower()
        if c_type not in ["ic", "io", "other"]:
            return
        else:
            port_prop = cp.GetPortProperty().Clone()
            reference_height = port_prop.GetReferenceHeightValue().ToString()
            reference_size_auto = port_prop.GetReferenceSizeAuto()
            _, reference_size_x, reference_size_y = port_prop.GetReferenceSize()
            temp["reference_height"] = reference_height
            temp["reference_size_auto"] = reference_size_auto
            temp["reference_size_x"] = str(reference_size_x)
            temp["reference_size_y"] = str(reference_size_y)
            self.port_properties = temp

    def set_parameters_to_edb(self):
        if self.type:
            self.pyedb_obj.type = self.type
        if self.enabled is not None:
            self.pyedb_obj.enabled = self.enabled

        self._set_model_properties_to_edb()
        if self.pyedb_obj.type.lower() == "ic":
            self._set_ic_die_properties_to_edb()
            self._set_port_properties_to_edb()
            self._set_solder_ball_properties_to_edb()
        elif self.pyedb_obj.type.lower() in ["io", "other"]:
            self._set_solder_ball_properties_to_edb()
            self._set_port_properties_to_edb()

    def retrieve_parameters_from_edb(self):
        self.type = self.pyedb_obj.type
        self.definition = self.pyedb_obj.part_name
        self.reference_designator = self.pyedb_obj.name
        self.retrieve_model_properties_from_edb()
        if self.pyedb_obj.type.lower() == "ic":
            self._retrieve_ic_die_properties_from_edb()
            self._retrieve_port_properties_from_edb()
            self._retrieve_solder_ball_properties_from_edb()
        elif self.pyedb_obj.type.lower() in ["io", "other"]:
            self._retrieve_solder_ball_properties_from_edb()
            self._retrieve_port_properties_from_edb()

    def __init__(self, _pedb, pedb_object, **kwargs):
        self._pedb = _pedb
        self.pyedb_obj = pedb_object

        self.enabled = kwargs.get("enabled", None)
        self.reference_designator = kwargs.get("reference_designator", None)
        self.definition = kwargs.get("definition", None)
        self.type = kwargs["part_type"].lower() if kwargs.get("part_type") else None
        self.placement_layer = kwargs.get("placement_layer", None)
        self.pins = kwargs.get("pins", [])

        self.port_properties = kwargs.get("port_properties", {})
        self.solder_ball_properties = kwargs.get("solder_ball_properties", {})
        self.ic_die_properties = kwargs.get("ic_die_properties", {"type": "no_die"})
        self.pin_pair_model = kwargs.get("pin_pair_model", [])
        self.spice_model = kwargs.get("spice_model", {})
        self.s_parameter_model = kwargs.get("s_parameter_model", {})
        self.netlist_model = kwargs.get("netlist_model", {})


class CfgComponents:
    def __init__(self, pedb, components_data):
        self._pedb = pedb
        self.components = []

        if components_data:
            for comp in components_data:
                obj = self._pedb.components.instances[comp["reference_designator"]]
                self.components.append(CfgComponent(self._pedb, obj, **comp))

    def clean(self):
        self.components = []

    def apply(self):
        for comp in self.components:
            comp.set_parameters_to_edb()

    def retrieve_parameters_from_edb(self):
        self.clean()
        comps_in_db = self._pedb.components
        for _, comp in comps_in_db.instances.items():
            cfg_comp = CfgComponent(self._pedb, comp)
            cfg_comp.retrieve_parameters_from_edb()
            self.components.append(cfg_comp)
