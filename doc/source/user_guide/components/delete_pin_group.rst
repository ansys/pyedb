.. _delete_pingroup_example:

Delete pin group
================
This section describes how to delete pin group.

.. autosummary::
   :toctree: _autosummary

.. code:: python



    from pyedb.dotnet.edb import Edb

    # loading EDB
    edbapp = Edb(edbpath=targetfile, edbversion="2023.2")

    for _, pingroup in edbapp.siwave.pin_groups.items():
        ingroup.delete()
    edbapp.close()