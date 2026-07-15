# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

import re

from ansys.edb.core.definition.component_property import ComponentProperty as CoreComponentProperty
from ansys.edb.core.definition.die_property import (
    DieOrientation as CoreDieOrientation,
    DieProperty as CoreDieProperty,
    DieType as CoreDieType,
)
from ansys.edb.core.definition.port_property import PortProperty as CorePortProperty
from ansys.edb.core.definition.solder_ball_property import (
    SolderBallProperty as CoreSolderBallProperty,
    SolderballShape as CoreSolderballShape,
)
from pydantic import BaseModel

from pyedb.configuration.cfg_common import CfgBase
from pyedb.grpc.database.components import _EDB_CORE_TYPED_COMPONENT_PROPERTY


def _smallest_pin_pad_size(comp) -> float | None:
    """Return the smallest pin pad dimension (metres) for *comp*, or ``None``.

    Only pins that expose a valid ``bounding_box`` attribute returning a
    non-degenerate ``((x1, y1), (x2, y2))`` tuple are considered.  Pins
    that do not have the attribute or that return a zero-area box are
    skipped silently so a single bad pin never blocks the whole component.
    """
    min_size: float | None = None
    for pin in comp.pins.values():
        bbox = getattr(pin, "bounding_box", None)
        if not bbox or len(bbox) < 2:
            continue
        p0, p1 = bbox[0], bbox[1]
        if not p0 or not p1 or len(p0) < 2 or len(p1) < 2:
            continue
        dx: float | int = abs(float(p1[0]) - float(p0[0]))
        dy: float | int = abs(float(p1[1]) - float(p0[1]))
        size: float | int = dx if dx < dy else dy
        if size > 0 and (min_size is None or size < min_size):
            min_size = size
    return min_size


def _height_from_diameter(diameter: str) -> str:
    """Return ``2/3 * diameter`` as a unit string, e.g. ``"100um"``.

    Raises ``ValueError`` if *diameter* cannot be parsed.
    """
    m = re.match(r"([0-9.eE+\-]+)\s*([a-zA-Z]*)", diameter)
    if m is None:
        raise ValueError(f"Cannot parse diameter value: {diameter!r}")
    num = float(m.group(1))
    unit = m.group(2) or "um"
    return f"{num * 2 / 3:.6g}{unit}"


def _get_snake_to_pascal():
    """Lazy import of snake_to_pascal to avoid loading .NET when using gRPC."""
    from pyedb.dotnet.database.general import snake_to_pascal

    return snake_to_pascal


_solder_shape_mapping = {
    "cylinder": CoreSolderballShape.SOLDERBALL_CYLINDER,
    "spheroid": CoreSolderballShape.SOLDERBALL_SPHEROID,
    "no_solder_ball": CoreSolderballShape.NO_SOLDERBALL,
}

_die_type_mapping = {
    "flip_chip": CoreDieType.FLIPCHIP,
    "flipchip": CoreDieType.FLIPCHIP,
    "wire_bond": CoreDieType.WIREBOND,
    "wirebond": CoreDieType.WIREBOND,
    "no_die": CoreDieType.NONE,
    "none": CoreDieType.NONE,
}

_die_orientation_mapping = {
    "chip_up": CoreDieOrientation.CHIP_UP,
    "chip_down": CoreDieOrientation.CHIP_DOWN,
}

_NO_DIE_TYPES = ("no_die", "none", None)


def _persist_component_property(core_component, cp) -> None:
    """Write *cp* back to *core_component* so changes are saved to disk.

    On EDB 2026.1 with the typed component property API (``ICComponentProperty``,
    ``RLCComponentProperty``, ``IOComponentProperty``) the server-side
    ``SetComponentProperty`` RPC silently drops sub-property mutations when the
    value is passed as a typed subclass.  Casting to the base
    :class:`ComponentProperty` (same underlying ``msg`` id) makes the write
    persist correctly across save / reopen.

    Additionally, sub-properties **must** be brand-new objects created via
    ``SolderBallProperty.create()`` / ``PortProperty.create()`` /
    ``DieProperty.create()``; mutating an instance returned by
    ``cp.solder_ball_property`` (etc.) and re-assigning it does **not**
    persist in 2026.1 even with the base-class cast.  Callers must therefore
    ``create()`` the sub-property, populate it, then assign it to *cp* before
    calling this helper.

    Parameters
    ----------
    core_component : ansys.edb.core.hierarchy.component_group.ComponentGroup
        The raw core component (``pyedb_obj.core``).
    cp : ComponentProperty | ICComponentProperty | IOComponentProperty | RLCComponentProperty
        The mutated component property previously fetched from
        ``core_component.component_property``.
    """
    core_component.component_property = CoreComponentProperty(cp.msg)


