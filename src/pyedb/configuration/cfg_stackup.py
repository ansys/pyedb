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
from typing import Optional, List, Union

from pyedb import Edb
from pyedb.dotnet.database.materials import MaterialProperties
from pydantic import BaseModel, Field


class CfgMaterial(MaterialProperties):
    name: str


class RoughnessSideModel(BaseModel):
    model: str
    nodule_radius: Optional[str] = None  # e.g., '0.1um'
    surface_ratio: Optional[str] = None  # e.g., '1'
    roughness: Optional[str] = None      # e.g., '2um' for non-huray


class RoughnessModel(BaseModel):
    enabled: Optional[bool] = False
    top: Optional[RoughnessSideModel] = None
    bottom: Optional[RoughnessSideModel] = None
    side: Optional[RoughnessSideModel] = None


class EtchingModel(BaseModel):
    factor: Optional[Union[float, str]] = 0.5
    etch_power_ground_nets: Optional[bool] = False
    enabled: Optional[bool] = False


class CfgLayer(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    material: Optional[str] = None
    fill_material: Optional[str] = None
    thickness: Optional[Union[float, str]] = None
    roughness: Optional[RoughnessModel] = None
    etching: Optional[EtchingModel] = None


class CfgStackup(BaseModel):
    materials: List[CfgMaterial] = Field(default_factory=list)
    layers: List[CfgLayer] = Field(default_factory=list)

    def add_material(self, name, **kwargs):
        self.materials.append(CfgMaterial(name=name, **kwargs))

    def add_layer_at_bottom(self, name, **kwargs):
        self.layers.append(CfgLayer(name=name, **kwargs))
