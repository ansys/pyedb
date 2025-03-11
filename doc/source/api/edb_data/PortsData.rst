Ports
=====
These classes are the containers of ports methods of the EDB for both HFSS and SIwave.

.. autosummary::
   :toctree: _autosummary

.. code:: python

    from pyedb import Edb

    edb = Edb(myedb, edbversion="2023.1")

    # this call returns the EDB excitations dictionary
    edb.ports
    ...


.. currentmodule:: pyedb.dotnet.edb_core.edb_data.ports

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   GapPort
   WavePort
