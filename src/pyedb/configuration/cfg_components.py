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

"""Build the ``components`` configuration section and its model helpers."""

from ansys.edb.core.definition.die_property import DieOrientation as CoreDieOrientation, DieType as CoreDieType
from ansys.edb.core.definition.solder_ball_property import SolderballShape as CoreSolderballShape
from pydantic import BaseModel

from pyedb.configuration.cfg_common import CfgBase


def _get_snake_to_pascal():
    """Lazy import of snake_to_pascal to avoid loading .NET when using gRPC."""
    # Import from dotnet module - only called in non-gRPC mode
    from pyedb.dotnet.database.general import snake_to_pascal

    return snake_to_pascal


_solder_shape_mapping = {
    "cylinder": CoreSolderballShape.SOLDERBALL_CYLINDER,
    "spheroid": CoreSolderballShape.SOLDERBALL_SPHEROID,
    "no_solder_ball": CoreSolderballShape.NO_SOLDERBALL,
}

_die_type_mapping = {
    "flip_chip": CoreDieType.FLIPCHIP,
    "wire_bond": CoreDieType.WIREBOND,
    "no_die": CoreDieType.NONE,
}

_die_orientation_mapping = {
    "chip_up": CoreDieOrientation.CHIP_UP,
    "chip_down": CoreDieOrientation.CHIP_DOWN,
}


class CfgPinPairModel(BaseModel):
    """Represent one pin-pair RLC model entry."""

    first_pin: str
    second_pin: str
    resistance: str | float | None = None
    inductance: str | float | None = None
    capacitance: str | float | None = None
    is_parallel: bool = False
    resistance_enabled: bool = False
    inductance_enabled: bool = False
    capacitance_enabled: bool = False

    def __init__(
        self,
        first_pin: str,
        second_pin: str,
        resistance: str | float | None = None,
        inductance: str | float | None = None,
        capacitance: str | float | None = None,
        is_parallel: bool = False,
        resistance_enabled: bool = False,
        inductance_enabled: bool = False,
        capacitance_enabled: bool = False,
        **kwargs,
    ):
        super().__init__(
            first_pin=first_pin,
            second_pin=second_pin,
            resistance=resistance,
            inductance=inductance,
            capacitance=capacitance,
            is_parallel=is_parallel,
            resistance_enabled=resistance_enabled,
            inductance_enabled=inductance_enabled,
            capacitance_enabled=capacitance_enabled,
            **kwargs,
        )

    def to_dict(self) -> dict:
        return self.model_dump()


