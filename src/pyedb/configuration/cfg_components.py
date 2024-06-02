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

from enum import Enum


class CfgRlcModel:
    def __init__(self):
        self.resistance = 0.0
        self.inductance = 0.0
        self.capacitance = 0.0
        self.rlc_model_type = self.RlcModelType.SERIES
        self.enabled = False
        self.pin_pairs = []

    class RlcModelType(Enum):
        SERIES = 0
        PARALLEL = 1


class CfgPortProperties:
    def __init__(self):
        self.ref_offset = 0.0
        self.ref_size_auto = True
        self.ref_size_x = 0.0
        self.ref_size_y = 0.0


class CfgSolderBallsProperties:
    def __init__(self):
        self.shape = self.Shape.CYLINDER
        self.diameter = 0.0
        self.mid_diameter = 0.0
        self.height = 0.0
        self.enable = True

    class Shape(Enum):
        CYLINDER = 0
        SPHEROID = 1


class CfgComponent:
    def __init__(self, pdata, **kwargs):
        self._pedb = pdata._pedb
        self._comp_dict = kwargs
        self.reference_designator = ""
        self.part_type = self.ComponentType.RESISTOR
        self.enabled = True
        self.rlc_model = CfgRlcModel()
        self.port_properties = CfgPortProperties()
        self.solder_balls = CfgSolderBallsProperties()
        self._update()
        self.layout_comp = None

    class ComponentType(Enum):
        RESISTOR = 0
        INDUCTOR = 1
        CAPACITOR = 2
        IO = 3
        IC = 4
        OTHER = 5

    def _update(self):
        self.reference_designator = self._comp_dict.get("reference_designator")
        self.enabled = self._comp_dict.get("enabled")
        part_type = self._comp_dict["part_type"].lower()
        if part_type == "resistor":
            self.part_type = self.part_type.RESISTOR
        elif part_type == "capacitor":
            self.part_type = self.part_type.CAPACITOR
        elif part_type == "inductor":
            self.part_type = self.part_type.INDUCTOR
        elif part_type == "io":
            self.part_type = self.part_type.IO
        elif part_type == "ic":
            self.part_type = self.part_type.IC
        else:
            self.part_type = self.part_type.OTHER

        if self.part_type.value in [0, 1, 2]:
            rlc_model = self._comp_dict["rlc_model"] if "rlc_model" in self._comp_dict else None
            if rlc_model:
                pin_pairs = rlc_model["pin_pairs"] if "pin_pairs" in rlc_model else None
                if pin_pairs:
                    self.rlc_model.pin_pairs = []
                    for pp in pin_pairs:
                        if pp["type"] == "Parallel":
                            self.rlc_model.rlc_model_type = self.rlc_model.rlc_model_type.PARALLEL

                        self.rlc_model.pin_pairs.append([pp["p1"], pp["p2"]])
                        self.rlc_model.resistance = pp["resistance"] if "resistance" in pp else None
                        self.rlc_model.inductance = pp["inductance"] if "inductance" in pp else None
                        self.rlc_model.capacitance = pp["capacitance"] if "capacitance" in pp else None

        port_properties = self._comp_dict["port_properties"] if "port_properties" in self._comp_dict else None
        if port_properties:
            self.port_properties.ref_offset = float(port_properties["reference_offset"])
            self.port_properties.ref_size_auto = bool(port_properties["reference_size_auto"])
            self.port_properties.ref_size_x = float(port_properties["reference_size_x"])
            self.port_properties.ref_size_y = float(port_properties["reference_size_y"])

        solder_ball_properties = (
            self._comp_dict["solder_ball_properties"] if "solder_ball_properties" in self._comp_dict else None
        )
        if solder_ball_properties:
            if solder_ball_properties["shape"].lower() == "spheroid":
                self.solder_balls.shape = self.solder_balls.shape.SPHEROID
            self.solder_balls.diameter = solder_ball_properties["diameter"]
            self.solder_balls.mid_diameter = (
                float(solder_ball_properties["mid_diameter"])
                if "mid_diameter" in solder_ball_properties
                else self.solder_balls.diameter
            )
            self.solder_balls.height = solder_ball_properties["height"]

    def apply(self):
        """Apply component on layout."""
        self.layout_comp = self._pedb.components[self.reference_designator]
        if self.layout_comp:
            self._apply_part_type()
            if self.part_type.name in ["CAPACITOR", "RESISTOR", "INDUCTOR"]:
                self._apply_rlc_model()
            else:
                self._apply_solder_balls()

    def _apply_part_type(self):
        if self.part_type.name == "CAPACITOR":
            self.layout_comp.type = "Capacitor"
        elif self.part_type.name == "RESISTOR":
            self.layout_comp.type = "Resistor"
        elif self.part_type.name == "INDUCTOR":
            self.layout_comp.type = "Inductor"
        elif self.part_type.name == "IC":
            self.layout_comp.type = "IC"
        elif self.part_type.name == "IO":
            self.layout_comp.type = "IO"
        elif self.part_type.name == "OTHER":
            self.layout_comp.type = "Other"

    def _apply_rlc_model(self):
        if self.part_type.value in [0, 1, 2]:
            self.layout_comp.is_enabled = self.enabled
            if self.rlc_model:
                model_layout = self.layout_comp.model
                if self.rlc_model.pin_pairs:
                    for pp in model_layout.pin_pairs:
                        model_layout.delete_pin_pair_rlc(pp)
                    for pp in self.rlc_model.pin_pairs:
                        pin_pair = self._pedb.edb_api.utility.PinPair(pp[0], pp[1])
                        rlc = self._pedb.edb_api.utility.Rlc()
                        rlc.IsParallel = False if self.rlc_model.rlc_model_type.SERIES else True
                        if not self.rlc_model.resistance is None:
                            rlc.REnabled = True
                            rlc.R = self._pedb.edb_value(self.rlc_model.resistance)
                        else:
                            rlc.REnabled = False
                        if not self.rlc_model.inductance is None:
                            rlc.LEnabled = True
                            rlc.L = self._pedb.edb_value(self.rlc_model.inductance)
                        else:
                            rlc.LEnabled = False

                        if not self.rlc_model.capacitance is None:
                            rlc.CEnabled = True
                            rlc.C = self._pedb.edb_value(self.rlc_model.capacitance)
                        else:
                            rlc.CEnabled = False
                        model_layout._set_pin_pair_rlc(pin_pair, rlc)
                        self.layout_comp.model = model_layout

    def _apply_solder_balls(self):
        if self.solder_balls.enable:
            shape = "Cylinder"
            if self.solder_balls.shape == self.solder_balls.shape.SPHEROID:
                shape = "Spheroid"
            self._pedb.components.set_solder_ball(
                component=self.reference_designator,
                sball_diam=self.solder_balls.diameter,
                sball_mid_diam=self.solder_balls.mid_diameter,
                sball_height=self.solder_balls.height,
                shape=shape,
                auto_reference_size=self.port_properties.ref_size_auto,
                reference_height=self.port_properties.ref_offset,
                reference_size_x=self.port_properties.ref_size_x,
                reference_size_y=self.port_properties.ref_size_y,
            )
