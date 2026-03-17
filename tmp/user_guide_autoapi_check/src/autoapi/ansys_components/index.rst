ansys_components
================

.. py:module:: ansys_components


Attributes
----------

.. autoapisummary::

   ansys_components.Network


Classes
-------

.. autoapisummary::

   ansys_components.ComponentLib
   ansys_components.Series
   ansys_components.ComponentPart


Module Contents
---------------

.. py:data:: Network
   :value: None


.. py:class:: ComponentLib

   Handle component libraries.


   .. py:attribute:: capacitors


   .. py:attribute:: inductors


   .. py:attribute:: path
      :value: ''



   .. py:attribute:: series


.. py:class:: Series

   Handle component series.


.. py:class:: ComponentPart(name, index, sbin_file)

   Handle component part definition.


   .. py:attribute:: name


   .. py:attribute:: nb_ports
      :value: 2



   .. py:attribute:: nb_freq
      :value: 0



   .. py:attribute:: ref_impedance
      :value: 50.0



   .. py:attribute:: type
      :value: ''



   .. py:property:: s_parameters
      :type: skrf.network.Network


      Return a skrf.network.Network object.

      See `scikit-rf documentation <https://scikit-rf.readthedocs.io/en/latest/api/network.html#network-class>`_.



   .. py:property:: esr
      :type: float


      Return the equivalent serial resistor for capacitor only.



   .. py:property:: f0
      :type: float


      Return the capacitor self resonant frequency in Hz.



   .. py:property:: esl
      :type: float


      Return the equivalent serial inductor for capacitor only.



   .. py:property:: cap_value
      :type: float


      Returns the capacitance value.



   .. py:property:: ind_value
      :type: float


      Return the inductance value.



