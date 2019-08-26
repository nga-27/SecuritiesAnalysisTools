import pandas as pd 
import numpy as np 
from datetime import datetime
from scipy.stats import linregress

from .math_functions import linear_regression
from .moving_average import simple_ma_list, windowed_ma_list, windowed_ema_list
from libs.utils import generic_plotting

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


def resistance(highs) -> list:
    highs = list(highs)
    if len(highs) <= 14:
        points = TREND_PTS[1]
    elif len(highs) <= 28:
        points = TREND_PTS[2]
    else:
        points = TREND_PTS[0]

    sortedList = sorted(highs, reverse=True)
    
    refs = []
    indices = []
    for i in range(points):
        refs.append(sortedList[i])
        indices.append(highs.index(refs[i]))
    
    trendslope = linear_regression(indices, refs)
    resistance_level = trendslope[1] + trendslope[0] * len(highs)

    return [trendslope, resistance_level]


def support(lows) -> list:
    lows = list(lows)
    if len(lows) <= 14:
        points = TREND_PTS[1]
    elif len(lows) <= 28:
        points = TREND_PTS[2]
    else:
        points = TREND_PTS[0]

    sortedList = sorted(lows)
    
    refs = []
    indices = []
    for i in range(points):
        refs.append(sortedList[i])
        indices.append(lows.index(refs[i]))
    
    trendslope = linear_regression(indices, refs)
    resistance_level = trendslope[1] + trendslope[0] * len(lows)

    return [trendslope, resistance_level]


def trendline(resistance, support) -> list:
    trend_slope = (resistance[0][0] + support[0][0]) / 2.0
    intercept = (resistance[0][1] + support[0][1]) / 2.0
    final_val = intercept + trend_slope * len(resistance)
    difference = resistance[0][0] - support[0][0]

    return [[trend_slope, intercept], final_val, difference]


def trendline_deriv(price) -> list:
    price = list(price)
    derivative = []
    for val in range(1, len(price)):
        derivative.append(price[val] - price[val-1])

    deriv = np.sum(derivative)
    deriv = deriv / float(len(derivative))
    return deriv


def trend_filter(osc: dict, position: pd.DataFrame) -> dict:
    """ Filters oscillator dict to remove trend bias.

        Ex: strong upward trend -> removes weaker drops in oscillators
    """
    filtered = {}

    return filtered 



################################
"""
Algorithmic theory:
1) Find min and max of each iteration.
2) If trend in region of top 3 points has high rvalue (>= 0.95?), then use trend

Another option:
1) Find linear regression of a size (interval?)
2) Find variance/error from points from linear regression line.  Max deviations are max/min?

Option (from online):
https://stackoverflow.com/questions/43769906/how-to-calculate-the-trendline-for-stock-price
"""

def get_maxima_minima(data: pd.DataFrame, interval: list=[8, 16, 34, 55]):
    
    MULTIPLIER = 2
    for inter in interval:
        mins = []
        xs = []
        y = []
        x = []

        data1 = data.copy()
        data1.reset_index(drop=True, inplace=True)
        data1['date_index'] = list(range(len(data['Close'])))
        leng = len(data1['Close'])
        data1.drop(data1.index[0:leng-(MULTIPLIER * inter)], inplace=True)
        data2 = pd.DataFrame() 

        start = data1['Close'][leng - (MULTIPLIER * inter)]
        end = data1['Close'][leng-1]
        if end - start > 0:
            slope = 1
        else:
            slope = -1

        reg = linregress(x=data1['date_index'], y=data1['Close'])
        data2 = data1.copy()
        if slope > 0:
            print("+ slope")
            slope = 1
            while ((len(data1['Close']) > 3) and (reg[0] > 0.0)):
                reg = linregress(x=data1['date_index'], y=data1['Close'])
                data2 = data1.copy()
                data1 = data1.loc[data1['Close'] < reg[0] * data1['date_index'] + reg[1]]
        else:
            print("- slope")
            slope = -1
            while ((len(data1['Close']) > 3) and (reg[0] <= 0.0)):
                reg = linregress(x=data1['date_index'], y=data1['Close'])
                data2 = data1.copy()
                data1 = data1.loc[data1['Close'] > reg[0] * data1['date_index'] + reg[1]]

        if len(data1['Close']) < 2:
            reg = linregress(x=data2['date_index'], y=data2['Close'])
        else:
            reg = linregress(x=data1['date_index'], y=data1['Close'])

        if ((slope > 0) and (reg[0] < 0)):
            reg = linregress(x=data2['date_index'], y=data2['Close'])
        elif ((slope < 0) and (reg[0] > 0)):
            reg = linregress(x=data2['date_index'], y=data2['Close'])
                 
        x = list(range(leng - (MULTIPLIER * inter), leng))
        y = [reg[0] * xi + reg[1] for xi in x]   
        mins.append(y)
        xs.append(x)

        xs.append(list(range(len(data['Close']))))
        mins.append(list(data['Close']))
        generic_plotting(mins, x_=xs)



