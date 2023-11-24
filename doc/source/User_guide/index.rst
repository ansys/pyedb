.. _ref_user_guide:

==========
User guide
==========
PyEDB is loading ANSYS EDB in memory meaning non graphically.


.. code:: python

    # Load EDB

    from pyedb.legacy.edb_core.edb import EdbLegacy
    edb_file = pyedb.layout_examples.ANSYS_HSD_v1.aedb
    edb = EdbLegacy(edb_file)


   loading_layout
   edb_queries
   cutout
   layer_stackup
   ports
   simulation_setup

