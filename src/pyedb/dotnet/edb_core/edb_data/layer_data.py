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


class LayerEdbClass(object):
    """Manages Edb Layers. Replaces EDBLayer."""

    def __init__(self, pedb, edb_object=None, name="", layer_type="undefined", **kwargs):
        self._pedb = pedb
        self._name = name
        self._color = ()
        self._type = ""

        if edb_object:
            self._edb_object = edb_object.Clone()
        else:
            self._create(layer_type)
            self.update(**kwargs)

    def _create(self, layer_type):
        layer_type = self._layer_name_mapping[layer_type]
        layer_type = self._doc_layer_mapping[layer_type]

        self._edb_object = self._pedb.edb_api.cell._cell.Layer(
            self._name,
            layer_type,
        )

    def update(self, **kwargs):
        for k, v in kwargs.items():
            if k in dir(self):
                self.__setattr__(k, v)
            else:
                self._pedb.logger.error(f"{k} is not a valid layer attribute")

    @property
    def id(self):
        return self._edb_object.GetLayerId()

    @property
    def fill_material(self):
        """The layer's fill material."""
        return self._edb_object.GetFillMaterial(True)

    @fill_material.setter
    def fill_material(self, value):
        self._edb_object.SetFillMaterial(value)

    @property
    def _stackup_layer_mapping(self):
        return {
            "SignalLayer": self._edb.cell.layer_type.SignalLayer,
            "DielectricLayer": self._edb.cell.layer_type.DielectricLayer,
        }

    @property
    def _doc_layer_mapping(self):
        return {
            "ConductingLayer": self._edb.cell.layer_type.ConductingLayer,
            "AirlinesLayer": self._edb.cell.layer_type.AirlinesLayer,
            "ErrorsLayer": self._edb.cell.layer_type.ErrorsLayer,
            "SymbolLayer": self._edb.cell.layer_type.SymbolLayer,
            "MeasureLayer": self._edb.cell.layer_type.MeasureLayer,
            "AssemblyLayer": self._edb.cell.layer_type.AssemblyLayer,
            "SilkscreenLayer": self._edb.cell.layer_type.SilkscreenLayer,
            "SolderMaskLayer": self._edb.cell.layer_type.SolderMaskLayer,
            "SolderPasteLayer": self._edb.cell.layer_type.SolderPasteLayer,
            "GlueLayer": self._edb.cell.layer_type.GlueLayer,
            "WirebondLayer": self._edb.cell.layer_type.WirebondLayer,
            "UserLayer": self._edb.cell.layer_type.UserLayer,
            "SIwaveHFSSSolverRegions": self._edb.cell.layer_type.SIwaveHFSSSolverRegions,
            "PostprocessingLayer": self._edb.cell.layer_type.PostprocessingLayer,
            "OutlineLayer": self._edb.cell.layer_type.OutlineLayer,
            "LayerTypesCount": self._edb.cell.layer_type.LayerTypesCount,
            "UndefinedLayerType": self._edb.cell.layer_type.UndefinedLayerType,
        }

    @property
    def _layer_type_mapping(self):
        mapping = {}
        mapping.update(self._stackup_layer_mapping)
        mapping.update(self._doc_layer_mapping)
        return mapping

    @property
    def _layer_name_mapping(self):
        return {
            "signal": "SignalLayer",
            "dielectric": "DielectricLayer",
            "conducting": "ConductingLayer",
            "airlines": "AirlinesLayer",
            "errors": "ErrorsLayer",
            "symbol": "SymbolLayer",
            "measure": "MeasureLayer",
            "assembly": "AssemblyLayer",
            "silkscreen": "SilkscreenLayer",
            "soldermask": "SolderMaskLayer",
            "solderpaste": "SolderPasteLayer",
            "glue": "GlueLayer",
            "wirebound": "WirebondLayer",
            "user": "UserLayer",
            "siwavehfsssolverregions": "SIwaveHFSSSolverRegions",
            "postprocessing": "PostprocessingLayer",
            "outline": "OutlineLayer",
            "layertypescount": "LayerTypesCount",
            "undefined": "UndefinedLayerType",
        }

    @property
    def _layer_name_mapping_reversed(self):
        return {j: i for i, j in self._layer_name_mapping.items()}

    @property
    def _edb(self):
        return self._pedb.edb_api

    @property
    def _edb_layer(self):
        return self._edb_object

    @property
    def is_stackup_layer(self):
        """Determine whether this layer is a stackup layer.

        Returns
        -------
        bool
            True if this layer is a stackup layer, False otherwise.
        """
        return self._edb_layer.IsStackupLayer()

    @property
    def is_via_layer(self):
        """Determine whether this layer is a via layer.

        Returns
        -------
        bool
            True if this layer is a via layer, False otherwise.
        """
        return self._edb_layer.IsViaLayer()

    @property
    def color(self):
        """Color of the layer.

        Returns
        -------
        tuple
            RGB.
        """
        layer_color = self._edb_layer.GetColor()
        return layer_color.Item1, layer_color.Item2, layer_color.Item3

    @color.setter
    def color(self, rgb):
        layer_clone = self._edb_layer
        layer_clone.SetColor(*rgb)
        self._pedb.stackup._set_layout_stackup(layer_clone, "change_attribute")
        self._color = rgb

    @property
    def transparency(self):
        """Retrieve transparency of the layer.

        Returns
        -------
        int
            An integer between 0 and 100 with 0 being fully opaque and 100 being fully transparent.
        """
        return self._edb_layer.GetTransparency()

    @transparency.setter
    def transparency(self, trans):
        layer_clone = self._edb_layer
        layer_clone.SetTransparency(trans)
        self._pedb.stackup._set_layout_stackup(layer_clone, "change_attribute")

    @property
    def name(self):
        """Retrieve name of the layer.

        Returns
        -------
        str
        """
        return self._edb_layer.GetName()

    @name.setter
    def name(self, name):
        layer_clone = self._edb_layer
        old_name = layer_clone.GetName()
        layer_clone.SetName(name)
        self._pedb.stackup._set_layout_stackup(layer_clone, "change_name", self._name)
        self._name = name
        if self.type == "signal":
            for padstack_def in list(self._pedb.padstacks.definitions.values()):
                padstack_def._update_layer_names(old_name=old_name, updated_name=name)

    @property
    def type(self):
        """Retrieve type of the layer."""
        return self._layer_name_mapping_reversed[self._edb_layer.GetLayerType().ToString()]

    @type.setter
    def type(self, value):
        value = self._layer_name_mapping[value]
        layer_clone = self._edb_layer
        layer_clone.SetLayerType(self._layer_type_mapping[value])
        self._type = value
        self._pedb.stackup._set_layout_stackup(layer_clone, "change_attribute")


