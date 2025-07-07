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
from pyedb.configuration.cfg_common import CfgBase
from pydantic import BaseModel, Field


class CfgMaterialPropertyThermalModifier(BaseModel):
    property_name: str
    basic_quadratic_c1: float = 0
    basic_quadratic_c2: float = 0
    basic_quadratic_temperature_reference: float = 22
    advanced_quadratic_lower_limit: float = -273.15
    advanced_quadratic_upper_limit: float = 1000
    advanced_quadratic_auto_calculate: bool = True
    advanced_quadratic_lower_constant: float = 1
    advanced_quadratic_upper_constant: float = 1


class CfgMaterial(BaseModel):
    name: str
    permittivity: Optional[float] = None
    conductivity: Optional[float] = None
    dielectric_loss_tangent: Optional[float] = None
    magnetic_loss_tangent: Optional[float] = None
    mass_density: Optional[float] = None
    permeability: Optional[float] = None
    poisson_ratio: Optional[float] = None
    specific_heat: Optional[float] = None
    thermal_conductivity: Optional[float] = None
    thermal_modifiers: Optional[List[CfgMaterialPropertyThermalModifier]] = None


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


class CfgStackup:

    def apply(self):
        """Apply configuration settings to the current design"""
        if len(self.materials):
            self.__apply_materials()

        input_signal_layers = [i for i in self.layers if i.type.lower() == "signal"]

        if len(self.layers):
            if len(self._pedb.stackup.signal_layers) == 0:
                self.__create_stackup()
            elif not len(input_signal_layers) == len(self._pedb.stackup.signal_layers):
                raise Exception(f"Input signal layer count do not match.")
            else:
                self.__apply_layers()

    def __create_stackup(self):
        layers = list()
        layers.extend(self.layers)
        for l_attrs in layers:
            attrs = l_attrs.model_dump(exclude_none=True)
            self._pedb.stackup.add_layer_bottom(**attrs)

    def __apply_materials(self):
        """Apply material settings to the current design"""
        materials_in_db = {i.lower(): i for i, _ in self._pedb.materials.materials.items()}
        for mat_in_cfg in self.materials:
            if mat_in_cfg.name.lower() in materials_in_db:
                self._pedb.materials.delete_material(materials_in_db[mat_in_cfg.name.lower()])

            attrs = mat_in_cfg.model_dump(exclude_none=True)
            mat = self._pedb.materials.add_material(**attrs)

            for i in attrs.get("thermal_modifiers", []):
                mat.set_thermal_modifier(**i.to_dict())

    def get_materials_from_db(self):
        materials = []
        for name, p in self._pedb.materials.materials.items():
            mat = {}
            for p_name in CfgMaterial.model_fields.keys():
                mat[p_name] = getattr(p, p_name, None)
            materials.append(mat)
        return materials

    def get_layers_from_db(self):
        layers = []
        for name, obj in self._pedb.stackup.all_layers.items():
            layers.append(obj.properties)
        return layers

    def get_data_from_db(self):
        """Get configuration data from layout.

        Returns
        -------
        dict
        """
        stackup = {}
        materials = self.get_materials_from_db()
        stackup["materials"] = materials
        layers = self.get_layers_from_db()
        stackup["layers"] = layers
        return stackup

    def __apply_layers(self):
        """Apply layer settings to the current design"""
        layers = list()
        layers.extend(self.layers)

        removal_list = []
        lc_signal_layers = []
        for name, obj in self._pedb.stackup.all_layers.items():
            if obj.type == "dielectric":
                removal_list.append(name)
            elif obj.type == "signal":
                lc_signal_layers.append(obj.id)
        for l in removal_list:
            self._pedb.stackup.remove_layer(l)

        # update all signal layers
        id_name = {i[0]: i[1] for i in self._pedb.stackup.layers_by_id}
        signal_idx = 0
        for l in layers:
            if l.type == "signal":
                layer_id = lc_signal_layers[signal_idx]
                layer_name = id_name[layer_id]
                attrs = l.model_dump(exclude_none=True)
                self._pedb.stackup.layers[layer_name].update(**attrs)
                signal_idx = signal_idx + 1

        # add all dielectric layers. Dielectric layers must be added last. Otherwise,
        # dielectric layer will occupy signal and document layer id.
        prev_layer_clone = None
        l = layers.pop(0)
        if l.type == "signal":
            prev_layer_clone = self._pedb.stackup.layers[l.name]
        else:
            attrs = l.model_dump(exclude_none=True)
            prev_layer_clone = self._pedb.stackup.add_layer_top(**attrs)
        for idx, l in enumerate(layers):
            if l.type == "dielectric":
                attrs = l.model_dump(exclude_none=True)
                prev_layer_clone = self._pedb.stackup.add_layer_below(
                    base_layer_name=prev_layer_clone.name, **attrs
                )
            elif l.type == "signal":
                prev_layer_clone = self._pedb.stackup.layers[l.name]

    def __init__(self, pedb: Edb, data):
        self._pedb = pedb
        self.materials = [CfgMaterial(**mat) for mat in data.get("materials", [])]
        self.layers = [CfgLayer(**lay) for lay in data.get("layers", [])]

        materials = [m.name for m in self.materials]
        for i in self.layers:
            if i.type == "signal":
                if i.material not in materials:
                    self.materials.append(
                        CfgMaterial(name=i.material, **self._pedb.materials.default_conductor_property_values)
                    )
                    materials.append(i.material)
                if i.fill_material not in materials:
                    self.materials.append(
                        CfgMaterial(name=i.fill_material, **self._pedb.materials.default_dielectric_property_values)
                    )
                    materials.append(i.fill_material)
            elif i.type == "dielectric":
                if i.material not in materials:
                    self.materials.append(
                        CfgMaterial(name=i.material, **self._pedb.materials.default_dielectric_property_values)
                    )
                    materials.append(i.material)