def get_trendlines_2(fund: pd.DataFrame, interval: list=[4, 8, 16, 32]):
    mins_y = []
    mins_x = []
    maxes_y = []
    maxes_x = []
    all_x = []

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

    X = []
    Y = []
    for i, x in enumerate(X0):
        X.append(x)
        Y.append(Y0[i])
    for i, x in enumerate(X1):
        X.append(x)
        Y.append(Y1[i])
    for i, x in enumerate(X2):
        X.append(x)
        Y.append(Y2[i])
    for i, x in enumerate(X3):
        X.append(x)
        Y.append(Y3[i])

    X.append(list(range(0,len(fund['Close']))))
    Y.append(fund['Close'])
    generic_plotting(Y, x_=X)

    


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
            max_range = [start, end + EXTENSION]
            if max_range[1] > len(fund['Close']):
                max_range[1] = len(fund['Close'])
            if interval > 100:
                max_range[1] = len(fund['Close'])
            if end + EXTENSION > int(0.9 * float(len(fund['Close']))):
                max_range[1] = len(fund['Close'])
            max_range[1] = line_reducer(fund, max_range[1], reg)

            datax = list(range(max_range[0], max_range[1]))
            datay = [reg[0] * x + reg[1] for x in datax]
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
        while (end_pt < max_len):
            y_val = intercept + slope * end_pt
            if fund['Close'][i] < y_val:
                return end_pt
            end_pt += 1

    else:
        end_pt = x_range[len(x_range)-1]
        start_pt = x_range[0]
        for i in range(start_pt, end_pt):
                y_val = intercept + slope * i
                if fund['Close'][i] > (y_val * 1.01):
                    # Original trendline was not good enough - omit
                    return 0
        # Now that original trendline is good, find ending
        while (end_pt < max_len):
            y_val = intercept + slope * end_pt
            if fund['Close'][i] > y_val:
                return end_pt
            end_pt += 1

    return end_pt
        

def line_reducer(fund: pd.DataFrame, last_x_pt, reg_vals: list) -> int:
    """ returns shortened lines that protrude far away from overall fund price (to not distort plots) """
    slope = reg_vals[0]
    intercept = reg_vals[1]

    x_pt = last_x_pt
    if x_pt >= len(fund['Close']):
        x_pt = len(fund['Close']) -1
    last_pt = intercept + slope * x_pt
    # print(f"x_pt {x_pt}, last_pt {last_pt}, len {len(fund['Close'])}")
    if (last_pt <= (1.05 * fund['Close'][x_pt])) and (last_pt >= (0.95 * fund['Close'][x_pt])):
        return x_pt
    else:
        while (last_pt > (1.05 * fund['Close'][x_pt])) or (last_pt < (0.95 * fund['Close'][x_pt])):  
            x_pt -= 1
            last_pt = intercept + slope * x_pt
    return x_pt      


