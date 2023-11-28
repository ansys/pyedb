"""This module contains the `Components` class.

"""
import codecs
import json
import math
import re
import warnings
import ansys.edb.definition as definition
import ansys.edb.geometry as geometry
import ansys.edb.hierarchy as hierarchy
import ansys.edb.layer as layer
import ansys.edb.terminal as terminal
import ansys.edb.utility as utility
import ansys.edb.database as database

from pyedb.grpc.edb_core.edb_data.components_data import EDBComponent
from pyedb.grpc.edb_core.edb_data.components_data import EDBComponentDef
from pyedb.grpc.edb_core.edb_data.padstacks_data import EDBPadstackInstance
from pyedb.grpc.edb_core.edb_data.sources import Source
from pyedb.grpc.edb_core.edb_data.sources import SourceType
from pyedb.grpc.padstack import EdbPadstacks
from pyedb.generic.general_methods import get_filename_without_extension
from pyedb.generic.general_methods import pyedb_function_handler
from pyedb.modeler.geometry_operators import GeometryOperators


def resistor_value_parser(RValue):
    """Convert a resistor value.

    Parameters
    ----------
    RValue : float
        Resistor value.

    Returns
    -------
    float
        Resistor value.

    """
    if isinstance(RValue, str):
        RValue = RValue.replace(" ", "")
        RValue = RValue.replace("meg", "m")
        RValue = RValue.replace("Ohm", "")
        RValue = RValue.replace("ohm", "")
        RValue = RValue.replace("k", "e3")
        RValue = RValue.replace("m", "e-3")
        RValue = RValue.replace("M", "e6")
    RValue = float(RValue)
    return RValue


