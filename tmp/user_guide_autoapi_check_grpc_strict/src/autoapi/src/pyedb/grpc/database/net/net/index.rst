src.pyedb.grpc.database.net.net
===============================

.. py:module:: src.pyedb.grpc.database.net.net


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.net.net.Net


Module Contents
---------------

.. py:class:: Net(pedb, core)

   Class managing :class:`Net <ansys.edb.core.net.net.Net>` objects in EDB database.

   Parameters
   ----------
   pedb : :class:`.Edb`
       Parent EDB object.
   core : :class:`ansys.edb.core.net.net.Net`
       Core EDB Net object to manage.

   Examples
   --------
   >>> from pyedb import Edb
   >>> edb = Edb("myedb", edbversion="2026.1")
   >>> edb_net = edb.nets["GND"]
   >>> edb_net.name
   'GND'


   .. py:attribute:: core


   .. py:property:: name

      Name of the net.

      Returns
      -------
      str
          Name of the net.



   .. py:property:: is_null
      :type: bool


      Check if the net is a null net.

      Returns
      -------
      bool
          ``True`` if the net is a null net, ``False`` otherwise.



   .. py:property:: is_power_ground

      Check if the net is a power or ground net.

      Returns
      -------
      bool
          ``True`` if the net is a power or ground net, ``False`` otherwise.



   .. py:property:: primitives
      :type: list[Union[pyedb.grpc.database.primitive.path.Path, pyedb.grpc.database.primitive.polygon.Polygon, pyedb.grpc.database.primitive.circle.Circle, pyedb.grpc.database.primitive.rectangle.Rectangle, pyedb.grpc.database.primitive.bondwire.Bondwire]]


      All primitives belonging to this net.

      Returns
      -------
      list
          List of primitive objects which can be one of:
          - :class:`Path <pyedb.grpc.database.primitive.path.Path>`
          - :class:`Polygon <pyedb.grpc.database.primitive.polygon.Polygon>`
          - :class:`Circle <pyedb.grpc.database.primitive.circle.Circle>`
          - :class:`Rectangle <pyedb.grpc.database.primitive.rectangle.Rectangle>`
          - :class:`Bondwire <pyedb.grpc.database.primitive.bondwire.Bondwire>`



   .. py:property:: padstack_instances
      :type: list[pyedb.grpc.database.primitive.padstack_instance.PadstackInstance]


      All padstack instances belonging to this net.

      Returns
      -------
      list of :class:`PadstackInstance <pyedb.grpc.database.primitive.padstack_instance.PadstackInstance>`
          Padstack instances associated with the net.



   .. py:property:: components
      :type: dict[str, pyedb.grpc.database.hierarchy.component.Component]


      Components connected to this net.

      Returns
      -------
      dict
          Dictionary of components keyed by component name, with values as
          :class:`Component <pyedb.grpc.database.hierarchy.component.Component>` objects.



   .. py:method:: create(layout, name: str)
      :classmethod:


      Create a new net in the EDB database.
      Parameters
      ----------
      layout : :class:`pyedb.grpc.database.layout.layout.Layout`
          Layout to create the net in.
      name : str
          Name of the new net.

      Returns
      -------
      :class:`Net <pyedb.grpc.database.net.net.Net>`
          Newly created net object.



   .. py:method:: find_dc_short(fix=False) -> list[list[str]]

      Find DC-shorted nets connected to this net.

      Parameters
      ----------
      fix : bool, optional
          Whether to automatically rename nets to resolve shorts.
          Default: ``False`` (only report shorts).

      Returns
      -------
      list[list[str]]
          List of shorted net pairs in the format [[net_name1, net_name2], ...].



   .. py:method:: plot(layers=None, show_legend=True, save_plot=None, outline=None, size=(2000, 1000), show=True, title=None)

      Plot the net using Matplotlib.

      Parameters
      ----------
      layers : str or list[str], optional
          Layer name(s) to include. If ``None``, uses all signal layers.
      show_legend : bool, optional
          Enable legend display. Default: ``True``.
      save_plot : str, optional
          Full path to save the plot image. If specified, overrides ``show``.
      outline : list, optional
          Outline points for plot boundary.
      size : tuple, optional
          Image dimensions in pixels (width, height). Default: (2000, 1000).
      show : bool, optional
          Display the plot. Default: ``True``.
      title : str, optional
          Plot title. Uses net name if ``None``. Default: ``None``.



   .. py:method:: get_smallest_trace_width() -> float

      Get the minimum trace width from path primitives in this net.

      Returns
      -------
      float
          Smallest width found in database units. Returns 1e10 if no paths exist.



   .. py:property:: extended_net

      Extended net associated with this net.

      Returns
      -------
      :class:`ExtendedNet <pyedb.grpc.database.net.extended_net.ExtendedNet>` or None
          Extended net object if exists, otherwise ``None``.

      Examples
      --------
      >>> edb.nets["BST_V3P3_S5"].extended_net



   .. py:method:: delete()

      Delete the net from the EDB database.



   .. py:method:: find_by_name(layout, name)
      :classmethod:


      Find a net by name in a given layout.

      Parameters
      ----------
      layout : :class:`.Layout`
          Layout to search for the net.
      name : str
          Name of net.

      Returns
      -------
      Net
          Net found. Check the :obj:`is_null <.Net.is_null>` property
          of the returned net to see if it exists.



