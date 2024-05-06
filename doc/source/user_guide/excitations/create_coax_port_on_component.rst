.. _create_coaxial_port_on_component_example:

Create a coaxial port
=====================

This page shows how to create an HFSS coaxial port on a component.

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

    edbapp.hfss.create_coax_port_on_component("U1", ["DDR4_DQS0_P", "DDR4_DQS0_N"])
    edbapp.save_edb()
    edbapp.close_edb()

The preceding code creates a coaxial port on nets ``DDR4_DSQ0_P`` and ``DDR4_DSQ0_N`` from component ``U1``:

.. image:: ../../Resources/create_port_on_component_simple.png
..   :width: 800
..   :alt: HFSS coaxial port created on a component