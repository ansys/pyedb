src.pyedb.grpc.database.simulation_setup.mesh_operation
=======================================================

.. py:module:: src.pyedb.grpc.database.simulation_setup.mesh_operation


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.simulation_setup.mesh_operation.LengthMeshOperationDeprecated
   src.pyedb.grpc.database.simulation_setup.mesh_operation.MeshOperation
   src.pyedb.grpc.database.simulation_setup.mesh_operation.LengthMeshOperation


Module Contents
---------------

.. py:class:: LengthMeshOperationDeprecated

   PyEDB Length Mesh Operation class.


   .. py:property:: restrict_length


   .. py:property:: nets_layers_list


.. py:class:: MeshOperation(core)

   .. py:attribute:: core


   .. py:property:: mesh_operation_type


.. py:class:: LengthMeshOperation(core=None, name='', net_layer_info=None, enabled=True, refine_inside=False, mesh_region='', solve_inside=False, max_length: str = '1mm', restrict_max_length: bool = True, max_elements: str = '1000', restrict_max_elements: bool = False)

   Bases: :py:obj:`MeshOperation`, :py:obj:`LengthMeshOperationDeprecated`


   PyEDB Length Mesh Operation class.


   .. py:method:: create(name: str = '', net_layer_info: tuple[str, str, bool] = None, enabled: bool = True, refine_inside: bool = False, mesh_region: str = '', solve_inside: bool = False, max_length: str = '1mm', restrict_max_length: bool = True, max_elements: str = '1000', restrict_max_elements: bool = False) -> LengthMeshOperation
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
      max_length : str
          The maximum length for the mesh operation.
      restrict_max_length : bool
          Whether to restrict the maximum length.
      max_elements : str
          The maximum number of elements for the mesh operation.
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



   .. py:property:: max_length
      :type: float


      Get the length for the length mesh operation.

      Returns
      -------
      float
          The length value.




   .. py:property:: restrict_max_length
      :type: bool


      Get the restrict max length status of the mesh operation.

      Returns
      -------
      bool
          True if restricting max length is enabled, False otherwise.



   .. py:property:: max_elements
      :type: str


      Get the maximum number of elements for the length mesh operation.

      Returns
      -------
      str
          The maximum number of elements.




   .. py:property:: restrict_max_elements
      :type: bool


      Get the restrict max elements status of the mesh operation.

      Returns
      -------
      bool
          True if restricting max elements is enabled, False otherwise.



