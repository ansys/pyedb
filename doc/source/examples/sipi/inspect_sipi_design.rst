.. _inspect_sipi_design_example:

Inspect the generic SI/PI board
===============================

This example opens a temporary copy of the generic PyEDB system-example board
and inventories the objects required by the SI and PI examples. Run this
example first when adapting the examples to a new board fixture.

Learning objectives
-------------------

* Locate the generic board through the test fixture instead of hard-coding a
  developer-specific path.
* Protect the source board by opening a temporary copy.
* Inspect components, nets, layers, padstacks, ports, and simulation setups.
* Fail early when a required component or net is absent.
* Return a small inventory that the remaining examples can reuse.

Required fixture inventory
--------------------------

The shared fixture must define:

.. code-block:: python

   SIPI_BOARD = {
       "si_endpoints": ("<tx_component>", "<rx_component>"),
       "differential_pair": ("<positive_net>", "<negative_net>"),
       "power_net": "<power_rail>",
       "reference_net": "<ground_net>",
       "vrm_component": "<vrm_component>",
       "load_component": "<load_component>",
   }

Replace the placeholders once, in the shared test/example fixture, after
inspecting the generic board. The individual example scripts should import the
inventory rather than repeat it.

Run the example
---------------

.. literalinclude:: ../../../../tests/system_examples/sipi/inspect_sipi_design.py
   :language: python
   :linenos:
   :caption: inspect_sipi_design.py

Expected result
---------------

The example prints or returns:

* Available components and the required endpoint components.
* Signal, power, and reference nets.
* Stackup layers.
* Existing ports and setups.
* A validated inventory for the remaining examples.

The original generic board remains unchanged. Any generated copy is stored in
the example's temporary output directory.

Validation checks
-----------------

Verify that:

* The copied EDB opens and closes successfully.
* Every fixture component and net exists.
* The differential-pair nets are distinct.
* The power and reference nets are distinct.
* No modifications are written to the source EDB.

Next steps
----------

Continue with :doc:`si/prepare_hfss_channel` for an existing differential
channel or :doc:`si/build_transmission_line` to create a minimal SI design from
scratch.
