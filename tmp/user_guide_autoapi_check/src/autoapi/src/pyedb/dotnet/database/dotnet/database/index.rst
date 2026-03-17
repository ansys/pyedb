src.pyedb.dotnet.database.dotnet.database
=========================================

.. py:module:: src.pyedb.dotnet.database.dotnet.database

.. autoapi-nested-parse::

   Database.



Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.dotnet.database.HierarchyDotNet
   src.pyedb.dotnet.database.dotnet.database.PolygonDataDotNet
   src.pyedb.dotnet.database.dotnet.database.NetDotNet
   src.pyedb.dotnet.database.dotnet.database.NetClassDotNet
   src.pyedb.dotnet.database.dotnet.database.ExtendedNetDotNet
   src.pyedb.dotnet.database.dotnet.database.DifferentialPairDotNet
   src.pyedb.dotnet.database.dotnet.database.CellClassDotNet
   src.pyedb.dotnet.database.dotnet.database.UtilityDotNet
   src.pyedb.dotnet.database.dotnet.database.GeometryDotNet
   src.pyedb.dotnet.database.dotnet.database.CellDotNet
   src.pyedb.dotnet.database.dotnet.database.Database


Module Contents
---------------

.. py:class:: HierarchyDotNet(app)

   Hierarchy.


   .. py:attribute:: core


   .. py:property:: api_class

      Return Ansys.Ansoft.Edb class object.



   .. py:property:: component

      Edb Dotnet Api Database `Edb.Cell.Hierarchy.Component`.



   .. py:property:: cell_instance

      Edb Dotnet Api Database `Edb.Cell.Hierarchy.CellInstance`.



   .. py:property:: pin_group

      Edb Dotnet Api Database `Edb.Cell.Hierarchy.PinGroup`.



.. py:class:: PolygonDataDotNet(pedb, api_object=None)

   Polygon Data.


   .. py:attribute:: dotnetobj


   .. py:attribute:: core
      :value: None



   .. py:property:: api_class

      :class:`Ansys.Ansoft.Edb` class object.



   .. py:property:: arcs

      List of Edb.Geometry.ArcData.



   .. py:method:: add_point(x, y, incremental=False)

      Add a point at the end of the point list of the polygon.

      Parameters
      ----------
      x: str, int, float
          X coordinate.
      y: str, in, float
          Y coordinate.
      incremental: bool
          Whether to add the point incrementally. The default value is ``False``. When
          ``True``, the coordinates of the added point are incremental to the last point.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.



   .. py:method:: get_bbox_of_boxes(points)

      Get the EDB .NET API ``Edb.Geometry.GetBBoxOfBoxes`` database.

      Parameters
      ----------
      points : list or `Edb.Geometry.PointData`



   .. py:method:: get_bbox_of_polygons(polygons)

      Edb Dotnet Api Database `Edb.Geometry.GetBBoxOfPolygons`.

      Parameters
      ----------
      polygons : list or `Edb.Geometry.PolygonData`



   .. py:method:: create_from_bbox(points) -> list[Any]

      Edb Dotnet Api Database `Edb.Geometry.CreateFromBBox`.

      Parameters
      ----------
      points : list or `Edb.Geometry.PointData`



   .. py:method:: create_from_arcs(arcs, flag)

      Edb Dotnet Api Database `Edb.Geometry.CreateFromArcs`.

      Parameters
      ----------
      arcs : list or `Edb.Geometry.ArcData`
          List of ArcData.
      flag : bool



   .. py:method:: unite(pdata)

      Edb Dotnet Api Database `Edb.Geometry.Unite`.

      Parameters
      ----------
      pdata : list or `Edb.Geometry.PolygonData`
          Polygons to unite.




   .. py:method:: get_convex_hull_of_polygons(pdata)

      Edb Dotnet Api Database `Edb.Geometry.GetConvexHullOfPolygons`.

      Parameters
      ----------
      pdata : list or List of `Edb.Geometry.PolygonData`
          Polygons to unite in a Convex Hull.



