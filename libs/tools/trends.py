import os
import warnings
import json
import pprint
import math
import pandas as pd
import numpy as np
from datetime import datetime
from scipy.stats import linregress

from .moving_average import simple_moving_avg, windowed_moving_avg
from libs.utils import generic_plotting, dates_convert_from_index, ProgressBar
from libs.utils import INDEXES
from libs.utils import STANDARD_COLORS

from libs.features import find_filtered_local_extrema, reconstruct_extrema, remove_duplicates

WARNING = STANDARD_COLORS["warning"]
NORMAL = STANDARD_COLORS["normal"]

TREND_PTS = [2, 3, 6]


def get_trendlines(fund: pd.DataFrame, **kwargs) -> dict:
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

    vq = 0.06
    if meta is not None:
        vol = meta.get('volatility', {}).get('VQ')
        if vol is not None:
            vq = vol / 100.0

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

    # mins_xd = [fund.index[x] for x in mins_x]
    # maxes_xd = [fund.index[x] for x in maxes_x]

    long_term = trend_window[0]
    intermediate_term = trend_window[1]
    short_term = trend_window[2]
    near_term = trend_window[3]

    X0, Y0 = get_lines_from_period(
        fund, [mins_x, mins_y, maxes_x, maxes_y, all_x], interval=long_term, vq=vq)
    X1, Y1 = get_lines_from_period(
        fund, [mins_x, mins_y, maxes_x, maxes_y, all_x], interval=intermediate_term, vq=vq)
    X2, Y2 = get_lines_from_period(
        fund, [mins_x, mins_y, maxes_x, maxes_y, all_x], interval=short_term, vq=vq)
    X3, Y3 = get_lines_from_period(
        fund, [mins_x, mins_y, maxes_x, maxes_y, all_x], interval=near_term, vq=vq)

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

    analysis_list = generate_analysis(
        fund, x_list=X, y_list=Y, len_list=L, color_list=C)

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
                                 saveFig=True, filename=filename)

        except:
            print(
                f"{WARNING}Warning: plot failed to generate in trends.get_trendlines.{NORMAL}")

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


def get_trend(position: pd.DataFrame, **kwargs) -> dict:
    """Get Trend

    Generates a trend of a given position and features of trend

    Styles:
        'sma' - small moving average (uses 'ma_size')
        'ema' - exponential moving average (uses 'ma_size')
    Date_range:
        list -> [start_date, end_date] -> ['2018-04-18', '2019-01-20']

    Arguments:
        position {pd.DataFrame}

    Optional Arg:
        style {str} -- (default: {'sma'})
        ma_size {int} -- (default: {50})
        date_range {list} -- (default: {[]})

    Returns:
        dict -- trends
    """
    style = kwargs.get('style', 'sma')
    ma_size = kwargs.get('ma_size', 50)
    date_range = kwargs.get('date_range', [])

    trend = {}

    if style == 'sma':
        trend['tabular'] = simple_moving_avg(
            position, ma_size, data_type='list')

        trend['difference'] = difference_from_trend(position, trend['tabular'])

        trend['magnitude'] = trend_of_dates(
            position, trend_difference=trend['difference'], dates=date_range)

        trend['method'] = f'SMA-{ma_size}'

    return trend


def difference_from_trend(position: pd.DataFrame, trend: list) -> list:
    """Difference from Trend

    Simple difference of close from trend values 

    Arguments:
        position {pd.DataFrame} -- fund dataset
        trend {list} -- given trend

    Returns:
        list -- difference, point by point
    """
    diff_from_trend = []
    for i in range(len(trend)):
        diff_from_trend.append(np.round(position['Close'][i] - trend[i], 3))

    return diff_from_trend


