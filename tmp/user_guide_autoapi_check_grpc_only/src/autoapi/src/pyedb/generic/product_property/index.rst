src.pyedb.generic.product_property
==================================

.. py:module:: src.pyedb.generic.product_property


Classes
-------

.. autoapisummary::

   src.pyedb.generic.product_property.EMProperties


Module Contents
---------------

.. py:class:: EMProperties(/, **data: Any)

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


   .. py:class:: EMPropertiesInner(/, **data: Any)

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


      .. py:attribute:: general
         :type:  str
         :value: ''



      .. py:attribute:: modeled
         :type:  bool
         :value: True



      .. py:attribute:: union
         :type:  bool
         :value: True



      .. py:attribute:: use_precedence
         :type:  bool
         :value: False



      .. py:attribute:: precedence_value
         :type:  int
         :value: 1



      .. py:attribute:: planar_em
         :type:  str
         :value: ''



      .. py:attribute:: refined
         :type:  bool
         :value: True



      .. py:attribute:: refine_factor
         :type:  int
         :value: 1



      .. py:attribute:: no_edge_mesh
         :type:  bool
         :value: False



      .. py:attribute:: hfss
         :type:  str
         :value: ''



      .. py:attribute:: solve_inside
         :type:  bool
         :value: False



      .. py:attribute:: siwave
         :type:  str
         :value: ''



      .. py:attribute:: dcir_equipotential_region
         :type:  bool
         :value: False




   .. py:attribute:: type
      :type:  str
      :value: 'Mesh'



   .. py:attribute:: data_id
      :type:  str
      :value: 'EM properties1'



   .. py:attribute:: properties
      :type:  EMProperties.EMPropertiesInner


   .. py:method:: from_em_string(em_string: str) -> EMProperties
      :classmethod:


      Parse EM properties string.



   .. py:method:: to_em_string() -> str

      Convert back to EM properties string.



