.. _create_resistor_on_pin_example:

Create resistor boundary between pins
=====================================
This section describes how to create resistor on pins:

.. autosummary::
   :toctree: _autosummary

.. code:: python



    from pyedb.dotnet.edb import Edb
    from pyedb.generic.general_methods import generate_unique_folder_name
    import pyedb.misc.downloads as downloads

    temp_folder = generate_unique_folder_name()
    targetfile = downloads.download_file("edb/ANSYS-HSD_V1.aedb", destination=temp_folder)
    edbapp = Edb(edbpath=targetfile, edbversion="2023.2")

    pins = edbapp.components.get_pin_from_component("U1")
    resistor = edbapp.siwave.create_resistor_on_pin(pins[302], pins[10], 40, "RST4000")


