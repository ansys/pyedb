Delete pin group
================
This section describes how to delete pin group.

.. autosummary::
   :toctree: _autosummary

.. code:: python



    from pyedb.legacy.edb_core.edb import EdbLegacy

    # loading EDB
    edbapp = EdbLegacy(edbpath=targetfile, edbversion="2023.2")

    for _, pingroup in edbapp.siwave.pin_groups.items():
        ingroup.delete()
    edbapp.close()