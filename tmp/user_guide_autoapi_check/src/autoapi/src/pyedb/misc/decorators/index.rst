src.pyedb.misc.decorators
=========================

.. py:module:: src.pyedb.misc.decorators


Functions
---------

.. autoapisummary::

   src.pyedb.misc.decorators.deprecated
   src.pyedb.misc.decorators.deprecated_class
   src.pyedb.misc.decorators.deprecated_property
   src.pyedb.misc.decorators.deprecate_argument_name
   src.pyedb.misc.decorators.execution_timer


Module Contents
---------------

.. py:function:: deprecated(reason: str = '')

   Decorator to mark functions or methods as deprecated.

   Parameters
   ----------
   reason : str, optional
       Message to display with the deprecation warning.


.. py:function:: deprecated_class(reason: str = '')

   Decorator to mark a class as deprecated.

   Parameters
   ----------
   reason : str, optional
       Message to display with the deprecation warning.


.. py:function:: deprecated_property(func)

   This decorator marks a property as deprecated.
   It will emit a warning when the property is accessed.


.. py:function:: deprecate_argument_name(argument_map)

   Decorator to deprecate certain argument names in favor of new ones.


.. py:function:: execution_timer(custom_text)

