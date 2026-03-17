src.pyedb.grpc.database.layout_validation
=========================================

.. py:module:: src.pyedb.grpc.database.layout_validation


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.layout_validation.LayoutValidation


Module Contents
---------------

.. py:class:: LayoutValidation(pedb: Any)

   Manages all layout validation capabilities


   .. py:method:: dc_shorts(net_list: Optional[Union[str, List[str]]] = None, fix: bool = False) -> List[List[str]]

      Find DC shorts on layout.

      Parameters
      ----------
      net_list : str or list[str], optional
          List of nets.
      fix : bool, optional
          If `True`, rename all the nets. (default)
          If `False`, only report dc shorts.

      Returns
      -------
      List[List[str, str]]
          [[net name, net name]].

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb("edb_file")
      >>> # Find shorts without fixing
      >>> shorts = edb.layout_validation.dc_shorts()
      >>>
      >>> # Find and fix shorts on specific nets
      >>> fixed_shorts = edb.layout_validation.dc_shorts(net_list=["GND", "VCC"], fix=True)



   .. py:method:: disjoint_nets(net_list: Optional[Union[str, List[str]]] = None, keep_only_main_net: bool = False, clean_disjoints_less_than: float = 0.0, order_by_area: bool = False, keep_disjoint_pins: bool = False) -> List[str]

      Find and fix disjoint nets from a given netlist.

      Parameters
      ----------
      net_list : str, list, optional
          List of nets on which check disjoints. If `None` is provided then the algorithm will loop on all nets.
      keep_only_main_net : bool, optional
          Remove all secondary nets other than principal one (the one with more objects in it). Default is `False`.
      clean_disjoints_less_than : bool, optional
        Clean all disjoint nets with area less than specified area in square meters. Default is `0.0` to disable it.
      order_by_area : bool, optional
          Whether if the naming order has to be by number of objects (fastest) or area (slowest but more accurate).
          Default is ``False``.
      keep_disjoint_pins : bool, optional
          Whether if delete disjoints pins not connected to any other primitive or not. Default is ``False``.

      Returns
      -------
      List
          New nets created.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb("edb_file")
      >>> new_nets = edb.layout_validation.disjoint_nets()
      >>> # Clean disjoints on specific nets with advanced options
      >>> cleaned = edb.layout_validation.disjoint_nets(
      ...     net_list=["GND"],
      ...     keep_only_main_net=True,
      ...     clean_disjoints_less_than=1e-6,
      ...     order_by_area=True
      ... ))



   .. py:method:: fix_self_intersections(net_list: Optional[Union[str, List[str]]] = None) -> bool

      Find and fix self intersections from a given netlist.

      Parameters
      ----------
      net_list : str, list, optional
          List of nets on which check disjoints. If `None` is provided then the algorithm will loop on all nets.

      Returns
      -------
      bool

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb("edb_file")
      >>> # Fix self-intersections on all nets
      >>> edb.layout_validation.fix_self_intersections()
      >>>
      >>> # Fix self-intersections on specific nets
      >>> edb.layout_validation.fix_self_intersections(net_list=["RF_line"])



   .. py:method:: illegal_net_names(fix: bool = False) -> None

      Find and fix illegal net names.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb("edb_file")
      >>> # Identify illegal net names
      >>> edb.layout_validation.illegal_net_names()
      >>>
      >>> # Find and automatically fix illegal names
      >>> edb.layout_validation.illegal_net_names(fix=True)



   .. py:method:: illegal_rlc_values(fix: bool = False) -> List[str]

      Find and fix RLC illegal values.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb("edb_file")
      >>> # Identify components with illegal RLC values
      >>> bad_components = edb.layout_validation.illegal_rlc_values()
      >>>
      # Automatically fix invalid inductor values
      #     edb.layout_validation.illegal_rlc_values(fix=True)



   .. py:method:: padstacks_no_name(fix: bool = False) -> None

      Identify and fix padstacks without names.

      Examples
      --------
      # Use an Edb instance (see `dc_shorts` example above) and call:
      #     edb.layout_validation.padstacks_no_name()
      >>>
      # Automatically assign names to unnamed padstacks
      #     edb.layout_validation.padstacks_no_name(fix=True)



