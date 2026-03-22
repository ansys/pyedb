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

"""XML stackup module for handling EDB stackup configurations."""

from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from pyedb.configuration.cfg_data import CfgStackup

SurfaceOption = Literal["all", "top", "bottom", "side"]


class XmlMaterialProperty(BaseModel):
    """Represents a material property value in the XML stackup.

    Parameters
    ----------
    value : float, optional
        Numerical value of the material property. The default is ``None``.
    """

    value: float | None = Field(None, alias="Double")

    model_config = dict(populate_by_name=True)


class XmlMaterial(BaseModel):
    """Represents a material definition in the XML stackup.

    Parameters
    ----------
    name : str
        Name of the material.
    permittivity : XmlMaterialProperty, optional
        Relative permittivity (dielectric constant). The default is ``None``.
    permeability : XmlMaterialProperty, optional
        Relative permeability. The default is ``None``.
    conductivity : XmlMaterialProperty, optional
        Electrical conductivity in S/m. The default is ``None``.
    dielectric_loss_tangent : XmlMaterialProperty, optional
        Dielectric loss tangent. The default is ``None``.
    magnetic_loss_tangent : XmlMaterialProperty, optional
        Magnetic loss tangent. The default is ``None``.
    """

    name: str = Field(alias="@Name")
    permittivity: XmlMaterialProperty | None = Field(None, alias="Permittivity")
    permeability: XmlMaterialProperty | None = Field(None, alias="Permeability")
    conductivity: XmlMaterialProperty | None = Field(None, alias="Conductivity")
    dielectric_loss_tangent: XmlMaterialProperty | None = Field(None, alias="DielectricLossTangent")
    magnetic_loss_tangent: XmlMaterialProperty | None = Field(None, alias="MagneticLossTangent")
    model_config = dict(populate_by_name=True)


class XmlHuraySurfaceRoughness(BaseModel):
    """Represents Huray roughness settings for a conductor surface."""

    nodule_radius: str | int | float | None = Field(None, alias="@NoduleRadius")
    surface_ratio: int | float | None = Field(None, alias="@HallHuraySurfaceRatio")

    model_config = dict(populate_by_name=True)


class XmlGroissSurfaceRoughness(BaseModel):
    """Represents Groiss bottom roughness settings for a conductor surface."""

    roughness: str | None = Field(None, alias="@Roughness")

    model_config = dict(populate_by_name=True)


class XmlLayer(BaseModel):
    """Represents a layer in the XML stackup.

    Parameters
    ----------
    name : str
        Name of the layer.
    color : str, optional
        Color code for layer visualization. The default is ``None``.
    gdsii_via : bool, optional
        Whether the layer is a GDSII via layer. The default is ``None``.
    material : str, optional
        Name of the layer material. The default is ``None``.
    fill_material : str, optional
        Name of the fill material for the layer. The default is ``None``.
    negative : bool, optional
        Whether the layer uses negative artwork. The default is ``None``.
    thickness : float or str, optional
        Layer thickness value with or without units. The default is ``None``.
    type : str, optional
        Layer type (signal, dielectric, conductor, etc.). The default is ``None``.
    """

    color: str | None = Field(None, alias="@Color")
    gdsii_via: bool | None = Field(None, alias="@GDSIIVia")
    material: str | None = Field(None, alias="@Material")
    fill_material: str | None = Field(None, alias="@FillMaterial")
    name: str = Field(alias="@Name")
    negative: bool | None = Field(None, alias="@Negative")
    thickness: float | str | None = Field(None, alias="@Thickness")
    type: str | None = Field(None, alias="@Type")

    huray_surface_roughness: XmlHuraySurfaceRoughness | None = Field(None, alias="HuraySurfaceRoughness")
    huray_bottom_surface_roughness: XmlHuraySurfaceRoughness | None = Field(None, alias="HurayBottomSurfaceRoughness")
    huray_side_surface_roughness: XmlHuraySurfaceRoughness | None = Field(None, alias="HuraySideSurfaceRoughness")

    groiss_surface_roughness: XmlGroissSurfaceRoughness | None = Field(None, alias="GroissSurfaceRoughness")
    groiss_bottom_surface_roughness: XmlGroissSurfaceRoughness | None = Field(
        None, alias="GroissBottomSurfaceRoughness"
    )
    groiss_side_surface_roughness: XmlGroissSurfaceRoughness | None = Field(None, alias="GroissSideSurfaceRoughness")

    model_config = dict(populate_by_name=True)

    def set_huray_surface_roughness(
        self, nodule_radius: int | float | int, surface_ratio=int | float | str, surface: SurfaceOption = "all"
    ) -> XmlHuraySurfaceRoughness:

        if surface == "top":
            self.huray_surface_roughness = XmlHuraySurfaceRoughness(
                nodule_radius=nodule_radius, surface_ratio=surface_ratio
            )
        elif surface == "bottom":
            self.huray_bottom_surface_roughness = XmlHuraySurfaceRoughness(
                nodule_radius=nodule_radius, surface_ratio=surface_ratio
            )
        elif surface == "side":
            self.huray_side_surface_roughness = XmlHuraySurfaceRoughness(
                nodule_radius=nodule_radius, surface_ratio=surface_ratio
            )
        else:
            self.huray_surface_roughness = XmlHuraySurfaceRoughness(
                nodule_radius=nodule_radius, surface_ratio=surface_ratio
            )
            self.huray_bottom_surface_roughness = XmlHuraySurfaceRoughness(
                nodule_radius=nodule_radius, hall_huray_surface_ratio=surface_ratio
            )
            self.huray_side_surface_roughness = XmlHuraySurfaceRoughness(
                nodule_radius=nodule_radius, surface_ratio=surface_ratio
            )

    def set_groisse_surface_roughness(
        self, roughness: int | float | str, surface: SurfaceOption = "all"
    ) -> XmlGroissSurfaceRoughness:
        if surface == "top":
            self.groiss_surface_roughness = XmlGroissSurfaceRoughness(roughness=roughness)
        elif surface == "bottom":
            self.groiss_bottom_surface_roughness = XmlGroissSurfaceRoughness(roughness=roughness)
        elif surface == "side":
            self.groiss_side_surface_roughness = XmlGroissSurfaceRoughness(roughness=roughness)
        else:
            self.groiss_surface_roughness = XmlGroissSurfaceRoughness(roughness=roughness)
            self.groiss_bottom_surface_roughness = XmlGroissSurfaceRoughness(roughness=roughness)
            self.groiss_side_surface_roughness = XmlGroissSurfaceRoughness(roughness=roughness)


