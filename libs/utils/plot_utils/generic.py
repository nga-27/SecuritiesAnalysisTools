""" generic """

import pandas as pd
from pandas.plotting import register_matplotlib_converters
import matplotlib.pyplot as plt

from libs.utils import dates_extractor_list

from .utils import plot_xaxis_disperse, WARNING, NORMAL, save_or_render_plot


def generic_plotting(list_of_plots: list, **kwargs):
    """Generic Plotting

    Plot any number of plots together, using same Y-axis. Note, each plot in list_of_plots can be a
    different length as long as the "x" key is utilized and that the corresponding x-plot has the
    same length as the corresponding y-plot. Great use for a fund's price versus various moving
    average plots.

    Arguments:
        list_of_plots {list} -- list of y-value data sets to be plotted (multiple), a list of lists.
                                If only one used, ensure the y-list is wrapped in outer [].

    Optional Args:
        x {list} -- x-value data, can be list of lists, length(s) must match length(s) of y plot(s).
                    NOTE: for list of list of dates, ensure each list is wrapped in a list()
                    (default: {[]})
        colors {list} -- color data for each plot (default: {[]})
        title {str} -- title of plot (default: {''})
        legend {list} -- list of plot labels in legend (default: {[]})
        save_fig {bool} -- True will save as 'filename' (default: {False})
        filename {str} -- path to save plot (default: {'temp_generic_plot.png'})
        ylabel {str} -- label for y axis (default: {''})

    Returns:
        None
    """
    # pylint: disable=too-many-branches,too-many-statements
    register_matplotlib_converters()

    x_list = kwargs.get('x', [])
    colors = kwargs.get('colors', [])
    title = kwargs.get('title', '')
    legend = kwargs.get('legend', [])
    save_fig = kwargs.get('save_fig', False)
    filename = kwargs.get('filename', 'temp_generic_plot')
    y_label = kwargs.get('ylabel', '')

    if len(colors) > 0:
        if len(colors) != len(list_of_plots):
            print(
                f"{WARNING}Warning: lengths of plots ({len(list_of_plots)}) and colors " +
                f"({len(colors)}) do not match in generic_plotting.{NORMAL}")
            return None

    if len(x_list) > 0:
        if isinstance(x_list[0], (list, pd.core.indexes.datetimes.DatetimeIndex)):
            for i, plot in enumerate(list_of_plots):
                if len(plot) != len(x_list[i]):
                    print(
                        f"{WARNING}Warning: lengths of plots ({len(plot)}) and x " +
                        f"({len(x_list[i])}) " +
                        f"do not match in generic_plotting.{NORMAL}")
                    return None

    fig, axis = plt.subplots()

    if len(x_list) < 1:
        x_list = dates_extractor_list(list_of_plots[0])
        for i, fig in enumerate(list_of_plots):
            if len(colors) > 0:
                plt.plot(x_list, fig, colors[i])
            else:
                plt.plot(x_list, fig)

    else:
        if isinstance(x_list[0], (list, pd.core.indexes.datetimes.DatetimeIndex)):
            for i, fig_y in enumerate(list_of_plots):
                if len(colors) > 0:
                    plt.plot(x_list[i], fig_y, colors[i])
                else:
                    plt.plot(x_list[i], fig_y)

        else:
            for i, fig_y in enumerate(list_of_plots):
                if len(colors) > 0:
                    plt.plot(x_list, fig_y, colors[i])
                else:
                    plt.plot(x_list, fig_y)

    plt.title(title)
    if len(legend) > 0:
        plt.legend(legend)
    if y_label != '':
        plt.ylabel(y_label)

    plot_xaxis_disperse(axis)
    save_or_render_plot(plt, fig, save_fig, title, filename, 'generic plot')
    plt.close('all')
    plt.clf()
    return None
