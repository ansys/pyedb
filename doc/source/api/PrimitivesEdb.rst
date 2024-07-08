Modeler & primitives
====================
These classes are the containers of primitives and all relative methods.
Primitives are planes, lines, rectangles, and circles.


.. code:: python

    from pyedb import Edb

    edb = Edb(myedb, edbversion="2023.1")

    top_layer_obj = edb.modeler.create_rectangle(
        "TOP", net_name="gnd", lower_left_point=plane_lw_pt, upper_right_point=plane_up_pt
    )

    ...

.. currentmodule:: pyedb.dotnet.edb_core.modeler

.. autosummary::
   :toctree: _autosummary
   :nosignatures:


   Modeler


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
