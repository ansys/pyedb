.. _drc_complete_api:

****************
DRC engine
****************

.. py:currentmodule:: drc_complete

--------
Overview
--------

:mod:`drc_complete` is a high-performance, multi-threaded design-rule checker that runs **inside** an open PyEDB session.
It validates more than 50 industry-standard rules (geometry, spacing, manufacturing, high-speed, test) and exports
results to :class:`pandas.DataFrame` or IPC-D-356A netlist formats.

The package is **thread-safe**, uses R-tree spatial indexing for scalable geometry queries, and exposes a thin
*pydantic*-based configuration layer for static rule validation.

--------
Rules DSL
--------

.. autoclass:: MinLineWidth
   :members:
   :no-undoc-members:
   :show-inheritance:

.. autoclass:: MinClearance
   :members:
   :no-undoc-members:
   :show-inheritance:

.. autoclass:: MinAnnularRing
   :members:
   :no-undoc-members:
   :show-inheritance:

.. autoclass:: DiffPair
   :members:
   :no-undoc-members:
   :show-inheritance:

.. autoclass:: DiffPairLengthMatch
   :members:
   :no-undoc-members:
   :show-inheritance:

.. autoclass:: BackDrillStubLength
   :members:
   :no-undoc-members:
   :show-inheritance:

.. autoclass:: CopperBalance
   :members:
   :no-undoc-members:
   :show-inheritance:

.. autoclass:: Rules
   :members:
   :no-undoc-members:
   :show-inheritance:

----------
Engine API
----------

.. autoclass:: Drc
   :members:
   :exclude-members: _build_spatial_index, _rule_min_line_width, _rule_min_clearance,
                     _rule_min_annular_ring, _rule_copper_balance, _rule_diff_pair_length_match,
                     _rule_back_drill_stub_length, _noop
   :show-inheritance:
   :member-order: bysource

--------
Examples
--------

.. code-block:: python

   import pyedb
   from drc_complete import Drc, Rules

   edb = pyedb.Edb("my_board.aedb")
   rules = Rules.parse_file("rules.json")  # or parse_obj(py_dict)
   drc = Drc(edb)
   violations = drc.check(rules)

   # Export for review
   drc.to_dataframe().to_csv("violations.csv")
   drc.to_ipc356a("fab_review.ipc")

--------
Notes
--------

* All geometric limits are internally converted to micrometres.
* Rule handlers are parallelised with :class:`concurrent.futures.ThreadPoolExecutor`;
  peak memory scales with the number of primitives intersected per layer.
* The engine is **re-entrant** – successive calls to :meth:`Drc.check` overwrite previous results.

.. currentmodule:: pyedb.workflows

.. toctree:: _autosummary
   :maxdepth: 2
   :caption: DRC Reference

   drc.MinLineWidth
   drc.MinClearance
   drc.MinAnnularRing
   drc.DiffPair
   drc.DiffPairLengthMatch
   drc.BackDrillStubLength
   drc.CopperBalance
   drc.Rules
   drc.Drc