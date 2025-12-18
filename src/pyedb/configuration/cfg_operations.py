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

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

# from pyedb.configuration.cfg_common import CfgBase


class CfgAutoIdentifyNets(BaseModel):
    enabled: bool = False
    resistor_below: float | str | None = 100
    inductor_below: float | str | None = 1
    capacitor_above: float | str | None = "10nF"


class CfgCutout(BaseModel):
    auto_identify_nets: CfgAutoIdentifyNets | None = CfgAutoIdentifyNets()
    signal_list: Optional[List[str]] = None
    reference_list: Optional[List[str]] = None
    extent_type: Optional[str] = "ConvexHull"
    expansion_size: Optional[Union[float, str]] = 0.002
    number_of_threads: Optional[int] = 1
    custom_extent: Optional[Any] = None
    custom_extent_units: str = Field(default="meter")
    expansion_factor: Optional[float] = 0


class CfgOperations(BaseModel):
    cutout: Optional[CfgCutout] = None

    def add_cutout(self, **kwargs):
        self.cutout = CfgCutout(**kwargs)
