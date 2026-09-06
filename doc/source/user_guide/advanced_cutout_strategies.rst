.. _advanced_cutout_strategies:

Advanced cutouts: comparing extent strategies and custom shapes
=====================================================================

Go beyond a single default cutout call: compare the three built-in extent algorithms side by side
on the same nets, and build a custom rectangular cutout polygon centered on a specific component
with an explicit margin — useful when you need a cutout region defined by mechanical placement
rather than by net geometry.

What you will learn
--------------------

- How the three extent strategies (``ConvexHull``, ``Conforming``, ``Bounding``) differ in the size
  of the resulting cutout for the same input nets.
- How to build a ``custom_extent`` polygon programmatically from a component's bounding box, instead
  of relying on an automatically computed extent.
- How to verify a cutout output quantitatively (layer count, net count) rather than just checking
  that a file was written.

When to use this workflow
----------------------------

Use extent-strategy comparison when you are tuning a cutout recipe for a new design family and want
to understand the size/accuracy trade-off before committing to one strategy in production. Use a
custom-extent cutout when the region you want to simulate is defined by a physical keep-out area
(for example, "everything within 5 mm of component U3") rather than by which nets happen to be
routed there.

Prerequisites
-------------

- An open ``Edb`` instance pointing at an existing design with signal and reference nets and at
  least one component (see :doc:`../getting_started/quick_start`).
- Familiarity with :doc:`cutouts` (the single-call cutout pattern this page builds on).

Software and license requirements
-------------------------------------

- A licensed local AEDT installation, release 2026.1 or later for the default gRPC backend.
- Cutout generation is license-free layout preparation.

API concepts introduced
---------------------------

- :meth:`Edb.cutout <pyedb.grpc.edb.Edb.cutout>` with ``extent_type`` set to each of the three
  supported values, and with an explicit ``custom_extent`` polygon.
- :attr:`Component.bounding_box <pyedb.grpc.database.hierarchy.component.Component.bounding_box>` —
  ``[x_min, y_min, x_max, y_max]`` in meters, used here to build a margin-based custom extent.
- :meth:`Edb.get_statistics <pyedb.grpc.edb.Edb.get_statistics>` — used to quantitatively compare
  the three cutout outputs.

Complete executable example
--------------------------------

.. code-block:: python

   import shutil
   import tempfile
   from pathlib import Path

   from pyedb import Edb

   # --- 1. Define inputs -------------------------------------------------------------
   source_path = "my_board.aedb"
   signal_nets = ["DDR4_DQS0_P", "DDR4_DQS0_N"]
   reference_nets = ["GND"]

   work_dir = Path(tempfile.mkdtemp(prefix="pyedb_cutout_compare_"))


   def make_working_copy(suffix: str) -> Path:
       """Create an independent working copy for one cutout trial."""
       copy_path = work_dir / f"board_{suffix}.aedb"
       shutil.copytree(source_path, copy_path)
       return copy_path


   # --- 2/3/4/5. Run the same cutout with each extent strategy on an independent copy,
   #              and record layout statistics for comparison. ------------------------
   results = {}
   for strategy in ("ConvexHull", "Conforming", "Bounding"):
       working_copy = make_working_copy(strategy.lower())
       edb = Edb(edbpath=str(working_copy), version="2026.1")

       output_path = str(work_dir / f"cutout_{strategy.lower()}.aedb")
       extent = edb.cutout(
           signal_nets=signal_nets,
           reference_nets=reference_nets,
           extent_type=strategy,
           expansion_size="1mm",
           output_aedb_path=output_path,
           open_cutout_at_end=False,
       )
       assert extent, f"{strategy} cutout failed to produce an extent"
       edb.close()

       # Open the cutout output independently to measure it.
       edb_cutout = Edb(edbpath=output_path, version="2026.1")
       stats = edb_cutout.get_statistics(compute_area=True)
       results[strategy] = {
           "net_count": len(edb_cutout.nets.netlist),
           "layer_count": stats.num_layers,
           "layout_size_m": stats.layout_size,
       }
       edb_cutout.close()

   print("Extent strategy comparison:")
   for strategy, metrics in results.items():
       print(f"  {strategy:12s} -> {metrics}")

   # Deterministic cross-check: every strategy must retain the same signal/reference
   # nets (the *shape* of the clip differs, but the requested nets must all survive).
   for strategy, metrics in results.items():
       assert metrics["net_count"] >= len(signal_nets) + len(
           reference_nets
       ), f"{strategy} cutout lost one or more requested nets"

   # --- 6. Build a custom-extent cutout centered on a specific component -------------
   working_copy = make_working_copy("custom_extent")
   edb = Edb(edbpath=str(working_copy), version="2026.1")

   target_component = "U1"
   margin_m = 0.005  # 5 mm margin around the component's bounding box, in meters
   assert (
       target_component in edb.components.instances
   ), f"Component {target_component!r} not found"

   x_min, y_min, x_max, y_max = edb.components[target_component].bounding_box
   custom_polygon = [
       (x_min - margin_m, y_min - margin_m),
       (x_max + margin_m, y_min - margin_m),
       (x_max + margin_m, y_max + margin_m),
       (x_min - margin_m, y_max + margin_m),
   ]

   custom_output_path = str(work_dir / "cutout_custom_extent.aedb")
   custom_extent = edb.cutout(
       signal_nets=signal_nets,
       reference_nets=reference_nets,
       custom_extent=custom_polygon,
       custom_extent_units="meter",
       output_aedb_path=custom_output_path,
       open_cutout_at_end=False,
   )
   assert custom_extent, "Custom-extent cutout failed"
   edb.close()

   # Verify the custom-extent output opens and is a valid, reopenable database.
   edb_custom = Edb(edbpath=custom_output_path, version="2026.1")
   assert (
       edb_custom.active_cell is not None
   ), "Custom-extent cutout output has no active cell"
   print(
       f"Custom-extent cutout around {target_component!r} written to {custom_output_path}"
   )
   edb_custom.close()

