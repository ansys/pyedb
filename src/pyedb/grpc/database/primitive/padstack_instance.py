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
from __future__ import annotations

import math
import re
from typing import TYPE_CHECKING, Union
import warnings

if TYPE_CHECKING:
    from pyedb.grpc.database.layers.stackup_layer import StackupLayer
from ansys.edb.core.database import ProductIdType as GrpcProductIdType
from ansys.edb.core.geometry.point_data import PointData as GrpcPointData
from ansys.edb.core.geometry.polygon_data import PolygonData as GrpcPolygonData
from ansys.edb.core.hierarchy.pin_group import PinGroup as GrpcPinGroup
from ansys.edb.core.hierarchy.structure3d import MeshClosure as GrpcMeshClosure, Structure3D as GrpcStructure3D
from ansys.edb.core.primitive.padstack_instance import (
    PadstackInstance as GrpcPadstackInstance,
)
from ansys.edb.core.terminal.pin_group_terminal import (
    PinGroupTerminal as GrpcPinGroupTerminal,
)

from pyedb.generic.general_methods import generate_unique_name
from pyedb.grpc.database.definition.padstack_def import PadstackDef
from pyedb.grpc.database.modeler import Circle
from pyedb.grpc.database.net.net import Net
from pyedb.grpc.database.terminal.padstack_instance_terminal import (
    PadstackInstanceTerminal,
)
from pyedb.grpc.database.utility.layer_map import LayerMap
from pyedb.grpc.database.utility.value import Value
from pyedb.modeler.geometry_operators import GeometryOperators


