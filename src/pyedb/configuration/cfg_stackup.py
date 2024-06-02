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


from pyedb.generic.general_methods import pyedb_function_handler


class CfgStackup:
    def __init__(self, pedb, data):
        self._pedb = pedb

        self.materials = [CfgMaterial(self._pedb, **mat) for mat in data.get("materials", [])]
        self.layers = [CfgLayer(self._pedb, **lay) for lay in data.get("layers", [])]

    @pyedb_function_handler
    def apply(self):
        """Apply configuration settings to the current design"""
        if len(self.materials):
            self.__apply_materials()
        if len(self.layers):
            self.__apply_layers()

    @pyedb_function_handler
    def __apply_layers(self):
        """Apply layer settings to the current design"""
        layers = list()
        layers.extend(self.layers)
        input_signal_layers = [i for i in layers if i.type.lower() == "signal"]
        if not len(input_signal_layers) == len(self._pedb.stackup.signal_layers):
            self._pedb.logger.error("Input signal layer count do not match.")
            return False

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
                attrs = {
                    i: j for i, j in l.__dict__.items() if not i.startswith("_") and isinstance(j, (int, float, str))
                }
                self._pedb.stackup.layers[layer_name].update(**attrs)
                signal_idx = signal_idx + 1

        # add all dielectric layers. Dielectric layers must be added last. Otherwise,
        # dielectric layer will occupy signal and document layer id.
        prev_layer_clone = None
        l = layers.pop(0)
        if l.type == "signal":
            prev_layer_clone = self._pedb.stackup.layers[l.name]
        else:
            attrs = {i: j for i, j in l.__dict__.items() if not i.startswith("_") and isinstance(j, (int, float, str))}
            prev_layer_clone = self._pedb.stackup.add_layer_top(**attrs)
        for idx, l in enumerate(layers):
            if l.type == "dielectric":
                attrs = {
                    i: j for i, j in l.__dict__.items() if not i.startswith("_") and isinstance(j, (int, float, str))
                }
                prev_layer_clone = self._pedb.stackup.add_layer_below(base_layer_name=prev_layer_clone.name, **attrs)
            elif l.type == "signal":
                prev_layer_clone = self._pedb.stackup.layers[l.name]

    @pyedb_function_handler
    def __apply_materials(self):
        """Apply material settings to the current design"""
        materials_in_db = {i.lower(): i for i, _ in self._pedb.materials.materials.items()}
        for mat_in_cfg in self.materials:
            if mat_in_cfg.name.lower() in materials_in_db:
                self._pedb.materials.delete_material(materials_in_db[mat_in_cfg.name.lower()])

            attrs = {
                i: j
                for i, j in mat_in_cfg.__dict__.items()
                if not i.startswith("_") and isinstance(j, (int, float, str))
            }
            mat = self._pedb.materials.add_material(**attrs)


class CfgMaterial:
    def __init__(self, pedb, **kwargs):
        self._pedb = pedb
        self.name = kwargs.get("name")
        self.permittivity = kwargs.get("permittivity", None)
        self.conductivity = kwargs.get("conductivity", None)
        self.dielectric_loss_tangent = kwargs.get("dielectric_loss_tangent", None)
        self.magnetic_loss_tangent = kwargs.get("magnetic_loss_tangent", None)
        self.mass_density = kwargs.get("mass_density", None)
        self.permeability = kwargs.get("permeability", None)
        self.poisson_ratio = kwargs.get("poisson_ratio", None)
        self.specific_heat = kwargs.get("specific_heat", None)
        self.thermal_conductivity = kwargs.get("thermal_conductivity", None)
        self.youngs_modulus = kwargs.get("youngs_modulus", None)
        self.thermal_expansion_coefficient = kwargs.get("thermal_expansion_coefficient", None)


class CfgLayer:
    def __init__(self, pedb, **kwargs):
        self._pedb = pedb
        self.name = kwargs.get("name", None)
        self.type = kwargs.get("type", None)
        self.material = kwargs.get("material", None)
        self.fill_material = kwargs.get("fill_material", None)
        self.thickness = kwargs.get("thickness", None)
        self.etch_factor = kwargs.get("etch_factor", None)
        self.lower_elevation = kwargs.get("lower_elevation", None)
