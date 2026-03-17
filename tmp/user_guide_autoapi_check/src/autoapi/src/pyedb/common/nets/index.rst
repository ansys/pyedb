src.pyedb.common.nets
=====================

.. py:module:: src.pyedb.common.nets


Classes
-------

.. autoapisummary::

   src.pyedb.common.nets.CommonNets


Module Contents
---------------

.. py:class:: CommonNets(_pedb)

   .. py:method:: plot(nets: str | list[str] = None, layers: str | list[str] = None, color_by_net: bool = False, show_legend: bool = True, save_plot: str = None, outline: list[list[float]] = None, size: list | tuple = (6000, 3000), plot_components: bool = True, top_view: bool = True, show: bool = True, annotate_component_names: bool = True, plot_vias: bool = False, title: str = None, **kwargs) -> tuple[matplotlib.figure.Figure, matplotlib.axes.Axes] | None

      Plot a Net to Matplotlib 2D Chart.

      Parameters
      ----------
      nets : str, list, optional
          Name of the net or list of nets to plot. If ``None`` all nets will be plotted.
      layers : str, list, optional
          Name of the layers to include in the plot. If ``None`` all the signal layers will be considered.
      color_by_net : bool, optional
          If ``True``  the plot will be colored by net.
          If ``False`` the plot will be colored by layer. (default)
      show_legend : bool, optional
          If ``True`` the legend is shown in the plot. (default)
          If ``False`` the legend is not shown.
      save_plot : str, optional
          If a path is specified the plot will be saved in this location.
          If ``save_plot`` is provided, the ``show`` parameter is ignored.
      outline : list, optional
          List of points of the outline to plot.
      size : tuple, int, optional
          Image size in pixel (width, height). Default value is ``(6000, 3000)``
      top_view : bool, optional
          Whether if use top view or bottom view. Components will be visible only for the highest layer in the view.
      plot_components : bool, optional
          If ``True``  the components placed on top layer are plotted.
          If ``False`` the components are not plotted. (default).
          This may impact in the plot computation time.
          If nets and/or layers is specified, only the components belonging to the specified nets/layers are plotted.
      annotate_component_names: bool, optional
          Whether to add the component names to the plot or not. Default is ``True``.
      plot_vias : bool, optional
          Whether to plot vias (circular and rectangular) or not. This may impact in the plot computation time.
          Default is ``False``.
      title : str, optional
          Specify the default plot title. Is value is ``None`` the project name is assigned by default. Default value
          is ``None``.
      show : bool, optional
          Whether to show the plot or not. Default is `True`.

      Returns
      -------
      (ax, fig)
          Matplotlib ax and figures.



