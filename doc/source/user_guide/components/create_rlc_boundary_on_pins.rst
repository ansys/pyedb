.. _create_rlc_boundary_on_pin_example:

Create an RLC boundary on pins
==============================

This page shows how to create an RLC boundary on pins.

.. autosummary::
   :toctree: _autosummary

.. code:: python

    from pyedb.dotnet.edb import Edb
    from pyedb.generic.general_methods import generate_unique_folder_name
    import pyedb.misc.downloads as downloads

    # download and open EDB project
    temp_folder = generate_unique_folder_name()
    targetfile = downloads.download_file("edb/ANSYS-HSD_V1.aedb", destination=temp_folder)
    edbapp = Edb(edbpath=targetfile, edbversion="2024.1")

    # retrieve pins from ``U1`` component and ``1V0`` net
    pins = edbapp.components.get_pin_from_component("U1", "1V0")

    # reference pins
    ref_pins = edbapp.components.get_pin_from_component("U1", "GND")

    # create rlc boundary
    edbapp.hfss.create_rlc_boundary_on_pins(
        pins[0], ref_pins[0], rvalue=1.05, lvalue=1.05e-12, cvalue=1.78e-13
    )

    # close EDB
    edbapp.save_edb()
    edbapp.close_edb()


.. image:: ../../resources/create_rlc_boundary_on_pin.png
  :width: 800
  :alt: RLC boundary created on pins