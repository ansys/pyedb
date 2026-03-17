src.pyedb.dotnet.database.general
=================================

.. py:module:: src.pyedb.dotnet.database.general

.. autoapi-nested-parse::

   This module contains EDB general methods and related methods.



Attributes
----------

.. autoapisummary::

   src.pyedb.dotnet.database.general.logger


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.general.PadGeometryTpe
   src.pyedb.dotnet.database.general.DielectricExtentType
   src.pyedb.dotnet.database.general.Primitives
   src.pyedb.dotnet.database.general.LayoutObjType


Functions
---------

.. autoapisummary::

   src.pyedb.dotnet.database.general.convert_netdict_to_pydict
   src.pyedb.dotnet.database.general.convert_pytuple_to_nettuple
   src.pyedb.dotnet.database.general.convert_pydict_to_netdict
   src.pyedb.dotnet.database.general.convert_py_list_to_net_list
   src.pyedb.dotnet.database.general.convert_net_list_to_py_list
   src.pyedb.dotnet.database.general.pascal_to_snake
   src.pyedb.dotnet.database.general.snake_to_pascal


Module Contents
---------------

.. py:data:: logger

.. py:function:: convert_netdict_to_pydict(dict_in)

   Convert a net dictionary to a Python dictionary.

   Parameters
   ----------
   dict_in : dict
       Net dictionary to convert.

   Returns
   -------
   dict
       Dictionary converted to Python.



.. py:function:: convert_pytuple_to_nettuple(_tuple)

   Convert a Python tuple into a .NET tuple.
   Parameters
   ----------
   tuple : Python tuple

   Returns
   -------
   .NET tuple.


.. py:function:: convert_pydict_to_netdict(input_dict)

   Convert a Python dictionary to a .NET dictionary.

   Parameters
   ----------
   input_dict : dict
       Python dictionary to convert.


   Returns
   -------
   dict
       Dictionary converted to .NET.


.. py:function:: convert_py_list_to_net_list(pylist, list_type=None)

   Convert a Python list to a Net list.

   Parameters
   ----------
   pylist : list
       Python list to convert.

   Returns
   -------
   list
       List converted to Net.


.. py:function:: convert_net_list_to_py_list(netlist)

   Convert a Net list to a Python list.

   Parameters
   ----------
   netlist : list
      Net list to convert.


   Returns
   -------
   list
       List converted to Python.


.. py:function:: pascal_to_snake(s)

.. py:function:: snake_to_pascal(s)

.. py:class:: PadGeometryTpe(*args, **kwds)

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


   .. py:attribute:: Circle
      :value: 1



   .. py:attribute:: Square
      :value: 2



   .. py:attribute:: Rectangle
      :value: 3



   .. py:attribute:: Oval
      :value: 4



   .. py:attribute:: Bullet
      :value: 5



   .. py:attribute:: NSidedPolygon
      :value: 6



   .. py:attribute:: Polygon
      :value: 7



   .. py:attribute:: Round45
      :value: 8



   .. py:attribute:: Round90
      :value: 9



   .. py:attribute:: Square45
      :value: 10



   .. py:attribute:: Square90
      :value: 11



   .. py:attribute:: InvalidGeometry
      :value: 12



.. py:class:: DielectricExtentType(*args, **kwds)

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


   .. py:attribute:: BoundingBox
      :value: 0



   .. py:attribute:: Conforming
      :value: 1



   .. py:attribute:: ConvexHull
      :value: 2



   .. py:attribute:: Polygon
      :value: 3



.. py:class:: Primitives(*args, **kwds)

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


   .. py:attribute:: Rectangle
      :value: 0



   .. py:attribute:: Circle
      :value: 1



   .. py:attribute:: Polygon
      :value: 2



   .. py:attribute:: Path
      :value: 3



   .. py:attribute:: Bondwire
      :value: 4



   .. py:attribute:: PrimitivePlugin
      :value: 5



   .. py:attribute:: Text
      :value: 6



   .. py:attribute:: Path3D
      :value: 7



   .. py:attribute:: BoardBendDef
      :value: 8



   .. py:attribute:: InValidType
      :value: 9



.. py:class:: LayoutObjType(*args, **kwds)

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


   .. py:attribute:: InvalidLayoutObj
      :value: -1



   .. py:attribute:: Primitive
      :value: 0



   .. py:attribute:: PadstackInstance
      :value: 1



   .. py:attribute:: Terminal
      :value: 2



   .. py:attribute:: TerminalInstance
      :value: 3



   .. py:attribute:: CellInstance
      :value: 4



   .. py:attribute:: Layer
      :value: 5



   .. py:attribute:: Net
      :value: 6



   .. py:attribute:: Padstack
      :value: 7



   .. py:attribute:: Group
      :value: 8



   .. py:attribute:: NetClass
      :value: 9



   .. py:attribute:: Cell
      :value: 10



   .. py:attribute:: DifferentialPair
      :value: 11



   .. py:attribute:: PinGroup
      :value: 12



   .. py:attribute:: VoltageRegulator
      :value: 13



   .. py:attribute:: ExtendedNet
      :value: 14



   .. py:attribute:: LayoutObjTypeCount
      :value: 15



