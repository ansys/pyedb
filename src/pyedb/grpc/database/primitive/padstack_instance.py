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
from __future__ import annotations

import math
import re
from typing import Literal, Union, overload
import warnings

from ansys.edb.core.database import ProductIdType as CoreProductIdType
from ansys.edb.core.geometry.point_data import PointData as CorePointData
from ansys.edb.core.geometry.polygon_data import PolygonData as CorePolygonData
from ansys.edb.core.hierarchy.pin_group import PinGroup as CorePinGroup
from ansys.edb.core.hierarchy.structure3d import MeshClosure as CoreMeshClosure, Structure3D as CoreStructure3D
from ansys.edb.core.primitive.padstack_instance import (
    PadstackInstance as CorePadstackInstance,
)
from ansys.edb.core.terminal.pin_group_terminal import (
    PinGroupTerminal as CorePinGroupTerminal,
)

from pyedb.generic.general_methods import generate_unique_name
from pyedb.generic.geometry_operators import GeometryOperators
from pyedb.grpc.database.definition.padstack_def import PadstackDef
from pyedb.grpc.database.inner import conn_obj
from pyedb.grpc.database.layers.stackup_layer import StackupLayer
from pyedb.grpc.database.modeler import Circle
from pyedb.grpc.database.net.net import Net
from pyedb.grpc.database.terminal.padstack_instance_terminal import (
    PadstackInstanceTerminal,
)
from pyedb.grpc.database.utility.layer_map import LayerMap
from pyedb.grpc.database.utility.value import Value
from pyedb.misc.decorators import deprecated


