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

from pyedb.dotnet.edb_core.cell.hierarchy.hierarchy_obj import Group
from pyedb.dotnet.edb_core.cell.hierarchy.model import PinPairModel, SPICEModel
from pyedb.dotnet.edb_core.cell.hierarchy.netlist_model import NetlistModel
from pyedb.dotnet.edb_core.cell.hierarchy.pin_pair_model import PinPair
from pyedb.dotnet.edb_core.cell.hierarchy.s_parameter_model import SparamModel
from pyedb.dotnet.edb_core.cell.hierarchy.spice_model import SpiceModel
from pyedb.dotnet.edb_core.definition.package_def import PackageDef
from pyedb.dotnet.edb_core.edb_data.padstacks_data import EDBPadstackInstance
from pyedb.dotnet.edb_core.general import pascal_to_snake, snake_to_pascal

try:
    import numpy as np
except ImportError:
    warnings.warn(
        "The NumPy module is required to run some functionalities of EDB.\n"
        "Install with \n\npip install numpy\n\nRequires CPython."
    )
from pyedb.generic.general_methods import get_filename_without_extension


class EDBComponent(Group):
    """Manages EDB functionalities for components.

    Parameters
    ----------
    parent : :class:`pyedb.dotnet.edb_core.components.Components`
        Components object.
    component : object
        Edb Component Object

    """

    def __init__(self, pedb, edb_object):
        super().__init__(pedb, edb_object)
        self.edbcomponent = edb_object
        self._layout_instance = None
        self._comp_instance = None

    @property
    def name(self):
        """Name of the definition."""
        return self._edb_object.GetName()

    @name.setter
    def name(self, value):
        self._edb_object.SetName(value)

    @property
    def group_type(self):
        return self._edb_object.ToString().split(".")[-1].lower()

    @property
    def layout_instance(self):
        """EDB layout instance object."""
        return self._pedb.layout_instance

    @property
    def component_instance(self):
        """Edb component instance."""
        if self._comp_instance is None:
            self._comp_instance = self.layout_instance.GetLayoutObjInstance(self.edbcomponent, None)
        return self._comp_instance

    @property
    def _active_layout(self):  # pragma: no cover
        return self._pedb.active_layout

    @property
    def component_property(self):
        """``ComponentProperty`` object."""
        return self.edbcomponent.GetComponentProperty().Clone()

    @component_property.setter
    def component_property(self, value):
        if value:
            self.edbcomponent.SetComponentProperty(value)

    @property
    def _edb_model(self):  # pragma: no cover
        return self.component_property.GetModel().Clone()

    @property  # pragma: no cover
    def _pin_pairs(self):
        edb_comp_prop = self.component_property
        edb_model = self._edb_model
        return [
            PinPair(self, self.edbcomponent, edb_comp_prop, edb_model, pin_pair)
            for pin_pair in list(edb_model.PinPairs)
        ]

    @property
    def model(self):
        """Component model."""
        edb_object = self.component_property.GetModel().Clone()
        model_type = edb_object.ToString().split(".")[-1]
        if model_type == "PinPairModel":
            return PinPairModel(self._pedb, edb_object)
        elif model_type == "SPICEModel":
            return SPICEModel(self._pedb, edb_object)

    @model.setter
    def model(self, value):
        if not isinstance(value, PinPairModel):
            self._pedb.logger.error("Invalid input. Set model failed.")

        comp_prop = self.component_property
        comp_prop.SetModel(value._edb_object)
        self.edbcomponent.SetComponentProperty(comp_prop)

    @property
    def package_def(self):
        """Package definition."""
        edb_object = self.component_property.GetPackageDef()

        package_def = PackageDef(self._pedb, edb_object)
        if not package_def.is_null:
            return package_def

    @package_def.setter
    def package_def(self, value):
        package_def = self._pedb.definitions.package[value]
        comp_prop = self.component_property
        comp_prop.SetPackageDef(package_def._edb_object)
        self.edbcomponent.SetComponentProperty(comp_prop)

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

            from pyedb.dotnet.edb_core.dotnet.database import PolygonDataDotNet

            polygon = PolygonDataDotNet(self._pedb).create_from_bbox(self.component_instance.GetBBox())
            self.package_def._edb_object.SetExteriorBoundary(polygon)
            return True
        else:
            logging.error(f"Package definition {name} already exists")
            return False

    @property
    def is_enabled(self):
        """Get or Set the component to active mode.

        Returns
        -------
        bool
            ``True`` if component is active, ``False`` if is disabled..
        """
        warnings.warn("Use new property :func:`enabled` instead.", DeprecationWarning)
        return self.enabled

    @is_enabled.setter
    def is_enabled(self, value):
        warnings.warn("Use new property :func:`enabled` instead.", DeprecationWarning)
        self.enabled = value

    @property
    def enabled(self):
        """Get or Set the component to active mode."""
        if self.type.lower() in ["resistor", "capacitor", "inductor"]:
            return self.component_property.IsEnabled()
        else:
            return

    @enabled.setter
    def enabled(self, value):
        cmp_prop = self.component_property.Clone()
        cmp_prop.SetEnabled(value)
        self.edbcomponent.SetComponentProperty(cmp_prop)

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
            return SparamModel(self._edb_model)

    @property
    def netlist_model(self):
        """Get assigned netlist model properties."""
        if not self.model_type == "NetlistModel":
            return None
        else:
            return NetlistModel(self._edb_model)

    @property
    def solder_ball_height(self):
        """Solder ball height if available."""
        if "GetSolderBallProperty" in dir(self.component_property):
            return self.component_property.GetSolderBallProperty().GetHeight()
        return None

    @solder_ball_height.setter
    def solder_ball_height(self, value):
        if "GetSolderBallProperty" in dir(self.component_property):
            sball_height = round(self._edb.utility.Value(value).ToDouble(), 9)
            cmp_property = self.component_property
            solder_ball_prop = cmp_property.GetSolderBallProperty().Clone()
            solder_ball_prop.SetHeight(self._get_edb_value(sball_height))
            cmp_property.SetSolderBallProperty(solder_ball_prop)
            self.component_property = cmp_property

    @property
    def solder_ball_shape(self):
        """Solder ball shape."""
        if "GetSolderBallProperty" in dir(self.component_property):
            shape = self.component_property.GetSolderBallProperty().GetShape()
            if shape.value__ == 0:
                return "None"
            elif shape.value__ == 1:
                return "Cylinder"
            elif shape.value__ == 2:
                return "Spheroid"

    @solder_ball_shape.setter
    def solder_ball_shape(self, value):
        shape = None
        if isinstance(value, str):
            if value.lower() == "cylinder":
                shape = self._edb.definition.SolderballShape.Cylinder
            elif value.lower() == "none":
                shape = self._edb.definition.SolderballShape.NoSolderball
            elif value.lower() == "spheroid":
                shape = self._edb.definition.SolderballShape.Spheroid
        if isinstance(value, int):
            if value == 0:
                shape = self._edb.definition.SolderballShape.NoSolderball
            elif value == 1:
                shape = self._edb.definition.SolderballShape.Cylinder
            elif value == 2:
                shape = self._edb.definition.SolderballShape.Spheroid
        if shape:
            cmp_property = self.component_property
            solder_ball_prop = cmp_property.GetSolderBallProperty().Clone()
            solder_ball_prop.SetShape(shape)
            cmp_property.SetSolderBallProperty(solder_ball_prop)
            self.component_property = cmp_property

    @property
    def solder_ball_diameter(self):
        """Solder ball diameter."""
        if "GetSolderBallProperty" in dir(self.component_property):
            result = self.component_property.GetSolderBallProperty().GetDiameter()
            succeed = result[0]
            diameter = result[1]
            mid_diameter = result[2]
            if succeed:
                return diameter, mid_diameter

    @solder_ball_diameter.setter
    def solder_ball_diameter(self, value):
        diameter = None
        mid_diameter = None  # used with spheroid shape
        if isinstance(value, tuple) or isinstance(value, list):
            if len(value) == 2:
                diameter = self._get_edb_value(value[0])
                mid_diameter = self._get_edb_value(value[1])
            elif len(value) == 1:
                diameter = self._get_edb_value(value[0])
                mid_diameter = self._get_edb_value(value[0])
        if isinstance(value, str):
            diameter = self._get_edb_value(value)
            mid_diameter = self._get_edb_value(value)
        if diameter and mid_diameter:
            cmp_property = self.component_property
            solder_ball_prop = cmp_property.GetSolderBallProperty().Clone()
            solder_ball_prop.SetDiameter(diameter, mid_diameter)
            cmp_property.SetSolderBallProperty(solder_ball_prop)
            self.component_property = cmp_property

    @property
    def solder_ball_placement(self):
        """Solder ball placement if available.."""
        if "GetSolderBallProperty" in dir(self.component_property):
            return int(self.component_property.GetSolderBallProperty().GetPlacement())
        return 2

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
    def is_null(self):
        """Flag indicating if the current object exists."""
        return self.edbcomponent.IsNull()

    @property
    def is_enabled(self):
        """Flag indicating if the current object is enabled.

        Returns
        -------
        bool
            ``True`` if current object is enabled, ``False`` otherwise.
        """
        if self.type in ["Resistor", "Capacitor", "Inductor"]:
            return self.component_property.IsEnabled()
        else:  # pragma: no cover
            return True

    @is_enabled.setter
    def is_enabled(self, enabled):
        """Enables the current object."""
        if self.type in ["Resistor", "Capacitor", "Inductor"]:
            component_property = self.component_property
            component_property.SetEnabled(enabled)
            self.edbcomponent.SetComponentProperty(component_property)

    @property
    def model_type(self):
        """Retrieve assigned model type."""
        _model_type = self._edb_model.ToString().split(".")[-1]
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
            rlc_values = [self._get_edb_value(i) for i in value]
            model = self._edb.cell.hierarchy._hierarchy.PinPairModel()
            pin_names = list(self.pins.keys())
            for idx, i in enumerate(np.arange(len(pin_names) // 2)):
                pin_pair = self._edb.utility.utility.PinPair(pin_names[idx], pin_names[idx + 1])
                rlc = self._edb.utility.utility.Rlc(
                    rlc_values[0], rlc_enabled[0], rlc_values[1], rlc_enabled[1], rlc_values[2], rlc_enabled[2], False
                )
                model.SetPinPairRlc(pin_pair, rlc)
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
        rlc_values = [self._get_edb_value(i) for i in rlc_values]

        model = self._edb.cell.hierarchy._hierarchy.PinPairModel()
        pin_names = list(self.pins.keys())
        for idx, i in enumerate(np.arange(len(pin_names) // 2)):
            pin_pair = self._edb.utility.utility.PinPair(pin_names[idx], pin_names[idx + 1])
            rlc = self._edb.utility.utility.Rlc(
                rlc_values[0], rlc_enabled[0], rlc_values[1], rlc_enabled[1], rlc_values[2], rlc_enabled[2], False
            )
            model.SetPinPairRlc(pin_pair, rlc)
        self._set_model(model)

    @property
    def res_value(self):
        """Resistance value.

        Returns
        -------
        str
            Resistance value or ``None`` if not an RLC type.
        """
        cmp_type = int(self.edbcomponent.GetComponentType())
        if 0 < cmp_type < 4:
            componentProperty = self.edbcomponent.GetComponentProperty()
            model = componentProperty.GetModel().Clone()
            pinpairs = model.PinPairs
            if not list(pinpairs):
                return "0"
            for pinpair in pinpairs:
                pair = model.GetPinPairRlc(pinpair)
                return pair.R.ToString()
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
        cmp_type = int(self.edbcomponent.GetComponentType())
        if 0 < cmp_type < 4:
            componentProperty = self.edbcomponent.GetComponentProperty()
            model = componentProperty.GetModel().Clone()
            pinpairs = model.PinPairs
            if not list(pinpairs):
                return "0"
            for pinpair in pinpairs:
                pair = model.GetPinPairRlc(pinpair)
                return pair.C.ToString()
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
        cmp_type = int(self.edbcomponent.GetComponentType())
        if 0 < cmp_type < 4:
            componentProperty = self.edbcomponent.GetComponentProperty()
            model = componentProperty.GetModel().Clone()
            pinpairs = model.PinPairs
            if not list(pinpairs):
                return "0"
            for pinpair in pinpairs:
                pair = model.GetPinPairRlc(pinpair)
                return pair.L.ToString()
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
        cmp_type = int(self.edbcomponent.GetComponentType())
        if 0 < cmp_type < 4:
            model = self.component_property.GetModel().Clone()
            pinpairs = model.PinPairs
            for pinpair in pinpairs:
                pair = model.GetPinPairRlc(pinpair)
                return pair.IsParallel
        return None

    @is_parallel_rlc.setter
    def is_parallel_rlc(self, value):  # pragma no cover
        if not len(self._pin_pairs):
            logging.warning(self.refdes, " has no pin pair.")
        else:
            if isinstance(value, bool):
                componentProperty = self.edbcomponent.GetComponentProperty()
                model = componentProperty.GetModel().Clone()
                pinpairs = model.PinPairs
                if not list(pinpairs):
                    return "0"
                for pin_pair in pinpairs:
                    pin_pair_rlc = model.GetPinPairRlc(pin_pair)
                    pin_pair_rlc.IsParallel = value
                    pin_pair_model = self._edb_model
                    pin_pair_model.SetPinPairRlc(pin_pair, pin_pair_rlc)
                    comp_prop = self.component_property
                    comp_prop.SetModel(pin_pair_model)
                    self.edbcomponent.SetComponentProperty(comp_prop)

    @property
    def center(self):
        """Compute the component center.

        Returns
        -------
        list
        """
        center = self.component_instance.GetCenter()
        return [center.X.ToDouble(), center.Y.ToDouble()]

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
        bbox = self.component_instance.GetBBox()
        pt1 = bbox.Item1
        pt2 = bbox.Item2
        return [pt1.X.ToDouble(), pt1.Y.ToDouble(), pt2.X.ToDouble(), pt2.Y.ToDouble()]

    @property
    def rotation(self):
        """Compute the component rotation in radian.

        Returns
        -------
        float
        """
        return self.edbcomponent.GetTransform().Rotation.ToDouble()

    @property
    def pinlist(self):
        """Pins of the component.

        Returns
        -------
        list
            List of Pins of Component.
        """
        pins = [
            p
            for p in self.edbcomponent.LayoutObjs
            if p.GetObjType() == self._edb.cell.layout_object_type.PadstackInstance
            and p.IsLayoutPin()
            and p.GetComponent().GetName() == self.refdes
        ]
        return pins

    @property
    def nets(self):
        """Nets of Component.

        Returns
        -------
        list
            List of Nets of Component.
        """
        netlist = []
        for pin in self.pinlist:
            netlist.append(pin.GetNet().GetName())
        return list(set(netlist))

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
            pins[el.GetName()] = EDBPadstackInstance(el, self._pedb)
        return pins

    @property
    def type(self):
        """Component type.

        Returns
        -------
        str
            Component type.
        """
        cmp_type = int(self.edbcomponent.GetComponentType())
        if cmp_type == 1:
            return "Resistor"
        elif cmp_type == 2:
            return "Inductor"
        elif cmp_type == 3:
            return "Capacitor"
        elif cmp_type == 4:
            return "IC"
        elif cmp_type == 5:
            return "IO"
        elif cmp_type == 0:
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
        new_type = new_type.lower()
        if new_type == "resistor":
            type_id = self._pedb.definition.ComponentType.Resistor
        elif new_type == "inductor":
            type_id = self._pedb.definition.ComponentType.Inductor
        elif new_type == "capacitor":
            type_id = self._pedb.definition.ComponentType.Capacitor
        elif new_type == "ic":
            type_id = self._pedb.definition.ComponentType.IC
        elif new_type == "io":
            type_id = self._pedb.definition.ComponentType.IO
        elif new_type == "other":
            type_id = self._pedb.definition.ComponentType.Other
        else:
            return
        self.edbcomponent.SetComponentType(type_id)

    @property
    def numpins(self):
        """Number of Pins of Component.

        Returns
        -------
        int
            Number of Pins of Component.
        """
        return self.edbcomponent.GetNumberOfPins()

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
        return self.edbcomponent.GetComponentDef().GetName()

    @part_name.setter
    def part_name(self, name):  # pragma: no cover
        """Set component part name."""
        self.edbcomponent.GetComponentDef().SetName(name)

    @property
    def placement_layer(self):
        """Placement layer.

        Returns
        -------
        str
           Name of the placement layer.
        """
        return self.edbcomponent.GetPlacementLayer().Clone().GetName()

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
        return self.edbcomponent.GetPlacementLayer().Clone().GetLowerElevation()

    @property
    def upper_elevation(self):
        """Upper elevation of the placement layer.

        Returns
        -------
        float
            Upper elevation of the placement layer.

        """
        return self.edbcomponent.GetPlacementLayer().Clone().GetUpperElevation()

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
        return int(self.edbcomponent.GetPlacementLayer().GetTopBottomAssociation())

    def _get_edb_value(self, value):
        return self._pedb.edb_value(value)

    def _set_model(self, model):  # pragma: no cover
        comp_prop = self.component_property
        comp_prop.SetModel(model)
        if not self.edbcomponent.SetComponentProperty(comp_prop):
            logging.error("Fail to assign model on {}.".format(self.refdes))
            return False
        return True

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
        sub_circuit_name : str, optional
            Name of the sub circuit.
        terminal_pairs : list, optional
            list of terminal pairs.

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

        model = self._edb.cell.hierarchy._hierarchy.SPICEModel()
        model.SetModelPath(file_path)
        model.SetModelName(name)
        if sub_circuit_name:
            model.SetSubCkt(sub_circuit_name)

        if terminal_pairs:
            terminal_pairs = terminal_pairs if isinstance(terminal_pairs[0], list) else [terminal_pairs]
            for pair in terminal_pairs:
                pname, pnumber = pair
                if pname not in pin_names_sp:  # pragma: no cover
                    raise ValueError(f"Pin name {pname} doesn't exist in {file_path}.")
                model.AddTerminalPinPair(pname, str(pnumber))
        else:
            for idx, pname in enumerate(pin_names_sp):
                model.AddTerminalPinPair(pname, str(idx + 1))

        return self._set_model(model)

    def assign_s_param_model(self, file_path, name=None, reference_net=None):
        """Assign S-parameter to this component.

        Parameters
        ----------
        file_path : str
            File path of the S-parameter model.
        name : str, optional
            Name of the S-parameter model.
        reference_net : str, optional
            Name of the reference net.
        Returns
        -------

        """
        if not name:
            name = get_filename_without_extension(file_path)

        edbComponentDef = self.edbcomponent.GetComponentDef()
        nPortModel = self._edb.definition.NPortComponentModel.FindByName(edbComponentDef, name)
        if nPortModel.IsNull():
            nPortModel = self._edb.definition.NPortComponentModel.Create(name)
            nPortModel.SetReferenceFile(file_path)
            edbComponentDef.AddComponentModel(nPortModel)

        model = self._edb.cell.hierarchy._hierarchy.SParameterModel()
        model.SetComponentModelName(name)
        if reference_net:
            model.SetReferenceNet(reference_net)
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
        model = self._edb.cell.hierarchy._hierarchy.SParameterModel()
        model.SetComponentModelName(name)
        if reference_net:
            model.SetReferenceNet(reference_net)
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
        res, ind, cap = self._get_edb_value(res), self._get_edb_value(ind), self._get_edb_value(cap)
        model = self._edb.cell.hierarchy._hierarchy.PinPairModel()

        pin_names = list(self.pins.keys())
        for idx, i in enumerate(np.arange(len(pin_names) // 2)):
            pin_pair = self._edb.utility.utility.PinPair(pin_names[idx], pin_names[idx + 1])

            rlc = self._edb.utility.utility.Rlc(res, r_enabled, ind, l_enabled, cap, c_enabled, is_parallel)
            model.SetPinPairRlc(pin_pair, rlc)
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

    @property
    def model_properties(self):
        pp = {}
        c_p = self.component_property
        model = c_p.GetModel().Clone()
        netlist_model = {}
        pin_pair_model = []
        s_parameter_model = {}
        spice_model = {}
        if model.GetModelType().ToString() == "NetlistModel":
            netlist_model["netlist"] = model.GetNetlist()
        elif model.GetModelType().ToString() == "PinPairModel":
            temp = {}
            for i in model.PinPairs:
                temp["first_pin"] = i.FirstPin
                temp["second_pin"] = i.SecondPin
                rlc = model.GetPinPairRlc(i)
                temp["is_parallel"] = rlc.IsParallel
                temp["resistance"] = rlc.R.ToString()
                temp["resistance_enabled"] = rlc.REnabled
                temp["inductance"] = rlc.L.ToString()
                temp["inductance_enabled"] = rlc.LEnabled
                temp["capacitance"] = rlc.C.ToString()
                temp["capacitance_enabled"] = rlc.CEnabled
                pin_pair_model.append(temp)
        elif model.GetModelType().ToString() == "SParameterModel":
            s_parameter_model["reference_net"] = model.GetReferenceNet()
            s_parameter_model["model_name"] = model.GetComponentModelName()
        elif model.GetModelType().ToString() == "SPICEModel":
            spice_model["model_name"] = model.GetModelName()
            spice_model["model_path"] = model.GetModelPath()
            spice_model["sub_circuit"] = model.GetSubCkt()
            spice_model["terminal_pairs"] = [[i, j] for i, j in dict(model.GetTerminalPinPairs()).items()]

        if netlist_model:
            pp["netlist_model"] = netlist_model
        if pin_pair_model:
            pp["pin_pair_model"] = pin_pair_model
        if s_parameter_model:
            pp["s_parameter_model"] = s_parameter_model
        if spice_model:
            pp["spice_model"] = spice_model
        return pp

    @model_properties.setter
    def model_properties(self, kwargs):
        netlist_model = kwargs.get("netlist_model")
        pin_pair_model = kwargs.get("pin_pair_model")
        s_parameter_model = kwargs.get("s_parameter_model")
        spice_model = kwargs.get("spice_model")

        c_p = self.component_property
        if netlist_model:
            m = self._pedb._edb.Cell.Hierarchy.SParameterModel()
            m.SetNetlist(netlist_model["netlist"])
            c_p.SetModel(m)
            self.component_property = c_p
        elif pin_pair_model:
            m = self._pedb._edb.Cell.Hierarchy.PinPairModel()
            for i in pin_pair_model:
                p = self._pedb._edb.Utility.PinPair(str(i["first_pin"]), str(i["second_pin"]))
                rlc = self._pedb._edb.Utility.Rlc(
                    self._pedb.edb_value(i["resistance"]),
                    i["resistance_enabled"],
                    self._pedb.edb_value(i["inductance"]),
                    i["inductance_enabled"],
                    self._pedb.edb_value(i["capacitance"]),
                    i["capacitance_enabled"],
                    i["is_parallel"],
                )
                m.SetPinPairRlc(p, rlc)
            c_p.SetModel(m)
            self.component_property = c_p
        elif s_parameter_model:
            m = self._pedb._edb.Cell.Hierarchy.SParameterModel()
            m.SetComponentModelName(s_parameter_model["model_name"])
            m.SetReferenceNet(s_parameter_model["reference_net"])
            c_p.SetModel(m)
            self.component_property = c_p
        elif spice_model:
            self.assign_spice_model(
                spice_model["model_path"],
                spice_model["model_name"],
                spice_model["sub_circuit"],
                spice_model["terminal_pairs"],
            )

    @property
    def ic_die_properties(self):
        temp = dict()
        cp = self.component_property
        c_type = self.type.lower()
        if not c_type == "ic":
            return temp
        else:
            ic_die_prop = cp.GetDieProperty().Clone()
            die_type = pascal_to_snake(ic_die_prop.GetType().ToString())
            temp["type"] = die_type
            if not die_type == "no_die":
                temp["orientation"] = pascal_to_snake(ic_die_prop.GetOrientation().ToString())
                if die_type == "wire_bond":
                    temp["height"] = ic_die_prop.GetHeightValue().ToString()
            return temp

    @ic_die_properties.setter
    def ic_die_properties(self, kwargs):
        cp = self.component_property
        c_type = self.type.lower()
        if not c_type == "ic":
            return
        else:
            ic_die_prop = cp.GetDieProperty().Clone()
            die_type = kwargs.get("type")
            ic_die_prop.SetType(getattr(self._edb.definition.DieType, snake_to_pascal(die_type)))
            if not die_type == "no_die":
                orientation = kwargs.get("orientation")
                if orientation:
                    ic_die_prop.SetOrientation(
                        getattr(self._edb.definition.DieOrientation, snake_to_pascal(orientation))
                    )
                if die_type == "wire_bond":
                    height = kwargs.get("height")
                    if height:
                        ic_die_prop.SetHeight(self._pedb.edb_value(height))
            cp.SetDieProperty(ic_die_prop)
            self.component_property = cp

    @property
    def solder_ball_properties(self):
        temp = dict()
        cp = self.component_property
        c_type = self.type.lower()
        if c_type not in ["io", "other"]:
            return temp
        else:
            solder_ball_prop = cp.GetSolderBallProperty().Clone()
            _, diam, mid_diam = solder_ball_prop.GetDiameterValue()
            height = solder_ball_prop.GetHeightValue().ToString()
            shape = solder_ball_prop.GetShape().ToString()
            uses_solder_ball = solder_ball_prop.UsesSolderball()
            temp["uses_solder_ball"] = uses_solder_ball
            temp["shape"] = pascal_to_snake(shape)
            temp["diameter"] = diam.ToString()
            temp["mid_diameter"] = mid_diam.ToString()
            temp["height"] = height
            return temp

    @solder_ball_properties.setter
    def solder_ball_properties(self, kwargs):
        cp = self.component_property
        solder_ball_prop = cp.GetSolderBallProperty().Clone()
        shape = kwargs.get("shape")
        if shape:
            solder_ball_prop.SetShape(getattr(self._edb.definition.SolderballShape, snake_to_pascal(shape)))
        if shape == "cylinder":
            diameter = kwargs["diameter"]
            solder_ball_prop.SetDiameter(self._pedb.edb_value(diameter), self._pedb.edb_value(diameter))
        elif shape == "spheroid":
            diameter = kwargs["diameter"]
            mid_diameter = kwargs["mid_diameter"]
            solder_ball_prop.SetDiameter(self._pedb.edb_value(diameter), self._pedb.edb_value(mid_diameter))
        else:
            return
        solder_ball_prop.SetHeight(self._get_edb_value(kwargs["height"]))
        cp.SetSolderBallProperty(solder_ball_prop)
        self.component_property = cp

    @property
    def port_properties(self):
        temp = dict()
        cp = self.component_property
        c_type = self.type.lower()
        if c_type not in ["ic", "io", "other"]:
            return temp
        else:
            port_prop = cp.GetPortProperty().Clone()
            reference_height = port_prop.GetReferenceHeightValue().ToString()
            reference_size_auto = port_prop.GetReferenceSizeAuto()
            _, reference_size_x, reference_size_y = port_prop.GetReferenceSize()
            temp["reference_height"] = reference_height
            temp["reference_size_auto"] = reference_size_auto
            temp["reference_size_x"] = str(reference_size_x)
            temp["reference_size_y"] = str(reference_size_y)
            return temp

    @port_properties.setter
    def port_properties(self, kwargs):
        cp = self.component_property
        port_prop = cp.GetPortProperty().Clone()
        height = kwargs.get("reference_height")
        if height:
            port_prop.SetReferenceHeight(self._pedb.edb_value(height))
        reference_size_auto = kwargs.get("reference_size_auto")
        if reference_size_auto:
            port_prop.SetReferenceSizeAuto(reference_size_auto)
        reference_size_x = kwargs.get("reference_size_x", 0)
        reference_size_y = kwargs.get("reference_size_y", 0)
        port_prop.SetReferenceSize(self._pedb.edb_value(reference_size_x), self._pedb.edb_value(reference_size_y))
        cp.SetPortProperty(port_prop)
        self.component_property = cp
