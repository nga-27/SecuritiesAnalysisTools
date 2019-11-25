import pandas as pd 
import numpy as np 
from datetime import datetime
from scipy.stats import linregress
import warnings, pprint, math

from .math_functions import linear_regression
from .moving_average import simple_ma_list, windowed_ma_list, windowed_ema_list
from libs.utils import generic_plotting, dates_convert_from_index, ProgressBar

from libs.features import local_extrema, reconstruct_extrema, remove_duplicates

TREND_PTS = [2, 3, 6]

def get_trend(position: pd.DataFrame, style: str='sma', ma_size: int=50, date_range: list=[]) -> dict:
    """ generates a trend of a given position and features of trend

    Styles:
        'sma' - small moving average (uses 'ma_size')
        'ema' - exponential moving average (uses 'ma_size')
    Date_range:
        list -> [start_date, end_date] -> ['2018-04-18', '2019-01-20']

    """
    trend = {}

    if style == 'sma':
        trend['tabular'] = simple_ma_list(position, ma_size)
        trend['difference'] = difference_from_trend(position, trend['tabular'])
        trend['magnitude'] = trend_of_dates(position, trend_difference=trend['difference'], dates=date_range)
        trend['method'] = f'SMA-{ma_size}'

    return trend


def difference_from_trend(position: pd.DataFrame, trend: list) -> list:
    diff_from_trend = []
    for i in range(len(trend)):
        diff_from_trend.append(np.round(position['Close'][i] - trend[i], 3))

    return diff_from_trend



def trend_of_dates(position: pd.DataFrame, trend_difference: list, dates: list) -> float:
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


def get_trend_analysis(position: pd.DataFrame, date_range: list=[], config=[50, 25, 12]) -> dict:
    """ Determines long, med, and short trend of a position """
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

    if ((trend_analysis['short'] > 0.0) and (trend_analysis['medium'] > 0.0) and (trend_analysis['long'] < 0.0)):
        trend_analysis['report'] += ', rebounding from BOTTOM'

    if ((trend_analysis['short'] < 0.0) and (trend_analysis['medium'] < 0.0) and (trend_analysis['long'] > 0.0)):
        trend_analysis['report'] += ', falling from TOP'

    return trend_analysis


def get_trendlines( fund: pd.DataFrame, plot_output: bool=True,
                    name: str='', interval: list=[4, 8, 16, 32], progress_bar: ProgressBar=None ):

    # Not ideal to ignore warnings, but these are handled already by scipy/numpy so... eh...
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    
    mins_y = []
    mins_x = []
    maxes_y = []
    maxes_x = []
    all_x = []

    increment = 0.7 / (float(len(interval)) * 3)

    for i, period in enumerate(interval):
        ma_size = period

        # ma = windowed_ma_list(fund['Close'], interval=ma_size)
        weight_strength = 2.0 + (0.1 * float(i))
        ma = windowed_ema_list(fund['Close'], interval=ma_size, weight_strength=weight_strength)
        ex = local_extrema(ma)
        r = reconstruct_extrema(fund['Close'], extrema=ex, ma_size=ma_size, ma_type='windowed')

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

        if progress_bar is not None: progress_bar.uptick(increment=increment)

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

    long_term = 163
    intermediate_term = 91
    short_term = 56
    near_term = 27
    X0, Y0 = get_lines_from_period(fund, [mins_x, mins_y, maxes_x, maxes_y, all_x], interval=long_term)
    X1, Y1 = get_lines_from_period(fund, [mins_x, mins_y, maxes_x, maxes_y, all_x], interval=intermediate_term)
    X2, Y2 = get_lines_from_period(fund, [mins_x, mins_y, maxes_x, maxes_y, all_x], interval=short_term)
    X3, Y3 = get_lines_from_period(fund, [mins_x, mins_y, maxes_x, maxes_y, all_x], interval=near_term)

    if progress_bar is not None: progress_bar.uptick(increment=increment*4.0)

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
    if progress_bar is not None: progress_bar.uptick(increment=increment*4.0)

    analysis_list = generate_analysis(fund, x_list=X, y_list=Y, len_list=L, color_list=C)

    if progress_bar is not None: progress_bar.uptick(increment=0.1)

    X = dates_convert_from_index(fund, X)

    X.append(fund.index)
    Y.append(fund['Close'])
    C.append('black')
    
    if plot_output:
        generic_plotting(Y, x=X, colors=C, title=f"{name} Trend Lines for {near_term}, {short_term}, {intermediate_term}, and {long_term} Periods")
    else:
        filename = f"{name}/trendline_{name}.png"
        generic_plotting(Y, x=X, colors=C, 
                            title=f"{name} Trend Lines for {near_term}, {short_term}, {intermediate_term}, and {long_term} Periods",
                            saveFig=True, filename=filename)

    if progress_bar is not None: progress_bar.uptick(increment=0.2)

    return analysis_list



def get_lines_from_period(fund: pd.DataFrame, kargs: list, interval: int) -> list:
    # print(f"Get Trendlines for period: {interval}")

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

            max_range[1] = line_reducer(fund, max_range[1], reg, threshold=0.06)

            datax = list(range(max_range[0], max_range[1]))
            datay = [reg[0] * float(x) + reg[1] for x in datax]
            if not math.isnan(datay[0]):
                X.append(datax)
                Y.append(datay)

    return X, Y


