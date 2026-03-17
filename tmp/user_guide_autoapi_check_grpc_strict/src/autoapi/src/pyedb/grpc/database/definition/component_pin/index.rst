src.pyedb.grpc.database.definition.component_pin
================================================

.. py:module:: src.pyedb.grpc.database.definition.component_pin


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.definition.component_pin.ComponentPin


Module Contents
---------------

.. py:class:: ComponentPin(core)

   Class managing :class:`ComponentPin <ansys.edb.core.definition.component_pin.ComponentPin>`.


   .. py:attribute:: core


   .. py:method:: create(component_def, name) -> ansys.edb.core.definition.component_pin.ComponentPin
      :classmethod:


      Create a component pin.

      Parameters
      ----------
      component_def : :class:`ComponentDef <pyedb.grpc.database.definition.component_def.ComponentDef>`
          Component definition object.
      name : str
          Name of the component pin.

      Returns
      -------
      :class:`ComponentPin <pyedb.grpc.database.definition.component_pin.ComponentPin>`
          The created component pin object.



   .. py:property:: is_null
      :type: bool



   .. py:property:: name
      :type: str



