# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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
This module contains the `Padstacks` class.
"""

from collections import defaultdict
import math
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union
import warnings

from ansys.edb.core.definition.padstack_def_data import (
    PadGeometryType as CorePadGeometryType,
    PadstackDefData as CorePadstackDefData,
    PadstackHoleRange as CorePadstackHoleRange,
    PadType as CorePadType,
    SolderballPlacement as CoreSolderballPlacement,
    SolderballShape as CoreSolderballShape,
)
from ansys.edb.core.geometry.polygon_data import PolygonData as CorePolygonData
from ansys.edb.core.inner.exceptions import InvalidArgumentException
import numpy as np

from pyedb.generic.general_methods import generate_unique_name
from pyedb.generic.geometry_operators import GeometryOperators
from pyedb.grpc.database.definition.padstack_def import PadstackDef
from pyedb.grpc.database.primitive.padstack_instance import PadstackInstance
from pyedb.grpc.database.utility.value import Value
from pyedb.misc.decorators import deprecate_argument_name, deprecated, deprecated_property

if TYPE_CHECKING:
    import rtree


GEOMETRY_MAP = {
    0: CorePadGeometryType.PADGEOMTYPE_NO_GEOMETRY,
    1: CorePadGeometryType.PADGEOMTYPE_CIRCLE,
    2: CorePadGeometryType.PADGEOMTYPE_SQUARE,
    3: CorePadGeometryType.PADGEOMTYPE_RECTANGLE,
    4: CorePadGeometryType.PADGEOMTYPE_OVAL,
    5: CorePadGeometryType.PADGEOMTYPE_BULLET,
    6: CorePadGeometryType.PADGEOMTYPE_NSIDED_POLYGON,
    7: CorePadGeometryType.PADGEOMTYPE_POLYGON,
    8: CorePadGeometryType.PADGEOMTYPE_ROUND45,
    9: CorePadGeometryType.PADGEOMTYPE_ROUND90,
    10: CorePadGeometryType.PADGEOMTYPE_SQUARE45,
    11: CorePadGeometryType.PADGEOMTYPE_SQUARE90,
}

PAD_TYPE_MAP = {
    0: CorePadType.REGULAR_PAD,
    1: CorePadType.ANTI_PAD,
    2: CorePadType.THERMAL_PAD,
    3: CorePadType.HOLE,
    4: CorePadType.UNKNOWN_GEOM_TYPE,
}


class Padstacks(object):
    """
    Manages EDB methods for padstacks accessible from `Edb.padstacks` property.

    Examples
    --------
    >>> from pyedb import Edb
    >>> edbapp = Edb("myaedbfolder", edbversion="2024.2")
    >>> edb_padstacks = edbapp.padstacks

    """

    def __getitem__(self, name):
        """
        Get a padstack definition or instance from the EDB project.

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
            return self.instances.get(name, None)
        elif name in self.definitions:
            return self.definitions.get(name, None)
        else:
            return next((i for i in self.instances.values() if i.name == name or i.aedt_name == name), None)

    def __init__(self, p_edb: Any) -> None:
        self._pedb = p_edb
        self.__definitions: Dict[str, Any] = {}
        self._instances_by_name = {}
        self._instances_by_net = {}

    def clear_instances_cache(self):
        """Clear the cached padstack instances."""
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
    def int_to_pad_type(val=0) -> CorePadType:
        """
        Convert an integer to an EDB.PadGeometryType.

        Parameters
        ----------
        val : int

        Returns
        -------
        object
            EDB.PadType enumerator value.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb("my_design.edb")
        >>> pad_type = edb.padstacks.int_to_pad_type(0)  # Returns REGULAR_PAD
        >>> pad_type2 = edb.padstacks.int_to_pad_type(1)  # Returns ANTI_PAD

        """

        return PAD_TYPE_MAP.get(val, val)

    @staticmethod
    def int_to_geometry_type(val: int = 0) -> CorePadGeometryType:
        """
        Convert an integer to an EDB.PadGeometryType.

        Parameters
        ----------
        val : int

        Returns
        -------
        object
            EDB.PadGeometryType enumerator value.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb()
        >>> geom_type = edb.padstacks.int_to_geometry_type(1)  # Returns CIRCLE
        >>> geom_type2 = edb.padstacks.int_to_geometry_type(2)  # Returns SQUARE

        """
        return GEOMETRY_MAP.get(val, val)

    @property
    def definitions(self) -> Dict[str, PadstackDef]:
        """
        Padstack definitions.

        Returns
        -------
        dict[str, :class:`pyedb.grpc.database.definition.padstack_def.PadstackDef`]
            Dictionary of padstack definitions with definition names as keys.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb("my_design.edb")
        >>> all_definitions = edb.padstacks.definitions
        >>> for name, definition in all_definitions.items():
        ...     print(f"Padstack: {name}")

        """
        self.__definitions = {}
        for padstack_def in self._pedb.db.padstack_defs:
            try:
                self.__definitions[padstack_def.name] = PadstackDef(self._pedb, padstack_def)
            except (Exception, InvalidArgumentException) as e:
                self._logger.warning(f"Error processing padstack definition {padstack_def.name}: {e}")
        return self.__definitions

    @property
    def instances(self) -> Dict[int, PadstackInstance]:
        """
        All padstack instances (vias and pins) in the layout.

        Returns
        -------
        dict[int, :class:`pyedb.grpc.database.primitive.padstack_instance.PadstackInstance`]
            Dictionary of padstack instances with database IDs as keys.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb("my_design.edb")
        >>> all_instances = edb.padstacks.instances
        >>> for inst_id, instance in all_instances.items():
        ...     print(f"Instance {inst_id}: {instance.name}")

        """
        return {i.id: i for i in self._pedb.layout.padstack_instances}

    @property
    def instances_by_net(self) -> Dict[Any, PadstackInstance]:
        if not self._instances_by_net:
            for instance in self._pedb.layout.padstack_instances:
                net_name = instance.net_name
                if net_name:
                    self._instances_by_net.setdefault(net_name, []).append(instance)
        return self._instances_by_net

    @property
    def instances_by_name(self) -> Dict[str, PadstackInstance]:
        """
        All padstack instances (vias and pins) indexed by name.

        Returns
        -------
        dict[str, :class:`pyedb.grpc.database.primitive.padstack_instance.PadstackInstance`]
            Dictionary of padstack instances with names as keys.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb("my_design.edb")
        >>> named_instances = edb.padstacks.instances_by_name
        >>> for name, instance in named_instances.items():
        ...     print(f"Instance named {name}")

        """
        if not self._instances_by_net:
            for pds in self._pedb.layout.padstack_instances:
                name = pds.aedt_name
                if name:
                    self._instances_by_net[name] = pds
        return self._instances_by_net

    def find_instance_by_id(self, value: int) -> Optional[PadstackInstance]:
        """
        Find a padstack instance by database ID.

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
        >>> from pyedb import Edb
        >>> edb = Edb("my_design.edb")
        >>> via = edb.padstacks.find_instance_by_id(123)
        >>> if via:
        ...     print(f"Found via: {via.name}")

        """
        return next(i for i in self._pedb.layout.padstack_instances if i.id == value)

    @property
    def pins(self) -> Dict[int, PadstackInstance]:
        """
        All pin instances belonging to components.

        Returns
        -------
        dict[int, :class:`pyedb.grpc.database.primitive.padstack_instance.PadstackInstance`]
            Dictionary of pin instances with database IDs as keys.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb("my_design.edb")
        >>> all_pins = edb.padstacks.pins
        >>> for pin_id, pin in all_pins.items():
        ...     print(f"Pin {pin_id} belongs to {pin.component.refdes}")

        """
        pins = {}
        for instance in self.instances.values():
            if instance.is_pin and instance.component:
                pins[instance.name] = instance
        return pins

    @property
    def vias(self) -> Dict[int, PadstackInstance]:
        """
        All via instances not belonging to components.

        Returns
        -------
        dict[int, :class:`pyedb.grpc.database.primitive.padstack_instance.PadstackInstance`]
            Dictionary of via instances with database IDs as keys.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb("my_design.edb")
        >>> all_vias = edb.padstacks.vias
        >>> for via_id, via in all_vias.items():
        ...     print(f"Via {via_id} on net {via.net_name}")

        """
        pnames = list(self.pins.keys())
        vias = {i_id: i for i_id, i in self.instances.items() if i not in pnames}
        return vias

    @property
    @deprecated_property("use pin_groups property instead.")
    def pingroups(self) -> List[Any]:
        """
        All Layout Pin groups.

        . deprecated:: pyedb 0.28.0
        Use :func:`pyedb.grpc.core.layout.pin_groups` instead.

        Returns
        -------
        list
            List of all layout pin groups.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb("my_design.edb")
        >>> groups = edb.padstacks._layout.pin_groups  # New way

        """
        return self._layout.pin_groups

    @property
    def pad_type(self) -> CorePadType:
        """Return a PadType Enumerator."""
        return CorePadType

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
        r"""
        Create dielectric-filled back-drills for through-hole vias.

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

        >>> from pyedb import Edb
        >>> edb = Edb("my_design.edb")
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
            definition = self.definitions[padstack_def_backdrill_name]
            for inst in instances:
                inst.set_back_drill_by_layer(drill_to_layer=layer, offset=0.0, diameter=self._pedb.value(diameter))
                self.place(
                    position=inst.position,
                    definition_name=definition,
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
        """
        Create a circular padstack.

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
        >>> from pyedb import Edb
        >>> edb = Edb("my_design.edb")
        >>> via_name = edb.padstacks.create_circular_padstack(
        ...     padstackname="VIA1", holediam="200um", paddiam="400um", antipaddiam="600um"
        ... )

        """

        padstack_def = PadstackDef.create(self._pedb, padstackname)

        padstack_data = CorePadstackDefData.create()
        list_values = [
            self._pedb._value_setter(holediam),
            self._pedb._value_setter(paddiam),
            self._pedb._value_setter(antipaddiam),
        ]
        padstack_data.set_hole_parameters(
            offset_x=0.0,
            offset_y=0.0,
            rotation=0.0,
            type_geom=CorePadGeometryType.PADGEOMTYPE_CIRCLE,
            sizes=list_values,
        )

        padstack_data.hole_range = CorePadstackHoleRange.UPPER_PAD_TO_LOWER_PAD
        layers = list(self._pedb.stackup.signal_layers.keys())
        if not startlayer:
            startlayer = layers[0]
        if not endlayer:
            endlayer = layers[len(layers) - 1]

        antipad_shape = CorePadGeometryType.PADGEOMTYPE_CIRCLE
        started = False
        padstack_data.set_pad_parameters(
            layer="Default",
            pad_type=CorePadType.REGULAR_PAD,
            type_geom=CorePadGeometryType.PADGEOMTYPE_CIRCLE,
            offset_x=0.0,
            offset_y=0.0,
            rotation=0,
            sizes=[self._pedb._value_setter(paddiam)],
        )

        padstack_data.set_pad_parameters(
            layer="Default",
            pad_type=CorePadType.ANTI_PAD,
            type_geom=CorePadGeometryType.PADGEOMTYPE_CIRCLE,
            offset_x=0,
            offset_y=0,
            rotation=0,
            sizes=[self._pedb._value_setter(antipaddiam)],
        )

        for layer in layers:
            if layer == startlayer:
                started = True
            if layer == endlayer:
                started = False
            if started:
                padstack_data.set_pad_parameters(
                    layer=layer,
                    pad_type=CorePadType.ANTI_PAD,
                    type_geom=CorePadGeometryType.PADGEOMTYPE_CIRCLE,
                    offset_x=0,
                    offset_y=0,
                    rotation=0,
                    sizes=[self._pedb._value_setter(antipaddiam)],
                )

                padstack_data.set_pad_parameters(
                    layer=layer,
                    pad_type=CorePadType.ANTI_PAD,
                    type_geom=CorePadGeometryType.PADGEOMTYPE_CIRCLE,
                    offset_x=0,
                    offset_y=0,
                    rotation=0,
                    sizes=[self._pedb._value_setter(antipaddiam)],
                )

        padstack_def.data = padstack_data

        return padstackname

    def delete_batch_instances(self, instances_to_delete):
        for inst in instances_to_delete:
            inst.core.delete()
        self._instances = None

    def delete_padstack_instances(self, net_names: Union[str, List[str]]) -> bool:
        """
        Delete padstack instances by net names.

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
        >>> from pyedb import Edb
        >>> edb = Edb("my_design.edb")
        >>> success = edb.padstacks.delete_padstack_instances("GND")

        """
        if not isinstance(net_names, list):  # pragma: no cover
            net_names = [net_names]

        for p_id, p in self.instances.items():
            if p.net_name in net_names:
                if not p.core.delete():  # pragma: no cover
                    return False
        return True

    @deprecate_argument_name(
        {
            "padstackInst": "padstack_instance",
            "isTopPlaced": "top_placed",
            "sballLayer_name": "solder_ball_layer",
            "ballDIam": "solder_ball_diameter",
        }
    )
    def set_solderball(
        self, padstack_instance, solder_ball_layer, top_placed=True, solder_ball_diameter=100e-6, material: str = None
    ):
        """
        Set solderball for the given PadstackInstance.

        Parameters
        ----------
        padstack_instance : Edb.Cell.Primitive.PadstackInstance or int
            Padstack instance id or object.
        solder_ball_layer : str,
            Name of the layer where the solder ball is placed. No default values.
        top_placed : bool, optional.
            Boolean triggering is the solder ball is placed on Top or Bottom of the layer stackup.
        solder_ball_diameter : double, optional,
            Solder ball diameter value.
        material : str, optional,
            Material name for the solder ball. If the material does not exist in the central material library,
            it will be created on the fly with a default conductivity of 1e7 Siemens.

        Returns
        -------
        bool

        """
        if isinstance(padstack_instance, int):
            psdef = self.definitions[self.instances[padstack_instance].padstack_definition].core

        else:
            psdef = padstack_instance.padstack_def
        newdef_data = psdef.data
        newdef_data.solder_ball_shape = CoreSolderballShape.SOLDERBALL_CYLINDER
        solder_ball_diameter = self._pedb._value_setter(solder_ball_diameter)
        newdef_data.solder_ball_param = solder_ball_diameter, solder_ball_diameter
        sball_placement = (
            CoreSolderballPlacement.ABOVE_PADSTACK if top_placed else CoreSolderballPlacement.BELOW_PADSTACK
        )
        newdef_data.solder_ball_placement = sball_placement
        if material:
            if material not in self._pedb.materials:
                self._pedb.materials.add_conductor_material(name=material, conductivity=1e7)
            newdef_data.solder_ball_material = material
        psdef.data = newdef_data
        sball_layer = [lay.core for lay in list(self._layers.values()) if lay.name == solder_ball_layer][0]
        if sball_layer is not None:
            padstack_instance.solder_ball_layer = sball_layer
            return True

        return False

    @deprecated("use edb.excitation_manager.create_source_on_component method instead")
    def create_coax_port(self, padstackinstance, use_dot_separator=True, name=None):
        """
        Create HFSS 3Dlayout coaxial lumped port on a pastack
        Requires to have solder ball defined before calling this method.

        . deprecated:: pyedb 0.28.0
        Use :func:`edb.grpc.core.excitations.create_source_on_component` instead.

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
        self._pedb.excitation_manager.create_coax_port(padstackinstance, use_dot_separator=use_dot_separator, name=name)

    def get_pin_from_component_and_net(
        self, refdes: Optional[str] = None, netname: Optional[str] = None
    ) -> List[PadstackInstance]:
        """
        Retrieve pins by component reference designator and net name.

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
        >>> from pyedb import Edb
        >>> edb = Edb("my_design.edb")
        >>> pins = edb.padstacks.get_pin_from_component_and_net(refdes="U1", netname="VCC")
        >>> pins2 = edb.padstacks.get_pin_from_component_and_net(netname="GND")  # All GND pins

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

    @deprecated("use get_pin_from_component_and_net method instead")
    def get_pinlist_from_component_and_net(self, refdes=None, netname=None):
        """
        Retrieve pins given a component's reference designator and net name.

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
        >>> from pyedb import Edb
        >>> edb = Edb("my_design.edb")
        >>> pins = edb.padstacks.get_pin_from_component_and_net(refdes="U1", netname="CLK")  # New way

        """
        return self.get_pin_from_component_and_net(refdes=refdes, netname=netname)

    def get_pad_parameters(
        self, pin: PadstackInstance, layername: str, pad_type: str = "regular_pad"
    ) -> Tuple[str, Union[List[float], List[List[float]]], float, float, float]:
        """
        Get pad parameters for a pin on a specific layer.

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
        tuple[str, list[float] or list[list[float]], float, float, float]
            Tuple of ``(geometry_type, parameters, offset_x, offset_y, rotation)``
            where ``geometry_type`` is the pad shape name, ``parameters`` are the
            shape dimensions, and ``offset_x``, ``offset_y``, ``rotation`` are the
            pad placement offsets and rotation angle.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb("my_design.edb")
        >>> via = edb.padstacks.instances[123]
        >>> geom_type, params, x, y, rot = edb.padstacks.get_pad_parameters(via, "TOP", "regular_pad")

        """
        if pad_type == "regular_pad":
            pad_type = CorePadType.REGULAR_PAD
        elif pad_type == "anti_pad":
            pad_type = CorePadType.ANTI_PAD
        elif pad_type == "thermal_pad":
            pad_type = CorePadType.THERMAL_PAD
        else:
            pad_type = pad_type = CorePadType.REGULAR_PAD
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
                geometry_type = CorePadGeometryType.PADGEOMTYPE_POLYGON
                return geometry_type.name, points, offset_x, offset_y, rotation
            return "unknown", [0.0], 0.0, 0.0, 0.0
        # Fallback: ensure a consistent return type for all code paths
        return "unknown", [0.0], 0.0, 0.0, 0.0

    def set_all_antipad_value(self, value: Union[float, str]) -> bool:
        """
        Set anti-pad value for all padstack definitions.

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
        >>> from pyedb import Edb
        >>> edb = Edb("my_design.edb")
        >>> success = edb.padstacks.set_all_antipad_value("0.3mm")

        """
        if self.definitions:
            all_succeed = True
            for padstack in list(self.definitions.values()):
                cloned_padstack_data = padstack.core.data
                layers_name = cloned_padstack_data.layer_names
                for layer in layers_name:
                    try:
                        geom_type, points, offset_x, offset_y, rotation = cloned_padstack_data.get_pad_parameters(
                            layer, CorePadType.ANTI_PAD
                        )
                        if geom_type == CorePadGeometryType.PADGEOMTYPE_CIRCLE.name:
                            cloned_padstack_data.set_pad_parameters(
                                layer=layer,
                                pad_type=CorePadType.ANTI_PAD,
                                offset_x=self._pedb._value_setter(offset_x),
                                offset_y=self._pedb._value_setter(offset_y),
                                rotation=self._pedb._value_setter(rotation),
                                type_geom=CorePadGeometryType.PADGEOMTYPE_CIRCLE,
                                sizes=[self._pedb._value_setter(value)],
                            )
                            self._logger.info(
                                f"Pad-stack definition {padstack.name}, anti-pad on layer {layer}, has been set "
                                f"to {str(value)}"
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
        else:
            return True

    def check_and_fix_via_plating(
        self, minimum_value_to_replace: float = 0.0, default_plating_ratio: float = 0.2
    ) -> bool:
        """
        Check and fix via plating ratios below a minimum value.

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
        >>> from pyedb import Edb
        >>> edb = Edb("my_design.edb")
        >>> success = edb.padstacks.check_and_fix_via_plating(minimum_value_to_replace=0.1)

        """
        for padstack_def in list(self.definitions.values()):
            if padstack_def.hole_plating_ratio <= minimum_value_to_replace:
                padstack_def.hole_plating_ratio = default_plating_ratio
                self._logger.info(
                    "Padstack definition with zero plating ratio, defaulting to 20%".format(padstack_def.name)
                )
        return True

    def get_via_instance_from_net(self, net_list: Optional[Union[str, List[str]]] = None) -> List[PadstackInstance]:
        """
        Get via instances by net names.

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
        >>> from pyedb import Edb
        >>> edb = Edb("my_design.edb")
        >>> vias = edb.padstacks.get_via_instance_from_net(["GND", "PWR"])

        """
        if net_list and not isinstance(net_list, list):
            net_list = [net_list]
        via_list = []
        for inst in self.instances.values():
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
        Return the sub-list of layers that lies between ``start_layer`` and ``stop_layer`` (both inclusive).

        Works regardless of which of the two layers is nearer to the top of the stack.

        Parameters
        ----------
        layers : list[str]
            Ordered list of all layer names.
        start_layer : str, optional
            Starting layer name. If ``None``, defaults to the first layer.
        stop_layer : str, optional
            Stopping layer name. If ``None``, defaults to the last layer.

        Returns
        -------
        list[str]
            Sub-list of layer names between ``start_layer`` and ``stop_layer``, inclusive.

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
        """
        Create a padstack definition.

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

        holediam = self._pedb._value_setter(holediam)
        paddiam = self._pedb._value_setter(paddiam)
        antipaddiam = self._pedb._value_setter(antipaddiam)
        layers = list(self._pedb.stackup.signal_layers.keys())[:]
        value0 = 0.0
        if not padstackname:
            padstackname = generate_unique_name("VIA")
        padstack_data = CorePadstackDefData.create()
        if has_hole and not polygon_hole:
            hole_param = [holediam, holediam]
            padstack_data.set_hole_parameters(
                offset_x=value0,
                offset_y=value0,
                rotation=value0,
                type_geom=CorePadGeometryType.PADGEOMTYPE_CIRCLE,
                sizes=hole_param,
            )
            padstack_data.plating_percentage = 20.0
        elif polygon_hole:
            if isinstance(polygon_hole, list):
                polygon_hole = CorePolygonData(points=polygon_hole)
            padstack_data.set_hole_parameters(
                offset_x=value0,
                offset_y=value0,
                rotation=value0,
                type_geom=CorePadGeometryType.PADGEOMTYPE_POLYGON,
                poly=polygon_hole.core,
            )
            padstack_data.plating_percentage = 20.0
        else:
            pass

        x_size = self._pedb._value_setter(x_size)
        y_size = self._pedb._value_setter(y_size)
        corner_radius = self._pedb._value_setter(corner_radius)
        pad_offset_x = self._pedb._value_setter(pad_offset_x)
        pad_offset_y = self._pedb._value_setter(pad_offset_y)
        pad_rotation = self._pedb._value_setter(pad_rotation)
        anti_pad_x_size = self._pedb._value_setter(anti_pad_x_size)
        anti_pad_y_size = self._pedb._value_setter(anti_pad_y_size)

        if hole_range == "through":  # pragma no cover
            padstack_data.hole_range = CorePadstackHoleRange.THROUGH
        elif hole_range == "begin_on_upper_pad":  # pragma no cover
            padstack_data.hole_range = CorePadstackHoleRange.BEGIN_ON_UPPER_PAD
        elif hole_range == "end_on_lower_pad":  # pragma no cover
            padstack_data.hole_range = CorePadstackHoleRange.END_ON_LOWER_PAD
        elif hole_range == "upper_pad_to_lower_pad":  # pragma no cover
            padstack_data.hole_range = CorePadstackHoleRange.UPPER_PAD_TO_LOWER_PAD
        else:  # pragma no cover
            self._logger.error("Unknown padstack hole range")
        padstack_data.material = "copper"
        layers = self.layers_between(layers=layers, start_layer=start_layer, stop_layer=stop_layer)
        if not isinstance(paddiam, list):
            pad_array = [paddiam]
        else:
            pad_array = paddiam
        antipad_array = [antipaddiam] if not isinstance(antipaddiam, list) else antipaddiam
        if pad_shape == "Circle":  # pragma no cover
            pad_shape = CorePadGeometryType.PADGEOMTYPE_CIRCLE
        elif pad_shape == "Rectangle":  # pragma no cover
            pad_array = [x_size, y_size]
            pad_shape = CorePadGeometryType.PADGEOMTYPE_RECTANGLE
        elif pad_shape == "Polygon":
            if isinstance(pad_polygon, list):
                pad_polygon = PolygonData(core=CorePolygonData(points=pad_polygon))
        if antipad_shape == "Bullet":  # pragma no cover
            antipad_array = [x_size, y_size, corner_radius]
            antipad_shape = CorePadGeometryType.PADGEOMTYPE_BULLET
        elif antipad_shape == "Rectangle":  # pragma no cover
            antipad_array = [anti_pad_x_size, anti_pad_y_size]
            antipad_shape = CorePadGeometryType.PADGEOMTYPE_RECTANGLE
        elif antipad_shape == "Polygon":
            if isinstance(antipad_polygon, list):
                antipad_polygon = PolygonData(core=CorePolygonData(points=antipad_polygon))
        else:
            antipad_array = [antipaddiam] if not isinstance(antipaddiam, list) else antipaddiam
            antipad_shape = CorePadGeometryType.PADGEOMTYPE_CIRCLE
        if add_default_layer:  # pragma no cover
            layers = layers + ["Default"]
        if antipad_shape == "Polygon" and pad_shape == "Polygon":
            for layer in layers:
                if pad_polygon.core is not None:
                    padstack_data.set_pad_parameters(
                        layer=layer,
                        pad_type=CorePadType.REGULAR_PAD,
                        offset_x=pad_offset_x,
                        offset_y=pad_offset_y,
                        rotation=pad_rotation,
                        poly=pad_polygon.core,
                    )
                else:
                    self._pedb.logger.error(
                        f"Polygon used for defining pad-stack {padstackname} pad on layer {layer} is not valid"
                    )
                if antipad_polygon.core is not None:
                    padstack_data.set_pad_parameters(
                        layer=layer,
                        pad_type=CorePadType.ANTI_PAD,
                        offset_x=pad_offset_x,
                        offset_y=pad_offset_y,
                        rotation=pad_rotation,
                        poly=antipad_polygon.core,
                    )
                else:
                    self._pedb.logger.error(
                        f"Polygon used for defining pad-stack {padstackname} anti-pad on layer {layer} is not valid"
                    )
        else:
            for layer in layers:
                padstack_data.set_pad_parameters(
                    layer=layer,
                    pad_type=CorePadType.REGULAR_PAD,
                    offset_x=pad_offset_x,
                    offset_y=pad_offset_y,
                    rotation=pad_rotation,
                    type_geom=pad_shape,
                    sizes=pad_array,
                )

                padstack_data.set_pad_parameters(
                    layer=layer,
                    pad_type=CorePadType.ANTI_PAD,
                    offset_x=pad_offset_x,
                    offset_y=pad_offset_y,
                    rotation=pad_rotation,
                    type_geom=antipad_shape,
                    sizes=antipad_array,
                )

        padstack_definition = PadstackDef.create(self._pedb, padstackname)
        padstack_definition.data = padstack_data
        self._logger.info(f"Padstack {padstackname} successfully created.")
        return padstackname

    def _get_pin_layer_range(self, pin: PadstackInstance) -> Union[Tuple[str, str], bool]:
        layers = pin.get_layer_range()
        if layers:
            return layers[0], layers[1]
        else:
            return False

    def duplicate(self, target_padstack_name: str, new_padstack_name: str = "") -> str:
        """
        Duplicate a padstack definition.

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
        if not new_padstack_name:
            new_padstack_name = generate_unique_name(target_padstack_name)
        padstack_definition = PadstackDef.create(self, new_padstack_name)
        padstack_definition.data = self.definitions[target_padstack_name].core.data
        return new_padstack_name

    @deprecate_argument_name({"fromlayer": "from_layer", "tolayer": "to_layer", "solderlayer": "solder_ball_layer"})
    def place(
        self,
        position: List[float],
        definition_name: str | PadstackDef,
        net_name: str = "",
        via_name: str = "",
        rotation: float = 0.0,
        from_layer: Optional[str] = None,
        to_layer: Optional[str] = None,
        solder_ball_layer: Optional[str] = None,
        is_pin: bool = False,
        layer_map: str = "two_way",
    ) -> PadstackInstance:
        """
        Place a padstack instance.

        Parameters
        ----------
        position : list[float, float]
            [x, y] position for placement.
        definition_name : str or :class:`PadstackDef`
            Padstack definition name.
        net_name : str, optional
            Net name. Default is ``""``.
        via_name : str, optional
            Instance name. Default is ``""``.
        rotation : float, optional
            Rotation in degrees. Default is ``0.0``.
        from_layer : str, optional
            Starting layer name.
        to_layer : str, optional
            Ending layer name.
        solder_ball_layer : str, optional
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
        if isinstance(definition_name, PadstackDef):
            padstack_def = definition_name
        else:
            padstack_def = self.definitions.get(definition_name)
        if not padstack_def:
            raise RuntimeError("Padstack definition not found")

        self._pedb.nets.find_or_create_net(net_name)
        rotation = self._pedb._value_setter(rotation * math.pi / 180)
        sign_layers_values = {}
        sign_layers = []
        if not from_layer:
            sign_layers_values = {i: v for i, v in self._pedb.stackup.signal_layers.items()}
            sign_layers = list(sign_layers_values.keys())
            try:
                from_layer = sign_layers_values[list(padstack_def.pad_by_layer.keys())[0]]
            except KeyError:
                from_layer = sign_layers_values[sign_layers[0]]

        if not to_layer:
            if not sign_layers_values:
                sign_layers_values = {i: v for i, v in self._pedb.stackup.signal_layers.items()}
            if not sign_layers:
                sign_layers = list(sign_layers_values.keys())
            try:
                to_layer = sign_layers_values[list(padstack_def.pad_by_layer.keys())[-1]]
            except KeyError:
                to_layer = sign_layers_values[sign_layers[-1]]

        if solder_ball_layer:
            solder_ball_layer = sign_layers_values[solder_ball_layer]
        if not via_name:
            via_name = generate_unique_name(padstack_def.name)
        if padstack_def:
            padstack_instance = PadstackInstance.create(
                layout=self._active_layout,
                net=net_name,
                padstack_definition=padstack_def,
                position_x=self._pedb._value_setter(position[0]),
                position_y=self._pedb._value_setter(position[1]),
                rotation=rotation,
                top_layer=from_layer,
                bottom_layer=to_layer,
                name=via_name,
                solder_ball_layer=solder_ball_layer,
                layer_map=layer_map,
            )
            padstack_instance.is_pin = is_pin
            return padstack_instance
        else:
            raise RuntimeError("Place padstack failed")

    def remove_pads_from_padstack(self, padstack_name: str, layer_name: Optional[str] = None):
        """
        Remove pads from a padstack definition on specified layers.

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
        pad_type = CorePadType.REGULAR_PAD
        pad_geo = CorePadGeometryType.PADGEOMTYPE_CIRCLE
        vals = 0
        params = [0]
        new_padstack_definition_data = CorePadstackDefData(self.definitions[padstack_name].data.core)
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
        """
        Set pad and anti-pad properties for a padstack definition.

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
            "Circle": CorePadGeometryType.PADGEOMTYPE_CIRCLE,
            "Square": CorePadGeometryType.PADGEOMTYPE_SQUARE,
            "Rectangle": CorePadGeometryType.PADGEOMTYPE_RECTANGLE,
            "Oval": CorePadGeometryType.PADGEOMTYPE_OVAL,
            "Bullet": CorePadGeometryType.PADGEOMTYPE_BULLET,
        }
        pad_shape = shape_dict[pad_shape]
        if not isinstance(pad_params, list):
            pad_params = [pad_params]
        pad_params = [self._pedb._value_setter(i) for i in pad_params]
        pad_x_offset = self._pedb._value_setter(pad_x_offset)
        pad_y_offset = self._pedb._value_setter(pad_y_offset)
        pad_rotation = self._pedb._value_setter(pad_rotation)

        antipad_shape = shape_dict[antipad_shape]
        if not isinstance(antipad_params, list):
            antipad_params = [antipad_params]
        antipad_params = [self._pedb._value_setter(i) for i in antipad_params]
        antipad_x_offset = self._pedb._value_setter(antipad_x_offset)
        antipad_y_offset = self._pedb._value_setter(antipad_y_offset)
        antipad_rotation = self._pedb._value_setter(antipad_rotation)
        cloned_padstack_def_data = self.definitions[padstack_name].core.data
        if not layer_name:
            layer_name = list(self._pedb.stackup.signal_layers.keys())
        elif isinstance(layer_name, str):
            layer_name = [layer_name]
        for layer in layer_name:
            cloned_padstack_def_data.set_pad_parameters(
                layer=layer,
                pad_type=CorePadType.REGULAR_PAD,
                offset_x=pad_x_offset,
                offset_y=pad_y_offset,
                rotation=pad_rotation,
                type_geom=pad_shape,
                sizes=pad_params,
            )
            cloned_padstack_def_data.set_pad_parameters(
                layer=layer,
                pad_type=CorePadType.ANTI_PAD,
                offset_x=antipad_x_offset,
                offset_y=antipad_y_offset,
                rotation=antipad_rotation,
                type_geom=antipad_shape,
                sizes=antipad_params,
            )
        self.definitions[padstack_name].data = cloned_padstack_def_data
        return True

    def get_instances(
        self,
        name: Optional[str] = None,
        pid: Optional[int] = None,
        definition_name: Optional[str] = None,
        net_name: Optional[Union[str, List[str]]] = None,
        component_reference_designator: Optional[str] = None,
        component_pin: Optional[str] = None,
    ) -> List[PadstackInstance]:
        """
        Get padstack instances by search criteria.

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
        instances_dict = self.instances
        instances = []
        if pid:
            instance = instances_dict.get(pid, None)
            return [instance] if instance is not None else []
        elif name:
            instances = [inst for inst in self.instances.values() if inst.aedt_name == name]
            if instances:
                return instances
            else:
                return []
        else:
            if definition_name:
                definition_name = definition_name if isinstance(definition_name, list) else [definition_name]
                instances = [inst for inst in instances_dict.values() if inst.padstack_def.name in definition_name]
            if net_name:
                net_name = net_name if isinstance(net_name, list) else [net_name]
                instances = [inst for inst in instances_dict.values() if inst.net_name in net_name]
            if component_reference_designator:
                refdes = (
                    component_reference_designator
                    if isinstance(component_reference_designator, list)
                    else [component_reference_designator]
                )
                instances = [inst for inst in instances_dict.values() if inst.component]
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
        pinlist_position: dict = None,
    ) -> List[PadstackInstance]:
        """
        Find reference pins near a specified pin.

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
        if not pinlist_position:
            pinlist = []
            if not positive_pin:
                search_radius = 10e-2
                component_only = True
            if component_only:
                references_pins = [
                    pin
                    for pin in list(positive_pin.component.pins.values())
                    if pin.net_name == reference_net and isinstance(pin, PadstackInstance)
                ]
                references_pins = [pin for pin in references_pins if not pin.terminal]
                if not references_pins:
                    return pinlist
            else:
                references_pins = self.get_instances(net_name=reference_net)
                if not references_pins:
                    return pinlist
            pinlist_position = {p: p.position for p in references_pins}
        pos_position = positive_pin.position
        pinlist = [
            p
            for p, pos in pinlist_position.items()
            if GeometryOperators.points_distance(pos_position, pos) <= search_radius
        ]
        if max_limit and len(pinlist) > max_limit:
            pin_dict = {GeometryOperators.points_distance(pos_position, p.position): p for p in pinlist}
            pinlist = [pin[1] for pin in sorted(pin_dict.items())[:max_limit]]
        return pinlist

    def get_padstack_instances_rtree_index(self, nets: Optional[Union[str, List[str]]] = None) -> "rtree.index.Index":
        """
        Returns padstack instances Rtree index.

        Parameters
        ----------
        nets : str or list, optional
            net name of list of nets name applying filtering on padstack instances selection. If ``None`` is provided
            all instances are included in the index. Default value is ``None``.

        Returns
        -------
        Rtree index object.

        """
        try:
            import rtree
        except ImportError:
            raise ImportError(
                "Rtree library is required for spatial indexing. "
                "Please install it using 'pip install pyedb[geometry]' or 'pip install rtree'."
            )

        if isinstance(nets, str):
            nets = [nets]
        padstack_instances_index = rtree.index.Index()
        if nets:
            instances = [inst for inst in self.instances.values() if inst.net_name in nets]
        else:
            instances = self.instances.values()
        for inst in instances:
            padstack_instances_index.insert(inst.id, inst.position)
        return padstack_instances_index

    def get_padstack_instances_id_intersecting_polygon(
        self,
        points: List[Tuple[float, float]],
        nets: Optional[Union[str, List[str]]] = None,
        padstack_instances_index: Optional[Union[Dict[int, Tuple[float, float]], "rtree.index.Index"]] = None,
    ) -> List[int]:
        """
        Returns the list of padstack instances ID intersecting a given bounding box and nets.

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

        polygon_x = [float(pt[0]) for pt in points]
        polygon_y = [float(pt[1]) for pt in points]
        polygon = [polygon_x, polygon_y]
        min_x, max_x = min(polygon_x), max(polygon_x)
        min_y, max_y = min(polygon_y), max(polygon_y)

        net_filter = [nets] if isinstance(nets, str) else nets

        if padstack_instances_index and hasattr(padstack_instances_index, "intersection"):
            candidate_ids = self.get_padstack_instances_intersecting_bounding_box(
                [min_x, min_y, max_x, max_y],
                nets=nets,
                padstack_instances_index=padstack_instances_index,
            )
            candidate_positions = ((inst_id, self.instances[inst_id].position) for inst_id in candidate_ids)
        else:
            if not padstack_instances_index:
                instances = self.instances.values()
                if net_filter:
                    instances = [inst for inst in instances if inst.net_name in net_filter]
                candidate_positions = ((inst.id, inst.position) for inst in instances)
            else:
                candidate_positions = padstack_instances_index.items()

        inside_ids = []
        for inst_id, position in candidate_positions:
            try:
                x = float(position[0])
                y = float(position[1])
            except (TypeError, ValueError, IndexError):
                continue

            if not (math.isfinite(x) and math.isfinite(y)):
                continue
            if x < min_x or x > max_x or y < min_y or y > max_y:
                continue
            if GeometryOperators.is_point_in_polygon([x, y], polygon):
                inside_ids.append(inst_id)
        return inside_ids

    def get_padstack_instances_intersecting_bounding_box(
        self,
        bounding_box: List[float],
        nets: Optional[Union[str, List[str]]] = None,
        padstack_instances_index: Optional["rtree.index.Index"] = None,
    ) -> List[int]:
        """
        Returns the list of padstack instances ID intersecting a given bounding box and nets.

        Parameters
        ----------
        bounding_box : tuple or list
            Bounding box as ``[x1, y1, x2, y2]``.
        nets : str or list, optional
            Net name or list of net names to filter padstack instances. If ``None``, all
            instances are included. The default is ``None``.
        padstack_instances_index : optional
            Rtree index object. Can be provided to avoid recomputing the index.

        Returns
        -------
        list[int]
            List of padstack instance IDs intersecting the bounding box.

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
        """
        Replace padstack instances along lines into a single polygon.

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

        selected_angles : list[int or float], optional
            Angles in degrees to detect. For example, ``[0, 180]`` detects only
            horizontal and vertical lines. When ``None``, all angles are detected.
            The default is ``None``.

        padstack_instances_id : list[int], optional
            List of padstack instance IDs to include. If ``None``, the algorithm
            scans all padstack instances belonging to the specified net.
            The default is ``None``.

        Returns
        -------
        list[str]
            List of created padstack instance IDs.

        """
        _def = list(set([inst.padstack_def for inst in list(self.instances.values()) if inst.net_name == net_name]))
        if not _def:
            self._logger.error(f"No padstack definition found for net {net_name}")
            return []
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
                    self._logger.error(f"Failed to create padstack definition {new_padstack_def}")
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
    ) -> List[PadstackInstance]:
        """
        Evaluate pad-stack instances included on the provided point list and replace all by single instance.

        Parameters
        ----------
        contour_boxes : list[list[list[float]]]
            Nested list of polygons, each defined by a list of ``[x, y]`` points.
        net_filter : str or list[str], optional
            Net name or list of net names to exclude from the via merge.
        start_layer : str, optional
            Padstack instance start layer. If ``None``, the top layer is used.
        stop_layer : str, optional
            Padstack instance stop layer. If ``None``, the bottom layer is used.

        Returns
        -------
        list[:class:`PadstackInstance <pyedb.grpc.database.primitive.padstack_instance.PadstackInstance>`]
            List of created padstack instances.

        """
        try:
            from scipy.spatial import ConvexHull
        except ImportError:
            raise ImportError(
                "Scipy library is required for convex hull calculations. "
                "Please install it using 'pip install pyedb[geometry]' or 'pip install scipy'."
            )

        merged_vias = []
        if not contour_boxes:
            raise Exception("No contour box provided, you need to pass a nested list as argument.")
        instances_index = {}
        instances_dict = self.instances
        for id, inst in instances_dict.items():
            instances_index[id] = inst.position
        for contour_box in contour_boxes:
            instances = self.get_padstack_instances_id_intersecting_polygon(
                points=[tuple(pt) for pt in contour_box], padstack_instances_index=instances_index
            )
            if net_filter:
                instances = [id for id in instances if not instances_dict[id].net.name in net_filter]
            net = instances_dict[instances[0]].net.name
            instances_pts = np.array([instances_dict[inst].position for inst in instances])
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
            merged_vias.append(merged_instance)
            [instances_dict[inst].delete() for inst in instances]
        return merged_vias

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

                for item in padstacks_inbox:
                    if item not in to_keep:
                        self.instances[item].delete()
                return True

    @staticmethod
    def dbscan(
        padstack: Dict[int, List[float]], max_distance: float = 1e-3, min_samples: int = 5
    ) -> Dict[int, List[int]]:
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
        clusters: Dict[int, List[int]] = defaultdict(list)
        for i, label in enumerate(labels):
            clusters[int(label)].append(padstack_ids[i])

        return dict(clusters)

    def reduce_via_by_density(
        self, padstacks: List[int], cell_size_x: float = 1e-3, cell_size_y: float = 1e-3, delete: bool = False
    ) -> tuple[List[int], List[List[List[float]]]]:
        """
        Reduce the number of vias by density.

        Keeps only one via closest to the center of each grid cell. The cells
        are automatically populated based on the input vias.

        Parameters
        ----------
        padstacks : list[int]
            List of padstack IDs to be reduced.
        cell_size_x : float, optional
            Width of each grid cell in meters. The default is ``1e-3``.
        cell_size_y : float, optional
            Height of each grid cell in meters. The default is ``1e-3``.
        delete : bool, optional
            If ``True``, delete vias that are not kept. The default is ``False``.

        Returns
        -------
        tuple[list[int], list[list[list[float]]]]
            Tuple of ``(kept_ids, grid)`` where ``kept_ids`` is the list of via IDs
            kept after reduction, and ``grid`` is the list of grid cell coordinate
            boundaries for plotting.

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
