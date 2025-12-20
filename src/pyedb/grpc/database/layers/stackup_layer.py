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

from __future__ import absolute_import, annotations

from typing import TYPE_CHECKING, Union

from ansys.edb.core.layer.layer import LayerType as GrpcLayerType
from ansys.edb.core.layer.stackup_layer import RoughnessRegion as GrpcRoughnessRegion, StackupLayer as GrpcStackupLayer

if TYPE_CHECKING:
    from pyedb.grpc.database.layout.layout import Layout
from pyedb.grpc.database.utility.value import Value

_mapping_layer_type = {
    "signal": GrpcLayerType.SIGNAL_LAYER,
    "dielectric": GrpcLayerType.DIELECTRIC_LAYER,
    "wirebond": GrpcLayerType.WIREBOND_LAYER,
}


class StackupLayer:
    def __init__(self, pedb, edb_object=None):
        self.core = edb_object
        self._pedb = pedb

    @property
    def _stackup_layer_mapping(self):
        return {
            "conducting_layer": GrpcLayerType.CONDUCTING_LAYER,
            "silkscreen_layer": GrpcLayerType.SILKSCREEN_LAYER,
            "solder_mask_layer": GrpcLayerType.SOLDER_MASK_LAYER,
            "solder_paste_layer": GrpcLayerType.SOLDER_PASTE_LAYER,
            "glue_layer": GrpcLayerType.GLUE_LAYER,
            "wirebond_layer": GrpcLayerType.WIREBOND_LAYER,
            "user_layer": GrpcLayerType.USER_LAYER,
            "siwave_hfss_solver_regions": GrpcLayerType.SIWAVE_HFSS_SOLVER_REGIONS,
        }

    @classmethod
    def create(
        cls,
        layout: Layout,
        name: str,
        layer_type: str = "signal",
        thickness: Union[str, float] = "17um",
        elevation: Union[str, float] = 0.0,
        material: str = "copper",
    ) -> StackupLayer:
        layer = GrpcStackupLayer.create(
            name=name,
            layer_type=_mapping_layer_type[layer_type],
            thickness=Value(thickness),
            elevation=Value(elevation),
            material=material,
        )
        return cls(layout._pedb, layer)

    @property
    def id(self):
        """Layer ID.

        Returns
        -------
        int
            Layer ID.
        """
        return self.core.id

    @property
    def type(self) -> str:
        """Layer type.

        Returns
        -------
        str
            Layer name.
        """
        return self.core.type.name.lower().split("_")[0]

    @type.setter
    def type(self, value):
        if value in self._stackup_layer_mapping:
            self.core.type = value

    def update(self, **kwargs):
        for k, v in kwargs.items():
            if k in dir(self):
                self.__setattr__(k, v)
            elif k == "roughness":
                self.roughness_enabled = v["enabled"]
                if "top" in v:
                    top_roughness = v["top"]
                    if top_roughness:
                        if top_roughness["model"] == "huray":
                            nodule_radius = top_roughness["nodule_radius"]
                            surface_ratio = top_roughness["surface_ratio"]
                            self.assign_roughness_model(
                                model_type="huray",
                                huray_radius=nodule_radius,
                                huray_surface_ratio=surface_ratio,
                                apply_on_surface="top",
                            )
                        elif top_roughness["model"] == "groisse":
                            roughness = top_roughness["roughness"]
                            self.assign_roughness_model(
                                model_type="groisse", groisse_roughness=roughness, apply_on_surface="top"
                            )
                    if "bottom" in v:
                        bottom_roughness = v["bottom"]
                        if bottom_roughness:
                            if bottom_roughness["model"] == "huray":
                                nodule_radius = bottom_roughness["nodule_radius"]
                                surface_ratio = bottom_roughness["surface_ratio"]
                                self.assign_roughness_model(
                                    model_type="huray",
                                    huray_radius=nodule_radius,
                                    huray_surface_ratio=surface_ratio,
                                    apply_on_surface="bottom",
                                )
                            elif bottom_roughness["model"] == "groisse":
                                roughness = bottom_roughness["roughness"]
                                self.assign_roughness_model(
                                    model_type="groisse", groisse_roughness=roughness, apply_on_surface="bottom"
                                )
                    if "side" in v:
                        side_roughness = v["side"]
                        if side_roughness:
                            if side_roughness["model"] == "huray":
                                nodule_radius = side_roughness["nodule_radius"]
                                surface_ratio = side_roughness["surface_ratio"]
                                self.assign_roughness_model(
                                    model_type="huray",
                                    huray_radius=nodule_radius,
                                    huray_surface_ratio=surface_ratio,
                                    apply_on_surface="side",
                                )
                            elif side_roughness["model"] == "groisse":
                                roughness = side_roughness["roughness"]
                                self.assign_roughness_model(
                                    model_type="groisse", groisse_roughness=roughness, apply_on_surface="side"
                                )

            elif k == "etching":
                self.etch_factor_enabled = v["enabled"]
                self.etch_factor = float(v["factor"])
            else:
                self._pedb.logger.error(f"{k} is not a valid layer attribute")

    def _create(self, layer_type):
        if layer_type in self._stackup_layer_mapping:
            layer_type = self._stackup_layer_mapping[layer_type]
            self._edb_object = GrpcStackupLayer.create(
                self._name,
                layer_type,
                Value(0),
                Value(0),
                "copper",
            )

    @property
    def lower_elevation(self) -> float:
        """Lower elevation.

        Returns
        -------
        float
            Lower elevation.
        """
        return Value(self.core.lower_elevation, self._pedb.active_cell)

    @lower_elevation.setter
    def lower_elevation(self, value):
        if self._pedb.stackup.mode == "overlapping":
            self.core.lower_elevation = Value(value)

    @property
    def fill_material(self) -> Union[str, None]:
        """The layer's fill material.

        Returns
        -------
        str
            Material name.
        """
        if self.type == "signal":
            return self.core.get_fill_material()
        else:
            return None

    @fill_material.setter
    def fill_material(self, value):
        self.core.set_fill_material(value)

    @property
    def upper_elevation(self) -> float:
        """Upper elevation.

        Returns
        -------
        float
            Upper elevation.
        """
        return Value(self.core.upper_elevation, self._pedb.active_cell)

    @property
    def is_negative(self) -> bool:
        """Determine whether this layer is a negative layer.

        Returns
        -------
        bool
            True if this layer is a negative layer, False otherwise.
        """
        return self.core.negative

    @property
    def name(self) -> str:
        """Layer name.

        Returns
        -------
        str
            Layer name.

        """
        return self.core.name

    @name.setter
    def name(self, value):
        self.core.name = value

    @is_negative.setter
    def is_negative(self, value):
        """Layer negative.

        Returns
        -------
        bool

        """
        self.core.negative = value

    @property
    def is_stackup_layer(self) -> bool:
        """Testing if layer is stackup layer.

        Returns
        -------
        `True` if layer type is "signal" or "dielectric".
        """
        if self.type in ["signal", "dielectric", "via", "wirebond"]:
            return True
        return False

    @property
    def material(self) -> str:
        """Material.

        Returns
        -------
        str
            Material name.
        """
        return self.core.get_material()

    @material.setter
    def material(self, name):
        self.core.set_material(name)

    @property
    def conductivity(self) -> float:
        """Material conductivity.

        Returns
        -------
        float
            Material conductivity value.
        """
        if self.material in self._pedb.materials.materials:
            condcutivity = self._pedb.materials[self.material].conductivity
            return condcutivity if condcutivity else 0.0
        return 0.0

    @property
    def permittivity(self) -> float:
        """Material permittivity.

        Returns
        -------
        float
            Material permittivity value.
        """
        if self.material in self._pedb.materials.materials:
            permittivity = self._pedb.materials[self.material].permittivity
            return permittivity if permittivity else 1.0
        return 1.0

    @property
    def loss_tangent(self) -> float:
        """Material loss_tangent.

        Returns
        -------
        float
            Material loss tangent value.
        """
        if self.material in self._pedb.materials.materials:
            loss_tangent = self._pedb.materials[self.material].loss_tangent
            return loss_tangent if loss_tangent else 0.0
        return 0.0

    @property
    def dielectric_fill(self) -> str:
        """Material name of the layer dielectric fill.

        Returns
        -------
        str
            Material name.
        """
        if self.type == "signal":
            return self.core.get_fill_material()
        else:
            return ""

    @dielectric_fill.setter
    def dielectric_fill(self, name):
        if self.type == "signal":
            self.core.set_fill_material(name)
        else:
            pass

    @property
    def thickness(self) -> float:
        """Layer thickness.

        Returns
        -------
        float
            Layer thickness.
        """
        return Value(self.core.thickness, self._pedb.active_cell)

    @thickness.setter
    def thickness(self, value):
        self.core.thickness = Value(value)

    @property
    def etch_factor(self) -> float:
        """Layer etching factor.

        Returns
        -------
        float
            Etching factor value.
        """
        return Value(self.core.etch_factor, self._pedb.active_cell)

    @etch_factor.setter
    def etch_factor(self, value):
        if not value:
            self.core.etch_factor_enabled = False

        else:
            self.core.etch_factor_enabled = True
            self.core.etch_factor = Value(value, self._pedb.active_cell)

    @property
    def top_hallhuray_nodule_radius(self) -> float:
        """Huray model nodule radius on layer top.

        Returns
        -------
        float
            Nodule radius value.
        """
        try:
            top_roughness_model = self.core.get_roughness_model(GrpcRoughnessRegion.TOP)
            if len(top_roughness_model) == 2:
                return Value(top_roughness_model[0], self._pedb.active_cell)
            else:
                return 0.0
        except:
            return 0.0

    @top_hallhuray_nodule_radius.setter
    def top_hallhuray_nodule_radius(self, value):
        try:
            top_roughness_model = self.core.get_roughness_model(GrpcRoughnessRegion.TOP)
            if len(top_roughness_model) == 2:
                top_roughness_model[0] = Value(value)
                self.core.set_roughness_model(top_roughness_model, GrpcRoughnessRegion.TOP)
        except Exception as e:
            self._pedb.logger.error(
                f"Failed to update property top_hallhuray_nodule_radius with value {value} "
                f"- {type(e).__name__}: {str(e)}"
            )

    @property
    def top_hallhuray_surface_ratio(self) -> float:
        """Huray model surface ratio on layer top.

        Returns
        -------
        float
            Surface ratio.
        """
        try:
            top_roughness_model = self.core.get_roughness_model(GrpcRoughnessRegion.TOP)
            if len(top_roughness_model) == 2:
                return Value(top_roughness_model[1], self._pedb.active_cell)
            else:
                return 0.0
        except:
            return 0.0

    @top_hallhuray_surface_ratio.setter
    def top_hallhuray_surface_ratio(self, value):
        try:
            top_roughness_model = self.core.get_roughness_model(GrpcRoughnessRegion.TOP)
            if len(top_roughness_model) == 2:
                top_roughness_model[1] = Value(value)
                self.core.set_roughness_model(top_roughness_model, GrpcRoughnessRegion.TOP)
        except Exception as e:
            self._pedb.logger.error(
                f"Failed to update property top_hallhuray_surface_ratio with value {value} "
                f"- {type(e).__name__}: {str(e)}"
            )

    @property
    def bottom_hallhuray_nodule_radius(self) -> float:
        """Huray model nodule radius on layer bottom.

        Returns
        -------
        float
            Nodule radius.
        """
        try:
            bottom_roughness_model = self.core.get_roughness_model(GrpcRoughnessRegion.BOTTOM)
            if len(bottom_roughness_model) == 2:
                return Value(bottom_roughness_model[0], self._pedb.active_cell)
            else:
                return 0.0
        except:
            return 0.0

    @bottom_hallhuray_nodule_radius.setter
    def bottom_hallhuray_nodule_radius(self, value):
        try:
            bottom_roughness_model = self.core.get_roughness_model(GrpcRoughnessRegion.BOTTOM)
            if len(bottom_roughness_model) == 2:
                bottom_roughness_model[0] = Value(value)
                self.core.set_roughness_model(bottom_roughness_model, GrpcRoughnessRegion.BOTTOM)
        except Exception as e:
            self._pedb.logger.error(
                f"Failed to update property bottom_hallhuray_nodule_radius with value {value} "
                f"- {type(e).__name__}: {str(e)}"
            )

    @property
    def bottom_hallhuray_surface_ratio(self) -> float:
        """Huray model surface ratio on layer bottom.

        Returns
        -------
        float
            Surface ratio value.
        """
        try:
            bottom_roughness_model = self.core.get_roughness_model(GrpcRoughnessRegion.BOTTOM)
            if len(bottom_roughness_model) == 2:
                return Value(bottom_roughness_model[1], self._pedb.active_cell)
            else:
                return 0.0
        except:
            return 0.0

    @bottom_hallhuray_surface_ratio.setter
    def bottom_hallhuray_surface_ratio(self, value):
        try:
            bottom_roughness_model = self.core.get_roughness_model(GrpcRoughnessRegion.BOTTOM)
            if len(bottom_roughness_model) == 2:
                bottom_roughness_model[1] = Value(value)
                self.core.set_roughness_model(bottom_roughness_model, GrpcRoughnessRegion.BOTTOM)
        except Exception as e:
            self._pedb.logger.error(
                f"Failed to update property bottom_hallhuray_surface_ratio with value {value} "
                f"- {type(e).__name__}: {str(e)}"
            )

    @property
    def side_hallhuray_nodule_radius(self) -> float:
        """Huray model nodule radius on layer sides.

        Returns
        -------
        float
            Nodule radius value.

        """
        try:
            side_roughness_model = self.core.get_roughness_model(GrpcRoughnessRegion.SIDE)
            if len(side_roughness_model) == 2:
                return Value(side_roughness_model[0], self._pedb.active_cell)
            return Value(0.0)
        except:
            return Value(0.0)

    @side_hallhuray_nodule_radius.setter
    def side_hallhuray_nodule_radius(self, value):
        try:
            side_roughness_model = self.core.get_roughness_model(GrpcRoughnessRegion.SIDE)
            if len(side_roughness_model) == 2:
                side_roughness_model[0] = Value(value)
                self.core.set_roughness_model(side_roughness_model, GrpcRoughnessRegion.SIDE)
        except Exception as e:
            self._pedb.logger.error(
                f"Failed to update property side_hallhuray_nodule_radius with value {value} "
                f"- {type(e).__name__}: {str(e)}"
            )

    @property
    def side_hallhuray_surface_ratio(self) -> float:
        """Huray model surface ratio on layer sides.

        Returns
        -------
        float
            surface ratio.
        """
        try:
            side_roughness_model = self.core.get_roughness_model(GrpcRoughnessRegion.SIDE)
            if len(side_roughness_model) == 2:
                return Value(side_roughness_model[1], self._pedb.active_cell)
            return 0.0
        except:
            return 0.0

    @side_hallhuray_surface_ratio.setter
    def side_hallhuray_surface_ratio(self, value):
        try:
            side_roughness_model = self.core.get_roughness_model(GrpcRoughnessRegion.SIDE)
            if len(side_roughness_model) == 2:
                side_roughness_model[1] = Value(value)
                self.core.set_roughness_model(side_roughness_model, GrpcRoughnessRegion.SIDE)
        except Exception as e:
            self._pedb.logger.error(
                f"Failed to update property side_hallhuray_surface_ratio with value {value} "
                f"- {type(e).__name__}: {str(e)}"
            )

    @property
    def top_groisse_roughness(self) -> float:
        """Groisse model on layer top.

        Returns
        -------
        float
            Roughness value.
        """
        try:
            top_roughness_model = self.core.get_roughness_model(GrpcRoughnessRegion.TOP)
            if isinstance(top_roughness_model, Value):
                return Value(top_roughness_model, self._pedb.active_cell)
            else:
                return Value(0.0)
        except:
            return Value(0.0)

    @top_groisse_roughness.setter
    def top_groisse_roughness(self, value):
        try:
            top_roughness_model = self.core.get_roughness_model(GrpcRoughnessRegion.TOP)
            if isinstance(top_roughness_model, Value):
                top_roughness_model = Value(value)
                self.core.set_roughness_model(top_roughness_model, GrpcRoughnessRegion.TOP)
        except Exception as e:
            self._pedb.logger.error(
                f"Failed to update property top_groisse_roughness with value {value} - {type(e).__name__}: {str(e)}"
            )

    @property
    def bottom_groisse_roughness(self) -> float:
        """Groisse model on layer bottom.

        Returns
        -------
        float
            Roughness value.
        """
        try:
            bottom_roughness_model = self.core.get_roughness_model(GrpcRoughnessRegion.BOTTOM)
            if isinstance(bottom_roughness_model, Value):
                return Value(bottom_roughness_model, self._pedb.active_cell)
            else:
                return Value(0.0)
        except:
            return Value(0.0)

    @bottom_groisse_roughness.setter
    def bottom_groisse_roughness(self, value):
        try:
            bottom_roughness_model = self.core.get_roughness_model(GrpcRoughnessRegion.BOTTOM)
            if isinstance(bottom_roughness_model, Value):
                bottom_roughness_model = Value(value)
                self.core.set_roughness_model(bottom_roughness_model, GrpcRoughnessRegion.BOTTOM)
        except Exception as e:
            self._pedb.logger.error(
                f"Failed to update property bottom_groisse_roughness with value {value} - {type(e).__name__}: {str(e)}"
            )

    @property
    def side_groisse_roughness(self) -> float:
        """Groisse model on layer bottom.

        Returns
        -------
        float
            Roughness value.
        """
        try:
            side_roughness_model = self.core.get_roughness_model(GrpcRoughnessRegion.SIDE)
            if isinstance(side_roughness_model, Value):
                return Value(side_roughness_model, self._pedb.active_cell)
            else:
                return Value(0.0)
        except:
            return Value(0.0)

    @side_groisse_roughness.setter
    def side_groisse_roughness(self, value):
        try:
            side_roughness_model = self.core.get_roughness_model(GrpcRoughnessRegion.BOTTOM)
            if isinstance(side_roughness_model, Value):
                side_roughness_model = Value(value)
                self.core.set_roughness_model(side_roughness_model, GrpcRoughnessRegion.BOTTOM)
        except Exception as e:
            self._pedb.logger.error(
                f"Failed to update property side_groisse_roughness with value {value} - {type(e).__name__}: {str(e)}"
            )

    @property
    def color(self) -> tuple[int, int, int]:
        """Layer color.

        Returns
        -------
        str
            Layer color in hex format.
        """
        return self.core.color

    @color.setter
    def color(self, value):
        self.core.color = value

    @property
    def transparency(self) -> int:
        """Layer transparency.

        Returns
        -------
        float
            Layer transparency value between 0 and 100.
        """
        return self.core.transparency

    @transparency.setter
    def transparency(self, value):
        self.core.transparency = value

    @property
    def roughness_enabled(self) -> bool:
        """Roughness model enabled status.

        Returns
        -------
        bool
            True if roughness model is enabled, False otherwise.
        """
        return self.core.roughness_enabled

    @roughness_enabled.setter
    def roughness_enabled(self, value):
        self.core.roughness_enabled = value

    def assign_roughness_model(
        self,
        model_type="huray",
        huray_radius="0.5um",
        huray_surface_ratio="2.9",
        groisse_roughness="1um",
        apply_on_surface="all",
    ) -> bool:
        """Assign roughness model on this layer.

        Parameters
        ----------
        model_type : str, optional
            Type of roughness model. The default is ``"huray"``. Options are ``"huray"``, ``"groisse"``.
        huray_radius : str, float, optional
            Radius of huray model. The default is ``"0.5um"``.
        huray_surface_ratio : str, float, optional.
            Surface ratio of huray model. The default is ``"2.9"``.
        groisse_roughness : str, float, optional
            Roughness of groisse model. The default is ``"1um"``.
        apply_on_surface : str, optional.
            Where to assign roughness model. The default is ``"all"``. Options are ``"top"``, ``"bottom"``,
             ``"side"``.

        Returns
        -------
        bool
        """
        regions = []
        if apply_on_surface == "all":
            regions = [GrpcRoughnessRegion.TOP, GrpcRoughnessRegion.BOTTOM, GrpcRoughnessRegion.SIDE]
        elif apply_on_surface == "top":
            regions = [GrpcRoughnessRegion.TOP]
        elif apply_on_surface == "bottom":
            regions = [GrpcRoughnessRegion.BOTTOM]
        elif apply_on_surface == "side":
            regions = [GrpcRoughnessRegion.SIDE]
        self.core.roughness_enabled = True
        for r in regions:
            if model_type == "huray":
                model = (Value(huray_radius), Value(huray_surface_ratio))
            else:
                model = Value(groisse_roughness)
            self.core.set_roughness_model(model, r)
        if [
            self.core.get_roughness_model(GrpcRoughnessRegion.TOP),
            self.core.get_roughness_model(GrpcRoughnessRegion.BOTTOM),
            self.core.get_roughness_model(GrpcRoughnessRegion.SIDE),
        ]:
            return True
        return False

    @property
    def properties(self):
        data = {"name": self.core.name, "type": self.type, "color": self.color}
        if self.type == "signal" or self.type == "dielectric":
            data["material"] = self.material
            data["thickness"] = self.thickness
        if self.type == "signal":
            data["fill_material"] = self.fill_material
        roughness = {"top": {}, "bottom": {}, "side": {}}
        if self.top_hallhuray_nodule_radius:
            roughness["top"]["model"] = "huray"
            roughness["top"]["nodule_radius"] = self.top_hallhuray_nodule_radius
            roughness["top"]["surface_ratio"] = self.top_hallhuray_surface_ratio

        elif self.top_groisse_roughness:
            roughness["top"]["model"] = "groisse"
            roughness["top"]["roughness"] = self.top_groisse_roughness

        if self.bottom_hallhuray_nodule_radius:
            roughness["bottom"]["model"] = "huray"
            roughness["bottom"]["nodule_radius"] = self.bottom_hallhuray_nodule_radius
            roughness["bottom"]["surface_ratio"] = self.bottom_hallhuray_surface_ratio

        elif self.bottom_groisse_roughness:
            roughness["bottom"]["model"] = "groisse"
            roughness["bottom"]["roughness"] = self.bottom_groisse_roughness

        if self.side_hallhuray_nodule_radius:
            roughness["side"]["model"] = "huray"
            roughness["side"]["nodule_radius"] = self.side_hallhuray_nodule_radius
            roughness["side"]["surface_ratio"] = self.side_hallhuray_surface_ratio

        elif self.side_groisse_roughness:
            roughness["side"]["model"] = "groisse"
            roughness["side"]["roughness"] = self.side_groisse_roughness

        if roughness["top"] or roughness["bottom"] or roughness["side"]:
            roughness["enabled"] = True
        else:
            roughness["enabled"] = False
        data["roughness"] = roughness
        data["etching"] = {"enabled": self.etch_factor_enabled, "factor": self.etch_factor}
        return data

    def _json_format(self):
        dict_out = {
            "color": self.color,
            "dielectric_fill": self.dielectric_fill,
            "etch_factor": self.etch_factor,
            "material": self.material,
            "loss_tangent": self.loss_tangent,
            "permittivity": self.permittivity,
            "conductivity": self.conductivity,
            "zones": self.core.zones,
            "transparency": self.core.transparency,
            "name": self.name,
            "roughness_enabled": self.roughness_enabled,
            "thickness": self.thickness,
            "lower_elevation": self.lower_elevation,
            "upper_elevation": self.upper_elevation,
            "type": self.type,
            "top_hallhuray_nodule_radius": self.top_hallhuray_nodule_radius,
            "top_hallhuray_surface_ratio": self.top_hallhuray_surface_ratio,
            "side_hallhuray_nodule_radius": self.side_hallhuray_nodule_radius,
            "side_hallhuray_surface_ratio": self.side_hallhuray_surface_ratio,
            "bottom_hallhuray_nodule_radius": self.bottom_hallhuray_nodule_radius,
            "bottom_hallhuray_surface_ratio": self.bottom_hallhuray_surface_ratio,
        }
        return dict_out

    def _load_layer(self, layer):
        if layer:
            self.color = layer["color"]
            self.type = layer["type"]
            if isinstance(layer["material"], str):
                self.material = layer["material"]
            else:
                material_data = layer["material"]
                if material_data is not None:
                    material_name = layer["material"]["name"]
                    self._pedb.materials.add_material(material_name, **material_data)
                    self.material = material_name
            if layer["dielectric_fill"]:
                if isinstance(layer["dielectric_fill"], str):
                    self.dielectric_fill = layer["dielectric_fill"]
                else:
                    dielectric_data = layer["dielectric_fill"]
                    if dielectric_data is not None:
                        self._pedb.materials.add_material(**dielectric_data)
                    self.dielectric_fill = layer["dielectric_fill"]["name"]
            self.thickness = layer["thickness"]
            self.etch_factor = layer["etch_factor"]
            self.roughness_enabled = layer["roughness_enabled"]
            if self.roughness_enabled:
                self.top_hallhuray_nodule_radius = layer["top_hallhuray_nodule_radius"]
                self.top_hallhuray_surface_ratio = layer["top_hallhuray_surface_ratio"]
                self.assign_roughness_model(
                    "huray",
                    layer["top_hallhuray_nodule_radius"],
                    layer["top_hallhuray_surface_ratio"],
                    apply_on_surface="top",
                )
                self.bottom_hallhuray_nodule_radius = layer["bottom_hallhuray_nodule_radius"]
                self.bottom_hallhuray_surface_ratio = layer["bottom_hallhuray_surface_ratio"]
                self.assign_roughness_model(
                    "huray",
                    layer["bottom_hallhuray_nodule_radius"],
                    layer["bottom_hallhuray_surface_ratio"],
                    apply_on_surface="bottom",
                )
                self.side_hallhuray_nodule_radius = layer["side_hallhuray_nodule_radius"]
                self.side_hallhuray_surface_ratio = layer["side_hallhuray_surface_ratio"]
                self.assign_roughness_model(
                    "huray",
                    layer["side_hallhuray_nodule_radius"],
                    layer["side_hallhuray_surface_ratio"],
                    apply_on_surface="side",
                )
