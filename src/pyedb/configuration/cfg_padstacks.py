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
"""Build padstack definition and instance entries for configuration payloads."""

from pydantic import Field, PrivateAttr, field_validator

from pyedb.configuration.cfg_common import CfgBaseModel as CfgBase
from pyedb.misc.decorators import deprecated


def _make_pad_entry(layer, shape, diameter, x_size, y_size, offset_x, offset_y, rotation):
    """Build a single pad entry dict for a given layer and shape."""
    entry = {
        "layer_name": layer,
        "shape": shape,
        "offset_x": str(offset_x),
        "offset_y": str(offset_y),
        "rotation": str(rotation),
    }
    if shape == "circle":
        if diameter is not None:
            entry["diameter"] = str(diameter)
    elif shape == "square":
        if x_size is not None:
            entry["size"] = str(x_size)
    elif shape in ("rectangle", "oval", "bullet"):
        if x_size is not None:
            entry["x_size"] = str(x_size)
        if y_size is not None:
            entry["y_size"] = str(y_size)
    return entry


class CfgBackdrillParameters(CfgBase):
    """Store optional backdrill definitions for a padstack instance."""

    class DrillParametersByLayer(CfgBase):
        drill_to_layer: str
        diameter: str

    class DrillParametersByLayerWithStub(DrillParametersByLayer):
        stub_length: str | None

    class DrillParameters(CfgBase):
        drill_depth: str
        diameter: str

    from_top: DrillParameters | DrillParametersByLayer | DrillParametersByLayerWithStub | None = None
    from_bottom: DrillParameters | DrillParametersByLayer | DrillParametersByLayerWithStub | None = None

    def add_backdrill_to_layer(
        self, drill_to_layer: str, diameter: str, stub_length: str = "", drill_from_bottom: bool = True
    ):
        """Configure a backdrill stopping at a named layer.

        Parameters
        ----------
        drill_to_layer : str
            Target layer name where the backdrill stops.
        diameter : str
            Backdrill diameter, e.g. ``"0.25mm"``.
        stub_length : str or None, optional
            Stub length beyond the target layer.  ``None`` means no stub.
        drill_from_bottom : bool, optional
            ``True`` (default) drills from the bottom; ``False`` from the top.
        """
        if stub_length is None:
            drill = self.DrillParametersByLayer(drill_to_layer=drill_to_layer, diameter=diameter)
        else:
            drill = self.DrillParametersByLayerWithStub(
                drill_to_layer=drill_to_layer, diameter=diameter, stub_length=stub_length
            )

        if drill_from_bottom:
            self.from_bottom = drill
        else:
            self.from_top = drill


