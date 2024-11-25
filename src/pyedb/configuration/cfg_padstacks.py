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
from pyedb.dotnet.edb_core.general import (
    convert_py_list_to_net_list,
    pascal_to_snake,
    snake_to_pascal,
)


class CfgPadstacks:
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

    def clean(self):
        self.definitions = []
        self.instances = []

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


class CfgPadstackDefinition(CfgBase):
    """Padstack definition data class."""

    PAD_SHAPE_PARAMETERS = {
        "circle": ["diameter"],
        "square": ["size"],
        "rectangle": ["x_size", "y_size"],
        "oval": ["x_size", "y_size", "corner_radius"],
        "bullet": ["x_size", "y_size", "corner_radius"],
        "round45": ["inner", "channel_width", "isolation_gap"],
        "round90": ["inner", "channel_width", "isolation_gap"],
        "no_geometry": [],
    }

    def __init__(self, pedb, pedb_object, **kwargs):
        self._pedb = pedb
        self._pyedb_obj = pedb_object
        self.name = kwargs.get("name", None)
        self.hole_plating_thickness = kwargs.get("hole_plating_thickness", None)
        self.material = kwargs.get("hole_material", None)
        self.hole_range = kwargs.get("hole_range", None)
        self.pad_parameters = kwargs.get("pad_parameters", None)
        self.hole_parameters = kwargs.get("hole_parameters", None)
        self.solder_ball_parameters = kwargs.get("solder_ball_parameters", None)

        self._solder_shape_type = {
            "no_solder_ball": self._pedb._edb.Definition.SolderballShape.NoSolderball,
            "cylinder": self._pedb._edb.Definition.SolderballShape.Cylinder,
            "spheroid": self._pedb._edb.Definition.SolderballShape.Spheroid,
        }
        self._solder_placement = {
            "above_padstack": self._pedb._edb.Definition.SolderballPlacement.AbovePadstack,
            "below_padstack": self._pedb._edb.Definition.SolderballPlacement.BelowPadstack,
        }

    def set_parameters_to_edb(self):
        if self.hole_parameters:
            self._set_hole_parameters_to_edb(self.hole_parameters)
        if self.hole_range:
            self._pyedb_obj.hole_range = self.hole_range
        if self.hole_plating_thickness:
            self._pyedb_obj.hole_plating_thickness = self.hole_plating_thickness
        if self.material:
            self._pyedb_obj.material = self.material
        if self.pad_parameters:
            self._set_pad_parameters_to_edb(self.pad_parameters)
        if self.solder_ball_parameters:
            self._set_solder_parameters_to_edb(self.solder_ball_parameters)

    def _set_solder_parameters_to_edb(self, parameters):
        pdef_data = self._pyedb_obj._padstack_def_data

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
        self._pyedb_obj._padstack_def_data = pdef_data

    def _get_solder_parameters_from_edb(self):
        pdef_data = self._pyedb_obj._padstack_def_data
        shape = pdef_data.GetSolderBallShape()
        _, diameter, mid_diameter = pdef_data.GetSolderBallParameterValue()
        placement = pdef_data.GetSolderBallPlacement()
        material = pdef_data.GetSolderBallMaterial()

        parameters = {
            "shape": [i for i, j in self._solder_shape_type.items() if j == shape][0],
            "diameter": self._pedb.edb_value(diameter).ToString(),
            "mid_diameter": self._pedb.edb_value(mid_diameter).ToString(),
            "placement": [i for i, j in self._solder_placement.items() if j == placement][0],
            "material": material,
        }
        return parameters

    def retrieve_parameters_from_edb(self):
        self.name = self._pyedb_obj.name
        self.hole_plating_thickness = self._pyedb_obj.hole_plating_thickness
        self.material = self._pyedb_obj.material
        self.hole_range = self._pyedb_obj.hole_range
        self.pad_parameters = self._get_pad_parameters_from_edb()
        self.hole_parameters = self._get_hole_parameters_from_edb()
        self.solder_ball_parameters = self._get_solder_parameters_from_edb()

    def _get_pad_parameters_from_edb(self):
        """Pad parameters.

        Returns
        -------
        dict
            params = {
            'regular_pad': [
                {'layer_name': '1_Top', 'shape': 'circle', 'offset_x': '0.1mm', 'offset_y': '0', 'rotation': '0',
                 'diameter': '0.5mm'}
            ],
            'anti_pad': [
                {'layer_name': '1_Top', 'shape': 'circle', 'offset_x': '0', 'offset_y': '0', 'rotation': '0',
                'diameter': '1mm'}
            ],
            'thermal_pad': [
                {'layer_name': '1_Top', 'shape': 'round90', 'offset_x': '0', 'offset_y': '0', 'rotation': '0',
                'inner': '1mm', 'channel_width': '0.2mm', 'isolation_gap': '0.3mm'},
            ],
            'hole': [
                {'layer_name': '1_Top', 'shape': 'circle', 'offset_x': '0', 'offset_y': '0', 'rotation': '0',
                 'diameter': '0.1499997mm'},
            ]
        }
        """
        pdef_data = self._pyedb_obj._padstack_def_data
        pad_type_list = [
            self._pedb._edb.Definition.PadType.RegularPad,
            self._pedb._edb.Definition.PadType.AntiPad,
            self._pedb._edb.Definition.PadType.ThermalPad,
            # self._ppadstack._pedb._edb.Definition.PadType.Hole,
            # This property doesn't appear in UI. It is unclear what it is used for. Suppressing this property for now.
        ]
        data = {}
        for pad_type in pad_type_list:
            pad_type_name = pascal_to_snake(pad_type.ToString())
            temp_list = []
            for lyr_name in list(pdef_data.GetLayerNames()):
                result = pdef_data.GetPadParametersValue(lyr_name, pad_type)
                _, pad_shape, params, offset_x, offset_y, rotation = result
                pad_shape = pascal_to_snake(pad_shape.ToString())

                pad_params = {}
                pad_params["layer_name"] = lyr_name
                pad_params["shape"] = pad_shape
                pad_params["offset_x"] = offset_x.ToString()
                pad_params["offset_y"] = offset_y.ToString()
                pad_params["rotation"] = rotation.ToString()

                for idx, i in enumerate(self.PAD_SHAPE_PARAMETERS[pad_shape]):
                    pad_params[i] = params[idx].ToString()
                temp_list.append(pad_params)
            data[pad_type_name] = temp_list
        return data

    def _set_pad_parameters_to_edb(self, param):
        pdef_data = self._pyedb_obj._padstack_def_data

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
        self._pyedb_obj._padstack_def_data = pdef_data

    def _get_hole_parameters_from_edb(self):
        pdef_data = self._pyedb_obj._padstack_def_data
        _, hole_shape, params, offset_x, offset_y, rotation = pdef_data.GetHoleParametersValue()
        hole_shape = pascal_to_snake(hole_shape.ToString())

        hole_params = {}
        hole_params["shape"] = hole_shape
        for idx, i in enumerate(self.PAD_SHAPE_PARAMETERS[hole_shape]):
            hole_params[i] = params[idx].ToString()
        hole_params["offset_x"] = offset_x.ToString()
        hole_params["offset_y"] = offset_y.ToString()
        hole_params["rotation"] = rotation.ToString()
        return hole_params

    def _set_hole_parameters_to_edb(self, params):
        original_params = self.hole_parameters
        pdef_data = self._pyedb_obj._padstack_def_data

        temp_param = []
        shape = params["shape"]
        if shape == "no_geometry":
            return  # .net api doesn't tell how to set no_geometry shape.
        for idx, i in enumerate(self.PAD_SHAPE_PARAMETERS[shape]):
            temp_param.append(params[i])
            pedb_shape = getattr(self._pedb._edb.Definition.PadGeometryType, snake_to_pascal(shape))

        pdef_data.SetHoleParameters(
            pedb_shape,
            convert_py_list_to_net_list([self._pedb.edb_value(i) for i in temp_param]),
            self._pedb.edb_value(params.get("offset_x", original_params.get("offset_x", 0))),
            self._pedb.edb_value(params.get("offset_y", original_params.get("offset_y", 0))),
            self._pedb.edb_value(params.get("rotation", original_params.get("rotation", 0))),
        )
        self._pyedb_obj._padstack_def_data = pdef_data


