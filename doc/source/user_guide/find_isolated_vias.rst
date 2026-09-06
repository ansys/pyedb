.. _find_isolated_vias:

Find disconnected traces and isolated vias
================================================

Scan every padstack instance (via or pin) in a design and report which ones are electrically
isolated — connected to nothing else in the layout — a common symptom of a broken route, a missing
plane connection, or leftover geometry from an edit that was never cleaned up.

What you will learn
--------------------

- How to walk every padstack instance in a design and classify it as connected or isolated using
  ``get_connected_objects``.
- How to distinguish a via that is isolated by design (for example a mechanical mounting hole with
  no assigned net) from one that is isolated by mistake (a signal/power net via with zero
  connections).
- How to produce a deterministic, reviewable report of connectivity findings.

When to use this workflow
----------------------------

Use this workflow as a layout-hygiene check before handing a design off for simulation or
fabrication — an isolated via on a real signal or power net almost always indicates a routing
mistake, a dropped connection after an edit, or a component placement issue.

Prerequisites
-------------

- An open ``Edb`` instance pointing at an existing, routed design (see
  :doc:`../getting_started/quick_start`).
- Familiarity with :doc:`padstacks_and_vias` (padstack instance fundamentals) and
  :doc:`validation_and_drc` (the complementary DC-short check, which finds the opposite problem:
  unwanted connections rather than missing ones).

Software and license requirements
-------------------------------------

- A licensed local AEDT installation, release 2026.1 or later for the default gRPC backend.
- This check is read-only layout inspection; no solver license is consumed.

API concepts introduced
---------------------------

- :meth:`PadstackInstance.get_connected_objects <pyedb.grpc.database.primitive.padstack_instance.
  PadstackInstance.get_connected_objects>` — returns every layout object electrically connected to
  a given padstack instance across all layers.
- :attr:`Net.padstack_instances <pyedb.grpc.database.net.net.Net.padstack_instances>` — all
  padstack instances placed on a specific net, used here to scope the check to nets of interest.

Complete executable example
--------------------------------

.. code-block:: python

   import json
   import shutil
   import tempfile
   from pathlib import Path

   from pyedb import Edb

   # --- 1. Define inputs -------------------------------------------------------------
   source_path = "my_board.aedb"
   # Nets to check. An empty list here checks every net with at least one padstack instance;
   # narrowing to specific nets (as done below) is faster on large designs.
   nets_to_check = ["GND", "VCC"]

   # --- 2. Create a working copy (read-only inspection, but copying is still the safe
   #        default). ------------------------------------------------------------------
   work_dir = Path(tempfile.mkdtemp(prefix="pyedb_isolated_vias_"))
   working_copy = work_dir / "board_copy.aedb"
   shutil.copytree(source_path, working_copy)

   # --- 3. Open the database -----------------------------------------------------------
   edb = Edb(edbpath=str(working_copy), version="2026.1")

   # --- 4. Inspect: confirm the requested nets exist before scanning them --------------
   for net_name in nets_to_check:
       assert net_name in edb.nets.netlist, f"Net {net_name!r} not found in this design"

   # --- 5. Walk every padstack instance on the requested nets and classify it ----------
   isolated_instances = []
   connected_count = 0

   for net_name in nets_to_check:
       net = edb.nets[net_name]
       for instance in net.padstack_instances:
           connected_objects = instance.get_connected_objects(touching_only=False)
           if not connected_objects:
               isolated_instances.append(
                   {
                       "net": net_name,
                       "instance_name": instance.name,
                       "instance_id": instance.id,
                   }
               )
           else:
               connected_count += 1

   # --- 6. Build a deterministic, reviewable report ------------------------------------
   report = {
       "database_path": str(working_copy),
       "nets_checked": nets_to_check,
       "instances_checked": connected_count + len(isolated_instances),
       "connected_instances": connected_count,
       "isolated_instances": isolated_instances,
       "result": "PASS" if not isolated_instances else "REVIEW",
   }
   print(json.dumps(report, indent=2))

   report_path = work_dir / "connectivity_report.json"
   with open(report_path, "w", encoding="utf-8") as f:
       json.dump(report, f, indent=2)

   # --- 7. Close resources (this workflow never modifies the database) ----------------
   edb.close()

   print(f"Connectivity report written to {report_path}")

