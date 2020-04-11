import pandas as pd
import numpy as np

from libs.utils import candlestick
from .moving_average import simple_moving_avg


def candlesticks(fund: pd.DataFrame, **kwargs) -> dict:

    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    view = kwargs.get('view', '')
    pbar = kwargs.get('progress_bar')

    thresholding_determination(fund)
    candle = pattern_detection(fund)

    if plot_output:
        candlestick(fund, title=name)
    else:
        filename = f"{name}/{view}/candlestick_{name}"
        candlestick(fund, title=name, filename=filename,
                    saveFig=True)
    return candle


def pattern_detection(fund: pd.DataFrame, **kwargs) -> dict:

    patterns = dict()

    return patterns


def thresholding_determination(fund: pd.DataFrame):

    open_close = []
    high_low = []
    for i, op in enumerate(fund['Open']):
        open_close.append(np.abs(op - fund['Close'][i]))
        high_low.append(np.abs(fund['High'][i] - fund['Low'][i]))

    print(
        f"Open-Close: 35% {np.percentile(open_close, 35)}, 50% {np.percentile(open_close, 50)}, 65% {np.percentile(open_close, 65)}")


def day_classification(fund: pd.DataFrame) -> list:

    days = []
    # classification elements:
    # current trend (sma-10); short-med-long; black-white; shadow/body ratio;
    # open, close, high, low (raw)
    return days
