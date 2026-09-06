.. _design_inventory_report:

Retrieve data from EDB: design inventory and audit report
=============================================================

Extract a complete, machine-readable snapshot of a design — layer stackup, net and component
counts, layout area and metal coverage, a bill of materials, and a materials-completeness audit —
without modifying the database. This is the pattern to reuse whenever you need to answer
"what is actually in this design?" programmatically instead of opening the AEDT GUI.

What you will learn
--------------------

- How to pull a single, structured statistics object covering layers, vias, traces, polygons, and
  net/component counts (:meth:`Edb.get_statistics <pyedb.grpc.edb.Edb.get_statistics>`).
- How to export a bill of materials (BOM) directly from ``edb.components``.
- How to audit the material library for definitions that are referenced by the stackup but
  missing electrical properties.
- How to assemble everything into one JSON report suitable for CI artifacts or dashboards.

When to use this workflow
----------------------------

Use this workflow as a first inspection step on any design you receive from someone else, as a
pre-flight check before starting a simulation project, or as a periodic health-check job that
tracks how a design's complexity (net count, via count, layer count) changes across revisions.

Prerequisites
-------------

- An open ``Edb`` instance pointing at an existing design (see
  :doc:`../getting_started/quick_start`). A freshly created, empty database will produce a report
  with every count at zero — open a real design to see meaningful numbers.

Software and license requirements
-------------------------------------

- A licensed local AEDT installation, release 2026.1 or later for the default gRPC backend.
- Every operation in this example is read-only layout inspection; no solver license is consumed.

API concepts introduced
---------------------------

- :meth:`Edb.get_statistics <pyedb.grpc.edb.Edb.get_statistics>` — returns a
  :class:`LayoutStatistics <pyedb.grpc.database.utility.layout_statistics.LayoutStatistics>` object
  with ``num_layers``, ``stackup_thickness``, ``num_vias``, ``num_nets``, ``num_traces``,
  ``num_polygons``, ``num_discrete_components``, ``num_resistors``, ``num_capacitors``,
  ``num_inductors``, ``layout_size``, and (when ``compute_area=True``) per-layer
  ``occupying_ratio``/``occupying_surface``.
- :meth:`Components.export_bom <pyedb.grpc.database.components.Components.export_bom>` — writes a
  CSV bill of materials (reference designator, part name, type, value) directly to disk.
- :attr:`Edb.materials <pyedb.grpc.edb.Edb.materials>` — iterate every material definition and
  inspect ``conductivity``, ``permittivity``, ``dielectric_loss_tangent``.

Complete executable example
--------------------------------

.. code-block:: python

   import json
   import shutil
   import tempfile
   from pathlib import Path

   import pyedb
   from pyedb import Edb

   # --- 1. Define inputs -------------------------------------------------------------
   source_path = "my_design.aedb"  # replace with the design you want to inspect

   # --- 2. Create a working copy (this workflow is read-only, but copying is still the
   #        safe default so a future edit to this script cannot accidentally touch the
   #        original file). ------------------------------------------------------------
   work_dir = Path(tempfile.mkdtemp(prefix="pyedb_inventory_"))
   working_copy = work_dir / "inspected_board.aedb"
   shutil.copytree(source_path, working_copy)

   # --- 3. Open the database -----------------------------------------------------------
   edb = Edb(edbpath=str(working_copy), version="2026.1")

   # --- 4. Retrieve layout statistics (compute_area=True adds per-layer copper coverage,
   #        at the cost of extra computation time on very large designs). --------------
   stats = edb.get_statistics(compute_area=True)

   # --- 5. Retrieve a materials-completeness audit -------------------------------------
   # A material with neither "conductivity" nor "permittivity" set in its property list is
   # incomplete: reading .conductivity/.permittivity on such a material silently returns a
   # default (0.0 / 1.0) instead of None or raising, so check all_properties explicitly
   # instead of checking the property values themselves.
   material_issues = []
   for material_name, material in edb.materials.materials.items():
       has_conductivity = "conductivity" in material.all_properties
       has_permittivity = "permittivity" in material.all_properties
       if not has_conductivity and not has_permittivity:
           material_issues.append(material_name)

   # --- 6. Export a bill of materials to CSV -------------------------------------------
   bom_path = work_dir / "bom.csv"
   bom_written = edb.components.export_bom(str(bom_path))
   assert bom_written, "BOM export failed"
   assert bom_path.exists(), "BOM file was not written to disk"

   # --- 7. Assemble one structured, machine-readable report ---------------------------
   report = {
       "database_path": str(working_copy),
       "pyedb_version": pyedb.__version__,
       "layer_count": stats.num_layers,
       "stackup_thickness_m": stats.stackup_thickness,
       "layout_size_m": stats.layout_size,
       "net_count": len(edb.nets.netlist),
       "power_ground_net_count": len(edb.nets.power),
       "signal_net_count": len(edb.nets.signal),
       "component_count": len(edb.components.instances),
       "resistor_count": stats.num_resistors,
       "capacitor_count": stats.num_capacitors,
       "inductor_count": stats.num_inductors,
       "via_count": stats.num_vias,
       "trace_count": stats.num_traces,
       "polygon_count": stats.num_polygons,
       "copper_coverage_by_layer": stats.occupying_ratio,
       "material_definitions_missing_properties": material_issues,
       "dc_shorts_found": len(edb.layout_validation.dc_shorts()),
       "bom_file": str(bom_path),
   }
   report["validation_result"] = (
       "PASS" if not material_issues and report["dc_shorts_found"] == 0 else "REVIEW"
   )

   # --- 8. Validate the report is well-formed before writing it -----------------------
   assert (
       report["layer_count"] > 0
   ), "Report shows zero layers -- is the design actually populated?"
   assert report["net_count"] >= 0

   report_path = work_dir / "design_inventory_report.json"
   with open(report_path, "w", encoding="utf-8") as f:
       json.dump(report, f, indent=2)
   print(json.dumps(report, indent=2))

   # --- 9. Close resources (this workflow never modifies the database, so there is
   #        nothing to save). -----------------------------------------------------------
   edb.close()

   print(f"Report written to {report_path}")

