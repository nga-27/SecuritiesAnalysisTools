import os
import warnings
import json

import pandas as pd
import numpy as np
from scipy.stats import linregress

from libs.utils import generic_plotting, dates_convert_from_index, INDEXES, STANDARD_COLORS
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

    trends = dict()

    mins_y = []
    mins_x = []
    maxes_y = []
    maxes_x = []
    all_x = []

    vf = 0.06
    if meta is not None:
        vol = meta.get('volatility', {}).get('VF')
        if vol is not None:
            vf = vol / 100.0

    increment = 0.7 / (float(len(interval)) * 3)

    for i, period in enumerate(interval):
        ma_size = period

        # ma = windowed_ma_list(fund['Close'], interval=ma_size)
        weight_strength = 2.0 + (0.1 * float(i))
        ma = windowed_moving_avg(fund['Close'], interval=ma_size, weight_strength=weight_strength,
                                 data_type='list', filter_type='exponential')
        ex = find_filtered_local_extrema(ma)
        r = reconstruct_extrema(
            fund, extrema=ex, ma_size=ma_size, ma_type='windowed')

        # Cleanse data sample for duplicates and errors
        r = remove_duplicates(r, method='point')

        for y in r['min']:
            if y[0] not in mins_x:
                mins_x.append(y[0])
                mins_y.append(y[1])
            if y[0] not in all_x:
                all_x.append(y[0])
        for y in r['max']:
            if y[0] not in maxes_x:
                maxes_x.append(y[0])
                maxes_y.append(y[1])
            if y[0] not in all_x:
                all_x.append(y[0])

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

    X0, Y0 = get_lines_from_period(
        fund, [mins_x, mins_y, maxes_x, maxes_y, all_x], interval=long_term, vf=vf)
    X1, Y1 = get_lines_from_period(
        fund, [mins_x, mins_y, maxes_x, maxes_y, all_x], interval=intermediate_term, vf=vf)
    X2, Y2 = get_lines_from_period(
        fund, [mins_x, mins_y, maxes_x, maxes_y, all_x], interval=short_term, vf=vf)
    X3, Y3 = get_lines_from_period(
        fund, [mins_x, mins_y, maxes_x, maxes_y, all_x], interval=near_term, vf=vf)

    if progress_bar is not None:
        progress_bar.uptick(increment=increment*4.0)

    X = []
    Y = []
    C = []
    L = []

    for i, x in enumerate(X0):
        X.append(x)
        Y.append(Y0[i])
        C.append('blue')
        L.append('long')

    for i, x in enumerate(X1):
        X.append(x)
        Y.append(Y1[i])
        C.append('green')
        L.append('intermediate')

    for i, x in enumerate(X2):
        X.append(x)
        Y.append(Y2[i])
        C.append('orange')
        L.append('short')

    for i, x in enumerate(X3):
        X.append(x)
        Y.append(Y3[i])
        C.append('red')
        L.append('near')

    if progress_bar is not None:
        progress_bar.uptick(increment=increment*4.0)

    analysis_list = generate_analysis(fund, x_list=X, y_list=Y, len_list=L, color_list=C)

    if progress_bar is not None:
        progress_bar.uptick(increment=0.1)

    X = dates_convert_from_index(fund, X)

    X.append(fund.index)
    Y.append(fund['Close'])
    C.append('black')

    name2 = INDEXES.get(name, name)
    if not out_suppress:
        try:
            title = f"{name2} Trend Lines for {near_term}, {short_term}, " + \
                f"{intermediate_term}, and {long_term} Periods"
            if plot_output:
                generic_plotting(Y, x=X, colors=C,
                                 title=title)
            else:
                filename = os.path.join(name, view, f"{sub_name}.png")
                generic_plotting(Y, x=X, colors=C,
                                 title=title,
                                 save_fig=True, filename=filename)

        except:
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
                          future_periods: list = [5, 10, 20],
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
    periods = kwargs.get('periods', [])
    weights = kwargs.get('weights', [])
    return_type = kwargs.get('return_type', 'slope')
    normalize = kwargs.get('normalize', False)

    trend = [0.0] * len(data)

    try:
        periods = [int(period) for period in periods]
        for j, period in enumerate(periods):
            trends = []
            for _ in range(period):
                trends.append(0.0)

            # X range will always be the same for any given period
            x = list(range(period))
            for i in range(period, len(data)):
                y = data[i-period:i].copy()
                reg = linregress(x, y)

                if return_type == 'slope':
                    trends.append(reg[0])

            wt = 1.0
            if j < len(weights):
                wt = weights[j]
            for k, t in enumerate(trends):
                trend[k] = trend[k] + (wt * t)

        if normalize:
            max_factor = max(trend)
            min_factor = min(trend)
            for i in range(len(trend)):
                if trend[i] < 0.0:
                    trend[i] = (trend[i] / min_factor) * -0.35
                else:
                    trend[i] = (trend[i] / max_factor) * 0.35

    except:
        print(f"Trend for trends.py failed.")

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
    config_path = os.path.join("resources", "config.json")
    if os.path.exists(config_path):
        with open(config_path, 'r') as cpf:
            c_data = json.load(cpf)
            cpf.close()

        ranges = c_data.get('trendlines', {}).get(
            'divisors', {}).get('ranges', [])
        ranged = 0
        for rg in ranges:
            if len(signal) > rg:
                ranged += 1

        divs = c_data.get('trendlines', {}).get('divisors', {}).get('divisors')
        if divs is not None:
            if len(divs) > ranged:
                DIVISORS = divs[ranged]

    iterations = kwargs.get('iterations', len(DIVISORS))
    threshold = kwargs.get('threshold', 0.1)
    dates = kwargs.get('dates')
    indicator = kwargs.get('indicator', '')
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    views = kwargs.get('views', '')

    indexes = list(range(len(signal)))

    if iterations > len(DIVISORS):
        iterations = len(DIVISORS)
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

                data = dict()
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
                    # lines.append(line)
                    # x_s.append(x_line)

        for i in range(period, len(signal), 2):
            for k in range(2):

                data = dict()
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
    if plot_output:
        generic_plotting(plots, x=x_plots, title=title)
    else:
        filename = os.path.join(
            name, views, f"{indicator}_trendlines_{name}.png")
        generic_plotting(plots, x=x_plots, title=title,
                         filename=filename, save_fig=True)

    trends = dict()
    return trends
