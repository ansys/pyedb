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
from typing import Union, Optional, List, Any, Dict

from pydantic import BaseModel, Field

from pyedb.dotnet.database.general import (
    convert_py_list_to_net_list,
    pascal_to_snake,
    snake_to_pascal,
)


class CfgBase(BaseModel):
    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
    }


class CfgBackdrillParameters(BaseModel):
    class DrillParametersByLayer(CfgBase):
        drill_to_layer: str
        diameter: str

    class DrillParametersByLayerWithStub(DrillParametersByLayer):
        stub_length: Union[str, None]

    class DrillParameters(CfgBase):
        drill_depth: str
        diameter: str

    from_top: Union[None, DrillParameters, DrillParametersByLayer, DrillParametersByLayerWithStub] = None
    from_bottom: Union[None, DrillParameters, DrillParametersByLayer, DrillParametersByLayerWithStub] = None

    def add_backdrill_to_layer(self, drill_to_layer, diameter, stub_length=None, drill_from_bottom=True):
        if stub_length is None:
            drill = self.DrillParametersByLayer(
                drill_to_layer=drill_to_layer,
                diameter=diameter)
        else:
            drill = self.DrillParametersByLayerWithStub(
                drill_to_layer=drill_to_layer,
                diameter=diameter,
                stub_length=stub_length)

        if drill_from_bottom:
            self.from_bottom = drill
        else:
            self.from_top = drill


class CfgPadstackInstance(CfgBase):
    name: str = None
    eid: Union[int, None] = Field(None, alias="id")
    backdrill_parameters: Union[CfgBackdrillParameters, None] = None
    is_pin: bool = Field(default=False)
    net_name: Optional[str] = None
    layer_range: Optional[List[str]] = None
    definition: Optional[str] = None
    position: Optional[List[Union[str, float]]] = None
    rotation: Optional[str] = None
    hole_override_enabled: Optional[bool] = None
    hole_override_diameter: Optional[Union[str, float]] = None
    solder_ball_layer: Optional[str] = None

    @property
    def _id(self):
        return self.eid

    @classmethod
    def create(cls, **kwargs):
        obj = cls(**kwargs)
        obj.backdrill_parameters = CfgBackdrillParameters()
        return obj


class CfgPadstackDefinition(CfgBase):
    name: str
    hole_plating_thickness: Optional[Union[str, float]] = None
    material: Optional[str] = Field(default=None, alias="hole_material")
    hole_range: Optional[str] = None
    pad_parameters: Optional[Dict] = None
    hole_parameters: Optional[Dict] = None
    solder_ball_parameters: Optional[Dict] = None

    @classmethod
    def create(cls, **kwargs):
        return cls(**kwargs)


class CfgPadstacks(CfgBase):
    definitions: Optional[List[CfgPadstackDefinition]] = []
    instances: Optional[List[CfgPadstackInstance]] = []

    @classmethod
    def create(cls, **kwargs):
        return cls(**kwargs)

    def clean(self):
        self.definitions = []
        self.instances = []

    def add_padstack_definition(self, **kwargs):
        obj = CfgPadstackDefinition(**kwargs)
        self.definitions.append(obj)
        return obj

    def add_padstack_instance(self, **kwargs):
        obj = CfgPadstackInstance(**kwargs)
        self.instances.append(obj)
        return obj
