src.pyedb.generic.plot
======================

.. py:module:: src.pyedb.generic.plot


Functions
---------

.. autoapisummary::

   src.pyedb.generic.plot.plot_matplotlib


Module Contents
---------------

.. py:function:: plot_matplotlib(plot_data, size=(2000, 1000), show_legend=True, xlabel='', ylabel='', title='', save_plot=None, x_limits=None, y_limits=None, axis_equal=False, annotations=None, show=True)

   Create a matplotlib plot based on a list of data.

   Parameters
   ----------
   plot_data : list of list
       List of plot data. Every item has to be in the following format
       For type ``fill``: `[x points, y points, color, label, alpha, type=="fill"]`.
       For type ``path``: `[vertices, codes, color, label, alpha, type=="path"]`.
       For type ``contour``: `[vertices, codes, color, label, alpha, line_width, type=="contour"]`.
   size : tuple, optional
       Image size in pixel (width, height). Default is `(2000, 1000)`.
   show_legend : bool, optional
       Either to show legend or not. Default is `True`.
   xlabel : str, optional
       Plot X label. Default is `""`.
   ylabel : str, optional
       Plot Y label. Default is `""`.
   title : str, optional
       Plot Title label. Default is `""`.
   save_plot : str, optional
       If a path is specified the plot will be saved in this location.
       If ``save_plot`` is provided, the ``show`` parameter is ignored.
   x_limits : list, optional
       List of x limits (left and right). Default is `None`.
   y_limits : list, optional
       List of y limits (bottom and top). Default is `None`.
   axis_equal : bool, optional
        Whether to show the same scale on both axis or have a different scale based on plot size.
       Default is `False`.
   annotations : list, optional
       List of annotations to add to the plot. The format is [x, y, string, dictionary of font options].
       Default is `None`.
   show : bool, optional
       Whether to show the plot or return the matplotlib object. Default is `True`.


   Returns
   -------
   :class:`matplotlib.plt`
       Matplotlib fig object.


