""" shapes """
from datetime import datetime

import numpy as np
import pandas as pd
from pandas.plotting import register_matplotlib_converters

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from .utils import plot_xaxis_disperse, save_or_render_plot


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
        save_fig {bool} -- True will save as 'filename' (default: {False})
        filename {str} -- path to save plot (default: {'temp_shape_plot.png'})

    Returns:
        None
    """
    # pylint: disable=too-many-locals,too-many-statements,too-many-branches
    register_matplotlib_converters()

    shape_xy = kwargs.get('shapeXY', [])
    feature = kwargs.get('feature', 'default')
    title = kwargs.get('title', '')
    legend = kwargs.get('legend', [])
    save_fig = kwargs.get('save_fig', False)
    filename = kwargs.get('filename', 'temp_shape_plot.png')

    fig, axis = plt.subplots()
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    # As of yfinance==0.2.9, we need to split the date, because there are HMS-? in it.
    x_list = [datetime.strptime(d.split(' ')[0], '%Y-%m-%d').date()
         for d in main_plot.index.astype(str)]
    plt.plot(x_list, main_plot)

    x_pts = plt.gca().get_lines()[0].get_xdata()
    y_pts = plt.gca().get_lines()[0].get_ydata()
    #  CONVERT SHAPEXY (DICT OF ITEMS) TO DATE

    if feature == 'default':
        dotted_line = plt.Line2D((x_pts[40], x_pts[len(x_pts)-40]),
        (np.min(y_pts), np.max(y_pts)), lw=1, ls='-', alpha=0.5)
        plt.gca().add_line(dotted_line)

    elif (feature == 'head_and_shoulders') and (shape_xy != []):
        for shape in shape_xy:

            y_shp_pts = []
            x_shp_pts = []
            if shape['type'] == 'bullish':
                colors = 'green'
            else:
                colors = 'red'

            for point in shape['indexes']:
                # convert to date here
                y_shp_pts.append(point[1])
                x_shp_pts.append(x_pts[point[0]])

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

    elif (feature == 'price_gaps') and (shape_xy != []):
        for oval in shape_xy:
            x_val = x_pts[oval['x']]
            y_val = oval['y']
            radius = oval['rad']

            if oval['type'] == 'up':
                color = 'g'
            else:
                color = 'r'

            circle = plt.Circle((x_val, y_val), radius, color=color, fill=False)
            plt.gcf().gca().add_artist(circle)

    plt.title(title)
    if len(legend) > 0:
        plt.legend(legend)
    plot_xaxis_disperse(axis)

    save_or_render_plot(plt, fig, save_fig, title, filename, 'shapes')
    plt.close('all')
    plt.clf()
