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


class _CfgPadstacks:
    """Padstack data class."""

    def __init__(self, pedb, padstack_dict=None):
        self._pedb = pedb
        self.definitions = []
        self.instances = []

        if padstack_dict:
            padstack_defs_layout = self._pedb.padstacks.definitions
            for pdef in padstack_dict.get("definitions", []):
                obj = padstack_defs_layout[pdef["name"]]
                self.definitions.append(CfgPadstackDefinition(self._pedb, obj, **pdef))

            inst_from_layout = self._pedb.padstacks.instances_by_name
            for inst in padstack_dict.get("instances", []):
                obj = inst_from_layout[inst["name"]]
                self.instances.append(CfgPadstackInstance(self._pedb, obj, **inst))

    def apply(self):
        """Apply padstack definition and instances on layout."""
        if self.definitions:
            for pdef in self.definitions:
                pdef.set_parameters_to_edb()
        if self.instances:
            for inst in self.instances:
                inst.set_parameters_to_edb()

    def retrieve_parameters_from_edb(self):
        self.clean()
        for name, obj in self._pedb.padstacks.definitions.items():
            if name.lower() == "symbol":
                continue
            pdef = CfgPadstackDefinition(self._pedb, obj)
            pdef.retrieve_parameters_from_edb()
            self.definitions.append(pdef)

        for obj in self._pedb.layout.padstack_instances:
            inst = CfgPadstackInstance(self._pedb, obj)
            inst.retrieve_parameters_from_edb()
            self.instances.append(inst)


