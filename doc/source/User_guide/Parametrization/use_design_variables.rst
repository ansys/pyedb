Define design variables
=======================
This section shows how to use variables with EDB:

.. autosummary::
   :toctree: _autosummary

.. code:: python



    from pyedb.legacy.edb import EdbLegacy
    from pyedb.generic.general_methods import generate_unique_folder_name
    import pyedb.misc.downloads as downloads

    temp_folder = generate_unique_folder_name()
    targetfile = downloads.download_file("edb/ANSYS-HSD_V1.aedb", destination=temp_folder)
    edbapp = EdbLegacy(edbpath=targetfile, edbversion="2023.2")

    # adding design variable
    edbapp.add_design_variable("my_variable", "1mm")

    # parametrize trace width
    edbapp.modeler.parametrize_trace_width("A0_N")
    edbapp.modeler.parametrize_trace_width("A0_N_R")

    # adding project variable
    edbapp.add_project_variable("$my_project_variable", "3mm")