class CfgPadstackInstance(CfgBase):
    """Represent one padstack instance entry."""

    name: str | None = None
    eid: int | None = Field(None, alias="id")

    backdrill_parameters: CfgBackdrillParameters | None = Field(default_factory=CfgBackdrillParameters)
    is_pin: bool = Field(default=False)

    net_name: str | None = None
    layer_range: list[str] | None = None
    definition: str | None = None
    position: list[str | float] | None = None
    rotation: str | None = None

    hole_override_enabled: bool | None = None
    hole_override_diameter: str | float | None = None
    solder_ball_layer: str | None = None

    @field_validator("rotation", mode="before")
    @staticmethod
    def _coerce_rotation_to_str(v: str | float | None) -> str | None:
        """Coerce rotation value to string.

        Converts any numeric rotation value (like 45 or 90.5) to its string
        representation (like "45" or "90.5"), while leaving None values unchanged.
        This maintains consistency since rotation can be specified as either a
        string or float in the method signatures, but the model stores it as a
        string internally.

        Parameters
        ----------
        v : str, float, or None
            Rotation value to coerce.

        Returns
        -------
        str or None
            String representation of the rotation value, or None if input is None.
        """
        return str(v) if v is not None else None

    @field_validator("backdrill_parameters", mode="before")
    @staticmethod
    def _default_backdrill(v):
        return v if v is not None else CfgBackdrillParameters()

    @property
    def _id(self):
        return self.eid

    @classmethod
    def create(cls, **kwargs) -> "CfgPadstackInstance":
        """Create a :class:`CfgPadstackInstance` with an empty backdrill object."""
        return cls(**kwargs)

    def set_backdrill(
        self,
        drill_to_layer: str,
        diameter: str,
        stub_length: str | None = None,
        drill_from_bottom: bool = True,
    ):
        """Configure backdrill parameters for this padstack instance.

        Parameters
        ----------
        drill_to_layer : str
            Layer name where the backdrill stops.
        diameter : str
            Backdrill bore diameter, e.g. ``"0.25mm"``.
        stub_length : str or None, optional
            Stub length beyond the target layer.  ``None`` means no stub.
        drill_from_bottom : bool, optional
            ``True`` (default) drills from the bottom side.

        Returns
        -------
        CfgPadstackInstance
            *self* — enables method chaining.

        Examples
        --------
        via.set_backdrill("L3", "0.25mm", drill_from_bottom=True)
        """
        if self.backdrill_parameters is None:
            self.backdrill_parameters = CfgBackdrillParameters()
        self.backdrill_parameters.add_backdrill_to_layer(
            drill_to_layer=drill_to_layer,
            diameter=diameter,
            stub_length=stub_length,
            drill_from_bottom=drill_from_bottom,
        )
        return self


class CfgPadstackDefinition(CfgBase):
    """Represent one padstack definition entry."""

    name: str

    hole_plating_thickness: str | float | None = None
    material: str | None = None
    hole_range: str | None = None

    pad_parameters: dict | None = None
    hole_parameters: dict | None = None
    solder_ball_parameters: dict | None = None

    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
    }

    @classmethod
    def create(cls, **kwargs) -> "CfgPadstackDefinition":
        """Create a :class:`CfgPadstackDefinition` from keyword arguments."""
        return cls(**kwargs)


