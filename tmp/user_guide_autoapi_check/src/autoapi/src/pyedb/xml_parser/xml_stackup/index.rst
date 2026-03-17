src.pyedb.xml_parser.xml_stackup
================================

.. py:module:: src.pyedb.xml_parser.xml_stackup

.. autoapi-nested-parse::

   XML stackup module for handling EDB stackup configurations.



Classes
-------

.. autoapisummary::

   src.pyedb.xml_parser.xml_stackup.XmlMaterialProperty
   src.pyedb.xml_parser.xml_stackup.XmlMaterial
   src.pyedb.xml_parser.xml_stackup.XmlLayer
   src.pyedb.xml_parser.xml_stackup.XmlMaterials
   src.pyedb.xml_parser.xml_stackup.XmlLayers
   src.pyedb.xml_parser.xml_stackup.XmlStackup


Module Contents
---------------

.. py:class:: XmlMaterialProperty(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Represents a material property value in the XML stackup.

   Parameters
   ----------
   value : float, optional
       Numerical value of the material property. The default is ``None``.


   .. py:attribute:: value
      :type:  float | None
      :value: None



   .. py:attribute:: model_config

      Configuration for the model, should be a dictionary conforming to [`ConfigDict`][pydantic.config.ConfigDict].



.. py:class:: XmlMaterial(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Represents a material definition in the XML stackup.

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


   .. py:attribute:: name
      :type:  str
      :value: None



   .. py:attribute:: permittivity
      :type:  XmlMaterialProperty | None
      :value: None



   .. py:attribute:: permeability
      :type:  XmlMaterialProperty | None
      :value: None



   .. py:attribute:: conductivity
      :type:  XmlMaterialProperty | None
      :value: None



   .. py:attribute:: dielectric_loss_tangent
      :type:  XmlMaterialProperty | None
      :value: None



   .. py:attribute:: magnetic_loss_tangent
      :type:  XmlMaterialProperty | None
      :value: None



   .. py:attribute:: model_config

      Configuration for the model, should be a dictionary conforming to [`ConfigDict`][pydantic.config.ConfigDict].



.. py:class:: XmlLayer(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Represents a layer in the XML stackup.

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


   .. py:attribute:: color
      :type:  str | None
      :value: None



   .. py:attribute:: gdsii_via
      :type:  bool | None
      :value: None



   .. py:attribute:: material
      :type:  str | None
      :value: None



   .. py:attribute:: fill_material
      :type:  str | None
      :value: None



   .. py:attribute:: name
      :type:  str
      :value: None



   .. py:attribute:: negative
      :type:  bool | None
      :value: None



   .. py:attribute:: thickness
      :type:  float | str | None
      :value: None



   .. py:attribute:: type
      :type:  str | None
      :value: None



   .. py:attribute:: model_config

      Configuration for the model, should be a dictionary conforming to [`ConfigDict`][pydantic.config.ConfigDict].



.. py:class:: XmlMaterials(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Container for material definitions in the XML stackup.

   Parameters
   ----------
   material : list of XmlMaterial, optional
       List of material definitions. The default is an empty list.


   .. py:attribute:: material
      :type:  list[XmlMaterial] | None
      :value: None



   .. py:attribute:: model_config

      Configuration for the model, should be a dictionary conforming to [`ConfigDict`][pydantic.config.ConfigDict].



   .. py:method:: add_material(name: str, **kwargs) -> XmlMaterial

      Add a material to the stackup.

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



.. py:class:: XmlLayers(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Container for layer definitions in the XML stackup.

   Parameters
   ----------
   length_unit : str, optional
       Unit for layer thickness measurements. The default is ``None``.
   layer : list of XmlLayer, optional
       List of layer definitions. The default is an empty list.


   .. py:attribute:: length_unit
      :type:  str | None
      :value: None



   .. py:attribute:: layer
      :type:  list[XmlLayer] | None
      :value: None



   .. py:attribute:: model_config

      Configuration for the model, should be a dictionary conforming to [`ConfigDict`][pydantic.config.ConfigDict].



   .. py:method:: add_layer(**kwargs) -> XmlLayer

      Add a layer to the stackup.

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



.. py:class:: XmlStackup(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Main stackup configuration for EDB XML files.

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


   .. py:attribute:: materials
      :type:  XmlMaterials | None
      :value: None



   .. py:attribute:: layers
      :type:  XmlLayers | None
      :value: None



   .. py:attribute:: schema_version
      :type:  str | None
      :value: None



   .. py:attribute:: model_config

      Configuration for the model, should be a dictionary conforming to [`ConfigDict`][pydantic.config.ConfigDict].



   .. py:method:: add_materials() -> XmlMaterials

      Add a materials container to the stackup.

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



   .. py:method:: add_layers() -> XmlLayers

      Add a layers container to the stackup.

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



   .. py:method:: import_from_cfg_stackup(cfg_stackup: pyedb.configuration.cfg_data.CfgStackup) -> None

      Import stackup configuration from a CFG stackup object.

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



   .. py:method:: to_dict() -> dict

      Convert the stackup configuration to a dictionary.

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