class CfgPadstackInstance(CfgBase):
    """Instance data class."""

    def __init__(self, pedb, pyedb_obj, **kwargs):
        self._pedb = pedb
        self._pyedb_obj = pyedb_obj
        self.name = kwargs.get("name", None)
        self.net_name = kwargs.get("net_name", "")
        self.layer_range = kwargs.get("layer_range", [None, None])
        self.definition = kwargs.get("definition", None)
        self.backdrill_parameters = kwargs.get("backdrill_parameters", None)
        self._id = kwargs.get("id", None)
        self.position = kwargs.get("position", [])
        self.rotation = kwargs.get("rotation", None)
        self.hole_override_enabled = kwargs.get("hole_override_enabled", None)
        self.hole_override_diameter = kwargs.get("hole_override_diameter", None)
        self.solder_ball_layer = kwargs.get("solder_ball_layer", None)

    def set_parameters_to_edb(self):
        if self.name is not None:
            self._pyedb_obj.aedt_name = self.name
        if self.net_name is not None:
            self._pyedb_obj.net_name = self._pedb.nets.find_or_create_net(self.net_name).name
        if self.layer_range[0] is not None:
            self._pyedb_obj.start_layer = self.layer_range[0]
        if self.layer_range[1] is not None:
            self._pyedb_obj.stop_layer = self.layer_range[1]
        if self.backdrill_parameters:
            self._pyedb_obj.backdrill_parameters = self.backdrill_parameters
        if self.solder_ball_layer:
            self._pyedb_obj._edb_object.SetSolderBallLayer(self._pedb.stackup[self.solder_ball_layer]._edb_object)

        hole_override_enabled, hole_override_diam = self._pyedb_obj._edb_object.GetHoleOverrideValue()
        hole_override_enabled = self.hole_override_enabled if self.hole_override_enabled else hole_override_enabled
        hole_override_diam = self.hole_override_diameter if self.hole_override_diameter else hole_override_diam
        self._pyedb_obj._edb_object.SetHoleOverride(hole_override_enabled, self._pedb.edb_value(hole_override_diam))

    def retrieve_parameters_from_edb(self):
        self.name = self._pyedb_obj.aedt_name
        self.definition = self._pyedb_obj.padstack_definition
        self.backdrill_parameters = self._pyedb_obj.backdrill_parameters
        _, position, rotation = self._pyedb_obj._edb_object.GetPositionAndRotationValue()
        self.position = [position.X.ToString(), position.Y.ToString()]
        self.rotation = rotation.ToString()
        self._id = self._pyedb_obj.id
        self.hole_override_enabled, hole_override_diameter = self._pyedb_obj._edb_object.GetHoleOverrideValue()
        self.hole_override_diameter = hole_override_diameter.ToString()
        self.solder_ball_layer = self._pyedb_obj._edb_object.GetSolderBallLayer().GetName()
        self.layer_range = [self._pyedb_obj.start_layer, self._pyedb_obj.stop_layer]
