""" trends """
import os
import warnings
import json
from typing import Union

import pandas as pd
import numpy as np
from scipy.stats import linregress

from libs.utils import generate_plot, PlotType, dates_convert_from_index, INDEXES, STANDARD_COLORS
from libs.features import find_filtered_local_extrema, reconstruct_extrema, remove_duplicates

from .moving_average import windowed_moving_avg
from .trend_utils import (
    get_lines_from_period, generate_analysis, filter_nearest_to_signal, consolidate_lines
)

WARNING = STANDARD_COLORS["warning"]
NORMAL = STANDARD_COLORS["normal"]

TREND_PTS = [2, 3, 6]


def get_trend_lines(fund: pd.DataFrame, **kwargs) -> dict:
    """Get Trendlines

    Arguments:
        fund {pd.DataFrame} -- fund historical data

    Optional Args:
        name {str} -- name of fund, primarily for plotting (default: {''})
        plot_output {bool} -- True to render plot in realtime (default: {True})
        interval {list} -- list of windowed filter time periods (default: {[4, 8, 16, 32]})
        progress_bar {ProgressBar} -- (default: {None})
        sub_name {str} -- file extension within 'name' directory (default: {name})
        view {str} -- directory of plots (default: {''})
        meta {dict} -- 'metadata' object for fund (default: {None})
        out_suppress {bool} -- if True, skips plotting (default: {False})
        trend_window {list} -- line time windows (default: {[163, 91, 56, 27]})

    Returns:
        trends {dict} -- contains all trend lines determined by algorithm
    """
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    name = kwargs.get('name', '')
    plot_output = kwargs.get('plot_output', True)
    interval = kwargs.get('interval', [4, 8, 16, 32])
    progress_bar = kwargs.get('progress_bar', None)
    sub_name = kwargs.get('sub_name', f"trendline_{name}")
    view = kwargs.get('view', '')
    meta = kwargs.get('meta')
    out_suppress = kwargs.get('out_suppress', False)
    trend_window = kwargs.get('trend_window', [163, 91, 56, 27])

    # Not ideal to ignore warnings, but these are handled already by scipy/numpy so... eh...
    warnings.filterwarnings("ignore", category=RuntimeWarning)

    trends = {}
    mins_y = []
    mins_x = []
    maxes_y = []
    maxes_x = []
    all_x = []

    volatility = 0.06
    if meta is not None:
        vol = meta.get('volatility', {}).get('VF')
        if vol is not None:
            volatility = vol / 100.0

    increment = 0.7 / (float(len(interval)) * 3)
    for i, period in enumerate(interval):
        ma_size = period

        # ma = windowed_ma_list(fund['Close'], interval=ma_size)
        weight_strength = 2.0 + (0.1 * float(i))
        wma = windowed_moving_avg(fund['Close'], ma_size, weight_strength=weight_strength,
                                 data_type='list', filter_type='exponential')
        ex = find_filtered_local_extrema(wma)
        recon = reconstruct_extrema(
            fund, extrema=ex, ma_size=ma_size, ma_type='windowed')

        # Cleanse data sample for duplicates and errors
        recon = remove_duplicates(recon, method='point')

        for y_list in recon['min']:
            if y_list[0] not in mins_x:
                mins_x.append(y_list[0])
                mins_y.append(y_list[1])
            if y_list[0] not in all_x:
                all_x.append(y_list[0])

        for y_list in recon['max']:
            if y_list[0] not in maxes_x:
                maxes_x.append(y_list[0])
                maxes_y.append(y_list[1])
            if y_list[0] not in all_x:
                all_x.append(y_list[0])

        if progress_bar is not None:
            progress_bar.uptick(increment=increment)

    zipped_min = list(zip(mins_x, mins_y))
    zipped_min.sort(key=lambda x: x[0])
    mins_x = [x[0] for x in zipped_min]
    mins_y = [y[1] for y in zipped_min]

    zipped_max = list(zip(maxes_x, maxes_y))
    zipped_max.sort(key=lambda x: x[0])
    maxes_x = [x[0] for x in zipped_max]
    maxes_y = [y[1] for y in zipped_max]

    long_term = trend_window[0]
    intermediate_term = trend_window[1]
    short_term = trend_window[2]
    near_term = trend_window[3]

    x_list_0, y_list_0 = get_lines_from_period(
        fund, [mins_x, mins_y, maxes_x, maxes_y, all_x], interval=long_term, vf=volatility)
    x_list_1, y_list_1 = get_lines_from_period(
        fund, [mins_x, mins_y, maxes_x, maxes_y, all_x], interval=intermediate_term, vf=volatility)
    x_list_2, y_list_2 = get_lines_from_period(
        fund, [mins_x, mins_y, maxes_x, maxes_y, all_x], interval=short_term, vf=volatility)
    x_list_3, y_list_3 = get_lines_from_period(
        fund, [mins_x, mins_y, maxes_x, maxes_y, all_x], interval=near_term, vf=volatility)

    if progress_bar is not None:
        progress_bar.uptick(increment=increment*4.0)

    x_list_full = []
    y_list_full = []
    color_list = []
    term_list = []

    for i, x_val in enumerate(x_list_0):
        x_list_full.append(x_val)
        y_list_full.append(y_list_0[i])
        color_list.append('blue')
        term_list.append('long')

    for i, x_val in enumerate(x_list_1):
        x_list_full.append(x_val)
        y_list_full.append(y_list_1[i])
        color_list.append('green')
        term_list.append('intermediate')

    for i, x_val in enumerate(x_list_2):
        x_list_full.append(x_val)
        y_list_full.append(y_list_2[i])
        color_list.append('orange')
        term_list.append('short')

    for i, x_val in enumerate(x_list_3):
        x_list_full.append(x_val)
        y_list_full.append(y_list_3[i])
        color_list.append('red')
        term_list.append('near')

    if progress_bar is not None:
        progress_bar.uptick(increment=increment*4.0)

    analysis_list = generate_analysis(fund, x_list=x_list_full, y_list=y_list_full,
        len_list=term_list, color_list=color_list)

    if progress_bar is not None:
        progress_bar.uptick(increment=0.1)

    x_list_full = dates_convert_from_index(fund, x_list_full)

    x_list_full.append(fund.index)
    y_list_full.append(fund['Close'])
    color_list.append('black')

    name2 = INDEXES.get(name, name)
    if not out_suppress:
        try:
            title = f"{name2} Trend Lines for {near_term}, {short_term}, " + \
                f"{intermediate_term}, and {long_term} Periods"
            generate_plot(
                PlotType.GENERIC_PLOTTING, y_list_full, **{
                    "x": x_list_full, "colors": color_list, "plot_output": plot_output,
                    "title": title,
                    "save_fig": True, "filename": os.path.join(name, view, f"{sub_name}.png")
                }
            )

        except: # pylint: disable=bare-except
            print(
                f"{WARNING}Warning: plot failed to generate in trends.get_trend_lines.{NORMAL}")

    if progress_bar is not None:
        progress_bar.uptick(increment=0.2)

    trends['trendlines'] = analysis_list

    current = []
    metrics = []

    for trend in analysis_list:
        if trend['current']:
            current.append(trend)
            met = {f"{trend.get('term')} term": trend.get('type')}
            met['periods'] = trend.get('length')
            metrics.append(met)

    trends['current'] = current
    trends['metrics'] = metrics
    trends['type'] = 'trend'

    return trends


