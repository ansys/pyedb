src.pyedb.grpc.database.utility.sources
=======================================

.. py:module:: src.pyedb.grpc.database.utility.sources


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.utility.sources.Node
   src.pyedb.grpc.database.utility.sources.Source
   src.pyedb.grpc.database.utility.sources.CircuitPort
   src.pyedb.grpc.database.utility.sources.VoltageSource
   src.pyedb.grpc.database.utility.sources.CurrentSource
   src.pyedb.grpc.database.utility.sources.DCTerminal
   src.pyedb.grpc.database.utility.sources.ResistorSource


Module Contents
---------------

.. py:class:: Node

   Provides for handling nodes for Siwave sources.


   .. py:property:: component
      :type: str


      Component name containing the node.



   .. py:property:: net

      Net of the node.



   .. py:property:: node_type

      Type of the node.



   .. py:property:: name

      Name of the node.



.. py:class:: Source(pedb)

   Bases: :py:obj:`object`


   Provides for handling Siwave sources.


   .. py:property:: name

      Source name.



   .. py:property:: source_type

      Source type.



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


.. py:class:: CircuitPort(pedb, impedance='50')

   Bases: :py:obj:`Source`


   Manages a circuit port.


   .. py:property:: impedance

      Impedance.



   .. py:property:: get_type

      Get type.



.. py:class:: VoltageSource

   Bases: :py:obj:`Source`


   Manages a voltage source.


   .. py:property:: magnitude

      Magnitude.



   .. py:property:: phase

      Phase.



   .. py:property:: impedance

      Impedance.



   .. py:property:: source_type

      Source type.



.. py:class:: CurrentSource

   Bases: :py:obj:`Source`


   Manages a current source.


   .. py:property:: magnitude

      Magnitude.



   .. py:property:: phase

      Phase.



   .. py:property:: impedance

      Impedance.



   .. py:property:: source_type

      Source type.



.. py:class:: DCTerminal

   Bases: :py:obj:`Source`


   Manages a dc terminal source.


   .. py:property:: source_type

      Source type.



.. py:class:: ResistorSource

   Bases: :py:obj:`Source`


   Manages a resistor source.


   .. py:property:: rvalue

      Resistance value.



   .. py:property:: source_type

      Source type.



