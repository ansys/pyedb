.. _cutout_example:

Clip a design
=============
Most of the time, only a specific part of a layout needs to be simulated. Thus, you want to
clip the design to reduce computer resources and speed up the simulation.

This page shows how to clip a design based on net selection.

.. autosummary::
   :toctree: _autosummary

.. code:: python

    from pyedb.dotnet.edb import Edb
    from pyedb.generic.general_methods import generate_unique_folder_name
    import pyedb.misc.downloads as downloads


    # Ansys release version
    ansys_version = "2024.1"

    # download and copy the layout file from examples
    temp_folder = generate_unique_folder_name()
    targetfile = downloads.download_file("edb/ANSYS-HSD_V1.aedb", destination=temp_folder)

    # load EDB
    edbapp = Edb(edbpath=targetfile, edbversion="2024.1")

    # select signal nets to evaluate the extent for clipping the layout
    signal_nets = [
        "DDR4_DQ0",
        "DDR4_DQ1",
        "DDR4_DQ2",
        "DDR4_DQ3",
        "DDR4_DQ4",
        "DDR4_DQ5",
        "DDR4_DQ6",
        "DDR4_DQ7",
    ]
    # At least one reference net must be included. Reference nets are included in the design but clipped.
    reference_nets = ["GND"]
    # Define the expansion factor, which gives the distance for evaluating the cutout extent. This code defines a cutout.
    expansion = 0.01  # 1cm in this case
    # process cutout
    edbapp.cutout(
        signal_list=signal_nets, reference_list=reference_nets, expansion_size=expansion
    )
    # save and close project
    edbapp.save_edb()
    edbapp.close_edb()

.. image:: ../../resources/clipped_layout.png
  :width: 800
  :alt: Clipped design