#############################################################
# Forecasters for trendlines - more 'future' development
#############################################################


def trend_simple_forecast(trend: dict,
                          future_periods: Union[list, None] = None,
                          return_type='price',
                          current_price: float = None) -> dict:
    """Trend Simple Forecast

    Arguments:
        trend {dict} each trend is a dict created by generate analysis / attribute analysis

    Keyword Arguments:
        future_periods {list} -- trading periods FROM last date of trend; if not a 'current' trend,
                                 ensure that each future period is far enough in the future to be
                                 relevant to the present (default: {[5, 10, 20]})
        return_type {str} -- various return types possible (default: {'price'})
        current_price {float} -- current fund price in comparison with trend (default: {None})

    Returns:
        dict -- forecast data object
    """
    if not future_periods:
        future_periods = [5, 10, 20]
    forecast = {
        'return_type': return_type,
        'periods': future_periods,
        'returns': [],
        'above_below': 'n/a',
        'slope': 'n/a'
    }

    if return_type == 'price':
        # Likely will be only return_type
        slope = trend['slope']
        intercept = trend['intercept']
        end_index = trend['end']['index']
        prices = [np.round(slope * (x + end_index) + intercept, 2)
                  for x in future_periods]

        forecast['returns'] = prices

        if current_price is not None:
            if current_price < prices[0]:
                forecast['above_below'] = 'Below'
            else:
                forecast['above_below'] = 'Above'

        if slope < 0:
            forecast['slope'] = 'DOWN'
        elif slope > 0:
            forecast['slope'] = 'UP'

    return forecast


