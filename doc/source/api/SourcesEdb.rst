Sources and excitations
=======================
These classes are the containers of sources methods of the EDB for both HFSS and Siwave.


.. code:: python

    from pyedb.legacy.edb_core.edb import Edb

    edb = Edb(myedb, edbversion="2023.1")

    # this call returns the EDB excitations dictionary
    edb.excitations
    ...


.. currentmodule:: pyedb.legacy.edb_core.edb_data.sources

.. autosummary::
   :toctree: _autosummary
   :nosignatures:
