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

"""Build the ``operations`` configuration section, including cutouts."""

from typing import Any, ClassVar, List, Optional, Union

from pydantic import BaseModel, Field, field_validator


class CfgAutoIdentifyNets(BaseModel):
    """Store threshold settings for automatic cutout net discovery."""

    enabled: bool = False
    resistor_below: float | str | int | None = Field(100)
    inductor_below: float | str | int | None = Field(1)
    capacitor_above: float | str | int | None = Field("10nF")


class CfgCutout(BaseModel):
    """Represent one cutout operation configuration payload."""

    auto_identify_nets: CfgAutoIdentifyNets | None = Field(default_factory=CfgAutoIdentifyNets)
    signal_nets: Optional[List[str]] = Field(
        default=None,
        alias="signal_list",
    )
    reference_nets: Optional[List[str]] = Field(
        default=None,
        alias="reference_list",
    )
    extent_type: Optional[str] = "ConvexHull"
    expansion_size: Optional[Union[float, str]] = 0.002
    number_of_threads: Optional[int] = 1
    custom_extent: Optional[Any] = None
    custom_extent_units: str = Field(default="meter")
    expansion_factor: Optional[float] = 0

    model_config = dict(populate_by_name=True)

    # Accepted extent_type values and their canonical form
    _EXTENT_TYPE_MAP: ClassVar[dict[str, str]] = {
        "convexhull": "ConvexHull",
        "convex_hull": "ConvexHull",
        "conforming": "Conformal",
        "conformal": "Conformal",
        "bounding": "BoundingBox",
        "boundingbox": "BoundingBox",
        "bounding_box": "BoundingBox",
    }

    @field_validator("extent_type", mode="before")
    @classmethod
    def _normalise_extent_type(cls, v):
        if v is None:
            return v
        key = str(v).lower().replace(" ", "")
        normalised = cls._EXTENT_TYPE_MAP.get(key)
        if normalised is None:
            # fall back to the original value unchanged so unknown values
            # surface as a runtime error from the underlying cutout method
            return v
        return normalised

    def __init__(
        self,
        signal_nets=None,
        reference_nets=None,
        auto_identify_nets_enabled: bool = False,
        resistor_below: float = 100,
        inductor_below: float = 1,
        capacitor_above: float | str = "10nF",
        **kwargs,
    ):
        if signal_nets is not None and "signal_list" not in kwargs and "signal_nets" not in kwargs:
            kwargs["signal_list"] = signal_nets
        if reference_nets is not None and "reference_list" not in kwargs and "reference_nets" not in kwargs:
            kwargs["reference_list"] = reference_nets
        if "auto_identify_nets" not in kwargs:
            kwargs["auto_identify_nets"] = CfgAutoIdentifyNets(
                enabled=auto_identify_nets_enabled,
                resistor_below=resistor_below,
                inductor_below=inductor_below,
                capacitor_above=capacitor_above,
            )
        super().__init__(**kwargs)

    def to_dict(self) -> dict:
        """Serialize the cutout operation."""
        return self.model_dump(exclude_none=True, by_alias=True)


class CfgOperations(BaseModel):
    """Collect operations to apply after the core design sections."""

    cutout: Optional[CfgCutout] = None
    generate_auto_hfss_regions: bool = False

    def add_cutout(
        self,
        signal_nets=None,
        reference_nets=None,
        extent_type: str = "ConvexHull",
        expansion_size: float | str = 0.002,
        expansion_factor: float = 0,
        auto_identify_nets_enabled: bool = False,
        resistor_below: float = 100,
        inductor_below: float = 1,
        capacitor_above: float | str = "10nF",
        **kwargs,
    ):
        """Create and store a cutout operation."""
        self.cutout = CfgCutout(
            signal_nets=signal_nets,
            reference_nets=reference_nets,
            extent_type=extent_type,
            expansion_size=expansion_size,
            expansion_factor=expansion_factor,
            auto_identify_nets_enabled=auto_identify_nets_enabled,
            resistor_below=resistor_below,
            inductor_below=inductor_below,
            capacitor_above=capacitor_above,
            **kwargs,
        )
        return self.cutout

    def to_dict(self) -> dict:
        """Serialize the configured operations."""
        data: dict = {}
        if self.cutout is not None:
            data["cutout"] = self.cutout.to_dict()
        if self.generate_auto_hfss_regions:
            data["generate_auto_hfss_regions"] = self.generate_auto_hfss_regions
        return data
