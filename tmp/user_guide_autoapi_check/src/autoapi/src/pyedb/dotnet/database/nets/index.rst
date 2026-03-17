src.pyedb.dotnet.database.nets
==============================

.. py:module:: src.pyedb.dotnet.database.nets


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.nets.EdbNets


Module Contents
---------------

.. py:class:: EdbNets(p_edb)

   Bases: :py:obj:`pyedb.common.nets.CommonNets`


   Manages EDB methods for nets management accessible from `Edb.nets` property.

   Examples
   --------
   >>> from pyedb import Edb
   >>> edbapp = Edb("myaedbfolder", edbversion="2021.2")
   >>> edb_nets = edbapp.nets


   .. py:property:: db

      Db object.



   .. py:property:: nets

      Nets.

      Returns
      -------
      dict[str, :class:`pyedb.dotnet.database.edb_data.nets_data.EDBNetsData`]
          Dictionary of nets.



   .. py:property:: netlist

      Return the cell netlist.

      Returns
      -------
      list
          Net names.



   .. py:property:: signal

      Signal nets.

      Returns
      -------
      dict[str, :class:`pyedb.dotnet.database.edb_data.EDBNetsData`]
          Dictionary of signal nets.



   .. py:property:: power

      Power nets.

      Returns
      -------
      dict[str, :class:`pyedb.dotnet.database.edb_data.EDBNetsData`]
          Dictionary of power nets.



   .. py:method:: eligible_power_nets(threshold=0.3)

      Return a list of nets calculated by area to be eligible for PWR/Ground net classification.
          It uses the same algorithm implemented in SIwave.

      Parameters
      ----------
      threshold : float, optional
         Area ratio used by the ``get_power_ground_nets`` method.

      Returns
      -------
      list of  :class:`pyedb.dotnet.database.edb_data.EDBNetsData`



   .. py:property:: nets_by_components
      :type: dict


      Get all nets for each component instance.



   .. py:property:: components_by_nets
      :type: dict


      Get all component instances grouped by nets.



   .. py:method:: generate_extended_nets(resistor_below: int | float = 10, inductor_below: int | float = 1, capacitor_above: int | float = 1, exception_list: list = None, include_signal: bool = True, include_power: bool = True) -> list

      Get extended net and associated components.

      Parameters
      ----------
      resistor_below : int, float, optional
          Threshold of resistor value. Search extended net across resistors which has value lower than the threshold.
      inductor_below : int, float, optional
          Threshold of inductor value. Search extended net across inductances which has value lower than the
          threshold.
      capacitor_above : int, float, optional
          Threshold of capacitor value. Search extended net across capacitors which has value higher than the
          threshold.
      exception_list : list, optional
          List of components to bypass when performing threshold checks. Components
          in the list are considered as serial components. The default is ``None``.
      include_signal : str, optional
          Whether to generate extended signal nets. The default is ``True``.
      include_power : str, optional
          Whether to generate extended power nets. The default is ``True``.

      Returns
      -------
      list
          List of all extended nets.

      Examples
      --------
      >>> from pyedb import Edb
      >>> app = Edb()
      >>> app.nets.get_extended_nets()



   .. py:method:: classify_nets(power_nets=None, signal_nets=None)

      Reassign power/ground or signal nets based on list of nets.

      Parameters
      ----------
      power_nets : str, list, optional
          List of power nets to assign. Default is `None`.
      signal_nets : str, list, optional
          List of signal nets to assign. Default is `None`.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.



   .. py:method:: is_power_gound_net(netname_list)

      Determine if one of the  nets in a list is power or ground.

      Parameters
      ----------
      netname_list : list
          List of net names.

      Returns
      -------
      bool
          ``True`` when one of the net names is ``"power"`` or ``"ground"``, ``False`` otherwise.



   .. py:method:: get_dcconnected_net_list(ground_nets=['GND'], res_value=0.001)

      Get the nets connected to the direct current through inductors.

      .. note::
         Only inductors are considered.

      Parameters
      ----------
      ground_nets : list, optional
          List of ground nets. The default is ``["GND"]``.

      Returns
      -------
      list
          List of nets connected to DC through inductors.



   .. py:method:: get_powertree(power_net_name, ground_nets)

      Retrieve the power tree.

      Parameters
      ----------
      power_net_name : str
          Name of the power net.
      ground_nets :


      Returns
      -------




   .. py:method:: get_net_by_name(net_name)

      Find a net by name.



   .. py:method:: delete(netlist)

      Delete one or more nets from EDB.

      Parameters
      ----------
      netlist : str or list
          One or more nets to delete.

      Returns
      -------
      list
          List of nets that were deleted.

      Examples
      --------

      >>> deleted_nets = database.nets.delete(["Net1", "Net2"])



   .. py:method:: find_or_create_net(net_name='', start_with='', contain='', end_with='')

      Find or create the net with the given name in the layout.

      Parameters
      ----------
      net_name : str, optional
          Name of the net to find or create. The default is ``""``.

      start_with : str, optional
          All net name starting with the string. Not case-sensitive.

      contain : str, optional
          All net name containing the string. Not case-sensitive.

      end_with : str, optional
          All net name ending with the string. Not case-sensitive.

      Returns
      -------
      object
          Net Object.



   .. py:method:: is_net_in_component(component_name, net_name)

      Check if a net belongs to a component.

      Parameters
      ----------
      component_name : str
          Name of the component.
      net_name : str
          Name of the net.

      Returns
      -------
      bool
          ``True`` if the net is found in component pins.




   .. py:method:: find_and_fix_disjoint_nets(net_list=None, keep_only_main_net=False, clean_disjoints_less_than=0.0, order_by_area=False)

      Find and fix disjoint nets from a given netlist.

      .. deprecated::
         Use new property :func:`edb.layout_validation.disjoint_nets` instead.

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

      Returns
      -------
      List
          New nets created.

      Examples
      --------

      >>> renamed_nets = database.nets.find_and_fix_disjoint_nets(["GND", "Net2"])



   .. py:method:: merge_nets_polygons(net_names_list)

      Convert paths from net into polygons, evaluate all connected polygons and perform the merge.

      Parameters
      ----------
      net_names_list : str or list[str]
          Net name of list of net name.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.




