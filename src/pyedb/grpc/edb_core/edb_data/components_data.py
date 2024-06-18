import logging
import re
import warnings

from pyedb.grpc.edb_core.edb_data.padstacks_data import EDBPadstackInstance
import numpy as np
from pyedb.generic.general_methods import get_filename_without_extension
from pyedb.generic.general_methods import pyedb_function_handler
from pyedb.modeler.geometry_operators import GeometryOperators
import ansys.edb.hierarchy as hierarchy
import ansys.edb.utility as utility


class EDBComponentDef(object):
    """Manages EDB functionalities for component definitions.

    Parameters
    ----------
    parent : :class:`edb_core.components.Components`
    comp_def : object
        Edb ComponentDef Object
    """

    def __init__(self, pedb, comp_def):
        self._pedb = pedb
        self._edb_comp_def = comp_def

    @property
    def _comp_model(self):
        return self._edb_comp_def.component_models

    @property
    def part_name(self):
        """Retrieve component definition name."""
        return self._edb_comp_def.name

    @part_name.setter
    def part_name(self, name):
        self._edb_comp_def.name = name

    @property
    def components(self):
        """Get the list of components belonging to this component definition.

        Returns
        -------
        dict of :class:`edb_core.edb_data.components_data.EDBComponent`
        """
        comp_list = [
            EDBComponent(self._pedb, l)
            for l in self._pedb.hierarchy.component.find_by_def(
                self._pedb.layout, self.part_name
            )
        ]
        return {comp.refdes: comp for comp in comp_list}

    @pyedb_function_handler()
    def assign_rlc_model(self, res=None, ind=None, cap=None, is_parallel=False):
        """Assign RLC to all components under this part name.

        Parameters
        ----------
        res : int, float
            Resistance. Default is ``None``.
        ind : int, float
            Inductance. Default is ``None``.
        cap : int, float
            Capacitance. Default is ``None``.
        is_parallel : bool, optional
            Whether it is parallel or series RLC component.
        """
        for comp in list(self.components.values()):
            comp.assign_rlc_model(res, ind, cap, is_parallel)
        return True

    @pyedb_function_handler()
    def assign_s_param_model(self, file_path, model_name=None, reference_net=None):
        """Assign S-parameter to all components under this part name.

        Parameters
        ----------
        file_path : str
            File path of the S-parameter model.
        name : str, optional
            Name of the S-parameter model.
        Returns
        -------

        """
        for comp in list(self.components.values()):
            comp.assign_s_param_model(file_path, model_name, reference_net)
        return True

    @pyedb_function_handler()
    def assign_spice_model(self, file_path, model_name=None):
        """Assign Spice model to all components under this part name.

        Parameters
        ----------
        file_path : str
            File path of the Spice model.
        name : str, optional
            Name of the Spice model.
        Returns
        -------

        """
        for comp in list(self.components.values()):
            comp.assign_spice_model(file_path, model_name)
        return True


