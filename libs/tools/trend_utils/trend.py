""" Get Trend """
import pandas as pd
import numpy as np

from libs.tools import simple_moving_avg
from .trend_of_dates import trend_of_dates


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
        trend['tabular'] = simple_moving_avg(position, ma_size, data_type='list')
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
    for i, trend_val in enumerate(trend):
        diff_from_trend.append(np.round(position['Close'][i] - trend_val, 3))
    return diff_from_trend
