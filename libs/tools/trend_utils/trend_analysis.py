""" Trend Analysis """
from typing import Union
import pandas as pd

from .trend import get_trend


def get_trend_analysis(position: pd.DataFrame, config: Union[list, None] = None) -> dict:
    """Get Trend Analysis

    Determines long, med, and short trend of a position

    Arguments:
        position {pd.DataFrame} -- fund dataset

    Keyword Arguments:
        config {list} -- list of moving average look backs, longest to shortest
                         (default: {[50, 25, 12]})

    Returns:
        dict -- trend notes
    """
    # pylint: disable=chained-comparison
    if not config:
        config = [50, 25, 12]

    t_long = get_trend(position, style='sma', ma_size=config[0])
    t_med = get_trend(position, style='sma', ma_size=config[1])
    t_short = get_trend(position, style='sma', ma_size=config[2])

    trend_analysis = {}
    trend_analysis['long'] = t_long['magnitude']
    trend_analysis['medium'] = t_med['magnitude']
    trend_analysis['short'] = t_short['magnitude']

    if trend_analysis['long'] > 0.0:
        trend_analysis['report'] = 'Overall UPWARD, '
    else:
        trend_analysis['report'] = 'Overall DOWNWARD, '

    if abs(trend_analysis['short']) > abs(trend_analysis['medium']):
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