class EDBComponent(object):
    """Manages EDB functionalities for components.

    Parameters
    ----------
    parent : :class:`pyaedt.edb_core.components.Components`
        Inherited AEDT object.
    component : object
        Edb Component Object

    """

    class _PinPair(object):  # pragma: no cover
        def __init__(self, pcomp, edb_comp, edb_comp_prop, edb_model, edb_pin_pair):
            self._pedb_comp = pcomp
            self._edb_comp = edb_comp
            self._edb_comp_prop = edb_comp_prop
            self._edb_model = edb_model
            self._edb_pin_pair = edb_pin_pair

        @property
        def is_parallel(self):
            return self._pin_pair_rlc.is_parallel  # pragma: no cover

        @is_parallel.setter
        def is_parallel(self, value):
            rlc = self._pin_pair_rlc
            rlc.is_parallel = value
            self._set_comp_prop()  # pragma: no cover

        @property
        def _pin_pair_rlc(self):
            return self._edb_model.GetPinPairRlc(self._edb_pin_pair)

        @property
        def rlc_enable(self):
            rlc = self._pin_pair_rlc
            return [rlc.REnabled, rlc.LEnabled, rlc.CEnabled]

        @rlc_enable.setter
        def rlc_enable(self, value):
            rlc = self._pin_pair_rlc
            rlc.REnabled = value[0]
            rlc.LEnabled = value[1]
            rlc.CEnabled = value[2]
            self._set_comp_prop()  # pragma: no cover

        @property
        def resistance(self):
            return self._pin_pair_rlc.R.value  # pragma: no cover

        @resistance.setter
        def resistance(self, value):
            self._pin_pair_rlc.R = value
            self._set_comp_prop(self._pin_pair_rlc)  # pragma: no cover

        @property
        def inductance(self):
            return self._pin_pair_rlc.L.ToDouble()  # pragma: no cover

        @inductance.setter
        def inductance(self, value):
            self._pin_pair_rlc.L = value
            self._set_comp_prop(self._pin_pair_rlc)  # pragma: no cover

        @property
        def capacitance(self):
            return self._pin_pair_rlc.C.ToDouble()  # pragma: no cover

        @capacitance.setter
        def capacitance(self, value):
            self._pin_pair_rlc.C = value
            self._set_comp_prop(self._pin_pair_rlc)  # pragma: no cover

        @property
        def rlc_values(self):  # pragma: no cover
            cmp_type = self.edbcomponent.component_type.value
            if 0 < cmp_type < 4:
                rlc = self._pin_pair_rlc
                return [rlc.r, rlc.r, rlc.c]
            return None

        @rlc_values.setter
        def rlc_values(self, values):  # pragma: no cover
            rlc = self._pin_pair_rlc
            rlc.R = values[0]
            rlc.L = values[1]
            rlc.C = values[2]
            self._set_comp_prop()  # pragma: no cover

        def _set_comp_prop(self):  # pragma: no cover
            self._edb_model.SetPinPairRlc(self._edb_pin_pair, self._pin_pair_rlc)
            self._edb_comp_prop.SetModel(self._edb_model)
            self._edb_comp.SetComponentProperty(self._edb_comp_prop)

    class _SpiceModel(object):  # pragma: no cover
        def __init__(self, edb_model):
            self._edb_model = edb_model

        @property
        def file_path(self):
            return self._edb_model.model_path

        @property
        def name(self):
            return self._edb_model.model_name

    class _SparamModel(object):  # pragma: no cover
        def __init__(self, edb_model):
            self._edb_model = edb_model

        @property
        def name(self):
            return self._edb_model.name

        @property
        def reference_net(self):
            return self._edb_model.reference_net

    class _NetlistModel(object):  # pragma: no cover
        def __init__(self, edb_model):
            self._edb_model = edb_model

        @property
        def netlist(self):
            return self._edb_model.net_list

    def __init__(self, pedb, cmp):
        self._pedb = pedb
        self.edbcomponent = cmp
        self._layout_instance = None
        self._comp_instance = None

    @property
    def layout_instance(self):
        """EDB layout instance object."""
        return self._pedb.layout_instance

    @property
    def component_instance(self):
        """Edb component instance."""
        if self._comp_instance is None:
            self._comp_instance = self.layout_instance.get_layout_obj_instance_in_context(self.edbcomponent, None)
        return self._comp_instance

    @property
    def _active_layout(self):  # pragma: no cover
        return self._pedb.active_layout

    @property
    def component_property(self):
        """``ComponentProperty`` object."""
        return self.edbcomponent.component_property

    @property
    def _edb_model(self):  # pragma: no cover
        return self.component_property.model

    @property  # pragma: no cover
    def _pin_pairs(self):
        cmp_type = self.edbcomponent.component_type.value
        if 0 < cmp_type < 4:
            return self._edb_model.pin_pairs()
        return []

    @property
    def is_enabled(self):
        """Get or Set the component to active mode.

        Returns
        -------
        bool
            ``True`` if component is active, ``False`` if is disabled..
        """
        return self.component_property.is_enabled

    @is_enabled.setter
    def is_enabled(self, value):
        cmp_prop = self.component_property
        if isinstance(value, bool):
            cmp_prop.is_enabled = value
            self.edbcomponent.component_property = cmp_prop

    @property
    def spice_model(self):
        """Get assigned Spice model properties."""
        if not self.model_type == "SPICEModel":
            return None
        else:
            return self._SpiceModel(self._edb_model)

    @property
    def s_param_model(self):
        """Get assigned S-parameter model properties."""
        if not self.model_type == "SParameterModel":
            return None
        else:
            return self._SparamModel(self._edb_model)

    @property
    def netlist_model(self):
        """Get assigned netlist model properties."""
        if not self.model_type == "NetlistModel":
            return None
        else:
            return self._NetlistModel(self._edb_model)

    @property
    def solder_ball_height(self):
        """Solder ball height if available."""
        if "solder_ball_property" in dir(self.component_property):
            return self.component_property.solder_ball_property.height
        return None

    @property
    def solder_ball_placement(self):
        """Solder ball placement if available.."""
        if "solder_ball_property" in dir(self.component_property):
            return self.component_property.solder_ball_property.placement.value
        return 2

    @property
    def name(self):
        """Component name, same as reference designator.

        Returns
        -------
        str
            Reference designator name.
        """
        return self.refdes

    @name.setter
    def name(self, name):
        if isinstance(name, str):
            self.edbcomponent.name = name

    @property
    def refdes(self):
        """Reference Designator Name.

        Returns
        -------
        str
            Reference Designator Name.
        """
        return self.edbcomponent.name

    @refdes.setter
    def refdes(self, name):
        if isinstance(name, str):
            self.edbcomponent.name = name

    @property
    def is_null(self):
        """Flag indicating if the current object exists."""
        return self.edbcomponent.is_null

    @property
    def is_enabled(self):
        """Flag indicating if the current object is enabled.

        Returns
        -------
        bool
            ``True`` if current object is enabled, ``False`` otherwise.
        """
        if self.type in ["Resistor", "Capacitor", "Inductor"]:
            return self.component_property.enabled
        else:  # pragma: no cover
            return True

    @is_enabled.setter
    def is_enabled(self, enabled):
        """Enables the current object."""
        if self.type in ["Resistor", "Capacitor", "Inductor"]:
            component_property = self.component_property
            component_property.enabled = enabled
            self.edbcomponent.component_property = component_property

    @property
    def model_type(self):
        """Retrieve assigned model type."""
        if self.type not in ["Resistor", "Inductor", "Capacitor"]:
            return None
        _model_type = str(self._edb_model).split(".")[-1]
        if _model_type == "PinPairModel":
            return "RLC"
        else:
            return _model_type

    @property
    def rlc_values(self):
        """Get component rlc values."""
        if not self._pin_pairs:
            return [None, None, None]
        model = self.component_property.model.clone()
        pair = model.rlc(self._pin_pairs[0])
        return [pair.r.value, pair.l.value, pair.c.value]


    @rlc_values.setter
    def rlc_values(self, value):
        if isinstance(value, list):  # pragma no cover
            rlc_enabled = [True if i else False for i in value]
            rlc_values = [utility.Value(i) for i in value]
            model = hierarchy.PinPairModel()
            pin_names = list(self.pins.keys())
            for idx, i in enumerate(np.arange(len(pin_names) // 2)):
                pin_pair = self._edb.utility.utility.PinPair(pin_names[idx], pin_names[idx + 1])
                rlc = self._edb.utility.utility.Rlc(
                    rlc_values[0], rlc_enabled[0], rlc_values[1], rlc_enabled[1], rlc_values[2], rlc_enabled[2], False
                )
                model.rlc(pin_pair)
            self._set_model(model)

    @property
    def value(self):
        """Retrieve discrete component value.

        Returns
        -------
        str
            Value. ``None`` if not an RLC Type.
        """
        if self.model_type == "RLC":
            if not self._pin_pairs:
                if self.type == "Inductor":
                    return 1e-9
                elif self.type == "Resistor":
                    return 1e6
                else:
                    return 1
            else:
                pin_pair = self._pin_pairs[0]
            if len([i for i in pin_pair.rlc_enable if i]) == 1:
                return [pin_pair.rlc_values[idx] for idx, val in enumerate(pin_pair.rlc_enable) if val][0]
            else:
                return pin_pair.rlc_values
        elif self.model_type == "SPICEModel":
            return self.spice_model.file_path
        elif self.model_type == "SParameterModel":
            return self.s_param_model.name
        else:
            try:
                return self.netlist_model.netlist
            except:
                return None

    @value.setter
    def value(self, value):
        rlc_enabled = [True if i == self.type else False for i in ["Resistor", "Inductor", "Capacitor"]]
        rlc_values = [value if i == self.type else 0 for i in ["Resistor", "Inductor", "Capacitor"]]
        rlc_values = [utility.Value(i) for i in rlc_values]

        model = hierarchy.PinPairModel()
        pin_names = list(self.pins.keys())
        for idx, i in enumerate(np.arange(len(pin_names) // 2)):
            pin_pair = utility.PinPair(pin_names[idx], pin_names[idx + 1])
            rlc = self._edb.utility.utility.Rlc(
                rlc_values[0], rlc_enabled[0], rlc_values[1], rlc_enabled[1], rlc_values[2], rlc_enabled[2], False
            )
            model.rlc = pin_pair, rlc
        self._set_model(model)

    @property
    def res_value(self):
        """Resistance value.

        Returns
        -------
        str
            Resistance value or ``None`` if not an RLC type.
        """
        cmp_type = self.edbcomponent.component_type.value
        if 0 < cmp_type < 4:
            componentProperty = self.edbcomponent.component_property
            model = componentProperty.model.clone()
            pinpairs = model.pin_pairs()
            if not pinpairs:
                return "0"
            for pinpair in pinpairs:
                pair = model.rlc(pinpair)
                return pair.r.value
        return None

    @res_value.setter
    def res_value(self, value):  # pragma no cover
        if value:
            if self.rlc_values == [None, None, None]:
                self.rlc_values = [value, 0, 0]
            else:
                self.rlc_values = [value, self.rlc_values[1], self.rlc_values[2]]

    @property
    def cap_value(self):
        """Capacitance Value.

        Returns
        -------
        str
            Capacitance Value. ``None`` if not an RLC Type.
        """
        cmp_type = self.edbcomponent.component_type.value
        if 0 < cmp_type < 4:
            componentProperty = self.edbcomponent.component_property
            model = componentProperty.model.clone()
            pinpairs = model.pin_pairs()
            if not pinpairs:
                return "0"
            for pinpair in pinpairs:
                pair = model.rlc(pinpair)
                return pair.c.value
        return None

    @cap_value.setter
    def cap_value(self, value):  # pragma no cover
        if value:
            if self.rlc_values == [None, None, None]:
                self.rlc_values = [0, 0, value]
            else:
                self.rlc_values = [self.rlc_values[1], self.rlc_values[2], value]

    @property
    def ind_value(self):
        """Inductance Value.

        Returns
        -------
        str
            Inductance Value. ``None`` if not an RLC Type.
        """
        cmp_type = self.edbcomponent.component_type.value
        if 0 < cmp_type < 4:
            componentProperty = self.edbcomponent.component_property
            model = componentProperty.model.clone()
            pinpairs = model.pin_pairs()
            if not pinpairs:
                return "0"
            for pinpair in pinpairs:
                pair = model.rlc(pinpair)
                return pair.l.value
        return None

    @ind_value.setter
    def ind_value(self, value):  # pragma no cover
        if value:
            if self.rlc_values == [None, None, None]:
                self.rlc_values = [0, value, 0]
            else:
                self.rlc_values = [self.rlc_values[1], value, self.rlc_values[2]]

    @property
    def is_parallel_rlc(self):
        """Define if model is Parallel or Series.

        Returns
        -------
        bool
            ``True`` if it is a parallel rlc model. ``False`` for series RLC. ``None`` if not an RLC Type.
        """
        cmp_type = self.edbcomponent.component_type.value
        if 0 < cmp_type < 4:
            model = self.component_property.model.clone()
            pinpairs = model.pin_pairs()
            for pinpair in pinpairs:
                pair = model.rlc(pinpair)
                return pair.is_parallel
        return None

    @is_parallel_rlc.setter
    def is_parallel_rlc(self, value):  # pragma no cover
        if not len(self._pin_pairs):
            logging.warning(self.refdes, " has no pin pair.")
        else:
            if isinstance(value, bool):
                componentProperty = self.edbcomponent.component_property
                model = componentProperty.model.clone()
                pinpairs = model.pin_pairs
                if not list(pinpairs):
                    return "0"
                for pin_pair in pinpairs:
                    pin_pair_rlc = model.rlc(pin_pair)
                    pin_pair_rlc.is_parallel = value
                    pin_pair_model = self._edb_model
                    pin_pair_model.rlc(pin_pair, pin_pair_rlc)
                    comp_prop = self.component_property
                    comp_prop.model = pin_pair_model
                    self.edbcomponent.component_property = comp_prop

    @property
    def center(self):
        """Compute the component center.

        Returns
        -------
        list
        """
        polygon_data = self.component_instance.get_bbox()
        comp_outline = [[pt.x.value, pt.y.value, 0] for pt in polygon_data.points]
        center = GeometryOperators.get_polygon_centroid(comp_outline)
        return center[:2]

    @property
    def bounding_box(self):
        """Component's bounding box.

        Returns
        -------
        List[float]
            List of coordinates for the component's bounding box, with the list of
            coordinates in this order: [X lower left corner, Y lower left corner,
            X upper right corner, Y upper right corner].
        """
        bbox = self.component_instance.get_bbox()
        lower_left = bbox.points[0]
        upper_right = bbox.points[2]
        return [lower_left.x.value, lower_left.y.value, upper_right.x.value, upper_right.y.value]

    @property
    def rotation(self):
        """Compute the component rotation in radian.

        Returns
        -------
        float
        """
        return self.edbcomponent.transform.rotation.value

    @property
    def pinlist(self):
        """Pins of the component.

        Returns
        -------
        list
            List of Pins of Component.
        """
        pins = [p for p in self.edbcomponent.members if p.layout_obj_type.value == 1 and p.is_layout_pin
                and p.component.name == self.refdes]
        return pins

    @property
    def nets(self):
        """Property returning component net list.

        Returns
        -------
        list
            List of component nets.
        """
        return list(set([pin.net_name for pin in list(self.pins.values())]))

    @property
    def pins(self):
        """Property returning EDBPadstackInstance objects from Component. This object are also called pins for
        components.

        Returns
        -------
        dic[str, :class:`pyaedt.edb_core.edb_data.definitions.EDBPadstackInstance`]
            Dictionary of EDBPadstackInstance Components.
        """
        return {pin.name: EDBPadstackInstance(pin, self._pedb) for pin in self.pinlist}

    @property
    def type(self):
        """Property returning component type.

        Returns
        -------
        str
            Component type.
        """
        cmp_type = self.edbcomponent.component_type
        if cmp_type == hierarchy.ComponentType.RESISTOR:
            return "Resistor"
        elif cmp_type == hierarchy.ComponentType.INDUCTOR:
            return "Inductor"
        elif cmp_type == hierarchy.ComponentType.CAPACITOR:
            return "Capacitor"
        elif cmp_type == hierarchy.ComponentType.IC:
            return "IC"
        elif cmp_type == hierarchy.ComponentType.IO:
            return "IO"
        elif cmp_type == hierarchy.ComponentType.OTHER:
            return "Other"

    @type.setter
    def type(self, new_type):
        """Set component type

        Parameters
        ----------
        new_type : str
            Type of the component. Options are ``"Resistor"``,  ``"Inductor"``, ``"Capacitor"``,
            ``"IC"``, ``"IO"`` and ``"Other"``.
        """
        type_id = None
        if new_type == "Resistor":
            type_id = hierarchy.ComponentType.RESISTOR
        elif new_type == "Inductor":
            type_id = hierarchy.ComponentType.INDUCTOR
        elif new_type == "Capacitor":
            type_id = hierarchy.ComponentType.CAPACITOR
        elif new_type == "IC":
            type_id = hierarchy.ComponentType.IC
        elif new_type == "IO":
            ttype_id = hierarchy.ComponentType.IO
        elif new_type == "Other":
            type_id = hierarchy.ComponentType.OTHER
        else:
            return
        if type_id:
            self.edbcomponent.component_type = type_id

    @property
    def numpins(self):
        """Property returning component pin number.

        Returns
        -------
        int
            Number of Pins of Component.
        """
        return self.edbcomponent.num_pins

    @property
    def part_name(self):
        """Property returning component part name.

        Returns
        -------
        str
            Component part name.
        """
        return self.edbcomponent.component_def.name

    @part_name.setter
    def part_name(self, name):  # pragma: no cover
        """Set component part name."""
        if isinstance(name, str):
            self.edbcomponent.component_def.name = name

    @property
    def _edb(self):
        return self._pedb

    @property
    def placement_layer(self):
        """Property returning the component placement layer name.

        Returns
        -------
        str
           Name of the placement layer.
        """
        return self.edbcomponent.placement_layer.name

    @property
    def lower_elevation(self):
        """Property returning component placement layer lower elevation.

        Returns
        -------
        float
            Lower elevation of the placement layer.
        """
        return self.edbcomponent.placement_layer.lower_elevation

    @property
    def upper_elevation(self):
        """Property returning component placement layer upper elevation.

        Returns
        -------
        float
            Upper elevation of the placement layer.

        """
        return self.edbcomponent.placement_layer.upper_elevation

    @property
    def top_bottom_association(self):
        """Top/bottom association of the component placement layer.

        Returns
        -------
        int
            Top/bottom association of the placement layer, where:

            * 0 - Top associated
            * 1 - No association
            * 2 - Bottom associated
            * 4 - Number of top/bottom associations.
            * -1 - Undefined
        """
        return self.edbcomponent.placement_layer.top_bottom_association.value

    @pyedb_function_handler
    def _set_model(self, model):  # pragma: no cover
        comp_prop = self.component_property
        comp_prop.model = model
        self.edbcomponent.component_property = comp_prop
        return True

    @pyedb_function_handler
    def assign_spice_model(self, file_path, name=None):
        """Assign Spice model to this component.

        Parameters
        ----------
        file_path : str
            File path of the Spice model.
        name : str, optional
            Name of the Spice model.

        Returns
        -------

        """
        if not name:
            name = get_filename_without_extension(file_path)

        with open(file_path, "r") as f:
            for line in f:
                if "subckt" in line.lower():
                    pinNames = [i.strip() for i in re.split(" |\t", line) if i]
                    pinNames.remove(pinNames[0])
                    pinNames.remove(pinNames[0])
                    break
        model = None
        if len(pinNames) == self.numpins:
            model = self._edb.hierarchy.SPICEModel()
            model.model_path = file_path
            model.model_name = name
            terminal = 1
            for pn in pinNames:
                model.add_terminal(pn, str(terminal))
                terminal += 1
        else:  # pragma: no cover
            logging.error("Wrong number of Pins")
            return False
        if model:
            return self._set_model(model)

    @pyedb_function_handler
    def assign_s_param_model(self, file_path, name=None, reference_net=None):
        """Assign S-parameter to the component.

        Parameters
        ----------
        file_path : str
            File path of the S-parameter model.
        name : str, optional
            Name of the S-parameter model.

        Returns
        -------

        """
        if not name:
            name = get_filename_without_extension(file_path)
        edb_component_def = self.edbcomponent.component_def
        nport_model = self._edb.definition.NPortComponentModel.find(edb_component_def, name)
        if nport_model.is_null:
            nport_model = self._edb.definition.NPortComponentModel.create(name)
            nport_model.reference_file = file_path
            self.edbcomponent.component_def = edb_component_def

        model = self._edb.hierarchy.SParameterModel()
        model.component_model = name
        if reference_net:
            model.reference_net = reference_net
        return self._set_model(model)

    @pyedb_function_handler
    def assign_rlc_model(self, res=None, ind=None, cap=None, is_parallel=False):
        """Assign RLC to this component.

        Parameters
        ----------
        res : int, float
            Resistance. Default is ``None``.
        ind : int, float
            Inductance. Default is ``None``.
        cap : int, float
            Capacitance. Default is ``None``.
        is_parallel : bool, optional
            Whether it is a parallel or series RLC component. The default is ``False``.
        """
        if res is None and ind is None and cap is None:
            self._pedb.logger.error("At least one value has to be provided.")
            return False
        r_enabled = True if res else False
        l_enabled = True if ind else False
        c_enabled = True if cap else False
        res = 0 if res is None else res
        ind = 0 if ind is None else ind
        cap = 0 if cap is None else cap
        res, ind, cap = self._pedb.utility.value(res), self._pedb.utility.value(ind), self._pedb.utility.value(cap)
        model = self._edb.hierarchy.PinPairModel()
        pin_names = list(self.pins.keys())
        for idx, i in enumerate(np.arange(len(pin_names) // 2)):
            pin_pair = self._edb.utility.PinPair(pin_names[idx], pin_names[idx + 1])
            rlc = self._edb.utility.Rlc(res, r_enabled, ind, l_enabled, cap, c_enabled, is_parallel)
            model.rlc(pin_pair, rlc)
        return self._set_model(model)

    @pyedb_function_handler
    def create_clearance_on_component(self, extra_soldermask_clearance=1e-4):
        """Create a Clearance on Soldermask layer by drawing a rectangle.

        Parameters
        ----------
        extra_soldermask_clearance : float, optional
            Extra Soldermask value in meter to be applied on component bounding box.
        Returns
        -------
            bool
        """
        bounding_box = self.bounding_box
        opening = [bounding_box[0] - extra_soldermask_clearance]
        opening.append(bounding_box[1] - extra_soldermask_clearance)
        opening.append(bounding_box[2] + extra_soldermask_clearance)
        opening.append(bounding_box[3] + extra_soldermask_clearance)

        comp_layer = self.placement_layer
        layer_names = list(self._pedb.stackup.stackup_layers.keys())
        layer_index = layer_names.index(comp_layer)
        if comp_layer in [layer_names[0] + layer_names[-1]]:
            return False
        elif layer_index < len(layer_names) / 2:
            soldermask_layer = layer_names[layer_index - 1]
        else:
            soldermask_layer = layer_names[layer_index + 1]

        if not self._pedb.modeler.get_primitives(layer_name=soldermask_layer):
            all_nets = list(self._pedb.nets.nets.values())
            poly = self._pedb._create_conformal(all_nets, 0, 1e-12, False, 0)
            self._pedb.modeler.create_polygon(poly, soldermask_layer, [], "")

        void = self._pedb.modeler.create_rectangle(
            soldermask_layer,
            "{}_opening".format(self.refdes),
            lower_left_point=opening[:2],
            upper_right_point=opening[2:],
        )
        void.is_negative = True
        return True