class StackupLayerEdbClass(LayerEdbClass):
    def __init__(self, pedb, edb_object=None, name="", layer_type="signal", **kwargs):
        super().__init__(pedb, edb_object, name=name, layer_type=layer_type, **kwargs)
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

    def _create(self, layer_type):
        layer_type_edb_name = self._layer_name_mapping[layer_type]
        layer_type = self._layer_type_mapping[layer_type_edb_name]
        self._edb_object = self._pedb.edb_api.cell._cell.StackupLayer(
            self._name,
            layer_type,
            self._pedb.edb_value(0),
            self._pedb.edb_value(0),
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
        self._lower_elevation = self._edb_layer.GetLowerElevation()
        return self._lower_elevation

    @lower_elevation.setter
    def lower_elevation(self, value):
        if self._pedb.stackup.mode == "Overlapping":
            layer_clone = self._edb_layer
            layer_clone.SetLowerElevation(self._pedb.stackup._edb_value(value))
            self._pedb.stackup._set_layout_stackup(layer_clone, "change_attribute")

    @property
    def upper_elevation(self):
        """Upper elevation.

        Returns
        -------
        float
            Upper elevation.
        """
        self._upper_elevation = self._edb_layer.GetUpperElevation()
        return self._upper_elevation

    @property
    def is_negative(self):
        """Determine whether this layer is a negative layer.

        Returns
        -------
        bool
            True if this layer is a negative layer, False otherwise.
        """
        return self._edb_layer.GetNegative()

    @is_negative.setter
    def is_negative(self, value):
        layer_clone = self._edb_layer
        layer_clone.SetNegative(value)
        self._pedb.stackup._set_layout_stackup(layer_clone, "change_attribute")

    @property
    def material(self):
        """Get/Set the material loss_tangent.

        Returns
        -------
        float
        """
        return self._edb_layer.GetMaterial()

    @material.setter
    def material(self, name):
        layer_clone = self._edb_layer
        layer_clone.SetMaterial(name)
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
            self._dielectric_fill = self._edb_layer.GetFillMaterial()
            return self._dielectric_fill
        else:
            return

    @dielectric_fill.setter
    def dielectric_fill(self, name):
        name = name.lower()
        if self.type == "signal":
            layer_clone = self._edb_layer
            layer_clone.SetFillMaterial(name)
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
        if not self.is_stackup_layer:  # pragma: no cover
            return
        self._thickness = self._edb_layer.GetThicknessValue().ToDouble()
        return self._thickness

    @thickness.setter
    def thickness(self, value):
        if not self.is_stackup_layer:  # pragma: no cover
            return
        layer_clone = self._edb_layer
        layer_clone.SetThickness(self._pedb.stackup._edb_value(value))
        self._pedb.stackup._set_layout_stackup(layer_clone, "change_attribute")
        self._thickness = value

    @property
    def etch_factor(self):
        """Retrieve etch factor of this layer.

        Returns
        -------
        float
        """
        self._etch_factor = self._edb_layer.GetEtchFactor().ToDouble()
        return self._etch_factor

    @etch_factor.setter
    def etch_factor(self, value):
        if not self.is_stackup_layer:  # pragma: no cover
            return
        if not value:
            layer_clone = self._edb_layer
            layer_clone.SetEtchFactorEnabled(False)
        else:
            layer_clone = self._edb_layer
            layer_clone.SetEtchFactorEnabled(True)
            layer_clone.SetEtchFactor(self._pedb.stackup._edb_value(value))
        self._pedb.stackup._set_layout_stackup(layer_clone, "change_attribute")
        self._etch_factor = value

    @property
    def roughness_enabled(self):
        """Determine whether roughness is enabled on this layer.

        Returns
        -------
        bool
        """
        if not self.is_stackup_layer:  # pragma: no cover
            return
        self._roughness_enabled = self._edb_layer.IsRoughnessEnabled()
        return self._roughness_enabled

    @roughness_enabled.setter
    def roughness_enabled(self, set_enable):
        if not self.is_stackup_layer:  # pragma: no cover
            return
        self._roughness_enabled = set_enable
        if set_enable:
            layer_clone = self._edb_layer
            layer_clone.SetRoughnessEnabled(True)
            self._pedb.stackup._set_layout_stackup(layer_clone, "change_attribute")
            self.assign_roughness_model()
        else:
            layer_clone = self._edb_layer
            layer_clone.SetRoughnessEnabled(False)
            self._pedb.stackup._set_layout_stackup(layer_clone, "change_attribute")

    @property
    def top_hallhuray_nodule_radius(self):
        """Retrieve huray model nodule radius on top of the conductor."""
        top_roughness_model = self.get_roughness_model("top")
        if top_roughness_model:
            self._top_hallhuray_nodule_radius = top_roughness_model.NoduleRadius.ToDouble()
        return self._top_hallhuray_nodule_radius

    @top_hallhuray_nodule_radius.setter
    def top_hallhuray_nodule_radius(self, value):
        self._top_hallhuray_nodule_radius = value

    @property
    def top_hallhuray_surface_ratio(self):
        """Retrieve huray model surface ratio on top of the conductor."""
        top_roughness_model = self.get_roughness_model("top")
        if top_roughness_model:
            self._top_hallhuray_surface_ratio = top_roughness_model.SurfaceRatio.ToDouble()
        return self._top_hallhuray_surface_ratio

    @top_hallhuray_surface_ratio.setter
    def top_hallhuray_surface_ratio(self, value):
        self._top_hallhuray_surface_ratio = value

    @property
    def bottom_hallhuray_nodule_radius(self):
        """Retrieve huray model nodule radius on bottom of the conductor."""
        bottom_roughness_model = self.get_roughness_model("bottom")
        if bottom_roughness_model:
            self._bottom_hallhuray_nodule_radius = bottom_roughness_model.NoduleRadius.ToDouble()
        return self._bottom_hallhuray_nodule_radius

    @bottom_hallhuray_nodule_radius.setter
    def bottom_hallhuray_nodule_radius(self, value):
        self._bottom_hallhuray_nodule_radius = value

    @property
    def bottom_hallhuray_surface_ratio(self):
        """Retrieve huray model surface ratio on bottom of the conductor."""
        bottom_roughness_model = self.get_roughness_model("bottom")
        if bottom_roughness_model:
            self._bottom_hallhuray_surface_ratio = bottom_roughness_model.SurfaceRatio.ToDouble()
        return self._bottom_hallhuray_surface_ratio

    @bottom_hallhuray_surface_ratio.setter
    def bottom_hallhuray_surface_ratio(self, value):
        self._bottom_hallhuray_surface_ratio = value

    @property
    def side_hallhuray_nodule_radius(self):
        """Retrieve huray model nodule radius on sides of the conductor."""
        side_roughness_model = self.get_roughness_model("side")
        if side_roughness_model:
            self._side_hallhuray_nodule_radius = side_roughness_model.NoduleRadius.ToDouble()
        return self._side_hallhuray_nodule_radius

    @side_hallhuray_nodule_radius.setter
    def side_hallhuray_nodule_radius(self, value):
        self._side_hallhuray_nodule_radius = value

    @property
    def side_hallhuray_surface_ratio(self):
        """Retrieve huray model surface ratio on sides of the conductor."""
        side_roughness_model = self.get_roughness_model("side")
        if side_roughness_model:
            self._side_hallhuray_surface_ratio = side_roughness_model.SurfaceRatio.ToDouble()
        return self._side_hallhuray_surface_ratio

    @side_hallhuray_surface_ratio.setter
    def side_hallhuray_surface_ratio(self, value):
        self._side_hallhuray_surface_ratio = value

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
            return self._edb_layer.GetRoughnessModel(self._pedb.edb_api.Cell.RoughnessModel.Region.Top)
        elif surface == "bottom":
            return self._edb_layer.GetRoughnessModel(self._pedb.edb_api.Cell.RoughnessModel.Region.Bottom)
        elif surface == "side":
            return self._edb_layer.GetRoughnessModel(self._pedb.edb_api.Cell.RoughnessModel.Region.Side)

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
        if not self.is_stackup_layer:  # pragma: no cover
            return

        radius = self._pedb.stackup._edb_value(huray_radius)
        self._hurray_nodule_radius = huray_radius
        surface_ratio = self._pedb.stackup._edb_value(huray_surface_ratio)
        self._hurray_surface_ratio = huray_surface_ratio
        groisse_roughness = self._pedb.stackup._edb_value(groisse_roughness)
        regions = []
        if apply_on_surface == "all":
            self._side_roughness = "all"
            regions = [
                self._pedb.edb_api.Cell.RoughnessModel.Region.Top,
                self._pedb.edb_api.Cell.RoughnessModel.Region.Side,
                self._pedb.edb_api.Cell.RoughnessModel.Region.Bottom,
            ]
        elif apply_on_surface == "top":
            self._side_roughness = "top"
            regions = [self._pedb.edb_api.Cell.RoughnessModel.Region.Top]
        elif apply_on_surface == "bottom":
            self._side_roughness = "bottom"
            regions = [self._pedb.edb_api.Cell.RoughnessModel.Region.Bottom]
        elif apply_on_surface == "side":
            self._side_roughness = "side"
            regions = [self._pedb.edb_api.Cell.RoughnessModel.Region.Side]

        layer_clone = self._edb_layer
        layer_clone.SetRoughnessEnabled(True)
        for r in regions:
            if model_type == "huray":
                model = self._pedb.edb_api.Cell.HurrayRoughnessModel(radius, surface_ratio)
            else:
                model = self._pedb.edb_api.Cell.GroisseRoughnessModel(groisse_roughness)
            layer_clone.SetRoughnessModel(r, model)
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
