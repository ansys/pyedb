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

.. toctree::
   :hidden:
   :maxdepth: 2


   Excitations/index
   Simulation_setup/index
   Edb_information_queries/index
   Load_export_edb/index
   Build_simulation_project/index
   Padstacks/index
   Layer_stackup/index
   Components/index
   Parametrization/index