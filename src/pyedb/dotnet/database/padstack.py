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

"""
This module contains the `EdbPadstacks` class.
"""

from collections import defaultdict
import math
from typing import Dict, List, Optional, Union
import warnings

import numpy as np
import rtree
from scipy.spatial import ConvexHull

from pyedb.dotnet.clr_module import Array
from pyedb.dotnet.database.edb_data.padstacks_data import (
    EDBPadstack,
    EDBPadstackInstance,
)
from pyedb.dotnet.database.general import convert_py_list_to_net_list
from pyedb.dotnet.database.geometry.polygon_data import PolygonData
from pyedb.generic.general_methods import generate_unique_name
from pyedb.modeler.geometry_operators import GeometryOperators


class EdbPadstacks(object):
    """Manages EDB methods for nets management accessible from `Edb.padstacks` property.

    Examples
    --------
    >>> from pyedb import Edb
    >>> edbapp = Edb("myaedbfolder", edbversion="2021.2")
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
    def _edb(self):
        """ """
        return self._pedb.core

    def _get_edb_value(self, value):
        return self._pedb.edb_value(value)

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
            return self._edb.Definition.PadType.RegularPad
        elif val == 1:
            return self._edb.Definition.PadType.AntiPad
        elif val == 2:
            return self._edb.Definition.PadType.ThermalPad
        elif val == 3:
            return self._edb.Definition.PadType.Hole
        elif val == 4:
            return self._edb.Definition.PadType.UnknownGeomType
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
            return self._edb.Definition.PadGeometryType.NoGeometry
        elif val == 1:
            return self._edb.Definition.PadGeometryType.Circle
        elif val == 2:
            return self._edb.Definition.PadGeometryType.Square
        elif val == 3:
            return self._edb.Definition.PadGeometryType.Rectangle
        elif val == 4:
            return self._edb.Definition.PadGeometryType.Oval
        elif val == 5:
            return self._edb.Definition.PadGeometryType.Bullet
        elif val == 6:
            return self._edb.Definition.PadGeometryType.NSidedPolygon
        elif val == 7:
            return self._edb.Definition.PadGeometryType.Polygon
        elif val == 8:
            return self._edb.Definition.PadGeometryType.Round45
        elif val == 9:
            return self._edb.Definition.PadGeometryType.Round90
        elif val == 10:
            return self._edb.Definition.PadGeometryType.Square45
        elif val == 11:
            return self._edb.Definition.PadGeometryType.Square90
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
        if len(self._definitions) == len(list(self._pedb._db.PadstackDefs)):
            return self._definitions
        self._definitions = {}
        for padstackdef in list(self._pedb._db.PadstackDefs):
            PadStackData = padstackdef.GetData()
            if len(PadStackData.GetLayerNames()) >= 1:
                self._definitions[padstackdef.GetName()] = EDBPadstack(padstackdef, self)
        return self._definitions

    @property
    def padstacks(self):
        """Padstacks via padstack definitions.

        .. deprecated:: 0.6.58
        Use :func:`definitions` property instead.

        Returns
        -------
        dict[str, :class:`pyedb.dotnet.database.edb_data.EdbPadstack`]
            List of definitions via padstack definitions.

        """
        warnings.warn("Use `definitions` property instead.", DeprecationWarning)
        return self.definitions

    @property
    def instances(self):
        """Dictionary  of all padstack instances (vias and pins).

        Returns
        -------
        dict[int, :class:`dotnet.database.edb_data.padstacks_data.EDBPadstackInstance`]
            List of padstack instances.

        """
        edb_padstack_inst_list = self._pedb.layout.padstack_instances
        if len(self._instances) == len(edb_padstack_inst_list):
            return self._instances
        self._instances = {i.id: i for i in edb_padstack_inst_list}
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
    def padstack_instances(self):
        """List of padstack instances.

        .. deprecated:: 0.6.58
        Use :func:`instances` property instead.

        Returns
        -------
        dict[str, :class:`dotnet.database.edb_data.padstacks_data.EDBPadstackInstance`]
            List of padstack instances.
        """

        warnings.warn("Use `instances` property instead.", DeprecationWarning)
        return self.instances

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

        class PadType:
            (RegularPad, AntiPad, ThermalPad, Hole, UnknownGeomType) = (
                self._edb.Definition.PadType.RegularPad,
                self._edb.Definition.PadType.AntiPad,
                self._edb.Definition.PadType.ThermalPad,
                self._edb.Definition.PadType.Hole,
                self._edb.Definition.PadType.UnknownGeomType,
            )

        return PadType

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

        PadStack = self._edb.Definition.PadstackDef.Create(self._layout.cell.GetDatabase(), padstackname)
        new_PadStackData = self._edb.Definition.PadstackDefData.Create()
        list_values = convert_py_list_to_net_list(
            [self._get_edb_value(holediam), self._get_edb_value(paddiam), self._get_edb_value(antipaddiam)]
        )
        value0 = self._get_edb_value(0.0)
        new_PadStackData.SetHoleParameters(
            self._edb.Definition.PadGeometryType.Circle,
            list_values,
            value0,
            value0,
            value0,
        )
        new_PadStackData.SetHoleRange(self._edb.Definition.PadstackHoleRange.UpperPadToLowerPad)
        layers = list(self._pedb.stackup.signal_layers.keys())
        if not startlayer:
            startlayer = layers[0]
        if not endlayer:
            endlayer = layers[len(layers) - 1]

        antipad_shape = self._edb.Definition.PadGeometryType.Circle
        started = False
        new_PadStackData.SetPadParameters(
            "Default",
            self._edb.Definition.PadType.RegularPad,
            self._edb.Definition.PadGeometryType.Circle,
            convert_py_list_to_net_list([self._get_edb_value(paddiam)]),
            value0,
            value0,
            value0,
        )

        new_PadStackData.SetPadParameters(
            "Default",
            self._edb.Definition.PadType.AntiPad,
            antipad_shape,
            convert_py_list_to_net_list([self._get_edb_value(antipaddiam)]),
            value0,
            value0,
            value0,
        )
        for layer in layers:
            if layer == startlayer:
                started = True
            if layer == endlayer:
                started = False
            if started:
                new_PadStackData.SetPadParameters(
                    layer,
                    self._edb.Definition.PadType.RegularPad,
                    self._edb.Definition.PadGeometryType.Circle,
                    convert_py_list_to_net_list([self._get_edb_value(paddiam)]),
                    value0,
                    value0,
                    value0,
                )
                new_PadStackData.SetPadParameters(
                    layer,
                    self._edb.Definition.PadType.AntiPad,
                    antipad_shape,
                    convert_py_list_to_net_list([self._get_edb_value(antipaddiam)]),
                    value0,
                    value0,
                    value0,
                )
        PadStack.SetData(new_PadStackData)

    def create_dielectric_filled_backdrills(
        self,
        layer: str,
        diameter: Union[float, str],
        material: str,
        permittivity: float,
        padstack_instances: Optional[List[EDBPadstackInstance]] = None,
        padstack_definition: Optional[Union[str, List[str]]] = None,
        dielectric_loss_tangent: Optional[float] = None,
        nets: Optional[Union[str, List[str]]] = None,
    ) -> bool:
        r"""Create dielectric-filled back-drills for through-hole vias.

        Back-drilling (a.k.a. controlled-depth drilling) is used to remove the
        unused via stub that acts as an unterminated transmission-line segment,
        thereby improving signal-integrity at high frequencies.  This routine
        goes one step further: after the stub is removed the resulting cylindrical
        cavity is **completely filled** with a user-specified dielectric.  The
        fill material restores mechanical rigidity, prevents solder-wicking, and
        keeps the original via’s electrical characteristics intact on the
        remaining, still-plated, portion.

        Selection criteria
        ------------------
        A via is processed only when **all** of the following are true:

        1. It is a through-hole structure (spans at least three metal layers).
        2. It includes the requested ``layer`` somewhere in its layer span.
        3. It belongs to one of the supplied ``padstack_definition`` names
           (or to *any* definition if the argument is omitted).
        4. It is attached to one of the supplied ``nets`` (or to *any* net if
           the argument is omitted).

        Geometry that is created
        ------------------------
        For every qualified via the routine

        * Generates a new pad-stack definition named ``<original_name>_BD``.
          The definition is drilled from the **bottom-most signal layer** up to
          and **including** ``layer``, uses the exact ``diameter`` supplied, and
          is plated at 100 %.
        * Places an additional pad-stack instance on top of the original via,
          thereby filling the newly drilled cavity with the requested
          ``material``.
        * Leaves the original via untouched—only its unused stub is removed.

        The back-drill is **not** subtracted from anti-pads or plane clearances;
        the filling material is assumed to be electrically invisible at the
        frequencies of interest.

        Parameters
        ----------
        layer : :class:`str`
            Signal layer name up to which the back-drill is performed (inclusive).
            The drill always starts on the bottom-most signal layer of the stack-up.
        diameter : :class:`float` or :class:`str`
            Finished hole diameter for the back-drill.  A numeric value is
            interpreted in the database length unit; a string such as
            ``"0.3mm"`` is evaluated with units.
        material : :class:`str`
            Name of the dielectric material that fills the drilled cavity.  If the
            material does not yet exist in the central material library it is
            created on the fly.
        permittivity : :class:`float`
            Relative permittivity :math:`\varepsilon_{\mathrm{r}}` used when the
            material has to be created.  Must be positive.
        padstack_instances : :class:`list` [:class:`PadstackInstance` ], optional
            Explicit list of via instances to process.  When provided,
            ``padstack_definition`` and ``nets`` are ignored for filtering.
        padstack_definition : :class:`str` or :class:`list` [:class:`str` ], optional
            Pad-stack definition(s) to process.  If omitted, **all** through-hole
            definitions are considered.
        dielectric_loss_tangent : :class:`float`, optional
            Loss tangent :math:`\tan\delta` used when the material has to be
            created.  Defaults to ``0.0``.
        nets : :class:`str` or :class:`list` [:class:`str` ], optional
            Net name(s) used to filter vias.  If omitted, vias belonging to
            **any** net are processed.

        Returns
        -------
        :class:`bool`
            ``True`` when at least one back-drill was successfully created.
            ``False`` if no suitable via was found or any error occurred.

        Raises
        ------
        ValueError
            If ``material`` is empty or if ``permittivity`` is non-positive when a
            new material must be created.

        Notes
        -----
        * The routine is safe to call repeatedly: existing back-drills are **not**
          duplicated because the ``*_BD`` definition name is deterministic.
        * The original via keeps its pad-stack definition and net assignment; only
          its unused stub is removed.
        * The back-drill is **not** subtracted from anti-pads or plane clearances;
          the filling material is assumed to be electrically invisible at the
          frequencies of interest.

        Examples
        --------
        Create back-drills on all vias belonging to two specific pad-stack
        definitions and two DDR4 nets:

        >>> edb.padstacks.create_dielectric_filled_backdrills(
        ...     layer="L3",
        ...     diameter="0.25mm",
        ...     material="EPON_827",
        ...     permittivity=3.8,
        ...     dielectric_loss_tangent=0.015,
        ...     padstack_definition=["VIA_10MIL", "VIA_16MIL"],
        ...     nets=["DDR4_DQ0", "DDR4_DQ1"],
        ... )
        True
        """
        _padstack_instances = defaultdict(list)
        if padstack_instances:
            for inst in padstack_instances:
                _padstack_instances[inst.padstack_definition].append(inst)
        else:
            if padstack_definition:
                if isinstance(padstack_definition, str):
                    padstack_definition = [padstack_definition]

                padstack_definitions = [
                    self.definitions.get(padstack_def, None) for padstack_def in padstack_definition
                ]
                if nets:
                    if isinstance(nets, str):
                        nets = [nets]
                    for padstack_definition in padstack_definitions:
                        _padstack_instances[padstack_definition.name] = self.get_instances(
                            definition_name=padstack_definition.name, net_name=nets
                        )
                else:
                    for padstack_definition in padstack_definitions:
                        _padstack_instances[padstack_definition.name] = padstack_definition.instances
            elif nets:
                instances = self.get_instances(net_name=nets)
                for inst in instances:
                    padsatck_def_name = inst.padstack_definition
                    padstack_def_layers = inst.layer_range_names
                    if layer in padstack_def_layers and len(padstack_def_layers) >= 3:
                        if not padsatck_def_name in _padstack_instances:
                            _padstack_instances[padsatck_def_name] = [inst]
                        else:
                            _padstack_instances[padsatck_def_name].append(inst)
                    else:
                        self._pedb.logger.info(
                            f"Drill layer {layer} not in padstack definition layers "
                            f"or layer number = {len(padstack_def_layers)} "
                            f"for padstack definition {padsatck_def_name}, skipping for backdrills"
                        )
        if not material:
            raise ValueError("`material` must be specified")
        if not material in self._pedb.materials:
            if not dielectric_loss_tangent:
                dielectric_loss_tangent = 0.0
            self._pedb.materials.add_dielectric_material(
                name=material, permittivity=permittivity, dielectric_loss_tangent=dielectric_loss_tangent
            )
        for def_name, instances in _padstack_instances.items():
            padstack_def_backdrill_name = f"{def_name}_BD"
            start_layer = list(self._pedb.stackup.signal_layers.keys())[-1]  # bottom layer
            self.create(
                padstackname=padstack_def_backdrill_name,
                holediam=self._pedb.value(diameter),
                paddiam="0.0",
                antipaddiam="0.0",
                start_layer=start_layer,
                stop_layer=layer,
            )
            self.definitions[padstack_def_backdrill_name].material = material
            self.definitions[padstack_def_backdrill_name].hole_plating_ratio = 100.0
            for inst in instances:
                inst.set_back_drill_by_layer(drill_to_layer=layer, offset=0.0, diameter=self._pedb.value(diameter))
                self.place(
                    position=inst.position,
                    definition_name=padstack_def_backdrill_name,
                    fromlayer=start_layer,
                    tolayer=layer,
                )
        return True

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
            padstackInst = self.instances[padstackInst]._edb_padstackinstance

        else:
            psdef = padstackInst._edb_object.GetPadstackDef()
        newdefdata = self._edb.Definition.PadstackDefData(psdef.GetData())
        newdefdata.SetSolderBallShape(self._edb.Definition.SolderballShape.Cylinder)
        newdefdata.SetSolderBallParameter(self._get_edb_value(ballDiam), self._get_edb_value(ballDiam))
        sball_placement = (
            self._edb.Definition.SolderballPlacement.AbovePadstack
            if isTopPlaced
            else self._edb.Definition.SolderballPlacement.BelowPadstack
        )
        newdefdata.SetSolderBallPlacement(sball_placement)
        psdef.SetData(newdefdata)
        sball_layer = [lay._edb_layer for lay in list(self._layers.values()) if lay.name == sballLayer_name][0]
        if sball_layer is not None:
            padstackInst._edb_object.SetSolderBallLayer(sball_layer)
            return True

        return False

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
        cmp_name = padstackinstance.GetComponent().GetName()
        if cmp_name == "":
            cmp_name = "no_comp"
        net_name = padstackinstance.GetNet().GetName()
        if net_name == "":
            net_name = "no_net"
        pin_name = padstackinstance.GetName()
        if pin_name == "":
            pin_name = "no_pin_name"
        if use_dot_separator:
            port_name = "{0}.{1}.{2}".format(cmp_name, pin_name, net_name)
        else:
            port_name = "{0}_{1}_{2}".format(cmp_name, pin_name, net_name)
        if not padstackinstance.IsLayoutPin():
            padstackinstance.SetIsLayoutPin(True)
        res = padstackinstance.GetLayerRange()
        if name:
            port_name = name
        if self._port_exist(port_name):
            port_name = generate_unique_name(port_name, n=2)
            self._logger.info("An existing port already has this same name. Renaming to {}.".format(port_name))
        self._edb.Cell.Terminal.PadstackInstanceTerminal.Create(
            self._active_layout,
            padstackinstance.GetNet(),
            port_name,
            padstackinstance,
            res[2],
        )
        if res[0]:
            return port_name
        return ""

    def _port_exist(self, port_name):
        return any(port for port in list(self._pedb.excitations.keys()) if port == port_name)

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

        if "PadstackDef" in str(type(pin)):
            padparams = pin.GetData().GetPadParametersValue(layername, self.int_to_pad_type(pad_type))
        else:
            if not isinstance(pin, EDBPadstackInstance):
                pin = EDBPadstackInstance(pin, self._pedb)
            padparams = self._edb.Definition.PadstackDefData(
                pin._edb_object.GetPadstackDef().GetData()
            ).GetPadParametersValue(layername, self.int_to_pad_type(pad_type))
        if padparams[2]:
            geometry_type = int(padparams[1])
            parameters = [i.ToString() for i in padparams[2]]
            offset_x = padparams[3].ToDouble()
            offset_y = padparams[4].ToDouble()
            rotation = padparams[5].ToDouble()
            return geometry_type, parameters, offset_x, offset_y, rotation
        else:
            if isinstance(pin, self._edb.Definition.PadstackDef):
                padparams = self._edb.Definition.PadstackDefData(pin.GetData()).GetPolygonalPadParameters(
                    layername, self.int_to_pad_type(pad_type)
                )
            else:
                padparams = self._edb.Definition.PadstackDefData(
                    pin._edb_object.GetPadstackDef().GetData()
                ).GetPolygonalPadParameters(layername, self.int_to_pad_type(pad_type))

            if padparams[0]:
                parameters = [
                    padparams[1].GetBBox().Item1.X.ToDouble(),
                    padparams[1].GetBBox().Item1.Y.ToDouble(),
                    padparams[1].GetBBox().Item2.X.ToDouble(),
                    padparams[1].GetBBox().Item2.Y.ToDouble(),
                ]
                offset_x = padparams[2]
                offset_y = padparams[3]
                rotation = padparams[4]
                geometry_type = 7
                return geometry_type, parameters, offset_x, offset_y, rotation
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
            for padstack in list(self.definitions.values()):
                cloned_padstack_data = self._edb.Definition.PadstackDefData(padstack.edb_padstack.GetData())
                layers_name = cloned_padstack_data.GetLayerNames()
                all_succeed = True
                for layer in layers_name:
                    geom_type, parameters, offset_x, offset_y, rot = self.get_pad_parameters(
                        padstack.edb_padstack, layer, 1
                    )
                    if geom_type == 1:  # pragma no cover
                        params = convert_py_list_to_net_list(
                            [self._pedb.edb_value(value)] * len(parameters)
                        )  # pragma no cover
                        geom = self._edb.Definition.PadGeometryType.Circle
                        offset_x = self._pedb.edb_value(offset_x)
                        offset_y = self._pedb.edb_value(offset_y)
                        rot = self._pedb.edb_value(rot)
                        antipad = self._edb.Definition.PadType.AntiPad
                        if cloned_padstack_data.SetPadParameters(
                            layer, antipad, geom, params, offset_x, offset_y, rot
                        ):  # pragma no cover
                            self._logger.info(
                                "Pad-stack definition {}, anti-pad on layer {}, has been set to {}".format(
                                    padstack.edb_padstack.GetName(), layer, str(value)
                                )
                            )
                        else:  # pragma no cover
                            self._logger.error(
                                "Failed to reassign anti-pad value {} on Pads-stack definition {}, layer{}".format(
                                    str(value), padstack.edb_padstack.GetName(), layer
                                )
                            )
                            all_succeed = False
                padstack.edb_padstack.SetData(cloned_padstack_data)
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
        if net_list == None:
            net_list = []

        if not isinstance(net_list, list):
            net_list = [net_list]
        layout_lobj_collection = self._layout.padstack_instances
        layout_lobj_collection = [i._edb_object for i in layout_lobj_collection]
        via_list = []
        for lobj in layout_lobj_collection:
            pad_layers_name = lobj.GetPadstackDef().GetData().GetLayerNames()
            if len(pad_layers_name) > 1:
                if not net_list:
                    via_list.append(lobj)
                elif lobj.GetNet().GetName() in net_list:
                    via_list.append(lobj)
        return via_list

    def create_padstack(
        self,
        padstackname=None,
        holediam="300um",
        paddiam="400um",
        antipaddiam="600um",
        startlayer=None,
        endlayer=None,
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
    ):  # pragma: no cover
        """Create a padstack.

        .. deprecated:: 0.6.62
        Use :func:`create` method instead.

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
        antipad_shape : str, optional
            Shape of the antipad. The default is ``"Circle"``. Options are ``"Circle"`` and ``"Bullet"``.
        x_size : str, optional
            Only applicable to bullet shape. The default is ``"600um"``.
        y_size : str, optional
            Only applicable to bullet shape. The default is ``"600um"``.
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

        Returns
        -------
        str
            Name of the padstack if the operation is successful.
        """
        warnings.warn("Use :func:`create` method instead.", DeprecationWarning)
        return self.create(
            padstackname=padstackname,
            holediam=holediam,
            paddiam=paddiam,
            antipaddiam=antipaddiam,
            antipad_shape=antipad_shape,
            x_size=x_size,
            y_size=y_size,
            corner_radius=corner_radius,
            offset_x=offset_x,
            offset_y=offset_y,
            rotation=rotation,
            has_hole=has_hole,
            pad_offset_x=pad_offset_x,
            pad_offset_y=pad_offset_y,
            pad_rotation=pad_rotation,
        )

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
        holediam = self._get_edb_value(holediam)
        paddiam = self._get_edb_value(paddiam)
        antipaddiam = self._get_edb_value(antipaddiam)
        layers = list(self._pedb.stackup.signal_layers.keys())[:]
        value0 = self._get_edb_value("0.0")
        if not padstackname:
            padstackname = generate_unique_name("VIA")
        # assert not self.isreadonly, "Write Functions are not available within AEDT"
        padstackData = self._edb.Definition.PadstackDefData.Create()
        if has_hole and not polygon_hole:
            ptype = self._edb.Definition.PadGeometryType.Circle
            hole_param = Array[type(holediam)]([holediam])
            padstackData.SetHoleParameters(ptype, hole_param, value0, value0, value0)
            padstackData.SetHolePlatingPercentage(self._get_edb_value(20.0))
        elif polygon_hole:
            if isinstance(polygon_hole, list):
                _poly = self._pedb.modeler.create_polygon(polygon_hole, layers[0], net_name="dummy")
                if not _poly.is_null:
                    hole_param = _poly.polygon_data
                    _poly.delete()
                else:
                    return False
            elif isinstance(polygon_hole, PolygonData):
                hole_param = polygon_hole._edb_object
            else:
                return False
            padstackData.SetPolygonalHoleParameters(hole_param, value0, value0, value0)
            padstackData.SetHolePlatingPercentage(self._get_edb_value(20.0))
        else:
            ptype = self._edb.Definition.PadGeometryType.NoGeometry

        x_size = self._get_edb_value(x_size)
        y_size = self._get_edb_value(y_size)
        corner_radius = self._get_edb_value(corner_radius)
        offset_x = self._get_edb_value(offset_x)
        offset_y = self._get_edb_value(offset_y)
        rotation = self._get_edb_value(rotation)

        pad_offset_x = self._get_edb_value(pad_offset_x)
        pad_offset_y = self._get_edb_value(pad_offset_y)
        pad_rotation = self._get_edb_value(pad_rotation)
        anti_pad_x_size = self._get_edb_value(anti_pad_x_size)
        anti_pad_y_size = self._get_edb_value(anti_pad_y_size)

        if hole_range == "through":  # pragma no cover
            padstackData.SetHoleRange(self._edb.Definition.PadstackHoleRange.Through)
        elif hole_range == "begin_on_upper_pad":  # pragma no cover
            padstackData.SetHoleRange(self._edb.Definition.PadstackHoleRange.BeginOnUpperPad)
        elif hole_range == "end_on_lower_pad":  # pragma no cover
            padstackData.SetHoleRange(self._edb.Definition.PadstackHoleRange.EndOnLowerPad)
        elif hole_range == "upper_pad_to_lower_pad":  # pragma no cover
            padstackData.SetHoleRange(self._edb.Definition.PadstackHoleRange.UpperPadToLowerPad)
        else:  # pragma no cover
            self._logger.error("Unknown padstack hole range")
        padstackData.SetMaterial("copper")

        if start_layer and start_layer in layers:  # pragma no cover
            layers = layers[layers.index(start_layer) :]
        if stop_layer and stop_layer in layers:  # pragma no cover
            layers = layers[: layers.index(stop_layer) + 1]
        pad_array = Array[type(paddiam)]([paddiam])
        if pad_shape == "Circle":  # pragma no cover
            pad_shape = self._edb.Definition.PadGeometryType.Circle
        elif pad_shape == "Rectangle":  # pragma no cover
            pad_array = Array[type(x_size)]([x_size, y_size])
            pad_shape = self._edb.Definition.PadGeometryType.Rectangle
        elif pad_shape == "Polygon":
            if isinstance(pad_polygon, list):
                _poly = self._pedb.modeler.create_polygon(pad_polygon, layers[0], net_name="dummy")
                if not _poly.is_null:
                    pad_array = _poly.polygon_data
                    _poly.delete()
                else:
                    return False
            elif isinstance(pad_polygon, PolygonData):
                pad_array = pad_polygon
        if antipad_shape == "Bullet":  # pragma no cover
            antipad_array = Array[type(x_size)]([x_size, y_size, corner_radius])
            antipad_shape = self._edb.Definition.PadGeometryType.Bullet
        elif antipad_shape == "Rectangle":  # pragma no cover
            antipad_array = Array[type(anti_pad_x_size)]([anti_pad_x_size, anti_pad_y_size])
            antipad_shape = self._edb.Definition.PadGeometryType.Rectangle
        elif antipad_shape == "Polygon":
            if isinstance(antipad_polygon, list):
                _poly = self._pedb.modeler.create_polygon(antipad_polygon, layers[0], net_name="dummy")
                if not _poly.is_null:
                    antipad_array = _poly.polygon_data
                    _poly.delete()
                else:
                    return False
            elif isinstance(antipad_polygon, PolygonData):
                antipad_array = antipad_polygon
        else:  # pragma no cover
            antipad_array = Array[type(antipaddiam)]([antipaddiam])
            antipad_shape = self._edb.Definition.PadGeometryType.Circle
        if add_default_layer:  # pragma no cover
            layers = layers + ["Default"]
        if antipad_shape == "Polygon" and pad_shape == "Polygon":
            for layer in layers:
                padstackData.SetPolygonalPadParameters(
                    layer,
                    self._edb.Definition.PadType.RegularPad,
                    pad_array._edb_object,
                    pad_offset_x,
                    pad_offset_y,
                    pad_rotation,
                )
                padstackData.SetPolygonalPadParameters(
                    layer,
                    self._edb.Definition.PadType.AntiPad,
                    antipad_array._edb_object,
                    pad_offset_x,
                    pad_offset_y,
                    pad_rotation,
                )
        else:
            for layer in layers:
                padstackData.SetPadParameters(
                    layer,
                    self._edb.Definition.PadType.RegularPad,
                    pad_shape,
                    pad_array,
                    pad_offset_x,
                    pad_offset_y,
                    pad_rotation,
                )

                padstackData.SetPadParameters(
                    layer,
                    self._edb.Definition.PadType.AntiPad,
                    antipad_shape,
                    antipad_array,
                    offset_x,
                    offset_y,
                    rotation,
                )

        padstackDefinition = self._edb.Definition.PadstackDef.Create(self.db, padstackname)
        padstackDefinition.SetData(padstackData)
        self._logger.info("Padstack %s create correctly", padstackname)
        return padstackname

    def _get_pin_layer_range(self, pin):
        res, fromlayer, tolayer = pin._edb_object.GetLayerRange()
        if res:
            return fromlayer, tolayer
        else:
            return False

    def duplicate_padstack(self, target_padstack_name, new_padstack_name=""):
        """Duplicate a padstack.

        .. deprecated:: 0.6.62
        Use :func:`duplicate` method instead.

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
        warnings.warn("Use :func:`create` method instead.", DeprecationWarning)
        return self.duplicate(target_padstack_name=target_padstack_name, new_padstack_name=new_padstack_name)

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
        p1 = self.definitions[target_padstack_name].edb_padstack.GetData()
        new_padstack_definition_data = self._edb.Definition.PadstackDefData(p1)

        if not new_padstack_name:
            new_padstack_name = generate_unique_name(target_padstack_name)

        padstack_definition = self._edb.Definition.PadstackDef.Create(self.db, new_padstack_name)
        padstack_definition.SetData(new_padstack_definition_data)

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
        rotation : float, str, optional
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
        padstack = None
        for pad in list(self.definitions.keys()):
            if pad == definition_name:
                padstack = self.definitions[pad].edb_padstack
        # position = self._edb.Geometry.PointData(position[0], position[1])
        position = self._pedb.pedb_class.database.geometry.point_data.PointData.create_from_xy(self._pedb, *position)
        net = self._pedb.nets.find_or_create_net(net_name)
        rotation = (
            self._get_edb_value(rotation * math.pi / 180)
            if not isinstance(rotation, str)
            else self._get_edb_value(rotation)
        )
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
            padstack_instance = self._edb.Cell.Primitive.PadstackInstance.Create(
                self._active_layout,
                net._edb_object,
                via_name,
                padstack,
                position._edb_object,
                rotation,
                fromlayer,
                tolayer,
                solderlayer,
                None,
            )
            padstack_instance.SetIsLayoutPin(is_pin)
            py_padstack_instance = EDBPadstackInstance(padstack_instance, self._pedb)

            return py_padstack_instance
        else:
            return False

    def place_padstack(
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
        """Place the padstack.

        .. deprecated:: 0.6.62
        Use :func:`place` method instead.

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

        Returns
        -------

        """
        warnings.warn(" Use :func:`place` method instead.", DeprecationWarning)
        return self.place(
            position=position,
            definition_name=definition_name,
            net_name=net_name,
            via_name=via_name,
            rotation=rotation,
            fromlayer=fromlayer,
            tolayer=tolayer,
            solderlayer=solderlayer,
            is_pin=is_pin,
        )

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
        pad_type = self._edb.Definition.PadType.RegularPad
        pad_geo = self._edb.Definition.PadGeometryType.Circle
        vals = self._get_edb_value(0)
        params = convert_py_list_to_net_list([self._get_edb_value(0)])
        p1 = self.definitions[padstack_name].edb_padstack.GetData()
        newPadstackDefinitionData = self._edb.Definition.PadstackDefData(p1)

        if not layer_name:
            layer_name = list(self._pedb.stackup.signal_layers.keys())
        elif isinstance(layer_name, str):
            layer_name = [layer_name]
        for lay in layer_name:
            newPadstackDefinitionData.SetPadParameters(lay, pad_type, pad_geo, params, vals, vals, vals)

        self.definitions[padstack_name].edb_padstack.SetData(newPadstackDefinitionData)
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
            "Circle": self._edb.Definition.PadGeometryType.Circle,
            "Square": self._edb.Definition.PadGeometryType.Square,
            "Rectangle": self._edb.Definition.PadGeometryType.Rectangle,
            "Oval": self._edb.Definition.PadGeometryType.Oval,
            "Bullet": self._edb.Definition.PadGeometryType.Bullet,
        }
        pad_shape = shape_dict[pad_shape]
        if not isinstance(pad_params, list):
            pad_params = [pad_params]
        pad_params = convert_py_list_to_net_list([self._get_edb_value(i) for i in pad_params])
        pad_x_offset = self._get_edb_value(pad_x_offset)
        pad_y_offset = self._get_edb_value(pad_y_offset)
        pad_rotation = self._get_edb_value(pad_rotation)

        antipad_shape = shape_dict[antipad_shape]
        if not isinstance(antipad_params, list):
            antipad_params = [antipad_params]
        antipad_params = convert_py_list_to_net_list([self._get_edb_value(i) for i in antipad_params])
        antipad_x_offset = self._get_edb_value(antipad_x_offset)
        antipad_y_offset = self._get_edb_value(antipad_y_offset)
        antipad_rotation = self._get_edb_value(antipad_rotation)

        p1 = self.definitions[padstack_name].edb_padstack.GetData()
        new_padstack_def = self._edb.Definition.PadstackDefData(p1)
        if not layer_name:
            layer_name = list(self._pedb.stackup.signal_layers.keys())
        elif isinstance(layer_name, str):
            layer_name = [layer_name]
        for layer in layer_name:
            new_padstack_def.SetPadParameters(
                layer,
                self._edb.Definition.PadType.RegularPad,
                pad_shape,
                pad_params,
                pad_x_offset,
                pad_y_offset,
                pad_rotation,
            )
            new_padstack_def.SetPadParameters(
                layer,
                self._edb.Definition.PadType.AntiPad,
                antipad_shape,
                antipad_params,
                antipad_x_offset,
                antipad_y_offset,
                antipad_rotation,
            )
        self.definitions[padstack_name].edb_padstack.SetData(new_padstack_def)
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
            return self.instances_by_name[name]
        else:
            instances = list(instances_by_id.values())
            if definition_name:
                definition_name = definition_name if isinstance(definition_name, list) else [definition_name]
                instances = [inst for inst in instances if inst.padstack_definition in definition_name]
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

    def get_padstack_instance_by_net_name(self, net_name):
        """Get a list of padstack instances by net name.

        Parameters
        ----------
        net_name : str
            The net name to be used for filtering padstack instances.

        Returns
        -------
        list
            List of :class:`dotnet.database.edb_data.padstacks_data.EDBPadstackInstance`.
        """
        warnings.warn("Use new property :func:`get_padstack_instance` instead.", DeprecationWarning)
        return self.get_instances(net_name=net_name)

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
            padstack_instances_index.insert(inst.id, inst.position)
        return padstack_instances_index

    def get_padstack_instances_id_intersecting_polygon(self, points, nets=None, padstack_instances_index=None):
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

    def merge_via(self, contour_boxes, net_filter=None, start_layer=None, stop_layer=None):
        """Evaluate padstack instances included on the provided point list and replace all by single instance.

        Parameters
        ----------
        contour_boxes : List[List[List[float, float]]]
            Nested list of polygon with points [x,y].
        net_filter : optional
            List[str: net_name] apply a net filter, nets included in the filter are excluded from the via merge.
        start_layer : optional, str
            Padstack instance start layer, if `None` the top layer is selected.
        stop_layer : optional, str
            Padstack instance stop layer, if `None` the bottom layer is selected.

        Return
        ------
        List[str], list of created padstack instances ID.

        """
        merged_via_ids = []
        if not contour_boxes:
            raise Exception("No contour box provided, you need to pass a nested list as argument.")

        instances_index = {}
        for id, inst in self.instances.items():
            instances_index[id] = inst.position
        for contour_box in contour_boxes:
            all_instances = self.instances
            instances = self.get_padstack_instances_id_intersecting_polygon(
                points=contour_box, padstack_instances_index=instances_index
            )
            if not instances:
                raise Exception(f"No padstack instances found inside {contour_box}")
            else:
                if net_filter:
                    # instances = [id for id in instances if not self.instances[id].net_name in net_filter]
                    instances = [id for id in instances if all_instances[id].net_name not in net_filter]
                # filter instances by start and stop layer
                if start_layer:
                    if start_layer not in self._pedb.stackup.layers.keys():
                        raise Exception(f"{start_layer} not exist")
                    else:
                        instances = [id for id in instances if all_instances[id].start_layer == start_layer]
                if stop_layer:
                    if stop_layer not in self._pedb.stackup.layers.keys():
                        raise Exception(f"{stop_layer} not exist")
                    else:
                        instances = [id for id in instances if all_instances[id].stop_layer == stop_layer]
                if not instances:
                    raise Exception(
                        f"No padstack instances found inside {contour_box} between {start_layer} and {stop_layer}"
                    )

                if not start_layer:
                    start_layer = list(self._pedb.stackup.layers.values())[0].name
                if not stop_layer:
                    stop_layer = list(self._pedb.stackup.layers.values())[-1].name

                net = self.instances[instances[0]].net_name
                x_values = []
                y_values = []
                for inst in instances:
                    pos = instances_index[inst]
                    x_values.append(pos[0])
                    y_values.append(pos[1])
                x_values = list(set(x_values))
                y_values = list(set(y_values))
                if len(x_values) == 1 or len(y_values) == 1:
                    create_instances = self.merge_via_along_lines(
                        net_name=net, padstack_instances_id=instances, minimum_via_number=2
                    )
                    merged_via_ids.extend(create_instances)
                else:
                    instances_pts = np.array([instances_index[id] for id in instances])
                    convex_hull_contour = ConvexHull(instances_pts)
                    contour_points = list(instances_pts[convex_hull_contour.vertices])
                    layer = list(self._pedb.stackup.layers.values())[0].name
                    polygon = self._pedb.modeler.create_polygon(main_shape=contour_points, layer_name=layer)
                    polygon_data = polygon.polygon_data
                    polygon.delete()
                    new_padstack_def = generate_unique_name(self.instances[instances[0]].definition.name)
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
                        raise Exception(f"Failed to create padstack definition {new_padstack_def}")
                    merged_instance = self.place(position=[0, 0], definition_name=new_padstack_def, net_name=net)
                    merged_instance.start_layer = start_layer
                    merged_instance.stop_layer = stop_layer

                    merged_via_ids.append(merged_instance.id)
                    _ = [all_instances[id].delete() for id in instances]
        return merged_via_ids

    def merge_via_along_lines(
        self,
        net_name="GND",
        distance_threshold=5e-3,
        minimum_via_number=6,
        selected_angles=None,
        padstack_instances_id=None,
    ):
        """Replace padstack instances along lines into a single polygon.

        Detect all padstack instances that are placed along lines and replace them by a single polygon based one
        forming a wall shape. This method is designed to simplify meshing on via fence usually added to shield RF traces
        on PCB.

        Parameters
        ----------
        net_name : str
            Net name used for detected padstack instances. Default value is ``"GND"``.

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
         List of padstack instances ID's to include. If `None`, the algorithm will scan all padstack instances belonging
         to the specified net. Default value is `None`.


        Returns
        -------
        bool
            List[int], list of created padstack instances id.

        """
        _def = list(
            set([inst.padstack_definition for inst in list(self.instances.values()) if inst.net_name == net_name])
        )
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
                    [inst for inst in self.definitions[pdstk_def].instances if inst.net_name == net_name]
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
                padstack_def = start_point.padstack_definition
                trace_width = self.definitions[padstack_def].pad_by_layer[stop_point.start_layer].parameters_values[0]
                trace = self._pedb.modeler.create_trace(
                    path_list=[start_point.position, stop_point.position],
                    layer_name=start_point.start_layer,
                    width=trace_width,
                )
                polygon_data = trace.polygon_data
                trace.delete()
                new_padstack_def = generate_unique_name(padstack_def)
                if not self.create(
                    padstackname=new_padstack_def,
                    pad_shape="Polygon",
                    antipad_shape="Polygon",
                    pad_polygon=polygon_data,
                    antipad_polygon=polygon_data,
                    polygon_hole=polygon_data,
                ):
                    self._logger.error(f"Failed to create padstack definition {new_padstack_def}")
                new_instance = self.place(position=[0, 0], definition_name=new_padstack_def, net_name=net_name)
                if not new_instance:
                    self._logger.error(f"Failed to place padstack instance {new_padstack_def}")
                else:
                    instances_created.append(new_instance.id)
            for inst in _instances_to_delete:
                inst.delete()
        return instances_created

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
            net name of list of nets name applying filtering on padstack instances selection. If ``None`` is provided
            all instances are included in the index. Default value is ``None``.

        Returns
        -------
        bool
            ``True`` when succeeded ``False`` when failed. <
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

                all_instances = self.instances
                for item in padstacks_inbox:
                    if item not in to_keep:
                        all_instances[item].delete()

                return True

    @staticmethod
    def dbscan(
        padstack: Dict[int, List[float]], max_distance: float = 1e-3, min_samples: int = 5
    ) -> Dict[int, List[str]]:
        """
        density based spatial clustering for padstack instances

        Parameters
        ----------
        padstack : dict.
            padstack id: [x, y]

        max_distance: float
            maximum distance between two points to be included in one cluster

        min_samples: int
            minimum number of points that a cluster must have

        Returns
        -------
        dict
            clusters {cluster label: [padstack ids]} <
        """

        padstack_ids = list(padstack.keys())
        xy_array = np.array([padstack[pid] for pid in padstack_ids])
        n = len(padstack_ids)

        labels = -1 * np.ones(n, dtype=int)
        visited = np.zeros(n, dtype=bool)
        cluster_id = 0

        def region_query(point_idx):
            distances = np.linalg.norm(xy_array - xy_array[point_idx], axis=1)
            return np.where(distances <= max_distance)[0]

        def expand_cluster(point_idx, neighbors):
            nonlocal cluster_id
            labels[point_idx] = cluster_id
            i = 0
            while i < len(neighbors):
                neighbor_idx = neighbors[i]
                if not visited[neighbor_idx]:
                    visited[neighbor_idx] = True
                    neighbor_neighbors = region_query(neighbor_idx)
                    if len(neighbor_neighbors) >= min_samples:
                        neighbors = np.concatenate((neighbors, neighbor_neighbors))
                if labels[neighbor_idx] == -1:
                    labels[neighbor_idx] = cluster_id
                i += 1

        for point_idx in range(n):
            if visited[point_idx]:
                continue
            visited[point_idx] = True
            neighbors = region_query(point_idx)
            if len(neighbors) < min_samples:
                labels[point_idx] = -1
            else:
                expand_cluster(point_idx, neighbors)
                cluster_id += 1

        # group point IDs by label
        clusters = defaultdict(list)
        for i, label in enumerate(labels):
            clusters[int(label)].append(padstack_ids[i])

        return dict(clusters)

    def reduce_via_by_density(
        self, padstacks: List[int], cell_size_x: float = 1e-3, cell_size_y: float = 1e-3, delete: bool = False
    ) -> tuple[List[int], List[List[List[float]]]]:
        """
        Reduce the number of vias by density. Keep only one via which is closest to the center of the cell. The cells
        are automatically populated based on the input vias.

        Parameters
        ----------
        padstacks: List[int]
            List of padstack ids to be reduced.

        cell_size_x : float
            Width of each grid cell (default is 1e-3).

        cell_size_y : float
            Height of each grid cell (default is 1e-3).

        delete: bool
            If True, delete vias that are not kept (default is False).

        Returns
        -------
        List[int]
            IDs of vias kept after reduction.

        List[List[float]]
            coordinates for grid lines (for plotting).

        """
        to_keep = set()

        all_instances = self.instances
        positions = np.array([all_instances[_id].position for _id in padstacks])

        x_coords, y_coords = positions[:, 0], positions[:, 1]
        x_min, x_max = np.min(x_coords), np.max(x_coords)
        y_min, y_max = np.min(y_coords), np.max(y_coords)

        padstacks_array = np.array(padstacks)
        cell_map = {}  # {(cell_x, cell_y): [(id1, [x1, y1]), (id2, [x2, y2), ...]}
        grid = []

        for idx, pos in enumerate(positions):
            i = int((pos[0] - x_min) // cell_size_x)
            j = int((pos[1] - y_min) // cell_size_y)
            cell_key = (i, j)
            cell_map.setdefault(cell_key, []).append((padstacks_array[idx], pos))

        for (i, j), items in cell_map.items():
            # cell center
            cell_x_min = x_min + i * cell_size_x
            cell_y_min = y_min + j * cell_size_y
            cell_x_mid = cell_x_min + 0.5 * cell_size_x
            cell_y_mid = cell_y_min + 0.5 * cell_size_y

            grid.append(
                [
                    [
                        cell_x_min,
                        cell_x_min + cell_size_x,
                        cell_x_min + cell_size_x,
                        cell_x_min,
                        cell_x_min,
                    ],
                    [
                        cell_y_min,
                        cell_y_min,
                        cell_y_min + cell_size_y,
                        cell_y_min + cell_size_y,
                        cell_y_min,
                    ],
                ]
            )

            # Find closest via to cell center
            distances = [np.linalg.norm(pos - [cell_x_mid, cell_y_mid]) for _, pos in items]
            closest_idx = np.argmin(distances)
            to_keep.add(items[closest_idx][0])

        if delete:
            to_delete = set(padstacks) - to_keep
            for _id in to_delete:
                all_instances[_id].delete()

        return list(to_keep), grid
