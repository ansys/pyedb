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
    def __init__(self, pedb, edb_object=None, name="", layer_type="signal", **kwargs):
        super().__init__(pedb, edb_object, name=name, layer_type=layer_type, **kwargs)
        self._pedb = pedb
        self._material = ""
        self._conductivity = 0.0
        self._permittivity = 0.0
        self._loss_tangent = 0.0
        self._dielectric_fill = ""
        self._thickness = 0.0
        self._etch_factor = 0.0
        self._roughness_enabled = False
        self._top_hallhuray_nodule_radius = 0.5e-6
        self._top_hallhuray_surface_ratio = 2.9
        self._bottom_hallhuray_nodule_radius = 0.5e-6
        self._bottom_hallhuray_surface_ratio = 2.9
        self._side_hallhuray_nodule_radius = 0.5e-6
        self._side_hallhuray_surface_ratio = 2.9
        self._material = None
        self._upper_elevation = 0.0
        self._lower_elevation = 0.0

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
        """Retrieve type of the layer."""
        return self.type.name.lower()

    @type.setter
    def type(self, value):
        if value in self._stackup_layer_mapping:
            layer_type = self._stackup_layer_mapping[value]
            layer_clone = self.clone()
            layer_clone.type = layer_type
            self._pedb.stackup._set_layout_stackup(layer_clone, "change_attribute")

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
        return self.lower_elevation.value

    @lower_elevation.setter
    def lower_elevation(self, value):
        if self._pedb.stackup.mode == "overlapping":
            layer_clone = self.clone()
            layer_clone.lower_elevation = GrpcValue(value)
            self._pedb.stackup._set_layout_stackup(layer_clone, "change_attribute")

    @property
    def fill_material(self):
        """The layer's fill material."""
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
        return self.upper_elevation.value

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
        layer_clone = self.clone()
        layer_clone.negative = value
        self._pedb.stackup._set_layout_stackup(layer_clone, "change_attribute")

    @property
    def material(self):
        """Get/Set the material loss_tangent.

        Returns
        -------
        float
        """
        return self.get_material()

    @material.setter
    def material(self, name):
        layer_clone = self.clone()
        layer_clone.set_material(name)
        self._pedb.stackup._set_layout_stackup(layer_clone, "change_attribute")
        self._material = name

    @property
    def conductivity(self):
        """Get the material conductivity.

        Returns
        -------
        float
        """
        if self.material in self._pedb.materials.materials:
            self._conductivity = self._pedb.materials[self.material].conductivity
            return self._conductivity

        return None

    @property
    def permittivity(self):
        """Get the material permittivity.

        Returns
        -------
        float
        """
        if self.material in self._pedb.materials.materials:
            self._permittivity = self._pedb.materials[self.material].permittivity
            return self._permittivity
        return None

    @property
    def loss_tangent(self):
        """Get the material loss_tangent.

        Returns
        -------
        float
        """
        if self.material in self._pedb.materials.materials:
            self._loss_tangent = self._pedb.materials[self.material].loss_tangent
            return self._loss_tangent
        return None

    @property
    def dielectric_fill(self):
        """Retrieve material name of the layer dielectric fill."""
        if self.type == "signal":
            self._dielectric_fill = self.get_fill_material()
            return self._dielectric_fill
        else:
            return

    @dielectric_fill.setter
    def dielectric_fill(self, name):
        name = name.lower()
        if self.type == "signal":
            layer_clone = self.clone()
            layer_clone.set_fill_material(name)
            self._pedb.stackup._set_layout_stackup(layer_clone, "change_attribute")
            self._dielectric_fill = name
        else:
            pass

    @property
    def thickness(self):
        """Retrieve thickness of the layer.

        Returns
        -------
        float
        """
        return self.thickness.value

    @thickness.setter
    def thickness(self, value):
        self.thickness = GrpcValue(value)

    @property
    def etch_factor(self):
        """Retrieve etch factor of this layer.

        Returns
        -------
        float
        """
        return self.etch_factor.value

    @etch_factor.setter
    def etch_factor(self, value):
        layer_clone = self.clone()
        if not value:
            layer_clone.etch_factor_enabled = False
        else:
            layer_clone.etch_factor_enabled = True
            layer_clone.etch_factor = GrpcValue(value)
        self._pedb.stackup._set_layout_stackup(layer_clone, "change_attribute")
        self._etch_factor = value

    @property
    def roughness_enabled(self):
        """Determine whether roughness is enabled on this layer.

        Returns
        -------
        bool
        """
        return self.roughness_enabled

    @roughness_enabled.setter
    def roughness_enabled(self, value):
        layer_clone = self.clone()
        layer_clone.roughness_enabled = value
        self._pedb.stackup._set_layout_stackup(layer_clone, "change_attribute")

    @property
    def top_hallhuray_nodule_radius(self):
        """Retrieve huray model nodule radius on top of the conductor."""
        top_roughness_model = self.get_roughness_model(GrpcRoughnessRegion.TOP)
        if top_roughness_model:
            return top_roughness_model.nodule_radius.value
        else:
            return None

    @top_hallhuray_nodule_radius.setter
    def top_hallhuray_nodule_radius(self, value):
        layer_clone = self.clone()
        top_roughness_model = layer_clone.get_roughness_model(GrpcRoughnessRegion.TOP)
        top_roughness_model.nodule_radius = GrpcValue(value)
        self._pedb.stackup._set_layout_stackup(layer_clone, "change_attribute")

    @property
    def top_hallhuray_surface_ratio(self):
        """Retrieve huray model surface ratio on top of the conductor."""
        top_roughness_model = self.get_roughness_model(GrpcRoughnessRegion.TOP)
        if top_roughness_model:
            return top_roughness_model.surface_ratio.value
        else:
            return None

    @top_hallhuray_surface_ratio.setter
    def top_hallhuray_surface_ratio(self, value):
        layer_clone = self.clone()
        top_roughness_model = layer_clone.get_roughness_model(GrpcRoughnessRegion.TOP)
        top_roughness_model.surface_roughness = GrpcValue(value)
        self._pedb.stackup._set_layout_stackup(layer_clone, "change_attribute")

    @property
    def bottom_hallhuray_nodule_radius(self):
        """Retrieve huray model nodule radius on bottom of the conductor."""
        bottom_roughness_model = self.get_roughness_model(GrpcRoughnessRegion.BOTTOM)
        if bottom_roughness_model:
            return bottom_roughness_model.nodule_radius.value

    @bottom_hallhuray_nodule_radius.setter
    def bottom_hallhuray_nodule_radius(self, value):
        layer_clone = self.clone()
        top_roughness_model = layer_clone.get_roughness_model(GrpcRoughnessRegion.BOTTOM)
        top_roughness_model.nodule_radius = GrpcValue(value)
        self._pedb.stackup._set_layout_stackup(layer_clone, "change_attribute")

    @property
    def bottom_hallhuray_surface_ratio(self):
        """Retrieve huray model surface ratio on bottom of the conductor."""
        bottom_roughness_model = self.get_roughness_model(GrpcRoughnessRegion.BOTTOM)
        if bottom_roughness_model:
            return bottom_roughness_model.surface_ratio.value

    @bottom_hallhuray_surface_ratio.setter
    def bottom_hallhuray_surface_ratio(self, value):
        layer_clone = self.clone()
        top_roughness_model = layer_clone.get_roughness_model(GrpcRoughnessRegion.BOTTOM)
        top_roughness_model.surface_ratio = GrpcValue(value)
        self._pedb.stackup._set_layout_stackup(layer_clone, "change_attribute")

    @property
    def side_hallhuray_nodule_radius(self):
        """Retrieve huray model nodule radius on sides of the conductor."""
        side_roughness_model = self.get_roughness_model(GrpcRoughnessRegion.SIDE)
        if side_roughness_model:
            return side_roughness_model.nodule_radius.value
        return self._side_hallhuray_nodule_radius

    @side_hallhuray_nodule_radius.setter
    def side_hallhuray_nodule_radius(self, value):
        layer_clone = self.clone()
        top_roughness_model = layer_clone.get_roughness_model(GrpcRoughnessRegion.SIDE)
        top_roughness_model.nodule_radius = GrpcValue(value)
        self._pedb.stackup._set_layout_stackup(layer_clone, "change_attribute")

    @property
    def side_hallhuray_surface_ratio(self):
        """Retrieve huray model surface ratio on sides of the conductor."""
        side_roughness_model = self.get_roughness_model(GrpcRoughnessRegion.SIDE)
        if side_roughness_model:
            return side_roughness_model.surface_ratio.value
        else:
            return None

    @side_hallhuray_surface_ratio.setter
    def side_hallhuray_surface_ratio(self, value):
        layer_clone = self.clone()
        top_roughness_model = layer_clone.get_roughness_model(GrpcRoughnessRegion.SIDE)
        top_roughness_model.surface_ratio = GrpcValue(value)
        self._pedb.stackup._set_layout_stackup(layer_clone, "change_attribute")

    def get_roughness_model(self, surface="top"):
        """Get roughness model of the layer.

        Parameters
        ----------
        surface : str, optional
            Where to fetch roughness model. The default is ``"top"``. Options are ``"top"``, ``"bottom"``, ``"side"``.

        Returns
        -------
        ``"Ansys.Ansoft.Edb.Cell.RoughnessModel"``

        """
        if not self.is_stackup_layer:  # pragma: no cover
            return
        if surface == "top":
            return self.get_roughness_model(GrpcRoughnessRegion.TOP)
        elif surface == "bottom":
            return self.get_roughness_model(GrpcRoughnessRegion.BOTTOM)
        elif surface == "side":
            return self.get_roughness_model(GrpcRoughnessRegion.SIDE)

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

        Returns
        -------

        """
        radius = GrpcValue(huray_radius)
        surface_ratio = GrpcValue(huray_surface_ratio)
        groisse_roughness = GrpcValue(groisse_roughness)
        regions = []
        if apply_on_surface == "all":
            regions = [GrpcRoughnessRegion.TOP, GrpcRoughnessRegion.BOTTOM, GrpcRoughnessRegion.SIDE]
        elif apply_on_surface == "top":
            regions = [GrpcRoughnessRegion.TOP]
        elif apply_on_surface == "bottom":
            regions = [GrpcRoughnessRegion.BOTTOM]
        elif apply_on_surface == "side":
            regions = [GrpcRoughnessRegion.BOTTOM]

        layer_clone = self.clone()
        layer_clone.roughness_enabled = True
        for r in regions:
            if model_type == "huray":
                model = (radius, surface_ratio)
            else:
                model = groisse_roughness
            layer_clone.set_roughness_model(model, r)
        return self._pedb.stackup._set_layout_stackup(layer_clone, "change_attribute")

    def _json_format(self):
        dict_out = {}
        self._color = self.color
        self._dielectric_fill = self.dielectric_fill
        self._etch_factor = self.etch_factor
        self._material = self.material
        self._name = self.name
        self._roughness_enabled = self.roughness_enabled
        self._thickness = self.thickness
        self._type = self.type
        self._roughness_enabled = self.roughness_enabled
        self._top_hallhuray_nodule_radius = self.top_hallhuray_nodule_radius
        self._top_hallhuray_surface_ratio = self.top_hallhuray_surface_ratio
        self._side_hallhuray_nodule_radius = self.side_hallhuray_nodule_radius
        self._side_hallhuray_surface_ratio = self.side_hallhuray_surface_ratio
        self._bottom_hallhuray_nodule_radius = self.bottom_hallhuray_nodule_radius
        self._bottom_hallhuray_surface_ratio = self.bottom_hallhuray_surface_ratio
        for k, v in self.__dict__.items():
            if (
                not k == "_pclass"
                and not k == "_conductivity"
                and not k == "_permittivity"
                and not k == "_loss_tangent"
            ):
                dict_out[k[1:]] = v
        return dict_out

    # TODO: This method might need some refactoring
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
