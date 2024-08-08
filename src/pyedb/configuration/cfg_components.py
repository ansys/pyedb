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


class CfgPortProperties(CfgBase):
    def __init__(self, **kwargs):
        self.reference_offset = kwargs.pop("reference_offset", 0)
        self.reference_size_auto = kwargs.pop("reference_size_auto", 0)
        self.reference_size_x = kwargs.pop("reference_size_x", 0)
        self.reference_size_y = kwargs.pop("reference_size_y", 0)


class CfgSolderBallsProperties(CfgBase):
    def __init__(self, **kwargs):
        self.shape = kwargs.pop("shape", None)
        self.diameter = kwargs.pop("diameter", None)
        self.mid_diameter = kwargs.pop("mid_diameter", None)
        self.height = kwargs.pop("height", None)
        self.enabled = kwargs.pop("enabled", None)


class CfgRlcModel(CfgBase):
    def __init__(self, **kwargs):
        self.resistance = kwargs.get("resistance", None)
        self.inductance = kwargs.get("inductance", None)
        self.capacitance = kwargs.get("capacitance", None)
        self.type = kwargs.get("type", None)
        self.p1 = kwargs.get("p1", None)
        self.p2 = kwargs.get("p2", None)


class CfgComponent(CfgBase):
    protected_attributes = ["reference_designator", "definition", "location", "angle", "placement_layer"]

    def __init__(self, **kwargs):
        self.enabled = kwargs.get("enabled", None)

        self.reference_designator = kwargs.get("reference_designator", None)
        self.definition = kwargs.get("definition", None)
        self.type = kwargs.get("part_type", None)
        self.value = kwargs.get("value", None)
        self.port_properties = CfgPortProperties(**kwargs["port_properties"]) if "port_properties" in kwargs else None
        self.solder_ball_properties = (
            CfgSolderBallsProperties(**kwargs["solder_ball_properties"]) if "solder_ball_properties" in kwargs else None
        )
        rlc_models = kwargs.get("rlc_model", [])

        self.rlc_model = [CfgRlcModel(**rlc_m) for rlc_m in rlc_models]

        self.x_location, self.y_location = kwargs.get("location", [None, None])
        self.angle = kwargs.get("angle", None)
        self.placement_layer = kwargs.get("placement_layer", None)

    def export_properties(self):
        """Export component properties.

        Returns
        -------
        Dict
        """
        data_comp = {}
        data_comp["enabled"] = self.enabled
        data_comp["reference_designator"] = self.reference_designator
        data_comp["definition"] = self.definition
        data_comp["type"] = self.type
        data_comp["value"] = self.value
        data_comp["x_location"] = self.x_location
        data_comp["y_location"] = self.y_location
        # data_comp["angle"] = self.angle
        data_comp["placement_layer"] = self.placement_layer
        return data_comp


class CfgComponents:
    def __init__(self, pedb, components_data):
        self._pedb = pedb
        self.components = [CfgComponent(**comp) for comp in components_data]

    def apply(self):
        comps_in_db = self._pedb.components
        for comp in self.components:
            c_db = comps_in_db[comp.reference_designator]

            for attr, value in comp.get_attributes().items():  # All component properties
                if attr == "solder_ball_properties":
                    solder_ball_properties = value
                    port_properties = comp.port_properties
                    self._pedb.components.set_solder_ball(
                        component=comp.reference_designator,
                        sball_diam=solder_ball_properties.diameter,
                        sball_mid_diam=solder_ball_properties.mid_diameter,
                        sball_height=solder_ball_properties.height,
                        shape=solder_ball_properties.shape,
                        auto_reference_size=port_properties.reference_size_auto,
                        reference_height=port_properties.reference_offset,
                        reference_size_x=port_properties.reference_size_x,
                        reference_size_y=port_properties.reference_size_y,
                    )
                elif attr == "port_properties":
                    pass
                elif attr == "rlc_model":
                    rlc_models = value
                    model_layout = c_db.model
                    for pp in model_layout.pin_pairs:
                        model_layout.delete_pin_pair_rlc(pp)
                    for pp in rlc_models:
                        pin_pair = self._pedb.edb_api.utility.PinPair(pp.p1, pp.p2)
                        rlc = self._pedb.edb_api.utility.Rlc()
                        rlc.IsParallel = False if pp.type else True
                        if pp.resistance is not None:
                            rlc.REnabled = True
                            rlc.R = self._pedb.edb_value(pp.resistance)
                        else:
                            rlc.REnabled = False
                        if pp.inductance is not None:
                            rlc.LEnabled = True
                            rlc.L = self._pedb.edb_value(pp.inductance)
                        else:
                            rlc.LEnabled = False

                        if pp.capacitance is not None:
                            rlc.CEnabled = True
                            rlc.C = self._pedb.edb_value(pp.capacitance)
                        else:
                            rlc.CEnabled = False
                        model_layout._set_pin_pair_rlc(pin_pair, rlc)
                        comps_in_db.model = model_layout
                else:
                    if attr in dir(c_db):
                        setattr(c_db, attr, value)
                    else:
                        raise AttributeError(f"'{attr}' is not valid component attribute.")

    def _load_data_from_db(self):
        self.components = []
        comps_in_db = self._pedb.components
        for _, comp in comps_in_db.instances.items():
            cfg_comp = CfgComponent(
                enabled=comp.enabled,
                reference_designator=comp.name,
                part_type=comp.type,
                value=comp.value,
                definition=comp.component_def,
                location=comp.location,
                placement_layer=comp.placement_layer,
            )
            self.components.append(cfg_comp)

    def get_data_from_db(self):
        self._load_data_from_db()
        data = []
        for comp in self.components:
            data.append(comp.export_properties())
        return data
