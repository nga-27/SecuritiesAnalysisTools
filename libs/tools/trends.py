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


"""
New algorithm idea:
1) Find slope for interval[MIN] at index=0, where MIN is current shortest interval chain
    1a) if index(min(data[int])) != 0 AND index(max(data[int])) != 0 -> regression to find trend
    1b) if index(min(data[int])) == 0 -> up trend ("higher lows")
    1c) if index(max(data[int])) == 0 -> down trend ("lower highs")
2) Find trend line for interval[MIN] at index, where MIN is current shortest interval chain
2) Crossing?
    2a) Yes - Drop to interval[MAX-1], goto 1
    2b) No - Seen cross?
        2ba) No - set interval to next item w/ same slope goto 2
        2bb) Yes - Done. Add current interval to index (index+=cur_inter), goto 2
"""
    
def has_crossover(data: pd.DataFrame, trendline: list, x: list, slope: int):
    breaker = 0
    tind = 0
    breaks = []
    for i in range(x[0], x[len(x)-1]+1):
        if slope > 0:
            if trendline[tind] > data['Close'][i]:
                breaker += 1
                breaks.append(i)
        else:
            if trendline[tind] < data['Close'][i]:
                breaker += 1
                breaks.append(i)
        tind += 1
    if breaker > 3:
        return True, breaks
    return False, None


def get_slope(data: pd.DataFrame, start: int, interval: int) -> int:
    minx = np.where(data['Close'][start:start+interval] == np.min(data['Close'][start:start+interval]))[0][0] + start
    maxx = np.where(data['Close'][start:start+interval] == np.max(data['Close'][start:start+interval]))[0][0] + start

    if (start != minx) and (start != maxx):
        # Regression case
        return 0
    elif start == minx:
        return 1
    elif start == maxx:
        return -1
    else:
        print(f"WARNING: Logic Error (get_slope); start: {start}, min: {minx}, max: {maxx}")
        return 0



def get_tline(data: pd.DataFrame, start: int, interval: int, slope: int) -> list:
    """ Assume logic outside function to prevent index out of bounds issues, etc. """
    # slope = get_slope(data, start, interval)
    # print(f"t_line slope: {slope}")

    data1 = data.copy()
    data1.reset_index(drop=True, inplace=True)
    data1['date_index'] = list(range(len(data['Close'])))
    leng = len(data1['Close'])
    if start > 0:
        data1.drop(data1.index[0:start], inplace=True)
    data1.drop(data1.index[start + interval:leng], inplace=True)
    data2 = data1.copy()

    if slope == 0:
        # print(f"t_line x: {data1['date_index']}, y: {data1['Close']}")
        reg = linregress(x=data1['date_index'], y=data1['Close'])
        print(f"t_line slope determine: {reg[0]}")
        if reg[0] > 0:
            slope = 1
        else:
            slope = -1

    reg = [0.0, 0.0]
    if slope > 0:
        reg[0] = 1.0
        while ((len(data1['Close']) > 3) and (reg[0] > 0.0)):
            reg = linregress(x=data1['date_index'], y=data1['Close'])
            data2 = data1.copy()
            data1 = data1.loc[data1['Close'] < reg[0] * data1['date_index'] + reg[1]]
    else:
        reg[0] = -1.0
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
            
    X = list(range(start, start + interval))
    Y = [reg[0] * xi + reg[1] for xi in X] 

    return X, Y, slope



def get_trendlines(data: pd.DataFrame, interval: list=[16]):
    ADD_INTERVAL = 3
    tX = []
    tY = []
    tX.append(list(range(len(data['Close']))))
    tY.append(list(data['Close']))

    start_index = 0
    len_data = len(data['Close'])
    inter_count = 0
    cur_interval = interval[inter_count]
    max_interval = 90
    X = []
    Y = []

    slope = get_slope(data, start_index, cur_interval)

    while (start_index + cur_interval < len_data):
        print(f"start_index: {start_index}, cur_interval: {cur_interval}, slope: {slope}")
        X2 = X.copy()
        Y2 = Y.copy()

        X, Y, temp_slope = get_tline(data, start_index, cur_interval, slope)
        if slope == 0:
            slope = temp_slope

        crossover, breaks = has_crossover(data, Y, X, slope)
        print(f"Y: {Y[0:8]} breaks: {breaks}")

        if crossover == False:
            inter_count += 1
            if inter_count >= len(interval):
                cur_interval = interval[len(interval)-1]
                temp_int = (inter_count - (len(interval)-1)) * ADD_INTERVAL
                cur_interval += temp_int
            else:
                cur_interval = interval[inter_count]
            
            if (start_index + cur_interval > len_data):
                tY.append(Y)
                tX.append(X)
                break

        if crossover == True:
            # We've gone too far! Use X2, Y2 since they were previous state.
            tX.append(X2)
            tY.append(Y2)
            breaker = breaks[len(breaks)-1]
            start_index = breaker
            # start_index += cur_interval
            inter_count = 0
            cur_interval = interval[inter_count]
            if start_index + cur_interval < len_data:
                slope = get_slope(data, start_index, cur_interval)
            X = []
            Y = []

        if cur_interval >= max_interval:
            tX.append(X)
            tY.append(Y)
            start_index += cur_interval 
            inter_count = 0
            cur_interval = interval[inter_count]
            if start_index + cur_interval < len_data:
                slope = get_slope(data, start_index, cur_interval)
            X = []
            Y = []
            
    generic_plotting(tY, x_=tX)



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

        # print(f"extrema: {r}")

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

    mins_xd = [fund.index[x] for x in mins_x]
    maxes_xd = [fund.index[x] for x in maxes_x]

    generic_plotting([fund['Close'], mins_y, maxes_y], x_=[list(fund.index), mins_xd, maxes_xd], legend=['f', 'min', 'max'])

    long_term = 180
    intermediate_term = 90
    short_term = 20 
    get_lines_from_period(fund, [mins_x, mins_y, maxes_x, maxes_y, all_x], interval=long_term)

    


