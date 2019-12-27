import pandas as pd 
import numpy as np 
from datetime import datetime
import pprint

from libs.utils import ProgressBar
from libs.tools import trends
from .feature_utils import feature_plotter

NEXT_STATE = {
    "breakaway": "runaway",
    "runaway": "exhaustion",
    "exhaustion": "breakaway"
}


def analyze_price_gaps(fund: pd.DataFrame, **kwargs) -> dict:
    """
    Analyze Price Gaps - determine state, if any, of price gaps for funds

    args:
        position:       (pd.DataFrame) list of y-value datasets to be plotted (multiple)

    optional args:
        name:           (list) name of fund, primarily for plotting; DEFAULT=''
        plot_output:    (bool) True to render plot in realtime; DEFAULT=True
        progress_bar:   (ProgressBar) DEFAULT=None
    """
    name = kwargs.get('name', '')
    plot_output = kwargs.get('plot_output', True)
    progress_bar = kwargs.get('progress_bar', None)

    threshold = 0.0075
    gaps = get_gaps(fund, threshold=threshold)
    if progress_bar is not None: progress_bar.uptick(increment=0.25)

    gaps = determine_gap_types(fund, gaps, name=name)
    if progress_bar is not None: progress_bar.uptick(increment=0.25)

    feature_plotter(fund, shapes=gaps['plot'], name=name, feature='price_gaps', plot_output=plot_output)
    if progress_bar is not None: progress_bar.uptick(increment=0.5)

    return gaps


def get_gaps(fund: pd.DataFrame, threshold=0.0) -> list:
    gap_index = []
    gap_date = []
    gap_direction = []
    diff = []
    for i in range(1, len(fund['Close'])):
        if (fund['High'][i-1] < fund['Low'][i] * (1.0 - threshold)): 
            # Positive price gap
            gap_index.append(i)
            gap_date.append(fund.index[i].strftime("%Y-%m-%d"))
            gap_direction.append("up")
            diff.append(fund['High'][i] - fund['High'][i-1])
        elif (fund['High'][i] < fund['Low'][i-1] * (1.0 - threshold)): 
            # Negative price gap
            gap_index.append(i)
            gap_date.append(fund.index[i].strftime("%Y-%m-%d"))
            gap_direction.append("down")
            diff.append(fund['Low'][i] - fund['Low'][i-1])

    return {"indexes": gap_index, "dates": gap_date, "direction": gap_direction, "difference": diff}


def determine_gap_types(fund: pd.DataFrame, gaps: dict, name: str='') -> dict:
    trend_short = trends.autotrend(fund['Close'], periods=[7], normalize=True)
    trend_med = trends.autotrend(fund['Close'], periods=[14], normalize=True)
    trend_long = trends.autotrend(fund['Close'], periods=[28], normalize=True)

    # TODO: Trends w/ gaps might provide insights...
    gaps['trend_short'] = list()
    gaps['trend_med'] = list()
    gaps['trend_long'] = list()
    gaps['plot'] = list()

    for i, index in enumerate(gaps['indexes']):
        sl_short = trend_short[index]
        gaps['trend_short'].append(sl_short)
        sl_med = trend_med[index]
        gaps['trend_med'].append(sl_med)
        sl_long = trend_long[index]
        gaps['trend_long'].append(sl_long)

        if gaps['direction'] == 'up':
            y_diff = float(gaps['difference'][i]) / 2.0 + fund['High'][index-1]
        else:
            y_diff = float(gaps['difference'][i]) / 2.0 + fund['Low'][index-1]
        gaps['plot'].append({"type": gaps['direction'][i], "x": index, "y": y_diff, "rad": gaps['difference'][i]})

    return gaps
