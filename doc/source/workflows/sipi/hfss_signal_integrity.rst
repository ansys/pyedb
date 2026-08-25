Prepare an HFSS signal-integrity project
========================================

PyEDB prepares the layout database, channel cutout, ports, and HFSS analysis
setup. Use PyAEDT or Ansys Electronics Desktop to validate, solve, and export
simulation results.

Choose a workflow
-----------------

Use the workflow that matches the level of automation you need.

.. list-table::
   :header-rows: 1
   :widths: 42 58

   * - Requirement
     - Recommended approach
   * - Configure one known channel
     - Configuration Builder
   * - Specify the signal and reference nets explicitly
     - Configuration Builder
   * - Control every cutout, port, setup, and sweep setting
     - Configuration Builder
   * - Serialize design intent to JSON or TOML
     - Configuration Builder
   * - Discover signal nets automatically
     - :class:`pyedb.workflows.sipi.hfss_auto_configuration.HFSSAutoConfiguration`
   * - Preserve recognized differential pairs while batching nets
     - :class:`pyedb.workflows.sipi.hfss_auto_configuration.HFSSAutoConfiguration`
   * - Generate multiple independent cutout projects
     - :class:`pyedb.workflows.sipi.hfss_auto_configuration.HFSSAutoConfiguration`
   * - Perform fine-grained geometry editing or custom rule processing
     - Direct PyEDB APIs, optionally combined with a configuration
   * - Validate, solve, and export results
     - PyAEDT or Ansys Electronics Desktop

Prerequisites
-------------

Before preparing a project, verify that:

* PyEDB and a compatible Ansys Electronics Desktop release are installed.
* The source EDB opens successfully.
* The signal nets, reference nets, and endpoint components exist.
* The stackup, materials, padstacks, and component geometry are suitable for
  electromagnetic analysis.

For installation requirements, see :doc:`../../getting_started/installation`.
For design navigation, see :doc:`../../user_guide/design_navigation`.

Protect the source EDB
----------------------

.. warning::

   Do not use the released or original EDB as the default output of an
   automated simulation-preparation workflow. Create a working copy or specify
   a separate target path before applying cutouts, ports, or setup changes.

A practical project layout is:

