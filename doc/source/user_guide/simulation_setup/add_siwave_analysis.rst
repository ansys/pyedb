.. _add_siwave_setup_example:

Set up a SIwave analysis
========================

This page shows how to create and set up a SIwave SYZ analysis.

.. autosummary::
   :toctree: _autosummary

.. code:: python

    from pyedb import Edb
    from pyedb.generic.general_methods import generate_unique_folder_name
    import pyedb.misc.downloads as downloads

    temp_folder = generate_unique_folder_name()
    targetfile = downloads.download_file("edb/ANSYS-HSD_V1.aedb", destination=temp_folder)
    edbapp = Edb(edbpath=targetfile, edbversion="2024.2")

    # Add SIwave SYZ analysis
    edbapp.siwave.add_siwave_syz_analysis(
        start_freq="=GHz", stop_freq="10GHz", step_freq="10MHz"
    )

    # Add DC analysis
    edbapp.siwave.add_siwave_dc_analysis(name="Test_dc")
    edbapp.save()
    edbapp.close()


.. image:: ../../resources/add_siwave_setup.png
  :width: 400
  :alt: Add SIwave setup
