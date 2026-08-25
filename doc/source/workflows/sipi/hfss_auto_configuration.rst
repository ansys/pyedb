HFSS automatic configuration
============================

The :class:`pyedb.workflows.sipi.hfss_auto_configuration.HFSSAutoConfiguration`
workflow discovers signal nets, creates channel batches, generates cutouts and
ports, and writes analysis-ready HFSS projects.

Not sure whether to use this workflow? See :doc:`hfss_signal_integrity`.

When to use this workflow
-------------------------

Use automatic configuration when you need to:

* Discover signal nets from a full-board EDB.
* Select nets by an interface or naming pattern.
* Preserve recognized differential pairs during batching.
* Generate multiple independent cutout projects.
* Apply consistent ports and HFSS setup settings across batches.

Use the Configuration Builder instead when the exact channel, components,
ports, and setup are already known and must be controlled explicitly.

Before you begin
----------------

Verify that the source EDB opens successfully and contains valid stackup,
component, net, pin, and padstack data. Specify separate source and target
paths so the released input remains unchanged.

Quick start
-----------

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

The numerical values in this example demonstrate the API. Review the batch
size, cutout margin, port type, and setup values for the actual board.

Expected output
---------------

The workflow creates one or more generated EDB projects. Each project contains
a batch-specific subset of signal nets, selected reference structures, a
cutout, ports, and an HFSS analysis setup.

Review the generated project list and open representative projects before
submitting simulations. Confirm the cutout, reference structures, port count,
setup, and sweep.

Control channel selection
-------------------------

Call :meth:`~pyedb.workflows.sipi.hfss_auto_configuration.HFSSAutoConfiguration.auto_populate_batch_groups`
to discover nets automatically. Supply a pattern when only a named interface
or signal family should be included.

For workflows that require complete control, assign signal nets explicitly or
create batch groups manually.

Configure batch groups
----------------------

The ``batch_size`` setting limits the intended number of nets per generated
project. Differential-pair preservation can affect the final group boundary,
because paired nets must remain together.

Inspect ``config.batch_groups`` after discovery and before calling
:meth:`~pyedb.workflows.sipi.hfss_auto_configuration.HFSSAutoConfiguration.create_projects`.
Adjust the groups when automatic naming rules do not reflect the electrical
interface.

Preserve differential pairs
---------------------------

Automatic grouping keeps recognized differential pairs in the same batch.
Net naming remains design dependent. Review the discovered pairs when the board
uses uncommon suffixes, swapped polarity notation, or hierarchical net names.

Do not assume that similarly named nets are electrically paired without
checking connectivity and endpoint assignments.

Select the reference net
------------------------

Automatic configuration can select a reference net from common ground naming
patterns. For designs with several ground domains or interface-specific return
paths, set the reference net explicitly.

A valid reference-net name does not by itself guarantee a valid return path.
Inspect plane continuity, stitching structures, and layer transitions in each
cutout.

Configure ports
---------------

The workflow supports coaxial and circuit ports through ``port_type``.

Use coaxial ports when the excitation is associated with component pins or
via-like structures. Verify padstack and solder-ball geometry.

Use circuit ports when the excitation must be defined between signal and
reference terminals. Verify reference-pin resolution and pin-group behavior.

For trace-edge wave, gap, or differential wave ports, use the Configuration
Builder or direct PyEDB APIs.

Configure solder balls
----------------------

Supply solder-ball geometry only when the component definition does not already
represent the required physical structure. Review the shape, diameter, height,
and optional middle diameter before generating projects.

Avoid replacing valid package geometry with generic values only to satisfy port
creation.

Configure cutout extents
------------------------

Applicable workflows support bounding-box, convex-hull, and conformal extents.
The selected extent and expansion margin must preserve:

* Signal routing and differential-pair geometry.
* Reference planes and return-current paths.
* Stitching vias and via fields.
* Pads, antipads, connectors, and package launches.
* Coupling structures relevant to the analysis.

A smaller cutout can reduce model size, but a cutout that removes relevant
return or coupling structures produces a physically incomplete model.

Configure the HFSS setup
------------------------

Use
:meth:`~pyedb.workflows.sipi.hfss_auto_configuration.HFSSAutoConfiguration.add_simulation_setup`
to override the workflow setup values.

.. code-block:: python

   config.add_simulation_setup(
       meshing_frequency="10GHz",
       maximum_pass_number=15,
       start_frequency="1GHz",
       stop_frequency="20GHz",
       frequency_step="0.1GHz",
   )

These are example values. Select the adaptive and sweep settings from the
channel bandwidth, model complexity, and analysis objective.

Review generated projects
-------------------------

Before solving, verify for every generated project:

* The intended nets and pair membership.
* The selected reference net.
* The cutout boundary and retained reference structures.
* Port count, names, and endpoint assignment.
* Solder-ball geometry when supplied.
* HFSS setup, adaptive settings, sweep, and mesh seeding.

Handle errors
-------------

Treat project-generation failures as actionable errors. Do not silently skip a
batch. Record at least the source design, PyEDB version, AEDT version, batch
name, signal nets, reference net, output path, and error message.

Performance considerations
--------------------------

Batching and cutouts can reduce individual model size and allow independent
execution. Runtime still depends on geometry, frequency range, mesh settings,
convergence behavior, solver resources, and available licenses.

Avoid promising a fixed runtime or hardware requirement. Measure representative
projects and adjust batch size and cutout strategy from observed results.

Limitations
-----------

Automatic discovery is based on the design data and configured naming rules.
Always review:

* Uncommon differential-pair names.
* Multiple possible reference nets.
* Components with incomplete pin or solder-ball data.
* Existing ports or setups that could conflict.
* Extremely large pair groups relative to ``batch_size``.
* Designs where the electromagnetic scope cannot be inferred from net names.

API reference
-------------

Use the generated API reference for complete signatures and attributes:

* :class:`pyedb.workflows.sipi.hfss_auto_configuration.HFSSAutoConfiguration`
* :class:`pyedb.workflows.sipi.hfss_auto_configuration.SimulationSetup`
* :class:`pyedb.workflows.sipi.hfss_auto_configuration.BatchGroup`
* :class:`pyedb.workflows.sipi.hfss_auto_configuration.SolderBallsInfo`
* :func:`pyedb.workflows.sipi.hfss_auto_configuration.create_hfss_auto_configuration`

Troubleshooting
---------------

No signal nets are discovered
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Verify the pattern, signal-net classification, and actual net names. For
nonstandard naming, assign signal nets or batch groups explicitly.

The wrong reference net is selected
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Set the reference net explicitly and review return-path continuity inside the
cutout.

A differential pair is split or not recognized
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Review the net naming and discovered groups before project generation. Define
an explicit batch group when automatic naming rules do not identify the pair.

A port cannot be created
~~~~~~~~~~~~~~~~~~~~~~~~

Verify component reference designators, pin-to-net assignments, padstacks,
reference pins, existing terminals, and solder-ball geometry.

A generated cutout is incomplete
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Increase or change the extent, then inspect the reference planes, stitching
vias, connector launches, and coupling structures again.

Project generation fails for one batch
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Record the failing batch and stop the workflow. Correct the design data or
batch definition before regenerating projects.
