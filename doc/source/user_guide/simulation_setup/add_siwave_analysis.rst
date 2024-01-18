Adding Siwave analysis
======================
This section shows how to add Siwave analysis:

.. autosummary::
   :toctree: _autosummary

.. code:: python



    from pyedb.dotnet import Edb
    from pyedb.generic.general_methods import generate_unique_folder_name
    import pyedb.misc.downloads as downloads

    temp_folder = generate_unique_folder_name()
    targetfile = downloads.download_file("edb/ANSYS-HSD_V1.aedb", destination=temp_folder)
    edbapp = Edb(edbpath=targetfile, edbversion="2023.2")

    # Adding Siwave SYZ analysis
    edbapp.siwave.add_siwave_syz_analysis(
        start_freq="=GHz", stop_freq="10GHz", step_freq="10MHz"
    )

    # Adding DC analysis
    edbapp.siwave.add_siwave_dc_analysis(name="Test_dc")
