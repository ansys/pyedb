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

from pathlib import Path


class CfgSParameterModel:
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", "")
        self.component_definition = kwargs.get("component_definition", "")
        self.file_path = kwargs.get("file_path", "")
        self.apply_to_all = kwargs.get("apply_to_all", False)
        self.components = kwargs.get("components", [])
        self.reference_net = kwargs.get("reference_net", "")
        self.reference_net_per_component = kwargs.get("reference_net_per_component", {})
        self.pin_order = kwargs.get("pin_order", None)


class CfgSParameters:
    def apply(self):
        for s_param in self.s_parameters_models:
            fpath = s_param.file_path
            if not Path(fpath).anchor:
                fpath = str(Path(self.path_libraries) / fpath)
            comp_def = self._pedb.definitions.component[s_param.component_definition]
            if s_param.pin_order:
                comp_def.set_properties(pin_order=s_param.pin_order)
            comp_def.add_n_port_model(fpath, s_param.name)
            comp_list = dict()
            if s_param.apply_to_all:
                comp_list.update(
                    {refdes: comp for refdes, comp in comp_def.components.items() if refdes not in s_param.components}
                )
            else:
                comp_list.update(
                    {refdes: comp for refdes, comp in comp_def.components.items() if refdes in s_param.components}
                )

            for refdes, comp in comp_list.items():
                if refdes in s_param.reference_net_per_component:
                    ref_net = s_param.reference_net_per_component[refdes]
                else:
                    ref_net = s_param.reference_net
                comp.use_s_parameter_model(s_param.name, reference_net=ref_net)

    def get_data_from_db(self, cfg_components):
        db_comp_def = self._pedb.definitions.component
        for name, compdef_obj in db_comp_def.items():
            nport_models = compdef_obj.component_models
            if not nport_models:
                continue
            else:
                pin_order = compdef_obj.get_properties()["pin_order"]
                temp_comps = [i for i in cfg_components if i["definition"] == name]
                for model_name, model_obj in nport_models.items():
                    temp_comp_list = []
                    reference_net_per_component = {}
                    for i in temp_comps:
                        s_param_model = i.get("s_parameter_model")
                        if s_param_model:
                            if s_param_model["model_name"] == model_name:
                                temp_comp_list.append(i["reference_designator"])
                                reference_net_per_component[i["reference_designator"]] = s_param_model["reference_net"]
                        else:
                            continue

                    self.s_parameters_models.append(
                        CfgSParameterModel(
                            name=model_name,
                            component_definition=name,
                            file_path=model_obj.reference_file,
                            apply_to_all=False,
                            components=temp_comp_list,
                            reference_net_per_component=reference_net_per_component,
                            pin_order=pin_order,
                        )
                    )

        data = []
        for i in self.s_parameters_models:
            data.append(
                {
                    "name": i.name,
                    "component_definition": i.component_definition,
                    "file_path": i.file_path,
                    "apply_to_all": i.apply_to_all,
                    "components": i.components,
                    "reference_net_per_component": i.reference_net_per_component,
                    "pin_order": i.pin_order,
                }
            )
        return data

    def __init__(self, pedb, data, path_lib=None):
        self._pedb = pedb
        self.path_libraries = path_lib
        self.s_parameters_models = [CfgSParameterModel(**i) for i in data]
