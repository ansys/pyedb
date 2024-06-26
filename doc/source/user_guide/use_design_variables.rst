.. _use_design_variables_example:

Define design variables
=======================

This page shows how to define design variables for use by EDB.

.. autosummary::
   :toctree: _autosummary

.. code:: python

    from pyedb import Edb
    from pyedb.generic.general_methods import generate_unique_folder_name
    import pyedb.misc.downloads as downloads

    temp_folder = generate_unique_folder_name()
    targetfile = downloads.download_file("edb/ANSYS-HSD_V1.aedb", destination=temp_folder)
    edbapp = Edb(edbpath=targetfile, edbversion="2024.1")

    # adding design variable
    edbapp.add_design_variable("my_variable", "1mm")

    # parametrize trace width
    edbapp.modeler.parametrize_trace_width("A0_N")
    edbapp.modeler.parametrize_trace_width("A0_N_R")

    # adding project variable
    edbapp.add_project_variable("$my_project_variable", "3mm")

