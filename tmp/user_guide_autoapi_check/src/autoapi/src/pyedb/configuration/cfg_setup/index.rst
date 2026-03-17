src.pyedb.configuration.cfg_setup
=================================

.. py:module:: src.pyedb.configuration.cfg_setup


Classes
-------

.. autoapisummary::

   src.pyedb.configuration.cfg_setup.CfgFrequencies
   src.pyedb.configuration.cfg_setup.CfgSetupDC
   src.pyedb.configuration.cfg_setup.CfgSetupAC
   src.pyedb.configuration.cfg_setup.CfgSIwaveACSetup
   src.pyedb.configuration.cfg_setup.CfgSIwaveDCSetup
   src.pyedb.configuration.cfg_setup.CfgHFSSSetup
   src.pyedb.configuration.cfg_setup.CfgSetups


Module Contents
---------------

.. py:class:: CfgFrequencies(/, **data: Any)

   Bases: :py:obj:`pyedb.configuration.cfg_common.CfgBaseModel`


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


   .. py:attribute:: start
      :type:  float | str
      :value: None



   .. py:attribute:: stop
      :type:  float | str
      :value: None



   .. py:attribute:: increment
      :type:  int | str
      :value: None



   .. py:attribute:: distribution
      :type:  Literal['linear_scale', 'log_scale', 'single', 'linear_count', 'log_count', 'linear scale', 'log scale', 'linear count']
      :value: None



.. py:class:: CfgSetupDC(/, **data: Any)

   Bases: :py:obj:`pyedb.configuration.cfg_common.CfgBaseModel`


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


.. py:class:: CfgSetupAC(/, **data: Any)

   Bases: :py:obj:`CfgSetupDC`


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


   .. py:class:: CfgFrequencySweep(/, **data: Any)

      Bases: :py:obj:`pyedb.configuration.cfg_common.CfgBaseModel`


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


      .. py:attribute:: type
         :type:  Literal['discrete', 'interpolation', 'interpolating']


      .. py:attribute:: frequencies
         :type:  list[CfgFrequencies | str]
         :value: None



      .. py:attribute:: use_q3d_for_dc
         :type:  bool
         :value: None



      .. py:attribute:: compute_dc_point
         :type:  bool
         :value: None



      .. py:attribute:: enforce_causality
         :type:  bool
         :value: False



      .. py:attribute:: enforce_passivity
         :type:  bool
         :value: True



      .. py:attribute:: adv_dc_extrapolation
         :type:  bool
         :value: False



      .. py:attribute:: use_hfss_solver_regions
         :type:  bool
         :value: None



      .. py:attribute:: hfss_solver_region_setup_name
         :type:  str | None
         :value: '<default>'



      .. py:attribute:: hfss_solver_region_sweep_name
         :type:  str | None
         :value: '<default>'



      .. py:method:: add_frequencies(freq: CfgFrequencies)



   .. py:attribute:: freq_sweep
      :type:  list[CfgSetupAC.CfgFrequencySweep] | None
      :value: []



   .. py:method:: add_frequency_sweep(sweep: CfgFrequencySweep)


.. py:class:: CfgSIwaveACSetup(/, **data: Any)

   Bases: :py:obj:`CfgSetupAC`


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


   .. py:attribute:: type
      :type:  str
      :value: 'siwave_ac'



   .. py:attribute:: use_si_settings
      :type:  bool
      :value: None



   .. py:attribute:: si_slider_position
      :type:  int
      :value: None



   .. py:attribute:: pi_slider_position
      :type:  int
      :value: None



.. py:class:: CfgSIwaveDCSetup(/, **data: Any)

   Bases: :py:obj:`CfgSetupDC`


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


   .. py:class:: CfgDCIRSettings(/, **data: Any)

      Bases: :py:obj:`pyedb.configuration.cfg_common.CfgBaseModel`


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


      .. py:attribute:: export_dc_thermal_data
         :type:  bool
         :value: None




   .. py:attribute:: type
      :type:  str
      :value: 'siwave_dc'



   .. py:attribute:: dc_slider_position
      :type:  int | str


   .. py:attribute:: dc_ir_settings
      :type:  CfgSIwaveDCSetup.CfgDCIRSettings | None
      :value: None



