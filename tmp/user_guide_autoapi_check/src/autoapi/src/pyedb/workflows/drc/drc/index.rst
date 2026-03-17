src.pyedb.workflows.drc.drc
===========================

.. py:module:: src.pyedb.workflows.drc.drc

.. autoapi-nested-parse::

   Design Rule Check (DRC) engine for PyEDB.

   This module provides a high-performance, multi-threaded design-rule checker
   that runs inside an open PyEDB session and validates industry-standard rules
   including geometry, spacing, manufacturing, high-speed, and test constraints.

   The DRC engine features:

   - Multi-threaded rule checking using ThreadPoolExecutor
   - R-tree spatial indexing for fast geometry queries
   - Impedance checks via analytical formulas (Wheeler, Cohn, Hammerstad-Jensen)
   - Copper balance verification by layer or zone polygons
   - Back-drill stub and depth verification
   - IPC-D-356A netlist export with DRC annotations

   Examples
   --------
   Basic DRC workflow:

   >>> import pyedb
   >>> from pyedb.workflows.drc.drc import Drc, Rules
   >>> edb = pyedb.Edb(edbpath="my_board.aedb")
   >>> rules = Rules.parse_file("rules.json")
   >>> drc = Drc(edb)
   >>> violations = drc.check(rules)
   >>> print(f"Found {len(violations)} violations")

   Build rules programmatically:

   >>> rules = (
   ...     Rules()
   ...     .add_min_line_width("trace_width", "3.5mil")
   ...     .add_min_clearance("clk2data", "4mil", "CLK*", "DATA*")
   ...     .add_copper_balance("top_balance", max_percent=10, layers=["TOP"])
   ... )
   >>> drc = Drc(edb)
   >>> violations = drc.check(rules)

   Export results for fabrication review:

   >>> drc.to_ipc356a("fab_review.ipc")



Classes
-------

.. autoapisummary::

   src.pyedb.workflows.drc.drc.MinLineWidth
   src.pyedb.workflows.drc.drc.MinClearance
   src.pyedb.workflows.drc.drc.MinAnnularRing
   src.pyedb.workflows.drc.drc.DiffPair
   src.pyedb.workflows.drc.drc.DiffPairLengthMatch
   src.pyedb.workflows.drc.drc.BackDrillStubLength
   src.pyedb.workflows.drc.drc.CopperBalance
   src.pyedb.workflows.drc.drc.Rules
   src.pyedb.workflows.drc.drc.Drc


Module Contents
---------------

