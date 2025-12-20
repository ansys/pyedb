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

import logging
import re
from typing import List, Optional, Union
import warnings

from ansys.edb.core.definition.component_model import (
    NPortComponentModel as GrpcNPortComponentModel,
)
from ansys.edb.core.definition.die_property import DieOrientation as GrpcDieOrientation, DieType as GrpcDieType
from ansys.edb.core.definition.solder_ball_property import SolderballShape
from ansys.edb.core.geometry.polygon_data import PolygonData as GrpcPolygonData
from ansys.edb.core.hierarchy.component_group import ComponentType as GrpcComponentType
from ansys.edb.core.hierarchy.netlist_model import NetlistModel as GrpcNetlistModel
from ansys.edb.core.hierarchy.pin_pair_model import PinPairModel as GrpcPinPairModel
from ansys.edb.core.hierarchy.sparameter_model import (
    SParameterModel as GrpcSParameterModel,
)
from ansys.edb.core.hierarchy.spice_model import SPICEModel as GrpcSPICEModel
from ansys.edb.core.primitive.padstack_instance import (
    PadstackInstance as GrpcPadstackInstance,
)
from ansys.edb.core.terminal.padstack_instance_terminal import (
    PadstackInstanceTerminal as GrpcPadstackInstanceTerminal,
)
from ansys.edb.core.utility.rlc import Rlc as GrpcRlc
import numpy as np

from pyedb.generic.general_methods import get_filename_without_extension
from pyedb.grpc.database.hierarchy.pin_pair_model import PinPairModel
from pyedb.grpc.database.hierarchy.s_parameter_model import SparamModel
from pyedb.grpc.database.hierarchy.spice_model import SpiceModel
from pyedb.grpc.database.layers.stackup_layer import StackupLayer
from pyedb.grpc.database.primitive.padstack_instance import PadstackInstance
from pyedb.grpc.database.terminal.padstack_instance_terminal import (
    PadstackInstanceTerminal,
)
from pyedb.grpc.database.utility.value import Value

component_type_mapping = {
    GrpcComponentType.OTHER: "other",
    GrpcComponentType.RESISTOR: "resistor",
    GrpcComponentType.INDUCTOR: "inductor",
    GrpcComponentType.CAPACITOR: "capacitor",
    GrpcComponentType.IC: "ic",
    GrpcComponentType.IO: "io",
    GrpcComponentType.INVALID: "invalid",
}


