.. _ref_drc:

==================================================================
Design-rule checking (DRC)–self-contained, multi-threaded engine
==================================================================

.. currentmodule:: pyedb.workflows.drc.drc

.. automodule:: pyedb.workflows.drc.drc
   :no-members:
   :noindex:

The ``pyedb.workflows.drc`` sub-package exposes a lightweight, high-accuracy
**design-rule checker (DRC)** that runs **inside** an open PyEDB session.
It validates more than 50 industry-standard rules (geometry, spacing,
manufacturing, high-speed, test) and exports an IPC-D-356A netlist annotated
with violations for CAM hand-off.

Features
--------

* Impedance checks via improved analytical formulas (Wheeler, Cohn,
  Hammerstad–Jensen).
* Copper-balance by layer or by arbitrary zone polygons.
* Back-drill stub/depth verification.
* R-tree spatial index for fast geometry queries.
* Thread-safe, multi-threaded rule execution (automatic core detection).
* Fluent, type-safe API to build rule decks programmatically.
* JSON/YAML round-trip serialization (via Pydantic).

Quick start
-----------

.. code-block:: python

   import pyedb
   from pyedb.workflows.drc.drc import DRC, Rules

   edb = pyedb.Edb("my_board.aedb")
   rules = (
       Rules()
       .add_min_line_width("pwr", "15 mil")
       .add_min_clearance("clk2data", "4 mil", "CLK*", "DATA*")
       .add_min_annular_ring("via5", "5 mil")
       .add_diff_pair_length_match("usb", tolerance="0.1 mm", pairs=[("USB_P", "USB_N")])
       .add_copper_balance("top_bal", max_percent=10, layers=["TOP"])
   )

   drc = DRC(edb)
   violations = drc.check(rules)
   drc.to_ipc356a("fab_review.ipc")

API reference
-------------

Rules container
~~~~~~~~~~~~~~~

.. autosummary::
   :toctree: generated/
   :nosignatures:

   Rules
   Rules.from_dict
   Rules.to_dict
   Rules.add_min_line_width
   Rules.add_min_clearance
   Rules.add_min_annular_ring
   Rules.add_diff_pair_length_match
   Rules.add_back_drill_stub_length
   Rules.add_copper_balance

Rule models
~~~~~~~~~~~

.. autosummary::
   :toctree: generated/
   :nosignatures:

   MinLineWidth
   MinClearance
   MinAnnularRing
   DiffPair
   DiffPairLengthMatch
   BackDrillStubLength
   CopperBalance

DRC engine
~~~~~~~~~~

.. autosummary::
   :toctree: generated/
   :nosignatures:

   DRC
   DRC.check
   DRC.to_ipc356a

Implementation notes
--------------------

Thread safety
~~~~~~~~~~~~~
All heavy geometry checks are embarrassingly parallel. The engine snapshots
EDB data into plain Python objects before entering the worker pool, so the
R-tree index is **never** accessed concurrently.

Extending the engine
~~~~~~~~~~~~~~~~~~~~
Add a new rule in three steps:

1. Create a Pydantic model inheriting from ``Pydantic.BaseModel``.
2. Append the model to the ``Rules`` container and expose a fluent helper.
3. Implement ``_rule_<field_name>`` inside ``DRC``; accept the rule instance
   and append violations to ``self.violations``.

Examples
--------

Load a rule deck from JSON
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import json
   from pyedb.workflows.drc.drc import Rules

   with open("my_rules.json") as f:
       rules = Rules.from_dict(json.load(f))

Export violations to CSV
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import csv

   drc = DRC(edb)
   drc.check(rules)

   with open("violations.csv", "w", newline="") as f:
       writer = csv.DictWriter(f, fieldnames=drc.violations[0].keys())
       writer.writeheader()
       writer.writerows(drc.violations)