src.pyedb.generic.constants
===========================

.. py:module:: src.pyedb.generic.constants


Attributes
----------

.. autoapisummary::

   src.pyedb.generic.constants.RAD2DEG
   src.pyedb.generic.constants.DEG2RAD
   src.pyedb.generic.constants.HOUR2SEC
   src.pyedb.generic.constants.MIN2SEC
   src.pyedb.generic.constants.SEC2MIN
   src.pyedb.generic.constants.SEC2HOUR
   src.pyedb.generic.constants.INV2PI
   src.pyedb.generic.constants.V2PI
   src.pyedb.generic.constants.METER2IN
   src.pyedb.generic.constants.METER2MILES
   src.pyedb.generic.constants.MILS2METER
   src.pyedb.generic.constants.SpeedOfLight
   src.pyedb.generic.constants.AEDT_UNITS
   src.pyedb.generic.constants.SI_UNITS
   src.pyedb.generic.constants.UNIT_SYSTEM_OPERATIONS
   src.pyedb.generic.constants.CSS4_COLORS


Classes
-------

.. autoapisummary::

   src.pyedb.generic.constants.SWEEPDRAFT
   src.pyedb.generic.constants.FlipChipOrientation
   src.pyedb.generic.constants.SolverType
   src.pyedb.generic.constants.CutoutSubdesignType
   src.pyedb.generic.constants.RadiationBoxType
   src.pyedb.generic.constants.SweepType
   src.pyedb.generic.constants.BasisOrder
   src.pyedb.generic.constants.NodeType
   src.pyedb.generic.constants.SourceType
   src.pyedb.generic.constants.CommonMapper
   src.pyedb.generic.constants.TerminalTypeMapper
   src.pyedb.generic.constants.BoundaryTypeMapper
   src.pyedb.generic.constants.SourceTermMapper
   src.pyedb.generic.constants.FAdaptTypeMapper
   src.pyedb.generic.constants.MeshOperationTypeMapper
   src.pyedb.generic.constants.DCBehaviorMapper
   src.pyedb.generic.constants.SParamExtrapolationMapper
   src.pyedb.generic.constants.SparamInterpolationMapper


Functions
---------

.. autoapisummary::

   src.pyedb.generic.constants.db20
   src.pyedb.generic.constants.db10
   src.pyedb.generic.constants.dbw
   src.pyedb.generic.constants.dbm
   src.pyedb.generic.constants.fah2kel
   src.pyedb.generic.constants.cel2kel
   src.pyedb.generic.constants.unit_system
   src.pyedb.generic.constants.decompose_variable_value
   src.pyedb.generic.constants.unit_converter
   src.pyedb.generic.constants.scale_units
   src.pyedb.generic.constants.validate_enum_class_value


Module Contents
---------------

.. py:data:: RAD2DEG
   :value: 57.29577951308232


.. py:data:: DEG2RAD
   :value: 0.017453292519943295


.. py:data:: HOUR2SEC
   :value: 3600.0


.. py:data:: MIN2SEC
   :value: 60.0


.. py:data:: SEC2MIN
   :value: 0.016666666666666666


.. py:data:: SEC2HOUR
   :value: 0.0002777777777777778


.. py:data:: INV2PI
   :value: 0.15915494309189535


.. py:data:: V2PI
   :value: 6.283185307179586


.. py:data:: METER2IN
   :value: 0.0254


.. py:data:: METER2MILES
   :value: 1609.344051499


.. py:data:: MILS2METER
   :value: 39370.078740157


.. py:data:: SpeedOfLight
   :value: 299792458.0


.. py:function:: db20(x, inverse=True)

   Convert db20 to decimal and vice versa.


.. py:function:: db10(x, inverse=True)

   Convert db10 to decimal and vice versa.


.. py:function:: dbw(x, inverse=True)

   Convert W to decimal and vice versa.


.. py:function:: dbm(x, inverse=True)

   Convert W to decimal and vice versa.


.. py:function:: fah2kel(val, inverse=True)

   Convert a temperature from Fahrenheit to Kelvin.

   Parameters
   ----------
   val : float
       Temperature value in Fahrenheit.
   inverse : bool, optional
       The default is ``True``.

   Returns
   -------
   float
       Temperature value converted to Kelvin.



.. py:function:: cel2kel(val, inverse=True)

   Convert a temperature from Celsius to Kelvin.

   Parameters
   ----------
   val : float
       Temperature value in Celsius.
   inverse : bool, optional
       The default is ``True``.

   Returns
   -------
   float
       Temperature value converted to Kelvin.



.. py:function:: unit_system(units)

   Retrieve the name of the unit system associated with a unit string.

   Parameters
   ----------
   units : str
       Units for retrieving the associated unit system name.

   Returns
   -------
   str
       Key from the ``AEDT_units`` when successful. For example, ``"AngularSpeed"``.
   ``False`` when the units specified are not defined in AEDT units.