.. py:class:: MinLineWidth(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Minimum trace width constraint rule.

   This rule validates that all trace widths meet or exceed a specified
   minimum value on selected layers.

   Attributes
   ----------
   name : str
       Rule identifier for reporting violations.
   value : str
       Minimum acceptable width with unit (e.g., ``"3.5mil"``, ``"0.1mm"``).

   Examples
   --------
   >>> rule = MinLineWidth(name="signal_width", value="3.5mil")
   >>> rule.name
   'signal_width'


   .. py:attribute:: name
      :type:  str


   .. py:attribute:: value
      :type:  str


.. py:class:: MinClearance(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Minimum spacing constraint between nets.

   This rule validates that spacing between specified nets meets or exceeds
   a minimum clearance value. Supports wildcard matching for net names.

   Attributes
   ----------
   name : str
       Rule identifier for reporting violations.
   value : str
       Minimum acceptable clearance with unit (e.g., ``"4mil"``, ``"0.15mm"``).
   net1 : str
       First net name or wildcard pattern (``"*"`` matches all nets).
   net2 : str
       Second net name or wildcard pattern (``"*"`` matches all nets).

   Examples
   --------
   >>> rule = MinClearance(name="clk2data", value="4mil", net1="CLK*", net2="DATA*")
   >>> rule.net1
   'CLK*'


   .. py:attribute:: name
      :type:  str


   .. py:attribute:: value
      :type:  str


   .. py:attribute:: net1
      :type:  str


   .. py:attribute:: net2
      :type:  str


.. py:class:: MinAnnularRing(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Minimum annular ring constraint for drilled holes.

   This rule validates that the copper ring around drilled holes (vias, pins)
   meets a minimum width requirement.

   Attributes
   ----------
   name : str
       Rule identifier for reporting violations.
   value : str
       Minimum acceptable ring width with unit (e.g., ``"2mil"``, ``"0.05mm"``).

   Examples
   --------
   >>> rule = MinAnnularRing(name="via_ring", value="2mil")
   >>> rule.value
   '2mil'


   .. py:attribute:: name
      :type:  str


   .. py:attribute:: value
      :type:  str


.. py:class:: DiffPair(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Differential pair net definition.

   Defines a single differential pair consisting of positive and negative nets.

   Attributes
   ----------
   positive : str
       Positive net name in the differential pair.
   negative : str
       Negative net name in the differential pair.

   Examples
   --------
   >>> pair = DiffPair(positive="USB_DP", negative="USB_DN")
   >>> pair.positive
   'USB_DP'


   .. py:attribute:: positive
      :type:  str


   .. py:attribute:: negative
      :type:  str


.. py:class:: DiffPairLengthMatch(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Length matching constraint for differential pairs.

   This rule validates that the length difference between positive and
   negative traces in differential pairs stays within tolerance.

   Attributes
   ----------
   name : str
       Rule identifier for reporting violations.
   tolerance : str
       Maximum allowed length difference with unit (e.g., ``"0.1mm"``, ``"5mil"``).
   pairs : list of DiffPair
       List of differential pairs to validate.

   Examples
   --------
   >>> pair1 = DiffPair(positive="USB_DP", negative="USB_DN")
   >>> rule = DiffPairLengthMatch(name="usb_match", tolerance="0.1mm", pairs=[pair1])
   >>> rule.tolerance
   '0.1mm'


   .. py:attribute:: name
      :type:  str


   .. py:attribute:: tolerance
      :type:  str


   .. py:attribute:: pairs
      :type:  list[DiffPair]


.. py:class:: BackDrillStubLength(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Maximum back-drill stub length constraint.

   This rule validates that remaining stub length after back-drilling
   stays below a maximum value to minimize signal reflections.

   Attributes
   ----------
   name : str
       Rule identifier for reporting violations.
   value : str
       Maximum allowed stub length with unit (e.g., ``"6mil"``, ``"0.15mm"``).

   Examples
   --------
   >>> rule = BackDrillStubLength(name="max_stub", value="6mil")
   >>> rule.value
   '6mil'


   .. py:attribute:: name
      :type:  str


   .. py:attribute:: value
      :type:  str


.. py:class:: CopperBalance(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Copper density balance constraint.

   This rule validates that copper distribution across layers stays within
   acceptable balance limits to prevent warping during fabrication.

   Attributes
   ----------
   name : str
       Rule identifier for reporting violations.
   max_percent : int
       Maximum allowed imbalance percentage (e.g., ``15`` for 15%).
   layers : list of str
       Layer names to check for balance.

   Examples
   --------
   >>> rule = CopperBalance(name="top_balance", max_percent=10, layers=["TOP"])
   >>> rule.max_percent
   10


   .. py:attribute:: name
      :type:  str


   .. py:attribute:: max_percent
      :type:  int


   .. py:attribute:: layers
      :type:  list[str]


.. py:class:: Rules(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Centralized container for all design rule categories.

   This class provides a type-safe, serializable container for design rules
   with JSON/YAML round-trip support and a fluent API for building rule decks.

   Attributes
   ----------
   min_line_width : list of MinLineWidth
       Minimum acceptable trace width rules per layer or globally.
   min_clearance : list of MinClearance
       Spacing requirements between nets (wildcards allowed).
   min_annular_ring : list of MinAnnularRing
       Minimum annular ring requirements for drilled holes.
   diff_pair_length_match : list of DiffPairLengthMatch
       Length matching constraints for differential pairs.
   back_drill_stub_length : list of BackDrillStubLength
       Maximum allowed back-drill stub length constraints.
   copper_balance : list of CopperBalance
       Copper density balance limits per layer or zone.

   Examples
   --------
   Build rules programmatically:

   >>> rules = (
   ...     Rules()
   ...     .add_min_line_width("pwr", "15mil")
   ...     .add_min_clearance("clk2data", "4mil", "CLK*", "DATA*")
   ...     .add_min_annular_ring("via5", "5mil")
   ...     .add_copper_balance("top_bal", max_percent=10, layers=["TOP"])
   ... )

   Load from JSON file:

   >>> rules = Rules.parse_file("my_rules.json")

   Export to JSON:

   >>> rules.model_dump_json(indent=2)


   .. py:attribute:: min_line_width
      :type:  list[MinLineWidth]
      :value: []



   .. py:attribute:: min_clearance
      :type:  list[MinClearance]
      :value: []



   .. py:attribute:: min_annular_ring
      :type:  list[MinAnnularRing]
      :value: []



   .. py:attribute:: diff_pair_length_match
      :type:  list[DiffPairLengthMatch]
      :value: []



   .. py:attribute:: back_drill_stub_length
      :type:  list[BackDrillStubLength]
      :value: []



   .. py:attribute:: copper_balance
      :type:  list[CopperBalance]
      :value: []



   .. py:method:: from_dict(data: dict[str, Any]) -> Rules
      :classmethod:


      Create Rules instance from dictionary.

      Parameters
      ----------
      data : dict
          Dictionary produced by ``json.load()``, ``yaml.safe_load()``, etc.

      Returns
      -------
      Rules
          Validated instance ready for ``Drc.check()``.

      Examples
      --------
      >>> import json
      >>> with open("rules.json") as f:
      ...     data = json.load(f)
      >>> rules = Rules.from_dict(data)



   .. py:method:: to_dict() -> dict[str, Any]

      Convert Rules to dictionary.

      Returns
      -------
      dict
          JSON-serializable dictionary.

      Examples
      --------
      >>> rules = Rules().add_min_line_width("trace", "3mil")
      >>> data = rules.to_dict()
      >>> "min_line_width" in data
      True



   .. py:method:: add_min_line_width(name: str, value: str, layers: list[str] | None = None) -> Rules

      Append a minimum line width rule.

      Parameters
      ----------
      name : str
          Rule identifier for reporting.
      value : str
          Minimum width with unit (e.g., ``"3.5mil"``, ``"0.1mm"``).
      layers : list of str or None, optional
          Layer names to apply rule to. If ``None``, applies to all
          signal layers. The default is ``None``.

      Returns
      -------
      Rules
          Self for method chaining.

      Examples
      --------
      >>> rules = Rules().add_min_line_width("trace_width", "3.5mil")
      >>> len(rules.min_line_width)
      1



   .. py:method:: add_min_clearance(name: str, value: str, net1: str, net2: str) -> Rules

      Append a minimum clearance rule between nets.

      Parameters
      ----------
      name : str
          Rule identifier for reporting.
      value : str
          Minimum clearance with unit (e.g., ``"4mil"``, ``"0.15mm"``).
      net1 : str
          First net name or wildcard (``"*"`` matches all).
      net2 : str
          Second net name or wildcard (``"*"`` matches all).

      Returns
      -------
      Rules
          Self for method chaining.

      Examples
      --------
      >>> rules = Rules().add_min_clearance("clk2data", "4mil", "CLK*", "DATA*")
      >>> rules.min_clearance[0].net1
      'CLK*'



   .. py:method:: add_min_annular_ring(name: str, value: str) -> Rules

      Append a minimum annular ring rule for drilled holes.

      Parameters
      ----------
      name : str
          Rule identifier for reporting.
      value : str
          Minimum ring width with unit (e.g., ``"2mil"``, ``"0.05mm"``).

      Returns
      -------
      Rules
          Self for method chaining.

      Examples
      --------
      >>> rules = Rules().add_min_annular_ring("via_ring", "2mil")
      >>> rules.min_annular_ring[0].value
      '2mil'



   .. py:method:: add_diff_pair_length_match(name: str, tolerance: str, pairs: list[tuple[str, str]]) -> Rules

      Append a differential pair length matching rule.

      Parameters
      ----------
      name : str
          Rule identifier for reporting.
      tolerance : str
          Maximum allowed length difference with unit (e.g., ``"0.1mm"``).
      pairs : list of tuple[str, str]
          List of (positive_net, negative_net) tuples.

      Returns
      -------
      Rules
          Self for method chaining.

      Examples
      --------
      >>> rules = Rules().add_diff_pair_length_match("usb_match", tolerance="0.1mm", pairs=[("USB_DP", "USB_DN")])
      >>> rules.diff_pair_length_match[0].tolerance
      '0.1mm'



   .. py:method:: add_back_drill_stub_length(name: str, value: str) -> Rules

      Append a maximum back-drill stub length rule.

      Parameters
      ----------
      name : str
          Rule identifier for reporting.
      value : str
          Maximum allowed stub length with unit (e.g., ``"6mil"``).

      Returns
      -------
      Rules
          Self for method chaining.

      Examples
      --------
      >>> rules = Rules().add_back_drill_stub_length("max_stub", "6mil")
      >>> rules.back_drill_stub_length[0].value
      '6mil'



   .. py:method:: add_copper_balance(name: str, max_percent: int, layers: list[str]) -> Rules

      Append a copper density balance rule.

      Parameters
      ----------
      name : str
          Rule identifier for reporting.
      max_percent : int
          Maximum allowed imbalance percentage (e.g., ``15`` for 15%).
      layers : list of str
          Layer names to check for balance.

      Returns
      -------
      Rules
          Self for method chaining.

      Examples
      --------
      >>> rules = Rules().add_copper_balance("top_bal", max_percent=10, layers=["TOP"])
      >>> rules.copper_balance[0].max_percent
      10



.. py:class:: Drc(edb: pyedb.Edb)

   High-performance DRC engine for PyEDB.

   This class provides a multi-threaded design rule checker that runs inside
   an open PyEDB session. It uses R-tree spatial indexing for efficient
   geometry queries and parallelizes all rule checks using ThreadPoolExecutor.

   Parameters
   ----------
   edb : pyedb.Edb
       Active EDB session that must already be open.

   Attributes
   ----------
   edb : pyedb.Edb
       Reference to the EDB instance.
   violations : list of dict
       List of violation dictionaries populated by ``check()``.
   idx_primitives : rtree.index.Index
       R-tree spatial index for primitive geometries.
   idx_vias : rtree.index.Index
       R-tree spatial index for via locations.
   idx_components : rtree.index.Index
       R-tree spatial index for component bounding boxes.

   Examples
   --------
   Basic DRC workflow:

   >>> import pyedb
   >>> from pyedb.workflows.drc.drc import Drc, Rules
   >>> edb = pyedb.Edb("my_board.aedb")
   >>> rules = Rules.parse_file("rules.json")
   >>> drc = Drc(edb)
   >>> violations = drc.check(rules)
   >>> print(f"Found {len(violations)} violations")

   Export to IPC-356A format:

   >>> drc.to_ipc356a("review.ipc")


   .. py:attribute:: edb


   .. py:attribute:: violations
      :type:  list[dict[str, Any]]
      :value: []



   .. py:method:: check(rules: Rules) -> list[dict[str, Any]]

      Run all rules and return a list of violations.

      This method dispatches each rule to its appropriate handler and
      collects all violations. Successive calls overwrite previous results.

      Parameters
      ----------
      rules : Rules
          Validated rule container with design constraints.

      Returns
      -------
      list of dict
          Each dictionary describes a single violation with keys:

          - ``rule`` : Rule type (e.g., ``"minLineWidth"``)
          - ``limit_um`` : Limit value in micrometers
          - Additional rule-specific keys (``layer``, ``net1``, ``primitive``, etc.)

      Examples
      --------
      >>> rules = Rules().add_min_line_width("trace", "3.5mil")
      >>> drc = Drc(edb)
      >>> violations = drc.check(rules)
      >>> for v in violations:
      ...     print(f"{v['rule']}: {v}")



   .. py:method:: to_ipc356a(file_path: str) -> None

      Write a complete IPC-D-356A netlist with DRC annotations.

      This method exports the full netlist in IPC-D-356A format with all
      detected violations appended as comment lines. The file can be imported
      by CAM tools (Valor, Genesis, etc.) for fabrication review.

      Parameters
      ----------
      file_path : str
          Output file path. Overwrites existing files without warning.

      Examples
      --------
      >>> drc = Drc(edb)
      >>> violations = drc.check(rules)
      >>> drc.to_ipc356a("fab_review.ipc")

      Export with violations:

      >>> rules = Rules().add_min_line_width("trace", "3mil")
      >>> drc = Drc(edb)
      >>> drc.check(rules)
      >>> drc.to_ipc356a("review_with_violations.ipc")

      Notes
      -----
      - File format follows IPC-D-356A specification
      - Violations are appended as comment lines starting with ``C``
      - Includes netlist information (nets, primitives, padstack instances)
      - Compatible with major CAM software packages



