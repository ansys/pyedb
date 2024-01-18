.. _ref_user_guide:

==========
User guide
==========

.. toctree::
   :maxdepth: 3
   load_export_edb/index
   edb_information_queries/index
   build_simulation_project/index
   excitations/index
   simulation_setup/index
   layer_stackup/index
   padstacks/index
   components/index
   parametrization/index

This section provides a general overview of PyEDB and how you use it.
PyEDB is loading ANSYS EDB in memory meaning non graphically.
To use PyEDB you must follow the installation step :ref:`ref_install_pyedb`.

The first step usually is to load an existing AEDB file or create a new one.
To open an AEDB file you will need to instantiate a new Edb class.

.. code:: python

    from pyedb.legacy.edb_core.edb import EdbLegacy as Edb

    edb_file = r"C:\Temp\my_edb.aedb"
    edb = Edb(edb_file)

Note that if you want to create an empty one you just need to instantiate the class without providing AEDB file path
as argument. You can also check these examples to load and export EDB.



Once the EDB loaded in memory you can start performing operations on it.
For getting general information's on the layout you can check these examples:


To build simulation projects for SI-PI using HFSS or SIwave:


Creating excitations:



Create Simulation setup:


Manage layer stackup:



Creating and editing padstack definition's:


Create components and query information's on them:


Create parametrized project's:

.. toctree::
   :maxdepth: 2