class _CfgPadstackDefinition:
    """Padstack definition data class."""

    def get_solder_ball_definition(self):
        definition = self._pedb._edb.Definition
        self._solder_shape_type = {
            "no_solder_ball": definition.SolderballShape.NoSolderball,
            "cylinder": definition.SolderballShape.Cylinder,
            "spheroid": definition.SolderballShape.Spheroid,
        }
        self._solder_placement = {
            "above_padstack": definition.SolderballPlacement.AbovePadstack,
            "below_padstack": definition.SolderballPlacement.BelowPadstack,
        }

    def set_hole_parameters_to_edb(self, params):
        original_params = self.hole_parameters
        pdef_data = self.pyedb_obj._padstack_def_data

        temp_param = []
        shape = params["shape"]
        if shape == "no_geometry":
            return  # .net api doesn't tell how to set no_geometry shape.
        for i in self.PAD_SHAPE_PARAMETERS[shape]:
            temp_param.append(params[i])
            pedb_shape = getattr(self._pedb._edb.Definition.PadGeometryType, snake_to_pascal(shape))

        pdef_data.SetHoleParameters(
            pedb_shape,
            convert_py_list_to_net_list([self._pedb.edb_value(i) for i in temp_param]),
            self._pedb.edb_value(params.get("offset_x", original_params.get("offset_x", 0))),
            self._pedb.edb_value(params.get("offset_y", original_params.get("offset_y", 0))),
            self._pedb.edb_value(params.get("rotation", original_params.get("rotation", 0))),
        )
        self.pyedb_obj._padstack_def_data = pdef_data

    def set_solder_parameters_to_edb(self, parameters):
        pdef_data = self.pyedb_obj._padstack_def_data

        shape = parameters.get("shape", "no_solder_ball")
        diameter = parameters.get("diameter", "0.4mm")
        mid_diameter = parameters.get("mid_diameter", diameter)
        placement = parameters.get("placement", "above_padstack")
        material = parameters.get("material", None)

        pdef_data.SetSolderBallShape(self._solder_shape_type[shape])
        if not shape == "no_solder_ball":
            pdef_data.SetSolderBallParameter(self._pedb.edb_value(diameter), self._pedb.edb_value(mid_diameter))
            pdef_data.SetSolderBallPlacement(self._solder_placement[placement])

        if material:
            pdef_data.SetSolderBallMaterial(material)
        self.pyedb_obj._padstack_def_data = pdef_data


    def set_pad_parameters_to_edb(self, param):
        pdef_data = self.pyedb_obj._padstack_def_data

        pad_type_list = [
            self._pedb._edb.Definition.PadType.RegularPad,
            self._pedb._edb.Definition.PadType.AntiPad,
            self._pedb._edb.Definition.PadType.ThermalPad,
            self._pedb._edb.Definition.PadType.Hole,
        ]
        for pad_type in pad_type_list:
            pad_type_name = pascal_to_snake(pad_type.ToString())
            rpp = param.get(pad_type_name, [])
            for idx, layer_data in enumerate(rpp):
                # Get geometry type from kwargs
                p = layer_data.get("shape")
                temp_param = []

                # Handle Circle geometry type
                if p == pascal_to_snake(self._pedb._edb.Definition.PadGeometryType.Circle.ToString()):
                    temp_param.append(layer_data["diameter"])
                    pad_shape = self._pedb._edb.Definition.PadGeometryType.Circle

                # Handle Square geometry type
                elif p == pascal_to_snake(self._pedb._edb.Definition.PadGeometryType.Square.ToString()):
                    temp_param.append(layer_data["size"])
                    pad_shape = self._pedb._edb.Definition.PadGeometryType.Square

                elif p == pascal_to_snake(self._pedb._edb.Definition.PadGeometryType.Rectangle.ToString()):
                    temp_param.append(layer_data["x_size"])
                    temp_param.append(layer_data["y_size"])
                    pad_shape = self._pedb._edb.Definition.PadGeometryType.Rectangle

                # Handle Oval geometry type
                elif p == pascal_to_snake(self._pedb._edb.Definition.PadGeometryType.Oval.ToString()):
                    temp_param.append(layer_data["x_size"])
                    temp_param.append(layer_data["y_size"])
                    temp_param.append(layer_data["corner_radius"])
                    pad_shape = self._pedb._edb.Definition.PadGeometryType.Oval

                # Handle Bullet geometry type
                elif p == pascal_to_snake(self._pedb._edb.Definition.PadGeometryType.Bullet.ToString()):
                    temp_param.append(layer_data["x_size"])
                    temp_param.append(layer_data["y_size"])
                    temp_param.append(layer_data["corner_radius"])
                    pad_shape = self._pedb._edb.Definition.PadGeometryType.Bullet

                # Handle Round45 geometry type
                elif p == pascal_to_snake(self._pedb._edb.Definition.PadGeometryType.Round45.ToString()):
                    temp_param.append(layer_data["inner"])
                    temp_param.append(layer_data["channel_width"])
                    temp_param.append(layer_data["isolation_gap"])
                    pad_shape = self._pedb._edb.Definition.PadGeometryType.Round45

                # Handle Round90 geometry type
                elif p == pascal_to_snake(self._pedb._edb.Definition.PadGeometryType.Round90.ToString()):
                    temp_param.append(layer_data["inner"])
                    temp_param.append(layer_data["channel_width"])
                    temp_param.append(layer_data["isolation_gap"])
                    pad_shape = self._pedb._edb.Definition.PadGeometryType.Round90
                elif p == pascal_to_snake(self._pedb._edb.Definition.PadGeometryType.NoGeometry.ToString()):
                    continue

                # Set pad parameters for the current layer
                pdef_data.SetPadParameters(
                    layer_data["layer_name"],
                    pad_type,
                    pad_shape,
                    convert_py_list_to_net_list([self._pedb.edb_value(i) for i in temp_param]),
                    self._pedb.edb_value(layer_data.get("offset_x", 0)),
                    self._pedb.edb_value(layer_data.get("offset_y", 0)),
                    self._pedb.edb_value(layer_data.get("rotation", 0)),
                )
        self.pyedb_obj._padstack_def_data = pdef_data


    def set_parameters_to_edb(self):
        if self.hole_parameters:
            self.set_hole_parameters_to_edb(self.hole_parameters)
        if self.hole_range:
            self.pyedb_obj.hole_range = self.hole_range
        if self.hole_plating_thickness:
            self.pyedb_obj.hole_plating_thickness = self.hole_plating_thickness
        if self.material:
            self.pyedb_obj.material = self.material
        if self.pad_parameters:
            self.set_pad_parameters_to_edb(self.pad_parameters)
        if self.solder_ball_parameters:
            self.set_solder_parameters_to_edb(self.solder_ball_parameters)

    def __init__(self, pedb, pedb_object, **kwargs):
        self._pedb = pedb
        self.pyedb_obj = pedb_object

        self.name = kwargs.get("name", None)
        self.hole_plating_thickness = kwargs.get("hole_plating_thickness", None)
        self.material = kwargs.get("hole_material", None)
        self.hole_range = kwargs.get("hole_range", None)
        self.pad_parameters = kwargs.get("pad_parameters", None)
        self.hole_parameters = kwargs.get("hole_parameters", None)
        self.solder_ball_parameters = kwargs.get("solder_ball_parameters", None)

        self._solder_shape_type = None
        self._solder_placement = None
        self.get_solder_ball_definition()


