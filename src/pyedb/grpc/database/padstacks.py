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

"""
This module contains the `EdbPadstacks` class.
"""
import math
import warnings

from ansys.edb.core.definition.padstack_def_data import (
    PadGeometryType as GrpcPadGeometryType,
)
from ansys.edb.core.definition.padstack_def_data import (
    PadstackDefData as GrpcPadstackDefData,
)
from ansys.edb.core.definition.padstack_def_data import (
    PadstackHoleRange as GrpcPadstackHoleRange,
)
from ansys.edb.core.definition.padstack_def_data import (
    SolderballPlacement as GrpcSolderballPlacement,
)
from ansys.edb.core.definition.padstack_def_data import (
    SolderballShape as GrpcSolderballShape,
)
from ansys.edb.core.definition.padstack_def_data import PadType as GrpcPadType
from ansys.edb.core.geometry.point_data import PointData as GrpcPointData
from ansys.edb.core.geometry.polygon_data import PolygonData as GrpcPolygonData
from ansys.edb.core.utility.value import Value as GrpcValue
import numpy as np
import rtree

from pyedb.generic.general_methods import generate_unique_name
from pyedb.grpc.database.definition.padstack_def import PadstackDef
from pyedb.grpc.database.primitive.padstack_instance import PadstackInstance
from pyedb.modeler.geometry_operators import GeometryOperators


