from collections import OrderedDict
import math
import re
import warnings

from pyedb.grpc.edb_core.edb_data.primitives_data import EDBPrimitivesMain
from ansys.edb.layer.layer import LayerType
from pyedb.grpc.edb_core.edb_data.terminals import PadstackInstanceTerminal
import ansys.edb.utility as utility
import ansys.edb.geometry as geometry
import ansys.edb.definition as definition
import ansys.edb.database as database
import ansys.edb.hierarchy as hierachy
#from ansys.edb.utility import Value
#from ansys.edb.geometry.point_data import PointData
#from ansys.edb.database import ProductIdType
#from ansys.edb.definition.padstack_def_data import PadType
from pyedb.generic.general_methods import generate_unique_name
from pyedb.generic.general_methods import pyedb_function_handler
#from ansys.edb.geometry.polygon_data import PolygonData
#from ansys.edb.hierarchy import MeshClosure
#from ansys.edb.definition.padstack_def_data import PadGeometryType
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
    >>> edb = Edb(myedb, edbversion="2021.2")
    >>> edb_pad_properties = edb.padstacks.definitions["MyPad"].pad_by_layer["TOP"]
    """

    def __init__(self, edb_padstack, layer_name, pad_type, p_edb_padstack):
        self._edb_padstack = edb_padstack
        self._pedbpadstack = p_edb_padstack
        self.layer_name = layer_name
        self.pad_type = pad_type

    @property
    def _stackup_layers(self):
        return self._pedbpadstack._stackup_layers

    @property
    def _edb(self):
        return self._pedbpadstack._edb

    @property
    def _pad_parameter_value(self):
        pad_params = self._edb_padstack.data.get_pad_parameters(self.layer_name, self.int_to_pad_type(self.pad_type))
        return pad_params

    @property
    def geometry_type(self):
        """Geometry type.

        Returns
        -------
        int
            Type of the geometry.
        """

        padparams = self._edb_padstack.data.get_pad_parameters(self.layer_name, self.int_to_pad_type(self.pad_type))
        return int(padparams[1])

    @geometry_type.setter
    def geometry_type(self, geom_type):
        """0, NoGeometry. 1, Circle. 2 Square. 3, Rectangle. 4, Oval. 5, Bullet. 6, N-sided polygon. 7, Polygonal
        shape.8, Round gap with 45 degree thermal ties. 9, Round gap with 90 degree thermal ties.10, Square gap
        with 45 degree thermal ties. 11, Square gap with 90 degree thermal ties.
        """
        val = utility.Value(0)
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
        self._update_pad_parameters_parameters(geom_type=definition.PadGeometryType[value].value)

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
    def polygon_data(self):
        """Parameters.

        Returns
        -------
        list
            List of parameters.
        """
        try:
            pad_values = self._edb_padstack.data.get_pad_parameters(self.layer_name,
                                                                    self.int_to_pad_type(self.pad_type))
            if isinstance(pad_values[0], geometry.PolygonData):
                return pad_values[0]
            else:
                return
        except:
            return

    @property
    def parameters(self):
        """Get parameters.

        Returns
        -------
        dict
        """
        value = list(self._pad_parameter_value[2])
        if self.shape == definition.PadGeometryType.PADGEOMTYPE_CIRCLE:
            return OrderedDict({"Diameter": utility.Value(value[0])})
        elif self.shape == definition.PadGeometryType.PADGEOMTYPE_SQUARE:
            return OrderedDict({"Size": utility.Value(value[0])})
        elif self.shape == definition.PadGeometryType.PADGEOMTYPE_RECTANGLE:
            return OrderedDict({"XSize": utility.Value(value[0]), "YSize": utility.Value(value[1])})
        elif self.shape in [definition.PadGeometryType.PADGEOMTYPE_OVAL, definition.PadGeometryType.PADGEOMTYPE_BULLET]:
            return OrderedDict(
                {"XSize": utility.Value(value[0]), "YSize": utility.Value(value[1]), "CornerRadius": utility.Value(value[2])}
            )
        elif self.shape == definition.PadGeometryType.PADGEOMTYPE_NSIDED_POLYGON.name:
            return OrderedDict({"Size": utility.Value(value[0]), "NumSides": utility.Value(value[1])})
        elif self.shape in [definition.PadGeometryType.PADGEOMTYPE_ROUND45,
                            definition.PadGeometryType.PADGEOMTYPE_ROUND90]:  # pragma: no cover
            return OrderedDict(
                {"Inner": utility.Value(value[0]), "ChannelWidth": utility.Value(value[1]), "IsolationGap": utility.Value(value[2])}
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
            value = {k: v.tostring if isinstance(v, utility.Value) else v for k, v in value.items()}
            if self.shape == definition.PadGeometryType.PADGEOMTYPE_CIRCLE:
                params = [utility.Value(value["Diameter"])]
            elif self.shape == definition.PadGeometryType.PADGEOMTYPE_SQUARE:
                params = [utility.Value(value["Size"])]
            elif self.shape == definition.PadGeometryType.PADGEOMTYPE_RECTANGLE:
                params = [utility.Value(value["XSize"]), utility.Value(value["YSize"])]
            elif self.shape == [definition.PadGeometryType.PADGEOMTYPE_OVAL, definition.PadGeometryType.PADGEOMTYPE_BULLET]:
                params = [utility.Value(value["XSize"]), utility.Value(value["YSize"]), utility.Value(value["CornerRadius"])]
            elif self.shape in [definition.PadGeometryType.PADGEOMTYPE_ROUND45,
                                definition.PadGeometryType.PADGEOMTYPE_ROUND90]:  # pragma: no cover
                params = [utility.Value(value["Inner"]), utility.Value(value["ChannelWidth"]), utility.Value(value["IsolationGap"])]
            else:  # pragma: no cover
                params = None
        elif isinstance(value, list):
            params = [utility.Value(i) for i in value]
        else:
            params = [utility.Value(value)]
        self._update_pad_parameters_parameters(params=params)

    @property
    def offset_x(self):
        """Offset for the X axis.

        Returns
        -------
        str
            Offset for the X axis.
        """

        pad_values = self._edb_padstack.data.get_pad_parameters(self.layer_name, self.int_to_pad_type(self.pad_type))
        return pad_values[3]

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

        pad_values = self._edb_padstack.data.get_pad_parameters(self.layer_name, self.int_to_pad_type(self.pad_type))
        return pad_values[4]

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

        pad_values = self._edb_padstack.data.get_pad_parameters(self.layer_name, self.int_to_pad_type(self.pad_type))
        return pad_values[5]

    @rotation.setter
    def rotation(self, rotation_value):
        self._update_pad_parameters_parameters(rotation=rotation_value)

    @pyedb_function_handler()
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
        new_padstack_def_data = self._edb.definition.PadstackDefData(self._edb_padstack.data)
        if not pad_type:
            pad_type = self.pad_type
        if not geom_type:
            geom_type = self.geometry_type
        if params:
            params = self._pad_parameter_value[2]
        if not offsetx:
            offsetx = self.offset_x
        if not offsety:
            offsety = self.offset_y
        if not rotation:
            rotation = self.rotation
        if not layer_name:
            layer_name = self.layer_name

        new_padstack_def_data.set_pad_parameters(
            layer_name,
            pad_type.value,
            geom_type.value,
            params,
            utility.Value(offsetx),
            utility.Value(offsety),
            utility.Value(rotation),
        )
        self._edb_padstack.SetData(new_padstack_def_data)


class EDBPadstack(object):
    """Manages EDB functionalities for a padstack.

    Parameters
    ----------
    edb_padstack :

    ppadstack : str
        Inherited AEDT object.

    Examples
    --------
    >>> from src.pyedb.grpc.edb import Edb
    >>> edb = Edb(myedb, edbversion="2024.1")
    >>> edb_padstack = edb.padstacks.definitions["MyPad"]
    """

    def __init__(self, edb_padstack, ppadstack):
        self.edb_padstack = edb_padstack
        self._ppadstack = ppadstack
        self.pad_by_layer = {}
        self.antipad_by_layer = {}
        self.thermalpad_by_layer = {}
        self._bounding_box = []
        self._hole_params = None
        for layer in self.via_layers:
            self.pad_by_layer[layer] = EDBPadProperties(edb_padstack, layer, 0, self)
            self.antipad_by_layer[layer] = EDBPadProperties(edb_padstack, layer, 1, self)
            self.thermalpad_by_layer[layer] = EDBPadProperties(edb_padstack, layer, 2, self)

    @property
    def name(self):
        """Padstack Definition Name."""
        return self.edb_padstack.GetName()

    @property
    def _stackup_layers(self):
        return self._ppadstack._stackup_layers

    @property
    def _edb(self):
        return self._ppadstack._edb

    @property
    def via_layers(self):
        """Layers.

        Returns
        -------
        list
            List of layers.
        """
        return self.edb_padstack.data.layer_names

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
    def hole_parameters(self):
        """Hole parameters.

        Returns
        -------
        list
            List of the hole parameters.
        """
        return self.edb_padstack.data.get_hole_parameters()

    @pyedb_function_handler()
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
        new_padsatck_def_data = self._edb.definition.PadstackDefData(self.edb_padstack.data)
        if not hole_type:
            hole_type = self.hole_type
        if not params:
            params = self.hole_parameters
        if not offsetx:
            offsetx = self.hole_offset_x
        if not offsety:
            offsety = self.hole_offset_y
        if not rotation:
            rotation = self.hole_rotation
        new_padsatck_def_data.set_hole_parameters(
            hole_type,
            params,
            utility.Value(offsetx),
            utility.Value(offsety),
            utility.Value(rotation),
        )
        self.edb_padstack.SetData(new_padsatck_def_data)

    @property
    def hole_properties(self):
        """Hole properties.

        Returns
        -------
        list
            List of float values for hole properties.
        """
        self._hole_properties = [i.value for i in self.hole_parameters]
        return self._hole_properties

    @hole_properties.setter
    def hole_properties(self, propertylist):
        if not isinstance(propertylist, list):
            propertylist = [utility.Value(propertylist)]
        else:
            propertylist = [utility.Value(i) for i in propertylist]
        self._update_hole_parameters(params=propertylist)

    @property
    def hole_type(self):
        """Hole type.

        Returns
        -------
        int
            Type of the hole.
        """
        self._hole_type = self.hole_parameters
        return self._hole_type

    @property
    def hole_offset_x(self):
        """Hole offset for the X axis.

        Returns
        -------
        str
            Hole offset value for the X axis.
        """
        self._hole_offset_x = self.hole_parameters[3]
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
        self._hole_offset_y = self.hole_parameters[4]
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
        self._hole_rotation = self.hole_parameters[5]
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
        return self._edb.definition.PadstackDefData(self.edb_padstack.data.plating_percentage)

    @hole_plating_ratio.setter
    def hole_plating_ratio(self, ratio):
        new_padstack_def_data = self._edb.definition.PadstackDefData(self.edb_padstack.data)
        new_padstack_def_data.plating_percentage = utility.Value(ratio)
        self.edb_padstack.data = new_padstack_def_data

    @property
    def hole_plating_thickness(self):
        """Hole plating thickness.

        Returns
        -------
        float
            Thickness of the hole plating if present.
        """
        if len(self.hole_properties) > 0:
            return (self.hole_properties[0] * self.hole_plating_ratio / 100) / 2
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
        hr = 200 * value / self.hole_properties[0]
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
        return self.edb_padstack.data.material

    @material.setter
    def material(self, materialname):
        new_padstack_def_data = self._edb.definition.PadstackDefData(self.edb_padstack.data)
        new_padstack_def_data.material = materialname
        self.edb_padstack.data = new_padstack_def_data

    @property
    def padstack_instances(self):
        """Get all the padstack instances that belongs to active padstack definition.

        Returns
        -------
        dict
        """
        return {
            id: via for id, via in self._ppadstack.padstack_instances.items() if via.padstack_definition == self.name
        }

    @property
    def hole_range(self):
        """Get hole range value from padstack definition.

        Returns
        -------
        str
            Possible returned values are ``"through"``, ``"begin_on_upper_pad"``,
            ``"end_on_lower_pad"``, ``"upper_pad_to_lower_pad"``, and ``"undefined"``.
        """
        cloned_padstackdef_data = self._edb.definition.PadstackDefData(self.edb_padstack.data)
        hole_range_type = int(cloned_padstackdef_data.hole_range)
        if hole_range_type == 0:  # pragma no cover
            return "through"
        elif hole_range_type == 1:  # pragma no cover
            return "begin_on_upper_pad"
        elif hole_range_type == 2:  # pragma no cover
            return "end_on_lower_pad"
        elif hole_range_type == 3:  # pragma no cover
            return "upper_pad_to_lower_pad"
        else:  # pragma no cover
            return "undefined"

    @hole_range.setter
    def hole_range(self, value):
        if isinstance(value, str):  # pragma no cover
            cloned_padstackdef_data = self._edb.definition.PadstackDefData(self.edb_padstack.data)
            if value == "through":  # pragma no cover
                cloned_padstackdef_data.SetHoleRange(self._edb.definition.PadstackHoleRange.THROUGH)
            elif value == "begin_on_upper_pad":  # pragma no cover
                cloned_padstackdef_data.SetHoleRange(self._edb.definition.PadstackHoleRange.BEGIN_ON_UPPER_PAD)
            elif value == "end_on_lower_pad":  # pragma no cover
                cloned_padstackdef_data.SetHoleRange(self._edb.definition.PadstackHoleRange.END_ON_LOWER_PAD)
            elif value == "upper_pad_to_lower_pad":  # pragma no cover
                cloned_padstackdef_data.SetHoleRange(self._edb.definition.PadstackHoleRange.UPPER_PAD_TO_LOWER_PAD)
            else:  # pragma no cover
                return
            self.edb_padstack.data = cloned_padstackdef_data

    @pyedb_function_handler()
    def convert_to_3d_microvias(self, convert_only_signal_vias=True, hole_wall_angle=15):
        """Convert actual padstack instance to microvias 3D Objects with a given aspect ratio.

        Parameters
        ----------
        convert_only_signal_vias : bool, optional
            Either to convert only vias belonging to signal nets or all vias. Defaults is ``True``.
        hole_wall_angle : float, optional
            Angle of laser penetration in deg. It will define the bottom hole diameter with the following formula:
            HoleDiameter -2*tan(laser_angle* Hole depth). Hole depth is the height of the via (dielectric thickness).
            The default value is ``15``.
            The bottom hole will be ``0.75*HoleDepth/HoleDiam``.

        Returns
        -------
        bool
        """
        if self.via_start_layer == self.via_stop_layer:
            self._ppadstack._pedb.logger.error("Microvias cannot be applied when Start and Stop Layers are the same.")
        layout = self._ppadstack._pedb.active_layout
        layers = self._ppadstack._pedb.stackup.signal_layers
        layer_names = [i for i in list(layers.keys())]
        if convert_only_signal_vias:
            signal_nets = [i for i in list(self._ppadstack._pedb.nets.signal_nets.keys())]
        topl, topz, bottoml, bottomz = self._ppadstack._pedb.stackup.stackup_limits(True)
        start_elevation = layers[self.via_start_layer].lower_elevation
        diel_thick = abs(start_elevation - layers[self.via_stop_layer].upper_elevation)
        rad1 = self.hole_properties[0] / 2
        rad2 = self.hole_properties[0] / 2 - math.tan(hole_wall_angle * diel_thick * math.pi / 180)

        if start_elevation < (topz + bottomz) / 2:
            rad1, rad2 = rad2, rad1
        i = 0
        for via in list(self.padstack_instances.values()):
            if convert_only_signal_vias and via.net_name in signal_nets or not convert_only_signal_vias:
                pos = via.position
                started = False
                if len(self.pad_by_layer[self.via_start_layer].parameters) == 0:
                    self._edb.cell.primitive.polygon.create(
                        layout,
                        self.via_start_layer,
                        via._edb_padstackinstance.GetNet(),
                        self.pad_by_layer[self.via_start_layer].polygon_data,
                    )
                else:
                    self._edb.cell.primitive.circle.create(
                        layout,
                        self.via_start_layer,
                        via._edb_padstackinstance.GetNet(),
                        utility.Value(pos[0]),
                        utility.Value(pos[1]),
                        utility.Value(self.pad_by_layer[self.via_start_layer].parameters_values[0] / 2),
                    )
                if len(self.pad_by_layer[self.via_stop_layer].parameters) == 0:
                    self._edb.cell.primitive.polygon.create(
                        layout,
                        self.via_stop_layer,
                        via._edb_padstackinstance.net,
                        self.pad_by_layer[self.via_stop_layer].polygon_data,
                    )
                else:
                    self._edb.cell.primitive.circle.create(
                        layout,
                        self.via_stop_layer,
                        via._edb_padstackinstance.net,
                        utility.Value(pos[0]),
                        utility.Value(pos[1]),
                        utility.Value(self.pad_by_layer[self.via_stop_layer].parameters_values[0] / 2),
                    )
                for layer_name in layer_names:
                    stop = ""
                    if layer_name == via.start_layer or started:
                        start = layer_name
                        stop = layer_names[layer_names.index(layer_name) + 1]
                        cloned_circle = self._edb.cell.primitive.circle.create(
                            layout,
                            start,
                            via._edb_padstackinstance.net,
                            utility.Value(pos[0]),
                            utility.Value(pos[1]),
                            utility.Value(rad1),
                        )
                        cloned_circle2 = self._edb.cell.primitive.circle.create(
                            layout,
                            stop,
                            via._edb_padstackinstance.net,
                            utility.Value(pos[0]),
                            utility.Value(pos[1]),
                            utility.Value(rad2),
                        )
                        s3d = self._edb.cell.hierarchy._hierarchy.Structure3D.create(
                            layout, generate_unique_name("via3d_" + via.aedt_name.replace("via_", ""), n=3)
                        )
                        s3d.add_member(cloned_circle.prim_obj)
                        s3d.add_member(cloned_circle2.prim_obj)
                        s3d.set_material(self.material)
                        s3d.mesh_closure = hierachy.MeshClosure.ENDS_CLOSED
                        started = True
                        i += 1
                    if stop == via.stop_layer:
                        break
                via.delete()
        self._ppadstack._pedb.logger.info("{} Converted successfully to 3D Objects.".format(i))
        return True

    @pyedb_function_handler()
    def split_to_microvias(self):
        """Convert actual padstack definition to multiple microvias definitions.

        Returns
        -------
        List of :class:`pyaedt.edb_core.padstackEDBPadstack`
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
        p1 = self.edb_padstack.data
        new_instances = []
        for layer_name in layer_names:
            stop = ""
            if layer_name == self.via_start_layer or started:
                start = layer_name
                stop = layer_names[layer_names.index(layer_name) + 1]
                new_padstack_name = "MV_{}_{}_{}".format(self.name, start, stop)
                included = [start, stop]
                new_padstack_definition_data = self._ppadstack._pedb.edb_api.definition.PadstackDefData.create()
                new_padstack_definition_data.add_layers(included)
                for layer in included:
                    pl = self.pad_by_layer[layer]
                    new_padstack_definition_data.set_pad_parameters(
                        layer,
                        definition.PadType.REGULAR_PAD,
                        pl.geometry_type.value,
                        list(
                            pl._edb_padstack.data.get_pad_parameters(
                                pl.layer_name, pl.pad_type.value
                            )
                        )[2],
                        pl._edb_padstack.data.get_pad_parameters(
                            pl.layer_name, pl.pad_type.value
                        )[3],
                        pl._edb_padstack.data.get_pad_parameters(
                            pl.layer_name, pl.pad_type.value
                        )[4],
                        pl._edb_padstack.data.get_pad_parameters(
                            pl.layer_name, pl.pad_type.value
                        )[5],
                    )
                    pl = self.antipad_by_layer[layer]
                    new_padstack_definition_data.set_pad_parameters(
                        layer,
                        definition.PadType.ANTI_PAD,
                        pl.geometry_type.value,
                        list(
                            pl._edb_padstack.data.get_pad_parameters(
                                pl.layer_name, pl.pad_type.value
                            )
                        )[2],
                        pl._edb_padstack.data.get_pad_parameters(
                            pl.layer_name, pl.pad_type.value
                        )[3],
                        pl._edb_padstack.data.get_pad_parameters(
                            pl.layer_name, pl.pad_type.value
                        )[4],
                        pl._edb_padstack.data.get_pad_parameters(
                            pl.layer_name, pl.pad_type.value
                        )[5],
                    )
                    pl = self.thermalpad_by_layer[layer]
                    new_padstack_definition_data.SetPadParameters(
                        layer,
                        definition.PadType.THERMAL_PAD,
                        pl.geometry_type.value,
                        list(
                            pl._edb_padstack.data.get_pad_parameters(
                                pl.layer_name, pl.pad_type.value
                            )
                        )[2],
                        pl._edb_padstack.data.get_pad_parameters(
                            pl.layer_name, pl.pad_type.value
                        )[3],
                        pl._edb_padstack.data.get_pad_parameters(
                            pl.layer_name, pl.pad_type.value
                        )[4],
                        pl._edb_padstack.data.get_pad_parameters(
                            pl.layer_name, pl.pad_type.value
                        )[5],
                    )
                new_padstack_definition_data.set_hole_parameters(
                    self.hole_type,
                    self.hole_parameters,
                    utility.Value(self.hole_offset_x),
                    utility.Value(self.hole_offset_y),
                    utility.Value(self.hole_rotation),
                )
                new_padstack_definition_data.material = self.material
                new_padstack_definition_data.plating_percent(utility.Value(self.hole_plating_ratio))
                padstack_definition = self._edb.definition.PadstackDef.create(
                    self._ppadstack._pedb.active_db, new_padstack_name
                )
                padstack_definition.data = new_padstack_definition_data
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
                    if l.name == list(instance.data.layer_names)[0]
                ][0]
                to_layer = [
                    l
                    for l in self._ppadstack._pedb.stackup._edb_layer_list
                    if l.name == list(instance.data.layer_names())[-1]
                ][0]
                padstack_instance = self._edb.cell.primitive.padstack_instance.create(
                    layout,
                    via._edb_padstackinstance.net,
                    generate_unique_name(instance.name),
                    instance,
                    via._edb_padstackinstance.get_position_and_rotation()[1],
                    via._edb_padstackinstance.get_position_and_rotation()[2],
                    from_layer,
                    to_layer,
                    None,
                    None,
                )
                padstack_instance.is_layout_pin = via.is_pin
                i += 1
            via.delete()
        self._ppadstack._pedb.logger.info("Created {} new microvias.".format(i))
        return new_instances


