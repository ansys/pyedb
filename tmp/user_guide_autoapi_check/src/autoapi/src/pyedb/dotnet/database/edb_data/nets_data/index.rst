src.pyedb.dotnet.database.edb_data.nets_data
============================================

.. py:module:: src.pyedb.dotnet.database.edb_data.nets_data


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.edb_data.nets_data.EDBNetsData
   src.pyedb.dotnet.database.edb_data.nets_data.EDBNetClassData
   src.pyedb.dotnet.database.edb_data.nets_data.EDBExtendedNetData
   src.pyedb.dotnet.database.edb_data.nets_data.EDBDifferentialPairData


Module Contents
---------------

.. py:class:: EDBNetsData(raw_net, core_app)

   Bases: :py:obj:`pyedb.dotnet.database.dotnet.database.NetDotNet`


   Manages EDB functionalities for a primitives.
   It Inherits EDB Object properties.

   Examples
   --------
   >>> from pyedb import Edb
   >>> edb = Edb("myedb", edbversion="2026.1")
   >>> edb_net = edb.nets.nets["GND"]
   >>> edb_net.name  # Class Property
   >>> edb_net.name  # EDB Object Property


   .. py:attribute:: net_object


   .. py:property:: primitives
      :type: list[pyedb.dotnet.database.dotnet.primitive.PrimitiveDotNet]


      Return the list of primitives that belongs to the net.

      Returns
      -------
      list of :class:`pyedb.dotnet.database.edb_data.primitives_data.EDBPrimitives`



   .. py:property:: padstack_instances
      :type: list[pyedb.dotnet.database.edb_data.padstacks_data.EDBPadstackInstance]


      Return the list of primitives that belongs to the net.

      Returns
      -------
      list of :class:`pyedb.dotnet.database.edb_data.padstacks_data.EDBPadstackInstance`



   .. py:property:: components
      :type: dict[str, pyedb.dotnet.database.cell.hierarchy.component.EDBComponent]


      Return the list of components that touch the net.

      Returns
      -------
      dict[str, :class:`pyedb.dotnet.database.cell.hierarchy.component.EDBComponent`]



   .. py:method:: find_dc_short(fix=False) -> list[list[str]]

      Find DC-shorted nets.

      Parameters
      ----------
      fix : bool, optional
          If `True`, rename all the nets. (default)
          If `False`, only report dc shorts.

      Returns
      -------
      List[List[str, str]]
          [[net name, net name]].



   .. py:method:: plot(layers=None, show_legend=True, save_plot=None, outline=None, size=(2000, 1000), show=True)

      Plot a net to Matplotlib 2D chart.

      Parameters
      ----------
      layers : str, list, optional
          Name of the layers to include in the plot. If `None` all the signal layers will be considered.
      show_legend : bool, optional
          If `True` the legend is shown in the plot. (default)
          If `False` the legend is not shown.
      save_plot : str, optional
          If a path is specified the plot will be saved in this location.
          If ``save_plot`` is provided, the ``show`` parameter is ignored.
      outline : list, optional
          List of points of the outline to plot.
      size : tuple, optional
          Image size in pixel (width, height).
      show : bool, optional
          Whether to show the plot or not. Default is `True`.



   .. py:method:: get_smallest_trace_width() -> float

      Retrieve the smallest trace width from paths.

      Returns
      -------
      float
          Trace smallest width.



   .. py:property:: extended_net
      :type: EDBExtendedNetData | None


      Get extended net and associated components.

      Returns
      -------
      :class:` :class:`pyedb.dotnet.database.edb_data.nets_data.EDBExtendedNetData`

      Examples
      --------
      >>> from pyedb import Edb
      >>> app = Edb()
      >>> app.nets["BST_V3P3_S5"].extended_net



.. py:class:: EDBNetClassData(core_app, raw_extended_net=None)

   Bases: :py:obj:`pyedb.dotnet.database.dotnet.database.NetClassDotNet`


   Manages EDB functionalities for a primitives.
   It inherits EDB Object properties.

   Examples
   --------
   >>> from pyedb import Edb
   >>> edb = Edb("myedb", edbversion="2026.1")
   >>> edb.net_classes


   .. py:property:: nets
      :type: dict[str, EDBNetsData]


      Get nets belong to this net class.



.. py:class:: EDBExtendedNetData(core_app, raw_extended_net=None)

   Bases: :py:obj:`pyedb.dotnet.database.dotnet.database.ExtendedNetDotNet`


   Manages EDB functionalities for a primitives.
   It Inherits EDB Object properties.

   Examples
   --------
   >>> from pyedb import Edb
   >>> edb = Edb("myedb", edbversion="2026.1")
   >>> edb_extended_net = edb.nets.extended_nets["GND"]
   >>> edb_extended_net.name  # Class Property


   .. py:property:: nets
      :type: dict[str, EDBNetsData]


      Nets dictionary.



   .. py:property:: components
      :type: dict[str, pyedb.dotnet.database.cell.hierarchy.component.EDBComponent]


      Dictionary of components.



   .. py:property:: rlc
      :type: dict[str, pyedb.dotnet.database.cell.hierarchy.component.EDBComponent]


      Dictionary of RLC components.



   .. py:property:: serial_rlc
      :type: dict[str, pyedb.dotnet.database.cell.hierarchy.component.EDBComponent]


      Dictionary of serial RLC components.



   .. py:property:: shunt_rlc
      :type: dict[str, pyedb.dotnet.database.cell.hierarchy.component.EDBComponent]


      Dictionary of shunt RLC components.



.. py:class:: EDBDifferentialPairData(core_app, api_object=None)

   Bases: :py:obj:`pyedb.dotnet.database.dotnet.database.DifferentialPairDotNet`


   Manages EDB functionalities for a primitive.
   It inherits EDB object properties.



   .. py:property:: positive_net
      :type: EDBNetsData


      Positive Net.



   .. py:property:: negative_net
      :type: EDBNetsData


      Negative Net.



