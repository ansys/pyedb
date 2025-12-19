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

import math
import warnings

from ansys.edb.core.definition.padstack_def import PadstackDef as GrpcPadstackDef
from ansys.edb.core.definition.padstack_def_data import (
    PadGeometryType as GrpcPadGeometryType,
    PadstackHoleRange as GrpcPadstackHoleRange,
    PadType as GrpcPadType,
)
import ansys.edb.core.geometry.polygon_data
from ansys.edb.core.geometry.polygon_data import PolygonData as GrpcPolygonData
from ansys.edb.core.hierarchy.structure3d import MeshClosure as GrpcMeshClosure, Structure3D as GrpcStructure3D
from ansys.edb.core.primitive.circle import Circle as GrpcCircle

from pyedb.generic.general_methods import generate_unique_name
from pyedb.grpc.database.primitive.circle import Circle
from pyedb.grpc.database.utility.value import Value


class PadProperties:
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
    def _stackup_layers(self):
        return self._pedbpadstack._stackup_layers

    @property
    def _edb(self):
        return self._pedbpadstack._edb

    @property
    def _pad_parameter_value(self):
        p_val = self._edb_padstack.get_pad_parameters(self.layer_name, GrpcPadType.REGULAR_PAD)
        if isinstance(p_val[0], ansys.edb.core.geometry.polygon_data.PolygonData):
            p_val = [GrpcPadGeometryType.PADGEOMTYPE_POLYGON] + [i for i in p_val]
        return p_val

    @property
    def geometry_type(self) -> float:
        """Geometry type.

        Returns
        -------
        int
            Type of the geometry.
        """
        return self._pad_parameter_value[0].value

    @property
    def _edb_geometry_type(self):
        return self._pad_parameter_value[0]

    @property
    def shape(self) -> str:
        """Pad shape.

        Returns
        -------
        str
            pad shape.
        """
        return self._pad_parameter_value[0].name.split("_")[-1].lower()

    @shape.setter
    def shape(self, value: str):
        """Set pad shape.

        Parameters
        ----------
        value : str
            Pad shape.
        """
        if value.lower() == "circle":
            self._update_pad_parameters_parameters(geom_type=GrpcPadGeometryType.PADGEOMTYPE_CIRCLE)
        elif value.lower() == "rectangle":
            self._update_pad_parameters_parameters(geom_type=GrpcPadGeometryType.PADGEOMTYPE_RECTANGLE)
        elif value.lower() == "polygon":
            self._update_pad_parameters_parameters(geom_type=GrpcPadGeometryType.PADGEOMTYPE_POLYGON)
        else:
            raise ValueError(
                f"Unsupported pad shape: {value}. Supported shapes are 'circle', 'rectangle', and 'polygon'."
            )

    @property
    def parameters_values(self):
        """Parameters.

        Returns
        -------
        list
            List of parameters.
        """
        try:
            return [Value(i) for i in self._pad_parameter_value[1]]
        except TypeError:
            return []

    @parameters_values.setter
    def parameters_values(self, value):
        if isinstance(value, (float, str)):
            value = [value]
        self._update_pad_parameters_parameters(params=value)

    @property
    def parameters_values_string(self):
        """Parameters value in string format."""
        try:
            return [str(i) for i in self._pad_parameter_value[1]]
        except TypeError:
            return []

    @property
    def polygon_data(self) -> GrpcPolygonData:
        """Parameters.

        Returns
        -------
        list
            List of parameters.
        """
        p = self._pad_parameter_value[1]
        return p if isinstance(p, ansys.edb.core.geometry.polygon_data.PolygonData) else None

    @property
    def offset_x(self) -> float:
        """Offset for the X axis.

        Returns
        -------
        str
            Offset for the X axis.
        """
        return Value(self._pad_parameter_value[2])

    @property
    def offset_y(self) -> float:
        """Offset for the Y axis.

        Returns
        -------
        str
            Offset for the Y axis.
        """

        return Value(self._pad_parameter_value[3])

    @offset_x.setter
    def offset_x(self, value):
        self._update_pad_parameters_parameters(offsetx=value)

    @offset_y.setter
    def offset_y(self, value):
        self._update_pad_parameters_parameters(offsety=value)

    @property
    def rotation(self) -> float:
        """Rotation.

        Returns
        -------
        str
            Value for the rotation.
        """

        return Value(self._pad_parameter_value[4])

    @rotation.setter
    def rotation(self, value):
        self._update_pad_parameters_parameters(rotation=value)

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
        if layer_name is None:
            layer_name = self.layer_name
        if pad_type is None:
            pad_type = GrpcPadType.REGULAR_PAD
        if geom_type is None:
            geom_type = self.geometry_type
        for k in GrpcPadGeometryType:
            if k.value == geom_type:
                geom_type = k
        if params is None:
            params = self._pad_parameter_value[1]
        elif isinstance(params, list):
            offsetx = [Value(i, self._pedbpadstack._pedb.db) for i in params]
        if rotation is None:
            rotation = self._pad_parameter_value[4]
        elif isinstance(rotation, (str, float, int)):
            rotation = Value(rotation, self._pedbpadstack._pedb.db)
        if offsetx is None:
            offsetx = self._pad_parameter_value[2]
        elif isinstance(offsetx, (str, float, int)):
            offsetx = Value(offsetx, self._pedbpadstack._pedb.db)
        if offsety is None:
            offsety = self._pad_parameter_value[3]
        elif isinstance(offsety, (str, float, int)):
            offsety = Value(offsety, self._pedbpadstack._pedb.db)
        self._edb_padstack.set_pad_parameters(
            layer=layer_name,
            pad_type=pad_type,
            type_geom=geom_type,
            offset_x=Value(offsetx, self._pedbpadstack._pedb.db),
            offset_y=Value(offsety, self._pedbpadstack._pedb.db),
            rotation=Value(rotation, self._pedbpadstack._pedb.db),
            sizes=[Value(i, self._pedbpadstack._pedb.db) for i in params],
        )


