.. _configure_dcir_example:

Configure a SIwave DC IR-drop analysis
=======================================

This example prepares a power rail on the generic system-example board for a
SIwave DC IR-drop analysis. It defines the regulator voltage source, one or
more current loads, and a SIwave DC setup.

Learning objectives
-------------------

* Reuse the generic-board power topology from the PDN AC example.
* Define source and load pin groups.
* Add voltage and current sources with explicit electrical values.
* Configure the SIwave DC accuracy level.
* Optionally request DC thermal-data export for a later multiphysics workflow.

Prerequisites
-------------

Run :doc:`../inspect_sipi_design` first. Confirm that the selected regulator,
loads, power rail, and reference net form the intended DC current path.

Workflow
--------

#. Copy the source EDB to a working directory.
#. Verify the regulator, load components, power rail, and reference net.
#. Create regulator and load pin groups.
#. Add the regulator voltage source.
#. Add one or more current loads.
#. Create a SIwave DC setup.
#. Configure the DC accuracy level and thermal-data export option.
#. Serialize and apply the configuration.
#. Inspect all source terminal assignments before closing the EDB.

Run the example
---------------

.. literalinclude:: ../../../../../tests/system_examples/pi/configure_dcir.py
   :language: python
   :linenos:
   :caption: configure_dcir.py

Expected output
---------------

.. code-block:: text

   <output_directory>/vdd_dcir.aedb
   <output_directory>/vdd_dcir.json

Validation checks
-----------------

Verify that:

* The source voltage and polarity are correct.
* Every current-source magnitude and polarity is correct.
* The sum of the configured loads matches the example intent.
* No source terminal resolves to an unintended pin or net.
* The SIwave DC setup exists with the requested accuracy level.
* Thermal-data export is enabled only when required.
* The source EDB remains unchanged.

.. warning::

   Incorrect source polarity, load magnitude, or terminal grouping can produce
   plausible but invalid DC results. Review the generated sources in the EDB
   before running SIwave.

Related APIs
------------

* :class:`pyedb.configuration.cfg_ports_sources.CfgSources`
* :class:`pyedb.configuration.cfg_setup.CfgSIwaveDCSetup`
* :meth:`pyedb.configuration.cfg_setup.CfgSetups.add_siwave_dc_setup`
