src.pyedb.generic.general_methods
=================================

.. py:module:: src.pyedb.generic.general_methods


Functions
---------

.. autoapisummary::

   src.pyedb.generic.general_methods.installed_ansys_em_versions


Module Contents
---------------

.. py:function:: installed_ansys_em_versions() -> dict[str, str]

   Retrieve paths of installed ANSYS EM versions.

   Scan the environment variables and return a dict of the form
   {version: installation_path} for every ANSYS EM release found.
   Versions are ordered from the oldest to the latest (latest appears last).

   Returns
   -------
   Dict[str, str]
       Dictionary of the form {version: installation_path} for every ANSYS EM release found.


