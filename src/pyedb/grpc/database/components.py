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

"""This module contains the `Components` class."""

import codecs
import json
import math
import os
import re
from typing import Any, Dict, List, Optional, Tuple, Union
import warnings

from ansys.edb.core.definition.die_property import DieOrientation as GrpDieOrientation, DieType as GrpcDieType
from ansys.edb.core.definition.solder_ball_property import (
    SolderballShape as GrpcSolderballShape,
)
from ansys.edb.core.hierarchy.component_group import ComponentType as GrpcComponentType
from ansys.edb.core.hierarchy.spice_model import SPICEModel as GrpcSPICEModel
from ansys.edb.core.utility.rlc import Rlc as GrpcRlc

from pyedb.component_libraries.ansys_components import (
    ComponentLib,
    ComponentPart,
    Series,
)
from pyedb.generic.general_methods import (
    generate_unique_name,
    get_filename_without_extension,
)
from pyedb.grpc.database.definition.component_def import ComponentDef
from pyedb.grpc.database.definition.component_pin import ComponentPin
from pyedb.grpc.database.hierarchy.component import Component
from pyedb.grpc.database.hierarchy.pin_pair_model import PinPairModel
from pyedb.grpc.database.hierarchy.pingroup import PinGroup
from pyedb.grpc.database.padstacks import Padstacks
from pyedb.grpc.database.utility.sources import SourceType
from pyedb.grpc.database.utility.value import Value
from pyedb.misc.decorators import deprecate_argument_name
from pyedb.modeler.geometry_operators import GeometryOperators


def resistor_value_parser(r_value) -> float:
    """Convert a resistor value to float.

    Parameters
    ----------
    r_value : float or str
        Resistor value to convert.

    Returns
    -------
    float
        Converted resistor value.
    """
    if isinstance(r_value, str):
        r_value = r_value.replace(" ", "")
        r_value = r_value.replace("meg", "m")
        r_value = r_value.replace("Ohm", "")
        r_value = r_value.replace("ohm", "")
        r_value = r_value.replace("k", "e3")
        r_value = r_value.replace("m", "e-3")
        r_value = r_value.replace("M", "e6")
    r_value = float(r_value)
    return r_value


