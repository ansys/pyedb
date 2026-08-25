.. _batch_hfss_channels_example:

Discover and batch high-speed channels for HFSS
================================================

This example uses ``HFSSAutoConfiguration`` to discover high-speed nets on the
generic system-example board, review channel grouping, and generate independent
analysis-ready EDB projects.

Learning objectives
-------------------

* Select channels from an interface pattern or explicit net list.
* Review discovered batch groups before writing projects.
* Keep recognized differential pairs in the same batch.
* Configure the cutout, port strategy, and HFSS setup consistently.
* Generate independent EDB projects for downstream execution.

Prerequisites
-------------

Run :doc:`../inspect_sipi_design` first. Use an interface prefix that exists on
the generic board. If its naming does not support reliable pattern matching,
provide the signal nets or batch groups explicitly.

Workflow
--------

#. Locate the generic source EDB through the repository fixture.
#. Create an automatic HFSS configuration with separate output paths.
#. Discover the selected high-speed channels.
#. Inspect every batch name and net list.
#. Correct grouping or the reference net when necessary.
#. Add explicit simulation settings.
#. Generate the batch projects.
#. Open representative outputs and inspect their ports and setups.

Run the example
---------------

.. literalinclude:: ../../../../tests/system_examples/sipi/si/batch_hfss_channels.py
   :language: python
   :linenos:
   :caption: batch_hfss_channels.py

Expected output
---------------

.. code-block:: text

   <output_directory>/hfss_batches/
   |-- <batch_1>.aedb
   |-- <batch_2>.aedb
   `-- ...

Validation checks
-----------------

Verify that:

* The expected interface nets are discovered.
* Recognized differential pairs are not split.
* The configured reference net exists in every relevant project.
* The batch-size behavior is consistent with pair preservation.
* Every generated EDB reopens successfully.
* Each generated EDB contains the intended ports and HFSS setup.

.. important::

   Automatic discovery is a starting point, not an electrical sign-off step.
   Review uncommon net suffixes, hierarchical names, endpoint connectivity,
   reference-net selection, and return-path continuity before solving.

Related APIs
------------

* :class:`pyedb.workflows.sipi.hfss_auto_configuration.HFSSAutoConfiguration`
* :class:`pyedb.workflows.sipi.hfss_auto_configuration.BatchGroup`
* :class:`pyedb.workflows.sipi.hfss_auto_configuration.SimulationSetup`
* :func:`pyedb.workflows.sipi.hfss_auto_configuration.create_hfss_auto_configuration`

For detailed workflow guidance, see
:doc:`../../../workflows/sipi/hfss_auto_configuration`.
