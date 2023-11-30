EDB queries
===========
PyEDB allows layout information queries, this section describe some basic examples:

.. autosummary::
   :toctree: _autosummary

- Load EDB

.. code:: python


    # loading EDB
    from pyedb.legacy.edb import EdbLegacy
    from pyedb.generic.general_methods import generate_unique_folder_name
    import pyedb.misc.downloads as downloads

    temp_folder = generate_unique_folder_name()
    targetfile = downloads.download_file('edb/ANSYS-HSD_V1.aedb', destination=temp_folder)
    edbapp = EdbLegacy(edbpath=targetfile, edbversion="2023.2")

- Getting layout statistics

.. code:: python


    stats = edbapp.get_statistics()


- Nets

.. code:: python



   # net list
   edbapp.nets.netlist
   # power nets
   nets.power
   # Plotting layout in matplotlib
   edbapp.nets.plot(None)

.. image:: ../../Resources/layout_plot_all_nets.png
   :width: 800
   :alt: Plot all nets

- Components

.. code:: python



   # Getting all components
   nets = edbapp.components.instances
   # Getting pins from components connected to given net
   u9_gnd_pins = [pin for pin in list(edbapp.components["U9"].pins.values()) if pin.net_name == "GND"]
