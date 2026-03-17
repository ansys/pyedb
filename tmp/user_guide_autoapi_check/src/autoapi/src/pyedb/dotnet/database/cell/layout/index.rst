src.pyedb.dotnet.database.cell.layout
=====================================

.. py:module:: src.pyedb.dotnet.database.cell.layout

.. autoapi-nested-parse::

   This module contains these classes: `EdbLayout` and `Shape`.



Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.cell.layout.Layout


Functions
---------

.. autoapisummary::

   src.pyedb.dotnet.database.cell.layout.primitive_cast


Module Contents
---------------

.. py:function:: primitive_cast(pedb, edb_object)

.. py:class:: Layout(pedb, edb_object)

   Bases: :py:obj:`pyedb.dotnet.database.utilities.obj_base.ObjBase`


   Manages EDB functionalities for a base object.


   .. py:property:: cell

      :class:`Cell <ansys.edb.layout.Cell>`: Owning cell for this layout.

      Read-Only.



   .. py:property:: layer_collection

      :class:`LayerCollection <ansys.edb.layer.LayerCollection>` : Layer collection of this layout.



   .. py:method:: expanded_extent(nets, extent, expansion_factor, expansion_unitless, use_round_corner, num_increments)

      Get an expanded polygon for the Nets collection.

      Parameters
      ----------
      nets : list[:class:`Net <ansys.edb.net.Net>`]
          A list of nets.
      extent : :class:`ExtentType <ansys.edb.geometry.ExtentType>`
          Geometry extent type for expansion.
      expansion_factor : float
          Expansion factor for the polygon union. No expansion occurs if the `expansion_factor` is less than or             equal to 0.
      expansion_unitless : bool
          When unitless, the distance by which the extent expands is the factor multiplied by the longer dimension            (X or Y distance) of the expanded object/net.
      use_round_corner : bool
          Whether to use round or sharp corners.
          For round corners, this returns a bounding box if its area is within 10% of the rounded expansion's area.
      num_increments : int
          Number of iterations desired to reach the full expansion.

      Returns
      -------
      :class:`PolygonData <ansys.edb.geometry.PolygonData>`

      Notes
      -----
      Method returns the expansion of the contour, so any voids within expanded objects are ignored.



   .. py:method:: convert_primitives_to_vias(primitives, is_pins=False)

      Convert a list of primitives into vias or pins.

      Parameters
      ----------
      primitives : list[:class:`Primitive <ansys.edb.primitive.Primitive>`]
          List of primitives to convert.
      is_pins : bool, optional
          True for pins, false for vias (default).



   .. py:property:: zone_primitives

      :obj:`list` of :class:`Primitive <ansys.edb.primitive.Primitive>` : List of all the primitives in         :term:`zones <Zone>`.

      Read-Only.



   .. py:property:: fixed_zone_primitive

      :class:`Primitive <ansys.edb.primitive.Primitive>` : Fixed :term:`zones <Zone>` primitive.



   .. py:property:: terminals

      Get terminals belonging to active layout.

      Returns
      -------
      Terminal dictionary : Dict[str, pyedb.dotnet.database.edb_data.terminals.Terminal]



   .. py:property:: cell_instances

      :obj:`list` of :class:`CellInstance <ansys.edb.hierarchy.CellInstances>` : List of the cell instances in                 this layout.

      Read-Only.



   .. py:property:: layout_instance

      :class:`LayoutInstance <ansys.edb.layout_instance.LayoutInstance>` : Layout instance of this layout.

      Read-Only.



   .. py:property:: nets

      Nets.

      Returns
      -------



   .. py:property:: primitives

      List of primitives.Read-Only.

      Returns
      -------
      list of :class:`dotnet.database.dotnet.primitive.PrimitiveDotNet` cast objects.



   .. py:property:: primitives_by_aedt_name
      :type: dict


      Primitives.



   .. py:property:: bondwires

      Bondwires.

      Returns
      -------
      list :
          List of bondwires.



   .. py:property:: groups


   .. py:property:: pin_groups
      :type: List[pyedb.dotnet.database.edb_data.sources.PinGroup]



   .. py:property:: net_classes
      :type: List[pyedb.dotnet.database.edb_data.nets_data.EDBNetClassData]



   .. py:property:: extended_nets
      :type: List[pyedb.dotnet.database.edb_data.nets_data.EDBExtendedNetData]



   .. py:property:: differential_pairs
      :type: List[pyedb.dotnet.database.edb_data.nets_data.EDBDifferentialPairData]



   .. py:property:: padstack_instances
      :type: List[pyedb.dotnet.database.edb_data.padstacks_data.EDBPadstackInstance]


      Get all padstack instances in a list.



   .. py:property:: voltage_regulators
      :type: List[pyedb.dotnet.database.cell.voltage_regulator.VoltageRegulator]



   .. py:property:: port_reference_terminals_connected
      :type: bool


      :obj:`bool`: Determine if port reference terminals are connected, applies to lumped ports and circuit ports.

      True if they are connected, False otherwise.
      Read-Only.



   .. py:method:: find_object_by_id(value: int) -> pyedb.dotnet.database.edb_data.padstacks_data.EDBPadstackInstance | pyedb.dotnet.database.edb_data.primitives_data.EdbRectangle | pyedb.dotnet.database.edb_data.primitives_data.EdbPolygon | pyedb.dotnet.database.edb_data.primitives_data.EdbText | pyedb.dotnet.database.edb_data.primitives_data.EdbCircle | pyedb.dotnet.database.cell.primitive.path.Path | None

      Find a layout object by Database ID.

      Parameters
      ----------
      value : int
          ID of the object.



   .. py:method:: find_net_by_name(value: str)

      Find a net object by name

      Parameters
      ----------
      value : str
          Name of the net.

      Returns
      -------




   .. py:method:: find_component_by_name(value: str) -> pyedb.dotnet.database.cell.hierarchy.component.EDBComponent | None

      Find a component object by name. Component name is the reference designator in layout.

      Parameters
      ----------
      value : str
          Name of the component.
      Returns
      -------




   .. py:method:: find_primitive(layer_name: Union[str, list] = None, name: Union[str, list] = None, net_name: Union[str, list] = None) -> list

      Find a primitive objects by layer name.

      Parameters
      ----------
      layer_name : str, list, optional
          Name of the layer.
      name : str, list, optional
          Name of the primitive
      net_name : str, list, optional
          Name of the primitive
      Returns
      -------
      list



   .. py:method:: find_padstack_instances(aedt_name: Union[str, List[str]] = None, component_name: Union[str, List[str]] = None, component_pin_name: Union[str, List[str]] = None, net_name: Union[str, List[str]] = None, instance_id: Union[int, List[int]] = None) -> List[pyedb.dotnet.database.edb_data.padstacks_data.EDBPadstackInstance]

      Finds padstack instances matching the specified criteria.

      This method filters the available padstack instances based on specified attributes such as
      `aedt_name`, `component_name`, `component_pin_name`, `net_name`, or `instance_id`. Criteria
      can be passed as individual values or as a list of values. If no padstack instances match
      the criteria, an error is raised.

      Parameters
      ----------
      aedt_name : Union[str, List[str]], optional
          Name(s) of the AEDT padstack instance(s) to filter.
      component_name : Union[str, List[str]], optional
          Name(s) of the component(s) to filter padstack instances by.
      component_pin_name : Union[str, List[str]], optional
          Name(s) of the component pin(s) to filter padstack instances by.
      net_name : Union[str, List[str]], optional
          Name(s) of the net(s) to filter padstack instances by.
      instance_id : Union[int, List[int]], optional
          ID(s) of the padstack instance(s) to filter.

      Returns
      -------
      List
          A list of padstack instances matching the specified criteria.



