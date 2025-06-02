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

from pyedb.configuration.cfg_common import CfgBase


class CfgCutout(CfgBase):
    class Grpc:
        def __init__(self, parent):
            self.parent = parent
            self._pedb = parent._pedb

        def get_parameters_from_edb(self):
            if "pyedb_cutout" in self._pedb.stackup.all_layers:
                polygons = self._pedb.layout.find_primitive(layer_name="pyedb_cutout")
                if polygons:
                    poly = polygons[0]
                    self.parent.custom_extent = poly.polygon_data.points
                    net_names = []
                    for name, obj in self._pedb.nets.nets.items():
                        if obj.primitives:
                            if obj.primitives[0].layer.name == "pyedb_cutout":
                                continue
                            else:
                                net_names.append(name)
                    self.parent.reference_list = []
                    self.parent.signal_list = net_names
                return self.parent.export_properties()

    class DotNet(Grpc):
        def __init__(self, parent):
            super().__init__(parent)

    def __init__(self, pedb, **kwargs):
        self._pedb = pedb
        if self._pedb.grpc:
            self.api = self.Grpc(self)
        else:
            self.api = self.DotNet(self)
        self.auto_identify_nets = kwargs.get("auto_identify_nets")
        self.signal_list = kwargs.get("signal_list")
        self.reference_list = kwargs.get("reference_list")
        self.extent_type = kwargs.get("extent_type")
        self.expansion_size = kwargs.get("expansion_size")
        self.use_round_corner = kwargs.get("use_round_corner")
        self.output_aedb_path = kwargs.get("output_aedb_path")
        self.open_cutout_at_end = kwargs.get("open_cutout_at_end")
        self.use_pyaedt_cutout = kwargs.get("use_pyaedt_cutout")
        self.number_of_threads = kwargs.get("number_of_threads")
        self.use_pyaedt_extent_computing = kwargs.get("use_pyaedt_extent_computing")
        self.extent_defeature = kwargs.get("extent_defeature")
        self.remove_single_pin_components = kwargs.get("remove_single_pin_components")
        self.custom_extent = kwargs.get("custom_extent")
        self.custom_extent_units = kwargs.get("custom_extent_units", "meter")
        self.include_partial_instances = kwargs.get("include_partial_instances")
        self.keep_voids = kwargs.get("keep_voids")
        self.check_terminals = kwargs.get("check_terminals")
        self.include_pingroups = kwargs.get("include_pingroups")
        self.expansion_factor = kwargs.get("expansion_factor")
        self.maximum_iterations = kwargs.get("maximum_iterations")
        self.preserve_components_with_model = kwargs.get("preserve_components_with_model")
        self.simple_pad_check = kwargs.get("simple_pad_check")
        self.keep_lines_as_path = kwargs.get("keep_lines_as_path")

    def get_data_from_db(self):
        return self.api.get_parameters_from_edb()

    def export_properties(self):
        return {
            "signal_list": self.signal_list,
            "reference_list": self.reference_list,
            "custom_extent": self.custom_extent,
        }


class CfgOperations(CfgBase):
    class Grpc:
        def __init__(self, parent):
            self.parent = parent
            self._pedb = parent._pedb

        def apply_on_edb(self):
            if self.parent.op_cutout:
                cutout_params = self.parent.op_cutout.get_attributes()
                auto_identify_nets = cutout_params.pop("auto_identify_nets")
                if auto_identify_nets["enabled"]:
                    reference_list = cutout_params.get("reference_list", [])
                    if auto_identify_nets:
                        self._pedb.nets.generate_extended_nets(
                            auto_identify_nets["resistor_below"],
                            auto_identify_nets["inductor_below"],
                            auto_identify_nets["capacitor_above"],
                            auto_identify_nets.get("exception_list", []),
                        )
                        signal_nets = []
                        for i in self._pedb.ports.values():
                            # Positive terminal
                            extended_net = i.net.extended_net
                            if extended_net:
                                temp = [i2 for i2 in extended_net.nets.keys() if i2 not in reference_list]
                                temp = [i2 for i2 in temp if i2 not in signal_nets]
                                signal_nets.extend(temp)
                            else:
                                signal_nets.append(i.net.name)

                            # Negative terminal
                            ref_net = i.ref_terminal.net if i.ref_terminal else None
                            if ref_net is None:
                                continue
                            elif ref_net.name not in reference_list:
                                extended_net = ref_net.extended_net
                                if extended_net:
                                    temp = [i2 for i2 in extended_net.nets.keys() if i2 not in reference_list]
                                    temp = [i2 for i2 in temp if i2 not in signal_nets]
                                    signal_nets.extend(temp)
                                else:
                                    signal_nets.append(ref_net.name)

                        cutout_params["signal_list"] = signal_nets
                polygon_points = self._pedb.cutout(**cutout_params)
                if "pyedb_cutout" not in self._pedb.stackup.all_layers:
                    self._pedb.stackup.add_document_layer(name="pyedb_cutout")
                    self._pedb.modeler.create_polygon(
                        polygon_points, layer_name="pyedb_cutout", net_name="pyedb_cutout"
                    )

        def get_parameter_from_edb(self):
            self.parent.op_cutout = CfgCutout(self._pedb)
            data_from_db = self.parent.op_cutout.get_data_from_db()
            if data_from_db:
                return {"cutout": data_from_db}
            else:
                return {}

    class DotNet(Grpc):
        def __init__(self, parent):
            super().__init__(parent)

    def __init__(self, pedb, data):
        self._pedb = pedb
        if self._pedb.grpc:
            self.api = self.Grpc(self)
        else:
            self.api = self.DotNet(self)
        cutout = data.get("cutout", None)
        if cutout:
            auto_identify_nets = (
                cutout.pop("auto_identify_nets")
                if cutout.get("auto_identify_nets")
                else {"enabled": False, "resistor_below": 100, "inductor_below": 1, "capacitor_above": 1}
            )
            self.op_cutout = CfgCutout(pedb, auto_identify_nets=auto_identify_nets, **cutout)
        else:
            self.op_cutout = None

    def apply(self):
        """Imports operation information from JSON."""
        self.api.apply_on_edb()

    def get_data_from_db(self):
        return self.api.get_parameter_from_edb()