class CfgComponent(CfgBase):
    """Fluent builder for a single component entry."""

    def retrieve_model_properties_from_edb(self):
        c_p = self.pyedb_obj

        model_type = c_p.model_type

        if "NetlistModel" in model_type:
            self.netlist_model["netlist"] = c_p.netlist_model
        elif "PinPairModel" in model_type or "RLC" in model_type:
            temp = {}

            pin_pairs = c_p.pin_pairs[::]
            if not pin_pairs:
                return
            pp0 = pin_pairs[0]
            temp["first_pin"] = pp0.first_pin
            temp["second_pin"] = pp0.second_pin

            # Read all RLC values directly from the already-fetched pin_pair
            # to avoid repeated GetComponentProperty() calls (EDB 2026.1 heap
            # corruption risk when iterating many components after model writes).
            try:
                rlc = pp0._pin_pair_rlc
                temp["is_parallel"] = rlc.IsParallel
                temp["resistance"] = str(rlc.R.ToDouble())
                temp["resistance_enabled"] = rlc.REnabled
                temp["inductance"] = str(rlc.L.ToDouble())
                temp["inductance_enabled"] = rlc.LEnabled
                temp["capacitance"] = str(rlc.C.ToDouble())
                temp["capacitance_enabled"] = rlc.CEnabled
            except Exception:
                temp["is_parallel"] = False
                temp["resistance"] = str(c_p.res_value)
                temp["resistance_enabled"] = (c_p.rlc_enable or [False, False, False])[0]
                temp["inductance"] = str(c_p.ind_value)
                temp["inductance_enabled"] = (c_p.rlc_enable or [False, False, False])[1]
                temp["capacitance"] = str(c_p.cap_value)
                temp["capacitance_enabled"] = (c_p.rlc_enable or [False, False, False])[2]
            self.pin_pair_model.append(temp)
        elif "SParameterModel" in model_type:
            self.s_parameter_model["reference_net"] = c_p.model.reference_net
            self.s_parameter_model["model_name"] = c_p.model.component_model_name
        elif "SPICEModel" in model_type:
            self.spice_model["model_name"] = c_p.model.model_name
            self.spice_model["model_path"] = c_p.model.spice_file_path
            self.spice_model["sub_circuit"] = c_p.model.sub_circuit
            self.spice_model["terminal_pairs"] = c_p.model.pin_pairs

    def _set_ic_die_properties_to_edb(self):
        if not self.ic_die_properties:
            return
        if hasattr(self.pyedb_obj.component_property, "core"):
            cp = self.pyedb_obj.component_property.core
        else:
            # grpc is returning pyedb-core object directly as it is internal.
            cp = self.pyedb_obj.component_property
        if self._pedb.grpc:
            ic_die_prop = cp.die_property
        else:
            ic_die_prop = cp.GetDieProperty().Clone()
        die_type = self.ic_die_properties.get("type")
        if self._pedb.grpc:
            ic_die_prop.die_type = _die_type_mapping[die_type]
        else:
            snake_to_pascal = _get_snake_to_pascal()
            ic_die_prop.SetType(getattr(self._pedb._edb.Definition.DieType, snake_to_pascal(die_type)))
        if not die_type == "no_die":
            orientation = self.ic_die_properties.get("orientation")
            if orientation:
                if self._pedb.grpc:
                    ic_die_prop.die_orientation = _die_orientation_mapping[orientation]
                else:
                    snake_to_pascal = _get_snake_to_pascal()
                    ic_die_prop.SetOrientation(
                        getattr(self._pedb._edb.Definition.DieOrientation, snake_to_pascal(orientation))
                    )
            if die_type == "wire_bond":
                height = self.ic_die_properties.get("height")
                if height:
                    if self._pedb.grpc:
                        ic_die_prop.height = self._pedb.value(height)
                    else:
                        ic_die_prop.SetHeight(self._pedb.edb_value(height))
        if self._pedb.grpc:
            self.pyedb_obj.core.component_property.die_property = ic_die_prop
        else:
            self.pyedb_obj.ic_die_properties = ic_die_prop

    def _set_port_properties_to_edb(self):
        if self._pedb.grpc:
            cp = self.pyedb_obj.component_property
            port_prop = cp.port_property
        else:
            # Use a mutable clone so SetPortProperty does not raise
            # ReadOnlyModificationAttemptException on the live object.
            cp = self.pyedb_obj._get_component_property_clone()
            port_prop = cp.GetPortProperty().Clone()
        height = self.port_properties.get("reference_height")
        if height:
            if self._pedb.grpc:
                port_prop.reference_height = self._pedb.value(height)
            else:
                port_prop.SetReferenceHeight(self._pedb.edb_value(height))
        reference_size_auto = self.port_properties.get("reference_size_auto")
        if reference_size_auto is not None:
            if self._pedb.grpc:
                port_prop.reference_size_auto = reference_size_auto
            else:
                port_prop.SetReferenceSizeAuto(reference_size_auto)
        reference_size_x = self.port_properties.get("reference_size_x", 0)
        reference_size_y = self.port_properties.get("reference_size_y", 0)
        if self._pedb.grpc:
            port_prop.set_reference_size(self._pedb.value(reference_size_x), self._pedb.value(reference_size_y))
            cp.port_properties = port_prop
        else:
            port_prop.SetReferenceSize(self._pedb.edb_value(reference_size_x), self._pedb.edb_value(reference_size_y))
            cp.SetPortProperty(port_prop)
            self.pyedb_obj.edbcomponent.SetComponentProperty(cp)

    def _set_model_properties_to_edb(self):
        if hasattr(self.pyedb_obj.component_property, "core"):
            c_p = self.pyedb_obj.component_property.core
        else:
            # grpc is returning pyedb-core object directly as it is internal.
            c_p = self.pyedb_obj.component_property
        if self.netlist_model:
            self.pyedb_obj.assign_netlist_model(self.netlist_model["netlist"])
        elif self.pin_pair_model:
            m = self.pyedb_obj.model
            for i in self.pin_pair_model:
                m.add_pin_pair(
                    r=i.get("resistance"),
                    l=i.get("inductance"),
                    c=i.get("capacitance"),
                    is_parallel=i.get("is_parallel", False),
                    first_pin=str(i["first_pin"]),
                    second_pin=str(i["second_pin"]),
                    r_enabled=i.get("resistance_enabled", False),
                    l_enabled=i.get("inductance_enabled", False),
                    c_enabled=i.get("capacitance_enabled", False),
                )
        elif self.s_parameter_model:
            self.pyedb_obj.assign_s_param_model(
                self.s_parameter_model["model_path"],
                self.s_parameter_model["model_name"],
                self.s_parameter_model["reference_net"],
            )
        elif self.spice_model:
            self.pyedb_obj.assign_spice_model(
                self.spice_model["model_path"],
                self.spice_model["model_name"],
                self.spice_model["sub_circuit"],
                self.spice_model["terminal_pairs"],
            )

    def _set_solder_ball_properties_to_edb(self):
        if self._pedb.grpc:
            cp = self.pyedb_obj.component_property
            solder_ball_prop = cp.solder_ball_property
            shape = self.solder_ball_properties.get("shape")
            if shape:
                solder_ball_prop.shape = _solder_shape_mapping.get(shape, CoreSolderballShape.NO_SOLDERBALL)
        else:
            # Use a mutable clone so SetSolderBallProperty does not raise
            # ReadOnlyModificationAttemptException on the live object.
            cp = self.pyedb_obj._get_component_property_clone()
            solder_ball_prop = cp.GetSolderBallProperty().Clone()
            shape = self.solder_ball_properties.get("shape")
            if shape:
                snake_to_pascal = _get_snake_to_pascal()
                solder_ball_prop.SetShape(getattr(self._pedb._edb.Definition.SolderballShape, snake_to_pascal(shape)))
            else:
                return

        if shape == "cylinder":
            diameter = self.solder_ball_properties["diameter"]
            if self._pedb.grpc:
                solder_ball_prop.set_diameter(self._pedb.value(diameter), self._pedb.value(diameter))
            else:
                solder_ball_prop.SetDiameter(self._pedb.edb_value(diameter), self._pedb.edb_value(diameter))
        elif shape == "spheroid":
            diameter = self.solder_ball_properties["diameter"]
            mid_diameter = self.solder_ball_properties["mid_diameter"]
            if self._pedb.grpc:
                solder_ball_prop.set_diameter(self._pedb.value(diameter), self._pedb.value(mid_diameter))
            else:
                solder_ball_prop.SetDiameter(self._pedb.edb_value(diameter), self._pedb.edb_value(mid_diameter))
        else:
            raise ValueError("Solderball shape must be either cylinder or spheroid")
        if self._pedb.grpc:
            solder_ball_prop.height = self._pedb.value(self.solder_ball_properties["height"])
            solder_ball_prop.material_name = self.solder_ball_properties.get("material", "solder")
            cp.solder_ball_property = solder_ball_prop
        else:
            solder_ball_prop.SetHeight(self._pedb.edb_value(self.solder_ball_properties["height"]))
            solder_ball_prop.SetMaterialName(self.solder_ball_properties.get("material", "solder"))
            cp.SetSolderBallProperty(solder_ball_prop)
            self.pyedb_obj.edbcomponent.SetComponentProperty(cp)

    def _retrieve_ic_die_properties_from_edb(self):
        temp = dict()
        cp = self.pyedb_obj

        # ic_die_prop = cp.GetDieProperty().Clone()
        # die_type = pascal_to_snake(ic_die_prop.GetType().ToString())
        temp["type"] = cp.ic_die_properties.die_type
        if not temp["type"] == "no_die":
            temp["orientation"] = cp.ic_die_properties.die_orientation
            if temp["type"] == "wire_bond":
                temp["height"] = str(cp.ic_die_properties.height)
        self.ic_die_properties = temp

    def _retrieve_solder_ball_properties_from_edb(self):
        temp = dict()
        cp = self.pyedb_obj
        uses_solder_ball = cp.uses_solderball

        temp["uses_solder_ball"] = uses_solder_ball
        temp["shape"] = cp.solder_ball_shape
        temp["diameter"] = str(cp.solder_ball_diameter[0])
        temp["mid_diameter"] = str(cp.solder_ball_diameter[1])
        temp["height"] = str(cp.solder_ball_height)
        temp["material"] = cp.solder_ball_material
        self.solder_ball_properties = temp

    def _retrieve_port_properties_from_edb(self):
        temp = dict()
        cp = self.pyedb_obj.component_property
        c_type = self.type.lower()
        if c_type not in ["ic", "io", "other"]:
            return
        else:
            # port_prop = cp.GetPortProperty().Clone()
            # reference_height = port_prop.GetReferenceHeightValue().ToString()
            # reference_size_auto = port_prop.GetReferenceSizeAuto()
            # _, reference_size_x, reference_size_y = port_prop.GetReferenceSize()
            temp["reference_height"] = str(cp.port_property.reference_height)
            temp["reference_size_auto"] = cp.port_property.reference_size_auto
            temp["reference_size_x"] = str(cp.port_property.get_reference_size()[0])
            temp["reference_size_y"] = str(cp.port_property.get_reference_size()[1])
            self.port_properties = temp

    def set_parameters_to_edb(self):
        if self.pyedb_obj is None:
            return self.to_dict()
        if self.type:
            self.pyedb_obj.type = self.type
        if self.enabled is not None:
            self.pyedb_obj.enabled = self.enabled

        self._set_model_properties_to_edb()
        if self.pyedb_obj.type.lower() == "ic":
            self._set_ic_die_properties_to_edb()
            self._set_port_properties_to_edb()
            self._set_solder_ball_properties_to_edb()
        elif self.pyedb_obj.type.lower() in ["io", "other"]:
            self._set_solder_ball_properties_to_edb()
            self._set_port_properties_to_edb()

    def retrieve_parameters_from_edb(self):
        if self.pyedb_obj is None:
            return self.to_dict()
        self.type = self.pyedb_obj.type
        self.definition = self.pyedb_obj.part_name
        self.reference_designator = self.pyedb_obj.name
        self.retrieve_model_properties_from_edb()
        if self.pyedb_obj.type.lower() == "ic":
            self._retrieve_ic_die_properties_from_edb()
            self._retrieve_port_properties_from_edb()
            self._retrieve_solder_ball_properties_from_edb()
        elif self.pyedb_obj.type.lower() in ["io", "other"]:
            self._retrieve_solder_ball_properties_from_edb()
            self._retrieve_port_properties_from_edb()

    def __init__(self, _pedb=None, pedb_object=None, **kwargs):
        if pedb_object is None and not hasattr(_pedb, "components") and "reference_designator" not in kwargs and _pedb is not None:
            kwargs["reference_designator"] = _pedb
            _pedb = None
        self._pedb = _pedb
        self.pyedb_obj = pedb_object

        self.enabled = kwargs.get("enabled", None)
        self.reference_designator = kwargs.get("reference_designator", None)
        self.definition = kwargs.get("definition", None)
        self.type = kwargs["part_type"].lower() if kwargs.get("part_type") else None
        self.placement_layer = kwargs.get("placement_layer", None)
        self.pins = kwargs.get("pins", [])

        self.port_properties = kwargs.get("port_properties", {})
        self.solder_ball_properties = kwargs.get("solder_ball_properties", {})
        self.ic_die_properties = kwargs.get("ic_die_properties", {})
        self.pin_pair_model = kwargs.get("pin_pair_model", [])
        self.spice_model = kwargs.get("spice_model", {})
        self.s_parameter_model = kwargs.get("s_parameter_model", {})
        self.netlist_model = kwargs.get("netlist_model", {})

    def add_pin_pair_rlc(
        self,
        first_pin: str,
        second_pin: str,
        resistance=None,
        inductance=None,
        capacitance=None,
        is_parallel: bool = False,
        resistance_enabled: bool = False,
        inductance_enabled: bool = False,
        capacitance_enabled: bool = False,
    ):
        """Append a pin-pair RLC model between two component pins.

        Parameters
        ----------
        first_pin : str
            Name of the first pin, e.g. ``"1"``.
        second_pin : str
            Name of the second pin, e.g. ``"2"``.
        resistance : str, float, or None, optional
            Resistance value, e.g. ``"100ohm"`` or ``100.0``.
        inductance : str, float, or None, optional
            Inductance value, e.g. ``"1nH"``.
        capacitance : str, float, or None, optional
            Capacitance value, e.g. ``"100nF"``.
        is_parallel : bool, optional
            ``True`` for a parallel RLC topology.  Default is ``False``
            (series).
        resistance_enabled : bool, optional
            Activate the resistance element.  Default is ``False``.
        inductance_enabled : bool, optional
            Activate the inductance element.  Default is ``False``.
        capacitance_enabled : bool, optional
            Activate the capacitance element.  Default is ``False``.

        Examples
        --------
        >>> r1 = cfg.components.add("R1", part_type="resistor")
        >>> r1.add_pin_pair_rlc("1", "2", resistance="100ohm", resistance_enabled=True)
        """
        self.pin_pair_model.append(
            CfgPinPairModel(
                first_pin=first_pin,
                second_pin=second_pin,
                resistance=resistance,
                inductance=inductance,
                capacitance=capacitance,
                is_parallel=is_parallel,
                resistance_enabled=resistance_enabled,
                inductance_enabled=inductance_enabled,
                capacitance_enabled=capacitance_enabled,
            ).to_dict()
        )

    def set_s_parameter_model(self, model_name: str, model_path: str, reference_net: str):
        """Assign a Touchstone S-parameter model to this component.

        Parameters
        ----------
        model_name : str
            Name registered in the EDB component model library.
        model_path : str
            Absolute path to the ``.sNp`` Touchstone file.
        reference_net : str
            Reference (ground) net for the model, e.g. ``"GND"``.

        Examples
        --------
        >>> u1.set_s_parameter_model("cap_100nF", "/snp/cap.s2p", "GND")
        """
        self.s_parameter_model = {
            "model_name": model_name,
            "model_path": model_path,
            "reference_net": reference_net,
        }

    def set_spice_model(self, model_name: str, model_path: str, sub_circuit: str = "", terminal_pairs=None):
        """Assign a SPICE subcircuit model to this component.

        Parameters
        ----------
        model_name : str
            SPICE model name registered in the library.
        model_path : str
            Absolute path to the ``.sp`` SPICE file.
        sub_circuit : str, optional
            Subcircuit name inside the file.  Default is ``""``.
        terminal_pairs : list, optional
            Pin-to-node mapping list.  Default is ``[]``.

        Examples
        --------
        >>> u1.set_spice_model("ic_spice", "/spice/ic.sp", sub_circuit="IC_TOP")
        """
        self.spice_model = {
            "model_name": model_name,
            "model_path": model_path,
            "sub_circuit": sub_circuit,
            "terminal_pairs": terminal_pairs or [],
        }

    def set_netlist_model(self, netlist: str):
        """Assign a raw netlist model to this component.

        Parameters
        ----------
        netlist : str
            SPICE-compatible netlist string.
        """
        self.netlist_model = {"netlist": netlist}

    def set_ic_die_properties(self, die_type: str = "no_die", orientation: str = "chip_up", height=None):
        """Configure IC die and orientation properties.

        Parameters
        ----------
        die_type : str, optional
            Die type.  Accepted values: ``"flip_chip"`` | ``"wire_bond"`` |
            ``"no_die"``.  Default is ``"no_die"``.
        orientation : str, optional
            Die orientation.  ``"chip_up"`` (default) or ``"chip_down"``.
        height : str or float, optional
            Die height (wire bond only), e.g. ``"100um"``.

        Examples
        --------
        >>> u1.set_ic_die_properties("flip_chip", orientation="chip_down")
        """
        data = {"type": die_type}
        if die_type != "no_die":
            data["orientation"] = orientation
            if die_type == "wire_bond" and height:
                data["height"] = height
        self.ic_die_properties = data

    def set_solder_ball_properties(
        self,
        shape: str = "cylinder",
        diameter: str = "150um",
        height: str = "100um",
        material: str = "solder",
        mid_diameter=None,
    ):
        """Configure solder-ball geometry for this component.

        Parameters
        ----------
        shape : str, optional
            Solder-ball shape.  ``"cylinder"`` (default), ``"spheroid"``, or
            ``"no_solder_ball"``.
        diameter : str, optional
            Outer diameter, e.g. ``"150um"``.  Default is ``"150um"``.
        height : str, optional
            Solder-ball height, e.g. ``"100um"``.  Default is ``"100um"``.
        material : str, optional
            Material name.  Default is ``"solder"``.
        mid_diameter : str or None, optional
            Mid-diameter for spheroid shape.  Defaults to *diameter* when
            *None*.

        Examples
        --------
        >>> u1.set_solder_ball_properties("cylinder", "150um", "100um")
        """
        data = {"shape": shape, "diameter": diameter, "height": height, "material": material}
        if shape == "spheroid":
            data["mid_diameter"] = mid_diameter or diameter
        self.solder_ball_properties = data

    def set_port_properties(
        self,
        reference_height: str = "0",
        reference_size_auto: bool = True,
        reference_size_x: str = "0",
        reference_size_y: str = "0",
    ):
        """Configure port reference geometry for this IC component.

        Parameters
        ----------
        reference_height : str, optional
            Port reference height, e.g. ``"50um"``.  Default is ``"0"``.
        reference_size_auto : bool, optional
            Let the solver auto-compute the reference size.  Default is
            ``True``.
        reference_size_x : str, optional
            Explicit reference size in X when *reference_size_auto* is
            ``False``.  Default is ``"0"``.
        reference_size_y : str, optional
            Explicit reference size in Y.  Default is ``"0"``.

        Examples
        --------
        >>> u1.set_port_properties(reference_height="50um")
        """
        self.port_properties = {
            "reference_height": reference_height,
            "reference_size_auto": reference_size_auto,
            "reference_size_x": reference_size_x,
            "reference_size_y": reference_size_y,
        }

    def to_dict(self) -> dict:
        """Serialize the component configuration."""
        data: dict = {"reference_designator": self.reference_designator}
        part_type = self.type
        if part_type is not None:
            data["part_type"] = part_type
        for key in ("enabled", "definition", "placement_layer"):
            val = getattr(self, key)
            if val is not None:
                data[key] = val
        if self.pins:
            data["pins"] = self.pins
        if self.pin_pair_model:
            data["pin_pair_model"] = self.pin_pair_model
        for key in (
            "s_parameter_model",
            "spice_model",
            "netlist_model",
            "ic_die_properties",
            "solder_ball_properties",
            "port_properties",
        ):
            val = getattr(self, key)
            if val not in [None, {}, []]:
                data[key] = val
        return data


