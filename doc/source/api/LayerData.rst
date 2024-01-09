Stackup & layers
================
These classes are the containers of the layer and stackup manager of the EDB API.


.. code:: python

    from pyedb.legacy.edb_core.edb import Edb

    edb = Edb(myedb, edbversion="2023.1")

    # this call returns the EDBLayers class
    layer = edb.stackup.stackup_layers

    # this call returns the EDBLayer class
    layer = edb.stackup["TOP"]
    ...


.. currentmodule:: pyedb.legacy.edb_core.stackup

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   Stackup


.. currentmodule:: pyedb.legacy.edb_core.edb_data.layer_data

.. autosummary::
   :toctree: _autosummary
   :nosignatures:


   LayerEdbClass