class PadstackInstance:
    """Manages EDB functionalities for a padstack.

    Parameters
    ----------
    :class:`PadstackInstance <pyedb.grpc.dataybase.primitive.PadstackInstance>`
        PadstackInstance object.

    Examples
    --------
    >>> from pyedb import Edb
    >>> edb = Edb(myedb, edbversion="2021.2")
    >>> edb_padstack_instance = edb.padstacks.instances[0]
    """

    def __init__(self, pedb, edb_instance):
        self.core = edb_instance
        self._pedb = pedb
        self._bounding_box = []
        self._position = []
        self._side_number = None
        self._pdef = None
        self._object_instance = None

    @classmethod
    def create(
        cls,
        layout,
        padstack_definition: str,
        net: Union[Net, str],
        position_x: float,
        position_y: float,
        rotation: float,
        top_layer: StackupLayer,
        bottom_layer: StackupLayer,
        name: str = None,
        solder_ball_layer: StackupLayer = None,
        layer_map: str = "two_way",
    ) -> PadstackInstance:
        """Create a padstack instance.

        Parameters
        ----------
        layout : :class:`Layout <py
            edb.grpc.database.layout.layout.Layout>`
            Layout object.
        net : :class:`Net <pyedb.grpc.database.net.net.Net>` or str
            Net object or net name.
        padstack_definition : str
            Padstack definition name.
        position_x : float
            X position.
        position_y : float
            Y position.
        rotation : float
            Rotation.
        top_layer : :class:`StackupLayer <pyedb.grpc.database.layers.stackup_layer.StackupLayer>`
            Top layer.
        bottom_layer : :class:`StackupLayer <pyedb.grpc.database.layers.stackup_layer.StackupLayer>`
            Bottom layer.
        name : str, optional
            Padstack instance name. The default is ``None``, in which case a name is automatically assigned.
        solder_ball_layer : :class:`StackupLayer <pyedb.grpc.database.layers.stackup_layer.StackupLayer>`, optional
            Solder ball layer. The default is ``None``.
        layer_map : str, optional
            Layer map type. The default is ``"two_way"``. Options are ``"forward"``, ``"backward"``.

        Returns
        -------
        :class:`PadstackInstance <pyedb.grpc.database.primitive.padstack_instance.PadstackInstance>`
            PadstackInstance object.
        """
        if isinstance(net, str):
            net = layout._pedb.nets.nets.get(net, Net.create(layout, generate_unique_name("net")))
        if isinstance(padstack_definition, PadstackDef):
            padstack_definition = padstack_definition.name
        if not name:
            name = generate_unique_name(padstack_definition)
        layer_map = LayerMap.create(layer_map)
        if not padstack_definition in layout._pedb.padstacks.definitions:
            raise Exception(f"Padstack definition {padstack_definition} not found in layout.")
        padstack_def = layout._pedb.padstacks.definitions[padstack_definition].core
        inst = GrpcPadstackInstance.create(
            layout=layout.core,
            net=net.core,
            padstack_def=padstack_def,
            position_x=layout._pedb.value(position_x),
            position_y=layout._pedb.value(position_y),
            rotation=layout._pedb.value(rotation),
            top_layer=top_layer.core,
            bottom_layer=bottom_layer.core,
            name=name,
            solder_ball_layer=solder_ball_layer.core if solder_ball_layer else None,
            layer_map=layer_map.core,
        )
        return cls(layout._pedb, inst)

    @property
    def is_pin(self):
        """Property added for backward compatibility with earlier versions of pyEDB."""
        return self.core.is_layout_pin

    @is_pin.setter
    def is_pin(self, value):
        """Property added for backward compatibility with earlier versions of pyEDB."""
        self.core.is_layout_pin = value

    @property
    def net(self):
        """Net.

        Returns
        -------
        :class:`Net <pyedb.grpc.database.net.net.Net>`
            Net object.
        """

        net = Net(self._pedb, self.core.net)
        return net if net is not None else None

    @net.setter
    def net(self, value):
        """Net.

        Parameters
        ----------
        value : :class:`Net <pyedb.grpc.database.net.net.Net>`
            Net object.
        """
        if isinstance(value, Net):
            self.core.net = value.core

    @property
    def layout(self):
        """Layout.

        Returns
        -------
        :class:`Layout <pyedb.grpc.database.layout.layout.Layout>`
            Layout object.
        """
        return self._pedb.active_layout

    @property
    def is_null(self):
        """Check if the padstack instance is null.

        Returns
        -------
        bool
            True if the padstack instance is null, False otherwise.
        """
        return self.core.is_null

    @property
    def definition(self) -> PadstackDef:
        """Padstack definition.

        Returns
        -------
        :class:`PadstackDef`<pyedb.grpc.database.definition.padstack_def.PadstackDef>`
        """
        return PadstackDef(self._pedb, self.core.padstack_def)

    @property
    def padstack_definition(self) -> str:
        """Padstack definition name.

        Returns
        -------
        str
            Padstack definition name.

        """
        return self.core.padstack_def.name

    @property
    def terminal(self) -> PadstackInstanceTerminal:
        """PadstackInstanceTerminal.

        Returns
        -------
        :class:`PadstackInstanceTerminal <pyedb.grpc.database.terminal.padstack_instance_terminal.
        PadstackInstanceTerminal>`
            PadstackInstanceTerminal object.
        """
        from pyedb.grpc.database.terminal.padstack_instance_terminal import (
            PadstackInstanceTerminal,
        )

        term = self.core.get_padstack_instance_terminal()
        if not term.is_null:
            term = PadstackInstanceTerminal(self._pedb, term)
        return term if not term.is_null else None

    @property
    def side_number(self):
        """Return the number of sides meshed of the padstack instance.
        Returns
        -------
        int
            Number of sides meshed of the padstack instance.
        """
        side_value = self.core.get_product_property(GrpcProductIdType.HFSS_3D_LAYOUT, 21)
        if side_value:
            return int(re.search(r"(?m)^\s*sid=(\d+)", side_value).group(1))
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
            self.core.set_product_property(GrpcProductIdType.HFSS_3D_LAYOUT, 21, prop_string)
        else:
            raise ValueError("Number of sides must be an integer between 3 and 64")

    def delete(self):
        """Delete the padstack instance."""
        try:
            self._pedb.padstacks._instances.pop(self.core.edb_uid, None)
        except Exception:
            self._pedb.padstacks.clear_instances_cache()
        self.core.delete()

    def set_backdrill_top(self, drill_depth, drill_diameter, offset=0.0):
        """Set backdrill from top.

        .deprecated:: 0.55.0
        Use :method:`set_back_drill_by_depth` instead.

        Parameters
        ----------
        drill_depth : str
            Name of the drill to layer.
        drill_diameter : float, str
            Diameter of backdrill size.
        offset : str, optional.
            offset with respect to the layer to drill to.

        Returns
        -------
        bool
            True if success, False otherwise.
        """
        warnings.warn(
            "`set_backdrill_top` is deprecated. Use `set_back_drill_by_depth` or `set_back_drill_by_layer` instead.",
            DeprecationWarning,
        )
        if isinstance(drill_depth, str):
            if drill_depth in self._pedb.stackup.layers:
                return self.set_back_drill_by_layer(
                    drill_to_layer=self._pedb.stackup.layers[drill_depth],
                    offset=Value(offset),
                    diameter=Value(drill_diameter),
                    from_bottom=False,
                )
            else:
                return self.set_back_drill_by_depth(Value(drill_depth), Value(drill_diameter), from_bottom=False)

    def set_backdrill_bottom(self, drill_depth, drill_diameter, offset=0.0):
        """Set backdrill from bottom.

        .deprecated: 0.55.0
        Use: method:`set_back_drill_by_depth` instead.

        Parameters
        ----------
        drill_depth : str
            Name of the drill to layer.
        drill_diameter : float, str
            Diameter of backdrill size.
        offset : str, optional.
            offset with respect to the layer to drill to.

        Returns
        -------
        bool
            True if success, False otherwise.
        """
        warnings.warn(
            "`set_backdrill_bottom` is deprecated. Use `set_back_drill_by_depth` or `set_back_drill_by_layer` instead.",
            DeprecationWarning,
        )
        if isinstance(drill_depth, str):
            if drill_depth in self._pedb.stackup.layers:
                return self.set_back_drill_by_layer(
                    drill_to_layer=self._pedb.stackup.layers[drill_depth],
                    offset=Value(offset),
                    diameter=Value(drill_diameter),
                    from_bottom=True,
                )
            else:
                return self.set_back_drill_by_depth(Value(drill_depth), Value(drill_diameter), from_bottom=True)

    def create_terminal(self, name=None) -> PadstackInstanceTerminal:
        """Create a padstack instance terminal.

        Returns
        -------
        :class:`PadstackInstanceTerminal <pyedb.grpc.database.terminal.padstack_instance_terminal.
        PadstackInstanceTerminal>`
            PadstackInstanceTerminal object.

        """
        if not name:
            name = self.name
        term = PadstackInstanceTerminal.create(
            layout=self.layout,
            name=name,
            padstack_instance=self,
            layer=self.core.get_layer_range()[0],
            net=self.net,
            is_ref=False,
        )
        return term

    def get_terminal(self, create_new_terminal=True) -> PadstackInstanceTerminal:
        """Returns padstack instance terminal.

        Parameters
        ----------
        create_new_terminal : bool, optional
            If terminal instance is not created,
            and value is ``True``, a new PadstackInstanceTerminal is created.

        Returns
        -------
        :class:`PadstackInstanceTerminal <pyedb.grpc.database.terminal.padstack_instance_terminal.
        PadstackInstanceTerminal>`
            PadstackInstanceTerminal object.

        """
        inst_term = self.core.get_padstack_instance_terminal()
        if inst_term.is_null and create_new_terminal:
            inst_term = self.create_terminal()
            inst_term = inst_term.core
        return PadstackInstanceTerminal(self._pedb, inst_term)

    def create_coax_port(self, name=None, radial_extent_factor=0):
        """Create a coax port.

        Parameters
        ----------
        name : str, optional.
            Port name, the default is ``None``, in which case a name is automatically assigned.
        radial_extent_factor : int, float, optional
            Radial extent of coaxial port.

        Returns
        -------
        :class:`Terminal <pyedb.grpc.database.terminal.terminal.Terminal>`
            Port terminal.
        """
        port = self.create_port(name)
        port.radial_extent_factor = radial_extent_factor
        return port

    def create_port(self, name=None, reference=None, is_circuit_port=False):
        """Create a port on the padstack instance.

        Parameters
        ----------
        name : str, optional
            Name of the port. The default is ``None``, in which case a name is automatically assigned.
        reference : reference net or pingroup  optional
            Negative terminal of the port.
        is_circuit_port : bool, optional
            Whether it is a circuit port.

        Returns
        -------
        :class:`Terminal <pyedb.grpc.database.terminal.terminal.Terminal>`
            Port terminal.
        """
        if not reference:
            return self.create_terminal(name)
        else:
            positive_terminal = self.create_terminal()
            if positive_terminal.is_null:
                self._pedb.logger(
                    f"Positive terminal on padsatck instance {self.name} is null. Make sure a terminal"
                    f"is not already defined."
                )
            negative_terminal = None
            if isinstance(reference, list):
                pg = GrpcPinGroup.create(
                    self.core.layout, name=f"pingroup_{self.name}_ref", padstack_instances=reference
                )
                negative_terminal = GrpcPinGroupTerminal.create(
                    layout=self.core.layout,
                    name=f"pingroup_term{self.name}_ref)",
                    pin_group=pg,
                    net=reference[0].net,
                    is_ref=True,
                )
                is_circuit_port = True
            else:
                if isinstance(reference, PadstackInstance):
                    negative_terminal = reference.create_terminal()
                elif isinstance(reference, str):
                    if reference in self._pedb.padstacks.instances:
                        reference = self._pedb.padstacks.instances[reference]
                    else:
                        pin_groups = [pg for pg in self._pedb.active_layout.pin_groups if pg.name == reference]
                        if pin_groups:
                            reference = pin_groups[0]
                        else:
                            self._pedb.logger.error(f"No reference found for {reference}")
                            return False
                    negative_terminal = reference.create_terminal()
            if negative_terminal:
                positive_terminal.reference_terminal = negative_terminal
            else:
                self._pedb.logger.error("No reference terminal created")
                return False
            positive_terminal.is_circuit_port = is_circuit_port
            negative_terminal.is_circuit_port = is_circuit_port
            return positive_terminal

    @property
    def _em_properties(self):
        """Get EM properties."""
        from ansys.edb.core.database import ProductIdType

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

        p = self.core.get_product_property(ProductIdType.DESIGNER, 18)
        if p:
            return p
        else:
            return default

    @_em_properties.setter
    def _em_properties(self, em_prop):
        """Set EM properties"""
        pid = self._pedb.core.ProductId.Designer
        self.core.set_product_property(pid, 18, em_prop)

    @property
    def dcir_equipotential_region(self) -> bool:
        """Check whether dcir equipotential region is enabled.

        Returns
        -------
        bool

        """
        pattern = r"'DCIR Equipotential Region'='([^']+)'"
        em_pp = self._em_properties
        result = re.search(pattern, em_pp).group(1)
        if result == "true":
            return True
        else:
            return False

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
        """Layout object instance.

        Returns
        -------
        :class:`LayoutObjInstance <ansys.edb.core.layout_instance.layout_obj_instance import.LayoutObjInstance>`

        """
        if not self._object_instance:
            self._object_instance = self.core.layout.layout_instance.get_layout_obj_instance_in_context(self.core, None)
        return self._object_instance

    @property
    def bounding_box(self) -> tuple[tuple[float, float], tuple[float, float]]:
        """Padstack instance bounding box.
        Because this method is slow, the bounding box is stored in a variable and reused.

        Returns
        -------
        list of float
        """
        if self._bounding_box:
            return self._bounding_box
        bbox = self.layout_object_instance.get_bbox()
        pt1 = bbox.points[0]
        pt2 = bbox.points[2]
        self._bounding_box = ((pt1.x.value, pt1.y.value), (pt2.x.value, pt2.y.value))
        return self._bounding_box

    def in_polygon(self, polygon_data, include_partial=True, arbitrary_extent_value=300e-6) -> bool:
        """Check if padstack Instance is in given polygon data.

        Parameters
        ----------
        polygon_data : PolygonData Object
        include_partial : bool, optional
            Whether to include partial intersecting instances. The default is ``True``.
        simple_check : bool, optional
            Whether to perform a single check based on the padstack center or check the padstack bounding box.
        arbitrary_extent_value : float, optional
            When ``include_partial`` is ``True``, an arbitrary value is used to create a bounding box for the padstack
            instance to check for intersection and save computation time during the cutout. The default is ``300e-6``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        int_val = 1 if polygon_data.is_inside(GrpcPointData(self.position)) else 0
        if int_val == 0:
            if include_partial:
                # pad-stack instance bbox is slow we take an arbitrary value e.g. 300e-6
                arbitrary_value = arbitrary_extent_value
                position = self.position
                inst_bbox = [
                    position[0] - arbitrary_value / 2,
                    position[1] - arbitrary_value / 2,
                    position[0] + arbitrary_value / 2,
                    position[1] + arbitrary_value / 2,
                ]
                int_val = polygon_data.intersection_type(GrpcPolygonData(inst_bbox)).value
                if int_val == 0:  # fully outside
                    return False
                elif int_val in [2, 3]:  # fully or partially inside
                    return True
            return False
        else:
            return True

    @property
    def start_layer(self) -> str:
        """Starting layer.

        Returns
        -------
        str
            Name of the starting layer.
        """
        return self.core.get_layer_range()[0].name

    @start_layer.setter
    def start_layer(self, layer_name):
        stop_layer = self._pedb.stackup.signal_layers[self.stop_layer]
        start_layer = self._pedb.stackup.signal_layers[layer_name]
        self.core.set_layer_range(start_layer.core, stop_layer.core)

    @property
    def stop_layer(self) -> str:
        """Stopping layer.

        Returns
        -------
        str
            Name of the stopping layer.
        """
        return self.core.get_layer_range()[-1].name

    @stop_layer.setter
    def stop_layer(self, layer_name):
        start_layer = self._pedb.stackup.signal_layers[self.start_layer]
        stop_layer = self._pedb.stackup.signal_layers[layer_name]
        self.core.set_layer_range(start_layer.core, stop_layer.core)

    @property
    def layer_range_names(self) -> list[str]:
        """List of all layers to which the padstack instance belongs.

        Returns
        -------
        List[str]
            List of layer names.

        """
        layer_range = self.core.get_layer_range()
        if layer_range:
            start_layer, stop_layer = layer_range
        else:
            return []
        started = False
        layer_list = []
        start_layer_name = start_layer.name
        stop_layer_name = stop_layer.name
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
    def id(self):
        """Padstack instance ID."""
        return self.core.edb_uid

    @property
    def edb_uid(self):
        """Padstack instance EDB UID."""
        return self.core.edb_uid

    @property
    def net_name(self) -> str:
        """Net name.

        Returns
        -------
        str
            Name of the net.
        """
        if self.core.net.is_null:
            return ""
        else:
            return self.net.name

    @net_name.setter
    def net_name(self, val):
        if not self.core.is_null and not self.core.net.is_null:
            self.net = self._pedb.nets.nets[val]

    @property
    def layout_object_instance(self):
        """Layout object instance.

        Returns
        -------
        :class:`LayoutObjInstance <ansys.edb.core.layout_instance.layout_obj_instance.LayoutObjInstance>`

        """
        if not self._object_instance:
            self._object_instance = self.core.layout.layout_instance.get_layout_obj_instance_in_context(self.core, None)
        return self._object_instance

    @property
    def component(self):
        """Component.

        Returns
        -------
        :class:`Component <pyedb.grpc.database.hierarchy.component.Component>`

        """
        from pyedb.grpc.database.hierarchy.component import Component

        comp = Component(self._pedb, self.core.component)
        return comp if not comp.core.is_null else False

    @property
    def position(self) -> list[float]:
        """Padstack instance position.

        Returns
        -------
        list
            List of ``[x, y]`` coordinates for the padstack instance position.
        """
        position = self.core.get_position_and_rotation()
        if self.component:
            out2 = self.component.core.transform.transform_point(GrpcPointData(position[:2]))
            self._position = [Value(out2[0]), Value(out2[1])]
        else:
            self._position = [Value(pt) for pt in position[:2]]
        return self._position

    @position.setter
    def position(self, value):
        pos = []
        for v in value:
            if isinstance(v, (float, int, str)):
                pos.append(Value(v, self._pedb.active_cell))
            else:
                pos.append(v)
        point_data = GrpcPointData(pos[0], pos[1])
        self.core.set_position_and_rotation(
            x=point_data.x, y=point_data.y, rotation=Value(self.rotation, self._pedb.active_cell)
        )

    @property
    def rotation(self) -> float:
        """Padstack instance rotation.

        Returns
        -------
        float
            Rotatation value for the padstack instance.
        """
        return Value(self.core.get_position_and_rotation()[-1])

    @property
    def name(self) -> str:
        """Padstack Instance Name.

        Returns
        -------
        str
            If it is a pin, the syntax will be like in AEDT ComponentName-PinName.

        """
        if not self.core.name:
            return self.aedt_name
        else:
            return self.core.name

    @name.setter
    def name(self, value):
        self.core.name = value
        # changing aedt_name too
        self.core.set_product_property(GrpcProductIdType.DESIGNER, 11, value)

    @property
    def backdrill_type(self) -> str:
        """Backdrill type.


        Returns
        -------
        str
            Backdrill type.

        """
        return self.get_backdrill_type()

    @property
    def backdrill_top(self) -> bool:
        if self.core.get_back_drill_type(False).value == 0:
            return False
        else:
            try:
                if self.get_back_drill_by_layer(from_bottom=False):
                    return True
            except:
                return False

    @property
    def backdrill_bottom(self) -> bool:
        """Check is backdrill is starting at bottom.


        Returns
        -------
        bool

        """
        if self.core.get_back_drill_type(True).value == 0:
            return False
        else:
            try:
                if self.get_back_drill_by_layer(True):
                    return True
            except:
                return False

    @property
    def backdrill_diameter(self):
        parameters = []
        if self.backdrill_bottom:
            parameters = self.get_back_drill_by_layer(True)
        elif self.backdrill_top:
            parameters = self.get_back_drill_by_layer(False)
        if parameters:
            return round(parameters[-1].value, 9)
        return 0.0

    @backdrill_diameter.setter
    def backdrill_diameter(self, value):
        if self.backdrill_bottom:
            parameters = self.get_back_drill_by_layer(True)
            self.set_back_drill_by_layer(
                drill_to_layer=parameters[0],
                offset=parameters[1],
                diameter=self._pedb.value(value),
                from_bottom=True,
            )
        elif self.backdrill_top:
            parameters = self.get_back_drill_by_layer(False)
            self.set_back_drill_by_layer(
                drill_to_layer=parameters[0],
                offset=parameters[1],
                diameter=Value(value),
                from_bottom=False,
            )

    @property
    def backdrill_layer(self):
        parameters = []
        if self.backdrill_bottom:
            parameters = self.get_back_drill_by_layer(True)
        elif self.backdrill_top:
            parameters = self.get_back_drill_by_layer(False)
        if parameters:
            return parameters[0]
        return ""

    @backdrill_layer.setter
    def backdrill_layer(self, value):
        if self.backdrill_bottom:
            parameters = self.get_back_drill_by_layer(True)
            self.set_back_drill_by_layer(
                drill_to_layer=self._pedb.stackup.layers[value],
                offset=parameters[1],
                diameter=parameters[2],
                from_bottom=True,
            )
        elif self.backdrill_top:
            parameters = self.get_back_drill_by_layer(False)
            self.set_back_drill_by_layer(
                drill_to_layer=value,
                offset=parameters[1],
                diameter=parameters[2],
                from_bottom=False,
            )

    @property
    def backdrill_offset(self):
        parameters = []
        if self.backdrill_bottom:
            parameters = self.get_back_drill_by_layer(True)
        elif self.backdrill_top:
            parameters = self.get_back_drill_by_layer(False)
        if parameters:
            return parameters[1].value
        return 0.0

    @backdrill_offset.setter
    def backdrill_offset(self, value):
        if self.backdrill_bottom:
            parameters = self.get_back_drill_by_layer(True)
            self.set_back_drill_by_layer(
                drill_to_layer=parameters[0],
                offset=Value(value),
                diameter=parameters[2],
                from_bottom=True,
            )
        elif self.backdrill_top:
            parameters = self.get_back_drill_by_layer(False)
            self.set_back_drill_by_layer(
                drill_to_layer=parameters[0],
                offset=Value(value),
                diameter=parameters[2],
                from_bottom=False,
            )

    @property
    def padstack_def(self):
        """Padstack definition.

        Returns
        -------
        :class:`PadstackDef`<pyedb.grpc.database.definition.padstack_def.PadstackDef>`
        """
        return PadstackDef(self._pedb, self.core.padstack_def)

    @property
    def metal_volume(self) -> float:
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
            via_length = (
                self._pedb.stackup.signal_layers[start_layer].upper_elevation
                - self._pedb.stackup.signal_layers[stop_layer].lower_elevation
            )
            if self.get_backdrill_type == "layer_drill":
                layer, _, _ = self.get_back_drill_by_layer()
                start_layer = self._pedb.stackup.signal_layers[0]
                stop_layer = self._pedb.stackup.signal_layers[layer.name]
                via_length = (
                    self._pedb.stackup.signal_layers[start_layer].upper_elevation
                    - self._pedb.stackup.signal_layers[stop_layer].lower_elevation
                )
            elif self.get_backdrill_type == "depth_drill":
                drill_depth, _ = self.get_back_drill_by_depth()
                start_layer = self._pedb.stackup.signal_layers[0]
                via_length = self._pedb.stackup.signal_layers[start_layer].upper_elevation - drill_depth
            padstack_def = self._pedb.padstacks.definitions[self.core.padstack_def.name]
            hole_diameter = padstack_def.hole_diameter
            if hole_diameter:
                hole_finished_size = padstack_def.hole_finished_size
                volume = (math.pi * (hole_diameter / 2) ** 2 - math.pi * (hole_finished_size / 2) ** 2) * via_length
        return volume

    @property
    def component_pin(self) -> str:
        """Component pin.

        Returns
        -------
        str
            Component pin name.

        """
        return self.name

    @property
    def aedt_name(self) -> str:
        """Retrieve the pin name that is shown in AEDT.

        .. note::
           To obtain the EDB core pin name, use `pin.name`.

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

        name = self.core.get_product_property(GrpcProductIdType.DESIGNER, 11)
        return str(name).strip("'")

    @aedt_name.setter
    def aedt_name(self, value):
        self.core.set_product_property(GrpcProductIdType.DESIGNER, 11, value)

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

    def get_layer_range(self) -> tuple[str, str]:
        """Get the layer range of the padstack instance.

        Returns
        -------
        tuple
            Tuple of (start_layer_name, stop_layer_name).
        """
        layer_range = self.core.get_layer_range()
        if layer_range:
            start_layer, stop_layer = layer_range
            return start_layer.name, stop_layer.name
        return None, None

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
        stackup_layers = self._pedb.stackup.layers
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
        cloned_circle = Circle(self._pedb).create(
            layout=layout,
            layer=self.start_layer,
            net=self.net,
            center_x=Value(self.position[0]),
            center_y=Value(self.position[1]),
            radius=Value(rad_u),
        )
        cloned_circle2 = Circle(self._pedb).create(
            layout=layout,
            layer=self.stop_layer,
            net=self.net,
            center_x=Value(self.position[0]),
            center_y=Value(self.position[1]),
            radius=Value(rad_l),
        )

        s3d = GrpcStructure3D.create(
            layout.core, generate_unique_name("via3d_" + self.aedt_name.replace("via_", ""), n=3)
        )
        s3d.add_member(cloned_circle.core)
        s3d.add_member(cloned_circle2.core)
        s3d.set_material(self.definition.material)
        s3d.mesh_closure = GrpcMeshClosure.ENDS_CLOSED
        hole_override_enabled = True
        hole_override_diam = 0
        self.core.set_hole_overrides(hole_override_enabled, Value(hole_override_diam))

    def get_backdrill_type(self, from_bottom=True):
        """Return backdrill type
        Parameters
        ----------
        from_bottom : bool, optional
            default value is `True.`

        Return
        ------
        str
            Back drill type, `"layer_drill"`,`"depth_drill"`, `"no_drill"`.

        """
        return self.core.get_back_drill_type(from_bottom).name.lower()

    def get_back_drill_by_layer(self, from_bottom=True) -> tuple[str, float, float]:
        """Get backdrill by layer.

        Parameters
        ----------
        from_bottom : bool, optional.
         Default value is `True`.

         Return
         ------
         tuple (layer, offset, diameter) (str, [float, float], float).

        """
        back_drill = self.core.get_back_drill_by_layer(from_bottom)
        layer = back_drill[0].name
        offset = Value(back_drill[1])
        diameter = Value(back_drill[2])
        return layer, offset, diameter

    def get_back_drill_by_depth(self, from_bottom=True) -> tuple[float, float]:
        """Get back drill by depth parameters
        Parameters
        ----------
        from_bottom : bool, optional
            Default value is `True`.

        Return
        ------
        tuple (drill_depth, drill_diameter) (float, float)
        """
        back_drill = self.core.get_back_drill_by_depth(from_bottom)
        drill_depth = Value(back_drill[0])
        drill_diameter = Value(back_drill[1])
        return drill_depth, drill_diameter

    def set_back_drill_by_depth(self, drill_depth, diameter, from_bottom=True):
        """Set back drill by depth.

        Parameters
        ----------
        drill_depth : str, float
            drill depth value
        diameter : str, float
            drill diameter
        from_bottom : bool, optional
            Default value is `True`.
        """
        self.core.set_back_drill_by_depth(
            drill_depth=Value(drill_depth), diameter=Value(diameter), from_bottom=from_bottom
        )

    def set_back_drill_by_layer(self, drill_to_layer, offset, diameter, from_bottom=True):
        """Set back drill layer.

        Parameters
        ----------
        drill_to_layer : str, Layer
            Layer to drill to.
        offset : str, float
            Offset value
        diameter : str, float
            Drill diameter
        from_bottom : bool, optional
            Default value is `True`
        """
        if isinstance(drill_to_layer, str):
            drill_to_layer = self._pedb.stackup.layers[drill_to_layer]
        self.core.set_back_drill_by_layer(
            drill_to_layer=drill_to_layer.core,
            offset=Value(offset),
            diameter=Value(diameter),
            from_bottom=from_bottom,
        )

    def parametrize_position(self, prefix=None) -> list[str]:
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

    def in_voids(self, net_name=None, layer_name=None) -> list[any]:
        """Check if this padstack instance is in any void.

        Parameters
        ----------
        net_name : str
            Net name of the voids to be checked. Default is ``None``.
        layer_name : str
            Layer name of the voids to be checked. Default is ``None``.

        Returns
        -------
        List[:class:`PadstackInstance <pyedb.grpc.database.primitive.padstack_instance.PadstackInstance>`]
            List of the voids that include this padstack instance.
        """
        x_pos = Value(self.position[0])
        y_pos = Value(self.position[1])
        point_data = GrpcPointData([x_pos, y_pos])

        voids = []
        for prim in self._pedb.modeler.get_primitives(net_name, layer_name, is_void=True):
            if prim.polygon_data.point_in_polygon(point_data):
                voids.append(prim)
        return voids

    @property
    def pingroups(self):
        """Pin groups that the pin belongs to.

        Returns
        -------
        List[:class:`PinGroup <ansys.edb.core.hierarchy.pin_group>`]
            List of pin groups that the pin belongs to.
        """
        return self.core.pin_groups

    @property
    def placement_layer(self):
        """Placement layer name.

        Returns
        -------
        str
            Name of the placement layer.
        """
        return self.component.placement_layer

    @property
    def layer(self):
        """Placement layer object.

        Returns
        -------
        :class:`pyedb.grpc.database.layers.stackup_layer.StackupLayer`
           Placement layer.
        """
        return self.component.layer

    @property
    def lower_elevation(self) -> float:
        """Lower elevation of the placement layer.

        Returns
        -------
        float
            Lower elavation of the placement layer.
        """
        return self._pedb.stackup.layers[self.component.placement_layer].lower_elevation

    @property
    def upper_elevation(self) -> float:
        """Upper elevation of the placement layer.

        Returns
        -------
        float
           Upper elevation of the placement layer.
        """
        return self._pedb.stackup.layers[self.component.placement_layer].upper_elevation

    @property
    def top_bottom_association(self) -> int:
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
        return self._pedb.stackup.layers[self.component.placement_layer].core.top_bottom_association.value

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
        bool, List, :class:`Primitive <pyedb.grpc.database.primitive.primitive.Primitive>`
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
        # TODO check if still used anf fix if yes.
        padstack_center = self.position
        rotation = self.rotation  # in radians
        # padstack = self._pedb.padstacks.definitions[self.padstack_def.name]
        try:
            padstack_pad = PadstackDef(self._pedb, self.padstack_def).pad_by_layer[layer_name]
        except KeyError:  # pragma: no cover
            try:
                padstack_pad = PadstackDef(self._pedb, self.padstack_def).pad_by_layer[
                    PadstackDef(self._pedb, self.padstack_def).start_layer
                ]
            except KeyError:  # pragma: no cover
                return False

        try:
            pad_shape = padstack_pad.geometry_type
            params = padstack_pad.parameters_values
            polygon_data = padstack_pad.polygon_data
        except:
            self._pedb.logger.warning(f"No pad defined on padstack definition {self.padstack_def.name}")
            return False

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
        elif pad_shape == 7 and polygon_data is not None:
            # Polygon
            points = []
            i = 0
            while i < len(polygon_data.points):
                point = polygon_data.points[i]
                i += 1
                if point.is_arc:
                    continue
                else:
                    points.append([Value(point.x), Value(point.y)])
            xpoly, ypoly = zip(*points)
            polygon = [list(xpoly), list(ypoly)]
            rectangles = GeometryOperators.find_largest_rectangle_inside_polygon(
                polygon, partition_max_order=partition_max_order
            )
            rect = rectangles[0]
            for i in range(4):
                rect[i] = _translate(_rotate(rect[i]))

        # if rect is None or len(rect) != 4:
        #     return False
        rect = [GrpcPointData(pt) for pt in rect]
        path = GrpcPolygonData(rect)
        new_rect = []
        for point in path.points:
            if self.component:
                p_transf = self.component.transform.transform_point(point)
                new_rect.append([Value(p_transf.x), Value(p_transf.y)])
        if return_points:
            return new_rect
        else:
            created_polygon = self._pedb.modeler.create_polygon(path, layer_name)
            return created_polygon

    def get_reference_pins(
        self, reference_net="GND", search_radius=5e-3, max_limit=0, component_only=True
    ) -> list[any]:
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
        List[:class:`PadstackInstance <pyedb.grpc.database.primitive.padstack_instance.PadstackInstance>`]

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

    def get_connected_objects(self):
        """Get connected objects.

        Returns
        -------
        List[:class:`LayoutObjInstance <ansys.edb.core.layout_instance.layout_obj_instance.LayoutObjInstance>`]
        """
        return self._pedb.get_connected_objects(self.object_instance)
