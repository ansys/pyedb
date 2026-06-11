# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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

"""Build S-parameter model assignment entries for configuration payloads."""

from pathlib import Path
from typing import Any, Optional

from pydantic import Field

from pyedb.configuration.cfg_common import CfgBaseModel
from pyedb.misc.decorators import deprecated_property


class CfgSParameterModel(CfgBaseModel):
    """Represent one Touchstone model assignment for a component definition."""

    model_config = {"populate_by_name": True, "extra": "ignore"}

    name: str = ""
    component_definition: str = ""
    file_path: str = ""
    reference_net: str = ""
    apply_to_all: bool = True
    components: list[str] = Field(default_factory=list)
    reference_net_per_component: dict[str, str] = Field(default_factory=dict)
    pin_order: Optional[Any] = None


class CfgSParameters:
    """Manage all configured S-parameter model assignments."""

    def apply(self):
        """Write all S-parameter model assignments into the open EDB design."""
        for s_param in self.models:
            fpath = s_param.file_path
            if not Path(fpath).anchor:
                if self.path_libraries:
                    base = Path(self.path_libraries)
                else:
                    base = Path(self._pedb.edbpath).parent
                fpath = str(base / fpath)
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
        """Read S-parameter model assignments from EDB."""
        if self._pedb is None:
            return [m.model_dump() for m in self.models]
        db_comp_def = self._pedb.definitions.components
        for name, compdef_obj in db_comp_def.items():
            nport_models = compdef_obj.component_models
            if not nport_models:
                continue
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

                self.models.append(
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

        return [m.model_dump() for m in self.models]

    def __init__(self, pedb=None, data=None, path_lib=None):
        self._pedb = pedb
        self.path_libraries = path_lib
        self.models = [CfgSParameterModel(**i) if isinstance(i, dict) else i for i in (data or [])]

    def to_list(self):
        """Serialize all S-parameter models to a list of dictionaries."""
        return [m.model_dump() for m in self.models]

    @property
    @deprecated_property("Use models instead of s_parameters_models.")
    def s_parameters_models(self):
        """Alias for :attr:`models` for backwards compatibility.

        ..deprecated:: 0.76.0
            Use :attr:`models` instead of :attr:`s_parameters_models`.

        """
        return self.models

    @s_parameters_models.setter
    def s_parameters_models(self, value):
        self.models = value

    def add(
        self,
        name: str,
        component_definition: str,
        file_path: str,
        reference_net: str = "",
        apply_to_all: bool = True,
        components=None,
        reference_net_per_component=None,
        pin_order=None,
    ):
        """Add an S-parameter model assignment to this configuration.

        Parameters
        ----------
        name : str
            Model name registered in the EDB component library.
        component_definition : str
            Component definition (part) name, e.g. ``"CAP_100nF"``.
        file_path : str
            Absolute or library-relative path to the Touchstone file.
        reference_net : str, optional
            Default reference (ground) net for the model.
        apply_to_all : bool, optional
            Assign the model to all components matching *component_definition*
            when ``True`` (default).  When ``False``, only the entries in
            *components* are assigned.
        components : list of str, optional
            Reference designators to assign when *apply_to_all* is ``False``.
        reference_net_per_component : dict, optional
            Per-component reference net overrides:
            ``{"U1": "GND_U1", "U2": "GND"}``.
        pin_order : list, optional
            Custom port-to-pin mapping list.

        Returns
        -------
        CfgSParameterModel
            The newly created model assignment object.

        Examples
        --------
        cfg.s_parameters.add(
            "cap_model",
            component_definition="CAP_100nF",
            file_path="/snp/cap.s2p",
            reference_net="GND"
        )
        """
        model = CfgSParameterModel(
            name=name,
            component_definition=component_definition,
            file_path=file_path,
            reference_net=reference_net,
            apply_to_all=apply_to_all,
            components=components or [],
            reference_net_per_component=reference_net_per_component or {},
            pin_order=pin_order,
        )
        self.models.append(model)
        return model
