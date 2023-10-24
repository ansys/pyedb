EDB Queries
===========
PyEBD allows layout information queries, this section describe some basic examples:

- Load EDB
.. code:: python
   # loading EDB
   edbapp = Edb(edbpath=targetfile, edbversion=desktop_version)

- Getting layout statistics
.. code:: python
   stats = edbapp.get_statistics()

- Nets
.. code:: python
   # net list
   nets.netlist
   # power nets
   nets.power
   # Plotting layout in matplotlib
   edbapp.nets.plot(None)
. image:: ../Resources/layout_plot_all_nets.png
   :width: 800
   :alt: Plot all nets

- Components
.. code:: python
   # Getting all components
   nets = edbapp.components.instances
   # Getting pins from components connected to given net
   u9_gnd_pins = [pin for pin in list(edbapp.components["U9"].pins.values()) if pin.net_name == "GND"]

. image:: ../Resources/aedt_box.png
  :width: 800
  :alt: Modeler Object
