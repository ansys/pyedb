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
    >>> edbapp.components  # access components object
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
        >>> from pyedb import Edb
        >>> edb = Edb("myaedbfolder")
        >>> component = edb.components["R1"]
        """
        if name in self.instances:
            return self.instances[name]
        elif name in self.definitions:
            return self.definitions[name]
        self._pedb.logger.error("Component or definition not found.")
        return None

    def __init__(self, p_edb: Any) -> None:
        self._pedb = p_edb
        # Initialize internal mappings and helpers here so static analyzers see them
        self._cmp: Dict[str, Component] = {}
        self._res: Dict[str, Component] = {}
        self._ind: Dict[str, Component] = {}
        self._cap: Dict[str, Component] = {}
        self._ics: Dict[str, Component] = {}
        self._ios: Dict[str, Component] = {}
        self._others: Dict[str, Component] = {}
        self._pins = {}
        self._comps_by_part = {}
        self._padstack = Padstacks(self._pedb)
        # Populate component dictionaries from the layout
        self.refresh_components()

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
        >>> from pyedb import Edb
        >>> edb = Edb("myaedbfolder")
        >>> component = edb.components.instances
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
        Example usage: edbapp.components.definitions
        """
        return {l.name: ComponentDef(self._pedb, l) for l in self._pedb.component_defs}

    @property
    def nport_comp_definition(self) -> Dict[str, ComponentDef]:
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
        >>> from pyedb import Edb
        >>> edb = Edb("aedb_folder")
        >>> edb.components.import_definition("definitions.json")
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
        >>> from pyedb import Edb
        >>> edb = Edb("aedb_folder")
        >>> edb.components.export_definition("exported_definitions.json")
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
                        # use getattr to avoid static-analysis warnings if attributes are not present
                        model_name_attr = getattr(model, "name", None) or getattr(model, "netlist", None) or ""
                        data["Definitions"][part_name]["Model_name"] = model_name_attr
                        data["Definitions"][part_name]["Reference_net"] = getattr(model, "reference_net", None)
                        if model_name_attr and model_name_attr not in data["SParameterModel"]:
                            data["SParameterModel"][model_name_attr] = getattr(model, "file_path", "")
                    elif comp.model_type == "SPICEModel":
                        model = comp.spice_model
                        model_name_attr = getattr(model, "name", None) or getattr(model, "netlist", None) or ""
                        data["Definitions"][part_name]["Model_name"] = model_name_attr
                        if model_name_attr and model_name_attr not in data["SPICEModel"]:
                            data["SPICEModel"][model_name_attr] = getattr(model, "file_path", "")
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
        >>> from pyedb import Edb
        >>> edb = Edb("aedb_folder")
        >>> edb.components.refresh_components()
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
            except (AttributeError, KeyError, TypeError) as exc:
                self._logger.warning(
                    "Assigning component %s as default type other due to exception: %s", i.name, str(exc)
                )
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
        >>> from pyedb import Edb
        >>> edb = Edb("aedb_folder")
        >>> edb.components.resistors
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
        Example usage: edbapp.components.capacitors
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
        >>> from pyedb import Edb
        >>> edb = Edb("aedb_folder")
        >>> edb.components.inductors
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
        >>> from pyedb import Edb
        >>> edb = Edb("aedb_folder")
        >>> edb.components.ICs
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
        >>> from pyedb import Edb
        >>> edb = Edb("aedb_folder")
        >>> edb.components.IOs
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
        >>> from pyedb import Edb
        >>> edb = Edb("aedb_folder")
        >>> edb.components.Others
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
        >>> from pyedb import Edb
        >>> edb = Edb("aedb_folder")
        >>> edb.components.components_by_partname
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
        >>> from pyedb import Edb
        >>> edb = Edb("aedb_folder")
        >>> edb.components.get_component_by_name("R1")
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
        >>> from pyedb import Edb
        >>> edb = Edb("aedb_folder")
        >>> edb.components.get_pin_from_component("R1", net_name="GND")
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
        >>> from pyedb import Edb
        >>> edb = Edb("aedb_folder")
        >>> edb.components.get_components_from_nets(["GND", "VCC"])
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

    @staticmethod
    def _get_edb_pin_from_pin_name(cmp: Component, pin: str) -> Union[Any, bool]:
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

    @staticmethod
    def get_pin_position(pin: Any) -> List[float]:
        """Get pin position as [x, y] (meters) handling component transform if present.

        Parameters
        ----------
        pin : :class:`pyedb.grpc.database.padstacks.PadstackInstance`
            Pin instance.

        Returns
        -------
        list[float]
            [x, y] position in meters.
        """
        if pin is None:
            return [0.0, 0.0]
        pt_pos = getattr(pin, "position", None)
        if pt_pos is None:
            return [0.0, 0.0]
        # If pin belongs to a component instance with a transform, apply it
        try:
            if hasattr(pin, "component") and pin.component and not getattr(pin.component, "is_null", False):
                transformed_pt_pos = pin.component.core.transform.transform_point(pt_pos)
            else:
                transformed_pt_pos = pt_pos
        except (AttributeError, TypeError, ValueError):
            # Be defensive for attribute/method errors or bad types/values: fall back to original point
            transformed_pt_pos = pt_pos
        return [Value(transformed_pt_pos[0]), Value(transformed_pt_pos[1])]

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
        >>> from pyedb import Edb
        >>> edb = Edb("aedb_folder")
        >>> edb.components.get_component_placement_vector(...)
        """
        if not isinstance(mounted_component, Component):
            return False, [0, 0], 0.0, 0.0
        if not isinstance(hosting_component, Component):
            return False, [0, 0], 0.0, 0.0

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
        return False, [0, 0], 0.0, 0.0

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
        >>> from pyedb import Edb
        >>> edb = Edb("aedb_folder")
        >>> edb.components.get_solder_ball_height("U1")
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
        >>> from pyedb import Edb
        >>> edb = Edb("aedb_folder")
        >>> edb.components.get_vendor_libraries()
        """
        comp_lib_path = os.path.join(self._pedb.base_path, "complib", "Locked")
        comp_types = ["Capacitors", "Inductors"]
        comp_lib = ComponentLib()
        comp_lib.path = comp_lib_path
        for cmp_type in comp_types:
            folder = os.path.join(comp_lib_path, cmp_type)
            if not os.path.isdir(folder):
                vendors = {}
            else:
                vendors = {f.name: {} for f in os.scandir(folder) if f.is_dir()}
            for vendor in list(vendors.keys()):
                vendor_folder = os.path.join(folder, vendor)
                if not os.path.isdir(vendor_folder):
                    series = {}
                else:
                    series = {f.name: {} for f in os.scandir(vendor_folder) if f.is_dir()}
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
            Solder ball mid-size.
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
            "`_create_terminal` is deprecated; use pin.create_terminal() or "
            "pyedb.grpc.core.excitations.create_terminal instead.",
            DeprecationWarning,
        )
        return self._pedb.create_terminal(pin, term_name)

    @staticmethod
    def _get_closest_pin_from(pin, ref_pinlist):
        """Get the closest pin from a list of pins.

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
            temp_distance = GeometryOperators.points_distance(pin_position, ref_pin.position)
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
        return self._pedb._create_pin_group_terminal(
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
        >>> from pyedb import Edb
        >>> edb = Edb("aedb_folder")
        >>> edb.components.create(pins, "R1")
        """
        from ansys.edb.core.hierarchy.component_group import (
            ComponentGroup as GrpcComponentGroup,
        )

        if is_rlc and (r_value is None and c_value is None and l_value is None):
            raise ValueError("At least one of r_value, c_value, or l_value must be provided for RLC components.")

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
            rlc_model.core.set_rlc(pin_pair, rlc)
            component_property = new_cmp.component_property
            component_property.model = rlc_model.core
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
        >>> from pyedb import Edb
        >>> edb = Edb("aedb_folder")
        >>> edb.components.set_component_model("U1", "Spice", "path/to/model.sp")
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
                        pin_names = [i.strip() for i in re.split(r"[\t ]+", line) if i.strip()]
                        if len(pin_names) >= 2:
                            pin_names = pin_names[2:]
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

            # Use the supported component_definition attribute
            n_port_model = GrpcNPortComponentModel.find_by_name(component.component_definition, n_port_model_name)
            if n_port_model.is_null:
                n_port_model = GrpcNPortComponentModel.create(n_port_model_name)
                n_port_model.reference_file = modelpath
                component.component_definition.add_component_model(n_port_model)
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
        >>> from pyedb import Edb
        >>> edb = Edb("aedb_folder")
        >>> edb.components.create_pingroup_from_pins(pins, "GND_pins")
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
                    group_name = PinGroup.unique_name(self._pedb.active_layout, group_name)
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
        >>> from pyedb import Edb
        >>> edb = Edb("aedb_folder")
        >>> edb.components.delete_single_pin_rlc()
        """
        deleted_comps = []
        for comp, val in self.instances.items():
            if hasattr(val, "pins") and val.pins:
                if val.num_pins == 1 and val.component_type in ["resistor", "capacitor", "inductor"]:
                    if deactivate_only:
                        val.is_enabled = False
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
        >>> from pyedb import Edb
        >>> edb = Edb("aedb_folder")
        >>> edb.components.delete("R1")
        """
        edb_cmp = self.get_component_by_name(component_name)
        if edb_cmp is not None:
            edb_cmp.delete()
            if component_name in list(self._cmp.keys()):
                del self._cmp[component_name]
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
        >>> from pyedb import Edb
        >>> edb = Edb("aedb_folder")
        >>> edb.components.disable_rlc_component("R1")
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
        component: Union[str, Component],
        sball_diam: Optional[float] = None,
        sball_height: Optional[float] = None,
        sball_mid_diam: Optional[float] = None,
        chip_orientation: Optional[str] = None,
        shape: str = "sphere",
        auto_reference_size: bool = True,
        reference_size_x: float = 0.0,
        reference_size_y: float = 0.0,
        reference_height: float = 0.0,
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
        sball_mid_diam : float, optional
            Solder ball mid-diameter.
        chip_orientation : str, optional
            Chip orientation ("chip_down" or "chip_up").
        shape : str, optional
            Solder ball shape ("sphere" or "cylinder").
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
        >>> from pyedb import Edb
        >>> edb = Edb("aedb_folder")
        >>> edb.components.set_solder_ball("U1", sball_diam=0.5e-3)
        """
        if isinstance(component, str):
            cmp = self.instances.get(component, None)
        else:
            # component may already be a Component instance
            cmp = self.instances.get(component.name) if hasattr(component, "name") else None
        if cmp is None:
            self._logger.error("Component %s not found for solder ball configuration", str(component))
            return False
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

        if chip_orientation is None:
            # Default to chip_down if not specified
            chip_orientation = "chip_down"

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
        res_value: Optional[Union[float, str]] = None,
        ind_value: Optional[Union[float, str]] = None,
        cap_value: Optional[Union[float, str]] = None,
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
        >>> from pyedb import Edb
        >>> edb = Edb("aedb_folder")
        >>> edb.components.set_component_rlc("R1", res_value=50)
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
                if isinstance(res_value, str):
                    try:
                        rlc.r = Value(resistor_value_parser(res_value))
                    except (ValueError, TypeError):
                        # Parsing may fail for malformed strings; fall back to wrapping the original value
                        rlc.r = Value(res_value)
            else:
                rlc.r_enabled = False
            if ind_value is not None:
                rlc.l_enabled = True
                rlc.l = Value(float(ind_value)) if isinstance(ind_value, str) else Value(ind_value)
            else:
                rlc.l_enabled = False
            if cap_value is not None:
                rlc.c_enabled = True
                rlc.c = Value(float(cap_value)) if isinstance(cap_value, str) else Value(cap_value)
            else:
                rlc.c_enabled = False
            pin_pair = (from_pin.name, to_pin.name)
            rlc_model = PinPairModel(self._pedb, component.component_property.model)
            rlc_model.core.set_rlc(pin_pair, rlc)
            component.component_property.model = rlc_model.core
            component.component_type = GrpcComponentType.RESISTOR
            return True
        return False

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
        >>> from pyedb import Edb
        >>> edb = Edb("aedb_folder")
        >>> edb.components.update_rlc_from_bom("bom.csv")
        """
        with open(bom_file, "r") as f:
            lines = f.readlines()
            refdescolumn = None
            comptypecolumn = None
            valuecolumn = None
            unmount_comp_list = list(self.instances.keys())
            for line in lines:
                content_line = [i.strip() for i in line.split(delimiter)]
                if valuefield in content_line:
                    valuecolumn = content_line.index(valuefield)
                if comptype in content_line:
                    comptypecolumn = content_line.index(comptype)
                if refdes in content_line:
                    refdescolumn = content_line.index(refdes)
                elif refdescolumn:
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
                try:
                    self.instances[comp].enabled = False
                except (KeyError, AttributeError):
                    # Be defensive if component was removed/renamed or doesn't have `enabled`
                    continue
        return True

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
        >>> from pyedb import Edb
        >>> edb = Edb("aedb_folder")
        >>> edb.components.import_bom("bom.csv")
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
                if part_name_col is not None:
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
                if value_col is not None:
                    try:
                        value = l[value_col]
                    except (IndexError, ValueError):
                        value = None
                    if value:
                        if comp_type == "Resistor":
                            self.set_component_rlc(refdes, res_value=value)
                        elif comp_type == "Capacitor":
                            self.set_component_rlc(refdes, cap_value=value)
                        elif comp_type == "Inductor":
                            self.set_component_rlc(refdes, ind_value=value)

            for comp in unmount_comp_list:
                try:
                    self.instances[comp].enabled = False
                except (KeyError, AttributeError):
                    # Be defensive if component was removed/renamed or doesn't have `enabled`
                    continue
        return True