def trend_of_dates(position: pd.DataFrame, trend_difference: list, dates: list) -> float:
    """Trend of Dates

    Find the average of a fund over or under an existing trend for a period of dates.

    Arguments:
        position {pd.DataFrame} -- fund dataset
        trend_difference {list} -- trend difference list (close[i] - trend[i])
        dates {list} -- list of dates to examine for overall trend

    Returns:
        float -- mean (close-trend) value over period of time
    """
    overall_trend = 0.0

    if len(dates) == 0:
        # Trend of entire period provided
        trend = np.round(np.average(trend_difference), 6)
        overall_trend = trend

    else:
        i = 0
        d_start = datetime.strptime(dates[0], '%Y-%m-%d')
        d_match = datetime.strptime(position['Date'][0], '%Y-%m-%d')

        while ((i < len(position['Date'])) and (d_start > d_match)):
            i += 1
            d_match = datetime.strptime(position['Date'][i], '%Y-%m-%d')

        start = i
        d_end = datetime.strptime(dates[1], '%Y-%m-%d')
        d_match = datetime.strptime(position['Date'][i], '%Y-%m-%d')

        while ((i < len(position['Date'])) and (d_end > d_match)):
            i += 1
            if i < len(position['Date']):
                d_match = datetime.strptime(position['Date'][i], '%Y-%m-%d')

        end = i

        trend = np.round(np.average(trend_difference[start:end+1]), 6)
        overall_trend = trend

    return overall_trend


def get_trend_analysis(position: pd.DataFrame,
                       config: list = [50, 25, 12]) -> dict:
    """Get Trend Analysis

    Determines long, med, and short trend of a position

    Arguments:
        position {pd.DataFrame} -- fund dataset

    Keyword Arguments:
        config {list} -- list of moving average lookbacks, longest to shortest
                         (default: {[50, 25, 12]})

    Returns:
        dict -- trend notes
    """
    tlong = get_trend(position, style='sma', ma_size=config[0])
    tmed = get_trend(position, style='sma', ma_size=config[1])
    tshort = get_trend(position, style='sma', ma_size=config[2])

    trend_analysis = {}
    trend_analysis['long'] = tlong['magnitude']
    trend_analysis['medium'] = tmed['magnitude']
    trend_analysis['short'] = tshort['magnitude']

    if trend_analysis['long'] > 0.0:
        trend_analysis['report'] = 'Overall UPWARD, '
    else:
        trend_analysis['report'] = 'Overall DOWNWARD, '

    if np.abs(trend_analysis['short']) > np.abs(trend_analysis['medium']):
        trend_analysis['report'] += 'accelerating '
    else:
        trend_analysis['report'] += 'slowing '
    if trend_analysis['short'] > trend_analysis['medium']:
        trend_analysis['report'] += 'UPWARD'
    else:
        trend_analysis['report'] += 'DOWNWARD'

    if ((trend_analysis['short'] > 0.0) and (trend_analysis['medium'] > 0.0) and
            (trend_analysis['long'] < 0.0)):
        trend_analysis['report'] += ', rebounding from BOTTOM'

    if ((trend_analysis['short'] < 0.0) and (trend_analysis['medium'] < 0.0) and
            (trend_analysis['long'] > 0.0)):
        trend_analysis['report'] += ', falling from TOP'

    return trend_analysis