.. py:function:: decompose_variable_value(variable_value, full_variables={})

   Decompose a variable value.

   Parameters
   ----------
   variable_value : str
   full_variables : dict

   Returns
   -------
   tuples
       Tuples made of the float value of the variable and the units exposed as a string.


.. py:function:: unit_converter(values, unit_system='Length', input_units='meter', output_units='mm')

   Convert unit in specified unit system.

   Parameters
   ----------
   values : float, list
       Values to convert.
   unit_system : str
       Unit system. Default is `"Length"`.
   input_units : str
       Input units. Default is `"meter"`.
   output_units : str
       Output units. Default is `"mm"`.

   Returns
   -------
   float, list
       Converted value.


.. py:function:: scale_units(scale_to_unit)

   Find the scale_to_unit into main system unit.

   Parameters
   ----------
   scale_to_unit : str
       Unit to Scale.

   Returns
   -------
   float
       Return the scaling factor if any.


.. py:function:: validate_enum_class_value(cls, value)

   Check whether the value for the class ``enumeration-class`` is valid.

   Parameters
   ----------
   cls : class
       Enumeration-style class with integer members in range(0, N) where cls.Invalid equals N-1.
   value : int
       Value to check.

   Returns
   -------
   bool
       ``True`` when the value is valid for the ``enumeration-class``, ``False`` otherwise.


.. py:data:: AEDT_UNITS

.. py:data:: SI_UNITS

.. py:data:: UNIT_SYSTEM_OPERATIONS

.. py:class:: SWEEPDRAFT

   Bases: :py:obj:`object`


   SweepDraftType Enumerator class.


.. py:class:: FlipChipOrientation

   Bases: :py:obj:`object`


   Chip orientation enumerator class.


.. py:class:: SolverType

   Bases: :py:obj:`object`


   Provides solver type classes.


.. py:class:: CutoutSubdesignType

   Bases: :py:obj:`object`


.. py:class:: RadiationBoxType

   Bases: :py:obj:`object`


.. py:class:: SweepType

   Bases: :py:obj:`object`


.. py:class:: BasisOrder

   Bases: :py:obj:`object`


   Enumeration-class for HFSS basis order settings.


   Warning: the value ``single`` has been renamed to ``Single`` for consistency. Please update references to
   ``single``.


.. py:class:: NodeType

   Bases: :py:obj:`object`


   Type of node for source creation.


.. py:class:: SourceType

   Bases: :py:obj:`object`


   Type of excitation enumerator.


.. py:data:: CSS4_COLORS

.. py:class:: CommonMapper

   .. py:method:: get(value, *, as_grpc: bool = True)
      :classmethod:


      Bidirectional converter:
        - If 'value' is GRPC (enum or string), return the corresponding DOTNET enum (or .value if as_value=True).
        - If 'value' is DOTNET (enum or string), return the corresponding GRPC enum (or .value if as_value=True).

      Auto-detects the side by trying enum construction and membership.
      Raises ValueError on unknown inputs.



   .. py:method:: get_grpc(value)
      :classmethod:



   .. py:method:: get_dotnet(value)
      :classmethod:



.. py:class:: TerminalTypeMapper

   Bases: :py:obj:`CommonMapper`


   .. py:class:: GRPC(*args, **kwds)

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



   .. py:class:: DOTNET(*args, **kwds)

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



.. py:class:: BoundaryTypeMapper

   Bases: :py:obj:`CommonMapper`


   .. py:class:: GRPC(*args, **kwds)

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



   .. py:class:: DOTNET(*args, **kwds)

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



.. py:class:: SourceTermMapper

   Bases: :py:obj:`CommonMapper`


   .. py:class:: GRPC(*args, **kwds)

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



   .. py:class:: DOTNET(*args, **kwds)

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



.. py:class:: FAdaptTypeMapper

   Bases: :py:obj:`CommonMapper`


   .. py:class:: GRPC(*args, **kwds)

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



   .. py:class:: DOTNET(*args, **kwds)

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



.. py:class:: MeshOperationTypeMapper

   Bases: :py:obj:`CommonMapper`


   .. py:class:: GRPC(*args, **kwds)

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



   .. py:class:: DOTNET(*args, **kwds)

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



.. py:class:: DCBehaviorMapper

   Bases: :py:obj:`CommonMapper`


   .. py:class:: GRPC(*args, **kwds)

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



   .. py:class:: DOTNET(*args, **kwds)

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



.. py:class:: SParamExtrapolationMapper

   Bases: :py:obj:`CommonMapper`


   .. py:class:: GRPC(*args, **kwds)

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



   .. py:class:: DOTNET(*args, **kwds)

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



.. py:class:: SparamInterpolationMapper

   Bases: :py:obj:`CommonMapper`


   .. py:class:: GRPC(*args, **kwds)

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



   .. py:class:: DOTNET(*args, **kwds)

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



