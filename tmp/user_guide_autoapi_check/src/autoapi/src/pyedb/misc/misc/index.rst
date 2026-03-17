src.pyedb.misc.misc
===================

.. py:module:: src.pyedb.misc.misc

.. autoapi-nested-parse::

   Miscellaneous Methods for PyEDB.



Functions
---------

.. autoapisummary::

   src.pyedb.misc.misc.list_installed_ansysem
   src.pyedb.misc.misc.installed_versions
   src.pyedb.misc.misc.current_version
   src.pyedb.misc.misc.current_student_version


Module Contents
---------------

.. py:function:: list_installed_ansysem() -> list[str]

   Return a list of installed AEDT versions on ``ANSYSEM_ROOT``.

   Returns
   -------
   list[str]
       List of environment variable names for installed AEDT versions.

   Examples
   --------
   >>> from pyedb.misc.misc import list_installed_ansysem
   >>> versions = list_installed_ansysem()
   >>> versions
   ['ANSYSEM_ROOT241', 'ANSYSEM_ROOT232']



.. py:function:: installed_versions() -> dict[str, str]

   Get the installed AEDT versions.

   Returns
   -------
   dict[str, str]
       Dictionary with version as the key and installation path as the value.

   Examples
   --------
   >>> from pyedb.misc.misc import installed_versions
   >>> versions = installed_versions()
   >>> versions
   {'2024.1': 'C:/Program Files/AnsysEM/v241/Win64', '2023.2': 'C:/Program Files/AnsysEM/v232/Win64'}



.. py:function:: current_version() -> str

   Get the current AEDT version.

   Returns
   -------
   str
       Current AEDT version string, or empty string if no version is found.

   Examples
   --------
   >>> from pyedb.misc.misc import current_version
   >>> version = current_version()
   >>> version
   '2024.1'



.. py:function:: current_student_version() -> str

   Get the current AEDT student version.

   Returns
   -------
   str
       Current AEDT student version string with 'SV' suffix, or empty string if no student version is found.

   Examples
   --------
   >>> from pyedb.misc.misc import current_student_version
   >>> version = current_student_version()
   >>> version
   '2024.1SV'



