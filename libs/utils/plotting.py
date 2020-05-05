import os
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from pandas.plotting import register_matplotlib_converters

from .formatting import dates_extractor_list
from .progress_bar import ProgressBar
from .constants import STANDARD_COLORS

WARNING = STANDARD_COLORS["warning"]
NORMAL = STANDARD_COLORS["normal"]


def plot_xaxis_disperse(axis_obj, every_nth: int = 2, dynamic=True):
    """Plot Xaxis Disperse

    Arguments:
        axis_obj {} -- Matplotlib axis object, likely a dictionary

    Keyword Arguments:
        every_nth {int} -- tick mark interval (default: {2})
        dynamic {bool} -- determines if ticks should end on even or odd (default: {True})
    """
    num_ticks = len(axis_obj.xaxis.get_ticklabels())
    tick_even = True
    if dynamic:
        if num_ticks % 2 == 0:
            # length is even, end with tick mark
            tick_even = True
        else:
            tick_even = False

    for n, label in enumerate(axis_obj.xaxis.get_ticklabels()):
        if tick_even:
            if n % every_nth == 0:
                label.set_visible(False)
        else:
            if n % every_nth != 0:
                label.set_visible(False)
    return


def is_data_list(data) -> bool:
    """ Determines if data provided is a list [of lists] or simply a vector of data """
    for dat in data:
        if type(dat) == list:
            return True
    return False


