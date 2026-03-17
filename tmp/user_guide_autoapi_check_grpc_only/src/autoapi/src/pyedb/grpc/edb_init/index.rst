src.pyedb.grpc.edb_init
=======================

.. py:module:: src.pyedb.grpc.edb_init

.. autoapi-nested-parse::

   Database.



Classes
-------

.. autoapisummary::

   src.pyedb.grpc.edb_init.EdbInit


Module Contents
---------------

.. py:class:: EdbInit(edbversion)

   Bases: :py:obj:`object`


   Edb Dot Net Class.


   .. py:attribute:: logger
      :value: None



   .. py:attribute:: version


   .. py:attribute:: session
      :value: None



   .. py:property:: db

      Active database object.



   .. py:method:: delete(db_path)

      Delete a database at the specified file location.

      Parameters
      ----------
      db_path : str
          Path to top-level database folder.



   .. py:method:: save()

      Save any changes into a file.



   .. py:method:: close(terminate_rpc_session=True)

      Close the database.

      Parameters
      ----------
      terminate_rpc_session : bool, optional
          Terminate RPC session when closing the database. The default value is `True`.

      . note::
          Unsaved changes will be lost. If multiple databases are open and RPC session is terminated, the connection
          with all databases will be lost. You might be careful and set to `False` until the last open database
          remains.



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

      Get all footprint cells in the Database.

      Returns
      -------
      list[:class:`Cell <ansys.edb.layout.Cell>`]



   .. py:property:: edb_uid

      Get ID of the database.

      Returns
      -------
      int
          The unique EDB id of the Database.



   .. py:property:: is_read_only

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



   .. py:method:: save_as(path: str | pathlib.Path, version: str = '') -> bool

      Save this Database to a new location and older EDB version.

      Parameters
      ----------
      path : str
          New Database file location.
      version : str
          EDB version to save to. Empty string means current version.



   .. py:property:: directory

      Get the directory of the Database.

      Returns
      -------
      str
          Directory of the Database.



   .. py:method:: get_product_property(prod_id, attr_it)

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



   .. py:method:: get_product_property_ids(prod_id)

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



   .. py:method:: scale(scale_factor)

      Uniformly scale all geometry and their locations by a positive factor.

      Parameters
      ----------
      scale_factor : float
          Amount that coordinates are multiplied by.



   .. py:property:: source

      Get source name for this Database.

      This attribute is also used to set the source name.

      Returns
      -------
      str
          name of the source



   .. py:property:: source_version

      Get the source version for this Database.

      This attribute is also used to set the version.

      Returns
      -------
      str
          version string




   .. py:method:: copy_cells(cells_to_copy)

      Copy Cells from other Databases or this Database into this Database.

      Parameters
      ----------
      cells_to_copy : list[:class:`Cell <ansys.edb.core.layout.cell.Cell>`]
          Cells to copy.

      Returns
      -------
      list[:class:`Cell <ansys.edb.core.layout.cell.Cell>`]



