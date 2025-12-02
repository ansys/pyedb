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
import warnings

from pyedb.dotnet.database.geometry.polygon_data import PolygonData
from pyedb.dotnet.database.utilities.obj_base import ObjBase
from pyedb.dotnet.database.general import (
    convert_py_list_to_net_list,
    pascal_to_snake,
    snake_to_pascal,
)


class PackageDef(ObjBase):
    """Manages EDB functionalities for package definitions.

    Parameters
    ----------
    pedb : :class:`pyedb.edb`
        Edb object.
    edb_object : object
    Edb PackageDef Object
        component_part_name : str, optional
        Part name of the component.
    extent_bounding_box : list, optional
        Bounding box defines the shape of the package. For example, [[0, 0], ["2mm", "2mm"]].

    """

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

    def __init__(self, pedb, edb_object=None, name=None, component_part_name=None, extent_bounding_box=None):
        super().__init__(pedb, edb_object)

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

        if self._edb_object is None and name is not None:
            self._edb_object = self.__create_from_name(name, component_part_name, extent_bounding_box)
        else:
            self._edb_object = edb_object

    def __create_from_name(self, name, component_part_name=None, extent_bounding_box=None):
        """Create a package definition.

        Parameters
        ----------
        name: str
            Name of the package definition.

        Returns
        -------
        edb_object: object
            EDB PackageDef Object
        """
        edb_object = self._pedb.core.Definition.PackageDef.Create(self._pedb.active_db, name)
        if component_part_name:
            x_pt1, y_pt1, x_pt2, y_pt2 = list(
                self._pedb.components.definitions[component_part_name].components.values()
            )[0].bounding_box
            x_mid = (x_pt1 + x_pt2) / 2
            y_mid = (y_pt1 + y_pt2) / 2
            bbox = [[y_pt1 - y_mid, x_pt1 - x_mid], [y_pt2 - y_mid, x_pt2 - x_mid]]
        else:
            bbox = extent_bounding_box
        if bbox is None:
            self._pedb.logger.warning(
                "Package creation uses bounding box but it cannot be inferred. "
                "Please set argument 'component_part_name' or 'extent_bounding_box'."
            )
        polygon_data = PolygonData(self._pedb, create_from_bounding_box=True, points=bbox)

        edb_object.SetExteriorBoundary(polygon_data._edb_object)
        return edb_object

    def delete(self):
        """Delete a package definition object from the database."""
        return self._edb_object.Delete()

    @property
    def exterior_boundary(self):
        """Get the exterior boundary of a package definition."""
        return PolygonData(self._pedb, self._edb_object.GetExteriorBoundary()).points

    @exterior_boundary.setter
    def exterior_boundary(self, value):
        self._edb_object.SetExteriorBoundary(value._edb_object)

    @property
    def maximum_power(self):
        """Maximum power of the package."""
        return self._edb_object.GetMaximumPower().ToDouble()

    @maximum_power.setter
    def maximum_power(self, value):
        value = self._pedb.edb_value(value)
        self._edb_object.SetMaximumPower(value)

    @property
    def thermal_conductivity(self):
        """Adding this property for compatibility with grpc."""
        return self._edb_object.GetTherm_Cond().ToDouble()

    @thermal_conductivity.setter
    def thermal_conductivity(self, value):
        value = self._pedb.edb_value(value)
        self._edb_object.SetTherm_Cond(value)

    @property
    def therm_cond(self):
        """Thermal conductivity of the package.

        ..deprecated:: 0.48.0
           Use: func:`thermal_conductivity` property instead.
        """
        warnings.warn("Use property thermal_conductivity instead.", DeprecationWarning)
        return self.thermal_conductivity

    @therm_cond.setter
    def therm_cond(self, value):
        self.thermal_conductivity = value

    @property
    def theta_jb(self):
        """Theta Junction-to-Board of the package."""
        return self._edb_object.GetTheta_JB().ToDouble()

    @theta_jb.setter
    def theta_jb(self, value):
        value = self._pedb.edb_value(value)
        self._edb_object.SetTheta_JB(value)

    @property
    def theta_jc(self):
        """Theta Junction-to-Case of the package."""
        return self._edb_object.GetTheta_JC().ToDouble()

    @theta_jc.setter
    def theta_jc(self, value):
        value = self._pedb.edb_value(value)
        self._edb_object.SetTheta_JC(value)

    @property
    def height(self):
        """Height of the package."""
        return self._edb_object.GetHeight().ToDouble()

    @height.setter
    def height(self, value):
        value = self._pedb.edb_value(value)
        self._edb_object.SetHeight(value)

    def set_heatsink(self, fin_base_height, fin_height, fin_orientation, fin_spacing, fin_thickness):
        from pyedb.dotnet.database.utilities.heatsink import HeatSink

        heatsink = HeatSink(self._pedb)
        heatsink.fin_base_height = fin_base_height
        heatsink.fin_height = fin_height
        heatsink.fin_orientation = fin_orientation
        heatsink.fin_spacing = fin_spacing
        heatsink.fin_thickness = fin_thickness
        return self._edb_object.SetHeatSink(heatsink._edb_object)

    @property
    def heatsink(self):
        """Component heatsink.

        ..deprecated:: 0.48.0
           Use: func:`heat_sink` property instead.
        """
        return self.heat_sink

    @property
    def heat_sink(self):
        """Component heatsink."""
        from pyedb.dotnet.database.utilities.heatsink import HeatSink

        flag, edb_object = self._edb_object.GetHeatSink()
        if flag:
            return HeatSink(self._pedb, edb_object)
        else:
            return None

    def get_pad_parameters(self):
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
        from pyedb.dotnet.database.general import (
            pascal_to_snake,
        )

        pdef_data = self._edb_object._padstack_def_data
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

                for idx, i in enumerate(self.PAD_SHAPE_PARAMETERS[pad_shape]):
                    pad_params[i] = params[idx].ToString()
                temp_list.append(pad_params)
            data[pad_type_name] = temp_list
        return data

    def get_hole_parameters(self):
        pdef_data = self._edb_object._padstack_def_data
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

    def get_solder_parameters(self):
        pdef_data = self._edb_object._padstack_def_data
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