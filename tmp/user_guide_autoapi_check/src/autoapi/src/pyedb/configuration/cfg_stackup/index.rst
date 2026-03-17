src.pyedb.configuration.cfg_stackup
===================================

.. py:module:: src.pyedb.configuration.cfg_stackup


Classes
-------

.. autoapisummary::

   src.pyedb.configuration.cfg_stackup.CfgMaterialPropertyThermalModifier
   src.pyedb.configuration.cfg_stackup.MaterialProperties
   src.pyedb.configuration.cfg_stackup.CfgMaterial
   src.pyedb.configuration.cfg_stackup.RoughnessSideModel
   src.pyedb.configuration.cfg_stackup.RoughnessModel
   src.pyedb.configuration.cfg_stackup.EtchingModel
   src.pyedb.configuration.cfg_stackup.CfgLayer
   src.pyedb.configuration.cfg_stackup.CfgStackup


Module Contents
---------------

.. py:class:: CfgMaterialPropertyThermalModifier(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   !!! abstract "Usage Documentation"
       [Models](../concepts/models.md)

   A base class for creating Pydantic models.

   Attributes:
       __class_vars__: The names of the class variables defined on the model.
       __private_attributes__: Metadata about the private attributes of the model.
       __signature__: The synthesized `__init__` [`Signature`][inspect.Signature] of the model.

       __pydantic_complete__: Whether model building is completed, or if there are still undefined fields.
       __pydantic_core_schema__: The core schema of the model.
       __pydantic_custom_init__: Whether the model has a custom `__init__` function.
       __pydantic_decorators__: Metadata containing the decorators defined on the model.
           This replaces `Model.__validators__` and `Model.__root_validators__` from Pydantic V1.
       __pydantic_generic_metadata__: Metadata for generic models; contains data used for a similar purpose to
           __args__, __origin__, __parameters__ in typing-module generics. May eventually be replaced by these.
       __pydantic_parent_namespace__: Parent namespace of the model, used for automatic rebuilding of models.
       __pydantic_post_init__: The name of the post-init method for the model, if defined.
       __pydantic_root_model__: Whether the model is a [`RootModel`][pydantic.root_model.RootModel].
       __pydantic_serializer__: The `pydantic-core` `SchemaSerializer` used to dump instances of the model.
       __pydantic_validator__: The `pydantic-core` `SchemaValidator` used to validate instances of the model.

       __pydantic_fields__: A dictionary of field names and their corresponding [`FieldInfo`][pydantic.fields.FieldInfo] objects.
       __pydantic_computed_fields__: A dictionary of computed field names and their corresponding [`ComputedFieldInfo`][pydantic.fields.ComputedFieldInfo] objects.

       __pydantic_extra__: A dictionary containing extra values, if [`extra`][pydantic.config.ConfigDict.extra]
           is set to `'allow'`.
       __pydantic_fields_set__: The names of fields explicitly set during instantiation.
       __pydantic_private__: Values of private attributes set on the model instance.


   .. py:attribute:: property_name
      :type:  str


   .. py:attribute:: basic_quadratic_c1
      :type:  float
      :value: 0



   .. py:attribute:: basic_quadratic_c2
      :type:  float
      :value: 0



   .. py:attribute:: basic_quadratic_temperature_reference
      :type:  float
      :value: 22



   .. py:attribute:: advanced_quadratic_lower_limit
      :type:  float
      :value: -273.15



   .. py:attribute:: advanced_quadratic_upper_limit
      :type:  float
      :value: 1000



   .. py:attribute:: advanced_quadratic_auto_calculate
      :type:  bool
      :value: True



   .. py:attribute:: advanced_quadratic_lower_constant
      :type:  float
      :value: 1



   .. py:attribute:: advanced_quadratic_upper_constant
      :type:  float
      :value: 1



.. py:class:: MaterialProperties(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Store material properties.


   .. py:attribute:: conductivity
      :type:  Optional[Union[str, float]]
      :value: None



   .. py:attribute:: dielectric_loss_tangent
      :type:  Optional[Union[str, float]]
      :value: None



   .. py:attribute:: magnetic_loss_tangent
      :type:  Optional[Union[str, float]]
      :value: None



   .. py:attribute:: mass_density
      :type:  Optional[Union[str, float]]
      :value: None



   .. py:attribute:: permittivity
      :type:  Optional[Union[str, float]]
      :value: None



   .. py:attribute:: permeability
      :type:  Optional[Union[str, float]]
      :value: None



   .. py:attribute:: poisson_ratio
      :type:  Optional[Union[str, float]]
      :value: None



   .. py:attribute:: specific_heat
      :type:  Optional[Union[str, float]]
      :value: None



   .. py:attribute:: thermal_conductivity
      :type:  Optional[Union[str, float]]
      :value: None



   .. py:attribute:: youngs_modulus
      :type:  Optional[Union[str, float]]
      :value: None



   .. py:attribute:: thermal_expansion_coefficient
      :type:  Optional[Union[str, float]]
      :value: None



   .. py:attribute:: dc_conductivity
      :type:  Optional[Union[str, float]]
      :value: None



   .. py:attribute:: dc_permittivity
      :type:  Optional[Union[str, float]]
      :value: None



   .. py:attribute:: dielectric_model_frequency
      :type:  Optional[Union[str, float]]
      :value: None



   .. py:attribute:: loss_tangent_at_frequency
      :type:  Optional[Union[str, float]]
      :value: None



   .. py:attribute:: permittivity_at_frequency
      :type:  Optional[Union[str, float]]
      :value: None



.. py:class:: CfgMaterial(/, **data: Any)

   Bases: :py:obj:`MaterialProperties`


   Store material properties.


   .. py:attribute:: name
      :type:  Optional[str]
      :value: None



   .. py:attribute:: thermal_modifiers
      :type:  Optional[list[CfgMaterialPropertyThermalModifier]]
      :value: None



.. py:class:: RoughnessSideModel(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   !!! abstract "Usage Documentation"
       [Models](../concepts/models.md)

   A base class for creating Pydantic models.

   Attributes:
       __class_vars__: The names of the class variables defined on the model.
       __private_attributes__: Metadata about the private attributes of the model.
       __signature__: The synthesized `__init__` [`Signature`][inspect.Signature] of the model.

       __pydantic_complete__: Whether model building is completed, or if there are still undefined fields.
       __pydantic_core_schema__: The core schema of the model.
       __pydantic_custom_init__: Whether the model has a custom `__init__` function.
       __pydantic_decorators__: Metadata containing the decorators defined on the model.
           This replaces `Model.__validators__` and `Model.__root_validators__` from Pydantic V1.
       __pydantic_generic_metadata__: Metadata for generic models; contains data used for a similar purpose to
           __args__, __origin__, __parameters__ in typing-module generics. May eventually be replaced by these.
       __pydantic_parent_namespace__: Parent namespace of the model, used for automatic rebuilding of models.
       __pydantic_post_init__: The name of the post-init method for the model, if defined.
       __pydantic_root_model__: Whether the model is a [`RootModel`][pydantic.root_model.RootModel].
       __pydantic_serializer__: The `pydantic-core` `SchemaSerializer` used to dump instances of the model.
       __pydantic_validator__: The `pydantic-core` `SchemaValidator` used to validate instances of the model.

       __pydantic_fields__: A dictionary of field names and their corresponding [`FieldInfo`][pydantic.fields.FieldInfo] objects.
       __pydantic_computed_fields__: A dictionary of computed field names and their corresponding [`ComputedFieldInfo`][pydantic.fields.ComputedFieldInfo] objects.

       __pydantic_extra__: A dictionary containing extra values, if [`extra`][pydantic.config.ConfigDict.extra]
           is set to `'allow'`.
       __pydantic_fields_set__: The names of fields explicitly set during instantiation.
       __pydantic_private__: Values of private attributes set on the model instance.


   .. py:attribute:: model
      :type:  Optional[str]
      :value: None



   .. py:attribute:: nodule_radius
      :type:  Optional[str]
      :value: None



   .. py:attribute:: surface_ratio
      :type:  Optional[str]
      :value: None



   .. py:attribute:: roughness
      :type:  Optional[str]
      :value: None



.. py:class:: RoughnessModel(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   !!! abstract "Usage Documentation"
       [Models](../concepts/models.md)

   A base class for creating Pydantic models.

   Attributes:
       __class_vars__: The names of the class variables defined on the model.
       __private_attributes__: Metadata about the private attributes of the model.
       __signature__: The synthesized `__init__` [`Signature`][inspect.Signature] of the model.

       __pydantic_complete__: Whether model building is completed, or if there are still undefined fields.
       __pydantic_core_schema__: The core schema of the model.
       __pydantic_custom_init__: Whether the model has a custom `__init__` function.
       __pydantic_decorators__: Metadata containing the decorators defined on the model.
           This replaces `Model.__validators__` and `Model.__root_validators__` from Pydantic V1.
       __pydantic_generic_metadata__: Metadata for generic models; contains data used for a similar purpose to
           __args__, __origin__, __parameters__ in typing-module generics. May eventually be replaced by these.
       __pydantic_parent_namespace__: Parent namespace of the model, used for automatic rebuilding of models.
       __pydantic_post_init__: The name of the post-init method for the model, if defined.
       __pydantic_root_model__: Whether the model is a [`RootModel`][pydantic.root_model.RootModel].
       __pydantic_serializer__: The `pydantic-core` `SchemaSerializer` used to dump instances of the model.
       __pydantic_validator__: The `pydantic-core` `SchemaValidator` used to validate instances of the model.

       __pydantic_fields__: A dictionary of field names and their corresponding [`FieldInfo`][pydantic.fields.FieldInfo] objects.
       __pydantic_computed_fields__: A dictionary of computed field names and their corresponding [`ComputedFieldInfo`][pydantic.fields.ComputedFieldInfo] objects.

       __pydantic_extra__: A dictionary containing extra values, if [`extra`][pydantic.config.ConfigDict.extra]
           is set to `'allow'`.
       __pydantic_fields_set__: The names of fields explicitly set during instantiation.
       __pydantic_private__: Values of private attributes set on the model instance.


   .. py:attribute:: enabled
      :type:  Optional[bool]
      :value: False



   .. py:attribute:: top
      :type:  Optional[RoughnessSideModel]
      :value: None



   .. py:attribute:: bottom
      :type:  Optional[RoughnessSideModel]
      :value: None



   .. py:attribute:: side
      :type:  Optional[RoughnessSideModel]
      :value: None



.. py:class:: EtchingModel(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   !!! abstract "Usage Documentation"
       [Models](../concepts/models.md)

   A base class for creating Pydantic models.

   Attributes:
       __class_vars__: The names of the class variables defined on the model.
       __private_attributes__: Metadata about the private attributes of the model.
       __signature__: The synthesized `__init__` [`Signature`][inspect.Signature] of the model.

       __pydantic_complete__: Whether model building is completed, or if there are still undefined fields.
       __pydantic_core_schema__: The core schema of the model.
       __pydantic_custom_init__: Whether the model has a custom `__init__` function.
       __pydantic_decorators__: Metadata containing the decorators defined on the model.
           This replaces `Model.__validators__` and `Model.__root_validators__` from Pydantic V1.
       __pydantic_generic_metadata__: Metadata for generic models; contains data used for a similar purpose to
           __args__, __origin__, __parameters__ in typing-module generics. May eventually be replaced by these.
       __pydantic_parent_namespace__: Parent namespace of the model, used for automatic rebuilding of models.
       __pydantic_post_init__: The name of the post-init method for the model, if defined.
       __pydantic_root_model__: Whether the model is a [`RootModel`][pydantic.root_model.RootModel].
       __pydantic_serializer__: The `pydantic-core` `SchemaSerializer` used to dump instances of the model.
       __pydantic_validator__: The `pydantic-core` `SchemaValidator` used to validate instances of the model.

       __pydantic_fields__: A dictionary of field names and their corresponding [`FieldInfo`][pydantic.fields.FieldInfo] objects.
       __pydantic_computed_fields__: A dictionary of computed field names and their corresponding [`ComputedFieldInfo`][pydantic.fields.ComputedFieldInfo] objects.

       __pydantic_extra__: A dictionary containing extra values, if [`extra`][pydantic.config.ConfigDict.extra]
           is set to `'allow'`.
       __pydantic_fields_set__: The names of fields explicitly set during instantiation.
       __pydantic_private__: Values of private attributes set on the model instance.


   .. py:attribute:: factor
      :type:  Optional[Union[float, str]]
      :value: 0.5



   .. py:attribute:: etch_power_ground_nets
      :type:  Optional[bool]
      :value: False



   .. py:attribute:: enabled
      :type:  Optional[bool]
      :value: False



.. py:class:: CfgLayer(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   !!! abstract "Usage Documentation"
       [Models](../concepts/models.md)

   A base class for creating Pydantic models.

   Attributes:
       __class_vars__: The names of the class variables defined on the model.
       __private_attributes__: Metadata about the private attributes of the model.
       __signature__: The synthesized `__init__` [`Signature`][inspect.Signature] of the model.

       __pydantic_complete__: Whether model building is completed, or if there are still undefined fields.
       __pydantic_core_schema__: The core schema of the model.
       __pydantic_custom_init__: Whether the model has a custom `__init__` function.
       __pydantic_decorators__: Metadata containing the decorators defined on the model.
           This replaces `Model.__validators__` and `Model.__root_validators__` from Pydantic V1.
       __pydantic_generic_metadata__: Metadata for generic models; contains data used for a similar purpose to
           __args__, __origin__, __parameters__ in typing-module generics. May eventually be replaced by these.
       __pydantic_parent_namespace__: Parent namespace of the model, used for automatic rebuilding of models.
       __pydantic_post_init__: The name of the post-init method for the model, if defined.
       __pydantic_root_model__: Whether the model is a [`RootModel`][pydantic.root_model.RootModel].
       __pydantic_serializer__: The `pydantic-core` `SchemaSerializer` used to dump instances of the model.
       __pydantic_validator__: The `pydantic-core` `SchemaValidator` used to validate instances of the model.

       __pydantic_fields__: A dictionary of field names and their corresponding [`FieldInfo`][pydantic.fields.FieldInfo] objects.
       __pydantic_computed_fields__: A dictionary of computed field names and their corresponding [`ComputedFieldInfo`][pydantic.fields.ComputedFieldInfo] objects.

       __pydantic_extra__: A dictionary containing extra values, if [`extra`][pydantic.config.ConfigDict.extra]
           is set to `'allow'`.
       __pydantic_fields_set__: The names of fields explicitly set during instantiation.
       __pydantic_private__: Values of private attributes set on the model instance.


   .. py:attribute:: name
      :type:  Optional[str]
      :value: None



   .. py:attribute:: type
      :type:  Optional[str]
      :value: None



   .. py:attribute:: material
      :type:  Optional[str]
      :value: None



   .. py:attribute:: fill_material
      :type:  Optional[str]
      :value: None



   .. py:attribute:: thickness
      :type:  Optional[Union[float, str]]
      :value: None



   .. py:attribute:: roughness
      :type:  Optional[RoughnessModel]
      :value: None



   .. py:attribute:: etching
      :type:  Optional[EtchingModel]
      :value: None



.. py:class:: CfgStackup(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   !!! abstract "Usage Documentation"
       [Models](../concepts/models.md)

   A base class for creating Pydantic models.

   Attributes:
       __class_vars__: The names of the class variables defined on the model.
       __private_attributes__: Metadata about the private attributes of the model.
       __signature__: The synthesized `__init__` [`Signature`][inspect.Signature] of the model.

       __pydantic_complete__: Whether model building is completed, or if there are still undefined fields.
       __pydantic_core_schema__: The core schema of the model.
       __pydantic_custom_init__: Whether the model has a custom `__init__` function.
       __pydantic_decorators__: Metadata containing the decorators defined on the model.
           This replaces `Model.__validators__` and `Model.__root_validators__` from Pydantic V1.
       __pydantic_generic_metadata__: Metadata for generic models; contains data used for a similar purpose to
           __args__, __origin__, __parameters__ in typing-module generics. May eventually be replaced by these.
       __pydantic_parent_namespace__: Parent namespace of the model, used for automatic rebuilding of models.
       __pydantic_post_init__: The name of the post-init method for the model, if defined.
       __pydantic_root_model__: Whether the model is a [`RootModel`][pydantic.root_model.RootModel].
       __pydantic_serializer__: The `pydantic-core` `SchemaSerializer` used to dump instances of the model.
       __pydantic_validator__: The `pydantic-core` `SchemaValidator` used to validate instances of the model.

       __pydantic_fields__: A dictionary of field names and their corresponding [`FieldInfo`][pydantic.fields.FieldInfo] objects.
       __pydantic_computed_fields__: A dictionary of computed field names and their corresponding [`ComputedFieldInfo`][pydantic.fields.ComputedFieldInfo] objects.

       __pydantic_extra__: A dictionary containing extra values, if [`extra`][pydantic.config.ConfigDict.extra]
           is set to `'allow'`.
       __pydantic_fields_set__: The names of fields explicitly set during instantiation.
       __pydantic_private__: Values of private attributes set on the model instance.


   .. py:attribute:: materials
      :type:  List[CfgMaterial]
      :value: None



   .. py:attribute:: layers
      :type:  List[CfgLayer]
      :value: None



   .. py:method:: add_material(name, **kwargs)


   .. py:method:: add_layer_at_bottom(name, **kwargs)


