.. _configure_pdn_ac_example:

Configure a power-distribution-network AC analysis
===================================================

This example prepares the generic system-example board for a SIwave AC power-
integrity analysis. It creates power and reference pin groups, defines a source
and observation point, and adds a PI-oriented SIwave AC setup with a logarithmic
frequency sweep.

Learning objectives
-------------------

* Identify the power rail, reference net, regulator, and load components.
* Create reusable pin groups for power and reference terminals.
* Add a voltage source with explicit magnitude and impedance.
* Add a circuit port or load excitation for PDN observation.
* Create a SIwave AC setup using PI accuracy settings.
* Add a logarithmic frequency sweep.

Prerequisites
-------------

Run :doc:`../inspect_sipi_design` first. The fixture inventory must identify a
power rail, reference net, regulator component, and load component that are
physically connected on the generic board.

Workflow
--------

#. Copy the generic board to a working directory.
#. Verify the power and reference nets and the regulator and load components.
#. Create pin groups on the regulator and load.
#. Add the regulator voltage source.
#. Add the PDN observation port or load excitation.
#. Create a SIwave AC setup with ``use_si_settings=False``.
#. Select the PI accuracy level.
#. Add a logarithmic sweep.
#. Serialize and apply the configuration.

Run the example
---------------

.. literalinclude:: ../../../../../tests/system_examples/pi/configure_pdn_ac.py
   :language: python
   :linenos:
   :caption: configure_pdn_ac.py

Expected output
---------------

.. code-block:: text

   <output_directory>/pdn_ac.aedb
   <output_directory>/pdn_ac.json

Validation checks
-----------------

Verify that:

* The source and load pin groups contain the intended pins.
* Source polarity and magnitude are correct.
* Source impedance is explicit rather than inferred silently.
* The observation port or load excitation uses the intended terminals.
* The SIwave AC setup is configured for PI settings.
* The sweep distribution and range match the example definition.
* The configuration round-trips through JSON.

Engineering review
------------------

The voltage, source impedance, frequency range, point count, and PI accuracy
level are example values. Select them from the power-rail operating conditions,
regulator model, component models, target impedance, and analysis bandwidth.

Related APIs
------------

* :class:`pyedb.configuration.cfg_ports_sources.CfgSources`
* :class:`pyedb.configuration.cfg_ports_sources.CfgPorts`
* :class:`pyedb.configuration.cfg_setup.CfgSIwaveACSetup`
* :class:`pyedb.configuration.cfg_setup.CfgSetups`