class PadstackInstance(conn_obj.ConnObj):
    """Manages EDB functionalities for a padstack.

    Parameters
    ----------
    :class:`PadstackInstance <pyedb.grpc.dataybase.primitive.PadstackInstance>`
        PadstackInstance object.

    Examples
    --------
    >>> from pyedb import Edb
    >>> edb = Edb("myedb", version="2026.1")
    >>> edb_padstack_instance = edb.padstacks.instances[0]
    """

    def __init__(self, pedb, core):
        self.core = core
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
        top_layer: str | StackupLayer,
        bottom_layer: str | StackupLayer,
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
        top_layer : str, :class:`StackupLayer <pyedb.grpc.database.layers.stackup_layer.StackupLayer>`
            Top layer.
        bottom_layer : str, :class:`StackupLayer <pyedb.grpc.database.layers.stackup_layer.StackupLayer>`
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
            padstack_def = padstack_definition.core
            padstack_definition = padstack_definition.name

        elif padstack_definition not in layout._pedb.padstacks.definitions:
            raise Exception(f"Padstack definition {padstack_definition} not found in layout.")
        else:
            padstack_def = layout._pedb.padstacks.definitions[padstack_definition].core

        if not name:
            name = generate_unique_name(padstack_definition)
        layer_map = LayerMap.create(layer_map)

        if isinstance(top_layer, StackupLayer):
            top_layer = top_layer.core
        else:
            top_layer = layout._pedb.stackup.layers[top_layer].core
        if isinstance(bottom_layer, StackupLayer):
            bottom_layer = bottom_layer.core
        else:
            bottom_layer = layout._pedb.stackup.layers[bottom_layer].core
        inst = CorePadstackInstance.create(
            layout=layout.core,
            net=net.core,
            padstack_def=padstack_def,
            position_x=layout._pedb._value_setter(position_x),
            position_y=layout._pedb._value_setter(position_y),
            rotation=layout._pedb._value_setter(rotation),
            top_layer=top_layer,
            bottom_layer=bottom_layer,
            name=name,
            solder_ball_layer=solder_ball_layer.core if solder_ball_layer else None,
            layer_map=layer_map.core,
        )
        return cls(layout._pedb, inst)

    @property
    def layer_map(self):
        return self.core.layer_map

    @layer_map.setter
    def layer_map(self, layer_map):
        self.core.layer_map = layer_map

    @property
    def solderball_layer(self):
        return self.core.solderball_layer

    @solderball_layer.setter
    def solderball_layer(self, solderball_layer):
        self.core.solderball_layer = solderball_layer

    def get_hole_overrides(self):
        return self.core.get_hole_overrides()

    def set_hole_overrides(self, enabled, diameter):
        if isinstance(diameter, (float, int)):
            diameter = self._pedb._value_setter(diameter)
        self.core.set_hole_overrides(enabled, Value(diameter))

    @property
    def backdrill_parameters(self):
        data = {}
        drill_to_layer, offset, diameter = self.get_back_drill_by_layer(True)

        if drill_to_layer:
            data["from_bottom"] = {
                "drill_to_layer": drill_to_layer,
                "diameter": str(diameter),
                "stub_length": str(offset),
            }
        drill_to_layer, offset, diameter = self.get_back_drill_by_layer(False)

        if drill_to_layer:
            data["from_top"] = {
                "drill_to_layer": drill_to_layer,
                "diameter": str(diameter),
                "stub_length": str(offset),
            }
        return data

    @backdrill_parameters.setter
    def backdrill_parameters(self, params):
        from_bottom = params.get("from_bottom")
        if from_bottom:
            if from_bottom.get("drill_to_layer"):
                self.set_back_drill_by_layer(
                    drill_to_layer=from_bottom.get("drill_to_layer"),
                    offset=self._pedb._value_setter(from_bottom.get("stub_length", 0)),
                    diameter=self._pedb._value_setter(from_bottom.get("diameter", 0)),
                    from_bottom=True,
                )
            else:
                self.set_back_drill_by_depth(
                    self._pedb._value_setter(from_bottom.get("stub_length", 0)),
                    self._pedb._value_setter(from_bottom.get("diameter", 0)),
                    from_bottom=True,
                )
        from_bottom = params.get("from_top")
        if from_bottom:
            if from_bottom.get("drill_to_layer"):
                self.set_back_drill_by_layer(
                    drill_to_layer=from_bottom.get("drill_to_layer"),
                    offset=self._pedb._value_setter(from_bottom.get("stub_length", 0)),
                    diameter=self._pedb._value_setter(from_bottom.get("diameter", 0)),
                    from_bottom=False,
                )
            else:
                self.set_back_drill_by_depth(
                    self._pedb._value_setter(from_bottom.get("stub_length", 0)),
                    self._pedb._value_setter(from_bottom.get("diameter", 0)),
                    from_bottom=False,
                )

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
        side_value = self.core.get_product_property(CoreProductIdType.HFSS_3D_LAYOUT, 21)
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
            self.core.set_product_property(CoreProductIdType.HFSS_3D_LAYOUT, 21, prop_string)
        else:
            raise ValueError("Number of sides must be an integer between 3 and 64")

    def delete(self):
        """Delete the padstack instance."""
        self.core.delete()

    @deprecated("use set_back_drill_by_layer or set_back_drill_by_depth methods instead")
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
        if isinstance(drill_depth, str):
            if drill_depth in self._pedb.stackup.layers:
                return self.set_back_drill_by_layer(
                    drill_to_layer=drill_depth,
                    offset=self._pedb._value_setter(offset),
                    diameter=self._pedb._value_setter(drill_diameter),
                    from_bottom=False,
                )
            else:
                return self.set_back_drill_by_depth(
                    self._pedb._value_setter(drill_depth), self._pedb._value_setter(drill_diameter), from_bottom=False
                )

    @deprecated("use set_back_drill_by_layer or set_back_drill_by_depth methods instead")
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
        if isinstance(drill_depth, str):
            if drill_depth in self._pedb.stackup.layers:
                return self.set_back_drill_by_layer(
                    drill_to_layer=self._pedb.stackup.layers[drill_depth],
                    offset=self._pedb._value_setter(offset),
                    diameter=self._pedb._value_setter(drill_diameter),
                    from_bottom=True,
                )
            else:
                return self.set_back_drill_by_depth(
                    self._pedb._value_setter(drill_depth), self._pedb._value_setter(drill_diameter), from_bottom=True
                )

    def create_terminal(self, name=None) -> PadstackInstanceTerminal:
        """Create a padstack instance terminal.

        Returns
        -------
        :class:`PadstackInstanceTerminal <pyedb.grpc.database.terminal.padstack_instance_terminal.
        PadstackInstanceTerminal>`
            PadstackInstanceTerminal object.

        """
        existing_terminal = self.terminal
        if existing_terminal is not None:
            self._pedb.logger.warning(f"Terminal already exists on padstack {self.name}.")
            return existing_terminal

        if not name:
            name = f"{self.name}_{self.id}"
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
        if not name:
            name = f"Port_{self.component.name}_{self.net.name}_{self.name}"
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
                pg = CorePinGroup.create(
                    self.core.layout, name=f"pingroup_{self.name}_ref", padstack_instances=reference
                )
                negative_terminal = CorePinGroupTerminal.create(
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
    def bounding_box(self) -> list[float]:
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
        int_val = 1 if polygon_data.is_inside(CorePointData(self.position)) else 0
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
                int_val = polygon_data.intersection_type(CorePolygonData(inst_bbox)).value
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
        list[float, float]
            List of ``[x, y]`` coordinates for the padstack instance position.
        """
        position = self.core.get_position_and_rotation()
        if self.component:
            point = CorePointData(position[:2])
            out2 = self.component.core.transform.transform_point(point)
            if hasattr(out2, "x"):
                self._position = [Value(out2.x), Value(out2.y)]
            else:
                self._position = [Value(out2[0]), Value(out2[1])]
        else:
            self._position = [Value(pt) for pt in position[:2]]
        return self._position

    @position.setter
    def position(self, value):
        pos = []
        for v in value:
            if isinstance(v, (float, int, str)):
                pos.append(self._pedb._value_setter(v))
            else:
                pos.append(v)
        point_data = CorePointData(pos[0], pos[1])
        self.core.set_position_and_rotation(
            x=point_data.x, y=point_data.y, rotation=self._pedb._value_setter(self.rotation)
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

    @rotation.setter
    def rotation(self, value):
        pos = []
        if isinstance(value, (float, int, str)):
            pos.append(self._pedb._value_setter(value, self._pedb.active_cell))
        else:
            pos.append(value)
        pos = self.position
        point_data = CorePointData(pos[0], pos[1])
        self.core.set_position_and_rotation(
            x=point_data.x,
            y=point_data.y,
            rotation=self._pedb._value_setter(
                self.rotation,
            ),
        )

    @property
    def position_and_rotation(self) -> list[float]:
        """Padstack instance position.

        Returns
        -------
        list
            List of ``[x, y,r]`` coordinates for the padstack instance position and rotation.
        """
        position = self.core.get_position_and_rotation()
        if self.component:
            point = CorePointData(position[:2])
            out2 = self.component.core.transform.transform_point(point)
            _position_and_rotation = [out2.x.value, out2.y.value]
            _position_and_rotation.append(Value(position[-1]).value)
        else:
            _position_and_rotation = [Value(pt).value for pt in position]
        return _position_and_rotation

    @position_and_rotation.setter
    def position_and_rotation(self, value):
        pos = []
        for v in value:
            if isinstance(v, (float, int, str)):
                pos.append(self._pedb._value_setter(v))
            else:
                pos.append(v)
        point_data = CorePointData(pos[0], pos[1])
        self.core.set_position_and_rotation(x=point_data.x, y=point_data.y, rotation=self._pedb._value_setter(pos[2]))

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
        self.core.set_product_property(CoreProductIdType.DESIGNER, 11, value)

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
                diameter=self._pedb._value_setter(value),
                from_bottom=True,
            )
        elif self.backdrill_top:
            parameters = self.get_back_drill_by_layer(False)
            self.set_back_drill_by_layer(
                drill_to_layer=parameters[0],
                offset=parameters[1],
                diameter=self._pedb._value_setter(value),
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
                offset=self._pedb._value_setter(value),
                diameter=parameters[2],
                from_bottom=True,
            )
        elif self.backdrill_top:
            parameters = self.get_back_drill_by_layer(False)
            self.set_back_drill_by_layer(
                drill_to_layer=parameters[0],
                offset=self._pedb._value_setter(value),
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

        name = self.core.get_product_property(CoreProductIdType.DESIGNER, 11)
        return str(name).strip("'")

    @aedt_name.setter
    def aedt_name(self, value):
        self.core.set_product_property(CoreProductIdType.DESIGNER, 11, value)

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
            center_x=self._pedb._value_setter(self.position[0]),
            center_y=self._pedb._value_setter(self.position[1]),
            radius=self._pedb._value_setter(rad_u),
        )
        cloned_circle2 = Circle(self._pedb).create(
            layout=layout,
            layer=self.stop_layer,
            net=self.net,
            center_x=self._pedb._value_setter(self.position[0]),
            center_y=self._pedb._value_setter(self.position[1]),
            radius=self._pedb._value_setter(rad_l),
        )

        s3d = CoreStructure3D.create(
            layout.core, generate_unique_name("via3d_" + self.aedt_name.replace("via_", ""), n=3)
        )
        s3d.add_member(cloned_circle.core)
        s3d.add_member(cloned_circle2.core)
        s3d.set_material(self.definition.material)
        s3d.mesh_closure = CoreMeshClosure.ENDS_CLOSED
        hole_override_enabled = True
        hole_override_diam = 0
        self.core.set_hole_overrides(hole_override_enabled, self._pedb._value_setter(hole_override_diam))

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

    @overload
    def get_back_drill_by_depth(
        self, from_bottom: bool, include_fill_material: Literal[False] = False
    ) -> tuple[Value, Value]: ...

    @overload
    def get_back_drill_by_depth(
        self, from_bottom: bool, include_fill_material: Literal[True]
    ) -> tuple[Value, Value, str]: ...

    def get_back_drill_by_depth(
        self, from_bottom: bool, include_fill_material: bool = False
    ) -> tuple[float | Value, float | Value] | tuple[float | Value, float | Value, str]:
        """Get the back drill type by depth.

        Parameters
        ----------
        from_bottom : bool
            Whether to get the back drill type from the bottom.
        include_fill_material : bool, optional
            Input flag to obtain fill material as well as other parameters.
            If false, the return tuple does not include fill material and is backward compatible with previous versions.
        Returns
        -------
        tuple of (.Value, .Value, str)
            Tuple containing:

            - **drill_depth** : Drilling depth, may not align with layer.
            - **diameter** : Drilling diameter.
            - **fill_material** : Fill material name (empty string if no fill),
              only included when ``include_fill_material`` is True.

        """
        if float(self._pedb.version) < 2027.1 and include_fill_material:
            warnings.warn(
                "Backdrill fill material is not supported by AEDT 2026 R1 and below. The parameter will be ignored.",
                UserWarning,
                stacklevel=2,
            )

        if float(self._pedb.version) < 2027.1:
            drill_depth, drill_diameter = self.core.get_back_drill_by_depth(from_bottom)
            return Value(drill_depth), Value(drill_diameter)
        else:
            params = self.core.get_back_drill_by_depth(from_bottom, include_fill_material)
            if include_fill_material:
                drill_depth, drill_diameter, fill_material = params
                return Value(drill_depth), Value(drill_diameter), fill_material
            else:
                drill_depth, drill_diameter = params
                return Value(drill_depth), Value(drill_diameter)

    def set_back_drill_by_depth(self, drill_depth, diameter, from_bottom=True, fill_material=""):
        """Set back drill by depth.

        Parameters
        ----------
        drill_depth : str, float
            drill depth value
        diameter : str, float
            drill diameter
        from_bottom : bool, optional
            Default value is `True`.
        fill_material : str, optional
        """
        if float(self._pedb.version) < 2027.1 and fill_material:
            warnings.warn(
                "Backdrill fill material is not supported by AEDT 2025.2 and below. The parameter will be ignored.",
                UserWarning,
                stacklevel=2,
            )

        if float(self._pedb.version) < 2027.1:
            self.core.set_back_drill_by_depth(
                drill_depth=self._pedb._value_setter(drill_depth),
                diameter=self._pedb._value_setter(diameter),
                from_bottom=from_bottom,
            )
        else:
            self.core.set_back_drill_by_depth(
                drill_depth=self._pedb._value_setter(drill_depth),
                diameter=self._pedb._value_setter(diameter),
                from_bottom=from_bottom,
                fill_material=fill_material,
            )

    @overload
    def get_back_drill_by_layer(
        self, from_bottom: bool, include_fill_material: Literal[False] = False
    ) -> tuple[str, Value, Value]: ...

    @overload
    def get_back_drill_by_layer(
        self, from_bottom: bool, include_fill_material: Literal[True]
    ) -> tuple[str, Value, Value, str]: ...

    def get_back_drill_by_layer(
        self, from_bottom: bool, include_fill_material: bool = False
    ) -> tuple[str, float | Value, float | Value] | tuple[str, float | Value, float | Value, str]:
        """Get the back drill type by the layer.

        Parameters
        ----------
        from_bottom : bool
            Whether to get the back drill type from the bottom.
        include_fill_material : bool, optional
            Input flag to obtain fill material as well as other parameters.
            If false, the return tuple does not include fill material and is backward compatible with previous versions.
        Returns
        -------
        tuple of (.Layer, .Value, .Value, str)
            Returns a tuple in this format:

            **(drill_to_layer, offset, diameter, fill_material)**

            - **drill_to_layer** : Layer drills to. If drill from top, drill stops at the upper elevation of the layer.
                                   If from bottom, drill stops at the lower elevation of the layer.
            - **offset** : Layer offset (or depth if layer is empty).
            - **diameter** : Drilling diameter.
            - **fill_material** : Fill material name (empty string if no fill).
                                  Returned only when include_fill_material is true.

        """
        if float(self._pedb.version) < 2027.1 and include_fill_material:
            warnings.warn(
                "Backdrill fill material is not supported by AEDT 2026 R1 and below. The parameter will be ignored.",
                UserWarning,
                stacklevel=2,
            )
        if float(self._pedb.version) < 2027.1:
            if self.backdrill_type == "no_drill":
                return "", Value(0), Value(0)
            else:
                drill_to_layer, offset, diameter = self.core.get_back_drill_by_layer(from_bottom)
                return drill_to_layer.name, Value(offset), Value(diameter)
        else:
            # Todo include_fill_material is not merged in core yet.
            # params = self.core.get_back_drill_by_layer(from_bottom, include_fill_material)
            params = self.core.get_back_drill_by_layer(from_bottom, include_fill_material)
            if include_fill_material:
                drill_to_layer, offset, diameter, fill_material = params
                return drill_to_layer.name, Value(offset), Value(diameter), fill_material
            else:
                drill_to_layer, offset, diameter = params
                return drill_to_layer.name, Value(offset), Value(diameter)

    def set_back_drill_by_layer(self, drill_to_layer, diameter, offset, from_bottom=True, fill_material=""):
        """Set back drill layer.

        Parameters
        ----------
        drill_to_layer : str
            Layer to drill to.
        offset : str, float
            Offset value
        diameter : str, float
            Drill diameter
        from_bottom : bool, optional
            Default value is `True`
        fill_material : str, optional
            Fill material name
        """
        if float(self._pedb.version) < 2027.1 and fill_material:
            warnings.warn(
                "Backdrill fill material is not supported by AEDT 2025.2 and below. The parameter will be ignored.",
                UserWarning,
                stacklevel=2,
            )

        drill_to_layer = (
            self._pedb.stackup.layers[drill_to_layer] if isinstance(drill_to_layer, str) else drill_to_layer
        )
        if float(self._pedb.version) < 2027.1:
            self.core.set_back_drill_by_layer(
                drill_to_layer=drill_to_layer.core,
                offset=self._pedb._value_setter(offset),
                diameter=self._pedb._value_setter(diameter),
                from_bottom=from_bottom,
            )
        else:
            self.core.set_back_drill_by_layer(
                drill_to_layer=drill_to_layer.core,
                offset=self._pedb._value_setter(offset),
                diameter=self._pedb._value_setter(diameter),
                from_bottom=from_bottom,
                fill_material=fill_material,
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
        x_pos = self._pedb._value_setter(self.position[0])
        y_pos = self._pedb._value_setter(self.position[1])
        point_data = CorePointData([x_pos, y_pos])

        voids = []
        prims = [i for i in self._pedb.layout.find_primitive(net_name=net_name, layer_name=layer_name) if i.is_void]
        for prim in prims:
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
                    points.append([self._pedb._value_setter(point.x), self._pedb._value_setter(point.y)])
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
        rect = [CorePointData(pt) for pt in rect]
        path = CorePolygonData(rect)
        new_rect = []
        for point in path.points:
            if self.component:
                p_transf = self.component.transform.transform_point(point)
                new_rect.append([p_transf.x, p_transf.y])
        if return_points:
            return new_rect
        else:
            created_polygon = self._pedb.modeler.create_polygon(path, layer_name)
            return created_polygon

    def get_reference_pins(
        self, reference_net="GND", search_radius=5e-3, max_limit=0, component_only=True, pinlist_position=None
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
            pinlist_position=pinlist_position,
        )

    def get_connected_objects(self):
        """Get connected objects.

        Returns
        -------
        List[:class:`LayoutObjInstance <ansys.edb.core.layout_instance.layout_obj_instance.LayoutObjInstance>`]
        """
        return self._pedb.get_connected_objects(self.object_instance)

    def set_dcir_equipotential_advanced(self, contact_radius=None, layer_name=None):
        """Set DCIR equipotential region on the padstack instance. This method allows to set equipotential region on
        specified layer and specify contact circle size. If contact_radius is not specified, the method will use the
        pad size. If layer_name is not specified, the method will use the start layer of the padstack definition.

        Parameters
        ----------
        contact_radius : float, optional
            Radius of the contact circle. The default is ``None```, in which case the
            method will use the pad size.
        layer_name : str, optional
            Layer name to set the equipotential region. The default is ``None``, in which case the method will use the
            start layer of the padstack definition.
        """
        layer_name = layer_name if layer_name else self.start_layer
        pad = self.definition.pad_by_layer[layer_name]

        pos_x, pos_y = self.position

        if contact_radius is not None:
            prim = self._pedb.modeler.create_circle(pad.layer_name, pos_x, pos_y, contact_radius, self.net_name)
            prim.dcir_equipotential_region = True
        elif pad.shape.lower() == "circle":
            ra = self._pedb.value(pad.parameters_values[0] / 2)
            pos = self.position
            prim = self._pedb.modeler.create_circle(pad.layer_name, pos[0], pos[1], ra, self.net_name)
        elif pad.shape.lower() == "rectangle":
            width, height = pad.parameters_values
            prim = self._pedb.modeler.create_rectangle(
                pad.layer_name,
                self.net_name,
                width=width,
                height=height,
                representation_type="CenterWidthHeight",
                center_point=self.position,
                rotation=self.component.rotation,
            )
        elif pad.shape.lower() == "oval":
            width, height, _ = pad.parameters_values
            prim = self._pedb.modeler.create_circle(
                pad.layer_name, self.position[0], self.position[1], height / 2, self.net_name
            )
        elif pad.polygon_data:
            prim = self._pedb.modeler.create_polygon(
                pad.polygon_data._edb_object, self.start_layer, net_name=self.net_name
            )
            prim.move(self.position)
        else:
            raise AttributeError(f"Unsupported pad shape {pad.shape} for DCIR equipotential region.")

        prim.dcir_equipotential_region = True
        return prim
