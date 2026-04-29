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

from typing import Union

from pydantic import BaseModel, Field


class CfgBase(BaseModel):
    """Base Pydantic model for padstack-section payloads."""

    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
    }


class CfgBackdrillParameters(BaseModel):
    """Store optional backdrill definitions for a padstack instance."""

    class DrillParametersByLayer(CfgBase):
        drill_to_layer: str
        diameter: str

    class DrillParametersByLayerWithStub(DrillParametersByLayer):
        stub_length: Union[str, None]

    class DrillParameters(CfgBase):
        drill_depth: str
        diameter: str

    from_top: DrillParameters | DrillParametersByLayer | DrillParametersByLayerWithStub | None = None
    from_bottom: DrillParameters | DrillParametersByLayer | DrillParametersByLayerWithStub | None = None

    def add_backdrill_to_layer(self, drill_to_layer, diameter, stub_length=None, drill_from_bottom=True):
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

    backdrill_parameters: CfgBackdrillParameters | None = CfgBackdrillParameters()
    is_pin: bool = Field(default=False)

    net_name: str | None = None
    layer_range: list[str] | None = None
    definition: str | None = None
    position: list[str | float] | None = None
    rotation: str | None = None

    hole_override_enabled: bool | None = None
    hole_override_diameter: str | float | None = None
    solder_ball_layer: str | None = None

    def __init__(
        self,
        name: str = None,
        net_name: str | None = None,
        definition: str | None = None,
        layer_range: list[str] | None = None,
        position: list[str | float] | None = None,
        rotation: str | float | None = None,
        is_pin: bool = False,
        hole_override_enabled: bool | None = None,
        hole_override_diameter: str | float | None = None,
        solder_ball_layer: str | None = None,
        eid: int | None = None,
        backdrill_parameters: CfgBackdrillParameters | None = None,
        **kwargs,
    ):
        super().__init__(
            name=name,
            net_name=net_name,
            definition=definition,
            layer_range=layer_range,
            position=position,
            rotation=str(rotation) if rotation is not None else None,
            is_pin=is_pin,
            hole_override_enabled=hole_override_enabled,
            hole_override_diameter=hole_override_diameter,
            solder_ball_layer=solder_ball_layer,
            eid=eid,
            backdrill_parameters=backdrill_parameters or CfgBackdrillParameters(),
            **kwargs,
        )

    @property
    def _id(self):
        return self.eid

    @classmethod
    def create(cls, **kwargs):
        """Create a :class:`CfgPadstackInstance` with an empty backdrill object.

        Returns
        -------
        CfgPadstackInstance
        """
        obj = cls(**kwargs)
        obj.backdrill_parameters = CfgBackdrillParameters()
        return obj

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
        >>> via.set_backdrill("L3", "0.25mm", drill_from_bottom=True)
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

    def to_dict(self) -> dict:
        """Serialize the padstack instance."""
        return self.model_dump(exclude_none=True, by_alias=False)


class CfgPadstackDefinition(CfgBase):
    """Represent one padstack definition entry."""

    name: str

    hole_plating_thickness: str | float | None = None
    material: str | None = Field(None, alias="hole_material")
    hole_range: str | None = None

    pad_parameters: dict | None = None
    hole_parameters: dict | None = None
    solder_ball_parameters: dict | None = None

    def __init__(
        self,
        name: str,
        hole_plating_thickness: str | float | None = None,
        material: str | None = None,
        hole_range: str | None = None,
        pad_parameters: dict | None = None,
        hole_parameters: dict | None = None,
        solder_ball_parameters: dict | None = None,
        **kwargs,
    ):
        if material is not None and "hole_material" not in kwargs:
            kwargs["hole_material"] = material
        super().__init__(
            name=name,
            hole_plating_thickness=hole_plating_thickness,
            hole_range=hole_range,
            pad_parameters=pad_parameters,
            hole_parameters=hole_parameters,
            solder_ball_parameters=solder_ball_parameters,
            **kwargs,
        )

    @classmethod
    def create(cls, **kwargs) -> "CfgPadstackDefinition":
        """Create a :class:`CfgPadstackDefinition` from keyword arguments.

        Returns
        -------
        CfgPadstackDefinition
        """
        return cls(**kwargs)
        return self.model_dump(exclude_none=True)


