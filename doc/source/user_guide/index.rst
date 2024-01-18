.. _ref_user_guide:

==========
User guide
==========

This section provides a general overview of PyEDB and how you use it.

.. toctree::
   :maxdepth: 2
   :hidden:

   excitations/index
   simulation_setup/index
   edb_information_queries/index
   load_export_edb/index
   build_simulation_project/index
   padstacks/index
   layer_stackup/index
   components/index
   parametrization/index


PyEDB is loading ANSYS EDB in memory meaning non graphically.

.. code:: python

    # Load EDB

    from pyedb.dotnet import Edb

    edb_file = pyedb.layout_examples.ANSYS_HSD_v1.aedb
    edb = Edb(edb_file)

To use PyEDB you must follow the installation step :ref:`ref_install_pyedb`.
