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

from collections import OrderedDict
import math
import re
import warnings

from pyedb.dotnet.clr_module import String
from pyedb.dotnet.database.cell.primitive.primitive import Connectable
from pyedb.dotnet.database.dotnet.database import PolygonDataDotNet
from pyedb.dotnet.database.edb_data.edbvalue import EdbValue
from pyedb.dotnet.database.general import (
    PadGeometryTpe,
    convert_py_list_to_net_list,
    pascal_to_snake,
    snake_to_pascal,
)
from pyedb.dotnet.database.geometry.polygon_data import PolygonData
from pyedb.generic.data_handlers import float_units
from pyedb.generic.general_methods import generate_unique_name
from pyedb.modeler.geometry_operators import GeometryOperators


class EDBPadProperties(object):
    """Manages EDB functionalities for pad properties.

    Parameters
    ----------
    edb_padstack :

    layer_name : str
        Name of the layer.
    pad_type :
        Type of the pad.
    pedbpadstack : str
        Inherited AEDT object.

    Examples
    --------
    >>> from pyedb import Edb
    >>> edb = Edb(myedb, edbversion="2021.2")
    >>> edb_pad_properties = edb.padstacks.definitions["MyPad"].pad_by_layer["TOP"]
    """

    def __init__(self, edb_padstack, layer_name, pad_type, p_edb_padstack):
        self._edb_object = edb_padstack
        self._pedbpadstack = p_edb_padstack
        self.layer_name = layer_name
        self.pad_type = pad_type

        self._edb_padstack = self._edb_object

    @property
    def _padstack_methods(self):
        return self._pedbpadstack._padstack_methods

    @property
    def _stackup_layers(self):
        return self._pedbpadstack._stackup_layers

    @property
    def _edb(self):
        return self._pedbpadstack._edb

    def _get_edb_value(self, value):
        return self._pedbpadstack._get_edb_value(value)

    @property
    def _pad_parameter_value(self):
        pad_params = self._edb_padstack.GetData().GetPadParametersValue(
            self.layer_name, self.int_to_pad_type(self.pad_type)
        )
        return pad_params

    @property
    def geometry_type(self):
        """Geometry type.

        Returns
        -------
        int
            Type of the geometry.
        """

        padparams = self._edb_padstack.GetData().GetPadParametersValue(
            self.layer_name, self.int_to_pad_type(self.pad_type)
        )
        return int(padparams[1])

    @geometry_type.setter
    def geometry_type(self, geom_type):
        """0, NoGeometry. 1, Circle. 2 Square. 3, Rectangle. 4, Oval. 5, Bullet. 6, N-sided polygon. 7, Polygonal
        shape.8, Round gap with 45 degree thermal ties. 9, Round gap with 90 degree thermal ties.10, Square gap
        with 45 degree thermal ties. 11, Square gap with 90 degree thermal ties.
        """
        val = self._get_edb_value(0)
        params = []
        if geom_type == 0:
            pass
        elif geom_type == 1:
            params = [val]
        elif geom_type == 2:
            params = [val]
        elif geom_type == 3:
            params = [val, val]
        elif geom_type == 4:
            params = [val, val, val]
        elif geom_type == 5:
            params = [val, val, val]
        self._update_pad_parameters_parameters(geom_type=geom_type, params=params)

    @property
    def shape(self):
        """Get the shape of the pad."""
        return self._pad_parameter_value[1].ToString()

    @shape.setter
    def shape(self, value):
        self._update_pad_parameters_parameters(geom_type=PadGeometryTpe[value].value)

    @property
    def parameters_values(self):
        """Parameters.

        Returns
        -------
        list
            List of parameters.
        """
        return [i.tofloat for i in self.parameters.values()]

    @property
    def parameters_values_string(self):
        """Parameters value in string format."""
        return [i.tostring for i in self.parameters.values()]

    @property
    def polygon_data(self):
        """Parameters.

        Returns
        -------
        list
            List of parameters.
        """

        flag, edb_object, _, _, _ = self._edb_padstack.GetData().GetPolygonalPadParameters(
            self.layer_name, self.int_to_pad_type(self.pad_type)
        )
        if flag:
            return PolygonData(self._pedbpadstack._ppadstack._pedb, edb_object)
        else:  # pragma no cover
            raise AttributeError("No polygon data.")

    @property
    def _polygon_data_dotnet(self):
        """Parameters.

        Returns
        -------
        list
            List of parameters.
        """
        pad_values = self._edb_padstack.GetData().GetPolygonalPadParameters(
            self.layer_name, self.int_to_pad_type(self.pad_type)
        )
        if pad_values[1]:
            return PolygonDataDotNet(self._pedbpadstack._ppadstack._pedb, pad_values[1])
        else:
            return

    @property
    def parameters(self):
        """Get parameters.

        Returns
        -------
        dict
        """
        value = list(self._pad_parameter_value[2])
        if self.shape == PadGeometryTpe.Circle.name:
            return OrderedDict({"Diameter": EdbValue(value[0])})
        elif self.shape == PadGeometryTpe.Square.name:
            return OrderedDict({"Size": EdbValue(value[0])})
        elif self.shape == PadGeometryTpe.Rectangle.name:
            return OrderedDict({"XSize": EdbValue(value[0]), "YSize": EdbValue(value[1])})
        elif self.shape in [PadGeometryTpe.Oval.name, PadGeometryTpe.Bullet.name]:
            return OrderedDict(
                {"XSize": EdbValue(value[0]), "YSize": EdbValue(value[1]), "CornerRadius": EdbValue(value[2])}
            )
        elif self.shape == PadGeometryTpe.NSidedPolygon.name:
            return OrderedDict({"Size": EdbValue(value[0]), "NumSides": EdbValue(value[1])})
        elif self.shape in [PadGeometryTpe.Round45.name, PadGeometryTpe.Round90.name]:  # pragma: no cover
            return OrderedDict(
                {"Inner": EdbValue(value[0]), "ChannelWidth": EdbValue(value[1]), "IsolationGap": EdbValue(value[2])}
            )
        else:
            return OrderedDict()  # pragma: no cover

    @parameters.setter
    def parameters(self, value):
        """Set parameters.
        "Circle", {"Diameter": "0.5mm"}

        Parameters
        ----------
        value : dict
            Pad parameters in dictionary.
        >>> pad = Edb.padstacks["PlanarEMVia"]["TOP"]
        >>> pad.shape = "Circle"
        >>> pad.pad_parameters{"Diameter": "0.5mm"}
        >>> pad.shape = "Bullet"
        >>> pad.pad_parameters{"XSize": "0.5mm", "YSize": "0.5mm"}
        """

        if isinstance(value, dict):
            value = {k: v.tostring if isinstance(v, EdbValue) else v for k, v in value.items()}
            if self.shape == PadGeometryTpe.Circle.name:
                params = [self._get_edb_value(value["Diameter"])]
            elif self.shape == PadGeometryTpe.Square.name:
                params = [self._get_edb_value(value["Size"])]
            elif self.shape == PadGeometryTpe.Rectangle.name:
                params = [self._get_edb_value(value["XSize"]), self._get_edb_value(value["YSize"])]
            elif self.shape == [PadGeometryTpe.Oval.name, PadGeometryTpe.Bullet.name]:
                params = [
                    self._get_edb_value(value["XSize"]),
                    self._get_edb_value(value["YSize"]),
                    self._get_edb_value(value["CornerRadius"]),
                ]
            elif self.shape in [PadGeometryTpe.Round45.name, PadGeometryTpe.Round90.name]:  # pragma: no cover
                params = [
                    self._get_edb_value(value["Inner"]),
                    self._get_edb_value(value["ChannelWidth"]),
                    self._get_edb_value(value["IsolationGap"]),
                ]
            else:  # pragma: no cover
                params = None
        elif isinstance(value, list):
            params = [self._get_edb_value(i) for i in value]
        else:
            params = [self._get_edb_value(value)]
        self._update_pad_parameters_parameters(params=params)

    @property
    def offset_x(self):
        """Offset for the X axis.

        Returns
        -------
        str
            Offset for the X axis.
        """

        pad_values = self._edb_padstack.GetData().GetPadParametersValue(
            self.layer_name, self.int_to_pad_type(self.pad_type)
        )
        return pad_values[3].ToString()

    @offset_x.setter
    def offset_x(self, offset_value):
        self._update_pad_parameters_parameters(offsetx=offset_value)

    @property
    def offset_y(self):
        """Offset for the Y axis.

        Returns
        -------
        str
            Offset for the Y axis.
        """

        pad_values = self._edb_padstack.GetData().GetPadParametersValue(
            self.layer_name, self.int_to_pad_type(self.pad_type)
        )
        return pad_values[4].ToString()

    @offset_y.setter
    def offset_y(self, offset_value):
        self._update_pad_parameters_parameters(offsety=offset_value)

    @property
    def rotation(self):
        """Rotation.

        Returns
        -------
        str
            Value for the rotation.
        """

        pad_values = self._edb_padstack.GetData().GetPadParametersValue(
            self.layer_name, self.int_to_pad_type(self.pad_type)
        )
        return pad_values[5].ToString()

    @rotation.setter
    def rotation(self, rotation_value):
        self._update_pad_parameters_parameters(rotation=rotation_value)

    def int_to_pad_type(self, val=0):
        """Convert an integer to an EDB.PadGeometryType.

        Parameters
        ----------
        val : int

        Returns
        -------
        object
            EDB.PadType enumerator value.
        """
        return self._pedbpadstack._ppadstack.int_to_pad_type(val)

    def int_to_geometry_type(self, val=0):
        """Convert an integer to an EDB.PadGeometryType.

        Parameters
        ----------
        val : int

        Returns
        -------
        object
            EDB.PadGeometryType enumerator value.
        """
        return self._pedbpadstack._ppadstack.int_to_geometry_type(val)

    def _update_pad_parameters_parameters(
        self,
        layer_name=None,
        pad_type=None,
        geom_type=None,
        params=None,
        offsetx=None,
        offsety=None,
        rotation=None,
    ):
        """Update padstack parameters.

        Parameters
        ----------
        layer_name : str, optional
            Name of the layer. The default is ``None``.
        pad_type : int, optional
            Type of the pad. The default is ``None``.
        geom_type : int, optional
            Type of the geometry. The default is ``None``.
        params : list, optional
            The default is ``None``.
        offsetx : float, optional
            Offset value for the X axis. The default is ``None``.
        offsety :  float, optional
            Offset value for the Y axis. The default is ``None``.
        rotation : float, optional
            Rotation value. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        originalPadstackDefinitionData = self._edb_padstack.GetData()
        newPadstackDefinitionData = self._edb.Definition.PadstackDefData(originalPadstackDefinitionData)
        if not pad_type:
            pad_type = self.pad_type
        if not geom_type:
            geom_type = self.geometry_type
        if params:
            params = convert_py_list_to_net_list(params)
        else:
            params = self._pad_parameter_value[2]
        if not offsetx:
            offsetx = self.offset_x
        if not offsety:
            offsety = self.offset_y
        if not rotation:
            rotation = self.rotation
        if not layer_name:
            layer_name = self.layer_name

        newPadstackDefinitionData.SetPadParameters(
            layer_name,
            self.int_to_pad_type(pad_type),
            self.int_to_geometry_type(geom_type),
            params,
            self._get_edb_value(offsetx),
            self._get_edb_value(offsety),
            self._get_edb_value(rotation),
        )
        self._edb_padstack.SetData(newPadstackDefinitionData)


class EDBPadstack(object):
    """Manages EDB functionalities for a padstack.

    Parameters
    ----------
    edb_padstack :

    ppadstack : str
        Inherited AEDT object.

    Examples
    --------
    >>> from pyedb import Edb
    >>> edb = Edb(myedb, edbversion="2021.2")
    >>> edb_padstack = edb.padstacks.definitions["MyPad"]
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

    def __init__(self, edb_padstack, ppadstack):
        self._edb_object = edb_padstack
        self.edb_padstack = edb_padstack
        self._ppadstack = ppadstack
        self._bounding_box = []
        self._hole_params = None

        definition = self._ppadstack._pedb._edb.Definition
        self._solder_shape_type = {
            "no_solder_ball": definition.SolderballShape.NoSolderball,
            "cylinder": definition.SolderballShape.Cylinder,
            "spheroid": definition.SolderballShape.Spheroid,
        }
        self._solder_placement = {
            "above_padstack": definition.SolderballPlacement.AbovePadstack,
            "below_padstack": definition.SolderballPlacement.BelowPadstack,
        }

    @property
    def pad_by_layer(self):
        """Regular pad property."""
        temp = {}
        for layer in self.via_layers:
            temp[layer] = EDBPadProperties(self._edb_object, layer, 0, self)
        return temp

    @property
    def antipad_by_layer(self):
        """Anti pad property."""
        temp = {}
        for layer in self.via_layers:
            temp[layer] = EDBPadProperties(self._edb_object, layer, 1, self)
        return temp

    @property
    def thermalpad_by_layer(self):
        """Thermal pad property."""
        temp = {}
        for layer in self.via_layers:
            temp[layer] = EDBPadProperties(self._edb_object, layer, 2, self)
        return temp

    @property
    def _padstack_def_data(self):
        """Get padstack definition data.

        Returns
        -------

        """
        pstack_data = self._edb_object.GetData()
        return self._edb.Definition.PadstackDefData(pstack_data)

    @_padstack_def_data.setter
    def _padstack_def_data(self, value):
        self._edb_object.SetData(value)

    @property
    def instances(self):
        """Definitions Instances."""
        name = self.name
        return [i for i in self._ppadstack.instances.values() if i.padstack_definition == name]

    @property
    def name(self):
        """Padstack Definition Name."""
        return self.edb_padstack.GetName()

    @property
    def _padstack_methods(self):
        return self._ppadstack._padstack_methods

    @property
    def _stackup_layers(self):
        return self._ppadstack._stackup_layers

    @property
    def _edb(self):
        return self._ppadstack._edb

    def _get_edb_value(self, value):
        return self._ppadstack._get_edb_value(value)

    @property
    def via_layers(self):
        """Layers.

        Returns
        -------
        list
            List of layers.
        """
        return list(self._padstack_def_data.GetLayerNames())

    @property
    def via_start_layer(self):
        """Starting layer.

        Returns
        -------
        str
            Name of the starting layer.
        """
        return self.via_layers[0]

    @property
    def via_stop_layer(self):
        """Stopping layer.

        Returns
        -------
        str
            Name of the stopping layer.
        """
        return self.via_layers[-1]

    @property
    def hole_params(self):
        """Via Hole parameters values."""

        viaData = self.edb_padstack.GetData()
        self._hole_params = viaData.GetHoleParametersValue()
        return self._hole_params

    @property
    def _hole_parameters(self):
        """Hole parameters.

        Returns
        -------
        list
            List of the hole parameters.
        """
        return self.hole_params[2]

    @property
    def hole_diameter(self):
        """Hole diameter."""
        return list(self.hole_params[2])[0].ToDouble()

    @hole_diameter.setter
    def hole_diameter(self, value):
        params = convert_py_list_to_net_list([self._get_edb_value(value)])
        self._update_hole_parameters(params=params)

    @property
    def hole_diameter_string(self):
        """Hole diameter in string format."""
        return list(self.hole_params[2])[0].ToString()

    def _update_hole_parameters(self, hole_type=None, params=None, offsetx=None, offsety=None, rotation=None):
        """Update hole parameters.

        Parameters
        ----------
        hole_type : optional
            Type of the hole. The default is ``None``.
        params : optional
            The default is ``None``.
        offsetx : float, optional
            Offset value for the X axis. The default is ``None``.
        offsety :  float, optional
            Offset value for the Y axis. The default is ``None``.
        rotation : float, optional
            Rotation value in degrees. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        originalPadstackDefinitionData = self.edb_padstack.GetData()
        newPadstackDefinitionData = self._edb.Definition.PadstackDefData(originalPadstackDefinitionData)
        if not hole_type:
            hole_type = self.hole_type
        if not params:
            params = self._hole_parameters
        if isinstance(params, list):
            params = convert_py_list_to_net_list(params)
        if not offsetx:
            offsetx = self.hole_offset_x
        if not offsety:
            offsety = self.hole_offset_y
        if not rotation:
            rotation = self.hole_rotation
        newPadstackDefinitionData.SetHoleParameters(
            hole_type,
            params,
            self._get_edb_value(offsetx),
            self._get_edb_value(offsety),
            self._get_edb_value(rotation),
        )
        self.edb_padstack.SetData(newPadstackDefinitionData)

    @property
    def hole_properties(self):
        """Hole properties.

        Returns
        -------
        list
            List of float values for hole properties.
        """
        self._hole_properties = [i.ToDouble() for i in self.hole_params[2]]
        return self._hole_properties

    @hole_properties.setter
    def hole_properties(self, propertylist):
        if not isinstance(propertylist, list):
            propertylist = [self._get_edb_value(propertylist)]
        else:
            propertylist = [self._get_edb_value(i) for i in propertylist]
        self._update_hole_parameters(params=propertylist)

    @property
    def hole_type(self):
        """Hole type.

        Returns
        -------
        int
            Type of the hole.
        """
        self._hole_type = self.hole_params[1]
        return self._hole_type

    @property
    def hole_offset_x(self):
        """Hole offset for the X axis.

        Returns
        -------
        str
            Hole offset value for the X axis.
        """
        self._hole_offset_x = self.hole_params[3].ToString()
        return self._hole_offset_x

    @hole_offset_x.setter
    def hole_offset_x(self, offset):
        self._hole_offset_x = offset
        self._update_hole_parameters(offsetx=offset)

    @property
    def hole_offset_y(self):
        """Hole offset for the Y axis.

        Returns
        -------
        str
            Hole offset value for the Y axis.
        """
        self._hole_offset_y = self.hole_params[4].ToString()
        return self._hole_offset_y

    @hole_offset_y.setter
    def hole_offset_y(self, offset):
        self._hole_offset_y = offset
        self._update_hole_parameters(offsety=offset)

    @property
    def hole_rotation(self):
        """Hole rotation.

        Returns
        -------
        str
            Value for the hole rotation.
        """
        self._hole_rotation = self.hole_params[5].ToString()
        return self._hole_rotation

    @hole_rotation.setter
    def hole_rotation(self, rotation):
        self._hole_rotation = rotation
        self._update_hole_parameters(rotation=rotation)

    @property
    def hole_plating_ratio(self):
        """Hole plating ratio.

        Returns
        -------
        float
            Percentage for the hole plating.
        """
        return self._edb.Definition.PadstackDefData(self.edb_padstack.GetData()).GetHolePlatingPercentage()

    @hole_plating_ratio.setter
    def hole_plating_ratio(self, ratio):
        originalPadstackDefinitionData = self.edb_padstack.GetData()
        newPadstackDefinitionData = self._edb.Definition.PadstackDefData(originalPadstackDefinitionData)
        newPadstackDefinitionData.SetHolePlatingPercentage(self._get_edb_value(ratio))
        self.edb_padstack.SetData(newPadstackDefinitionData)

    @property
    def hole_plating_thickness(self):
        """Hole plating thickness.

        Returns
        -------
        float
            Thickness of the hole plating if present.
        """
        if len(self.hole_properties) > 0:
            return (float(self.hole_properties[0]) * self.hole_plating_ratio / 100) / 2
        else:
            return 0

    @hole_plating_thickness.setter
    def hole_plating_thickness(self, value):
        """Hole plating thickness.

        Returns
        -------
        float
            Thickness of the hole plating if present.
        """
        value = self._get_edb_value(value).ToDouble()
        hr = 200 * float(value) / float(self.hole_properties[0])
        self.hole_plating_ratio = hr

    @property
    def hole_finished_size(self):
        """Finished hole size.

        Returns
        -------
        float
            Finished size of the hole (Total Size + PlatingThickess*2).
        """
        if len(self.hole_properties) > 0:
            return float(self.hole_properties[0]) - (self.hole_plating_thickness * 2)
        else:
            return 0

    @property
    def material(self):
        """Hole material.

        Returns
        -------
        str
            Material of the hole.
        """
        return self._padstack_def_data.GetMaterial()

    @material.setter
    def material(self, materialname):
        pdef_data = self._padstack_def_data
        pdef_data.SetMaterial(materialname)
        self._padstack_def_data = pdef_data

    @property
    def padstack_instances(self):
        """Get all the vias that belongs to active Padstack definition.

        Returns
        -------
        dict
        """
        return {id: via for id, via in self._ppadstack.instances.items() if via.padstack_definition == self.name}

    @property
    def hole_range(self):
        """Get hole range value from padstack definition.

        Returns
        -------
        str
            Possible returned values are ``"through"``, ``"begin_on_upper_pad"``,
            ``"end_on_lower_pad"``, ``"upper_pad_to_lower_pad"``, and ``"unknown_range"``.
        """
        return pascal_to_snake(self._padstack_def_data.GetHoleRange().ToString())

    @hole_range.setter
    def hole_range(self, value):
        pdef_data = self._padstack_def_data
        pdef_data.SetHoleRange(getattr(self._edb.Definition.PadstackHoleRange, snake_to_pascal(value)))
        self._padstack_def_data = pdef_data

    def convert_to_3d_microvias(self, convert_only_signal_vias=True, hole_wall_angle=75, delete_padstack_def=True):
        """Convert actual padstack instance to microvias 3D Objects with a given aspect ratio.

        Parameters
        ----------
        convert_only_signal_vias : bool, optional
            Either to convert only vias belonging to signal nets or all vias. Defaults is ``True``.
        hole_wall_angle : float, optional
            Angle of laser penetration in degrees. The angle defines the lowest hole diameter with this formula:
            HoleDiameter -2*tan(laser_angle* Hole depth). Hole depth is the height of the via (dielectric thickness).
            The default is ``15``.
            The lowest hole is ``0.75*HoleDepth/HoleDiam``.
        delete_padstack_def : bool, optional
            Whether to delete the padstack definition. The default is ``True``.
            If ``False``, the padstack definition is not deleted and the hole size is set to zero.

        Returns
        -------
            ``True`` when successful, ``False`` when failed.
        """

        if len(self.hole_properties) == 0:
            self._ppadstack._pedb.logger.error("Microvias cannot be applied on vias using hole shape polygon")
            return False

        if self.via_start_layer == self.via_stop_layer:
            self._ppadstack._pedb.logger.error("Microvias cannot be applied when Start and Stop Layers are the same.")
        layout = self._ppadstack._pedb.active_layout
        layers = self._ppadstack._pedb.stackup.signal_layers
        layer_names = [i for i in list(layers.keys())]
        if convert_only_signal_vias:
            signal_nets = [i for i in list(self._ppadstack._pedb.nets.signal_nets.keys())]

        layer_count = len(self._ppadstack._pedb.stackup.signal_layers)

        i = 0
        for via in list(self.padstack_instances.values()):
            if convert_only_signal_vias and via.net_name in signal_nets or not convert_only_signal_vias:
                pos = via.position
                started = False
                if len(self.pad_by_layer[self.via_start_layer].parameters) == 0:
                    self._ppadstack._pedb.modeler.create_polygon(
                        self.pad_by_layer[self.via_start_layer].polygon_data._edb_object,
                        layer_name=self.via_start_layer,
                        net_name=via._edb_padstackinstance.GetNet().GetName(),
                    )
                else:
                    self._edb.Cell.Primitive.Circle.Create(
                        layout,
                        self.via_start_layer,
                        via._edb_padstackinstance.GetNet(),
                        self._get_edb_value(pos[0]),
                        self._get_edb_value(pos[1]),
                        self._get_edb_value(self.pad_by_layer[self.via_start_layer].parameters_values[0] / 2),
                    )
                if len(self.pad_by_layer[self.via_stop_layer].parameters) == 0:
                    self._ppadstack._pedb.modeler.create_polygon(
                        self.pad_by_layer[self.via_stop_layer].polygon_data._edb_object,
                        layer_name=self.via_stop_layer,
                        net_name=via._edb_padstackinstance.GetNet().GetName(),
                    )
                else:
                    self._edb.Cell.Primitive.Circle.Create(
                        layout,
                        self.via_stop_layer,
                        via._edb_padstackinstance.GetNet(),
                        self._get_edb_value(pos[0]),
                        self._get_edb_value(pos[1]),
                        self._get_edb_value(self.pad_by_layer[self.via_stop_layer].parameters_values[0] / 2),
                    )
                for layer_idx, layer_name in enumerate(layer_names):
                    stop = ""
                    if layer_name == via.start_layer or started:
                        start = layer_name
                        stop = layer_names[layer_names.index(layer_name) + 1]

                        start_elevation = layers[start].lower_elevation
                        stop_elevation = layers[stop].upper_elevation
                        diel_thick = abs(start_elevation - stop_elevation)

                        rad_large = self.hole_diameter / 2
                        rad_small = rad_large - diel_thick * 1 / math.tan(math.radians(hole_wall_angle))

                        if layer_idx + 1 < layer_count / 2:  # upper half of stack
                            rad_u = rad_large
                            rad_l = rad_small
                        else:
                            rad_u = rad_small
                            rad_l = rad_large

                        cloned_circle = self._edb.Cell.Primitive.Circle.Create(
                            layout,
                            start,
                            via._edb_padstackinstance.GetNet(),
                            self._get_edb_value(pos[0]),
                            self._get_edb_value(pos[1]),
                            self._get_edb_value(rad_u),
                        )
                        cloned_circle2 = self._edb.Cell.Primitive.Circle.Create(
                            layout,
                            stop,
                            via._edb_padstackinstance.GetNet(),
                            self._get_edb_value(pos[0]),
                            self._get_edb_value(pos[1]),
                            self._get_edb_value(rad_l),
                        )
                        s3d = self._edb.Cell.Hierarchy.Structure3D.Create(
                            layout, generate_unique_name("via3d_" + via.aedt_name.replace("via_", ""), n=3)
                        )
                        s3d.AddMember(cloned_circle)
                        s3d.AddMember(cloned_circle2)
                        s3d.SetMaterial(self.material)
                        s3d.SetMeshClosureProp(self._edb.Cell.Hierarchy.Structure3D.TClosure.EndsClosed)
                        started = True
                        i += 1
                    if stop == via.stop_layer:
                        break
                if delete_padstack_def:  # pragma no cover
                    via.delete()
                else:  # pragma no cover
                    padstack_def = self._ppadstack.definitions[via.padstack_definition]
                    padstack_def.hole_properties = 0
                    self._ppadstack._pedb.logger.info("Padstack definition kept, hole size set to 0.")

        self._ppadstack._pedb.logger.info("{} Converted successfully to 3D Objects.".format(i))
        return True

    def split_to_microvias(self):
        """Convert actual padstack definition to multiple microvias definitions.

        Returns
        -------
        List of :class:`pyedb.dotnet.database.padstackEDBPadstack`
        """
        if self.via_start_layer == self.via_stop_layer:
            self._ppadstack._pedb.logger.error("Microvias cannot be applied when Start and Stop Layers are the same.")
        layout = self._ppadstack._pedb.active_layout
        layers = self._ppadstack._pedb.stackup.signal_layers
        layer_names = [i for i in list(layers.keys())]
        if abs(layer_names.index(self.via_start_layer) - layer_names.index(self.via_stop_layer)) < 2:
            self._ppadstack._pedb.logger.error(
                "Conversion can be applied only if Padstack definition is composed by more than 2 layers."
            )
            return False
        started = False
        p1 = self.edb_padstack.GetData()
        new_instances = []
        for layer_name in layer_names:
            stop = ""
            if layer_name == self.via_start_layer or started:
                start = layer_name
                stop = layer_names[layer_names.index(layer_name) + 1]
                new_padstack_name = "MV_{}_{}_{}".format(self.name, start, stop)
                included = [start, stop]
                new_padstack_definition_data = self._ppadstack._pedb.core.Definition.PadstackDefData.Create()
                new_padstack_definition_data.AddLayers(convert_py_list_to_net_list(included))
                for layer in included:
                    pl = self.pad_by_layer[layer]
                    new_padstack_definition_data.SetPadParameters(
                        layer,
                        self._ppadstack._pedb.core.Definition.PadType.RegularPad,
                        pl.int_to_geometry_type(pl.geometry_type),
                        list(
                            pl._edb_padstack.GetData().GetPadParametersValue(
                                pl.layer_name, pl.int_to_pad_type(pl.pad_type)
                            )
                        )[2],
                        pl._edb_padstack.GetData().GetPadParametersValue(
                            pl.layer_name, pl.int_to_pad_type(pl.pad_type)
                        )[3],
                        pl._edb_padstack.GetData().GetPadParametersValue(
                            pl.layer_name, pl.int_to_pad_type(pl.pad_type)
                        )[4],
                        pl._edb_padstack.GetData().GetPadParametersValue(
                            pl.layer_name, pl.int_to_pad_type(pl.pad_type)
                        )[5],
                    )
                    pl = self.antipad_by_layer[layer]
                    new_padstack_definition_data.SetPadParameters(
                        layer,
                        self._ppadstack._pedb.core.Definition.PadType.AntiPad,
                        pl.int_to_geometry_type(pl.geometry_type),
                        list(
                            pl._edb_padstack.GetData().GetPadParametersValue(
                                pl.layer_name, pl.int_to_pad_type(pl.pad_type)
                            )
                        )[2],
                        pl._edb_padstack.GetData().GetPadParametersValue(
                            pl.layer_name, pl.int_to_pad_type(pl.pad_type)
                        )[3],
                        pl._edb_padstack.GetData().GetPadParametersValue(
                            pl.layer_name, pl.int_to_pad_type(pl.pad_type)
                        )[4],
                        pl._edb_padstack.GetData().GetPadParametersValue(
                            pl.layer_name, pl.int_to_pad_type(pl.pad_type)
                        )[5],
                    )
                    pl = self.thermalpad_by_layer[layer]
                    new_padstack_definition_data.SetPadParameters(
                        layer,
                        self._ppadstack._pedb.core.Definition.PadType.ThermalPad,
                        pl.int_to_geometry_type(pl.geometry_type),
                        list(
                            pl._edb_padstack.GetData().GetPadParametersValue(
                                pl.layer_name, pl.int_to_pad_type(pl.pad_type)
                            )
                        )[2],
                        pl._edb_padstack.GetData().GetPadParametersValue(
                            pl.layer_name, pl.int_to_pad_type(pl.pad_type)
                        )[3],
                        pl._edb_padstack.GetData().GetPadParametersValue(
                            pl.layer_name, pl.int_to_pad_type(pl.pad_type)
                        )[4],
                        pl._edb_padstack.GetData().GetPadParametersValue(
                            pl.layer_name, pl.int_to_pad_type(pl.pad_type)
                        )[5],
                    )
                new_padstack_definition_data.SetHoleParameters(
                    self.hole_type,
                    self._hole_parameters,
                    self._get_edb_value(self.hole_offset_x),
                    self._get_edb_value(self.hole_offset_y),
                    self._get_edb_value(self.hole_rotation),
                )
                new_padstack_definition_data.SetMaterial(self.material)
                new_padstack_definition_data.SetHolePlatingPercentage(self._get_edb_value(self.hole_plating_ratio))
                padstack_definition = self._edb.Definition.PadstackDef.Create(
                    self._ppadstack._pedb.active_db, new_padstack_name
                )
                padstack_definition.SetData(new_padstack_definition_data)
                new_instances.append(EDBPadstack(padstack_definition, self._ppadstack))
                started = True
            if self.via_stop_layer == stop:
                break
        i = 0
        for via in list(self.padstack_instances.values()):
            for inst in new_instances:
                instance = inst.edb_padstack
                from_layer = [
                    l
                    for l in self._ppadstack._pedb.stackup._edb_layer_list
                    if l.GetName() == list(instance.GetData().GetLayerNames())[0]
                ][0]
                to_layer = [
                    l
                    for l in self._ppadstack._pedb.stackup._edb_layer_list
                    if l.GetName() == list(instance.GetData().GetLayerNames())[-1]
                ][0]
                padstack_instance = self._edb.Cell.Primitive.PadstackInstance.Create(
                    layout,
                    via._edb_padstackinstance.GetNet(),
                    generate_unique_name(instance.GetName()),
                    instance,
                    via._edb_padstackinstance.GetPositionAndRotationValue()[1],
                    via._edb_padstackinstance.GetPositionAndRotationValue()[2],
                    from_layer,
                    to_layer,
                    None,
                    None,
                )
                padstack_instance.SetIsLayoutPin(via.is_pin)
                i += 1
            via.delete()
        self._ppadstack._pedb.logger.info("Created {} new microvias.".format(i))
        return new_instances

    def _update_layer_names(self, old_name, updated_name):
        """Update padstack definition layer name when layer name is edited with the layer name setter.
        Parameters
        ----------
        old_name
            old name : str
        updated_name
            new name : str
        Returns
        -------
        bool
            ``True`` when succeed ``False`` when failed.
        """
        cloned_padstack_data = self._edb.Definition.PadstackDefData(self.edb_padstack.GetData())
        new_padstack_data = self._edb.Definition.PadstackDefData.Create()
        layers_name = cloned_padstack_data.GetLayerNames()
        layers_to_add = []
        for layer in layers_name:
            if layer == old_name:
                layers_to_add.append(updated_name)
            else:
                layers_to_add.append(layer)
        new_padstack_data.AddLayers(convert_py_list_to_net_list(layers_to_add))
        for layer in layers_name:
            updated_pad = self.pad_by_layer[layer]
            if not updated_pad.geometry_type == 0:  # pragma no cover
                pad_type = self._edb.Definition.PadType.RegularPad
                geom_type = self.pad_by_layer[layer]._pad_parameter_value[1]
                parameters = self.pad_by_layer[layer]._pad_parameter_value[2]
                offset_x = self.pad_by_layer[layer]._pad_parameter_value[3]
                offset_y = self.pad_by_layer[layer]._pad_parameter_value[4]
                rot = self.pad_by_layer[layer]._pad_parameter_value[5]
                if layer == old_name:  # pragma no cover
                    new_padstack_data.SetPadParameters(
                        updated_name, pad_type, geom_type, parameters, offset_x, offset_y, rot
                    )
                else:
                    new_padstack_data.SetPadParameters(layer, pad_type, geom_type, parameters, offset_x, offset_y, rot)

            updated_anti_pad = self.antipad_by_layer[layer]
            if not updated_anti_pad.geometry_type == 0:  # pragma no cover
                pad_type = self._edb.Definition.PadType.AntiPad
                geom_type = self.pad_by_layer[layer]._pad_parameter_value[1]
                parameters = self.pad_by_layer[layer]._pad_parameter_value[2]
                offset_x = self.pad_by_layer[layer]._pad_parameter_value[3]
                offset_y = self.pad_by_layer[layer]._pad_parameter_value[4]
                rotation = self.pad_by_layer[layer]._pad_parameter_value[5]
                if layer == old_name:  # pragma no cover
                    new_padstack_data.SetPadParameters(
                        updated_name, pad_type, geom_type, parameters, offset_x, offset_y, rotation
                    )
                else:
                    new_padstack_data.SetPadParameters(
                        layer, pad_type, geom_type, parameters, offset_x, offset_y, rotation
                    )

            updated_thermal_pad = self.thermalpad_by_layer[layer]
            if not updated_thermal_pad.geometry_type == 0:  # pragma no cover
                pad_type = self._edb.Definition.PadType.ThermalPad
                geom_type = self.pad_by_layer[layer]._pad_parameter_value[1]
                parameters = self.pad_by_layer[layer]._pad_parameter_value[2]
                offset_x = self.pad_by_layer[layer]._pad_parameter_value[3]
                offset_y = self.pad_by_layer[layer]._pad_parameter_value[4]
                rotation = self.pad_by_layer[layer]._pad_parameter_value[5]
                if layer == old_name:  # pragma no cover
                    new_padstack_data.SetPadParameters(
                        updated_name, pad_type, geom_type, parameters, offset_x, offset_y, rotation
                    )
                else:
                    new_padstack_data.SetPadParameters(
                        layer, pad_type, geom_type, parameters, offset_x, offset_y, rotation
                    )

        hole_param = cloned_padstack_data.GetHoleParameters()
        if hole_param[0]:
            hole_geom = hole_param[1]
            hole_params = convert_py_list_to_net_list([self._get_edb_value(i) for i in hole_param[2]])
            hole_off_x = self._get_edb_value(hole_param[3])
            hole_off_y = self._get_edb_value(hole_param[4])
            hole_rot = self._get_edb_value(hole_param[5])
            new_padstack_data.SetHoleParameters(hole_geom, hole_params, hole_off_x, hole_off_y, hole_rot)

        new_padstack_data.SetHolePlatingPercentage(self._get_edb_value(cloned_padstack_data.GetHolePlatingPercentage()))

        new_padstack_data.SetHoleRange(cloned_padstack_data.GetHoleRange())
        new_padstack_data.SetMaterial(cloned_padstack_data.GetMaterial())
        new_padstack_data.SetSolderBallMaterial(cloned_padstack_data.GetSolderBallMaterial())
        solder_ball_param = cloned_padstack_data.GetSolderBallParameter()
        if solder_ball_param[0]:
            new_padstack_data.SetSolderBallParameter(
                self._get_edb_value(solder_ball_param[1]), self._get_edb_value(solder_ball_param[2])
            )
        new_padstack_data.SetSolderBallPlacement(cloned_padstack_data.GetSolderBallPlacement())
        new_padstack_data.SetSolderBallShape(cloned_padstack_data.GetSolderBallShape())
        self.edb_padstack.SetData(new_padstack_data)
        return True

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

        pdef_data = self._padstack_def_data
        pad_type_list = [
            self._ppadstack._pedb._edb.Definition.PadType.RegularPad,
            self._ppadstack._pedb._edb.Definition.PadType.AntiPad,
            self._ppadstack._pedb._edb.Definition.PadType.ThermalPad,
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

    def set_pad_parameters(self, param):
        pdef_data = self._padstack_def_data

        pad_type_list = [
            self._ppadstack._pedb._edb.Definition.PadType.RegularPad,
            self._ppadstack._pedb._edb.Definition.PadType.AntiPad,
            self._ppadstack._pedb._edb.Definition.PadType.ThermalPad,
            self._ppadstack._pedb._edb.Definition.PadType.Hole,
        ]
        for pad_type in pad_type_list:
            pad_type_name = pascal_to_snake(pad_type.ToString())
            rpp = param.get(pad_type_name, [])
            for _, layer_data in enumerate(rpp):
                # Get geometry type from kwargs
                p = layer_data.get("shape")
                temp_param = []

                # Handle Circle geometry type
                if p == pascal_to_snake(self._ppadstack._pedb._edb.Definition.PadGeometryType.Circle.ToString()):
                    temp_param.append(layer_data["diameter"])
                    pad_shape = self._ppadstack._pedb._edb.Definition.PadGeometryType.Circle

                # Handle Square geometry type
                elif p == pascal_to_snake(self._ppadstack._pedb._edb.Definition.PadGeometryType.Square.ToString()):
                    temp_param.append(layer_data["size"])
                    pad_shape = self._ppadstack._pedb._edb.Definition.PadGeometryType.Square

                elif p == pascal_to_snake(self._ppadstack._pedb._edb.Definition.PadGeometryType.Rectangle.ToString()):
                    temp_param.append(layer_data["x_size"])
                    temp_param.append(layer_data["y_size"])
                    pad_shape = self._ppadstack._pedb._edb.Definition.PadGeometryType.Rectangle

                # Handle Oval geometry type
                elif p == pascal_to_snake(self._ppadstack._pedb._edb.Definition.PadGeometryType.Oval.ToString()):
                    temp_param.append(layer_data["x_size"])
                    temp_param.append(layer_data["y_size"])
                    temp_param.append(layer_data["corner_radius"])
                    pad_shape = self._ppadstack._pedb._edb.Definition.PadGeometryType.Oval

                # Handle Bullet geometry type
                elif p == pascal_to_snake(self._ppadstack._pedb._edb.Definition.PadGeometryType.Bullet.ToString()):
                    temp_param.append(layer_data["x_size"])
                    temp_param.append(layer_data["y_size"])
                    temp_param.append(layer_data["corner_radius"])
                    pad_shape = self._ppadstack._pedb._edb.Definition.PadGeometryType.Bullet

                # Handle Round45 geometry type
                elif p == pascal_to_snake(self._ppadstack._pedb._edb.Definition.PadGeometryType.Round45.ToString()):
                    temp_param.append(layer_data["inner"])
                    temp_param.append(layer_data["channel_width"])
                    temp_param.append(layer_data["isolation_gap"])
                    pad_shape = self._ppadstack._pedb._edb.Definition.PadGeometryType.Round45

                # Handle Round90 geometry type
                elif p == pascal_to_snake(self._ppadstack._pedb._edb.Definition.PadGeometryType.Round90.ToString()):
                    temp_param.append(layer_data["inner"])
                    temp_param.append(layer_data["channel_width"])
                    temp_param.append(layer_data["isolation_gap"])
                    pad_shape = self._ppadstack._pedb._edb.Definition.PadGeometryType.Round90
                elif p == pascal_to_snake(self._ppadstack._pedb._edb.Definition.PadGeometryType.NoGeometry.ToString()):
                    continue

                # Set pad parameters for the current layer
                pdef_data.SetPadParameters(
                    layer_data["layer_name"],
                    pad_type,
                    pad_shape,
                    convert_py_list_to_net_list([self._ppadstack._pedb.edb_value(i) for i in temp_param]),
                    self._ppadstack._pedb.edb_value(layer_data.get("offset_x", 0)),
                    self._ppadstack._pedb.edb_value(layer_data.get("offset_y", 0)),
                    self._ppadstack._pedb.edb_value(layer_data.get("rotation", 0)),
                )
        self._padstack_def_data = pdef_data

    def get_hole_parameters(self):
        pdef_data = self._padstack_def_data
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

    def set_hole_parameters(self, params):
        original_params = self.get_hole_parameters()
        pdef_data = self._padstack_def_data

        temp_param = []
        shape = params["shape"]
        if shape == "no_geometry":
            return  # .net api doesn't tell how to set no_geometry shape.
        for i in self.PAD_SHAPE_PARAMETERS[shape]:
            temp_param.append(params[i])
            pedb_shape = getattr(self._ppadstack._pedb._edb.Definition.PadGeometryType, snake_to_pascal(shape))

        pdef_data.SetHoleParameters(
            pedb_shape,
            convert_py_list_to_net_list([self._ppadstack._pedb.edb_value(i) for i in temp_param]),
            self._ppadstack._pedb.edb_value(params.get("offset_x", original_params.get("offset_x", 0))),
            self._ppadstack._pedb.edb_value(params.get("offset_y", original_params.get("offset_y", 0))),
            self._ppadstack._pedb.edb_value(params.get("rotation", original_params.get("rotation", 0))),
        )
        self._padstack_def_data = pdef_data

    def get_solder_parameters(self):
        pdef_data = self._padstack_def_data
        shape = pdef_data.GetSolderBallShape()
        _, diameter, mid_diameter = pdef_data.GetSolderBallParameterValue()
        placement = pdef_data.GetSolderBallPlacement()
        material = pdef_data.GetSolderBallMaterial()

        parameters = {
            "shape": [i for i, j in self._solder_shape_type.items() if j == shape][0],
            "diameter": self._ppadstack._pedb.edb_value(diameter).ToString(),
            "mid_diameter": self._ppadstack._pedb.edb_value(mid_diameter).ToString(),
            "placement": [i for i, j in self._solder_placement.items() if j == placement][0],
            "material": material,
        }
        return parameters

    def set_solder_parameters(self, parameters):
        pdef_data = self._padstack_def_data

        shape = parameters.get("shape", "no_solder_ball")
        diameter = parameters.get("diameter", "0.4mm")
        mid_diameter = parameters.get("mid_diameter", diameter)
        placement = parameters.get("placement", "above_padstack")
        material = parameters.get("material", None)

        pdef_data.SetSolderBallShape(self._solder_shape_type[shape])
        if not shape == "no_solder_ball":
            pdef_data.SetSolderBallParameter(
                self._ppadstack._pedb.edb_value(diameter), self._ppadstack._pedb.edb_value(mid_diameter)
            )
            pdef_data.SetSolderBallPlacement(self._solder_placement[placement])

        if material:
            pdef_data.SetSolderBallMaterial(material)
        self._padstack_def_data = pdef_data


class EDBPadstackInstance(Connectable):
    """Manages EDB functionalities for a padstack.

    Parameters
    ----------
    edb_padstackinstance :

    _pedb :
        Inherited AEDT object.

    Examples
    --------
    >>> from pyedb import Edb
    >>> edb = Edb(myedb, edbversion="2021.2")
    >>> edb_padstack_instance = edb.padstacks.instances[0]
    """

    def __init__(self, edb_padstackinstance, _pedb):
        super().__init__(_pedb, edb_padstackinstance)
        self._edb_padstackinstance = self._edb_object
        self._bounding_box = []
        self._side_number = None
        self._object_instance = None
        self._position = []
        self._pdef = None

    def get_terminal(self, name=None, create_new_terminal=False):
        """Get PadstackInstanceTerminal object.

        Parameters
        ----------
        name : str, optional
            Name of the terminal. Only applicable when create_new_terminal is True.
        create_new_terminal : bool, optional
            Whether to create a new terminal.

        Returns
        -------
        :class:`pyedb.dotnet.database.edb_data.terminals`
        """
        warnings.warn("Use new property :func:`terminal` instead.", DeprecationWarning)
        if create_new_terminal:
            term = self._create_terminal(name)
        else:
            from pyedb.dotnet.database.cell.terminal.padstack_instance_terminal import (
                PadstackInstanceTerminal,
            )

            term = PadstackInstanceTerminal(self._pedb, self._edb_object.GetPadstackInstanceTerminal())
        if not term.is_null:
            return term

    @property
    def side_number(self):
        """Return the number of sides meshed of the padstack instance.
        Returns
        -------
        int
            Number of sides meshed of the padstack instance.
        """
        side_value = self._edb_object.GetProductProperty(self._pedb._edb.ProductId.Hfss3DLayout, 21)
        if side_value[0]:
            return int(re.search(r"(?m)^\s*sid=(\d+)", side_value[1]).group(1))
        return 0

    @side_number.setter
    def side_number(self, value):
        """Set the number of sides meshed of the padstack instance.

        Parameters
        ----------
        value : int
            Number of sides to mesh the padstack instance.

        Returns
        -------
        bool
            True if successful, False otherwise.
        """
        if isinstance(value, int) and 3 <= value <= 64:
            prop_string = f"$begin ''\n\tsid={value}\n\tmat='copper'\n\tvs='Wirebond'\n$end ''\n"
            self._edb_object.SetProductProperty(self._pedb._edb.ProductId.Hfss3DLayout, 21, prop_string)
        else:
            raise ValueError("Number of sides must be an integer between 3 and 64")

    @property
    def terminal(self):
        """Terminal."""
        from pyedb.dotnet.database.cell.terminal.padstack_instance_terminal import (
            PadstackInstanceTerminal,
        )

        term = PadstackInstanceTerminal(self._pedb, self._edb_object.GetPadstackInstanceTerminal())
        return term if not term.is_null else None

    def _create_terminal(self, name=None):
        """Create a padstack instance terminal"""
        warnings.warn("`_create_terminal` is deprecated. Use `create_terminal` instead.", DeprecationWarning)
        return self.create_terminal(name)

    def create_terminal(self, name=None):
        """Create a padstack instance terminal"""
        from pyedb.dotnet.database.cell.terminal.padstack_instance_terminal import (
            PadstackInstanceTerminal,
        )

        term = PadstackInstanceTerminal(self._pedb, self._edb_object.GetPadstackInstanceTerminal())
        return term.create(self, name)

    def create_coax_port(self, name=None, radial_extent_factor=0):
        """Create a coax port."""
        port = self.create_port(name)
        port.radial_extent_factor = radial_extent_factor
        return port

    def create_port(self, name=None, reference=None, is_circuit_port=False):
        """Create a port on the padstack.

        Parameters
        ----------
        name : str, optional
            Name of the port. The default is ``None``, in which case a name is automatically assigned.
        reference : class:`pyedb.dotnet.database.edb_data.nets_data.EDBNetsData`, \
            class:`pyedb.dotnet.database.edb_data.padstacks_data.EDBPadstackInstance`, \
            class:`pyedb.dotnet.database.edb_data.sources.PinGroup`, optional
            Negative terminal of the port.
        is_circuit_port : bool, optional
            Whether it is a circuit port.
        """
        terminal = self.create_terminal(name)
        if reference:
            if isinstance(reference, tuple):
                reference = reference[1]
            ref_terminal = reference.create_terminal(terminal.name + "_ref")
            if reference._edb_object.ToString() == "PinGroup":
                is_circuit_port = True
        else:
            ref_terminal = None

        return self._pedb.create_port(terminal, ref_terminal, is_circuit_port)

    def _set_equipotential(self, contact_radius=None):
        """Workaround solution. Remove when EDBAPI bug is fixed for dcir_equipotential_region."""
        pad = self.definition.pad_by_layer[self.start_layer]

        pos_x, pos_y = self.position

        if contact_radius is not None:
            prim = self._pedb.modeler.create_circle(pad.layer_name, pos_x, pos_y, contact_radius, self.net_name)
            prim.dcir_equipotential_region = True
            return

        elif pad.shape.lower() == "circle":
            ra = self._pedb.edb_value(pad.parameters_values[0] / 2)
            pos = self.position
            prim = self._pedb.modeler.create_circle(pad.layer_name, pos[0], pos[1], ra, self.net_name)
        elif pad.shape.lower() == "rectangle":
            width, height = pad.parameters_values
            prim = self._pedb.modeler.create_rectangle(
                pad.layer_name,
                self.net_name,
                width=width,
                height=height,
                representation_type="CenterWidthHeight",
                center_point=self.position,
                rotation=self.component.rotation,
            )
        elif pad.shape.lower() == "oval":
            width, height, _ = pad.parameters_values
            prim = self._pedb.modeler.create_circle(
                pad.layer_name, self.position[0], self.position[1], height / 2, self.net_name
            )
        elif pad.polygon_data:
            prim = self._pedb.modeler.create_polygon(
                pad.polygon_data._edb_object, self.start_layer, net_name=self.net_name
            )
            prim.move(self.position)
        else:
            return
        prim.dcir_equipotential_region = True

    @property
    def object_instance(self):
        """Return Ansys.Ansoft.Edb.LayoutInstance.LayoutObjInstance object."""
        if not self._object_instance:
            self._object_instance = (
                self._edb_padstackinstance.GetLayout()
                .GetLayoutInstance()
                .GetLayoutObjInstance(self._edb_padstackinstance, None)
            )
        return self._object_instance

    @property
    def bounding_box(self):
        """Get bounding box of the padstack instance.
        Because this method is slow, the bounding box is stored in a variable and reused.

        Returns
        -------
        list of float
        """
        if self._bounding_box:
            return self._bounding_box
        bbox = self.object_instance.GetBBox()
        self._bounding_box = [
            [bbox.Item1.X.ToDouble(), bbox.Item1.Y.ToDouble()],
            [bbox.Item2.X.ToDouble(), bbox.Item2.Y.ToDouble()],
        ]
        return self._bounding_box

    def in_polygon(self, polygon_data, include_partial=True, simple_check=False):
        """Check if padstack Instance is in given polygon data.

        Parameters
        ----------
        polygon_data : PolygonData Object
        include_partial : bool, optional
            Whether to include partial intersecting instances. The default is ``True``.
        simple_check : bool, optional
            Whether to perform a single check based on the padstack center or check the padstack bounding box.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        pos = [i for i in self.position]
        int_val = 1 if polygon_data.PointInPolygon(self._pedb.point_data(*pos)) else 0
        if int_val == 0:
            return False

        if simple_check:
            # pos = [i for i in self.position]
            # int_val = 1 if polygon_data.PointInPolygon(self._pedb.point_data(*pos)) else 0
            return True
        else:
            plane = self._pedb.modeler.Shape("rectangle", pointA=self.bounding_box[0], pointB=self.bounding_box[1])
            rectangle_data = self._pedb.modeler.shape_to_polygon_data(plane)
            int_val = polygon_data.GetIntersectionType(rectangle_data)
        # Intersection type:
        # 0 = objects do not intersect
        # 1 = this object fully inside other (no common contour points)
        # 2 = other object fully inside this
        # 3 = common contour points 4 = undefined intersection
        if int_val == 0:
            return False
        elif include_partial:
            return True
        elif int_val < 3:
            return True
        else:
            return False

    @property
    def pin(self):
        """EDB padstack object."""
        warnings.warn("`pin` is deprecated.", DeprecationWarning)
        return self._edb_padstackinstance

    @property
    def padstack_definition(self):
        """Padstack definition Name.

        Returns
        -------
        str
            Name of the padstack definition.
        """
        return self.definition.name

    @property
    def definition(self):
        """Padstack definition.

        Returns
        -------
        str
            Name of the padstack definition.
        """
        self._pdef = EDBPadstack(self._edb_padstackinstance.GetPadstackDef(), self._pedb.padstacks)
        return self._pdef

    @property
    def backdrill_top(self):
        """Backdrill layer from top.

        Returns
        -------
        tuple
            Tuple of the layer name, drill diameter, and offset if it exists.
        """
        layer = self._pedb.core.Cell.Layer("", self._pedb.core.Cell.LayerType.SignalLayer)
        val = self._pedb.edb_value(0)
        offset = self._pedb.edb_value(0.0)
        (
            flag,
            drill_to_layer,
            offset,
            diameter,
        ) = self._edb_padstackinstance.GetBackDrillParametersLayerValue(layer, offset, val, False)
        if flag:
            if offset.ToDouble():
                return drill_to_layer.GetName(), diameter.ToString(), offset.ToString()
            else:
                return drill_to_layer.GetName(), diameter.ToString()
        else:
            return

    def set_backdrill_top(self, drill_depth, drill_diameter, offset=0.0):
        """Set backdrill from top.

        Parameters
        ----------
        drill_depth : str
            Name of the drill to layer.
        drill_diameter : float, str
            Diameter of backdrill size.
        offset : float, str
            Offset for the backdrill. The default is ``0.0``. If the value is other than the
            default, the stub does not stop at the layer. In AEDT, this parameter is called
            "Mfg stub length".

        Returns
        -------
        bool
            True if success, False otherwise.
        """
        layer = self._pedb.stackup.layers[drill_depth]._edb_layer
        val = self._pedb.edb_value(drill_diameter)
        offset = self._pedb.edb_value(offset)
        if offset.ToDouble():
            return self._edb_padstackinstance.SetBackDrillParameters(layer, offset, val, False)
        else:
            return self._edb_padstackinstance.SetBackDrillParameters(layer, val, False)

    @property
    def backdrill_type(self):
        """Adding grpc compatibility. DotNet is supporting only layer drill type with adding stub length."""
        return "layer_drill"

    def get_back_drill_by_layer(self):
        params = self.backdrill_parameters["from_bottom"]
        return (
            params["drill_to_layer"],
            round(self._pedb.edb_value(params["stub_length"]).ToDouble(), 6),
            round(self._pedb.edb_value(params["diameter"]).ToDouble(), 6),
        )

    @property
    def backdrill_bottom(self):
        """Backdrill layer from bottom.

        Returns
        -------
        tuple
            Tuple of the layer name, drill diameter, and drill offset if it exists.
        """
        layer = self._pedb.core.Cell.Layer("", self._pedb.core.Cell.LayerType.SignalLayer)
        val = self._pedb.edb_value(0)
        offset = self._pedb.edb_value(0.0)
        (
            flag,
            drill_to_layer,
            offset,
            diameter,
        ) = self._edb_padstackinstance.GetBackDrillParametersLayerValue(layer, offset, val, True)
        if flag:
            if offset.ToDouble():
                return drill_to_layer.GetName(), diameter.ToString(), offset.ToString()
            else:
                return drill_to_layer.GetName(), diameter.ToString()
        else:
            return

    @property
    def backdrill_parameters(self):
        data = {}
        flag, drill_to_layer, offset, diameter = self._edb_object.GetBackDrillParametersLayerValue(
            self._pedb.core.Cell.Layer("", self._pedb.core.Cell.LayerType.SignalLayer),
            self._pedb.edb_value(0),
            self._pedb.edb_value(0.0),
            True,
        )
        if flag:
            if drill_to_layer.GetName():
                data["from_bottom"] = {
                    "drill_to_layer": drill_to_layer.GetName(),
                    "diameter": diameter.ToString(),
                    "stub_length": offset.ToString(),
                }
        flag, drill_to_layer, offset, diameter = self._edb_object.GetBackDrillParametersLayerValue(
            self._pedb.core.Cell.Layer("", self._pedb.core.Cell.LayerType.SignalLayer),
            self._pedb.edb_value(0),
            self._pedb.edb_value(0.0),
            False,
        )
        if flag:
            if drill_to_layer.GetName():
                data["from_top"] = {
                    "drill_to_layer": drill_to_layer.GetName(),
                    "diameter": diameter.ToString(),
                    "stub_length": offset.ToString(),
                }
        return data

    @backdrill_parameters.setter
    def backdrill_parameters(self, params):
        from_bottom = params.get("from_bottom")
        if from_bottom:
            self._edb_object.SetBackDrillParameters(
                self._pedb.stackup.layers[from_bottom.get("drill_to_layer")]._edb_object,
                self._pedb.edb_value(from_bottom.get("stub_length")),
                self._pedb.edb_value(from_bottom.get("diameter")),
                True,
            )
        from_top = params.get("from_top")
        if from_top:
            self._edb_object.SetBackDrillParameters(
                self._pedb.stackup.layers[from_top.get("drill_to_layer")]._edb_object,
                self._pedb.edb_value(from_top.get("stub_length")),
                self._pedb.edb_value(from_top.get("diameter")),
                False,
            )

    def set_back_drill_by_layer(self, drill_to_layer, diameter, offset, from_bottom=True):
        """Method added to bring compatibility with grpc."""
        if from_bottom:
            if not isinstance(drill_to_layer, str):
                drill_to_layer = drill_to_layer.name
            self.set_backdrill_bottom(drill_depth=drill_to_layer, drill_diameter=diameter, offset=offset)

    def set_backdrill_bottom(self, drill_depth, drill_diameter, offset=0.0):
        """Set backdrill from bottom.

        Parameters
        ----------
        drill_depth : str
            Name of the drill to layer.
        drill_diameter : float, str
            Diameter of the backdrill size.
        offset : float, str, optional
            Offset for the backdrill. The default is ``0.0``. If the value is other than the
            default, the stub does not stop at the layer. In AEDT, this parameter is called
            "Mfg stub length".

        Returns
        -------
        bool
            True if success, False otherwise.
        """
        layer = self._pedb.stackup.layers[drill_depth]._edb_layer
        val = self._pedb.edb_value(drill_diameter)
        offset = self._pedb.edb_value(offset)
        if offset.ToDouble():
            return self._edb_object.SetBackDrillParameters(layer, offset, val, True)
        else:
            return self._edb_object.SetBackDrillParameters(layer, val, True)

    @property
    def start_layer(self):
        """Starting layer.

        Returns
        -------
        str
            Name of the starting layer.
        """
        _, start_layer, stop_layer = self._edb_object.GetLayerRange()

        if start_layer:
            return start_layer.GetName()
        return None

    @start_layer.setter
    def start_layer(self, layer_name):
        stop_layer = self._pedb.stackup.signal_layers[self.stop_layer]._edb_layer
        layer = self._pedb.stackup.signal_layers[layer_name]._edb_layer
        self._edb_padstackinstance.SetLayerRange(layer, stop_layer)

    @property
    def stop_layer(self):
        """Stopping layer.

        Returns
        -------
        str
            Name of the stopping layer.
        """
        _, start_layer, stop_layer = self._edb_padstackinstance.GetLayerRange()

        if stop_layer:
            return stop_layer.GetName()
        return None

    @stop_layer.setter
    def stop_layer(self, layer_name):
        start_layer = self._pedb.stackup.signal_layers[self.start_layer]._edb_layer
        layer = self._pedb.stackup.signal_layers[layer_name]._edb_layer
        self._edb_padstackinstance.SetLayerRange(start_layer, layer)

    @property
    def layer_range_names(self):
        """List of all layers to which the padstack instance belongs."""
        _, start_layer, stop_layer = self._edb_padstackinstance.GetLayerRange()
        started = False
        layer_list = []
        start_layer_name = start_layer.GetName()
        stop_layer_name = stop_layer.GetName()
        for layer_name in list(self._pedb.stackup.signal_layers.keys()):
            if started:
                layer_list.append(layer_name)
                if layer_name == stop_layer_name or layer_name == start_layer_name:
                    break
            elif layer_name == start_layer_name:
                started = True
                layer_list.append(layer_name)
                if layer_name == stop_layer_name:
                    break
            elif layer_name == stop_layer_name:
                started = True
                layer_list.append(layer_name)
                if layer_name == start_layer_name:
                    break
        return layer_list

    @property
    def is_pin(self):
        """Determines whether this padstack instance is a layout pin.

        Returns
        -------
        bool
            True if this padstack type is a layout pin, False otherwise.
        """
        return self._edb_padstackinstance.IsLayoutPin()

    @is_pin.setter
    def is_pin(self, pin):
        """Set padstack type

        Parameters
        ----------
        pin : bool
            True if set this padstack instance as pin, False otherwise
        """
        self._edb_padstackinstance.SetIsLayoutPin(pin)

    @property
    def position(self):
        """Padstack instance position.

        Returns
        -------
        list
            List of ``[x, y]`` coordinates for the padstack instance position.
        """
        self._position = []
        out = self._edb_padstackinstance.GetPositionAndRotationValue()
        if self._edb_padstackinstance.GetComponent():
            out2 = self._edb_padstackinstance.GetComponent().GetTransform().TransformPoint(out[1])
            self._position = [round(out2.X.ToDouble(), 6), round(out2.Y.ToDouble(), 6)]
        elif out[0]:
            self._position = [round(out[1].X.ToDouble(), 6), round(out[1].Y.ToDouble(), 6)]
        return self._position

    @position.setter
    def position(self, value):
        pos = []
        for v in value:
            if isinstance(v, (float, int, str)):
                pos.append(self._pedb.edb_value(v))
            else:
                pos.append(v)
        point_data = self._pedb.pedb_class.database.geometry.point_data.PointData.create_from_xy(
            self._pedb, pos[0], pos[1]
        )
        self._edb_padstackinstance.SetPositionAndRotation(point_data._edb_object, self._pedb.edb_value(self.rotation))

    @property
    def rotation(self):
        """Padstack instance rotation.

        Returns
        -------
        float
            Rotatation value for the padstack instance.
        """
        out = self._edb_padstackinstance.GetPositionAndRotationValue()

        if out[0]:
            return round(out[2].ToDouble(), 6)

    @property
    def metal_volume(self):
        """Metal volume of the via hole instance in cubic units (m3). Metal plating ratio is accounted.

        Returns
        -------
        float
            Metal volume of the via hole instance.

        """
        volume = 0
        if not self.start_layer == self.stop_layer:
            start_layer = self.start_layer
            stop_layer = self.stop_layer
            if self.backdrill_top:  # pragma no cover
                start_layer = self.backdrill_top[0]
            if self.backdrill_bottom:  # pragma no cover
                stop_layer = self.backdrill_bottom[0]
            padstack_def = self._pedb.padstacks.definitions[self.padstack_definition]
            hole_diam = 0
            try:  # pragma no cover
                hole_diam = padstack_def.hole_properties[0]
            except Exception as e:  # pragma no cover
                self._pedb.logger.error(
                    f"Failed to access first element of hole_properties attribute of object "
                    f"{padstack_def} - Hole diameter is set to default value 0 - {type(e).__name__}: {str(e)}"
                )
            if hole_diam:  # pragma no cover
                hole_finished_size = padstack_def.hole_finished_size
                via_length = (
                    self._pedb.stackup.signal_layers[start_layer].upper_elevation
                    - self._pedb.stackup.signal_layers[stop_layer].lower_elevation
                )
                volume = (math.pi * (hole_diam / 2) ** 2 - math.pi * (hole_finished_size / 2) ** 2) * via_length
        return volume

    @property
    def pin_number(self):
        """Get pin number."""
        warnings.warn("`pin_number` is deprecated. Use `name` method instead.", DeprecationWarning)
        return self.name

    @property
    def component_pin(self):
        """Get component pin."""
        warnings.warn("`pin_number` is deprecated. Use `name` method instead.", DeprecationWarning)
        return self.name

    @property
    def aedt_name(self):
        """Retrieve the pin name that is shown in AEDT.

        .. note::
           To obtain the EDB core pin name, use `pin.GetName()`.

        Returns
        -------
        str
            Name of the pin in AEDT.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edbapp.padstacks.instances[111].get_aedt_pin_name()

        """

        val = String("")
        _, name = self._edb_padstackinstance.GetProductProperty(self._pedb.core.ProductId.Designer, 11, val)
        aedt_name = str(name).strip("'")
        if aedt_name == "":
            if self.component_name:
                aedt_name = f"{self.component_name}-{self.name}"
            else:
                aedt_name = "Via_{}".format(self.id)
            self.aedt_name = aedt_name
        return aedt_name

    @aedt_name.setter
    def aedt_name(self, value):
        self._edb_object.SetProductProperty(self._pedb.core.ProductId.Designer, 11, value)

    def parametrize_position(self, prefix=None):
        """Parametrize the instance position.

        Parameters
        ----------
        prefix : str, optional
            Prefix for the variable name. Default is ``None``.
            Example `"MyVariableName"` will create 2 Project variables $MyVariableNamesX and $MyVariableNamesY.

        Returns
        -------
        List
            List of variables created.
        """
        p = self.position
        if not prefix:
            var_name = "${}_pos".format(self.name)
        else:
            var_name = "${}".format(prefix)
        self._pedb.add_project_variable(var_name + "X", p[0])
        self._pedb.add_project_variable(var_name + "Y", p[1])
        self.position = [var_name + "X", var_name + "Y"]
        return [var_name + "X", var_name + "Y"]

    def in_voids(self, net_name=None, layer_name=None):
        """Check if this padstack instance is in any void.

        Parameters
        ----------
        net_name : str
            Net name of the voids to be checked. Default is ``None``.
        layer_name : str
            Layer name of the voids to be checked. Default is ``None``.

        Returns
        -------
        list
            List of the voids that include this padstack instance.
        """
        x_pos = self._pedb.edb_value(self.position[0])
        y_pos = self._pedb.edb_value(self.position[1])
        point_data = self._pedb.modeler._edb.geometry.point_data(x_pos, y_pos)

        voids = []
        for prim in self._pedb.modeler.get_primitives(net_name, layer_name, is_void=True):
            if prim.primitive_object.GetPolygonData().PointInPolygon(point_data):
                voids.append(prim)
        return voids

    @property
    def pingroups(self):
        """Pin groups that the pin belongs to.

        Returns
        -------
        list
            List of pin groups that the pin belongs to.
        """
        return self._edb_padstackinstance.GetPinGroups()

    @property
    def placement_layer(self):
        """Placement layer.

        Returns
        -------
        str
            Name of the placement layer.
        """
        return self._edb_padstackinstance.GetGroup().GetPlacementLayer().Clone().GetName()

    @property
    def lower_elevation(self):
        """Lower elevation of the placement layer.

        Returns
        -------
        float
            Lower elavation of the placement layer.
        """
        try:
            return round(self._edb_padstackinstance.GetGroup().GetPlacementLayer().Clone().GetLowerElevation(), 6)
        except AttributeError:  # pragma: no cover
            return None

    @property
    def upper_elevation(self):
        """Upper elevation of the placement layer.

        Returns
        -------
        float
           Upper elevation of the placement layer.
        """
        try:
            return round(self._edb_padstackinstance.GetGroup().GetPlacementLayer().Clone().GetUpperElevation(), 6)
        except AttributeError:  # pragma: no cover
            return None

    @property
    def top_bottom_association(self):
        """Top/bottom association of the placement layer.

        Returns
        -------
        int
            Top/bottom association of the placement layer.

            * 0 Top associated.
            * 1 No association.
            * 2 Bottom associated.
            * 4 Number of top/bottom association type.
            * -1 Undefined.
        """
        return int(self._edb_padstackinstance.GetGroup().GetPlacementLayer().GetTopBottomAssociation())

    def create_rectangle_in_pad(self, layer_name, return_points=False, partition_max_order=16):
        """Create a rectangle inscribed inside a padstack instance pad.

        The rectangle is fully inscribed in the pad and has the maximum area.
        It is necessary to specify the layer on which the rectangle will be created.

        Parameters
        ----------
        layer_name : str
            Name of the layer on which to create the polygon.
        return_points : bool, optional
            If `True` does not create the rectangle and just returns a list containing the rectangle vertices.
            Default is `False`.
        partition_max_order : float, optional
            Order of the lattice partition used to find the quasi-lattice polygon that approximates ``polygon``.
            Default is ``16``.

        Returns
        -------
        bool, List,  :class:`pyedb.dotnet.database.edb_data.primitives.EDBPrimitives`
            Polygon when successful, ``False`` when failed, list of list if `return_points=True`.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder", edbversion="2021.2")
        >>> edb_layout = edbapp.modeler
        >>> list_of_padstack_instances = list(edbapp.padstacks.instances.values())
        >>> padstack_inst = list_of_padstack_instances[0]
        >>> padstack_inst.create_rectangle_in_pad("TOP")
        """

        padstack_center = self.position
        rotation = self.rotation  # in radians
        padstack_name = self.padstack_definition

        padstack = self._pedb.padstacks.definitions[padstack_name]
        padstack_pad = (
            padstack.pad_by_layer[layer_name]
            if layer_name in padstack.pad_by_layer
            else padstack.pad_by_layer[padstack.via_start_layer]
        )

        pad_shape = padstack_pad.geometry_type
        params = padstack_pad.parameters_values
        polygon_data = padstack_pad._polygon_data_dotnet
        pad_offset = [float_units(padstack_pad.offset_x), float_units(padstack_pad.offset_y)]

        def _rotate(p):
            x = p[0] * math.cos(rotation) - p[1] * math.sin(rotation)
            y = p[0] * math.sin(rotation) + p[1] * math.cos(rotation)
            return [x, y]

        def _translate(p, t=None):
            if t is None:
                t = padstack_center
            x = p[0] + t[0]
            y = p[1] + t[1]
            return [x, y]

        rect = None

        if pad_shape == 1:
            # Circle
            diameter = params[0]
            r = diameter * 0.5
            p1 = [r, 0.0]
            p2 = [0.0, r]
            p3 = [-r, 0.0]
            p4 = [0.0, -r]
            rect = [_translate(p1), _translate(p2), _translate(p3), _translate(p4)]
        elif pad_shape == 2:
            # Square
            square_size = params[0]
            s2 = square_size * 0.5
            p1 = [s2, s2]
            p2 = [-s2, s2]
            p3 = [-s2, -s2]
            p4 = [s2, -s2]
            rect = [
                _translate(_rotate(p1)),
                _translate(_rotate(p2)),
                _translate(_rotate(p3)),
                _translate(_rotate(p4)),
            ]
        elif pad_shape == 3:
            # Rectangle
            x_size = float(params[0])
            y_size = float(params[1])
            sx2 = x_size * 0.5
            sy2 = y_size * 0.5
            p1 = [sx2, sy2]
            p2 = [-sx2, sy2]
            p3 = [-sx2, -sy2]
            p4 = [sx2, -sy2]
            rect = [
                _translate(_rotate(p1)),
                _translate(_rotate(p2)),
                _translate(_rotate(p3)),
                _translate(_rotate(p4)),
            ]
        elif pad_shape == 4:
            # Oval
            x_size = params[0]
            y_size = params[1]
            corner_radius = float(params[2])
            if corner_radius >= min(x_size, y_size):
                r = min(x_size, y_size)
            else:
                r = corner_radius
            sx = x_size * 0.5 - r
            sy = y_size * 0.5 - r
            k = r / math.sqrt(2)
            p1 = [sx + k, sy + k]
            p2 = [-sx - k, sy + k]
            p3 = [-sx - k, -sy - k]
            p4 = [sx + k, -sy - k]
            rect = [
                _translate(_rotate(p1)),
                _translate(_rotate(p2)),
                _translate(_rotate(p3)),
                _translate(_rotate(p4)),
            ]
        elif pad_shape == 5:
            # Bullet
            x_size = params[0]
            y_size = params[1]
            corner_radius = params[2]
            if corner_radius >= min(x_size, y_size):
                r = min(x_size, y_size)
            else:
                r = corner_radius
            sx = x_size * 0.5 - r
            sy = y_size * 0.5 - r
            k = r / math.sqrt(2)
            p1 = [sx + k, sy + k]
            p2 = [-x_size * 0.5, sy + k]
            p3 = [-x_size * 0.5, -sy - k]
            p4 = [sx + k, -sy - k]
            rect = [
                _translate(_rotate(p1)),
                _translate(_rotate(p2)),
                _translate(_rotate(p3)),
                _translate(_rotate(p4)),
            ]
        elif pad_shape == 6:
            # N-Sided Polygon
            size = params[0]
            num_sides = params[1]
            ext_radius = size * 0.5
            apothem = ext_radius * math.cos(math.pi / num_sides)
            p1 = [apothem, 0.0]
            p2 = [0.0, apothem]
            p3 = [-apothem, 0.0]
            p4 = [0.0, -apothem]
            rect = [
                _translate(_rotate(p1)),
                _translate(_rotate(p2)),
                _translate(_rotate(p3)),
                _translate(_rotate(p4)),
            ]
        elif pad_shape == 0 and polygon_data is not None:
            # Polygon
            points = []
            i = 0
            while i < polygon_data._edb_object.Count:
                point = polygon_data._edb_object.GetPoint(i)
                i += 1
                if point.IsArc():
                    continue
                else:
                    points.append([point.X.ToDouble(), point.Y.ToDouble()])
            xpoly, ypoly = zip(*points)
            polygon = [list(xpoly), list(ypoly)]
            rectangles = GeometryOperators.find_largest_rectangle_inside_polygon(
                polygon, partition_max_order=partition_max_order
            )
            rect = rectangles[0]
            for i in range(4):
                rect[i] = _translate(_rotate(rect[i]))

        if rect is None or len(rect) != 4:
            raise RuntimeError()
        offset_rect = [_translate(p, _rotate(pad_offset)) for p in rect]
        path = self._pedb.modeler.Shape("polygon", points=offset_rect)
        pdata = self._pedb.modeler.shape_to_polygon_data(path)
        new_rect = []
        for point in pdata.Points:
            p_transf = self._edb_padstackinstance.GetComponent().GetTransform().TransformPoint(point)
            new_rect.append([p_transf.X.ToDouble(), p_transf.Y.ToDouble()])
        if return_points:
            return new_rect
        else:
            path = self._pedb.modeler.Shape("polygon", points=new_rect)
            created_polygon = self._pedb.modeler.create_polygon(path, layer_name)
            return created_polygon

    def get_reference_pins(self, reference_net="GND", search_radius=5e-3, max_limit=0, component_only=True):
        """Search for reference pins using given criteria.

        Parameters
        ----------
        reference_net : str, optional
            Reference net. The default is ``"GND"``.
        search_radius : float, optional
            Search radius for finding padstack instances. The default is ``5e-3``.
        max_limit : int, optional
            Maximum limit for the padstack instances found. The default is ``0``, in which
            case no limit is applied. The maximum limit value occurs on the nearest
            reference pins from the positive one that is found.
        component_only : bool, optional
            Whether to limit the search to component padstack instances only. The
            default is ``True``. When ``False``, the search is extended to the entire layout.

        Returns
        -------
        list
            List of :class:`dotnet.database.edb_data.padstacks_data.EDBPadstackInstance`.

        Examples
        --------
        >>> edbapp = Edb("target_path")
        >>> pin = edbapp.components.instances["J5"].pins["19"]
        >>> reference_pins = pin.get_reference_pins(reference_net="GND", search_radius=5e-3, max_limit=0,
        >>> component_only=True)
        """
        return self._pedb.padstacks.get_reference_pins(
            positive_pin=self,
            reference_net=reference_net,
            search_radius=search_radius,
            max_limit=max_limit,
            component_only=component_only,
        )

    def split(self) -> list:
        """Split padstack instance into multiple instances. The new instances only connect adjacent layers."""
        pdef_name = self.padstack_definition
        position = self.position
        net_name = self.net_name
        name = self.name
        stackup_layer_range = list(self._pedb.stackup.signal_layers.keys())
        start_idx = stackup_layer_range.index(self.start_layer)
        stop_idx = stackup_layer_range.index(self.stop_layer)
        temp = []
        for idx, (l1, l2) in enumerate(
            list(zip(stackup_layer_range[start_idx:stop_idx], stackup_layer_range[start_idx + 1 : stop_idx + 1]))
        ):
            pd_inst = self._pedb.padstacks.place(
                position, pdef_name, net_name, f"{name}_{idx}", fromlayer=l1, tolayer=l2
            )
            temp.append(pd_inst)
        self.delete()
        return temp

    def convert_hole_to_conical_shape(self, angle=75):
        """Convert actual padstack instance to microvias 3D Objects with a given aspect ratio.

        Parameters
        ----------
        angle : float, optional
            Angle of laser penetration in degrees. The angle defines the lowest hole diameter with this formula:
            HoleDiameter -2*tan(laser_angle* Hole depth). Hole depth is the height of the via (dielectric thickness).
            The default is ``75``.
            The lowest hole is ``0.75*HoleDepth/HoleDiam``.

        Returns
        -------
        """
        pos = self.position
        stackup_layers = self._pedb.stackup.stackup_layers
        signal_layers = self._pedb.stackup.signal_layers
        layer_idx = list(signal_layers.keys()).index(self.start_layer)

        _layer_idx = list(stackup_layers.keys()).index(self.start_layer)
        diel_layer_idx = list(stackup_layers.keys())[_layer_idx + 1]
        diel_thickness = stackup_layers[diel_layer_idx].thickness

        rad_large = self.definition.hole_diameter / 2
        rad_small = rad_large - diel_thickness * 1 / math.tan(math.radians(angle))

        if layer_idx + 1 < len(signal_layers) / 2:  # upper half of stack
            rad_u = rad_large
            rad_l = rad_small
        else:
            rad_u = rad_small
            rad_l = rad_large

        layout = self._pedb.active_layout
        cloned_circle = self._edb.Cell.Primitive.Circle.Create(
            layout,
            self.start_layer,
            self._edb_padstackinstance.GetNet(),
            self._pedb.edb_value(pos[0]),
            self._pedb.edb_value(pos[1]),
            self._pedb.edb_value(rad_u),
        )
        cloned_circle2 = self._edb.Cell.Primitive.Circle.Create(
            layout,
            self.stop_layer,
            self._edb_padstackinstance.GetNet(),
            self._pedb.edb_value(pos[0]),
            self._pedb.edb_value(pos[1]),
            self._pedb.edb_value(rad_l),
        )
        s3d = self._pedb._edb.Cell.Hierarchy.Structure3D.Create(
            layout, generate_unique_name("via3d_" + self.aedt_name.replace("via_", ""), n=3)
        )
        s3d.AddMember(cloned_circle)
        s3d.AddMember(cloned_circle2)
        s3d.SetMaterial(self.definition.material)
        s3d.SetMeshClosureProp(self._pedb._edb.Cell.Hierarchy.Structure3D.TClosure.EndsClosed)

        hole_override_enabled = True
        hole_override_diam = 0
        self._edb_object.SetHoleOverride(hole_override_enabled, self._pedb.edb_value(hole_override_diam))