def get_lines_from_period(fund: pd.DataFrame, kargs: list, interval: int, **kwargs) -> list:
    """Get Lines from Period

    Arguments:
        fund {pd.DataFrame} -- fund dataset
        kargs {list} -- mins and maxes of x and y lists
        interval {int} -- period of time for a lookback of a trend

    Optional Args:
        vq {dict} -- volatility quotient, used to determine if a trendline is still valid at the
                     end of the period by providing a volatility threshold (default: {0.06})

    Returns:
        list -- list of trendlines given the period
    """
    vq = kwargs.get('vq', 0.06)

    EXTENSION = interval
    BREAK_LOOP = 50
    cycles = int(np.floor(len(fund['Close'])/interval))
    mins_y = kargs[1]
    mins_x = kargs[0]
    maxes_y = kargs[3]
    maxes_x = kargs[2]
    X = []
    Y = []

    for cycle in range(cycles):
        start = cycle * interval
        end = start + interval
        data = fund['Close'][start:end].copy()

        x = list(range(start, end))
        reg = linregress(x=x, y=data)
        if reg[0] >= 0:
            use_min = True
        else:
            use_min = False

        count = 0
        st_count = count
        if use_min:
            while (count < len(mins_x)) and (mins_x[count] < start):
                count += 1
                st_count = count

            end_count = st_count
            while (count < len(mins_x)) and (mins_x[count] < end):
                count += 1
                end_count = count

            datay = mins_y[st_count:end_count].copy()
            datax = mins_x[st_count:end_count].copy()
            dataz = {}
            dataz['x'] = datax
            dataz['y'] = datay
            dataw = pd.DataFrame.from_dict(dataz)
            dataw.set_index('x')
            datav = dataw.copy()

            stop_loop = 0
            while ((len(dataw['x']) > 0) and (reg[0] > 0.0)) and (stop_loop < BREAK_LOOP):
                reg = linregress(x=dataw['x'], y=dataw['y'])
                datav = dataw.copy()
                dataw = dataw.loc[dataw['y'] < reg[0] * dataw['x'] + reg[1]]
                stop_loop += 1

            if reg[0] < 0.0:
                dataw = datav.copy()
                if len(dataw) >= 2:
                    reg = linregress(x=dataw['x'], y=dataw['y'])

        else:
            while (count < len(maxes_x)) and (maxes_x[count] < start):
                count += 1
                st_count = count

            end_count = st_count
            while (count < len(maxes_x)) and (maxes_x[count] < end):
                count += 1
                end_count = count

            datay = maxes_y[st_count:end_count].copy()
            datax = maxes_x[st_count:end_count].copy()
            dataz = {}
            dataz['x'] = datax
            dataz['y'] = datay
            dataw = pd.DataFrame.from_dict(dataz)
            dataw.set_index('x')
            datav = dataw.copy()

            stop_loop = 0
            while ((len(dataw['x']) > 0) and (reg[0] < 0.0)) and (stop_loop < BREAK_LOOP):
                reg = linregress(x=dataw['x'], y=dataw['y'])
                datav = dataw.copy()
                dataw = dataw.loc[dataw['y'] > reg[0] * dataw['x'] + reg[1]]
                stop_loop += 1

            if reg[0] > 0.0:
                dataw = datav.copy()
                if len(dataw) >= 2:
                    reg = linregress(x=dataw['x'], y=dataw['y'])

        end = line_extender(fund, list(range(start, end)), reg)
        if end != 0:
            max_range = [start, end]

            if max_range[1] > len(fund['Close']):
                max_range[1] = len(fund['Close'])
            if interval > 100:
                max_range[1] = len(fund['Close'])
            if end + EXTENSION > int(0.9 * float(len(fund['Close']))):
                max_range[1] = len(fund['Close'])

            max_range[1] = line_reducer(
                fund, max_range[1], reg, threshold=vq)

            datax = list(range(max_range[0], max_range[1]))
            datay = [reg[0] * float(x) + reg[1] for x in datax]

            if (len(datay) > 0) and (not math.isnan(datay[0])):
                X.append(datax)
                Y.append(datay)

    return X, Y


def line_extender(fund: pd.DataFrame, x_range: list, reg_vals: list) -> int:
    """Line Extender

    returns the end of a particular trend line. returns 0 if segment should be omitted

    Arguments:
        fund {pd.DataFrame} -- fund dataset
        x_range {list} -- applicable x data points
        reg_vals {list} -- linear regression values

    Returns:
        int -- new endpoint to end the inspected trendline
    """
    slope = reg_vals[0]
    intercept = reg_vals[1]
    max_len = len(fund['Close'])

    if slope > 0.0:
        end_pt = x_range[len(x_range)-1]
        start_pt = x_range[0]
        for i in range(start_pt, end_pt):
            y_val = intercept + slope * i
            if fund['Close'][i] < (y_val * 0.99):
                    # Original trendline was not good enough - omit
                return 0
        # Now that original trendline is good, find ending
        # Since we have 'line_reducer', send the maximum and let reducer fix it
        return max_len

    else:
        end_pt = x_range[len(x_range)-1]
        start_pt = x_range[0]
        for i in range(start_pt, end_pt):
            y_val = intercept + slope * i
            if fund['Close'][i] > (y_val * 1.01):
                # Original trendline was not good enough - omit
                return 0
        # Now that original trendline is good, find ending
        # since we have 'line_reducer', send the maximum and let reducer fix it
        return max_len

    return end_pt


