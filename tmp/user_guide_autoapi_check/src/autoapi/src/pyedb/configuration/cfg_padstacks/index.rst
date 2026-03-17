src.pyedb.configuration.cfg_padstacks
=====================================

.. py:module:: src.pyedb.configuration.cfg_padstacks


Classes
-------

.. autoapisummary::

   src.pyedb.configuration.cfg_padstacks.CfgBase
   src.pyedb.configuration.cfg_padstacks.CfgBackdrillParameters
   src.pyedb.configuration.cfg_padstacks.CfgPadstackInstance
   src.pyedb.configuration.cfg_padstacks.CfgPadstackDefinition
   src.pyedb.configuration.cfg_padstacks.CfgPadstacks


Module Contents
---------------

.. py:class:: CfgBase(/, **data: Any)

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


   .. py:attribute:: model_config

      Configuration for the model, should be a dictionary conforming to [`ConfigDict`][pydantic.config.ConfigDict].



.. py:class:: CfgBackdrillParameters(/, **data: Any)

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


   .. py:class:: DrillParametersByLayer(/, **data: Any)

      Bases: :py:obj:`CfgBase`


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


      .. py:attribute:: drill_to_layer
         :type:  str


      .. py:attribute:: diameter
         :type:  str



   .. py:class:: DrillParametersByLayerWithStub(/, **data: Any)

      Bases: :py:obj:`DrillParametersByLayer`


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


      .. py:attribute:: stub_length
         :type:  Union[str, None]



   .. py:class:: DrillParameters(/, **data: Any)

      Bases: :py:obj:`CfgBase`


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


      .. py:attribute:: drill_depth
         :type:  str


      .. py:attribute:: diameter
         :type:  str



   .. py:attribute:: from_top
      :type:  CfgBackdrillParameters.DrillParameters | CfgBackdrillParameters.DrillParametersByLayer | CfgBackdrillParameters.DrillParametersByLayerWithStub | None
      :value: None



   .. py:attribute:: from_bottom
      :type:  CfgBackdrillParameters.DrillParameters | CfgBackdrillParameters.DrillParametersByLayer | CfgBackdrillParameters.DrillParametersByLayerWithStub | None
      :value: None



   .. py:method:: add_backdrill_to_layer(drill_to_layer, diameter, stub_length=None, drill_from_bottom=True)


.. py:class:: CfgPadstackInstance(/, **data: Any)

   Bases: :py:obj:`CfgBase`


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
      :type:  str
      :value: None



   .. py:attribute:: eid
      :type:  int | None
      :value: None



   .. py:attribute:: backdrill_parameters
      :type:  CfgBackdrillParameters | None


   .. py:attribute:: is_pin
      :type:  bool
      :value: None



   .. py:attribute:: net_name
      :type:  str | None
      :value: None



   .. py:attribute:: layer_range
      :type:  list[str] | None
      :value: None



   .. py:attribute:: definition
      :type:  str | None
      :value: None



   .. py:attribute:: position
      :type:  list[str | float] | None
      :value: None



   .. py:attribute:: rotation
      :type:  str | None
      :value: None



   .. py:attribute:: hole_override_enabled
      :type:  bool | None
      :value: None



   .. py:attribute:: hole_override_diameter
      :type:  str | float | None
      :value: None



   .. py:attribute:: solder_ball_layer
      :type:  str | None
      :value: None



   .. py:method:: create(**kwargs)
      :classmethod:



.. py:class:: CfgPadstackDefinition(/, **data: Any)

   Bases: :py:obj:`CfgBase`


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
      :type:  str


   .. py:attribute:: hole_plating_thickness
      :type:  str | float | None
      :value: None



   .. py:attribute:: material
      :type:  str | None
      :value: None



   .. py:attribute:: hole_range
      :type:  str | None
      :value: None



   .. py:attribute:: pad_parameters
      :type:  dict | None
      :value: None



   .. py:attribute:: hole_parameters
      :type:  dict | None
      :value: None



   .. py:attribute:: solder_ball_parameters
      :type:  dict | None
      :value: None



   .. py:method:: create(**kwargs)
      :classmethod:



.. py:class:: CfgPadstacks(/, **data: Any)

   Bases: :py:obj:`CfgBase`


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


   .. py:attribute:: definitions
      :type:  list[CfgPadstackDefinition] | None
      :value: []



   .. py:attribute:: instances
      :type:  list[CfgPadstackInstance] | None
      :value: []



   .. py:method:: create(**kwargs)
      :classmethod:



   .. py:method:: clean()


   .. py:method:: add_padstack_definition(**kwargs)


   .. py:method:: add_padstack_instance(**kwargs)


