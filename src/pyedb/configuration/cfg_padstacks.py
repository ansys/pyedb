# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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
from typing import Union

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
    name: str | None = None
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

    def __init__(
        self,
        name: str = None,
        net_name: str | None = None,
        definition: str | None = None,
        layer_range: list[str] | None = None,
        position: list[str | float] | None = None,
        rotation: str | float | None = None,
        is_pin: bool = False,
        hole_override_enabled: bool | None = None,
        hole_override_diameter: str | float | None = None,
        solder_ball_layer: str | None = None,
        eid: int | None = None,
        backdrill_parameters: CfgBackdrillParameters | None = None,
        **kwargs,
    ):
        super().__init__(
            name=name,
            net_name=net_name,
            definition=definition,
            layer_range=layer_range,
            position=position,
            rotation=str(rotation) if rotation is not None else None,
            is_pin=is_pin,
            hole_override_enabled=hole_override_enabled,
            hole_override_diameter=hole_override_diameter,
            solder_ball_layer=solder_ball_layer,
            eid=eid,
            backdrill_parameters=backdrill_parameters or CfgBackdrillParameters(),
            **kwargs,
        )

    @property
    def _id(self):
        return self.eid

    @classmethod
    def create(cls, **kwargs):
        obj = cls(**kwargs)
        obj.backdrill_parameters = CfgBackdrillParameters()
        return obj

    def set_backdrill(
        self,
        drill_to_layer: str,
        diameter: str,
        stub_length: str | None = None,
        drill_from_bottom: bool = True,
    ):
        """Configure backdrill parameters."""
        if self.backdrill_parameters is None:
            self.backdrill_parameters = CfgBackdrillParameters()
        self.backdrill_parameters.add_backdrill_to_layer(
            drill_to_layer=drill_to_layer,
            diameter=diameter,
            stub_length=stub_length,
            drill_from_bottom=drill_from_bottom,
        )
        return self

    def to_dict(self) -> dict:
        """Serialize the padstack instance."""
        return self.model_dump(exclude_none=True, by_alias=False)


class CfgPadstackDefinition(CfgBase):
    name: str

    hole_plating_thickness: str | float | None = None
    material: str | None = Field(None, alias="hole_material")
    hole_range: str | None = None

    pad_parameters: dict | None = None
    hole_parameters: dict | None = None
    solder_ball_parameters: dict | None = None

    def __init__(
        self,
        name: str,
        hole_plating_thickness: str | float | None = None,
        material: str | None = None,
        hole_range: str | None = None,
        pad_parameters: dict | None = None,
        hole_parameters: dict | None = None,
        solder_ball_parameters: dict | None = None,
        **kwargs,
    ):
        if material is not None and "hole_material" not in kwargs:
            kwargs["hole_material"] = material
        super().__init__(
            name=name,
            hole_plating_thickness=hole_plating_thickness,
            hole_range=hole_range,
            pad_parameters=pad_parameters,
            hole_parameters=hole_parameters,
            solder_ball_parameters=solder_ball_parameters,
            **kwargs,
        )

    @classmethod
    def create(cls, **kwargs):
        return cls(**kwargs)

    def to_dict(self) -> dict:
        """Serialize the padstack definition."""
        return self.model_dump(exclude_none=True)


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

    def add_definition(
        self,
        name,
        hole_plating_thickness=None,
        material=None,
        hole_range=None,
        pad_parameters=None,
        hole_parameters=None,
        solder_ball_parameters=None,
    ):
        """Add a padstack definition."""
        kwargs = {
            "name": name,
            "hole_plating_thickness": hole_plating_thickness,
            "hole_material": material,
            "hole_range": hole_range,
            "pad_parameters": pad_parameters,
            "hole_parameters": hole_parameters,
            "solder_ball_parameters": solder_ball_parameters,
        }
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        return self.add_padstack_definition(**kwargs)

    def add_padstack_instance(self, **kwargs):
        obj = CfgPadstackInstance(**kwargs)
        self.instances.append(obj)
        return obj

    def add_instance(self, **kwargs):
        """Add a padstack instance."""
        if kwargs.get("rotation") is not None:
            kwargs["rotation"] = str(kwargs["rotation"])
        return self.add_padstack_instance(**kwargs)

    def to_dict(self) -> dict:
        """Serialize all configured padstack definitions and instances."""
        data = {}
        if self.definitions:
            data["definitions"] = [d.to_dict() for d in self.definitions]
        if self.instances:
            data["instances"] = [i.to_dict() for i in self.instances]
        return data