def line_reducer(fund: pd.DataFrame, last_x_pt: int, reg_vals: list, threshold=0.05) -> int:
    """Line Extender

    returns shortened lines that protrude far away from overall fund price (to not distort plots)

    Arguments:
        fund {pd.DataFrame} -- fund dataset
        last_x_pt {int} -- calculated last x point (from line_extender)
        reg_vals {list} -- linear regression values

    Keyword Arguments:
        threshold {float} -- +/- threshold to see if trend is still valid at last point
                             (default: {0.05})

    Returns:
        int -- new endpoint to end the inspected trendline
    """
    slope = reg_vals[0]
    intercept = reg_vals[1]
    top_thresh = 1.0 + threshold
    bot_thresh = 1.0 - threshold

    x_pt = last_x_pt
    if x_pt > len(fund['Close']):
        x_pt = len(fund['Close'])

    last_pt = intercept + slope * x_pt
    if (last_pt <= (top_thresh * fund['Close'][x_pt-1])) and \
            (last_pt >= (bot_thresh * fund['Close'][x_pt-1])):
        return x_pt

    else:
        while (x_pt-1 > 0) and (((last_pt > (top_thresh * fund['Close'][x_pt-1]))) or
                                (last_pt < (bot_thresh * fund['Close'][x_pt-1]))):
            x_pt -= 1
            last_pt = intercept + slope * x_pt

    return x_pt


def generate_analysis(fund: pd.DataFrame,
                      x_list: list,
                      y_list: list,
                      len_list: list,
                      color_list: list) -> list:
    """Generate Analysis

    Arguments:
        fund {pd.DataFrame} -- fund dataset
        x_list {list} -- list of x-value lists
        y_list {list} -- list of y-value lists
        len_list {list} -- list of trendline lengths
        color_list {list} -- list of colors, associated with each trendline

    Returns:
        list -- list of analysis data objects
    """
    analysis = []

    for i, x in enumerate(x_list):
        sub = {}
        sub['length'] = len(x)
        sub['color'] = color_list[i]

        reg = linregress(x[0:3], y=y_list[i][0:3])
        sub['slope'] = reg[0]
        sub['intercept'] = reg[1]

        sub['start'] = {}
        sub['start']['index'] = x[0]
        sub['start']['date'] = fund.index[x[0]].strftime("%Y-%m-%d")

        sub['end'] = {}
        sub['end']['index'] = x[len(x)-1]
        sub['end']['date'] = fund.index[x[len(x)-1]].strftime("%Y-%m-%d")

        sub['term'] = len_list[i]
        if sub['slope'] < 0:
            sub['type'] = 'bear'
        else:
            sub['type'] = 'bull'

        sub['x'] = {}
        sub['x']['by_date'] = dates_convert_from_index(fund, [x], to_str=True)
        sub['x']['by_index'] = x

        if sub['end']['index'] == len(fund['Close'])-1:
            sub['current'] = True
        else:
            sub['current'] = False

        sub = attribute_analysis(fund, x, y_list[i], sub)

        analysis.append(sub)

    return analysis