class Components(object):
    """Manages EDB components and related method accessible from `Edb.components` property.

    Parameters
    ----------
    edb_class : :class:`pyaedt.edb.Edb`

    Examples
    --------
    >>> from pyedb.grpc.edb import Edb
    >>> edbapp = Edb("myaedbfolder")
    >>> edbapp.components
    """

    @pyedb_function_handler()
    def __getitem__(self, name):
        """Get  a component or component definition from the Edb project.

        Parameters
        ----------
        name : str

        Returns
        -------
        :class:`pyaedt.edb_core.edb_data.components_data.EDBComponent`

        """
        if name in self.instances:
            return self.instances[name]
        elif name in self.definitions:
            return self.definitions[name]
        self._pedb.logger.error("Component or definition not found.")
        return

    def __init__(self, p_edb):
        self._pedb = p_edb
        self._cmp = {}
        self._res = {}
        self._cap = {}
        self._ind = {}
        self._ios = {}
        self._ics = {}
        self._others = {}
        self._pins = {}
        self._comps_by_part = {}
        self._init_parts()
        self._padstack = EdbPadstacks(self._pedb)

    @property
    def _logger(self):
        """Logger."""
        return self._pedb.logger

    @property
    def _edb(self):
        return self._pedb

    @pyedb_function_handler()
    def _init_parts(self):
        a = self.instances
        a = self.resistors
        a = self.ICs
        a = self.Others
        a = self.inductors
        a = self.IOs
        a = self.components_by_partname
        return True

    @property
    def _layout(self):
        return self._pedb.active_cell.layout

    @property
    def _cell(self):
        return self._pedb.active_cell

    @property
    def _db(self):
        return self._pedb.active_db

    @property
    def instances(self):
        """All Cell components objects.

        Returns
        -------
        Dict[str, :class:`pyaedt.edb_core.edb_data.components_data.EDBComponent`]
            Default dictionary for the EDB component.

        Examples
        --------

        >>> from pyedb.grpc.edb import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.components.components

        """
        if not self._cmp:
            self.refresh_components()
        return self._cmp

    @property
    def definitions(self):
        """Retrieve component definition list.

        Returns
        -------
        dict of :class:`pyaedt.edb_core.edb_data.components_data.EDBComponentDef`"""
        return {l.GetName(): EDBComponentDef(self._pedb, l) for l in list(self._pedb.component_defs)}

    @property
    def nport_comp_definition(self):
        """Retrieve Nport component definition list."""
        m = "Ansys.Ansoft.Edb.Definition.NPortComponentModel"
        return {name: l for name, l in self.definitions.items() if m in [str(i) for i in l._comp_model]}

    @pyedb_function_handler()
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

    @pyedb_function_handler()
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

    @pyedb_function_handler()
    def refresh_components(self):
        """Refresh the component dictionary."""
        # self._logger.info("Refreshing the Components dictionary.")
        self._cmp = {l.name: EDBComponent(self._pedb, l) for l in self._layout.groups}
        return True

    @property
    def resistors(self):
        """Resistors.

        Returns
        -------
        dict[str, :class:`pyaedt.edb_core.edb_data.components_data.EDBComponent`]
            Dictionary of resistors.

        Examples
        --------

        >>> from src.pyedb.grpc.edb import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.components.resistors
        """
        self._res = {}
        for el, val in self.instances.items():
            if val.type == "Resistor":
                self._res[el] = val
        return self._res

    @property
    def capacitors(self):
        """Capacitors.

        Returns
        -------
        dict[str, :class:`pyaedt.edb_core.edb_data.components_data.EDBComponent`]
            Dictionary of capacitors.

        Examples
        --------

        >>> from pyedb.grpc.edb import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.components.capacitors
        """
        self._cap = {}
        for el, val in self.instances.items():
            if val.type == "Capacitor":
                self._cap[el] = val
        return self._cap

    @property
    def inductors(self):
        """Inductors.

        Returns
        -------
        dict[str, :class:`pyaedt.edb_core.edb_data.components_data.EDBComponent`]
            Dictionary of inductors.

        Examples
        --------

        >>> from pyedb.grpc.edb import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.components.inductors

        """
        self._ind = {}
        for el, val in self.instances.items():
            if val.type == "Inductor":
                self._ind[el] = val
        return self._ind

    @property
    def ICs(self):
        """Integrated circuits.

        Returns
        -------
        dict[str, :class:`pyaedt.edb_core.edb_data.components_data.EDBComponent`]
            Dictionary of integrated circuits.

        Examples
        --------

        >>> from pyedb.grpc.edb import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.components.ICs

        """
        self._ics = {}
        for el, val in self.instances.items():
            if val.type == "IC":
                self._ics[el] = val
        return self._ics

    @property
    def IOs(self):
        """Circuit inupts and outputs.

        Returns
        -------
        dict[str, :class:`pyaedt.edb_core.edb_data.components_data.EDBComponent`]
            Dictionary of circuit inputs and outputs.

        Examples
        --------

        >>> from pyedb.grpc.edb import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.components.IOs

        """
        self._ios = {}
        for el, val in self.instances.items():
            if val.type == "IO":
                self._ios[el] = val
        return self._ios

    @property
    def Others(self):
        """Other core components.

        Returns
        -------
        dict[str, :class:`pyaedt.edb_core.edb_data.components_data.EDBComponent`]
            Dictionary of other core components.

        Examples
        --------

        >>> from pyedb.grpc.edb import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.components.others

        """
        self._others = {}
        for el, val in self.instances.items():
            if val.type == "Other":
                self._others[el] = val
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

        >>> from src.pyedb.grpc.edb import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.components.components_by_partname

        """
        self._comps_by_part = {}
        for el, val in self.instances.items():
            if val.part_name in self._comps_by_part.keys():
                self._comps_by_part[val.part_name].append(val)
            else:
                self._comps_by_part[val.part_name] = [val]
        return self._comps_by_part

    @pyedb_function_handler()
    def get_component_by_name(self, name):
        """Retrieve a component by name.

        Parameters
        ----------
        name : str
            Name of the component.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        edbcmp = hierarchy.ComponentGroup.find(self._edb.layout, name)
        if edbcmp:
            return edbcmp
        else:
            pass

    @pyedb_function_handler()
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

    @pyedb_function_handler()
    def _get_edb_pin_from_pin_name(self, cmp, pin):
        if not isinstance(cmp, self._pedb.cell.hierarchy.group):
            return False
        if not isinstance(pin, str):
            pin = pin.name
        pins = self.get_pin_from_component(component=cmp, pinName=pin)
        if pins:
            return pins[0]
        return False

    @pyedb_function_handler()
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
        if not isinstance(mounted_component, self._pedb.cell.hierarchy.component):
            return False
        if not isinstance(hosting_component, self._pedb.cell.hierarchy.component):
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
            layinst = mounted_component.layout.layout_instance
            cmpinst = layinst.layout_obj_instance(mounted_component, None)
            center = cmpinst.center
            center_double = [center.x.value, center.y.value]
            vector_center = GeometryOperators.v_points(center_double, m_pin1_pos)
            x_v2 = vector_center[0] * math.cos(rotation) + multiplier * vector_center[1] * math.sin(rotation)
            y_v2 = -1 * vector_center[0] * math.sin(rotation) + multiplier * vector_center[1] * math.cos(rotation)
            new_vector = [x_v2 + center_double[0], y_v2 + center_double[1]]
            vector = [h_pin1_pos[0] - new_vector[0], h_pin1_pos[1] - new_vector[1]]

        if vector:
            solder_ball_height = self.get_solder_ball_height(mounted_component)
            return True, vector, rotation, solder_ball_height
        self._logger.warning("Failed to compute vector.")
        return False, [0, 0], 0, 0

    @pyedb_function_handler()
    def get_solder_ball_height(self, cmp):
        """Get component solder ball height.

        Parameters
        ----------
        cmp : str or  self._pedb.component
            EDB component or str component name.

        Returns
        -------
        double, bool
            Salder ball height vale, ``False`` when failed.

        """
        if cmp is not None:
            if not (isinstance(cmp, hierarchy.group.Group)):
                cmp = self.get_component_by_name(cmp)
            return cmp.property.solder_ball_property.height
        return False

    @pyedb_function_handler()
    def create_source_on_component(self, sources=None):
        """Create voltage, current source, or resistor on component.

        Parameters
        ----------
        sources : list[Source]
            List of ``edb_data.sources.Source`` objects.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """

        if not sources:  # pragma: no cover
            return False
        if isinstance(sources, Source):  # pragma: no cover
            sources = [sources]
        if isinstance(sources, list):  # pragma: no cover
            for src in sources:
                if not isinstance(src, Source):  # pragma: no cover
                    self._logger.error("List of source objects must be passed as an argument.")
                    return False
        for source in sources:
            positive_pins = self.get_pin_from_component(source.positive_node.component, source.positive_node.net)
            negative_pins = self.get_pin_from_component(source.negative_node.component, source.negative_node.net)
            positive_pin_group = self.create_pingroup_from_pins(positive_pins)
            if not positive_pin_group:  # pragma: no cover
                return False
            negative_pin_group = self.create_pingroup_from_pins(negative_pins)
            if not negative_pin_group:  # pragma: no cover
                return False
            if source.source_type == SourceType.Vsource:  # pragma: no cover
                positive_pin_group_term = self._create_pin_group_terminal(
                    positive_pin_group,
                )
                negative_pin_group_term = self._create_pin_group_terminal(negative_pin_group, isref=True)
                positive_pin_group_term.boundary_type(terminal.BoundaryType.VOLTAGE_SOURCE)
                negative_pin_group_term.SetBoundaryType(terminal.BoundaryType.VOLTAGE_SOURCE)
                term_name = source.name
                positive_pin_group_term.name = term_name
                negative_pin_group_term.name = "{}_ref".format(term_name)
                positive_pin_group_term.source_amplitude = utility.Value(source.amplitude)
                negative_pin_group_term.source_amplitude = utility.Value(source.amplitude)
                positive_pin_group_term.source_phase = utility.Value(source.phase)
                negative_pin_group_term.source_phase = utility.Value(source.phase)
                positive_pin_group_term.impedance = utility.Value(source.impedance)
                negative_pin_group_term.impedance = utility.Value(source.impedance)
                positive_pin_group_term.reference_Terminal = negative_pin_group_term
            elif source.source_type == SourceType.Isource:  # pragma: no cover
                positive_pin_group_term = self._create_pin_group_terminal(
                    positive_pin_group,
                )
                negative_pin_group_term = self._create_pin_group_terminal(negative_pin_group, isref=True)
                positive_pin_group_term.BoundaryType = terminal.BoundaryType.CURRENT_SOURCE
                negative_pin_group_term.BoundaryType = terminal.BoundaryType.CURRENT_SOURCE
                term_name = source.name
                positive_pin_group_term.name = term_name
                negative_pin_group_term.name = "{}_ref".format(term_name)
                positive_pin_group_term.source_amplitude = utility.Value(source.amplitude)
                negative_pin_group_term.source_amplitude = utility.Value(source.amplitude)
                positive_pin_group_term.source_phase = utility.Value(source.phase)
                negative_pin_group_term.source_phase = utility.Value(source.phase)
                positive_pin_group_term.impedance = utility.Value(source.impedance)
                negative_pin_group_term.impedance = utility.Value(source.impedance)
                positive_pin_group_term.reference_terminal = negative_pin_group_term
            elif source.source_type == SourceType.Rlc:  # pragma: no cover
                self.create(
                    pins=[positive_pins[0], negative_pins[0]],
                    component_name=source.name,
                    is_rlc=True,
                    r_value=source.r_value,
                    l_value=source.l_value,
                    c_value=source.c_value,
                )
        return True

    @pyedb_function_handler()
    def create_port_on_pins(self, refdes, pins, reference_pins, impedance=50.0):
        """Create circuit port between pins and reference ones.

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

        Returns
        -------
        EDB terminal created, or False if failed to create.

        Example:
        >>> from pyedb.grpc.edb import Edb
        >>> edb = Edb(path_to_edb_file)
        >>> pin = "AJ6"
        >>> ref_pins = ["AM7", "AM4"]
        Or to take all reference pins
        >>> ref_pins = [pin for pin in list(edb.components["U2A5"].pins.values()) if pin.net_name == "GND"]
        >>> edb.components.create_port_on_pins(refdes="U2A5", pins=pin, reference_pins=ref_pins)
        >>> edb.save_edb()
        >>> edb.close_edb()
        """

        if isinstance(pins, str) or isinstance(pins, EDBPadstackInstance):
            pins = [pins]
        if isinstance(reference_pins, str):
            reference_pins = [reference_pins]
        if isinstance(refdes, str) or isinstance(refdes, EDBComponent):
            refdes = self.instances[refdes]
        if len([pin for pin in pins if isinstance(pin, str)]) == len(pins):
            cmp_pins = []
            for pin_name in pins:
                cmp_pin = [pin for pin in list(refdes.pins.values()) if pin_name in pin.name]
                if cmp_pin:
                    cmp_pins.append(cmp_pin[0])
            if not cmp_pins:
                return
            pins = cmp_pins
        if not len([pin for pin in pins if isinstance(pin, EDBPadstackInstance)]) == len(pins):
            self._logger.error("Pin list must contain only pins instances")
            return
        if len([pin for pin in reference_pins if isinstance(pin, str)]) == len(reference_pins):
            ref_cmp_pins = []
            for ref_pin_name in reference_pins:
                cmp_ref_pin = [pin for pin in list(refdes.pins.values()) if ref_pin_name in pin.name]
                if cmp_ref_pin:
                    ref_cmp_pins.append(cmp_ref_pin[0])
            if not ref_cmp_pins:
                return
            reference_pins = ref_cmp_pins
        if not len([pin for pin in reference_pins if isinstance(pin, EDBPadstackInstance)]) == len(reference_pins):
            return
        if len(pins) > 1:
            group_name = "group_{}_{}".format(pins[0].net_name, pins[0].name)
            pin_group = self.create_pingroup_from_pins(pins, group_name)
            term = self._create_pin_group_terminal(pingroup=pin_group)

        else:
            term = self._create_terminal(pins[0])
        term.is_circuit_port = True
        if len(reference_pins) > 1:
            ref_group_name = "group_{}_{}_ref".format(reference_pins[0].net_name, reference_pins[0].name)
            ref_pin_group = self.create_pingroup_from_pins(reference_pins, ref_group_name)
            ref_term = self._create_pin_group_terminal(pingroup=ref_pin_group)
        else:
            ref_term = self._create_terminal(reference_pins[0])
        ref_term.is_circuit_port = True
        term.impedance = utility.Value(impedance)
        term.reference_terminal = ref_term
        if term:
            return term
        return False

    @pyedb_function_handler()
    def create_port_on_component(
            self, component, net_list, port_type=SourceType.CoaxPort, do_pingroup=True, reference_net="gnd",
            port_name=None
    ):
        """Create ports on a component.

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
            True activate pingroup during port creation (only used with combination of CoaxPort),
            False will take the closest reference pin and generate one port per signal pin.
        refnet : string or list of string.
            list of the reference net.
        port_name : string
            Port name for overwriting the default port-naming convention,
            which is ``[component][net][pin]``. The port name must be unique.
            If a port with the specified name already exists, the
            default naming convention is used so that port creation does
            not fail.

        Returns
        -------
        double, bool
            Salder ball height vale, ``False`` when failed.

        Examples
        --------

        >>> from pyedb.grpc.edb import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> net_list = ["M_DQ<1>", "M_DQ<2>", "M_DQ<3>", "M_DQ<4>", "M_DQ<5>"]
        >>> edbapp.components.create_port_on_component(cmp="U2A5", net_list=net_list,
        >>> port_type=SourceType.CoaxPort, do_pingroup=False, refnet="GND")

        """
        if isinstance(component, str):
            component = self.instances[component].edbcomponent
        if not isinstance(net_list, list):
            net_list = [net_list]
        for net in net_list:
            if not isinstance(net, str):
                try:
                    net_name = net.name
                    if net_name != "":
                        net_list.append(net_name)
                except:
                    pass
        if reference_net in net_list:
            net_list.remove(reference_net)
        cmp_pins = [
            p for p in list(component.members) if not p.net.is_null and p.layout_obj_type.value == 1
                                                  and p.net.name in net_list]
        for p in cmp_pins:  # pragma no cover
            if not p.is_layout_pin:
                p.is_layout_pin = True
        if len(cmp_pins) == 0:
            self._logger.info(
                "No pins found on component {}, searching padstack instances instead".format(component.name)
            )
            return False
        pin_layers = cmp_pins[0].padstack_def.data.layer_names
        if port_type == SourceType.CoaxPort:
            pad_params = self._padstack.get_pad_parameters(pin=cmp_pins[0], layername=pin_layers[0], pad_type=0)
            if isinstance(pad_params[0], definition.PadGeometryType):
               sball_diam = min([utility.Value(val).value for val in pad_params[1]])
               solder_ball_height = 2 * sball_diam / 3
            elif isinstance(pad_params[0], geometry.PolygonData):
                bbox = pad_params[0].bbox()
                sball_diam = min([abs(bbox[1].x - bbox[0].x), abs(bbox[3] - bbox[1])]) * 0.8
                solder_ball_height = 2 * sball_diam / 3
            self.set_solder_ball(component, solder_ball_height, sball_diam)
            for pin in cmp_pins:
                self._padstack.create_coax_port(padstackinstance=pin, name=port_name)

        elif port_type == SourceType.CircPort:  # pragma no cover
            ref_pins = [
            p for p in list(component.members) if not p.net.is_null and p.layout_obj_type.value == 1
                                                  and p.net.name in reference_net]
            for p in ref_pins:
                if not p.is_layout_pin:
                    p.is_layout_pin = True
            if len(ref_pins) == 0:
                self._logger.info("No reference pin found on component {}.".format(component.GetName()))
            if do_pingroup:
                if len(ref_pins) == 1:
                    ref_pin_group_term = self._create_terminal(ref_pins[0])
                else:
                    ref_pin_group = self.create_pingroup_from_pins(ref_pins)
                    if not ref_pin_group or ref_pin_group.is_null:
                        return False
                    ref_pin_group_term = self._create_pin_group_terminal(ref_pin_group, isref=True)
                    if not ref_pin_group_term:
                        return False
                for net in net_list:
                    pins = [pin for pin in cmp_pins if pin.net.name == net]
                    if pins:
                        if len(pins) == 1:
                            pin_term = self._create_terminal(pins[0])
                            if pin_term:
                                pin_term.reference_terminal = ref_pin_group_term
                        else:
                            pin_group = self.create_pingroup_from_pins(pins)
                            if not pin_group or pin_group.is_null:
                                return False
                            pin_group_term = self._create_pin_group_terminal(pin_group)
                            if pin_group_term:
                                pin_group_term.reference_terminal = ref_pin_group_term
                    else:
                        self._logger.info("No pins found on component {} for the net {}".format(component, net))
            else:
                ref_pin_group = self.create_pingroup_from_pins(ref_pins)
                if not ref_pin_group:
                    self._logger.warning("failed to create reference pin group")
                    return False
                ref_pin_group_term = self._create_pin_group_terminal(ref_pin_group, isref=True)
                for net in net_list:
                    pins = [pin for pin in cmp_pins if pin.net.name == net]
                    for pin in pins:
                        pin_group = self.create_pingroup_from_pins([pin])
                        pin_group_term = self._create_pin_group_terminal(pin_group, isref=False)
                        pin_group_term.SetReferenceTerminal(ref_pin_group_term)
        return True

    @pyedb_function_handler()
    def _create_terminal(self, pin):
        """Create terminal on component pin.

        Parameters
        ----------
        pin : Edb padstack instance.

        Returns
        -------
        Edb terminal.
        """

        pin_position = self.get_pin_position(pin)  # pragma no cover
        pin_pos = self._pedb.point_data(*pin_position)
        res, from_layer, _ = pin.layer_range
        cmp_name = pin.component.name
        net_name = pin.net.name
        pin_name = pin.name
        term_name = "{}.{}.{}".format(cmp_name, pin_name, net_name)
        for term in list(self._pedb.active_layout.terminals):
            if term.GetName() == term_name:
                return term
        term = terminal.PointTerminal.create(pin.layout, pin.net, term_name, pin_pos, from_layer)
        return term

    @pyedb_function_handler()
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
        pin_position, pin_rot = pin.position_and_rotation()
        distance = 1e3
        closest_pin = ref_pinlist[0]
        for ref_pin in ref_pinlist:
            res, ref_pin_position, ref_pin_rot = ref_pin.position_and_rotation()
            temp_distance = pin_position.distance(ref_pin_position)
            if temp_distance < distance:
                distance = temp_distance
                closest_pin = ref_pin
        return closest_pin

    @pyedb_function_handler()
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
        >>> from pyedb.grpc.edb import Edb
        >>> edb = Edb(edb_file)
        >>>  for refdes, cmp in edb.components.capacitors.items():
        >>>     edb.components.replace_rlc_by_gap_boundaries(refdes)
        >>> edb.save_edb()
        >>> edb.close_edb()
        """
        if not component:  # pragma no cover
            return False
        if isinstance(component, str):
            component = self.instances[component]
            if not component:  # pragma  no cover
                self._logger.error("component %s not found.", component)
                return False
        component_type = component.edbcomponent.component_type
        if (
                component_type == hierarchy.ComponentType.OTHER
                or component_type == hierarchy.ComponentType.IC
                or component_type == hierarchy.ComponentType.IO
        ):
            self._logger.info("Component %s passed to deactivate is not an RLC.", component.refdes)
            return False
        component.is_enabled = False
        return self.add_rlc_boundary(component.refdes, False)

    @pyedb_function_handler()
    def deactivate_rlc_component(self, component=None, create_circuit_port=False):
        """Deactivate RLC component with a possibility to convert to a circuit port.

        Parameters
        ----------
        component : str
            Reference designator of the RLC component.

        create_circuit_port : bool, optional
            Whether to replace the deactivated RLC component with a circuit port. The default
            is ``False``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from pyedb.grpc.edb import Edb
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
        component_type = component.edbcomponent.component_type
        if (
                component_type == hierarchy.ComponentType.OTHER
                or component_type == hierarchy.ComponentType.IC
                or component_type == hierarchy.ComponentType.IO
        ):
            self._logger.info("Component %s passed to deactivate is not an RLC.", component.refdes)
            return False
        component.is_enabled = False
        return self.add_port_on_rlc_component(component=component.refdes, circuit_ports=create_circuit_port)

    @pyedb_function_handler()
    def add_port_on_rlc_component(self, component=None, circuit_ports=True):
        """Deactivate RLC component and replace it with a circuit port.
        The circuit port supports only 2-pin components.

        Parameters
        ----------
        component : str
            Reference designator of the RLC component.

        circuit_ports : bool
            ``True`` will replace RLC component by circuit ports, ``False`` gap ports compatible with HFSS 3D modeler
            export.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if isinstance(component, str):  # pragma: no cover
            component = self.instances[component]
        if not isinstance(component, EDBComponent):  # pragma: no cover
            return False
        self.set_component_rlc(component.refdes)
        pins = self.get_pin_from_component(component.refdes)
        if len(pins) == 2:  # pragma: no cover
            pos_pin_loc = self.get_pin_position(pins[0])
            pt = self._pedb.point_data(*pos_pin_loc)

            pin_layers = self._padstack._get_pin_layer_range(pins[0])
            pos_pin_term = terminal.PointTerminal.create(self._active_layout, pins[0].GetNet(),
                                                "{}_{}".format(component.refdes, pins[0].GetName()),
                                                pins[0],
                                                pin_layers[0],
                                                False,
                                                )
            if not pos_pin_term:  # pragma: no cover
                return False
            neg_pin_loc = self.get_pin_position(pins[1])
            pt = self._pedb.point_data(*neg_pin_loc)

            neg_pin_term = terminal.PadstackInstanceTerminal.create(
                self._active_layout,
                pins[1].net,
                "{}_{}_ref".format(component.refdes, pins[1].GetName()),
                pins[1],
                pin_layers[0],
                False,
            )
            if not neg_pin_term:  # pragma: no cover
                return False
            pos_pin_term.boundary_type = terminal.BoundaryType.PORT
            pos_pin_term.name = component.refdes
            neg_pin_term.boundary_type = terminal.BoundaryType.PORT
            pos_pin_term.reference_terminal = neg_pin_term
            if circuit_ports:
                pos_pin_term.is_circuit_port = True
                neg_pin_term.is_circuit_port = True
            else:
                pos_pin_term.is_circuit_port = False
                neg_pin_term.is_circuit_port = False
            self._logger.info("Component {} has been replaced by port".format(component.refdes))
            return True
        return False

    @pyedb_function_handler()
    def add_rlc_boundary(self, component=None, circuit_type=True):
        """Add RLC gap boundary on component and replace it with a circuit port.
        The circuit port supports only 2-pin components.

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
        if isinstance(component, str):  # pragma: no cover
            component = self.instances[component]
        if not isinstance(component, EDBComponent):  # pragma: no cover
            return False
        self.set_component_rlc(component.refdes)
        pins = self.get_pin_from_component(component.refdes)
        if len(pins) == 2:  # pragma: no cover
            pin_layer = self._padstack._get_pin_layer_range(pins[0])[0]
            pos_pin_term = terminal.PadstackInstanceTerminal.create(
                self._active_layout,
                pins[0].net,
                "{}_{}".format(component.refdes, pins[0].name),
                pins[0],
                pin_layer,
                False,
            )
            if not pos_pin_term:  # pragma: no cover
                return False
            neg_pin_term = terminal.PadstackInstanceTerminal.create(
                self._active_layout,
                pins[1].net,
                "{}_{}_ref".format(component.refdes, pins[1].name),
                pins[1],
                pin_layer,
                True,
            )
            if not neg_pin_term:  # pragma: no cover
                return False
            pos_pin_term.boundary_type = terminal.BoundaryType.RLC
            if not circuit_type:
                pos_pin_term.is_circuit_port = False
            else:
                pos_pin_term.is_circuit_port = True
            pos_pin_term.name = component.refdes
            neg_pin_term.boundary_type = terminal.BoundaryType.RLC
            if not circuit_type:
                neg_pin_term.is_circuit_port = False
            else:
                neg_pin_term.is_circuit_port = True
            pos_pin_term.reference_terminal = neg_pin_term
            rlc_values = component.rlc_values
            rlc = utility.Rlc()
            if rlc_values[0]:
                rlc.r_enabled = True
                rlc.r = utility.Value(rlc_values[0])
            if rlc_values[1]:
                rlc.l_enabled = True
                rlc.l = utility.Value(rlc_values[1])
            if rlc_values[2]:
                rlc.c_enabled = True
                rlc.c = utility.Value(rlc_values[2])
            rlc.is_parallel = component.is_parallel_rlc
            pos_pin_term.rlc_boundary_parameters = rlc
            self._logger.info("Component {} has been replaced by port".format(component.refdes))
            return True

    @pyedb_function_handler()
    def _create_pin_group_terminal(self, pingroup, isref=False):
        """Creates an EDB pin group terminal from a given EDB pin group.

        Parameters
        ----------
        pingroup : Edb pin group.

        isref : bool

        Returns
        -------
        Edb pin group terminal.
        """
        pin = pingroup.pins[0]
        term_name = "{}.{}.{}".format(pin.component.name, pin.component.name, pin.net.name)
        for t in self._pedb.active_layout.terminals:
            if t.name == term_name:
                return t
        pingroup_term = terminal.PinGroupTerminal.create(layout=self._pedb.active_layout,
                                                         net_ref=pingroup.net,
                                                         name=term_name,
                                                         pin_group=pingroup,
                                                         is_ref=isref)
        return pingroup_term

    @pyedb_function_handler()
    def _is_top_component(self, cmp):
        """Test the component placment layer.

        Parameters
        ----------
        cmp :  self._pedb.component
             Edb component.

        Returns
        -------
        bool
            ``True`` when component placed on top layer, ``False`` on bottom layer.


        """
        signal_layers = cmp.layout.layers(layer.LayerType.SIGNAL_LAYER)
        if cmp.placement_layer == signal_layers[0]:
            return True
        else:
            return False

    @pyedb_function_handler()
    def _get_component_definition(self, name, pins):
        component_definition = definition.ComponentDef.find(self._db, name)
        if component_definition.is_null:
            component_definition = definition.ComponentDef.create(db=self._db, comp_def_name=name, fp=None)
            if component_definition.is_null:
                self._logger.error("Failed to create component definition {}".format(name))
                return None
            ind = 1
            for pin in pins:
                if not pin.name:
                    pin.name = str(ind)
                ind += 1
                component_definition_pin = definition.ComponentPin.create(component_definition, pin.name)
                if component_definition_pin.is_null:
                    self._logger.error("Failed to create component definition pin {}-{}".format(name, pin.name))
                    return None
        else:
            self._logger.warning("Found existing component definition for footprint {}".format(name))
        return component_definition

    @pyedb_function_handler()
    def create_rlc_component(
            self, pins, component_name="", r_value=1.0, c_value=1e-9, l_value=1e-9, is_parallel=False
    ):  # pragma: no cover
        """Create physical Rlc component.

        Parameters
        ----------
        pins : list
             List of EDB pins, length must be 2, since only 2 pins component are currently supported.
             It can be an `pyaedt.edb_core.edb_data.padstacks_data.EDBPadstackInstance` object or
             an Edb Padstack Instance object.
        component_name : str
            Component definition name.
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
        Component
            Created EDB component.

        """
        warnings.warn("`create_rlc_component` is deprecated. Use `create` method instead.", DeprecationWarning)
        return self.create(
            pins=pins,
            component_name=component_name,
            is_rlc=True,
            r_value=r_value,
            l_value=l_value,
            c_value=c_value,
            is_parallel=is_parallel,
        )

    @pyedb_function_handler()
    def create(
            self,
            pins,
            component_name,
            placement_layer=None,
            component_part_name=None,
            is_rlc=False,
            r_value=1.0,
            c_value=1e-9,
            l_value=1e-9,
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

        >>> from pyedb.grpc.edb import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> pins = edbapp.components.get_pin_from_component("A1")
        >>> edbapp.components.create(pins, "A1New")

        """
        if component_part_name:
            compdef = self._get_component_definition(component_part_name, pins)
        else:
            compdef = self._get_component_definition(component_name, pins)
        if not compdef:
            return False
        new_cmp = hierarchy.ComponentGroup.create(self._layout, component_name, compdef.name)

        if isinstance(pins[0], EDBPadstackInstance):
            pins = [i._edb_padstackinstance for i in pins]
        for pin in pins:
            pin.is_layout_pin = True
            new_cmp.add_member(pin)
        new_cmp.component_type = hierarchy.ComponentType.OTHER
        if not placement_layer:
            new_cmp_layer_name = pins[0].padstack_def.data.layer_names[0]
        else:
            new_cmp_layer_name = placement_layer
        new_cmp_placement_layer = self._edb.cell.layer_collection.find_by_name(new_cmp_layer_name)
        new_cmp.placement_layer = new_cmp_placement_layer
        hosting_component_location = pins[0].component.transform

        if is_rlc:
            rlc = utility.Rlc()
            rlc.IsParallel = is_parallel
            if r_value:
                rlc.r_enabled = True
                rlc.r = utility.Value(r_value)
            else:
                rlc.r_enabled = False
            if l_value:
                rlc.l_enabled = True
                rlc.l = utility.Value(l_value)
            else:
                rlc.l_enabled = False
            if c_value:
                rlc.c_enabled = True
                rlc.c = utility.Value(c_value)
            else:
                rlc.c_enabled = False
            if rlc.r_enabled and not rlc.c_enabled and not rlc.l_enabled:
                new_cmp.component_type = hierarchy.ComponentType.RESISTOR
            elif rlc.c_enabled and not rlc.r_enabled and not rlc.l_enabled:
                new_cmp.component_type = hierarchy.ComponentType.CAPACITOR
            elif rlc.l_enabled and not rlc.r_enabled and not rlc.c_enabled:
                new_cmp.component_type = hierarchy.ComponentType.INDUCTOR
            else:
                new_cmp.component_type = hierarchy.ComponentType.RESISTOR

            pin_pair = utility.Rlc(pins[0].name, pins[1].name)
            rlc_model = hierarchy.PinPairModel(pin_pair)
            edb_rlc_component_property = definition.RLCComponentProperty()
            edb_rlc_component_property.model = rlc_model
            new_cmp.component_property = edb_rlc_component_property
        new_cmp.transform = hosting_component_location
        new_edb_comp = EDBComponent(self._pedb, new_cmp)
        self._cmp[new_cmp.name] = new_edb_comp
        return new_edb_comp

    @pyedb_function_handler()
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

        >>> from pyedb.grpc.edb import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.components.set_component_model("A1", model_type="Spice",
        ...                                            modelpath="pathtospfile",
        ...                                            modelname="spicemodelname")

        """
        if not modelname:
            modelname = get_filename_without_extension(modelpath)
        edb_component = self.get_component_by_name(componentname)
        edb_rlc_component_property = edb_component.component_property

        component_pins = self.get_pin_from_component(componentname)
        component_nets = self.get_nets_from_pin_list(component_pins)
        pin_number = len(component_pins)
        if model_type == "Spice":
            with open(modelpath, "r") as f:
                for line in f:
                    if "subckt" in line.lower():
                        pin_names = [i.strip() for i in re.split(" |\t", line) if i]
                        pin_names.remove(pin_names[0])
                        pin_names.remove(pin_names[0])
                        break
            if len(pin_names) == pin_number:
                spice_model = hierarchy.SPICEModel()
                spice_model.model_path = modelpath
                spice_model.model_name = modelname
                terminal = 1
                for pn in pin_names:
                    spice_model.add_terminal(pn, str(terminal))
                    terminal += 1

                edb_rlc_component_property.model = spice_model
                edb_component.component_property = edb_rlc_component_property

            else:
                self._logger.error("Wrong number of Pins")
                return False

        elif model_type == "Touchstone":  # pragma: no cover
            nPortModelName = modelname
            edbComponentDef = edb_component.component_def
            nPortModel = definition.NPortComponentModel.find(edbComponentDef, nPortModelName)  # -> Missing command in pyedb
            if nPortModel.IsNull():
                nPortModel = definition.NPortComponentModel.create(nPortModelName)
                nPortModel.reference_file(modelpath)
                edbComponentDef.component_model = nPortModel

            s_parameter_model = hierarchy.SParameterModel()
            s_parameter_model.component_model = nPortModelName
            gndnets = filter(lambda x: "gnd" in x.lower(), component_nets)
            if len(list(gndnets)) > 0:  # pragma: no cover
                net = gndnets[0]
            else:  # pragma: no cover
                net = component_nets[len(component_nets) - 1]
            s_parameter_model.reference_net = net
            edb_rlc_component_property.model = s_parameter_model
            edb_component.component_property = edb_rlc_component_property
        return True

    @pyedb_function_handler()
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
        >>> from pyedb.grpc.edb import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.components.create_pingroup_from_pins(gndpinlist, "MyGNDPingroup")

        """
        if len(pins) < 1:
            self._logger.error("No pins specified for pin group %s", group_name)
            return (False, None)
        if len([pin for pin in pins if isinstance(pin, EDBPadstackInstance)]):
            _pins = [pin._edb_padstackinstance for pin in pins]
            if _pins:
                pins = _pins
        if not group_name:
            group_name = hierarchy.PinGroup.unique_name(self._edb.layout, "")
        for pin in pins:
            pin.is_layout_pin = True
        forbiden_car = "-><"
        group_name = group_name.translate({ord(i): "_" for i in forbiden_car})
        for pgroup in self._pedb.layout.pin_groups:
            if pgroup.name == group_name:
                pin_group_exists = True
                if len(pgroup.pins) == len(pins):
                    pnames = [i.name for i in pins]
                    for p in pgroup.pins:
                        if p.name in pnames:
                            continue
                        else:
                            group_name = self._edb.cell.hierarchy.pin_group.unique_name(
                                self._edb.layout, group_name
                            )
                            pin_group_exists = False
                else:
                    group_name = hierarchy.PinGroup.unique_name(self._edb.layout, group_name)
                    pin_group_exists = False
                if pin_group_exists:
                    return pgroup
        pingroup = hierarchy.PinGroup.create(self._edb.layout, group_name, pins)
        if pingroup.is_null:
            return False
        else:
            pingroup.net = pins[0].net
            return pingroup

    @pyedb_function_handler()
    def delete_single_pin_rlc(self, deactivate_only=False):
        # type: (bool) -> list
        """Delete all RLC components with a single pin.

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

        >>> from pyedb.grpc.edb import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> list_of_deleted_rlcs = edbapp.components.delete_single_pin_rlc()
        >>> print(list_of_deleted_rlcs)

        """
        deleted_comps = []
        for comp, val in self.instances.items():
            if val.numpins < 2 and val.type in ["Resistor", "Capacitor", "Inductor"]:
                if deactivate_only:
                    val.is_enabled = False
                else:
                    val.edbcomponent.delete()
                    deleted_comps.append(comp)
        if not deactivate_only:
            self.refresh_components()
        self._pedb._logger.info("Deleted {} components".format(len(deleted_comps)))

        return deleted_comps

    @pyedb_function_handler()
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

        >>> from pyedb.grpc.edb import Edb
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

    @pyedb_function_handler()
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

        >>> from pyedb.grpc.edb import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.components.disable_rlc_component("A1")

        """
        edb_cmp = self.get_component_by_name(component_name)  # not correct need to be checked in debug
        if edb_cmp is not None:
            rlc_property = edb_cmp.component_property
            pin_pair_model = rlc_property.model
            pprlc = utility.Rlc(list(pin_pair_model.pin_pairs)[0])
            pprlc.c_enabled = False
            pprlc.l_enabled = False
            pprlc.r_enabled = False
            pin_pair_model.rlc = pin_pair_model.pin_pairs
            rlc_property.model = pin_pair_model
            edb_cmp.component_property = rlc_property
            return True
        return False

    @pyedb_function_handler()
    def set_solder_ball(
            self,
            component="",
            sball_diam="100um",
            sball_height="150um",
            shape="Cylinder",
            sball_mid_diam=None,
            chip_orientation="chip_down",
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

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------

        >>> from pyedb.grpc.edb import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.components.set_solder_ball("A1")

        """
        if not isinstance(component, hierarchy.ComponentGroup):
            edb_cmp = self.get_component_by_name(component)
            cmp = self.instances[component]
        else:
            edb_cmp = component
            cmp = self.instances[edb_cmp.name]
        if edb_cmp:
            cmp_type = edb_cmp.component_type
            if not sball_diam:
                pin1 = list(cmp.pins.values())[0].pin
                pin_layers = pin1.padstack_def.data.layer_names
                pad_params = self._padstack.get_pad_parameters(pin=pin1, layername=pin_layers[0], pad_type=0)
                _sb_diam = min([utility.Value(val).value for val in pad_params[1]])
                sball_diam = _sb_diam
            if not sball_height:
                sball_height = 2 * round(utility.Value(sball_diam).value, 9) / 3
            if not sball_mid_diam:
                sball_mid_diam = sball_diam

            if shape == "Cylinder":
                sball_shape = definition.SolderballShape.SOLDERBALL_CYLINDER
            else:
                sball_shape = definition.SolderballShape.SOLDERBALL_SPHEROID

            cmp_property = edb_cmp.component_property
            if cmp_type == hierarchy.ComponentType.IC:
                ic_die_prop = cmp_property.die_property.clone()
                ic_die_prop.type = definition.DieType.FLIPCHIP
                if chip_orientation.lower() == "chip_down":
                    ic_die_prop.orientation = definition.DieOrientation.CHIP_DOWN
                if chip_orientation.lower() == "chip_up":
                    ic_die_prop.orientation = definition.DieOrientation.CHIP_UP
                cmp_property.die_property = ic_die_prop

            solder_ball_prop = cmp_property.solder_ball_property
            solder_ball_prop.set_diameter(utility.Value(sball_diam), utility.Value(sball_mid_diam))
            solder_ball_prop.height = utility.Value(sball_height)
            solder_ball_prop.shape = sball_shape
            cmp_property.solder_ball_property = solder_ball_prop

            port_prop = cmp_property.port_property
            port_prop.reference_size_auto = True
            cmp_property.port_property = port_prop
            edb_cmp.component_property = cmp_property
            return True
        else:
            return False

    @pyedb_function_handler()
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

        >>> from pyedb.grpc.edb import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.components.set_component_rlc(
        ...     "R1", res_value=50, ind_value=1e-9, cap_value=1e-12, isparallel=False
        ... )

        """
        if res_value is None and ind_value is None and cap_value is None:
            self.instances[componentname].is_enabled = False
            self._logger.info("No parameters passed, component %s  is disabled.", componentname)
            return True
        edb_component = self.get_component_by_name(componentname)
        edb_rlc_component_property = definition.RLCComponentProperty()
        component_pins = self.get_pin_from_component(componentname)
        pin_number = len(component_pins)
        if pin_number == 2:
            from_pin = component_pins[0]
            to_pin = component_pins[1]
            rlc = utility.Rlc()
            rlc.is_parallel = isparallel
            if res_value is not None:
                rlc.r_enabled = True
                rlc.r = utility.Value(res_value)
            else:
                rlc.r_enabled = False
            if ind_value is not None:
                rlc.l_enabled = True
                rlc.l = utility.Value(ind_value)
            else:
                rlc.l_enabled = False
            if cap_value is not None:
                rlc.c_enabled = True
                rlc.c = utility.Value(cap_value)
            else:
                rlc.c_enabled = False
            pin_pair = (from_pin.name, to_pin.name)  # missing PinPair ?
            rlc_model = hierarchy.PinPairModel.create()  # all to check
            rlc_model.pin_pairs(pin_pair, rlc)
            edb_rlc_component_property.model = rlc_model
            edb_component.component_property = edb_rlc_component_property
        else:
            self._logger.warning(
                "Component %s has not been assigned because either it is not present in the layout "
                "or it contains a number of pins not equal to 2",
                componentname,
            )
            return False
        self._logger.info("RLC properties for Component %s has been assigned.", componentname)
        return True

    @pyedb_function_handler()
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
                self.instances[comp].is_enabled = False
        return found

    @pyedb_function_handler()
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
                        pinlist = self.get_pin_from_component(refdes)
                        if not part_name in self.definitions:
                            footprint_cell = self.definitions[comp.partname]._edb_comp_def.footprint_cell
                            comp_def = definition.ComponentDef.create(self._db, part_name, footprint_cell)
                            for pin in pinlist:
                                definition.ComponentPin.create(comp_def, pin.name)

                        p_layer = comp.placement_layer
                        refdes_temp = comp.refdes + "_temp"
                        comp.refdes = refdes_temp

                        unmount_comp_list.remove(refdes)
                        comp.edbcomponent.ungroup = True

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
                self.instances[comp].is_enabled = False
        return True

    @pyedb_function_handler()
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

    @pyedb_function_handler()
    def get_pin_from_component(self, component, netName=None, pinName=None):
        """Retrieve the pins of a component.

        Parameters
        ----------
        component : str or EDB component
            Name of the component or the EDB component object.
        netName : str, optional
            Filter on the net name as an alternative to
            ``pinName``. The default is ``None``.
        pinName : str, optional
            Filter on the pin name an an alternative to
            ``netName``. The default is ``None``.

        Returns
        -------
        list
            List of pins when the component is found or ``[]`` otherwise.

        Examples
        --------

        >>> from pyedb.grpc.edb import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edbapp.components.get_pin_from_component("R1", refdes)

        """
        if not isinstance(component, hierarchy.ComponentGroup):
            component = hierarchy.ComponentGroup.find(self._edb.layout, component)
        if netName:
            if not isinstance(netName, list):
                netName = [netName]
            pins = [
                p
                for p in component.members if p.layout_obj_type.value == 1 and not p.net.is_null
                                              and p.is_layout_pin and p.net.name in netName]
        elif pinName:
            if not isinstance(pinName, list):
                pinName = [pinName]
            pins = [
                p
                for p in list(component.members)
                if p.layout_obj_type.value == 1
                   and p.is_layout_pin
                   and not p.net.is_null
                   and (self.get_aedt_pin_name(p) in pinName or p.name in pinName)
            ]
        else:
            pins = [p for p in list(component.members) if p.layout_obj_type.value == 1 and not p.net.is_null
                    and p.is_layout_pin]

        return [EDBPadstackInstance(pin, self._pedb) for pin in pins]

    @pyedb_function_handler()
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

        >>> from pyedb.grpc.edb import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edbapp.components.get_aedt_pin_name(pin)

        """
        if isinstance(pin, EDBPadstackInstance):
            pin = pin._edb_padstackinstance
        _, name = pin.get_product_property(database.ProductIdType.DESIGNER, 11, "")
        name = str(name).strip("'")
        return name

    @pyedb_function_handler()
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

        >>> from pyedb.grpc.edb import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edbapp.components.get_pin_position(pin)

        """
        pin_position = geometry.PointData(pin.get_position_and_rotation()[:2])
        if pin.component.is_null:
            transformed_pt_pos = pin_position
        else:
            transformed_pt_pos = pin.component.transform.transform_point(pin_position)
        return [transformed_pt_pos[0].value, transformed_pt_pos[1].value]

    @pyedb_function_handler()
    def get_pins_name_from_net(self, pin_list, net_name):
        """Retrieve pins belonging to a net.

        Parameters
        ----------
        pin_list : list
            List of pins to check.
        net_name : str
            Name of the net.

        Returns
        -------
        list
            List of pins belong to the net.

        Examples
        --------

        >>> from pyedb.grpc.edb import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edbapp.components.get_pins_name_from_net(pin_list, net_name)

        """
        pinlist = []
        for pin in pin_list:
            if pin.net.name == net_name:
                pinlist.append(pin.name)
        return pinlist

    @pyedb_function_handler()
    def get_nets_from_pin_list(self, PinList):
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

        >>> from pyedb.grpc.edb import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edbapp.components.get_nets_from_pin_list(pinlist)

        """
        netlist = []
        for pin in PinList:
            netlist.append(pin.net.name)
        return list(set(netlist))

    @pyedb_function_handler()
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

        >>> from pyedb.grpc.edb import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edbapp.components.get_component_net_connection_info(refdes)

        """
        component_pins = self.get_pin_from_component(refdes)
        data = {"refdes": [], "pin_name": [], "net_name": []}
        for pin_obj in component_pins:
            pin_name = pin_obj.name
            net_name = pin_obj.net.name
            if pin_name is not None:
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

        >>> from pyedb.grpc.edb import Edb
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

        >>> from pyedb.grpc.edb import Edb
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

    @pyedb_function_handler()
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

        >>> from pyedb.grpc.edb import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.components.short_component_pins("J4A2", ["G4", "9", "3"])

        """
        component = self.instances[component_name]
        pins = component.pins
        pins_list = []

        component.center
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
            if placement_layer in self._pedb.padstacks.definitions[pin.pin.padstack_def.name].pad_by_layer:
                pad = self._pedb.padstacks.definitions[pin.pin.padstack_def.name].pad_by_layer[placement_layer]
            else:
                layer = list(self._pedb.padstacks.definitions[pin.pin.padstack_def().name].pad_by_layer.keys())[
                    0
                ]
                pad = self._pedb.padstacks.definitions[pin.pin.padstack_def.name].pad_by_layer[layer]
            pars = pad.parameters_values
            geom = pad.geometry_type
            if geom < 6 and pars:
                delta_pins.append(max(pars) + min(pars) / 2)
                w = min(min(pars), w)
            elif pars:
                delta_pins.append(1.5 * pars[0])
                w = min(pars[0], w)
            elif pad.polygon_data:  # pragma: no cover
                bbox = pad.polygon_data.bbox()
                lower = [bbox[0].y.value, bbox[0].y.value]
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