class XmlMaterials(BaseModel):
    """Container for material definitions in the XML stackup.

    Parameters
    ----------
    material : list of XmlMaterial, optional
        List of material definitions. The default is an empty list.
    """

    material: list[XmlMaterial] | None = Field(list(), alias="Material")

    model_config = dict(populate_by_name=True)

    def add_material(self, name: str, **kwargs) -> XmlMaterial:
        """Add a material to the stackup.

        Parameters
        ----------
        name : str
            Name of the material.
        **kwargs : float
            Material properties as keyword arguments. Supported properties include
            ``permittivity``, ``permeability``, ``conductivity``,
            ``dielectric_loss_tangent``, and ``magnetic_loss_tangent``.

        Returns
        -------
        XmlMaterial
            The newly created material object.

        Examples
        --------
        >>> from pyedb.xml_parser.xml_stackup import XmlMaterials
        >>> materials = XmlMaterials()
        >>> copper = materials.add_material("copper", conductivity=5.8e7)
        >>> fr4 = materials.add_material("fr4", permittivity=4.5, dielectric_loss_tangent=0.02)
        """
        mat = XmlMaterial(
            **{"name": name},
            **{p_name: XmlMaterialProperty(**{"value": p_value}) for p_name, p_value in kwargs.items()},
        )
        self.material.append(mat)
        return mat


class XmlLayers(BaseModel):
    """Container for layer definitions in the XML stackup.

    Parameters
    ----------
    length_unit : str, optional
        Unit for layer thickness measurements. The default is ``None``.
    layer : list of XmlLayer, optional
        List of layer definitions. The default is an empty list.
    """

    length_unit: str | None = Field(None, alias="@LengthUnit")
    layer: list[XmlLayer] | None = Field(list(), alias="Layer")

    model_config = dict(populate_by_name=True)

    def add_layer(self, **kwargs) -> XmlLayer:
        """Add a layer to the stackup.

        Parameters
        ----------
        **kwargs : Any
            Layer properties as keyword arguments. Supported properties include
            ``name``, ``type``, ``thickness``, ``material``, ``fill_material``,
            ``color``, ``negative``, and ``gdsii_via``.

        Returns
        -------
        XmlLayer
            The newly created layer object.

        Examples
        --------
        >>> from pyedb.xml_parser.xml_stackup import XmlLayers
        >>> layers = XmlLayers(length_unit="mm")
        >>> signal = layers.add_layer(name="TOP", type="signal", thickness=0.035, material="copper")
        >>> dielectric = layers.add_layer(name="Core", type="dielectric", thickness=0.2, material="fr4")
        """
        layer = XmlLayer(**kwargs)
        self.layer.append(layer)
        return layer


