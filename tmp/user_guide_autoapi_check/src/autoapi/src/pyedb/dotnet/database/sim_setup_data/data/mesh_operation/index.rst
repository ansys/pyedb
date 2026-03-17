src.pyedb.dotnet.database.sim_setup_data.data.mesh_operation
============================================================

.. py:module:: src.pyedb.dotnet.database.sim_setup_data.data.mesh_operation


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.sim_setup_data.data.mesh_operation.MeshOpType
   src.pyedb.dotnet.database.sim_setup_data.data.mesh_operation.MeshOperation
   src.pyedb.dotnet.database.sim_setup_data.data.mesh_operation.LengthMeshOperation
   src.pyedb.dotnet.database.sim_setup_data.data.mesh_operation.SkinDepthMeshOperation


Module Contents
---------------

.. py:class:: MeshOpType(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   Create a collection of name/value pairs.

   Example enumeration:

   >>> class Color(Enum):
   ...     RED = 1
   ...     BLUE = 2
   ...     GREEN = 3

   Access them by:

   - attribute access::

   >>> Color.RED
   <Color.RED: 1>

   - value lookup:

   >>> Color(1)
   <Color.RED: 1>

   - name lookup:

   >>> Color['RED']
   <Color.RED: 1>

   Enumerations can be iterated over, and know how many members they have:

   >>> len(Color)
   3

   >>> list(Color)
   [<Color.RED: 1>, <Color.BLUE: 2>, <Color.GREEN: 3>]

   Methods can be added to enumerations, and members can have their own
   attributes -- see the documentation for details.


   .. py:attribute:: kMeshSetupBase
      :value: 'base'



   .. py:attribute:: kMeshSetupLength
      :value: 'length'



   .. py:attribute:: kMeshSetupSkinDepth
      :value: 'skin_depth'



   .. py:attribute:: kNumMeshOpTypes
      :value: 'num_mesh_op_types'



.. py:class:: MeshOperation(parent, edb_object)

   Bases: :py:obj:`object`


   Mesh Operation Class.


   .. py:property:: net_layer_info

      Adding property for grpc compatibility.

      Returns
      -------
      The tuple is in this form: (net_name, layer_name, is_sheet)``.



   .. py:property:: enabled

      Whether if mesh operation is enabled.

      Returns
      -------
      bool
          ``True`` if mesh operation is used, ``False`` otherwise.



   .. py:property:: mesh_operation_type

      Mesh operation type.
      Options:
      0- ``kMeshSetupBase``
      1- ``kMeshSetupLength``
      2- ``kMeshSetupSkinDepth``
      3- ``kNumMeshOpTypes``.

      Returns
      -------
      str



   .. py:property:: type


   .. py:property:: mesh_region

      Mesh region name.

      Returns
      -------
      str
          Name of the mesh region.



   .. py:property:: name

      Mesh operation name.

      Returns
      -------
      str



   .. py:property:: nets_layers_list

      List of nets and layers.

      Returns
      -------
      list
         List of lists with three elements. Each list must contain:
         1- net name
         2- layer name
         3- bool.
         Third element is represents whether if the mesh operation is enabled or disabled.




   .. py:property:: refine_inside

      Whether to turn on refine inside objects.

      Returns
      -------
      bool
          ``True`` if refine inside objects is used, ``False`` otherwise.




   .. py:property:: max_elements

      Maximum number of elements.

      Returns
      -------
      str



   .. py:property:: restrict_max_elements

      Whether to restrict maximum number  of elements.

      Returns
      -------
      bool



.. py:class:: LengthMeshOperation(parent, edb_object)

   Bases: :py:obj:`MeshOperation`, :py:obj:`object`


   Mesh operation Length class.
   This class is accessible from Hfss Setup in EDB and add_length_mesh_operation method.

   Examples
   --------
   >>> mop = edbapp.setups["setup1a"].add_length_mesh_operation({"GND": ["TOP", "BOTTOM"]})
   >>> mop.max_elements = 3000


   .. py:property:: max_length

      Maximum length of elements.

      Returns
      -------
      str



   .. py:property:: restrict_max_length

      Adding property for grpc compatibility.



   .. py:property:: restrict_length

      Whether to restrict length of elements.

      Returns
      -------
      bool



.. py:class:: SkinDepthMeshOperation(parent, edb_object)

   Bases: :py:obj:`MeshOperation`, :py:obj:`object`


   Mesh operation Skin Depth class.
   This class is accessible from Hfss Setup in EDB and assign_skin_depth_mesh_operation method.

   Examples
   --------
   >>> mop = edbapp.setups["setup1a"].add_skin_depth_mesh_operation({"GND": ["TOP", "BOTTOM"]})
   >>> mop.max_elements = 3000


   .. py:property:: skin_depth

      Skin depth value.

      Returns
      -------
      str



   .. py:property:: surface_triangle_length

      Surface triangle length value.

      Returns
      -------
      str



   .. py:property:: number_of_layers

      Adding property for grpc compatibility.



   .. py:property:: number_of_layer_elements

      Number of layer elements.

      Returns
      -------
      str



