import ast
import os
import warnings

try:
    import numpy  # noqa: F401
except ImportError:
    warnings.warn(
        "The NumPy module is required to run some functionalities of PostProcess.\n"
        "Install with \n\npip install numpy\n\nRequires CPython."
    )

try:
    from matplotlib.patches import PathPatch
    from matplotlib.path import Path

    # Use matplotlib agg backend (non-interactive) when the CI is running.
    if bool(int(os.getenv("PYEDB_CI_NO_DISPLAY", "0"))):  # pragma: no cover
        import matplotlib

        matplotlib.use("Agg")
    import matplotlib.pyplot as plt

except ImportError:
    warnings.warn(
        "The Matplotlib module is required to run some functionalities of PostProcess.\n"
        "Install with \n\npip install matplotlib\n\nRequires CPython."
    )
except:
    pass


def plot_matplotlib(
    plot_data,
    size=(2000, 1000),
    show_legend=True,
    xlabel="",
    ylabel="",
    title="",
    save_plot=None,
    x_limits=None,
    y_limits=None,
    axis_equal=False,
    annotations=None,
    show=True,
):
    """Create a matplotlib plot based on a list of data.

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
    """
    dpi = 100.0
    figsize = (size[0] / dpi, size[1] / dpi)
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(1, 1, 1)
    if isinstance(plot_data, str):
        plot_data = ast.literal_eval(plot_data)
    for points in plot_data:
        if points[-1] == "fill":
            plt.fill(points[0], points[1], c=points[2], label=points[3], alpha=points[4])
        elif points[-1] == "path":
            path = Path(points[0], points[1])
            patch = PathPatch(path, color=points[2], alpha=points[4], label=points[3])
            ax.add_patch(patch)
        elif points[-1] == "contour":
            path = Path(points[0], points[1])
            patch = PathPatch(path, color=points[2], alpha=points[4], label=points[3], fill=False, linewidth=points[5])
            ax.add_patch(patch)

    ax.set(xlabel=xlabel, ylabel=ylabel, title=title)
    if show_legend:
        ax.legend(loc="upper right")

    # evaluating the limits
    xmin = ymin = 1e30
    xmax = ymax = -1e30
    for points in plot_data:
        if points[-1] == "fill":
            xmin = min(xmin, min(points[0]))
            xmax = max(xmax, max(points[0]))
            ymin = min(ymin, min(points[1]))
            ymax = max(ymax, max(points[1]))
        else:
            for p in points[0]:
                xmin = min(xmin, p[0])
                xmax = max(xmax, p[0])
                ymin = min(ymin, p[1])
                ymax = max(ymax, p[1])
    if x_limits:
        ax.set_xlim(x_limits)
    else:
        ax.set_xlim([xmin, xmax])
    if y_limits:
        ax.set_ylim(y_limits)
    else:
        ax.set_ylim([ymin, ymax])

    if axis_equal:
        ax.axis("equal")

    if annotations:
        for annotation in annotations:
            plt.text(annotation[0], annotation[1], annotation[2], **annotation[3])

    if save_plot:
        plt.savefig(save_plot)
    elif show:
        plt.show()
    return plt