class CfgPadstacks(CfgBase):
    """Collect padstack definitions and instances for serialization."""

    definitions: list[CfgPadstackDefinition] | None = []
    instances: list[CfgPadstackInstance] | None = []

    @classmethod
    def create(cls, **kwargs) -> "CfgPadstacks":
        """Create a :class:`CfgPadstacks` from keyword arguments.

        Returns
        -------
        CfgPadstacks
        """
        return cls(**kwargs)

    def clean(self):
        """Reset all padstack definitions and instances to empty lists."""
        self.definitions = []
        self.instances = []

    def add_padstack_definition(self, **kwargs):
        """Add a padstack definition from raw keyword arguments.

        Parameters
        ----------
        **kwargs
            Arguments forwarded to :class:`CfgPadstackDefinition`.

        Returns
        -------
        CfgPadstackDefinition
        """
        obj = CfgPadstackDefinition(**kwargs)
        self.definitions.append(obj)
        return obj

    def add_definition(
        self,
        name,
        hole_plating_thickness=None,
        material=None,
        hole_range=None,
        pad_parameters=None,
        hole_parameters=None,
        solder_ball_parameters=None,
    ):
        """Add a padstack definition with named parameters.

        Parameters
        ----------
        name : str
            Padstack definition name, e.g. ``"via_0.2"``.
        hole_plating_thickness : str or float, optional
            Plating thickness, e.g. ``"25um"``.
        material : str, optional
            Hole conductor material name.
        hole_range : str, optional
            Layer range the hole spans.
        pad_parameters : dict, optional
            Raw pad-parameter dictionary.
        hole_parameters : dict, optional
            Raw hole-parameter dictionary.
        solder_ball_parameters : dict, optional
            Raw solder-ball parameter dictionary.

        Returns
        -------
        CfgPadstackDefinition
            The newly created definition object.

        Examples
        --------
        >>> cfg.padstacks.add_definition("via_0.2", material="copper", hole_plating_thickness="25um")
        """
        kwargs = {
            "name": name,
            "hole_plating_thickness": hole_plating_thickness,
            "hole_material": material,
            "hole_range": hole_range,
            "pad_parameters": pad_parameters,
            "hole_parameters": hole_parameters,
            "solder_ball_parameters": solder_ball_parameters,
        }
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        return self.add_padstack_definition(**kwargs)

    def add_padstack_instance(self, **kwargs):
        """Add a padstack instance from raw keyword arguments.

        Parameters
        ----------
        **kwargs
            Arguments forwarded to :class:`CfgPadstackInstance`.

        Returns
        -------
        CfgPadstackInstance
        """
        obj = CfgPadstackInstance(**kwargs)
        self.instances.append(obj)
        return obj

    def add_instance(self, **kwargs):
        """Add a padstack instance with named parameters.

        Parameters
        ----------
        **kwargs
            Arguments forwarded to :class:`CfgPadstackInstance`.
            Common keys: ``name``, ``net_name``, ``definition``,
            ``layer_range``, ``position``, ``rotation``.

        Returns
        -------
        CfgPadstackInstance
            The newly created instance object (call
            :meth:`CfgPadstackInstance.set_backdrill` on it to add
            backdrill geometry).

        Examples
        --------
        >>> via = cfg.padstacks.add_instance(name="v1", net_name="GND", layer_range=["top", "bot"])
        >>> via.set_backdrill("L3", "0.25mm", drill_from_bottom=True)
        """
        if kwargs.get("rotation") is not None:
            return self.add_padstack_instance(**kwargs)

    def to_dict(self) -> dict:
        """Serialize all configured padstack definitions and instances."""
        data = {}
        if self.definitions:
            data["definitions"] = [d.to_dict() for d in self.definitions]
        if self.instances:
            data["instances"] = [i.to_dict() for i in self.instances]
        return data

