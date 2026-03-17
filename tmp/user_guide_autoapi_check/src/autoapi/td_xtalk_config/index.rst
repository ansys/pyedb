td_xtalk_config
===============

.. py:module:: td_xtalk_config


Classes
-------

.. autoapisummary::

   td_xtalk_config.CrossTalkTime


Module Contents
---------------

.. py:class:: CrossTalkTime(pedb)

   Time domain crosstalk configuration class handler.

   Parameters
   ----------
   pedb : object
       PyEDB instance.

   Examples
   --------
   >>> from pyedb import Edb
   >>> edb = Edb("path/to/aedb")
   >>> xtalk = CrossTalkTime(edb)
   >>> xtalk.add_single_ended_net("CLK", driver_rise_time=5.0, voltage=1.8)



   .. py:attribute:: nets


   .. py:attribute:: driver_pins
      :value: []



   .. py:attribute:: receiver_pins
      :value: []



   .. py:method:: add_single_ended_net(name: str, driver_rise_time: float | str = 5.0, voltage: float | str = 10, driver_impedance: float | str = 5.0, termination_impedance: float | str = 5.0) -> bool

      Add single ended net.

      Parameters
      ----------
      name : str
          Net name.
      driver_rise_time : float or str, optional
          Driver rise time value.
          The default is ``5.0``.
      voltage : float or str, optional
          Voltage value.
          The default is ``10``.
      driver_impedance : float or str, optional
          Driver impedance value.
          The default is ``5.0``.
      termination_impedance : float or str, optional
          Termination impedance value.
          The default is ``5.0``.

      Returns
      -------
      bool
          ``True`` if the net was added successfully, ``False`` otherwise.

      Examples
      --------
      >>> xtalk = CrossTalkTime(pedb)
      >>> xtalk.add_single_ended_net("DDR_DQ0", driver_rise_time=2.0, voltage=1.2)
      True




   .. py:method:: add_driver_pins(name: str, ref_des: str, rise_time: str = '100ps', voltage: float = 1.0, impedance: float = 50.0) -> None

      Add driver pins.

      Parameters
      ----------
      name : str
          Pin name.
      ref_des : str
          Reference designator of the component.
      rise_time : str, optional
          Driver rise time.
          The default is ``"100ps"``.
      voltage : float, optional
          Voltage value.
          The default is ``1.0``.
      impedance : float, optional
          Driver impedance value.
          The default is ``50.0``.

      Examples
      --------
      >>> xtalk = CrossTalkTime(pedb)
      >>> xtalk.add_driver_pins("A1", "U1", rise_time="50ps", voltage=1.8, impedance=40.0)




   .. py:method:: add_receiver_pin(name: str, ref_des: str, impedance: float) -> None

      Add receiver pin.

      Parameters
      ----------
      name : str
          Pin name.
      ref_des : str
          Reference designator of the component.
      impedance : float
          Receiver impedance value.

      Examples
      --------
      >>> xtalk = CrossTalkTime(pedb)
      >>> xtalk.add_receiver_pin("B1", "U2", impedance=75.0)




   .. py:method:: extend_xml(parent) -> None

      Extend XML tree with crosstalk configuration.

      Parameters
      ----------
      parent : xml.etree.ElementTree.Element
          Parent XML element to extend.




