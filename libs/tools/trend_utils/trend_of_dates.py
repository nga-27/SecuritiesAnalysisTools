""" Trend of Dates """
from datetime import datetime

import numpy as np
import pandas as pd


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
