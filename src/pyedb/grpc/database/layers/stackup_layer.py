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

from __future__ import absolute_import

from ansys.edb.core.layer.layer import LayerType as GrpcLayerType
from ansys.edb.core.layer.stackup_layer import RoughnessRegion as GrpcRoughnessRegion
from ansys.edb.core.layer.stackup_layer import StackupLayer as GrpcStackupLayer
from ansys.edb.core.utility.value import Value as GrpcValue


class StackupLayer(GrpcStackupLayer):
    def __init__(self, pedb, edb_object=None):
        super().__init__(edb_object.msg)
        self._pedb = pedb
        self._edb_object = edb_object

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

    @property
    def type(self):
        """Layer type.

        Returns
        -------
        str
            Layer name.
        """
        return super().type.name.lower().split("_")[0]

    @type.setter
    def type(self, value):
        if value in self._stackup_layer_mapping:
            super(StackupLayer, self.__class__).type.__set__(self, self._stackup_layer_mapping[value])

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
                GrpcValue(0),
                GrpcValue(0),
                "copper",
            )

    @property
    def lower_elevation(self):
        """Lower elevation.

        Returns
        -------
        float
            Lower elevation.
        """
        return round(super().lower_elevation.value, 9)

    @lower_elevation.setter
    def lower_elevation(self, value):
        if self._pedb.stackup.mode == "overlapping":
            super(StackupLayer, self.__class__).lower_elevation.__set__(self, GrpcValue(value))

    @property
    def fill_material(self):
        """The layer's fill material.

        Returns
        -------
        str
            Material name.
        """
        if self.type == "signal":
            return self.get_fill_material()

    @fill_material.setter
    def fill_material(self, value):
        if self.type == "signal":
            self.set_fill_material(value)

    @property
    def upper_elevation(self):
        """Upper elevation.

        Returns
        -------
        float
            Upper elevation.
        """
        return round(super().upper_elevation.value, 9)

    @property
    def is_negative(self):
        """Determine whether this layer is a negative layer.

        Returns
        -------
        bool
            True if this layer is a negative layer, False otherwise.
        """
        return self.negative

    @is_negative.setter
    def is_negative(self, value):
        """Layer negative.

        Returns
        -------
        bool

        """
        self.negative = value

    @property
    def material(self):
        """Material.

        Returns
        -------
        str
            Material name.
        """
        return self.get_material()

    @material.setter
    def material(self, name):
        self.set_material(name)

    @property
    def conductivity(self):
        """Material conductivity.

        Returns
        -------
        float
            Material conductivity value.
        """
        if self.material in self._pedb.materials.materials:
            return self._pedb.materials[self.material].conductivity
        return None

    @property
    def permittivity(self):
        """Material permittivity.

        Returns
        -------
        float
            Material permittivity value.
        """
        if self.material in self._pedb.materials.materials:
            return self._pedb.materials[self.material].permittivity
        return None

    @property
    def loss_tangent(self):
        """Material loss_tangent.

        Returns
        -------
        float
            Material loss tangent value.
        """
        if self.material in self._pedb.materials.materials:
            return self._pedb.materials[self.material].loss_tangent
        return None

    @property
    def dielectric_fill(self):
        """Material name of the layer dielectric fill.

        Returns
        -------
        str
            Material name.
        """
        if self.type == "signal":
            return self.get_fill_material()
        else:
            return

    @dielectric_fill.setter
    def dielectric_fill(self, name):
        if self.type == "signal":
            self.set_fill_material(name)
        else:
            pass

    @property
    def thickness(self):
        """Layer thickness.

        Returns
        -------
        float
            Layer thickness.
        """
        return round(super().thickness.value, 9)

    @thickness.setter
    def thickness(self, value):
        super(StackupLayer, self.__class__).thickness.__set__(self, GrpcValue(value))

    @property
    def etch_factor(self):
        """Layer etching factor.

        Returns
        -------
        float
            Etching factor value.
        """
        return super().etch_factor.value

    @etch_factor.setter
    def etch_factor(self, value):
        if not value:
            self.etch_factor_enabled = False
        else:
            self.etch_factor_enabled = True
            super(StackupLayer, self.__class__).etch_factor.__set__(self, GrpcValue(value))

    @property
    def top_hallhuray_nodule_radius(self):
        """Huray model nodule radius on layer top.

        Returns
        -------
        float
            Nodule radius value.
        """
        try:
            top_roughness_model = self.get_roughness_model(GrpcRoughnessRegion.TOP)
            if len(top_roughness_model) == 2:
                return top_roughness_model[0].value
            else:
                return None
        except:
            return None

    @top_hallhuray_nodule_radius.setter
    def top_hallhuray_nodule_radius(self, value):
        try:
            top_roughness_model = self.get_roughness_model(GrpcRoughnessRegion.TOP)
            if len(top_roughness_model) == 2:
                top_roughness_model[0] = GrpcValue(value)
                self.set_roughness_model(top_roughness_model, GrpcRoughnessRegion.TOP)
        except:
            pass

    @property
    def top_hallhuray_surface_ratio(self):
        """Huray model surface ratio on layer top.

        Returns
        -------
        float
            Surface ratio.
        """
        try:
            top_roughness_model = self.get_roughness_model(GrpcRoughnessRegion.TOP)
            if len(top_roughness_model) == 2:
                return top_roughness_model[1].value
            else:
                return None
        except:
            return None

    @top_hallhuray_surface_ratio.setter
    def top_hallhuray_surface_ratio(self, value):
        try:
            top_roughness_model = self.get_roughness_model(GrpcRoughnessRegion.TOP)
            if len(top_roughness_model) == 2:
                top_roughness_model[1] = GrpcValue(value)
                self.set_roughness_model(top_roughness_model, GrpcRoughnessRegion.TOP)
        except:
            pass

    @property
    def bottom_hallhuray_nodule_radius(self):
        """Huray model nodule radius on layer bottom.

        Returns
        -------
        float
            Nodule radius.
        """
        try:
            bottom_roughness_model = self.get_roughness_model(GrpcRoughnessRegion.BOTTOM)
            if len(bottom_roughness_model) == 2:
                return round(bottom_roughness_model[0].value, 9)
            else:
                return None
        except:
            return None

    @bottom_hallhuray_nodule_radius.setter
    def bottom_hallhuray_nodule_radius(self, value):
        try:
            bottom_roughness_model = self.get_roughness_model(GrpcRoughnessRegion.BOTTOM)
            if len(bottom_roughness_model) == 2:
                bottom_roughness_model[0] = GrpcValue(value)
                self.set_roughness_model(bottom_roughness_model, GrpcRoughnessRegion.BOTTOM)
        except:
            pass

    @property
    def bottom_hallhuray_surface_ratio(self):
        """Huray model surface ratio on layer bottom.

        Returns
        -------
        float
            Surface ratio value.
        """
        try:
            bottom_roughness_model = self.get_roughness_model(GrpcRoughnessRegion.BOTTOM)
            if len(bottom_roughness_model) == 2:
                return bottom_roughness_model[1].value
            else:
                return None
        except:
            return None

    @bottom_hallhuray_surface_ratio.setter
    def bottom_hallhuray_surface_ratio(self, value):
        try:
            bottom_roughness_model = self.get_roughness_model(GrpcRoughnessRegion.BOTTOM)
            if len(bottom_roughness_model) == 2:
                bottom_roughness_model[1] = GrpcValue(value)
                self.set_roughness_model(bottom_roughness_model, GrpcRoughnessRegion.BOTTOM)
        except:
            pass

    @property
    def side_hallhuray_nodule_radius(self):
        """Huray model nodule radius on layer sides.

        Returns
        -------
        float
            Nodule radius value.

        """
        try:
            side_roughness_model = self.get_roughness_model(GrpcRoughnessRegion.SIDE)
            if len(side_roughness_model) == 2:
                return round(side_roughness_model[0].value, 9)
            return None
        except:
            return None

    @side_hallhuray_nodule_radius.setter
    def side_hallhuray_nodule_radius(self, value):
        try:
            side_roughness_model = self.get_roughness_model(GrpcRoughnessRegion.SIDE)
            if len(side_roughness_model) == 2:
                side_roughness_model[0] = GrpcValue(value)
                self.set_roughness_model(side_roughness_model, GrpcRoughnessRegion.SIDE)
        except:
            pass

    @property
    def side_hallhuray_surface_ratio(self):
        """Huray model surface ratio on layer sides.

        Returns
        -------
        float
            surface ratio.
        """
        try:
            side_roughness_model = self.get_roughness_model(GrpcRoughnessRegion.SIDE)
            if len(side_roughness_model) == 2:
                return side_roughness_model[1].value
            return None
        except:
            return None

    @side_hallhuray_surface_ratio.setter
    def side_hallhuray_surface_ratio(self, value):
        try:
            side_roughness_model = self.get_roughness_model(GrpcRoughnessRegion.SIDE)
            if len(side_roughness_model) == 2:
                side_roughness_model[1] = GrpcValue(value)
                self.set_roughness_model(side_roughness_model, GrpcRoughnessRegion.SIDE)
        except:
            pass

    @property
    def top_groisse_roughness(self):
        """Groisse model on layer top.

        Returns
        -------
        float
            Roughness value.
        """
        try:
            top_roughness_model = self.get_roughness_model(GrpcRoughnessRegion.TOP)
            if isinstance(top_roughness_model, GrpcValue):
                return top_roughness_model.value
            else:
                return None
        except:
            return None

    @top_groisse_roughness.setter
    def top_groisse_roughness(self, value):
        try:
            top_roughness_model = self.get_roughness_model(GrpcRoughnessRegion.TOP)
            if isinstance(top_roughness_model, GrpcValue):
                top_roughness_model = GrpcValue(value)
                self.set_roughness_model(top_roughness_model, GrpcRoughnessRegion.TOP)
        except:
            pass

    @property
    def bottom_groisse_roughness(self):
        """Groisse model on layer bottom.

        Returns
        -------
        float
            Roughness value.
        """
        try:
            bottom_roughness_model = self.get_roughness_model(GrpcRoughnessRegion.BOTTOM)
            if isinstance(bottom_roughness_model, GrpcValue):
                return bottom_roughness_model.value
            else:
                return None
        except:
            return None

    @bottom_groisse_roughness.setter
    def bottom_groisse_roughness(self, value):
        try:
            bottom_roughness_model = self.get_roughness_model(GrpcRoughnessRegion.BOTTOM)
            if isinstance(bottom_roughness_model, GrpcValue):
                bottom_roughness_model = GrpcValue(value)
                self.set_roughness_model(bottom_roughness_model, GrpcRoughnessRegion.BOTTOM)
        except:
            pass

    @property
    def side_groisse_roughness(self):
        """Groisse model on layer bottom.

        Returns
        -------
        float
            Roughness value.
        """
        try:
            side_roughness_model = self.get_roughness_model(GrpcRoughnessRegion.SIDE)
            if isinstance(side_roughness_model, GrpcValue):
                return side_roughness_model.value
            else:
                return None
        except:
            return None

    @side_groisse_roughness.setter
    def side_groisse_roughness(self, value):
        try:
            side_roughness_model = self.get_roughness_model(GrpcRoughnessRegion.BOTTOM)
            if isinstance(side_roughness_model, GrpcValue):
                side_roughness_model = GrpcValue(value)
                self.set_roughness_model(side_roughness_model, GrpcRoughnessRegion.BOTTOM)
        except Exception as e:
            self._pedb.logger.error(e)

    def assign_roughness_model(
        self,
        model_type="huray",
        huray_radius="0.5um",
        huray_surface_ratio="2.9",
        groisse_roughness="1um",
        apply_on_surface="all",
    ):
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
        self.roughness_enabled = True
        for r in regions:
            if model_type == "huray":
                model = (GrpcValue(huray_radius), GrpcValue(huray_surface_ratio))
            else:
                model = GrpcValue(groisse_roughness)
            self.set_roughness_model(model, r)

    @property
    def properties(self):
        data = {"name": self.name, "type": self.type, "color": self.color}
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
