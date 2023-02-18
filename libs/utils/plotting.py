""" plotting utility """
import os
from datetime import datetime
from typing import List
from enum import Enum

import numpy as np
import pandas as pd
from pandas.plotting import register_matplotlib_converters

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle

from intellistop import VFStopsResultType

from .formatting import dates_extractor_list
from .plot_utils import (
    bar_charting, candlesticks, utils, dual_plotting, generic, speciality
)


class PlotType(Enum):
    CANDLESTICKS = 'candlesticks'
    DUAL_PLOTTING = 'dual_plotting'
    GENERIC_PLOTTING = 'generic_plotting'
    BAR_CHART = 'bar_chart'
    SPECIALITY = 'speciality'


FUNCTIONS = {
    PlotType.CANDLESTICKS: candlesticks.candlestick_plot,
    PlotType.DUAL_PLOTTING: dual_plotting.dual_plotting,
    PlotType.GENERIC_PLOTTING: generic.generic_plotting,
    PlotType.BAR_CHART: bar_charting.bar_chart,
    PlotType.SPECIALITY: speciality.specialty_plotting,
}


def generate_plot(plot_type: PlotType, fund: pd.DataFrame, **kwargs):
    # plot_output = kwargs.get('plot_output', True)
    # title = kwargs.get('title', f'{plot_type.value}')
    # filename = kwargs.get('filename', '')
    # additional_plots = kwargs.get('additional_plots', [])
    # save_fig = not plot_output
    # fund_name = kwargs.get('name', '')
    # view = kwargs.get('view', '')
    kwargs['save_fig'] = not kwargs.get('plot_output', False)
    FUNCTIONS.get(plot_type, {})(fund, **kwargs)


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

    utils.plot_xaxis_disperse(axis)

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
            f"{utils.WARNING}Warning: plot failed to render in 'shape plotting' of title: " +
            f"{title}{utils.NORMAL}")

    plt.close('all')
    plt.clf()


# pylint: disable=too-many-arguments
def volatility_factor_plot(prices: list, dates: list, vf_data: VFStopsResultType,
                           green_zone_x_values: List[list], red_zone_x_values: List[list],
                           yellow_zone_x_values: List[list], y_range: float, minimum: float,
                           text_str: str = "", str_color: str = "", **kwargs):
    """plot_volatility_factor

    Primary plotting function that generates the standalone app's visual output. The default is
    that this plot is rendered live as well as stored in output/.

    Args:
        prices (list): close/adjusted close prices
        dates (list): dates of the prices
        stop_loss_objects (List[VFTimeSeriesType]): objects that contain stop losses, caution lines,
            etc.
        green_zone_x_values (List[list]): list of lists of the green / buy zone
        red_zone_x_values (List[list]): list of lists of the red / stopped-out zones
        yellow_zone_x_values (List[list]): list of lists of the yellow / caution zone
        y_range (float): range of max value and min value of data set (includes VFTimeSeriesType)
        minimum (float): minimum of the value of data set (includes VFTimeSeriesType)

        text_str (str, optional): text box for notes displayed
        str_color (str, optional): color for notes displayed

    Optional Keyword Args:

    """
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    register_matplotlib_converters()

    title = kwargs.get('title', '')
    save_fig = kwargs.get('save_fig', False)
    filename = kwargs.get('filename', 'temp_candlestick.png')

    stop_loss_objects = vf_data.data_sets

    shown_stop_loss = f"VF: {np.round(vf_data.vf.curated, 3)}\n"
    if vf_data.current_status.status.value != 'stopped_out':
        shown_stop_loss += f"Stop Loss: ${np.round(vf_data.stop_loss.curated, 2)}"
    else:
        shown_stop_loss += "Stop Loss: n/a"

    fig, ax_handle = plt.subplots()

    date_indexes = [datetime.strptime(date, '%Y-%m-%d').date() for date in dates]
    ax_handle.plot(date_indexes, prices, color='black')

    # Set the tick spacing (this is because dates crowd easily)
    mid_tick_size = int(len(date_indexes) / 4)
    ax_handle.xaxis.set_ticks([
        date_indexes[0], date_indexes[mid_tick_size], date_indexes[mid_tick_size * 2],
        date_indexes[mid_tick_size * 3], date_indexes[-1]
    ])

    y_start = minimum - (y_range * 0.05)
    height = y_range * 0.02

    for stop in stop_loss_objects:
        sub_dates = [date_indexes[index] for index in stop.time_index_list]
        ax_handle.plot(sub_dates, stop.caution_line, color='gold')
        ax_handle.plot(sub_dates, stop.stop_loss_line, color='red')

    for green_zone in green_zone_x_values:
        start = mdates.date2num(date_indexes[green_zone[0]])
        end = mdates.date2num(date_indexes[green_zone[-1]])
        width = end - start
        ax_handle.add_patch(
            Rectangle(
                (start, y_start),
                width,
                height,
                edgecolor='green',
                facecolor='green',
                fill=True
            )
        )

    for red_zone in red_zone_x_values:
        start = mdates.date2num(date_indexes[red_zone[0]])
        end = mdates.date2num(date_indexes[red_zone[-1]])
        width = end - start
        ax_handle.add_patch(
            Rectangle(
                (start, y_start),
                width,
                height,
                edgecolor='red',
                facecolor='red',
                fill=True
            )
        )

    for yellow_zone in yellow_zone_x_values:
        start = mdates.date2num(date_indexes[yellow_zone[0]])
        end = mdates.date2num(date_indexes[yellow_zone[-1]])
        width = end - start
        ax_handle.add_patch(
            Rectangle(
                (start, y_start),
                width,
                height,
                edgecolor='yellow',
                facecolor='yellow',
                fill=True
            )
        )

    ax_handle.set_title(title)

    if len(text_str) > 0 and len(str_color) > 0:
        new_start = minimum - (y_range * 0.2)
        new_end = minimum + (y_range * 1.02)
        ax_handle.set_ylim(new_start, new_end)
        props = dict(boxstyle='round', facecolor='white', alpha=0.25)
        ax_handle.text(
            0.02,
            0.02,
            text_str,
            color=str_color,
            transform=ax_handle.transAxes,
            bbox=props
        )

    if len(shown_stop_loss) > 0:
        props = dict(boxstyle='round', facecolor='white', alpha=0.25)
        ax_handle.text(
            0.02,
            0.90,
            shown_stop_loss,
            transform=ax_handle.transAxes,
            bbox=props
        )

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
            f"{utils.WARNING}Warning: plot failed to render in 'volatility factor plot' of title: " +
            f"{title}{utils.NORMAL}")

    plt.close('all')
    plt.clf()
