# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Operations builder API."""

from __future__ import annotations

from typing import Any, List, Optional, Union


class CutoutConfig:
    """Builder for a cutout operation."""

    def __init__(
        self,
        signal_nets: Optional[List[str]] = None,
        reference_nets: Optional[List[str]] = None,
        extent_type: str = "ConvexHull",
        expansion_size: Union[float, str] = 0.002,
        number_of_threads: int = 1,
        auto_identify_nets_enabled: bool = False,
        resistor_below: Union[float, str, int] = 100,
        inductor_below: Union[float, str, int] = 1,
        capacitor_above: Union[float, str, int] = "10nF",
        custom_extent=None,
        custom_extent_units: str = "meter",
        expansion_factor: float = 0,
    ):
        self.signal_list = signal_nets
        self.reference_list = reference_nets
        self.extent_type = extent_type
        self.expansion_size = expansion_size
        self.number_of_threads = number_of_threads
        self.auto_identify_nets = {
            "enabled": auto_identify_nets_enabled,
            "resistor_below": resistor_below,
            "inductor_below": inductor_below,
            "capacitor_above": capacitor_above,
        }
        self.custom_extent = custom_extent
        self.custom_extent_units = custom_extent_units
        self.expansion_factor = expansion_factor

    def to_dict(self) -> dict:
        data: dict = {
            "extent_type": self.extent_type,
            "expansion_size": self.expansion_size,
            "number_of_threads": self.number_of_threads,
            "auto_identify_nets": self.auto_identify_nets,
        }
        if self.signal_list is not None:
            data["signal_list"] = self.signal_list
        if self.reference_list is not None:
            data["reference_list"] = self.reference_list
        if self.custom_extent is not None:
            data["custom_extent"] = self.custom_extent
        if self.custom_extent_units != "meter":
            data["custom_extent_units"] = self.custom_extent_units
        if self.expansion_factor:
            data["expansion_factor"] = self.expansion_factor
        return data


class OperationsConfig:
    """Fluent builder for the ``operations`` configuration section."""

    def __init__(self):
        self._cutout: Optional[CutoutConfig] = None
        self.generate_auto_hfss_regions: bool = False

    def add_cutout(
        self,
        signal_nets: Optional[List[str]] = None,
        reference_nets: Optional[List[str]] = None,
        **kwargs,
    ) -> CutoutConfig:
        """Add a cutout operation. Returns the CutoutConfig."""
        self._cutout = CutoutConfig(signal_nets=signal_nets, reference_nets=reference_nets, **kwargs)
        return self._cutout

    def to_dict(self) -> dict:
        data: dict = {}
        if self._cutout is not None:
            data["cutout"] = self._cutout.to_dict()
        if self.generate_auto_hfss_regions:
            data["generate_auto_hfss_regions"] = self.generate_auto_hfss_regions
        return data
