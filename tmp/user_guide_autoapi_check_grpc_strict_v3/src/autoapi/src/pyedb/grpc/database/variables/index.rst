src.pyedb.grpc.database.variables
=================================

.. py:module:: src.pyedb.grpc.database.variables


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.variables.Variable


Module Contents
---------------

.. py:class:: Variable(pedb, name)

   Manages EDB methods for variable accessible from `Edb.Utility.VariableServer` property.


   .. py:property:: name

      Get the name of this variable.



   .. py:property:: value

      Get the value of this variable.

      Returns
      -------
      float



   .. py:property:: description

      Get the description of this variable.



   .. py:property:: is_parameter

      Determine whether this variable is a parameter.



   .. py:method:: delete()

      Delete this variable.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> edb.design_variables["new_variable"].delete()



