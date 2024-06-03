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


from pyedb.generic.general_methods import pyedb_function_handler


class CfgBase:
    attr_names = []
    attr2class = {}

    def __init__(self, **kwargs):
        self.data = kwargs
        self.set_attributes()

    def set_attributes(self):
        for k, v in self.data.items():
            if k in self.attr_names:
                self.__setattr__(k, v)
            if k in self.attr2class:
                self.__setattr__(k, self.attr2class[k](**v))


class CfgMaterial(CfgBase):
    attr_names = [
        "name",
        "permittivity",
        "conductivity"
        "dielectric_loss_tangent",
        "magnetic_loss_tangent",
        "mass_density",
        "permeability",
        "poisson_ratio",
        "specific_heat",
        "thermal_conductivity"
    ]


class CfgLayer(CfgBase):
    attr_names = [
        "name",
        "type",
        "material",
        "fill_material",
        "thickness",
    ]


class CfgPortProperties(CfgBase):
    attr_names = [
        "ref_offset",
        "ref_size_auto",
        "ref_size_x",
        "ref_size_y"
    ]


class CfgSolderBallsProperties(CfgBase):
    attr_names = [
        "shape",
        "diameter",
        "mid_diameter",
        "height",
        "enabled"
    ]


class CfgComponent(CfgBase):
    attr_names = [
        "enabled",
        "reference_designator",
        "part_type",
    ]
    attr2class = {
        "port_properties": CfgPortProperties,
        "solder_ball_properties": CfgSolderBallsProperties,

    }


class CfgRlcModel:
    attr_names = [
        "resistance",
        "inductance",
        "capacitance",
        "type"
    ]

    def __init__(self):
        self.resistance = 0.0
        self.inductance = 0.0
        self.capacitance = 0.0
        self.rlc_model_type = self.RlcModelType.SERIES
        self.enabled = False
        self.pin_pairs = []