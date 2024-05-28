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


class LayerType(Enum):
    SIGNAL = 0
    DIELECTRIC = 1


class CfgLayerStackup:
    def __init__(self, pdata, materials=None, layers=None):
        self._pedb = pdata.pedb
        self.materials = []
        self.layers = []


class Material:
    def __init__(self, pedb):
        self._pedb = pedb
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

    def apply(self):
        edb_materials = {i.lower(): i for i, _ in self._pedb.materials.materials.items()}
        if self.name.lower() in edb_materials:
            self._pedb.materials.delete_material(edb_materials[self.name])
        self._pedb.materials.add_material(**mat)


class Layer:
    def __init__(self):
        self.name = ""
        self.color = [random.randint(1, 255), random.randint(1, 255), random.randint(1, 255)]
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

    data = self.data["stackup"]
    materials = data.get("materials")

    if layers:
        lc = self._pedb.stackup
        input_signal_layers = [i for i in layers if i["type"].lower() == "signal"]
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
        for l in layers:
            if l["type"] == "signal":
                clone = layer_clones.pop(0)
                clone.update(**l)
                lc_new.add_layer_bottom(name=clone.name, layer_clone=clone)
                signal_layer_ids[clone.name] = clone.id

        # add all document layers at bottom
        for l in doc_layer_clones:
            doc_layer = lc_new.add_document_layer(name=l.name, layer_clone=l)
            first_doc_layer_name = doc_layer.name

        # add all dielectric layers. Dielectric layers must be added last. Otherwise,
        # dielectric layer will occupy signal and document layer id.
        prev_layer_clone = None
        l = layers.pop(0)
        if l["type"] == "signal":
            prev_layer_clone = lc_new.layers[l["name"]]
        else:
            prev_layer_clone = lc_new.add_layer_top(**l)
        for idx, l in enumerate(layers):
            if l["type"] == "dielectric":
                prev_layer_clone = lc_new.add_layer_below(base_layer_name=prev_layer_clone.name, **l)
            else:
                prev_layer_clone = lc_new.layers[l["name"]]

        lc._edb_object = lc_new._edb_object
        lc_new.auto_refresh = True
        lc.update_layout()
