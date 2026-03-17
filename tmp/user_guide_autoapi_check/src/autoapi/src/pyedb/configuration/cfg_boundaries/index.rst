src.pyedb.configuration.cfg_boundaries
======================================

.. py:module:: src.pyedb.configuration.cfg_boundaries


Classes
-------

.. autoapisummary::

   src.pyedb.configuration.cfg_boundaries.CfgBase
   src.pyedb.configuration.cfg_boundaries.CfgBoundaries


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



.. py:class:: CfgBoundaries(/, **data: Any)

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


   .. py:class:: PaddingData(/, **data: Any)

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


      .. py:attribute:: size
         :type:  Union[float, str]


      .. py:attribute:: is_multiple
         :type:  bool



   .. py:attribute:: use_open_region
      :type:  Optional[bool]
      :value: None



   .. py:attribute:: open_region_type
      :type:  Optional[str]
      :value: None



   .. py:attribute:: is_pml_visible
      :type:  Optional[bool]
      :value: None



   .. py:attribute:: operating_freq
      :type:  Optional[Any]
      :value: None



   .. py:attribute:: radiation_level
      :type:  Optional[float]
      :value: None



   .. py:attribute:: dielectric_extent_type
      :type:  Optional[str]
      :value: None



   .. py:attribute:: dielectric_base_polygon
      :type:  Optional[str]
      :value: None



   .. py:attribute:: dielectric_extent_size
      :type:  Optional[CfgBoundaries.PaddingData]
      :value: None



   .. py:attribute:: honor_user_dielectric
      :type:  bool
      :value: None



   .. py:attribute:: extent_type
      :type:  Optional[str]
      :value: None



   .. py:attribute:: base_polygon
      :type:  Optional[str]
      :value: None



   .. py:attribute:: truncate_air_box_at_ground
      :type:  Optional[bool]
      :value: None



   .. py:attribute:: air_box_horizontal_extent
      :type:  Optional[CfgBoundaries.PaddingData]
      :value: None



   .. py:attribute:: air_box_positive_vertical_extent
      :type:  Optional[CfgBoundaries.PaddingData]
      :value: None



   .. py:attribute:: air_box_negative_vertical_extent
      :type:  Optional[CfgBoundaries.PaddingData]
      :value: None



   .. py:attribute:: sync_air_box_vertical_extent
      :type:  Optional[bool]
      :value: None



   .. py:method:: create(**kwargs)
      :classmethod:



