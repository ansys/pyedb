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

from pydantic import BaseModel, Field


# ---------- Materials ----------
class XmlMaterialProperty(BaseModel):
    value: float | None = Field(None, alias="Double")

    model_config = dict(populate_by_name=True)


class XmlMaterial(BaseModel):
    name: str = Field(alias="@Name")
    permittivity: XmlMaterialProperty | None = Field(None, alias="Permittivity")
    permeability: XmlMaterialProperty | None = Field(None, alias="Permeability")
    conductivity: XmlMaterialProperty | None = Field(None, alias="Conductivity")
    dielectric_loss_tangent: XmlMaterialProperty | None = Field(None, alias="DielectricLossTangent")
    magnetic_loss_tangent: XmlMaterialProperty | None = Field(None, alias="MagneticLossTangent")

    model_config = dict(populate_by_name=True)


# ---------- Layers ----------
class XmlLayer(BaseModel):
    color: str | None = Field(None, alias="@Color")
    gdsii_via: bool | None = Field(None, alias="@GDSIIVia")
    material: str | None = Field(None, alias="@Material")
    fill_material: str | None = Field(None, alias="@FillMaterial")
    name: str = Field(alias="@Name")
    negative: bool | None = Field(None, alias="@Negative")
    thickness: float | str | None = Field(None, alias="@Thickness")
    type: str | None = Field(None, alias="@Type")

    model_config = dict(populate_by_name=True)


# ---------- Stackup ----------
class XmlMaterials(BaseModel):
    material: list[XmlMaterial] | None = Field(list(), alias="Material")

    model_config = dict(populate_by_name=True)

    def add_material(self, name, **kwargs) -> XmlMaterial:
        mat = XmlMaterial(
            **{"name": name},
            **{p_name: XmlMaterialProperty(**{"value": p_value}) for p_name, p_value in kwargs.items()},
        )
        self.material.append(mat)
        return mat


class XmlLayers(BaseModel):
    length_unit: str | None = Field(None, alias="@LengthUnit")
    layer: list[XmlLayer] | None = Field(list(), alias="Layer")

    model_config = dict(populate_by_name=True)

    def add_layer(self, **kwargs) -> XmlLayer:
        layer = XmlLayer(**kwargs)
        self.layer.append(layer)
        return layer


class XmlStackup(BaseModel):
    materials: XmlMaterials | None = Field(None, alias="Materials")
    layers: XmlLayers | None = Field(None, alias="Layers")
    schema_version: str | None = Field(None, alias="schemaVersion")

    model_config = dict(populate_by_name=True)

    def add_materials(self):
        self.materials = XmlMaterials()
        return self.materials

    def add_layers(self):
        self.layers = XmlLayers(length_unit="mm")
        return self.layers

    def import_from_cfg_stackup(self, cfg_stackup):
        self.add_materials()
        for mat in cfg_stackup.materials:
            mat_kwargs = {}
            for key, value in mat.model_dump(exclude_none=True).items():
                if key != "name":
                    mat_kwargs[key] = value
            self.materials.add_material(name=mat.name, **mat_kwargs)

        self.add_layers()
        for layer in cfg_stackup.layers:
            layer_kwargs = {}
            for key, value in layer.model_dump(exclude_none=True).items():
                layer_kwargs[key] = value
            self.layers.add_layer(**layer_kwargs)

    def to_dict(self):
        layer_data = []
        unit = self.layers.length_unit
        for lay in self.layers.layer:
            layer_dict = lay.model_dump(exclude_none=True)

            if not str(lay.thickness)[-1].isalpha():
                layer_dict["thickness"] = f"{layer_dict['thickness']}{unit}"
            layer_dict["type"] = "signal" if layer_dict["type"].lower() == "conductor" else layer_dict["type"].lower()
            layer_data.append(layer_dict)

        material_data = []
        for mat in self.materials.material:
            _mat = {}
            for key, value in mat.model_dump(exclude_none=True).items():
                if isinstance(getattr(mat, key), XmlMaterialProperty):
                    value = getattr(mat, key).value
                _mat[key] = value
            material_data.append(_mat)

        return {
            "layers": layer_data,
            "materials": material_data,
        }
