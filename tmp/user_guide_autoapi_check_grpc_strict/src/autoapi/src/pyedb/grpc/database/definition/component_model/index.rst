src.pyedb.grpc.database.definition.component_model
==================================================

.. py:module:: src.pyedb.grpc.database.definition.component_model


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.definition.component_model.ComponentModel
   src.pyedb.grpc.database.definition.component_model.NPortComponentModel


Module Contents
---------------

.. py:class:: ComponentModel(core)

   Class managing :class:`ComponentModel <pyedb.grpc.database.definition.component_model.ComponentModel>`.


   .. py:attribute:: core


   .. py:property:: is_null
      :type: bool


      Check if the component model is null.

      Returns
      -------
      bool
          True if the component model is null, False otherwise.




   .. py:property:: name
      :type: str


      Get the name of the component model.

      Returns
      -------
      str
          The name of the component model.




   .. py:property:: reference_file
      :type: str


      Get the reference file of the component model.

      Returns
      -------
      str
          The reference file of the component model.




.. py:class:: NPortComponentModel(core)

   Class managing :class:`NPortComponentModel <pyedb.grpc.database.definition.component_model.ComponentModel>`


   .. py:attribute:: core


   .. py:method:: create(name: str) -> NPortComponentModel
      :classmethod:


      Create an N-Port component model.

      Parameters
      ----------
      name : str
          Name of the N-Port component model.

      Returns
      -------
      NPortComponentModel
          The created N-Port component model object.




   .. py:method:: find_by_id(component_definition, id: int) -> Union[None, NPortComponentModel]
      :classmethod:


      Find an N-Port component model by IO count in a given component definition.

      Parameters
      ----------
      component_definition : :class:`ComponentDef <pyedb.grpc.database.definition.component_def.ComponentDef>`
          Component definition to search for the N-Port component model.
      id : int
          IO count of the N-Port component model.
      Returns
      -------
      NPortComponentModel
          N-Port component model that is found, ``None`` otherwise.



   .. py:method:: find_by_name(component_definition, name: str) -> Union[None, NPortComponentModel]
      :classmethod:


      Find an N-Port component model by name in a given component definition.

      Parameters
      ----------
      component_definition : :class:`ComponentDef <pyedb.grpc.database.definition.component_def.ComponentDef>`
          Component definition to search for the N-Port component model.
      name : str
          Name of the N-Port component model.

      Returns
      -------
      NPortComponentModel
          N-Port component model that is found, ``None`` otherwise.



   .. py:property:: is_null
      :type: bool


      Check if the N-Port component model is null.

      Returns
      -------
      bool
          True if the N-Port component model is null, False otherwise.




   .. py:property:: name
      :type: str


      Get the name of the N-Port component model.

      Returns
      -------
      str
          The name of the N-Port component model.




   .. py:property:: reference_file
      :type: str


      Get the reference file of the N-Port component model.

      Returns
      -------
      str
          The reference file of the N-Port component model.




