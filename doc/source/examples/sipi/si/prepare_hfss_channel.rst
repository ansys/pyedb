.. _prepare_hfss_channel_example:

Prepare a differential channel for HFSS 3D Layout
==================================================

This example uses the Configuration Builder to prepare one known differential
channel from the generic system-example board. It creates a protected working
copy, verifies the required design objects, and adds the cutout, ports, HFSS
setup, frequency sweep, and mesh settings.

Learning objectives
-------------------

* Use a session-bound Configuration Builder.
* Classify signal and reference nets.
* Create a channel cutout while preserving reference structures.
* Create coaxial ports at both channel endpoints.
* Configure broadband adaptation, a frequency sweep, and mesh seeding.
* Serialize the configuration for review and version control.

Prerequisites
-------------

Run :doc:`../inspect_sipi_design` first. The shared fixture inventory must
provide the differential pair, endpoint components, and reference net.

.. warning::

   The example must operate on a temporary or working copy. Cutouts, ports, and
   setup changes must never be applied to the generic source fixture.

Workflow
--------

#. Copy the generic EDB to the output directory.
#. Verify both endpoint components and both signal nets.
#. Create a session-bound configuration builder.
#. Classify the differential pair and reference net.
#. Add a physically reviewed cutout.
#. Add coaxial ports at both endpoints.
#. Add the HFSS setup, adaptation, sweep, and mesh settings.
#. Save the configuration to JSON.
#. Apply the configuration and inspect the result.

Run the example
---------------

.. literalinclude:: ../../../../../tests/system_examples/si/prepare_hfss_channel.py
   :language: python
   :linenos:
   :caption: prepare_hfss_channel.py

Expected output
---------------

.. code-block:: text

   <output_directory>/hfss_channel.aedb
   <output_directory>/hfss_channel.json

Validation checks
-----------------

Verify that:

* The source EDB checksum is unchanged.
* Both signal nets and the reference net are classified correctly.
* Both endpoint components remain in the generated project.
* The intended ports exist at both endpoints.
* The expected HFSS setup and sweep exist.
* The cutout retains the required planes, stitching vias, pads, and antipads.
* The serialized configuration contains the demonstrated sections.

Engineering review
------------------

The cutout expansion, adaptive frequencies, sweep range, convergence value,
and mesh settings are example values. Select them from the actual channel
bandwidth, geometry, return-current environment, and analysis objective.

Related APIs
------------

* :class:`pyedb.configuration.cfg_ports_sources.CfgPorts`
* :class:`pyedb.configuration.cfg_setup.CfgHFSSSetup`
* :meth:`pyedb.configuration.configuration.Configuration.run`

For workflow selection guidance, see
:doc:`../../../workflows/sipi/hfss_signal_integrity`.
