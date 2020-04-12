import pprint
import pandas as pd
import numpy as np

from libs.utils import candlestick
from .moving_average import simple_moving_avg


def candlesticks(fund: pd.DataFrame, **kwargs) -> dict:

    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    view = kwargs.get('view', '')
    pbar = kwargs.get('progress_bar')

    candle = dict()

    candle['thresholds'] = thresholding_determination(
        fund, plot_output=plot_output)
    candle['classification'] = day_classification(fund, candle['thresholds'])
    candle['patterns'] = pattern_detection(fund)

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


def thresholding_determination(fund: pd.DataFrame, **kwargs) -> dict:

    LONG = kwargs.get('long_percentile', 85)
    SHORT = kwargs.get('short_percentile', 25)
    DOJI = kwargs.get('doji_percentile', 1)
    DOJI_RATIO = kwargs.get('doji_ratio', 8)
    plot_output = kwargs.get('plot_output', True)

    open_close = []
    high_low = []
    for i, op in enumerate(fund['Open']):
        open_close.append(np.abs(op - fund['Close'][i]))
        high_low.append(np.abs(fund['High'][i] - fund['Low'][i]))

    thresholds = dict()
    thresholds['short'] = np.percentile(open_close, SHORT)
    thresholds['long'] = np.percentile(open_close, LONG)
    thresholds['doji'] = np.percentile(open_close, DOJI)
    thresholds['doji_ratio'] = DOJI_RATIO

    if plot_output:
        print(f"Thresholding for candlesticks:")
        pprint.pprint(thresholds)
        candlestick(fund, title="Doji & Long/Short Days",
                    threshold_candles=thresholds)

    return thresholds


def day_classification(fund: pd.DataFrame, thresholds: dict) -> list:

    days = []
    # classification elements:
    # current trend (sma-10); short-med-long; black-white; shadow/body ratio;
    # open, close, high, low (raw)
    return days
