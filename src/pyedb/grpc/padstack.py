"""
This module contains the `EdbPadstacks` class.
"""
import math

from pyedb.grpc.edb_core.edb_data.padstacks_data import EDBPadstack
from pyedb.grpc.edb_core.edb_data.padstacks_data import EDBPadstackInstance
from pyedb.generic.general_methods import generate_unique_name
from pyedb.generic.general_methods import pyedb_function_handler
from pyedb.modeler.geometry_operators import GeometryOperators
import ansys.edb.definition as definition
import ansys.edb.primitive as primitive
import ansys.edb.utility as utility
import ansys.edb.terminal as terminal
import ansys.edb.geometry as geometry


# from ansys.edb.definition.padstack_def_data import PadType, PadGeometryType
# from ansys.edb.definition.padstack_def import PadstackDef, PadstackDefData
# from ansys.edb.definition.padstack_def_data import PadstackHoleRange
# from ansys.edb.utility.value import Value
# from ansys.edb.definition.solder_ball_property import SolderballShape, SolderballPlacement
# from ansys.edb.terminal.terminals import PadstackInstanceTerminal
# from ansys.edb.geometry.polygon_data import PolygonData
# from ansys.edb.geometry.point_data import PointData


class EdbPadstacks(object):
    """Manages EDB methods for nets management accessible from `Edb.padstacks` property.

    Examples
    --------
    >>> from src.pyedb.grpc.edb import Edb
    >>> edbapp = Edb("myaedbfolder", edbversion="2021.2")
    >>> edb_padstacks = edbapp.padstacks
    """

    @pyedb_function_handler()
    def __getitem__(self, name):
        """Get  a padstack definition or instance from the Edb project.

        Parameters
        ----------
        name : str, int

        Returns
        -------
        :class:`pyaedt.edb_core.edb_data.components_data.EDBComponent`

        """
        if name in self.instances:
            return self.instances[name]
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

    @property
    def _edb(self):
        """ """
        return self._pedb

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
        return self._pedb.stackup.stackup_layers

    @pyedb_function_handler()
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
            return definition.PadGeometryType.PADGEOMTYPE_NO_GEOMETRY
        elif val == 1:
            return definition.PadGeometryType.PADGEOMTYPE_CIRCLE
        elif val == 2:
            return definition.PadGeometryType.PADGEOMTYPE_SQUARE
        elif val == 3:
            return definition.PadGeometryType.PADGEOMTYPE_RECTANGLE
        elif val == 4:
            return definition.PadGeometryType.PADGEOMTYPE_OVAL
        elif val == 5:
            return definition.PadGeometryType.PADGEOMTYPE_BULLET
        elif val == 6:
            return definition.PadGeometryType.PADGEOMTYPE_NSIDED_POLYGON
        elif val == 7:
            return definition.PadGeometryType.PADGEOMTYPE_POLYGON
        elif val == 8:
            return definition.PadGeometryType.PADGEOMTYPE_ROUND45
        elif val == 9:
            return definition.PadGeometryType.PADGEOMTYPE_ROUND90
        elif val == 10:
            return definition.PadGeometryType.PADGEOMTYPE_SQUARE45
        elif val == 11:
            return definition.PadGeometryType.PADGEOMTYPE_SQUARE90
        elif val == 12:
            return definition.PadGeometryType.PADGEOMTYPE_INVALID_GEOMETRY
        else:
            return val

    @property
    def definitions(self):
        """Padstack definitions.

        Returns
        -------
        dict[str, :class:`pyaedt.edb_core.edb_data.padstacks_data.EdbPadstack`]
            List of definitions via padstack definitions.

        """
        _padstacks = {}
        for padstackdef in self._pedb.active_db.padstack_defs:
            PadStackData = padstackdef.data
            if len(PadStackData.layer_names) >= 1:
                _padstacks[padstackdef.name] = EDBPadstack(padstackdef, self)
        return _padstacks

    @property
    def instances(self):
        """Dictionary  of all padstack instances (vias and pins).

        Returns
        -------
        dict[str, :class:`pyaedt.edb_core.edb_data.padstacks_data.EDBPadstackInstance`]
            List of padstack instances.

        """

        padstack_instances = {}
        edb_padstack_inst_list = self._pedb.layout.padstack_instances
        for edb_padstack_instance in edb_padstack_inst_list:
            padstack_instances[edb_padstack_instance.id] = EDBPadstackInstance(edb_padstack_instance, self._pedb)
        return padstack_instances

    @property
    def pins(self):
        """Dictionary  of all pins instances (belonging to component).

        Returns
        -------
        dic[str, :class:`pyaedt.edb_core.edb_data.definitions.EDBPadstackInstance`]
            Dictionary of EDBPadstackInstance Components.


        Examples
        --------
        >>> edbapp = pyedb.Edb("myproject.aedb")
        >>> pin_net_name = edbapp.pins[424968329].netname
        """
        pins = {}
        for instancename, instance in self.instances.items():
            if instance.is_pin and instance.primitive_object.component:
                pins[instancename] = instance
        return pins

    @property
    def vias(self):
        """Dictionary  of all vias instances not belonging to component.

        Returns
        -------
        dic[str, :class:`pyaedt.edb_core.edb_data.definitions.EDBPadstackInstance`]
            Dictionary of EDBPadstackInstance Components.


        Examples
        --------
        >>> edbapp = pyedb.Edb("myproject.aedb")
        >>> pin_net_name = edbapp.pins[424968329].netname
        """
        pnames = list(self.pins.keys())
        vias = {i: j for i, j in self.instances.items() if i not in pnames}
        return vias

    @property
    def pingroups(self):
        """All Layout Pin groups.

        Returns
        -------
        list
            List of all layout pin groups.
        """
        pingroups = []
        for el in self._layout.pin_groups:
            pingroups.append(el)
        return pingroups

    @property
    def pad_type(self):
        """Return a PadType Enumerator."""

        class Pad_Type:
            (RegularPad, AntiPad, ThermalPad, Hole, UnknownGeomType) = (definition.PadType.REGULAR_PAD,
                                                                        definition.PadType.ANTI_PAD,
                                                                        definition.PadType.THERMAL_PAD,
                                                                        definition.PadType.HOLE,
                                                                        definition.PadType.UNKNOWN_GEOM_TYPE)

        return Pad_Type

    @pyedb_function_handler()
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

        PadStack = definition.PadstackDef.create(self._layout.cell.database, padstackname)
        new_PadStackData = definition.PadstackDefData.create()
        list_values = [utility.Value(holediam), utility.Value(paddiam), utility.Value(antipaddiam)]

        new_PadStackData.set_hole_parameters(type_geom=definition.PadGeometryType.PADGEOMTYPE_CIRCLE,
                                             sizes=list_values,
                                             offset_x=utility.Value(0),
                                             offset_y=utility.Value(0),
                                             rotation=utility.Value(0))
        new_PadStackData.hole_range(definition.PadstackHoleRange.UPPER_PAD_TO_LOWER_PAD)
        layers = list(self._pedb.stackup.signal_layers.keys())
        if not startlayer:
            startlayer = layers[0]
        if not endlayer:
            endlayer = layers[len(layers) - 1]

        antipad_shape = definition.PadGeometryType.PADGEOMTYPE_CIRCLE
        started = False
        new_PadStackData.set_pad_parameters(
            layer="dafault",
            pad_type=definition.PadType.REGULAR_PAD,
            offset_x=utility.Value(0),
            offset_y=utility.Value(0),
            rotation=utility.Value(0),
            type_geom=definition.PadGeometryType.PADGEOMTYPE_CIRCLE,
            sizes=[utility.Value(paddiam)]

        )

        new_PadStackData.set_pad_parameters(
            layer="Default",
            pad_type=definition.PadType.ANTI_PAD,
            offset_x=utility.Value(0),
            offset_y=utility.Value(0),
            rotation=utility.Value(0),
            type_geom=definition.PadGeometryType.PADGEOMTYPE_CIRCLE,
            sizes=[utility.Value(antipaddiam)]
        )
        for layer in layers:
            if layer == startlayer:
                started = True
            if layer == endlayer:
                started = False
            if started:
                new_PadStackData.set_pad_parameters(
                    layer=layer,
                    pad_type=definition.PadType.REGULAR_PAD,
                    type_geom=definition.PadGeometryType.PADGEOMTYPE_CIRCLE,
                    sizes=[utility.Value(antipaddiam)],
                    offset_x=utility.Value(0),
                    offset_y=utility.Value(0),
                    rotation=utility.Value(0),
                )
                new_PadStackData.set_pad_parameters(
                    layer=layer,
                    pad_type=definition.PadType.ANTI_PAD,
                    type_geom=definition.PadGeometryType.PADGEOMTYPE_RECTANGLE,
                    sizes=[utility.Value(antipaddiam)],
                    offset_x=utility.Value(0),
                    offset_y=utility.Value(0),
                    rotation=utility.Value(0)
                )
        PadStack.data = new_PadStackData

    @pyedb_function_handler
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

    @pyedb_function_handler()
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
            padstackInst = self.instances[padstackInst]._edb_padstackinstance

        else:
            psdef = padstackInst.padstack_def
        newdefdata = definition.PadstackDefData(psdef.data)
        newdefdata.solder_ball_shape = definition.SolderballShape.SOLDERBALL_CYLINDER
        newdefdata.solder_ball_param = (utility.Value(ballDiam), utility.Value(ballDiam))
        sball_placement = definition.SolderballPlacement.ABOVE_PADSTACK if isTopPlaced else definition.SolderballPlacement.BELOW_PADSTACK
        newdefdata.solder_ball_placement = sball_placement
        psdef.data = newdefdata
        sball_layer = [lay._edb_layer for lay in list(self._layers.values()) if lay.name == sballLayer_name][0]
        if sball_layer is not None:
            padstackInst.solder_ball_layer = sball_layer
            return True

        return False

    @pyedb_function_handler()
    def create_coax_port(self, padstackinstance, use_dot_separator=True, name=None):
        """Create HFSS 3Dlayout coaxial lumped port on a pastack
        Requires to have solder ball defined before calling this method.

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
        if isinstance(padstackinstance, int):
            padstackinstance = self.instances[padstackinstance]._edb_padstackinstance
        elif isinstance(padstackinstance, EDBPadstackInstance):
            padstackinstance = padstackinstance._edb_padstackinstance
        cmp_name = padstackinstance.component.name
        if cmp_name == "":
            cmp_name = "no_comp"
        net_name = padstackinstance.net.name
        if net_name == "":
            net_name = "no_net"
        pin_name = padstackinstance.name
        if pin_name == "":
            pin_name = "no_pin_name"
        if use_dot_separator:
            port_name = "{0}.{1}.{2}".format(cmp_name, pin_name, net_name)
        else:
            port_name = "{0}_{1}_{2}".format(cmp_name, pin_name, net_name)
        if not padstackinstance.is_layout_pin:
            padstackinstance.is_layout_pin = True
        top_bottom_layer = padstackinstance.get_layer_range()
        if name:
            port_name = name
        if self._port_exist(port_name):
            port_name = generate_unique_name(port_name, n=2)
            self._logger.info("An existing port already has this same name. Renaming to {}.".format(port_name))
        term = terminal.PadstackInstanceTerminal.create(
            layout=self._active_layout,
            net=padstackinstance.net,
            name=port_name,
            padstack_instance=padstackinstance,
            layer=top_bottom_layer[0],
        )
        if term:
            return port_name
        return ""

    @pyedb_function_handler()
    def _port_exist(self, port_name):
        return any(port for port in list(self._pedb.excitations.keys()) if port == port_name)

    @pyedb_function_handler()
    def get_pinlist_from_component_and_net(self, refdes=None, netname=None):
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

    @pyedb_function_handler()
    def get_pad_parameters(self, pin, layername, pad_type=0):
        """Get Padstack Parameters from Pin or Padstack Definition.

        Parameters
        ----------
        pin : Edb.definition.PadstackDef or Edb.definition.PadstackInstance
            Pin or PadstackDef on which get values.
        layername : str
            Layer on which get properties.
        pad_type : int
            Pad Type.

        Returns
        -------
        tuple
            Tuple of (GeometryType, ParameterList, OffsetX, OffsetY, Rot).
        """

        if isinstance(pin, definition.PadstackDef):
            padparams = definition.PadstackDefData(pin.data).get_pad_parameters(layername, definition.PadType(pad_type))
        else:
            padparams = definition.PadstackDefData(pin.padstack_def.data).get_pad_parameters(layername,
                                                                                             definition.PadType(
                                                                                                 pad_type))

        if isinstance(padparams[0], definition.PadGeometryType):
            geometry_type = padparams[0]
            size = padparams[1]
            offset_x = padparams[2]
            offset_y = padparams[3]
            rotation = padparams[4]
            return geometry_type, size, offset_x, offset_y, rotation
        elif isinstance(padparams[0], geometry.PolygonData):
            polygon_data = padparams[0]
            offset_x = padparams[1]
            offset_y = padparams[2]
            rotation = padparams[3]
            return polygon_data, offset_x, offset_y, rotation
        return definition.PadType.UNKNOWN_GEOM_TYPE

    @pyedb_function_handler
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
            for padstack in list(self.definitions.values()):
                cloned_padstack_data = definition.PadstackDefData(padstack.edb_padstack.data)
                layers_name = cloned_padstack_data.layer_names
                all_succeed = True
                for layer in layers_name:
                    pad_parameters = self.get_pad_parameters(padstack.edb_padstack, layer, 1)
                    if pad_parameters[0].value == 1:  # pragma no cover
                        size = [utility.Value(value)] * len(pad_parameters[1].value)
                        geom_type = definition.PadGeometryType.PADGEOMTYPE_CIRCLE
                        offset_x = utility.Value(pad_parameters[2].value)
                        offset_y = utility.Value(pad_parameters[3].value)
                        rot = utility.Value(pad_parameters[4].value)
                        antipad = definition.PadType.ANTI_PAD
                        if cloned_padstack_data.set_pad_parameters(
                                layer, antipad, geom_type, size, offset_x, offset_y, rot
                        ):  # pragma no cover
                            self._logger.info(
                                "Pad-stack definition {}, anti-pad on layer {}, has been set to {}".format(
                                    padstack.edb_padstack.name, layer, str(value)
                                )
                            )
                        else:  # pragma no cover
                            self._logger.error(
                                "Failed to reassign anti-pad value {} on Pads-stack definition {},"
                                " layer{}".format(str(value), padstack.edb_padstack.name, layer)
                            )
                            all_succeed = False
                padstack.edb_padstack.data = cloned_padstack_data
            return all_succeed

    @pyedb_function_handler
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

    @pyedb_function_handler()
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
        if net_list == None:
            net_list = []

        if not isinstance(net_list, list):
            net_list = [net_list]
        layout_lobj_collection = self._layout.padstack_instances
        via_list = []
        for lobj in layout_lobj_collection:
            pad_layers_name = lobj.padstack_def.data.layer_names
            if len(pad_layers_name) > 1:
                if not net_list:
                    via_list.append(lobj)
                elif lobj.net.name in net_list:
                    via_list.append(lobj)
        return via_list

    @pyedb_function_handler()
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
            Shape of the pad. The default is ``"Circle``. Options are ``"Circle"`` and ``"Rectangle"``.
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
        holediam = utility.Value(holediam)
        paddiam = utility.Value(paddiam)
        antipaddiam = utility.Value(antipaddiam)

        if not padstackname:
            padstackname = generate_unique_name("VIA")
        # assert not self.isreadonly, "Write Functions are not available within AEDT"
        padstackData = definition.PadstackDefData.create()
        if has_hole:
            pad_type = definition.PadGeometryType.PADGEOMTYPE_CIRCLE
        else:
            pad_type = definition.PadGeometryType.PADGEOMTYPE_NO_GEOMETRY
        x_size = utility.Value(x_size)
        y_size = utility.Value(y_size)
        corner_radius = utility.Value(corner_radius)
        offset_x = utility.Value(offset_x)
        offset_y = utility.Value(offset_y)
        rotation = utility.Value(rotation)

        pad_offset_x = utility.Value(pad_offset_x)
        pad_offset_y = utility.Value(pad_offset_y)
        pad_rotation = utility.Value(pad_rotation)
        anti_pad_x_size = utility.Value(anti_pad_x_size)
        anti_pad_y_size = utility.Value(anti_pad_y_size)
        padstackData.set_hole_parameters(type_geom=pad_type, sizes=[holediam], offset_x=offset_x, offset_y=offset_y,
                                         rotation=rotation)
        padstackData.plating_percentage = utility.Value(20.0)
        if hole_range == "through":
            padstackData.hole_range = definition.PadstackHoleRange.THROUGH
        elif hole_range == "begin_on_upper_pad":
            padstackData.hole_range = definition.PadstackHoleRange.BEGIN_ON_UPPER_PAD
        elif hole_range == "end_on_lower_pad":
            padstackData.hole_range = definition.PadstackHoleRange.END_ON_LOWER_PAD
        elif hole_range == "upper_pad_to_lower_pad":  # pragma no cover
            padstackData.hole_range = definition.PadstackHoleRange.UPPER_PAD_TO_LOWER_PAD
        else:  # pragma no cover
            self._logger.error("Unknown padstack hole range")
        padstackData.material = "copper"
        layers = list(self._pedb.stackup.signal_layers.keys())[:]
        if start_layer and start_layer in layers:
            layers = layers[layers.index(start_layer):]
        if stop_layer and stop_layer in layers:
            layers = layers[: layers.index(stop_layer) + 1]
        pad_array = [paddiam]
        if pad_shape == "Circle":
            pad_shape = definition.PadGeometryType.PADGEOMTYPE_CIRCLE
        elif pad_shape == "Rectangle":
            pad_array = [x_size, y_size]
            pad_shape = definition.PadGeometryType.PADGEOMTYPE_RECTANGLE
        if antipad_shape == "Bullet":
            antipad_array = [x_size, y_size, corner_radius]
            antipad_shape = definition.PadGeometryType.PADGEOMTYPE_BULLET
        elif antipad_shape == "Rectangle":
            antipad_array = [anti_pad_x_size, anti_pad_y_size]
            antipad_shape = definition.PadGeometryType.PADGEOMTYPE_RECTANGLE
        else:
            antipad_array = [antipaddiam]
            antipad_shape = definition.PadGeometryType.PADGEOMTYPE_CIRCLE
        if add_default_layer:
            layers = layers + ["Default"]
        for layer in layers:
            padstackData.set_pad_parameters(
                layer=layer,
                pad_type=definition.PadType.REGULAR_PAD,
                type_geom=pad_shape,
                sizes=pad_array,
                offset_x=pad_offset_x,
                offset_y=pad_offset_y,
                rotation=pad_rotation,
            )

            padstackData.set_pad_parameters(
                layer=layer,
                pad_type=definition.PadType.ANTI_PAD,
                type_geom=antipad_shape,
                sizes=antipad_array,
                offset_x=offset_x,
                offset_y=offset_y,
                rotation=rotation,
            )

        padstackDefinition = definition.PadstackDef.create(self.db, padstackname)
        padstackDefinition.data = padstackData
        self._logger.info("Padstack %s create correctly", padstackname)
        return padstackname

    @pyedb_function_handler()
    def _get_pin_layer_range(self, pin):
        res, fromlayer, tolayer = pin.layerRange
        if res:
            return fromlayer, tolayer
        else:
            return False

    @pyedb_function_handler()
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
        p1 = self.definitions[target_padstack_name].edb_padstack.data
        new_padstack_definition_data = definition.PadstackDefData(p1)

        if not new_padstack_name:
            new_padstack_name = generate_unique_name(target_padstack_name)

        padstack_definition = definition.PadstackDef.create(self.db, new_padstack_name)
        padstack_definition.data = new_padstack_definition_data

        return new_padstack_name

    @pyedb_function_handler()
    def place(
            self,
            position,
            definition_name,
            net_name="pyedb_default",
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
        :class:`pyaedt.edb_core.edb_data.padstacks_data.EDBPadstackInstance`
        """
        padstack = None
        for pad in list(self.definitions.keys()):
            if pad == definition_name:
                padstack = self.definitions[pad].edb_padstack
        position = geometry.PointData(position[0], position[1])
        net = self._pedb.nets.find_or_create_net(net_name)
        rotation = utility.Value(rotation * math.pi / 180)
        sign_layers_values = {i: v for i, v in self._pedb.stackup.signal_layers.items()}
        sign_layers = list(sign_layers_values.keys())
        if not fromlayer:
            try:
                fromlayer = sign_layers_values[list(self.definitions[pad].pad_by_layer.keys())[0]]._edb_layer
            except KeyError:
                fromlayer = sign_layers_values[sign_layers[0]]._edb_layer
        else:
            fromlayer = sign_layers_values[fromlayer]._edb_layer

        if not tolayer:
            try:
                tolayer = sign_layers_values[list(self.definitions[pad].pad_by_layer.keys())[-1]]._edb_layer
            except KeyError:
                tolayer = sign_layers_values[sign_layers[-1]]._edb_layer
        else:
            tolayer = sign_layers_values[tolayer]._edb_layer
        if solderlayer:
            solderlayer = sign_layers_values[solderlayer]._edb_layer
        if padstack:
            padstack_instance = primitive.PadstackInstance.create(layout=self._active_layout,
                                                                  net=net,
                                                                  name=via_name,
                                                                  padstack_def=padstack,
                                                                  top_layer=fromlayer,
                                                                  bottom_layer=tolayer,
                                                                  solder_ball_layer=solderlayer,
                                                                  rotation=0.0,
                                                                  layer_map=None)
            padstack_instance.set_position_and_rotation(position.x, position.y, rotation)
            padstack_instance.is_layout_pin = is_pin
            pyedb_padstack_instance = EDBPadstackInstance(padstack_instance, self._pedb)
            return pyedb_padstack_instance
        else:
            return False

    @pyedb_function_handler()
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
        pad_type = definition.PadType.REGULAR_PAD
        pad_geo = definition.PadGeometryType.PADGEOMTYPE_CIRCLE
        vals = utility.Value(0)
        params = [utility.Value(0)]
        p1 = self.definitions[padstack_name].edb_padstack.data
        newPadstackDefinitionData = definition.PadstackDefData(p1)

        if not layer_name:
            layer_name = list(self._pedb.stackup.signal_layers.keys())
        elif isinstance(layer_name, str):
            layer_name = [layer_name]
        for lay in layer_name:
            newPadstackDefinitionData.set_pad_parameters(layer=lay,
                                                         pad_type=pad_type,
                                                         type_geom=pad_geo,
                                                         sizes=[utility.Value(0)],
                                                         offset_x=utility.Value(0),
                                                         offset_y=utility.Value(0),
                                                         rotation=utility.Value(0))

        self.definitions[padstack_name].edb_padstack.data = newPadstackDefinitionData
        return True

    @pyedb_function_handler()
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
            "Circle": definition.PadGeometryType.PADGEOMTYPE_CIRCLE,
            "Square": definition.PadGeometryType.PADGEOMTYPE_SQUARE,
            "Rectangle": definition.PadGeometryType.PADGEOMTYPE_RECTANGLE,
            "Oval": definition.PadGeometryType.PADGEOMTYPE_OVAL,
            "Bullet": definition.PadGeometryType.PADGEOMTYPE_BULLET,
        }
        pad_shape = shape_dict[pad_shape]
        if not isinstance(pad_params, list):
            pad_params = [pad_params]
        pad_params = [utility.Value(i) for i in pad_params]
        pad_x_offset = utility.Value(pad_x_offset)
        pad_y_offset = utility.Value(pad_y_offset)
        pad_rotation = utility.Value(pad_rotation)

        antipad_shape = shape_dict[antipad_shape]
        if not isinstance(antipad_params, list):
            antipad_params = [antipad_params]
        antipad_params = [utility.Value(i) for i in antipad_params]
        antipad_x_offset = utility.Value(antipad_x_offset)
        antipad_y_offset = utility.Value(antipad_y_offset)
        antipad_rotation = utility.Value(antipad_rotation)

        p1 = self.definitions[padstack_name].edb_padstack.data
        new_padstack_def = definition.PadstackDefData(p1)
        if not layer_name:
            layer_name = list(self._pedb.stackup.signal_layers.keys())
        elif isinstance(layer_name, str):
            layer_name = [layer_name]
        for layer in layer_name:
            new_padstack_def.set_pad_parameters(
                layer=layer,
                pad_type=definition.PadType.REGULAR_PAD,
                type_geom=pad_shape,
                sizes=pad_params,
                offset_x=pad_x_offset,
                offset_y=pad_y_offset,
                rotation=pad_rotation,
            )
            new_padstack_def.set_pad_parameters(
                layer=layer,
                pad_type=definition.PadType.ANTI_PAD,
                type_geom=antipad_shape,
                sizes=antipad_params,
                offset_x=antipad_x_offset,
                offset_y=antipad_y_offset,
                rotation=antipad_rotation,
            )
        self.definitions[padstack_name].edb_padstack.data = new_padstack_def
        return True

    @pyedb_function_handler()
    def get_padstack_instance_by_net_name(self, net_name):
        """Get a list of padstack instances by net name.

        Parameters
        ----------
        net_name : str
            The net name to be used for filtering padstack instances.
        Returns
        -------
        list
            List of :class:`pyaedt.edb_core.edb_data.padstacks_data.EDBPadstackInstance`.
        """
        padstack_instances = []
        for inst_id, inst in self.instances.items():
            if inst.net_name == net_name:
                padstack_instances.append(inst)
        return padstack_instances

    @pyedb_function_handler()
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
            List of :class:`pyaedt.edb_core.edb_data.padstacks_data.EDBPadstackInstance`.

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
            references_pins = self.get_padstack_instance_by_net_name(reference_net)
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
