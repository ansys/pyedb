src.pyedb.generic.data_handlers
===============================

.. py:module:: src.pyedb.generic.data_handlers


Attributes
----------

.. autoapisummary::

   src.pyedb.generic.data_handlers.RKM_MAPS
   src.pyedb.generic.data_handlers.UNIT_VAL


Functions
---------

.. autoapisummary::

   src.pyedb.generic.data_handlers.format_decimals
   src.pyedb.generic.data_handlers.random_string
   src.pyedb.generic.data_handlers.unique_string_list
   src.pyedb.generic.data_handlers.string_list
   src.pyedb.generic.data_handlers.ensure_list
   src.pyedb.generic.data_handlers.from_rkm
   src.pyedb.generic.data_handlers.str_to_bool
   src.pyedb.generic.data_handlers.float_units
   src.pyedb.generic.data_handlers.json_to_dict


Module Contents
---------------

.. py:data:: RKM_MAPS

.. py:data:: UNIT_VAL

.. py:function:: format_decimals(el: int | str) -> str

   Format a number with appropriate decimal places and commas.

   Parameters
   ----------
   el : int or str
       The number to format.

   Returns
   -------
   str
       The formatted number as a string, with commas and appropriate decimal places.


.. py:function:: random_string(length: int = 6, only_digits: bool = False, char_set: str | None = None) -> str

   Generate a random string

   Parameters
   ----------
   length : int
       Length of the random string. Default value is ``6``.
   only_digits : bool, optional
       Whether only digits are to be included. Default is ``False``.
   char_set : str, optional
       Custom character set to pick the characters from. By default chooses from
       ASCII and digit characters or just digits if ``only_digits`` is ``True``.

   Returns
   -------
   str
       Random string of specified length.


.. py:function:: unique_string_list(element_list: str | Iterable[str], only_string: bool = True) -> list[str]

   Return a unique list of strings from an element list.

   Parameters
   ----------
   element_list : str or Iterable[str]
       The input element(s) to be converted to a unique list of strings.
   only_string : bool, optional
       Whether only strings are allowed in the input list. Default is ``True``.

   Returns
   -------
   list[str]
       A unique list of strings without duplicates.


.. py:function:: string_list(element_list: str | list) -> list[str]

   Return a list of strings from a string or a list of strings.

   Parameters
   ----------
   element_list : str or list
       The input element(s) to be converted to a list of strings.

   Returns
   -------
   list[str]
       A list of strings.


.. py:function:: ensure_list(element_list: Any) -> list[Any]

   Check if the input is a list, if not, convert it to a list.

   Parameters
   ----------
   element_list : Any
       The input element(s) to be converted to a list.

   Returns
   -------
   list[Any]
       A list containing the input element(s).


.. py:function:: from_rkm(code: str) -> str

   Convert an RKM code string to a string with a decimal point.

   Parameters
   ----------
   code : str
       RKM code string.

   Returns
   -------
   str
       String with a decimal point and an R value.

   Examples
   --------
   >>> from_rkm("R47")
   '0.47'

   >>> from_rkm("4R7")
   '4.7'

   >>> from_rkm("470R")
   '470'

   >>> from_rkm("4K7")
   '4.7k'

   >>> from_rkm("47K")
   '47k'

   >>> from_rkm("47K3")
   '47.3k'

   >>> from_rkm("470K")
   '470k'

   >>> from_rkm("4M7")
   '4.7M'



.. py:function:: str_to_bool(s: str) -> bool | str

   Convert a ``"True"`` or ``"False"`` string to its corresponding Boolean value.

   If the passed arguments are not relevant in the context of conversion, the argument
   itself is returned. This method can be called using the ``map()`` function to
   ensure conversion of Boolean strings in a list.

   The method is not case-sensitive:

       - ``True`` is returned if the input is ``"true"``, ``"1"``, `"yes"``, or ``"y"``;
       - ``False`` is returned if the input is ``"false"``, ``"no"``, ``"n"``,  or ``"0"``.
       - Otherwise, the input value is passed through the method unchanged.

   Parameters
   ----------
   s: str

   Returns
   -------
   bool or str


.. py:function:: float_units(val_str: str, units: str = '') -> float

   Retrieve units for a value.

   Parameters
   ----------
   val_str : str
       Name of the float value.

   units : str, optional
        The default is ``""``.

   Returns
   -------
   float
        The value of the float with the appropriate units.


.. py:function:: json_to_dict(fn: str) -> dict[str, Any]

   Load JSON file to a dictionary.

   Parameters
   ----------
   fn : str
       JSON file full path.

   Returns
   -------
   dict[str, Any]


