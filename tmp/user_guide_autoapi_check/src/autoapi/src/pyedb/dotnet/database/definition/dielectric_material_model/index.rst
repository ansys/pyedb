src.pyedb.dotnet.database.definition.dielectric_material_model
==============================================================

.. py:module:: src.pyedb.dotnet.database.definition.dielectric_material_model


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.definition.dielectric_material_model.DielectricMaterialModel
   src.pyedb.dotnet.database.definition.dielectric_material_model.DjordjecvicSarkarModel
   src.pyedb.dotnet.database.definition.dielectric_material_model.DebyeModel
   src.pyedb.dotnet.database.definition.dielectric_material_model.MultipoleDebyeModel


Module Contents
---------------

.. py:class:: DielectricMaterialModel(pedb: pyedb.dotnet.edb.Edb, edb_object)

   Bases: :py:obj:`pyedb.dotnet.database.utilities.obj_base.ObjBase`


   Class for dielectric material model.


.. py:class:: DjordjecvicSarkarModel(pedb: pyedb.dotnet.edb.Edb, edb_object)

   Bases: :py:obj:`DielectricMaterialModel`


   Class for Djordjecvic-Sarkar model.


   .. py:method:: create(pedb) -> DjordjecvicSarkarModel
      :classmethod:


      Constructs a Djordjecvic-Sarkar model with the following default values.
      Frequency: 1GHz. Relative Permitivity: 4. Loss Tangent: 0.02.Use DC relative permitivity: false.
      DC relative permitivity: 5.DC conductivity: 1e-12.



   .. py:property:: dc_conductivity
      :type: float | pyedb.dotnet.database.utilities.value.Value


      DC conductivity.



   .. py:property:: dc_relative_permittivity
      :type: float | pyedb.dotnet.database.utilities.value.Value


      DC relative permittivity.



   .. py:property:: frequency
      :type: float | pyedb.dotnet.database.utilities.value.Value


      Frequency in Hz.



   .. py:property:: loss_tangent_at_frequency
      :type: float | pyedb.dotnet.database.utilities.value.Value


      Loss tangent at frequency.



   .. py:property:: relative_permittivity_at_frequency


   .. py:property:: use_dc_relative_permittivity

      whether the DC relative permittivity nominal value is used



.. py:class:: DebyeModel(pedb: pyedb.dotnet.edb.Edb, edb_object)

   Bases: :py:obj:`DielectricMaterialModel`


   Class for Debye model.


.. py:class:: MultipoleDebyeModel(pedb: pyedb.dotnet.edb.Edb, edb_object)

   Bases: :py:obj:`DielectricMaterialModel`


   Class for multipole Debye model.


