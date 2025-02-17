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
        return super().type.name.lower()

    @type.setter
    def type(self, value):
        if value in self._stackup_layer_mapping:
            super(StackupLayer, self.__class__).type.__set__(self, self._stackup_layer_mapping[value])

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
        if self.is_stackup_layer:
            return self.get_fill_material()

    @fill_material.setter
    def fill_material(self, value):
        if self.is_stackup_layer:
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
        top_roughness_model = self.get_roughness_model(GrpcRoughnessRegion.TOP)
        if top_roughness_model:
            return top_roughness_model.nodule_radius.value
        else:
            return None

    @top_hallhuray_nodule_radius.setter
    def top_hallhuray_nodule_radius(self, value):
        top_roughness_model = self.get_roughness_model(GrpcRoughnessRegion.TOP)
        top_roughness_model.nodule_radius = GrpcValue(value)

    @property
    def top_hallhuray_surface_ratio(self):
        """Huray model surface ratio on layer top.

        Returns
        -------
        float
            Surface ratio.
        """
        top_roughness_model = self.get_roughness_model(GrpcRoughnessRegion.TOP)
        if top_roughness_model:
            return top_roughness_model.surface_ratio.value
        else:
            return None

    @top_hallhuray_surface_ratio.setter
    def top_hallhuray_surface_ratio(self, value):
        top_roughness_model = self.get_roughness_model(GrpcRoughnessRegion.TOP)
        top_roughness_model.surface_roughness = GrpcValue(value)

    @property
    def bottom_hallhuray_nodule_radius(self):
        """Huray model nodule radius on layer bottom.

        Returns
        -------
        float
            Nodule radius.
        """
        bottom_roughness_model = self.get_roughness_model(GrpcRoughnessRegion.BOTTOM)
        if bottom_roughness_model:
            return bottom_roughness_model.nodule_radius.value
        return None

    @bottom_hallhuray_nodule_radius.setter
    def bottom_hallhuray_nodule_radius(self, value):
        top_roughness_model = self.get_roughness_model(GrpcRoughnessRegion.BOTTOM)
        top_roughness_model.nodule_radius = GrpcValue(value)

    @property
    def bottom_hallhuray_surface_ratio(self):
        """Huray model surface ratio on layer bottom.

        Returns
        -------
        float
            Surface ratio value.
        """
        bottom_roughness_model = self.get_roughness_model(GrpcRoughnessRegion.BOTTOM)
        if bottom_roughness_model:
            return bottom_roughness_model.surface_ratio.value
        return None

    @bottom_hallhuray_surface_ratio.setter
    def bottom_hallhuray_surface_ratio(self, value):
        top_roughness_model = self.get_roughness_model(GrpcRoughnessRegion.BOTTOM)
        top_roughness_model.surface_ratio = GrpcValue(value)

    @property
    def side_hallhuray_nodule_radius(self):
        """Huray model nodule radius on layer sides.

        Returns
        -------
        float
            Nodule radius value.

        """
        side_roughness_model = self.get_roughness_model(GrpcRoughnessRegion.SIDE)
        if side_roughness_model:
            return side_roughness_model.nodule_radius.value
        return None

    @side_hallhuray_nodule_radius.setter
    def side_hallhuray_nodule_radius(self, value):
        top_roughness_model = self.get_roughness_model(GrpcRoughnessRegion.SIDE)
        top_roughness_model.nodule_radius = GrpcValue(value)

    @property
    def side_hallhuray_surface_ratio(self):
        """Huray model surface ratio on layer sides.

        Returns
        -------
        float
            surface ratio.
        """
        side_roughness_model = self.get_roughness_model(GrpcRoughnessRegion.SIDE)
        if side_roughness_model:
            return side_roughness_model.surface_ratio.value
        else:
            return None

    @side_hallhuray_surface_ratio.setter
    def side_hallhuray_surface_ratio(self, value):
        top_roughness_model = self.get_roughness_model(GrpcRoughnessRegion.SIDE)
        top_roughness_model.surface_ratio = GrpcValue(value)

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
            regions = [GrpcRoughnessRegion.BOTTOM]
        self.roughness_enabled = True
        for r in regions:
            if model_type == "huray":
                model = (GrpcValue(huray_radius), GrpcValue(huray_surface_ratio))
            else:
                model = GrpcValue(groisse_roughness)
            self.set_roughness_model(model, r)