class EDBPadstackInstance(EDBPrimitivesMain):
    """Manages EDB functionalities for a padstack.

    Parameters
    ----------
    edb_padstackinstance :

    _pedb :
        Inherited AEDT object.

    Examples
    --------
    >>> from src.pyedb.grpc.edb import Edb
    >>> edb = Edb(myedb, edbversion="2021.2")
    >>> edb_padstack_instance = edb.padstacks.instances[0]
    """

    def __init__(self, edb_padstackinstance, _pedb):
        super().__init__(edb_padstackinstance, _pedb)
        self._edb_padstackinstance = self._edb_object
        self._pedb = _pedb
        #self._edb_padstackinstance = edb_padstackinstance
        self._bounding_box = []
        self._object_instance = None
        self._position = []
        self._pdef = None

    @property
    def terminal(self):
        """Return PadstackInstanceTerminal object."""

        term = PadstackInstanceTerminal(self._pedb, self._edb_padstackinstance.get_padstack_instance_terminal())
        if not term.is_null:
            return term

    @property
    def component(self):
        """Return Padstack Instance Component"""
        return self._app.components.instances[self._edb_padstackinstance.component.name]

    @pyedb_function_handler
    def _create_terminal(self, name=None):
        """Create a padstack instance terminal"""

        term = PadstackInstanceTerminal(self._pedb, self._edb_padstackinstance.get_padstack_instance_terminal())
        return term.create(self, name)

    @pyedb_function_handler
    def create_coax_port(self, name=None, radial_extent_factor=0):
        """Create a coax port."""
        from ports import CoaxPort

        term = self._create_terminal(name)
        coax = CoaxPort(self._pedb, term._edb_object)
        coax.radial_extent_factor = radial_extent_factor
        return coax

    @property
    def _em_properties(self):
        """Get EM properties."""
        default = (
            r"$begin 'EM properties'\n"
            r"\tType('Mesh')\n"
            r"\tDataId='EM properties1'\n"
            r"\t$begin 'Properties'\n"
            r"\t\tGeneral=''\n"
            r"\t\tModeled='true'\n"
            r"\t\tUnion='true'\n"
            r"\t\t'Use Precedence'='false'\n"
            r"\t\t'Precedence Value'='1'\n"
            r"\t\tPlanarEM=''\n"
            r"\t\tRefined='true'\n"
            r"\t\tRefineFactor='1'\n"
            r"\t\tNoEdgeMesh='false'\n"
            r"\t\tHFSS=''\n"
            r"\t\t'Solve Inside'='false'\n"
            r"\t\tSIwave=''\n"
            r"\t\t'DCIR Equipotential Region'='false'\n"
            r"\t$end 'Properties'\n"
            r"$end 'EM properties'\n"
        )

        pid = database.ProductIdType.DESIGNER
        p = self._edb_padstackinstance.get_product_property(pid, 18)
        if p:
            return p
        else:
            return default

    @_em_properties.setter
    def _em_properties(self, em_prop):
        """Set EM properties"""
        pid = database.ProductIdType.DESIGNER
        self._edb_padstackinstance.set_product_property(pid, 18, em_prop)

    @property
    def dcir_equipotential_region(self):
        """Check whether dcir equipotential region is enabled.

        Returns
        -------
        bool
        """
        pass # not working with grpc
        #pattern = r"'DCIR Equipotential Region'='([^']+)'"
        #em_pp = self._em_properties
        #result = re.search(pattern, em_pp).group(1)
        #if result == "true":
        #    return True
        #else:
        #    return False

    @dcir_equipotential_region.setter
    def dcir_equipotential_region(self, value):
        """Set dcir equipotential region."""
        pp = r"'DCIR Equipotential Region'='true'" if value else r"'DCIR Equipotential Region'='false'"
        em_pp = self._em_properties
        pattern = r"'DCIR Equipotential Region'='([^']+)'"
        new_em_pp = re.sub(pattern, pp, em_pp)
        self._em_properties = new_em_pp

    @property
    def object_instance(self):
        """Return Ansys.Ansoft.Edb.LayoutInstance.LayoutObjInstance object."""
        if not self._object_instance:
            self._object_instance = (
                self._edb_padstackinstance.layout.layout_instance.get_layout_obj_instance_in_context(self._edb_padstackinstance, None)
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
        bbox = self.object_instance.get_bbox().points
        self._bounding_box = [
            [bbox[0].x.value, bbox[0].y.value],
            [bbox[1].x.value, bbox[1].y.value],
        ]
        return self._bounding_box

    @pyedb_function_handler()
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
        int_val = 1 if polygon_data.is_inside(geometry.PointData(*pos)) else 0
        if int_val == 0:
            return False

        if simple_check:
            # pos = [i for i in self.position]
            # int_val = 1 if polygon_data.PointInPolygon(self._pedb.point_data(*pos)) else 0
            return True
        else:
            plane = self._pedb.modeler.Shape("rectangle", pointA=self.bounding_box[0], pointB=self.bounding_box[1])
            rectangle_data = self._pedb.modeler.shape_to_polygon_data(plane)
            int_val = polygon_data.tntersection_type(rectangle_data)
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
        """Return Edb padstack object."""
        return self._edb_padstackinstance

    @property
    def padstack_definition(self):
        """Padstack definition.

        Returns
        -------
        str
            Name of the padstack definition.
        """
        self._pdef = self._edb_padstackinstance.padstack_def.name
        return self._pdef

    @property
    def backdrill_top(self):
        """Backdrill layer from top.

        Returns
        -------
        tuple
            Tuple of the layer name, drill diameter, and offset if it exists.
        """
        if not self._edb_padstackinstance.get_back_drill_type(True).value == 0:
            flag, drill_to_layer, offset, diameter = self._edb_padstackinstance.get_back_drill_by_layer()
            if flag:
                if offset.value:
                    return drill_to_layer.name, diameter.value, offset.value
                else:
                    return drill_to_layer.name, diameter.value
        return False

    def set_backdrill_top(self, drill_depth, drill_diameter, offset=0.0, from_bottom=True):
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
        from_bottom : bool
            ``True`` back drill starts from bottom ``True`` from top. Default value is ``False``.

        Returns
        -------
        bool
            True if success, False otherwise.
        """
        layer = self._pedb.stackup.layers[drill_depth]._edb_layer
        val = utility.Value(drill_diameter)
        offset = utility.Value(offset)
        if offset.value:
            return self._edb_padstackinstance.set_back_drill_by_layer(drill_to_layer=layer,
                                                                      offset=offset,
                                                                      diameter=val,
                                                                      from_bottom=from_bottom)
        else:
            return self._edb_padstackinstance.set_back_drill_by_layer(layer, val, False)

    @property
    def backdrill_bottom(self):
        """Backdrill layer from bottom.

        Returns
        -------
        tuple
            Tuple of the layer name, drill diameter, and drill offset if it exists.
        """
        if not self._edb_padstackinstance.get_back_drill_type(True).value == 0:
            back_drill = self._edb_padstackinstance.get_back_drill_by_layer(True)
            drill_to_layer = back_drill[0]
            offset = back_drill[1]
            diameter = back_drill[2]
            if offset.value:
                return drill_to_layer, diameter.value, offset.value
            else:
                return drill_to_layer.name, diameter.value
        return False


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
        val = utility.Value(drill_diameter)
        offset = utility.Value(offset)
        if offset.value:
            return self._edb_padstackinstance.set_back_drill_parameters(layer, offset, val, True)
        else:
            return self._edb_padstackinstance.set_bBack_drillParameters(layer, val, True)

    @property
    def start_layer(self):
        """Starting layer.

        Returns
        -------
        str
            Name of the starting layer.
        """
        start_layer = self.primitive_object.get_layer_range()[0]
        if start_layer:
            return start_layer.name
        return None

    @start_layer.setter
    def start_layer(self, layer_name):
        stop_layer = self._pedb.stackup.signal_layers[self.stop_layer]._edb_layer
        layer = self._pedb.stackup.signal_layers[layer_name]._edb_layer
        self.primitive_object.set_layer_range(layer, stop_layer)

    @property
    def stop_layer(self):
        """Stopping layer.

        Returns
        -------
        str
            Name of the stopping layer.
        """
        stop_layer = self.primitive_object.get_layer_range()[1]
        if stop_layer:
            return stop_layer.name
        return None

    @stop_layer.setter
    def stop_layer(self, layer_name):
        start_layer = self._pedb.stackup.signal_layers[self.start_layer]._edb_layer
        layer = self._pedb.stackup.signal_layers[layer_name]._edb_layer
        self.primitive_object.set_layer_range(start_layer, layer)

    @property
    def layer_range_names(self):
        """List of all layers to which the padstack instance belongs."""
        layer_range = self.primitive_object.get_layer_range()
        return [layer_range[0].name, layer_range[1].name]

    @property
    def net_name(self):
        """Net name.

        Returns
        -------
        str
            Name of the net.
        """
        return self.primitive_object.net.name

    @net_name.setter
    def net_name(self, val):
        if not isinstance(val, str):
            try:
                self.primitive_object.net = val.net_obj
            except:
                raise AttributeError("Value inserted not found. Input has to be net name or net object.")
        elif val in self._pedb.nets.netlist:
            net = self._pedb.nets.nets[val].net_object
            self.primitive_object.net = net
        else:
            raise AttributeError("Value inserted not found. Input has to be net name or net object.")

    @property
    def is_pin(self):
        """Determines whether this padstack instance is a layout pin.

        Returns
        -------
        bool
            True if this padstack type is a layout pin, False otherwise.
        """
        return self.primitive_object.is_layout_pin

    @is_pin.setter
    def is_pin(self, pin):
        """Set padstack type

        Parameters
        ----------
        pin : bool
            True if set this padstack instance as pin, False otherwise
        """
        if isinstance(pin, bool):
            self.primitive_object.is_layout_pin = pin

    @property
    def position(self):
        """Padstack instance position.

        Returns
        -------
        list
            List of ``[x, y]``` coordinates for the padstack instance position.
        """
        self._position = []
        out = self._edb_padstackinstance.get_position_and_rotation()
        if self._edb_padstackinstance.component:
            out2 = self._edb_padstackinstance.component.transform.transform_point(geometry.PointData(out[0], out[1]))
            self._position = [out2[0].value, out2[1].value]
        elif out[0]:
            self._position = [out[0].value, out[1].value]
        return self._position

    @position.setter
    def position(self, value):
        pos = []
        for v in value:
            if isinstance(v, (float, int, str)):
                pos.append(utility.Value(v))
            else:
                pos.append(v)
        point_data = self._pedb.edb_api.geometry.point_data(pos[0], pos[1])
        self._edb_padstackinstance.set_position_and_rotation(point_data, utility.Value(self.rotation))

    @property
    def rotation(self):
        """Padstack instance rotation.

        Returns
        -------
        float
            Rotation value for the padstack instance.
        """
        out = self._edb_padstackinstance.get_position_and_rotation()
        return out[2].value

    @property
    def name(self):
        """Padstack Instance Name. If it is a pin, the syntax will be like in AEDT ComponentName-PinName."""
        if self.is_pin:
            comp_name = self._edb_padstackinstance.component.name
            pin_name = self._edb_padstackinstance.name
            return "-".join([comp_name, pin_name])
        else:
            return self._edb_padstackinstance.name

    @name.setter
    def name(self, value):
        self._edb_padstackinstance.name = value
        self._edb_padstackinstance.set_product_property(database.ProductIdType.DESIGNER, 11, value)

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
            except:  # pragma no cover
                pass
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
        return self._edb_padstackinstance.name

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

        >>> from src.pyedb.grpc.edb import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edbapp.padstacks.instances[111].get_aedt_pin_name()

        """
        return self._edb_padstackinstance.get_product_property(database.ProductIdType.DESIGNER, 11).strip("'")

    @pyedb_function_handler()
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

    @pyedb_function_handler()
    def delete_padstack_instance(self):
        """Delete this padstack instance.

        .. deprecated:: 0.6.28
           Use :func:`delete` property instead.
        """
        warnings.warn("`delete_padstack_instance` is deprecated. Use `delete` instead.", DeprecationWarning)
        self._edb_padstackinstance.delete()
        return True

    @pyedb_function_handler()
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
        x_pos = utility.Value(self.position[0])
        y_pos = utility.Value(self.position[1])
        point_data = self._pedb.modeler._edb.geometry.point_data(x_pos, y_pos)

        voids = []
        for prim in self._pedb.modeler.get_primitives(net_name, layer_name, is_void=True):
            if prim.primitive_object.polygon_data.in_polygon(point_data):
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
        return self._edb_padstackinstance.pin_groups

    @property
    def placement_layer(self):
        """Placement layer.

        Returns
        -------
        str
            Name of the placement layer.
        """
        return self._edb_padstackinstance.group.placement_layer.name

    @property
    def lower_elevation(self):
        """Lower elevation of the placement layer.

        Returns
        -------
        float
            Lower elavation of the placement layer.
        """
        return self._edb_padstackinstance.group.placement_layer.lower_elevation.value

    @property
    def upper_elevation(self):
        """Upper elevation of the placement layer.

        Returns
        -------
        float
           Upper elevation of the placement layer.
        """
        return self._edb_padstackinstance.group.placement_layer.upper_elevation.value

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
        return self._edb_padstackinstance.group.placement_layer.top_bottom_association.value

    @pyedb_function_handler()
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
        bool, List,  :class:`pyaedt.edb_core.edb_data.primitives.EDBPrimitives`
            Polygon when successful, ``False`` when failed, list of list if `return_points=True`.

        Examples
        --------
        >>> from src.pyedb.grpc.edb import Edb
        >>> edbapp = Edb("myaedbfolder", edbversion="2021.2")
        >>> edb_layout = edbapp.modeler
        >>> list_of_padstack_instances = list(edbapp.padstacks.instances.values())
        >>> padstack_inst = list_of_padstack_instances[0]
        >>> padstack_inst.create_rectangle_in_pad("TOP")
        """

        padstack_center = self.position
        rotation = self.rotation  # in radians
        padstack_name = self.padstack_definition
        try:
            padstack = self._pedb.padstacks.definitions[padstack_name]
        except KeyError:  # pragma: no cover
            return False
        try:
            padstack_pad = padstack.pad_by_layer[layer_name]
        except KeyError:  # pragma: no cover
            try:
                padstack_pad = padstack.pad_by_layer[padstack.via_start_layer]
            except KeyError:  # pragma: no cover
                return False

        pad_shape = padstack_pad.geometry_type
        params = padstack_pad.parameters_values
        polygon_data = padstack_pad.polygon_data

        def _rotate(p):
            x = p[0] * math.cos(rotation) - p[1] * math.sin(rotation)
            y = p[0] * math.sin(rotation) + p[1] * math.cos(rotation)
            return [x, y]

        def _translate(p):
            x = p[0] + padstack_center[0]
            y = p[1] + padstack_center[1]
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
            while i < len(polygon_data.points):
                point = polygon_data.points[i]
                i += 1
                if point.is_arc:
                    continue
                else:
                    points.append([point.x.value, point.y.value])
            xpoly, ypoly = zip(*points)
            polygon = [list(xpoly), list(ypoly)]
            rectangles = GeometryOperators.find_largest_rectangle_inside_polygon(
                polygon, partition_max_order=partition_max_order
            )
            rect = rectangles[0]
            for i in range(4):
                rect[i] = _translate(_rotate(rect[i]))

        if rect is None or len(rect) != 4:
            return False
        path = self._pedb.modeler.Shape("polygon", points=rect)
        pdata = self._pedb.modeler.shape_to_polygon_data(path)
        new_rect = []
        for point in pdata.Points:
            p_transf = self._edb_padstackinstance.component.transform.transform_point(point)
            new_rect.append([p_transf.x.value, p_transf.y.value])
        if return_points:
            return new_rect
        else:
            path = self._pedb.modeler.Shape("polygon", points=new_rect)
            created_polygon = self._pedb.modeler.create_polygon(path, layer_name)
            return created_polygon

    @pyedb_function_handler()
    def get_connected_object_id_set(self):
        """Produce a list of all geometries physically connected to a given layout object.

        Returns
        -------
        list
            Found connected objects IDs with Layout object.
        """
        layout_inst = self._edb_padstackinstance.layout.layout_instance
        layout_bbj_inst = self.object_instance
        return [loi.layout_obj.id for loi in layout_inst.get_connected_objects(layout_bbj_inst).Items]

    @pyedb_function_handler()
    def _get_connected_object_obj_set(self):
        layout_inst = self._edb_padstackinstance.layout.layout_instance
        layout_bbj_inst = self.object_instance
        return [loi.layout_obj for loi in layout_inst.get_connected_objects(layout_bbj_inst).Items]

    @pyedb_function_handler()
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
            List of :class:`pyaedt.edb_core.edb_data.padstacks_data.EDBPadstackInstance`.

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