class PadstackDef:
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

    def __init__(self, pedb, edb_object):
        self.core = edb_object
        self._pedb = pedb
        self._pad_by_layer = {}
        self._antipad_by_layer = {}
        self._thermalpad_by_layer = {}
        self._bounding_box = []

    @classmethod
    def create(cls, edb, name: str):
        """Create a new padstack definition."""
        padstack_def = GrpcPadstackDef.create(edb.db, name)
        return cls(edb, padstack_def)

    @property
    def instances(self) -> list[any]:
        """Definitions Instances.

        Returns
        -------
        List[:class:`PadstackInstance <pyedb.grpc.database.primitive.padstack_instance.PadstackInstance>`]
            List of PadstackInstance objects.
        """
        return [
            i
            for i in list(self._pedb.padstacks.instances.values())
            if not i.is_null and i.padstack_def.name == self.core.name
        ]

    @property
    def name(self):
        """Padstack definition name."""
        return self.core.name

    @name.setter
    def name(self, value):
        self.core.name = value

    @property
    def data(self):
        """Padstack definition data.

        Returns
        -------
        PadstackDef
            Padstack definition data object.
        """
        return self.core.data

    @data.setter
    def data(self, value):
        self.core.data = value

    @property
    def layers(self) -> list[str]:
        """Layers.

        Returns
        -------
        list[str]
            List of layer names.
        """
        return self.core.data.layer_names

    @property
    def start_layer(self):
        """Starting layer.

        Returns
        -------
        str
            Name of the starting layer.
        """
        return self.layers[0]

    @property
    def via_start_layer(self):
        """Via starting layer.

        .deprecated
        Use: :method:`start_layer <pyedb.grpc.database.definition.padstack_def.PadstackDef.start_layer>`
        instead.

        Returns
        -------
        str
            Name of the via starting layer.
        """
        warnings.warn("via_start_layer is deprecated. Use start_layer instead.", DeprecationWarning)
        return self.start_layer

    @property
    def stop_layer(self):
        """Stopping layer.

        Returns
        -------
        str
            Name of the stopping layer.
        """
        return self.layers[-1]

    @property
    def via_stop_layer(self):
        """Via stop layer.

        .deprecated
        Use :method:`stop_layer <pyedb.grpc.database.definition.padstack_def.PadstackDef.stop_layer>`
        instead.

        Returns
        -------
        str
            Name of the via stop layer.
        """
        warnings.warn("via_stop_layer is deprecated. Use stop_layer instead.", DeprecationWarning)
        return self.stop_layer

    @property
    def material(self):
        """Return hole material name.

        Returns
        -------
        str
            Hole material name.
        """
        return self.core.data.material.value

    @material.setter
    def material(self, value):
        if isinstance(value, str):
            self.core.data.material = value

    @property
    def hole_diameter(self) -> float:
        """Hole diameter.

        Returns
        -------
        float
            Diameter value.

        """
        try:
            hole_parameter = self.core.data.get_hole_parameters()
            if hole_parameter[0].name.lower() == "padgeomtype_circle":
                return Value(hole_parameter[1][0])
        except:
            return 0.0

    @hole_diameter.setter
    def hole_diameter(self, value):
        hole_parameter = self.core.data.get_hole_parameters()
        if not isinstance(value, list):
            value = [Value(value)]
        else:
            value = [Value(p) for p in value]
        hole_size = value
        geometry_type = hole_parameter[0]
        hole_offset_x = hole_parameter[2]
        hole_offset_y = hole_parameter[3]
        if not isinstance(geometry_type, GrpcPolygonData):
            hole_rotation = hole_parameter[4]
            self.core.data.set_hole_parameters(
                offset_x=hole_offset_x,
                offset_y=hole_offset_y,
                rotation=hole_rotation,
                type_geom=geometry_type,
                sizes=hole_size,
            )

    @property
    def hole_type(self) -> float:
        """Holy type.

        Returns
        -------
        float
            hole type.

        """
        return Value(self.core.data.get_hole_parameters()[0])

    @property
    def edb_hole_type(self):
        """EDB hole type.

        Returns
        -------
        str
            Hole type.

        """
        return self.core.data.get_hole_parameters()[0]

    @property
    def hole_offset_x(self) -> float:
        """Hole offset for the X axis.

        Returns
        -------
        float
            Hole offset value for the X axis.
        """
        try:
            return Value(self.core.data.get_hole_parameters()[2])
        except:
            return 0.0

    @hole_offset_x.setter
    def hole_offset_x(self, value):
        hole_parameter = list(self.core.data.get_hole_parameters())
        hole_parameter[2] = Value(value, self._pedb.db)
        self.core.data.set_hole_parameters(
            offset_x=hole_parameter[2],
            offset_y=hole_parameter[3],
            rotation=hole_parameter[4],
            type_geom=hole_parameter[0],
            sizes=hole_parameter[1],
        )

    @property
    def hole_offset_y(self) -> float:
        """Hole offset for the Y axis.

        Returns
        -------
        float
            Hole offset value for the Y axis.
        """
        try:
            return Value(self.core.data.get_hole_parameters()[3])
        except:
            return 0.0

    @hole_offset_y.setter
    def hole_offset_y(self, value):
        hole_parameter = list(self.core.data.get_hole_parameters())
        hole_parameter[3] = Value(value, self._pedb.db)
        self.core.data.set_hole_parameters(
            offset_x=hole_parameter[2],
            offset_y=hole_parameter[3],
            rotation=hole_parameter[4],
            type_geom=hole_parameter[0],
            sizes=hole_parameter[1],
        )

    @property
    def hole_rotation(self) -> float:
        """Hole rotation.

        Returns
        -------
        float
            Value for the hole rotation.
        """
        try:
            return Value(self.core.data.get_hole_parameters()[4])
        except:
            return 0.0

    @hole_rotation.setter
    def hole_rotation(self, value):
        hole_parameter = list(self.core.data.get_hole_parameters())
        hole_parameter[4] = Value(value, self._pedb.db)
        self.core.data.set_hole_parameters(
            offset_x=hole_parameter[2],
            offset_y=hole_parameter[3],
            rotation=hole_parameter[4],
            type_geom=hole_parameter[0],
            sizes=hole_parameter[1],
        )

    @property
    def pad_by_layer(self) -> dict[str, PadProperties]:
        """Pad by layer.

        Returns
        -------
        Dict[str, :class:`PadProperties <pyedb.grpc.database.definition.padstack_def.PadProperties>`]
            Dictionary with layer as key and PadProperties as value.
        """
        if not self._pad_by_layer:
            for layer in self.layers:
                try:
                    self._pad_by_layer[layer] = PadProperties(self.core.data, layer, GrpcPadType.REGULAR_PAD, self)
                except:
                    self._pad_by_layer[layer] = None
        return self._pad_by_layer

    @property
    def antipad_by_layer(self) -> dict[str, PadProperties]:
        """Antipad by layer.

        Returns
        -------
        Dict[str, :class:`PadProperties <pyedb.grpc.database.definition.padstack_def.PadProperties>`]
            Dictionary with layer as key and PadProperties as value.
        """
        if not self._antipad_by_layer:
            for layer in self.layers:
                try:
                    self._pad_by_layer[layer] = PadProperties(self.core.data, layer, GrpcPadType.ANTI_PAD, self)
                except:
                    self._antipad_by_layer[layer] = None
        return self._antipad_by_layer

    @property
    def thermalpad_by_layer(self) -> dict[str, PadProperties]:
        """Thermal by layer.

        Returns
        -------
        Dict[str, :class:`PadProperties <pyedb.grpc.database.definition.padstack_def.PadProperties>`]
            Dictionary with layer as key and PadProperties as value.
        """
        if not self._thermalpad_by_layer:
            for layer in self.layers:
                try:
                    self._pad_by_layer[layer] = PadProperties(self.core.data, layer, GrpcPadType.THERMAL_PAD, self)
                except:
                    self._thermalpad_by_layer[layer] = None
        return self._thermalpad_by_layer

    @property
    def hole_plating_ratio(self) -> float:
        """Hole plating ratio.

        Returns
        -------
        float
            Percentage for the hole plating.
        """
        return Value(self.core.data.plating_percentage)

    @hole_plating_ratio.setter
    def hole_plating_ratio(self, ratio):
        self.core.data.plating_percentage = Value(ratio)

    @property
    def hole_plating_thickness(self) -> float:
        """Hole plating thickness.

        Returns
        -------
         float
            Thickness of the hole plating if present.
        """
        try:
            if len(self.core.data.get_hole_parameters()) > 0:
                return round((self.hole_diameter * self.hole_plating_ratio / 100) / 2, 6)
            else:
                return 0.0
        except:
            return 0.0

    @hole_plating_thickness.setter
    def hole_plating_thickness(self, value):
        """Hole plating thickness.

        Returns
        -------
        float
            Thickness of the hole plating if present.
        """
        hr = 200 * Value(value) / self.hole_diameter
        self.hole_plating_ratio = hr

    @property
    def hole_finished_size(self) -> float:
        """Finished hole size.

        Returns
        -------
        float
            Finished size of the hole (Total Size + PlatingThickess*2).
        """
        try:
            if len(self.core.data.get_hole_parameters()) > 0:
                return round(self.hole_diameter - (self.hole_plating_thickness * 2), 6)
            else:
                return 0.0
        except:
            return 0.0

    @property
    def hole_range(self) -> str:
        """Get hole range value from padstack definition.

        Returns
        -------
        str
            Possible returned values are ``"through"``, ``"begin_on_upper_pad"``,
            ``"end_on_lower_pad"``, ``"upper_pad_to_lower_pad"``, and ``"undefined"``.
        """
        try:
            return self.core.data.hole_range.name.lower()
        except:
            return None

    @hole_range.setter
    def hole_range(self, value):
        if isinstance(value, str):
            if value == "through":
                self.core.data.hole_range = GrpcPadstackHoleRange.THROUGH
            elif value == "begin_on_upper_pad":
                self.core.data.hole_range = GrpcPadstackHoleRange.BEGIN_ON_UPPER_PAD
            elif value == "end_on_lower_pad":
                self.core.data.hole_range = GrpcPadstackHoleRange.END_ON_LOWER_PAD
            elif value == "upper_pad_to_lower_pad":
                self.core.data.hole_range = GrpcPadstackHoleRange.UPPER_PAD_TO_LOWER_PAD
            else:  # pragma no cover
                self.core.data.hole_range = GrpcPadstackHoleRange.UNKNOWN_RANGE

    def convert_to_3d_microvias(
        self, convert_only_signal_vias=True, hole_wall_angle=15, delete_padstack_def=True
    ) -> bool:
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

        if isinstance(self.core.data.get_hole_parameters()[0], GrpcPolygonData):
            self._pedb.logger.error("Microvias cannot be applied on vias using hole shape polygon")
            return False

        if self.start_layer == self.stop_layer:
            self._pedb.logger.error("Microvias cannot be applied when Start and Stop Layers are the same.")
        layout = self._pedb.active_layout
        layers = self._pedb.stackup.signal_layers
        layer_names = [i for i in list(layers.keys())]
        if convert_only_signal_vias:
            signal_nets = [i for i in list(self._pedb._pedb.nets.signal_nets.keys())]
        topl, topz, bottoml, bottomz = self._pedb.stackup.limits(True)
        if self.start_layer in layers:
            start_elevation = layers[self.start_layer].lower_elevation
        else:
            start_elevation = layers[self.instances[0].start_layer].lower_elevation
        if self.stop_layer in layers:
            stop_elevation = layers[self.stop_layer].upper_elevation
        else:
            stop_elevation = layers[self.instances[0].stop_layer].upper_elevation

        diel_thick = abs(start_elevation - stop_elevation)
        if self.hole_diameter:
            rad1 = self.hole_diameter / 2 - math.tan(hole_wall_angle * diel_thick * math.pi / 180)
            rad2 = self.hole_diameter / 2
        else:
            rad1 = 0.0
            rad2 = 0.0

        if start_elevation < (topz + bottomz) / 2:
            rad1, rad2 = rad2, rad1
        i = 0
        for via in self.instances:
            if convert_only_signal_vias and via.net_name in signal_nets or not convert_only_signal_vias:
                pos = via.position
                started = False
                if len(self.pad_by_layer[self.start_layer].parameters_values) == 0:
                    self._pedb.modeler.create_polygon(
                        self.pad_by_layer[self.start_layer].polygon_data,
                        layer_name=self.start_layer,
                        net_name=via.net_name,
                    )
                else:
                    Circle(self._pedb).create(
                        layout,
                        self.start_layer,
                        via.net,
                        Value(pos[0]),
                        Value(pos[1]),
                        Value(self.pad_by_layer[self.start_layer].parameters_values[0] / 2),
                    )
                if len(self.pad_by_layer[self.stop_layer].parameters_values) == 0:
                    self._pedb.modeler.create_polygon(
                        self.pad_by_layer[self.stop_layer].polygon_data,
                        layer_name=self.stop_layer,
                        net_name=via.net_name,
                    )
                else:
                    Circle(self._pedb).create(
                        layout,
                        self.stop_layer,
                        via.net,
                        Value(pos[0]),
                        Value(pos[1]),
                        Value(self.pad_by_layer[self.stop_layer].parameters_values[0] / 2),
                    )
                for layer_name in layer_names:
                    stop = ""
                    if layer_name == via.start_layer or started:
                        start = layer_name
                        stop = layer_names[layer_names.index(layer_name) + 1]
                        cloned_circle = Circle(self._pedb).create(
                            layout,
                            start,
                            via.net,
                            Value(pos[0]),
                            Value(pos[1]),
                            Value(rad1),
                        )
                        cloned_circle2 = Circle(self._pedb).create(
                            layout,
                            stop,
                            via.net,
                            Value(pos[0]),
                            Value(pos[1]),
                            Value(rad2),
                        )
                        s3d = GrpcStructure3D.create(
                            layout.core, generate_unique_name("via3d_" + via.aedt_name.replace("via_", ""), n=3)
                        )
                        s3d.add_member(cloned_circle.core)
                        s3d.add_member(cloned_circle2.core)
                        if not self.core.data.material.value:
                            self._pedb.logger.warning(
                                f"Padstack definution {self.name} has no material defined.Defaulting to copper"
                            )
                            self.data.material = "copper"
                        s3d.set_material(self.core.data.material.value)
                        s3d.mesh_closure = GrpcMeshClosure.ENDS_CLOSED
                        started = True
                        i += 1
                    if stop == via.stop_layer:
                        break
                if delete_padstack_def:  # pragma no cover
                    via.delete()
                else:  # pragma no cover
                    self.hole_diameter = 0.0
                    self._pedb.logger.info("Padstack definition kept, hole size set to 0.")

        self._pedb.logger.info(f"{i} Converted successfully to 3D Objects.")
        return True

    def split_to_microvias(self) -> list[any]:
        """Convert actual padstack definition to multiple microvias definitions.

        Returns
        -------
        List[:class:`PadstackInstance <pyedb.grpc.database.primitive.padstack_instance.PadstackInstance>`]
        """
        from pyedb.grpc.database.primitive.padstack_instance import PadstackInstance

        if self.start_layer == self.stop_layer:
            self._pedb.logger.error("Microvias cannot be applied when Start and Stop Layers are the same.")
        layout = self._pedb.active_layout
        layers = self._pedb.stackup.signal_layers
        layer_names = [i for i in list(layers.keys())]
        if abs(layer_names.index(self.start_layer) - layer_names.index(self.stop_layer)) < 2:
            self._pedb.logger.error(
                "Conversion can be applied only if padstack definition is composed by more than 2 layers."
            )
            return False
        started = False
        new_instances = []
        for layer_name in layer_names:
            stop = ""
            if layer_name == self.start_layer or started:
                start = layer_name
                stop = layer_names[layer_names.index(layer_name) + 1]
                new_padstack_name = f"MV_{self.name}_{start}_{stop}"
                included = [start, stop]
                new_padstack_definition = GrpcPadstackDef.create(self._pedb.db, new_padstack_name)
                new_padstack_definition.data.add_layers(included)
                for layer in included:
                    pl = self.pad_by_layer[layer]
                    new_padstack_definition.data.set_pad_parameters(
                        layer=layer,
                        pad_type=GrpcPadType.REGULAR_PAD,
                        offset_x=Value(pl.offset_x, self._pedb.db),
                        offset_y=Value(pl.offset_y, self._pedb.db),
                        rotation=Value(pl.rotation, self._pedb.db),
                        type_geom=pl._edb_geometry_type,
                        sizes=pl.parameters_values,
                    )
                    antipads = self.antipad_by_layer
                    if layer in antipads:
                        pl = antipads[layer]
                        new_padstack_definition.data.set_pad_parameters(
                            layer=layer,
                            pad_type=GrpcPadType.ANTI_PAD,
                            offset_x=Value(pl.offset_x, self._pedb.db),
                            offset_y=Value(pl.offset_y, self._pedb.db),
                            rotation=Value(pl.rotation, self._pedb.db),
                            type_geom=pl._edb_geometry_type,
                            sizes=pl.parameters_values,
                        )
                    thermal_pads = self.thermalpad_by_layer
                    if layer in thermal_pads:
                        pl = thermal_pads[layer]
                        new_padstack_definition.data.set_pad_parameters(
                            layer=layer,
                            pad_type=GrpcPadType.THERMAL_PAD,
                            offset_x=Value(pl.offset_x, self._pedb.db),
                            offset_y=Value(pl.offset_y, self._pedb.db),
                            rotation=Value(pl.rotation, self._pedb.db),
                            type_geom=pl._edb_geometry_type,
                            sizes=pl.parameters_values,
                        )
                new_padstack_definition.data.set_hole_parameters(
                    offset_x=Value(self.hole_offset_x, self._pedb.db),
                    offset_y=Value(self.hole_offset_y, self._pedb.db),
                    rotation=Value(self.hole_rotation, self._pedb.db),
                    type_geom=self.edb_hole_type,
                    sizes=[self.hole_diameter],
                )
                new_padstack_definition.data.material = self.material
                new_padstack_definition.data.plating_percentage = Value(self.hole_plating_ratio, self._pedb.db)
                new_instances.append(PadstackDef(self._pedb, new_padstack_definition))
                started = True
            if self.stop_layer == stop:
                break
        i = 0
        for via in self.instances:
            for instance in new_instances:
                from_layer = self.core.data.layer_names[0]
                to_layer = self.core.data.layer_names[-1]
                from_layer = next(l for layer_name, l in self._pedb.stackup.layers.items() if l.name == from_layer)
                to_layer = next(l for layer_name, l in self._pedb.stackup.layers.items() if l.name == to_layer)
                padstack_instance = PadstackInstance.create(
                    layout=layout,
                    net=via.net,
                    name=generate_unique_name(instance.name),
                    padstack_definition=instance.name,
                    position_x=via.position[0],
                    position_y=via.position[1],
                    rotation=0.0,
                    top_layer=from_layer,
                    bottom_layer=to_layer,
                    solder_ball_layer=None,
                    layer_map="two_way",
                )
                padstack_instance.is_layout_pin = via.is_pin
                i += 1
            via.delete()
        self._pedb.logger.info("Created {} new microvias.".format(i))
        return new_instances

    # TODO check if update layer name is needed.
