Modeler & primitives
====================
These classes are the containers of primitives and all relative methods.
Primitives are planes, lines, rectangles, and circles.


Primitives properties
---------------------
These classes are the containers of data management for primitives and arcs.

.. currentmodule:: pyedb.grpc.database

.. autosummary::
   :toctree: _autosummary
   :nosignatures:


   modeler.Modeler


.. code:: python

    from pyedb.grpc.edb import Edb

    edb = Edb(myedb, edbversion="2025.2")

    polygon = edbapp.modeler.polygons[0]
    polygon.is_void
    poly2 = polygon.clone()

    ...
