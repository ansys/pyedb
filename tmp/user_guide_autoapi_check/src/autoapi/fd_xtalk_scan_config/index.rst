fd_xtalk_scan_config
====================

.. py:module:: fd_xtalk_scan_config


Classes
-------

.. autoapisummary::

   fd_xtalk_scan_config.CrosstalkFrequency


Module Contents
---------------

.. py:class:: CrosstalkFrequency(pedb)

   SIwave frequency domain crosstalk configuration handler.

   This class manages frequency domain crosstalk scanning configuration including
   transmission line segment length, frequency, and net-specific crosstalk thresholds.

   Parameters
   ----------
   pedb : object
       PyEDB instance.

   Examples
   --------
   >>> from pyedb import Edb
   >>> edb = Edb("path/to/aedb")
   >>> xtalk_freq = CrosstalkFrequency(edb)
   >>> xtalk_freq.min_transmission_line_segment_length = "0.5mm"
   >>> xtalk_freq.frequency = "5e9Hz"
   >>> xtalk_freq.add_single_ended_net("USB_DP", next_warning_threshold=3.0, fext_warning_threshold=2.0)



   .. py:attribute:: min_transmission_line_segment_length
      :type:  str
      :value: '0.25mm'



   .. py:attribute:: frequency
      :type:  str
      :value: '2e9Hz'



   .. py:attribute:: nets
      :type:  dict[str, pyedb.misc.siw_feature_config.xtalk_scan.net.SingleEndedNet]


   .. py:method:: extend_xml(parent) -> None

      Write class XML section.

      Parameters
      ----------
      parent : xml.etree.ElementTree.Element
          Parent XML element to extend.




   .. py:method:: add_single_ended_net(name: str, next_warning_threshold: float | str = 5.0, next_violation_threshold: float | str = 10.0, fext_warning_threshold_warning: float | str = 5.0, fext_violation_threshold: float | str = 5.0) -> bool

      Add single ended net to frequency domain crosstalk configuration.

      Parameters
      ----------
      name : str
          Net name.
      next_warning_threshold : float or str, optional
          Near end crosstalk warning threshold value in dB.
          The default is ``5.0``.
      next_violation_threshold : float or str, optional
          Near end crosstalk violation threshold value in dB.
          The default is ``10.0``.
      fext_warning_threshold_warning : float or str, optional
          Far end crosstalk warning threshold value in dB.
          The default is ``5.0``.
      fext_violation_threshold : float or str, optional
          Far end crosstalk violation threshold value in dB.
          The default is ``5.0``.

      Returns
      -------
      bool
          ``True`` if the net was added successfully, ``False`` otherwise.

      Examples
      --------
      >>> xtalk_freq = CrosstalkFrequency(pedb)
      >>> xtalk_freq.add_single_ended_net("USB_DP", next_warning_threshold=3.0, fext_warning_threshold=2.0)
      True




