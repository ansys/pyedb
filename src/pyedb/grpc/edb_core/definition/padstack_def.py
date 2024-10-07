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

import math

from ansys.edb.core.definition.padstack_def import PadstackDef as GrpcPadstackDef
from ansys.edb.core.definition.padstack_def_data import (
    PadstackHoleRange as GrpcPadstackHoleRange,
)
from ansys.edb.core.definition.padstack_def_data import PadType as GrpcPadType
from ansys.edb.core.hierarchy.structure3d import MeshClosure as GrpcMeshClosure
from ansys.edb.core.hierarchy.structure3d import Structure3D as GrpcStructure3D
from ansys.edb.core.primitive.primitive import Circle as GrpcCircle
from ansys.edb.core.utility.value import Value as GrpcValue

from pyedb.generic.general_methods import generate_unique_name


class PadstackDef(GrpcPadstackDef):
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
        super().__init__(edb_object.msg)
        self._pedb = pedb
        self._pad_by_layer = {}
        self._antipad_by_layer = {}
        self._thermalpad_by_layer = {}
        self._bounding_box = []

    @property
    def instances(self):
        """Definitions Instances."""
        return [i for i in list(self._pedb.padstacks.instances.values()) if i.padstack_def.name == self.name]

    @property
    def layers(self):
        """Layers.

        Returns
        -------
        list
            List of layers.
        """
        return self.data.layer_names

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
    def stop_layer(self):
        """Stopping layer.

        Returns
        -------
        str
            Name of the stopping layer.
        """
        return self.layers[-1]

    @property
    def hole_diameter(self):
        """Hole diameter."""
        hole_parameter = self.data.get_hole_parameters()
        if hole_parameter[0].name.lower() == "padgeomtype_circle":
            return round(hole_parameter[1][0].value, 6)

    @hole_diameter.setter
    def hole_diameter(self, value):
        hole_parameter = self.data.get_hole_parameters()
        if hole_parameter[0].name.lower() == "padgeomtype_circle":
            hole_parameter[1] = GrpcValue(value)
            self.data.set_hole_parameters(hole_parameter)

    @property
    def hole_offset_x(self):
        """Hole offset for the X axis.

        Returns
        -------
        str
            Hole offset value for the X axis.
        """
        return round(self.data.get_hole_parameters()[2].value, 6)

    @hole_offset_x.setter
    def hole_offset_x(self, value):
        hole_parameter = self.data.get_hole_parameters()
        hole_parameter[2] = GrpcValue(value)
        self.data.set_hole_parameters(hole_parameter)

    @property
    def hole_offset_y(self):
        """Hole offset for the Y axis.

        Returns
        -------
        str
            Hole offset value for the Y axis.
        """
        return round(self.data.get_hole_parameters()[3].value, 6)

    @hole_offset_y.setter
    def hole_offset_y(self, value):
        hole_parameter = self.data.get_hole_parameters()
        hole_parameter[3] = GrpcValue(value)
        self.data.set_hole_parameters(hole_parameter)

    @property
    def hole_rotation(self):
        """Hole rotation.

        Returns
        -------
        str
            Value for the hole rotation.
        """
        return round(self.data.get_hole_parameters()[4].value, 6)

    @hole_rotation.setter
    def hole_rotation(self, value):
        hole_parameter = self.data.get_hole_parameters()
        hole_parameter[4] = GrpcValue(value)
        self.data.set_hole_parameters(hole_parameter)

    @property
    def pad_by_layer(self):
        if not self._pad_by_layer:
            for layer in self.layers:
                try:
                    self._pad_by_layer[layer] = round(
                        self.data.get_pad_parameters(layer, GrpcPadType.REGULAR_PAD)[1][0].value, 6
                    )
                except:
                    self._pad_by_layer[layer] = None
            return self._pad_by_layer

    @property
    def antipad_by_layer(self):
        if not self._antipad_by_layer:
            for layer in self.layers:
                try:
                    self._antipad_by_layer[layer] = round(
                        self.data.get_pad_parameters(layer, GrpcPadType.ANTI_PAD)[1][0].value, 6
                    )
                except:
                    self._antipad_by_layer[layer] = None
            return self._antipad_by_layer

    @property
    def thermalpad_by_layer(self):
        if not self._thermalpad_by_layer:
            for layer in self.layers:
                try:
                    self._thermalpad_by_layer[layer] = round(
                        self.data.get_pad_parameters(layer, GrpcPadType.THERMAL_PAD)[1][0].value, 6
                    )
                except:
                    self._thermalpad_by_layer[layer] = None
            return self._thermalpad_by_layer

    @property
    def hole_plating_ratio(self):
        """Hole plating ratio.

        Returns
        -------
        float
            Percentage for the hole plating.
        """
        return round(self.data.plating_percentage.value, 6)

    @hole_plating_ratio.setter
    def hole_plating_ratio(self, ratio):
        self.data.plating_percentage = GrpcValue(ratio)

    @property
    def hole_plating_thickness(self):
        """Hole plating thickness.

        Returns
        -------
        float
            Thickness of the hole plating if present.
        """
        if len(self.data.get_hole_parameters()) > 0:
            return round((self.hole_diameter * self.hole_plating_ratio / 100) / 2, 6)
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
        hr = 200 * GrpcValue(value).value / self.hole_diameter
        self.hole_plating_ratio = hr

    @property
    def hole_finished_size(self):
        """Finished hole size.

        Returns
        -------
        float
            Finished size of the hole (Total Size + PlatingThickess*2).
        """
        if len(self.data.get_hole_parameters()) > 0:
            return round(self.hole_diameter - (self.hole_plating_thickness * 2), 6)
        else:
            return 0

    @property
    def hole_range(self):
        """Get hole range value from padstack definition.

        Returns
        -------
        str
            Possible returned values are ``"through"``, ``"begin_on_upper_pad"``,
            ``"end_on_lower_pad"``, ``"upper_pad_to_lower_pad"``, and ``"undefined"``.
        """
        return self.data.hole_range.name.lower()

    @hole_range.setter
    def hole_range(self, value):
        if isinstance(value, str):
            if value == "through":
                self.data.hole_range = GrpcPadstackHoleRange.THROUGH
            elif value == "begin_on_upper_pad":
                self.data.hole_range = GrpcPadstackHoleRange.BEGIN_ON_UPPER_PAD
            elif value == "end_on_lower_pad":
                self.data.hole_range = GrpcPadstackHoleRange.END_ON_LOWER_PAD
            elif value == "upper_pad_to_lower_pad":
                self.data.hole_range = GrpcPadstackHoleRange.UPPER_PAD_TO_LOWER_PAD
            else:  # pragma no cover
                self.data.hole_range = GrpcPadstackHoleRange.UNKNOWN_RANGE

    def convert_to_3d_microvias(self, convert_only_signal_vias=True, hole_wall_angle=15, delete_padstack_def=True):
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

        if len(self.data.get_hole_parameters()) == 0:
            self._pedb.logger.error("Microvias cannot be applied on vias using hole shape polygon")
            return False

        if self.start_layer == self.stop_layer:
            self._pedb.logger.error("Microvias cannot be applied when Start and Stop Layers are the same.")
        layout = self._pedb.active_layout
        layers = self._pedb.stackup.signal_layers
        layer_names = [i for i in list(layers.keys())]
        if convert_only_signal_vias:
            signal_nets = [i for i in list(self._pedb._pedb.nets.signal_nets.keys())]
        topl, topz, bottoml, bottomz = self._pedb._pedb.stackup.limits(True)
        if self.start_layer in layers:
            start_elevation = layers[self.start_layer].lower_elevation
        else:
            start_elevation = layers[self.instances[0].start_layer].lower_elevation
        if self.stop_layer in layers:
            stop_elevation = layers[self.stop_layer].upper_elevation
        else:
            stop_elevation = layers[self.instances[0].stop_layer].upper_elevation

        diel_thick = abs(start_elevation - stop_elevation)
        rad1 = self.hole_diameter / 2 - math.tan(hole_wall_angle * diel_thick * math.pi / 180)
        rad2 = self.hole_diameter / 2

        if start_elevation < (topz + bottomz) / 2:
            rad1, rad2 = rad2, rad1
        i = 0
        for via in list(self.padstack_instances.values()):
            if convert_only_signal_vias and via.net_name in signal_nets or not convert_only_signal_vias:
                pos = via.position
                started = False
                if len(self.pad_by_layer[self.start_layer].parameters) == 0:
                    self._pedb.modeler.create_polygon(
                        self.pad_by_layer[self.start_layer].polygon_data,
                        layer_name=self.start_layer,
                        net_name=via.net.name,
                    )
                else:
                    GrpcCircle.create(
                        layout,
                        self.start_layer,
                        via.net,
                        GrpcValue(pos[0]),
                        GrpcValue(pos[1]),
                        GrpcValue(self.pad_by_layer[self.start_layer].parameters_values[0] / 2),
                    )
                if len(self.pad_by_layer[self.stop_layer].parameters) == 0:
                    self._pedb.modeler.create_polygon(
                        self.pad_by_layer[self.stop_layer].polygon_data,
                        layer_name=self.stop_layer,
                        net_name=via.net.name,
                    )
                else:
                    GrpcCircle.create(
                        layout,
                        self.stop_layer,
                        via.net,
                        GrpcValue(pos[0]),
                        GrpcValue(pos[1]),
                        GrpcValue(self.pad_by_layer[self.stop_layer].parameters_values[0] / 2),
                    )
                for layer_name in layer_names:
                    stop = ""
                    if layer_name == via.start_layer or started:
                        start = layer_name
                        stop = layer_names[layer_names.index(layer_name) + 1]
                        cloned_circle = GrpcCircle.create(
                            layout,
                            start,
                            via.net,
                            GrpcValue(pos[0]),
                            GrpcValue(pos[1]),
                            GrpcValue(rad1),
                        )
                        cloned_circle2 = GrpcCircle.create(
                            layout,
                            stop,
                            via.net,
                            GrpcValue(pos[0]),
                            GrpcValue(pos[1]),
                            GrpcValue(rad2),
                        )
                        s3d = GrpcStructure3D.create(
                            layout, generate_unique_name("via3d_" + via.aedt_name.replace("via_", ""), n=3)
                        )
                        s3d.add_member(cloned_circle)
                        s3d.add_member(cloned_circle2)
                        s3d.set_material(self.data.material.value)
                        s3d.mesh_closure = GrpcMeshClosure.ENDS_CLOSED
                        started = True
                        i += 1
                    if stop == via.stop_layer:
                        break
                if delete_padstack_def:  # pragma no cover
                    via.delete()
                else:  # pragma no cover
                    padstack_def = self._pedb.definitions[via.padstack_definition]
                    padstack_def.hole_properties = 0
                    self._pedb.logger.info("Padstack definition kept, hole size set to 0.")

        self._pedb.logger.info(f"{i} Converted successfully to 3D Objects.")
        return True

    def split_to_microvias(self):
        """Convert actual padstack definition to multiple microvias definitions.

        Returns
        -------
        List of :class:`pyedb.dotnet.edb_core.padstackEDBPadstack`
        """
        if self.via_start_layer == self.via_stop_layer:
            self._pedb._pedb.logger.error("Microvias cannot be applied when Start and Stop Layers are the same.")
        layout = self._pedb._pedb.active_layout
        layers = self._pedb._pedb.stackup.signal_layers
        layer_names = [i for i in list(layers.keys())]
        if abs(layer_names.index(self.via_start_layer) - layer_names.index(self.via_stop_layer)) < 2:
            self._pedb._pedb.logger.error(
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
                new_padstack_definition_data = self._pedb._pedb.edb_api.definition.PadstackDefData.Create()
                new_padstack_definition_data.AddLayers(convert_py_list_to_net_list(included))
                for layer in included:
                    pl = self.pad_by_layer[layer]
                    new_padstack_definition_data.SetPadParameters(
                        layer,
                        self._pedb._pedb.edb_api.definition.PadType.RegularPad,
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
                        self._pedb._pedb.edb_api.definition.PadType.AntiPad,
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
                        self._pedb._pedb.edb_api.definition.PadType.ThermalPad,
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
                    self.hole_parameters,
                    self._get_edb_value(self.hole_offset_x),
                    self._get_edb_value(self.hole_offset_y),
                    self._get_edb_value(self.hole_rotation),
                )
                new_padstack_definition_data.SetMaterial(self.material)
                new_padstack_definition_data.SetHolePlatingPercentage(self._get_edb_value(self.hole_plating_ratio))
                padstack_definition = self._edb.definition.PadstackDef.Create(
                    self._pedb._pedb.active_db, new_padstack_name
                )
                padstack_definition.SetData(new_padstack_definition_data)
                new_instances.append(EDBPadstack(padstack_definition, self._pedb))
                started = True
            if self.via_stop_layer == stop:
                break
        i = 0
        for via in list(self.padstack_instances.values()):
            for inst in new_instances:
                instance = inst.edb_padstack
                from_layer = [
                    l
                    for l in self._pedb._pedb.stackup._edb_layer_list
                    if l.GetName() == list(instance.GetData().GetLayerNames())[0]
                ][0]
                to_layer = [
                    l
                    for l in self._pedb._pedb.stackup._edb_layer_list
                    if l.GetName() == list(instance.GetData().GetLayerNames())[-1]
                ][0]
                padstack_instance = self._edb.cell.primitive.padstack_instance.create(
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
                padstack_instance._edb_object.SetIsLayoutPin(via.is_pin)
                i += 1
            via.delete()
        self._pedb._pedb.logger.info("Created {} new microvias.".format(i))
        return new_instances

    # TODO check if update layer name is needed.
