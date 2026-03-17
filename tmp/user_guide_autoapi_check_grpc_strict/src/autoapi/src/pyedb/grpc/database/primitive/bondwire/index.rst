src.pyedb.grpc.database.primitive.bondwire
==========================================

.. py:module:: src.pyedb.grpc.database.primitive.bondwire


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.primitive.bondwire.Bondwire


Module Contents
---------------

.. py:class:: Bondwire(_pedb, core)

   Class representing a bond-wire object.


   .. py:attribute:: core


   .. py:method:: create(layout, definition_name: str, placement_layer: str, start_layer_name: str, start_x: float, start_y: float, end_layer_name: str, end_x: float, end_y: float, net: str, material: str = 'copper', bondwire_type: str = 'jedec4', width=3e-05, start_cell_inst=None, end_cell_inst=None) -> Bondwire
      :classmethod:


      Create a bondwire object.

      Parameters
      ----------
      layout : :class: <Layout `pyedb.grpc.database.layout.layout.Layout`>
          Layout object associated with the bondwire.
      bondwire_type : str, optional
          Type of bondwire. Supported values are `"jedec4"`, `"jedec5"`, and `"apd"`. Default is `"jedec4"`.
      definition_name : str
          Definition name of the bondwire. Default is an empty string.
      placement_layer : str
          Placement layer name of the bondwire.
      width : float, optional
          Width of the bondwire. Default is 30um.
      material : str, optional
          Material of the bondwire. Default is "copper".
      start_layer_name : str, optional
          Start layer name of the bondwire. Default is None.
      start_x : float, optional
          X-coordinate of the start point of the bondwire. Default is 0.0.
      start_y : float, optional
          Y-coordinate of the start point of the bondwire. Default is 0.0.
      end_layer_name : str, optional
          End layer name of the bondwire. Default is None.
      end_x : float, optional
          X-coordinate of the end point of the bondwire. Default is 0.0.
      end_y : float, optional
          Y-coordinate of the end point of the bondwire. Default is 0.0.
      net : :class: <Net `pyedb.grpc.database.net.net.Net`>,
          Net object associated with the bondwire. Default is None.
      start_cell_inst : :class: <Component `pyedb.grpc.database.hierarchy.component
          .Component`>, optional
          Start cell instance context for the bondwire. Default is None.
      end_cell_inst : :class: <Component
          `pyedb.grpc.database.hierarchy.component.Component`>, optional
          End cell instance context for the bondwire. Default is None.


      Returns
      -------
      Bondwire
          The created bondwire object.




   .. py:property:: id


   .. py:property:: edb_uid


   .. py:property:: material

      Bondwire material

      Returns
      -------
      str
          Material name.




   .. py:property:: type

      str: Bondwire-type of a bondwire object. Supported values for setter: `"apd"`, `"jedec4"`, `"jedec5"`,
      `"num_of_type"`



   .. py:property:: cross_section_type

      str: Bondwire-cross-section-type of a bondwire object. Supported values for setter: `"round",
      `"rectangle"`

      Returns
      -------
      str
          cross section type.



   .. py:property:: cross_section_height

      float: Bondwire-cross-section height of a bondwire object.

      Returns
      -------
      float
          Cross section height.



   .. py:property:: width

      :class:`Value <ansys.edb.utility.Value>`: Width of a bondwire object.

      Returns
      -------
      float
          Width value.



   .. py:method:: get_material()

      Get the bondwire material.

      Returns
      -------
      str
          Material name.



   .. py:method:: set_material(material)

      Set the bondwire material.

      Parameters
      ----------
      material : str
          Material name.



   .. py:method:: get_definition_name() -> str

      Get the bondwire definition name.

      Returns
      -------
      str
          Definition name.



   .. py:method:: set_definition_name(definition_name)

      Set the bondwire definition name.

      Parameters
      ----------
      definition_name : str
          Definition name.



