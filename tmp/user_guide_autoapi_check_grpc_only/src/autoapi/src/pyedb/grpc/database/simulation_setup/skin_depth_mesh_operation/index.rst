src.pyedb.grpc.database.simulation_setup.skin_depth_mesh_operation
==================================================================

.. py:module:: src.pyedb.grpc.database.simulation_setup.skin_depth_mesh_operation


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.simulation_setup.skin_depth_mesh_operation.SkinDepthMeshOperation


Module Contents
---------------

.. py:class:: SkinDepthMeshOperation(core=None, name='', net_layer_info=None, enabled=True, refine_inside=False, mesh_region='', solve_inside=False, skin_depth: str = '1um', surface_triangle_length: str = '1mm', num_layers: str = '2', max_elements: str = '1000', restrict_max_elements: bool = False)

   PyEDB Length Mesh Operation class.


   .. py:method:: create(name: str = '', net_layer_info: tuple[str, str, bool] = None, enabled: bool = True, refine_inside: bool = False, mesh_region: str = '', solve_inside: bool = False, skin_depth: str = '1um', surface_triangle_length: str = '1mm', num_layers: str = '2', max_elements: str = '1000', restrict_max_elements: bool = False) -> SkinDepthMeshOperation
      :classmethod:


      Create a Length Mesh Operation.
      Parameters
      ----------
      name : str
          Name of the mesh operation.
      net_layer_info : tuple[str, str, bool]
          A tuple containing the net name, layer name, and a boolean indicating whether to include
          child layers.
      enabled : bool
          Whether the mesh operation is enabled.
      refine_inside : bool
          Whether to refine the mesh inside the specified region.
      mesh_region : str
          The name of the mesh region.
      solve_inside : bool
          Whether to solve inside the specified region.
      skin_depth : str
          The skin_depth value.
      surface_triangle_length : str
          The surface triangle length value.
      num_layers: int
          Number of layers for the skin depth mesh operation.
      max_elements : int
          Maximum number of elements for the mesh operation.
      restrict_max_elements : bool
          Whether to restrict the maximum number of elements.
      Returns
      -------
      LengthMeshOperation : LengthMeshOperation
          The Length Mesh Operation object.



   .. py:property:: name
      :type: str


      Get the name of the mesh operation.

      Returns
      -------
      str
          Name of the mesh operation.



   .. py:property:: enabled
      :type: bool


      Get the enabled status of the mesh operation.

      Returns
      -------
      bool
          True if the mesh operation is enabled, False otherwise.



   .. py:property:: mesh_region
      :type: str


      Get the mesh region name.

      Returns
      -------
      str
          Name of the mesh region.



   .. py:property:: net_layer_info
      :type: list[tuple[str, str, bool]]


      Get the net layer information list.

      Returns
      -------
      list[tuple(str, str, bool)]
          List of net layer information for the mesh operation.



   .. py:property:: refine_inside
      :type: bool


      Get the refine inside status of the mesh operation.

      Returns
      -------
      bool
          True if refining inside is enabled, False otherwise.



   .. py:property:: solve_inside
      :type: bool


      Get the solve inside status of the mesh operation.

      Returns
      -------
      bool
          True if solving inside is enabled, False otherwise.



   .. py:property:: skin_depth
      :type: str


      Get the skin depth value.

      Returns
      -------
      str
          Skin depth value.



   .. py:property:: surface_triangle_length
      :type: str


      Get the surface triangle length value.

      Returns
      -------
      str
          Surface triangle length value.



   .. py:property:: num_layers
      :type: str


      Get the number of layers for the skin depth mesh operation.

      Returns
      -------
      int
          Number of layers.



   .. py:property:: max_elements
      :type: str


      Get the maximum number of elements for the mesh operation.

      Returns
      -------
      int
          Maximum number of elements.



   .. py:property:: restrict_max_elements
      :type: bool


      Get the restrict maximum elements status of the mesh operation.

      Returns
      -------
      bool
          True if restricting maximum elements is enabled, False otherwise.