class _CfgPadstackInstance(CfgBase):
    """Instance data class."""

    def set_parameters_to_edb(self):
        if self.name is not None:
            self.pyedb_obj.aedt_name = self.name
        self.pyedb_obj.is_pin = self.is_pin
        if self.net_name is not None:
            self.pyedb_obj.net_name = self._pedb.nets.find_or_create_net(self.net_name).name
        if self.layer_range[0] is not None:
            self.pyedb_obj.start_layer = self.layer_range[0]
        if self.layer_range[1] is not None:
            self.pyedb_obj.stop_layer = self.layer_range[1]
        if self.backdrill_parameters:
            self.pyedb_obj.backdrill_parameters = self.backdrill_parameters
        if self.solder_ball_layer:
            self.pyedb_obj._edb_object.SetSolderBallLayer(self._pedb.stackup[self.solder_ball_layer]._edb_object)

        hole_override_enabled, hole_override_diam = self.pyedb_obj._edb_object.GetHoleOverrideValue()
        hole_override_enabled = self.hole_override_enabled if self.hole_override_enabled else hole_override_enabled
        hole_override_diam = self.hole_override_diameter if self.hole_override_diameter else hole_override_diam
        self.pyedb_obj._edb_object.SetHoleOverride(hole_override_enabled, self._pedb.edb_value(hole_override_diam))

    def retrieve_parameters_from_edb(self):
        self.name = self.pyedb_obj.aedt_name
        self.is_pin = self.pyedb_obj.is_pin
        self.definition = self.pyedb_obj.padstack_definition
        self.backdrill_parameters = self.pyedb_obj.backdrill_parameters
        _, position, rotation = self.pyedb_obj._edb_object.GetPositionAndRotationValue()
        self.position = [position.X.ToString(), position.Y.ToString()]
        self.rotation = rotation.ToString()
        self._id = self.pyedb_obj.id
        (
            self.hole_override_enabled,
            hole_override_diameter,
        ) = self.pyedb_obj._edb_object.GetHoleOverrideValue()
        self.hole_override_diameter = hole_override_diameter.ToString()
        self.solder_ball_layer = self.pyedb_obj._edb_object.GetSolderBallLayer().GetName()
        self.layer_range = [self.pyedb_obj.start_layer, self.pyedb_obj.stop_layer]

    def __init__(self, pedb, pyedb_obj, **kwargs):
        self._pedb = pedb
        self.pyedb_obj = pyedb_obj


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
    _id: Union[int, None] = Field(None, alias="id")
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

    @classmethod
    def create(cls, **kwargs):
        obj = cls(**kwargs)
        obj.backdrill_parameters = CfgBackdrillParameters()
        return obj


class CfgPadstackDefinition(CfgBase):
    name: str
    hole_plating_thickness: Optional[float] = None
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