def attribute_analysis(fund: pd.DataFrame, x_list: list, y_list: list, content: dict) -> dict:
    """Attribute Analysis

    Arguments:
        fund {pd.DataFrame} -- fund dataset
        x_list {list} -- list of trendline x values
        y_list {list} -- list of trendline y values
        content {dict} -- trendline content data object

    Returns:
        dict -- trendline content data object
    """
    touches = []
    if fund['Close'][x_list[0]] >= y_list[0]:
        state = 'above'
    else:
        state = 'below'

    for i, x in enumerate(x_list):
        if state == 'above':
            if fund['Close'][x] < y_list[i]:
                state = 'below'
                touches.append(
                    {'index': x, 'price': fund['Close'][x], 'type': 'cross', 'state': 'below'})
            if fund['Close'][x] == y_list[i]:
                touches.append(
                    {'index': x, 'price': fund['Close'][x], 'type': 'touch', 'state': 'above'})

        else:
            if fund['Close'][x] >= y_list[i]:
                state = 'above'
                touches.append(
                    {'index': x, 'price': fund['Close'][x], 'type': 'cross', 'state': 'above'})
            if fund['Close'][x] == y_list[i]:
                touches.append(
                    {'index': x, 'price': fund['Close'][x], 'type': 'touch', 'state': 'below'})

    content['test_line'] = touches

    valid = []
    broken = []
    if content['type'] == 'bull':
        # trendline will have positive slope. 'above' is valid, 'below' is broken.
        v_start_index = x_list[0]
        v_stop_index = x_list[0]
        b_start_index = x_list[0]
        b_stop_index = x_list[0]
        state = 'above'

        for touch in touches:
            if touch['type'] == 'cross' and touch['state'] == 'below':
                # End of a valid period
                v_stop_index = touch['index'] - \
                    1 if touch['index'] != 0 else x_list[0]
                v = {'start': {}, 'end': {}}
                v['start']['index'] = v_start_index
                v['start']['date'] = fund.index[v_start_index].strftime(
                    "%Y-%m-%d")
                v['end']['index'] = v_stop_index
                v['end']['date'] = fund.index[v_stop_index].strftime(
                    "%Y-%m-%d")
                valid.append(v)
                b_start_index = touch['index']
                state = 'below'

            if touch['type'] == 'cross' and touch['state'] == 'above':
                # End of a broken period
                b_stop_index = touch['index'] - \
                    1 if touch['index'] != 0 else x_list[0]
                b = {'start': {}, 'end': {}}
                b['start']['index'] = b_start_index
                b['start']['date'] = fund.index[b_start_index].strftime(
                    "%Y-%m-%d")
                b['end']['index'] = b_stop_index
                b['end']['date'] = fund.index[b_stop_index].strftime(
                    "%Y-%m-%d")
                broken.append(b)
                v_start_index = touch['index']
                state = 'above'

        # End state of trend line
        if state == 'above':
            v_stop_index = x_list[len(x_list)-1]
            v = {'start': {}, 'end': {}}
            v['start']['index'] = v_start_index
            v['start']['date'] = fund.index[v_start_index].strftime("%Y-%m-%d")
            v['end']['index'] = v_stop_index
            v['end']['date'] = fund.index[v_stop_index].strftime("%Y-%m-%d")
            valid.append(v)

        else:
            b_stop_index = x_list[len(x_list)-1]
            b = {'start': {}, 'end': {}}
            b['start']['index'] = b_start_index
            b['start']['date'] = fund.index[b_start_index].strftime("%Y-%m-%d")
            b['end']['index'] = b_stop_index
            b['end']['date'] = fund.index[b_stop_index].strftime("%Y-%m-%d")
            broken.append(b)

    else:
        # trendline will have negative slope. 'below' is valid, 'above' is broken.
        v_start_index = x_list[0]
        v_stop_index = x_list[0]
        b_start_index = x_list[0]
        b_stop_index = x_list[0]
        state = 'below'

        for touch in touches:
            if touch['type'] == 'cross' and touch['state'] == 'above':
                # End of a valid period
                v_stop_index = touch['index'] - \
                    1 if touch['index'] != 0 else x_list[0]
                v = {'start': {}, 'end': {}}
                v['start']['index'] = v_start_index
                v['start']['date'] = fund.index[v_start_index].strftime(
                    "%Y-%m-%d")
                v['end']['index'] = v_stop_index
                v['end']['date'] = fund.index[v_stop_index].strftime(
                    "%Y-%m-%d")
                valid.append(v)
                b_start_index = touch['index']
                state = 'above'

            if touch['type'] == 'cross' and touch['state'] == 'below':
                # End of a broken period
                b_stop_index = touch['index'] - \
                    1 if touch['index'] != 0 else x_list[0]
                b = {'start': {}, 'end': {}}
                b['start']['index'] = b_start_index
                b['start']['date'] = fund.index[b_start_index].strftime(
                    "%Y-%m-%d")
                b['end']['index'] = b_stop_index
                b['end']['date'] = fund.index[b_stop_index].strftime(
                    "%Y-%m-%d")
                broken.append(b)
                v_start_index = touch['index']
                state = 'below'

        # End state of trend line
        if state == 'below':
            v_stop_index = x_list[len(x_list)-1]
            v = {'start': {}, 'end': {}}
            v['start']['index'] = v_start_index
            v['start']['date'] = fund.index[v_start_index].strftime("%Y-%m-%d")
            v['end']['index'] = v_stop_index
            v['end']['date'] = fund.index[v_stop_index].strftime("%Y-%m-%d")
            valid.append(v)

        else:
            b_stop_index = x_list[len(x_list)-1]
            b = {'start': {}, 'end': {}}
            b['start']['index'] = b_start_index
            b['start']['date'] = fund.index[b_start_index].strftime("%Y-%m-%d")
            b['end']['index'] = b_stop_index
            b['end']['date'] = fund.index[b_stop_index].strftime("%Y-%m-%d")
            broken.append(b)

    content['valid_period'] = valid
    content['broken_period'] = broken

    return content


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


