import os
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pandas.plotting import register_matplotlib_converters

from .formatting import dates_extractor_list
from .progress_bar import ProgressBar
from .constants import TEXT_COLOR_MAP

WARNING_COLOR = TEXT_COLOR_MAP["yellow"]
NORMAL_COLOR = TEXT_COLOR_MAP["white"]


def plot_xaxis_disperse(axis_obj, every_nth: int = 2, dynamic=True):
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
    """
    args:
        y1:         (list) y-value data to be plotted on y1-axis
        y2:         (list) y-value data to be plotted on y2-axis
        y1_label:   (str) label for y1 axis
        y2_label:   (str) label for y2 axis

    optional args:
        x_label:    (str) label for x axis; DEFAULT='Trading Days'
        x:          (list) x-value data; DEFAULT=[] (length of lists)
        title:      (str) title of plot; DEFAULT=''
        saveFig:    (bool) True will save as 'filename'; DEFAULT=False
        filename:   (str) path to save plot; DEFAULT='temp_dual_plot.png'

    returns:
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
            filename = 'output/temp/' + filename
            if not os.path.exists('output/temp/'):
                # For functions, this directory may not exist.
                plt.close(fig)
                plt.clf()
                return
            if os.path.exists(filename):
                os.remove(filename)
            plt.savefig(filename, bbox_inches="tight")
        else:
            plt.show()
    except:
        print(f"{WARNING_COLOR} Warning: plot failed to render in 'dual_plotting' of title: {title}{NORMAL_COLOR}")
    plt.close('all')
    plt.clf()


def generic_plotting(list_of_plots: list, **kwargs):
    """
    args:
        list_of_plots:  (list) list of y-value data sets to be plotted (multiple)

    optional args:
        x:              (list) x-value data; DEFAULT=[] (length of lists)
        colors:         (list) color data for each plot; DEFAULT=[]
        title:          (str) title of plot; DEFAULT=''
        legend:         (list) list of plot labels in legend; DEFAULT=[] 
        saveFig:        (bool) True will save as 'filename'; DEFAULT=False
        filename:       (str) path to save plot; DEFAULT='temp_generic_plot.png'
        ylabel:         (str) label for y axis; DEFAULT=''

    returns:
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
                f"{WARNING_COLOR}Warning: lengths of plots ({len(list_of_plots)}) and colors ({len(colors)}) do not match in generic_plotting.{NORMAL_COLOR}")
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
            filename = 'output/temp/' + filename
            if os.path.exists(filename):
                os.remove(filename)
            plt.savefig(filename)
        else:
            plt.show()
    except:
        print(f"{WARNING_COLOR}Warning: plot failed to render in 'generic_plotting' of title: {title}{NORMAL_COLOR}")
    plt.close('all')
    plt.clf()


def bar_chart(data: list, **kwargs):
    """
    Exclusively used for MACD, On Balance Volume

    args:
        data:           (list) list of y-values to be plotted 

    optional args:
        x:              (list) x-value data; DEFAULT=[] (length of lists)
        position:       (pd.DataFrame) fund data, plotted as normal plot; DEFAULT=[]
        title:          (str) title of plot; DEFAULT=''
        saveFig:        (bool) True will save as 'filename'; DEFAULT=False
        filename:       (str) path to save plot; DEFAULT='temp_bar_chart.png'
        positive:       (bool) True plots all color bars positively; DEFAULT=False

    returns:
        None
    """
    register_matplotlib_converters()

    x = kwargs.get('x', [])
    position = kwargs.get('position', [])
    title = kwargs.get('title', '')
    saveFig = kwargs.get('saveFig', False)
    filename = kwargs.get('filename', 'temp_bar_chart.png')
    all_positive = kwargs.get('all_positive', False)

    if len(x) < 1:
        x = list(range(len(data)))
    else:
        x = x

    colors = []
    positive = []
    for bar in data:
        if bar > 0.0:
            positive.append(bar)
            colors.append('green')
        elif bar < 0.0:
            positive.append(-1.0 * bar)
            colors.append('red')
        else:
            positive.append(bar)
            colors.append('black')

    if all_positive:
        data = positive

    _, ax1 = plt.subplots()
    barlist = ax1.bar(x, data, width=1, color=colors)
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
            filename = 'output/temp/' + filename
            if os.path.exists(filename):
                os.remove(filename)
            plt.savefig(filename)
        else:
            plt.show()
    except:
        print(f"{WARNING_COLOR}Warning: plot failed to render in 'bar_chart' of name: {title}{NORMAL_COLOR}")
    plt.close()
    plt.clf()


