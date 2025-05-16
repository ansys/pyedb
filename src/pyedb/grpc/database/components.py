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

"""This module contains the `Components` class.

"""
import codecs
import json
import math
import os
import re
import warnings

from ansys.edb.core.definition.die_property import DieOrientation as GrpDieOrientation
from ansys.edb.core.definition.die_property import DieType as GrpcDieType
from ansys.edb.core.definition.solder_ball_property import (
    SolderballShape as GrpcSolderballShape,
)
from ansys.edb.core.hierarchy.component_group import ComponentType as GrpcComponentType
from ansys.edb.core.hierarchy.spice_model import SPICEModel as GrpcSPICEModel
from ansys.edb.core.utility.rlc import Rlc as GrpcRlc
from ansys.edb.core.utility.value import Value as GrpcValue

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
from pyedb.modeler.geometry_operators import GeometryOperators


def resistor_value_parser(r_value):
    """Convert a resistor value.

    Parameters
    ----------
    r_value : float
        Resistor value.

    Returns
    -------
    float
        Resistor value.

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
    """Manages EDB components and related method accessible from `Edb.components` property.

    Parameters
    ----------
    edb_class : :class:`pyedb.grpc.edb.Edb`

    Examples
    --------
    >>> from pyedb import Edb
    >>> edbapp = Edb("myaedbfolder")
    >>> edbapp.components
    """

    def __getitem__(self, name):
        """Get  a component or component definition from the Edb project.

        Parameters
        ----------
        name : str

        Returns
        -------
        :class:`pyedb.dotnet.database.cell.hierarchy.component.EDBComponent`

        """
        if name in self.instances:
            return self.instances[name]
        elif name in self.definitions:
            return self.definitions[name]
        self._pedb.logger.error("Component or definition not found.")
        return

    def __init__(self, p_edb):
        self._pedb = p_edb
        self.refresh_components()
        self._pins = {}
        self._comps_by_part = {}
        self._padstack = Padstacks(self._pedb)
        # self._excitations = self._pedb.excitations

    @property
    def _logger(self):
        """Logger."""
        return self._pedb.logger

    @property
    def _active_layout(self):
        return self._pedb.active_layout

    @property
    def _layout(self):
        return self._pedb.layout

    @property
    def _cell(self):
        return self._pedb.cell

    @property
    def _db(self):
        return self._pedb.active_db

    @property
    def instances(self):
        """All Cell components objects.

        Returns
        -------
        Dict[str, :class:`pyedb.grpc.database.cell.hierarchy.component.Component`]
            Default dictionary for the EDB component.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.components.instances

        """
        return self._cmp

    @property
    def definitions(self):
        """Retrieve component definition list.

        Returns
        -------
        dict of :class:`EDBComponentDef`"""
        return {l.name: ComponentDef(self._pedb, l) for l in self._pedb.component_defs}

    @property
    def nport_comp_definition(self):
        """Retrieve Nport component definition list."""
        return {name: l for name, l in self.definitions.items() if l.reference_file}

    def import_definition(self, file_path):
        """Import component definition from json file.

        Parameters
        ----------
        file_path : str
            File path of json file.
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

    def export_definition(self, file_path):
        """Export component definitions to json file.

        Parameters
        ----------
        file_path : str
            File path of json file.

        Returns
        -------

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
        return file_path

    def refresh_components(self):
        """Refresh the component dictionary."""
        self._logger.info("Refreshing the Components dictionary.")
        self._cmp = {}
        self._res = {}
        self._ind = {}
        self._cap = {}
        self._ics = {}
        self._ios = {}
        self._others = {}
        for i in self._pedb.layout.groups:
            self._cmp[i.name] = i
            try:
                if i.type == "resistor":
                    self._res[i.name] = i
                elif i.type == "capacitor":
                    self._cap[i.name] = i
                elif i.type == "inductor":
                    self._ind[i.name] = i
                elif i.type == "ic":
                    self._ics[i.name] = i
                elif i.type == "io":
                    self._ios[i.name] = i
                elif i.type == "other":
                    self._others[i.name] = i
                else:
                    self._logger.warning(
                        f"Unknown component type {i.name} found while refreshing components, will ignore"
                    )
            except:
                self._logger.warning(f"Assigning component {i.name} as default type other.")
                self._others[i.name] = i
        return True

    @property
    def resistors(self):
        """Resistors.

        Returns
        -------
        dict[str, .:class:`pyedb.dotnet.database.cell.hierarchy.component.EDBComponent`]
            Dictionary of resistors.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.components.resistors
        """
        return self._res

    @property
    def capacitors(self):
        """Capacitors.

        Returns
        -------
        dict[str, .:class:`pyedb.dotnet.database.cell.hierarchy.component.EDBComponent`]
            Dictionary of capacitors.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.components.capacitors
        """
        return self._cap

    @property
    def inductors(self):
        """Inductors.

        Returns
        -------
        dict[str, .:class:`pyedb.dotnet.database.cell.hierarchy.component.EDBComponent`]
            Dictionary of inductors.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.components.inductors

        """
        return self._ind

    @property
    def ICs(self):
        """Integrated circuits.

        Returns
        -------
        dict[str, .:class:`pyedb.dotnet.database.cell.hierarchy.component.EDBComponent`]
            Dictionary of integrated circuits.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.components.ICs

        """
        return self._ics

    @property
    def IOs(self):
        """Circuit inupts and outputs.

        Returns
        -------
        dict[str, .:class:`pyedb.dotnet.database.cell.hierarchy.component.EDBComponent`]
            Dictionary of circuit inputs and outputs.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.components.IOs

        """
        return self._ios

    @property
    def Others(self):
        """Other core components.

        Returns
        -------
        dict[str, .:class:`pyedb.dotnet.database.cell.hierarchy.component.EDBComponent`]
            Dictionary of other core components.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.components.others

        """
        return self._others

    @property
    def components_by_partname(self):
        """Components by part name.

        Returns
        -------
        dict
            Dictionary of components by part name.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.components.components_by_partname

        """
        self._comps_by_part = {}
        for el, val in self.instances.items():
            if val.partname in self._comps_by_part.keys():
                self._comps_by_part[val.partname].append(val)
            else:
                self._comps_by_part[val.partname] = [val]
        return self._comps_by_part

    def get_component_by_name(self, name):
        """Retrieve a component by name.

        Parameters
        ----------
        name : str
            Name of the component.

        Returns
        -------
        bool
            Component object.

        """
        return self.instances[name]

    def get_pin_from_component(self, component, net_name=None, pin_name=None):
        """Return component pins.
        Parameters
        ----------
        component: .:class: `Component` or str.
            Component object or component name.
        net_name : str, List[str], optional
            Apply filter on net name.
        pin_name : str, optional
            Apply filter on specific pin name.
        Return
        ------
        List[:clas: `PadstackInstance`]



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

    def get_components_from_nets(self, netlist=None):
        """Retrieve components from a net list.

        Parameters
        ----------
        netlist : str, optional
            Name of the net list. The default is ``None``.

        Returns
        -------
        list
            List of components that belong to the signal nets.

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

    def _get_edb_pin_from_pin_name(self, cmp, pin):
        if not isinstance(cmp, Component):
            return False
        if not isinstance(pin, str):
            return False
        if pin in cmp.pins:
            return cmp.pins[pin]
        return False

    def get_component_placement_vector(
        self,
        mounted_component,
        hosting_component,
        mounted_component_pin1,
        mounted_component_pin2,
        hosting_component_pin1,
        hosting_component_pin2,
        flipped=False,
    ):
        """Get the placement vector between 2 components.

        Parameters
        ----------
        mounted_component : `edb.cell.hierarchy._hierarchy.Component`
            Mounted component name.
        hosting_component : `edb.cell.hierarchy._hierarchy.Component`
            Hosting component name.
        mounted_component_pin1 : str
            Mounted component Pin 1 name.
        mounted_component_pin2 : str
            Mounted component Pin 2 name.
        hosting_component_pin1 : str
            Hosted component Pin 1 name.
        hosting_component_pin2 : str
            Hosted component Pin 2 name.
        flipped : bool, optional
            Either if the mounted component will be flipped or not.

        Returns
        -------
        tuple
            Tuple of Vector offset, rotation and solder height.

        Examples
        --------
        >>> edb1 = Edb(edbpath=targetfile1,  edbversion="2021.2")
        >>> hosting_cmp = edb1.components.get_component_by_name("U100")
        >>> mounted_cmp = edb2.components.get_component_by_name("BGA")
        >>> vector, rotation, solder_ball_height = edb1.components.get_component_placement_vector(
        ...                                             mounted_component=mounted_cmp,
        ...                                             hosting_component=hosting_cmp,
        ...                                             mounted_component_pin1="A12",
        ...                                             mounted_component_pin2="A14",
        ...                                             hosting_component_pin1="A12",
        ...                                             hosting_component_pin2="A14")
        """
        m_pin1_pos = [0.0, 0.0]
        m_pin2_pos = [0.0, 0.0]
        h_pin1_pos = [0.0, 0.0]
        h_pin2_pos = [0.0, 0.0]
        if not isinstance(mounted_component, Component):
            return False
        if not isinstance(hosting_component, Component):
            return False

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

    def get_solder_ball_height(self, cmp):
        """Get component solder ball height.

        Parameters
        ----------
        cmp : str or `Component` object.
            EDB component or str component name.

        Returns
        -------
        double, bool
            Salder ball height vale, ``False`` when failed.

        """
        if isinstance(cmp, str):
            cmp = self.get_component_by_name(cmp)
        return cmp.solder_ball_height

    def get_vendor_libraries(self):
        """Retrieve all capacitors and inductors libraries from ANSYS installation (used by Siwave).

        Returns
        -------
        ComponentLib object contains nested dictionaries to navigate through [component type][vendors][series]
        :class: `pyedb.component_libraries.ansys_components.ComponentPart`

        Examples
        --------
        >>> edbapp = Edb()
        >>> comp_lib = edbapp.components.get_vendor_libraries()
        >>> network = comp_lib.capacitors["AVX"]["AccuP01005"]["C005YJ0R1ABSTR"].s_parameters
        >>> network.write_touchstone(os.path.join(edbapp.directory, "test_export.s2p"))

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

    def create_source_on_component(self, sources=None):
        """Create voltage, current source, or resistor on component.

        . deprecated:: pyedb 0.28.0
        Use .:func:`pyedb.grpc.core.excitations.create_source_on_component` instead.

        Parameters
        ----------
        sources : list[Source]
            List of ``edb_data.sources.Source`` objects.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

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
    ):
        """Create circuit port between pins and reference ones.

        . deprecated:: pyedb 0.28.0
        Use :func:`pyedb.grpc.core.excitations.create_port_on_pins` instead.

        Parameters
        ----------
        refdes : Component reference designator
            str or EDBComponent object.
        pins : pin name where the terminal has to be created. Single pin or several ones can be provided.If several
        pins are provided a pin group will is created. Pin names can be the EDB name or the EDBPadstackInstance one.
        For instance the pin called ``Pin1`` located on component ``U1``, ``U1-Pin1`` or ``Pin1`` can be provided and
        will be handled.
            str, [str], EDBPadstackInstance, [EDBPadstackInstance]
        reference_pins : reference pin name used for terminal reference. Single pin or several ones can be provided.
        If several pins are provided a pin group will is created. Pin names can be the EDB name or the
        EDBPadstackInstance one. For instance the pin called ``Pin1`` located on component ``U1``, ``U1-Pin1``
        or ``Pin1`` can be provided and will be handled.
            str, [str], EDBPadstackInstance, [EDBPadstackInstance]
        impedance : Port impedance
            str, float
        port_name : str, optional
            Port name. The default is ``None``, in which case a name is automatically assigned.
        pec_boundary : bool, optional
        Whether to define the PEC boundary, The default is ``False``. If set to ``True``,
        a perfect short is created between the pin and impedance is ignored. This
        parameter is only supported on a port created between two pins, such as
        when there is no pin group.
        pingroup_on_single_pin : bool
            If ``True`` force using pingroup definition on single pin to have the port created at the pad center. If
            ``False`` the port is created at the pad edge. Default value is ``False``.

        Returns
        -------
        EDB terminal created, or False if failed to create.
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
    ):
        """Create ports on a component.

        . deprecated:: pyedb 0.28.0
        Use :func:`pyedb.grpc.core.excitations.create_port_on_component` instead.

        Parameters
        ----------
        component : str or  self._pedb.component
            EDB component or str component name.
        net_list : str or list of string.
            List of nets where ports must be created on the component.
            If the net is not part of the component, this parameter is skipped.
        port_type : SourceType enumerator, CoaxPort or CircuitPort
            Type of port to create. ``CoaxPort`` generates solder balls.
            ``CircuitPort`` generates circuit ports on pins belonging to the net list.
        do_pingroup : bool
            True activate pingroup during port creation (only used with combination of CircPort),
            False will take the closest reference pin and generate one port per signal pin.
        refnet : string or list of string.
            list of the reference net.
        port_name : str
            Port name for overwriting the default port-naming convention,
            which is ``[component][net][pin]``. The port name must be unique.
            If a port with the specified name already exists, the
            default naming convention is used so that port creation does
            not fail.
        solder_balls_height : float, optional
            Solder balls height used for the component. When provided default value is overwritten and must be
            provided in meter.
        solder_balls_size : float, optional
            Solder balls diameter. When provided auto evaluation based on padstack size will be disabled.
        solder_balls_mid_size : float, optional
            Solder balls mid-diameter. When provided if value is different than solder balls size, spheroid shape will
            be switched.
        extend_reference_pins_outside_component : bool
            When no reference pins are found on the component extend the pins search with taking the closest one. If
            `do_pingroup` is `True` will be set to `False`. Default value is `False`.

        Returns
        -------
        double, bool
            Salder ball height vale, ``False`` when failed.

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

    def _create_terminal(self, pin, term_name=None):
        """Create terminal on component pin.

        . deprecated:: pyedb 0.28.0
        Use :func:`pyedb.grpc.core.excitations._create_terminal` instead.

        Parameters
        ----------
        pin : Edb padstack instance.

        term_name : Terminal name (Optional).
            str.

        Returns
        -------
        EDB terminal.
        """
        warnings.warn(
            "`_create_terminal` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations._create_terminal` instead.",
            DeprecationWarning,
        )
        self._pedb.excitations._create_terminal(pin, term_name=term_name)

    def _get_closest_pin_from(self, pin, ref_pinlist):
        """Returns the closest pin from given pin among the list of reference pins.

        Parameters
        ----------
        pin : Edb padstack instance.

        ref_pinlist : list of reference edb pins.

        Returns
        -------
        Edb pin.

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

    def replace_rlc_by_gap_boundaries(self, component=None):
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

    def deactivate_rlc_component(self, component=None, create_circuit_port=False, pec_boundary=False):
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
        >>> edb_file = r'C:\my_edb_file.aedb'
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

    def add_port_on_rlc_component(self, component=None, circuit_ports=True, pec_boundary=False):
        """Deactivate RLC component and replace it with a circuit port.
        The circuit port supports only two-pin components.

        . deprecated:: pyedb 0.28.0
        Use :func:`pyedb.grpc.core.excitations.add_port_on_rlc_component` instead.

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
        """
        warnings.warn(
            "`add_port_on_rlc_component` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations.add_port_on_rlc_component` instead.",
            DeprecationWarning,
        )
        return self._pedb.source_excitation.add_port_on_rlc_component(
            component=component, circuit_ports=circuit_ports, pec_boundary=pec_boundary
        )

    def add_rlc_boundary(self, component=None, circuit_type=True):
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

    def _create_pin_group_terminal(self, pingroup, isref=False, term_name=None, term_type="circuit"):
        """Creates an EDB pin group terminal from a given EDB pin group.

        . deprecated:: pyedb 0.28.0
        Use :func:`pyedb.grpc.core.excitations._create_pin_group_terminal` instead.

        Parameters
        ----------
        pingroup : Edb pin group.

        isref : bool
        Specify if this terminal a reference terminal.

        term_name : Terminal name (Optional). If not provided default name is Component name, Pin name, Net name.
            str.

        term_type: Type of terminal, gap, circuit or auto.
        str.
        Returns
        -------
        Edb pin group terminal.
        """
        warnings.warn(
            "`_create_pin_group_terminal` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations._create_pin_group_terminal` instead.",
            DeprecationWarning,
        )
        return self._pedb.source_excitation._create_pin_group_terminal(
            pingroup=pingroup, term_name=term_name, term_type=term_type, isref=isref
        )

    def _is_top_component(self, cmp):
        """Test the component placement layer.

        Parameters
        ----------
        cmp :  self._pedb.component
             Edb component.

        Returns
        -------
        bool
            ``True`` when component placed on top layer, ``False`` on bottom layer.


        """
        top_layer = self._pedb.stackup.signal[0].name
        if cmp.placement_layer == top_layer:
            return True
        else:
            return False

    def _get_component_definition(self, name, pins):
        component_definition = ComponentDef.find(self._db, name)
        if component_definition.is_null:
            from ansys.edb.core.layout.cell import Cell as GrpcCell
            from ansys.edb.core.layout.cell import CellType as GrpcCellType

            foot_print_cell = GrpcCell.create(self._pedb.active_db, GrpcCellType.FOOTPRINT_CELL, name)
            component_definition = ComponentDef.create(self._db, name, fp=foot_print_cell)
            if component_definition.is_null:
                self._logger.error(f"Failed to create component definition {name}")
                return False
            ind = 1
            for pin in pins:
                if not pin.name:
                    pin.name = str(ind)
                ind += 1
                component_definition_pin = ComponentPin.create(component_definition, pin.name)
                if component_definition_pin.is_null:
                    self._logger.error(f"Failed to create component definition pin {name}-{pin.name}")
                    return None
        else:
            self._logger.warning("Found existing component definition for footprint {}".format(name))
        return component_definition

    def create(
        self,
        pins,
        component_name=None,
        placement_layer=None,
        component_part_name=None,
        is_rlc=False,
        r_value=None,
        c_value=None,
        l_value=None,
        is_parallel=False,
    ):
        """Create a component from pins.

        Parameters
        ----------
        pins : list
            List of EDB core pins.
        component_name : str
            Name of the reference designator for the component.
        placement_layer : str, optional
            Name of the layer used for placing the component.
        component_part_name : str, optional
            Part name of the component.
        is_rlc : bool, optional
            Whether if the new component will be an RLC or not.
        r_value : float
            Resistor value.
        c_value : float
            Capacitance value.
        l_value : float
            Inductor value.
        is_parallel : bool
            Using parallel model when ``True``, series when ``False``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> pins = edbapp.components.get_pin_from_component("A1")
        >>> edbapp.components.create(pins, "A1New")

        """
        from ansys.edb.core.hierarchy.component_group import (
            ComponentGroup as GrpcComponentGroup,
        )

        if not component_name:
            component_name = generate_unique_name("Comp_")
        if component_part_name:
            compdef = self._get_component_definition(component_part_name, pins)
        else:
            compdef = self._get_component_definition(component_name, pins)
        if not compdef:
            return False
        new_cmp = GrpcComponentGroup.create(self._active_layout, component_name, compdef.name)
        hosting_component_location = pins[0].component.transform
        if not len(pins) == len(compdef.component_pins):
            self._pedb.logger.error(
                f"Number on pins {len(pins)} does not match component definition number "
                f"of pins {len(compdef.component_pins)}"
            )
            return False
        for padstack_instance, component_pin in zip(pins, compdef.component_pins):
            padstack_instance.is_layout_pin = True
            padstack_instance.name = component_pin.name
            new_cmp.add_member(padstack_instance)
        if not placement_layer:
            new_cmp_layer_name = pins[0].padstack_def.data.layer_names[0]
        else:
            new_cmp_layer_name = placement_layer
        if new_cmp_layer_name in self._pedb.stackup.signal_layers:
            new_cmp_placement_layer = self._pedb.stackup.signal_layers[new_cmp_layer_name]
            new_cmp.placement_layer = new_cmp_placement_layer
        new_cmp.component_type = GrpcComponentType.OTHER
        if is_rlc and len(pins) == 2:
            rlc = GrpcRlc()
            rlc.is_parallel = is_parallel
            if not r_value:
                rlc.r_enabled = False
            else:
                rlc.r_enabled = True
                rlc.r = GrpcValue(r_value)
            if l_value is None:
                rlc.l_enabled = False
            else:
                rlc.l_enabled = True
                rlc.l = GrpcValue(l_value)
            if c_value is None:
                rlc.c_enabled = False
            else:
                rlc.c_enabled = True
                rlc.C = GrpcValue(c_value)
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
        new_cmp.transform = hosting_component_location
        new_edb_comp = Component(self._pedb, new_cmp)
        self._cmp[new_cmp.name] = new_edb_comp
        return new_edb_comp

    def create_component_from_pins(
        self, pins, component_name, placement_layer=None, component_part_name=None
    ):  # pragma: no cover
        """Create a component from pins.

        .. deprecated:: 0.6.62
           Use :func:`create` method instead.

        Parameters
        ----------
        pins : list
            List of EDB core pins.
        component_name : str
            Name of the reference designator for the component.
        placement_layer : str, optional
            Name of the layer used for placing the component.
        component_part_name : str, optional
            Part name of the component. It's created a new definition if doesn't exists.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> pins = edbapp.components.get_pin_from_component("A1")
        >>> edbapp.components.create(pins, "A1New")

        """
        warnings.warn("`create_component_from_pins` is deprecated use `create` instead..", DeprecationWarning)
        return self.create(
            pins=pins,
            component_name=component_name,
            placement_layer=placement_layer,
            component_part_name=component_part_name,
            is_rlc=False,
        )

    def set_component_model(self, componentname, model_type="Spice", modelpath=None, modelname=None):
        """Assign a Spice or Touchstone model to a component.

        Parameters
        ----------
        componentname : str
            Name of the component.
        model_type : str, optional
            Type of the model. Options are ``"Spice"`` and
            ``"Touchstone"``.  The default is ``"Spice"``.
        modelpath : str, optional
            Full path to the model file. The default is ``None``.
        modelname : str, optional
            Name of the model. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.components.set_component_model("A1", model_type="Spice",
        ...                                            modelpath="pathtospfile",
        ...                                            modelname="spicemodelname")

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

    def create_pingroup_from_pins(self, pins, group_name=None):
        """Create a pin group on a component.

        Parameters
        ----------
        pins : list
            List of EDB pins.
        group_name : str, optional
            Name for the group. The default is ``None``, in which case
            a default name is assigned as follows: ``[component Name] [NetName]``.

        Returns
        -------
        tuple
            The tuple is structured as: (bool, pingroup).

        Examples
        --------
        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.components.create_pingroup_from_pins(gndpinlist, "MyGNDPingroup")

        """
        if len(pins) < 1:
            self._logger.error("No pins specified for pin group %s", group_name)
            return (False, None)
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

    def delete_single_pin_rlc(self, deactivate_only=False):
        # type: (bool) -> list
        """Delete all RLC components with a single pin.
        Single pin component model type will be reverted to ``"RLC"``.

        Parameters
        ----------
        deactivate_only : bool, optional
            Whether to only deactivate RLC components with a single point rather than
            delete them. The default is ``False``, in which case they are deleted.

        Returns
        -------
        list
            List of deleted RLC components.


        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> list_of_deleted_rlcs = edbapp.components.delete_single_pin_rlc()
        >>> print(list_of_deleted_rlcs)

        """
        deleted_comps = []
        for comp, val in self.instances.items():
            if val.numpins < 2 and val.type in ["Resistor", "Capacitor", "Inductor"]:
                if deactivate_only:
                    val.is_enabled = False
                    val.model_type = "RLC"
                else:
                    val.edbcomponent.delete()
                    deleted_comps.append(comp)
        if not deactivate_only:
            self.refresh_components()
        self._pedb.logger.info("Deleted {} components".format(len(deleted_comps)))
        return deleted_comps

    def delete(self, component_name):
        """Delete a component.

        Parameters
        ----------
        component_name : str
            Name of the component.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.components.delete("A1")

        """
        edb_cmp = self.get_component_by_name(component_name)
        if edb_cmp is not None:
            edb_cmp.delete()
            if edb_cmp in list(self.instances.keys()):
                del self.instances[edb_cmp]
            return True
        return False

    def disable_rlc_component(self, component_name):
        """Disable a RLC component.

        Parameters
        ----------
        component_name : str
            Name of the RLC component.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.components.disable_rlc_component("A1")

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
        component="",
        sball_diam=None,
        sball_height=None,
        shape="Cylinder",
        sball_mid_diam=None,
        chip_orientation="chip_down",
        auto_reference_size=True,
        reference_size_x=0,
        reference_size_y=0,
        reference_height=0,
    ):
        """Set cylindrical solder balls on a given component.

        Parameters
        ----------
        component : str or EDB component, optional
            Name of the discrete component.
        sball_diam  : str, float, optional
            Diameter of the solder ball.
        sball_height : str, float, optional
            Height of the solder ball.
        shape : str, optional
            Shape of solder ball. Options are ``"Cylinder"``,
            ``"Spheroid"``. The default is ``"Cylinder"``.
        sball_mid_diam : str, float, optional
            Mid diameter of the solder ball.
        chip_orientation : str, optional
            Give the chip orientation, ``"chip_down"`` or ``"chip_up"``. Default is ``"chip_down"``. Only applicable on
            IC model.
        auto_reference_size : bool, optional
            Whether to automatically set reference size.
        reference_size_x : int, str, float, optional
            X size of the reference. Applicable when auto_reference_size is False.
        reference_size_y : int, str, float, optional
            Y size of the reference. Applicable when auto_reference_size is False.
        reference_height : int, str, float, optional
            Height of the reference. Applicable when auto_reference_size is False.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.components.set_solder_ball("A1")

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
            _sb_diam = min([abs(GrpcValue(val).value) for val in pad_params[1]])
            sball_diam = 0.8 * _sb_diam
        if sball_height:
            sball_height = round(GrpcValue(sball_height).value, 9)
        else:
            sball_height = round(GrpcValue(sball_diam).value, 9) / 2

        if not sball_mid_diam:
            sball_mid_diam = sball_diam

        if shape.lower() == "cylinder":
            sball_shape = GrpcSolderballShape.SOLDERBALL_CYLINDER
        else:
            sball_shape = GrpcSolderballShape.SOLDERBALL_SPHEROID

        cmp_property = cmp.component_property
        if cmp.type == GrpcComponentType.IC:
            ic_die_prop = cmp_property.die_property
            ic_die_prop.die_type = GrpcDieType.FLIPCHIP
            if chip_orientation.lower() == "chip_up":
                ic_die_prop.orientation = GrpDieOrientation.CHIP_UP
            else:
                ic_die_prop.orientation = GrpDieOrientation.CHIP_DOWN
            cmp_property.die_property = ic_die_prop

        solder_ball_prop = cmp_property.solder_ball_property
        solder_ball_prop.set_diameter(GrpcValue(sball_diam), GrpcValue(sball_mid_diam))
        solder_ball_prop.height = GrpcValue(sball_height)

        solder_ball_prop.shape = sball_shape
        cmp_property.solder_ball_property = solder_ball_prop

        port_prop = cmp_property.port_property
        port_prop.reference_height = GrpcValue(reference_height)
        port_prop.reference_size_auto = auto_reference_size
        if not auto_reference_size:
            port_prop.set_reference_size(GrpcValue(reference_size_x), GrpcValue(reference_size_y))
        cmp_property.port_property = port_prop
        cmp.component_property = cmp_property
        return True

    def set_component_rlc(
        self,
        componentname,
        res_value=None,
        ind_value=None,
        cap_value=None,
        isparallel=False,
    ):
        """Update values for an RLC component.

        Parameters
        ----------
        componentname :
            Name of the RLC component.
        res_value : float, optional
            Resistance value. The default is ``None``.
        ind_value : float, optional
            Inductor value.  The default is ``None``.
        cap_value : float optional
            Capacitor value.  The default is ``None``.
        isparallel : bool, optional
            Whether the RLC component is parallel. The default is ``False``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.components.set_component_rlc(
        ...     "R1", res_value=50, ind_value=1e-9, cap_value=1e-12, isparallel=False
        ... )

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
                rlc.r = GrpcValue(res_value)
            else:
                rlc.r_enabled = False
            if ind_value is not None:
                rlc.l_enabled = True
                rlc.l = GrpcValue(ind_value)
            else:
                rlc.l_enabled = False
            if cap_value is not None:
                rlc.c_enabled = True
                rlc.c = GrpcValue(cap_value)
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
        bom_file,
        delimiter=";",
        valuefield="Func des",
        comptype="Prod name",
        refdes="Pos / Place",
    ):
        """Update the EDC core component values (RLCs) with values coming from a BOM file.

        Parameters
        ----------
        bom_file : str
            Full path to the BOM file, which is a delimited text file.
            Header values needed inside the BOM reader must
            be explicitly set if different from the defaults.
        delimiter : str, optional
            Value to use for the delimiter. The default is ``";"``.
        valuefield : str, optional
            Field header containing the value of the component. The default is ``"Func des"``.
            The value for this parameter must being with the value of the component
            followed by a space and then the rest of the value. For example, ``"22pF"``.
        comptype : str, optional
            Field header containing the type of component. The default is ``"Prod name"``. For
            example, you might enter ``"Inductor"``.
        refdes : str, optional
            Field header containing the reference designator of the component. The default is
            ``"Pos / Place"``. For example, you might enter ``"C100"``.

        Returns
        -------
        bool
            ``True`` if the file contains the header and it is correctly parsed. ``True`` is
            returned even if no values are assigned.

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
        bom_file,
        delimiter=",",
        refdes_col=0,
        part_name_col=1,
        comp_type_col=2,
        value_col=3,
    ):
        """Load external BOM file.

        Parameters
        ----------
        bom_file : str
            Full path to the BOM file, which is a delimited text file.
        delimiter : str, optional
            Value to use for the delimiter. The default is ``","``.
        refdes_col : int, optional
            Column index of reference designator. The default is ``"0"``.
        part_name_col : int, optional
             Column index of part name. The default is ``"1"``. Set to ``None`` if
             the column does not exist.
        comp_type_col : int, optional
            Column index of component type. The default is ``"2"``.
        value_col : int, optional
            Column index of value. The default is ``"3"``. Set to ``None``
            if the column does not exist.

        Returns
        -------
        bool
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
                        pinlist = self._pedb.padstacks.get_instances(refdes)
                        if not part_name in self.definitions:
                            comp_def = ComponentDef.create(self._db, part_name, None)
                            # for pin in range(len(pinlist)):
                            #     ComponentPin.create(comp_def, str(pin))

                        p_layer = comp.placement_layer
                        refdes_temp = comp.refdes + "_temp"
                        comp.refdes = refdes_temp

                        unmount_comp_list.remove(refdes)
                        comp.ungroup(True)
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

    def export_bom(self, bom_file, delimiter=","):
        """Export Bom file from layout.

        Parameters
        ----------
        bom_file : str
            Full path to the BOM file, which is a delimited text file.
        delimiter : str, optional
            Value to use for the delimiter. The default is ``","``.
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

    def find_by_reference_designator(self, reference_designator):
        """Find a component.

        Parameters
        ----------
        reference_designator : str
            Reference designator of the component.
        """
        return self.instances[reference_designator]

    def get_aedt_pin_name(self, pin):
        """Retrieve the pin name that is shown in AEDT.

        .. note::
           To obtain the EDB core pin name, use `pin.GetName()`.

        Parameters
        ----------
        pin : str
            Name of the pin in EDB core.

        Returns
        -------
        str
            Name of the pin in AEDT.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edbapp.components.get_aedt_pin_name(pin)

        """
        return pin.aedt_name

    def get_pins(self, reference_designator, net_name=None, pin_name=None):
        """Get component pins.

        Parameters
        ----------
        reference_designator : str
            Reference designator of the component.
        net_name : str, optional
            Name of the net.
        pin_name : str, optional
            Name of the pin.

        Returns
        -------

        """
        comp = self.find_by_reference_designator(reference_designator)

        pins = comp.pins
        if net_name:
            pins = {i: j for i, j in pins.items() if j.net_name == net_name}

        if pin_name:
            pins = {i: j for i, j in pins.items() if i == pin_name}

        return pins

    def get_pin_position(self, pin):
        """Retrieve the pin position in meters.

        Parameters
        ----------
        pin : str
            Name of the pin.

        Returns
        -------
        list
            Pin position as a list of float values in the form ``[x, y]``.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edbapp.components.get_pin_position(pin)

        """

        pt_pos = pin.position
        if pin.component.is_null:
            transformed_pt_pos = pt_pos
        else:
            transformed_pt_pos = pin.component.transform.transform_point(pt_pos)
        return [transformed_pt_pos[0].value, transformed_pt_pos[1].value]

    def get_pins_name_from_net(self, net_name, pin_list=None):
        """Retrieve pins belonging to a net.

        Parameters
        ----------
        pin_list : list of EDBPadstackInstance, optional
            List of pins to check. The default is ``None``, in which case all pins are checked
        net_name : str
            Name of the net.

        Returns
        -------
        list of str names:
            Pins belonging to the net.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edbapp.components.get_pins_name_from_net(pin_list, net_name)

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

    def get_nets_from_pin_list(self, pins):
        """Retrieve nets with one or more pins.

        Parameters
        ----------
        PinList : list
            List of pins.

        Returns
        -------
        list
            List of nets with one or more pins.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edbapp.components.get_nets_from_pin_list(pins)

        """
        return list(set([pin.net.name for pin in pins]))

    def get_component_net_connection_info(self, refdes):
        """Retrieve net connection information.

        Parameters
        ----------
        refdes :
            Reference designator for the net.

        Returns
        -------
        dict
            Dictionary of the net connection information for the reference designator.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edbapp.components.get_component_net_connection_info(refdes)

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

    def get_rats(self):
        """Retrieve a list of dictionaries of the reference designator, pin names, and net names.

        Returns
        -------
        list
            List of dictionaries of the reference designator, pin names,
            and net names.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edbapp.components.get_rats()

        """
        df_list = []
        for refdes in self.instances.keys():
            df = self.get_component_net_connection_info(refdes)
            df_list.append(df)
        return df_list

    def get_through_resistor_list(self, threshold=1):
        """Retrieve through resistors.

        Parameters
        ----------
        threshold : int, optional
            Threshold value. The default is ``1``.

        Returns
        -------
        list
            List of through resistors.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edbapp.components.get_through_resistor_list()

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

    def short_component_pins(self, component_name, pins_to_short=None, width=1e-3):
        """Short pins of component with a trace.

        Parameters
        ----------
        component_name : str
            Name of the component.
        pins_to_short : list, optional
            List of pins to short. If `None`, all pins will be shorted.
        width : float, optional
            Short Trace width. It will be used in trace computation algorithm

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder")
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
                lower = [bbox[0].x.value, bbox[0].y.value]
                upper = [bbox[1].x.value, bbox[1].y.value]
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

    def create_pin_group(self, reference_designator, pin_numbers, group_name=None):
        """Create pin group on the component.

        Parameters
        ----------
        reference_designator : str
            References designator of the component.
        pin_numbers : int, str, list[str] or list[:class: `PadstackInstance]`
            List of pins.
        group_name : str, optional
            Name of the pin group.

        Returns
        -------
        PinGroup
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

    def create_pin_group_on_net(self, reference_designator, net_name, group_name=None):
        """Create pin group on component by net name.

        Parameters
        ----------
        reference_designator : str
            References designator of the component.
        net_name : str
            Name of the net.
        group_name : str, optional
            Name of the pin group. The default value is ``None``.

        Returns
        -------
        PinGroup
        """
        pins = [
            pin.name for pin in list(self.instances[reference_designator].pins.values()) if pin.net_name == net_name
        ]
        return self.create_pin_group(reference_designator, pins, group_name)
