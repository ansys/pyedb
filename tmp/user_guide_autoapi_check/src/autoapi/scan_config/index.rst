scan_config
===========

.. py:module:: scan_config


Classes
-------

.. autoapisummary::

   scan_config.ScanType
   scan_config.SiwaveScanConfig


Module Contents
---------------

.. py:class:: ScanType(*args, **kwds)

   Bases: :py:obj:`enum.Enum`


   Create a collection of name/value pairs.

   Example enumeration:

   >>> class Color(Enum):
   ...     RED = 1
   ...     BLUE = 2
   ...     GREEN = 3

   Access them by:

   - attribute access::

   >>> Color.RED
   <Color.RED: 1>

   - value lookup:

   >>> Color(1)
   <Color.RED: 1>

   - name lookup:

   >>> Color['RED']
   <Color.RED: 1>

   Enumerations can be iterated over, and know how many members they have:

   >>> len(Color)
   3

   >>> list(Color)
   [<Color.RED: 1>, <Color.BLUE: 2>, <Color.GREEN: 3>]

   Methods can be added to enumerations, and members can have their own
   attributes -- see the documentation for details.


   .. py:attribute:: IMPEDANCE
      :value: 0



   .. py:attribute:: FREQ_XTALK
      :value: 1



   .. py:attribute:: TIME_XTALK
      :value: 2



.. py:class:: SiwaveScanConfig(pedb, scan_type: str = 'impedance')

   XML control file handle for SIwave crosstalk scan.

   Parameters
   ----------
   pedb : object
       PyEDB instance.
   scan_type : str, optional
       Type of scan to configure. Options are ``"impedance"``, ``"frequency_xtalk"``, or ``"time_xtalk"``.
       The default is ``"impedance"``.

   Examples
   --------
   >>> from pyedb import Edb
   >>> edb = Edb("path/to/aedb")
   >>> scan_config = SiwaveScanConfig(edb, scan_type="impedance")
   >>> scan_config.file_path = "output_config.xml"
   >>> scan_config.write_xml()



   .. py:attribute:: file_path
      :value: ''



   .. py:attribute:: impedance_scan


   .. py:attribute:: frequency_xtalk_scan


   .. py:attribute:: time_xtalk_scan


   .. py:method:: write_xml() -> bool

      Write XML control file.

      Returns
      -------
      bool
          ``True`` if the file was written successfully, ``False`` otherwise.

      Examples
      --------
      >>> scan_config = SiwaveScanConfig(pedb, scan_type="impedance")
      >>> scan_config.file_path = "impedance_scan.xml"
      >>> scan_config.impedance_scan.add_net("CLK", threshold_near=5.0, threshold_far=10.0)
      >>> success = scan_config.write_xml()
      >>> success
      True




