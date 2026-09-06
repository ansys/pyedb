.. _batch_processing_multiple_designs:

Production automation: batch-process multiple designs
============================================================

Apply the same inspection-and-modification recipe across an entire library of designs, with
structured per-design logging, isolated failures (one bad design does not stop the batch), and a
single machine-readable summary report at the end — the pattern to reuse for any "run this on all
our boards" production job.

What you will learn
--------------------

- How to structure a batch job so each design gets its own isolated working copy and its own
  ``Edb`` session, with guaranteed cleanup even if one design fails.
- How to catch and record a per-design failure without aborting the whole batch.
- How to produce one aggregated, deterministic summary report across all processed designs.

When to use this workflow
----------------------------

Use this pattern for any recurring production job that must run unattended across many designs: a
nightly DRC sweep across a design library, a stackup-compliance check before a release, or a
bulk cutout-and-export step feeding a downstream simulation pipeline.

Prerequisites
-------------

- A folder containing multiple ``.aedb`` designs to process.
- Familiarity with :doc:`../getting_started/quick_start` (the open/inspect/modify/save/close
  pattern applied here to each design in a loop) and :doc:`validation_and_drc` (the specific check
  used as the example recipe below).

Software and license requirements
-------------------------------------

- A licensed local AEDT installation, release 2026.1 or later for the default gRPC backend.
- The recipe demonstrated here (DC-short checking) is license-free layout inspection.

API concepts introduced
---------------------------

- Reusing ``with Edb(...) as edb:`` (the context-manager form, see
  :doc:`../getting_started/quick_start`) inside a loop, so every design's session is closed even if
  an exception is raised while processing that design.
- Structured logging with Python's standard ``logging`` module, giving every log line a
  per-design context.
- Aggregating per-design results into one deterministic, sortable summary.

Complete executable example
--------------------------------

.. code-block:: python

   import json
   import logging
   import shutil
   import tempfile
   from pathlib import Path

   from pyedb import Edb

   # --- 1. Define inputs -------------------------------------------------------------
   design_library_dir = Path(
       "my_design_library"
   )  # a folder containing several *.aedb designs
   source_designs = sorted(design_library_dir.glob("*.aedb"))
   assert source_designs, f"No .aedb designs found under {design_library_dir}"

   # --- 2. Configure structured logging so every line is traceable to one design -----
   logging.basicConfig(
       level=logging.INFO,
       format="%(asctime)s [%(levelname)s] %(message)s",
   )
   logger = logging.getLogger("batch_drc")

   work_dir = Path(tempfile.mkdtemp(prefix="pyedb_batch_"))


   def process_one_design(source_path: Path) -> dict:
       """Open a working copy of one design, run the recipe, and return a result record.

       Any exception raised while processing this design is caught here so that one bad
       design cannot abort the rest of the batch.
       """
       design_name = source_path.stem
       working_copy = work_dir / source_path.name
       result = {"design": design_name, "status": "unknown"}

       try:
           shutil.copytree(source_path, working_copy)
           # The context-manager form guarantees edb.close() runs even if the recipe below
           # raises partway through -- essential inside a batch loop, where a single leaked
           # RPC session or file lock can silently degrade every subsequent iteration.
           with Edb(edbpath=str(working_copy), version="2026.1") as edb:
               logger.info(
                   "[%s] Opened. %d nets, %d components.",
                   design_name,
                   len(edb.nets.netlist),
                   len(edb.components.instances),
               )

               # --- The recipe: a license-free DC-short check (swap in your own logic). ---
               shorts = edb.layout_validation.dc_shorts()
               result["net_count"] = len(edb.nets.netlist)
               result["component_count"] = len(edb.components.instances)
               result["dc_shorts_found"] = len(shorts)
               result["status"] = "PASS" if not shorts else "FAIL"
               if shorts:
                   logger.warning(
                       "[%s] %d DC short(s) found: %s", design_name, len(shorts), shorts
                   )
               else:
                   logger.info("[%s] No DC shorts found.", design_name)

       except Exception as exc:  # noqa: BLE001 -- intentional: isolate failures per design
           logger.error("[%s] Processing failed: %s", design_name, exc)
           result["status"] = "ERROR"
           result["error"] = str(exc)

       return result


   # --- 3. Run the recipe across every design in the library, isolating failures -------
   batch_results = [process_one_design(path) for path in source_designs]

   # --- 4. Assemble one deterministic, machine-readable summary ------------------------
   summary = {
       "total_designs": len(batch_results),
       "passed": sum(1 for r in batch_results if r["status"] == "PASS"),
       "failed": sum(1 for r in batch_results if r["status"] == "FAIL"),
       "errored": sum(1 for r in batch_results if r["status"] == "ERROR"),
       "results": batch_results,
   }
   summary_path = work_dir / "batch_summary.json"
   with open(summary_path, "w", encoding="utf-8") as f:
       json.dump(summary, f, indent=2)

   print(json.dumps({k: v for k, v in summary.items() if k != "results"}, indent=2))
   print(f"Full summary written to {summary_path}")

   # --- 5. Deterministic batch-level assertion (customize for your CI policy) ---------
   assert (
       summary["errored"] == 0
   ), f"{summary['errored']} design(s) failed to process; see log above"

