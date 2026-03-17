src.pyedb.dotnet.database.materials
===================================

.. py:module:: src.pyedb.dotnet.database.materials


Attributes
----------

.. autoapisummary::

   src.pyedb.dotnet.database.materials.logger
   src.pyedb.dotnet.database.materials.PositiveFloat


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.materials.Materials


Functions
---------

.. autoapisummary::

   src.pyedb.dotnet.database.materials.get_line_float_value


Module Contents
---------------

.. py:data:: logger

.. py:data:: PositiveFloat

.. py:function:: get_line_float_value(line)

   Retrieve the float value expected in the line of an AMAT file.

   The associated string is expected to follow one of the following cases:
   - simple('permittivity', 12.)
   - permittivity='12'.


.. py:class:: Materials(edb: pyedb.Edb)

   Bases: :py:obj:`object`


   Manages EDB methods for material management accessible from `Edb.materials` property.


   .. py:attribute:: default_conductor_property_values


   .. py:attribute:: default_dielectric_property_values


   .. py:property:: syslib

      Get the project sys library.



   .. py:property:: materials

      Get materials.



   .. py:method:: add_material(name: str, **kwargs)

      Add a new material.

      Parameters
      ----------
      name : str
          Material name.

      Returns
      -------
      :class:`pyedb.dotnet.database.materials.Material`



   .. py:method:: add_conductor_material(name, conductivity=58000000, **kwargs)

      Add a new conductor material.

      Parameters
      ----------
      name : str
          Name of the new material.
      conductivity : str, float, int, optional
          Conductivity of the new material.

      Returns
      -------
      :class:`pyedb.dotnet.database.materials.Material`




   .. py:method:: add_dielectric_material(name, permittivity, dielectric_loss_tangent, **kwargs)

      Add a new dielectric material in library.

      Parameters
      ----------
      name : str
          Name of the new material.
      permittivity : str, float, int, optional
          Permittivity of the new material.
      dielectric_loss_tangent : str, float, int, optional
          Dielectric loss tangent of the new material.

      Returns
      -------
      :class:`pyedb.dotnet.database.materials.Material`



   .. py:method:: add_djordjevic_sarkar_dielectric(name: str, permittivity_at_frequency: int | float, loss_tangent_at_frequency: int | float, dielectric_model_frequency: int | float, dc_conductivity: int | float | None = None, dc_permittivity: int | float | None = None, **kwargs) -> pyedb.dotnet.database.definition.definition_obj.MaterialDef

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
          DC conductivity for the material.
      dc_permittivity : str, float, int, optional
          DC relative permittivity for the material.

      Returns
      -------
      :class:`pyedb.dotnet.database.materials.Material`



   .. py:method:: add_djordjevicsarkar_dielectric(name, permittivity_at_frequency, loss_tangent_at_frequency, dielectric_model_frequency, dc_conductivity=None, dc_permittivity=None, **kwargs)

      Add a dielectric using the Djordjevic-Sarkar model.

      .. deprecated:: 0.7.0
          This method name contains a typo and is deprecated.
          Use :func:`add_djordjevic_sarkar_dielectric` instead.



   .. py:method:: add_debye_material(name, permittivity_low, permittivity_high, loss_tangent_low, loss_tangent_high, lower_freqency, higher_frequency, **kwargs)

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
      :class:`pyedb.dotnet.database.materials.Material`



   .. py:method:: add_multipole_debye_material(name, frequencies, permittivities, loss_tangents, **kwargs)

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
      :class:`pyedb.dotnet.database.materials.Material`

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> freq = [0, 2, 3, 4, 5, 6]
      >>> rel_perm = [1e9, 1.1e9, 1.2e9, 1.3e9, 1.5e9, 1.6e9]
      >>> loss_tan = [0.025, 0.026, 0.027, 0.028, 0.029, 0.030]
      >>> diel = edb.materials.add_multipole_debye_material("My_MP_Debye", freq, rel_perm, loss_tan)



   .. py:method:: duplicate(material_name, new_material_name)

      Duplicate a material from the database.

      Parameters
      ----------
      material_name : str
          Name of the existing material.
      new_material_name : str
          Name of the new duplicated material.

      Returns
      -------
      :class:`pyedb.dotnet.database.materials.Material`



   .. py:method:: delete_material(material_name)

      Remove a material from the database.



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



   .. py:method:: load_amat(amat_file)

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



   .. py:method:: read_materials(amat_file)

      Read materials from an AMAT file.

      Parameters
      ----------
      amat_file : str
          Full path to the AMAT file to read.

      Returns
      -------
      dict
          {material name: dict of material properties}.



   .. py:method:: read_syslib_material(material_name)

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



