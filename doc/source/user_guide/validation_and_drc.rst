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

   import tempfile
   from pathlib import Path

   from pyedb import Edb
   from pyedb.workflows.drc.drc import Drc, Rules

   input_path = str(Path(tempfile.gettempdir()) / "drc_input.aedb")
   edb = Edb(edbpath=input_path, version="2026.1")

   shorts = edb.layout_validation.dc_shorts()
   print(f"Found {len(shorts)} DC shorts")

   rules = Rules().add_min_annular_ring("via5", "5mil")
   drc = Drc(edb)
   violations = drc.check(rules)
   print(f"Found {len(violations)} DRC violations")

   edb.close()

Expected result
----------------

``edb.layout_validation.dc_shorts()`` returns a list of ``[net_name, net_name]`` pairs for any shorted
nets found (empty on a design with no shorts). ``Drc.check(rules)`` returns a list of violation
records; ``Drc.to_ipc356a(path)`` writes an IPC-D-356A netlist file annotated with those violations.

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
