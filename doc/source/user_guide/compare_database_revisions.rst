.. _compare_database_revisions:

Compare two database revisions
====================================

Detect exactly what changed between two revisions of the same design — a new stackup layer, a
renamed net, an added component — by exporting each revision to a structured configuration file and
diffing the two files, instead of trying to compare ``.aedb`` binary folders directly.

What you will learn
--------------------

- How to export a complete, structured snapshot of a design using the configuration system
  (:doc:`../configuration/index`), independent of any change you intend to apply.
- How to compute a deterministic, human-readable diff between two such snapshots.
- How to turn that diff into a pass/fail regression check suitable for CI.

When to use this workflow
----------------------------

Use this workflow whenever you need to answer "what changed?" between two design revisions — after
a layout re-route, after a stackup update from manufacturing, or as an automated regression gate in
a CI pipeline that fails a pull request if an unexpected net or component was removed.

Prerequisites
-------------

- Two existing ``Edb`` designs to compare (for example, a released baseline and a candidate
  revision). This example also demonstrates the technique on a single design by comparing it
  against itself after one deliberate change, so you can try it immediately without needing two
  real revisions on hand.

Software and license requirements
-------------------------------------

- A licensed local AEDT installation, release 2026.1 or later for the default gRPC backend.
- Exporting configuration data is license-free layout inspection; no solver license is consumed.

API concepts introduced
---------------------------

- :meth:`Configuration.export <pyedb.configuration.configuration.Configuration.export>` — writes a
  structured JSON/TOML snapshot of a design's stackup, nets, components, padstacks, ports, sources,
  and setups.
- Standard library ``json`` and ``difflib``/set operations — used here to compute the diff itself;
  no PyEDB-specific comparison API is required once both revisions are exported to JSON.

Complete executable example
--------------------------------

.. code-block:: python

   import json
   import shutil
   import tempfile
   from pathlib import Path

   from pyedb import Edb

   # --- 1. Define inputs -------------------------------------------------------------
   # Replace with your two real revisions. To try this example immediately without two
   # designs on hand, both paths below can point at the same source; a deliberate change
   # is made to the "revision B" copy in step 3 so the diff has something to show.
   revision_a_path = "my_board_v1.aedb"
   revision_b_path = (
       "my_board_v1.aedb"  # substitute "my_board_v2.aedb" for a real comparison
   )

   work_dir = Path(tempfile.mkdtemp(prefix="pyedb_compare_revisions_"))


   def export_snapshot(source_path: str, label: str) -> Path:
       """Open a working copy of a design and export its configuration snapshot to JSON."""
       working_copy = work_dir / f"{label}.aedb"
       shutil.copytree(source_path, working_copy)
       edb = Edb(edbpath=str(working_copy), version="2026.1")
       snapshot_path = work_dir / f"{label}_snapshot.json"
       exported = edb.configuration.export(str(snapshot_path))
       assert exported, f"Configuration export failed for {label}"
       assert snapshot_path.exists(), f"Snapshot file was not written for {label}"
       edb.close()
       return snapshot_path


   # --- 2. Export revision A's snapshot -------------------------------------------------
   snapshot_a_path = export_snapshot(revision_a_path, "revision_a")

   # --- 3. (Optional, for a self-contained demo) make one deliberate change to a copy of
   #        revision B before exporting its snapshot, so the diff below has content. -----
   revision_b_copy = work_dir / "revision_b.aedb"
   shutil.copytree(revision_b_path, revision_b_copy)
   edb_b = Edb(edbpath=str(revision_b_copy), version="2026.1")
   edb_b.stackup.add_layer(
       layer_name="DEMO_LAYER", layer_type="signal", material="copper", thickness="18um"
   )
   edb_b.save()
   edb_b.close()
   snapshot_b_path = export_snapshot(str(revision_b_copy), "revision_b")

   # --- 4. Load both snapshots and compare structurally --------------------------------
   with open(snapshot_a_path, encoding="utf-8") as f:
       snapshot_a = json.load(f)
   with open(snapshot_b_path, encoding="utf-8") as f:
       snapshot_b = json.load(f)

   # --- 5. Compare stackup layer names (present in both snapshots as a "stackup" section) ---
   layers_a = {layer["name"] for layer in snapshot_a.get("stackup", {}).get("layers", [])}
   layers_b = {layer["name"] for layer in snapshot_b.get("stackup", {}).get("layers", [])}

   added_layers = layers_b - layers_a
   removed_layers = layers_a - layers_b

   # --- 6. Compare net classifications (the exported "nets" section is a dict with
   #        "signal_nets" and "power_ground_nets" lists of plain net-name strings). -----
   nets_a = set(
       snapshot_a.get("nets", {}).get("signal_nets", [])
       + snapshot_a.get("nets", {}).get("power_ground_nets", [])
   )
   nets_b = set(
       snapshot_b.get("nets", {}).get("signal_nets", [])
       + snapshot_b.get("nets", {}).get("power_ground_nets", [])
   )
   added_nets = nets_b - nets_a
   removed_nets = nets_a - nets_b

   # --- 7. Build a deterministic, structured diff report -------------------------------
   diff_report = {
       "revision_a": str(revision_a_path),
       "revision_b": str(revision_b_copy),
       "layers_added": sorted(added_layers),
       "layers_removed": sorted(removed_layers),
       "nets_added": sorted(added_nets),
       "nets_removed": sorted(removed_nets),
   }
   diff_report["has_changes"] = any(
       [
           diff_report["layers_added"],
           diff_report["layers_removed"],
           diff_report["nets_added"],
           diff_report["nets_removed"],
       ]
   )

   print(json.dumps(diff_report, indent=2))

   # --- 8. Deterministic regression-gate assertion (customize for your CI policy) -----
   # Example policy: fail if any net was removed (a common sign of an accidental layout
   # regression), but allow layers/nets to be added freely.
   assert not diff_report[
       "nets_removed"
   ], f"Regression: net(s) removed: {diff_report['nets_removed']}"

   print(f"Diff report written. has_changes={diff_report['has_changes']}")

