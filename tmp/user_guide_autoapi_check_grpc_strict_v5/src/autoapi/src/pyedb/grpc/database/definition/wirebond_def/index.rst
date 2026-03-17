src.pyedb.grpc.database.definition.wirebond_def
===============================================

.. py:module:: src.pyedb.grpc.database.definition.wirebond_def


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.definition.wirebond_def.BondwireDef
   src.pyedb.grpc.database.definition.wirebond_def.Jedec4BondwireDef
   src.pyedb.grpc.database.definition.wirebond_def.Jedec5BondwireDef
   src.pyedb.grpc.database.definition.wirebond_def.ApdBondwireDef


Module Contents
---------------

.. py:class:: BondwireDef(pedb, core=None)

   .. py:attribute:: core
      :value: None



   .. py:property:: name

      Get the name of the bondwire definition.



   .. py:property:: height

      Get the bondwire top-to-die distance of the bondwire definition.



   .. py:method:: delete()


   .. py:method:: get_parameters()

      Get the bondwire top-to-die distance of the JEDEC 4 bondwire definition.

      Returns
      -------
      float
          Bondwire top-to-die distance.



   .. py:method:: set_parameters(parameters)

      Set the bondwire top-to-die distance of the JEDEC 4 bondwire definition.

      Parameters
      ----------
      parameters : float
          Bondwire top-to-die distance.



.. py:class:: Jedec4BondwireDef(pedb, core=None)

   Bases: :py:obj:`BondwireDef`


   Class representing a JEDEC 4 bondwire definition.


   .. py:attribute:: core
      :value: None



   .. py:method:: create(edb, name)
      :classmethod:


      Create a new JEDEC 4 bondwire definition.

      Parameters
      ----------
      edb : :class:`pyedb.edb`
          Inherited AEDT object.
      name : str
          Name of the JEDEC 4 bondwire definition.

      Returns
      -------
      :class:`pyedb.grpc.database.definition.wirebond_def.Jedec4BondwireDef`
          The created JEDEC 4 bondwire definition.



   .. py:method:: find_by_name(edb, name)
      :staticmethod:


      Find a JEDEC 4 bondwire definition by name.

      Parameters
      ----------
      edb : :class:`pyedb.edb`
          Inherited AEDT object.
      name : str
          Name of the JEDEC 4 bondwire definition.

      Returns
      -------
      :class:`pyedb.grpc.database.definition.wirebond_def.Jedec4BondwireDef` or None
          The found JEDEC 4 bondwire definition or None if not found.



.. py:class:: Jedec5BondwireDef(pedb, core=None)

   Bases: :py:obj:`BondwireDef`


   Class representing a JEDEC 5 bondwire definition.


   .. py:attribute:: core
      :value: None



   .. py:method:: create(edb, name)
      :classmethod:


      Create a new JEDEC 5 bondwire definition.

      Parameters
      ----------
      edb : :class:`pyedb.edb`
          Inherited AEDT object.
      name : str
          Name of the JEDEC 5 bondwire definition.

      Returns
      -------
      :class:`pyedb.grpc.database.definition.wirebond_def.Jedec5BondwireDef`
          The created JEDEC 5 bondwire definition.



   .. py:method:: find_by_name(edb, name)
      :staticmethod:


      Find a JEDEC 5 bondwire definition by name.

      Parameters
      ----------
      edb : :class:`pyedb.edb`
          Inherited AEDT object.
      name : str
          Name of the JEDEC 5 bondwire definition.

      Returns
      -------
      :class:`pyedb.grpc.database.definition.wirebond_def.Jedec5BondwireDef` or None
          The found JEDEC 5 bondwire definition or None if not found.



.. py:class:: ApdBondwireDef(pedb, core=None)

   Bases: :py:obj:`BondwireDef`


   Class representing an Apd bondwire definition.


   .. py:attribute:: core
      :value: None



   .. py:method:: create(edb, name)
      :classmethod:


      Create a new Apd bondwire definition.

      Parameters
      ----------
      edb : :class:`pyedb.edb`
          Inherited AEDT object.
      name : str
          Name of the Apd bondwire definition.

      Returns
      -------
      :class:`pyedb.grpc.database.definition.wirebond_def.ApdBondwireDef`
          The created Apd bondwire definition.



   .. py:method:: find_by_name(edb, name)
      :staticmethod:


      Find an Apd bondwire definition by name.

      Parameters
      ----------
      edb : :class:`pyedb.edb`
          Inherited AEDT object.
      name : str
          Name of the Apd bondwire definition.

      Returns
      -------
      :class:`pyedb.grpc.database.definition.wirebond_def.ApdBondwireDef` or None
          The found Apd bondwire definition or None if not found.



