src.pyedb.dotnet.database.layout_validation
===========================================

.. py:module:: src.pyedb.dotnet.database.layout_validation


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.layout_validation.LayoutValidation


Module Contents
---------------

.. py:class:: LayoutValidation(pedb)

   Manages all layout validation capabilities


   .. py:method:: dc_shorts(net_list=None, fix=False)

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

      >>> edb = Edb("edb_file")
      >>> dc_shorts = edb.layout_validation.dc_shorts()




   .. py:method:: disjoint_nets(net_list=None, keep_only_main_net=False, clean_disjoints_less_than=0.0, order_by_area=False, keep_disjoint_pins=False)

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

      >>> renamed_nets = edb.layout_validation.disjoint_nets(["GND", "Net2"])



   .. py:method:: fix_self_intersections(net_list=None)

      Find and fix self intersections from a given netlist.

      Parameters
      ----------
      net_list : str, list, optional
          List of nets on which check disjoints. If `None` is provided then the algorithm will loop on all nets.

      Returns
      -------
      bool



   .. py:method:: illegal_net_names(fix=False)

      Find and fix illegal net names.



   .. py:method:: illegal_rlc_values(fix=False)

      Find and fix RLC illegal values.



   .. py:method:: padstacks_no_name(fix=False)

      Find and fix padstacks without aedt_name.



   .. py:method:: delete_empty_pin_groups()