def get_lines_from_period(fund: pd.DataFrame, kargs: list, interval: int) -> list:
    mins_y = kargs[1]
    mins_x = kargs[0]
    maxes_y = kargs[3]
    maxes_x = kargs[2]

    




def get_the_lines(fund: pd.DataFrame, kargs: list):
    mins_y = kargs[1]
    mins_x = kargs[0]
    maxes_y = kargs[3]
    maxes_x = kargs[2]
    # all_x = kargs[4]

    EXTENSION = 25

    X = []
    Y = []

    # Start with minimums
    print("Starting mins")
    ix = 1
    x0 = [mins_x[ix-1], mins_x[ix]]
    y0 = [mins_y[ix-1], mins_y[ix]]
    start_pt = x0[0]
    ix += 1
    while (ix < len(mins_x)):
        
        lin = linregress(x=x0, y=y0)
        above_line = True
        next_x = mins_x[ix]
        while above_line:
            next_x += 1
            if next_x == len(fund['Close']):
                break
            if ix == len(mins_x):
                break
            if next_x == mins_x[ix]:
                x1 = [mins_x[ix-1], mins_x[ix]]
                y1 = [mins_y[ix-1], mins_y[ix]]
                lin1 = linregress(x=x1, y=y1)
                if (lin1[0] > lin[0] * 0.99) and (lin1[0] < lin[0] * 1.01):
                    x0.append(mins_x[ix])
                    y0.append(mins_y[ix])
                    ix += 1

            new_line_x = list(range(start_pt, next_x))
            new_line_y = [lin[1] + lin[0]*x for x in new_line_x]
            above_line = line_check(fund, line_x=new_line_x, line_y=new_line_y, metric='above')

        new_line_x = list(range(start_pt, next_x+EXTENSION))
        new_line_y = [lin[1] + lin[0]*x for x in new_line_x]

        X.append(new_line_x)
        Y.append(new_line_y)

        if ix+1 < len(mins_x):
            ix+=1
            x0 = [mins_x[ix-1], mins_x[ix]]
            y0 = [mins_y[ix-1], mins_y[ix]]
            start_pt = mins_x[ix-1]
        else:
            break

    # Maxes 
    print("Starting maxes")
    ix = 1
    x0 = [maxes_x[ix-1], maxes_x[ix]]
    y0 = [maxes_y[ix-1], maxes_y[ix]]
    start_pt = x0[0]
    ix += 1
    while (ix < len(maxes_x)):
        
        lin = linregress(x=x0, y=y0)
        above_line = True
        next_x = maxes_x[ix]
        while above_line:
            next_x += 1
            if next_x == len(fund['Close']):
                break
            if ix == len(maxes_x):
                break
            if next_x == maxes_x[ix]:
                x1 = [maxes_x[ix-1], maxes_x[ix]]
                y1 = [maxes_y[ix-1], maxes_y[ix]]
                lin1 = linregress(x=x1, y=y1)
                if (lin1[0] > lin[0] * 0.99) and (lin1[0] < lin[0] * 1.01):
                    x0.append(maxes_x[ix])
                    y0.append(maxes_y[ix])
                    ix += 1

            new_line_x = list(range(start_pt, next_x))
            new_line_y = [lin[1] + lin[0]*x for x in new_line_x]
            above_line = line_check(fund, line_x=new_line_x, line_y=new_line_y, metric='below')

        new_line_x = list(range(start_pt, next_x+EXTENSION))
        new_line_y = [lin[1] + lin[0]*x for x in new_line_x]

        X.append(new_line_x)
        Y.append(new_line_y)

        if ix+1 < len(maxes_x):
            ix+=1
            x0 = [maxes_x[ix-1], maxes_x[ix]]
            y0 = [maxes_y[ix-1], maxes_y[ix]]
            start_pt = maxes_x[ix-1]
        else:
            break

    X.append(list(range(0,len(fund['Close']))))
    Y.append(fund['Close'])
    generic_plotting(Y, x_=X)


        


def line_check(fund: pd.DataFrame, line_x: list, line_y: list, metric='above') -> bool:
    if metric == 'above':
        for i, x in enumerate(line_x):
            if fund['Close'][x] < line_y[i]:
                return False

    else:
        for i, x in enumerate(line_x):
            if fund['Close'][x] > line_y[i]:
                return False

    return True


    
         

        


    