class Padstacks(object):
    """Manages EDB methods for nets management accessible from `Edb.padstacks` property.

    Examples
    --------
    >>> from pyedb import Edb
    >>> edbapp = Edb("myaedbfolder", edbversion="2024.2")
    >>> edb_padstacks = edbapp.padstacks
    """

    def __getitem__(self, name):
        """Get  a padstack definition or instance from the Edb project.

        Parameters
        ----------
        name : str, int

        Returns
        -------
        :class:`pyedb.dotnet.database.cell.hierarchy.component.EDBComponent`

        """
        if isinstance(name, int) and name in self.instances:
            return self.instances(name)
        elif name in self.definitions:
            return self.definitions[name]
        else:
            for i in list(self.instances.values()):
                if i.name == name or i.aedt_name == name:
                    return i
        self._pedb.logger.error("Component or definition not found.")
        return

    def __init__(self, p_edb):
        self._pedb = p_edb
        self._instances = {}
        self._definitions = {}

    @property
    def _active_layout(self):
        """ """
        return self._pedb.active_layout

    @property
    def _layout(self):
        """ """
        return self._pedb.layout

    @property
    def db(self):
        """Db object."""
        return self._pedb.active_db

    @property
    def _logger(self):
        """ """
        return self._pedb.logger

    @property
    def _layers(self):
        """ """
        return self._pedb.stackup.layers

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

        if val == 0:
            return GrpcPadType.REGULAR_PAD
        elif val == 1:
            return GrpcPadType.ANTI_PAD
        elif val == 2:
            return GrpcPadType.THERMAL_PAD
        elif val == 3:
            return GrpcPadType.HOLE
        elif val == 4:
            return GrpcPadType.UNKNOWN_GEOM_TYPE
        else:
            return val

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
        if val == 0:
            return GrpcPadGeometryType.PADGEOMTYPE_NO_GEOMETRY
        elif val == 1:
            return GrpcPadGeometryType.PADGEOMTYPE_CIRCLE
        elif val == 2:
            return GrpcPadGeometryType.PADGEOMTYPE_SQUARE
        elif val == 3:
            return GrpcPadGeometryType.PADGEOMTYPE_RECTANGLE
        elif val == 4:
            return GrpcPadGeometryType.PADGEOMTYPE_OVAL
        elif val == 5:
            return GrpcPadGeometryType.PADGEOMTYPE_BULLET
        elif val == 6:
            return GrpcPadGeometryType.PADGEOMTYPE_NSIDED_POLYGON
        elif val == 7:
            return GrpcPadGeometryType.PADGEOMTYPE_POLYGON
        elif val == 8:
            return GrpcPadGeometryType.PADGEOMTYPE_ROUND45
        elif val == 9:
            return GrpcPadGeometryType.PADGEOMTYPE_ROUND90
        elif val == 10:
            return GrpcPadGeometryType.PADGEOMTYPE_SQUARE45
        elif val == 11:
            return GrpcPadGeometryType.PADGEOMTYPE_SQUARE90
        else:
            return val

    @property
    def definitions(self):
        """Padstack definitions.

        Returns
        -------
        dict[str, :class:`pyedb.dotnet.database.edb_data.padstacks_data.EdbPadstack`]
            List of definitions via padstack definitions.

        """
        if len(self._definitions) == len(self.db.padstack_defs):
            return self._definitions
        self._definitions = {}
        for padstack_def in self._pedb.db.padstack_defs:
            if len(padstack_def.data.layer_names) >= 1:
                self._definitions[padstack_def.name] = PadstackDef(self._pedb, padstack_def)
        return self._definitions

    @property
    def instances(self):
        """Dictionary  of all padstack instances (vias and pins).

        Returns
        -------
        dict[int, :class:`dotnet.database.edb_data.padstacks_data.EDBPadstackInstance`]
            List of padstack instances.

        """
        pad_stack_inst = self._pedb.layout.padstack_instances
        if len(self._instances) == len(pad_stack_inst):
            return self._instances
        self._instances = {i.edb_uid: PadstackInstance(self._pedb, i) for i in pad_stack_inst}
        return self._instances

    @property
    def instances_by_name(self):
        """Dictionary  of all padstack instances (vias and pins) by name.

        Returns
        -------
        dict[str, :class:`dotnet.database.edb_data.padstacks_data.EDBPadstackInstance`]
            List of padstack instances.

        """
        padstack_instances = {}
        for _, edb_padstack_instance in self.instances.items():
            if edb_padstack_instance.aedt_name:
                padstack_instances[edb_padstack_instance.aedt_name] = edb_padstack_instance
        return padstack_instances

    def find_instance_by_id(self, value: int):
        """Find a padstack instance by database id.

        Parameters
        ----------
        value : int
        """
        return self._pedb.modeler.find_object_by_id(value)

    @property
    def pins(self):
        """Dictionary  of all pins instances (belonging to component).

        Returns
        -------
        dic[str, :class:`dotnet.database.edb_data.definitions.EDBPadstackInstance`]
            Dictionary of EDBPadstackInstance Components.


        Examples
        --------
        >>> edbapp = dotnet.Edb("myproject.aedb")
        >>> pin_net_name = edbapp.pins[424968329].netname
        """
        pins = {}
        for instancename, instance in self.instances.items():
            if instance.is_pin and instance.component:
                pins[instancename] = instance
        return pins

    @property
    def vias(self):
        """Dictionary  of all vias instances not belonging to component.

        Returns
        -------
        dic[str, :class:`dotnet.database.edb_data.definitions.EDBPadstackInstance`]
            Dictionary of EDBPadstackInstance Components.


        Examples
        --------
        >>> edbapp = dotnet.Edb("myproject.aedb")
        >>> pin_net_name = edbapp.pins[424968329].netname
        """
        pnames = list(self.pins.keys())
        vias = {i: j for i, j in self.instances.items() if i not in pnames}
        return vias

    @property
    def pingroups(self):
        """All Layout Pin groups.

        . deprecated:: pyedb 0.28.0
        Use :func:`pyedb.grpc.core.layout.pin_groups` instead.

        Returns
        -------
        list
            List of all layout pin groups.
        """
        warnings.warn(
            "`pingroups` is deprecated and is now located here " "`pyedb.grpc.core.layout.pin_groups` instead.",
            DeprecationWarning,
        )
        return self._layout.pin_groups

    @property
    def pad_type(self):
        """Return a PadType Enumerator."""

    def create_circular_padstack(
        self,
        padstackname=None,
        holediam="300um",
        paddiam="400um",
        antipaddiam="600um",
        startlayer=None,
        endlayer=None,
    ):
        """Create a circular padstack.

        Parameters
        ----------
        padstackname : str, optional
            Name of the padstack. The default is ``None``.
        holediam : str, optional
            Diameter of the hole with units. The default is ``"300um"``.
        paddiam : str, optional
            Diameter of the pad with units. The default is ``"400um"``.
        antipaddiam : str, optional
            Diameter of the antipad with units. The default is ``"600um"``.
        startlayer : str, optional
            Starting layer. The default is ``None``, in which case the top
            is the starting layer.
        endlayer : str, optional
            Ending layer. The default is ``None``, in which case the bottom
            is the ending layer.

        Returns
        -------
        str
            Name of the padstack if the operation is successful.
        """

        padstack_def = PadstackDef.create(self._pedb.db, padstackname)

        padstack_data = GrpcPadstackDefData.create()
        list_values = [GrpcValue(holediam), GrpcValue(paddiam), GrpcValue(antipaddiam)]
        padstack_data.set_hole_parameters(
            offset_x=GrpcValue(0),
            offset_y=GrpcValue(0),
            rotation=GrpcValue(0),
            type_geom=GrpcPadGeometryType.PADGEOMTYPE_CIRCLE,
            sizes=list_values,
        )

        padstack_data.hole_range = GrpcPadstackHoleRange.UPPER_PAD_TO_LOWER_PAD
        layers = list(self._pedb.stackup.signal_layers.keys())
        if not startlayer:
            startlayer = layers[0]
        if not endlayer:
            endlayer = layers[len(layers) - 1]

        antipad_shape = GrpcPadGeometryType.PADGEOMTYPE_CIRCLE
        started = False
        padstack_data.set_pad_parameters(
            layer="Default",
            pad_type=GrpcPadType.REGULAR_PAD,
            type_geom=GrpcPadGeometryType.PADGEOMTYPE_CIRCLE,
            offset_x=GrpcValue(0),
            offset_y=GrpcValue(0),
            rotation=GrpcValue(0),
            sizes=[GrpcValue(paddiam)],
        )

        padstack_data.set_pad_parameters(
            layer="Default",
            pad_type=GrpcPadType.ANTI_PAD,
            type_geom=GrpcPadGeometryType.PADGEOMTYPE_CIRCLE,
            offset_x=GrpcValue(0),
            offset_y=GrpcValue(0),
            rotation=GrpcValue(0),
            sizes=[GrpcValue(antipaddiam)],
        )

        for layer in layers:
            if layer == startlayer:
                started = True
            if layer == endlayer:
                started = False
            if started:
                padstack_data.set_pad_parameters(
                    layer=layer,
                    pad_type=GrpcPadType.ANTI_PAD,
                    type_geom=GrpcPadGeometryType.PADGEOMTYPE_CIRCLE,
                    offset_x=GrpcValue(0),
                    offset_y=GrpcValue(0),
                    rotation=GrpcValue(0),
                    sizes=[GrpcValue(antipaddiam)],
                )

                padstack_data.set_pad_parameters(
                    layer=layer,
                    pad_type=GrpcPadType.ANTI_PAD,
                    type_geom=GrpcPadGeometryType.PADGEOMTYPE_CIRCLE,
                    offset_x=GrpcValue(0),
                    offset_y=GrpcValue(0),
                    rotation=GrpcValue(0),
                    sizes=[GrpcValue(antipaddiam)],
                )

        padstack_def.data = padstack_data

    def delete_padstack_instances(self, net_names):  # pragma: no cover
        """Delete padstack instances by net names.

        Parameters
        ----------
        net_names : str, list
            Names of the nets to delete.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> Edb.padstacks.delete_padstack_instances(net_names=["GND"])
        """
        if not isinstance(net_names, list):  # pragma: no cover
            net_names = [net_names]

        for p_id, p in self.instances.items():
            if p.net_name in net_names:
                if not p.delete():  # pragma: no cover
                    return False
        return True

    def set_solderball(self, padstackInst, sballLayer_name, isTopPlaced=True, ballDiam=100e-6):
        """Set solderball for the given PadstackInstance.

        Parameters
        ----------
        padstackInst : Edb.Cell.Primitive.PadstackInstance or int
            Padstack instance id or object.
        sballLayer_name : str,
            Name of the layer where the solder ball is placed. No default values.
        isTopPlaced : bool, optional.
            Bollean triggering is the solder ball is placed on Top or Bottom of the layer stackup.
        ballDiam : double, optional,
            Solder ball diameter value.

        Returns
        -------
        bool

        """
        if isinstance(padstackInst, int):
            psdef = self.definitions[self.instances[padstackInst].padstack_definition].edb_padstack
            padstackInst = self.instances[padstackInst]

        else:
            psdef = padstackInst.padstack_def
        newdefdata = GrpcPadstackDefData.create(psdef.data)
        newdefdata.solder_ball_shape = GrpcSolderballShape.SOLDERBALL_CYLINDER
        newdefdata.solder_ball_param(GrpcValue(ballDiam), GrpcValue(ballDiam))
        sball_placement = (
            GrpcSolderballPlacement.ABOVE_PADSTACK if isTopPlaced else GrpcSolderballPlacement.BELOW_PADSTACK
        )
        newdefdata.solder_ball_placement = sball_placement
        psdef.data = newdefdata
        sball_layer = [lay._edb_layer for lay in list(self._layers.values()) if lay.name == sballLayer_name][0]
        if sball_layer is not None:
            padstackInst.solder_ball_layer = sball_layer
            return True

        return False

    def create_coax_port(self, padstackinstance, use_dot_separator=True, name=None):
        """Create HFSS 3Dlayout coaxial lumped port on a pastack
        Requires to have solder ball defined before calling this method.

        . deprecated:: pyedb 0.28.0
        Use :func:`pyedb.grpc.core.excitations.create_source_on_component` instead.

        Parameters
        ----------
        padstackinstance : `Edb.Cell.Primitive.PadstackInstance` or int
            Padstack instance object.
        use_dot_separator : bool, optional
            Whether to use ``.`` as the separator for the naming convention, which
            is ``[component][net][pin]``. The default is ``True``. If ``False``, ``_`` is
            used as the separator instead.
        name : str
            Port name for overwriting the default port-naming convention,
            which is ``[component][net][pin]``. The port name must be unique.
            If a port with the specified name already exists, the
            default naming convention is used so that port creation does
            not fail.

        Returns
        -------
        str
            Terminal name.

        """
        warnings.warn(
            "`create_coax_port` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations.create_coax_port` instead.",
            DeprecationWarning,
        )
        self._pedb.source_excitation.create_coax_port(
            self, padstackinstance, use_dot_separator=use_dot_separator, name=name
        )

    def get_pin_from_component_and_net(self, refdes=None, netname=None):
        """Retrieve pins given a component's reference designator and net name.

        Parameters
        ----------
        refdes : str, optional
            Reference designator of the component. The default is ``None``.
        netname : str optional
            Name of the net. The default is ``None``.

        Returns
        -------
        dict
            Dictionary of pins if the operation is successful.
            ``False`` is returned if the net does not belong to the component.

        """
        pinlist = []
        if refdes:
            if refdes in self._pedb.components.instances:
                if netname:
                    for pin, val in self._pedb.components.instances[refdes].pins.items():
                        if val.net_name == netname:
                            pinlist.append(val)
                else:
                    for pin in self._pedb.components.instances[refdes].pins.values():
                        pinlist.append(pin)
            elif netname:
                for pin in self._pedb.pins:
                    if pin.net_name == netname:
                        pinlist.append(pin)
            else:
                self._logger.error("At least a component or a net name has to be provided")

        return pinlist

    def get_pinlist_from_component_and_net(self, refdes=None, netname=None):
        """Retrieve pins given a component's reference designator and net name.

        . deprecated:: pyedb 0.28.0
        Use :func:`get_pin_from_component_and_net` instead.

        Parameters
        ----------
        refdes : str, optional
            Reference designator of the component. The default is ``None``.
        netname : str optional
            Name of the net. The default is ``None``.

        Returns
        -------
        dict
            Dictionary of pins if the operation is successful.
            ``False`` is returned if the net does not belong to the component.

        """
        warnings.warn(
            "`get_pinlist_from_component_and_net` is deprecated use `get_pin_from_component_and_net` instead.",
            DeprecationWarning,
        )
        return self.get_pin_from_component_and_net(refdes=refdes, netname=netname)

    def get_pad_parameters(self, pin, layername, pad_type="regular_pad"):
        """Get Padstack Parameters from Pin or Padstack Definition.

        Parameters
        ----------
        pin : Edb.definition.PadstackDef or Edb.definition.PadstackInstance
            Pin or PadstackDef on which get values.
        layername : str
            Layer on which get properties.
        pad_type : str
            Pad Type, `"pad"`, `"anti_pad"`, `"thermal_pad"`

        Returns
        -------
        tuple
            Tuple of (GeometryType, ParameterList, OffsetX, OffsetY, Rot).
        """
        if pad_type == "regular_pad":
            pad_type = GrpcPadType.REGULAR_PAD
        elif pad_type == "anti_pad":
            pad_type = GrpcPadType.ANTI_PAD
        elif pad_type == "thermal_pad":
            pad_type = GrpcPadType.THERMAL_PAD
        else:
            pad_type = pad_type = GrpcPadType.REGULAR_PAD
        padparams = pin.padstack_def.data.get_pad_parameters(layername, pad_type)
        if len(padparams) == 5:  # non polygon via
            geometry_type = padparams[0]
            parameters = [i.value for i in padparams[1]]
            offset_x = padparams[2].value
            offset_y = padparams[3].value
            rotation = padparams[4].value
            return geometry_type.name, parameters, offset_x, offset_y, rotation
        elif len(padparams) == 4:  # polygon based
            from ansys.edb.core.geometry.polygon_data import (
                PolygonData as GrpcPolygonData,
            )

            if isinstance(padparams[0], GrpcPolygonData):
                points = [[pt.x.value, pt.y.value] for pt in padparams[0].points]
                offset_x = padparams[1]
                offset_y = padparams[2]
                rotation = padparams[3]
                geometry_type = GrpcPadGeometryType.PADGEOMTYPE_POLYGON
                return geometry_type.name, points, offset_x, offset_y, rotation
            return 0, [0], 0, 0, 0

    def set_all_antipad_value(self, value):
        """Set all anti-pads from all pad-stack definition to the given value.

        Parameters
        ----------
        value : float, str
            Anti-pad value.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` if an anti-pad value fails to be assigned.
        """
        if self.definitions:
            all_succeed = True
            for padstack in list(self.definitions.values()):
                cloned_padstack_data = GrpcPadstackDefData(padstack.data.msg)
                layers_name = cloned_padstack_data.layer_names
                for layer in layers_name:
                    try:
                        geom_type, points, offset_x, offset_y, rotation = cloned_padstack_data.get_pad_parameters(
                            layer, GrpcPadType.ANTI_PAD
                        )
                        if geom_type == GrpcPadGeometryType.PADGEOMTYPE_CIRCLE.name:
                            cloned_padstack_data.set_pad_parameters(
                                layer=layer,
                                pad_type=GrpcPadType.ANTI_PAD,
                                offset_x=GrpcValue(offset_x),
                                offset_y=GrpcValue(offset_y),
                                rotation=GrpcValue(rotation),
                                type_geom=GrpcPadGeometryType.PADGEOMTYPE_CIRCLE,
                                sizes=[GrpcValue(value)],
                            )
                            self._logger.info(
                                "Pad-stack definition {}, anti-pad on layer {}, has been set to {}".format(
                                    padstack.edb_padstack.GetName(), layer, str(value)
                                )
                            )
                        else:  # pragma no cover
                            self._logger.error(
                                f"Failed to reassign anti-pad value {value} on Pads-stack definition {padstack.name},"
                                f" layer{layer}. This feature only support circular shape anti-pads."
                            )
                            all_succeed = False
                    except:
                        self._pedb.logger.info(
                            f"No antipad defined for padstack definition {padstack.name}-layer{layer}"
                        )
                padstack.data = cloned_padstack_data
            return all_succeed

    def check_and_fix_via_plating(self, minimum_value_to_replace=0.0, default_plating_ratio=0.2):
        """Check for minimum via plating ration value, values found below the minimum one are replaced by default
        plating ratio.

        Parameters
        ----------
        minimum_value_to_replace : float
            Plating ratio that is below or equal to this value is to be replaced
            with the value specified for the next parameter. Default value ``0.0``.
        default_plating_ratio : float
            Default value to use for plating ratio. The default value is ``0.2``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` if an anti-pad value fails to be assigned.
        """
        for padstack_def in list(self.definitions.values()):
            if padstack_def.hole_plating_ratio <= minimum_value_to_replace:
                padstack_def.hole_plating_ratio = default_plating_ratio
                self._logger.info(
                    "Padstack definition with zero plating ratio, defaulting to 20%".format(padstack_def.name)
                )
        return True

    def get_via_instance_from_net(self, net_list=None):
        """Get the list for EDB vias from a net name list.

        Parameters
        ----------
        net_list : str or list
            The list of the net name to be used for filtering vias. If no net is provided the command will
            return an all vias list.

        Returns
        -------
        list of Edb.Cell.Primitive.PadstackInstance
            List of EDB vias.
        """
        if net_list and not isinstance(net_list, list):
            net_list = [net_list]
        via_list = []
        for inst in self._layout.padstack_instances:
            pad_layers_name = inst.padstack_def.data.layer_names
            if len(pad_layers_name) > 1:
                if not net_list:
                    via_list.append(inst)
                elif not inst.net.is_null:
                    if inst.net.name in net_list:
                        via_list.append(inst)
        return via_list

    def create(
        self,
        padstackname=None,
        holediam="300um",
        paddiam="400um",
        antipaddiam="600um",
        pad_shape="Circle",
        antipad_shape="Circle",
        x_size="600um",
        y_size="600um",
        corner_radius="300um",
        offset_x="0.0",
        offset_y="0.0",
        rotation="0.0",
        has_hole=True,
        pad_offset_x="0.0",
        pad_offset_y="0.0",
        pad_rotation="0.0",
        pad_polygon=None,
        antipad_polygon=None,
        polygon_hole=None,
        start_layer=None,
        stop_layer=None,
        add_default_layer=False,
        anti_pad_x_size="600um",
        anti_pad_y_size="600um",
        hole_range="upper_pad_to_lower_pad",
    ):
        """Create a padstack.

        Parameters
        ----------
        padstackname : str, optional
            Name of the padstack. The default is ``None``.
        holediam : str, optional
            Diameter of the hole with units. The default is ``"300um"``.
        paddiam : str, optional
            Diameter of the pad with units, used with ``"Circle"`` shape. The default is ``"400um"``.
        antipaddiam : str, optional
            Diameter of the antipad with units. The default is ``"600um"``.
        pad_shape : str, optional
            Shape of the pad. The default is ``"Circle``. Options are ``"Circle"``, ``"Rectangle"`` and ``"Polygon"``.
        antipad_shape : str, optional
            Shape of the antipad. The default is ``"Circle"``. Options are ``"Circle"`` ``"Rectangle"`` and
            ``"Bullet"``.
        x_size : str, optional
            Only applicable to bullet and rectangle shape. The default is ``"600um"``.
        y_size : str, optional
            Only applicable to bullet and rectangle shape. The default is ``"600um"``.
        corner_radius :
            Only applicable to bullet shape. The default is ``"300um"``.
        offset_x : str, optional
            X offset of antipad. The default is ``"0.0"``.
        offset_y : str, optional
            Y offset of antipad. The default is ``"0.0"``.
        rotation : str, optional
            rotation of antipad. The default is ``"0.0"``.
        has_hole : bool, optional
            Whether this padstack has a hole.
        pad_offset_x : str, optional
            Padstack offset in X direction.
        pad_offset_y : str, optional
            Padstack offset in Y direction.
        pad_rotation : str, optional
            Padstack rotation.
        start_layer : str, optional
            Start layer of the padstack definition.
        stop_layer : str, optional
            Stop layer of the padstack definition.
        add_default_layer : bool, optional
            Add ``"Default"`` to padstack definition. Default is ``False``.
        anti_pad_x_size : str, optional
            Only applicable to bullet and rectangle shape. The default is ``"600um"``.
        anti_pad_y_size : str, optional
            Only applicable to bullet and rectangle shape. The default is ``"600um"``.
        hole_range : str, optional
            Define the padstack hole range. Arguments supported, ``"through"``, ``"begin_on_upper_pad"``,
            ``"end_on_lower_pad"``, ``"upper_pad_to_lower_pad"``.

        Returns
        -------
        str
            Name of the padstack if the operation is successful.
        """
        holediam = GrpcValue(holediam)
        paddiam = GrpcValue(paddiam)
        antipaddiam = GrpcValue(antipaddiam)
        layers = list(self._pedb.stackup.signal_layers.keys())[:]
        value0 = GrpcValue("0.0")
        if not padstackname:
            padstackname = generate_unique_name("VIA")
        padstack_data = GrpcPadstackDefData.create()
        if has_hole and not polygon_hole:
            hole_param = [holediam, holediam]
            padstack_data.set_hole_parameters(
                offset_x=value0,
                offset_y=value0,
                rotation=value0,
                type_geom=GrpcPadGeometryType.PADGEOMTYPE_CIRCLE,
                sizes=hole_param,
            )
            padstack_data.plating_percentage = GrpcValue(20.0)
        elif polygon_hole:
            if isinstance(polygon_hole, list):
                polygon_hole = GrpcPolygonData(points=polygon_hole)
            padstack_data.set_hole_parameters(
                offset_x=value0,
                offset_y=value0,
                rotation=value0,
                type_geom=GrpcPadGeometryType.PADGEOMTYPE_POLYGON,
                fp=polygon_hole,
            )
            padstack_data.plating_percentage = GrpcValue(20.0)
        else:
            pass

        x_size = GrpcValue(x_size)
        y_size = GrpcValue(y_size)
        corner_radius = GrpcValue(corner_radius)
        pad_offset_x = GrpcValue(pad_offset_x)
        pad_offset_y = GrpcValue(pad_offset_y)
        pad_rotation = GrpcValue(pad_rotation)
        anti_pad_x_size = GrpcValue(anti_pad_x_size)
        anti_pad_y_size = GrpcValue(anti_pad_y_size)

        if hole_range == "through":  # pragma no cover
            padstack_data.hole_range = GrpcPadstackHoleRange.THROUGH
        elif hole_range == "begin_on_upper_pad":  # pragma no cover
            padstack_data.hole_range = GrpcPadstackHoleRange.BEGIN_ON_UPPER_PAD
        elif hole_range == "end_on_lower_pad":  # pragma no cover
            padstack_data.hole_range = GrpcPadstackHoleRange.END_ON_LOWER_PAD
        elif hole_range == "upper_pad_to_lower_pad":  # pragma no cover
            padstack_data.hole_range = GrpcPadstackHoleRange.UPPER_PAD_TO_LOWER_PAD
        else:  # pragma no cover
            self._logger.error("Unknown padstack hole range")
        padstack_data.material = "copper"

        if start_layer and start_layer in layers:  # pragma no cover
            layers = layers[layers.index(start_layer) :]
        if stop_layer and stop_layer in layers:  # pragma no cover
            layers = layers[: layers.index(stop_layer) + 1]
        if not isinstance(paddiam, list):
            pad_array = [paddiam]
        else:
            pad_array = paddiam
        if pad_shape == "Circle":  # pragma no cover
            pad_shape = GrpcPadGeometryType.PADGEOMTYPE_CIRCLE
        elif pad_shape == "Rectangle":  # pragma no cover
            pad_array = [x_size, y_size]
            pad_shape = GrpcPadGeometryType.PADGEOMTYPE_RECTANGLE
        elif pad_shape == "Polygon":
            if isinstance(pad_polygon, list):
                pad_array = GrpcPolygonData(points=pad_polygon)
            elif isinstance(pad_polygon, GrpcPolygonData):
                pad_array = pad_polygon
        if antipad_shape == "Bullet":  # pragma no cover
            antipad_array = [x_size, y_size, corner_radius]
            antipad_shape = GrpcPadGeometryType.PADGEOMTYPE_BULLET
        elif antipad_shape == "Rectangle":  # pragma no cover
            antipad_array = [anti_pad_x_size, anti_pad_y_size]
            antipad_shape = GrpcPadGeometryType.PADGEOMTYPE_RECTANGLE
        elif antipad_shape == "Polygon":
            if isinstance(antipad_polygon, list):
                antipad_array = GrpcPolygonData(points=antipad_polygon)
            elif isinstance(antipad_polygon, GrpcPolygonData):
                antipad_array = antipad_polygon
        else:
            if not isinstance(antipaddiam, list):
                antipad_array = [antipaddiam]
            else:
                antipad_array = antipaddiam
            antipad_shape = GrpcPadGeometryType.PADGEOMTYPE_CIRCLE
        if add_default_layer:  # pragma no cover
            layers = layers + ["Default"]
        if antipad_shape == "Polygon" and pad_shape == "Polygon":
            for layer in layers:
                padstack_data.set_pad_parameters(
                    layer=layer,
                    pad_type=GrpcPadType.REGULAR_PAD,
                    offset_x=pad_offset_x,
                    offset_y=pad_offset_y,
                    rotation=pad_rotation,
                    fp=pad_array,
                )
                padstack_data.set_pad_parameters(
                    layer=layer,
                    pad_type=GrpcPadType.ANTI_PAD,
                    offset_x=pad_offset_x,
                    offset_y=pad_offset_y,
                    rotation=pad_rotation,
                    fp=antipad_array,
                )
        else:
            for layer in layers:
                padstack_data.set_pad_parameters(
                    layer=layer,
                    pad_type=GrpcPadType.REGULAR_PAD,
                    offset_x=pad_offset_x,
                    offset_y=pad_offset_y,
                    rotation=pad_rotation,
                    type_geom=pad_shape,
                    sizes=pad_array,
                )

                padstack_data.set_pad_parameters(
                    layer=layer,
                    pad_type=GrpcPadType.ANTI_PAD,
                    offset_x=pad_offset_x,
                    offset_y=pad_offset_y,
                    rotation=pad_rotation,
                    type_geom=antipad_shape,
                    sizes=antipad_array,
                )

        padstack_definition = PadstackDef.create(self.db, padstackname)
        padstack_definition.data = padstack_data
        self._logger.info(f"Padstack {padstackname} create correctly")
        return padstackname

    def _get_pin_layer_range(self, pin):
        layers = pin.get_layer_range()
        if layers:
            return layers[0], layers[1]
        else:
            return False

    def duplicate(self, target_padstack_name, new_padstack_name=""):
        """Duplicate a padstack.

        Parameters
        ----------
        target_padstack_name : str
            Name of the padstack to be duplicated.
        new_padstack_name : str, optional
            Name of the new padstack.

        Returns
        -------
        str
            Name of the new padstack.
        """
        new_padstack_definition_data = GrpcPadstackDefData(self.definitions[target_padstack_name].data.msg)
        if not new_padstack_name:
            new_padstack_name = generate_unique_name(target_padstack_name)
        padstack_definition = PadstackDef.create(self.db, new_padstack_name)
        padstack_definition.data = new_padstack_definition_data
        return new_padstack_name

    def place(
        self,
        position,
        definition_name,
        net_name="",
        via_name="",
        rotation=0.0,
        fromlayer=None,
        tolayer=None,
        solderlayer=None,
        is_pin=False,
    ):
        """Place a via.

        Parameters
        ----------
        position : list
            List of float values for the [x,y] positions where the via is to be placed.
        definition_name : str
            Name of the padstack definition.
        net_name : str, optional
            Name of the net. The default is ``""``.
        via_name : str, optional
            The default is ``""``.
        rotation : float, optional
            Rotation of the padstack in degrees. The default
            is ``0``.
        fromlayer :
            The default is ``None``.
        tolayer :
            The default is ``None``.
        solderlayer :
            The default is ``None``.
        is_pin : bool, optional
            Whether if the padstack is a pin or not. Default is `False`.

        Returns
        -------
        :class:`dotnet.database.edb_data.padstacks_data.EDBPadstackInstance`
        """
        padstack_def = None
        for pad in list(self.definitions.keys()):
            if pad == definition_name:
                padstack_def = self.definitions[pad]
        position = GrpcPointData(
            [GrpcValue(position[0], self._pedb.active_cell), GrpcValue(position[1], self._pedb.active_cell)]
        )
        net = self._pedb.nets.find_or_create_net(net_name)
        rotation = GrpcValue(rotation * math.pi / 180)
        sign_layers_values = {i: v for i, v in self._pedb.stackup.signal_layers.items()}
        sign_layers = list(sign_layers_values.keys())
        if not fromlayer:
            try:
                fromlayer = sign_layers_values[list(self.definitions[pad].pad_by_layer.keys())[0]]
            except KeyError:
                fromlayer = sign_layers_values[sign_layers[0]]
        else:
            fromlayer = sign_layers_values[fromlayer]

        if not tolayer:
            try:
                tolayer = sign_layers_values[list(self.definitions[pad].pad_by_layer.keys())[-1]]
            except KeyError:
                tolayer = sign_layers_values[sign_layers[-1]]
        else:
            tolayer = sign_layers_values[tolayer]
        if solderlayer:
            solderlayer = sign_layers_values[solderlayer]
        if not via_name:
            via_name = generate_unique_name(padstack_def.name)
        if padstack_def:
            padstack_instance = PadstackInstance.create(
                layout=self._active_layout,
                net=net,
                name=via_name,
                padstack_def=padstack_def,
                position_x=position.x,
                position_y=position.y,
                rotation=rotation,
                top_layer=fromlayer,
                bottom_layer=tolayer,
                solder_ball_layer=solderlayer,
                layer_map=None,
            )
            padstack_instance.is_layout_pin = is_pin
            return PadstackInstance(self._pedb, padstack_instance)
        else:
            return False

    def remove_pads_from_padstack(self, padstack_name, layer_name=None):
        """Remove the Pad from a padstack on a specific layer by setting it as a 0 thickness circle.

        Parameters
        ----------
        padstack_name : str
            padstack name
        layer_name : str, optional
            Layer name on which remove the PadParameters. If None, all layers will be taken.

        Returns
        -------
        bool
            ``True`` if successful.
        """
        pad_type = GrpcPadType.REGULAR_PAD
        pad_geo = GrpcPadGeometryType.PADGEOMTYPE_CIRCLE
        vals = GrpcValue(0)
        params = [GrpcValue(0)]
        new_padstack_definition_data = GrpcPadstackDefData(self.definitions[padstack_name].data)
        if not layer_name:
            layer_name = list(self._pedb.stackup.signal_layers.keys())
        elif isinstance(layer_name, str):
            layer_name = [layer_name]
        for lay in layer_name:
            new_padstack_definition_data.set_pad_parameters(
                layer=lay,
                pad_type=pad_type,
                offset_x=vals,
                offset_y=vals,
                rotation=vals,
                type_geom=pad_geo,
                sizes=params,
            )
        self.definitions[padstack_name].data = new_padstack_definition_data
        return True

    def set_pad_property(
        self,
        padstack_name,
        layer_name=None,
        pad_shape="Circle",
        pad_params=0,
        pad_x_offset=0,
        pad_y_offset=0,
        pad_rotation=0,
        antipad_shape="Circle",
        antipad_params=0,
        antipad_x_offset=0,
        antipad_y_offset=0,
        antipad_rotation=0,
    ):
        """Set pad and antipad properties of the padstack.

        Parameters
        ----------
        padstack_name : str
            Name of the padstack.
        layer_name : str, optional
            Name of the layer. If None, all layers will be taken.
        pad_shape : str, optional
            Shape of the pad. The default is ``"Circle"``. Options are ``"Circle"``,  ``"Square"``, ``"Rectangle"``,
            ``"Oval"`` and ``"Bullet"``.
        pad_params : str, optional
            Dimension of the pad. The default is ``"0"``.
        pad_x_offset : str, optional
            X offset of the pad. The default is ``"0"``.
        pad_y_offset : str, optional
            Y offset of the pad. The default is ``"0"``.
        pad_rotation : str, optional
            Rotation of the pad. The default is ``"0"``.
        antipad_shape : str, optional
            Shape of the antipad. The default is ``"0"``.
        antipad_params : str, optional
            Dimension of the antipad. The default is ``"0"``.
        antipad_x_offset : str, optional
            X offset of the antipad. The default is ``"0"``.
        antipad_y_offset : str, optional
            Y offset of the antipad. The default is ``"0"``.
        antipad_rotation : str, optional
            Rotation of the antipad. The default is ``"0"``.

        Returns
        -------
        bool
            ``True`` if successful.
        """
        shape_dict = {
            "Circle": GrpcPadGeometryType.PADGEOMTYPE_CIRCLE,
            "Square": GrpcPadGeometryType.PADGEOMTYPE_SQUARE,
            "Rectangle": GrpcPadGeometryType.PADGEOMTYPE_RECTANGLE,
            "Oval": GrpcPadGeometryType.PADGEOMTYPE_OVAL,
            "Bullet": GrpcPadGeometryType.PADGEOMTYPE_BULLET,
        }
        pad_shape = shape_dict[pad_shape]
        if not isinstance(pad_params, list):
            pad_params = [pad_params]
        pad_params = [GrpcValue(i) for i in pad_params]
        pad_x_offset = GrpcValue(pad_x_offset)
        pad_y_offset = GrpcValue(pad_y_offset)
        pad_rotation = GrpcValue(pad_rotation)

        antipad_shape = shape_dict[antipad_shape]
        if not isinstance(antipad_params, list):
            antipad_params = [antipad_params]
        antipad_params = [GrpcValue(i) for i in antipad_params]
        antipad_x_offset = GrpcValue(antipad_x_offset)
        antipad_y_offset = GrpcValue(antipad_y_offset)
        antipad_rotation = GrpcValue(antipad_rotation)
        new_padstack_def = GrpcPadstackDefData(self.definitions[padstack_name].data.msg)
        if not layer_name:
            layer_name = list(self._pedb.stackup.signal_layers.keys())
        elif isinstance(layer_name, str):
            layer_name = [layer_name]
        for layer in layer_name:
            new_padstack_def.set_pad_parameters(
                layer=layer,
                pad_type=GrpcPadType.REGULAR_PAD,
                offset_x=pad_x_offset,
                offset_y=pad_y_offset,
                rotation=pad_rotation,
                type_geom=pad_shape,
                sizes=pad_params,
            )
            new_padstack_def.set_pad_parameters(
                layer=layer,
                pad_type=GrpcPadType.ANTI_PAD,
                offset_x=antipad_x_offset,
                offset_y=antipad_y_offset,
                rotation=antipad_rotation,
                type_geom=antipad_shape,
                sizes=antipad_params,
            )
        self.definitions[padstack_name].data = new_padstack_def
        return True

    def get_instances(
        self,
        name=None,
        pid=None,
        definition_name=None,
        net_name=None,
        component_reference_designator=None,
        component_pin=None,
    ):
        """Get padstack instances by conditions.

        Parameters
        ----------
        name : str, optional
            Name of the padstack.
        pid : int, optional
            Id of the padstack.
        definition_name : str, list, optional
            Name of the padstack definition.
        net_name : str, optional
            The net name to be used for filtering padstack instances.
        component_pin: str, optional
            Pin Number of the component.
        Returns
        -------
        list
            List of :class:`dotnet.database.edb_data.padstacks_data.EDBPadstackInstance`.
        """

        instances_by_id = self.instances
        if pid:
            return instances_by_id[pid]
        elif name:
            instances = [inst for inst in list(self.instances.values()) if inst.name == name]
            if instances:
                return instances
        else:
            instances = list(instances_by_id.values())
            if definition_name:
                definition_name = definition_name if isinstance(definition_name, list) else [definition_name]
                instances = [inst for inst in instances if inst.padstack_def.name in definition_name]
            if net_name:
                net_name = net_name if isinstance(net_name, list) else [net_name]
                instances = [inst for inst in instances if inst.net_name in net_name]
            if component_reference_designator:
                refdes = (
                    component_reference_designator
                    if isinstance(component_reference_designator, list)
                    else [component_reference_designator]
                )
                instances = [inst for inst in instances if inst.component]
                instances = [inst for inst in instances if inst.component.refdes in refdes]
                if component_pin:
                    component_pin = component_pin if isinstance(component_pin, list) else [component_pin]
                    instances = [inst for inst in instances if inst.component_pin in component_pin]
            return instances

    def get_reference_pins(
        self, positive_pin, reference_net="gnd", search_radius=5e-3, max_limit=0, component_only=True
    ):
        """Search for reference pins using given criteria.

        Parameters
        ----------
        positive_pin : EDBPadstackInstance
            Pin used for evaluating the distance on the reference pins found.
        reference_net : str, optional
            Reference net. The default is ``"gnd"``.
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
        >>> reference_pins = edbapp.padstacks.get_reference_pins(positive_pin=pin, reference_net="GND",
        >>> search_radius=5e-3, max_limit=0, component_only=True)
        """
        pinlist = []
        if not positive_pin:
            search_radius = 10e-2
            component_only = True
        if component_only:
            references_pins = [
                pin for pin in list(positive_pin.component.pins.values()) if pin.net_name == reference_net
            ]
            if not references_pins:
                return pinlist
        else:
            references_pins = self.get_instances(net_name=reference_net)
            if not references_pins:
                return pinlist
        pinlist = [
            p
            for p in references_pins
            if GeometryOperators.points_distance(positive_pin.position, p.position) <= search_radius
        ]
        if max_limit and len(pinlist) > max_limit:
            pin_dict = {GeometryOperators.points_distance(positive_pin.position, p.position): p for p in pinlist}
            pinlist = [pin[1] for pin in sorted(pin_dict.items())[:max_limit]]
        return pinlist

    def get_padstack_instances_rtree_index(self, nets=None):
        """Returns padstack instances Rtree index.

        Parameters
        ----------
        nets : str or list, optional
            net name of list of nets name applying filtering on padstack instances selection. If ``None`` is provided
            all instances are included in the index. Default value is ``None``.

        Returns
        -------
        Rtree index object.

        """
        if isinstance(nets, str):
            nets = [nets]
        padstack_instances_index = rtree.index.Index()
        if nets:
            instances = [inst for inst in list(self.instances.values()) if inst.net_name in nets]
        else:
            instances = list(self.instances.values())
        for inst in instances:
            padstack_instances_index.insert(inst.edb_uid, inst.position)
        return padstack_instances_index

    def get_padstack_instances_id_intersecting_polygon(self, points, nets=None, padstack_instances_index=None):
        """Returns the list of padstack instances ID intersecting a given bounding box and nets.

        Parameters
        ----------
        points : tuple or list.
            bounding box, [x1, y1, x2, y2]
        nets : str or list, optional
            net name of list of nets name applying filtering on padstack instances selection. If ``None`` is provided
            all instances are included in the index. Default value is ``None``.
        padstack_instances_index : optional, Rtree object.
            Can be provided optionally to prevent computing padstack instances Rtree index again.

        Returns
        -------
        List[int]
            List of padstack instances ID intersecting the bounding box.
        """
        if not points:
            raise Exception("No points defining polygon was provided")
        if not padstack_instances_index:
            padstack_instances_index = {}
            for inst in self.instances:
                padstack_instances_index[inst.id] = inst.position
        _x = [pt[0] for pt in points]
        _y = [pt[1] for pt in points]
        points = [_x, _y]
        return [
            ind for ind, pt in padstack_instances_index.items() if GeometryOperators.is_point_in_polygon(pt, points)
        ]

    def get_padstack_instances_intersecting_bounding_box(self, bounding_box, nets=None, padstack_instances_index=None):
        """Returns the list of padstack instances ID intersecting a given bounding box and nets.
        Parameters
        ----------
        bounding_box : tuple or list.
            bounding box, [x1, y1, x2, y2]
        nets : str or list, optional
            net name of list of nets name applying filtering on padstack instances selection. If ``None`` is provided
            all instances are included in the index. Default value is ``None``.
        padstack_instances_index : optional, Rtree object.
            Can be provided optionally to prevent computing padstack instances Rtree index again.
        Returns
        -------
        List of padstack instances ID intersecting the bounding box.
        """
        if not bounding_box:
            raise Exception("No bounding box was provided")
        if not padstack_instances_index:
            index = self.get_padstack_instances_rtree_index(nets=nets)
        else:
            index = padstack_instances_index
        if not len(bounding_box) == 4:
            raise Exception("The bounding box length must be equal to 4")
        if isinstance(bounding_box, list):
            bounding_box = tuple(bounding_box)
        return list(index.intersection(bounding_box))

    def merge_via_along_lines(
        self,
        net_name="GND",
        distance_threshold=5e-3,
        minimum_via_number=6,
        selected_angles=None,
        padstack_instances_id=None,
    ):
        """Replace padstack instances along lines into a single polygon.

        Detect all pad-stack instances that are placed along lines and replace them by a single polygon based one
        forming a wall shape. This method is designed to simplify meshing on via fence usually added to shield RF traces
        on PCB.

        Parameters
        ----------
        net_name : str
            Net name used for detected pad-stack instances. Default value is ``"GND"``.

        distance_threshold : float, None, optional
            If two points in a line are separated by a distance larger than `distance_threshold`,
            the line is divided in two parts. Default is ``5e-3`` (5mm), in which case the control is not performed.

        minimum_via_number : int, optional
            The minimum number of points that a line must contain. Default is ``6``.

        selected_angles : list[int, float]
            Specify angle in degrees to detected, for instance [0, 180] is only detecting horizontal and vertical lines.
            Other values can be assigned like 45 degrees. When `None` is provided all lines are detected. Default value
            is `None`.

        padstack_instances_id : List[int]
            List of pad-stack instances ID's to include. If `None`, the algorithm will scan all pad-stack
            instances belonging to the specified net. Default value is `None`.

        Returns
        -------
        List[int], list of created pad-stack instances id.

        """
        _def = list(set([inst.padstack_def for inst in list(self.instances.values()) if inst.net_name == net_name]))
        if not _def:
            self._logger.error(f"No padstack definition found for net {net_name}")
            return False
        instances_created = []
        _instances_to_delete = []
        padstack_instances = []
        if padstack_instances_id:
            padstack_instances = [[self.instances[id] for id in padstack_instances_id]]
        else:
            for pdstk_def in _def:
                padstack_instances.append(
                    [inst for inst in self.definitions[pdstk_def.name].instances if inst.net_name == net_name]
                )
        for pdstk_series in padstack_instances:
            instances_location = [inst.position for inst in pdstk_series]
            lines, line_indexes = GeometryOperators.find_points_along_lines(
                points=instances_location,
                minimum_number_of_points=minimum_via_number,
                distance_threshold=distance_threshold,
                selected_angles=selected_angles,
            )
            for line in line_indexes:
                [_instances_to_delete.append(pdstk_series[ind]) for ind in line]
                start_point = pdstk_series[line[0]]
                stop_point = pdstk_series[line[-1]]
                padstack_def = start_point.padstack_def
                trace_width = (
                    self.definitions[padstack_def.name].pad_by_layer[stop_point.start_layer].parameters_values[0]
                )
                trace = self._pedb.modeler.create_trace(
                    path_list=[start_point.position, stop_point.position],
                    layer_name=start_point.start_layer,
                    width=trace_width,
                )
                polygon_data = trace.polygon_data
                trace.delete()
                new_padstack_def = generate_unique_name(padstack_def.name)
                if not self.create(
                    padstackname=new_padstack_def,
                    pad_shape="Polygon",
                    antipad_shape="Polygon",
                    pad_polygon=polygon_data,
                    antipad_polygon=polygon_data,
                    polygon_hole=polygon_data,
                ):
                    self._logger.error(f"Failed to create padstack definition {new_padstack_def.name}")
                new_instance = self.place(position=[0, 0], definition_name=new_padstack_def, net_name=net_name)
                if not new_instance:
                    self._logger.error(f"Failed to place padstack instance {new_padstack_def}")
                else:
                    instances_created.append(new_instance.id)
            for inst in _instances_to_delete:
                inst.delete()
        return instances_created

    def reduce_via_in_bounding_box(self, bounding_box, x_samples, y_samples, nets=None):
        """Reduces the number of vias intersecting bounding box and nets by x and y samples.

        Parameters
        ----------
        bounding_box : tuple or list.
            bounding box, [x1, y1, x2, y2]
        x_samples : int
        y_samples : int
        nets : str or list, optional
            net name or list of nets name applying filtering on padstack instances selection. If ``None`` is provided
            all instances are included in the index. Default value is ``None``.

        Returns
        -------
        bool
            ``True`` when succeeded ``False`` when failed.
        """

        padstacks_inbox = self.get_padstack_instances_intersecting_bounding_box(bounding_box, nets)
        if not padstacks_inbox:
            self._logger.info("no padstack in bounding box")
            return False
        else:
            if len(padstacks_inbox) <= (x_samples * y_samples):
                self._logger.info(f"more samples {x_samples * y_samples} than existing {len(padstacks_inbox)}")
                return False
            else:
                # extract ids and positions
                vias = {item: self.instances[item].position for item in padstacks_inbox}
                ids, positions = zip(*vias.items())
                pt_x, pt_y = zip(*positions)

                # meshgrid
                _x_min, _x_max = min(pt_x), max(pt_x)
                _y_min, _y_max = min(pt_y), max(pt_y)

                x_grid, y_grid = np.meshgrid(
                    np.linspace(_x_min, _x_max, x_samples), np.linspace(_y_min, _y_max, y_samples)
                )

                # mapping to meshgrid
                to_keep = {
                    ids[np.argmin(np.square(_x - pt_x) + np.square(_y - pt_y))]
                    for _x, _y in zip(x_grid.ravel(), y_grid.ravel())
                }

                for item in padstacks_inbox:
                    if item not in to_keep:
                        self.instances[item].delete()

                return True

    def merge_via(self, contour_boxes, net_filter=None, start_layer=None, stop_layer=None):
        """Evaluate pad-stack instances included on the provided point list and replace all by single instance.

        Parameters
        ----------
        contour_boxes : List[List[List[float, float]]]
            Nested list of polygon with points [x,y].
        net_filter : optional
            List[str: net_name] apply a net filter, nets included in the filter are excluded from the via merge.
        start_layer : optional, str
            Pad-stack instance start layer, if `None` the top layer is selected.
        stop_layer : optional, str
            Pad-stack instance stop layer, if `None` the bottom layer is selected.

        Return
        ------
        List[str], list of created pad-stack instances ID.

        """

        import numpy as np
        from scipy.spatial import ConvexHull

        merged_via_ids = []
        if not contour_boxes:
            raise Exception("No contour box provided, you need to pass a nested list as argument.")
        instances_index = {}
        for id, inst in self.instances.items():
            instances_index[id] = inst.position
        for contour_box in contour_boxes:
            instances = self.get_padstack_instances_id_intersecting_polygon(
                points=contour_box, padstack_instances_index=instances_index
            )
            if net_filter:
                instances = [id for id in instances if not self.instances[id].net.name in net_filter]
            net = self.instances[instances[0]].net.name
            instances_pts = np.array([self.instances[inst].position for inst in instances])
            convex_hull_contour = ConvexHull(instances_pts)
            contour_points = list(instances_pts[convex_hull_contour.vertices])
            layer = list(self._pedb.stackup.layers.values())[0].name
            polygon = self._pedb.modeler.create_polygon(points=contour_points, layer_name=layer)
            polygon_data = polygon.polygon_data
            polygon.delete()
            new_padstack_def = generate_unique_name("test")
            if not self.create(
                padstackname=new_padstack_def,
                pad_shape="Polygon",
                antipad_shape="Polygon",
                pad_polygon=polygon_data,
                antipad_polygon=polygon_data,
                polygon_hole=polygon_data,
                start_layer=start_layer,
                stop_layer=stop_layer,
            ):
                self._logger.error(f"Failed to create padstack definition {new_padstack_def}")
            merged_instance = self.place(
                position=[0, 0],
                definition_name=new_padstack_def,
                net_name=net,
                fromlayer=start_layer,
                tolayer=stop_layer,
            )
            merged_via_ids.append(merged_instance.edb_uid)
            [self.instances[inst].delete() for inst in instances]
        return merged_via_ids

    def reduce_via_in_bounding_box(self, bounding_box, x_samples, y_samples, nets=None):
        """
        reduce the number of vias intersecting bounding box and nets by x and y samples.

        Parameters
        ----------
        bounding_box : tuple or list.
            bounding box, [x1, y1, x2, y2]
        x_samples : int
        y_samples : int
        nets : str or list, optional
            net name of list of nets name applying filtering on pad-stack instances selection. If ``None`` is provided
            all instances are included in the index. Default value is ``None``.

        Returns
        -------
        bool
            ``True`` when succeeded ``False`` when failed.
        """

        padstacks_inbox = self.get_padstack_instances_intersecting_bounding_box(bounding_box, nets)
        if not padstacks_inbox:
            return False
        else:
            if len(padstacks_inbox) <= (x_samples * y_samples):
                self._pedb.logger.error(f"more samples {x_samples * y_samples} than existing {len(padstacks_inbox)}")
                return False
            else:
                # extract ids and positions
                vias = {item: self.instances[item].position for item in padstacks_inbox}
                ids, positions = zip(*vias.items())
                pt_x, pt_y = zip(*positions)

                # meshgrid
                _x_min, _x_max = min(pt_x), max(pt_x)
                _y_min, _y_max = min(pt_y), max(pt_y)

                x_grid, y_grid = np.meshgrid(
                    np.linspace(_x_min, _x_max, x_samples), np.linspace(_y_min, _y_max, y_samples)
                )

                # mapping to meshgrid
                to_keep = {
                    ids[np.argmin(np.square(_x - pt_x) + np.square(_y - pt_y))]
                    for _x, _y in zip(x_grid.ravel(), y_grid.ravel())
                }

                all_instances = self.instances
                for item in padstacks_inbox:
                    if item not in to_keep:
                        all_instances[item].delete()
                return True