.. py:class:: NetDotNet(app, net_obj=None)

   Net Objects.


   .. py:attribute:: net


   .. py:attribute:: core


   .. py:attribute:: net_obj
      :value: None



   .. py:property:: api_class

      Return Ansys.Ansoft.Edb class object.



   .. py:property:: api_object

      Return Ansys.Ansoft.Edb object.



   .. py:method:: find_by_name(layout, net) -> NetDotNet

      Edb Dotnet Api Database `Edb.Net.FindByName`.

      Returns
      -------
      :class:`NetDotNet`



   .. py:method:: create(layout, name) -> NetDotNet

      Edb Dotnet Api Database `Edb.Net.Create`.

      Returns
      -------
      :class:`NetDotNet`



   .. py:method:: delete()

      Edb Dotnet Api Database `Edb.Net.Delete`.



   .. py:property:: name
      :type: str


      Edb Dotnet Api Database `net.name` and  `Net.SetName()`.

      Returns
      -------
      str
          Name of the net.



   .. py:property:: is_null
      :type: bool


      Edb Dotnet Api Database `Net.IsNull()`.



   .. py:property:: is_power_ground
      :type: bool | None


      Edb Dotnet Api Database `Net.IsPowerGround()` and  `Net.SetIsPowerGround()`.



.. py:class:: NetClassDotNet(app, api_object=None)

   Net Class.


   .. py:attribute:: cell_net_class


   .. py:attribute:: api_object
      :value: None



   .. py:attribute:: core


   .. py:property:: api_nets

      Return Edb Nets object dictionary.



   .. py:method:: api_create(name)

      Edb Dotnet Api Database `Edb.NetClass.Create`.



   .. py:property:: name
      :type: str


      Edb Dotnet Api Database `NetClass.name` and  `NetClass.SetName()`.



   .. py:method:: add_net(name)

      Add a new net.

      Parameters
      ----------
      name : str
          The name of the net to be added.

      Returns
      -------
      object



   .. py:method:: delete()

      Edb Dotnet Api Database `Delete`.



   .. py:property:: is_null
      :type: bool


      Edb Dotnet Api Database `NetClass.IsNull()`.



.. py:class:: ExtendedNetDotNet(app, api_object=None)

   Bases: :py:obj:`NetClassDotNet`


   Extended net class.


   .. py:attribute:: cell_extended_net


   .. py:property:: api_class

      Return Ansys.Ansoft.Edb class object.



   .. py:method:: find_by_name(layout, net)

      Edb Dotnet Api Database `Edb.ExtendedNet.FindByName`.



   .. py:method:: api_create(name)

      Edb Dotnet Api Database `Edb.ExtendedNet.Create`.



.. py:class:: DifferentialPairDotNet(app, api_object=None)

   Bases: :py:obj:`NetClassDotNet`


   Differential Pairs.


   .. py:attribute:: cell_diff_pair


   .. py:property:: api_class

      Return Ansys.Ansoft.Edb class object.



   .. py:method:: find_by_name(layout, net) -> DifferentialPairDotNet

      Edb Dotnet Api Database `Edb.DifferentialPair.FindByName`.

      Returns
      -------
      :class:`DifferentialPairDotNet`




   .. py:method:: api_create(name)

      Edb Dotnet Api Database `Edb.DifferentialPair.Create`.



   .. py:property:: api_positive_net

      Edb Api Positive net object.



   .. py:property:: api_negative_net

      Edb Api Negative net object.



.. py:class:: CellClassDotNet(app, active_cell=None)

   Cell Class.


   .. py:attribute:: core


   .. py:property:: api_class

      Return Ansys.Ansoft.Edb class object.



   .. py:property:: api_object

      Return Ansys.Ansoft.Edb object.



   .. py:method:: create(db, cell_type, cell_name) -> CellClassDotNet

      Edb Dotnet Api Database `Edb.Cell.Create`.

      Returns
      -------
      :class:`CellClassDotNet`




   .. py:property:: terminal

      Edb Dotnet Api Database `Edb.Cell.Terminal`.



   .. py:property:: hierarchy
      :type: HierarchyDotNet


      Edb Dotnet Api Database `Edb.Cell.Hierarchy`.

      Returns
      -------
      :class:`dotnet.database.dotnet.HierarchyDotNet`



   .. py:property:: cell

      Edb Dotnet Api Database `Edb.Cell`.



   .. py:property:: net
      :type: NetDotNet


      Edb Dotnet Api Cell.Layer.



   .. py:property:: layer_type

      Edb Dotnet Api Cell.LayerType.



   .. py:property:: layer_type_set

      Edb Dotnet Api Cell.LayerTypeSet.



   .. py:property:: layer

      Edb Dotnet Api Cell.Layer.



   .. py:property:: layout_object_type

      Edb Dotnet Api LayoutObjType.



   .. py:property:: primitive
      :type: pyedb.dotnet.database.dotnet.primitive.PrimitiveDotNet


      Edb Dotnet Api Database `Edb.Cell.Primitive`.



   .. py:property:: simulation_setups


   .. py:method:: get_all_variable_names()

      Method added for compatibility with grpc.

      Returns
      -------
      List[Str]
          List of variables name.




