.. _ref_user_guide:

==========
User guide
==========

This section provides a general overview of PyEDB and how you use it.

.. toctree::
   :maxdepth: 2
   :includehidden:

   excitations/index
   simulation_setup/index
   edb_information_queries/index
   load_export_edb/index
   build_simulation_project
   padstacks/index
   layer_stackup/index
   components/index
   parametrization/index


PyEDB is loading ANSYS EDB in memory meaning non graphically.

.. code:: python

    # Load EDB

    from pyedb.legacy.edb_core.edb import EdbLegacy

    edb_file = pyedb.layout_examples.ANSYS_HSD_v1.aedb
    edb = EdbLegacy(edb_file)

To use PyEDB you must follow the installation step :ref:`ref_install_pyedb`.