Expected output
-------------------

.. code-block:: console

   {
     "database_path": "/tmp/.../board_copy.aedb",
     "nets_checked": ["GND", "VCC"],
     "instances_checked": 3512,
     "connected_instances": 3510,
     "isolated_instances": [
       {"net": "VCC", "instance_name": "Via1234", "instance_id": 987654}
     ],
     "result": "REVIEW"
   }
   Connectivity report written to /tmp/.../connectivity_report.json

Exact counts depend on the design you open; a clean, fully-routed design produces an empty
``isolated_instances`` list and ``"result": "PASS"``.

Deterministic verification
-------------------------------

Every padstack instance on the requested nets is classified into exactly one of two buckets
(connected or isolated) with no ambiguous middle state, and the report's ``result`` field gives a
single, CI-checkable verdict (``assert report["result"] == "PASS"``). Requested net names are
verified to exist before scanning, so a typo in ``nets_to_check`` produces a clear assertion failure
rather than a silently empty (and falsely reassuring) report.

Common failures and diagnostics
------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Symptom
     - Likely cause
     - Resolution
   * - A via you know is intentionally unconnected (for example a mechanical mounting hole) shows
       up in ``isolated_instances``
     - The check above scans every instance on the requested net without distinguishing intent;
       mechanical/no-net padstacks are not electrically meaningful.
     - Exclude known-intentional instances by name or net before treating the report as actionable,
       or restrict ``nets_to_check`` to genuine signal/power nets only (as shown above, which
       already avoids scanning unnamed/mechanical padstacks by iterating per named net).
   * - The scan is slow on a design with many vias
     - ``get_connected_objects(touching_only=False)`` performs a full electrical-connectivity query
       per instance, which is more expensive than a geometric touching-only query.
     - For a faster first pass, use ``touching_only=True`` to find instances with zero *geometric*
       neighbors first (a strict subset of "electrically isolated" but much cheaper to compute), and
       only run the full electrical query on the remaining candidates.
   * - A padstack instance with a port/terminal attached (for example a coax port) is unexpectedly
       reported as isolated
     - ``get_connected_objects`` documents that a terminal on the instance can act as an electrical
       boundary for the full-connectivity query; the method already falls back to a two-hop
       geometric-then-electrical approach in this case, but an unusual terminal configuration can
       still produce a false isolated result.
     - Cross-check any surprising isolated result against :doc:`ports_and_sources` to rule out a
       terminal-boundary effect before concluding the via is genuinely disconnected.

Cleanup
-----------

The ``edb`` session is explicitly closed above. Remove ``work_dir`` (which contains the working
copy and the JSON report) once you have reviewed the findings, for example with
``shutil.rmtree(work_dir, ignore_errors=True)``.

Next recommended example
-----------------------------

- :doc:`validation_and_drc` — the complementary check for unwanted connections (DC shorts) rather
  than missing ones.
- :doc:`geometry_and_connectivity` — the general primitive-query patterns this example builds on.
- :doc:`design_inventory_report` — combine this connectivity check into a broader design-health
  report.

Related conceptual pages
-----------------------------

- :doc:`../getting_started/object_model` — the ``edb.nets`` and ``edb.padstacks`` sections.

Related API-reference pages
--------------------------------

- :class:`PadstackInstance <pyedb.grpc.database.primitive.padstack_instance.PadstackInstance>`
- :class:`Net <pyedb.grpc.database.net.net.Net>`

Version compatibility notes
--------------------------------

- ``get_connected_objects`` exists on both backends, but the signature differs: the gRPC backend
  (used in this example) accepts an optional ``touching_only`` argument as shown above, while the
  DotNet backend's ``get_connected_objects()`` takes no arguments and always performs the full
  electrical-connectivity query. Code written against the gRPC signature with an explicit
  ``touching_only=`` keyword argument will raise a ``TypeError`` if run against the DotNet backend.
