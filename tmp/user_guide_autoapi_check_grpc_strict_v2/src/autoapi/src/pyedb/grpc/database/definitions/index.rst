src.pyedb.grpc.database.definitions
===================================

.. py:module:: src.pyedb.grpc.database.definitions


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.definitions.Definitions


Module Contents
---------------

.. py:class:: Definitions(pedb)

   .. py:property:: component_defs
      :type: Dict[str, pyedb.grpc.database.definition.component_def.ComponentDef]


      Component definitions.

      .. deprecated:: 0.66.0

         Use :attr:`components` instead.




   .. py:property:: component

      Component definitions.

      .. deprecated:: 0.66.0

         Use :attr:`components` instead.




   .. py:property:: apd_bondwire_defs

      Get all APD bondwire definitions in this Database.

      .. deprecated:: 0.66.0

         Use :attr:`apd_bondwires` instead.




   .. py:property:: jedec4_bondwire_defs

      Get all JEDEC4 bondwire definitions in this Database.

      .. deprecated:: 0.66.0

         Use :attr:`jedec4_bondwires` instead.




   .. py:property:: jedec5_bondwire_defs

      Get all JEDEC5 bondwire definitions in this Database.

      .. deprecated:: 0.66.0

         Use :attr:`jedec5_bondwires` instead.




   .. py:property:: package_defs
      :type: Dict[str, pyedb.grpc.database.definition.package_def.PackageDef]


      Package definitions.

      .. deprecated:: 0.66.0

         Use :attr:`packages` instead.




   .. py:property:: components
      :type: Dict[str, pyedb.grpc.database.definition.component_def.ComponentDef]


      Component definitions

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> component_defs = edb.definitions.component
      >>> for name, comp_def in component_defs.items():
      ...     print(f"Component: {name}, Part: {comp_def.part}")



   .. py:property:: package

      Package definitions.

      .. deprecated:: 0.66.0

         Use :attr:`packages` instead.




   .. py:property:: packages
      :type: Dict[str, pyedb.grpc.database.definition.package_def.PackageDef]


      Package definitions.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> package_defs = edb.definitions.package
      >>> for name, pkg_def in package_defs.items():
      ...     print(f"Package: {name}, Boundary: {pkg_def.exterior_boundary}")



   .. py:property:: apd_bondwires

      Get all APD bondwire definitions in this Database.

      Returns
      -------
      list[:class:`ApdBondwireDef <ansys.edb.definition.ApdBondwireDef>`]



   .. py:property:: jedec4_bondwires

      Get all JEDEC4 bondwire definitions in this Database.

      Returns
      -------
      list[:class:`Jedec4BondwireDef <ansys.edb.definition.Jedec4BondwireDef>`]



   .. py:property:: jedec5_bondwires

      Get all JEDEC5 bondwire definitions in this Database.

      Returns
      -------
      list[:class:`Jedec5BondwireDef <ansys.edb.definition.Jedec5BondwireDef>`]



   .. py:method:: add_package_def(name: str, component_part_name: Optional[str] = None, boundary_points: Optional[List[List[float]]] = None) -> Union[pyedb.grpc.database.definition.package_def.PackageDef, bool]

      Add a package definition.

      .. deprecated:: 0.66.0

         Use :meth:`add_package` instead.




   .. py:method:: add_package(name: str, component_part_name: Optional[str] = None, boundary_points: Optional[List[List[float]]] = None) -> Union[pyedb.grpc.database.definition.package_def.PackageDef, bool]

      Add a package definition.

      Parameters
      ----------
      name: str
          Name of the package definition.
      component_part_name : str, optional
          Part name of the component.
      boundary_points : list, optional
          Boundary points which define the shape of the package.

      Returns
      -------
      PackageDef object.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()

      Example 1: Create package using component's bounding box
      >>> comp_def = edb.definitions.add_package_def("QFP64", "QFP64_COMPONENT")
      >>> if comp_def:  # Check if created successfully
      ...     print(f"Created package: {comp_def.name}")

      Example 2: Create package with custom boundary
      >>> boundary = [[0, 0], [10e-3, 0], [10e-3, 10e-3], [0, 10e-3]]
      >>> custom_pkg = edb.definitions.add_package_def("CustomIC", boundary_points=boundary)
      >>> if custom_pkg:
      ...     print(f"Custom package boundary: {custom_pkg.exterior_boundary}")