.. py:class:: CfgHFSSSetup(/, **data: Any)

   Bases: :py:obj:`CfgSetupAC`


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


   .. py:class:: CfgSingleFrequencyAdaptiveSolution(/, **data: Any)

      Bases: :py:obj:`pyedb.configuration.cfg_common.CfgBaseModel`


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


      .. py:attribute:: adaptive_frequency
         :type:  float | str
         :value: None



      .. py:attribute:: max_passes
         :type:  int
         :value: None



      .. py:attribute:: max_delta
         :type:  float | str
         :value: None




   .. py:class:: CfgBroadbandAdaptiveSolution(/, **data: Any)

      Bases: :py:obj:`pyedb.configuration.cfg_common.CfgBaseModel`


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


      .. py:attribute:: low_frequency
         :type:  float | str
         :value: None



      .. py:attribute:: high_frequency
         :type:  float | str
         :value: None



      .. py:attribute:: max_passes
         :type:  int
         :value: None



      .. py:attribute:: max_delta
         :type:  float | str
         :value: None




   .. py:class:: CfgAutoMeshOperation(/, **data: Any)

      Bases: :py:obj:`pyedb.configuration.cfg_common.CfgBaseModel`


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
         :type:  bool
         :value: False



      .. py:attribute:: trace_ratio_seeding
         :type:  float
         :value: 3



      .. py:attribute:: signal_via_side_number
         :type:  int
         :value: 12



      .. py:attribute:: power_ground_via_side_number
         :type:  int
         :value: 6




   .. py:class:: CfgMultiFrequencyAdaptiveSolution(/, **data: Any)

      Bases: :py:obj:`pyedb.configuration.cfg_common.CfgBaseModel`


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


      .. py:class:: CfgAdaptFrequency(/, **data: Any)

         Bases: :py:obj:`pyedb.configuration.cfg_common.CfgBaseModel`


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


         .. py:attribute:: adaptive_frequency
            :type:  float | str
            :value: None



         .. py:attribute:: max_passes
            :type:  int
            :value: None



         .. py:attribute:: max_delta
            :type:  float | str
            :value: None




      .. py:attribute:: adapt_frequencies
         :type:  list[CfgHFSSSetup.CfgMultiFrequencyAdaptiveSolution.CfgAdaptFrequency]
         :value: None



      .. py:method:: add_adaptive_frequency(frequency: Union[float, str], max_passes: int, max_delta: Union[float, str])



   .. py:class:: CfgLengthMeshOperation(/, **data: Any)

      Bases: :py:obj:`pyedb.configuration.cfg_common.CfgBaseModel`


      Mesh operation export/import payload.


      .. py:attribute:: mesh_operation_type
         :type:  str
         :value: None



      .. py:attribute:: name
         :type:  str
         :value: None



      .. py:attribute:: max_elements
         :type:  int | str | None
         :value: None



      .. py:attribute:: max_length
         :type:  float | str | None
         :value: None



      .. py:attribute:: restrict_length
         :type:  bool | None
         :value: None



      .. py:attribute:: refine_inside
         :type:  bool | None
         :value: None



      .. py:attribute:: nets_layers_list
         :type:  dict[str, list]
         :value: None




   .. py:attribute:: type
      :type:  str
      :value: 'hfss'



   .. py:attribute:: adapt_type
      :type:  Literal['broadband', 'single', 'multi_frequencies']
      :value: None



   .. py:attribute:: single_frequency_adaptive_solution
      :type:  Optional[CfgHFSSSetup.CfgSingleFrequencyAdaptiveSolution]
      :value: None



   .. py:attribute:: broadband_adaptive_solution
      :type:  Optional[CfgHFSSSetup.CfgBroadbandAdaptiveSolution]
      :value: None



   .. py:attribute:: multi_frequency_adaptive_solution
      :type:  Optional[CfgHFSSSetup.CfgMultiFrequencyAdaptiveSolution]
      :value: None



   .. py:attribute:: auto_mesh_operation
      :type:  CfgHFSSSetup.CfgAutoMeshOperation | None


   .. py:attribute:: mesh_operations
      :type:  list[CfgHFSSSetup.CfgLengthMeshOperation] | None
      :value: []



   .. py:method:: add_length_mesh_operation(mesh_op: CfgLengthMeshOperation)


.. py:class:: CfgSetups(/, **data: Any)

   Bases: :py:obj:`pyedb.configuration.cfg_common.CfgBaseModel`


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


   .. py:attribute:: setups
      :type:  List[Union[CfgHFSSSetup, CfgSIwaveACSetup, CfgSIwaveDCSetup]]
      :value: None



   .. py:method:: create(setups: List[dict])
      :classmethod:



   .. py:method:: add_hfss_setup(config: CfgHFSSSetup = None, **kwargs)


   .. py:method:: add_siwave_ac_setup(config: CfgSIwaveACSetup = None, **kwargs)


   .. py:method:: add_siwave_dc_setup(config: CfgSIwaveDCSetup = None, **kwargs)


