impedance_scan_config
=====================

.. py:module:: impedance_scan_config


Classes
-------

.. autoapisummary::

   impedance_scan_config.ImpedanceScan


Module Contents
---------------

.. py:class:: ImpedanceScan(pedb)

   Impedance scan configuration class handler.

   This class manages impedance scanning configuration including transmission line
   segment length, frequency, and net-specific impedance parameters.

   Parameters
   ----------
   pedb : object
       PyEDB instance.

   Examples
   --------
   >>> from pyedb import Edb
   >>> edb = Edb("path/to/aedb")
   >>> impedance_scan = ImpedanceScan(edb)
   >>> impedance_scan.min_transmission_line_segment_length = "0.5mm"
   >>> impedance_scan.frequency = "5e9Hz"
   >>> impedance_scan.add_single_ended_net("CLK", nominal_impedance=50.0, warning_threshold=10.0)



   .. py:attribute:: min_transmission_line_segment_length
      :type:  str
      :value: '0.25mm'



   .. py:attribute:: frequency
      :type:  str
      :value: '2e9Hz'



   .. py:attribute:: nets
      :type:  dict[str, pyedb.misc.siw_feature_config.xtalk_scan.net.SingleEndedNet]


   .. py:method:: extend_xml(parent) -> None

      Write object to XML section.

      Parameters
      ----------
      parent : xml.etree.ElementTree.Element
          Parent XML element to extend.




   .. py:method:: add_single_ended_net(name: str, nominal_impedance: float | str = 50.0, warning_threshold: float | str = 17.0, violation_threshold: float | str = 32.0) -> bool

      Add single ended net to impedance scan configuration.

      Parameters
      ----------
      name : str
          Net name.
      nominal_impedance : float or str, optional
          Nominal impedance in ohms.
          The default is ``50.0``.
      warning_threshold : float or str, optional
          Warning threshold value in percentage.
          The default is ``17.0``.
      violation_threshold : float or str, optional
          Violation threshold value in percentage.
          The default is ``32.0``.

      Returns
      -------
      bool
          ``True`` if the net was added successfully, ``False`` otherwise.

      Examples
      --------
      >>> impedance_scan = ImpedanceScan(pedb)
      >>> impedance_scan.add_single_ended_net("DDR_DQ0", nominal_impedance=40.0, warning_threshold=15.0)
      True




