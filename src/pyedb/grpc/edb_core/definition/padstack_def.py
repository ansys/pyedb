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

from ansys.edb.core.definition.package_def import PackageDef as GrpcPackageDef


class PadstackDef(GrpcPackageDef):
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

    def __init__(self, edb_padstack, ppadstack):
        super().__init__(edb_padstack)
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
        pass

    @property
    def instances(self):
        """Definitions Instances."""
        name = self.name
        return [i for i in self._ppadstack.instances.values() if i.padstack_definition == name]

    @property
    def _edb(self):
        return self._ppadstack._edb

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
    def __hole_parameters(self):
        """Hole parameters."""
        return self.data.get_hole_parameters()

    @property
    def hole_diameter(self):
        """Hole diameter."""
        return self.__hole_parameters()[0].bounding_circle()[1].value

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
        newPadstackDefinitionData = self._edb.definition.PadstackDefData(originalPadstackDefinitionData)
        if not hole_type:
            hole_type = self.hole_type
        if not params:
            params = self.hole_parameters
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
        return self._edb.definition.PadstackDefData(self.edb_padstack.GetData()).GetHolePlatingPercentage()

    @hole_plating_ratio.setter
    def hole_plating_ratio(self, ratio):
        originalPadstackDefinitionData = self.edb_padstack.GetData()
        newPadstackDefinitionData = self._edb.definition.PadstackDefData(originalPadstackDefinitionData)
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
        return self.edb_padstack.GetData().GetMaterial()

    @material.setter
    def material(self, materialname):
        originalPadstackDefinitionData = self.edb_padstack.GetData()
        newPadstackDefinitionData = self._edb.definition.PadstackDefData(originalPadstackDefinitionData)
        newPadstackDefinitionData.SetMaterial(materialname)
        self.edb_padstack.SetData(newPadstackDefinitionData)

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
            ``"end_on_lower_pad"``, ``"upper_pad_to_lower_pad"``, and ``"undefined"``.
        """
        cloned_padstackdef_data = self._edb.definition.PadstackDefData(self.edb_padstack.GetData())
        hole_ange_type = int(cloned_padstackdef_data.GetHoleRange())
        if hole_ange_type == 0:  # pragma no cover
            return "through"
        elif hole_ange_type == 1:  # pragma no cover
            return "begin_on_upper_pad"
        elif hole_ange_type == 2:  # pragma no cover
            return "end_on_lower_pad"
        elif hole_ange_type == 3:  # pragma no cover
            return "upper_pad_to_lower_pad"
        else:  # pragma no cover
            return "undefined"

    @hole_range.setter
    def hole_range(self, value):
        if isinstance(value, str):  # pragma no cover
            cloned_padstackdef_data = self._edb.definition.PadstackDefData(self.edb_padstack.GetData())
            if value == "through":  # pragma no cover
                cloned_padstackdef_data.SetHoleRange(self._edb.definition.PadstackHoleRange.Through)
            elif value == "begin_on_upper_pad":  # pragma no cover
                cloned_padstackdef_data.SetHoleRange(self._edb.definition.PadstackHoleRange.BeginOnUpperPad)
            elif value == "end_on_lower_pad":  # pragma no cover
                cloned_padstackdef_data.SetHoleRange(self._edb.definition.PadstackHoleRange.EndOnLowerPad)
            elif value == "upper_pad_to_lower_pad":  # pragma no cover
                cloned_padstackdef_data.SetHoleRange(self._edb.definition.PadstackHoleRange.UpperPadToLowerPad)
            else:  # pragma no cover
                return
            self.edb_padstack.SetData(cloned_padstackdef_data)

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
        topl, topz, bottoml, bottomz = self._ppadstack._pedb.stackup.limits(True)
        if self.via_start_layer in layers:
            start_elevation = layers[self.via_start_layer].lower_elevation
        else:
            start_elevation = layers[self.instances[0].start_layer].lower_elevation
        if self.via_stop_layer in layers:
            stop_elevation = layers[self.via_stop_layer].upper_elevation
        else:
            stop_elevation = layers[self.instances[0].stop_layer].upper_elevation

        diel_thick = abs(start_elevation - stop_elevation)
        rad1 = self.hole_properties[0] / 2 - math.tan(hole_wall_angle * diel_thick * math.pi / 180)
        rad2 = self.hole_properties[0] / 2

        if start_elevation < (topz + bottomz) / 2:
            rad1, rad2 = rad2, rad1
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
                    self._edb.cell.primitive.circle.create(
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
                    self._edb.cell.primitive.circle.create(
                        layout,
                        self.via_stop_layer,
                        via._edb_padstackinstance.GetNet(),
                        self._get_edb_value(pos[0]),
                        self._get_edb_value(pos[1]),
                        self._get_edb_value(self.pad_by_layer[self.via_stop_layer].parameters_values[0] / 2),
                    )
                for layer_name in layer_names:
                    stop = ""
                    if layer_name == via.start_layer or started:
                        start = layer_name
                        stop = layer_names[layer_names.index(layer_name) + 1]
                        cloned_circle = self._edb.cell.primitive.circle.create(
                            layout,
                            start,
                            via._edb_padstackinstance.GetNet(),
                            self._get_edb_value(pos[0]),
                            self._get_edb_value(pos[1]),
                            self._get_edb_value(rad1),
                        )
                        cloned_circle2 = self._edb.cell.primitive.circle.create(
                            layout,
                            stop,
                            via._edb_padstackinstance.GetNet(),
                            self._get_edb_value(pos[0]),
                            self._get_edb_value(pos[1]),
                            self._get_edb_value(rad2),
                        )
                        s3d = self._edb.cell.hierarchy._hierarchy.Structure3D.Create(
                            layout, generate_unique_name("via3d_" + via.aedt_name.replace("via_", ""), n=3)
                        )
                        s3d.AddMember(cloned_circle.prim_obj)
                        s3d.AddMember(cloned_circle2.prim_obj)
                        s3d.SetMaterial(self.material)
                        s3d.SetMeshClosureProp(self._edb.cell.hierarchy._hierarchy.Structure3D.TClosure.EndsClosed)
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
        List of :class:`pyedb.dotnet.edb_core.padstackEDBPadstack`
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
                new_padstack_definition_data = self._ppadstack._pedb.edb_api.definition.PadstackDefData.Create()
                new_padstack_definition_data.AddLayers(convert_py_list_to_net_list(included))
                for layer in included:
                    pl = self.pad_by_layer[layer]
                    new_padstack_definition_data.SetPadParameters(
                        layer,
                        self._ppadstack._pedb.edb_api.definition.PadType.RegularPad,
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
                        self._ppadstack._pedb.edb_api.definition.PadType.AntiPad,
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
                        self._ppadstack._pedb.edb_api.definition.PadType.ThermalPad,
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
        cloned_padstack_data = self._edb.definition.PadstackDefData(self.edb_padstack.GetData())
        new_padstack_data = self._edb.definition.PadstackDefData.Create()
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
                pad_type = self._edb.definition.PadType.RegularPad
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
                pad_type = self._edb.definition.PadType.AntiPad
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
                pad_type = self._edb.definition.PadType.ThermalPad
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