def line_extender(fund: pd.DataFrame, x_range: list, reg_vals: list) -> int:
    """ returns the end of a particular trend line. returns 0 if segment should be omitted """
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
        """ since we have 'line_reducer', send the maximum and let reducer fix it """
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
        """ since we have 'line_reducer', send the maximum and let reducer fix it """
        return max_len

    return end_pt
        

def line_reducer(fund: pd.DataFrame, last_x_pt, reg_vals: list, threshold=0.05) -> int:
    """ returns shortened lines that protrude far away from overall fund price (to not distort plots) """
    slope = reg_vals[0]
    intercept = reg_vals[1]
    top_thresh = 1.0 + threshold
    bot_thresh = 1.0 - threshold

    x_pt = last_x_pt
    if x_pt > len(fund['Close']):
        x_pt = len(fund['Close'])
    last_pt = intercept + slope * x_pt
    if (last_pt <= (top_thresh * fund['Close'][x_pt-1])) and (last_pt >= (bot_thresh * fund['Close'][x_pt-1])):
        return x_pt
    else:
        while (last_pt > (top_thresh * fund['Close'][x_pt-1])) or (last_pt < (bot_thresh * fund['Close'][x_pt-1])):  
            x_pt -= 1
            last_pt = intercept + slope * x_pt
    return x_pt      


def generate_analysis(fund: pd.DataFrame, x_list: list, y_list: list, len_list: list, color_list: list) -> list:
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
    
    touches = []
    if fund['Close'][x_list[0]] >= y_list[0]:
        state = 'above'
    else:
        state = 'below'
    for i,x in enumerate(x_list):
        if state == 'above':
            if fund['Close'][x] < y_list[i]:
                state = 'below'
                touches.append({'index': x, 'price': fund['Close'][x], 'type': 'cross', 'state': 'below'})
            if fund['Close'][x] == y_list[i]: 
                touches.append({'index': x, 'price': fund['Close'][x], 'type': 'touch', 'state': 'above'})
        else: 
            if fund['Close'][x] >= y_list[i]:
                state = 'above'
                touches.append({'index': x, 'price': fund['Close'][x], 'type': 'cross', 'state': 'above'})
            if fund['Close'][x] == y_list[i]: 
                touches.append({'index': x, 'price': fund['Close'][x], 'type': 'touch', 'state': 'below'})

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
                v_stop_index = touch['index'] - 1 if touch['index'] != 0 else x_list[0]
                v = {'start': {}, 'end': {}}
                v['start']['index'] = v_start_index
                v['start']['date'] = fund.index[v_start_index].strftime("%Y-%m-%d")
                v['end']['index'] = v_stop_index
                v['end']['date'] = fund.index[v_stop_index].strftime("%Y-%m-%d")
                valid.append(v)
                b_start_index = touch['index']
                state = 'below'

            
            if touch['type'] == 'cross' and touch['state'] == 'above':
                # End of a broken period
                b_stop_index = touch['index'] - 1 if touch['index'] != 0 else x_list[0]
                b = {'start': {}, 'end': {}}
                b['start']['index'] = b_start_index
                b['start']['date'] = fund.index[b_start_index].strftime("%Y-%m-%d")
                b['end']['index'] = b_stop_index
                b['end']['date'] = fund.index[b_stop_index].strftime("%Y-%m-%d")
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
                v_stop_index = touch['index'] - 1 if touch['index'] != 0 else x_list[0]
                v = {'start': {}, 'end': {}}
                v['start']['index'] = v_start_index
                v['start']['date'] = fund.index[v_start_index].strftime("%Y-%m-%d")
                v['end']['index'] = v_stop_index
                v['end']['date'] = fund.index[v_stop_index].strftime("%Y-%m-%d")
                valid.append(v)
                b_start_index = touch['index']
                state = 'above'

            
            if touch['type'] == 'cross' and touch['state'] == 'below':
                # End of a broken period
                b_stop_index = touch['index'] - 1 if touch['index'] != 0 else x_list[0]
                b = {'start': {}, 'end': {}}
                b['start']['index'] = b_start_index
                b['start']['date'] = fund.index[b_start_index].strftime("%Y-%m-%d")
                b['end']['index'] = b_stop_index
                b['end']['date'] = fund.index[b_stop_index].strftime("%Y-%m-%d")
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


""" Forecasters for trendlines - more 'future' development """

def trend_simple_forecast(trend: dict, future_periods: list=[5, 10, 20], return_type='price') -> dict:
    """
    args:
        trend:              dict -> each trend is a dict created by generate analysis / attribute analysis
        future_periods:     list -> trading periods FROM last date of trend; if not a 'current' trend, ensure that
                                    each future period is far enough in the future to be relevant to the present
        return_type:        str ->  various return types possible: 'price' (primarily)
    """
    forecast = {'return_type': return_type, 'periods': future_periods, 'returns': []}
    if return_type == 'price':
        # Likely will be only return_type
        slope = trend['slope']
        intercept = trend['intercept']
        end_index = trend['end']['index']
        prices = [np.round(slope * (x + end_index) + intercept, 2) for x in future_periods]

        forecast['returns'] = prices

    return forecast