def auto_trend(data, **kwargs) -> list:
    """Auto trend

    A more simplistic trend-determiner. Takes a dataset, finds "trend" for each listed period of
    "periods" and returns either a 'slope' or other for all points in data.

    Arguments:
        data {list, pd.DataFrame} -- data to find trends at each point

    Optional Args:
        periods {list} -- look-back periods for trend analysis (default: {[]})
        weights {list} -- weighting for look-back periods (default: {[]})
        return_type {str} -- type of item to return in list (default: {'slope'})
        normalize {bool} -- True normalizes to max/min slopes (default: {False})

    Returns:
        list -- list of items desired in 'return_type'
    """
    # pylint: disable=too-many-locals
    periods = kwargs.get('periods', [])
    weights = kwargs.get('weights', [])
    return_type = kwargs.get('return_type', 'slope')
    normalize = kwargs.get('normalize', False)

    trend = [0.0] * len(data)

    try:
        periods = [int(period) for period in periods]
        for j, period in enumerate(periods):
            trends = [0.0] * period

            # X range will always be the same for any given period
            x_period_list = list(range(period))
            for i in range(period, len(data)):
                y_list = data[i-period:i].copy()
                reg = linregress(x_period_list, y_list)

                if return_type == 'slope':
                    trends.append(reg[0])

            weight = 1.0
            if j < len(weights):
                weight = weights[j]
            for k, trend_val in enumerate(trends):
                trend[k] = trend[k] + (weight * trend_val)

        if normalize:
            max_factor = max(trend)
            min_factor = min(trend)
            for i, trend_x in enumerate(trend):
                if trend_x < 0.0:
                    trend[i] = (trend_x / min_factor) * -0.35
                else:
                    trend[i] = (trend_x / max_factor) * 0.35

    except: # pylint: disable=bare-except
        print("Trend for trends.py failed.")

    return trend


######################################################
DIVISORS = [1, 2, 4, 8]


