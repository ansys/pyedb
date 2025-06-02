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
import os

from pyedb.configuration.cfg_common import CfgBase
from pyedb.dotnet.database.general import (
    convert_py_list_to_net_list,
    pascal_to_snake,
    snake_to_pascal,
)


class CfgPadstacks:
    """Padstack data class."""

    def __init__(self, pedb, padstack_dict=None):
        self.pedb = pedb
        self.definitions = []
        self.instances = []

        if padstack_dict:
            padstack_defs_layout = self.pedb.padstacks.definitions
            for pdef in padstack_dict.get("definitions", []):
                obj = padstack_defs_layout[pdef["name"]]
                self.definitions.append(CfgPadstackDefinition(self.pedb, obj, **pdef))

            inst_from_layout = self.pedb.padstacks.instances_by_name
            for inst in padstack_dict.get("instances", []):
                obj = inst_from_layout[inst["name"]]
                self.instances.append(CfgPadstackInstance(self.pedb, obj, **inst))

    def clean(self):
        self.definitions = []
        self.instances = []

    def apply(self):
        """Apply padstack definition and instances on layout."""
        if self.definitions:
            for pdef in self.definitions:
                pdef.api.set_parameters_to_edb()
        if self.instances:
            for inst in self.instances:
                inst.api.set_parameters_to_edb()

    def retrieve_parameters_from_edb(self):
        self.clean()
        for name, obj in self.pedb.padstacks.definitions.items():
            if name.lower() == "symbol":
                continue
            pdef = CfgPadstackDefinition(self.pedb, obj)
            pdef.api.retrieve_parameters_from_edb()
            self.definitions.append(pdef)

        for obj in self.pedb.layout.padstack_instances:
            inst = CfgPadstackInstance(self.pedb, obj)
            inst.api.retrieve_parameters_from_edb()
            self.instances.append(inst)