.. py:class:: UtilityDotNet(app)

   Utility Edb class.


   .. py:attribute:: utility


   .. py:attribute:: core


   .. py:attribute:: active_db


   .. py:attribute:: active_cell


   .. py:property:: api_class

      Return Ansys.Ansoft.Edb class object.



   .. py:method:: value(value, var_server=None)

      Edb Dotnet Api Utility.Value.



.. py:class:: GeometryDotNet(app)

   Geometry Edb Class.


   .. py:attribute:: geometry


   .. py:attribute:: core


   .. py:property:: api_class

      Return Ansys.Ansoft.Edb class object.



   .. py:property:: utility


   .. py:method:: point_data(p1, p2)

      Edb Dotnet Api Point.



   .. py:method:: point3d_data(p1, p2, p3)

      Edb Dotnet Api Point 3D.



   .. py:property:: extent_type

      Edb Dotnet Api Extent Type.



   .. py:property:: polygon_data

      Polygon Data.

      Returns
      -------
      :class:`dotnet.database.dotnet.PolygonDataDotNet`



   .. py:method:: arc_data(point1, point2, rotation=None, center=None, height=None)

      Compute EBD arc data.

      Parameters
      ----------
      point1 : list or PointData object
      point2 : list or PointData object
      rotation : int or RotationDir enumerator
      center :  list or PointData object
      height : float

      Returns
      -------
      Edb ArcData object



.. py:class:: CellDotNet(app)

   Cell Dot net.


   .. py:attribute:: core


   .. py:property:: definition

      Edb Dotnet Api Definition.



   .. py:property:: database

      Edb Dotnet Api Database.



   .. py:property:: cell

      Edb Dotnet Api Database `Edb.Cell`.

      Returns
      -------
      :class:`pyedb.dotnet.database.dotnet.database.CellClassDotNet`



   .. py:property:: utility

      Utility class.

      Returns
      -------
      :class:`pyedb.dotnet.database.dotnet.database.UtilityDotNet`



   .. py:property:: geometry

      Geometry class.

      Returns
      -------
      :class:`pyedb.dotnet.database.dotnet.database.GeometryDotNet`



