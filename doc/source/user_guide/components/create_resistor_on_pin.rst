.. _create_resistor_on_pin_example:

Create a resistor boundary on pins
==================================

This page shows how to create a resistor boundary on pins:

.. autosummary::
   :toctree: _autosummary

.. code:: python

    from pyedb import Edb
    from pyedb.generic.general_methods import generate_unique_folder_name
    import pyedb.misc.downloads as downloads

    temp_folder = generate_unique_folder_name()
    targetfile = downloads.download_file("edb/ANSYS-HSD_V1.aedb", destination=temp_folder)
    edbapp = Edb(edbpath=targetfile, edbversion="2024.1")

    pins = edbapp.components.get_pin_from_component("U1")
    resistor = edbapp.siwave.create_resistor_on_pin(pins[302], pins[10], 40, "RST4000")
    edbapp.save_edb()
    edbapp.close_edb()


.. image:: ../../resources/create_resistor_boundary_user_guide.png
  :width: 800
  :alt: Created resistor boundary