class CfgPadstackDefinition(CfgBase):
    """Padstack definition data class."""

    class Common:
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

        @property
        def pyedb_obj(self):
            return self.parent.pyedb_obj

        class Grpc:
            def __init__(self, parent):
                self.parent = parent
                self._pedb = parent._pedb

            def get_solder_ball_definition(self):
                from ansys.edb.core.definition.solder_ball_property import (
                    SolderballPlacement as GrpcSolderballPlacement,
                )
                from ansys.edb.core.definition.solder_ball_property import (
                    SolderballShape as GrpcSolderballShape,
                )

                self.parent._solder_shape_type = {
                    "no_solder_ball": GrpcSolderballShape.NO_SOLDERBALL,
                    "cylinder": GrpcSolderballShape.SOLDERBALL_CYLINDER,
                    "spheroid": GrpcSolderballShape.SOLDERBALL_SPHEROID,
                }
                self.parent._solder_placement = {
                    "above_padstack": GrpcSolderballPlacement.ABOVE_PADSTACK,
                    "below_padstack": GrpcSolderballPlacement.BELOW_PADSTACK,
                }

            def set_hole_parameters_to_edb(self, params):
                from ansys.edb.core.definition.padstack_def_data import (
                    PadGeometryType as GrpcPadGeometryType,
                )
                from ansys.edb.core.utility.value import Value as GrpcValue

                pad_geometry_type = {
                    "circle": GrpcPadGeometryType.PADGEOMTYPE_CIRCLE,
                    "polygon": GrpcPadGeometryType.PADGEOMTYPE_POLYGON,
                    "rectangle": GrpcPadGeometryType.PADGEOMTYPE_RECTANGLE,
                    "oval": GrpcPadGeometryType.PADGEOMTYPE_OVAL,
                    "square": GrpcPadGeometryType.PADGEOMTYPE_SQUARE,
                    "no_geometry": GrpcPadGeometryType.PADGEOMTYPE_NO_GEOMETRY,
                }

                original_params = self.parent.parent.hole_parameters
                pdef_data = self.parent.pyedb_obj.data

                temp_param = []
                shape = params["shape"]
                for idx, i in enumerate(self.parent.PAD_SHAPE_PARAMETERS[shape]):
                    temp_param.append(params[i])

                pdef_data.set_hole_parameters(
                    offset_x=GrpcValue(params.get("offset_x", original_params.get("offset_x", 0))),
                    offset_y=GrpcValue(params.get("offset_y", original_params.get("offset_y", 0))),
                    rotation=GrpcValue(params.get("rotation", original_params.get("rotation", 0))),
                    type_geom=pad_geometry_type[shape],
                    sizes=[GrpcValue(i) for i in temp_param],
                )
                self.parent.pyedb_obj.data = pdef_data

            def set_solder_parameters_to_edb(self, parameters):
                from ansys.edb.core.utility.value import Value as GrpcValue

                pdef_data = self.parent.pyedb_obj.data

                shape = parameters.get("shape", "no_solder_ball")
                diameter = parameters.get("diameter", "0.4mm")
                mid_diameter = parameters.get("mid_diameter", diameter)
                placement = parameters.get("placement", "above_padstack")
                material = parameters.get("material", None)

                pdef_data.solder_ball_shape = self.parent._solder_shape_type[shape]
                if not shape == "no_solder_ball":
                    pdef_data.solder_ball_param = (GrpcValue(diameter), GrpcValue(mid_diameter))
                    pdef_data.solder_ball_placement = self.parent._solder_placement[placement]

                if material:
                    pdef_data.solder_ball_material = material
                self.parent.pyedb_obj.data = pdef_data

            def get_solder_parameters_from_edb(self):
                from ansys.edb.core.definition.solder_ball_property import (
                    SolderballPlacement as GrpcSolderballPlacement,
                )
                from ansys.edb.core.utility.value import Value as GrpcValue

                pdef_data = self.parent.pyedb_obj.data
                shape = pdef_data.solder_ball_shape
                diameter, mid_diameter = pdef_data.solder_ball_param
                try:
                    placement = pdef_data.solder_ball_placement.name.lower()
                except:
                    placement = GrpcSolderballPlacement.ABOVE_PADSTACK.name.lower()
                material = pdef_data.solder_ball_material.value

                parameters = {
                    "shape": [i for i, j in self.parent._solder_shape_type.items() if j == shape][0],
                    "diameter": str(GrpcValue(diameter)),
                    "mid_diameter": str(GrpcValue(mid_diameter)),
                    "placement": placement,
                    "material": material,
                }
                return parameters

            def get_pad_parameters_from_edb(self):
                """Pad parameters.

                Returns
                -------
                dict
                    params = {
                    'regular_pad': [
                        {'layer_name': '1_Top', 'shape': 'circle', 'offset_x': '0.1mm', 'offset_y': '0',
                        'rotation': '0', 'diameter': '0.5mm'}
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
                from ansys.edb.core.definition.padstack_def_data import (
                    PadType as GrpcPadType,
                )

                pdef_data = self.parent.pyedb_obj.data
                pad_type_list = [GrpcPadType.REGULAR_PAD, GrpcPadType.ANTI_PAD, GrpcPadType.THERMAL_PAD]
                data = {}
                for pad_type in pad_type_list:
                    pad_type_name = pad_type.name.lower()
                    temp_list = []
                    for lyr_name in pdef_data.layer_names:
                        try:
                            result = pdef_data.get_pad_parameters(lyr_name, pad_type)
                            if len(result) == 4:
                                # polygon based pad
                                pass
                            elif len(result) == 5:
                                pad_shape, params, offset_x, offset_y, rotation = result
                                pad_shape = pad_shape.name.lower().split("_")[-1]
                                pad_params = {
                                    "layer_name": lyr_name,
                                    "shape": pad_shape,
                                    "offset_x": str(offset_x),
                                    "offset_y": str(offset_y),
                                    "rotation": str(rotation),
                                }
                                for idx, i in enumerate(self.parent.PAD_SHAPE_PARAMETERS[pad_shape]):
                                    pad_params[i] = str(params[idx])
                                temp_list.append(pad_params)
                        except:
                            pass
                    data[pad_type_name] = temp_list
                return data

            def set_pad_parameters_to_edb(self, param):
                from ansys.edb.core.definition.padstack_def_data import (
                    PadGeometryType as GrpcPadGeometryType,
                )
                from ansys.edb.core.definition.padstack_def_data import (
                    PadType as GrpcPadType,
                )
                from ansys.edb.core.utility.value import Value as GrpcValue

                pdef_data = self.parent.pyedb_obj.data

                pad_type_list = [GrpcPadType.REGULAR_PAD, GrpcPadType.ANTI_PAD, GrpcPadType.THERMAL_PAD]
                for pad_type in pad_type_list:
                    pad_type_name = pad_type.name.lower()
                    rpp = param.get(pad_type_name, [])
                    for idx, layer_data in enumerate(rpp):
                        # Get geometry type from kwargs
                        p = layer_data.get("shape")
                        temp_param = []
                        pad_shape = None
                        # Handle Circle geometry type
                        if p == "circle":
                            temp_param.append(layer_data["diameter"])
                            pad_shape = GrpcPadGeometryType.PADGEOMTYPE_CIRCLE

                        # Handle Square geometry type
                        elif p == "square":
                            temp_param.append(layer_data["size"])
                            pad_shape = GrpcPadGeometryType.PADGEOMTYPE_SQUARE

                        elif p == "rectangle":
                            temp_param.append(layer_data["x_size"])
                            temp_param.append(layer_data["y_size"])
                            pad_shape = GrpcPadGeometryType.PADGEOMTYPE_RECTANGLE

                        # Handle Oval geometry type
                        elif p == "oval":
                            temp_param.append(layer_data["x_size"])
                            temp_param.append(layer_data["y_size"])
                            temp_param.append(layer_data["corner_radius"])
                            pad_shape = GrpcPadGeometryType.PADGEOMTYPE_OVAL

                        # Handle Bullet geometry type
                        elif p == "bullet":
                            temp_param.append(layer_data["x_size"])
                            temp_param.append(layer_data["y_size"])
                            temp_param.append(layer_data["corner_radius"])
                            pad_shape = GrpcPadGeometryType.PADGEOMTYPE_BULLET

                        # Handle Round45 geometry type
                        elif p == "round45":
                            temp_param.append(layer_data["inner"])
                            temp_param.append(layer_data["channel_width"])
                            temp_param.append(layer_data["isolation_gap"])
                            pad_shape = GrpcPadGeometryType.PADGEOMTYPE_ROUND45

                        # Handle Round90 geometry type
                        elif p == "round90":
                            temp_param.append(layer_data["inner"])
                            temp_param.append(layer_data["channel_width"])
                            temp_param.append(layer_data["isolation_gap"])
                            pad_shape = GrpcPadGeometryType.PADGEOMTYPE_ROUND90
                        elif p == "no_geometry":
                            continue

                        # Set pad parameters for the current layer
                        if pad_shape:
                            pdef_data.set_pad_parameters(
                                layer=layer_data["layer_name"],
                                pad_type=pad_type,
                                offset_x=GrpcValue(layer_data.get("offset_x", 0)),
                                offset_y=GrpcValue(layer_data.get("offset_y", 0)),
                                rotation=GrpcValue(layer_data.get("rotation", 0)),
                                type_geom=pad_shape,
                                sizes=[GrpcValue(i) for i in temp_param],
                            )
                self.parent.pyedb_obj.data = pdef_data

            def get_hole_parameters_from_edb(self):
                pdef_data = self.parent.pyedb_obj.data
                try:
                    hole_shape, params, offset_x, offset_y, rotation = pdef_data.get_hole_parameters()
                    hole_shape = hole_shape.name.lower().split("_")[-1]

                    hole_params = {"shape": hole_shape}
                    for idx, i in enumerate(self.parent.PAD_SHAPE_PARAMETERS[hole_shape]):
                        hole_params[i] = str(params[idx])
                    hole_params["offset_x"] = str(offset_x)
                    hole_params["offset_y"] = str(offset_y)
                    hole_params["rotation"] = str(rotation)
                    return hole_params
                except:
                    return None

        class DotNet(Grpc):
            def __init__(self, parent):
                super().__init__(parent)

            def get_solder_ball_definition(self):
                definition = self._pedb._edb.Definition
                self.parent._solder_shape_type = {
                    "no_solder_ball": definition.SolderballShape.NoSolderball,
                    "cylinder": definition.SolderballShape.Cylinder,
                    "spheroid": definition.SolderballShape.Spheroid,
                }
                self.parent._solder_placement = {
                    "above_padstack": definition.SolderballPlacement.AbovePadstack,
                    "below_padstack": definition.SolderballPlacement.BelowPadstack,
                }

            def set_hole_parameters_to_edb(self, params):
                original_params = self.parent.parent.hole_parameters
                pdef_data = self.parent.pyedb_obj._padstack_def_data

                temp_param = []
                shape = params["shape"]
                if shape == "no_geometry":
                    return  # .net api doesn't tell how to set no_geometry shape.
                for idx, i in enumerate(self.parent.PAD_SHAPE_PARAMETERS[shape]):
                    temp_param.append(params[i])
                    pedb_shape = getattr(self._pedb._edb.Definition.PadGeometryType, snake_to_pascal(shape))

                pdef_data.SetHoleParameters(
                    pedb_shape,
                    convert_py_list_to_net_list([self._pedb.edb_value(i) for i in temp_param]),
                    self._pedb.edb_value(params.get("offset_x", original_params.get("offset_x", 0))),
                    self._pedb.edb_value(params.get("offset_y", original_params.get("offset_y", 0))),
                    self._pedb.edb_value(params.get("rotation", original_params.get("rotation", 0))),
                )
                self.parent.pyedb_obj._padstack_def_data = pdef_data

            def set_solder_parameters_to_edb(self, parameters):
                pdef_data = self.parent.pyedb_obj._padstack_def_data

                shape = parameters.get("shape", "no_solder_ball")
                diameter = parameters.get("diameter", "0.4mm")
                mid_diameter = parameters.get("mid_diameter", diameter)
                placement = parameters.get("placement", "above_padstack")
                material = parameters.get("material", None)

                pdef_data.SetSolderBallShape(self.parent._solder_shape_type[shape])
                if not shape == "no_solder_ball":
                    pdef_data.SetSolderBallParameter(self._pedb.edb_value(diameter), self._pedb.edb_value(mid_diameter))
                    pdef_data.SetSolderBallPlacement(self.parent._solder_placement[placement])

                if material:
                    pdef_data.SetSolderBallMaterial(material)
                self.parent.pyedb_obj._padstack_def_data = pdef_data

            def get_solder_parameters_from_edb(self):
                pdef_data = self.parent.pyedb_obj._padstack_def_data
                shape = pdef_data.GetSolderBallShape()
                _, diameter, mid_diameter = pdef_data.GetSolderBallParameterValue()
                placement = pdef_data.GetSolderBallPlacement()
                material = pdef_data.GetSolderBallMaterial()

                parameters = {
                    "shape": [i for i, j in self.parent._solder_shape_type.items() if j == shape][0],
                    "diameter": self._pedb.edb_value(diameter).ToString(),
                    "mid_diameter": self._pedb.edb_value(mid_diameter).ToString(),
                    "placement": [i for i, j in self.parent._solder_placement.items() if j == placement][0],
                    "material": material,
                }
                return parameters

            def get_pad_parameters_from_edb(self):
                """Pad parameters.

                Returns
                -------
                dict
                    params = {
                    'regular_pad': [
                        {'layer_name': '1_Top', 'shape': 'circle', 'offset_x': '0.1mm', 'offset_y': '0',
                        'rotation': '0', 'diameter': '0.5mm'}
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
                pdef_data = self.parent.pyedb_obj._padstack_def_data
                pad_type_list = [
                    self._pedb._edb.Definition.PadType.RegularPad,
                    self._pedb._edb.Definition.PadType.AntiPad,
                    self._pedb._edb.Definition.PadType.ThermalPad,
                    # self._ppadstack._pedb._edb.Definition.PadType.Hole,
                    # This property doesn't appear in UI. It is unclear what it is used for.
                    # Suppressing this property for now.
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

                        for idx, i in enumerate(self.parent.PAD_SHAPE_PARAMETERS[pad_shape]):
                            pad_params[i] = params[idx].ToString()
                        temp_list.append(pad_params)
                    data[pad_type_name] = temp_list
                return data

            def set_pad_parameters_to_edb(self, param):
                pdef_data = self.parent.pyedb_obj._padstack_def_data

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
                self.parent.pyedb_obj._padstack_def_data = pdef_data

            def get_hole_parameters_from_edb(self):
                pdef_data = self.parent.pyedb_obj._padstack_def_data
                _, hole_shape, params, offset_x, offset_y, rotation = pdef_data.GetHoleParametersValue()
                hole_shape = pascal_to_snake(hole_shape.ToString())

                hole_params = {}
                hole_params["shape"] = hole_shape
                for idx, i in enumerate(self.parent.PAD_SHAPE_PARAMETERS[hole_shape]):
                    hole_params[i] = params[idx].ToString()
                hole_params["offset_x"] = offset_x.ToString()
                hole_params["offset_y"] = offset_y.ToString()
                hole_params["rotation"] = rotation.ToString()
                return hole_params

        def __init__(self, parent):
            self.parent = parent
            self._pedb = parent.pedb
            if self._pedb.grpc:
                self.api = self.Grpc(self)
            else:
                self.api = self.DotNet(self)

            self._solder_shape_type = None
            self._solder_placement = None
            self.api.get_solder_ball_definition()

        def set_parameters_to_edb(self):
            if self.parent.hole_parameters:
                self.api.set_hole_parameters_to_edb(self.parent.hole_parameters)
            if self.parent.hole_range:
                self.pyedb_obj.hole_range = self.parent.hole_range
            if self.parent.hole_plating_thickness:
                self.pyedb_obj.hole_plating_thickness = self.parent.hole_plating_thickness
            if self.parent.material:
                self.pyedb_obj.material = self.parent.material
            if self.parent.pad_parameters:
                self.api.set_pad_parameters_to_edb(self.parent.pad_parameters)
            if self.parent.solder_ball_parameters:
                self.api.set_solder_parameters_to_edb(self.parent.solder_ball_parameters)

        def retrieve_parameters_from_edb(self):
            self.parent.name = self.pyedb_obj.name
            self.parent.hole_plating_thickness = self.pyedb_obj.hole_plating_thickness
            self.parent.material = self.pyedb_obj.material
            self.parent.hole_range = self.pyedb_obj.hole_range
            self.parent.pad_parameters = self.api.get_pad_parameters_from_edb()
            self.parent.hole_parameters = self.api.get_hole_parameters_from_edb()
            self.parent.solder_ball_parameters = self.api.get_solder_parameters_from_edb()

    class Grpc(Common):
        def __init__(self, parent):
            super().__init__(parent)

    class DotNet(Grpc):
        def __init__(self, parent):
            super().__init__(parent)

    def __init__(self, pedb, pedb_object, **kwargs):
        self.pedb = pedb
        self.pyedb_obj = pedb_object
        if os.environ["PYEDB_USE_DOTNET"] == "0":
            self.api = self.Grpc(self)
        else:
            self.api = self.DotNet(self)

        self.name = kwargs.get("name", None)
        self.hole_plating_thickness = kwargs.get("hole_plating_thickness", None)
        self.material = kwargs.get("hole_material", None)
        self.hole_range = kwargs.get("hole_range", None)
        self.pad_parameters = kwargs.get("pad_parameters", None)
        self.hole_parameters = kwargs.get("hole_parameters", None)
        self.solder_ball_parameters = kwargs.get("solder_ball_parameters", None)


class CfgPadstackInstance(CfgBase):
    """Instance data class."""

    class Common:
        @property
        def pyedb_obj(self):
            return self.parent.pyedb_obj

        class Grpc:
            def __init__(self, parent):
                self.parent = parent
                self._pedb = parent._pedb

            def set_parameters_to_edb(self):
                from ansys.edb.core.utility.value import Value as GrpcValue

                if self.parent.parent.name is not None:
                    self.parent.pyedb_obj.aedt_name = self.parent.parent.name
                self.parent.pyedb_obj.is_pin = self.parent.parent.is_pin
                if self.parent.parent.net_name is not None:
                    self.parent.pyedb_obj.net_name = self._pedb.nets.find_or_create_net(
                        self.parent.parent.net_name
                    ).name
                if self.parent.parent.layer_range[0] is not None:
                    self.parent.pyedb_obj.start_layer = self.parent.parent.layer_range[0]
                if self.parent.parent.layer_range[1] is not None:
                    self.parent.pyedb_obj.stop_layer = self.parent.parent.layer_range[1]
                if self.parent.parent.backdrill_parameters:
                    self.parent.pyedb_obj.backdrill_parameters = self.parent.parent.backdrill_parameters
                if self.parent.parent.solder_ball_layer:
                    self.parent.pyedb_obj.solderball_layer = self._pedb.stackup.layers[
                        self.parent.parent.solder_ball_layer
                    ]

                hole_override_enabled, hole_override_diam = self.parent.pyedb_obj.get_hole_overrides()
                hole_override_enabled = (
                    self.parent.parent.hole_override_enabled
                    if self.parent.parent.hole_override_enabled
                    else hole_override_enabled
                )
                hole_override_diam = (
                    self.parent.parent.hole_override_diameter
                    if self.parent.parent.hole_override_diameter
                    else hole_override_diam
                )
                self.parent.pyedb_obj.set_hole_overrides(hole_override_enabled, GrpcValue(hole_override_diam))

            def retrieve_parameters_from_edb(self):
                self.parent.parent.name = self.parent.pyedb_obj.aedt_name
                self.parent.parent.is_pin = self.parent.pyedb_obj.is_pin
                self.parent.parent.definition = self.parent.pyedb_obj.padstack_definition
                backdrill_type = self.parent.pyedb_obj.get_backdrill_type()
                if backdrill_type == "no_drill":
                    self.parent.parent.backdrill_parameters = None
                elif backdrill_type == "layer_drill":
                    self.parent.parent.backdrill_parameters = self.parent.pyedb_obj.get_back_drill_by_layer()
                elif backdrill_type == "depth_drill":
                    self.parent.parent.backdrill_parameters = self.parent.pyedb_obj.get_back_drill_by_depth
                position_x, position_y, rotation = self.parent.pyedb_obj.get_position_and_rotation()
                self.parent.parent.position = [str(position_x), str(position_y)]
                self.parent.parent.rotation = str(rotation)
                self.parent.parent._id = self.parent.pyedb_obj.id
                (
                    self.parent.parent.hole_override_enabled,
                    hole_override_diameter,
                ) = self.parent.pyedb_obj.get_hole_overrides()
                self.parent.hole_override_diameter = str(hole_override_diameter)
                try:
                    self.parent.parent.solder_ball_layer = self.parent.pyedb_obj.solderball_layer.name
                except:
                    self.parent.parent.solder_ball_layer = ""
                self.parent.parent.layer_range = [self.parent.pyedb_obj.start_layer, self.parent.pyedb_obj.stop_layer]

        class DotNet(Grpc):
            def __init__(self, parent):
                super().__init__(parent)

            def set_parameters_to_edb(self):
                if self.parent.parent.name is not None:
                    self.parent.pyedb_obj.aedt_name = self.parent.parent.name
                self.parent.pyedb_obj.is_pin = self.parent.parent.is_pin
                if self.parent.parent.net_name is not None:
                    self.parent.pyedb_obj.net_name = self._pedb.nets.find_or_create_net(
                        self.parent.parent.net_name
                    ).name
                if self.parent.parent.layer_range[0] is not None:
                    self.parent.pyedb_obj.start_layer = self.parent.parent.layer_range[0]
                if self.parent.parent.layer_range[1] is not None:
                    self.parent.pyedb_obj.stop_layer = self.parent.parent.layer_range[1]
                if self.parent.parent.backdrill_parameters:
                    self.parent.pyedb_obj.backdrill_parameters = self.parent.parent.backdrill_parameters
                if self.parent.parent.solder_ball_layer:
                    self.parent.pyedb_obj._edb_object.SetSolderBallLayer(
                        self._pedb.stackup[self.parent.parent.solder_ball_layer]._edb_object
                    )

                hole_override_enabled, hole_override_diam = self.parent.pyedb_obj._edb_object.GetHoleOverrideValue()
                hole_override_enabled = (
                    self.parent.parent.hole_override_enabled
                    if self.parent.parent.hole_override_enabled
                    else hole_override_enabled
                )
                hole_override_diam = (
                    self.parent.parent.hole_override_diameter
                    if self.parent.parent.hole_override_diameter
                    else hole_override_diam
                )
                self.parent.pyedb_obj._edb_object.SetHoleOverride(
                    hole_override_enabled, self._pedb.edb_value(hole_override_diam)
                )

            def retrieve_parameters_from_edb(self):
                self.parent.parent.name = self.parent.pyedb_obj.aedt_name
                self.parent.parent.is_pin = self.parent.pyedb_obj.is_pin
                self.parent.parent.definition = self.parent.pyedb_obj.padstack_definition
                self.parent.parent.backdrill_parameters = self.parent.pyedb_obj.backdrill_parameters
                _, position, rotation = self.parent.pyedb_obj._edb_object.GetPositionAndRotationValue()
                self.parent.parent.position = [position.X.ToString(), position.Y.ToString()]
                self.parent.parent.rotation = rotation.ToString()
                self.parent.parent._id = self.parent.pyedb_obj.id
                (
                    self.parent.hole_override_enabled,
                    hole_override_diameter,
                ) = self.parent.pyedb_obj._edb_object.GetHoleOverrideValue()
                self.parent.parent.hole_override_diameter = hole_override_diameter.ToString()
                self.parent.parent.solder_ball_layer = self.parent.pyedb_obj._edb_object.GetSolderBallLayer().GetName()
                self.parent.parent.layer_range = [self.parent.pyedb_obj.start_layer, self.parent.pyedb_obj.stop_layer]

        def __init__(self, parent):
            self.parent = parent
            self._pedb = parent.pedb
            if self._pedb.grpc:
                self.api = self.Grpc(self)
            else:
                self.api = self.DotNet(self)

        def set_parameters_to_edb(self):
            self.api.set_parameters_to_edb()

        def retrieve_parameters_from_edb(self):
            self.api.retrieve_parameters_from_edb()

    class Grpc(Common):
        def __init__(self, parent):
            super().__init__(parent)

    class DotNet(Grpc):
        def __init__(self, parent):
            super().__init__(parent)

    def __init__(self, pedb, pyedb_obj, **kwargs):
        self.pedb = pedb
        self.pyedb_obj = pyedb_obj
        if self.pedb.grpc:
            self.api = self.Grpc(self)
        else:
            self.api = self.DotNet(self)

        self.name = kwargs.get("name", None)
        self.is_pin = kwargs.get("is_pin", False)
        self.net_name = kwargs.get("net_name", None)
        self.layer_range = kwargs.get("layer_range", [None, None])
        self.definition = kwargs.get("definition", None)
        self.backdrill_parameters = kwargs.get("backdrill_parameters", None)
        self._id = kwargs.get("id", None)
        self.position = kwargs.get("position", [])
        self.rotation = kwargs.get("rotation", None)
        self.hole_override_enabled = kwargs.get("hole_override_enabled", None)
        self.hole_override_diameter = kwargs.get("hole_override_diameter", None)
        self.solder_ball_layer = kwargs.get("solder_ball_layer", None)