def dual_plotting(y1: list, y2: list, y1_label: str, y2_label: str, **kwargs):
    """Dual Plotting

    Plot two different scales of y-values against same x-axis. Both y scales can be sets
    of values, so y1 and y2 can be list of lists. Great use for a fund's price versus various
    oscillators and metrics with y-values far different than the prices.

    Arguments:
        y1 {list} -- y-value data to be plotted on y1-axis, can be list of lists
        y2 {list} -- y-value data to be plotted on y2-axis, can be list of lists
        y1_label {str} -- label for y1 axis
        y2_label {str} -- label for y2 axis

    Optional Args:
        x_label {str} -- label for x axis (default: {'Trading Days'})
        x {list} -- x-value data (default: {[]}) (length of lists)
        title {str} -- title of plot (default: {''})
        saveFig {bool} -- True will save as 'filename' (default: {False})
        filename {str} path to save plot (default: {'temp_dual_plot.png'})

    Returns:
        None
    """
    register_matplotlib_converters()

    x_label = kwargs.get('x_label', 'Trading Days')
    x = kwargs.get('x', [])
    title = kwargs.get('title', '')
    saveFig = kwargs.get('saveFig', False)
    filename = kwargs.get('filename', 'temp_dual_plot.png')

    if len(x) < 1:
        if is_data_list(y1):
            x = dates_extractor_list(y1[0])
        else:
            x = dates_extractor_list(y1)

    fig, ax1 = plt.subplots()

    if is_data_list(y2):
        color = 'k'
    else:
        color = 'tab:orange'
    ax1.set_xlabel(x_label)

    list_setting = False
    if is_data_list(y1):
        list_setting = True
        ax1.set_ylabel(y1_label[0])

        for y in y1:
            ax1.plot(x, y)
            ax1.tick_params(axis='y')
            ax1.grid(linestyle=':')

        plt.legend(y1_label)

    else:
        ax1.set_ylabel(y1_label, color=color)
        ax1.plot(x, y1, color=color)
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.grid(linestyle=':')
        plt.legend([y1_label])

    ax2 = ax1.twinx()

    if list_setting:
        color = 'k'
    else:
        color = 'tab:blue'

    if is_data_list(y2):
        ax2.set_ylabel(y2_label)

        for y in y2:
            ax2.plot(x, y)
            ax2.tick_params(axis='y')
            ax2.grid()

        if type(y2_label) == list:
            plt.legend(y2_label)
        else:
            plt.legend([y2_label])

    else:
        ax2.set_ylabel(y2_label, color=color)
        ax2.plot(x, y2, color=color)
        ax2.tick_params(axis='y', labelcolor=color)
        ax2.grid()
        plt.legend([y2_label])

    plt.tight_layout()
    plot_xaxis_disperse(ax1)

    if len(title) > 0:
        plt.title(title)

    try:
        if saveFig:
            temp_path = os.path.join("output", "temp")
            filename = os.path.join(temp_path, filename)

            if not os.path.exists(temp_path):
                # For functions, this directory may not exist.
                plt.close(fig)
                plt.clf()
                return

            if os.path.exists(filename):
                os.remove(filename)
            plt.savefig(filename, bbox_inches="tight")

        else:
            # Case of functions, show the plot and not save it.
            plt.show()

    except:
        print(
            f"{WARNING} Warning: plot failed to render in 'dual_plotting' of title: " +
            f"{title}{NORMAL}")

    plt.close('all')
    plt.clf()


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
                    (default: {[]})
        colors {list} -- color data for each plot (default: {[]})
        title {str} -- title of plot (default: {''})
        legend {list} -- list of plot labels in legend (default: {[]})
        saveFig {bool} -- True will save as 'filename' (default: {False})
        filename {str} -- path to save plot (default: {'temp_generic_plot.png'})
        ylabel {str} -- label for y axis (default: {''})

    Returns:
        None
    """
    register_matplotlib_converters()

    x = kwargs.get('x', [])
    colors = kwargs.get('colors', [])
    title = kwargs.get('title', '')
    legend = kwargs.get('legend', [])
    saveFig = kwargs.get('saveFig', False)
    filename = kwargs.get('filename', 'temp_generic_plot')
    ylabel = kwargs.get('ylabel', '')

    if len(colors) > 0:
        if len(colors) != len(list_of_plots):
            print(
                f"{WARNING}Warning: lengths of plots ({len(list_of_plots)}) and colors " +
                f"({len(colors)}) do not match in generic_plotting.{NORMAL}")
            return None

    if len(x) > 0:
        if type(x[0]) == list:
            for i, plot in enumerate(list_of_plots):
                if len(plot) != len(x[i]):
                    print(
                        f"{WARNING}Warning: lengths of plots ({len(plot)}) and x ({len(x[i])}) " +
                        f"do not match in generic_plotting.{NORMAL}")
                    return None

    fig, ax = plt.subplots()

    if len(x) < 1:
        x = dates_extractor_list(list_of_plots[0])
        for i, fig in enumerate(list_of_plots):
            if len(colors) > 0:
                plt.plot(x, fig, colors[i])
            else:
                plt.plot(x, fig)

    else:
        if type(x[0]) == list:
            x = x
            for i in range(len(list_of_plots)):
                if len(colors) > 0:
                    plt.plot(x[i], list_of_plots[i], colors[i])
                else:
                    plt.plot(x[i], list_of_plots[i])

        else:
            x = x
            for i, figy in enumerate(list_of_plots):
                if len(colors) > 0:
                    plt.plot(x, figy, colors[i])
                else:
                    plt.plot(x, figy)

    plt.title(title)
    if len(legend) > 0:
        plt.legend(legend)
    if ylabel != '':
        plt.ylabel(ylabel)

    plot_xaxis_disperse(ax)

    try:
        if saveFig:
            temp_path = os.path.join("output", "temp")
            if not os.path.exists(temp_path):
                # For functions, this directory may not exist.
                plt.close(fig)
                plt.clf()
                return

            filename = os.path.join(temp_path, filename)
            if os.path.exists(filename):
                os.remove(filename)

            plt.savefig(filename)

        else:
            plt.show()

    except:
        print(
            f"{WARNING}Warning: plot failed to render in 'generic_plotting' of title: " +
            f"{title}{NORMAL}")

    plt.close('all')
    plt.clf()


def bar_chart(data: list, **kwargs):
    """Bar Chart

    Exclusively used for MACD, On Balance Volume, Awesome Oscillator

    Arguments:
        data {list} -- list of y-values to be plotted 

    Optional Args:
        x {list} -- x-value data (default: {[]}) (length of lists)
        position {pd.DataFrame} -- fund data, plotted as normal plot (default: {[]})
        title {str} -- title of plot (default: {''})
        saveFig {bool} -- True will save as 'filename' (default: {False})
        filename {str} -- path to save plot (default: {'temp_bar_chart.png'})
        positive {bool} -- True plots all color bars positively (default: {False})
        bar_delta {bool} -- True: y[i] > y[i-1] -> green, else red (default: {False})

    Returns:
        None
    """
    register_matplotlib_converters()

    x = kwargs.get('x', [])
    position = kwargs.get('position', [])
    title = kwargs.get('title', '')
    saveFig = kwargs.get('saveFig', False)
    filename = kwargs.get('filename', 'temp_bar_chart.png')
    all_positive = kwargs.get('all_positive', False)
    bar_delta = kwargs.get('bar_delta', False)

    if len(x) < 1:
        x = list(range(len(data)))
    else:
        x = x

    colors = []
    positive = []
    bar_awesome = []

    for i, bar in enumerate(data):
        if bar > 0.0:
            positive.append(bar)
            colors.append('green')
        elif bar < 0.0:
            positive.append(-1.0 * bar)
            colors.append('red')
        else:
            positive.append(bar)
            colors.append('black')

        if i == 0:
            bar_awesome.append(colors[-1])
        else:
            if bar < data[i-1]:
                bar_awesome.append('red')
            elif bar > data[i-1]:
                bar_awesome.append('green')
            else:
                bar_awesome.append(bar_awesome[-1])

    if all_positive:
        data = positive

    _, ax1 = plt.subplots()
    if bar_delta:
        barlist = ax1.bar(x, data, width=1, color=bar_awesome)
    else:
        barlist = ax1.bar(x, data, width=1, color=colors)

    if not bar_delta:
        for i in range(1, len(data)):
            if data[i] > 0.0:
                if data[i] < data[i-1]:
                    barlist[i].set_alpha(0.3)
            else:
                if data[i] > data[i-1]:
                    barlist[i].set_alpha(0.3)

    plt.title(title)

    if len(position) > 0:
        ax2 = ax1.twinx()
        ax2.plot(position['Close'])

    plot_xaxis_disperse(ax1)

    try:
        if saveFig:
            temp_path = os.path.join("output", "temp")
            if not os.path.exists(temp_path):
                # For functions, this directory may not exist.
                plt.close(fig)
                plt.clf()
                return

            filename = os.path.join(temp_path, filename)
            if os.path.exists(filename):
                os.remove(filename)
            plt.savefig(filename)

        else:
            plt.show()

    except:
        print(
            f"{WARNING}Warning: plot failed to render in 'bar_chart' of name: {title}{NORMAL}")

    plt.close('all')
    plt.clf()


def specialty_plotting(list_of_plots: list, **kwargs):
    """Specialty Plotting

    Plot various datasets against others (different y-axes). Similar to dual plotting, in a sense.

    Arguments:
        list_of_plots {list} -- list of y-value datasets to be plotted (multiple)

    Optional Args:
        x {list} -- x-value data (default: {[]}) (length of lists)
        alt_ax_index {list} -- list of other y-value datasets to be plotted on other axis
                                (default: {[]})
        title {str} -- title of plot (default: {''})
        legend {list} -- list of plot labels in legend (default: {[]})
        saveFig {bool} -- True will save as 'filename' (default: {False})
        filename {str} -- path to save plot (default: {'temp_specialty_plot.png'})

    Returns:
        None
    """
    register_matplotlib_converters()

    x = kwargs.get('x', [])
    alt_ax_index = kwargs.get('alt_ax_index', [])
    title = kwargs.get('title', '')
    legend = kwargs.get('legend', [])
    saveFig = kwargs.get('saveFig', False)
    filename = kwargs.get('filename', 'temp_specialty_plot.png')

    x = x
    if len(x) < 1:
        x = dates_extractor_list(list_of_plots[0])
    _, ax = plt.subplots()

    for i in range(len(list_of_plots)):
        if i not in alt_ax_index:
            ax.plot(x, list_of_plots[i])

    ax2 = ax.twinx()
    for i in range(len(list_of_plots)):
        if i in alt_ax_index:
            ax2.plot(x, list_of_plots[i], color='tab:purple')

    plt.title(title)
    ax2.set_ylabel(legend[0])
    if len(legend) > 0:
        plt.legend(legend)

    plot_xaxis_disperse(ax)

    try:
        if saveFig:
            temp_path = os.path.join("output", "temp")
            if not os.path.exists(temp_path):
                # For functions, this directory may not exist.
                plt.close(fig)
                plt.clf()
                return

            filename = os.path.join(temp_path, filename)
            if os.path.exists(filename):
                os.remove(filename)

            plt.savefig(filename)

        else:
            plt.show()

    except:
        print(
            f"{WARNING}Warning: plot failed to render in 'specialty plotting' " +
            f"of title: {title}{NORMAL}")

    plt.close('all')
    plt.clf()


def shape_plotting(main_plot: pd.DataFrame, **kwargs):
    """Shape Plotting

    Plot shapes on top of a "main_plot" signal, such as feature detection or price gap shapes.
    Note, shapeXY is a list of dictionaries of coordinates and type.

    Arguments:
        main_plot {pd.DataFrame} -- list of y-value datasets to be plotted (multiple)

    Optional Args:
        shapeXY {list} -- list of dictionaries making up shape data (default: {[]})
        feature {str} -- type of shape (default: {'default'}) (others: 'head_and_shoulders')
        title {str} -- title of plot (default: {''})
        legend {list} -- list of plot labels in legend (default: {[]})
        saveFig {bool} -- True will save as 'filename' (default: {False})
        filename {str} -- path to save plot (default: {'temp_shape_plot.png'})

    Returns:
        None
    """
    register_matplotlib_converters()

    shapeXY = kwargs.get('shapeXY', [])
    feature = kwargs.get('feature', 'default')
    title = kwargs.get('title', '')
    legend = kwargs.get('legend', [])
    saveFig = kwargs.get('saveFig', False)
    filename = kwargs.get('filename', 'temp_shape_plot.png')

    _, ax = plt.subplots()
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    x = [datetime.strptime(d, '%Y-%m-%d').date()
         for d in main_plot.index.astype(str)]
    plt.plot(x, main_plot)

    xpts = plt.gca().get_lines()[0].get_xdata()
    ypts = plt.gca().get_lines()[0].get_ydata()
    #  CONVERT SHAPEXY (DICT OF ITEMS) TO DATE

    if feature == 'default':
        dotted_line = plt.Line2D((xpts[40], xpts[len(
            xpts)-40]), (np.min(ypts), np.max(ypts)), lw=1, ls='-', alpha=0.5)
        plt.gca().add_line(dotted_line)

    elif (feature == 'head_and_shoulders') and (shapeXY != []):
        for shape in shapeXY:

            y_shp_pts = []
            x_shp_pts = []
            if shape['type'] == 'bullish':
                colors = 'green'
            else:
                colors = 'red'

            for pt in shape['indexes']:
                # convert to date here
                y_shp_pts.append(pt[1])
                x_shp_pts.append(xpts[pt[0]])

            box = plt.Line2D((x_shp_pts[0], x_shp_pts[4]), (np.min(y_shp_pts), np.min(
                y_shp_pts)), lw=2, ls='-.', alpha=0.75, color=colors)
            plt.gca().add_line(box)

            box = plt.Line2D((x_shp_pts[0], x_shp_pts[0]), (np.min(y_shp_pts), np.max(
                y_shp_pts)), lw=2, ls='-.', alpha=0.75, color=colors)
            plt.gca().add_line(box)

            box = plt.Line2D((x_shp_pts[0], x_shp_pts[4]), (np.max(y_shp_pts), np.max(
                y_shp_pts)), lw=2, ls='-.', alpha=0.75, color=colors)
            plt.gca().add_line(box)

            box = plt.Line2D((x_shp_pts[4], x_shp_pts[4]), (np.min(y_shp_pts), np.max(
                y_shp_pts)), lw=2, ls='-.', alpha=0.75, color=colors)
            plt.gca().add_line(box)

    elif (feature == 'price_gaps') and (shapeXY != []):
        for oval in shapeXY:
            x = xpts[oval['x']]
            y = oval['y']
            radius = oval['rad']

            if oval['type'] == 'up':
                color = 'g'
            else:
                color = 'r'

            circle = plt.Circle((x, y), radius, color=color, fill=False)
            plt.gcf().gca().add_artist(circle)

    plt.title(title)
    if len(legend) > 0:
        plt.legend(legend)

    plot_xaxis_disperse(ax)

    try:
        if saveFig:
            temp_path = os.path.join("output", "temp")
            if not os.path.exists(temp_path):
                # For functions, this directory may not exist.
                plt.close(fig)
                plt.clf()
                return

            filename = os.path.join(temp_path, filename)
            if os.path.exists(filename):
                os.remove(filename)

            plt.savefig(filename)

        else:
            plt.show()

    except:
        print(
            f"{WARNING}Warning: plot failed to render in 'shape plotting' of title: " +
            f"{title}{NORMAL}")

    plt.close('all')
    plt.clf()


def candlestick_plot(data: pd.DataFrame, **kwargs):
    """Candlestick Plot

    Plot candlestick chart

    Arguments:
        data {list} -- list of y-values to be plotted 

    Optional Args:
        title {str} -- title of plot (default: {''})
        legend {list} -- list of plot labels in legend (default: {[]})
        saveFig {bool} -- True will save as 'filename' (default: {False})
        filename {str} -- path to save plot (default: {'temp_candlestick.png'})
        progress_bar {ProgressBar} -- (default: {None})
        threshold_candles {dict} -- candlestick thresholds for days (default: {None})
        additional_plts {list} -- plot_objects "plot", "color", "legend" (default: {[]})

    Returns:
        None
    """
    register_matplotlib_converters()

    title = kwargs.get('title', '')
    saveFig = kwargs.get('saveFig', False)
    filename = kwargs.get('filename', 'temp_candlestick.png')
    p_bar = kwargs.get('progress_bar', None)
    additional_plts = kwargs.get('additional_plts', [])
    threshold_candles = kwargs.get('threshold_candles', None)

    _, ax = plt.subplots()
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    x = [datetime.strptime(d, '%Y-%m-%d').date()
         for d in data.index.astype(str)]
    plt.plot(x, data['Close'], alpha=0.01)

    increment = 0.5 / float(len(data['Close']) + 1)

    th_candles = False
    if threshold_candles is not None:
        _doji = threshold_candles.get('doji', 0.0)
        _short = threshold_candles.get('short', 0.0)
        _long = threshold_candles.get('long', 0.0)
        _ratio = threshold_candles.get('doji_ratio', 5.0)
        th_candles = True

    for i in range(len(data['Close'])):
        op = data['Open'][i]
        close = data['Close'][i]
        high = data['High'][i]
        low = data['Low'][i]

        shadow_color = 'black'
        if th_candles:
            diff = np.abs(data['Close'][i] - data['Open'][i])
            colors = 'black'
            if diff >= _long:
                colors = 'blue'
            if diff <= _short:
                colors = 'orange'
            if diff <= _doji:
                shadow = data['High'][i] - data['Low'][i]
                if shadow >= (diff * _ratio):
                    colors = 'red'

            # Handle mutual fund case here:
            if (diff == 0) and (data['High'][i] == data['Low'][i]) and (i > 0):
                colors = 'black'
                op = data['Open'][i-1]
            shadow_color = colors

        else:
            if data['Close'][i] > data['Open'][i]:
                colors = 'green'
            elif data['Close'][i] == data['Open'][i]:
                colors = 'black'
                if i > 0:
                    op = data['Open'][i-1]
                    if op > close:
                        colors = 'red'
                    else:
                        colors = 'green'
            else:
                colors = 'red'

        oc = plt.Line2D((x[i], x[i]), (op, close), lw=3,
                        ls='-', alpha=1, color=colors)
        plt.gca().add_line(oc)
        hl = plt.Line2D((x[i], x[i]), (high, low), lw=0.75,
                        ls='-', alpha=1, color=shadow_color)
        plt.gca().add_line(hl)

        if p_bar is not None:
            p_bar.uptick(increment=increment)

    handles = []
    if len(additional_plts) > 0:
        for add_plt in additional_plts:
            color = add_plt.get('color')
            label = add_plt.get('legend')
            if color is not None:
                line, = plt.plot(x, add_plt["plot"],
                                 add_plt["color"], label=label,
                                 linewidth=0.5)
            else:
                line, = plt.plot(x, add_plt["plot"],
                                 label=label, linewidth=0.5)
            handles.append(line)

    plt.title(title)
    if len(handles) > 0:
        plt.legend(handles=handles)

    plot_xaxis_disperse(ax)

    try:
        if saveFig:
            temp_path = os.path.join("output", "temp")
            if not os.path.exists(temp_path):
                # For functions, this directory may not exist.
                plt.close(fig)
                plt.clf()
                return

            filename = os.path.join(temp_path, filename)
            if os.path.exists(filename):
                os.remove(filename)
            plt.savefig(filename)

        else:
            plt.show()

    except:
        print(
            f"{WARNING}Warning: plot failed to render in 'shape plotting' of title: " +
            f"{title}{NORMAL}")

    plt.close('all')
    plt.clf()

    if p_bar is not None:
        p_bar.uptick(increment=0.5)
