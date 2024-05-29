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

from enum import Enum
import random

from pyedb.dotnet.edb_core.stackup import LayerCollection


class LayerType(Enum):
    SIGNAL = 0
    DIELECTRIC = 1


class CfgLayerStackup:
    def __init__(self, pdata, materials=None, layers=None):
        self._pedb = pdata.pedb
        self._materials_dict = materials
        self._layers_dict = layers
        self.materials = []
        self.layers = []
        if self._materials_dict:
            self.materials = [Material(self._pedb, material_dict) for material_dict in self._materials_dict]
        if self._layers_dict:
            self.layers = [Layer(self._pedb, layer_dict) for layer_dict in self._layers_dict]

    def apply(self):
        for material in self.materials:
            material.apply()
        self.__apply_layers()

    def __apply_layers(self):
        lc = self._pedb.stackup
        input_signal_layers = [layer for layer in self.layers if layer.type == LayerType.SIGNAL]
        if not len(input_signal_layers) == len(lc.signal_layers):
            self._pedb.logger.error("Input signal layer count do not match.")
            return False

        layer_clones = []
        doc_layer_clones = []
        for name, obj in lc.layers.items():
            if obj.is_stackup_layer:
                if obj.type == "signal":  # keep signal layers
                    layer_clones.append(obj)
            else:
                doc_layer_clones.append(obj)

        lc_new = LayerCollection(self._pedb)
        lc_new.auto_refresh = False
        signal_layer_ids = {}
        top_layer_clone = None

        # add all signal layers
        for layer in self.layers:
            if layer.type == LayerType.SIGNAL:
                clone = layer_clones.pop(0)
                clone.update(layer.__dict__())
                lc_new.add_layer_bottom(name=clone.name, layer_clone=clone)
                signal_layer_ids[clone.name] = clone.id

        # add all document layers at bottom
        for layer in doc_layer_clones:
            doc_layer = lc_new.add_document_layer(name=layer.name, layer_clone=layer)
            first_doc_layer_name = doc_layer.name

        # add all dielectric layers. Dielectric layers must be added last. Otherwise,
        # dielectric layer will occupy signal and document layer id.
        prev_layer_clone = None
        layer = self.layers.pop(0)
        if layer.type == LayerType.SIGNAL:
            prev_layer_clone = lc_new.layers[layer.name]
        else:
            prev_layer_clone = lc_new.add_layer_top(layer.__dict__())
        for idx, layer in enumerate(self.layers):
            if layer.type == LayerType.DIELECTRIC:
                prev_layer_clone = lc_new.add_layer_below(base_layer_name=prev_layer_clone.name, **layer.__dict__())
            else:
                prev_layer_clone = lc_new.layers[layer.name]

        lc._edb_object = lc_new._edb_object
        lc_new.auto_refresh = True
        lc.update_layout()


class Material:
    def __init__(self, pedb, material_dict=None):
        self._pedb = pedb
        self._material_dict = material_dict
        self.name = ""
        self.conductivity = 0.0
        self.loss_tangent = 0.0
        self.magnetic_loss_tangent = 0.0
        self.mass_density = 0.0
        self.permittivity = 1.0
        self.permeability = 1.0
        self.poisson_ratio = 0.0
        self.specific_heat = 0.0
        self.thermal_conductivity = 0.0
        self.youngs_modulus = 0.0
        self.thermal_expansion_coefficient = 0.0
        self.dc_conductivity = None
        self.dc_permittivity = None
        self.dielectric_model_frequency = None
        self.loss_tangent_at_frequency = None
        self.permittivity_at_frequency = None
        self.__update()

    def __update(self):
        if self._material_dict:
            self.name = self._material_dict.get("name", "")
            self.conductivity = self._material_dict.get("conductivity", 0.0)
            self.loss_tangent = self._material_dict.get("loss_tangent", 0.0)
            self.magnetic_loss_tangent = self._material_dict.get("magnetic_loss_tangent", 0.0)
            self.mass_density = self._material_dict.get("mass_density", 0.0)
            self.permittivity = self._material_dict.get("permittivity", 1.0)
            self.permeability = self._material_dict.get("permeability", 1.0)
            self.poisson_ratio = self._material_dict.get("poisson_ratio", 0.0)
            self.specific_heat = self._material_dict.get("specific_heat", 0.0)
            self.thermal_conductivity = self._material_dict.get("thermal_conductivity", 0.0)
            self.youngs_modulus = self._material_dict.get("youngs_modulus", 0.0)
            self.thermal_expansion_coefficient = self._material_dict.get("thermal_expansion_coefficient", 0.0)
            self.dc_conductivity = self._material_dict.get("dc_conductivity", None)
            self.dc_permittivity = self._material_dict.get("dc_permittivity", None)
            self.dielectric_model_frequency = self._material_dict.get("dc_permittivity", None)
            self.loss_tangent_at_frequency = self._material_dict.get("loss_tangent_at_frequency", None)
            self.permittivity_at_frequency = self._material_dict.get("permittivity_at_frequency", None)

    def apply(self):
        edb_materials = {i.lower(): i for i, _ in self._pedb.materials.materials.items()}
        if self.name.lower() in edb_materials:
            self._pedb.materials.delete_material(edb_materials[self.name])
        self._pedb.materials.add_material(self.__dict__)