class Component:
    """Manages EDB functionalities for components.

    Parameters
    ----------
    parent : :class:`pyedb.grpc.database.components.Components`
        Components object.
    component : object
        Edb Component Object

    """

    def __init__(self, pedb, edb_object):
        self.core = edb_object
        self._pedb = pedb
        self._layout_instance = None
        self._comp_instance = None
        self._logger = pedb.logger
        self._package_def = None

    @property
    def group_type(self):
        return str(self.core.type).split(".")[-1].lower()

    @property
    def is_null(self):
        """Check if the component is null.

        Returns
        -------
        bool
            True if the component is null, False otherwise.
        """
        return self.core.is_null

    @property
    def component_type(self) -> str:
        """Component type.

        Returns
        -------
        str
        """
        return component_type_mapping[self.core.component_type]

    @component_type.setter
    def component_type(self, value):
        reverse_mapping = {v: k for k, v in component_type_mapping.items()}
        if value in reverse_mapping:
            self.core.component_type = GrpcComponentType(reverse_mapping[value])
        else:
            self._pedb.logger.error(f"Invalid component type: {value}")

    @property
    def layout_instance(self):
        """Layout instance object.

        Returns
        -------
        :class:`LayoutInstance <ansys.edb.core.layout_instance.layout_instance.LayoutInstance>`
        """
        return self._pedb.layout_instance

    @property
    def component_instance(self):
        """Component instance.

        Returns
        -------
        :class:`LayoutObjInstance <ansys.edb.core.layout_instance.layout_obj_instance.LayoutObjInstance>`
        """
        if self._comp_instance is None:
            self._comp_instance = self.layout_instance.get_layout_obj_instance_in_context(self.core, None)
        return self._comp_instance

    @property
    def is_enabled(self) -> bool:
        """Component enable.

        Returns
        -------
        bool

        """
        comp_prop = self.core.component_property
        if hasattr(comp_prop, "enabled"):
            return comp_prop.enabled
        else:
            return True

    @is_enabled.setter
    def is_enabled(self, value):
        comp_prop = self.core.component_property
        if hasattr(comp_prop, "enabled"):
            comp_prop.enabled = value
            self.core.component_property = comp_prop

    @property
    def ic_die_properties(self) -> any:
        """IC Die property.

        returns
        -------
        :class:`ICDieProperty <pyedb.grpc.database.hierarchy.component.ICDieProperty>`
        """
        if self.type == "ic":
            return ICDieProperty(self)
        else:
            return None

    @property
    def _active_layout(self):
        """Active layout.

        Returns
        -------
        :class:`Layout <ansys.edb.core.layout.layout.Layout>
        """
        return self._pedb.active_layout

    @property
    def _edb_model(self):
        """Component model.

        Returns
        -------
        :class:`Model <ansys.edb.core.hierarchy.model.Model>`

        """
        comp_prop = self.core.component_property
        return comp_prop.model

    @property  # pragma: no cover
    def _pin_pairs(self) -> PinPairModel:
        """Pins pairs.

        Returns
        -------
        :class:`PinPairModel <ansys.edb.core.hierarchy.pin_pair_model.PinPairModel>`
        """
        edb_model = self._edb_model
        return edb_model.pin_pairs()

    @property
    def _rlc(self):
        """Rlc class.

        Returns
        -------
        :class:`Rlc <ansys.edb.core.utility.rlc.Rlc>`

        """
        if self.model_type == "SPICEModel":
            if len(self.pins) == 2:
                self._pedb.logger.warning(f"Spice model defined on component {self.name}, replacing model by ")
                rlc = GrpcRlc()
                pins = list(self.pins.keys())
                pin_pair = (pins[0], pins[1])
                rlc_model = PinPairModel(self._pedb, GrpcPinPairModel.create())
                rlc_model.set_rlc(pin_pair, rlc)
                component_property = self.component_property
                component_property.model = rlc_model
                self.component_property = component_property
        return [self._edb_model.rlc(pin_pair) for pin_pair in self._edb_model.pin_pairs()]

    @property
    def component_definition(self):
        """Component definition.

        Returns
        -------
        :class:`ComponentDef <ansys.edb.core.definition.component_def.ComponentDef>`

        """
        from pyedb.grpc.database.definition.component_def import ComponentDef

        return ComponentDef(self._pedb, self.core.component_def)

    @component_definition.setter
    def component_definition(self, value):
        from pyedb.grpc.database.definition.component_def import ComponentDef

        if isinstance(value, ComponentDef):
            self.core.component_def = value.core
        else:
            self._pedb.logger.error("Invalid input. Set component definition failed.")

    @property
    def component_def(self):
        """Component definition.

        deprecated: use `component_definition` instead.

        """
        warnings.warn("`component_def` is deprecated. Use `component_definition` instead.", DeprecationWarning)
        return self.component_definition

    @component_def.setter
    def component_def(self, value):
        warnings.warn("`component_def` is deprecated. Use `component_definition` instead.", DeprecationWarning)
        self.component_definition = value

    @property
    def component_property(self):
        """Component property.

        Returns
        -------
        :class:`ComponentProperty <ansys.edb.core.hierarchy.component_property.ComponentProperty>`

        """
        return self.core.component_property

    @component_property.setter
    def component_property(self, value):
        self.core.component_property = value

    @property
    def model(self) -> Union[SparamModel, SpiceModel]:
        """Component model.

        Returns
        -------
        :class:`Model <ansys.edb.core.hierarchy.model.Model>`

        """

        if isinstance(self.component_property.model, GrpcSPICEModel):
            return SpiceModel(edb_object=self.component_property.model.msg)
        elif isinstance(self.component_property.model, GrpcSParameterModel):
            return SparamModel(edb_object=self.component_property.model.msg)
        else:
            return self.component_property.model

    @model.setter
    def model(self, value):
        if not isinstance(value, PinPairModel):
            self._pedb.logger.error("Invalid input. Set model failed.")

        comp_prop = self.core.component_property
        comp_prop.model = value
        self.core.component_property = comp_prop

    @property
    def package_def(self):
        """Package definition.

        Returns
        -------
        :class:`PackageDef <ansys.edb.core.definition.package_def.PackageDef>`
        """
        return self.core.component_property.package_def

    @package_def.setter
    def package_def(self, value):
        from pyedb.grpc.database.definition.package_def import PackageDef

        if value not in [package.name for package in self._pedb.package_defs]:
            from ansys.edb.core.definition.package_def import (
                PackageDef as GrpcPackageDef,
            )

            self._package_def = GrpcPackageDef.create(self._pedb.db, name=value)
            self._package_def.exterior_boundary = GrpcPolygonData(points=self.bounding_box)
            comp_prop = self.core.component_property
            comp_prop.package_def = self._package_def
            self.core.component_property = comp_prop
        elif isinstance(value, str):
            package = next(package for package in self._pedb.package_defs if package.name == value)
            comp_prop = self.component_property
            comp_prop.package_def = package
            self.core.component_property = comp_prop

        elif isinstance(value, PackageDef):
            comp_prop = self.component_property
            comp_prop.package_def = value
            self.core.component_property = comp_prop

    @property
    def is_mcad(self) -> bool:
        """MCad component.

        Returns
        -------
        bool

        """
        return self.core.is_mcad.value

    @is_mcad.setter
    def is_mcad(self, value):
        if isinstance(value, bool):
            self.core.is_mcad = value

    @property
    def is_mcad_3d_comp(self) -> bool:
        """Mcad 3D component.

        Returns
        -------
        bool

        """
        return self.core.is_mcad_3d_comp

    @is_mcad_3d_comp.setter
    def is_mcad_3d_comp(self, value):
        if isinstance(value, bool):
            self.is_mcad_3d_comp = value

    @property
    def is_mcad_hfss(self) -> bool:
        """MCad HFSS.

        Returns
        -------
        bool

        """
        return self.core.is_mcad_hfss

    @is_mcad_hfss.setter
    def is_mcad_hfss(self, value):
        if isinstance(value, bool):
            self.core.is_mcad_hfss = value

    @property
    def is_mcad_stride(self) -> bool:
        """MCar stride.

        Returns
        -------
        bool

        """
        return self.core.is_mcad_stride

    @is_mcad_stride.setter
    def is_mcad_stride(self, value):
        if isinstance(value, bool):
            self.core.is_mcad_stride = value

    def create_package_def(self, name=None, component_part_name=None) -> bool:
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
            name = f"{self.refdes}_{self.part_name}"
        if name not in [package.name for package in self._pedb.package_defs]:
            self._pedb.definitions.add_package_def(name, component_part_name=component_part_name)

            self.package_def = name

            return True
        else:
            logging.error(f"Package definition {name} already exists")
            return False

    @property
    def enabled(self) -> bool:
        """Component active mode.

        Returns
        -------
        bool

        """
        if self.type.lower() in ["resistor", "capacitor", "inductor"]:
            return self.component_property.enabled
        else:
            return False

    @enabled.setter
    def enabled(self, value):
        cmp_prop = self.core.component_property
        cmp_prop.enabled = value
        self.core.component_property = cmp_prop

    @property
    def spice_model(self) -> SpiceModel:
        """Assigned Spice model.

        Returns
        -------
        :class:`SpiceModel <pyedb.grpc.database.hierarchy.spice_model.SpiceModel>`
        """
        if not self.model_type == "SPICEModel":
            return None
        else:
            return SpiceModel(edb_object=self._edb_model)

    @property
    def s_param_model(self) -> SparamModel:
        """Assigned S-parameter model.

        Returns
        -------
        :class:`SParameterModel <ansys.edb.core.hierarchy.sparameter_model.SParameterModel>`
        """
        if not self.model_type == "SParameterModel":
            return None
        else:
            return SparamModel(edb_object=self._edb_model)

    @property
    def netlist_model(self) -> GrpcNetlistModel:
        """Assigned netlist model.

        Returns
        -------
        :class:`NetlistModel <ansys.edb.core.hierarchy.netlist_mode.NetlistModel>`
        """
        if not self.model_type == "NetlistModel":
            return None
        else:
            return GrpcNetlistModel(self._edb_model)

    @property
    def solder_ball_height(self) -> float:
        """Solder ball height if available.

        Returns
        -------
        float
            Balls height value.
        """
        try:
            return Value(self.component_property.solder_ball_property.height)
        except:
            return Value(0.0)

    @solder_ball_height.setter
    def solder_ball_height(self, value):
        if not self.component_property.solder_ball_property.is_null:
            cmp_property = self.core.component_property
            solder_ball_prop = cmp_property.solder_ball_property
            solder_ball_prop.height = Value(value)
            cmp_property.solder_ball_property = solder_ball_prop
            self.core.component_property = cmp_property

    @property
    def solder_ball_shape(self) -> str:
        """Solder ball shape.

        Returns
        -------
        str
            Solder balls shapes, ``none``, ``cylinder`` or ``spheroid``.
        """
        if not self.component_property.solder_ball_property.is_null:
            shape = self.component_property.solder_ball_property.shape
            if shape == SolderballShape.NO_SOLDERBALL:
                return "none"
            elif shape == SolderballShape.SOLDERBALL_CYLINDER:
                return "cylinder"
            elif shape == SolderballShape.SOLDERBALL_SPHEROID:
                return "spheroid"

    @solder_ball_shape.setter
    def solder_ball_shape(self, value):
        if not self.component_property.solder_ball_property.is_null:
            shape = None
            if isinstance(value, str):
                if value.lower() == "cylinder":
                    shape = SolderballShape.SOLDERBALL_CYLINDER
                elif value.lower() == "none":
                    shape = SolderballShape.NO_SOLDERBALL
                elif value.lower() == "spheroid":
                    shape = SolderballShape.SOLDERBALL_SPHEROID
            if shape:
                cmp_property = self.core.component_property
                solder_ball_prop = cmp_property.solder_ball_property
                solder_ball_prop.shape = shape
                cmp_property.solder_ball_property = solder_ball_prop
                self.core.component_property = cmp_property

    @property
    def solder_ball_diameter(self) -> Union[tuple[float, float], None]:
        """Solder ball diameter.

        Returns
        -------
        float
            diameter value.
        """
        if not self.component_property.solder_ball_property.is_null:
            diameter, mid_diameter = self.component_property.solder_ball_property.get_diameter()
            return Value(diameter), Value(mid_diameter)

    @solder_ball_diameter.setter
    def solder_ball_diameter(self, value):
        if not self.component_property.solder_ball_property.is_null:
            diameter = None
            mid_diameter = diameter
            if isinstance(value, tuple) or isinstance(value, list):
                if len(value) == 2:
                    diameter = Value(value[0])
                    mid_diameter = Value(value[1])
                elif len(value) == 1:
                    diameter = Value(value[0])
                    mid_diameter = Value(value[0])
            if isinstance(value, str) or isinstance(value, float):
                diameter = Value(value)
                mid_diameter = Value(value)
            cmp_property = self.core.component_property
            solder_ball_prop = cmp_property.solder_ball_property
            solder_ball_prop.set_diameter(diameter, mid_diameter)
            cmp_property.solder_ball_property = solder_ball_prop
            self.core.component_property = cmp_property

    @property
    def solder_ball_placement(self):
        """Solder ball placement if available.."""
        if not self.component_property.solder_ball_property.is_null:
            solder_placement = self.component_property.solder_ball_property.placement
            return solder_placement.value

    @property
    def refdes(self) -> str:
        """Reference Designator Name.

        Returns
        -------
        str
            Reference Designator Name.
        """
        return self.core.name

    @refdes.setter
    def refdes(self, name):
        self.core.name = name

    @property
    def model_type(self) -> str:
        """Retrieve assigned model type.

        Returns
        -------
        str
            Model type, ``RLC``, `` SParameterModel`` or ``SPICEModel``.
        """
        _model_type = str(self._edb_model).split(".")[-1]
        if _model_type == "PinPairModel":
            return "RLC"
        elif "SParameterModel" in _model_type:
            return "SParameterModel"
        elif "SPICEModel" in _model_type:
            return "SPICEModel"
        else:
            return _model_type

    @property
    def rlc_values(self) -> Union[List[list[float]], List[float]]:
        """Get component rlc values.

        Returns
        -------
        list[list[Rvalue(float), Lvalue(float), Cvalue(float)]].
        """
        if not len(self._rlc):
            return [0.0, 0.0, 0.0]
        elif len(self._rlc) == 1:
            return [Value(self._rlc[0].r), Value(self._rlc[0].l), Value(self._rlc[0].c)]
        else:
            return [[Value(rlc.r), Value(rlc.l), Value(rlc.c)] for rlc in self._rlc]

    @rlc_values.setter
    def rlc_values(self, value):
        comp_property = self.core.component_property
        if not isinstance(value, list) or isinstance(value, tuple):
            self._logger.error("RLC values must be provided as `List` or `Tuple` in this order.")
            return
        if not len(value) == 3:
            self._logger.error("RLC values must be provided as `List` or `Tuple` in this order.")
            return
        _rlc = []
        for rlc in self._rlc:
            if value[0]:
                rlc.r = Value(value[0])
                rlc.r_enabled = True
            else:
                rlc.r_enabled = False
            if value[1]:
                rlc.l = Value(value[1])
                rlc.l_enabled = True
            else:
                rlc.l_enabled = False
            if value[2]:
                rlc.c = Value(value[2])
                rlc.c_enabled = True
            else:
                rlc.c_enabled = False
            _rlc.append(rlc)
        for ind in range(len(self._rlc)):
            self._edb_model.set_rlc(self._pin_pairs[ind], self._rlc[ind])
        comp_property.model = self._edb_model
        self.core.component_property = comp_property

    @property
    def value(self) -> float:
        """Retrieve discrete component value.

        Returns
        -------
        float
            Value. ``None`` if not an RLC Type.
        """
        values_mapping = {
            "resistor": self.rlc_values[0],
            "inductor": self.rlc_values[1],
            "capacitor": self.rlc_values[2],
        }
        return values_mapping.get(self.component_type, 0.0)

    @value.setter
    def value(self, value):
        component_type = self.component_type
        if component_type == "resistor":
            self.res_value = value
        elif component_type == "inductor":
            self.ind_value = value
        elif component_type == "capacitor":
            self.cap_value = value

    @property
    def res_value(self) -> float:
        """Resistance value.

        Returns
        -------
        float
            Resistance value or ``None`` if not an RLC type.
        """
        if self.component_type in ["resistor", "capacitor", "inductor"]:
            result = [Value(rlc.r) for rlc in self._rlc]
            if result:
                return result[0]  # -> first pin pair change for managing multi pin pair components
        return 0.0

    @res_value.setter
    def res_value(self, value):  # pragma no cover
        _rlc = []
        model = PinPairModel(self._pedb, GrpcPinPairModel.create())
        for rlc in self._rlc:
            rlc.r_enabled = True
            rlc.r = Value(value)
            _rlc.append(rlc)
        for ind in range(len(self._pin_pairs)):
            model.set_rlc(self._pin_pairs[ind], _rlc[ind])
        comp_prop = self.core.component_property
        comp_prop.model = model
        self.core.component_property = comp_prop

    @property
    def cap_value(self) -> float:
        """Capacitance Value.

        Returns
        -------
        float
            Capacitance Value. ``None`` if not an RLC Type.
        """
        if self.component_type in ["resistor", "capacitor", "inductor"]:
            result = [Value(rlc.c) for rlc in self._rlc]
            if result:
                return result[0]  # -> first pin pair change for managing multi pin pair components
        return 0.0

    @cap_value.setter
    def cap_value(self, value):  # pragma no cover
        if value:
            _rlc = []
            model = PinPairModel(self._pedb, GrpcPinPairModel.create())
            for rlc in self._rlc:
                rlc.c_enabled = True
                rlc.c = Value(value)
                _rlc.append(rlc)
            for ind in range(len(self._pin_pairs)):
                model.set_rlc(self._pin_pairs[ind], _rlc[ind])
            comp_prop = self.core.component_property
            comp_prop.model = model
            self.core.component_property = comp_prop

    @property
    def ind_value(self):
        """Inductance Value.

        Returns
        -------
        float
            Inductance Value. ``None`` if not an RLC Type.
        """
        if self.component_type in ["resistor", "capacitor", "inductor"]:
            result = [Value(rlc.l) for rlc in self._rlc]
            if result:
                return result[0]  # -> first pin pair change for managing multi pin pair components
        return 0.0

    @ind_value.setter
    def ind_value(self, value) -> float:
        if value:
            _rlc = []
            model = PinPairModel(self._pedb, GrpcPinPairModel.create())
            for rlc in self._rlc:
                rlc.l_enabled = True
                rlc.l = Value(value)
                _rlc.append(rlc)
            for ind in range(len(self._pin_pairs)):
                model.set_rlc(self._pin_pairs[ind], _rlc[ind])
            comp_prop = self.core.component_property
            comp_prop.model = model
            self.core.component_property = comp_prop

    @property
    def is_parallel_rlc(self) -> bool:
        """Define if model is Parallel or Series.

        Returns
        -------
        bool
            `True´ if parallel rlc model.
            `False` series RLC.
            `None` if not RLC Type.
        """
        if self.component_type in ["resistor", "capacitor", "inductor"]:
            return self._rlc[0].is_parallel  # -> first pin pair change for managing multi pin pair components
        return False

    @is_parallel_rlc.setter
    def is_parallel_rlc(self, value):  # pragma no cover
        if not len(self._pin_pairs):
            logging.warning(self.refdes, " has no pin pair.")
        else:
            if isinstance(value, bool):
                for rlc in self._rlc:
                    rlc.is_parallel = value
                    comp_property = self.component_property
                    comp_property.set_rcl(rlc)
                    self.component_property = comp_property

    @property
    def center(self) -> tuple[float, float]:
        """Compute the component center.

        Returns
        -------
        list
            [x value, y value].
        """
        location = self.core.location
        return location[0].value, location[1].value

    @center.setter
    def center(self, value):
        if isinstance(value, list):
            value = Value(value[0], Value(value[1]))
        self.core.location = value

    @property
    def location(self) -> tuple[float, float]:
        """Component center.

        Returns
        -------
        List[float, float]
            [x, y].

        """
        location = self.core.location
        return location[0].value, location[1].value

    @location.setter
    def location(self, value):
        if isinstance(value, list):
            _location = Value(value[0], Value(value[1]))
            self.core.location = _location

    @property
    def bounding_box(self) -> tuple[tuple[float, float], tuple[float, float]]:
        """Component's bounding box.

        Returns
        -------
        List[float]
            List of coordinates for the component's bounding box, with the list of
            coordinates in this order: [X lower left corner, Y lower left corner,
            X upper right corner, Y upper right corner].
        """
        bbox = self.component_instance.get_bbox().points
        pt1 = bbox[0]
        pt2 = bbox[2]
        return (Value(pt1.x), Value(pt1.y)), (Value(pt2.x), Value(pt2.y))

    @property
    def rotation(self) -> float:
        """Compute the component rotation in radian.

        Returns
        -------
        float
            Rotation value.
        """
        return Value(self.core.transform.rotation)

    @property
    def pinlist(self) -> list[PadstackInstance]:
        """Pins of the component.

        Returns
        -------
        list
            List of Pins of Component.
        """
        return list(self.pins.values())

    @property
    def nets(self):
        """Nets of Component.

        Returns
        -------
        list[str]
            Component nets names.
        """
        nets = []
        for pin in list(self.pins.values()):
            if not pin.net.is_null:
                nets.append(pin.net.name)
        return list(set(nets))

    @property
    def pins(self) -> dict[str, PadstackInstance]:
        """Component pins.

        Returns
        -------
        Dic[str,:class:`PadstackInstance <pyedb.grpc.database.primitive.padstack_instance.PadstackInstance>`]
            Component dictionary pins.
        """
        _pins = {}
        for connectable in self.core.members:
            if isinstance(connectable, GrpcPadstackInstanceTerminal):
                _pins[connectable.name] = PadstackInstanceTerminal(self._pedb, connectable)
            if isinstance(connectable, GrpcPadstackInstance):
                _pins[connectable.name] = PadstackInstance(self._pedb, connectable)
        return _pins

    @property
    def num_pins(self):
        """Number of Pins of Component.

        Returns
        -------
        int
            Component pins number.
        """
        try:
            return self.core.num_pins
        except Exception as e:
            self._pedb.logger.error(f"{e}")
            return 0

    @property
    def type(self) -> str:
        """Component type.

        Returns
        -------
        str
            Type of the component. Options are ``"resistor"``, ``"inductor"``, ``"capacitor"``,
            ``"ic"``, ``"io"`` and ``"other"``.
        """
        return self.component_type

    @type.setter
    def type(self, new_type):
        """Set component type

        Parameters
        ----------
        new_type : str
            Type of the component. Options are ``"resistor"``,  ``"inductor"``, ``"capacitor"``,
            ``"ic"``, ``"io"`` and ``"other"``.
        """
        new_type = new_type.lower()
        self.component_type = new_type

    @property
    def numpins(self) -> int:
        """Number of Pins of Component.

        ..deprecated:: 0.51.0
           Use: func:`num_pins` instead.
        Returns
        -------
        int
            Component pins number.
        """

        warnings.warn("Use num_pins instead.", DeprecationWarning)
        try:
            return self.core.num_pins
        except Exception as e:
            self._pedb.logger.error(f"{e}")
            return 0

    @property
    def partname(self) -> str:
        """Component part name.

        Returns
        -------
        str
            Component part name.
        """
        return self.part_name

    @partname.setter
    def partname(self, name):  # pragma: no cover
        """Set component part name."""
        self.part_name = name

    @property
    def name(self):
        """Component part name.

        Returns
        -------
        str
            Component part name.
        """
        return self.core.name

    @name.setter
    def name(self, name):  # pragma: no cover
        """Set component part name."""
        self.core.name = name

    @property
    def ref_des(self):
        """Reference Designator Name.

        Returns
        -------
        str
            Reference Designator Name.
        """
        return self.name

    @ref_des.setter
    def ref_des(self, name):
        self.name = name

    @property
    def part_name(self) -> str:
        """Component part name.

        Returns
        -------
        str
            Component part name.
        """
        return self.core.component_def.name

    @part_name.setter
    def part_name(self, name):  # pragma: no cover
        """Set component part name."""
        self.core.component_def.name = name

    @property
    def placement_layer(self) -> str:
        """Placement layern name.

        Returns
        -------
        str
           Placement layer name.
        """
        return self.core.placement_layer.name

    @property
    def layer(self) -> StackupLayer:
        """Placement layern object.

        Returns
        -------
        :class:`pyedb.grpc.database.layers.stackup_layer.StackupLayer`
           Placement layer.
        """
        return StackupLayer(self._pedb, self.core.placement_layer)

    @property
    def is_top_mounted(self) -> bool:
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
    def lower_elevation(self) -> float:
        """Lower elevation of the placement layer.

        Returns
        -------
        float
            Placement layer lower elevation.
        """
        return self.layer.lower_elevation

    @property
    def upper_elevation(self) -> float:
        """Upper elevation of the placement layer.

        Returns
        -------
        float
            Placement layer upper elevation.

        """
        return self.layer.upper_elevation

    @property
    def top_bottom_association(self) -> int:
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
        return self.layer.core.top_bottom_association.value

    def _set_model(self, model):  # pragma: no cover
        """Set component model


        Returns
        -------
        :class:`Model <ansys.edb.core.hierarchy.model.Model>`
            Component Model.

        """
        comp_prop = self.component_property
        comp_prop.model = model
        self.component_property = comp_prop
        return model

    def delete(self):
        """Delete the component from the EDB.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        self.core.delete()

    def assign_spice_model(
        self,
        file_path: str,
        name: Optional[str] = None,
        sub_circuit_name: Optional[str] = None,
        terminal_pairs: Optional[list] = None,
    ) -> SpiceModel:
        """Assign Spice model to this component.

        Parameters
        ----------
        file_path : str
            File path of the Spice model.
        name : str, optional
            Name of the Spice model.

        Returns
        -------
        :class:`SpiceModel <pyedb.grpc.database.hierarchy.spice_model.SpiceModel>`
            Spice model.

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

        model = SpiceModel(file_path=file_path, name=name, sub_circuit=name)
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
                model.add_terminal(pname, str(idx + 1))
        self._set_model(model)
        if not model.is_null:
            return model
        else:
            return False

    def assign_s_param_model(self, file_path, name=None, reference_net=None) -> GrpcNPortComponentModel:
        """Assign S-parameter to this component.

        Parameters
        ----------
        file_path : str
            File path of the S-parameter model.
        name : str, optional
            Name of the S-parameter model.

        reference_net : str, optional
            Reference net.

        Returns
        -------
        :class:`NPortComponentModel <ansys.edb.core.definition.component_model.ComponentModel>`
            ComponentModel.

        """
        if not name:
            name = get_filename_without_extension(file_path)
        for model in self.core.component_def.component_models:
            if model.model_name == name:
                self._pedb.logger.error(f"Model {name} already defined for component {self.refdes}")
                return False
        if not reference_net:
            self._pedb.logger.warning(
                f"No reference net provided for S parameter file {file_path}, net `GND` is assigned by default"
            )
            reference_net = "GND"
        n_port_model = GrpcNPortComponentModel.find_by_name(self.core.component_def, name)
        if n_port_model.is_null:
            n_port_model = GrpcNPortComponentModel.create(name=name)
            n_port_model.reference_file = file_path
            self.component_definition.core.add_component_model(n_port_model)

        model = GrpcSParameterModel.create(name=name, ref_net=reference_net)
        return self._set_model(model)

    def use_s_parameter_model(self, name, reference_net=None) -> bool:
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
        from ansys.edb.core.definition.component_model import (
            ComponentModel as GrpcComponentModel,
        )

        model = GrpcComponentModel.find_by_name(self.core.component_def, name)
        if not model.is_null:
            s_param_model = GrpcSParameterModel.create(name=name, ref_net="GND")
            if reference_net:
                s_param_model.reference_net = reference_net
            return self._set_model(s_param_model)
        return False

    def assign_rlc_model(self, res=None, ind=None, cap=None, is_parallel=False) -> PinPairModel:
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

        Returns
        -------
        :class:`Model <ansys.edb.core.hierarchy.model.Model>`
            Component Model.

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
        res, ind, cap = Value(res), Value(ind), Value(cap)
        model = PinPairModel(self._pedb, self._edb_model)
        pin_names = list(self.pins.keys())
        for idx, i in enumerate(np.arange(len(pin_names) // 2)):
            # pin_pair = GrpcPinPair(pin_names[idx], pin_names[idx + 1])
            rlc = GrpcRlc(
                r=res,
                r_enabled=r_enabled,
                l=ind,
                l_enabled=l_enabled,
                c=cap,
                c_enabled=c_enabled,
                is_parallel=is_parallel,
            )
            model.set_rlc(("1", "2"), rlc)
        return self._set_model(model)

    def create_clearance_on_component(self, extra_soldermask_clearance=1e-4) -> bool:
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
        opening = [bounding_box[0][0] - extra_soldermask_clearance]
        opening.append(bounding_box[0][1] - extra_soldermask_clearance)
        opening.append(bounding_box[1][0] + extra_soldermask_clearance)
        opening.append(bounding_box[1][1] + extra_soldermask_clearance)

        comp_layer = self.layer
        layer_names = list(self._pedb.stackup.layers.keys())
        layer_index = layer_names.index(comp_layer.name)
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


class ICDieProperty:
    def __init__(self, component):
        self._component = component
        self._die_property = self._component.component_property.die_property

    @property
    def die_orientation(self) -> str:
        """Die orientation.

        Returns
        -------
        str
            Die orientation, ``chip_up`` or ``chip_down``.

        """
        return self._die_property.die_orientation.name.lower()

    @die_orientation.setter
    def die_orientation(self, value):
        component_property = self._component.component_property
        die_property = component_property.die_property
        if value.lower() == "chip_up":
            die_property.die_orientation = GrpcDieOrientation.CHIP_UP
        elif value.lower() == "chip_down":
            die_property.die_orientation = GrpcDieOrientation.CHIP_DOWN
        else:
            return
        component_property.die_property = die_property
        self._component.component_property = component_property

    @property
    def die_type(self) -> str:
        """Die type.

        Returns
        -------
        str
            Die type, ``noine``, ``flipchip``, ``wirebond``.

        """
        return self._die_property.die_type.name.lower()

    @die_type.setter
    def die_type(self, value):
        component_property = self._component.component_property
        die_property = component_property.die_property
        if value.lower() == "none":
            die_property.die_type = GrpcDieType.NONE
        elif value.lower() == "flipchip":
            die_property.die_type = GrpcDieType.FLIPCHIP
        elif value.lower() == "wirebond":
            die_property.die_type = GrpcDieType.WIREBOND
        else:
            return
        component_property.die_property = die_property
        self._component.component_property = component_property

    @property
    def height(self) -> float:
        """Die height.

        Returns
        -------
        float
            Die height.

        """
        return Value(self._die_property.height)

    @height.setter
    def height(self, value):
        component_property = self._component.component_property
        die_property = component_property.die_property
        die_property.height = Value(value)
        component_property.die_property = die_property
        self._component.component_property = component_property

    @property
    def is_null(self) -> bool:
        """Test is die is null.

        Returns
        -------
        bool

        """
        return self._die_property.is_null
