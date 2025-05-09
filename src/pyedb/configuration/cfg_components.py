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
from pyedb.dotnet.database.general import pascal_to_snake, snake_to_pascal


class CfgComponent(CfgBase):
    class Grpc:
        @property
        def pyedb_obj(self):
            return self.parent.pyedb_obj

        def __init__(self, parent):
            self.parent = parent
            self.pedb = parent.pedb

        def retrieve_model_properties_from_edb(self):
            from ansys.edb.core.hierarchy.netlist_model import (
                NetlistModel as GrpcNetlistModel,
            )
            from ansys.edb.core.hierarchy.pin_pair_model import (
                PinPairModel as GrpcPinPairModel,
            )
            from ansys.edb.core.hierarchy.sparameter_model import (
                SParameterModel as GrpcSParameterModel,
            )
            from ansys.edb.core.hierarchy.spice_model import (
                SPICEModel as GrpcSPICEModel,
            )

            c_p = self.pyedb_obj.component_property
            model = c_p.model
            if isinstance(model, GrpcNetlistModel):
                self.parent.netlist_model["netlist"] = model.netlist
            elif isinstance(model, GrpcPinPairModel):
                temp = {}
                for i in model.pin_pairs():
                    temp["first_pin"] = i[0]
                    temp["second_pin"] = i[1]
                    rlc = model.rlc(i)
                    temp["is_parallel"] = rlc.is_parallel
                    temp["resistance"] = rlc.r.value
                    temp["resistance_enabled"] = rlc.r_enabled
                    temp["inductance"] = rlc.l.value
                    temp["inductance_enabled"] = rlc.l_enabled
                    temp["capacitance"] = rlc.c.value
                    temp["capacitance_enabled"] = rlc.c_enabled
                    self.parent.pin_pair_model.append(temp)
            elif isinstance(model, GrpcSParameterModel):
                self.parent.s_parameter_model["reference_net"] = model.reference_net
                self.parent.s_parameter_model["model_name"] = model.component_model
            elif isinstance(model, GrpcSPICEModel):
                self.parent.spice_model["model_name"] = model.model_name
                self.parent.spice_model["model_path"] = model.model_path
                self.parent.spice_model["sub_circuit"] = model.sub_circuit
                # check bug #525 status
                self.parent.spice_model["terminal_pairs"] = [[i, j] for i, j in dict(model.terminals.items())]

        def _set_model_properties_to_edb(self):
            c_p = self.pyedb_obj.component_property
            if self.parent.netlist_model:
                m = self.pedb._edb.Cell.Hierarchy.SParameterModel()
                m.net_list = self.parent.netlist_model["netlist"]
                c_p.model = m
                self.component_property = c_p
            elif self.parent.pin_pair_model:
                from ansys.edb.core.hierarchy.pin_pair_model import (
                    PinPairModel as GrpcPinPairModel,
                )
                from ansys.edb.core.utility.rlc import Rlc as GrpcRlc
                from ansys.edb.core.utility.value import Value as GrpcValue

                m = GrpcPinPairModel.create()
                for i in self.parent.pin_pair_model:
                    p = (str(i["first_pin"]), str(i["second_pin"]))
                    rlc = GrpcRlc(
                        r_enabled=i["resistance_enabled"],
                        r=GrpcValue(i["resistance"]),
                        l_enabled=i["inductance_enabled"],
                        l=GrpcValue(i["inductance"]),
                        c_enabled=i["capacitance_enabled"],
                        c=GrpcValue(i["capacitance"]),
                        is_parallel=i["is_parallel"],
                    )
                    m.set_rlc(pin_pair=p, rlc=rlc)
                c_p.model = m
                from ansys.edb.core.hierarchy.pin_pair_model import (
                    PinPairModel as GrpcPinPairModel,
                )

                self.pyedb_obj.component_property = c_p
            elif self.parent.s_parameter_model:
                from ansys.edb.core.hierarchy.sparameter_model import (
                    SParameterModel as GrpcSParameterModel,
                )

                m = GrpcSParameterModel.create(
                    name=self.parent.s_parameter_model["model_name"],
                    ref_net=self.parent.s_parameter_model["reference_net"],
                )
                c_p.model = m
                self.component_property = c_p
            elif self.parent.spice_model:
                self.pyedb_obj.assign_spice_model(
                    self.parent.spice_model["model_path"],
                    self.parent.spice_model["model_name"],
                    self.parent.spice_model["sub_circuit"],
                    self.parent.spice_model["terminal_pairs"],
                )

        def _retrieve_ic_die_properties_from_edb(self):
            temp = dict()
            cp = self.pyedb_obj.component_property

            ic_die_prop = cp.die_property
            die_type = pascal_to_snake(ic_die_prop.die_type.name)
            temp["type"] = die_type
            if not die_type == "no_die":
                temp["orientation"] = ic_die_prop.die_orientation.name.lower()
                if die_type == "wire_bond":
                    temp["height"] = str(ic_die_prop.height.value)

            self.parent.ic_die_properties = temp

        def _set_ic_die_properties_to_edb(self):
            from ansys.edb.core.definition.die_property import (
                DieOrientation as GrpcDieOrientation,
            )
            from ansys.edb.core.definition.die_property import DieType as GrpcDieType
            from ansys.edb.core.utility.value import Value as GrpcValue

            cp = self.pyedb_obj.component_property
            ic_die_prop = cp.die_property
            die_type = self.parent.ic_die_properties.get("type")
            die_type = snake_to_pascal(die_type)
            if die_type == "wirebond":
                ic_die_prop.die_type = GrpcDieType.WIREBOND
            elif die_type == "flipchip":
                ic_die_prop.die_type = GrpcDieType.FLIPCHIP
            elif not die_type == "no_die":
                orientation = self.parent.ic_die_properties.get("orientation")
                if orientation == "chip_up":
                    ic_die_prop.die_orientation = GrpcDieOrientation.CHIP_UP
                else:
                    ic_die_prop.die_orientation = GrpcDieOrientation.CHIP_DOWN
                if die_type == "wire_bond":
                    height = self.parent.ic_die_properties.get("height")
                    if height:
                        ic_die_prop.height = GrpcValue(height)
            cp.die_property = ic_die_prop
            self.pyedb_obj.component_property = cp

        def _retrieve_solder_ball_properties_from_edb(self):
            temp = dict()
            cp = self.pyedb_obj.component_property
            solder_ball_prop = None
            try:
                solder_ball_prop = cp.solder_ball_property
                diam, mid_diam = solder_ball_prop.get_diameter()
                height = solder_ball_prop.height
                shape = solder_ball_prop.shape.name
                material = solder_ball_prop.material_name
                uses_solder_ball = solder_ball_prop.uses_solderball

                temp["uses_solder_ball"] = uses_solder_ball
                temp["shape"] = shape.lower()
                temp["diameter"] = str(diam)
                temp["mid_diameter"] = str(mid_diam)
                temp["height"] = str(height)
                temp["material"] = material

                self.parent.solder_ball_properties = temp
            except:
                if not solder_ball_prop:
                    self.pedb.logger.warning(
                        f"Failed retrieving solder balls property on component {self.pyedb_obj.name}"
                    )

        def _set_solder_ball_properties_to_edb(self):
            from ansys.edb.core.definition.solder_ball_property import (
                SolderballShape as GrpcSolderballShape,
            )
            from ansys.edb.core.utility.value import Value as GrpcValue

            cp = self.pyedb_obj.component_property
            solder_ball_prop = cp.solder_ball_property
            shape = self.parent.solder_ball_properties.get("shape")
            if shape == "cylinder":
                solder_ball_prop.shape = GrpcSolderballShape.SOLDERBALL_CYLINDER
                diameter = self.parent.solder_ball_properties["diameter"]
                solder_ball_prop.set_diameter(GrpcValue(diameter), GrpcValue(diameter))
            elif shape == "spheroid":
                solder_ball_prop.shape = GrpcSolderballShape.SOLDERBALL_SPHEROID
                diameter = self.parent.solder_ball_properties["diameter"]
                mid_diameter = self.parent.solder_ball_properties["mid_diameter"]
                solder_ball_prop.set_diameter(GrpcValue(diameter), GrpcValue(mid_diameter))
            else:
                raise ValueError("Solderball shape must be either cylinder or spheroid")

            solder_ball_prop.height = GrpcValue(self.parent.solder_ball_properties["height"])
            solder_ball_prop.material_name = self.parent.solder_ball_properties.get("material", "solder")
            cp.solder_ball_property = solder_ball_prop
            self.pyedb_obj.component_property = cp

        def _retrieve_port_properties_from_edb(self):
            temp = dict()
            cp = self.pyedb_obj.component_property
            c_type = self.parent.type.lower()
            if c_type not in ["ic", "io", "other"]:
                return
            else:
                try:
                    port_prop = cp.port_property
                    reference_height = port_prop.reference_height.value
                    reference_size_auto = port_prop.reference_size_auto
                    reference_size_x, reference_size_y = port_prop.get_reference_size()
                    temp["reference_height"] = reference_height
                    temp["reference_size_auto"] = reference_size_auto
                    temp["reference_size_x"] = reference_size_x.value
                    temp["reference_size_y"] = reference_size_y.value
                    self.parent.port_properties = temp
                except:
                    self.pedb.logger.warning(f"No port property found on component {self.pyedb_obj.name}")

        def _set_port_properties_to_edb(self):
            from ansys.edb.core.utility.value import Value as GrpcValue

            cp = self.pyedb_obj.component_property
            port_prop = cp.port_property
            height = self.parent.port_properties.get("reference_height")
            if height:
                port_prop.reference_height = GrpcValue(height)
            reference_size_auto = self.parent.port_properties.get("reference_size_auto")
            if reference_size_auto is not None:
                port_prop.reference_size_auto = reference_size_auto
            reference_size_x = self.parent.port_properties.get("reference_size_x", 0)
            reference_size_y = self.parent.port_properties.get("reference_size_y", 0)
            port_prop.set_reference_size(GrpcValue(reference_size_x), GrpcValue(reference_size_y))
            cp.port_property = port_prop
            self.pyedb_obj.component_property = cp

        def set_parameters_to_edb(self):
            if self.parent.type:
                self.pyedb_obj.type = self.parent.type
            if self.parent.enabled is not None:
                self.pyedb_obj.enabled = self.parent.enabled

            self._set_model_properties_to_edb()
            if self.pyedb_obj.type.lower() == "ic":
                self._set_ic_die_properties_to_edb()
                self._set_port_properties_to_edb()
                self._set_solder_ball_properties_to_edb()
            elif self.pyedb_obj.type.lower() in ["io", "other"]:
                self._set_solder_ball_properties_to_edb()
                self._set_port_properties_to_edb()

        def retrieve_parameters_from_edb(self):
            self.parent.type = self.pyedb_obj.type
            self.parent.definition = self.pyedb_obj.part_name
            self.parent.reference_designator = self.pyedb_obj.name
            self.retrieve_model_properties_from_edb()
            if self.pyedb_obj.type.lower() == "ic":
                self._retrieve_ic_die_properties_from_edb()
                self._retrieve_port_properties_from_edb()
                self._retrieve_solder_ball_properties_from_edb()
            elif self.pyedb_obj.type.lower() in ["io", "other"]:
                self._retrieve_solder_ball_properties_from_edb()
                self._retrieve_port_properties_from_edb()

    class DotNet(Grpc):
        def __init__(self, parent):
            super().__init__(parent)

        def retrieve_model_properties_from_edb(self):
            c_p = self.pyedb_obj.component_property
            model = c_p.GetModel().Clone()

            if model.GetModelType().ToString() == "NetlistModel":
                self.parent.netlist_model["netlist"] = model.GetNetlist()
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
                    self.parent.pin_pair_model.append(temp)
            elif model.GetModelType().ToString() == "SParameterModel":
                self.parent.s_parameter_model["reference_net"] = model.GetReferenceNet()
                self.parent.s_parameter_model["model_name"] = model.GetComponentModelName()
            elif model.GetModelType().ToString() == "SPICEModel":
                self.parent.spice_model["model_name"] = model.GetModelName()
                self.parent.spice_model["model_path"] = model.GetModelPath()
                self.parent.spice_model["sub_circuit"] = model.GetSubCkt()
                self.parent.spice_model["terminal_pairs"] = [
                    [i, j] for i, j in dict(model.GetTerminalPinPairs()).items()
                ]

        def _set_ic_die_properties_to_edb(self):
            cp = self.pyedb_obj.component_property
            ic_die_prop = cp.GetDieProperty().Clone()
            die_type = self.parent.ic_die_properties.get("type")
            ic_die_prop.SetType(getattr(self.pedb._edb.Definition.DieType, snake_to_pascal(die_type)))
            if not die_type == "no_die":
                orientation = self.parent.ic_die_properties.get("orientation")
                if orientation:
                    ic_die_prop.SetOrientation(
                        getattr(self.pedb._edb.Definition.DieOrientation, snake_to_pascal(orientation))
                    )
                if die_type == "wire_bond":
                    height = self.parent.ic_die_properties.get("height")
                    if height:
                        ic_die_prop.SetHeight(self.pedb.edb_value(height))
            cp.SetDieProperty(ic_die_prop)
            self.pyedb_obj.component_property = cp

        def _set_port_properties_to_edb(self):
            cp = self.pyedb_obj.component_property
            port_prop = cp.GetPortProperty().Clone()
            height = self.parent.port_properties.get("reference_height")
            if height:
                port_prop.SetReferenceHeight(self.pedb.edb_value(height))
            reference_size_auto = self.parent.port_properties.get("reference_size_auto")
            if reference_size_auto is not None:
                port_prop.SetReferenceSizeAuto(reference_size_auto)
            reference_size_x = self.parent.port_properties.get("reference_size_x", 0)
            reference_size_y = self.parent.port_properties.get("reference_size_y", 0)
            port_prop.SetReferenceSize(self.pedb.edb_value(reference_size_x), self.pedb.edb_value(reference_size_y))
            cp.SetPortProperty(port_prop)
            self.pyedb_obj.component_property = cp

        def _set_model_properties_to_edb(self):
            c_p = self.pyedb_obj.component_property
            if self.parent.netlist_model:
                m = self.pedb._edb.Cell.Hierarchy.SParameterModel()
                m.SetNetlist(self.parent.netlist_model["netlist"])
                c_p.SetModel(m)
                self.component_property = c_p
            elif self.parent.pin_pair_model:
                m = self.pedb._edb.Cell.Hierarchy.PinPairModel()
                for i in self.parent.pin_pair_model:
                    p = self.pedb._edb.Utility.PinPair(str(i["first_pin"]), str(i["second_pin"]))
                    rlc = self.pedb._edb.Utility.Rlc(
                        self.pedb.edb_value(i["resistance"]),
                        i["resistance_enabled"],
                        self.pedb.edb_value(i["inductance"]),
                        i["inductance_enabled"],
                        self.pedb.edb_value(i["capacitance"]),
                        i["capacitance_enabled"],
                        i["is_parallel"],
                    )
                    m.SetPinPairRlc(p, rlc)
                    c_p.SetModel(m)

                m = self.pedb._edb.Cell.Hierarchy.PinPairModel()
                for i in self.parent.pin_pair_model:
                    p = self.pedb._edb.Utility.PinPair(str(i["first_pin"]), str(i["second_pin"]))
                    rlc = self.pedb._edb.Utility.Rlc(
                        self.pedb.edb_value(i["resistance"]),
                        i["resistance_enabled"],
                        self.pedb.edb_value(i["inductance"]),
                        i["inductance_enabled"],
                        self.pedb.edb_value(i["capacitance"]),
                        i["capacitance_enabled"],
                        i["is_parallel"],
                    )
                    m.SetPinPairRlc(p, rlc)
                    c_p.SetModel(m)
                self.pyedb_obj.component_property = c_p
            elif self.parent.s_parameter_model:
                m = self.pedb._edb.Cell.Hierarchy.SParameterModel()
                m.SetComponentModelName(self.parent.s_parameter_model["model_name"])
                m.SetReferenceNet(self.parent.s_parameter_model["reference_net"])
                c_p.SetModel(m)
                self.component_property = c_p
            elif self.parent.spice_model:
                self.pyedb_obj.assign_spice_model(
                    self.parent.spice_model["model_path"],
                    self.parent.spice_model["model_name"],
                    self.parent.spice_model["sub_circuit"],
                    self.parent.spice_model["terminal_pairs"],
                )

        def _set_solder_ball_properties_to_edb(self):
            cp = self.pyedb_obj.component_property
            solder_ball_prop = cp.GetSolderBallProperty().Clone()
            shape = self.parent.solder_ball_properties.get("shape")
            if shape:
                solder_ball_prop.SetShape(getattr(self.pedb._edb.Definition.SolderballShape, snake_to_pascal(shape)))
            else:
                return

            if shape == "cylinder":
                diameter = self.parent.solder_ball_properties["diameter"]
                solder_ball_prop.SetDiameter(self.pedb.edb_value(diameter), self.pedb.edb_value(diameter))
            elif shape == "spheroid":
                diameter = self.parent.solder_ball_properties["diameter"]
                mid_diameter = self.parent.solder_ball_properties["mid_diameter"]
                solder_ball_prop.SetDiameter(self.pedb.edb_value(diameter), self.pedb.edb_value(mid_diameter))
            else:
                raise ValueError("Solderball shape must be either cylinder or spheroid")
            solder_ball_prop.SetHeight(self.pedb.edb_value(self.parent.solder_ball_properties["height"]))
            solder_ball_prop.SetMaterialName(self.parent.solder_ball_properties.get("material", "solder"))
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
            self.parent.ic_die_properties = temp

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
            self.parent.solder_ball_properties = temp

        def _retrieve_port_properties_from_edb(self):
            temp = dict()
            cp = self.pyedb_obj.component_property
            c_type = self.parent.type.lower()
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
                self.parent.port_properties = temp

    def __init__(self, pedb, pedb_object, **kwargs):
        self.pedb = pedb
        self.pyedb_obj = pedb_object
        if self.pedb.grpc:
            self.api = self.Grpc(self)
        else:
            self.api = self.DotNet(self)

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
        self.pedb = pedb
        self.components = []

        if components_data:
            for comp in components_data:
                obj = self.pedb.components.instances[comp["reference_designator"]]
                self.components.append(CfgComponent(self.pedb, obj, **comp))

    def clean(self):
        self.components = []

    def apply(self):
        for comp in self.components:
            comp.api.set_parameters_to_edb()

    def retrieve_parameters_from_edb(self):
        self.clean()
        comps_in_db = self.pedb.components
        for _, comp in comps_in_db.instances.items():
            cfg_comp = CfgComponent(self.pedb, comp)
            cfg_comp.api.retrieve_parameters_from_edb()
            self.components.append(cfg_comp)
