.. _sipi_examples:

Signal and power integrity examples
===================================

These examples demonstrate how to use PyEDB to inspect and prepare EDB designs
for signal-integrity and power-integrity analysis. They focus on PyEDB-owned
operations and stop at the analysis-ready EDB or batch-preparation boundary.
Use PyAEDT or Ansys Electronics Desktop to validate, solve, and post-process
the generated projects.

The board-based examples use the generic EDB model maintained by the PyEDB
system-example test infrastructure. Each example works on a temporary copy and
does not modify the source model.

Before you begin
----------------

* Install PyEDB and a compatible Ansys Electronics Desktop release.
* Locate the generic system-example board through the repository test fixture.
* Run examples from a writable working directory.
* Review the selected components, nets, and reference structures before
  applying a configuration.

.. important::

   Component and net names used by the examples must come from the shared
   generic-board fixture. Do not duplicate those names independently in every
   script. A single fixture inventory should define the SI pair, endpoint
   components, power rail, reference net, voltage-regulator component, and load
   component.

Start with design inspection
----------------------------

.. grid:: 1

   .. grid-item-card:: Inspect the generic SI/PI board
      :link: inspect_sipi_design
      :link-type: doc

      Open a temporary board copy, inspect its electrical content, and verify
      that the objects required by the other examples are available.

Signal-integrity examples
-------------------------

.. grid:: 3

   .. grid-item-card:: Build a transmission line
      :link: si/build_transmission_line
      :link-type: doc

      Create a small deterministic EDB and inspect its stackup, signal trace,
      reference geometry, and vias.

   .. grid-item-card:: Prepare an HFSS channel
      :link: si/prepare_hfss_channel
      :link-type: doc

      Configure a differential channel, cutout, ports, HFSS setup, sweep, and
      mesh settings with the Configuration Builder.

   .. grid-item-card:: Batch HFSS channels
      :link: si/batch_hfss_channels
      :link-type: doc

      Discover high-speed nets, review differential-pair grouping, and create
      independent analysis-ready projects.

Power-integrity examples
------------------------

.. grid:: 2

   .. grid-item-card:: Configure a PDN AC analysis
      :link: pi/configure_pdn_ac
      :link-type: doc

      Create power and reference pin groups, sources, an observation point, and
      a SIwave AC setup with a logarithmic sweep.

   .. grid-item-card:: Configure a DC IR-drop analysis
      :link: pi/configure_dcir
      :link-type: doc

      Create voltage and current sources and prepare a SIwave DC setup for a
      power rail.

Utilities
---------

.. grid:: 1

   .. grid-item-card:: Parse a SIwave batch log
      :link: utilities/parse_siwave_log
      :link-type: doc

      Check completion, inspect warnings and profile entries, and export a
      structured JSON summary without launching AEDT.

.. toctree::
   :hidden:
   :maxdepth: 2

   inspect_sipi_design
   si/build_transmission_line
   si/prepare_hfss_channel
   si/batch_hfss_channels
   pi/configure_pdn_ac
   pi/configure_dcir
   utilities/parse_siwave_log
   utilities/parse_hfss_log
