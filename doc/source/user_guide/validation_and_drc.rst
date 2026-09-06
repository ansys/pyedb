.. _validation_and_drc:

Validation and DRC
=====================

Check a design for common layout hygiene issues, or run a full design-rule check (DRC) against a
structured rule deck.

Prerequisites
-------------

- An open ``Edb`` instance (see :doc:`../getting_started/quick_start`).

Public API entry points
-------------------------

- :attr:`Edb.layout_validation <pyedb.grpc.edb.Edb.layout_validation>` — returns
  :class:`LayoutValidation <pyedb.grpc.database.layout_validation.LayoutValidation>`; built-in hygiene
  and repair checks.
- :class:`pyedb.workflows.drc.drc.Drc` and :class:`pyedb.workflows.drc.drc.Rules` — a separate,
  more comprehensive design-rule-check engine (spacing, manufacturing, high-speed, and test rules,
  with IPC-D-356A export).

These two tools are complementary: use ``edb.layout_validation`` for quick built-in hygiene checks
(DC shorts, disjoint nets, illegal names) that need no external rule deck, and use ``Drc``/``Rules``
when you need a structured, reusable, project-specific rule deck with more than 50 industry-standard
checks.

Procedure
---------

1. Find DC shorts without modifying the design.

   .. code-block:: python

      shorts = edb.layout_validation.dc_shorts()
      print(f"Found {len(shorts)} DC shorts")

2. Find and fix illegal net names.

   .. code-block:: python

      edb.layout_validation.illegal_net_names(fix=True)

3. Build a rule deck and run the full DRC engine.

   .. code-block:: python

      from pyedb.workflows.drc.drc import Drc, Rules

      rules = (
          Rules()
          .add_min_line_width("pwr", "15mil")
          .add_min_clearance("clk2data", "4mil", "CLK*", "DATA*")
          .add_min_annular_ring("via5", "5mil")
      )
      drc = Drc(edb)
      violations = drc.check(rules)
      print(f"Found {len(violations)} violations")

4. Export DRC violations to an IPC-D-356A netlist.

   .. code-block:: python

      drc.to_ipc356a("fab_review.ipc")

Complete example
-----------------

.. code-block:: python

   import re
   import tempfile
   from pathlib import Path

   from pyedb import Edb
   from pyedb.workflows.drc.drc import Drc, Rules

   # Same illegal-character pattern used internally by illegal_net_names(), used here only to
   # build a deterministic, independent check (see the note on illegal_net_names()'s return value
   # in "Common problems" below).
   _ILLEGAL_NET_NAME_PATTERN = r"[\(\)\\\/:;*?<>\'\"|`~$]"

   input_path = str(Path(tempfile.gettempdir()) / "drc_input.aedb")
   edb = Edb(edbpath=input_path, version="2026.1")

   shorts = edb.layout_validation.dc_shorts()
   print(f"Found {len(shorts)} DC shorts")

   # illegal_net_names(fix=True) mutates the in-memory database only; save is required to persist
   # it. The method does not return the count or list of renamed nets, so check the netlist
   # directly afterward instead of relying on its return value.
   edb.layout_validation.illegal_net_names(fix=True)
   still_illegal = [n for n in edb.nets.netlist if re.search(_ILLEGAL_NET_NAME_PATTERN, n)]
   assert (
       not still_illegal
   ), f"Illegal net names remain in memory after fix=True: {still_illegal}"

   rules = Rules().add_min_annular_ring("via5", "5mil")
   drc = Drc(edb)
   violations = drc.check(rules)
   print(f"Found {len(violations)} DRC violations")

   output_path = str(Path(tempfile.gettempdir()) / "drc_output.aedb")
   edb.save_as(output_path)
   edb.close()

   # Reopen the saved database and verify the illegal-net-name fix persisted to disk.
   edb_reopened = Edb(edbpath=output_path, version="2026.1")
   still_illegal_after_reopen = [
       n for n in edb_reopened.nets.netlist if re.search(_ILLEGAL_NET_NAME_PATTERN, n)
   ]
   assert (
       not still_illegal_after_reopen
   ), "Illegal net names reappeared after save_as + reopen"
   edb_reopened.close()

Expected result
----------------

``edb.layout_validation.dc_shorts()`` returns a list of ``[net_name, net_name]`` pairs for any shorted
nets found (empty on a design with no shorts). ``Drc.check(rules)`` returns a list of violation
records; ``Drc.to_ipc356a(path)`` writes an IPC-D-356A netlist file annotated with those violations.
The two assertions are the deterministic persistence check for the ``fix=True`` call: because
``illegal_net_names()`` does not return the count or list of nets it renamed (see "Common problems"
below), the example independently re-scans ``edb.nets.netlist`` for the same illegal-character
pattern, both immediately in memory and again after ``save_as``/close/reopen.

Backend and version notes
---------------------------

- ``edb.layout_validation`` is available on both backends with the same property name.
- ``Drc`` requires an already-open ``Edb`` session passed to its constructor; it builds spatial
  indexes immediately, so construct it once per design and reuse it across multiple ``check()`` calls
  rather than re-instantiating it.

Common problems
-----------------

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Symptom
     - Likely cause
     - Resolution
   * - ``illegal_net_names(fix=True)`` did not persist after reopening the design
     - Changes made with ``fix=True`` mutate the in-memory database only.
     - Call ``edb.save()`` (or ``edb.save_as(...)``) after any ``fix=True`` call.
   * - ``illegal_net_names(...)`` always returns ``None``, even though it counts renamed nets
       internally
     - The method's return value is not implemented — it logs the count via
       ``edb.logger`` but does not return it, regardless of ``fix``.
     - Do not rely on the return value. Check ``edb.logger`` output, or independently
       re-scan ``edb.nets.netlist`` for illegal characters as shown in the "Complete example" above.
   * - Rule deck fails to load from JSON
     - Using ``Rules.parse_file(...)``, which is not part of the public ``Rules`` API.
     - Load the file yourself and use ``Rules.from_dict(json.load(open(path)))`` instead.
   * - ``Drc(edb)`` raises or behaves unexpectedly
     - The ``Edb`` instance passed to the constructor was not fully open (for example ``active_db``
       is falsy) or has zero primitives to index.
     - Ensure the design is open and populated before constructing ``Drc``.

See also
--------

- :doc:`../workflows/drc/drc` — the full ``Drc``/``Rules`` API reference.
- :doc:`../getting_started/object_model` — the ``edb.layout_validation`` section.
- :doc:`pi_example_power_aware_dcir` — a complete power-integrity workflow that uses
  ``dc_shorts()`` to validate a power delivery network before creating a DCIR setup.