def get_trend_lines_regression(signal: list, **kwargs) -> dict:
    """Get Trendlines Regression

    A regression-only based method of generating trendlines (w/o use of local minima and maxima).

    Arguments:
        signal {list} -- signal of which to find a trend (can be anything)

    Optional Args:
        iterations {int} -- number of types through trendline creation with "divisors"
                            (default: {15})
        threshold {float} -- acceptable ratio a trendline can be off and still counted in current
                             plot (default: {0.1})
        dates {list} -- typically DataFrame.index (default: {None})
        indicator {str} -- for plot name, indicator trend analyzed (default: {''})
        plot_output {bool} -- (default: {True})
        name {str} -- (default: {''})
        views {str} -- (default: {''})

    Returns:
        dict -- trendline content
    """
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    divisors = DIVISORS
    config_path = os.path.join("resources", "config.json")
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as cpf:
            c_data = json.load(cpf)
            cpf.close()

        ranges = c_data.get('trendlines', {}).get(
            'divisors', {}).get('ranges', [])
        ranged = 0
        for range_val in ranges:
            if len(signal) > range_val:
                ranged += 1

        divs = c_data.get('trendlines', {}).get('divisors', {}).get('divisors')
        if divs is not None:
            if len(divs) > ranged:
                divisors = divs[ranged]

    iterations = kwargs.get('iterations', len(divisors))
    threshold = kwargs.get('threshold', 0.1)
    dates = kwargs.get('dates')
    indicator = kwargs.get('indicator', '')
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    views = kwargs.get('views', '')

    indexes = list(range(len(signal)))
    iterations = min(iterations, len(DIVISORS))
    divisors = DIVISORS[0:iterations]

    lines = []
    x_s = []
    t_line_content = []
    line_id = 0

    y_max = max(signal) - min(signal)
    x_max = len(signal)
    scale_change = float(x_max) / float(y_max)

    for div in divisors:
        period = int(len(signal) / div)
        for i in range(div):
            for k in range(2):
                data = {}
                if i == div-1:
                    data['value'] = signal[period*i: len(signal)].copy()
                    data['x'] = indexes[period*i: len(signal)].copy()
                else:
                    data['value'] = signal[period*i: period*(i+1)].copy()
                    data['x'] = indexes[period*i: period*(i+1)].copy()

                data = pd.DataFrame.from_dict(data)

                while len(data['x']) > 4:
                    reg = linregress(data['x'], data['value'])
                    if k == 0:
                        data = data.loc[data['value'] >
                                        reg[0] * data['x'] + reg[1]]
                    else:
                        data = data.loc[data['value'] <
                                        reg[0] * data['x'] + reg[1]]

                reg = linregress(data['x'], data['value'])
                content = {'slope': reg[0], 'intercept': reg[1]}
                content['angle'] = np.arctan(
                    reg[0] * scale_change) / np.pi * 180.0
                if reg[0] < 0.0:
                    content['angle'] = 180.0 + \
                        (np.arctan(reg[0] * scale_change) / np.pi * 180.0)

                line = []
                for ind in indexes:
                    line.append(reg[0] * ind + reg[1])

                x_line = indexes.copy()

                line_corrected, x_corrected = filter_nearest_to_signal(
                    signal, x_line, line)

                if len(x_corrected) > 0:
                    content['length'] = len(x_corrected)
                    content['id'] = line_id
                    line_id += 1

                    lines.append(line_corrected.copy())
                    x_s.append(x_corrected.copy())
                    t_line_content.append(content)

        for i in range(period, len(signal), 2):
            for k in range(2):
                data = {}
                data['value'] = signal[i-period: i].copy()
                data['x'] = indexes[i-period: i].copy()

                data = pd.DataFrame.from_dict(data)

                while len(data['x']) > 4:
                    reg = linregress(data['x'], data['value'])
                    if k == 0:
                        data = data.loc[data['value'] >
                                        reg[0] * data['x'] + reg[1]]
                    else:
                        data = data.loc[data['value'] <
                                        reg[0] * data['x'] + reg[1]]

                reg = linregress(data['x'], data['value'])
                content = {'slope': reg[0], 'intercept': reg[1]}
                content['angle'] = np.arctan(
                    reg[0] * scale_change) / np.pi * 180.0
                if reg[0] < 0.0:
                    content['angle'] = 180.0 + \
                        (np.arctan(reg[0] * scale_change) / np.pi * 180.0)

                line = []
                for ind in indexes:
                    line.append(reg[0] * ind + reg[1])

                x_line = indexes.copy()

                line_corrected, x_corrected = filter_nearest_to_signal(
                    signal, x_line, line, threshold=threshold)

                if len(x_corrected) > 0:
                    content['length'] = len(x_corrected)
                    content['id'] = line_id
                    line_id += 1

                    lines.append(line_corrected.copy())
                    x_s.append(x_corrected.copy())
                    t_line_content.append(content)

    # handle over load of lines (consolidate)
    # Idea: bucket sort t_line_content by 'slope', within each bucket then consolidate similar
    # intercepts, both by line extension/combination and on slope averaging. Track line 'id' list
    # so that the corrections can be made for plots and x_plots
    t_line_content, lines, x_s = consolidate_lines(
        t_line_content, lines, x_s, signal)

    t_line_content, lines, x_s = consolidate_lines(
        t_line_content, lines, x_s, signal, thresh=0.2)

    t_line_content, lines, x_s = consolidate_lines(
        t_line_content, lines, x_s, signal, thresh=0.3)

    plots = []
    x_plots = []
    plots.append(signal)
    x_plots.append(list(range(len(signal))))
    plots.extend(lines)
    x_plots.extend(x_s)

    if dates is not None:
        new_xs = []
        for xps in x_plots:
            nxs = [dates[i] for i in xps]
            new_xs.append(nxs)

        x_plots = new_xs

    title = f"{indicator.capitalize()} Trendlines"
    generate_plot(
        PlotType.GENERIC_PLOTTING, plots, **{
            "x": x_plots, "title": title, "plot_output": plot_output, "save_fig": True,
            "filename": os.path.join(name, views, f"{indicator}_trendlines_{name}.png")
        }
    )

    trends = {}
    return trends
