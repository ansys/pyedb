Modeler & primitives
====================
These classes are the containers of primitives and all relative methods.
Primitives are planes, lines, rectangles, and circles.


Primitives properties
---------------------
These classes are the containers of data management for primitives and arcs.

.. currentmodule:: pyedb.dotnet.edb_core.edb_data.primitives_data

.. autosummary::
   :toctree: _autosummary
   :nosignatures:


   EDBPrimitives
   EDBArcs


.. code:: python

    from pyedb import Edb

    edb = Edb(myedb, edbversion="2023.1")

    polygon = edbapp.modeler.polygons[0]
    polygon.is_void
    poly2 = polygon.clone()

    ...
