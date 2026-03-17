src.pyedb.grpc.database.definition.materials
============================================

.. py:module:: src.pyedb.grpc.database.definition.materials


Attributes
----------

.. autoapisummary::

   src.pyedb.grpc.database.definition.materials.logger
   src.pyedb.grpc.database.definition.materials.PositiveFloat
   src.pyedb.grpc.database.definition.materials.ATTRIBUTES
   src.pyedb.grpc.database.definition.materials.DC_ATTRIBUTES
   src.pyedb.grpc.database.definition.materials.PERMEABILITY_DEFAULT_VALUE


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.definition.materials.MaterialProperties
   src.pyedb.grpc.database.definition.materials.Material
   src.pyedb.grpc.database.definition.materials.Materials


Functions
---------

.. autoapisummary::

   src.pyedb.grpc.database.definition.materials.get_line_float_value


Module Contents
---------------

.. py:data:: logger

.. py:data:: PositiveFloat

.. py:data:: ATTRIBUTES
   :value: ['conductivity', 'dielectric_loss_tangent', 'magnetic_loss_tangent', 'mass_density',...


.. py:data:: DC_ATTRIBUTES
   :value: ['dielectric_model_frequency', 'loss_tangent_at_frequency', 'permittivity_at_frequency',...


.. py:data:: PERMEABILITY_DEFAULT_VALUE
   :value: 1


.. py:function:: get_line_float_value(line)

   Retrieve the float value expected in the line of an AMAT file.

   The associated string is expected to follow one of the following cases:
   - simple('permittivity', 12.)
   - permittivity='12'.


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



.. py:class:: Material(edb: pyedb.grpc.edb.Edb, core)

   Manage EDB methods for material property management.


   .. py:attribute:: core


   .. py:property:: name
      :type: str


      Material name.

      Returns
      -------
      str
          Material name.



   .. py:property:: dc_model
      :type: ansys.edb.core.definition.debye_model.DebyeModel | ansys.edb.core.definition.multipole_debye_model.MultipoleDebyeModel | ansys.edb.core.definition.djordjecvic_sarkar_model.DjordjecvicSarkarModel | float


      Dielectric material model.

      Returns the dielectric model object, or ``0.0`` when no dielectric
      model is assigned.



   .. py:property:: dielectric_material_model
      :type: ansys.edb.core.definition.debye_model.DebyeModel | ansys.edb.core.definition.multipole_debye_model.MultipoleDebyeModel | ansys.edb.core.definition.djordjecvic_sarkar_model.DjordjecvicSarkarModel | float


      Material dielectric model.

      Returns the dielectric model object associated with the material, or
      ``0.0`` when no dielectric model is assigned.



   .. py:property:: conductivity
      :type: float


      Get material conductivity.

      Returns
      -------
      float
          Conductivity value.



   .. py:property:: dc_conductivity
      :type: float | str | None


      Material DC conductivity.

      Returns
      -------
      float
          DC conductivity value.




   .. py:property:: dc_permittivity
      :type: float | str | None


      Material DC permittivity.

      Returns
      -------
      float
          DC permittivity value.




   .. py:property:: loss_tangent_at_frequency
      :type: float | str | None


      Material loss tangent at frequency if dielectric model is defined.

      Returns
      -------
      float
          Loss tangent value.




   .. py:property:: dielectric_model_frequency
      :type: float | str | None


      Dielectric model frequency if model is defined.

      Returns
      -------
      float
          Frequency value.




   .. py:property:: permittivity_at_frequency
      :type: float | str | None


      Material permittivity at frequency if model is defined.


      Returns
      -------
      float
          Permittivity value.




   .. py:property:: permittivity
      :type: float | str | None


      Material permittivity.


      Returns
      -------
      float
          Permittivity value.




   .. py:property:: permeability
      :type: float | str | None


      Material permeability.

      Returns
      -------
      float
          Permeability value.




   .. py:property:: loss_tangent
      :type: float | str | None


      Material loss tangent.

      Returns
      -------
      float
          Loss tangent value.




   .. py:property:: dielectric_loss_tangent
      :type: float | str | None


      Material loss tangent.

      Returns
      -------
      float
          Loss tangent value.




   .. py:property:: magnetic_loss_tangent
      :type: float | str | None


      Material magnetic loss tangent.

      Returns
      -------
      float
          Magnetic loss tangent value.



   .. py:property:: thermal_conductivity
      :type: float | str | None


      Material thermal conductivity.

      Returns
      -------
      float
          Thermal conductivity value.




   .. py:property:: mass_density
      :type: float | str | None


      Material mass density.

      Returns
      -------
      float
          Mass density value.




   .. py:property:: youngs_modulus
      :type: float | str | None


      Material young modulus.

      Returns
      -------
      float
          Material young modulus value.




   .. py:property:: specific_heat
      :type: float | str | None


      Material specific heat.

      Returns
      -------
      float
          Material specific heat value.



   .. py:property:: poisson_ratio
      :type: float | str | None


      Material poisson ratio.

      Returns
      -------
      float
          Material poisson ratio value.



   .. py:property:: thermal_expansion_coefficient
      :type: float | str | None


      Material thermal coefficient.

      Returns
      -------
      float
          Material thermal coefficient value.




   .. py:method:: set_debye_model()

      Set Debye model on current material.



   .. py:method:: set_multipole_debye_model()

      Set multi-pole debeye model on current material.



   .. py:method:: set_djordjecvic_sarkar_model()

      Set Djordjecvic-Sarkar model on current material.



   .. py:method:: to_dict()

      Convert material into dictionary.



   .. py:method:: update(input_dict: dict)


.. py:class:: Materials(edb: pyedb.grpc.edb.Edb)

   Bases: :py:obj:`object`


   Manages EDB methods for material management accessible from `Edb.materials` property.


   .. py:attribute:: default_conductor_property_values


   .. py:attribute:: default_dielectric_property_values


   .. py:property:: syslib

      Get the project sys library.

      Returns
      -------
      str
          Syslib path.



   .. py:property:: materials
      :type: dict[str, Material]


      Get materials.

      Returns
      -------
      Dict[str, :class:`Material <pyedb.grpc.database.definition.materials.Material>`]
          Materials dictionary.



   .. py:method:: add_material(name: str, **kwargs) -> Material

      Add a new material.

      Parameters
      ----------
      name : str
          Material name.

      Returns
      -------
      :class:`Material <pyedb.grpc.database.definition.materials.Material>`
          Material object.



   .. py:method:: add_conductor_material(name, conductivity, **kwargs) -> Material

      Add a new conductor material.

      Parameters
      ----------
      name : str
          Name of the new material.
      conductivity : str, float, int
          Conductivity of the new material.

      Returns
      -------
      :class:`Material <pyedb.grpc.database.definition.materials.Material>`
          Material object.




   .. py:method:: add_dielectric_material(name, permittivity, dielectric_loss_tangent, **kwargs) -> Material

      Add a new dielectric material in library.

      Parameters
      ----------
      name : str
          Name of the new material.
      permittivity : str, float, int
          Permittivity of the new material.
      dielectric_loss_tangent : str, float, int
          Dielectric loss tangent of the new material.

      Returns
      -------
      :class:`Material <pyedb.grpc.database.definition.materials.Material>`
          Material object.



   .. py:method:: add_djordjevicsarkar_dielectric(name, permittivity_at_frequency, loss_tangent_at_frequency, dielectric_model_frequency, dc_conductivity=None, dc_permittivity=None, **kwargs) -> Material

      Add a dielectric using the Djordjevic-Sarkar model.

      Parameters
      ----------
      name : str
          Name of the dielectric.
      permittivity_at_frequency : str, float, int
          Relative permittivity of the dielectric.
      loss_tangent_at_frequency : str, float, int
          Loss tangent for the material.
      dielectric_model_frequency : str, float, int
          Test frequency in GHz for the dielectric.
      dc_conductivity : str, float, int, optional
          DC conductivity for the material. If provided, it will be used in the model and the property
          use_dc_relative_conductivity will be set to True.
      dc_permittivity : str, float, int, optional
          DC permittivity for the material. If provided, it will be used in the model and the property
          dc_relative_permittivity will be set.

      Returns
      -------
      :class:`Material <pyedb.grpc.database.definition.materials.Material>`
          Material object.



   .. py:method:: add_debye_material(name, permittivity_low, permittivity_high, loss_tangent_low, loss_tangent_high, lower_freqency, higher_frequency, **kwargs) -> Material

      Add a dielectric with the Debye model.

      Parameters
      ----------
      name : str
          Name of the dielectric.
      permittivity_low : float, int
          Relative permittivity of the dielectric at the frequency specified
          for ``lower_frequency``.
      permittivity_high : float, int
          Relative permittivity of the dielectric at the frequency specified
          for ``higher_frequency``.
      loss_tangent_low : float, int
          Loss tangent for the material at the frequency specified
          for ``lower_frequency``.
      loss_tangent_high : float, int
          Loss tangent for the material at the frequency specified
          for ``higher_frequency``.
      lower_freqency : str, float, int
          Value for the lower frequency.
      higher_frequency : str, float, int
          Value for the higher frequency.

      Returns
      -------
      :class:`Material <pyedb.grpc.database.definition.materials.Material>`
          Material object.



   .. py:method:: add_multipole_debye_material(name, frequencies, permittivities, loss_tangents, **kwargs) -> Material

      Add a dielectric with the Multipole Debye model.

      Parameters
      ----------
      name : str
          Name of the dielectric.
      frequencies : list
          Frequencies in GHz.
      permittivities : list
          Relative permittivities at each frequency.
      loss_tangents : list
          Loss tangents at each frequency.

      Returns
      -------
      :class:`Material <pyedb.grpc.database.definition.materials.Material>`
          Material object.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> freq = [0, 2, 3, 4, 5, 6]
      >>> rel_perm = [1e9, 1.1e9, 1.2e9, 1.3e9, 1.5e9, 1.6e9]
      >>> loss_tan = [0.025, 0.026, 0.027, 0.028, 0.029, 0.030]
      >>> diel = edb.materials.add_multipole_debye_material("My_MP_Debye", freq, rel_perm, loss_tan)



   .. py:method:: duplicate(material_name, new_material_name) -> Material

      Duplicate a material from the database.

      Parameters
      ----------
      material_name : str
          Name of the existing material.
      new_material_name : str
          Name of the new duplicated material.

      Returns
      -------
      :class:`Material <pyedb.grpc.database.definition.materials.Material>`
          Material object.



   .. py:method:: delete_material(material_name)

      .deprecated: pyedb 0.32.0 use `delete` instead.

      Parameters
      ----------
      material_name : str
          Name of the material to delete.




   .. py:method:: delete(material_name) -> bool

      Remove a material from the database.

      Returns
      -------
      bool




   .. py:method:: update_material(material_name, input_dict)

      Update material attributes.



   .. py:method:: load_material(material: dict)

      Load material.



   .. py:method:: material_property_to_id(property_name)

      Convert a material property name to a material property ID.

      Parameters
      ----------
      property_name : str
          Name of the material property.

      Returns
      -------
      Any



   .. py:method:: load_amat(amat_file) -> bool

      Load materials from an AMAT file.

      Parameters
      ----------
      amat_file : str
          Full path to the AMAT file to read and add to the Edb.

      Returns
      -------
      bool



   .. py:method:: iterate_materials_in_amat(amat_file=None)

      Iterate over material description in an AMAT file.

      Parameters
      ----------
      amat_file : str
          Full path to the AMAT file to read.

      Yields
      ------
      dict



   .. py:method:: read_materials(amat_file) -> dict[str, Material]

      Read materials from an AMAT file.

      Parameters
      ----------
      amat_file : str
          Full path to the AMAT file to read.

      Returns
      -------
      dict
          {material name: dict of material properties}.



   .. py:method:: read_syslib_material(material_name) -> dict[str, Material]

      Read a specific material from syslib AMAT file.

      Parameters
      ----------
      material_name : str
          Name of the material.

      Returns
      -------
      dict
          {material name: dict of material properties}.



   .. py:method:: update_materials_from_sys_library(update_all: bool = True, material_name: Union[str, list] = None)

      Update material properties from syslib AMAT file.



