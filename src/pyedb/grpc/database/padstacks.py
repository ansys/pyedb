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
from functools import lru_cache
import math
from typing import Any, Dict, List, Optional, Tuple, Union
import warnings

from ansys.edb.core.definition.padstack_def_data import (
    PadGeometryType as GrpcPadGeometryType,
    PadstackDefData as GrpcPadstackDefData,
    PadstackHoleRange as GrpcPadstackHoleRange,
    PadType as GrpcPadType,
    SolderballPlacement as GrpcSolderballPlacement,
    SolderballShape as GrpcSolderballShape,
)
from ansys.edb.core.geometry.point_data import PointData as GrpcPointData
from ansys.edb.core.geometry.polygon_data import PolygonData as GrpcPolygonData
import numpy as np
import rtree

from pyedb.generic.general_methods import generate_unique_name
from pyedb.grpc.database.definition.padstack_def import PadstackDef
from pyedb.grpc.database.primitive.padstack_instance import PadstackInstance
from pyedb.grpc.database.utility.value import Value
from pyedb.modeler.geometry_operators import GeometryOperators

GEOMETRY_MAP = {
    0: GrpcPadGeometryType.PADGEOMTYPE_NO_GEOMETRY,
    1: GrpcPadGeometryType.PADGEOMTYPE_CIRCLE,
    2: GrpcPadGeometryType.PADGEOMTYPE_SQUARE,
    3: GrpcPadGeometryType.PADGEOMTYPE_RECTANGLE,
    4: GrpcPadGeometryType.PADGEOMTYPE_OVAL,
    5: GrpcPadGeometryType.PADGEOMTYPE_BULLET,
    6: GrpcPadGeometryType.PADGEOMTYPE_NSIDED_POLYGON,
    7: GrpcPadGeometryType.PADGEOMTYPE_POLYGON,
    8: GrpcPadGeometryType.PADGEOMTYPE_ROUND45,
    9: GrpcPadGeometryType.PADGEOMTYPE_ROUND90,
    10: GrpcPadGeometryType.PADGEOMTYPE_SQUARE45,
    11: GrpcPadGeometryType.PADGEOMTYPE_SQUARE90,
}

PAD_TYPE_MAP = {
    0: GrpcPadType.REGULAR_PAD,
    1: GrpcPadType.ANTI_PAD,
    2: GrpcPadType.THERMAL_PAD,
    3: GrpcPadType.HOLE,
    4: GrpcPadType.UNKNOWN_GEOM_TYPE,
}