Expected output
-------------------

.. code-block:: console

   Extent strategy comparison:
     ConvexHull   -> {'net_count': 3, 'layer_count': 12, 'layout_size_m': [0.0, 0.0, 0.021, 0.018]}
     Conforming   -> {'net_count': 3, 'layer_count': 12, 'layout_size_m': [0.0, 0.0, 0.019, 0.017]}
     Bounding     -> {'net_count': 3, 'layer_count': 12, 'layout_size_m': [0.0, 0.0, 0.024, 0.021]}
   Custom-extent cutout around 'U1' written to /tmp/.../cutout_custom_extent.aedb

Exact ``layout_size_m`` values depend on your design; the pattern to notice is that ``Bounding`` is
always the largest (a simple box), ``Conforming`` is typically the smallest (tight to geometry), and
``ConvexHull`` sits in between.

Deterministic verification
-------------------------------

Each cutout's ``extent`` return value is checked for truthiness immediately, and the net count of
every cutout output is asserted to retain all requested signal and reference nets — a strategy that
silently dropped a requested net would be caught here rather than surfacing later as a missing S-
parameter port. The custom-extent output is independently reopened and checked for a valid active
cell, exactly like the persistence checks used throughout this user guide.

Common failures and diagnostics
------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Symptom
     - Likely cause
     - Resolution
   * - One strategy's cutout has a much smaller net count than the others
     - The tighter extent (typically ``Conforming``) clipped through a component or pin group needed
       by one of the requested nets.
     - Increase ``expansion_size``, or set ``check_terminals=True`` as documented on :doc:`cutouts`.
   * - ``custom_extent`` cutout silently produces an empty or tiny region
     - ``custom_extent_units`` did not match the units the polygon coordinates were actually
       computed in (this example computes coordinates in meters and passes
       ``custom_extent_units="meter"`` explicitly to match).
     - Always pass ``custom_extent_units`` matching the unit system of your coordinate values; the
       default is ``"mm"``, which will misinterpret meter-scale coordinates as millimeters.
   * - ``Component.bounding_box`` raises or returns unexpected values
     - The component name does not exist, or the component has no placed footprint.
     - Verify with ``target_component in edb.components.instances`` before accessing
       ``.bounding_box`` (done in step 6 above).

Cleanup
-----------

Every ``edb`` session opened above is explicitly closed. Remove ``work_dir`` (which contains four
independent working copies and four cutout outputs) once you have compared the results, for example
with ``shutil.rmtree(work_dir, ignore_errors=True)``.

Next recommended example
-----------------------------

- :doc:`cutouts` — the single-call cutout pattern this page extends.
- :doc:`design_inventory_report` — the ``get_statistics`` call used here to compare cutout outputs,
  explained in full.
- :doc:`batch_processing_multiple_designs` — apply the same cutout recipe across many source
  designs instead of many strategies on one design.

Related conceptual pages
-----------------------------

- :doc:`../workflows/utilities/cutout` — the full parameter reference for the underlying ``Cutout``
  class, including every parameter used or referenced on this page.

Related API-reference pages
--------------------------------

- :class:`pyedb.workflows.utilities.cutout.Cutout`
- :class:`LayoutStatistics <pyedb.grpc.database.utility.layout_statistics.LayoutStatistics>`

Version compatibility notes
--------------------------------

- ``edb.cutout`` dispatches internally to a gRPC- or DotNet-specific implementation; the public
  method name, parameters, and unit conventions used on this page are identical on both backends.