class CfgPinPairModel(BaseModel):
    """Represent one pin-pair RLC model entry."""

    first_pin: str
    second_pin: str
    resistance: str | float | int | None = None
    inductance: str | float | int | None = None
    capacitance: str | float | int | None = None
    is_parallel: bool = False
    resistance_enabled: bool = False
    inductance_enabled: bool = False
    capacitance_enabled: bool = False


class CfgComponent(CfgBase):
    """Fluent builder for a single component entry."""

    def __init__(self, _pedb=None, pedb_object=None, **kwargs):
        """Initialize a CfgComponent instance."""
        if (
            pedb_object is None
            and not hasattr(_pedb, "components")
            and "reference_designator" not in kwargs
            and _pedb is not None
        ):
            kwargs["reference_designator"] = _pedb
            _pedb = None
        self._pedb = _pedb
        self.pyedb_obj = pedb_object

        self.enabled = kwargs.get("enabled")
        self.reference_designator = kwargs.get("reference_designator")
        self.definition = kwargs.get("definition")
        self.type = kwargs["part_type"].lower() if kwargs.get("part_type") else None
        self.placement_layer = kwargs.get("placement_layer")
        self.pins = kwargs.get("pins", [])

        self.port_properties = kwargs.get("port_properties", {})
        self.solder_ball_properties = kwargs.get("solder_ball_properties", {})
        ic_die = kwargs.get("ic_die_properties")
        self._ic_die_explicitly_set = ic_die is not None
        self.ic_die_properties = ic_die if ic_die is not None else {"type": "no_die"}
        self.pin_pair_model = kwargs.get("pin_pair_model", [])
        self.spice_model = kwargs.get("spice_model", {})
        self.s_parameter_model = kwargs.get("s_parameter_model", {})
        self.netlist_model = kwargs.get("netlist_model", {})
        self.vendor_library_model = kwargs.get("vendor_library_model", {})

    def retrieve_model_properties_from_edb(self):
        """Retrieve model properties from the EDB design."""
        c_p = self.pyedb_obj
        model_type = c_p.model_type

        if "NetlistModel" in model_type:
            self.netlist_model["netlist"] = c_p.netlist_model
        elif "PinPairModel" in model_type or "RLC" in model_type:
            pin_pairs = c_p.pin_pairs[::]
            if not pin_pairs:
                return
            pp0 = pin_pairs[0]
            temp = {"first_pin": pp0.first_pin, "second_pin": pp0.second_pin}
            # Read RLC directly from the cached pin_pair to avoid repeated
            # GetComponentProperty() calls (EDB 2026.1 heap-corruption risk).
            try:
                rlc = pp0._pin_pair_rlc
                temp.update(
                    is_parallel=rlc.IsParallel,
                    resistance=str(rlc.R.ToDouble()),
                    resistance_enabled=rlc.REnabled,
                    inductance=str(rlc.L.ToDouble()),
                    inductance_enabled=rlc.LEnabled,
                    capacitance=str(rlc.C.ToDouble()),
                    capacitance_enabled=rlc.CEnabled,
                )
            except (AttributeError, ValueError, TypeError):
                rlc_enable = c_p.rlc_enable or [False, False, False]
                temp.update(
                    is_parallel=False,
                    resistance=str(c_p.res_value),
                    resistance_enabled=rlc_enable[0],
                    inductance=str(c_p.ind_value),
                    inductance_enabled=rlc_enable[1],
                    capacitance=str(c_p.cap_value),
                    capacitance_enabled=rlc_enable[2],
                )
            self.pin_pair_model.append(temp)
        elif "SParameterModel" in model_type:
            self.s_parameter_model.update(
                reference_net=c_p.model.reference_net,
                model_name=c_p.model.component_model_name,
            )
        elif "SPICEModel" in model_type:
            self.spice_model.update(
                model_name=c_p.model.model_name,
                model_path=c_p.model.spice_file_path,
                sub_circuit=c_p.model.sub_circuit,
                terminal_pairs=c_p.model.pin_pairs,
            )

    def _set_ic_die_properties_to_edb(self):
        if not self.ic_die_properties:
            return
        grpc = self._pedb.grpc
        die_type = (self.ic_die_properties.get("type") or "").lower() or None
        if grpc:
            # See ``_persist_component_property`` for the EDB 2026.1 quirk: each
            # sub-property must be a freshly ``.create()``-d instance, populated
            # locally, then assigned to the typed component property — only
            # then does a base-class write-back persist to disk.
            cp = self.pyedb_obj.core.component_property
            ic_die_prop = CoreDieProperty.create()
            ic_die_prop.die_type = _die_type_mapping[die_type or "none"]
            if die_type not in _NO_DIE_TYPES:
                orientation = self.ic_die_properties.get("orientation")
                if orientation:
                    ic_die_prop.die_orientation = _die_orientation_mapping[orientation]
                if die_type == "wire_bond":
                    height = self.ic_die_properties.get("height")
                    if height:
                        ic_die_prop.height = self._pedb.value(height)
            cp.die_property = ic_die_prop
            _persist_component_property(self.pyedb_obj.core, cp)
        else:
            comp_prop = self.pyedb_obj.component_property
            cp = comp_prop.core if hasattr(comp_prop, "core") else comp_prop
            ic_die_prop = cp.GetDieProperty().Clone()
            s2p = _get_snake_to_pascal()
            ic_die_prop.SetType(getattr(self._pedb._edb.Definition.DieType, s2p(die_type)))
            if die_type not in _NO_DIE_TYPES:
                orientation = self.ic_die_properties.get("orientation")
                if orientation:
                    ic_die_prop.SetOrientation(getattr(self._pedb._edb.Definition.DieOrientation, s2p(orientation)))
                if die_type == "wire_bond":
                    height = self.ic_die_properties.get("height")
                    if height:
                        ic_die_prop.SetHeight(self._pedb.edb_value(height))
            self.pyedb_obj.ic_die_properties = ic_die_prop

    def _set_port_properties_to_edb(self):
        if not self.port_properties:
            return
        grpc = self._pedb.grpc
        height = self.port_properties.get("reference_height")
        reference_size_auto = self.port_properties.get("reference_size_auto")
        ref_x = self.port_properties.get("reference_size_x", 0)
        ref_y = self.port_properties.get("reference_size_y", 0)
        if grpc:
            # See ``_persist_component_property``: we need a fresh PortProperty
            # to make the write-back persist on EDB 2026.1.  Initial defaults
            # for fields the user did not specify are copied from the existing
            # port_property so we do not regress unrelated settings.
            cp = self.pyedb_obj.core.component_property
            existing = cp.port_property
            port_prop = CorePortProperty.create()
            port_prop.reference_height = self._pedb.value(height) if height is not None else existing.reference_height
            port_prop.reference_size_auto = (
                reference_size_auto if reference_size_auto is not None else existing.reference_size_auto
            )
            port_prop.set_reference_size(self._pedb.value(ref_x), self._pedb.value(ref_y))
            cp.port_property = port_prop
            _persist_component_property(self.pyedb_obj.core, cp)
        else:
            # Use a mutable clone to avoid ReadOnlyModificationAttemptException.
            cp = self.pyedb_obj._get_component_property_clone()
            port_prop = cp.GetPortProperty().Clone()
            if height is not None:
                port_prop.SetReferenceHeight(self._pedb.edb_value(height))
            if reference_size_auto is not None:
                port_prop.SetReferenceSizeAuto(reference_size_auto)
            port_prop.SetReferenceSize(self._pedb.edb_value(ref_x), self._pedb.edb_value(ref_y))
            cp.SetPortProperty(port_prop)
            self.pyedb_obj.edbcomponent.SetComponentProperty(cp)

    def _set_model_properties_to_edb(self):
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
        elif self.vendor_library_model:
            self._set_vendor_library_model_to_edb()
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

    def _set_vendor_library_model_to_edb(self):
        """Resolve a vendor-library model entry and assign it to this component.

        Steps:

        1. Call ``get_vendor_libraries()`` to obtain the :class:`ComponentLib`.
        2. Locate the :class:`ComponentPart` via vendor → series → part_name.
        3. Export the scikit-rf ``Network`` to a Touchstone ``.s2p`` file
           (cached in *touchstone_cache_dir* or a ``component_lib_cache`` folder
           next to the ``.aedb`` file).
        4. Call :meth:`assign_s_param_model` on the component instance.
        """
        import os
        from pathlib import Path

        vlm = self.vendor_library_model
        vendor = vlm.get("vendor", "")
        series = vlm.get("series", "")
        part_name = vlm.get("part_name", "")
        reference_net = vlm.get("reference_net", "GND")
        cache_dir = vlm.get("touchstone_cache_dir")

        if not (vendor and series and part_name):
            raise ValueError(f"vendor_library_model requires 'vendor', 'series', and 'part_name' keys. Got: {vlm!r}")

        comp_lib = self._pedb.components.get_vendor_libraries()

        # Locate the ComponentPart in capacitors or inductors
        part = None
        for lib_section in (comp_lib.capacitors, comp_lib.inductors):
            if vendor in lib_section:
                series_dict = lib_section[vendor]
                if series in series_dict and part_name in series_dict[series]:
                    part = series_dict[series][part_name]
                    break

        if part is None:
            available_caps = list(comp_lib.capacitors.keys())
            available_inds = list(comp_lib.inductors.keys())
            raise KeyError(
                f"Vendor '{vendor}' / series '{series}' / part '{part_name}' not found in "
                f"vendor libraries. Available capacitor vendors: {available_caps}, "
                f"inductor vendors: {available_inds}."
            )

        # Determine Touchstone cache directory
        if cache_dir is None:
            cache_dir = os.path.join(os.path.dirname(self._pedb.edbpath), "component_lib_cache")
        Path(cache_dir).mkdir(parents=True, exist_ok=True)

        snp_path = part.write_touchstone(os.path.join(cache_dir, f"{part_name}.s2p"))

        self.pyedb_obj.assign_s_param_model(snp_path, part_name, reference_net)

    def _set_solder_ball_properties_to_edb(self):
        sbp_data = self.solder_ball_properties
        if not sbp_data:
            return
        shape = sbp_data.get("shape")
        diameter = sbp_data.get("diameter")
        height = sbp_data.get("height")
        mid_diameter = sbp_data.get("mid_diameter", diameter)
        material = sbp_data.get("material")

        if self._pedb.grpc:
            if not shape:
                raise ValueError("Solderball shape must be either cylinder or spheroid")
            shape_lower = shape.lower()
            if shape_lower not in ("cylinder", "spheroid"):
                raise ValueError("Solderball shape must be either cylinder or spheroid")
            # See ``_persist_component_property``: we MUST instantiate a brand-
            # new SolderBallProperty (mutating one returned from
            # ``cp.solder_ball_property`` does not persist on EDB 2026.1, even
            # with the base-class write-back).
            cp = self.pyedb_obj.core.component_property

            # For IC components, solder balls imply a flip-chip die.  If the
            # user did not explicitly configure die type override it with FLIPCHIP
            # and use the orientation stored in the solder-ball data.  This
            # mirrors the behavior of ``components.set_solder_ball`` which
            # always sets die_type = FLIPCHIP when processing an IC.
            if self.pyedb_obj.type.lower() == "ic":
                configured_die_type = (self.ic_die_properties.get("type") or "no_die").lower()
                if configured_die_type in _NO_DIE_TYPES:
                    ic_die_prop = CoreDieProperty.create()
                    ic_die_prop.die_type = CoreDieType.FLIPCHIP
                    orientation = (sbp_data.get("orientation") or "chip_down").lower()
                    ic_die_prop.die_orientation = (
                        CoreDieOrientation.CHIP_UP if orientation == "chip_up" else CoreDieOrientation.CHIP_DOWN
                    )
                    cp.die_property = ic_die_prop

            sbp = CoreSolderBallProperty.create()
            if shape_lower == "cylinder":
                sbp.set_diameter(self._pedb.value(diameter), self._pedb.value(diameter))
            else:  # spheroid
                sbp.set_diameter(self._pedb.value(diameter), self._pedb.value(mid_diameter))
            sbp.shape = _solder_shape_mapping[shape_lower]
            if height is not None:
                sbp.height = self._pedb.value(height)
            if material is not None:
                sbp.material_name = material
            cp.solder_ball_property = sbp
            _persist_component_property(self.pyedb_obj.core, cp)
        else:
            if not shape:
                return
            self._pedb.components.set_solder_ball(
                component=self.pyedb_obj.name,
                sball_diam=self._pedb.edb_value(diameter).ToDouble() if diameter else None,
                sball_height=self._pedb.edb_value(height).ToDouble() if height else None,
                shape=shape.capitalize(),
                sball_mid_diam=self._pedb.edb_value(mid_diameter).ToDouble() if mid_diameter else None,
                chip_orientation=sbp_data.get("orientation", "chip_down"),
                material_name=material or "solder",
            )

    def _retrieve_ic_die_properties_from_edb(self):
        die_props = self.pyedb_obj.ic_die_properties
        die_type = die_props.die_type
        temp = {"type": "no_die" if die_type in _NO_DIE_TYPES else die_type}
        temp["orientation"] = die_props.die_orientation
        if die_type not in _NO_DIE_TYPES:
            if die_type == "wire_bond":
                temp["height"] = str(die_props.height)
        self.ic_die_properties = temp
        self._ic_die_explicitly_set = True

    def _retrieve_solder_ball_properties_from_edb(self):
        cp = self.pyedb_obj
        diam = cp.solder_ball_diameter
        self.solder_ball_properties = {
            "uses_solder_ball": cp.uses_solderball,
            "shape": cp.solder_ball_shape,
            "diameter": str(diam[0]),
            "mid_diameter": str(diam[1]),
            "height": str(cp.solder_ball_height),
            "material": cp.solder_ball_material,
        }

    def _retrieve_port_properties_from_edb(self):
        if self.type.lower() not in ("ic", "io", "other"):
            return
        pp = self.pyedb_obj.component_property.port_property
        self.port_properties = {
            "reference_height": str(pp.reference_height),
            "reference_size_auto": pp.reference_size_auto,
            "reference_size_x": str(pp.get_reference_size()[0]),
            "reference_size_y": str(pp.get_reference_size()[1]),
        }

    def set_parameters_to_edb(self):
        """Set component parameters to the EDB design."""
        obj = self.pyedb_obj
        if obj is None:
            return
        if self.type:
            obj.type = self.type
        if self.enabled is not None:
            obj.enabled = self.enabled
        self._set_model_properties_to_edb()
        comp_type = obj.type.lower()
        if comp_type == "ic":
            self._set_ic_die_properties_to_edb()
            self._set_port_properties_to_edb()
            self._set_solder_ball_properties_to_edb()
        elif comp_type in ("io", "other"):
            self._set_solder_ball_properties_to_edb()
            self._set_port_properties_to_edb()

    def retrieve_parameters_from_edb(self):
        """Retrieve component parameters from the EDB design."""
        obj = self.pyedb_obj
        if obj is None:
            return
        self.type = obj.type
        self.definition = obj.part_name
        self.reference_designator = obj.name
        self.retrieve_model_properties_from_edb()
        comp_type = obj.type.lower()
        if comp_type == "ic":
            self._retrieve_ic_die_properties_from_edb()
            self._retrieve_port_properties_from_edb()
            self._retrieve_solder_ball_properties_from_edb()
        elif comp_type in ("io", "other"):
            self._retrieve_solder_ball_properties_from_edb()
            self._retrieve_port_properties_from_edb()

    def add_pin_pair_rlc(
        self,
        first_pin: str,
        second_pin: str,
        resistance: str | float | int | None = None,
        inductance: str | float | int | None = None,
        capacitance: str | float | int | None = None,
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
        r1 = cfg.components.add("R1", part_type="resistor")
        r1.add_pin_pair_rlc("1", "2", resistance="100ohm", resistance_enabled=True)
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
            ).model_dump()
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
        u1.set_s_parameter_model("cap_100nF", "/snp/cap.s2p", "GND")
        """
        self.s_parameter_model = {"model_name": model_name, "model_path": model_path, "reference_net": reference_net}

    def set_vendor_library_model(
        self,
        vendor: str,
        series: str,
        part_name: str,
        reference_net: str = "GND",
        touchstone_cache_dir: str | None = None,
    ):
        """Assign a vendor component-library model (capacitor or inductor) to this component.

        The Ansys component library is looked up at apply-time via
        ``edbapp.components.get_vendor_libraries()``.  The scikit-rf
        ``Network`` is exported to a Touchstone ``.s2p`` file and then
        registered as an S-parameter model on the component instance.

        Parameters
        ----------
        vendor : str
            Vendor folder name inside the Ansys component library, e.g.
            ``"Murata"``.
        series : str
            Series folder name, e.g. ``"GRM15"``.
        part_name : str
            Exact part name as listed in the library ``index.txt``, e.g.
            ``"GRM155R71C104KA88"``.
        reference_net : str, optional
            Reference (ground) net for the model assignment.  Default is
            ``"GND"``.
        touchstone_cache_dir : str, optional
            Directory where exported Touchstone files are cached.  When
            ``None`` (default) a ``component_lib_cache`` folder next to the
            ``.aedb`` file is used.

        Examples
        --------
        cfg = edb.configuration.create_config_builder()
        c1 = cfg.components.add("C1", part_type="capacitor")
        c1.set_vendor_library_model("Murata", "GRM15", "GRM155R71C104KA88", reference_net="GND")
        edb.configuration.run(cfg)
        """
        data = {
            "vendor": vendor,
            "series": series,
            "part_name": part_name,
            "reference_net": reference_net,
        }
        if touchstone_cache_dir is not None:
            data["touchstone_cache_dir"] = touchstone_cache_dir
        self.vendor_library_model = data

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
        u1.set_spice_model("ic_spice", "/spice/ic.sp", sub_circuit="IC_TOP")
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
        u1.set_ic_die_properties("flip_chip", orientation="chip_down")
        """
        data = {"type": die_type}
        if die_type != "no_die":
            data["orientation"] = orientation
            if die_type == "wire_bond" and height:
                data["height"] = height
        self.ic_die_properties = data
        self._ic_die_explicitly_set = True

    def set_solder_ball_properties(
        self,
        shape: str = "cylinder",
        diameter: str | None = None,
        height: str | None = None,
        material: str = "solder",
        mid_diameter=None,
        orientation: str = "chip_down",
        reference_designator: str | None = None,
    ):
        """Configure solder-ball geometry for this component.

        Parameters
        ----------
        shape : str, optional
            Solder-ball shape.  ``"cylinder"`` (default), ``"spheroid"``, or
            ``"no_solder_ball"``.
        diameter : str, optional
            Outer diameter, e.g. ``"150um"``.  When *None* and a live EDB
            session is attached the smallest pin pad size found on the
            component is used automatically.  Falls back to ``"150um"`` if
            the pad size cannot be determined.
        height : str, optional
            Solder-ball height, e.g. ``"100um"``.  When *None* the height is
            set to ``2 * diameter / 3``.
        material : str, optional
            Material name.  Default is ``"solder"``.
        mid_diameter : str or None, optional
            Mid-diameter for spheroid shape.  Defaults to *diameter* when
            *None*.
        orientation : str, optional
            Die orientation for IC components.  ``"chip_down"`` (default) or
            ``"chip_up"``.
        reference_designator : str, optional
            Override the component reference designator used when querying pin
            sizes from EDB.  When *None* ``self.reference_designator`` is
            used.

        Examples
        --------
        u1.set_solder_ball_properties("cylinder", "150um", "100um")
        u1.set_solder_ball_properties()  # auto-sizes from pin pads

        """
        refdes = reference_designator or self.reference_designator
        if diameter is None:
            diameter = "150um"  # safe default
            if self._pedb is not None and refdes is not None:
                comp = self._pedb.components.instances.get(refdes)
                if comp is not None:
                    min_size = _smallest_pin_pad_size(comp)
                    if min_size is not None and min_size > 0:
                        diameter = f"{min_size * 1e6:.6g}um"
        if height is None:
            height = _height_from_diameter(diameter)
        data = {
            "shape": shape,
            "diameter": diameter,
            "height": height,
            "material": material,
            "orientation": orientation,
        }
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
        u1.set_port_properties(reference_height="50um")
        """
        self.port_properties = {
            "reference_height": reference_height,
            "reference_size_auto": reference_size_auto,
            "reference_size_x": reference_size_x,
            "reference_size_y": reference_size_y,
        }

    def _is_default_ic_die(self, key, val) -> bool:
        """Return True if *val* is the autopopulated default ic_die payload."""
        return (
            key == "ic_die_properties"
            and val == {"type": "no_die"}
            and not getattr(self, "_ic_die_explicitly_set", False)
        )

    def to_dict(self) -> dict:
        """Serialize the component configuration."""
        data: dict = {"reference_designator": self.reference_designator}
        if self.type is not None:
            data["part_type"] = self.type
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
            "vendor_library_model",
            "spice_model",
            "netlist_model",
            "ic_die_properties",
            "solder_ball_properties",
            "port_properties",
        ):
            val = getattr(self, key)
            if val not in (None, {}, []) and not self._is_default_ic_die(key, val):
                data[key] = val
        return data


class CfgComponents:
    """Fluent builder for the ``components`` configuration list."""

    def __init__(self, pedb=None, components_data=None):
        """Initialize a CfgComponents instance."""
        self._pedb = pedb
        if components_data:
            self.components = [
                CfgComponent(
                    self._pedb,
                    self._pedb.components.instances[c["reference_designator"]] if self._pedb else None,
                    **c,
                )
                for c in components_data
            ]
        else:
            self.components = []

    def get(self, reference_designator: str) -> "CfgComponent":
        """Return a :class:`CfgComponent` for an *existing* EDB component.

        The component is looked up by *reference_designator* in the live EDB
        session and its current properties (type, model, die, solder-ball,
        port) are preloaded into the returned builder.  Mutate the returned
        object and then call ``edb.configuration.run(cfg)`` to push the
        changes back to the database.

        If the component has already been registered via :meth:`add` or a
        previous :meth:`get` call, the cached entry is returned instead of
        creating a duplicate.

        Parameters
        ----------
        reference_designator : str
            Reference designator of the component to retrieve, e.g. ``"U1"``.

        Returns
        -------
        CfgComponent
            Component builder pre-populated with current EDB properties.

        Raises
        ------
        KeyError
            If no EDB session is attached or the component does not exist.

        Examples
        --------
        cfg = edb.configuration.create_config_builder()
        u1 = cfg.components.get("U1")
        u1.set_solder_ball_properties("cylinder", "150um", "100um")
        edb.configuration.run(cfg)
        """
        # Return cached entry if already present
        cached = next((c for c in self.components if c.reference_designator == reference_designator), None)
        if cached:
            return cached
        if self._pedb is None:
            raise KeyError(
                "No EDB session is attached to this builder. "
                "Use edb.configuration.create_config_builder() to get a session-aware builder."
            )
        instances = self._pedb.components.instances
        if reference_designator not in instances:
            raise KeyError(f"Component '{reference_designator}' not found in the EDB layout.")

        pedb_obj = instances[reference_designator]
        comp = CfgComponent(self._pedb, pedb_obj, reference_designator=reference_designator, part_type=pedb_obj.type)
        comp.retrieve_parameters_from_edb()
        self.components.append(comp)
        return comp

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
        r1 = cfg.components.add("R1", part_type="resistor", enabled=True)
        r1.add_pin_pair_rlc("1", "2", resistance="100ohm", resistance_enabled=True)
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
        """Clear all components from the list."""
        self.components = []

    def apply(self):
        """Apply all component settings to the EDB design."""
        for comp in self.components:
            comp.set_parameters_to_edb()

    def retrieve_parameters_from_edb(self):
        """Read all component settings from the open EDB design."""
        self.clean()
        if self._pedb is None:
            return [c.to_dict() for c in self.components]
        for obj in self._pedb.components.instances.values():
            cfg_comp = CfgComponent(self._pedb, obj)
            cfg_comp.retrieve_parameters_from_edb()
            self.components.append(cfg_comp)

    def get_data_from_db(self):
        """Read all component settings from the open EDB design."""
        return self.retrieve_parameters_from_edb()

    def to_list(self):
        """Serialize all configured components."""
        return [c.to_dict() for c in self.components]
