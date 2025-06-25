Sources and excitations
=======================
These classes are the containers of sources methods of the EDB for both HFSS and SIwave.


.. code:: python

    from pyedb.grpc.edb import Edb

    edb = Edb(myedb, edbversion="2025.2")

    # this call returns the EDB excitations dictionary
    edb.excitations
    ...


.. currentmodule:: pyedb.grpc.database

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   nets.Nets
