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

import logging
import re
from typing import Optional
import warnings

from ansys.edb.core.definition.solder_ball_property import SolderballShape
from ansys.edb.core.geometry.polygon_data import PolygonData as GrpcPolygonData
from ansys.edb.core.hierarchy.component_group import (
    ComponentGroup as GrpcComponentGroup,
)
from ansys.edb.core.hierarchy.component_group import ComponentType as GrpcComponentType
from ansys.edb.core.hierarchy.netlist_model import NetlistModel as GrpcNetlistModel
from ansys.edb.core.hierarchy.sparameter_model import (
    SParameterModel as GrpcSParameterModel,
)
from ansys.edb.core.utility.rlc import PinPair as GrpcPinPair
from ansys.edb.core.utility.rlc import Rlc as GrpcRlc
from ansys.edb.core.utility.value import Value as EDBValue

from pyedb.grpc.edb_core.definition.package_def import PackageDef
from pyedb.grpc.edb_core.hierarchy.pin_pair_model import PinPairModel
from pyedb.grpc.edb_core.hierarchy.spice_model import SpiceModel
from pyedb.grpc.edb_core.primitive.padstack_instances import PadstackInstance

try:
    import numpy as np
except ImportError:
    warnings.warn(
        "The NumPy module is required to run some functionalities of EDB.\n"
        "Install with \n\npip install numpy\n\nRequires CPython."
    )
from pyedb.generic.general_methods import get_filename_without_extension


class Component(GrpcComponentGroup):
    """Manages EDB functionalities for components.

    Parameters
    ----------
    parent : :class:`pyedb.dotnet.edb_core.components.Components`
        Components object.
    component : object
        Edb Component Object

    """

    def __init__(self, pedb, edb_object):
        super().__init__(edb_object._ConnObj__stub.GetGroup(edb_object.msg))
        self._pedb = pedb
        self._edb_object = edb_object
        self._layout_instance = None
        self._comp_instance = None

    @property
    def group_type(self):
        return str(self.type).split(".")[-1].lower()

    @property
    def layout_instance(self):
        """EDB layout instance object."""
        return self._pedb.layout_instance

    @property
    def component_instance(self):
        """Edb component instance."""
        if self._comp_instance is None:
            self._comp_instance = self.layout_instance.get_layout_obj_instance_in_context(self, None)
        return self._comp_instance

    @property
    def _active_layout(self):  # pragma: no cover
        return self._pedb.active_layout

    @property
    def component_property(self):
        """``ComponentProperty`` object."""
        return self.component_property

    @component_property.setter
    def component_property(self, value):
        if value:
            self.component_property = value

    @property
    def _edb_model(self):  # pragma: no cover
        return self.component_property.model

    @property  # pragma: no cover
    def _pin_pairs(self):
        edb_comp_prop = self.component_property
        edb_model = self._edb_model
        return [PinPairModel(self, self, edb_comp_prop, edb_model, pin_pair) for pin_pair in list(edb_model.PinPairs)]

    @property
    def model(self):
        """Component model."""
        edb_object = self.component_property.model
        if self.model_type == "PinPairModel":
            return PinPairModel(self._pedb, self)
        elif self.model_type == "SPICEModel":
            return SpiceModel(self._pedb, self)

    @model.setter
    def model(self, value):
        if not isinstance(value, PinPairModel):
            self._pedb.logger.error("Invalid input. Set model failed.")

        comp_prop = self.component_property
        comp_prop.model = value
        self.component_property = comp_prop

    @property
    def package_def(self):
        """Package definition."""
        edb_object = self.component_property.package_def
        package_def = PackageDef(self._pedb, edb_object)
        if not package_def.is_null:
            return package_def

    @package_def.setter
    def package_def(self, value):
        package_def = self._pedb.definitions.package[value]
        comp_prop = self.component_property
        comp_prop.package_def = package_def
        self.component_property = comp_prop

    def create_package_def(self, name="", component_part_name=None):
        """Create a package definition and assign it to the component.

        Parameters
        ----------
        name: str, optional
            Name of the package definition
        component_part_name : str, optional
            Part name of the component.

        Returns
        -------
        bool
            ``True`` if succeeded, ``False`` otherwise.
        """
        if not name:
            name = "{}_{}".format(self.refdes, self.part_name)
        if name not in self._pedb.definitions.package:
            self._pedb.definitions.add_package_def(name, component_part_name=component_part_name)
            self.package_def = name
            polygon = GrpcPolygonData(self.component_instance.GetBBox())
            self.package_def.exterior_boundary = polygon
            return True
        else:
            logging.error(f"Package definition {name} already exists")
            return False

    @property
    def enabled(self):
        """Get or Set the component to active mode."""
        if self.type.lower() in ["resistor", "capacitor", "inductor"]:
            return self.component_property.enabled
        else:
            return

    @enabled.setter
    def enabled(self, value):
        cmp_prop = self.component_property
        cmp_prop.enabled = value
        self.component_property = cmp_prop

    @property
    def spice_model(self):
        """Get assigned Spice model properties."""
        if not self.model_type == "SPICEModel":
            return None
        else:
            return SpiceModel(self._edb_model)

    @property
    def s_param_model(self):
        """Get assigned S-parameter model properties."""
        if not self.model_type == "SParameterModel":
            return None
        else:
            return GrpcSParameterModel(self._edb_model)

    @property
    def netlist_model(self):
        """Get assigned netlist model properties."""
        if not self.model_type == "NetlistModel":
            return None
        else:
            return GrpcNetlistModel(self._edb_model)

    @property
    def solder_ball_height(self):
        """Solder ball height if available."""
        if "GetSolderBallProperty" in dir(self.component_property):
            return self.component_property.solder_ball_property.height.value
        return None

    @solder_ball_height.setter
    def solder_ball_height(self, value):
        if "solder_ball_property" in dir(self.component_property):
            sball_height = round(EDBValue(value).value, 9)
            cmp_property = self.component_property
            solder_ball_prop = cmp_property.solder_ball_property
            solder_ball_prop.height = EDBValue(sball_height)
            cmp_property.solder_ball_property = solder_ball_prop
            self.component_property = cmp_property

    @property
    def solder_ball_shape(self):
        """Solder ball shape."""
        if "GetSolderBallProperty" in dir(self.component_property):
            shape = self.component_property.solder_ball_property.shape
            if shape == SolderballShape.NO_SOLDERBALL:
                return "None"
            elif shape == SolderballShape.SOLDERBALL_CYLINDER:
                return "Cylinder"
            elif shape == SolderballShape.SOLDERBALL_SPHEROID:
                return "Spheroid"

    @solder_ball_shape.setter
    def solder_ball_shape(self, value):
        shape = None
        if isinstance(value, str):
            if value.lower() == "cylinder":
                shape = SolderballShape.SOLDERBALL_CYLINDER
            elif value.lower() == "none":
                shape = SolderballShape.NO_SOLDERBALL
            elif value.lower() == "spheroid":
                shape = SolderballShape.SOLDERBALL_SPHEROID
        if isinstance(value, int):
            if value == 0:
                shape = SolderballShape.NO_SOLDERBALL
            elif value == 1:
                shape = SolderballShape.SOLDERBALL_CYLINDER
            elif value == 2:
                shape = SolderballShape.SOLDERBALL_SPHEROID
        if shape:
            cmp_property = self.component_property
            solder_ball_prop = cmp_property.solder_ball_property
            solder_ball_prop.shape = shape
            cmp_property.solder_ball_property = solder_ball_prop
            self.component_property = cmp_property

    @property
    def solder_ball_diameter(self):
        """Solder ball diameter."""
        if "solder_ball_property" in dir(self.component_property):
            diameter, mid_diameter = self.component_property.solder_ball_property.get_diameter()
            return diameter.value, mid_diameter.value

    @solder_ball_diameter.setter
    def solder_ball_diameter(self, value):
        diameter = None
        mid_diameter = None  # used with spheroid shape
        if isinstance(value, tuple) or isinstance(value, list):
            if len(value) == 2:
                diameter = EDBValue(value[0])
                mid_diameter = EDBValue(value[1])
            elif len(value) == 1:
                diameter = EDBValue(value[0])
                mid_diameter = EDBValue(value[0])
        if isinstance(value, str):
            diameter = EDBValue(value)
            mid_diameter = EDBValue(value)
        if diameter and mid_diameter:
            cmp_property = self.component_property
            solder_ball_prop = cmp_property.solder_ball_property
            solder_ball_prop.set_diameter(diameter, mid_diameter)
            cmp_property.solder_ball_property = solder_ball_prop
            self.component_property = cmp_property

    @property
    def solder_ball_placement(self):
        """Solder ball placement if available.."""
        if "solder_ball_property" in dir(self.component_property):
            solder_placement = self.component_property.solder_ball_property.placement
            return solder_placement.value

    @property
    def refdes(self):
        """Reference Designator Name.

        Returns
        -------
        str
            Reference Designator Name.
        """
        return self.name

    @refdes.setter
    def refdes(self, name):
        self.name = name

    @property
    def model_type(self):
        """Retrieve assigned model type."""
        _model_type = str(self._edb_model).split(".")[-1]
        if _model_type == "PinPairModel":
            return "RLC"
        else:
            return _model_type

    @property
    def rlc_values(self):
        """Get component rlc values."""
        if not len(self._pin_pairs):
            return [None, None, None]
        pin_pair = self._pin_pairs[0]
        return pin_pair.rlc_values

    @rlc_values.setter
    def rlc_values(self, value):
        if isinstance(value, list):  # pragma no cover
            rlc_enabled = [True if i else False for i in value]
            rlc_values = [EDBValue(i) for i in value]
            model = PinPairModel(self._pedb)
            pin_names = list(self.pins.keys())
            for idx, i in enumerate(np.arange(len(pin_names) // 2)):
                pin_pair = (pin_names[idx], pin_names[idx + 1])
                rlc = model.get_rlc(pin_pair)
                rlc.r = EDBValue(rlc_values[0])
                rlc.r_enabled = rlc_enabled[0]
                rlc.l = EDBValue(rlc_values[1])
                rlc.l_enabled = rlc_enabled[1]
                rlc.c = EDBValue(rlc_values[2])
                rlc.c_enabled = rlc_enabled[2]
                rlc.is_parallel = False
                model.set_rlc(pin_pair, rlc)
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
                return
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
            return self.netlist_model.netlist

    @value.setter
    def value(self, value):
        rlc_enabled = [True if i == self.type else False for i in ["Resistor", "Inductor", "Capacitor"]]
        rlc_values = [value if i == self.type else 0 for i in ["Resistor", "Inductor", "Capacitor"]]
        rlc_values = [EDBValue(i) for i in rlc_values]

        model = PinPairModel(self._pedb)._edb_object
        pin_names = list(self.pins.keys())
        for idx, i in enumerate(np.arange(len(pin_names) // 2)):
            pin_pair = (pin_names[idx], pin_names[idx + 1])
            rlc = model.get_rlc(pin_pair)
            rlc = model.get_rlc(pin_pair)
            rlc.r = EDBValue(rlc_values[0])
            rlc.r_enabled = rlc_enabled[0]
            rlc.l = EDBValue(rlc_values[1])
            rlc.l_enabled = rlc_enabled[1]
            rlc.c = EDBValue(rlc_values[2])
            rlc.c_enabled = rlc_enabled[2]
            rlc.is_parallel = False
            model.set_rlc(pin_pair, rlc)
        self._set_model(model)

    @property
    def res_value(self):
        """Resistance value.

        Returns
        -------
        str
            Resistance value or ``None`` if not an RLC type.
        """
        cmp_type = self.component_type
        if 0 < cmp_type.value < 4:
            model = self.component_property.model
            pinpairs = model.pin_pair_model
            if not list(pinpairs):
                return "0"
            for pinpair in pinpairs:
                pair = model.get_rlc(pinpair)
                return str(pair.r.value)
        return None

    @res_value.setter
    def res_value(self, value):  # pragma no cover
        if value:
            if self.rlc_values == [None, None, None]:
                self.rlc_values = [EDBValue(value), EDBValue(0), EDBValue(0)]
            else:
                self.rlc_values = [EDBValue(value), EDBValue(self.rlc_values[1]), EDBValue(self.rlc_values[2])]

    @property
    def cap_value(self):
        """Capacitance Value.

        Returns
        -------
        str
            Capacitance Value. ``None`` if not an RLC Type.
        """
        cmp_type = self.component_type
        if 0 < cmp_type.value < 4:
            model = self.component_property.model
            pinpairs = model.pin_pair_model
            if not list(pinpairs):
                return "0"
            for pinpair in pinpairs:
                pair = model.get_rlc(pinpair)
                return str(pair.c.value)
        return None

    @cap_value.setter
    def cap_value(self, value):  # pragma no cover
        if value:
            if self.rlc_values == [None, None, None]:
                self.rlc_values = [EDBValue(0), EDBValue(0), EDBValue(value)]
            else:
                self.rlc_values = [EDBValue(self.rlc_values[1]), EDBValue(self.rlc_values[2]), EDBValue(value)]

    @property
    def ind_value(self):
        """Inductance Value.

        Returns
        -------
        str
            Inductance Value. ``None`` if not an RLC Type.
        """
        cmp_type = self.component_type
        if 0 < cmp_type.value < 4:
            model = self.component_property.model
            pinpairs = model.pin_pair_model
            if not list(pinpairs):
                return "0"
            for pinpair in pinpairs:
                pair = model.get_rlc(pinpair)
                return str(pair.l.value)
        return None

    @ind_value.setter
    def ind_value(self, value):  # pragma no cover
        if value:
            if self.rlc_values == [None, None, None]:
                self.rlc_values = [EDBValue(0), EDBValue(value), EDBValue(0)]
            else:
                self.rlc_values = [EDBValue(self.rlc_values[1]), EDBValue(value), EDBValue(self.rlc_values[2])]

    @property
    def is_parallel_rlc(self):
        """Define if model is Parallel or Series.

        Returns
        -------
        bool
            ``True`` if it is a parallel rlc model. ``False`` for series RLC. ``None`` if not an RLC Type.
        """
        cmp_type = self.component_type
        if 0 < cmp_type.value < 4:
            model = self.component_property.model
            pinpairs = model.pin_pair_model
            for pinpair in pinpairs:
                pair = model.get_rlc(pinpair)
                return pair.is_parallel
        return None

    @is_parallel_rlc.setter
    def is_parallel_rlc(self, value):  # pragma no cover
        if not len(self._pin_pairs):
            logging.warning(self.refdes, " has no pin pair.")
        else:
            if isinstance(value, bool):
                model = self.component_property.model
                pinpairs = model.pin_pair_model
                if not list(pinpairs):
                    return "0"
                for pin_pair in pinpairs:
                    pin_pair_rlc = model.get_rlc(pin_pair)
                    pin_pair_rlc.is_parallel = value
                    pin_pair_model = self._edb_model
                    pin_pair_model.set_rlc(pin_pair, pin_pair_rlc)
                    comp_prop = self.component_property
                    comp_prop.model = pin_pair_model
                    self.component_property = comp_prop

    @property
    def center(self):
        """Compute the component center.

        Returns
        -------
        list
        """
        center = self.component_instance.location
        return [center[0].value, center[1].value]

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
        bbox = self.component_instance.bbox
        pt1 = bbox[0]
        pt2 = bbox[1]
        return [pt1[0][0].value, pt1[0][1].value, pt2[1][0].value, pt2[1][1].value]

    @property
    def rotation(self):
        """Compute the component rotation in radian.

        Returns
        -------
        float
        """
        return self.transform.rotation.value

    @property
    def pinlist(self):
        """Pins of the component.

        Returns
        -------
        list
            List of Pins of Component.
        """
        pins = [p for p in self.members if p.is_layout_pin]
        return pins

    @property
    def nets(self):
        """Nets of Component.

        Returns
        -------
        list
            List of Nets of Component.
        """
        return list(set([pin.net.name for pin in self.pinlist]))

    @property
    def pins(self):
        """EDBPadstackInstance of Component.

        Returns
        -------
        dic[str, :class:`dotnet.edb_core.edb_data.definitions.EDBPadstackInstance`]
            Dictionary of EDBPadstackInstance Components.
        """
        pins = {}
        for el in self.pinlist:
            pins[el.name] = PadstackInstance(el, self._pedb)
        return pins

    @property
    def type(self):
        """Component type.

        Returns
        -------
        str
            Component type.
        """
        return self.component_type.name

    @type.setter
    def type(self, new_type):
        """Set component type

        Parameters
        ----------
        new_type : str
            Type of the component. Options are ``"Resistor"``,  ``"Inductor"``, ``"Capacitor"``,
            ``"IC"``, ``"IO"`` and ``"Other"``.
        """
        new_type = new_type.lower()
        if new_type == "resistor":
            type_id = GrpcComponentType.RESISTOR
        elif new_type == "inductor":
            type_id = GrpcComponentType.INDUCTOR
        elif new_type == "capacitor":
            type_id = GrpcComponentType.CAPACITOR
        elif new_type == "ic":
            type_id = GrpcComponentType.IC
        elif new_type == "io":
            type_id = GrpcComponentType.IO
        elif new_type == "other":
            type_id = GrpcComponentType.OTHER
        else:
            return
        self.edbcomponent.component_type = type_id

    @property
    def numpins(self):
        """Number of Pins of Component.

        Returns
        -------
        int
            Number of Pins of Component.
        """
        return self.num_pins

    @property
    def partname(self):  # pragma: no cover
        """Component part name.

        Returns
        -------
        str
            Component Part Name.
        """
        return self.part_name

    @partname.setter
    def partname(self, name):  # pragma: no cover
        """Set component part name."""
        self.part_name = name

    @property
    def part_name(self):
        """Component part name.

        Returns
        -------
        str
            Component part name.
        """
        return self.component_def.name

    @part_name.setter
    def part_name(self, name):  # pragma: no cover
        """Set component part name."""
        self.component_def.name = name

    @property
    def placement_layer(self):
        """Placement layer.

        Returns
        -------
        str
           Name of the placement layer.
        """
        return self.placement_layer.name

    @property
    def is_top_mounted(self):
        """Check if a component is mounted on top or bottom of the layout.

        Returns
        -------
        bool
            ``True`` component is mounted on top, ``False`` on down.
        """
        signal_layers = [lay.name for lay in list(self._pedb.stackup.signal_layers.values())]
        if self.placement_layer in signal_layers[: int(len(signal_layers) / 2)]:
            return True
        return False

    @property
    def lower_elevation(self):
        """Lower elevation of the placement layer.

        Returns
        -------
        float
            Lower elevation of the placement layer.
        """
        layer = self.placement_layer
        return layer.lower_elevation

    @property
    def upper_elevation(self):
        """Upper elevation of the placement layer.

        Returns
        -------
        float
            Upper elevation of the placement layer.

        """
        layer = self.placement_layer()
        return layer.upper_elevation

    @property
    def top_bottom_association(self):
        """Top/bottom association of the placement layer.

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
        return self.placement_layer.top_bottom_association.value

    def _set_model(self, model):  # pragma: no cover
        comp_prop = self.component_property
        comp_prop.model = model
        self.component_property = comp_prop

    def assign_spice_model(
        self,
        file_path: str,
        name: Optional[str] = None,
        sub_circuit_name: Optional[str] = None,
        terminal_pairs: Optional[list] = None,
    ):
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
                    pin_names_sp = [i.strip() for i in re.split(" |\t", line) if i]
                    pin_names_sp.remove(pin_names_sp[0])
                    pin_names_sp.remove(pin_names_sp[0])
                    break
        if not len(pin_names_sp) == self.numpins:  # pragma: no cover
            raise ValueError(f"Pin counts doesn't match component {self.name}.")

        model = SpiceModel(self._pedb)
        model.model_path = file_path
        model.model_name = name
        if sub_circuit_name:
            model.sub_circuit = sub_circuit_name

        if terminal_pairs:
            terminal_pairs = terminal_pairs if isinstance(terminal_pairs[0], list) else [terminal_pairs]
            for pair in terminal_pairs:
                pname, pnumber = pair
                if pname not in pin_names_sp:  # pragma: no cover
                    raise ValueError(f"Pin name {pname} doesn't exist in {file_path}.")
                model.add_terminal(str(pnumber), pname)
        else:
            for idx, pname in enumerate(pin_names_sp):
                model.add_terminal(str(idx + 1), pname)

        return self._set_model(model)

    def assign_s_param_model(self, file_path, name=None, reference_net=None):
        """Assign S-parameter to this component.

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

        s_param_model = GrpcSParameterModel.find_by_name(self.component_def, name)
        if s_param_model.is_null:
            n_port_model = GrpcSParameterModel.create(name=name, ref_net=reference_net)
            n_port_model.reference_file = file_path
            self.component_def.add_component_model(n_port_model)

        model = GrpcSParameterModel()
        model.component_model = name
        if reference_net:
            model.reference_net = reference_net
        return self._set_model(model)

    def use_s_parameter_model(self, name, reference_net=None):
        """Use S-parameter model on the component.

        Parameters
        ----------
        name: str
            Name of the S-parameter model.
        reference_net: str, optional
            Reference net of the model.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> edbapp = Edb()
        >>>comp_def = edbapp.definitions.components["CAPC3216X180X55ML20T25"]
        >>>comp_def.add_n_port_model("c:GRM32_DC0V_25degC_series.s2p", "GRM32_DC0V_25degC_series")
        >>>edbapp.components["C200"].use_s_parameter_model("GRM32_DC0V_25degC_series")
        """
        model = GrpcSParameterModel()
        model.component_model = name
        if reference_net:
            model.reference_net = reference_net
        return self._set_model(model)

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
        res, ind, cap = EDBValue(res), EDBValue(ind), EDBValue(cap)
        model = PinPairModel(self._edb_model)._edb_object

        pin_names = list(self.pins.keys())
        for idx, i in enumerate(np.arange(len(pin_names) // 2)):
            pin_pair = GrpcPinPair(pin_names[idx], pin_names[idx + 1])
            rlc = GrpcRlc(
                r=res,
                r_enabled=r_enabled,
                l=ind,
                l_enabled=l_enabled,
                c=cap,
                c_enabled=c_enabled,
                is_parallel=is_parallel,
            )
            model.set_rlc(pin_pair, rlc)
        return self._set_model(model)

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
        layer_names = list(self._pedb.stackup.layers.keys())
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
