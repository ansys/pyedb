Ports
=====
These classes are the containers of ports methods of the EDB for both HFSS and Siwave.

.. autosummary::
   :toctree: _autosummary

.. code:: python

    from from pyedb.legacy.edb_core.edb import Edb
    edb = Edb(myedb, edbversion="2023.1")

    # this call returns the EDB excitations dictionary
    edb.ports
    ...


.. currentmodule:: pyedb.legacy.edb_core.edb_data.ports

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   GapPort
   WavePort