class Components(object):
    """Manages EDB components and related methods accessible from `Edb.components`.

    Parameters
    ----------
    p_edb : :class:`pyedb.grpc.edb.Edb`
        EDB object.

    Examples
    --------
    >>> from pyedb import Edb
    >>> edbapp = Edb("myaedbfolder")
    >>> edbapp.components
    """

    def __getitem__(self, name: str) -> Optional[Union[Component, ComponentDef]]:
        """Get a component or component definition by name.

        Parameters
        ----------
        name : str
            Name of the component or definition.

        Returns
        -------
        :class:`pyedb.grpc.database.hierarchy.component.Component` or
        :class:`pyedb.grpc.database.definition.component_def.ComponentDef` or None
            Component instance if found, component definition if found by name, otherwise None.

        Examples
        --------
        >>> component = edbapp.components["R1"]
        """
        if name in self.instances:
            return self.instances[name]
        elif name in self.definitions:
            return self.definitions[name]
        self._pedb.logger.error("Component or definition not found.")
        return

    def __init__(self, p_edb: Any) -> None:
        self._pedb = p_edb
        self.refresh_components()
        self._pins = {}
        self._comps_by_part = {}
        self._padstack = Padstacks(self._pedb)

    @property
    def _logger(self) -> Any:
        """Logger instance for the component manager.

        Returns
        -------
        :class:`logging.Logger`
            Logger instance.
        """
        return self._pedb.logger

    @property
    def _active_layout(self):
        """Active layout of the EDB database.

        Returns
        -------
        :class:`ansys.edb.core.layout.Layout`
            Active layout object.
        """
        return self._pedb.active_layout

    @property
    def _layout(self):
        """Layout of the EDB database.

        Returns
        -------
        :class:`ansys.edb.core.layout.Layout`
            Layout object.
        """
        return self._pedb.layout

    @property
    def _cell(self):
        """Cell of the EDB database.

        Returns
        -------
        :class:`ansys.edb.core.layout.Cell`
            Cell object.
        """
        return self._pedb.cell

    @property
    def _db(self):
        """Active database.

        Returns
        -------
        :class:`ansys.edb.core.database.Database`
            Active database object.
        """
        return self._pedb.active_db

    @property
    def instances(self) -> Dict[str, Component]:
        """Dictionary of all component instances in the layout.

        Returns
        -------
        dict[str, :class:`pyedb.grpc.database.hierarchy.component.Component`]
            Dictionary of component instances keyed by name.

        Examples
        --------
        >>> edbapp.components.instances
        """
        return self._cmp

    @property
    def definitions(self) -> Dict[str, ComponentDef]:
        """Dictionary of all component definitions.

        Returns
        -------
        dict[str, :class:`pyedb.grpc.database.definition.component_def.ComponentDef`]
            Dictionary of component definitions keyed by name.

        Examples
        --------
        >>> edbapp.components.definitions
        """
        return {l.name: ComponentDef(self._pedb, l) for l in self._pedb.component_defs}

    @property
    def nport_comp_definition(self) -> Dict[str, Component]:
        """Dictionary of N-port component definitions.

        Returns
        -------
        dict[str, :class:`pyedb.grpc.database.hierarchy.component.Component`]
            Dictionary of N-port component definitions keyed by name.
        """
        return {name: l for name, l in self.definitions.items() if l.reference_file}

    def import_definition(self, file_path) -> bool:
        """Import component definitions from a JSON file.

        Parameters
        ----------
        file_path : str
            Path to the JSON file.

        Returns
        -------
        bool
            True if successful, False otherwise.

        Examples
        --------
        >>> edbapp.components.import_definition("definitions.json")
        """
        with codecs.open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for part_name, p in data["Definitions"].items():
                model_type = p["Model_type"]
                if part_name not in self.definitions:
                    continue
                comp_definition = self.definitions[part_name]
                comp_definition.type = p["Component_type"]

                if model_type == "RLC":
                    comp_definition.assign_rlc_model(p["Res"], p["Ind"], p["Cap"], p["Is_parallel"])
                else:
                    model_name = p["Model_name"]
                    file_path = data[model_type][model_name]
                    if model_type == "SParameterModel":
                        if "Reference_net" in p:
                            reference_net = p["Reference_net"]
                        else:
                            reference_net = None
                        comp_definition.assign_s_param_model(file_path, model_name, reference_net)
                    elif model_type == "SPICEModel":
                        comp_definition.assign_spice_model(file_path, model_name)
                    else:
                        pass
        return True

    def export_definition(self, file_path) -> bool:
        """Export component definitions to a JSON file.

        Parameters
        ----------
        file_path : str
            Path to the output JSON file.

        Returns
        -------
        bool
            True if successful, False otherwise.

        Examples
        --------
        >>> edbapp.components.export_definition("exported_definitions.json")
        """
        data = {
            "SParameterModel": {},
            "SPICEModel": {},
            "Definitions": {},
        }
        for part_name, props in self.definitions.items():
            comp_list = list(props.components.values())
            if comp_list:
                data["Definitions"][part_name] = {}
                data["Definitions"][part_name]["Component_type"] = props.type
                comp = comp_list[0]
                data["Definitions"][part_name]["Model_type"] = comp.model_type
                if comp.model_type == "RLC":
                    rlc_values = [i if i else 0 for i in comp.rlc_values]
                    data["Definitions"][part_name]["Res"] = rlc_values[0]
                    data["Definitions"][part_name]["Ind"] = rlc_values[1]
                    data["Definitions"][part_name]["Cap"] = rlc_values[2]
                    data["Definitions"][part_name]["Is_parallel"] = True if comp.is_parallel_rlc else False
                else:
                    if comp.model_type == "SParameterModel":
                        model = comp.s_param_model
                        data["Definitions"][part_name]["Model_name"] = model.name
                        data["Definitions"][part_name]["Reference_net"] = model.reference_net
                        if not model.name in data["SParameterModel"]:
                            data["SParameterModel"][model.name] = model.file_path
                    elif comp.model_type == "SPICEModel":
                        model = comp.spice_model
                        data["Definitions"][part_name]["Model_name"] = model.name
                        if not model.name in data["SPICEModel"]:
                            data["SPICEModel"][model.name] = model.file_path
                    else:
                        model = comp.netlist_model
                        data["Definitions"][part_name]["Model_name"] = model.netlist

        with codecs.open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True

    def refresh_components(self) -> bool:
        """Refresh the component dictionary.

        Returns
        -------
        bool
            True if successful, False otherwise.

        Examples
        --------
        >>> edbapp.components.refresh_components()
        """
        self._logger.info("Refreshing the Components dictionary.")
        self._cmp = {}
        self._res = {}
        self._ind = {}
        self._cap = {}
        self._ics = {}
        self._ios = {}
        self._others = {}
        type_map = {
            "resistor": self._res,
            "capacitor": self._cap,
            "inductor": self._ind,
            "ic": self._ics,
            "io": self._ios,
            "other": self._others,
        }
        for i in self._pedb.layout.groups:
            self._cmp[i.name] = i
            try:
                target = type_map.get(i.component_type)
                if target is None:
                    self._logger.warning(
                        f"Unknown component type {i.name} found while refreshing components, will ignore"
                    )
                else:
                    target[i.name] = i
            except Exception:
                self._logger.warning(f"Assigning component {i.name} as default type other.")
                self._others[i.name] = i
        return True

    @property
    def resistors(self) -> Dict[str, Component]:
        """Dictionary of resistor components.

        Returns
        -------
        dict[str, :class:`pyedb.grpc.database.hierarchy.component.Component`]
            Dictionary of resistor components keyed by name.

        Examples
        --------
        >>> edbapp.components.resistors
        """
        return self._res

    @property
    def capacitors(self) -> Dict[str, Component]:
        """Dictionary of capacitor components.

        Returns
        -------
        dict[str, :class:`pyedb.grpc.database.hierarchy.component.Component`]
            Dictionary of capacitor components keyed by name.

        Examples
        --------
        >>> edbapp.components.capacitors
        """
        return self._cap

    @property
    def inductors(self) -> Dict[str, Component]:
        """Dictionary of inductor components.

        Returns
        -------
        dict[str, :class:`pyedb.grpc.database.hierarchy.component.Component`]
            Dictionary of inductor components keyed by name.

        Examples
        --------
        >>> edbapp.components.inductors
        """
        return self._ind

    @property
    def ICs(self) -> Dict[str, Component]:
        """Dictionary of integrated circuit components.

        Returns
        -------
        dict[str, :class:`pyedb.grpc.database.hierarchy.component.Component`]
            Dictionary of IC components keyed by name.

        Examples
        --------
        >>> edbapp.components.ICs
        """
        return self._ics

    @property
    def IOs(self) -> Dict[str, Component]:
        """Dictionary of I/O components.

        Returns
        -------
        dict[str, :class:`pyedb.grpc.database.hierarchy.component.Component`]
            Dictionary of I/O components keyed by name.

        Examples
        --------
        >>> edbapp.components.IOs
        """
        return self._ios

    @property
    def Others(self) -> Dict[str, Component]:
        """Dictionary of other components.

        Returns
        -------
        dict[str, :class:`pyedb.grpc.database.hierarchy.component.Component`]
            Dictionary of other components keyed by name.

        Examples
        --------
        >>> edbapp.components.Others
        """
        return self._others

    @property
    def components_by_partname(self) -> Dict[str, List[Component]]:
        """Dictionary of components grouped by part name.

        Returns
        -------
        dict[str, list[:class:`pyedb.grpc.database.hierarchy.component.Component`]]
            Dictionary of components lists keyed by part name.

        Examples
        --------
        >>> edbapp.components.components_by_partname
        """
        self._comps_by_part = {}
        for el, val in self.instances.items():
            if val.partname in self._comps_by_part.keys():
                self._comps_by_part[val.partname].append(val)
            else:
                self._comps_by_part[val.partname] = [val]
        return self._comps_by_part

    def get_component_by_name(self, name) -> Component:
        """Retrieve a component by name.

        Parameters
        ----------
        name : str
            Name of the component.

        Returns
        -------
        :class:`pyedb.grpc.database.hierarchy.component.Component`
            Component instance.

        Examples
        --------
        >>> comp = edbapp.components.get_component_by_name("R1")
        """
        return self.instances[name]

    @deprecate_argument_name({"pinName": "pin_name"})
    def get_pin_from_component(
        self,
        component: Union[str, Component],
        net_name: Optional[Union[str, List[str]]] = None,
        pin_name: Optional[str] = None,
    ) -> List[Any]:
        """Get pins from a component with optional filtering.

        Parameters
        ----------
        component : str or :class:`pyedb.grpc.database.hierarchy.component.Component`
            Component name or instance.
        net_name : str or list[str], optional
            Net name(s) to filter by.
        pin_name : str, optional
            Pin name to filter by.

        Returns
        -------
        list[:class:`pyedb.grpc.database.padstacks.PadstackInstance`]
            List of pin instances.

        Examples
        --------
        >>> pins = edbapp.components.get_pin_from_component("R1", net_name="GND")
        """
        if isinstance(component, Component):
            component = component.name
        pins = [pin for pin in list(self.instances[component].pins.values())]
        if net_name:
            if isinstance(net_name, str):
                net_name = [net_name]
            pins = [pin for pin in pins if pin.net_name in net_name]
        if pin_name:
            pins = [pin for pin in pins if pin.name == pin_name]
        return pins

    def get_components_from_nets(self, netlist=None) -> list[str]:
        """Get components connected to specified nets.

        Parameters
        ----------
        netlist : str or list[str], optional
            Net name(s) to filter by.

        Returns
        -------
        list[str]
            List of component names.

        Examples
        --------
        >>> comps = edbapp.components.get_components_from_nets(["GND", "VCC"])
        """
        cmp_list = []
        if isinstance(netlist, str):
            netlist = [netlist]
        components = list(self.instances.keys())
        for refdes in components:
            cmpnets = self._cmp[refdes].nets
            if set(cmpnets).intersection(set(netlist)):
                cmp_list.append(refdes)
        return cmp_list

    def _get_edb_pin_from_pin_name(self, cmp: Component, pin: str) -> Union[ComponentPin, bool]:
        """Get EDB pin from pin name.

        Parameters
        ----------
        cmp : :class:`pyedb.grpc.database.hierarchy.component.Component`
            Component instance.
        pin : str
            Pin name.

        Returns
        -------
        :class:`pyedb.grpc.database.definition.component_pin.ComponentPin` or bool
            Pin instance if found, False otherwise.
        """
        if not isinstance(cmp, Component):
            return False
        if not isinstance(pin, str):
            return False
        if pin in cmp.pins:
            return cmp.pins[pin]
        return False

    def get_component_placement_vector(
        self,
        mounted_component: Component,
        hosting_component: Component,
        mounted_component_pin1: str,
        mounted_component_pin2: str,
        hosting_component_pin1: str,
        hosting_component_pin2: str,
        flipped: bool = False,
    ) -> Tuple[bool, List[float], float, float]:
        """Get placement vector between two components.

        Parameters
        ----------
        mounted_component : :class:`pyedb.grpc.database.hierarchy.component.Component`
            Mounted component.
        hosting_component : :class:`pyedb.grpc.database.hierarchy.component.Component`
            Hosting component.
        mounted_component_pin1 : str
            Pin name on mounted component.
        mounted_component_pin2 : str
            Pin name on mounted component.
        hosting_component_pin1 : str
            Pin name on hosting component.
        hosting_component_pin2 : str
            Pin name on hosting component.
        flipped : bool, optional
            Whether the component is flipped.

        Returns
        -------
        tuple
            (success, vector, rotation, solder_ball_height)

        Examples
        --------
        >>> vec, rot, height = edbapp.components.get_component_placement_vector(...)
        """
        if not isinstance(mounted_component, Component):
            return False
        if not isinstance(hosting_component, Component):
            return False

        m_pin1_pos = [0.0, 0.0]
        m_pin2_pos = [0.0, 0.0]
        h_pin1_pos = [0.0, 0.0]
        h_pin2_pos = [0.0, 0.0]
        if mounted_component_pin1:
            m_pin1 = self._get_edb_pin_from_pin_name(mounted_component, mounted_component_pin1)
            m_pin1_pos = self.get_pin_position(m_pin1)
        if mounted_component_pin2:
            m_pin2 = self._get_edb_pin_from_pin_name(mounted_component, mounted_component_pin2)
            m_pin2_pos = self.get_pin_position(m_pin2)

        if hosting_component_pin1:
            h_pin1 = self._get_edb_pin_from_pin_name(hosting_component, hosting_component_pin1)
            h_pin1_pos = self.get_pin_position(h_pin1)

        if hosting_component_pin2:
            h_pin2 = self._get_edb_pin_from_pin_name(hosting_component, hosting_component_pin2)
            h_pin2_pos = self.get_pin_position(h_pin2)
        #
        vector = [h_pin1_pos[0] - m_pin1_pos[0], h_pin1_pos[1] - m_pin1_pos[1]]
        vector1 = GeometryOperators.v_points(m_pin1_pos, m_pin2_pos)
        vector2 = GeometryOperators.v_points(h_pin1_pos, h_pin2_pos)
        multiplier = 1
        if flipped:
            multiplier = -1
        vector1[1] = multiplier * vector1[1]

        rotation = GeometryOperators.v_angle_sign_2D(vector1, vector2, False)
        if rotation != 0.0:
            layinst = mounted_component.layout_instance
            cmpinst = layinst.GetLayoutObjInstance(mounted_component, None)
            center = cmpinst.center
            # center_double = [center.X.ToDouble(), center.Y.ToDouble()]
            vector_center = GeometryOperators.v_points(center, m_pin1_pos)
            x_v2 = vector_center[0] * math.cos(rotation) + multiplier * vector_center[1] * math.sin(rotation)
            y_v2 = -1 * vector_center[0] * math.sin(rotation) + multiplier * vector_center[1] * math.cos(rotation)
            new_vector = [x_v2 + center[0], y_v2 + center[1]]
            vector = [h_pin1_pos[0] - new_vector[0], h_pin1_pos[1] - new_vector[1]]

        if vector:
            solder_ball_height = self.get_solder_ball_height(mounted_component)
            return True, vector, rotation, solder_ball_height
        self._logger.warning("Failed to compute vector.")
        return False, [0, 0], 0, 0

    def get_solder_ball_height(self, cmp: Union[str, Component]) -> float:
        """Get solder ball height of a component.

        Parameters
        ----------
        cmp : str or :class:`pyedb.grpc.database.hierarchy.component.Component`
            Component name or instance.

        Returns
        -------
        float
            Solder ball height in meters.

        Examples
        --------
        >>> height = edbapp.components.get_solder_ball_height("U1")
        """
        if isinstance(cmp, str):
            cmp = self.get_component_by_name(cmp)
        return cmp.solder_ball_height

    def get_vendor_libraries(self) -> ComponentLib:
        """Get vendor component libraries.

        Returns
        -------
        :class:`pyedb.component_libraries.ansys_components.ComponentLib`
            Component library object.

        Examples
        --------
        >>> lib = edbapp.components.get_vendor_libraries()
        """
        comp_lib_path = os.path.join(self._pedb.base_path, "complib", "Locked")
        comp_types = ["Capacitors", "Inductors"]
        comp_lib = ComponentLib()
        comp_lib.path = comp_lib_path
        for cmp_type in comp_types:
            folder = os.path.join(comp_lib_path, cmp_type)
            vendors = {f.name: "" for f in os.scandir(folder) if f.is_dir()}
            for vendor in list(vendors.keys()):
                series = {f.name: Series() for f in os.scandir(os.path.join(folder, vendor)) if f.is_dir()}
                for serie_name, _ in series.items():
                    _serie = {}
                    index_file = os.path.join(folder, vendor, serie_name, "index.txt")
                    sbin_file = os.path.join(folder, vendor, serie_name, "sdata.bin")
                    if os.path.isfile(index_file):
                        with open(index_file, "r") as f:
                            for line in f.readlines():
                                part_name, index = line.split()
                                _serie[part_name] = ComponentPart(part_name, int(index), sbin_file)
                                _serie[part_name].type = cmp_type[:-1]
                            f.close()
                        series[serie_name] = _serie
                vendors[vendor] = series
            if cmp_type == "Capacitors":
                comp_lib.capacitors = vendors
            elif cmp_type == "Inductors":
                comp_lib.inductors = vendors
        return comp_lib

    def create_source_on_component(self, sources=None):  # pragma: no cover
        """Create sources on components.

        .. deprecated:: 0.28.0
            Use :func:`pyedb.grpc.core.excitations.create_source_on_component` instead.

        Parameters
        ----------
        sources : list, optional
            List of sources.

        Returns
        -------
        bool
            True if successful, False otherwise.
        """
        warnings.warn(
            "`create_source_on_component` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations.create_source_on_component` instead.",
            DeprecationWarning,
        )
        self._pedb.excitations.create_source_on_component(self, sources=sources)

    def create_port_on_pins(
        self,
        refdes,
        pins,
        reference_pins,
        impedance=50.0,
        port_name=None,
        pec_boundary=False,
        pingroup_on_single_pin=False,
    ):  # pragma: no cover
        """Create port on pins.

        .. deprecated:: 0.28.0
            Use :func:`pyedb.grpc.core.excitations.create_port_on_pins` instead.

        Parameters
        ----------
        refdes : str
            Reference designator.
        pins : list
            List of pins.
        reference_pins : list
            List of reference pins.
        impedance : float, optional
            Port impedance.
        port_name : str, optional
            Port name.
        pec_boundary : bool, optional
            Use PEC boundary.
        pingroup_on_single_pin : bool, optional
            Use pin group on single pin.

        Returns
        -------
        bool
            True if successful, False otherwise.
        """
        warnings.warn(
            "`create_port_on_pins` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations.create_port_on_pins` instead.",
            DeprecationWarning,
        )
        return self._pedb.source_excitation.create_port_on_pins(
            refdes,
            pins,
            reference_pins,
            impedance=impedance,
            port_name=port_name,
            pec_boundary=pec_boundary,
            pingroup_on_single_pin=pingroup_on_single_pin,
        )

    def create_port_on_component(
        self,
        component,
        net_list,
        port_type=SourceType.CoaxPort,
        do_pingroup=True,
        reference_net="gnd",
        port_name=None,
        solder_balls_height=None,
        solder_balls_size=None,
        solder_balls_mid_size=None,
        extend_reference_pins_outside_component=False,
    ):  # pragma: no cover
        """Create ports on a component.

        .. deprecated:: 0.28.0
            Use :func:`pyedb.grpc.core.excitations.create_port_on_component` instead.

        Parameters
        ----------
        component : str
            Component name.
        net_list : list
            List of nets.
        port_type : SourceType, optional
            Port type.
        do_pingroup : bool, optional
            Use pin groups.
        reference_net : str, optional
            Reference net.
        port_name : str, optional
            Port name.
        solder_balls_height : float, optional
            Solder ball height.
        solder_balls_size : float, optional
            Solder ball size.
        solder_balls_mid_size : float, optional
            Solder ball mid size.
        extend_reference_pins_outside_component : bool, optional
            Extend reference pins outside component.

        Returns
        -------
        bool
            True if successful, False otherwise.
        """
        warnings.warn(
            "`create_port_on_component` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations.create_port_on_component` instead.",
            DeprecationWarning,
        )
        return self._pedb.source_excitation.create_port_on_component(
            component,
            net_list,
            port_type=port_type,
            do_pingroup=do_pingroup,
            reference_net=reference_net,
            port_name=port_name,
            solder_balls_height=solder_balls_height,
            solder_balls_size=solder_balls_size,
            solder_balls_mid_size=solder_balls_mid_size,
            extend_reference_pins_outside_component=extend_reference_pins_outside_component,
        )

    def _create_terminal(self, pin, term_name=None):  # pragma: no cover
        """Create terminal on pin.

        .. deprecated:: 0.28.0
            Use :func:`pyedb.grpc.core.excitations._create_terminal` instead.

        Parameters
        ----------
        pin : :class:`pyedb.grpc.database.padstacks.PadstackInstance`
            Pin instance.
        term_name : str, optional
            Terminal name.

        Returns
        -------
        bool
            True if successful, False otherwise.
        """
        warnings.warn(
            "`_create_terminal` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations._create_terminal` instead.",
            DeprecationWarning,
        )
        self._pedb.excitations._create_terminal(pin, term_name=term_name)

    def _get_closest_pin_from(self, pin, ref_pinlist):
        """Get closest pin from a list of pins.

        Parameters
        ----------
        pin : :class:`pyedb.grpc.database.padstacks.PadstackInstance`
            Source pin.
        ref_pinlist : list[:class:`pyedb.grpc.database.padstacks.PadstackInstance`]
            List of reference pins.

        Returns
        -------
        :class:`pyedb.grpc.database.padstacks.PadstackInstance`
            Closest pin.
        """
        distance = 1e3
        pin_position = pin.position
        closest_pin = ref_pinlist[0]
        for ref_pin in ref_pinlist:
            temp_distance = pin_position.distance(ref_pin.position)
            if temp_distance < distance:
                distance = temp_distance
                closest_pin = ref_pin
        return closest_pin

    def _create_pin_group_terminal(
        self, pingroup, isref=False, term_name=None, term_type="circuit"
    ):  # pragma: no cover
        """Create pin group terminal.

        .. deprecated:: 0.28.0
            Use :func:`pyedb.grpc.core.excitations._create_pin_group_terminal` instead.

        Parameters
        ----------
        pingroup : :class:`pyedb.grpc.database.hierarchy.pingroup.PinGroup`
            Pin group.
        isref : bool, optional
            Is reference terminal.
        term_name : str, optional
            Terminal name.
        term_type : str, optional
            Terminal type.

        Returns
        -------
        bool
            True if successful, False otherwise.
        """
        warnings.warn(
            "`_create_pin_group_terminal` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations._create_pin_group_terminal` instead.",
            DeprecationWarning,
        )
        return self._pedb.source_excitation._create_pin_group_terminal(
            pingroup=pingroup, term_name=term_name, term_type=term_type, isref=isref
        )

    def _is_top_component(self, cmp) -> bool:
        """Check if component is on top layer.

        Parameters
        ----------
        cmp : :class:`pyedb.grpc.database.hierarchy.component.Component`
            Component instance.

        Returns
        -------
        bool
            True if on top layer, False otherwise.
        """
        top_layer = self._pedb.stackup.signal[0].name
        if cmp.placement_layer == top_layer:
            return True
        else:
            return False

    def _get_component_definition(self, name, pins) -> Union[ComponentDef, None]:
        """Get or create component definition.

        Parameters
        ----------
        name : str
            Definition name.
        pins : list
            List of pins.

        Returns
        -------
        :class:`pyedb.grpc.database.definition.component_def.ComponentDef` or None
            Component definition if successful, None otherwise.
        """
        component_definition = ComponentDef.find(self._pedb, name)
        if not component_definition:
            from ansys.edb.core.layout.cell import Cell as GrpcCell, CellType as GrpcCellType

            foot_print_cell = GrpcCell.create(self._pedb.active_db, GrpcCellType.FOOTPRINT_CELL, name)
            component_definition = ComponentDef.create(self._pedb, name, fp=foot_print_cell)
            if component_definition.core.is_null:
                self._logger.error(f"Failed to create component definition {name}")
                return None
            ind = 1
            for pin in pins:
                if not pin.name:
                    pin.name = str(ind)
                ind += 1
                component_definition_pin = ComponentPin.create(component_definition, pin.name)
                if component_definition_pin.core.is_null:
                    self._logger.error(f"Failed to create component definition pin {name}-{pin.name}")
                    return None
        return component_definition

    def create(
        self,
        pins: List[Any],
        component_name: Optional[str] = None,
        placement_layer: Optional[str] = None,
        component_part_name: Optional[str] = None,
        is_rlc: bool = False,
        r_value: Optional[float] = None,
        c_value: Optional[float] = None,
        l_value: Optional[float] = None,
        is_parallel: bool = False,
    ) -> Union[Component, bool]:
        """Create a new component.

        Parameters
        ----------
        pins : list[:class:`pyedb.grpc.database.padstacks.PadstackInstance`]
            List of pins.
        component_name : str, optional
            Component name.
        placement_layer : str, optional
            Placement layer name.
        component_part_name : str, optional
            Part name.
        is_rlc : bool, optional
            Whether the component is RLC.
        r_value : float, optional
            Resistance value.
        c_value : float, optional
            Capacitance value.
        l_value : float, optional
            Inductance value.
        is_parallel : bool, optional
            Whether RLC is parallel.

        Returns
        -------
        :class:`pyedb.grpc.database.hierarchy.component.Component` or bool
            New component instance if successful, False otherwise.

        Examples
        --------
        >>> new_comp = edbapp.components.create(pins, "R1")
        """
        from ansys.edb.core.hierarchy.component_group import (
            ComponentGroup as GrpcComponentGroup,
        )

        if not pins:
            raise ValueError("Pins must be a list of PadstackInstance objects.")

        if not component_name:
            component_name = generate_unique_name("Comp_")
        if component_part_name:
            compdef = self._get_component_definition(component_part_name, pins)
        else:
            compdef = self._get_component_definition(component_name, pins)
        if not compdef:
            return False
        new_cmp = GrpcComponentGroup.create(self._active_layout.core, component_name, compdef.name)
        if new_cmp.is_null:
            raise ValueError(f"Failed to create component {component_name}.")
        if hasattr(pins[0], "component") and pins[0].component:
            hosting_component_location = None
            if not pins[0].component.is_null:
                hosting_component_location = pins[0].component.core.transform
        else:
            hosting_component_location = None
        if not len(pins) == len(compdef.component_pins):
            self._pedb.logger.error(
                f"Number on pins {len(pins)} does not match component definition number "
                f"of pins {len(compdef.component_pins)}"
            )
            return False
        for padstack_instance, component_pin in zip(pins, compdef.component_pins):
            padstack_instance.is_layout_pin = True
            padstack_instance.name = component_pin.name
            new_cmp.add_member(padstack_instance.core)
        if not placement_layer:
            new_cmp_layer_name = pins[0].padstack_def.data.layer_names[0]
        else:
            new_cmp_layer_name = placement_layer
        if new_cmp_layer_name in self._pedb.stackup.signal_layers:
            new_cmp_placement_layer = self._pedb.stackup.signal_layers[new_cmp_layer_name]
            new_cmp.placement_layer = new_cmp_placement_layer.core
        if r_value:
            new_cmp.component_type = GrpcComponentType.RESISTOR
            is_rlc = True
        elif c_value:
            new_cmp.component_type = GrpcComponentType.CAPACITOR
            is_rlc = True
        elif l_value:
            new_cmp.component_type = GrpcComponentType.INDUCTOR
            is_rlc = True
        else:
            new_cmp.component_type = GrpcComponentType.OTHER
            is_rlc = False
        if is_rlc and len(pins) == 2:
            rlc = GrpcRlc()
            rlc.is_parallel = is_parallel
            if not r_value:
                rlc.r_enabled = False
            else:
                rlc.r_enabled = True
                rlc.r = Value(r_value)
            if l_value is None:
                rlc.l_enabled = False
            else:
                rlc.l_enabled = True
                rlc.l = Value(l_value)
            if c_value is None:
                rlc.c_enabled = False
            else:
                rlc.c_enabled = True
                rlc.c = Value(c_value)
            if rlc.r_enabled and not rlc.c_enabled and not rlc.l_enabled:
                new_cmp.component_type = GrpcComponentType.RESISTOR
            elif rlc.c_enabled and not rlc.r_enabled and not rlc.l_enabled:
                new_cmp.component_type = GrpcComponentType.CAPACITOR
            elif rlc.l_enabled and not rlc.r_enabled and not rlc.c_enabled:
                new_cmp.component_type = GrpcComponentType.INDUCTOR
            else:
                new_cmp.component_type = GrpcComponentType.RESISTOR
            pin_pair = (pins[0].name, pins[1].name)
            rlc_model = PinPairModel(self._pedb, new_cmp.component_property.model)
            rlc_model.set_rlc(pin_pair, rlc)
            component_property = new_cmp.component_property
            component_property.model = rlc_model
            new_cmp.component_property = component_property
        if hosting_component_location:
            new_cmp.transform = hosting_component_location
        new_edb_comp = Component(self._pedb, new_cmp)
        self._cmp[new_cmp.name] = new_edb_comp
        return new_edb_comp

    def create_component_from_pins(
        self, pins, component_name, placement_layer=None, component_part_name=None
    ) -> Union[Component, bool]:  # pragma: no cover
        """Create component from pins.

        .. deprecated:: 0.6.62
            Use :func:`create` instead.

        Parameters
        ----------
        pins : list
            List of pins.
        component_name : str
            Component name.
        placement_layer : str, optional
            Placement layer.
        component_part_name : str, optional
            Part name.

        Returns
        -------
        :class:`pyedb.grpc.database.hierarchy.component.Component` or bool
            Component instance if successful, False otherwise.
        """
        warnings.warn("`create_component_from_pins` is deprecated use `create` instead..", DeprecationWarning)
        return self.create(
            pins=pins,
            component_name=component_name,
            placement_layer=placement_layer,
            component_part_name=component_part_name,
            is_rlc=False,
        )

    def set_component_model(
        self,
        componentname: str,
        model_type: str = "Spice",
        modelpath: Optional[str] = None,
        modelname: Optional[str] = None,
    ) -> bool:
        """Set component model.

        Parameters
        ----------
        componentname : str
            Component name.
        model_type : str, optional
            Model type ("Spice" or "Touchstone").
        modelpath : str, optional
            Model file path.
        modelname : str, optional
            Model name.

        Returns
        -------
        bool
            True if successful, False otherwise.

        Examples
        --------
        >>> edbapp.components.set_component_model("U1", "Spice", "path/to/model.sp")
        """
        if not modelname:
            modelname = get_filename_without_extension(modelpath)
        if componentname not in self.instances:
            self._pedb.logger.error(f"Component {componentname} not found.")
            return False
        component = self.instances[componentname]
        pin_number = len(component.pins)
        if model_type == "Spice":
            with open(modelpath, "r") as f:
                for line in f:
                    if "subckt" in line.lower():
                        pin_names = [i.strip() for i in re.split(" |\t", line) if i]
                        pin_names.remove(pin_names[0])
                        pin_names.remove(pin_names[0])
                        break
            if len(pin_names) == pin_number:
                spice_mod = GrpcSPICEModel.create(name=modelname, path=modelpath, sub_circuit=f"{modelname}_sub")
                terminal = 1
                for pn in pin_names:
                    spice_mod.add_terminal(terminal=str(terminal), pin=pn)
                    terminal += 1
                component.component_property.model = spice_mod
            else:
                self._logger.error("Wrong number of Pins")
                return False

        elif model_type == "Touchstone":  # pragma: no cover
            n_port_model_name = modelname
            from ansys.edb.core.definition.component_model import (
                NPortComponentModel as GrpcNPortComponentModel,
            )
            from ansys.edb.core.hierarchy.sparameter_model import (
                SParameterModel as GrpcSParameterModel,
            )

            n_port_model = GrpcNPortComponentModel.find_by_name(component.component_def, n_port_model_name)
            if n_port_model.is_null:
                n_port_model = GrpcNPortComponentModel.create(n_port_model_name)
                n_port_model.reference_file = modelpath
                component.component_def.add_component_model(n_port_model)
            gndnets = list(filter(lambda x: "gnd" in x.lower(), component.nets))
            if len(gndnets) > 0:  # pragma: no cover
                net = gndnets[0]
            else:  # pragma: no cover
                net = component.nets[len(component.nets) - 1]
            s_parameter_mod = GrpcSParameterModel.create(name=n_port_model_name, ref_net=net)
            component.component_property.model = s_parameter_mod
        return True

    def create_pingroup_from_pins(self, pins: List[Any], group_name: Optional[str] = None) -> Union[PinGroup, bool]:
        """Create pin group from pins.

        Parameters
        ----------
        pins : list[:class:`pyedb.grpc.database.padstacks.PadstackInstance`]
            List of pins.
        group_name : str, optional
            Group name.

        Returns
        -------
        :class:`pyedb.grpc.database.hierarchy.pingroup.PinGroup` or bool
            Pin group instance if successful, False otherwise.

        Examples
        --------
        >>> pingroup = edbapp.components.create_pingroup_from_pins(pins, "GND_pins")
        """
        if len(pins) < 1:
            self._logger.error("No pins specified for pin group %s", group_name)
            return False
        if group_name is None:
            group_name = PinGroup.unique_name(self._active_layout, "pin_group")
        for pin in pins:
            pin.is_layout_pin = True
        forbiden_car = "-><"
        group_name = group_name.translate({ord(i): "_" for i in forbiden_car})
        for pgroup in list(self._pedb.active_layout.pin_groups):
            if pgroup.name == group_name:
                pin_group_exists = True
                if len(pgroup.pins) == len(pins):
                    pnames = [i.name for i in pins]
                    for p in pgroup.pins:
                        if p.name in pnames:
                            continue
                        else:
                            group_name = PinGroup.unique_name(self._active_layout, group_name)
                            pin_group_exists = False
                else:
                    group_name = PinGroup.unique_name(self._active_layout, group_name)
                    pin_group_exists = False
                if pin_group_exists:
                    return pgroup
        pin_group = PinGroup.create(self._active_layout, group_name, pins)
        if pin_group.is_null:
            return False
        else:
            pin_group.net = pins[0].net
            return pin_group

    def delete_single_pin_rlc(self, deactivate_only: bool = False) -> List[str]:
        """Delete or deactivate single-pin RLC components.

        Parameters
        ----------
        deactivate_only : bool, optional
            Whether to only deactivate instead of deleting.

        Returns
        -------
        list[str]
            List of affected components.

        Examples
        --------
        >>> deleted = edbapp.components.delete_single_pin_rlc()
        """
        deleted_comps = []
        for comp, val in self.instances.items():
            if hasattr(val, "pins") and val.pins:
                if val.num_pins == 1 and val.component_type in ["resistor", "capacitor", "inductor"]:
                    if deactivate_only:
                        val.is_enabled = False
                        val.model_type = "rlc"
                    else:
                        val.delete()
                        deleted_comps.append(comp)
        if not deactivate_only:
            self.refresh_components()
        self._pedb.logger.info("Deleted {} components".format(len(deleted_comps)))
        return deleted_comps

    def delete(self, component_name: str) -> bool:
        """Delete a component.

        Parameters
        ----------
        component_name : str
            Component name.

        Returns
        -------
        bool
            True if successful, False otherwise.

        Examples
        --------
        >>> edbapp.components.delete("R1")
        """
        edb_cmp = self.get_component_by_name(component_name)
        if edb_cmp is not None:
            edb_cmp.delete()
            if edb_cmp in list(self.instances.keys()):
                del self.instances[edb_cmp]
            return True
        return False

    def disable_rlc_component(self, component_name: str) -> bool:
        """Disable RLC component.

        Parameters
        ----------
        component_name : str
            Component name.

        Returns
        -------
        bool
            True if successful, False otherwise.

        Examples
        --------
        >>> edbapp.components.disable_rlc_component("R1")
        """
        cmp = self.get_component_by_name(component_name)
        if cmp is not None:
            component_property = cmp.component_property
            pin_pair_model = component_property.model
            for pin_pair in pin_pair_model.pin_pairs():
                rlc = pin_pair_model.rlc(pin_pair)
                rlc.c_enabled = False
                rlc.l_enabled = False
                rlc.r_enabled = False
                pin_pair_model.set_rlc(pin_pair, rlc)
            component_property.model = pin_pair_model
            cmp.component_property = component_property
            return True
        return False

    def set_solder_ball(
        self,
        component: Union[str, Component] = "",
        sball_diam: Optional[float] = None,
        sball_height: Optional[float] = None,
        shape: str = "Cylinder",
        sball_mid_diam: Optional[float] = None,
        chip_orientation: str = "chip_down",
        auto_reference_size: bool = True,
        reference_size_x: float = 0,
        reference_size_y: float = 0,
        reference_height: float = 0,
    ) -> bool:
        """Set solder ball properties for a component.

        Parameters
        ----------
        component : str or :class:`pyedb.grpc.database.hierarchy.component.Component`, optional
            Component name or instance.
        sball_diam : float, optional
            Solder ball diameter.
        sball_height : float, optional
            Solder ball height.
        shape : str, optional
            Solder ball shape ("Cylinder" or "Spheroid").
        sball_mid_diam : float, optional
            Solder ball mid diameter.
        chip_orientation : str, optional
            Chip orientation ("chip_down" or "chip_up").
        auto_reference_size : bool, optional
            Use auto reference size.
        reference_size_x : float, optional
            Reference size X.
        reference_size_y : float, optional
            Reference size Y.
        reference_height : float, optional
            Reference height.

        Returns
        -------
        bool
            True if successful, False otherwise.

        Examples
        --------
        >>> edbapp.components.set_solder_ball("U1", sball_diam=0.5e-3)
        """
        if isinstance(component, str):
            if component in self.instances:
                cmp = self.instances[component]
        else:
            cmp = self.instances[component.name]
        if not sball_diam:
            pin1 = list(cmp.pins.values())[0]
            pin_layers = pin1.padstack_def.data.layer_names
            pad_params = self._pedb.padstacks.get_pad_parameters(pin=pin1, layername=pin_layers[0], pad_type=0)
            _sb_diam = min([abs(Value(val)) for val in pad_params[1]])
            sball_diam = 0.8 * _sb_diam
        if sball_height:
            sball_height = Value(sball_height)
        else:
            sball_height = Value(sball_diam)

        if not sball_mid_diam:
            sball_mid_diam = sball_diam

        if shape.lower() == "cylinder":
            sball_shape = GrpcSolderballShape.SOLDERBALL_CYLINDER
        else:
            sball_shape = GrpcSolderballShape.SOLDERBALL_SPHEROID

        cmp_property = cmp.component_property
        if cmp.core.component_type == GrpcComponentType.IC:
            ic_die_prop = cmp_property.die_property
            ic_die_prop.die_type = GrpcDieType.FLIPCHIP
            if not cmp.placement_layer == list(self._pedb.stackup.layers.keys())[0]:
                chip_orientation = "chip_up"
            if chip_orientation.lower() == "chip_up":
                ic_die_prop.die_orientation = GrpDieOrientation.CHIP_UP
            else:
                ic_die_prop.die_orientation = GrpDieOrientation.CHIP_DOWN
            cmp_property.die_property = ic_die_prop

        solder_ball_prop = cmp_property.solder_ball_property
        solder_ball_prop.set_diameter(Value(sball_diam), Value(sball_mid_diam))
        solder_ball_prop.height = Value(sball_height)

        solder_ball_prop.shape = sball_shape
        cmp_property.solder_ball_property = solder_ball_prop

        port_prop = cmp_property.port_property
        port_prop.reference_height = Value(reference_height)
        port_prop.reference_size_auto = auto_reference_size
        if not auto_reference_size:
            port_prop.set_reference_size(Value(reference_size_x), Value(reference_size_y))
        cmp_property.port_property = port_prop
        cmp.component_property = cmp_property
        return True

    def set_component_rlc(
        self,
        componentname: str,
        res_value: Optional[float] = None,
        ind_value: Optional[float] = None,
        cap_value: Optional[float] = None,
        isparallel: bool = False,
    ) -> bool:
        """Set RLC values for a component.

        Parameters
        ----------
        componentname : str
            Component name.
        res_value : float, optional
            Resistance value.
        ind_value : float, optional
            Inductance value.
        cap_value : float, optional
            Capacitance value.
        isparallel : bool, optional
            Whether RLC is parallel.

        Returns
        -------
        bool
            True if successful, False otherwise.

        Examples
        --------
        >>> edbapp.components.set_component_rlc("R1", res_value=50)
        """
        if res_value is None and ind_value is None and cap_value is None:
            self.instances[componentname].enabled = False
            self._logger.info(f"No parameters passed, component {componentname} is disabled.")
            return True
        component = self.get_component_by_name(componentname)
        pin_number = len(component.pins)
        if pin_number == 2:
            from_pin = list(component.pins.values())[0]
            to_pin = list(component.pins.values())[1]
            rlc = GrpcRlc()
            rlc.is_parallel = isparallel
            if res_value is not None:
                rlc.r_enabled = True
                rlc.r = Value(res_value)
            else:
                rlc.r_enabled = False
            if ind_value is not None:
                rlc.l_enabled = True
                rlc.l = Value(ind_value)
            else:
                rlc.l_enabled = False
            if cap_value is not None:
                rlc.c_enabled = True
                rlc.c = Value(cap_value)
            else:
                rlc.CEnabled = False
            pin_pair = (from_pin.name, to_pin.name)
            component_property = component.component_property
            model = component_property.model
            model.set_rlc(pin_pair, rlc)
            component_property.model = model
            component.component_property = component_property
        else:
            self._logger.warning(
                f"Component {componentname} has not been assigned because either it is not present in the layout "
                "or it contains a number of pins not equal to 2."
            )
            return False
        self._logger.info(f"RLC properties for Component {componentname} has been assigned.")
        return True

    def update_rlc_from_bom(
        self,
        bom_file: str,
        delimiter: str = ";",
        valuefield: str = "Func des",
        comptype: str = "Prod name",
        refdes: str = "Pos / Place",
    ) -> bool:
        """Update RLC values from BOM file.

        Parameters
        ----------
        bom_file : str
            BOM file path.
        delimiter : str, optional
            Delimiter character.
        valuefield : str, optional
            Value field name.
        comptype : str, optional
            Component type field name.
        refdes : str, optional
            Reference designator field name.

        Returns
        -------
        bool
            True if successful, False otherwise.

        Examples
        --------
        >>> edbapp.components.update_rlc_from_bom("bom.csv")
        """
        with open(bom_file, "r") as f:
            Lines = f.readlines()
            found = False
            refdescolumn = None
            comptypecolumn = None
            valuecolumn = None
            unmount_comp_list = list(self.instances.keys())
            for line in Lines:
                content_line = [i.strip() for i in line.split(delimiter)]
                if valuefield in content_line:
                    valuecolumn = content_line.index(valuefield)
                if comptype in content_line:
                    comptypecolumn = content_line.index(comptype)
                if refdes in content_line:
                    refdescolumn = content_line.index(refdes)
                elif refdescolumn:
                    found = True
                    new_refdes = content_line[refdescolumn].split(" ")[0]
                    new_value = content_line[valuecolumn].split(" ")[0]
                    new_type = content_line[comptypecolumn]
                    if "resistor" in new_type.lower():
                        self.set_component_rlc(new_refdes, res_value=new_value)
                        unmount_comp_list.remove(new_refdes)
                    elif "capacitor" in new_type.lower():
                        self.set_component_rlc(new_refdes, cap_value=new_value)
                        unmount_comp_list.remove(new_refdes)
                    elif "inductor" in new_type.lower():
                        self.set_component_rlc(new_refdes, ind_value=new_value)
                        unmount_comp_list.remove(new_refdes)
            for comp in unmount_comp_list:
                self.instances[comp].enabled = False
        return found

    def import_bom(
        self,
        bom_file: str,
        delimiter: str = ",",
        refdes_col: int = 0,
        part_name_col: int = 1,
        comp_type_col: int = 2,
        value_col: int = 3,
    ) -> bool:
        """Import BOM file.

        Parameters
        ----------
        bom_file : str
            BOM file path.
        delimiter : str, optional
            Delimiter character.
        refdes_col : int, optional
            Reference designator column index.
        part_name_col : int, optional
            Part name column index.
        comp_type_col : int, optional
            Component type column index.
        value_col : int, optional
            Value column index.

        Returns
        -------
        bool
            True if successful, False otherwise.

        Examples
        --------
        >>> edbapp.components.import_bom("bom.csv")
        """
        with open(bom_file, "r") as f:
            lines = f.readlines()
            unmount_comp_list = list(self.instances.keys())
            for l in lines[1:]:
                l = l.replace(" ", "").replace("\n", "")
                if not l:
                    continue
                l = l.split(delimiter)

                refdes = l[refdes_col]
                comp = self.instances[refdes]
                if not part_name_col == None:
                    part_name = l[part_name_col]
                    if comp.partname == part_name:
                        pass
                    else:
                        pinlist = list(self.instances[refdes].pins.values())
                        if not pinlist:
                            continue
                        if not part_name in self.definitions:
                            ComponentDef.create(self._pedb, part_name, None)
                        p_layer = comp.placement_layer
                        refdes_temp = comp.refdes + "_temp"
                        comp.refdes = refdes_temp

                        unmount_comp_list.remove(refdes)
                        comp.core.ungroup(True)
                        self.create(pinlist, refdes, p_layer, part_name)
                        self.refresh_components()
                        comp = self.instances[refdes]

                comp_type = l[comp_type_col]
                if comp_type.capitalize() in ["Resistor", "Capacitor", "Inductor", "Other"]:
                    comp.type = comp_type.capitalize()
                else:
                    comp.type = comp_type.upper()

                if comp_type.capitalize() in ["Resistor", "Capacitor", "Inductor"] and refdes in unmount_comp_list:
                    unmount_comp_list.remove(refdes)
                if not value_col == None:
                    try:
                        value = l[value_col]
                    except:
                        value = None
                    if value:
                        if comp_type == "Resistor":
                            self.set_component_rlc(refdes, res_value=value)
                        elif comp_type == "Capacitor":
                            self.set_component_rlc(refdes, cap_value=value)
                        elif comp_type == "Inductor":
                            self.set_component_rlc(refdes, ind_value=value)
            for comp in unmount_comp_list:
                self.instances[comp].enabled = False
        return True

    def export_bom(self, bom_file: str, delimiter: str = ",") -> bool:
        """Export BOM file.

        Parameters
        ----------
        bom_file : str
            Output file path.
        delimiter : str, optional
            Delimiter character.

        Returns
        -------
        bool
            True if successful, False otherwise.

        Examples
        --------
        >>> edbapp.components.export_bom("exported_bom.csv")
        """
        with open(bom_file, "w") as f:
            f.writelines([delimiter.join(["RefDes", "Part name", "Type", "Value\n"])])
            for refdes, comp in self.instances.items():
                if not comp.is_enabled and comp.type in ["Resistor", "Capacitor", "Inductor"]:
                    continue
                part_name = comp.partname
                comp_type = comp.type
                if comp_type == "Resistor":
                    value = comp.res_value
                elif comp_type == "Capacitor":
                    value = comp.cap_value
                elif comp_type == "Inductor":
                    value = comp.ind_value
                else:
                    value = ""
                if not value:
                    value = ""
                f.writelines([delimiter.join([refdes, part_name, comp_type, value + "\n"])])
        return True

    def find_by_reference_designator(self, reference_designator: str) -> Component:
        """Find component by reference designator.

        Parameters
        ----------
        reference_designator : str
            Reference designator.

        Returns
        -------
        :class:`pyedb.grpc.database.hierarchy.component.Component`
            Component instance.

        Examples
        --------
        >>> comp = edbapp.components.find_by_reference_designator("R1")
        """
        return self.instances[reference_designator]

    def get_aedt_pin_name(self, pin: Any) -> str:
        """Get AEDT pin name.

        Parameters
        ----------
        pin : :class:`pyedb.grpc.database.padstacks.PadstackInstance`
            Pin instance.

        Returns
        -------
        str
            AEDT pin name.

        Examples
        --------
        >>> name = edbapp.components.get_aedt_pin_name(pin)
        """
        return pin.aedt_name

    def get_pins(
        self, reference_designator: str, net_name: Optional[str] = None, pin_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get pins of a component.

        Parameters
        ----------
        reference_designator : str
            Reference designator.
        net_name : str, optional
            Net name filter.
        pin_name : str, optional
            Pin name filter.

        Returns
        -------
        dict
            Dictionary of pins.

        Examples
        --------
        >>> pins = edbapp.components.get_pins("U1", net_name="GND")
        """
        comp = self.find_by_reference_designator(reference_designator)

        pins = comp.pins
        if net_name:
            pins = {i: j for i, j in pins.items() if j.net_name == net_name}

        if pin_name:
            pins = {i: j for i, j in pins.items() if i == pin_name}

        return pins

    def get_pin_position(self, pin: Any) -> List[float]:
        """Get pin position.

        Parameters
        ----------
        pin : :class:`pyedb.grpc.database.padstacks.PadstackInstance`
            Pin instance.

        Returns
        -------
        list[float]
            [x, y] position in meters.

        Examples
        --------
        >>> pos = edbapp.components.get_pin_position(pin)
        """

        pt_pos = pin.position
        if pin.component.is_null:
            transformed_pt_pos = pt_pos
        else:
            transformed_pt_pos = pin.component.core.transform.transform_point(pt_pos)
        return [Value(transformed_pt_pos[0]), Value(transformed_pt_pos[1])]

    def get_pins_name_from_net(self, net_name: str, pin_list: Optional[List[Any]] = None) -> List[str]:
        """Get pin names from net.

        Parameters
        ----------
        net_name : str
            Net name.
        pin_list : list, optional
            List of pins to search.

        Returns
        -------
        list[str]
            List of pin names.

        Examples
        --------
        >>> pins = edbapp.components.get_pins_name_from_net("GND")
        """
        pin_names = []
        if not pin_list:
            pin_list = []
            for i in [*self.components.values()]:
                for j in [*i.pins.values()]:
                    pin_list.append(j)
        for pin in pin_list:
            if not pin.net.is_null:
                if pin.net.name == net_name:
                    pin_names.append(self.get_aedt_pin_name(pin))
        return pin_names

    def get_nets_from_pin_list(self, pins: List[Any]) -> List[str]:
        """Get nets from pin list.

        Parameters
        ----------
        pins : list
            List of pins.

        Returns
        -------
        list[str]
            List of net names.

        Examples
        --------
        >>> nets = edbapp.components.get_nets_from_pin_list(pins)
        """
        return list(set([pin.net.name for pin in pins]))

    def get_component_net_connection_info(self, refdes: str) -> Dict[str, List[str]]:
        """Get net connection info for a component.

        Parameters
        ----------
        refdes : str
            Reference designator.

        Returns
        -------
        dict
            Dictionary with refdes, pin_name, and net_name.

        Examples
        --------
        >>> info = edbapp.components.get_component_net_connection_info("U1")
        """
        data = {"refdes": [], "pin_name": [], "net_name": []}
        for _, pin_obj in self.instances[refdes].pins.items():
            pin_name = pin_obj.name
            if not pin_obj.net.is_null:
                net_name = pin_obj.net.name
                if pin_name:
                    data["refdes"].append(refdes)
                    data["pin_name"].append(pin_name)
                    data["net_name"].append(net_name)
        return data

    def get_rats(self) -> List[Dict[str, List[str]]]:
        """Get RATS (Reference Designator, Pin, Net) information.

        Returns
        -------
        list[dict]
            List of dictionaries with refdes, pin_name, and net_name.

        Examples
        --------
        >>> rats = edbapp.components.get_rats()
        """
        df_list = []
        for refdes in self.instances.keys():
            df = self.get_component_net_connection_info(refdes)
            df_list.append(df)
        return df_list

    def get_through_resistor_list(self, threshold: float = 1) -> List[str]:
        """Get through resistors below threshold.

        Parameters
        ----------
        threshold : float, optional
            Resistance threshold.

        Returns
        -------
        list[str]
            List of component names.

        Examples
        --------
        >>> resistors = edbapp.components.get_through_resistor_list(1)
        """
        through_comp_list = []
        for refdes, comp_obj in self.resistors.items():
            numpins = comp_obj.numpins

            if numpins == 2:
                value = comp_obj.res_value
                value = resistor_value_parser(value)

                if value <= threshold:
                    through_comp_list.append(refdes)

        return through_comp_list

    def short_component_pins(
        self, component_name: str, pins_to_short: Optional[List[str]] = None, width: float = 1e-3
    ) -> bool:
        """Short component pins with traces.

        Parameters
        ----------
        component_name : str
            Component name.
        pins_to_short : list[str], optional
            List of pin names to short.
        width : float, optional
            Trace width.

        Returns
        -------
        bool
            True if successful, False otherwise.

        Examples
        --------
        >>> edbapp.components.short_component_pins("J4A2", ["G4", "9", "3"])
        """
        component = self.instances[component_name]
        pins = component.pins
        pins_list = []

        for pin_name, pin in pins.items():
            if pins_to_short:
                if pin_name in pins_to_short:
                    pins_list.append(pin)
            else:
                pins_list.append(pin)
        positions_to_short = []
        center = component.center
        c = [center[0], center[1], 0]
        delta_pins = []
        w = width
        for pin in pins_list:
            placement_layer = pin.placement_layer
            positions_to_short.append(pin.position)
            if placement_layer in self._pedb.padstacks.definitions[pin.padstack_def.name].pad_by_layer:
                pad = self._pedb.padstacks.definitions[pin.padstack_def.name].pad_by_layer[placement_layer]
            else:
                layer = list(self._pedb.padstacks.definitions[pin.padstack_def.name].pad_by_layer.keys())[0]
                pad = self._pedb.padstacks.definitions[pin.padstack_def.name].pad_by_layer[layer]
            pars = pad.parameters_values
            if pad.geometry_type < 6 and pars:
                delta_pins.append(max(pars) + min(pars) / 2)
                w = min(min(pars), w)
            elif pars:
                delta_pins.append(1.5 * pars[0])
                w = min(pars[0], w)
            elif pad.polygon_data:  # pragma: no cover
                bbox = pad.polygon_data.bbox()
                lower = [Value(bbox[0].x), Value(bbox[0].y)]
                upper = [Value(bbox[1].x), Value(bbox[1].y)]
                pars = [abs(lower[0] - upper[0]), abs(lower[1] - upper[1])]
                delta_pins.append(max(pars) + min(pars) / 2)
                w = min(min(pars), w)
            else:
                delta_pins.append(1.5 * width)
        i = 0

        while i < len(positions_to_short) - 1:
            p0 = []
            p0.append([positions_to_short[i][0] - delta_pins[i], positions_to_short[i][1], 0])
            p0.append([positions_to_short[i][0] + delta_pins[i], positions_to_short[i][1], 0])
            p0.append([positions_to_short[i][0], positions_to_short[i][1] - delta_pins[i], 0])
            p0.append([positions_to_short[i][0], positions_to_short[i][1] + delta_pins[i], 0])
            p0.append([positions_to_short[i][0], positions_to_short[i][1], 0])
            l0 = [
                GeometryOperators.points_distance(p0[0], c),
                GeometryOperators.points_distance(p0[1], c),
                GeometryOperators.points_distance(p0[2], c),
                GeometryOperators.points_distance(p0[3], c),
                GeometryOperators.points_distance(p0[4], c),
            ]
            l0_min = l0.index(min(l0))
            p1 = []
            p1.append(
                [
                    positions_to_short[i + 1][0] - delta_pins[i + 1],
                    positions_to_short[i + 1][1],
                    0,
                ]
            )
            p1.append(
                [
                    positions_to_short[i + 1][0] + delta_pins[i + 1],
                    positions_to_short[i + 1][1],
                    0,
                ]
            )
            p1.append(
                [
                    positions_to_short[i + 1][0],
                    positions_to_short[i + 1][1] - delta_pins[i + 1],
                    0,
                ]
            )
            p1.append(
                [
                    positions_to_short[i + 1][0],
                    positions_to_short[i + 1][1] + delta_pins[i + 1],
                    0,
                ]
            )
            p1.append([positions_to_short[i + 1][0], positions_to_short[i + 1][1], 0])

            l1 = [
                GeometryOperators.points_distance(p1[0], c),
                GeometryOperators.points_distance(p1[1], c),
                GeometryOperators.points_distance(p1[2], c),
                GeometryOperators.points_distance(p1[3], c),
                GeometryOperators.points_distance(p1[4], c),
            ]
            l1_min = l1.index(min(l1))

            trace_points = [positions_to_short[i]]

            trace_points.append(p0[l0_min][:2])
            trace_points.append(c[:2])
            trace_points.append(p1[l1_min][:2])

            trace_points.append(positions_to_short[i + 1])

            self._pedb.modeler.create_trace(
                trace_points,
                layer_name=placement_layer,
                net_name="short",
                width=w,
                start_cap_style="Flat",
                end_cap_style="Flat",
            )
            i += 1
        return True

    def create_pin_group(
        self, reference_designator: str, pin_numbers: Union[str, List[str]], group_name: Optional[str] = None
    ) -> Union[Tuple[str, PinGroup], bool]:
        """Create pin group on a component.

        Parameters
        ----------
        reference_designator : str
            Reference designator.
        pin_numbers : list[str]
            List of pin names.
        group_name : str, optional
            Group name.

        Returns
        -------
        tuple[str, :class:`pyedb.grpc.database.hierarchy.pingroup.PinGroup`] or bool
            (group_name, PinGroup) if successful, False otherwise.

        Examples
        --------
        >>> name, group = edbapp.components.create_pin_group("U1", ["1", "2"])
        """
        if not isinstance(pin_numbers, list):
            pin_numbers = [pin_numbers]
        pin_numbers = [str(p) for p in pin_numbers]
        if group_name is None:
            group_name = PinGroup.unique_name(self._active_layout, "")
        comp = self.instances[reference_designator]
        pins = [pin for pin_name, pin in comp.pins.items() if pin_name in pin_numbers]
        if not pins:
            pins = [pin for pin_name, pin in comp.pins.items() if pin.name in pin_numbers]
            if not pins:
                self._pedb.logger.error("No pin found to create pin group")
                return False
        pingroup = PinGroup.create(self._active_layout, group_name, pins)

        if pingroup.is_null:  # pragma: no cover
            raise RuntimeError(f"Failed to create pin group {group_name}.")
        else:
            for pin in pins:
                if not pin.net.is_null:
                    if pin.net.name:
                        pingroup.net = pin.net
                        return group_name, PinGroup(self._pedb, pingroup)
        return False

    def create_pin_group_on_net(
        self, reference_designator: str, net_name: str, group_name: Optional[str] = None
    ) -> PinGroup:
        """Create pin group by net name.

        Parameters
        ----------
        reference_designator : str
            Reference designator.
        net_name : str
            Net name.
        group_name : str, optional
            Group name.

        Returns
        -------
        :class:`pyedb.grpc.database.hierarchy.pingroup.PinGroup`
            Pin group instance.

        Examples
        --------
        >>> group = edbapp.components.create_pin_group_on_net("U1", "GND")
        """
        pins = [
            pin.name for pin in list(self.instances[reference_designator].pins.values()) if pin.net_name == net_name
        ]
        return self.create_pin_group(reference_designator, pins, group_name)

    def deactivate_rlc_component(
        self, component: Optional[str] = None, create_circuit_port: bool = False, pec_boundary: bool = False
    ) -> bool:
        """Deactivate RLC component with a possibility to convert it to a circuit port.

        Parameters
        ----------
        component : str
            Reference designator of the RLC component.

        create_circuit_port : bool, optional
            Whether to replace the deactivated RLC component with a circuit port. The default
            is ``False``.
        pec_boundary : bool, optional
            Whether to define the PEC boundary, The default is ``False``. If set to ``True``,
            a perfect short is created between the pin and impedance is ignored. This
            parameter is only supported on a port created between two pins, such as
            when there is no pin group.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb_file = r"C:\my_edb_file.aedb"
        >>> edb = Edb(edb_file)
        >>> for cmp in list(edb.components.instances.keys()):
        >>>     edb.components.deactivate_rlc_component(component=cmp, create_circuit_port=False)
        >>> edb.save_edb()
        >>> edb.close_edb()
        """
        if not component:
            return False
        if isinstance(component, str):
            component = self.instances[component]
            if not component:
                self._logger.error("component %s not found.", component)
                return False
        if component.type in ["other", "ic", "io"]:
            self._logger.info(f"Component {component.refdes} passed to deactivate is not an RLC.")
            return False
        component.is_enabled = False
        return self._pedb.source_excitation.add_port_on_rlc_component(
            component=component.refdes, circuit_ports=create_circuit_port, pec_boundary=pec_boundary
        )

    def add_port_on_rlc_component(
        self, component: Optional[Union[str, Component]] = None, circuit_ports: bool = True, pec_boundary: bool = False
    ) -> bool:
        """Deactivate RLC component and replace it with a circuit port.
        The circuit port supports only two-pin components.

        Parameters
        ----------
        component : str
            Reference designator of the RLC component.

        circuit_ports : bool
            ``True`` will replace RLC component by circuit ports, ``False`` gap ports compatible with HFSS 3D modeler
            export.

        pec_boundary : bool, optional
            Whether to define the PEC boundary, The default is ``False``. If set to ``True``,
            a perfect short is created between the pin and impedance is ignored. This
            parameter is only supported on a port created between two pins, such as
            when there is no pin group.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb()
        >>> edb.source_excitation.add_port_on_rlc_component("R1")
        """
        return self._pedb.source_excitation.add_port_on_rlc_component(
            component=component, circuit_ports=circuit_ports, pec_boundary=pec_boundary
        )

    def replace_rlc_by_gap_boundaries(self, component: Optional[Union[str, Component]] = None) -> bool:
        """Replace RLC component by RLC gap boundaries. These boundary types are compatible with 3D modeler export.
        Only 2 pins RLC components are supported in this command.

        Parameters
        ----------
        component : str
            Reference designator of the RLC component.

        Returns
        -------
        bool
        ``True`` when succeed, ``False`` if it failed.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb(edb_file)
        >>>  for refdes, cmp in edb.components.capacitors.items():
        >>>     edb.components.replace_rlc_by_gap_boundaries(refdes)
        >>> edb.save_edb()
        >>> edb.close_edb()
        """
        if not component:
            return False
        if isinstance(component, str):
            component = self.instances[component]
            if not component:
                self._logger.error("component %s not found.", component)
                return False
        if component.type in ["other", "ic", "io"]:
            self._logger.info(f"Component {component.refdes} skipped to deactivate is not an RLC.")
            return False
        component.enabled = False
        return self._pedb.source_excitation.add_rlc_boundary(component.refdes, False)

    def add_rlc_boundary(self, component: Optional[Union[str, Component]] = None, circuit_type: bool = True) -> bool:
        """Add RLC gap boundary on component and replace it with a circuit port.
        The circuit port supports only 2-pin components.

        . deprecated:: pyedb 0.28.0
        Use :func:`pyedb.grpc.core.excitations.add_rlc_boundary` instead.

        Parameters
        ----------
        component : str
            Reference designator of the RLC component.
        circuit_type : bool
            When ``True`` circuit type are defined, if ``False`` gap type will be used instead (compatible with HFSS 3D
            modeler). Default value is ``True``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        warnings.warn(
            "`add_rlc_boundary` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations.add_rlc_boundary` instead.",
            DeprecationWarning,
        )
        return self._pedb.source_excitation.add_rlc_boundary(self, component=component, circuit_type=circuit_type)