Expected output
-------------------

.. code-block:: console

   {
     "database_path": "/tmp/.../inspected_board.aedb",
     "pyedb_version": "0.83.0",
     "layer_count": 12,
     "stackup_thickness_m": 0.0016,
     "layout_size_m": [0.0, 0.0, 0.1016, 0.0762],
     "net_count": 187,
     "power_ground_net_count": 6,
     "signal_net_count": 181,
     "component_count": 42,
     "resistor_count": 18,
     "capacitor_count": 24,
     "inductor_count": 2,
     "via_count": 3512,
     "trace_count": 940,
     "polygon_count": 26,
     "copper_coverage_by_layer": {"TOP": 0.34, "GND1": 0.91, "...": "..."},
     "material_definitions_missing_properties": [],
     "dc_shorts_found": 0,
     "bom_file": "/tmp/.../bom.csv",
     "validation_result": "PASS"
   }
   Report written to /tmp/.../design_inventory_report.json

Exact numeric values depend on the design you open; the structure and the two ``assert`` checks
are deterministic and will hold for any populated design.

Deterministic verification
-------------------------------

``bom_written`` and ``bom_path.exists()`` are checked explicitly rather than assuming
``export_bom`` succeeded silently. The report itself asserts a non-zero layer count as a sanity
check that a real design (not an empty one) was opened, and ``validation_result`` gives a
deterministic PASS/REVIEW verdict a CI job can assert on directly
(``assert report["validation_result"] == "PASS"``).

Common failures and diagnostics
------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Symptom
     - Likely cause
     - Resolution
   * - Every count in the report is ``0``
     - ``source_path`` pointed at a newly created, empty database rather than an existing design.
     - Verify ``source_path`` points at a real ``.aedb`` folder containing an ``edb.def`` file.
   * - ``get_statistics(compute_area=True)`` is slow on a large design
     - Per-layer copper-coverage computation scans every primitive on every layer.
     - Call ``edb.get_statistics(compute_area=False)`` (the default) for a fast count-only report,
       and only enable ``compute_area=True`` when copper coverage is actually needed.
   * - ``material.conductivity`` reads as ``0.0`` (or ``permittivity`` reads as ``1.0``) for a
       material you expected to be fully defined
     - ``Material.conductivity``/``Material.permittivity`` never return ``None``: if the property
       was never set on the material definition, they silently return a default value (``0.0`` /
       ``1.0``) instead. Checking the raw property value cannot distinguish "genuinely 0" from
       "never set" — check ``"conductivity" in material.all_properties`` instead, as shown above.
     - Cross-check against :doc:`stackup_and_materials` and register the missing material property
       before relying on simulation results derived from it.

Cleanup
-----------

The ``edb`` session is explicitly closed above. Remove ``work_dir`` (which contains the working
copy, the BOM CSV, and the JSON report) once you have collected the artifacts you need, for example
with ``shutil.rmtree(work_dir, ignore_errors=True)``.

Next recommended example
-----------------------------

- :doc:`compare_database_revisions` — use the same report structure to detect what changed between
  two revisions of a design.
- :doc:`geometry_and_connectivity` — drill into specific nets or layers once the inventory report
  has told you where to look.

Related conceptual pages
-----------------------------

- :doc:`../getting_started/object_model` — the ``edb.materials``, ``edb.nets``, and
  ``edb.layout_validation`` sections.
- :doc:`stackup_and_materials` — fixing a material flagged as incomplete by this report.

Related API-reference pages
--------------------------------

- :class:`LayoutStatistics <pyedb.grpc.database.utility.layout_statistics.LayoutStatistics>`
- :class:`Components <pyedb.grpc.database.components.Components>`
- :class:`Materials <pyedb.grpc.database.definition.materials.Materials>`

Version compatibility notes
--------------------------------

- ``get_statistics``, ``export_bom``, and ``edb.materials`` are available on both the gRPC and
  DotNet backends with the same signatures.
