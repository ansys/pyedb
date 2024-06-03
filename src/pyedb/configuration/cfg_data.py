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

from pyedb.configuration.cfg_boundaries import CfgBoundaries
from pyedb.configuration.cfg_general import CfgGeneral
from pyedb.configuration.cfg_nets import CfgNets
from pyedb.configuration.cfg_padstacks import CfgPadstacks
from pyedb.configuration.cfg_pin_groups import CfgPinGroup
from pyedb.configuration.cfg_ports_sources import CfgPort, CfgSources
from pyedb.configuration.cfg_s_parameter_models import CfgSParameterModel
from pyedb.configuration.cfg_setup import CfgSetup
from pyedb.configuration.cfg_spice_models import CfgSpiceModel
from pyedb.generic.general_methods import pyedb_function_handler
from pyedb.configuration.cfg_members import (CfgLayer, CfgMaterial, CfgComponent)


class CfgData(object):
    """Manages configure data."""

    def __init__(self, pedb, **kwargs):
        self._pedb = pedb
        self.edb_comps = self._pedb.components.components
        self.general = CfgGeneral(self, kwargs.get("general", None))

        self.boundaries = {}
        if kwargs.get("boundaries", None):
            self.boundaries = CfgBoundaries(self, kwargs.get("boundaries", None))

        self.nets = None
        if kwargs.get("nets"):
            self.nets = CfgNets(
                self, kwargs.get("nets", {}).get("signal_nets", []), kwargs.get("nets", {}).get("power_ground_nets", [])
            )

        #self.components = [CfgComponent(self, **component) for component in kwargs.get("components", [])]
        self.components = CfgComponents(self._pedb, data=kwargs.get("components", []))

        self.padstacks = CfgPadstacks(self, kwargs.get("padstacks", None))

        self.pin_groups = [CfgPinGroup(self, pin_group) for pin_group in kwargs.get("pin_groups", [])]

        self.ports = [CfgPort(self, **port) for port in kwargs.get("ports", [])]

        self.sources = [CfgSources(self, **source) for source in kwargs.get("sources", [])]

        self.setups = []
        if kwargs.get("setups", None):
            self.setups = [CfgSetup(self, setup) for setup in kwargs.get("setups", [])]

        self.stackup = CfgStackup(self._pedb, data=kwargs.get("stackup", {}))

        self.s_parameters = [
            CfgSParameterModel(self, self.general.s_parameter_library, sparam_model)
            for sparam_model in kwargs.get("s_parameters", [])
        ]

        self.spice_models = [
            CfgSpiceModel(self, self.general.spice_model_library, spice_model)
            for spice_model in kwargs.get("spice_models", [])
        ]

        self.package_definition = None
        self.operations = None

    @pyedb_function_handler
    def apply(self):
        """Apply configuration settings to the current design"""
        self.stackup.apply()


class CfgStackup:
    def __init__(self, pedb, data):
        self._pedb = pedb
        self.data = data

        self.materials = [CfgMaterial(**mat) for mat in data.get("materials", [])]
        self.layers = [CfgLayer(**lay) for lay in data.get("layers", [])]

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
                    i: j for i, j in l.__dict__.items() if i in l.attr_names
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
            attrs = {i: j for i, j in l.__dict__.items() if i in l.attr_names}
            prev_layer_clone = self._pedb.stackup.add_layer_top(**attrs)
        for idx, l in enumerate(layers):
            if l.type == "dielectric":
                attrs = {
                    i: j for i, j in l.__dict__.items() if i in l.attr_names
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
                if i in mat_in_cfg.attr_names
            }
            mat = self._pedb.materials.add_material(**attrs)


class CfgComponents:
    def __init__(self, pedb, data):
        self._pedb = pedb
        self.data = data
        self.components = [CfgComponent(**comp) for comp in data]
        self.layout_comp = None

