.. _edb_queries_example:

Get layout statistics
=====================

PyEDB allows you to query a layout for statistics. This page shows how to perform
these tasks:

- Load a layout.
- Get statistics.
- Get nets and plot them in matplotlib.
- Get all components and then get pins from components connected to a given net.

.. autosummary::
   :toctree: _autosummary

Load a layout
~~~~~~~~~~~~~

.. code:: python


    # import EDB and load a layout
    from pyedb import Edb
    from pyedb.generic.general_methods import generate_unique_folder_name
    import pyedb.misc.downloads as downloads

    temp_folder = generate_unique_folder_name()
    targetfile = downloads.download_file("edb/ANSYS-HSD_V1.aedb", destination=temp_folder)
    edbapp = Edb(edbpath=targetfile, edbversion="2024.2")

Get statistics
~~~~~~~~~~~~~~

.. code:: python

    stats = edbapp.get_statistics()

.. image:: ../../resources/layout_stats.png
   :width: 400
   :alt: Layout stats

Get nets and plot them in matplotlib
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

   # net list
   edbapp.nets.netlist
   # power nets
   nets.power
   # Plot nets in matplotlib
   edbapp.nets.plot(None)

.. image:: ../../resources/layout_plot_all_nets.png
   :width: 800
   :alt: Plot all nets in matplotlib

Get all components and then pins from components connected to a net
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

   # Get all components
   nets = edbapp.components.instances
   # Get pins from components connected to a given net
   u9_gnd_pins = [
       pin for pin in list(edbapp.components["U9"].pins.values()) if pin.net_name == "GND"
   ]