Expected output
-------------------

.. code-block:: console

   2026-09-06 10:00:00 [INFO] [board_a] Opened. 187 nets, 42 components.
   2026-09-06 10:00:01 [INFO] [board_a] No DC shorts found.
   2026-09-06 10:00:02 [INFO] [board_b] Opened. 203 nets, 55 components.
   2026-09-06 10:00:03 [WARNING] [board_b] 1 DC short(s) found: [['VCC', 'GND']]
   {
     "total_designs": 2,
     "passed": 1,
     "failed": 1,
     "errored": 0
   }
   Full summary written to /tmp/.../batch_summary.json

Deterministic verification
-------------------------------

Every design produces an explicit ``status`` of ``PASS``, ``FAIL``, or ``ERROR`` — never an
ambiguous "it didn't crash, so presumably it's fine." The final assertion turns the whole batch into
one CI-checkable fact (``summary["errored"] == 0``), while still allowing individual ``FAIL``
results (a real DC short, not a script error) to be reviewed separately from ``ERROR`` results
(the script itself could not process that design at all).

Common failures and diagnostics
------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Symptom
     - Likely cause
     - Resolution
   * - One design's failure appears to affect subsequent designs in the batch (slower, or also
       failing)
     - A previous iteration's ``Edb`` session was not closed, leaking an RPC session or file lock.
     - Always use ``with Edb(...) as edb:`` (shown above) inside the per-design function, not a bare
       ``edb = Edb(...)`` followed by a ``close()`` call that might be skipped by an exception.
   * - The batch appears to hang on one specific design
     - That design is unusually large, or has a corrupted/partial ``.aedb`` folder that never opens
       or never finishes a query.
     - Add a per-design timeout at the process level (for example running each design in a
       subprocess with ``subprocess.run(..., timeout=...)``) if a single hung design must not block
       the whole batch indefinitely.
   * - ``summary["errored"]`` is non-zero
     - One or more designs raised an exception during processing (not a DC-short *finding*, an
       actual Python exception -- for example, a missing/corrupt ``.aedb`` folder).
     - Inspect ``result["error"]`` for each ``ERROR``-status entry in ``batch_summary.json`` to see
       the specific exception message per design.

Cleanup
-----------

Every ``Edb`` session is closed automatically by the ``with`` statement, even for designs that
raise an exception during processing. Remove ``work_dir`` (which contains one working copy per
design plus the summary JSON) once you have collected the results, for example with
``shutil.rmtree(work_dir, ignore_errors=True)``.

Next recommended example
-----------------------------

- :doc:`design_inventory_report` — a richer per-design recipe to substitute into
  ``process_one_design`` above.
- :doc:`compare_database_revisions` — combine with this batch pattern to regression-check an entire
  design library against a previous release in one run.
- :doc:`../getting_started/cli` — the ``pyedb`` command-line interface, useful when you want to
  drive a similar batch from a shell script or CI job without writing Python.

Related conceptual pages
-----------------------------

- :doc:`../getting_started/object_model` — the ``Edb`` context-manager protocol used throughout
  this example.

Version compatibility notes
--------------------------------

- The context-manager form of ``Edb`` and every method used in the example recipe are available on
  both the gRPC and DotNet backends.