def specialty_plotting(list_of_plots: list, **kwargs):
    """
    Plot various datasets against others (different y-axes)

    args:
        list_of_plots:  (list) list of y-value datasets to be plotted (multiple)

    optional args:
        x:              (list) x-value data; DEFAULT=[] (length of lists)
        alt_ax_index:   (list) list of other y-value datasets to be plotted on other axis; DEFAULT=[]
        title:          (str) title of plot; DEFAULT=''
        legend:         (list) list of plot labels in legend; DEFAULT=[] 
        saveFig:        (bool) True will save as 'filename'; DEFAULT=False
        filename:       (str) path to save plot; DEFAULT='temp_specialty_plot.png'

    returns:
        None
    """
    register_matplotlib_converters()

    x = kwargs.get('x', [])
    alt_ax_index = kwargs.get('alt_ax_index', [])
    title = kwargs.get('title', '')
    legend = kwargs.get('legend', [])
    saveFig = kwargs.get('saveFig', False)
    filename = kwargs.get('filename', 'temp_speciality_plot.png')

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
            filename = 'output/temp/' + filename
            if os.path.exists(filename):
                os.remove(filename)
            plt.savefig(filename)
        else:
            plt.show()
    except:
        print(
            f"{WARNING_COLOR}Warning: plot failed to render in 'specialty plotting' of title: {title}{NORMAL_COLOR}")
    plt.close()
    plt.clf()


def shape_plotting(main_plot: pd.DataFrame, **kwargs):
    """
    Note, shapeXY is a list of dictionaries of coordinates and type

    args:
        main_plot:      (pd.DataFrame) list of y-value datasets to be plotted (multiple)

    optional args:
        shapeXY:        (list) list of dictionaries making up shape data; DEFAULT=[]
        feature:        (str) type of shape; DEFAULT='default' (others: 'head_and_shoulders')
        title:          (str) title of plot; DEFAULT=''
        legend:         (list) list of plot labels in legend; DEFAULT=[] 
        saveFig:        (bool) True will save as 'filename'; DEFAULT=False
        filename:       (str) path to save plot; DEFAULT='temp_shape_plot.png'

    returns:
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
    """ CONVERT SHAPEXY (DICT OF ITEMS) TO DATE """

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
            filename = 'output/temp/' + filename
            if os.path.exists(filename):
                os.remove(filename)
            plt.savefig(filename)
        else:
            plt.show()
    except:
        print(f"{WARNING_COLOR}Warning: plot failed to render in 'shape plotting' of title: {title}{NORMAL_COLOR}")
    plt.close()
    plt.clf()


def candlestick(data: pd.DataFrame, **kwargs):
    """
    Plot candlestick chart

    args:
        data:           (list) list of y-values to be plotted 

    optional args:
        title:          (str) title of plot; DEFAULT=''
        legend:         (list) list of plot labels in legend; DEFAULT=[] 
        saveFig:        (bool) True will save as 'filename'; DEFAULT=False
        filename:       (str) path to save plot; DEFAULT='temp_candlestick.png'
        progress_bar:   (ProgressBar) increments progressbar as processes data

    returns:
        None
    """
    register_matplotlib_converters()

    title = kwargs.get('title', '')
    legend = kwargs.get('legend', [])
    saveFig = kwargs.get('saveFig', False)
    filename = kwargs.get('filename', 'temp_candlestick.png')
    p_bar = kwargs.get('progress_bar', None)

    _, ax = plt.subplots()
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    x = [datetime.strptime(d, '%Y-%m-%d').date()
         for d in data.index.astype(str)]
    plt.plot(x, data['Close'], alpha=0.01)

    increment = 0.5 / float(len(data['Close']) + 1)

    for i in range(len(data['Close'])):
        op = data['Open'][i]
        close = data['Close'][i]
        high = data['High'][i]
        low = data['Low'][i]

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
                        ls='-', alpha=1, color='black')
        plt.gca().add_line(hl)

        if p_bar is not None:
            p_bar.uptick(increment=increment)

    plt.title(title)
    if len(legend) > 0:
        plt.legend(legend)

    plot_xaxis_disperse(ax)

    try:
        if saveFig:
            filename = 'output/temp/' + filename
            if os.path.exists(filename):
                os.remove(filename)
            plt.savefig(filename)
        else:
            plt.show()
    except:
        print(f"{WARNING_COLOR}Warning: plot failed to render in 'shape plotting' of title: {title}{NORMAL_COLOR}")
    plt.close()
    plt.clf()

    if p_bar is not None:
        p_bar.uptick(increment=0.5)
