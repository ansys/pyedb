src.pyedb.dotnet.database.edb_data.sources
==========================================

.. py:module:: src.pyedb.dotnet.database.edb_data.sources


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.edb_data.sources.Node
   src.pyedb.dotnet.database.edb_data.sources.SourceBuilder
   src.pyedb.dotnet.database.edb_data.sources.PinGroup
   src.pyedb.dotnet.database.edb_data.sources.CircuitPortBuilder
   src.pyedb.dotnet.database.edb_data.sources.VoltageSourceBuilder
   src.pyedb.dotnet.database.edb_data.sources.CurrentSourceBuilder
   src.pyedb.dotnet.database.edb_data.sources.DCTerminal
   src.pyedb.dotnet.database.edb_data.sources.ResistorSourceBuilder


Module Contents
---------------

.. py:class:: Node

   Bases: :py:obj:`object`


   Provides for handling nodes for Siwave sources.


   .. py:property:: component

      Component name containing the node.



   .. py:property:: net

      Net of the node.



   .. py:property:: node_type

      Type of the node.



   .. py:property:: name

      Name of the node.



.. py:class:: SourceBuilder

   Bases: :py:obj:`object`


   Provides for handling Siwave sources.


   .. py:property:: name

      SourceBuilder name.



   .. py:property:: source_type

      SourceBuilder type.



   .. py:property:: positive_node

      Positive node of the source.



   .. py:property:: negative_node

      Negative node of the source.



   .. py:property:: amplitude

      Amplitude value of the source. Either amperes for current source or volts for
      voltage source.



   .. py:property:: phase

      Phase of the source.



   .. py:property:: impedance

      Impedance values of the source.



   .. py:property:: r_value


   .. py:property:: l_value


   .. py:property:: c_value


   .. py:property:: create_physical_resistor


.. py:class:: PinGroup(name='', edb_pin_group=None, pedb=None)

   Bases: :py:obj:`object`


   Manages pin groups.


   .. py:property:: name

      Name.



   .. py:property:: component

      Component.



   .. py:property:: pins

      Gets the pins belong to this pin group.



   .. py:method:: remove_pins(pins: Union[str, List[str]])

      Remove pins from the pin group.

      Parameters
      ----------
      pins : str, list
          List of padstack instance names.




   .. py:property:: node_pins

      Node pins.



   .. py:property:: net

      Net.



   .. py:property:: net_name


   .. py:method:: get_terminal(name=None, create_new_terminal=False)

      Terminal.



   .. py:property:: terminal

      Terminal.



   .. py:method:: create_terminal(name=None)

      Create a terminal.

      Parameters
      ----------
      name : str, optional
          Name of the terminal.



   .. py:method:: create_current_source_terminal(magnitude=1, phase=0)


   .. py:method:: create_voltage_source_terminal(magnitude=1, phase=0, impedance=0.001)


   .. py:method:: create_voltage_probe_terminal(impedance=1000000)


   .. py:method:: create_port_terminal(impedance=50)


   .. py:method:: delete()

      Delete active pin group.

      Returns
      -------
      bool




.. py:class:: CircuitPortBuilder(impedance='50')

   Bases: :py:obj:`SourceBuilder`, :py:obj:`object`


   Manages a circuit port.


   .. py:property:: impedance

      Impedance.



   .. py:property:: get_type

      Get type.



.. py:class:: VoltageSourceBuilder

   Bases: :py:obj:`SourceBuilder`


   Manages a voltage source.


   .. py:property:: magnitude

      Magnitude.



   .. py:property:: phase

      Phase.



   .. py:property:: impedance

      Impedance.



   .. py:property:: source_type

      SourceBuilder type.



.. py:class:: CurrentSourceBuilder

   Bases: :py:obj:`SourceBuilder`


   Manages a current source.


   .. py:property:: magnitude

      Magnitude.



   .. py:property:: phase

      Phase.



   .. py:property:: impedance

      Impedance.



   .. py:property:: source_type

      SourceBuilder type.



.. py:class:: DCTerminal

   Bases: :py:obj:`SourceBuilder`


   Manages a dc terminal source.


   .. py:property:: source_type

      SourceBuilder type.



.. py:class:: ResistorSourceBuilder

   Bases: :py:obj:`SourceBuilder`


   Manages a resistor source.


   .. py:property:: rvalue

      Resistance value.



   .. py:property:: source_type

      SourceBuilder type.