def autotrend(data, **kwargs) -> list:
    """Autotrend

    A more simplistic trend-determiner. Takes a dataset, finds "trend" for each listed period of
    "periods" and returns either a 'slope' or other for all points in data.

    Arguments:
        data {list, pd.DataFrame} -- data to find trends at each point

    Optional Args:
        periods {list} -- look-back periods for trend analysis (default: {[]})
        weights {list -- weighting for look-back periods (default: {[]})
        return_type {str} -- type of item to return in list (default: {'slope'})
        normalize {bool} -- True normalizes to max/min slopes (default: {False})

    Returns:
        list -- list of items desired in 'return_type'
    """
    periods = kwargs.get('periods', [])
    weights = kwargs.get('weights', [])
    return_type = kwargs.get('return_type', 'slope')
    normalize = kwargs.get('normalize', False)

    trend = []
    for _ in range(len(data)):
        trend.append(0.0)

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

    return trend


######################################################
# [1, 2, 3, 4, 5, 7, 9, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
DIVISORS = [1, 2, 4, 8]


def get_trendlines_regression(signal: list, **kwargs) -> dict:
    """Get Trendlines Regression

    A regression-only based method of generating trendlines (w/o use of local minima and maxima).

    Arguments:
        signal {list} -- signal of which to find a trend (can be anything)

    Optional Args:
        iterations {int} -- number of types through trendline creation with "divisors"
                            (default: {15})
        threshold {float} -- acceptable ratio a trendline can be off and still counted in current
                             plot (default: {0.1})

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

    # t_line_content, lines, x_s = consolidate_lines(
    #     t_line_content, lines, x_s, signal, thresh=0.2)

    # t_line_content, lines, x_s = consolidate_lines(
    #     t_line_content, lines, x_s, signal, thresh=0.3)

    plots = []
    x_plots = []
    plots.append(signal)
    x_plots.append(list(range(len(signal))))
    plots.extend(lines)
    x_plots.extend(x_s)

    generic_plotting(plots, x=x_plots)

    trends = dict()
    return trends


def consolidate_lines(line_content: list, lines: list, x_lines: list, signal: list, **kwargs) -> list:

    thresh = kwargs.get('thresh', 2.5)
    thresh2 = thresh / 20.0

    nan_free = []
    for sortie in line_content:
        if str(sortie['slope']) != 'nan':
            nan_free.append(sortie)

    print(f"number of lines: {len(nan_free)}\r\n")
    sort_by_slope = sorted(nan_free, key=lambda x: x['angle'])

    kept_grouped = []
    count_base = 0
    count_comp = 1
    kept_local = [sort_by_slope[count_base]['id']]

    angles = [sbs['angle'] for sbs in sort_by_slope]

    while count_base < len(sort_by_slope) and count_comp < len(sort_by_slope):

        # if sort_by_slope[count_base]['slope'] < 0.0:
        #     # base_lower = (1.0 - thresh) * sort_by_slope[count_base]['angle']
        #     # comp_upper = (1.0 + thresh) * sort_by_slope[count_comp]['angle']
        #     base_lower = 180.0 - \
        #         (sort_by_slope[count_base]['angle'] * 180 / np.pi)

        #     if base_lower > comp_upper:
        #         base_lower = (1.0 - thresh) * \
        #             sort_by_slope[count_base]['intercept']
        #         comp_upper = (1.0 + thresh) * \
        #             sort_by_slope[count_comp]['intercept']

        #         if base_lower > comp_upper:
        #             kept_local.append(sort_by_slope[count_comp]['id'])
        #             count_comp += 1
        #             continue

        # else:
            # base_upper = (1.0 + thresh) * sort_by_slope[count_base]['angle']
            # comp_lower = (1.0 - thresh) * sort_by_slope[count_comp]['angle']
        base_upper = thresh + sort_by_slope[count_base]['angle']
        comp_lower = sort_by_slope[count_comp]['angle']

        if base_upper > comp_lower:
            base_upper = (1.0 + thresh2) * \
                sort_by_slope[count_base]['intercept']
            comp_lower = (1.0 - thresh2) * \
                sort_by_slope[count_comp]['intercept']
            # base_lower = (1.0 - thresh2) * \
            #     sort_by_slope[count_base]['intercept']
            # comp_upper = (1.0 + thresh2) * \
            #     sort_by_slope[count_comp]['intercept']

            if base_upper > comp_lower:  # or base_lower < comp_upper:
                kept_local.append(sort_by_slope[count_comp]['id'])
                count_comp += 1
                continue

        count_base = count_comp
        count_comp += 1
        kept_grouped.append(kept_local.copy())
        kept_local = [sort_by_slope[count_base]['id']]

    print(f"kept_grouped: {len(kept_grouped)}")
    new_content, lines, x_lines = reconstruct_lines(
        kept_grouped, line_content, lines, x_lines, signal)

    print(f"reconstructed: {len(lines)}")

    return new_content, lines, x_lines


def reconstruct_lines(groups: list, content: list, lines: list, x_s: list, signal: list) -> list:

    new_lines = []
    new_xs = []
    new_content = []
    new_id = 0

    y_max = max(signal) - min(signal)
    x_max = len(signal)
    scale_change = x_max / y_max

    for id_list in groups:
        slope = []
        intercept = []
        start = []
        end = []

        for id_ in id_list:
            slope.append(content[id_]['slope'])
            intercept.append(content[id_]['intercept'])
            start.append(x_s[id_][0])
            end.append(x_s[id_][-1])

        slope = np.mean(slope)
        intercept = np.mean(intercept)
        item = {'slope': slope, 'intercept': intercept}
        item['angle'] = np.arctan(slope * scale_change) / np.pi * 180.0
        if slope < 0.0:
            item['angle'] = 180.0 + \
                (np.arctan(slope * scale_change) / np.pi * 180.0)

        start = np.min(start)
        end = np.max(end)

        xs = list(range(start, end+1))
        line = [slope * x + intercept for x in xs]

        line, xs = filter_nearest_to_signal(
            signal, xs, line, threshold=0.03, ratio=True)

        if len(xs) > 4:
            item['length'] = len(line)
            item['id'] = new_id
            new_content.append(item)
            new_id += 1

            new_lines.append(line)
            new_xs.append(xs)

    return new_content, new_lines, new_xs


def filter_nearest_to_signal(signal: list,
                             x_line: list,
                             line: list,
                             threshold=0.05,
                             ratio=False) -> list:

    removals = []
    for j, lin in enumerate(line):
        if lin < 0.0:
            if lin < ((1.0 + threshold) * signal[x_line[j]]) or \
                    lin > ((1.0 - threshold) * signal[x_line[j]]):
                removals.append(j)
        else:
            if lin > ((1.0 + threshold) * signal[x_line[j]]) or \
                    lin < ((1.0 - threshold) * signal[x_line[j]]):
                removals.append(j)

    line_corrected = []
    x_corrected = []
    indexes = []
    for j, x in enumerate(x_line):
        if j not in removals:
            x_corrected.append(x)
            indexes.append(j)

    if len(x_corrected) > 0:
        start = min(x_corrected)
        end = max(x_corrected)
        x_corrected = list(range(start, end+1))

        if ratio:
            start = min(indexes)
            end = max(indexes)

        line_corrected = line[start:end+1].copy()

    return line_corrected, x_corrected