class Padstacks(object):
    """Manages EDB methods for padstacks accessible from `Edb.padstacks` property.

    Examples
    --------
    >>> from pyedb import Edb
    >>> edbapp = Edb("myaedbfolder", edbversion="2024.2")
    >>> edb_padstacks = edbapp.padstacks
    """

    def __getitem__(self, name):
        """Get a padstack definition or instance from the EDB project.

        Parameters
        ----------
        name : str, int
            Name or ID of the padstack definition or instance.

        Returns
        -------
        :class:`pyedb.dotnet.database.definition.padstack_def.PadstackDef` or
        :class:`pyedb.dotnet.database.primitive.padstack_instance.PadstackInstance`
        Requested padstack definition or instance. Returns ``None`` if not found.
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

    def __init__(self, p_edb: Any) -> None:
        self._pedb = p_edb
        self.__definitions: Dict[str, Any] = {}
        self._instances = None
        self._instances_by_name = {}
        self._instances_by_net = {}

    def clear_instances_cache(self):
        """Clear the cached padstack instances."""
        self._instances = None
        self._instances_by_name = {}
        self._instances_by_net = {}

    @property
    def _active_layout(self) -> Any:
        """ """
        return self._pedb.active_layout

    @property
    def _layout(self) -> Any:
        """ """
        return self._pedb.layout

    @property
    def db(self) -> Any:
        """Db object."""
        return self._pedb.active_db

    @property
    def _logger(self) -> Any:
        """ """
        return self._pedb.logger

    @property
    def _layers(self) -> Any:
        """ """
        return self._pedb.stackup.layers

    @staticmethod
    def int_to_pad_type(val=0) -> GrpcPadType:
        """Convert an integer to an EDB.PadGeometryType.

        Parameters
        ----------
        val : int

        Returns
        -------
        object
            EDB.PadType enumerator value.

        Examples
        --------
        >>> pad_type = edb_padstacks.int_to_pad_type(0)  # Returns REGULAR_PAD
        >>> pad_type = edb_padstacks.int_to_pad_type(1)  # Returns ANTI_PAD
        """

        return PAD_TYPE_MAP.get(val, val)

    @staticmethod
    def int_to_geometry_type(val: int = 0) -> GrpcPadGeometryType:
        """Convert an integer to an EDB.PadGeometryType.

        Parameters
        ----------
        val : int

        Returns
        -------
        object
            EDB.PadGeometryType enumerator value.

        Examples
        --------
        >>> geom_type = edb_padstacks.int_to_geometry_type(1)  # Returns CIRCLE
        >>> geom_type = edb_padstacks.int_to_geometry_type(2)  # Returns SQUARE
        """
        return GEOMETRY_MAP.get(val, val)

    @property
    def definitions(self) -> Dict[str, PadstackDef]:
        """Padstack definitions.

        Returns
        -------
        dict[str, :class:`pyedb.grpc.database.definition.padstack_def.PadstackDef`]
            Dictionary of padstack definitions with definition names as keys.

        Examples
        --------
        >>> all_definitions = edb_padstacks.definitions
        >>> for name, definition in all_definitions.items():
        ...     print(f"Padstack: {name}")
        """
        padstack_defs = self._pedb.db.padstack_defs
        self.__definitions = {}
        for padstack_def in padstack_defs:
            if len(padstack_def.data.layer_names) >= 1:
                self.__definitions[padstack_def.name] = PadstackDef(self._pedb, padstack_def)
        return self.__definitions

    @property
    def instances(self) -> Dict[int, PadstackInstance]:
        """All padstack instances (vias and pins) in the layout.

        Returns
        -------
        dict[int, :class:`pyedb.grpc.database.primitive.padstack_instance.PadstackInstance`]
            Dictionary of padstack instances with database IDs as keys.

        Examples
        --------
        >>> all_instances = edb.padstacks.instances
        >>> for id, instance in all_instances.items():
        ...     print(f"Instance {id}: {instance.name}")
        """
        if self._instances is None:
            self._instances = self._pedb.layout.padstack_instances
        return self._instances

    @property
    def instances_by_net(self) -> Dict[Any, PadstackInstance]:
        if not self._instances_by_net:
            for edb_padstack_instance in self.instances.values():
                if edb_padstack_instance.net_name:
                    self._instances_by_net.setdefault(edb_padstack_instance.net_name, []).append(edb_padstack_instance)
        return self._instances_by_net

    @property
    def instances_by_name(self) -> Dict[str, PadstackInstance]:
        """All padstack instances (vias and pins) indexed by name.

        Returns
        -------
        dict[str, :class:`pyedb.grpc.database.primitive.padstack_instance.PadstackInstance`]
            Dictionary of padstack instances with names as keys.

        Examples
        --------
        >>> named_instances = edb_padstacks.instances_by_name
        >>> for name, instance in named_instances.items():
        ...     print(f"Instance named {name}")
        """
        if not self._instances_by_name:
            for _, edb_padstack_instance in self.instances.items():
                if edb_padstack_instance.aedt_name:
                    self._instances_by_name[edb_padstack_instance.aedt_name] = edb_padstack_instance
        return self._instances_by_name

    def find_instance_by_id(self, value: int) -> Optional[PadstackInstance]:
        """Find a padstack instance by database ID.

        Parameters
        ----------
        value : int
            Database ID of the padstack instance.

        Returns
        -------
        :class:`pyedb.grpc.database.primitive.padstack_instance.PadstackInstance` or None
            Padstack instance if found, otherwise ``None``.

        Examples
        --------
        >>> via = edb_padstacks.find_instance_by_id(123)
        >>> if via:
        ...     print(f"Found via: {via.name}")
        """
        return self._pedb.modeler.find_object_by_id(value)

    @property
    def pins(self) -> Dict[int, PadstackInstance]:
        """All pin instances belonging to components.

        Returns
        -------
        dict[int, :class:`pyedb.grpc.database.primitive.padstack_instance.PadstackInstance`]
            Dictionary of pin instances with database IDs as keys.

        Examples
        --------
        >>> all_pins = edb_padstacks.pins
        >>> for pin_id, pin in all_pins.items():
        ...     print(f"Pin {pin_id} belongs to {pin.component.refdes}")
        """
        pins = {}
        for instancename, instance in self.instances.items():
            if instance.is_pin and instance.component:
                pins[instancename] = instance
        return pins

    @property
    def vias(self) -> Dict[int, PadstackInstance]:
        """All via instances not belonging to components.

        Returns
        -------
        dict[int, :class:`pyedb.grpc.database.primitive.padstack_instance.PadstackInstance`]
            Dictionary of via instances with database IDs as keys.

        Examples
        --------
        >>> all_vias = edb_padstacks.vias
        >>> for via_id, via in all_vias.items():
        ...     print(f"Via {via_id} on net {via.net_name}")
        """
        pnames = list(self.pins.keys())
        vias = {i: j for i, j in self.instances.items() if i not in pnames}
        return vias

    @property
    def pingroups(self) -> List[Any]:
        """All Layout Pin groups.

        . deprecated:: pyedb 0.28.0
        Use :func:`pyedb.grpc.core.layout.pin_groups` instead.

        Returns
        -------
        list
            List of all layout pin groups.

        Examples
        --------
        >>> groups = edb_padstacks.pingroups  # Deprecated
        >>> groups = edb_padstacks._layout.pin_groups  # New way
        """
        warnings.warn(
            "`pingroups` is deprecated and is now located here `pyedb.grpc.core.layout.pin_groups` instead.",
            DeprecationWarning,
        )
        return self._layout.pin_groups

    @property
    def pad_type(self) -> GrpcPadType:
        """Return a PadType Enumerator."""
        return GrpcPadType

    def create_dielectric_filled_backdrills(
        self,
        layer: str,
        diameter: Union[float, str],
        material: str,
        permittivity: float,
        padstack_instances: Optional[List[PadstackInstance]] = None,
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
                _padstack_instances[inst.padstack_def.name].append(inst)
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
                    padsatck_def_name = inst.padstack_def.name
                    padstack_def_layers = inst.padstack_def.data.layer_names
                    if layer in padstack_def_layers and len(padstack_def_layers) >= 3:
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

    def create_circular_padstack(
        self,
        padstackname: Optional[str] = None,
        holediam: str = "300um",
        paddiam: str = "400um",
        antipaddiam: str = "600um",
        startlayer: Optional[str] = None,
        endlayer: Optional[str] = None,
    ) -> str:
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

        Examples
        --------
        >>> via_name = edb_padstacks.create_circular_padstack(
        ...     padstackname="VIA1", holediam="200um", paddiam="400um", antipaddiam="600um"
        ... )
        """

        padstack_def = PadstackDef.create(self._pedb, padstackname)

        padstack_data = GrpcPadstackDefData.create()
        list_values = [Value(holediam), Value(paddiam), Value(antipaddiam)]
        padstack_data.set_hole_parameters(
            offset_x=Value(0),
            offset_y=Value(0),
            rotation=Value(0),
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
            offset_x=Value(0),
            offset_y=Value(0),
            rotation=Value(0),
            sizes=[Value(paddiam)],
        )

        padstack_data.set_pad_parameters(
            layer="Default",
            pad_type=GrpcPadType.ANTI_PAD,
            type_geom=GrpcPadGeometryType.PADGEOMTYPE_CIRCLE,
            offset_x=Value(0),
            offset_y=Value(0),
            rotation=Value(0),
            sizes=[Value(antipaddiam)],
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
                    offset_x=Value(0),
                    offset_y=Value(0),
                    rotation=Value(0),
                    sizes=[Value(antipaddiam)],
                )

                padstack_data.set_pad_parameters(
                    layer=layer,
                    pad_type=GrpcPadType.ANTI_PAD,
                    type_geom=GrpcPadGeometryType.PADGEOMTYPE_CIRCLE,
                    offset_x=Value(0),
                    offset_y=Value(0),
                    rotation=Value(0),
                    sizes=[Value(antipaddiam)],
                )

        padstack_def.data = padstack_data

    def delete_batch_instances(self, instances_to_delete):
        for inst in instances_to_delete:
            inst.core.delete()
        self.clear_instances_cache()

    def delete_padstack_instances(self, net_names: Union[str, List[str]]) -> bool:
        """Delete padstack instances by net names.

        Parameters
        ----------
        net_names : str, list
            Names of the nets whose padstack instances should be deleted.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> success = edb_padstacks.delete_padstack_instances("GND")
        >>> success = edb_padstacks.delete_padstack_instances(["GND", "PWR"])
        """
        if not isinstance(net_names, list):  # pragma: no cover
            net_names = [net_names]

        for p_id, p in self.instances.items():
            if p.net_name in net_names:
                if not p._edb_object.delete():  # pragma: no cover
                    return False
        self.clear_instances_cache()
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
        newdefdata.solder_ball_param(Value(ballDiam), Value(ballDiam))
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

    def get_pin_from_component_and_net(
        self, refdes: Optional[str] = None, netname: Optional[str] = None
    ) -> (List)[PadstackInstance]:
        """Retrieve pins by component reference designator and net name.

        Parameters
        ----------
        refdes : str, optional
            Component reference designator.
        netname : str, optional
            Net name.

        Returns
        -------
        list[:class:`pyedb.grpc.database.primitive.padstack_instance.PadstackInstance`]
            List of matching pin instances.

        Examples
        --------
        >>> pins = edb_padstacks.get_pin_from_component_and_net(refdes="U1", netname="VCC")
        >>> pins = edb_padstacks.get_pin_from_component_and_net(netname="GND")  # All GND pins
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

        Examples
        --------
        >>> pins = edb_padstacks.get_pinlist_from_component_and_net(refdes="U1", netname="CLK")  # Deprecated
        >>> pins = edb_padstacks.get_pin_from_component_and_net(refdes="U1", netname="CLK")  # New way
        """
        warnings.warn(
            "`get_pinlist_from_component_and_net` is deprecated use `get_pin_from_component_and_net` instead.",
            DeprecationWarning,
        )
        return self.get_pin_from_component_and_net(refdes=refdes, netname=netname)

    def get_pad_parameters(
        self, pin: PadstackInstance, layername: str, pad_type: str = "regular_pad"
    ) -> Tuple[GrpcPadGeometryType, List[float], List[float], float]:
        """Get pad parameters for a pin on a specific layer.

        Parameters
        ----------
        pin : :class:`pyedb.grpc.database.primitive.padstack_instance.PadstackInstance`
            Padstack instance.
        layername : str
            Layer name.
        pad_type : str, optional
            Pad type ("regular_pad", "anti_pad", "thermal_pad"). Default is ``"regular_pad"``.

        Returns
        -------
        tuple
            (geometry_type, parameters, offset_x, offset_y, rotation) where:
            - geometry_type : str
            - parameters : list[float] or list[list[float]]
            - offset_x : float
            - offset_y : float
            - rotation : float

        Examples
        --------
        >>> via = edb_padstacks.instances[123]
        >>> geom_type, params, x, y, rot = edb_padstacks.get_pad_parameters(via, "TOP", "regular_pad")
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
            parameters = [Value(i) for i in padparams[1]]
            offset_x = Value(padparams[2])
            offset_y = Value(padparams[3])
            rotation = Value(padparams[4])
            return geometry_type.name, parameters, offset_x, offset_y, rotation
        elif len(padparams) == 4:  # polygon based
            from ansys.edb.core.geometry.polygon_data import (
                PolygonData as GrpcPolygonData,
            )

            if isinstance(padparams[0], GrpcPolygonData):
                points = [[Value(pt.x), Value(pt.y)] for pt in padparams[0].points]
                offset_x = Value(padparams[1])
                offset_y = Value(padparams[2])
                rotation = Value(padparams[3])
                geometry_type = GrpcPadGeometryType.PADGEOMTYPE_POLYGON
                return geometry_type.name, points, offset_x, offset_y, rotation
            return 0, [0], 0, 0, 0

    def set_all_antipad_value(self, value: Union[float, str]) -> bool:
        """Set anti-pad value for all padstack definitions.

        Parameters
        ----------
        value : float or str
            Anti-pad value with units (e.g., "0.2mm").

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> success = edb_padstacks.set_all_antipad_value("0.3mm")
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
                                offset_x=Value(offset_x),
                                offset_y=Value(offset_y),
                                rotation=Value(rotation),
                                type_geom=GrpcPadGeometryType.PADGEOMTYPE_CIRCLE,
                                sizes=[Value(value)],
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
                padstack.core.data = cloned_padstack_data
            return all_succeed

    def check_and_fix_via_plating(
        self, minimum_value_to_replace: float = 0.0, default_plating_ratio: float = 0.2
    ) -> bool:
        """Check and fix via plating ratios below a minimum value.

        Parameters
        ----------
        minimum_value_to_replace : float, optional
            Minimum plating ratio threshold. Default is ``0.0``.
        default_plating_ratio : float, optional
            Default plating ratio to apply. Default is ``0.2``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> success = edb_padstacks.check_and_fix_via_plating(minimum_value_to_replace=0.1)
        """
        for padstack_def in list(self.definitions.values()):
            if padstack_def.hole_plating_ratio <= minimum_value_to_replace:
                padstack_def.hole_plating_ratio = default_plating_ratio
                self._logger.info(
                    "Padstack definition with zero plating ratio, defaulting to 20%".format(padstack_def.name)
                )
        return True

    def get_via_instance_from_net(self, net_list: Optional[Union[str, List[str]]] = None) -> List[PadstackInstance]:
        """Get via instances by net names.

        Parameters
        ----------
        net_list : str or list, optional
            Net name(s) for filtering. Returns all vias if ``None``.

        Returns
        -------
        list[:class:`pyedb.grpc.database.primitive.padstack_instance.PadstackInstance`]
            List of via instances.

        Examples
        --------
        >>> vias = edb_padstacks.get_via_instance_from_net("GND")
        >>> vias = edb_padstacks.get_via_instance_from_net(["GND", "PWR"])
        """
        if net_list and not isinstance(net_list, list):
            net_list = [net_list]
        via_list = []
        for inst_id, inst in self._layout.padstack_instances.items():
            pad_layers_name = inst.padstack_def.data.layer_names
            if len(pad_layers_name) > 1:
                if not net_list:
                    via_list.append(inst)
                elif not inst.net.is_null:
                    if inst.net.name in net_list:
                        via_list.append(inst)
        return via_list

    def layers_between(self, layers, start_layer=None, stop_layer=None):
        """
        Return the sub-list of *layers* that lies between *start_layer*
        (inclusive) and *stop_layer* (inclusive).  Works no matter which
        of the two is nearer the top of the stack.
        """
        if not layers:
            return []

        # default to the full stack if one end is unspecified
        start_idx = layers.index(start_layer) if start_layer in layers else 0
        stop_idx = layers.index(stop_layer) if stop_layer in layers else len(layers) - 1

        # always slice from the smaller to the larger index
        lo, hi = sorted((start_idx, stop_idx))
        return layers[lo : hi + 1]

    def create(
        self,
        padstackname: Optional[str] = None,
        holediam: str = "300um",
        paddiam: str = "400um",
        antipaddiam: str = "600um",
        pad_shape: str = "Circle",
        antipad_shape: str = "Circle",
        x_size: str = "600um",
        y_size: str = "600um",
        corner_radius: str = "300um",
        offset_x: str = "0.0",
        offset_y: str = "0.0",
        rotation: str = "0.0",
        has_hole: bool = True,
        pad_offset_x: str = "0.0",
        pad_offset_y: str = "0.0",
        pad_rotation: str = "0.0",
        pad_polygon: Optional[Any] = None,
        antipad_polygon: Optional[Any] = None,
        polygon_hole: Optional[Any] = None,
        start_layer: Optional[str] = None,
        stop_layer: Optional[str] = None,
        add_default_layer: bool = False,
        anti_pad_x_size: str = "600um",
        anti_pad_y_size: str = "600um",
        hole_range: str = "upper_pad_to_lower_pad",
    ):
        """Create a padstack definition.

        Parameters
        ----------
        padstackname : str, optional
            Name of the padstack definition.
        holediam : str, optional
            Hole diameter with units. Default is ``"300um"``.
        paddiam : str, optional
            Pad diameter with units. Default is ``"400um"``.
        antipaddiam : str, optional
            Anti-pad diameter with units. Default is ``"600um"``.
        pad_shape : str, optional
            Pad geometry type ("Circle", "Rectangle", "Polygon"). Default is ``"Circle"``.
        antipad_shape : str, optional
            Anti-pad geometry type ("Circle", "Rectangle", "Bullet", "Polygon"). Default is ``"Circle"``.
        x_size : str, optional
            X-size for rectangular/bullet shapes. Default is ``"600um"``.
        y_size : str, optional
            Y-size for rectangular/bullet shapes. Default is ``"600um"``.
        corner_radius : str, optional
            Corner radius for bullet shapes. Default is ``"300um"``.
        offset_x : str, optional
            X-offset for anti-pad. Default is ``"0.0"``.
        offset_y : str, optional
            Y-offset for anti-pad. Default is ``"0.0"``.
        rotation : str, optional
            Rotation for anti-pad in degrees. Default is ``"0.0"``.
        has_hole : bool, optional
            Whether the padstack has a hole. Default is ``True``.
        pad_offset_x : str, optional
            X-offset for pad. Default is ``"0.0"``.
        pad_offset_y : str, optional
            Y-offset for pad. Default is ``"0.0"``.
        pad_rotation : str, optional
            Rotation for pad in degrees. Default is ``"0.0"``.
        pad_polygon : list or :class:`ansys.edb.core.geometry.PolygonData`, optional
            Polygon points for custom pad shape.
        antipad_polygon : list or :class:`ansys.edb.core.geometry.PolygonData`, optional
            Polygon points for custom anti-pad shape.
        polygon_hole : list or :class:`ansys.edb.core.geometry.PolygonData`, optional
            Polygon points for custom hole shape.
        start_layer : str, optional
            Starting layer name.
        stop_layer : str, optional
            Ending layer name.
        add_default_layer : bool, optional
            Whether to add "Default" layer. Default is ``False``.
        anti_pad_x_size : str, optional
            Anti-pad X-size. Default is ``"600um"``.
        anti_pad_y_size : str, optional
            Anti-pad Y-size. Default is ``"600um"``.
        hole_range : str, optional
            Hole range type ("through", "begin_on_upper_pad", "end_on_lower_pad", "upper_pad_to_lower_pad").
            Default is ``"upper_pad_to_lower_pad"``.

        Returns
        -------
        str
            Name of the created padstack definition.
        """
        from pyedb.grpc.database.geometry.polygon_data import PolygonData

        holediam = Value(holediam)
        paddiam = Value(paddiam)
        antipaddiam = Value(antipaddiam)
        layers = list(self._pedb.stackup.signal_layers.keys())[:]
        value0 = Value("0.0")
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
            padstack_data.plating_percentage = Value(20.0)
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
            padstack_data.plating_percentage = Value(20.0)
        else:
            pass

        x_size = Value(x_size)
        y_size = Value(y_size)
        corner_radius = Value(corner_radius)
        pad_offset_x = Value(pad_offset_x)
        pad_offset_y = Value(pad_offset_y)
        pad_rotation = Value(pad_rotation)
        anti_pad_x_size = Value(anti_pad_x_size)
        anti_pad_y_size = Value(anti_pad_y_size)

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
        layers = self.layers_between(layers=layers, start_layer=start_layer, stop_layer=stop_layer)
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
                pad_polygon = PolygonData(edb_object=GrpcPolygonData(points=pad_polygon))
        if antipad_shape == "Bullet":  # pragma no cover
            antipad_array = [x_size, y_size, corner_radius]
            antipad_shape = GrpcPadGeometryType.PADGEOMTYPE_BULLET
        elif antipad_shape == "Rectangle":  # pragma no cover
            antipad_array = [anti_pad_x_size, anti_pad_y_size]
            antipad_shape = GrpcPadGeometryType.PADGEOMTYPE_RECTANGLE
        elif antipad_shape == "Polygon":
            if isinstance(antipad_polygon, list):
                antipad_polygon = PolygonData(edb_object=GrpcPolygonData(points=antipad_polygon))
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
                    fp=pad_polygon.core,
                )
                padstack_data.set_pad_parameters(
                    layer=layer,
                    pad_type=GrpcPadType.ANTI_PAD,
                    offset_x=pad_offset_x,
                    offset_y=pad_offset_y,
                    rotation=pad_rotation,
                    fp=antipad_polygon.core,
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

        padstack_definition = PadstackDef.create(self._pedb, padstackname)
        padstack_definition.data = padstack_data
        self._logger.info(f"Padstack {padstackname} create correctly")
        return padstackname

    def _get_pin_layer_range(self, pin: PadstackInstance) -> Union[Tuple[str, str], bool]:
        layers = pin.get_layer_range()
        if layers:
            return layers[0], layers[1]
        else:
            return False

    def duplicate(self, target_padstack_name: str, new_padstack_name: str = "") -> str:
        """Duplicate a padstack definition.

        Parameters
        ----------
        target_padstack_name : str
            Name of the padstack definition to duplicate.
        new_padstack_name : str, optional
            Name for the new padstack definition.

        Returns
        -------
        str
            Name of the new padstack definition.
        """
        new_padstack_definition_data = GrpcPadstackDefData(self.definitions[target_padstack_name].data.msg)
        if not new_padstack_name:
            new_padstack_name = generate_unique_name(target_padstack_name)
        padstack_definition = PadstackDef.create(self, new_padstack_name)
        padstack_definition.data = new_padstack_definition_data
        return new_padstack_name

    def place(
        self,
        position: List[float],
        definition_name: str,
        net_name: str = "",
        via_name: str = "",
        rotation: float = 0.0,
        fromlayer: Optional[str] = None,
        tolayer: Optional[str] = None,
        solderlayer: Optional[str] = None,
        is_pin: bool = False,
        layer_map: str = "two_way",
    ) -> PadstackInstance:
        """Place a padstack instance.

        Parameters
        ----------
        position : list[float, float]
            [x, y] position for placement.
        definition_name : str
            Padstack definition name.
        net_name : str, optional
            Net name. Default is ``""``.
        via_name : str, optional
            Instance name. Default is ``""``.
        rotation : float, optional
            Rotation in degrees. Default is ``0.0``.
        fromlayer : str, optional
            Starting layer name.
        tolayer : str, optional
            Ending layer name.
        solderlayer : str, optional
            Solder ball layer name.
        is_pin : bool, optional
            Whether the instance is a pin. Default is ``False``.
        layer_map : str, optional
            Layer mapping information. Valid input is ``"two_way"``, ``"backward"``, or ``"forward"``.
            Default is ``two_way``.

        Returns
        -------
        :class:`pyedb.grpc.database.primitive.padstack_instance.PadstackInstance` or bool
            Created padstack instance or ``False`` if failed.
        """
        padstack_def = None
        for pad in list(self.definitions.keys()):
            if pad == definition_name:
                padstack_def = self.definitions[pad]
        position = GrpcPointData(
            [Value(position[0], self._pedb.active_cell), Value(position[1], self._pedb.active_cell)]
        )
        net = self._pedb.nets.find_or_create_net(net_name)
        rotation = Value(rotation * math.pi / 180)
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
                net=net_name,
                padstack_definition=padstack_def.name,
                position_x=position.x.value,
                position_y=position.y.value,
                rotation=rotation,
                top_layer=fromlayer,
                bottom_layer=tolayer,
                name=via_name,
                solder_ball_layer=solderlayer,
                layer_map=layer_map,
            )
            padstack_instance.is_pin = is_pin
            self.clear_instances_cache()
            return padstack_instance
        else:
            raise RuntimeError("Place padstack failed")

    def remove_pads_from_padstack(self, padstack_name: str, layer_name: Optional[str] = None):
        """Remove pads from a padstack definition on specified layers.

        Parameters
        ----------
        padstack_name : str
            Padstack definition name.
        layer_name : str or list, optional
            Layer name(s). Applies to all layers if ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        pad_type = GrpcPadType.REGULAR_PAD
        pad_geo = GrpcPadGeometryType.PADGEOMTYPE_CIRCLE
        vals = Value(0)
        params = [Value(0)]
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
        padstack_name: str,
        layer_name: Optional[str] = None,
        pad_shape: str = "Circle",
        pad_params: Union[float, List[float]] = 0,
        pad_x_offset: float = 0,
        pad_y_offset: float = 0,
        pad_rotation: float = 0,
        antipad_shape: str = "Circle",
        antipad_params: Union[float, List[float]] = 0,
        antipad_x_offset: float = 0,
        antipad_y_offset: float = 0,
        antipad_rotation: float = 0,
    ):
        """Set pad and anti-pad properties for a padstack definition.

        Parameters
        ----------
        padstack_name : str
            Padstack definition name.
        layer_name : str or list, optional
            Layer name(s). Applies to all layers if ``None``.
        pad_shape : str, optional
            Pad geometry type ("Circle", "Square", "Rectangle", "Oval", "Bullet"). Default is ``"Circle"``.
        pad_params : float or list, optional
            Pad dimension(s). Default is ``0``.
        pad_x_offset : float, optional
            Pad X-offset. Default is ``0``.
        pad_y_offset : float, optional
            Pad Y-offset. Default is ``0``.
        pad_rotation : float, optional
            Pad rotation in degrees. Default is ``0``.
        antipad_shape : str, optional
            Anti-pad geometry type ("Circle", "Square", "Rectangle", "Oval", "Bullet"). Default is ``"Circle"``.
        antipad_params : float or list, optional
            Anti-pad dimension(s). Default is ``0``.
        antipad_x_offset : float, optional
            Anti-pad X-offset. Default is ``0``.
        antipad_y_offset : float, optional
            Anti-pad Y-offset. Default is ``0``.
        antipad_rotation : float, optional
            Anti-pad rotation in degrees. Default is ``0``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
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
        pad_params = [Value(i) for i in pad_params]
        pad_x_offset = Value(pad_x_offset)
        pad_y_offset = Value(pad_y_offset)
        pad_rotation = Value(pad_rotation)

        antipad_shape = shape_dict[antipad_shape]
        if not isinstance(antipad_params, list):
            antipad_params = [antipad_params]
        antipad_params = [Value(i) for i in antipad_params]
        antipad_x_offset = Value(antipad_x_offset)
        antipad_y_offset = Value(antipad_y_offset)
        antipad_rotation = Value(antipad_rotation)
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

    def get_padstack_instance_by_net_name(self, net: str):
        """Get padstack instances by net name.

        .. deprecated:: 0.55.0
        Use: :func:`get_instances` with `net_name` parameter instead.

        Parameters
        ----------
        net : str
            Net name to filter padstack instances.

        Returns
        -------
        list[:class:`pyedb.grpc.database.primitive.padstack_instance.PadstackInstance`]
            List of padstack instances associated with the specified net.
        """
        warnings.warn(
            "`get_padstack_instance_by_net_name` is deprecated, use `get_instances` with `net_name` parameter instead.",
            DeprecationWarning,
        )
        return self.get_instances(net_name=net)

    def get_instances(
        self,
        name: Optional[str] = None,
        pid: Optional[int] = None,
        definition_name: Optional[str] = None,
        net_name: Optional[Union[str, List[str]]] = None,
        component_reference_designator: Optional[str] = None,
        component_pin: Optional[str] = None,
    ) -> List[PadstackInstance]:
        """Get padstack instances by search criteria.

        Parameters
        ----------
        name : str, optional
            Instance name.
        pid : int, optional
            Database ID.
        definition_name : str or list, optional
            Padstack definition name(s).
        net_name : str or list, optional
            Net name(s).
        component_reference_designator : str or list, optional
            Component reference designator(s).
        component_pin : str or list, optional
            Component pin number(s).

        Returns
        -------
        list[:class:`pyedb.grpc.database.primitive.padstack_instance.PadstackInstance`]
            List of matching padstack instances.
        """
        instances_by_id = self.instances
        if pid:
            return instances_by_id[pid]
        elif name:
            instances = [inst for inst in list(self.instances.values()) if inst.aedt_name == name]
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
        self,
        positive_pin: Union[int, str, PadstackInstance],
        reference_net: str = "gnd",
        search_radius: float = 5e-3,
        max_limit: int = 0,
        component_only: bool = True,
    ) -> List[PadstackInstance]:
        """Find reference pins near a specified pin.

        Parameters
        ----------
        positive_pin : :class:`pyedb.grpc.database.primitive.padstack_instance.PadstackInstance`
            Target pin.
        reference_net : str, optional
            Reference net name. Default is ``"gnd"``.
        search_radius : float, optional
            Search radius in meters. Default is ``5e-3`` (5 mm).
        max_limit : int, optional
            Maximum number of pins to return. Default is ``0`` (no limit).
        component_only : bool, optional
            Whether to search only in component pins. Default is ``True``.

        Returns
        -------
        list[:class:`pyedb.grpc.database.primitive.padstack_instance.PadstackInstance`]
            List of reference pins.
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

    def get_padstack_instances_rtree_index(self, nets: Optional[Union[str, List[str]]] = None) -> rtree.index.Index:
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

    def get_padstack_instances_id_intersecting_polygon(
        self,
        points: List[Tuple[float, float]],
        nets: Optional[Union[str, List[str]]] = None,
        padstack_instances_index: Optional[Dict[int, Tuple[float, float]]] = None,
    ) -> List[int]:
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

    def get_padstack_instances_intersecting_bounding_box(
        self,
        bounding_box: List[float],
        nets: Optional[Union[str, List[str]]] = None,
        padstack_instances_index: Optional[rtree.index.Index] = None,
    ) -> List[PadstackInstance]:
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
        net_name: str = "GND",
        distance_threshold: float = 5e-3,
        minimum_via_number: int = 6,
        selected_angles: Optional[List[float]] = None,
        padstack_instances_id: Optional[List[int]] = None,
    ) -> List[str]:
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

    def merge_via(
        self,
        contour_boxes: List[List[float]],
        net_filter: Optional[Union[str, List[str]]] = None,
        start_layer: Optional[str] = None,
        stop_layer: Optional[str] = None,
    ) -> List[str]:
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
        self.clear_instances_cache()
        return merged_via_ids

    def reduce_via_in_bounding_box(
        self, bounding_box: List[float], x_samples: int, y_samples: int, nets: Optional[Union[str, List[str]]] = None
    ) -> bool:
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
                self.clear_instances_cache()
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
        self.clear_instances_cache()
        return list(to_keep), grid
