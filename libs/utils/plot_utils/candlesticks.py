import os
from datetime import datetime

import pandas as pd
import numpy as np

from pandas.plotting import register_matplotlib_converters
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from .utils import plot_xaxis_disperse, WARNING, NORMAL


def candlestick_plot(data: pd.DataFrame, **kwargs):
    """Candlestick Plot

    Plot candlestick chart

    Arguments:
        data {pd.DataFrame} -- list of y-values to be plotted

    Optional Args:
        title {str} -- title of plot (default: {''})
        legend {list} -- list of plot labels in legend (default: {[]})
        save_fig {bool} -- True will save as 'filename' (default: {False})
        filename {str} -- path to save plot (default: {'temp_candlestick.png'})
        progress_bar {ProgressBar} -- (default: {None})
        threshold_candles {dict} -- candlestick thresholds for days (default: {None})
        additional_plots {list} -- plot_objects "plot", "color", "legend", "style" (default: {[]})

    additional_plots:
        plot {list} - "y" vector
        x {list} (optional) - "x" vector (default: {None})
        color {str} (optional) - color of line or scatter mark (default: {None})
        legend {str} (optional) - label for the plot (default: {''})
        style {str} (optional) - 'line' plotted or a 'scatter' (default: {'line'})

    Returns:
        None
    """
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    register_matplotlib_converters()

    title = kwargs.get('title', '')
    save_fig = kwargs.get('save_fig', False)
    filename = kwargs.get('filename', 'temp_candlestick.png')
    p_bar = kwargs.get('progress_bar', None)
    additional_plots = kwargs.get('additional_plots', [])
    threshold_candles = kwargs.get('threshold_candles', None)

    fig, axis = plt.subplots()
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    # As of yfinance==0.2.9, we need to split the date, because there are HMS-? in it.
    x_list = [datetime.strptime(d.split(' ')[0], '%Y-%m-%d').date()
         for d in data.index.astype(str)]
    plt.plot(x_list, data['Close'], alpha=0.01)

    increment = 0.5 / float(len(data['Close']) + 1)

    th_candles = False
    if threshold_candles is not None:
        _doji = threshold_candles.get('doji', 0.0)
        _short = threshold_candles.get('short', 0.0)
        _long = threshold_candles.get('long', 0.0)
        _ratio = threshold_candles.get('doji_ratio', 5.0)
        th_candles = True

    for i in range(len(data['Close'])):
        open_ = data['Open'][i]
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
                open_ = data['Open'][i-1]
            shadow_color = colors

        else:
            if data['Close'][i] > data['Open'][i]:
                colors = 'green'
            elif data['Close'][i] == data['Open'][i]:
                colors = 'black'
                if i > 0:
                    open_ = data['Open'][i-1]
                    if open_ > close:
                        colors = 'red'
                    else:
                        colors = 'green'
            else:
                colors = 'red'

        open_close = plt.Line2D((x_list[i], x_list[i]), (open_, close), lw=1.25,
                        ls='-', alpha=1, color=colors)
        plt.gca().add_line(open_close)
        high_low = plt.Line2D((x_list[i], x_list[i]), (high, low), lw=0.375,
                        ls='-', alpha=1, color=shadow_color)
        plt.gca().add_line(high_low)

        if p_bar is not None:
            p_bar.uptick(increment=increment)

    handles = []
    has_legend = False
    if len(additional_plots) > 0:
        for add_plt in additional_plots:
            color = add_plt.get('color')
            label = add_plt.get('legend', '')
            x_lines = add_plt.get('x', x_list)
            style = add_plt.get('style', 'line')

            if style == 'line':
                if color is not None:
                    line, = plt.plot(x_lines, add_plt["plot"],
                                     color, label=label,
                                     linewidth=0.5)
                else:
                    line, = plt.plot(x_lines, add_plt["plot"],
                                     label=label, linewidth=0.5)

                handles.append(line)

            if style == 'scatter':
                has_legend = True
                if color is not None:
                    plt.scatter(
                        x_lines, add_plt["plot"], c=color, s=3, label=label)
                else:
                    plt.scatter(x_lines, add_plt["plot"],
                                label=label, s=3)

    plt.title(title)
    if len(handles) > 0:
        plt.legend(handles=handles)
    elif has_legend:
        plt.legend()

    plot_xaxis_disperse(axis)

    try:
        if save_fig:
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

    except: # pylint: disable=bare-except
        print(
            f"{WARNING}Warning: plot failed to render in 'shape plotting' of title: " +
            f"{title}{NORMAL}")

    plt.close('all')
    plt.clf()

    if p_bar is not None:
        p_bar.uptick(increment=0.5)