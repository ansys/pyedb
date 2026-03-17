src.pyedb.dotnet.database.cell.primitive.bondwire
=================================================

.. py:module:: src.pyedb.dotnet.database.cell.primitive.bondwire


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.cell.primitive.bondwire.Bondwire


Module Contents
---------------

.. py:class:: Bondwire(pedb, edb_object=None, **kwargs)

   Bases: :py:obj:`pyedb.dotnet.database.cell.primitive.primitive.Primitive`


   Class representing a bondwire object.


   .. py:method:: get_material(evaluated=True)

      Get material of the bondwire.

      Parameters
      ----------
      evaluated : bool, optional
          True if an evaluated material name is wanted.

      Returns
      -------
      str
          Material name.



   .. py:method:: set_material(material)

      Set the material of a bondwire.

      Parameters
      ----------
      material : str
          Material name.



   .. py:property:: type

      :class:`BondwireType`: Bondwire-type of a bondwire object.



   .. py:property:: cross_section_type

      :class:`BondwireCrossSectionType`: Bondwire-cross-section-type of a bondwire object.



   .. py:property:: cross_section_height

      :class:`Value <ansys.edb.utility.Value>`: Bondwire-cross-section height of a bondwire object.



   .. py:method:: get_definition_name(evaluated=True)

      Get definition name of a bondwire object.

      Parameters
      ----------
      evaluated : bool, optional
          True if an evaluated (in variable namespace) material name is wanted.

      Returns
      -------
      str
          Bondwire name.



   .. py:method:: set_definition_name(definition_name)

      Set the definition name of a bondwire.

      Parameters
      ----------
      definition_name : str
          Bondwire name to be set.



   .. py:method:: get_trajectory()

      Get trajectory parameters of a bondwire object.

      Returns
      -------
      tuple[
          :class:`Value <ansys.edb.utility.Value>`,
          :class:`Value <ansys.edb.utility.Value>`,
          :class:`Value <ansys.edb.utility.Value>`,
          :class:`Value <ansys.edb.utility.Value>`
      ]

          Returns a tuple of the following format:

          **(x1, y1, x2, y2)**

          **x1** : X value of the start point.

          **y1** : Y value of the start point.

          **x1** : X value of the end point.

          **y1** : Y value of the end point.



   .. py:method:: set_trajectory(x1, y1, x2, y2)

      Set the parameters of the trajectory of a bondwire.

      Parameters
      ----------
      x1 : :class:`Value <ansys.edb.utility.Value>`
          X value of the start point.
      y1 : :class:`Value <ansys.edb.utility.Value>`
          Y value of the start point.
      x2 : :class:`Value <ansys.edb.utility.Value>`
          X value of the end point.
      y2 : :class:`Value <ansys.edb.utility.Value>`
          Y value of the end point.



   .. py:property:: width

      :class:`Value <ansys.edb.utility.Value>`: Width of a bondwire object.



   .. py:method:: set_start_elevation(layer, start_context=None)

      Set the start elevation of a bondwire.

      Parameters
      ----------
      start_context : :class:`CellInstance <ansys.edb.hierarchy.CellInstance>`
          Start cell context of the bondwire. None means top level.
      layer : str or :class:`Layer <ansys.edb.layer.Layer>`
          Start layer of the bondwire.



   .. py:method:: set_end_elevation(layer, end_context=None)

      Set the end elevation of a bondwire.

      Parameters
      ----------
      end_context : :class:`CellInstance <ansys.edb.hierarchy.CellInstance>`
          End cell context of the bondwire. None means top level.
      layer : str or :class:`Layer <ansys.edb.layer.Layer>`
          End layer of the bondwire.