class Layer:
    def __init__(self, pedb, layer_dict=None):
        self._pedb = pedb
        self._layer_dict = layer_dict
        self.name = ""
        self.color = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
        self.type = LayerType.SIGNAL
        self.material = "copper"
        self.dielectric_fill = "fr4"
        self.thickness = 35e-6
        self.etch_factor = 0.0
        self.roughness_enabled = False
        self.top_hallhuray_nodule_radius = 0.0
        self.top_hallhuray_surface_ratio = 0.0
        self.bottom_hallhuray_nodule_radius = 0.0
        self.bottom_hallhuray_surface_ratio = 0.0
        self.side_hallhuray_nodule_radius = 0.0
        self.side_hallhuray_surface_ratio = 0.0
        self.upper_elevation = 0.0
        self.lower_elevation = 0.0
        self.__update()

    def __update(self):
        if self._layer_dict:
            self.name = self._layer_dict.get("name", self.name)
            self.color = self._layer_dict.get("color", self.color)
            self.__map_layer_type()
            self.material = self._layer_dict.get("material", self.material)
            self.dielectric_fill = self._layer_dict.get("dielectric_fill", self.dielectric_fill)
            self.thickness = self._layer_dict.get("thickness", self.thickness)
            self.etch_factor = self._layer_dict.get("etch_factor", self.etch_factor)
            self.roughness_enabled = self._layer_dict.get("roughness_enabled", self.roughness_enabled)
            self.top_hallhuray_nodule_radius = self._layer_dict.get(
                "top_hallhuray_nodule_radius", self.top_hallhuray_nodule_radius
            )
            self.top_hallhuray_surface_ratio = self._layer_dict.get(
                "top_hallhuray_surface_ratio", self.top_hallhuray_surface_ratio
            )
            self.bottom_hallhuray_nodule_radius = self._layer_dict.get(
                "bottom_hallhuray_nodule_radius", self.bottom_hallhuray_nodule_radius
            )
            self.bottom_hallhuray_surface_ratio = self._layer_dict.get(
                "bottom_hallhuray_surface_ratio", self.bottom_hallhuray_surface_ratio
            )
            self.side_hallhuray_nodule_radius = self._layer_dict.get(
                "side_hallhuray_nodule_radius", self.side_hallhuray_nodule_radius
            )
            self.side_hallhuray_surface_ratio = self._layer_dict.get(
                "side_hallhuray_surface_ratio", self.side_hallhuray_surface_ratio
            )
            self.upper_elevation = self._layer_dict.get("upper_elevation", self.upper_elevation)
            self.lower_elevation = self._layer_dict.get("lower_elevation", self.lower_elevation)

    def __map_layer_type(self):
        if self._layer_dict.get("type") == "signal":
            self.type = LayerType.SIGNAL
        elif self._layer_dict.get("type") == "dielectric":
            self.type = LayerType.DIELECTRIC