class CfgPadstacks(CfgBase):
    """Collect padstack definitions and instances for serialization."""

    definitions: list[CfgPadstackDefinition] = Field(default_factory=list)
    instances: list[CfgPadstackInstance] = Field(default_factory=list)

    # PrivateAttr used to not serialize pydantic model_dump()
    _pedb: object = PrivateAttr(default=None)
    _cfg_stackup: object = PrivateAttr(default=None)

    model_config = {"populate_by_name": True, "extra": "forbid", "arbitrary_types_allowed": True}

    def _set_pedb(self, pedb):
        """Attach a live EDB session (called by CfData)."""
        self._pedb = pedb

    def _set_cfg_stackup(self, cfg_stackup):
        """Attach the CfgStackup builder (called by CfData)."""
        self._cfg_stackup = cfg_stackup

    @classmethod
    def create(cls, pedb=None, **kwargs) -> "CfgPadstacks":
        """Create a :class:`CfgPadstacks` from keyword arguments."""
        obj = cls(**kwargs)
        if pedb is not None:
            obj._pedb = pedb
        return obj

    def clean(self):
        """Reset all padstack definitions and instances to empty lists."""
        self.definitions = []
        self.instances = []

    def get_definition(self, name: str) -> "CfgPadstackDefinition":
        """Return a :class:`CfgPadstackDefinition` for an existing padstack definition.

        If the definition has already been registered via :meth:`add_definition`
        the cached entry is returned, otherwise the definition is looked up in
        the live EDB session and a new entry is created from its current properties.

        Parameters
        ----------
        name : str
            Padstack definition name, e.g. ``"via_0.2"``.

        Returns
        -------
        CfgPadstackDefinition
            Definition builder pre-populated with current properties.

        Raises
        ------
        KeyError
            If no EDB session is attached or the definition does not exist.

        Examples
        --------
        cfg = edb.configuration.create_config_builder()
        via_def = cfg.padstacks.get_definition("via_0.2")
        via_def.hole_plating_thickness = "30um"
        edb.configuration.run(cfg)
        """
        for d in self.definitions:
            if d.name == name:
                return d
        if self._pedb is None:
            raise KeyError(
                f"Padstack definition '{name}' not found in the builder. "
                "Use edb.configuration.create_config_builder() to auto-load from EDB."
            )
        pdefs = self._pedb.padstacks.definitions
        if name not in pdefs:
            raise KeyError(f"Padstack definition '{name}' not found in the EDB database.")
        pdef = pdefs[name]
        obj = self.add_definition(
            name=pdef.name,
            hole_plating_thickness=pdef.hole_plating_thickness,
            material=pdef.material,
            hole_range=pdef.hole_range,
            pad_parameters=pdef.get_pad_parameters(),
            hole_parameters=pdef.get_hole_parameters(),
            solder_ball_parameters=pdef.get_solder_parameters(),
        )
        return obj

    def get_instance(self, name: str) -> "CfgPadstackInstance":
        """Return a :class:`CfgPadstackInstance` for an existing padstack instance.

        If the instance has already been registered via :meth:`add_instance`
        the cached entry is returned, otherwise the instance is looked up in
        the live EDB session and a new entry is created from its current
        properties.

        Parameters
        ----------
        name : str
            Padstack instance AEDT name, e.g. ``"via_A1"``.

        Returns
        -------
        CfgPadstackInstance
            Instance builder pre-populated with current properties.

        Raises
        ------
        KeyError
            If no EDB session is attached or the instance does not exist.

        Examples
        --------
        cfg = edb.configuration.create_config_builder()
        via = cfg.padstacks.get_instance("via_A1")
        via.set_backdrill("L3", "0.25mm", drill_from_bottom=True)
        edb.configuration.run(cfg)
        """
        for inst in self.instances:
            if inst.name == name:
                return inst
        if self._pedb is None:
            raise KeyError(
                f"Padstack instance '{name}' not found in the builder. "
                "Use edb.configuration.create_config_builder() to auto-load from EDB."
            )
        by_name = self._pedb.padstacks.instances_by_name
        if name not in by_name:
            raise KeyError(f"Padstack instance '{name}' not found in the EDB layout.")
        p_inst = by_name[name]
        result = p_inst.position_and_rotation
        position = result[:2]
        rotation = result[-1]
        hole_override_enabled, hole_override_diameter = p_inst.get_hole_overrides()
        try:
            solderball_layer = p_inst.solderball_layer
        except Exception:
            solderball_layer = None
        obj = self.add_instance(
            name=p_inst.aedt_name,
            is_pin=p_inst.is_pin,
            definition=p_inst.padstack_definition,
            backdrill_parameters=p_inst.backdrill_parameters,
            position=[str(position[0]), str(position[1])],
            rotation=str(rotation),
            hole_override_enabled=hole_override_enabled,
            hole_override_diameter=str(hole_override_diameter),
            solder_ball_layer=solderball_layer,
            layer_range=[p_inst.start_layer, p_inst.stop_layer],
        )
        return obj

    @deprecated("add_padstack_definition is deprecated, use add_definition instead.")
    def add_padstack_definition(self, **kwargs):
        """Add a padstack definition from raw keyword arguments.

        .. deprecated::
            Use :meth:`add_definition` instead.

        Parameters
        ----------
        **kwargs
            Arguments forwarded to :meth:`add_definition`.

        Returns
        -------
        CfgPadstackDefinition
        """
        return self.add_definition(**kwargs)

    def add_definition(
        self,
        name: str,
        hole_plating_thickness=None,
        material=None,
        hole_range=None,
        hole_diameter=None,
        hole_shape="circle",
        hole_offset_x="0",
        hole_offset_y="0",
        pad_shape="circle",
        pad_diameter=None,
        pad_offset_x="0",
        pad_offset_y="0",
        pad_rotation="0",
        pad_x_size=None,
        pad_y_size=None,
        anti_pad_shape="circle",
        anti_pad_diameter=None,
        anti_pad_x_size=None,
        anti_pad_y_size=None,
        pad_layers=None,
        pad_parameters=None,
        hole_parameters=None,
        solder_ball_parameters=None,
    ):
        """Add a padstack definition with named parameters.

        Pad geometry can be specified either via the **convenience arguments**
        (which build the ``pad_parameters`` and ``hole_parameters`` dicts
        automatically) or by passing raw ``pad_parameters`` / ``hole_parameters``
        dicts directly for full control.

        Parameters
        ----------
        name : str
            Padstack definition name, e.g. ``"via_0.2"``.
        hole_plating_thickness : str or float, optional
            Plating thickness, e.g. ``"25um"``.
        material : str, optional
            Hole conductor material name, e.g. ``"copper"``.
        hole_range : str, optional
            Layer range the hole spans.  Accepted values:

            * ``"through"`` — hole goes fully through all layers.
            * ``"begin_on_upper_pad"`` — hole starts at the upper pad surface.
            * ``"end_on_lower_pad"`` — hole ends at the lower pad surface.
            * ``"upper_pad_to_lower_pad"`` *(default)* — upper pad to lower pad.
        hole_diameter : str or float, optional
            Drill hole diameter, e.g. ``"0.2mm"``.  Used together with
            *hole_shape* when *hole_parameters* is not given.
        hole_shape : str, optional
            Hole geometry type.  Default is ``"circle"``.
        hole_offset_x : str, optional
            Hole X offset.  Default is ``"0"``.
        hole_offset_y : str, optional
            Hole Y offset.  Default is ``"0"``.
        pad_shape : str, optional
            Regular-pad geometry type.  Accepted values:
            ``"circle"``, ``"square"``, ``"rectangle"``, ``"oval"``,
            ``"bullet"``, ``"round45"``, ``"round90"``, ``"square45"``,
            ``"square90"``.  Default is ``"circle"``.
        pad_diameter : str or float, optional
            Pad diameter (for ``"circle"`` shape), e.g. ``"0.5mm"``.
        pad_offset_x : str, optional
            Pad X offset.  Default is ``"0"``.
        pad_offset_y : str, optional
            Pad Y offset.  Default is ``"0"``.
        pad_rotation : str, optional
            Pad rotation angle.  Default is ``"0"``.
        pad_x_size : str or float, optional
            Pad X size for non-circular shapes (``"rectangle"``, ``"oval"``,
            ``"bullet"``), e.g. ``"0.5mm"``.
        pad_y_size : str or float, optional
            Pad Y size for non-circular shapes.
        anti_pad_shape : str, optional
            Anti-pad geometry type.  Default is ``"circle"``.
        anti_pad_diameter : str or float, optional
            Anti-pad diameter (for ``"circle"`` shape).
        anti_pad_x_size : str or float, optional
            Anti-pad X size for non-circular shapes.
        anti_pad_y_size : str or float, optional
            Anti-pad Y size for non-circular shapes.
        pad_layers : list of str, optional
            Layer names on which the pad geometry is applied.  When ``None``
            and a live EDB session is attached, all signal layers are used
            automatically.  Only used when *pad_parameters* is not given.
        pad_parameters : dict, optional
            Full raw pad-parameter dictionary.  Overrides all convenience pad
            arguments above.  Structure::

                {
                    "regular_pad": [
                        {
                            "layer_name": "1_Top",
                            "shape": "circle",
                            "diameter": "0.5mm",
                            "offset_x": "0",
                            "offset_y": "0",
                            "rotation": "0",
                        },
                        ...,
                    ],
                    "anti_pad": [...],
                    "thermal_pad": [...],
                    "hole": [...],
                }

        hole_parameters : dict, optional
            Full raw hole-parameter dictionary.  Overrides *hole_diameter* /
            *hole_shape* convenience args.  Structure::

                {"shape": "circle", "diameter": "0.2mm", "offset_x": "0", "offset_y": "0", "rotation": "0"}

        solder_ball_parameters : dict, optional
            Raw solder-ball parameter dictionary.

        Returns
        -------
        CfgPadstackDefinition
            The newly created definition object.

        Examples
        --------
        Simple circular via on all signal layers (requires live session):

        cfg.padstacks.add_definition(
            "via_0.2",
            material="copper",
            hole_plating_thickness="25um",
            hole_diameter="0.2mm",
            pad_diameter="0.5mm",
            anti_pad_diameter="0.8mm"
        )

        Blind via with explicit layers:

            cfg.padstacks.add_definition(
                "via_blind",
                hole_range="begin_on_upper_pad",
                hole_diameter="0.15mm",
                pad_diameter="0.35mm",
                anti_pad_diameter="0.6mm",
                pad_layers=["1_Top", "DE1"]
            )

        Raw dict form for full control:

            cfg.padstacks.add_definition(
                "via_custom",
                pad_parameters={
                    "regular_pad": [
                        {
                            "layer_name": "1_Top",
                            "shape": "rectangle",
                            "x_size": "0.5mm",
                            "y_size": "0.3mm",
                            "offset_x": "0",
                            "offset_y": "0",
                            "rotation": "0",
                        },
                    ],
                    "anti_pad": [
                        {
                            "layer_name": "1_Top",
                            "shape": "circle",
                            "diameter": "0.8mm",
                            "offset_x": "0",
                            "offset_y": "0",
                            "rotation": "0",
                        },
                    ],
                },
                hole_parameters={
                    "shape": "circle",
                    "diameter": "0.2mm",
                    "offset_x": "0",
                    "offset_y": "0",
                    "rotation": "0",
                }
            )
        """
        if hole_parameters is None and hole_diameter is not None:
            hole_parameters = {
                "shape": hole_shape,
                "diameter": str(hole_diameter),
                "offset_x": str(hole_offset_x),
                "offset_y": str(hole_offset_y),
                "rotation": "0",
            }

        if pad_parameters is None and (pad_diameter is not None or pad_x_size is not None):
            pad_parameters = self._build_pad_parameters(
                pad_layers=pad_layers,
                pad_shape=pad_shape,
                pad_diameter=pad_diameter,
                pad_x_size=pad_x_size,
                pad_y_size=pad_y_size,
                pad_offset_x=pad_offset_x,
                pad_offset_y=pad_offset_y,
                pad_rotation=pad_rotation,
                anti_pad_shape=anti_pad_shape,
                anti_pad_diameter=anti_pad_diameter,
                anti_pad_x_size=anti_pad_x_size,
                anti_pad_y_size=anti_pad_y_size,
            )

        kwargs = {
            "name": name,
            "hole_plating_thickness": hole_plating_thickness,
            "material": material,
            "hole_range": hole_range,
            "pad_parameters": pad_parameters,
            "hole_parameters": hole_parameters,
            "solder_ball_parameters": solder_ball_parameters,
        }
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        obj = CfgPadstackDefinition(**kwargs)
        self.definitions.append(obj)
        return obj

    def _build_pad_parameters(
        self,
        pad_layers,
        pad_shape,
        pad_diameter,
        pad_x_size,
        pad_y_size,
        pad_offset_x,
        pad_offset_y,
        pad_rotation,
        anti_pad_shape,
        anti_pad_diameter,
        anti_pad_x_size,
        anti_pad_y_size,
    ) -> dict:
        """Build a pad_parameters dict from convenience arguments."""
        layers = pad_layers
        if layers is None and self._cfg_stackup is not None:
            layers = [la.name for la in self._cfg_stackup.get_signal_layers()]
        if layers is None:
            layers = []

        regular_pads = [
            _make_pad_entry(
                layer=layer,
                shape=pad_shape,
                diameter=pad_diameter,
                x_size=pad_x_size,
                y_size=pad_y_size,
                offset_x=pad_offset_x,
                offset_y=pad_offset_y,
                rotation=pad_rotation,
            )
            for layer in layers
        ]
        anti_pads = []
        if anti_pad_diameter is not None or anti_pad_x_size is not None:
            anti_pads = [
                _make_pad_entry(
                    layer=layer,
                    shape=anti_pad_shape,
                    diameter=anti_pad_diameter,
                    x_size=anti_pad_x_size,
                    y_size=anti_pad_y_size,
                    offset_x="0",
                    offset_y="0",
                    rotation="0",
                )
                for layer in layers
            ]
        pad_parameters = {}
        if regular_pads:
            pad_parameters["regular_pad"] = regular_pads
        if anti_pads:
            pad_parameters["anti_pad"] = anti_pads
        return pad_parameters

    @deprecated("add_padstack_instance is deprecated, use add_instance instead.")
    def add_padstack_instance(self, **kwargs):
        """Add a padstack instance from raw keyword arguments.

        .. deprecated::
            Use :meth:`add_instance` instead.

        Parameters
        ----------
        **kwargs
            Arguments forwarded to :meth:`add_instance`.

        Returns
        -------
        CfgPadstackInstance
        """
        return self.add_instance(**kwargs)

    def add_instance(
        self,
        name: str = None,
        net_name: str = None,
        definition: str = None,
        layer_range: list = None,
        position: list = None,
        rotation: str | float = None,
        is_pin: bool = False,
        hole_override_enabled: bool = None,
        hole_override_diameter: str | float = None,
        solder_ball_layer: str = None,
        eid: int = None,
        backdrill_parameters: "CfgBackdrillParameters" = None,
    ) -> "CfgPadstackInstance":
        """Add a padstack instance.

        Parameters
        ----------
        name : str, optional
            AEDT name of the padstack instance, e.g. ``"via_A1"``.
        net_name : str, optional
            Net the instance belongs to, e.g. ``"GND"``.
        definition : str, optional
            Padstack definition name, e.g. ``"via_0.2"``.
        layer_range : list of str, optional
            ``[start_layer, stop_layer]``, e.g. ``["1_Top", "16_Bottom"]``.
        position : list, optional
            ``[x, y]`` position in metres or as unit strings.
        rotation : str or float, optional
            Rotation angle in degrees.
        is_pin : bool, optional
            Whether this instance is a component pin.  Default is ``False``.
        hole_override_enabled : bool, optional
            Enable hole-size override.
        hole_override_diameter : str or float, optional
            Override diameter value, e.g. ``"0.3mm"``.
        solder_ball_layer : str, optional
            Layer on which the solder ball is placed.
        eid : int, optional
            EDB element ID.
        backdrill_parameters : CfgBackdrillParameters, optional
            Pre-built backdrill descriptor.  Call
            :meth:`CfgPadstackInstance.set_backdrill` on the returned object
            to add backdrill geometry after creation.

        Returns
        -------
        CfgPadstackInstance
            The newly created instance object.

        Examples
        --------
        via = cfg.padstacks.add_instance(name="v1", net_name="GND", layer_range=["1_Top", "16_Bottom"])
        via.set_backdrill("L3", "0.25mm", drill_from_bottom=True)
        """
        obj = CfgPadstackInstance(
            name=name,
            net_name=net_name,
            definition=definition,
            layer_range=layer_range,
            position=position,
            rotation=rotation,
            is_pin=is_pin,
            hole_override_enabled=hole_override_enabled,
            hole_override_diameter=hole_override_diameter,
            solder_ball_layer=solder_ball_layer,
            eid=eid,
            backdrill_parameters=backdrill_parameters,
        )
        self.instances.append(obj)
        return obj

    def _to_dict(self) -> dict:
        """Internal serialization of configured padstack definitions and instances."""
        data = {}
        if self.definitions:
            data["definitions"] = [d.model_dump(exclude_none=True, by_alias=False) for d in self.definitions]
        if self.instances:
            data["instances"] = [i.model_dump(exclude_none=True, by_alias=False) for i in self.instances]
        return data