.. py:class:: Database

   Class representing a database object.


   .. py:property:: database

      Edb Dotnet Api Database.



   .. py:property:: definition

      Edb Dotnet Api Database `Edb.Definition`.



   .. py:method:: delete(db_path)

      Delete a database at the specified file location.

      Parameters
      ----------
      db_path : str
          Path to top-level database folder.



   .. py:method:: save()

      Save any changes into a file.



   .. py:method:: close()

      Close the database.

      .. note::
          Unsaved changes will be lost.



   .. py:property:: top_circuit_cells

      Get top circuit cells.

      Returns
      -------
      list[:class:`Cell <ansys.edb.layout.Cell>`]



   .. py:property:: circuit_cells

      Get all circuit cells in the Database.

      Returns
      -------
      list[:class:`Cell <ansys.edb.layout.Cell>`]



   .. py:property:: footprint_cells
      :type: list[Any]


      Get all footprint cells in the Database.

      Returns
      -------
      list[:class:`Cell <ansys.edb.layout.Cell>`]



   .. py:property:: edb_uid
      :type: int


      Get ID of the database.

      Returns
      -------
      int
          The unique EDB id of the Database.



   .. py:property:: is_read_only
      :type: bool


      Determine if the database is open in a read-only mode.

      Returns
      -------
      bool
          True if Database is open with read only access, otherwise False.



   .. py:method:: find_by_id(db_id)

      Find a database by ID.

      Parameters
      ----------
      db_id : int
          The Database's unique EDB id.

      Returns
      -------
      Database
          The Database or Null on failure.



   .. py:method:: save_as(path, version='') -> bool

      Save this Database to a new location and older EDB version.

      Parameters
      ----------
      path : str
          New Database file location.
      version : str
          EDB version to save to. Empty string means current version.

      Returns
      -------
      bool
          True if successful, False if failed.



   .. py:property:: directory
      :type: str


      Get the directory of the Database.

      Returns
      -------
      str
          Directory of the Database.



   .. py:method:: get_product_property(prod_id, attr_it) -> str

      Get the product-specific property value.

      Parameters
      ----------
      prod_id : ProductIdType
          Product ID.
      attr_it : int
          Attribute ID.

      Returns
      -------
      str
          Property value returned.



   .. py:method:: set_product_property(prod_id, attr_it, prop_value)

      Set the product property associated with the given product and attribute ids.

      Parameters
      ----------
      prod_id : ProductIdType
          Product ID.
      attr_it : int
          Attribute ID.
      prop_value : str
          Product property's new value



   .. py:method:: get_product_property_ids(prod_id) -> list[int]

      Get a list of attribute ids corresponding to a product property id.

      Parameters
      ----------
      prod_id : ProductIdType
          Product ID.

      Returns
      -------
      list[int]
          The attribute ids associated with this product property.



   .. py:method:: import_material_from_control_file(control_file, schema_dir=None, append=True)

      Import materials from the provided control file.

      Parameters
      ----------
      control_file : str
          Control file name with full path.
      schema_dir : str
          Schema file path.
      append : bool
          True if the existing materials in Database are kept. False to remove existing materials in database.



   .. py:property:: version
      :type: tuple[int, int]


      Get version of the Database.

      Returns
      -------
      tuple(int, int)
          A tuple of the version numbers [major, minor]



   .. py:method:: scale(scale_factor) -> float

      Uniformly scale all geometry and their locations by a positive factor.

      Parameters
      ----------
      scale_factor : float
          Amount that coordinates are multiplied by.



   .. py:property:: source
      :type: str


      Get source name for this Database.

      This attribute is also used to set the source name.

      Returns
      -------
      str
          name of the source



   .. py:property:: source_version
      :type: str


      Get the source version for this Database.

      This attribute is also used to set the version.

      Returns
      -------
      str
          version string




   .. py:method:: copy_cells(cells_to_copy) -> list[Any]

      Copy Cells from other Databases or this Database into this Database.

      Parameters
      ----------
      cells_to_copy : list[:class:`Cell <ansys.edb.layout.Cell>`]
          Cells to copy.

      Returns
      -------
      list[:class:`Cell <ansys.edb.layout.Cell>`]
          New Cells created in this Database.



   .. py:property:: apd_bondwire_defs
      :type: list[Any]


      Get all APD bondwire definitions in this Database.

      Returns
      -------
      list[:class:`ApdBondwireDef <ansys.edb.definition.ApdBondwireDef>`]



   .. py:property:: jedec4_bondwire_defs
      :type: list[Any]


      Get all JEDEC4 bondwire definitions in this Database.

      Returns
      -------
      list[:class:`Jedec4BondwireDef <ansys.edb.definition.Jedec4BondwireDef>`]



   .. py:property:: jedec5_bondwire_defs
      :type: list[Any]


      Get all JEDEC5 bondwire definitions in this Database.

      Returns
      -------
      list[:class:`Jedec5BondwireDef <ansys.edb.definition.Jedec5BondwireDef>`]



   .. py:property:: padstack_defs
      :type: list[Any]


      Get all Padstack definitions in this Database.

      Returns
      -------
      list[:class:`PadstackDef <ansys.edb.definition.PadstackDef>`]



   .. py:property:: package_defs
      :type: list[Any]


      Get all Package definitions in this Database.

      Returns
      -------
      list[:class:`PackageDef <ansys.edb.definition.PackageDef>`]



   .. py:property:: component_defs
      :type: list[Any]


      Get all component definitions in the database.

      Returns
      -------
      list[:class:`ComponentDef <ansys.edb.definition.ComponentDef>`]



   .. py:property:: material_defs
      :type: list[Any]


      Get all material definitions in the database.

      Returns
      -------
      list[:class:`MaterialDef <ansys.edb.definition.MaterialDef>`]



   .. py:property:: dataset_defs
      :type: list[Any]


      Get all dataset definitions in the database.

      Returns
      -------
      list[:class:`DatasetDef <ansys.edb.definition.DatasetDef>`]



   .. py:method:: attach(hdb)

      Attach the database to existing AEDT instance.

      Parameters
      ----------
      hdb



