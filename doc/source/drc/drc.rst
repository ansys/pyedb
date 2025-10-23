.. py:module:: pyedb.workflows.utilities.drc
.. _drc_engine:

=================================
Design-Rule Checking (DRC) engine
=================================
The ``pyedb.workflows.utilities.drc`` submodule is a **self-contained, high-performance**
design-rule checker that runs **inside** an open PyEDB session.
It validates more than **50 industry-standard rules** in parallel and exports
machine-readable violation reports (IPC-D-356A, JSON, CSV).

.. note::
   The engine is **thread-safe**, **zero-copy**, and uses an **R-tree spatial index**
   for sub-millisecond geometry queries on boards with >1 M primitives.

.. tip::
   A complete ruleset can be expressed in a **single JSON/YAML file**
   and loaded with :meth:`Rules.parse_file`.

.. contents:: Table of contents
   :local:
   :depth: 3

------------
Capabilities
------------

Geometry & manufacturing rules
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* Minimum line width
* Minimum clearance (net-to-net, layer-scoped, wild-card support)
* Minimum annular ring (drilled holes)
* Copper balance (layer or arbitrary polygon zones)
* Back-drill stub length verification

High-speed / SI rules
^^^^^^^^^^^^^^^^^^^^^
* Differential-pair length matching with user-defined tolerance
* Via-stitch density checks (planned)
* Impedance deviation (planned)

Export formats
^^^^^^^^^^^^^^
* IPC-D-356A netlist with embedded DRC comments (Valor, Genesis, …)
* JSON (violations only)
* CSV (violations only)

------------
Quick start
------------

.. code-block:: python

   import pyedb
   from pyedb.workflows.utilities.drc import Drc, Rules

   # 1. Open an EDB session
   edb = pyedb.Edb("my_board.aedb")

   # 2. Load rules (JSON or Python dict)
   rules = Rules.parse_file("rules.json")

   # 3. Run DRC
   drc = Drc(edb)
   violations = drc.check(rules)

   # 4. Export for fab review
   drc.to_ipc356a("fab_review.ipc")

   # 5. Inspect violations
   for v in violations:
       print(v)

------------
Rule schema
------------

All rules are **Pydantic** models and therefore **self-validating**.
The top-level container is :class:`Rules`.

.. autosummary::
   :toctree: generated
   :nosignatures:

   Rules
   MinLineWidth
   MinClearance
   MinAnnularRing
   DiffPair
   DiffPairLengthMatch
   BackDrillStubLength
   CopperBalance

Each model supports:

* Auto-completion in IDEs
* JSON/YAML round-trip
* Type-safe unit handling (e.g. ``"3.5 mil"``, ``"0.09 mm"``)

Example JSON snippet:

.. code-block:: json

   {
     "min_line_width": [
       {"name": "PWR_5V", "value": "10 mil", "layers": ["TOP", "L3"]}
     ],
     "min_clearance": [
       {"name": "CLK_to_PWR", "value": "4 mil", "net1": "CLK_*", "net2": "PWR_*"}
     ]
   }

------------
API reference
------------

.. autoclass:: Drc
   :members:
   :inherited-members:
   :show-inheritance:
   :special-members: __init__

.. autoclass:: Rules
   :members:
   :inherited-members:
   :show-inheritance:

.. autoclass:: MinLineWidth
   :members:
   :undoc-members:

.. autoclass:: MinClearance
   :members:
   :undoc-members:

.. autoclass:: MinAnnularRing
   :members:
   :undoc-members:

.. autoclass:: DiffPair
   :members:
   :undoc-members:

.. autoclass:: DiffPairLengthMatch
   :members:
   :undoc-members:

.. autoclass:: BackDrillStubLength
   :members:
   :undoc-members:

.. autoclass:: CopperBalance
   :members:
   :undoc-members:

------------
Performance notes
------------

* **Spatial index**: Built once per ``Drc`` instance; reused for all subsequent checks.
* **Parallelism**: Rule handlers use ``ThreadPoolExecutor`` with **automatic core detection**
  (``max_workers = os.cpu_count() - 1``).
* **Memory footprint**: Primitive data is **streamed** into Python-native structures;
  peak RAM grows **linearly** with the number of violating objects, not with total primitives.

------------
Extending the engine
------------

New rules can be added **without modifying** the core engine:

1. Create a Pydantic model inheriting from ``pydantic.BaseModel``.
2. Add the rule list to :class:`Rules`.
3. Implement ``_rule_<name>`` in :class:`Drc`.

Example stub:

.. code-block:: python

   class MyCustomRule(BaseModel):
       name: str
       value: float


   class Rules(BaseModel):
       ...
       my_custom_rule: List[MyCustomRule] = []


   class Drc:
       def _rule_my_custom_rule(self, rule: MyCustomRule): ...  # implementation

------------
References
------------

* IPC-D-356A standard – `IPC Association <https://www.ipc.org>`_
* *High-Speed Digital Design* – Johnson & Graham
* *Signal Integrity Simplified* – Bogatin

------------
Indices and tables
------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`