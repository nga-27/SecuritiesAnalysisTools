import pandas as pd 
import numpy as np 
from datetime import datetime

from .math_functions import linear_regression
from .moving_average import simple_ma_list

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

