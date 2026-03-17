src.pyedb.dotnet.database.definition.definition_obj
===================================================

.. py:module:: src.pyedb.dotnet.database.definition.definition_obj


Attributes
----------

.. autoapisummary::

   src.pyedb.dotnet.database.definition.definition_obj.PositiveFloat
   src.pyedb.dotnet.database.definition.definition_obj.ATTRIBUTES
   src.pyedb.dotnet.database.definition.definition_obj.DC_ATTRIBUTES
   src.pyedb.dotnet.database.definition.definition_obj.PERMEABILITY_DEFAULT_VALUE


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.definition.definition_obj.DefinitionObj
   src.pyedb.dotnet.database.definition.definition_obj.MaterialProperties
   src.pyedb.dotnet.database.definition.definition_obj.DeprecatedMaterial
   src.pyedb.dotnet.database.definition.definition_obj.MaterialDef


Module Contents
---------------

.. py:data:: PositiveFloat

.. py:data:: ATTRIBUTES
   :value: ['conductivity', 'dielectric_loss_tangent', 'magnetic_loss_tangent', 'mass_density',...


.. py:data:: DC_ATTRIBUTES
   :value: ['dielectric_model_frequency', 'loss_tangent_at_frequency', 'permittivity_at_frequency',...


.. py:data:: PERMEABILITY_DEFAULT_VALUE
   :value: 1


.. py:class:: DefinitionObj(pedb, edb_object)

   Bases: :py:obj:`pyedb.dotnet.database.utilities.obj_base.ObjBase`


   Base class for definition objects.


   .. py:property:: definition_obj_type


.. py:class:: MaterialProperties(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Store material properties.


   .. py:attribute:: conductivity
      :type:  Optional[PositiveFloat]
      :value: 0.0



   .. py:attribute:: dielectric_loss_tangent
      :type:  Optional[PositiveFloat]
      :value: 0.0



   .. py:attribute:: magnetic_loss_tangent
      :type:  Optional[PositiveFloat]
      :value: 0.0



   .. py:attribute:: mass_density
      :type:  Optional[PositiveFloat]
      :value: 0.0



   .. py:attribute:: permittivity
      :type:  Optional[PositiveFloat]
      :value: 0.0



   .. py:attribute:: permeability
      :type:  Optional[PositiveFloat]
      :value: 0.0



   .. py:attribute:: poisson_ratio
      :type:  Optional[PositiveFloat]
      :value: 0.0



   .. py:attribute:: specific_heat
      :type:  Optional[PositiveFloat]
      :value: 0.0



   .. py:attribute:: thermal_conductivity
      :type:  Optional[PositiveFloat]
      :value: 0.0



   .. py:attribute:: youngs_modulus
      :type:  Optional[PositiveFloat]
      :value: 0.0



   .. py:attribute:: thermal_expansion_coefficient
      :type:  Optional[PositiveFloat]
      :value: 0.0



   .. py:attribute:: dc_conductivity
      :type:  Optional[PositiveFloat]
      :value: 0.0



   .. py:attribute:: dc_permittivity
      :type:  Optional[PositiveFloat]
      :value: 0.0



   .. py:attribute:: dielectric_model_frequency
      :type:  Optional[PositiveFloat]
      :value: 0.0



   .. py:attribute:: loss_tangent_at_frequency
      :type:  Optional[PositiveFloat]
      :value: 0.0



   .. py:attribute:: permittivity_at_frequency
      :type:  Optional[PositiveFloat]
      :value: 0.0



.. py:class:: DeprecatedMaterial

   Manage EDB methods for material property management.


   .. py:property:: dc_model

      Material dielectric model.

      .. deprecated:: 0.70.0
         Use ``dielectric_material_model`` instead.



   .. py:property:: loss_tangent

      Get material loss tangent.



   .. py:property:: dc_conductivity

      Get material dielectric conductivity.



   .. py:property:: dc_permittivity

      Get material dielectric relative permittivity



   .. py:property:: dielectric_model_frequency

      Get material frequency in GHz.



   .. py:property:: loss_tangent_at_frequency

      Get material loss tangeat at frequency.



   .. py:property:: permittivity_at_frequency

      Get material relative permittivity at frequency.



   .. py:method:: to_dict()

      Convert material into dictionary.



   .. py:method:: update(input_dict: dict)


   .. py:method:: set_thermal_modifier(property_name: str, basic_quadratic_temperature_reference: float = 21, basic_quadratic_c1: float = 0.1, basic_quadratic_c2: float = 0.1, advanced_quadratic_lower_limit: float = -270, advanced_quadratic_upper_limit: float = 1001, advanced_quadratic_auto_calculate: bool = False, advanced_quadratic_lower_constant: float = 1.1, advanced_quadratic_upper_constant: float = 1.1)

      Sets the material property thermal modifier of a given material property.

      Parameters
      ----------
      property_name : str
          Name of the property to modify.
      basic_quadratic_temperature_reference : float, optional
          The TempRef value in the quadratic model.
      basic_quadratic_c1 : float, optional
          The C1 value in the quadratic model.
      basic_quadratic_c2 : float, optional
          The C2 value in the quadratic model.
      advanced_quadratic_lower_limit : float, optional
          The lower temperature limit where the quadratic model is valid.
      advanced_quadratic_upper_limit : float, optional
          The upper temperature limit where the quadratic model is valid.
      advanced_quadratic_auto_calculate : bool, optional
           The flag indicating whether or the LowerConstantThermalModifierVal and UpperConstantThermalModifierVal
           values should be auto calculated.
      advanced_quadratic_lower_constant : float, optional
          The constant thermal modifier value for temperatures lower than LowerConstantThermalModifierVal.
      advanced_quadratic_upper_constant : float, optional
          The constant thermal modifier value for temperatures greater than UpperConstantThermalModifierVal.

      Returns
      -------




.. py:class:: MaterialDef(edb, material_def)

   Bases: :py:obj:`DefinitionObj`, :py:obj:`DeprecatedMaterial`


   Class for material definition.


   .. py:attribute:: property_id


   .. py:attribute:: material_property_id_mapping


   .. py:method:: create(pedb, name: str) -> MaterialDef
      :classmethod:


      Creates a material definition into the database with given name.



   .. py:property:: dielectric_material_model

      dielectric material model. Set None to remove the existing model.



   .. py:method:: set_djordjecvic_sarkar_model(dc_conductivity: float | None = 1e-12, dc_relative_permittivity: float | None = 5, frequency: float | None = 1000000000.0, loss_tangent_at_frequency: float | None = 0.02, relative_permittivity_at_frequency: float | None = 4, use_dc_relative_permittivity: bool | None = False) -> pyedb.dotnet.database.definition.dielectric_material_model.DjordjecvicSarkarModel

      Sets the dielectric material model to Djordjecvic-Sarkar model. The returned model is read-only, any change
      on it will not be reflected on the database.

      Parameters
      ----------
      dc_conductivity : float, optional
          DC conductivity, by default 1e-12
      dc_relative_permittivity : float, optional
          DC relative permittivity, by default 5
      frequency : float, optional
          Frequency in Hz, by default 1e9
      loss_tangent_at_frequency : float, optional
          Loss tangent at frequency, by default 0.02
      relative_permittivity_at_frequency : float, optional
          Relative permittivity at frequency, by default 4
      use_dc_relative_permittivity : bool, optional
          Whether to use DC relative permittivity, by default False



   .. py:property:: conductivity

      Get material conductivity.



   .. py:property:: permittivity

      Get material permittivity.



   .. py:property:: permeability

      Get material permeability.



   .. py:property:: dielectric_loss_tangent

      Get material loss tangent.



   .. py:property:: magnetic_loss_tangent

      Get material magnetic loss tangent.



   .. py:property:: thermal_conductivity

      Get material thermal conductivity.



   .. py:property:: mass_density

      Get material mass density.



   .. py:property:: youngs_modulus

      Get material youngs modulus.



   .. py:property:: specific_heat

      Get material specific heat.



   .. py:property:: poisson_ratio

      Get material poisson ratio.



   .. py:property:: thermal_expansion_coefficient

      Get material thermal coefficient.