class XmlStackup(BaseModel):
    """Main stackup configuration for EDB XML files.

    This class represents the complete stackup definition including materials
    and layers for a PCB design.

    Parameters
    ----------
    materials : XmlMaterials, optional
        Container for material definitions. The default is ``None``.
    layers : XmlLayers, optional
        Container for layer definitions. The default is ``None``.
    schema_version : str, optional
        Version of the XML schema. The default is ``None``.

    Examples
    --------
    >>> from pyedb.xml_parser.xml_stackup import XmlStackup
    >>> stackup = XmlStackup()
    >>> materials = stackup.add_materials()
    >>> layers = stackup.add_layers()
    """

    materials: XmlMaterials | None = Field(None, alias="Materials")
    layers: XmlLayers | None = Field(None, alias="Layers")
    schema_version: str | None = Field(None, alias="schemaVersion")

    model_config = dict(populate_by_name=True)

    def add_materials(self) -> XmlMaterials:
        """Add a materials container to the stackup.

        Returns
        -------
        XmlMaterials
            The newly created materials container object.

        Examples
        --------
        >>> from pyedb.xml_parser.xml_stackup import XmlStackup
        >>> stackup = XmlStackup()
        >>> materials = stackup.add_materials()
        >>> materials.add_material("copper", conductivity=5.8e7)
        """
        # noinspection PyArgumentList
        self.materials = XmlMaterials()
        return self.materials

    def add_layers(self) -> XmlLayers:
        """Add a layers container to the stackup.

        Returns
        -------
        XmlLayers
            The newly created layers container object with default length unit of "mm".

        Examples
        --------
        >>> from pyedb.xml_parser.xml_stackup import XmlStackup
        >>> stackup = XmlStackup()
        >>> layers = stackup.add_layers()
        >>> layers.add_layer(name="TOP", type="signal", thickness=0.035, material="copper")
        """
        self.layers = XmlLayers(length_unit="mm")
        return self.layers

    def import_from_cfg_stackup(self, cfg_stackup: "CfgStackup") -> None:
        """Import stackup configuration from a CFG stackup object.

        Parameters
        ----------
        cfg_stackup : CfgStackup
            Configuration stackup object to import from. This should contain
            materials and layers attributes that can be converted to XML format.

        Examples
        --------
        >>> from pyedb.xml_parser.xml_stackup import XmlStackup
        >>> from pyedb.configuration.cfg_data import CfgStackup
        >>> stackup = XmlStackup()
        >>> cfg_data = CfgStackup(materials=[...], layers=[...])
        >>> stackup.import_from_cfg_stackup(cfg_data)
        """
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

    def to_dict(self) -> dict:
        """Convert the stackup configuration to a dictionary.

        Returns
        -------
        dict
            Dictionary containing 'layers' and 'materials' keys with their respective
            data as lists of dictionaries. Layer thicknesses are normalized to include
            units, and layer types are converted to lowercase format.

        Examples
        --------
        >>> from pyedb.xml_parser.xml_stackup import XmlStackup
        >>> stackup = XmlStackup()
        >>> stackup.add_materials()
        >>> stackup.materials.add_material("copper", conductivity=5.8e7)
        >>> stackup.add_layers()
        >>> stackup.layers.add_layer(name="TOP", type="signal", thickness=0.035, material="copper")
        >>> config = stackup.to_dict()
        >>> print(config["materials"])
        [{'name': 'copper', 'conductivity': 58000000.0}]
        """
        layer_data = []
        unit = self.layers.length_unit
        for lay in self.layers.layer:
            layer_dict = lay.model_dump(exclude_none=True)

            if not str(lay.thickness)[-1].isalpha():
                layer_dict["thickness"] = f"{layer_dict['thickness']}{unit}"
            # Correct type
            layer_dict["type"] = "signal" if layer_dict["type"].lower() == "conductor" else layer_dict["type"].lower()
            # Convert roughness
            huray_top = layer_dict.pop("huray_surface_roughness", None)
            huray_bottom = layer_dict.pop("huray_bottom_surface_roughness", None)
            huray_side = layer_dict.pop("huray_side_surface_roughness", None)
            groiss_top = layer_dict.pop("groiss_surface_roughness", None)
            groiss_bottom = layer_dict.pop("groiss_bottom_surface_roughness", None)
            groiss_side = layer_dict.pop("groiss_side_surface_roughness", None)

            if huray_top or huray_bottom or huray_side or groiss_top or groiss_bottom or groiss_side:
                roughness = {"enabled": True}
                if huray_top:
                    roughness["top"] = huray_top
                if huray_bottom:
                    roughness["bottom"] = huray_bottom
                if huray_side:
                    roughness["side"] = huray_side
                if groiss_top:
                    roughness["top"] = groiss_top
                if groiss_bottom:
                    roughness["bottom"] = groiss_bottom
                if groiss_side:
                    roughness["side"] = groiss_side
                layer_dict["roughness"] = roughness

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
