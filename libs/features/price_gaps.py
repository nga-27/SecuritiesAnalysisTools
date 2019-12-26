import pandas as pd 
import numpy as np 
from datetime import datetime
import pprint

from libs.utils import ProgressBar


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

    gaps = {}
    threshold = 0.01

    gap_points = get_gaps(fund, threshold=threshold)
    gaps['dates'] = gap_points['dates']
    gaps['indexes'] = gap_points['indexes']

    return gaps


def get_gaps(fund: pd.DataFrame, threshold=0.0) -> list:
    gap_index = []
    gap_date = []
    for i in range(1, len(fund['Close'])):
        if (fund['Close'][i-1] < fund['Open'][i] * (1.0 - threshold)) and (fund['Close'][i] > fund['Open'][i]):
            # Positive price gap
            gap_index.append(i)
            gap_date.append(fund.index[i].strftime("%Y-%m-%d"))
        elif (fund['Open'][i] < fund['Close'][i-1] * (1.0 - threshold) and (fund['Close'][i] < fund['Open'][i])):
            # Negative price gap
            gap_index.append(i)
            gap_date.append(fund.index[i].strftime("%Y-%m-%d"))

    return {"indexes": gap_index, "dates": gap_date}
