src.pyedb.dotnet.database.definition.definitions
================================================

.. py:module:: src.pyedb.dotnet.database.definition.definitions


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.definition.definitions.Definitions


Module Contents
---------------

.. py:class:: Definitions(pedb)

   .. py:property:: component

      Component definitions.

      .. deprecated:: 0.66.0

         Use :attr:`components` instead.




   .. py:property:: components


   .. py:property:: package

      Package definitions.

      .. deprecated:: 0.66.0

         Use :attr:`packages` instead.




   .. py:property:: packages

      Package definitions.



   .. py:property:: jedec4_bondwires

      Wirebond definitions.



   .. py:property:: jedec5_bondwires


   .. py:property:: apd_bondwires


   .. py:method:: add_packages(name, component_part_name=None, boundary_points=None)

      Add a package definition.

      .. deprecated:: 0.66.0

         Use :meth:`add_package` instead.




   .. py:method:: add_package(name, component_part_name=None, boundary_points=None)

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




   .. py:method:: create_jedec4_bondwire_def(name: str, top_to_die_distance: float = 3e-05)

      Create a JEDEC 4 bondwire definition.

      Parameters
      ----------
      name : str
          Name of the bondwire definition.
      top_to_die_distance : float, optional
          Top to die distance in meters. The default is 30e-6.

      Returns
      -------
      Jedec4BondwireDef
          The created JEDEC 4 bondwire definition.



   .. py:method:: create_jedec5_bondwire_def(name: str, top_to_die_distance: float = 3e-05)

      Create a JEDEC 5 bondwire definition.

      Parameters
      ----------
      name : str
          Name of the bondwire definition.
      top_to_die_distance : float, optional
          Top to die distance in meters. The default is 30e-6.

      Returns
      -------
      Jedec5BondwireDef
          The created JEDEC 5 bondwire definition.



   .. py:method:: create_apd_bondwire_def(name: str, top_to_die_distance: float = 3e-05)

      Create an APD bondwire definition.

      Parameters
      ----------
      name : str
          Name of the bondwire definition.
      top_to_die_distance : float, optional
          Top to die distance in meters. The default is 30e-6.

      Returns
      -------
      ApdBondwireDef
          The created APD bondwire definition.