class CfgComponents:
    """Fluent builder for the ``components`` configuration list."""

    def __init__(self, pedb=None, components_data=None):
        self._pedb = pedb
        self.components = []

        if components_data:
            for comp in components_data:
                obj = self._pedb.components.instances[comp["reference_designator"]] if self._pedb else None
                self.components.append(CfgComponent(self._pedb, obj, **comp))

    def add(
        self,
        reference_designator: str,
        part_type=None,
        enabled=None,
        definition=None,
        placement_layer=None,
    ):
        """Add a component configuration entry.

        Parameters
        ----------
        reference_designator : str
            Unique component reference designator (e.g. ``"U1"``).
        part_type : str, optional
            Component type.  Accepted values: ``"resistor"``,
            ``"capacitor"``, ``"inductor"``, ``"ic"``, ``"io"``,
            ``"other"``.
        enabled : bool, optional
            Whether the component is enabled in the simulation.
        definition : str, optional
            Component part definition name.
        placement_layer : str, optional
            Layer on which the component is placed.

        Returns
        -------
        CfgComponent
            The newly created component builder.

        Examples
        --------
        >>> r1 = cfg.components.add("R1", part_type="resistor", enabled=True)
        >>> r1.add_pin_pair_rlc("1", "2", resistance="100ohm", resistance_enabled=True)
        """
        comp = CfgComponent(
            self._pedb,
            None,
            reference_designator=reference_designator,
            part_type=part_type,
            enabled=enabled,
            definition=definition,
            placement_layer=placement_layer,
        )
        self.components.append(comp)
        return comp

    def clean(self):
        self.components = []

    def apply(self):
        for comp in self.components:
            comp.set_parameters_to_edb()

    def retrieve_parameters_from_edb(self):
        self.clean()
        if self._pedb is None:
            return self.to_list()
        comps_in_db = self._pedb.components
        for _, comp in comps_in_db.instances.items():
            cfg_comp = CfgComponent(self._pedb, comp)
            cfg_comp.retrieve_parameters_from_edb()
            self.components.append(cfg_comp)

    def to_list(self):
        """Serialize all configured components."""
        return [c.to_dict() for c in self.components]

