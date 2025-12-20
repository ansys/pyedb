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
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field


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

    from_top: DrillParameters | DrillParametersByLayer | DrillParametersByLayerWithStub | None = None
    from_bottom: DrillParameters | DrillParametersByLayer | DrillParametersByLayerWithStub | None = None

    def add_backdrill_to_layer(self, drill_to_layer, diameter, stub_length=None, drill_from_bottom=True):
        if stub_length is None:
            drill = self.DrillParametersByLayer(drill_to_layer=drill_to_layer, diameter=diameter)
        else:
            drill = self.DrillParametersByLayerWithStub(
                drill_to_layer=drill_to_layer, diameter=diameter, stub_length=stub_length
            )

        if drill_from_bottom:
            self.from_bottom = drill
        else:
            self.from_top = drill


class CfgPadstackInstance(CfgBase):
    name: str = None
    eid: int | None = Field(None, alias="id")

    backdrill_parameters: CfgBackdrillParameters | None = CfgBackdrillParameters()
    is_pin: bool = Field(default=False)

    net_name: str | None = None
    layer_range: list[str] | None = None
    definition: str | None = None
    position: list[str | float] | None = None
    rotation: str | None = None

    hole_override_enabled: bool | None = None
    hole_override_diameter: str | float | None = None
    solder_ball_layer: str | None = None

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

    hole_plating_thickness: str | float | None = None
    material: str | None = Field(None, alias="hole_material")
    hole_range: str | None = None

    pad_parameters: dict | None = None
    hole_parameters: dict | None = None
    solder_ball_parameters: dict | None = None

    @classmethod
    def create(cls, **kwargs):
        return cls(**kwargs)


class CfgPadstacks(CfgBase):
    definitions: list[CfgPadstackDefinition] | None = []
    instances: list[CfgPadstackInstance] | None = []

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