Expected output
-------------------

.. code-block:: console

   {
     "revision_a": "my_board_v1.aedb",
     "revision_b": "/tmp/.../revision_b.aedb",
     "layers_added": ["DEMO_LAYER"],
     "layers_removed": [],
     "nets_added": [],
     "nets_removed": [],
     "has_changes": true
   }
   Diff report written. has_changes=True

When comparing two genuinely different designs, the exact contents of ``layers_added``/
``nets_added``/etc. reflect the real differences between them.

Deterministic verification
-------------------------------

Both ``Configuration.export`` calls are checked for a truthy return value and for the snapshot file
actually existing on disk before anything is compared. The diff itself is computed from plain set
operations on structured JSON data (not a brittle text diff of two ``.aedb`` binary folders), so the
result is exact and reproducible. The final assertion demonstrates how to turn the diff into a
concrete CI regression gate — customize the policy (which kinds of changes are acceptable) to match
your team's review process.

Common failures and diagnostics
------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Symptom
     - Likely cause
     - Resolution
   * - ``snapshot.get("nets", {})`` does not contain the net you expect
     - The exported ``"nets"`` section groups net names into two flat lists,
       ``"signal_nets"`` and ``"power_ground_nets"`` (confirmed against
       ``pyedb.configuration.cfg_nets.CfgNets.get_data_from_db``), not a list of per-net objects.
       A net that has not been explicitly classified may not appear where you expect.
     - Print ``json.dumps(snapshot_a["nets"], indent=2)`` to inspect both lists directly, and
       remember that net classification (:doc:`components_and_nets`) affects which list a net
       appears in.
   * - The diff shows unrelated noise (for example every variable changing) between two revisions
       you expect to be nearly identical
     - The snapshot export defaults to including every section (stackup, setups, sources, ports,
       nets, components, and more); unrelated sections may differ for reasons not relevant to your
       comparison (for example auto-generated names).
     - Pass explicit ``False`` for sections you do not want to compare when calling
       ``edb.configuration.export(path, setups=False, sources=False, ports=False, ...)`` to narrow
       the snapshot to only the sections you care about.

Cleanup
-----------

All ``edb`` sessions above are explicitly closed. Remove ``work_dir`` (which contains both working
copies and both JSON snapshots) once you have reviewed the diff, for example with
``shutil.rmtree(work_dir, ignore_errors=True)``.

Next recommended example
-----------------------------

- :doc:`design_inventory_report` — the single-revision version of this report; run it on each
  revision individually before diffing them.
- :doc:`batch_processing_multiple_designs` — apply this comparison across an entire library of
  designs instead of a single pair.
- :doc:`../configuration/index` — the full configuration-file architecture this example's export
  step is built on.

Related conceptual pages
-----------------------------

- :doc:`../configuration/file_architecture` — the JSON/TOML schema produced by
  ``Configuration.export``.

Related API-reference pages
--------------------------------

- :class:`Configuration <pyedb.configuration.configuration.Configuration>`

Version compatibility notes
--------------------------------

- ``Configuration.export`` is available on both the gRPC and DotNet backends with the same
  signature. The exact JSON schema of the exported sections is version-sensitive (see "Common
  failures" above) — pin your PyEDB version in CI if you depend on specific key names in the
  exported snapshot.