.. code-block:: text

   project/
   |-- source/
   |   `-- board.aedb
   |-- working/
   |   `-- board_hfss.aedb
   |-- configurations/
   |-- validation/
   `-- results/

Inspect the design
------------------

Before creating a cutout or ports, verify:

* Signal and reference nets exist.
* Endpoint components and pins exist.
* Signal pins are assigned to the expected nets.
* The stackup and materials are complete.
* Required vias, padstacks, and reference structures are present.
* Existing terminals and setups do not conflict with the intended workflow.

Fail early when a required design object is missing. This prevents an invalid
project from reaching the solver.

Configure a known channel
-------------------------

Use the Configuration Builder when the channel and its endpoint components are
known. The builder collects the intended changes before
:meth:`pyedb.configuration.configuration.Configuration.run` applies them to the
working EDB.

The following skeleton identifies the channel and its reference net:

.. code-block:: python

   from pyedb import Edb

   edb = Edb("working/board_hfss.aedb", version="2026.1")

   try:
       cfg = edb.configuration.create_config_builder()
       cfg.nets.add_signal_nets(["PCIe_TX0_P", "PCIe_TX0_N"])
       cfg.nets.add_reference_nets(["GND"])

       # Add the cutout, ports, HFSS setup, and sweep.
       edb.configuration.run(cfg)
   finally:
       edb.close()

For a complete Configuration Builder example, including a convex-hull cutout,
solder balls, coaxial ports, and an HFSS sweep, see
:doc:`../../configuration/configuration_api_examples`.

Discover and batch channels automatically
------------------------------------------

Use automatic configuration when nets must be discovered and divided into
independent simulation projects.

.. code-block:: python

   from pyedb.workflows.sipi.hfss_auto_configuration import (
       create_hfss_auto_configuration,
   )

   config = create_hfss_auto_configuration(
       source_edb_path="source/board.aedb",
       target_edb_path="working/board_hfss.aedb",
       batch_group_folder="working/hfss_batches",
       ansys_version="2026.1",
       batch_size=30,
       port_type="coaxial",
       extent_type="convex_hull",
       cutout_expansion="3mm",
       auto_mesh_seeding=True,
   )

   config.auto_populate_batch_groups(pattern=["PCIe"])
   config.create_projects()

Review the discovered groups and generated project paths before submitting
simulations. For grouping rules, setup customization, solder-ball modeling,
and output details, see :doc:`hfss_auto_configuration`.

Choose a port strategy
----------------------

Select the port type from the physical excitation location and intended return
path.

.. list-table::
   :header-rows: 1
   :widths: 22 48 30

   * - Port type
     - Use when
     - Key check
   * - Coaxial
     - The excitation is associated with a component pin or via-like structure.
     - Verify the padstack and solder-ball geometry.
   * - Circuit
     - The excitation is defined between signal and reference terminals.
     - Verify reference-pin resolution and pin grouping.
   * - Wave
     - The excitation belongs on a trace edge.
     - Verify edge geometry, direction, and reference conductor.
   * - Differential wave
     - A differential excitation belongs on two trace edges.
     - Verify positive and negative ordering.
   * - Gap
     - A localized edge-gap excitation is required.
     - Verify the physical gap and terminal definitions.

For signatures and terminal-resolution details, see
:class:`pyedb.configuration.cfg_ports_sources.CfgPorts`.

Choose a cutout strategy
------------------------

PyEDB supports bounding-box, convex-hull, and conformal extents in applicable
workflows. A convex-hull extent is a useful starting point for many routed
channels, but the correct extent and expansion depend on the physical design.

Review whether the cutout preserves:

* Signal geometry and both legs of every differential pair.
* Reference planes and return-current paths.
* Stitching vias, via fields, pads, and antipads.
* BGA and connector launch structures.
* Coupling structures relevant to the analysis.

The expansion margin shown in an example is an example value, not a universal
signal-integrity recommendation.

Configure the HFSS analysis
---------------------------

An HFSS setup normally defines:

* The adaptive solution type and frequency range.
* The convergence threshold and maximum adaptive passes.
* The frequency sweep.
* Automatic or explicit mesh operations.

Distinguish the following when reviewing an example:

* A **default** is selected by the software when a setting is omitted.
* An **example value** demonstrates syntax for a representative channel.
* An **engineering recommendation** is selected for a stated modeling reason.

For complete setup signatures, see
:class:`pyedb.configuration.cfg_setup.CfgHFSSSetup`.

Review expected outputs
-----------------------

A Configuration Builder workflow produces a working EDB containing the
requested cutout, ports, setup, sweep, and mesh settings. It can also produce a
JSON or TOML configuration artifact for review and version control.

An automatic workflow produces one or more batch-specific EDB projects with
the selected nets, reference structures, ports, cutout, and HFSS setup.

.. tip::

   Before launching the solver, inspect the generated project. Verify the
   cutout boundary, reference structures, port count, port naming, setup, and
   sweep.

Validate and solve the generated project
----------------------------------------

After PyEDB creates the analysis-ready EDB, use PyAEDT or Ansys Electronics
Desktop to:

#. Open the generated EDB in HFSS 3D Layout.
#. Reuse the generated setup unless a change is intentional.
#. Validate the complete design.
#. Stop and review validation messages if validation fails.
#. Solve the intended setup.
#. Export the required Touchstone or other result files.

The PyEDB example gallery links to end-to-end PyAEDT workflows for solving and
post-processing. See :doc:`../../examples/index`.

Model-fidelity considerations
-----------------------------

A converged solution is not proof that the physical model is valid. Review at
least:

* Dielectric and conductor properties.
* Copper roughness when relevant to the frequency range.
* Trace, via, pad, and antipad geometry.
* Reference-plane continuity and return-path transitions.
* BGA, connector, and package geometry.
* Port placement and reference-terminal selection.
* Cutout boundaries and expansion margins.

Define protocol-specific sign-off limits outside this generic preparation
workflow.

Troubleshooting routes
----------------------

Use the documentation area that owns the failing stage:

* Installation or backend errors: :doc:`../../getting_started/index`
* EDB inspection: :doc:`../../user_guide/design_navigation`
* Configuration syntax or application: :doc:`../../configuration/index`
* Automatic discovery or batch generation: :doc:`hfss_auto_configuration`
* Solver validation, solve, or export: PyAEDT documentation

Next steps
----------

* Use the Configuration Builder examples for a controlled channel.
* Use automatic configuration for discovery and batch project generation.
* Validate every generated project before solving.
* Store the configuration and result metadata with the simulation outputs.
